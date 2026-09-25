#!/usr/bin/env python3
"""Proofread the corpus text against the page images, and apply the exact corrections found.

    proofread.py test <uid> <page> ...    # proofread these pages now (full price), print the corrections
    proofread.py submit <uid> ... | --all # queue every page not yet proofread in its current form (Batch API)
    proofread.py collect                  # fetch finished batches into the cache
    proofread.py apply [<uid> ...]        # apply cached corrections to data/text (all documents by default)
    proofread.py report [<uid> ...]       # what was applied and what was skipped

Claude sees the page image and our text for it, and returns only differences between the two, each as
{find, replace, kind}. A correction is applied only when its `find` occurs exactly once in the page text.
Corrections are cached in data/proof/<slug>.json under the PDF hash, page, the hash of the page text they
were made for, the model and the prompt version, so a page is only proofread again when its text changes.
A correction a reviewer finds wrong gets "rejected": "<reason>" in the cache and is never applied (the proofreader
sometimes "fixes" a typo that the page itself prints). Run it after vision_ocr.py writes (a rewrite from the vision cache drops applied corrections; run apply again).
"""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vision_ocr import DATA, MODEL, client, doc_for, pdf_hash, render, registry, base64
from extract import page_count

PROOF = os.path.join(DATA, "proof")
JOBS = os.path.join(PROOF, "jobs.json")
MAX_BATCH = 100
PROMPT_V = 1
KINDS = ["wrong_letters", "missing_text", "extra_text", "wrong_number", "wrong_order", "punctuation"]
SYSTEM = """You proofread a transcription of one page of a Persian-language constitutional document against the page image. The transcription feeds a research corpus that quotes the documents, so it must match the printed page word for word.

Report every place where the transcription differs from what is printed:
- wrong_letters: a word misspelled compared with the page (wrong, missing, extra or reversed letters, e.g. «اطاع» where the page has «اطلاع», «صالحیت» for «صلاحیت»).
- missing_text: words or whole lines printed on the page but absent from the transcription.
- extra_text: text in the transcription that is not on the page (garbage characters, repeated lines, invented words).
- wrong_number: an article, clause or other number that differs from the page.
- wrong_order: lines or words out of the page's reading order.
- punctuation: a punctuation mark that differs in a way that changes reading (e.g. «»» where the page has «،»).

Do not report:
- differences that are only a space versus a zero-width non-joiner (half-space), Arabic versus Persian letter forms (ي/ی, ك/ک), stretched letters (ـ), line breaks, or diacritics;
- the page's own spelling mistakes or unusual spellings: when the page itself has the error, the transcription is right to copy it;
- running headers, footers or page numbers the transcription left out;
- anything you cannot read clearly on the image.

Each correction:
- find: text copied exactly, character for character, from the transcription, long enough to occur only once on the page (usually 3 to 8 words including the error). For missing text, find the transcription text just before the gap.
- replace: what that same stretch should be according to the page (for missing text: the found text followed by the missing words or lines).
- kind: one of the kinds above.

If the transcription matches the page, return an empty list."""

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["corrections"],
          "properties": {"corrections": {"type": "array", "items": {
              "type": "object", "additionalProperties": False, "required": ["find", "replace", "kind"],
              "properties": {"find": {"type": "string"}, "replace": {"type": "string"},
                             "kind": {"type": "string", "enum": KINDS}}}}}}


def text_doc(uid):
    slug, pdf = doc_for(uid)
    path = os.path.join(DATA, "text", slug + ".json")
    return slug, pdf, path, json.load(open(path, encoding="utf-8"))


def key(sha, page, text):
    return f"{sha}:{page}:{hashlib.sha256(text.encode()).hexdigest()[:16]}:{MODEL}:v{PROMPT_V}"


def load(slug):
    path = os.path.join(PROOF, slug + ".json")
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"pages": {}}


def save(slug, cache):
    os.makedirs(PROOF, exist_ok=True)
    json.dump(cache, open(os.path.join(PROOF, slug + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def params(pdf, page, n, text):
    img = base64.standard_b64encode(render(pdf, page)).decode()
    return {"model": MODEL, "max_tokens": 8000, "thinking": {"type": "disabled"}, "system": SYSTEM,
            "output_config": {"format": {"type": "json_schema", "schema": SCHEMA}},
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img}},
                {"type": "text", "text": f"Page {page} of {n}. Transcription:\n<transcription>\n{text}\n</transcription>"}]}]}


def entry_for(msg):
    usage = {k: getattr(msg.usage, k, 0) or 0 for k in ("input_tokens", "output_tokens")}
    if msg.stop_reason != "end_turn":
        return None, f"stop_reason {msg.stop_reason}"
    text = next(b.text for b in msg.content if b.type == "text")
    return {"corrections": json.loads(text)["corrections"], "usage": usage}, None


def pending(uid):
    """(page, text) for pages not yet proofread in their current form."""
    slug, pdf, _, doc = text_doc(uid)
    sha, cache = pdf_hash(pdf), load(slug)
    return [(p["page"], p["text"]) for p in doc["pages"]
            if p["text"].strip() and key(sha, p["page"], p["text"]) not in cache["pages"]]


def cmd_test(uid, pages):
    slug, pdf, _, doc = text_doc(uid)
    sha, n, cache, c = pdf_hash(pdf), page_count(pdf), load(slug), client()
    for p in pages:
        text = doc["pages"][p - 1]["text"]
        k = key(sha, p, text)
        if k not in cache["pages"]:
            entry, why = entry_for(c.messages.create(**params(pdf, p, n, text)))
            if not entry:
                print(f"--- page {p}: {why}"); continue
            cache["pages"][k] = entry | {"page": p}
            save(slug, cache)
        e = cache["pages"][k]
        print(f"--- page {p}  {e.get('usage')}  {len(e['corrections'])} corrections")
        for x in e["corrections"]:
            print(f"  [{x['kind']}] {x['find']!r}\n      -> {x['replace']!r}  ({text.count(x['find'])}x on page)")


def cmd_submit(uids):
    c, reqs = client(), []
    for uid in uids:
        slug, pdf, _, _ = text_doc(uid)
        todo, n = pending(uid), page_count(pdf)
        print(f"{uid}: {len(todo)} pages to proofread")
        reqs += [(uid, pdf, p, n, t) for p, t in todo]
    jobs = json.load(open(JOBS)) if os.path.exists(JOBS) else []
    for i in range(0, len(reqs), MAX_BATCH):
        chunk = reqs[i:i + MAX_BATCH]
        batch = c.messages.batches.create(requests=[{"custom_id": f"{uid}--p{p}", "params": params(pdf, p, n, t)}
                                                    for uid, pdf, p, n, t in chunk])
        # the text each request saw, by hash, so results are keyed to it even if data/text changes meanwhile
        jobs.append({"batch": batch.id, "collected": False,
                     "pages": {f"{uid}--p{p}": [uid, p, hashlib.sha256(t.encode()).hexdigest()[:16]] for uid, _, p, _, t in chunk}})
        print(f"batch {batch.id}: {len(chunk)} pages")
    os.makedirs(PROOF, exist_ok=True)
    json.dump(jobs, open(JOBS, "w"), indent=1)


def cmd_collect():
    if not os.path.exists(JOBS): sys.exit("no jobs")
    jobs, c = json.load(open(JOBS)), client()
    for job in [j for j in jobs if not j["collected"]]:
        b = c.messages.batches.retrieve(job["batch"])
        if b.processing_status != "ended":
            print(f"batch {job['batch']}: {b.processing_status} ({b.request_counts.processing} processing)"); continue
        caches, failed = {}, []
        for r in c.messages.batches.results(job["batch"]):
            uid, p, th = job["pages"][r.custom_id]
            slug, pdf = doc_for(uid)
            if slug not in caches: caches[slug] = (load(slug), pdf_hash(pdf))
            entry, why = entry_for(r.result.message) if r.result.type == "succeeded" else (None, r.result.type)
            if not entry:
                failed.append(f"{uid} p{p}: {why}"); continue
            cache, sha = caches[slug]
            cache["pages"][f"{sha}:{p}:{th}:{MODEL}:v{PROMPT_V}"] = entry | {"page": p}
        for slug, (cache, _) in caches.items(): save(slug, cache)
        job["collected"] = True
        print(f"batch {job['batch']}: collected, {len(failed)} failed" + "".join(f"\n    {f}" for f in failed))
    json.dump(jobs, open(JOBS, "w"), indent=1)
    if all(j["collected"] for j in jobs): print("all batches collected")


def cmd_apply(uids, write=True):
    for uid in uids:
        slug, pdf, path, doc = text_doc(uid)
        sha, cache = pdf_hash(pdf), load(slug)
        done, skipped = [], []
        for pg in doc["pages"]:
            e = cache["pages"].get(key(sha, pg["page"], pg["text"]))
            if not e: continue
            text = pg["text"]
            for x in e["corrections"]:
                if x["find"] == x["replace"] or x.get("rejected"): continue
                n = text.count(x["find"])
                if n != 1:
                    skipped.append((pg["page"], x, f"found {n}x")); continue
                text = text.replace(x["find"], x["replace"])
                done.append((pg["page"], x))
            if text != pg["text"]:
                pg["text"] = text
                # the corrected page is what was proofread: record it so the next submit skips it
                cache["pages"][key(sha, pg["page"], text)] = {"corrections": [], "page": pg["page"], "after_apply": True}
        if write:
            json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            save(slug, cache)
        kinds = {}
        for _, x in done: kinds[x["kind"]] = kinds.get(x["kind"], 0) + 1
        print(f"{uid}: applied {len(done)} {kinds}, skipped {len(skipped)}")
        if not write:
            for p, x in done: print(f"  p{p} [{x['kind']}] {x['find']!r} -> {x['replace']!r}")
            for p, x, why in skipped: print(f"  SKIP p{p} ({why}) {x['find']!r} -> {x['replace']!r}")


def all_uids():
    return [u for u, d in registry().items() if os.path.exists(os.path.join(DATA, "text", d["legacy_slug"] + ".json"))]


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    uids = lambda: all_uids() if a[1:] in ([], ["--all"]) else a[1:]
    if a[0] == "test" and len(a) >= 3: cmd_test(a[1], [int(x) for x in a[2:]])
    elif a[0] == "submit" and len(a) >= 2: cmd_submit(uids())
    elif a[0] == "collect": cmd_collect()
    elif a[0] == "apply": cmd_apply(uids())
    elif a[0] == "report": cmd_apply(uids(), write=False)
    else: sys.exit(__doc__)

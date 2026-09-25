#!/usr/bin/env python3
"""Read scanned pages with Claude's vision where Tesseract loses lines or misreads digits.

    vision_ocr.py test <uid> <page> ...   # read these pages now (full price), print them
    vision_ocr.py submit <uid> ...        # queue every uncached page of these documents (Batch API, half price)
    vision_ocr.py collect                 # fetch finished batches; rewrite data/text for complete documents
    vision_ocr.py write <uid> ...         # rewrite data/text from the cache only

Each page is cached in data/vision/<slug>.json under a key made of the PDF's hash, the page,
the model and the prompt version, so unchanged input is never sent twice. The Anthropic key
comes from ANTHROPIC_API_KEY or local/anthropic.env (gitignored).
"""
import base64, hashlib, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "(پیشنهادهای پیش‌نویس) قانون اساسی")
DATA = os.path.join(ROOT, "data")
CACHE = os.path.join(DATA, "vision")
JOBS = os.path.join(CACHE, "jobs.json")
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
from extract import normalize_fa, page_count

MODEL = "claude-opus-5"
LONG_EDGE = 2576          # the model's full resolution; larger images are scaled down server side
MAX_BATCH = 100           # requests per batch, well under the 256 MB limit at ~1 MB a page
PROMPT_V = 1
SYSTEM = """You transcribe page images of Persian-language constitutional drafts into plain text for a research corpus. Output exactly the text printed on the page, in reading order, and nothing else.

- Copy every word as printed. Do not correct spelling, grammar or punctuation, do not modernise, do not complete cut-off words, do not translate.
- Keep every number exactly as printed, heading numbers above all («اصل ۶۴», «ماده ۱۲», «فصل سوم»). Persian digits stay Persian and Latin digits stay Latin.
- One printed line per output line. A heading printed on its own line goes on its own line.
- Leave out page numbers and running headers or footers repeated on every page. Keep footnotes, after the body text, each starting with its marker.
- Tables: one row per line, cells separated by " | ".
- Text on dark backgrounds, in banners, logos or stamps counts: transcribe it.
- Where a word cannot be read, write [?] in its place rather than guessing.
- No markdown and no commentary. If the page has no text, output nothing."""


def api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    path = os.path.join(ROOT, "local", "anthropic.env")
    if not key and os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.startswith("ANTHROPIC_API_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key:
        sys.exit("ANTHROPIC_API_KEY is not set (export it or put ANTHROPIC_API_KEY=... in local/anthropic.env)")
    return key


def client():
    import anthropic
    return anthropic.Anthropic(api_key=api_key())


def registry():
    return {d["uid"]: d for d in json.load(open(os.path.join(DATA, "registry.json"), encoding="utf-8"))}


def doc_for(uid):
    entry = registry().get(uid)
    if not entry: sys.exit(f"unknown uid: {uid}")
    slug = entry["legacy_slug"]
    text = json.load(open(os.path.join(DATA, "text", slug + ".json"), encoding="utf-8"))
    return slug, os.path.join(SRC, text["source_pdf"])


def pdf_hash(pdf):
    return hashlib.sha256(open(pdf, "rb").read()).hexdigest()[:16]


def page_key(sha, page):
    return f"{sha}:{page}:{MODEL}:{LONG_EDGE}:v{PROMPT_V}"


def load_cache(slug):
    path = os.path.join(CACHE, slug + ".json")
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"pages": {}}


def save_cache(slug, cache):
    os.makedirs(CACHE, exist_ok=True)
    json.dump(cache, open(os.path.join(CACHE, slug + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def render(pdf, page):
    """One page as a grayscale JPEG, long edge LONG_EDGE."""
    with tempfile.TemporaryDirectory(prefix="vocr_") as tmp:
        subprocess.run(["pdftoppm", "-gray", "-jpeg", "-jpegopt", "quality=90", "-scale-to", str(LONG_EDGE),
                        "-f", str(page), "-l", str(page), pdf, os.path.join(tmp, "pg")], check=True, capture_output=True)
        out = [f for f in os.listdir(tmp) if f.endswith(".jpg")]
        return open(os.path.join(tmp, out[0]), "rb").read()


def params(pdf, page, n):
    img = base64.standard_b64encode(render(pdf, page)).decode()
    return {"model": MODEL, "max_tokens": 8000, "thinking": {"type": "disabled"}, "system": SYSTEM,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img}},
                {"type": "text", "text": f"Page {page} of {n}. Transcribe it."}]}]}


def result_entry(msg):
    """Cache entry for one response, or None with a reason when it can't be used."""
    usage = {k: getattr(msg.usage, k, 0) or 0 for k in ("input_tokens", "output_tokens")}
    if msg.stop_reason != "end_turn":
        return None, f"stop_reason {msg.stop_reason}"
    return {"raw": "".join(b.text for b in msg.content if b.type == "text"), "usage": usage}, None


AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "۰۱۲۳۴۵۶۷۸۹")

def clean(raw):
    """Corpus form of a page. Applied when writing, so changes here never need a new reading."""
    s = normalize_fa(raw).translate(AR_DIGITS)
    s = re.sub(r"(?m)^#+ +", "", s.replace("**", ""))   # markdown the model sometimes adds to headings
    s = re.sub(r"(?<=\S) ـ+ (?=\S)", " - ", s)        # a spaced tatweel is a dash; repair() would join the words
    lines = s.split("\n")
    while lines and re.fullmatch(r"[\s۰-۹\d\-–—.()]*", lines[-1]): lines.pop()   # page number left in
    while lines and re.fullmatch(r"[\s۰-۹\d\-–—.()]*", lines[0]): lines.pop(0)
    return "\n".join(lines)


def cmd_test(uid, pages):
    slug, pdf = doc_for(uid)
    sha, n, cache, c = pdf_hash(pdf), page_count(pdf), load_cache(slug), client()
    for p in pages:
        key = page_key(sha, p)
        if key in cache["pages"]:
            print(f"--- page {p} (cached)"); print(clean(cache["pages"][key]["raw"])); continue
        msg = c.messages.create(**params(pdf, p, n))
        entry, why = result_entry(msg)
        if not entry:
            print(f"--- page {p}: {why}"); continue
        cache["pages"][key] = entry | {"page": p}
        save_cache(slug, cache)
        print(f"--- page {p}  {entry['usage']}"); print(clean(entry["raw"]))


def cmd_submit(uids):
    c, reqs = client(), []
    for uid in uids:
        slug, pdf = doc_for(uid)
        sha, n, cache = pdf_hash(pdf), page_count(pdf), load_cache(slug)
        todo = [p for p in range(1, n + 1) if page_key(sha, p) not in cache["pages"]]
        print(f"{uid}: {len(todo)} of {n} pages to read")
        reqs += [(uid, pdf, p, n) for p in todo]
    jobs = json.load(open(JOBS)) if os.path.exists(JOBS) else []
    for i in range(0, len(reqs), MAX_BATCH):
        chunk = reqs[i:i + MAX_BATCH]
        batch = c.messages.batches.create(requests=[{"custom_id": f"{uid}--p{p}", "params": params(pdf, p, n)}
                                                    for uid, pdf, p, n in chunk])
        jobs.append({"batch": batch.id, "pages": {f"{uid}--p{p}": [uid, p] for uid, _, p, _ in chunk}, "collected": False})
        print(f"batch {batch.id}: {len(chunk)} pages")
    os.makedirs(CACHE, exist_ok=True)
    json.dump(jobs, open(JOBS, "w"), indent=1)


def cmd_collect():
    if not os.path.exists(JOBS): sys.exit("no jobs")
    jobs, c, done = json.load(open(JOBS)), client(), set()
    for job in [j for j in jobs if not j["collected"]]:
        b = c.messages.batches.retrieve(job["batch"])
        if b.processing_status != "ended":
            print(f"batch {job['batch']}: {b.processing_status} ({b.request_counts.processing} processing)"); continue
        caches, failed = {}, []
        for r in c.messages.batches.results(job["batch"]):
            uid, p = job["pages"][r.custom_id]
            slug, pdf = doc_for(uid)
            if slug not in caches: caches[slug] = (load_cache(slug), pdf_hash(pdf))
            entry, why = (result_entry(r.result.message) if r.result.type == "succeeded" else (None, r.result.type))
            if not entry:
                failed.append(f"{uid} p{p}: {why}"); continue
            cache, sha = caches[slug]
            cache["pages"][page_key(sha, p)] = entry | {"page": p}
            done.add(uid)
        for slug, (cache, _) in caches.items(): save_cache(slug, cache)
        job["collected"] = True
        print(f"batch {job['batch']}: collected, {len(failed)} failed" + "".join(f"\n    {f}" for f in failed))
    json.dump(jobs, open(JOBS, "w"), indent=1)
    if done: cmd_write(sorted(done))
    if all(j["collected"] for j in jobs): print("all batches collected")


def cmd_write(uids):
    """Replace data/text pages with cached readings, for documents read in full."""
    for uid in uids:
        slug, pdf = doc_for(uid)
        sha, n, cache = pdf_hash(pdf), page_count(pdf), load_cache(slug)
        got = {p: cache["pages"].get(page_key(sha, p)) for p in range(1, n + 1)}
        missing = [p for p, e in got.items() if e is None]
        if missing:
            print(f"{uid}: not written, pages missing {missing}"); continue
        path = os.path.join(DATA, "text", slug + ".json")
        doc = json.load(open(path, encoding="utf-8"))
        doc["pages"] = [{"page": p, "text": clean(got[p]["raw"])} for p in range(1, n + 1)]
        doc["source"] = "vision"; doc["vision_model"] = MODEL
        json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        use = [e["usage"] for e in got.values()]
        print(f"{uid}: wrote {n} pages, {sum(len(clean(e['raw'])) for e in got.values()):,} chars "
              f"(in {sum(u['input_tokens'] for u in use):,} / out {sum(u['output_tokens'] for u in use):,} tokens)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "test" and len(a) >= 3: cmd_test(a[1], [int(x) for x in a[2:]])
    elif a[0] == "submit" and len(a) >= 2: cmd_submit(a[1:])
    elif a[0] == "collect": cmd_collect()
    elif a[0] == "write" and len(a) >= 2: cmd_write(a[1:])
    else: sys.exit(__doc__)

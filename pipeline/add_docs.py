#!/usr/bin/env python3
"""Add documents that no Atlas organisation links to: drafts by individuals and groups outside Atlas.

    add_docs.py <spec.json> [uid ...]

The spec (data/additions/*.json) holds one object per document: its registry fields, plus `file` (the corpus
file name) and optionally `fetch_url` (where to download it, when that differs from `source_url`) and
`drop_lines` (a regex; matching lines of a web page are left out, e.g. "read more" links). A PDF is copied into
the corpus as it is; a web page becomes a reading-copy PDF whose corpus text comes from the HTML, cut at the
copy's page breaks (as in harvest.py). Downloads stay in local/additions/ (gitignored). Afterwards run
extract.py; a PDF with a broken text layer goes through vision_ocr.py.
"""
import datetime, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harvest import ROOT, CORPUS, TEXT, REGISTRY, fetch_one, html_text, reading_copy, paged_text, save
from extract import slug_of

STORE = os.path.join(ROOT, "local", "additions")
SPEC_ONLY = {"file", "fetch_url", "drop_lines"}
ORDER = ["uid", "collection", "status", "source", "legacy_slug", "fa", "en", "author_fa", "author_en", "year", "era",
         "type", "kind", "org_ids", "pages", "doc_status", "source_url", "version", "tags"]


def add(spec):
    uid, url = spec["uid"], spec.get("fetch_url") or spec["source_url"]
    os.makedirs(STORE, exist_ok=True)
    meta_path = os.path.join(STORE, uid + ".json")
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else None
    if not meta or meta.get("url") != url:
        final, status, ctype, body = fetch_one(url)
        is_pdf = ctype == "application/pdf" or body[:5] == b"%PDF-"
        raw = uid + (".pdf" if is_pdf else ".html")
        open(os.path.join(STORE, raw), "wb").write(body)
        meta = {"url": url, "final_url": final, "status": status, "content_type": ctype, "raw": raw,
                "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        save(meta_path, meta)
    raw = os.path.join(STORE, meta["raw"])
    dest = os.path.join(CORPUS, spec["file"])
    slug = slug_of(spec["file"])
    if raw.endswith(".pdf"):
        if not os.path.exists(dest): subprocess.run(["cp", raw, dest], check=True)
        print(f"{uid}: pdf -> {spec['file']}")
    else:
        text, title, h1 = html_text(raw)
        if spec.get("drop_lines"):
            text = "\n".join(l for l in text.split("\n") if not re.fullmatch(spec["drop_lines"], l.strip()))
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if not reading_copy(text, spec["fa"], meta, dest): sys.exit(f"{uid}: reading copy failed")
        pages = paged_text(text, dest)
        save(os.path.join(TEXT, slug + ".json"),
             {"source_pdf": spec["file"], "source": "html", "source_url": spec["source_url"], "pages": pages})
        print(f"{uid}: html -> {spec['file']}, {len(pages)} pages, {len(text):,} chars")
    entry = {"collection": "iran-drafts", "status": "active", "source": spec["file"], "legacy_slug": slug,
             "org_ids": [], "pages": None, "doc_status": "draft"}
    entry |= {k: v for k, v in spec.items() if k not in SPEC_ONLY}
    return {k: entry[k] for k in ORDER if k in entry} | {k: v for k, v in entry.items() if k not in ORDER}


def main(path, only):
    specs = [s for s in json.load(open(path, encoding="utf-8")) if not only or s["uid"] in only]
    reg = json.load(open(REGISTRY, encoding="utf-8"))
    at = {e["uid"]: i for i, e in enumerate(reg)}
    slugs = {e["legacy_slug"]: e["uid"] for e in reg}
    for s in specs:
        other = slugs.get(slug_of(s["file"]))
        if other and other != s["uid"]: sys.exit(f"{s['uid']}: file slug already used by {other}")
        entry = add(s)
        if entry["uid"] in at: reg[at[entry["uid"]]] = entry
        else: at[entry["uid"]] = len(reg); reg.append(entry)
    open(REGISTRY, "w", encoding="utf-8").write(json.dumps(reg, ensure_ascii=False, indent=1) + "\n")
    print(f"\n{len(reg)} registry entries")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    main(a[0], set(a[1:]))

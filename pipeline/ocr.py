#!/usr/bin/env python3
"""OCR the scanned + legacy-font PDFs back into clean Persian text.

    ocr.py              # every document whose text fails the letter check
    ocr.py <uid> ...    # these documents, regardless of the check
"""
import json, glob, os, re, subprocess, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "(پیشنهادهای پیش‌نویس) قانون اساسی")
TEXT = os.path.join(ROOT, "data/text")
os.environ["TESSDATA_PREFIX"] = os.path.join(ROOT, "pipeline/tessdata")
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
from extract import normalize_fa, page_count

# Persian letters/digits, plus plain Latin letters (bilingual documents);
# legacy-font garbage comes out as Latin-1 symbols and still fails
OK = re.compile(r'[ء-غف-يٰ-ۓ۰-۹A-Za-z]')

def needs_ocr(path):
    doc = json.load(open(path, encoding="utf-8"))
    if doc.get("source") == "ocr": return False
    # tatweel-justified text is good text; don't count the stretch marks
    nz = "".join("".join(p["text"] for p in doc["pages"]).split()).replace("\u0640", "")
    if len(nz) < 500: return True
    return len(OK.findall(nz)) / len(nz) < 0.55

# Named documents (registry uid or text slug) are OCR'd regardless of the check:
# a legacy font with a wrong glyph map yields valid Persian letters in the wrong
# places, which the letter check cannot see.
force = sys.argv[1:]
if force:
    reg = {d["uid"]: d["legacy_slug"] for d in json.load(open(os.path.join(ROOT, "data/registry.json"), encoding="utf-8"))}
    targets = [os.path.join(TEXT, reg.get(a, a) + ".json") for a in force]
    missing = [t for t in targets if not os.path.exists(t)]
    if missing: sys.exit(f"no text for: {missing}")
else:
    targets = [p for p in sorted(glob.glob(os.path.join(TEXT, "*.json"))) if needs_ocr(p)]
print(f"{len(targets)} documents need OCR", flush=True)

for jp in targets:
    doc = json.load(open(jp, encoding="utf-8"))
    pdf = os.path.join(SRC, doc["source_pdf"])
    n = page_count(pdf)
    print(f"\n>>> {doc['source_pdf'][:56]}  ({n} pages)", flush=True)
    tmp = tempfile.mkdtemp(prefix="ocr_")
    pages = []
    try:
        for p in range(1, n + 1):
            subprocess.run(['pdftoppm','-r','300','-f',str(p),'-l',str(p),'-png',pdf,
                            os.path.join(tmp,'pg')], check=True, capture_output=True)
            img = glob.glob(os.path.join(tmp, 'pg*.png'))
            if not img:
                pages.append({"page": p, "text": ""}); continue
            r = subprocess.run(['tesseract', img[0], '-', '-l', 'fas', '--psm', '3'],
                               capture_output=True, text=True)
            pages.append({"page": p, "text": normalize_fa(r.stdout)})
            os.remove(img[0])
            if p % 10 == 0 or p == n:
                print(f"    {p}/{n} pages", flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    doc["pages"] = pages; doc["source"] = "ocr"
    json.dump(doc, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    got = sum(len(x["text"]) for x in pages)
    print(f"    DONE {got:,} chars", flush=True)

print("\nOCR COMPLETE", flush=True)

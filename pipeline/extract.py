#!/usr/bin/env python3
"""Extract + normalize Persian constitution PDFs into per-page JSON."""
import unicodedata, re, subprocess, json, sys, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "(پیشنهادهای پیش‌نویس) قانون اساسی")
OUT = os.path.join(ROOT, "data", "text")

FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def normalize_fa(s: str) -> str:
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[‎‏‪-‮⁦-⁩]', '', s)
    s = s.replace('ي', 'ی').replace('ى', 'ی')
    s = s.replace('ك', 'ک')
    s = re.sub(r'[ً-ْٰ]', '', s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

def page_count(path):
    r = subprocess.run(['pdfinfo', path], capture_output=True, text=True)
    m = re.search(r'^Pages:\s+(\d+)', r.stdout, re.M)
    return int(m.group(1)) if m else 0

def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC, "*.pdf")))
    manifest = []
    force = "--force" in sys.argv
    for path in files:
        base = os.path.basename(path)
        slug = re.sub(r'[^\w؀-ۿ]+', '_', base[:-4]).strip('_')[:80]
        dest = os.path.join(OUT, slug + ".json")
        if not force and os.path.exists(dest):
            prev = json.load(open(dest, encoding="utf-8"))
            if prev.get("source") in ("ocr", "vision"):   # keep OCR output; --force to redo
                chars = sum(len(pg["text"]) for pg in prev["pages"])
                manifest.append({"slug": slug, "source_pdf": base, "pages": len(prev["pages"]),
                                 "chars": chars, "needs_ocr": False})
                print(f"ocr  {len(prev['pages']):>4}p {chars:>8}c  {base[:58]}")
                continue
        n = page_count(path)
        pages = []
        for p in range(1, n + 1):
            r = subprocess.run(['pdftotext', '-q', '-f', str(p), '-l', str(p), path, '-'],
                               capture_output=True, text=True)
            pages.append({"page": p, "text": normalize_fa(r.stdout)})
        chars = sum(len(pg["text"]) for pg in pages)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump({"source_pdf": base, "pages": pages}, f, ensure_ascii=False, indent=1)
        manifest.append({"slug": slug, "source_pdf": base, "pages": n, "chars": chars,
                         "needs_ocr": chars < 500})
        print(f"{'OCR!' if chars < 500 else 'ok  '} {n:>4}p {chars:>8}c  {base[:58]}")
    with open(os.path.join(ROOT, "data", "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"\n{len(manifest)} docs, {sum(m['pages'] for m in manifest)} pages, "
          f"{sum(m['chars'] for m in manifest):,} chars, {sum(m['needs_ocr'] for m in manifest)} need OCR")

if __name__ == "__main__":
    main()

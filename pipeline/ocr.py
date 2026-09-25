#!/usr/bin/env python3
"""OCR the scanned + legacy-font PDFs back into clean Persian text.

    ocr.py              # every document whose text fails the letter check
    ocr.py <uid> ...    # these documents, regardless of the check
    ocr.py --lines <uid> ...

--lines cuts each page into text lines at the blank rows and reads every line
on its own (Tesseract --psm 13). Use it for clean single-column typeset pages
where page-level OCR skips whole lines (naoruz: "Microsoft Print to PDF" output).
It then restores a final «ی» the font's glyph hides from Tesseract («زندگ» ->
«زندگی») where the corpus knows the longer word and not the shorter one.
"""
import json, glob, os, re, subprocess, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "(پیشنهادهای پیش‌نویس) قانون اساسی")
TEXT = os.path.join(ROOT, "data/text")
os.environ["TESSDATA_PREFIX"] = os.path.join(ROOT, "pipeline/tessdata")
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
from extract import normalize_fa, page_count
from collections import Counter

# Persian letters/digits, plus plain Latin letters (bilingual documents);
# legacy-font garbage comes out as Latin-1 symbols and still fails
OK = re.compile(r'[ء-غف-يٰ-ۓ۰-۹A-Za-z]')

def needs_ocr(path):
    doc = json.load(open(path, encoding="utf-8"))
    if doc.get("source") in ("ocr", "vision"): return False
    # tatweel-justified text is good text; don't count the stretch marks
    nz = "".join("".join(p["text"] for p in doc["pages"]).split()).replace("\u0640", "")
    if len(nz) < 500: return True
    return len(OK.findall(nz)) / len(nz) < 0.55

# Named documents (registry uid or text slug) are OCR'd regardless of the check:
# a legacy font with a wrong glyph map yields valid Persian letters in the wrong
# places, which the letter check cannot see.
LINES = "--lines" in sys.argv
force = [a for a in sys.argv[1:] if a != "--lines"]
if force:
    reg = {d["uid"]: d["legacy_slug"] for d in json.load(open(os.path.join(ROOT, "data/registry.json"), encoding="utf-8"))}
    targets = [os.path.join(TEXT, reg.get(a, a) + ".json") for a in force]
    missing = [t for t in targets if not os.path.exists(t)]
    if missing: sys.exit(f"no text for: {missing}")
else:
    targets = [p for p in sorted(glob.glob(os.path.join(TEXT, "*.json"))) if needs_ocr(p)]
print(f"{len(targets)} documents need OCR", flush=True)

DARK = bytes(1 if i < 160 else 0 for i in range(256))

def read_pgm(path):
    b = open(path, "rb").read()
    m = re.match(rb"P5\s+(\d+)\s+(\d+)\s+\d+\s", b)
    return int(m[1]), int(m[2]), b[m.end():]

def line_bands(w, h, px):
    """Row ranges holding one text line each."""
    ink = [px[y * w:(y + 1) * w].translate(DARK).count(1) for y in range(h)]
    bands, y = [], 0
    while y < h:
        if ink[y] >= 2:
            s = y
            while y < h and ink[y] >= 2: y += 1
            if bands and s - bands[-1][1] < 4: bands[-1][1] = y     # dots below/above the line
            else: bands.append([s, y])
        y += 1
    bands = [b for b in bands if b[1] - b[0] >= 12]
    hs = sorted(b[1] - b[0] for b in bands)
    med = hs[len(hs) // 2] if hs else 0
    out = []
    for a, b in bands:          # two tightly set lines: split at the thinnest row
        while med and b - a > 1.6 * med:
            cut = min(range(a + int(med * .6), b - int(med * .6)), key=lambda y: ink[y])
            out.append([a, cut]); a = cut
        out.append([a, b])
    return out

def ocr_lines(png, tmp):
    w, h, px = read_pgm(png)
    lines, pad = [], 10
    for i, (a, b) in enumerate(line_bands(w, h, px)):
        cols = [x for x in range(w) if any(px[y * w + x] < 160 for y in range(a, b, 2))]
        x0, x1 = max(0, cols[0] - pad), min(w, cols[-1] + pad + 1)
        a2, b2 = max(0, a - pad), min(h, b + pad)
        lp = os.path.join(tmp, f"line{i}.pgm")
        with open(lp, "wb") as f:
            f.write(b"P5 %d %d 255\n" % (x1 - x0, b2 - a2))
            f.write(b"".join(px[y * w + x0:y * w + x1] for y in range(a2, b2)))
        r = subprocess.run(["tesseract", lp, "-", "-l", "fas", "--psm", "13"], capture_output=True, text=True)
        lines.append(r.stdout.strip())
        os.remove(lp)
    return "\n".join(l for l in lines if l)

WORD = re.compile(r"[آ-ی]+")

def corpus_vocab(skip):
    c = Counter()
    for p in glob.glob(os.path.join(TEXT, "*.json")):
        if os.path.abspath(p) in skip: continue
        for pg in json.load(open(p, encoding="utf-8"))["pages"]:
            c.update(WORD.findall(pg["text"]))
    return c

def restore_final_ye(text, vocab):
    def fix(m):
        w = m.group(0)
        return w + "ی" if len(w) > 1 and vocab[w] == 0 and vocab[w + "ی"] >= 3 else w
    return WORD.sub(fix, text)

def fix_commas(text):
    """Tesseract reads the Persian comma as a closing guillemet: «قانون»» for «قانون،»."""
    out = []
    for line in text.split("\n"):
        chars, depth = [], 0
        for ch in line:
            if ch == "«": depth += 1
            elif ch == "»":
                if depth: depth -= 1
                else: ch = "،"
            chars.append(ch)
        out.append("".join(chars))
    return "\n".join(out)

vocab = corpus_vocab({os.path.abspath(t) for t in targets}) if LINES else None

for jp in targets:
    doc = json.load(open(jp, encoding="utf-8"))
    pdf = os.path.join(SRC, doc["source_pdf"])
    n = page_count(pdf)
    print(f"\n>>> {doc['source_pdf'][:56]}  ({n} pages)", flush=True)
    tmp = tempfile.mkdtemp(prefix="ocr_")
    pages = []
    try:
        for p in range(1, n + 1):
            subprocess.run(['pdftoppm','-r','300','-f',str(p),'-l',str(p)] +
                           (['-gray'] if LINES else ['-png']) + [pdf, os.path.join(tmp,'pg')],
                           check=True, capture_output=True)
            img = glob.glob(os.path.join(tmp, 'pg*.p*m')) + glob.glob(os.path.join(tmp, 'pg*.png'))
            if not img:
                pages.append({"page": p, "text": ""}); continue
            text = ""
            if LINES:
                text = fix_commas(restore_final_ye(normalize_fa(ocr_lines(img[0], tmp)), vocab))
            if not text.strip():
                # page mode; also the fallback for pages with no clean text lines (e.g. a designed cover)
                text = normalize_fa(subprocess.run(['tesseract', img[0], '-', '-l', 'fas', '--psm', '3'],
                                                   capture_output=True, text=True).stdout)
            pages.append({"page": p, "text": text})
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

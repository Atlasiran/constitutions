#!/usr/bin/env python3
"""Put a copy of each source PDF in site/pdf/, so the site can link documents and articles to their pages.

    .venv/bin/python pipeline/publish_pdfs.py      # then build_site.py

Each file is named after its documents' uids (documents split from one PDF share the parts their uids have
in common: dp-bylaws-2026, dp-charter-2026 -> dp-2026.pdf). Images are downsampled to 150 dpi and the file
rewritten; where that does not make it smaller, the original is copied as it is. Page numbers never change,
so the page an article cites is the page the link opens. Needs PyMuPDF; build_site.py only reads the names.
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "(پیشنهادهای پیش‌نویس) قانون اساسی")
OUT = os.path.join(ROOT, "site", "pdf")


def pdf_names(catalog):
    """source_pdf -> published file name."""
    uids = {}
    for d in catalog:
        uids.setdefault(d["source_pdf"], []).append(d["uid"].split("-"))
    names = {}
    for src, parts in uids.items():
        if len(parts) == 1:
            names[src] = "-".join(parts[0]) + ".pdf"
        else:   # the tokens every uid shares, in the first uid's order
            names[src] = "-".join(t for t in parts[0] if all(t in p for p in parts[1:])) + ".pdf"
    assert len(set(names.values())) == len(names), "two source PDFs would get the same name"
    return names


def main():
    import pymupdf
    pymupdf.TOOLS.mupdf_display_errors(False)
    catalog = json.load(open(os.path.join(ROOT, "data", "catalog.json"), encoding="utf-8"))
    names = pdf_names(catalog)
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".pdf") and f not in names.values():
            os.remove(os.path.join(OUT, f))
    before = after = 0
    for src, name in sorted(names.items(), key=lambda x: x[1]):
        inp, out = os.path.join(SRC, src), os.path.join(OUT, name)
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(inp):
            before += os.path.getsize(inp); after += os.path.getsize(out)
            continue
        doc = pymupdf.open(inp)
        doc.rewrite_images(dpi_threshold=160, dpi_target=150, quality=70)
        doc.save(out, garbage=4, deflate=True, deflate_fonts=True, clean=True)
        doc.close()
        if os.path.getsize(out) >= os.path.getsize(inp):
            shutil.copyfile(inp, out)
        a, b = os.path.getsize(inp), os.path.getsize(out)
        before += a; after += b
        print(f"  {name:<40} {a / 1e6:6.2f} -> {b / 1e6:6.2f} MB")
    print(f"\n{len(names)} PDFs -> site/pdf/  ({before / 1e6:.1f} -> {after / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()

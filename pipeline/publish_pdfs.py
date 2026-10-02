#!/usr/bin/env python3
"""Put a copy of each source PDF in site/pdf/, so the site can link documents and articles to their pages.

    .venv/bin/python pipeline/publish_pdfs.py      # then build_site.py

Each file is named after its documents' uids (documents split from one PDF share the parts their uids have
in common: dp-bylaws-2026, dp-charter-2026 -> dp-2026.pdf). Images are downsampled to 150 dpi and the file
rewritten; where that does not make it smaller, or changes how any page looks (some image encodings come
out black), the original is copied as it is. Page numbers never change, so the page an article cites is the
page the link opens. Where a file's documents use less than half of its pages (a draft printed inside a book),
the other pages are published blank, at their size, with a line pointing to the full source. Needs PyMuPDF;
build_site.py only reads the names.
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


def looks_same(a, b, tol=15, pages=None):
    """Every page of b (or these 0-based pages) renders like the same page of a: mean grey within tol (0-255) at a
    coarse resolution."""
    import pymupdf
    da, db = pymupdf.open(a), pymupdf.open(b)
    if da.page_count != db.page_count:
        return False
    grey = lambda d, p: (lambda s: sum(s) / len(s))(d[p].get_pixmap(dpi=30, colorspace=pymupdf.csGRAY).samples)
    return all(abs(grey(da, p) - grey(db, p)) <= tol for p in (range(da.page_count) if pages is None else pages))


def used_pages(catalog, src, n):
    """The 0-based pages of src that its documents use, or None when they use at least half of it."""
    docs = [d for d in catalog if d["source_pdf"] == src]
    if any(not d.get("pages") for d in docs): return None
    used = {p - 1 for d in docs for p in range(d["pages"][0], d["pages"][1] + 1) if 0 < p <= n}
    return used if len(used) < n / 2 else None


def blank_others(doc, used, url):
    """The same file with every page outside `used` replaced by an empty page of its size and a pointer."""
    import pymupdf
    out = pymupdf.open()
    for i, page in enumerate(doc):
        if i in used:
            out.insert_pdf(doc, from_page=i, to_page=i)
        else:
            r = page.rect; blank = out.new_page(width=r.width, height=r.height)
            blank.insert_text((36, r.height / 2), f"Page {i + 1} is not part of this document and is left out here.",
                              fontsize=10, color=(.45, .45, .45))
            if url: blank.insert_text((36, r.height / 2 + 16), "Full source: " + url[:110], fontsize=8, color=(.45, .45, .45))
    return out


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
        used = used_pages(catalog, src, doc.page_count)
        if used:
            url = next((d.get("source_url") for d in catalog if d["source_pdf"] == src and d.get("source_url")), None)
            full, doc = doc, blank_others(doc, used, url)
        doc.rewrite_images(dpi_threshold=160, dpi_target=150, quality=70)
        doc.save(out, garbage=4, deflate=True, deflate_fonts=True, clean=True)
        doc.close()
        if not used and (os.path.getsize(out) >= os.path.getsize(inp) or not looks_same(inp, out)):
            shutil.copyfile(inp, out)
        elif used and not looks_same(inp, out, pages=sorted(used)):
            # the image rewrite changed how a page looks: keep the used pages as they are, blank the rest
            blank_others(full, used, url).save(out, garbage=4, deflate=True)
        a, b = os.path.getsize(inp), os.path.getsize(out)
        before += a; after += b
        print(f"  {name:<40} {a / 1e6:6.2f} -> {b / 1e6:6.2f} MB")
    print(f"\n{len(names)} PDFs -> site/pdf/  ({before / 1e6:.1f} -> {after / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()

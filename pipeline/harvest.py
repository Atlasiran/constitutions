#!/usr/bin/env python3
"""Collect the documents Atlas organisations link to (their `manifest` / `coc` fields) for review.

    harvest.py list <atlas data.json>   # write data/harvest/candidates.json from Atlas's org data
    harvest.py fetch <org id> ...        # download each link; a web page also gets a PDF reading copy
    harvest.py copy <org id> ...         # (re)make the reading copies of saved web pages
    harvest.py report [<org id> ...]     # extract text, guess the document kind, write data/harvest/review.json

Nothing enters the corpus here. review.json lists what was found per link, with a guessed `kind`
and `decision: "pending"`; a person sets the decision (and corrects kind / pages) before a document
is added to data/registry.json. A web page's corpus text is its main text taken from the HTML (the
reading copy's own text layer breaks «لا»); the reading copy is the PDF people open. Downloads stay in local/harvest/<org id>/ (gitignored)
until then. Requests carry a generic User-Agent, never anyone's personal contact details.
"""
import datetime, hashlib, time, html.parser, json, os, re, subprocess, sys, tempfile, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "harvest")
STORE = os.path.join(ROOT, "local", "harvest")
UA = "AtlasIran-constitutions/1.0 (+https://atlasiran.org)"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
from extract import normalize_fa

# Guessed from the document's title and opening; a reviewer confirms. Order matters: the first match wins.
KIND_WORDS = [
    ("bylaws",  r"اساسنامه|اساسنامە|آیین\s*نامه|نظام\s*نامه|statute|by-?laws?|constitution of the (party|organi[sz]ation)"),
    ("ideology", r"مرام\s*نامه|مرامنامە"),
    ("charter", r"منشور|میثاق|تفاهم\s*نامه|manifesto|مانیفست|charter"),
    ("program", r"برنامه|برنامە|platform|program"),
]


def candidates_path():
    return os.path.join(DATA, "candidates.json")


def load(path, default):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else default


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def cmd_list(atlas_json):
    out = []
    for e in json.load(open(atlas_json, encoding="utf-8")):
        for field in ("manifest", "coc"):
            urls = [u for u in re.split(r"\s+", (e.get(field) or "").strip()) if u.startswith("http")]
            for u in urls:
                out.append({"org_id": e["id"], "name_fa": e.get("name_fa", ""), "org_type": e.get("org_type", ""),
                            "field": field, "url": u})
    save(candidates_path(), out)
    print(f"{len(out)} links from {len({c['org_id'] for c in out})} organisations -> {candidates_path()}")


def fetch_one(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fa,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.geturl(), r.status, r.headers.get_content_type(), r.read()


def print_pdf(page, dest):
    """Print an HTML string to PDF with headless Chrome and no network (every host resolves to nothing)."""
    with tempfile.TemporaryDirectory(prefix="harvest_") as tmp:
        src = os.path.join(tmp, "page.html")
        open(src, "w", encoding="utf-8").write(page)
        # Chrome writes the PDF within seconds but may not exit afterwards: wait for the file to stop growing
        proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={tmp}/profile",
                                 "--host-resolver-rules=MAP * ~NOTFOUND", "--no-pdf-header-footer",
                                 "--virtual-time-budget=5000", f"--print-to-pdf={dest}", "file://" + src],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        size, deadline = -1, time.time() + 60
        while time.time() < deadline and proc.poll() is None:
            time.sleep(1)
            now = os.path.getsize(dest) if os.path.exists(dest) else -1
            if now > 0 and now == size: break
            size = now
        proc.kill(); proc.wait()
    return os.path.exists(dest) and os.path.getsize(dest) > 0


COPY_CSS = """@page { size: A4; margin: 18mm 20mm; }
body { font-family: "Geeza Pro", Tahoma, sans-serif; font-size: 12pt; line-height: 1.9; color: #111; }
h1 { font-size: 16pt; margin: 0 0 4mm; }
.src { direction: ltr; text-align: left; font: 8.5pt/1.4 Helvetica, Arial, sans-serif; color: #555;
       border-bottom: 0.5pt solid #bbb; padding-bottom: 3mm; margin-bottom: 6mm; word-break: break-all; }
p { margin: 0 0 3mm; }"""


def reading_copy(text, title, meta, dest):
    """A clean PDF of a web page's main text: the page's words only, with where and when they were taken."""
    esc = lambda t: t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    paras = "".join(f"<p>{esc(p).replace(chr(10), '<br>')}</p>" for p in re.split(r"\n\s*\n", text) if p.strip())
    src = (f"Source: {esc(urllib.parse.unquote(meta['final_url']))}<br>Retrieved {meta['fetched_at'][:10]} "
           f"(UTC) · reading copy made for the AtlasIran constitutions corpus from the page's main text")
    page = (f'<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{COPY_CSS}</style></head><body><h1>{esc(title)}</h1><div class=\"src\">{src}</div>{paras}</body></html>")
    return print_pdf(page, dest)


def cmd_copy(ids):
    """(Re)make the reading copies of these organisations' saved web pages."""
    for org in ids:
        d = os.path.join(STORE, org)
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not f.endswith(".json"): continue
            meta = load(os.path.join(d, f), {})
            if not meta.get("raw", "").endswith(".html"): continue
            text, title, h1 = html_text(os.path.join(d, meta["raw"]))
            dest = os.path.join(d, f[:-5] + ".copy.pdf")
            meta["copy"] = os.path.basename(dest) if reading_copy(text, h1 or title, meta, dest) else None
            meta.pop("snapshot", None)
            save(os.path.join(d, f), meta)
            print(f"{org:>4} {'ok ' if meta['copy'] else 'FAILED'} {meta['url'][:80]}")


def cmd_fetch(ids):
    cands = [c for c in load(candidates_path(), []) if c["org_id"] in ids]
    if not cands: sys.exit("no candidates for these ids (run `list` first)")
    for c in cands:
        d = os.path.join(STORE, c["org_id"]); os.makedirs(d, exist_ok=True)
        key = hashlib.sha256(c["url"].encode()).hexdigest()[:10]
        meta_path = os.path.join(d, key + ".json")
        if os.path.exists(meta_path):
            print(f"{c['org_id']:>4} cached  {c['url'][:80]}"); continue
        meta = {**c, "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
        try:
            final, status, ctype, body = fetch_one(c["url"])
        except Exception as ex:
            meta |= {"error": f"{type(ex).__name__}: {ex}"[:300]}
            save(meta_path, meta); print(f"{c['org_id']:>4} ERROR   {meta['error'][:80]}"); continue
        is_pdf = ctype == "application/pdf" or body[:5] == b"%PDF-"
        raw = os.path.join(d, key + (".pdf" if is_pdf else ".html"))
        open(raw, "wb").write(body)
        meta |= {"final_url": final, "status": status, "content_type": ctype, "sha256": hashlib.sha256(body).hexdigest(),
                 "raw": os.path.basename(raw)}
        save(meta_path, meta)
        if not is_pdf: cmd_copy([c["org_id"]])
        print(f"{c['org_id']:>4} {'pdf ' if is_pdf else 'html'}    {len(body):>9,} B  {c['url'][:70]}")


class _Tree(html.parser.HTMLParser):
    """A minimal element tree of a page, without scripts, styles, navigation, headers, footers or forms."""
    SKIP = {"script", "style", "noscript", "nav", "header", "footer", "form", "aside", "svg", "button", "select",
            "iframe", "template"}
    VOID = {"br", "img", "hr", "meta", "link", "input", "source", "wbr", "col", "area", "base", "embed", "track"}
    BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "article", "blockquote",
             "ul", "ol", "table", "main", "td", "th", "dd", "dt", "pre"}
    PARA = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "td", "pre", "dd"}

    def __init__(self):
        super().__init__()
        self.root = {"tag": "root", "kids": [], "parent": None}
        self.cur, self.skip, self.title, self._title = self.root, 0, "", False

    def handle_starttag(self, tag, attrs):
        if tag == "title": self._title = True
        if self.skip or tag in self.SKIP:
            if tag in self.SKIP and tag not in self.VOID: self.skip += 1
            return
        if tag == "br": self.cur["kids"].append("\n"); return
        if tag in self.VOID: return
        el = {"tag": tag, "kids": [], "parent": self.cur}
        if tag == "ol":   # the browser numbers these items; the numbers are not in the text
            start = dict(attrs).get("start") or "1"
            el["start"] = int(start) if start.isdigit() else 1
        self.cur["kids"].append(el); self.cur = el

    def handle_endtag(self, tag):
        if tag == "title": self._title = False
        if self.skip:
            if tag in self.SKIP: self.skip -= 1
            return
        el = self.cur
        while el is not self.root and el["tag"] != tag: el = el["parent"]   # tolerate unclosed tags
        if el is not self.root: self.cur = el["parent"]

    def handle_data(self, data):
        if self._title: self.title += data
        if not self.skip: self.cur["kids"].append(data)


def _render(el, out):
    n = el.get("start", 1)
    for k in el["kids"]:
        if isinstance(k, str): out.append(k); continue
        block = k["tag"] in _Tree.BLOCK
        if block: out.append("\n")
        if k["tag"] == "li" and el["tag"] == "ol":
            out.append(f"{n}. "); n += 1
        if k["tag"] in ("h1", "h2", "h3", "h4", "h5", "h6"): out.append("\n")
        _render(k, out)
        if block: out.append("\n")


def _para_chars(el, memo):
    """Characters of paragraph-like text under el (cached per element)."""
    key = id(el)
    if key not in memo:
        n = 0
        for k in el["kids"]:
            if isinstance(k, dict):
                n += (len("".join(_render_to(k)).strip()) if k["tag"] in _Tree.PARA else _para_chars(k, memo))
        memo[key] = n
    return memo[key]


def _render_to(el):
    out = []; _render(el, out); return out


def _main(root):
    """The deepest element holding at least 80% of the page's paragraph text: the document, not the site around it."""
    memo = {}; total = _para_chars(root, memo); best = root
    while True:
        kids = [k for k in best["kids"] if isinstance(k, dict) and _para_chars(k, memo) >= 0.8 * total]
        if not kids: return best
        best = kids[0]


def html_text(path):
    """Main text of a saved page, its <title> and first heading."""
    raw = open(path, "rb").read()
    m = re.search(rb'charset=["\']?([\w-]+)', raw[:4000])
    t = _Tree(); t.feed(raw.decode(m.group(1).decode() if m else "utf-8", errors="replace"))
    main = _main(t.root)
    text = normalize_fa("".join(_render_to(main)))
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    h1 = next((normalize_fa("".join(_render_to(e))) for e in _walk(t.root) if e["tag"] == "h1"), "")
    return text, normalize_fa(t.title), h1


def _walk(el):
    for k in el["kids"]:
        if isinstance(k, dict):
            yield k; yield from _walk(k)


def pdf_text(path):
    r = subprocess.run(["pdftotext", "-q", path, "-"], capture_output=True, text=True)
    info = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    pages = int(m.group(1)) if (m := re.search(r"^Pages:\s+(\d+)", info, re.M)) else 0
    title = m.group(1).strip() if (m := re.search(r"^Title:\s+(.*)$", info, re.M)) else ""
    return normalize_fa(r.stdout), title, pages


def guess_kind(*texts):
    for t in texts:
        for kind, pat in KIND_WORDS:
            if t and re.search(pat, t, re.I): return kind
    return None


def script_share(text):
    """Share of letters in Persian/Arabic script, and of those, how many look Arabic- or Kurdish-specific."""
    letters = re.findall(r"[^\W\d_]", text)
    ar = [ch for ch in letters if "؀" <= ch <= "ۿ"]
    return round(len(ar) / max(1, len(letters)), 2), len(re.findall(r"[ەێۆڕڵ]", text)), len(re.findall(r"[ةىإ]", text))


def cmd_report(ids):
    review_path = os.path.join(DATA, "review.json")
    review = {r["key"]: r for r in load(review_path, [])}
    for org in sorted(os.listdir(STORE)) if os.path.isdir(STORE) else []:
        if ids and org not in ids: continue
        for f in sorted(os.listdir(os.path.join(STORE, org))):
            if not f.endswith(".json"): continue
            meta = load(os.path.join(STORE, org, f), {})
            key = f"{org}:{f[:-5]}"
            row = {"key": key, "org_id": org, "name_fa": meta["name_fa"], "field": meta["field"], "url": meta["url"],
                   "fetched_at": meta["fetched_at"]}
            if meta.get("error"):
                row |= {"error": meta["error"], "kind_guess": None}
            else:
                path = os.path.join(STORE, org, meta["raw"])
                if meta["raw"].endswith(".pdf"):
                    text, title, pages = pdf_text(path); h1 = ""
                else:
                    text, title, h1 = html_text(path)
                    pages = pdf_text(os.path.join(STORE, org, meta["copy"]))[2] if meta.get("copy") else 0
                share, ku, ar = script_share(text)
                row |= {"type": "pdf" if meta["raw"].endswith(".pdf") else "html", "title": title[:200], "h1": h1[:200],
                        "pages": pages, "chars": len(text), "fa_script_share": share, "kurdish_letters": ku,
                        "arabic_letters": ar, "kind_guess": guess_kind(h1, title, text[:1500]),
                        "opening": text[:400]}
            old = review.get(key, {})
            row |= {k: old.get(k, v) for k, v in (("decision", "pending"), ("kind", None), ("pages_range", None), ("note", ""))}
            review[key] = row
    rows = sorted(review.values(), key=lambda r: (int(r["org_id"]), r["key"]))
    save(review_path, rows)
    print(f"{'ORG':>4} {'TYPE':<5}{'PAGES':>5}{'CHARS':>8}  {'FA%':>4}  {'GUESS':<9} NAME / TITLE")
    for r in rows:
        if ids and r["org_id"] not in ids: continue
        if r.get("error"):
            print(f"{r['org_id']:>4} ERROR {r['error'][:90]}"); continue
        print(f"{r['org_id']:>4} {r['type']:<5}{r['pages']:>5}{r['chars']:>8}  {r['fa_script_share']:>4}  "
              f"{str(r['kind_guess']):<9} {r['name_fa'][:26]} / {(r['h1'] or r['title'])[:40]}")
    print(f"\n{len(rows)} links in {review_path}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "list" and len(a) == 2: cmd_list(a[1])
    elif a[0] == "fetch" and len(a) >= 2: cmd_fetch(a[1:])
    elif a[0] == "copy" and len(a) >= 2: cmd_copy(a[1:])
    elif a[0] == "report": cmd_report(a[1:])
    else: sys.exit(__doc__)

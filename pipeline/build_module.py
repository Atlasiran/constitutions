#!/usr/bin/env python3
"""Package the site as a module another site can mount (Atlas's «اسناد بنیادین» tab).

    python3 pipeline/build_module.py [--out DIR]     # default: dist/

Copies site/app.js, app.css, atlas-theme.css and site/data/*.json into DIR, and
writes DIR/data/org-index.json: Atlas organisation id -> its documents, with the
comparison group each belongs to and how many other documents share that group
(Atlas shows a compare button only when there is one). Standard library only,
so Atlas's build can run it straight from the submodule.
"""
import json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
# Same groups as GROUP in site/app.js (plan §6): like is compared only with like
GROUP = {"constitution": "A", "constitution_proposal": "A", "bylaws": "B",
         "charter": "C", "program": "C", "ideology": "C", "treatise": "D"}
FILES = ["app.js", "app.css", "atlas-theme.css"]


def org_index(catalog):
    per_group = {}
    for d in catalog:
        per_group.setdefault(GROUP[d["kind"]], []).append(d["uid"])
    index = {}
    for d in catalog:
        for org in d.get("org_ids") or []:
            g = GROUP[d["kind"]]
            index.setdefault(str(org), []).append({
                "uid": d["uid"], "kind": d["kind"], "group": g,
                "fa": d["fa"], "en": d["en"], "year": d.get("year"),
                "doc_status": d.get("doc_status"),
                "comparable": len(per_group[g]) - 1,
            })
    return {k: index[k] for k in sorted(index, key=lambda x: (len(x), x))}


def main():
    aud = os.path.join(SITE, "data", "audits.json")
    if os.path.exists(aud) and any(a.get("preview") for a in json.load(open(aud, encoding="utf-8"))["audits"]):
        sys.exit("site/data/audits.json holds unreviewed audits (build_site.py --preview); rebuild without --preview")
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(ROOT, "dist")
    out = os.path.abspath(out)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "data"))
    for f in FILES:
        shutil.copy2(os.path.join(SITE, f), os.path.join(out, f))
    for f in sorted(os.listdir(os.path.join(SITE, "data"))):
        if f.endswith(".json"):
            shutil.copy2(os.path.join(SITE, "data", f), os.path.join(out, "data", f))
    catalog = json.load(open(os.path.join(SITE, "data", "catalog.json"), encoding="utf-8"))
    idx = org_index(catalog)
    json.dump(idx, open(os.path.join(out, "data", "org-index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out) for f in fs)
    print(f"module -> {out}  ({size / 1e6:.1f} MB, {len(catalog)} documents, {len(idx)} organisations)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Catalog built from data/registry.json — the single source of truth.

Documents are identified by a stable `uid` that survives file renames.
Removing a document means deleting its registry entry (or setting
status != "active") and re-running; nothing else references it positionally.
"""
import json, glob, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = os.path.join(ROOT, "data")

def load_registry():
    return json.load(open(os.path.join(D, "registry.json"), encoding="utf-8"))

def articles_by_source():
    idx = {}
    for p in glob.glob(os.path.join(D, "articles", "*.json")):
        a = json.load(open(p, encoding="utf-8"))
        idx[a["source_pdf"]] = (p, a)
    return idx

# `kind` decides what a document may be compared with (bylaws only with bylaws)
KINDS = {"constitution", "constitution_proposal", "bylaws", "charter", "program",
         "ideology", "treatise", "benchmark"}

def main():
    reg = load_registry()
    bad = [r["uid"] for r in reg if r.get("kind") not in KINDS]
    if bad: raise SystemExit(f"registry entries with missing/unknown kind: {bad}")
    idx = articles_by_source()
    out, missing = [], []
    for r in reg:
        if r.get("status") != "active": continue
        hit = idx.get(r["source"])
        if not hit: missing.append(r["uid"]); continue
        apath, art = hit
        tpath = os.path.join(D, "text", os.path.basename(apath))
        txt = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else {"pages": []}
        meta = {k: v for k, v in r.items() if k not in ("legacy_slug", "source")}
        out.append({**meta, "source_pdf": r["source"], "unit": art["unit"],
                    "n_articles": len(art["articles"]), "n_pages": len(txt["pages"]),
                    "confidence": art.get("seq_score", 0.0),
                    "ocr": txt.get("source") == "ocr"})
    out.sort(key=lambda d: (d.get("year") or 9999, d["uid"]))
    json.dump(out, open(os.path.join(D, "catalog.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"{'YEAR':<6}{'ARTS':>5}  {'UID':<34} TITLE")
    print("-"*92)
    for d in out:
        print(f"{str(d.get('year','?')):<6}{d['n_articles']:>5}  {d['uid']:<34} {d['en'][:32]}")
    inactive = [r["uid"] for r in reg if r.get("status") != "active"]
    print(f"\n{len(out)} active · {len(inactive)} inactive · {sum(d['n_articles'] for d in out)} articles")
    if inactive: print("inactive:", ", ".join(inactive))
    if missing: print("!! registry entries with no extracted articles:", missing)

if __name__ == "__main__": main()

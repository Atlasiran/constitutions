#!/usr/bin/env python3
"""Align the articles of each edition of one draft with the articles of its other editions.

Documents that share a registry `series` and carry a `rev` are editions of one text. For every pair in a series this
writes the article alignment that the site's editions view diffs: a list of rows [i, j, s], where i and j index
the two documents' articles in articles_all.json order (null where an article has no counterpart: added or
dropped) and s is the similarity of the pair. Articles are matched in order (an edition rarely moves an article),
by word overlap, so renumbering and split or merged chapters still line up.

    editions.py        → data/editions.json
"""
import itertools, json, os, re, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from articles import repair

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = os.path.join(ROOT, "data")
MIN_SIM = 0.35        # below this two articles are different provisions, not two wordings of one

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def words(text):
    t = repair(text).translate(DIGITS)
    t = re.sub(r"[ً-ْٰ]", "", t).replace("‌", "")
    return Counter(re.findall(r"\w+", t))


def sim(a, b):
    n = sum(a.values()) + sum(b.values())
    return 2 * sum((a & b).values()) / n if n else 0.0


def align(A, B):
    """Order-preserving alignment that maximises the summed similarity of matched pairs above MIN_SIM."""
    n, m = len(A), len(B)
    S = [[sim(a, b) for b in B] for a in A]
    best = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            v = max(best[i + 1][j], best[i][j + 1])
            if S[i][j] >= MIN_SIM: v = max(v, best[i + 1][j + 1] + S[i][j] - MIN_SIM)
            best[i][j] = v
    rows, i, j = [], 0, 0
    while i < n or j < m:
        if i < n and j < m and S[i][j] >= MIN_SIM and best[i][j] == best[i + 1][j + 1] + S[i][j] - MIN_SIM:
            rows.append([i, j, round(S[i][j], 3)]); i += 1; j += 1
        elif i < n and (j == m or best[i][j] == best[i + 1][j]):
            rows.append([i, None, 0]); i += 1
        else:
            rows.append([None, j, 0]); j += 1
    return rows


def order(d):
    return (d.get("rev") is None, d.get("rev") or 0, d.get("year") or 0, d["uid"])


def main():
    cat = json.load(open(os.path.join(D, "catalog.json"), encoding="utf-8"))
    arts = json.load(open(os.path.join(D, "articles_all.json"), encoding="utf-8"))
    by_doc = {}
    for a in arts: by_doc.setdefault(a["doc"], []).append(words(a["text"]))
    series = {}
    for d in cat:
        if d.get("series") and d["uid"] in by_doc: series.setdefault(d["series"], []).append(d)
    out = {}
    for name, docs in sorted(series.items()):
        # editions have an order (rev); a series without one holds variants (e.g. Saginian's monarchy and republic)
        if len(docs) < 2 or any(d.get("rev") is None for d in docs): continue
        docs.sort(key=order)
        pairs = {}
        for x, y in itertools.combinations(docs, 2):
            rows = align(by_doc[x["uid"]], by_doc[y["uid"]])
            pairs[x["uid"] + "|" + y["uid"]] = rows
            same = sum(r[2] >= 0.999 for r in rows); match = sum(r[0] is not None and r[1] is not None for r in rows)
            print(f"{name:<20} {x['uid']:<28} → {y['uid']:<28} matched {match:>3} (identical {same:>3}), "
                  f"dropped {sum(r[1] is None for r in rows):>3}, added {sum(r[0] is None for r in rows):>3}")
        out[name] = {"docs": [d["uid"] for d in docs], "pairs": pairs}
    json.dump(out, open(os.path.join(D, "editions.json"), "w", encoding="utf-8"), ensure_ascii=False,
              separators=(",", ":"))
    print(f"\n{len(out)} series · {sum(len(s['pairs']) for s in out.values())} pairs → data/editions.json")


if __name__ == "__main__": main()

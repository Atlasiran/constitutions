#!/usr/bin/env python3
"""Audit the corpus against the human-rights benchmark through normalcy's /v1/audit.

Each active document is sent as numbered segments: its articles when they were
identified reliably (seq_score >= 0.5 and articles of normal length), otherwise
its pages. The scoring guide
follows the document's kind (see normalcy's rubrics/*.json), so bylaws are never
scored with the constitutional guide. normalcy answers repeated input from its
cache and runs the rest through the Message Batches API.

    .venv/bin/python pipeline/audit.py --dry-run          # segments and size only
    .venv/bin/python pipeline/audit.py submit [uid ...]   # needs NORMALCY_KEY (env or local/normalcy.env)
    .venv/bin/python pipeline/audit.py collect

Results go to data/audits/<uid>.json with review.status "unreviewed": a verdict
is published only after a reviewer signs it off.
"""
import json, os, sys, urllib.error, urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from articles import repair

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(DATA, "audits")
JOBS = os.path.join(OUT, "jobs.json")
RUBRICS = os.environ.get("NORMALCY_RUBRICS") or os.path.join(ROOT, "vendor", "normalcy", "public", "data", "rubrics.json")
API = os.environ.get("NORMALCY_URL", "https://normalcy.is").rstrip("/")

UNIT = {"اص[سص]?ل": "اصل", "ماد[هدة]": "ماده", "بند": "بند", "تبصره": "تبصره"}
MAX_BATCH_DOCS, MAX_BATCH_CHARS = 10, 1_500_000
MAX_MEAN_ARTICLE = 4000  # longer "articles" mean the markers were missed: cite pages instead


def client_key():
    """NORMALCY_KEY from the environment, else from local/normalcy.env (gitignored)."""
    key = os.environ.get("NORMALCY_KEY")
    path = os.path.join(ROOT, "local", "normalcy.env")
    if not key and os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.startswith("NORMALCY_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key:
        sys.exit("NORMALCY_KEY is not set (the constitutions client key for normalcy /v1; "
                 "export it or put NORMALCY_KEY=... in local/normalcy.env)")
    return key


def api(method, path, body=None):
    key = client_key()
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(body, ensure_ascii=False).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "constitutions-pipeline"})
    try:
        with urllib.request.urlopen(req, timeout=300) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path}: HTTP {e.code} {e.read().decode(errors='replace')[:500]}")


def rubric_for(kind, rubrics):
    for name, g in rubrics.items():
        if kind in g["applies_to"]:
            return name
    return None


def segments(entry):
    """Numbered segments for one registry entry, and how they were made."""
    slug = entry["legacy_slug"]
    pages = json.load(open(os.path.join(DATA, "text", slug + ".json"), encoding="utf-8"))["pages"]
    arts = json.load(open(os.path.join(DATA, "articles", slug + ".json"), encoding="utf-8"))
    lo, hi = entry.get("pages") or (1, 10**9)
    pages = [p for p in pages if lo <= p["page"] <= hi]

    chosen = [a for a in arts["articles"] if lo <= a["page"] <= hi]
    mean = sum(len(a["text"]) for a in chosen) / len(chosen) if chosen else 0
    if arts["seq_score"] >= 0.5 and len(chosen) >= 3 and mean <= MAX_MEAN_ARTICLE:
        word = UNIT.get(arts["unit"], arts["unit"])
        segs, seen = [], {}
        full = "\n".join(repair(p["text"]) for p in pages)
        start = full.find(chosen[0]["text"][:200]) if chosen else -1
        if start > 0 and full[:start].strip():
            segs.append({"id": "pre", "label": "مقدمه / preamble", "text": full[:start].strip()})
        for a in chosen:
            seen[a["n"]] = seen.get(a["n"], 0) + 1
            sid = f"a{a['n']}" + (f"-{seen[a['n']]}" if seen[a["n"]] > 1 else "")
            segs.append({"id": sid, "label": f"{word} {a['n']} (p. {a['page']})", "text": a["text"]})
        return segs, "articles"
    segs = [{"id": f"p{p['page']}", "label": f"p. {p['page']}", "text": repair(p["text"]).strip()}
            for p in pages if p["text"].strip()]
    return segs, "pages"


def documents(uids):
    registry = json.load(open(os.path.join(DATA, "registry.json"), encoding="utf-8"))
    rubrics = json.load(open(RUBRICS, encoding="utf-8"))["rubrics"]
    out = []
    for e in registry:
        if e.get("status") != "active" or (uids and e["uid"] not in uids):
            continue
        rubric = rubric_for(e["kind"], rubrics)
        if not rubric:
            print(f"  skip {e['uid']}: no scoring guide for kind {e['kind']}")
            continue
        segs, mode = segments(e)
        out.append({"entry": e, "rubric": rubric, "mode": mode,
                    "doc": {"id": e["uid"], "title": e.get("fa") or e.get("en"), "segments": segs}})
    return out


def chars(d):
    return sum(len(s["text"]) for s in d["doc"]["segments"])


def dry_run(docs):
    total = 0
    for d in docs:
        n = chars(d)
        total += n
        print(f"  {d['entry']['uid']:<36} {d['rubric']:<20} {d['mode']:<8} "
              f"{len(d['doc']['segments']):>4} segs {n:>8,} chars")
    print(f"\n{len(docs)} documents, {total:,} characters")


def load_jobs():
    return json.load(open(JOBS, encoding="utf-8")) if os.path.exists(JOBS) else []


def save_jobs(jobs):
    os.makedirs(OUT, exist_ok=True)
    json.dump(jobs, open(JOBS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def submit(docs, refresh):
    jobs = load_jobs()
    for rubric in sorted({d["rubric"] for d in docs}):
        group, size = [], 0
        todo = [d for d in docs if d["rubric"] == rubric]
        for i, d in enumerate(todo):
            group.append(d)
            size += chars(d)
            last = i == len(todo) - 1
            if last or len(group) >= MAX_BATCH_DOCS or size + chars(todo[i + 1]) > MAX_BATCH_CHARS:
                res = api("POST", "/v1/audit", {"rubric": rubric, "refresh": refresh,
                                                "documents": [g["doc"] for g in group]})
                print(f"  job {res['job']}  {rubric}  {res['counts']}")
                jobs.append({"job": res["job"], "rubric": rubric, "status": res["status"],
                             "docs": {g["doc"]["id"]: g["mode"] for g in group}})
                group, size = [], 0
    save_jobs(jobs)


def collect(docs_by_uid):
    jobs = load_jobs()
    os.makedirs(OUT, exist_ok=True)
    waiting = 0
    for job in jobs:
        if job.get("collected"):
            continue
        res = api("GET", f"/v1/audit/{job['job']}")
        if res["status"] != "ended":
            waiting += 1
            print(f"  job {job['job']}: still processing {res['counts']}")
            continue
        for r in res["results"]:
            uid = r["id"]
            if r["state"] == "failed" or not r["result"]:
                print(f"  {uid}: FAILED {r['error']}")
                continue
            d = docs_by_uid.get(uid)
            labels = {s["id"]: s["label"] for s in d["doc"]["segments"]} if d else {}
            record = {
                "uid": uid,
                "doc_version": d["entry"].get("version") if d else None,
                "segmented_by": job["docs"].get(uid),
                "segment_labels": labels,
                **r["result"],
                "review": {"status": "unreviewed", "reviewer": None, "date": None, "notes": ""},
            }
            path = os.path.join(OUT, f"{uid}.json")
            if os.path.exists(path):  # keep a reviewer's sign-off when the audit itself is unchanged
                old = json.load(open(path, encoding="utf-8"))
                if old.get("hash") == record["hash"]:
                    record["review"] = old.get("review", record["review"])
            json.dump(record, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"  {uid}: {r['state']}, {record['rejected']} rejected, {record['warnings']} warnings")
        job["collected"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        job["status"] = "ended"
    save_jobs(jobs)
    print(f"\n{waiting} job(s) still processing" if waiting else "\nall jobs collected")


def main():
    args = sys.argv[1:]
    refresh = "--refresh" in args
    args = [a for a in args if a != "--refresh"]
    if not args or args[0] == "--dry-run":
        return dry_run(documents(set(args[1:])))
    cmd, uids = args[0], set(args[1:])
    if cmd == "submit":
        submit(documents(uids), refresh)
    elif cmd == "collect":
        collect({d["doc"]["id"]: d for d in documents(set())})
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()

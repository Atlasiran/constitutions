#!/usr/bin/env python3
"""Vocabularies beside Constitute's, from the Sartori ontology repository (github.com/conceptintegration/sartori-repo).

Three layers, each tagged on its own field of an article (`x` in data/topics/<uid>.json), so the Constitute tags and
their `ontology_version` are untouched:

    ccp:  the three topics of the CCP's later vocabulary (CCP-FACET) that Constitute's 334 lack: democracy, rule of
          law, social security. They join our subject groups and count with Constitute's topics.
    cap:  the Comparative Agendas Project's policy topics (CAP-TOP, 213 under 21 headings): the policy field an article
          governs (transport, energy, agriculture …), which Constitute does not code.
    ps:   power-sharing rules: Juon's Constitutional Power-Sharing Dataset (all 75) and the 18 rules of Strøm et al.'s
          Inclusion, Dispersion and Constraint dataset that a constitution can lay down and Constitute does not code.

    sartori.py fetch     # download the pinned files → data/ontology/sartori/ (+ source.json with sha256s)
    sartori.py check     # compare upstream HEAD with the pinned commit: changed, new and removed ontologies
    sartori.py           # print the layers as ontology.py builds them

Licences differ from Constitute's: see data/ontology/sartori/README.md. Persian labels are in
data/ontology/sartori/fa.json, kept apart from Constitute's fa.json because they fall under ShareAlike.
"""
import csv, hashlib, json, os, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "ontology", "sartori")
REPO = "conceptintegration/sartori-repo"
COMMIT = "0fa9ca380d8e5acb2986dc89036691d2253df0c5"   # 2026-05-27; `check` says when upstream moves on
# upstream folder → local file stem (ASCII: Strøm's folder has an Ø)
FILES = {"CAP-TOP": "CAP-TOP", "JUON-CPSD": "JUON-CPSD", "STRØM-IDC": "STROM-IDC", "CCP-FACET": "CCP-FACET"}
UA = {"User-Agent": "constitutions-pipeline"}

LAYERS = {
    "ccp": {"fa": "موضوع‌های افزوده از CCP", "en": "Added from the CCP's later vocabulary", "src": ["CCP-FACET"]},
    "cap": {"fa": "حوزه‌های سیاست‌گذاری", "en": "Policy fields", "src": ["CAP-TOP"]},
    "ps":  {"fa": "تقسیم قدرت", "en": "Power-sharing", "src": ["JUON-CPSD", "STRØM-IDC"]},
}
# CCP-FACET topics Constitute's vocabulary has no leaf for (checked 2026-10-03) → our subject group
CCP = {"democ": "principles", "rulelaw": "principles", "socsec": "social"}
# Strøm's rules a constitution can lay down → our power-sharing group. Left out: what governments did (gcimp, unity,
# gcseats1/2, resimp, resseatsimp, fedunits, violation) and what Constitute already codes (religion, the judiciary).
STROM = {"gcman": "incl", "partynoethnic": "incl", "resman": "incl", "mveto": "veto", "resseats": "leg",
         "stconst": "leg", "state": "terr", "muni": "terr", "subtax": "terr", "subed": "terr", "subpolice": "terr",
         "auton": "terr", "milleg": "mil", "miman": "mil", "mfound": "mil", "milvote": "mil", "milparty": "mil",
         "milparty2": "mil"}
PS_GROUPS = {"exec": ("مقام‌های اجرایی و ریاست مجلس‌ها", "Executive offices and speakers"),
             "leg": ("کرسی‌های مجلس", "Legislative seats"),
             "veto": ("حق وتو و اکثریت ویژه", "Vetoes and supermajorities"),
             "incl": ("مشارکت گروه‌ها در قدرت", "Inclusion of groups"),
             "terr": ("تقسیم سرزمینی قدرت", "Territorial dispersion"),
             "mil": ("ارتش و سیاست", "The military and politics")}


def juon_group(key):
    n = int(key)
    return "exec" if n <= 60 else "leg" if n <= 67 else "veto"


def raw(folder, name, ref=COMMIT):
    url = f"https://raw.githubusercontent.com/{REPO}/{ref}/{urllib.parse.quote(folder)}/{name}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read()


def fetch():
    os.makedirs(OUT, exist_ok=True)
    files = {}
    for folder, stem in FILES.items():
        for name, suffix in (("ontology.csv", ".csv"), ("metadata.csv", ".metadata.csv")):
            data = raw(folder, name)
            open(os.path.join(OUT, stem + suffix), "wb").write(data)
            files[stem + suffix] = {"from": f"{folder}/{name}", "sha256": hashlib.sha256(data).hexdigest()}
            print(f"  {folder}/{name}: {len(data):,} bytes")
    src = {"repo": f"https://github.com/{REPO}", "commit": COMMIT,
           "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "licence": "CC BY-NC-SA 4.0", "files": files}
    json.dump(src, open(os.path.join(OUT, "source.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def check():
    """Upstream HEAD against the pinned commit: our files changed or not, and ontologies added or removed."""
    api = lambda p: json.load(urllib.request.urlopen(urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{p}", headers=UA | {"Accept": "application/vnd.github+json"}), timeout=60))
    head = api("commits/HEAD")
    sha, date = head["sha"], head["commit"]["committer"]["date"][:10]
    print(f"pinned {COMMIT[:10]}; upstream HEAD {sha[:10]} ({date})" + ("  — no change" if sha == COMMIT else ""))
    if sha == COMMIT: return
    src = json.load(open(os.path.join(OUT, "source.json"), encoding="utf-8"))
    for stem, f in src["files"].items():
        folder, name = f["from"].split("/")
        try: new = hashlib.sha256(raw(folder, name, sha)).hexdigest()
        except Exception as e: print(f"  {f['from']}: gone? ({e})"); continue
        print(f"  {f['from']}: {'unchanged' if new == f['sha256'] else 'CHANGED'}")
    dirs = lambda ref: {x["name"] for x in api(f"contents?ref={ref}") if x["type"] == "dir" and not x["name"].startswith(".")}
    now, then = dirs(sha), dirs(COMMIT)
    if now - then: print("  new ontologies:", ", ".join(sorted(now - then)))
    if then - now: print("  removed:", ", ".join(sorted(then - now)))
    print("If anything changed: read it, update COMMIT, run `sartori.py fetch`, then `ontology.py`.")


def rows(folder):
    return list(csv.DictReader(open(os.path.join(OUT, FILES[folder] + ".csv"), encoding="utf-8-sig")))


def layers(groups):
    """{layers, leaves, version}: every added topic with its layer, group, English and Persian."""
    if not os.path.exists(os.path.join(OUT, "source.json")): sys.exit(f"{OUT} missing: run `sartori.py fetch` first")
    fa_path = os.path.join(OUT, "fa.json")
    fa = json.load(open(fa_path, encoding="utf-8")) if os.path.exists(fa_path) else {}
    leaves = []

    def add(layer, key, group, r, src):
        i = f"{layer}:{key}"
        f = fa.get(i, {})
        leaves.append({"id": i, "layer": layer, "group": group, "src": src, "en": r["label"].strip(),
                       "definition_en": (r.get("description") or "").strip(),
                       "fa": f.get("fa"), "fa_def": f.get("fa_def"), "fa_status": f.get("status", "missing")})

    facet = {r["key"]: r for r in rows("CCP-FACET")}
    for k, g in CCP.items():
        assert g in groups, g
        add("ccp", k, g, facet[k], "CCP-FACET")
    cap_groups = {}
    for r in rows("CAP-TOP"):
        head = r["parent_category"].strip()
        g = "cap-" + head.lower().replace(" ", "-")
        cap_groups[g] = head
        add("cap", r["key"], g, r, "CAP-TOP")
    for r in rows("JUON-CPSD"):
        add("ps", "j" + r["key"], "ps-" + juon_group(r["key"]), r, "JUON-CPSD")
    strom = {r["key"]: r for r in rows("STRØM-IDC")}
    for k, g in STROM.items():
        add("ps", k, "ps-" + g, strom[k], "STRØM-IDC")

    lgroups = {}
    for g, en in cap_groups.items():
        lgroups[g] = {"fa": fa.get("group:" + g, {}).get("fa"), "en": en, "layer": "cap"}
    for g, (gfa, gen) in PS_GROUPS.items():
        lgroups["ps-" + g] = {"fa": gfa, "en": gen, "layer": "ps"}
    src = json.load(open(os.path.join(OUT, "source.json"), encoding="utf-8"))
    mapping = json.dumps([CCP, STROM, sorted(f["sha256"] for f in src["files"].values())], sort_keys=True).encode()
    return {"version": hashlib.sha256(mapping).hexdigest()[:12], "source": src,
            "layers": LAYERS, "groups": lgroups, "leaves": leaves}


if __name__ == "__main__":
    cmd = sys.argv[1:]
    if cmd == ["fetch"]: fetch()
    elif cmd == ["check"]: check()
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from ontology import GROUPS
        L = layers(GROUPS)
        from collections import Counter
        print(f"layers version {L['version']}: " + ", ".join(f"{k} {v}" for k, v in Counter(x['layer'] for x in L['leaves']).items()))
        print(f"Persian: {Counter(x['fa_status'] for x in L['leaves'])}")

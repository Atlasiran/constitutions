#!/usr/bin/env python3
"""Import Constitute's topic vocabulary (Comparative Constitutions Project) and map it onto our topic groups.

Constitute codes constitutions with about 330 topics, each with a definition and the coding question it answers.
Each leaf topic is assigned to one of our groups: the 25 of analyze.py plus a few the keyword lists never had.
A leaf takes its group from its Constitute parents; a leaf whose parents point to different groups needs an entry
in LEAF, and the build stops until it has one. Persian labels live in data/ontology/fa.json, kept apart so a
re-import never overwrites a reviewed translation.

    ontology.py fetch     # download topics.xml → data/ontology/constitute-topics.xml (+ source.json)
    ontology.py           # → data/ontology/topics.json
    ontology.py fa        # draft Persian labels for topics fa.json lacks (model, ~50 a call), then rebuild

The vocabulary is CC BY-NC 3.0 (see data/ontology/README.md), not covered by the repository's AGPL.
`version` hashes the XML and the mapping, so tags cached against one version go stale when either changes.
"""
import hashlib, json, os, sys, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import TOPICS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "ontology")
XML = os.path.join(OUT, "constitute-topics.xml")
URL = "https://www.constituteproject.org/topics.xml"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
RDFS = "{http://www.w3.org/2000/01/rdf-schema#}"
LANG = "{http://www.w3.org/XML/1998/namespace}lang"

# groups the 25 keyword topics lacked: Constitute codes these and our drafts address them
EXTRA = {
    "principles":    ("اصول و نمادها", "Principles & symbols"),
    "international": ("حقوق بین‌الملل", "International law"),
    "oversight":     ("نهادهای مستقل نظارتی", "Independent oversight bodies"),
    "social":        ("حقوق اجتماعی", "Social rights"),
    "transition":    ("گذار و عدالت انتقالی", "Transition & transitional justice"),
}
GROUPS = {k: {"fa": v[0], "en": v[1]} for k, v in TOPICS.items()} | {k: {"fa": v[0], "en": v[1]} for k, v in EXTRA.items()}

# Constitute parent → our group
PARENT = {
    "amendment": "amendment",
    "Citizenship": "citizenship", "Indigenous_Groups": "ethnic_language", "Language": "ethnic_language",
    "Race_and_Ethnicity": "ethnic_language", "Religion": "religion_state",
    "Electoral_Oversight": "elections", "Electoral_Rules_and_Regulations": "elections", "Political_Parties": "association",
    "Referenda_and_Initiatives": "elections", "Suffrage_and_Turnout": "elections", "Elections": "elections",
    "Cabinet": "executive", "Executive_Independence_and_Power": "executive", "Head_of_Government": "executive",
    "Head_of_State": "executive", "Structure_of_the_Executive": "executive", "Military": "military",
    "Lawmaking_Power": "federalism", "Secession_and_Accession": "federalism", "Structure_of_the_State": "federalism",
    "Explicit_References_to_Int_Law": "international", "Foreign_Policy": "international", "Treaties": "international",
    "Administrative_Courts": "judiciary", "Constitutional_Court": "judiciary", "Electoral_Courts": "judiciary",
    "Judicial_Autonomy_and_Power": "judiciary", "Judicial_Review": "judiciary", "Ordinary_Courts": "judiciary",
    "Structure_of_the_Judiciary": "judiciary", "Supreme_Court": "judiciary",
    "First_Chamber": "legislature", "Legislation": "legislature", "Legislative_Independence_and_Power": "legislature",
    "Legislative_Rules_and_Restrictions": "legislature", "Removal_and_Replacement": "legislature",
    "Second_Chamber": "legislature", "Structure_of_the_Legislature": "legislature", "Special_Legislation": "economy",
    "Basic_Principles": "principles", "State_Definition_and_Symbols": "principles", "special_sections": "principles",
    "Independent_Agencies_and_Commissions": "oversight", "Media_and_Communications": "media", "Social_Issues": "social",
    "Citizen_Duties": "rights_fundamental", "Civil_and_Political_Rights": "rights_fundamental",
    "Economic_Rights": "economy", "Enforcement": "rights_fundamental", "General_Duties": "rights_fundamental",
    "Legal_Procedural_Rights": "due_process", "Minority_Rights": "equality", "Physical_Integrity_Rights": "punishment",
    "Social_Rights": "social",
}

# leaf → our group, where the parent's group is wrong for it or its parents disagree
LEAF = {
    # religion: the freedom is a right; equality on grounds of religion is equality
    "freerel": "religion", "equalgr6": "equality", "equalgr11": "equality",
    # ethnicity and language
    "equalgr4": "ethnic_language", "equalgr5": "ethnic_language", "equalgr14": "ethnic_language",
    "cultrght": "ethnic_language", "selfdet": "ethnic_language", "trilang": "ethnic_language",
    "indcit": "ethnic_language", "indpolgr1": "ethnic_language", "indpolgr2": "ethnic_language",
    "indpolgr3": "ethnic_language", "indpolgr4": "ethnic_language", "indpolgr5": "ethnic_language",
    "indpolgr6": "ethnic_language", "opgroup": "economy",
    # citizenship
    "equalgr2": "equality", "equalgr3": "equality", "citren": "citizenship", "asylum": "citizenship",
    "freemove": "citizenship", "resenex": "citizenship",
    # women
    "equalgr1": "women", "matequal": "women",
    # elections and parties
    "voteun": "elections", "partunco": "association", "equalgr15": "equality", "prtyduty": "association",
    "assem": "association", "assoc": "association", "ecom": "elections",
    "ecage": "elections", "ecpow": "elections", "ecrdet": "elections", "ecres": "elections",
    "ecsel": "elections", "ecterm": "elections", "ecterml": "elections",
    # executive, military, emergency
    "cabdiss": "executive", "cabpow": "executive", "cabrest": "executive", "cabinet": "executive",
    "comchief": "military", "em": "emergency", "war": "military", "nomil": "military", "milserv": "military",
    "civil": "executive", "invexe": "legislature",
    # judiciary
    "conpow": "judiciary", "conrem": "judiciary", "interp": "judiciary", "uncon": "judiciary", "suppow": "judiciary",
    "illadmin": "judiciary", "amparo": "judiciary", "judcrts1": "judiciary", "judcrts2": "judiciary",
    "judcrts3": "judiciary", "judcrts4": "judiciary", "judcrts8": "religion_state", "jc": "judiciary",
    # legislature
    "legapp": "legislature", "override": "legislature", "immunity": "legislature", "legdiss": "legislature",
    "legrep": "legislature", "remleg": "legislature",
    # international
    "intrght": "international",
    # rights
    "express": "expression", "opinion": "expression", "infoacc": "expression", "press": "media",
    "privacy": "privacy", "libel": "privacy", "acfree": "education", "debtors": "economy",
    "occupate": "labor", "taxes": "economy", "work": "labor", "abide": "principles",
    "hr": "oversight", "ombuds": "oversight",
    "life": "punishment", "slave": "rights_fundamental",
    "edcomp": "education", "edfree": "education", "achighed": "education", "scifree": "education",
    "env": "environment", "jointrde": "labor", "strike": "labor", "provwork": "labor", "remuner": "labor",
    "safework": "labor", "leisure": "labor", "childwrk": "labor",
    # agencies with a home group
    "bank": "economy", "medcom": "media", "truthcom": "transition",
    # principles
    "orglaw": "legislature", "resrce": "economy", "prevlead": "transition", "tranprov": "transition", "region": "international",
}


def fetch():
    os.makedirs(OUT, exist_ok=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "constitutions-pipeline"})
    with urllib.request.urlopen(req, timeout=120) as res:
        data = res.read()
    open(XML, "wb").write(data)
    src = {"url": URL, "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
           "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    json.dump(src, open(os.path.join(OUT, "source.json"), "w", encoding="utf-8"), indent=1)
    print(f"{URL}: {len(data):,} bytes, sha256 {src['sha256'][:16]}")


def text(el, tag, lang="en"):
    for x in el.findall(tag):
        if x.get(LANG) == lang: return (x.text or "").strip()
    return None


def parse():
    """Every Topic node: {id: {parents, en, definition_en, keywords_en, qid, question}}."""
    nodes = {}
    for t in ET.parse(XML).getroot().findall("Topic"):
        k = t.get(RDF + "about").rsplit("/", 1)[1]
        q = t.findtext("question")
        qid, q = q.split("|", 1) if q and "|" in q else (None, q)
        nodes[k] = {"parents": [p.get(RDF + "resource").rsplit("/", 1)[1] for p in t.findall(RDFS + "subClassOf")],
                    "en": text(t, RDFS + "label"), "definition_en": text(t, "description"),
                    "keywords_en": [x.text.strip() for x in t.findall("keyword") if x.get(LANG) == "en" and x.text],
                    "qid": qid, "question": q and q.strip()}
    return nodes


def build():
    if not os.path.exists(XML): sys.exit(f"{XML} missing: run `ontology.py fetch` first")
    nodes = parse()
    inner = {p for n in nodes.values() for p in n["parents"]}
    leaves = sorted(k for k in nodes if k not in inner)
    fa_path = os.path.join(OUT, "fa.json")
    fa = json.load(open(fa_path, encoding="utf-8")) if os.path.exists(fa_path) else {}

    topics, problems = [], []
    for k in leaves:
        n = nodes[k]
        cands = {PARENT[p] for p in n["parents"] if p in PARENT}
        group = LEAF.get(k) or (cands.pop() if len(cands) == 1 else None)
        if not group:
            problems.append(f"  {k} ({n['en']}): parents {n['parents']} → {sorted(cands) or 'no group'}")
            continue
        assert group in GROUPS, f"{k}: unknown group {group}"
        f = fa.get(k, {})
        topics.append({"id": k, "parent": n["parents"][0], "parents": n["parents"], "group": group,
                       "en": n["en"], "definition_en": n["definition_en"], "keywords_en": n["keywords_en"],
                       "qid": n["qid"], "question": n["question"],
                       "fa": f.get("fa"), "fa_def": f.get("fa_def"), "fa_status": f.get("status", "missing")})
    if problems:
        sys.exit(f"{len(problems)} leaves without a single group; add them to LEAF:\n" + "\n".join(problems))

    stale = [k for k in LEAF if k not in nodes]
    mapping = json.dumps([PARENT, LEAF, EXTRA], sort_keys=True, ensure_ascii=False).encode()
    version = hashlib.sha256(open(XML, "rb").read() + mapping).hexdigest()[:12]
    src = json.load(open(os.path.join(OUT, "source.json"), encoding="utf-8"))
    out = {"version": version, "source": src,
           "licence": "CC BY-NC 3.0 Unported; Comparative Constitutions Project, constituteproject.org",
           "groups": GROUPS, "topics": topics}
    json.dump(out, open(os.path.join(OUT, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    from collections import Counter
    by = Counter(t["group"] for t in topics)
    print(f"{len(nodes)} nodes, {len(leaves)} leaves, {sum(1 for t in topics if t['question'])} with a question, "
          f"{len(topics)} mapped, version {version}")
    print(f"Persian: {sum(1 for t in topics if t['fa_status'] == 'reviewed')} reviewed, "
          f"{sum(1 for t in topics if t['fa_status'] == 'draft')} draft, "
          f"{sum(1 for t in topics if t['fa_status'] == 'missing')} missing")
    for g in GROUPS: print(f"  {by.get(g, 0):>4}  {g}")
    if stale: print("LEAF entries not in the vocabulary:", stale)


MODEL = "claude-opus-5-5"   # user, 2026-10-03: Opus 5.5 at medium effort for the vocabulary and tagging
FA_BATCH = 50
FA_SYSTEM = """You translate the labels and definitions of a controlled vocabulary of constitutional topics (the Comparative Constitutions Project's, used by Constitute) into Persian, for a research site that compares Iranian draft constitutions. Readers are Iranian lawyers, activists and citizens.

For each topic give:
- fa: a short Persian label (a noun phrase, like the English label), using the established Persian legal term where one exists.
- fa_def: the definition in one plain Persian sentence.

Translate the meaning, not word for word. Keep terms consistent across topics: the same English term always gets the same Persian term (the glossary and the labels already made are given). Do not add commentary.

Orthography (follow exactly):
- Tanvin is written with «ن»: «معمولن، صرفن، مستقیمن». Never «ـاً».
- Ezafe after a silent ه is «ه‌ی» with a zero-width non-joiner: «قوه‌ی مقننه، درباره‌ی». Never «هٔ» or «ۀ».
- No hamza on alef or vav: «رای، تایید، تاسیس، هیات، ماموریت، موثر». Keep it on the yeh seat: «مسئله، مسئول، ارائه».
- Persian «ی» and «ک» only, never Arabic «ي» or «ك». Persian digits.
- Zero-width non-joiner in «می‌/نمی‌», in «ـ‌ها» after a joining letter, in «ـ‌تر/ـ‌ترین», and in «به‌عنوان، به‌جای، تصمیم‌گیری، رای‌گیری».
- «سازوکار», not «مکانیزم»; «فرایند»; «کورد، کوردستان»."""
FA_GLOSSARY = {
    "constitution": "قانون اساسی", "head of state": "رئیس کشور", "head of government": "رئیس دولت",
    "cabinet": "هیات وزیران", "legislature": "قوه‌ی مقننه", "first chamber": "مجلس نخست",
    "second chamber": "مجلس دوم", "judiciary": "قوه‌ی قضاییه", "constitutional court": "دادگاه قانون اساسی",
    "supreme court": "دیوان عالی", "subsidiarity": "تبعیت از محل", "referendum": "همه‌پرسی",
    "amendment": "بازنگری", "eligibility": "شرایط احراز", "term length": "مدت دوره", "term limits": "محدودیت دوره‌ها",
}


def fa_schema(ids):
    item = {"type": "object", "additionalProperties": False, "required": ["id", "fa", "fa_def"],
            "properties": {"id": {"type": "string", "enum": ids}, "fa": {"type": "string"}, "fa_def": {"type": "string"}}}
    return {"type": "object", "additionalProperties": False, "required": ["topics"],
            "properties": {"topics": {"type": "array", "items": item}}}


def draft_fa():
    """Ask the model for Persian labels of the topics fa.json lacks, FA_BATCH at a time; store them as drafts."""
    from vision_ocr import client
    fa_path = os.path.join(OUT, "fa.json")
    fa = json.load(open(fa_path, encoding="utf-8")) if os.path.exists(fa_path) else {}
    topics = json.load(open(os.path.join(OUT, "topics.json"), encoding="utf-8"))["topics"]
    todo = [t for t in topics if t["id"] not in fa]
    print(f"{len(todo)} topics without Persian")
    c, spent = client(), {"input_tokens": 0, "output_tokens": 0}
    for i in range(0, len(todo), FA_BATCH):
        batch = todo[i:i + FA_BATCH]
        made = {t["en"]: fa[t["id"]]["fa"] for t in topics if t["id"] in fa}
        rows = [{"id": t["id"], "en": t["en"], "definition": t["definition_en"], "group": GROUPS[t["group"]]["en"]}
                for t in batch]
        with c.beta.messages.stream(
                model=MODEL, max_tokens=64000, thinking={"type": "adaptive"},
                output_config={"effort": "medium",
                               "format": {"type": "json_schema", "schema": fa_schema([t["id"] for t in batch])}},
                betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                system=FA_SYSTEM,
                messages=[{"role": "user", "content":
                           "Glossary:\n" + json.dumps(FA_GLOSSARY, ensure_ascii=False, indent=0) +
                           "\n\nLabels already made:\n" + json.dumps(made, ensure_ascii=False, indent=0) +
                           "\n\nTranslate these topics:\n" + json.dumps(rows, ensure_ascii=False, indent=0)}]) as s:
            msg = s.get_final_message()
        for k in spent: spent[k] += getattr(msg.usage, k, 0) or 0
        if msg.stop_reason != "end_turn":
            sys.exit(f"batch {i // FA_BATCH + 1}: stop_reason {msg.stop_reason}; {len(fa)} kept")
        got = json.loads(next(b.text for b in msg.content if b.type == "text"))["topics"]
        for x in got:
            fa[x["id"]] = {"fa": x["fa"].strip(), "fa_def": x["fa_def"].strip(), "status": "draft", "model": msg.model}
        missing = [t["id"] for t in batch if t["id"] not in fa]
        print(f"batch {i // FA_BATCH + 1}: {len(got)} labels" + (f", missing {missing}" if missing else ""))
        json.dump(dict(sorted(fa.items())), open(fa_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"usage: {spent}")
    build()


if __name__ == "__main__":
    cmd = sys.argv[1:]
    fetch() if cmd == ["fetch"] else draft_fa() if cmd == ["fa"] else build()

#!/usr/bin/env python3
"""Our own vocabularies, for what neither Constitute nor the Sartori repository covers (plan 7.15).

    lang:    language policy, 27 items: status (official languages and who chooses them) and use in courts, administration,
             schools, media, culture and economic life. Built on the domains of the European Charter for Regional or
             Minority Languages (Part III, arts. 8–14) and the Framework Convention for the Protection of National
             Minorities (arts. 9–14, 17); data/ontology/own/lang.json.
    levels:  who holds a policy field (national, national law with regional execution, national principles with
             regional detail, shared, regional, local); recorded per policy-field tag of an article (`lv` in
             data/topics/<uid>.json). data/ontology/own/levels.json.
    rai:     the ten dimensions of the Regional Authority Index (Hooghe, Marks, Schakel et al.), scored per document
             (`rai` in data/topics/<uid>.json). data/ontology/own/rai.json.

ontology.py merges them into the `extra` block of topics.json, beside the Sartori layers.

    own.py    # print what would be merged
"""
import hashlib, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWN = os.path.join(ROOT, "data", "ontology", "own")


def load(name):
    return json.load(open(os.path.join(OWN, name), encoding="utf-8"))


def merge(extra):
    """Add the language layer, the levels and the RAI dimensions to the Sartori `extra` block, and version the whole."""
    lang, levels, rai = load("lang.json"), load("levels.json"), load("rai.json")
    extra["layers"]["lang"] = lang["layer"]
    for g, v in lang["groups"].items():
        extra["groups"][g] = v | {"layer": "lang"}
    for x in lang["leaves"]:
        # Persian written with the vocabulary, so it starts as draft like the rest
        extra["leaves"].append({"id": "lang:" + x["key"], "layer": "lang", "group": x["group"], "src": x["s"],
                                "en": x["en"], "definition_en": x["d"], "fa": x["fa"], "fa_def": x["df"],
                                "fa_status": x.get("status", "draft")})
    extra["levels"], extra["rai"] = levels, rai
    own = json.dumps([lang, levels, rai], sort_keys=True, ensure_ascii=False).encode()
    extra["version"] = hashlib.sha256(extra["version"].encode() + own).hexdigest()[:12]
    return extra


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ontology import GROUPS
    from sartori import layers
    X = merge(layers(GROUPS))
    print(f"extra version {X['version']}: lang {sum(1 for x in X['leaves'] if x['layer'] == 'lang')} items, "
          f"{len(X['levels']['levels'])} levels, {len(X['rai']['dims'])} RAI dimensions")

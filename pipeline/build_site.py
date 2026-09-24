#!/usr/bin/env python3
"""Assemble the browser payload from the pipeline outputs."""
import json, os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D,S=R+"/data",R+"/site/data"
os.makedirs(S,exist_ok=True)
cat=json.load(open(D+"/catalog.json",encoding="utf-8"))
an =json.load(open(D+"/analysis.json",encoding="utf-8"))
ar =json.load(open(D+"/articles_all.json",encoding="utf-8"))
an["topics"]={k:{"fa":v["fa"],"en":v["en"]} for k,v in an["topics"].items()}
uids={c["uid"] for c in cat}
an["edges"]=[e for e in an["edges"] if e["a"] in uids and e["b"] in uids]
slim=[{"doc":a["doc"],"n":a["n"],"unit":a["unit"],"page":a["page"],
       "topics":a["topics"],"text":a["text"][:2600]} for a in ar if a["doc"] in uids]
for n,o in [("catalog.json",cat),("analysis.json",an),("articles.json",slim)]:
    json.dump(o,open(S+"/"+n,"w",encoding="utf-8"),ensure_ascii=False,separators=(",",":"))
    print(f"  {n:<16} {os.path.getsize(S+'/'+n)/1e6:.2f} MB")
print(f"\n{len(cat)} documents · {len(slim)} articles · {len(an['edges'])} edges")

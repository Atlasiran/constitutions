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
# The copies publish_pdfs.py put in site/pdf/; a document without one gets no link
import sys; sys.path.insert(0,R+"/pipeline"); from publish_pdfs import pdf_names
PDF=pdf_names(cat)
for c in cat:
    if os.path.exists(R+"/site/pdf/"+PDF[c["source_pdf"]]):c["pdf"]=PDF[c["source_pdf"]]
an["edges"]=[e for e in an["edges"] if e["a"] in uids and e["b"] in uids]
# Article alignments between editions of one draft (editions.py); their articles keep their full text for the diff
ed=json.load(open(D+"/editions.json",encoding="utf-8")) if os.path.exists(D+"/editions.json") else {}
ed={k:s for k,s in ed.items() if all(u in uids for u in s["docs"])}
full={u for s in ed.values() for u in s["docs"]}
slim=[{"doc":a["doc"],"n":a["n"],"unit":a["unit"],"page":a["page"],**({"label":a["label"]} if "label" in a else {}),
       "topics":a["topics"],"text":a["text"] if a["doc"] in full else a["text"][:2600]} for a in ar if a["doc"] in uids]
# Benchmark audits (plan 5.4): published when a person approved them, or when review.publish is set, which
# shows them marked as not yet reviewed. --preview adds all the others, for a local look; build_module.py
# refuses to package a preview.
import glob, sys
preview="--preview" in sys.argv
NB=R+"/vendor/normalcy/public/data"
rub=json.load(open(NB+"/rubrics.json",encoding="utf-8"))["rubrics"]["audit-constitution"]
inst={i["id"]:{"en":i["en"],"fa":i["fa"],"url":i["source_url"]} for i in json.load(open(NB+"/instruments.json",encoding="utf-8"))["instruments"]}
prov={}
for f in glob.glob(NB+"/provisions/*.json"):
    for p in json.load(open(f,encoding="utf-8"))["provisions"]:
        prov[p["id"]]={"i":p["instrument"],"h":p.get("heading"),"en":p["text_en"],"fa":p.get("text_fa")}
        for q in p.get("paras") or []:
            prov[q["id"]]={"i":p["instrument"],"h":p.get("heading"),"en":q["text_en"],"fa":q.get("text_fa")}
audits,cited=[],set()
for f in sorted(glob.glob(D+"/audits/*.json")):
    if f.endswith("jobs.json"):continue
    a=json.load(open(f,encoding="utf-8"))
    rv=a.get("review",{}); ok=rv.get("status")=="approved"; public=ok or rv.get("publish") is True
    if a["uid"] not in uids or not (public or preview):continue
    for r in a["rights"].values():cited.update(r["provisions"])
    audits.append({k:a[k] for k in ("uid","doc_version","model","audited_at","benchmark","rubric_version",
                   "summary_en","summary_fa","review","rights","segment_labels")}
                  |({} if ok else {"unreviewed":True})|({} if public else {"preview":True}))
aud={"rights":[{k:r[k] for k in ("id","en","fa")} for r in rub["rights"]],
     "instruments":inst,"provisions":{k:prov[k] for k in sorted(cited) if k in prov},"audits":audits}
for n,o in [("catalog.json",cat),("analysis.json",an),("articles.json",slim),("audits.json",aud),("editions.json",ed)]:
    json.dump(o,open(S+"/"+n,"w",encoding="utf-8"),ensure_ascii=False,separators=(",",":"))
    print(f"  {n:<16} {os.path.getsize(S+'/'+n)/1e6:.2f} MB")
print(f"\n{len(cat)} documents · {len(slim)} articles · {len(an['edges'])} edges · "
      f"{len(ed)} edition series · {len(audits)} audits ({sum('unreviewed' in a for a in audits)} not yet reviewed, {sum('preview' in a for a in audits)} preview only)")

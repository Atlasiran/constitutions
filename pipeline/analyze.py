#!/usr/bin/env python3
"""TF-IDF similarity + transparent keyword topic tagging over the article corpus."""
import json, glob, os, re, math, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.join(ROOT,"pipeline")); from articles import repair

STOP = set("""و در به از که این را با است های برای آن یک می بر not های شود کنند خود تا
کرد بود شده هر یا نیز اگر همه باید کند دارد شد ای ها او ما آنها بین وی هم مورد اين
گیرد قرار دهد آید باشد بايد مي شوند کردن بودن نمی هیچ چه دیگر پس بی طبق ذیل فوق
موجب مطابق ماده اصل بند تبصره فصل قانون اساسی جمهوری ایران کشور ملی دولت""".split())

TOPICS = {
 "rights_fundamental": ("حقوق بنیادین","Fundamental rights", "حقوق بشر کرامت بنیادین ذاتی سلب ناپذیر منشور"),
 "expression":       ("آزادی بیان","Freedom of expression", "بیان اندیشه عقاید سانسور مطبوعات نشر گفتار"),
 "religion":         ("آزادی دین و عقیده","Freedom of religion & belief", "مذهب دین عقیده ایمان مذهبی اقلیت کیش باور"),
 "equality":         ("برابری","Equality & non-discrimination", "برابر تبعیض مساوی یکسان تساوی نژاد"),
 "women":            ("حقوق زنان","Women's rights", "زن زنان جنسیت مادر بانوان دختر"),
 "ethnic_language":  ("حقوق اقوام و زبان","Ethnic & language rights", "قوم اقوام زبان مادری ترک کرد بلوچ عرب لر ترکمن قومیت"),
 "legislature":      ("قوه مقننه","Legislature", "مجلس نمایندگان قانونگذاری پارلمان سنا مصوبه"),
 "executive":        ("قوه مجریه","Executive", "رئیس جمهور نخست وزیر هیات وزیران دولت مجریه کابینه"),
 "judiciary":        ("قوه قضاییه","Judiciary", "قضایی دادگاه قاضی دادرسی دیوان دادستان قضات"),
 "elections":        ("انتخابات","Elections", "انتخابات رای رأی نامزد صندوق اکثریت همه پرسی رفراندوم"),
 "federalism":       ("فدرالیسم و تقسیمات","Federalism & territory", "فدرال استان ایالت شورا محلی تقسیمات خودمختاری منطقه"),
 "military":         ("نیروهای مسلح","Armed forces", "ارتش نظامی سپاه دفاع مسلح نیروهای انتظامی"),
 "economy":          ("اقتصاد و مالکیت","Economy & property", "اقتصاد مالکیت اموال ملی سازی خصوصی بودجه مالیات دارایی"),
 "education":        ("آموزش","Education", "آموزش پرورش تحصیل مدرسه دانشگاه سواد"),
 "environment":      ("محیط زیست","Environment", "زیست محیط طبیعی آب جنگل آلودگی منابع"),
 "religion_state":   ("دین و دولت","Religion & state", "اسلام شرع فقیه روحانیت سکولار لائیک جدایی شریعت"),
 "amendment":        ("بازنگری قانون اساسی","Constitutional amendment", "بازنگری اصلاح تجدیدنظر تغییر متمم"),
 "emergency":        ("وضعیت اضطراری","Emergency powers", "اضطراری جنگ حکومت نظامی بحران تعلیق فوق العاده"),
 "citizenship":      ("شهروندی و تابعیت","Citizenship", "تابعیت شهروند ملیت اتباع مهاجر پناهنده"),
 "due_process":      ("دادرسی عادلانه","Due process", "بازداشت متهم وکیل بیگناه محاکمه علنی دفاع عادلانه"),
 "punishment":       ("مجازات و شکنجه","Punishment & torture", "شکنجه مجازات اعدام حبس قصاص زندان کیفر"),
 "media":            ("رسانه","Media & press", "رسانه مطبوعات روزنامه رادیو تلویزیون خبرگزاری"),
 "association":      ("احزاب و تشکل‌ها","Parties & association", "حزب احزاب انجمن تشکل اجتماعات تظاهرات سندیکا صنفی"),
 "labor":            ("حقوق کار","Labour rights", "کار کارگر مزد بیکاری اتحادیه اشتغال بازنشستگی"),
 "privacy":          ("حریم خصوصی","Privacy", "خصوصی مکاتبات تلفن مکالمات محرمانه منزل تفتیش"),
}
TOPIC_KW = {k: set(v[2].split()) for k, v in TOPICS.items()}

def tok(t):
    t = repair(t)
    t = re.sub(r'[^ء-ۿ\s]', ' ', t)
    return [w for w in t.split() if len(w) > 2 and w not in STOP]

def main():
    cat = json.load(open(os.path.join(D,"catalog.json"), encoding="utf-8"))
    by_src = {c["source_pdf"]: c for c in cat if not c.get("pages")}   # uid is the public identity
    by_uid = {c["uid"]: c for c in cat}
    arts, docs = [], []
    for path in sorted(glob.glob(os.path.join(D,"articles","*.json"))):
        a = json.load(open(path, encoding="utf-8"))
        c = by_uid.get(a["uid"]) if "uid" in a else by_src.get(a["source_pdf"])
        if not c: continue                               # not active in the registry
        uid = c["uid"]; docs.append(uid)
        for x in a["articles"]:
            if len(x["text"]) < 25: continue
            arts.append({"doc": uid, "n": x["n"], "unit": x["kind"], "page": x["page"],
                         "text": x["text"][:4000], "toks": tok(x["text"])})
    cat = {c["uid"]: c for c in cat}
    print(f"{len(arts)} articles with substantive text, {len(docs)} documents")

    vocab = {}
    for a in arts:
        for w in set(a["toks"]): vocab[w] = vocab.get(w, 0) + 1
    kept = [w for w, c in sorted(vocab.items()) if 2 <= c <= len(arts)*0.5]
    vocab = {w: i for i, w in enumerate(kept)}
    idf = np.zeros(len(vocab))
    for a in arts:
        for w in set(a["toks"]):
            if w in vocab: idf[vocab[w]] += 1
    idf = np.log(len(arts) / (1 + idf)) + 1
    print(f"vocabulary: {len(vocab):,} terms")

    X = np.zeros((len(arts), len(vocab)), dtype=np.float32)
    for i, a in enumerate(arts):
        for w in a["toks"]:
            if w in vocab: X[i, vocab[w]] += 1
    X *= idf
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    norms = np.linalg.norm(X, axis=1, keepdims=True); norms[norms == 0] = 1
    X /= norms

    # topic tagging (transparent keyword overlap)
    for a in arts:
        s = set(a["toks"]); hits = {}
        for k, kw in TOPIC_KW.items():
            o = len(s & kw)
            if o: hits[k] = o
        a["topics"] = sorted(hits, key=hits.get, reverse=True)[:3]

    # document-level similarity
    di = {d: i for i, d in enumerate(docs)}
    Dm = np.zeros((len(docs), X.shape[1]), dtype=np.float64)
    for i, a in enumerate(arts): Dm[di[a["doc"]]] += X[i].astype(np.float64)
    dn = np.linalg.norm(Dm, axis=1, keepdims=True); dn[dn < 1e-12] = 1
    Dm = np.nan_to_num(Dm / dn, nan=0.0, posinf=0.0, neginf=0.0)
    S = Dm @ Dm.T

    # cross-document nearest articles — one matmul, then read off rows
    SA = X @ X.T
    same = np.array([hash(a["doc"]) for a in arts])
    for i, a in enumerate(arts):
        sims = SA[i].copy()
        sims[same == same[i]] = -1
        top = np.argpartition(sims, -4)[-4:]
        top = top[np.argsort(sims[top])][::-1]
        a["near"] = [{"doc": arts[j]["doc"], "n": arts[j]["n"], "s": round(float(sims[j]), 3)}
                     for j in top if sims[j] > 0.18]
        del a["toks"]

    # edge list keyed by uid — deleting a document is just dropping its rows
    edges = [{"a": docs[i], "b": docs[j], "s": round(float(S[i, j]), 3)}
             for i in range(len(docs)) for j in range(i+1, len(docs)) if S[i, j] > 0.10]
    edges.sort(key=lambda e: -e["s"])
    json.dump({"topics": {k: {"fa": v[0], "en": v[1], "kw": v[2].split()} for k, v in TOPICS.items()},
               "edges": edges},
              open(os.path.join(D, "analysis.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(arts, open(os.path.join(D, "articles_all.json"), "w", encoding="utf-8"), ensure_ascii=False)

    print(f"\n{len(edges)} similarity edges (uid-keyed). Strongest:")
    for e in edges[:10]:
        print(f"  {e['s']:.3f}  {cat[e['a']]['en'][:32]}  ~  {cat[e['b']]['en'][:32]}")
    from collections import Counter
    c = Counter(t for a in arts for t in a["topics"])
    print("\ntop topics by article count:")
    for k, n in c.most_common(10): print(f"  {n:>5}  {TOPICS[k][1]}")

if __name__ == "__main__": main()

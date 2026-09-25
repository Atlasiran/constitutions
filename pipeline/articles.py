#!/usr/bin/env python3
"""Split documents into articles. Handles digits, ordinals, cardinals,
tatweel-justified text, and filters cross-references via longest increasing run."""
import re, json, glob, os, unicodedata

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
L = r'ء-غف-يٰ-ۓ'          # Persian letters, no tatweel/digits

FOLD = str.maketrans({'\u06be':'\u0647','\u06c0':'\u0647','\u06c1':'\u0647',
                      '\u0629':'\u0647','\u064a':'\u06cc','\u0649':'\u06cc',
                      '\u0643':'\u06a9','\u0623':'\u0627','\u0625':'\u0627',
                      '\u0671':'\u0627','\u06a4':'\u0641'})

def repair(s):
    """Fold Arabic/Urdu letter variants, rejoin tatweel-justified text."""
    s = s.translate(FOLD)
    prev = None
    while prev != s:
        prev = s
        s = re.sub(rf'(?<=[{L}])\s*ـ+\s*(?=[{L}])', '', s)
    return s

UC = {1:'یک',2:'دو',3:'سه',4:'چهار',5:'پنج',6:'شش',7:'هفت',8:'هشت',9:'نه'}
UO = {1:'اول',2:'دوم',3:'سوم',4:'چهارم',5:'پنجم',6:'ششم',7:'هفتم',8:'هشتم',9:'نهم'}
TC = {10:'ده',11:'یازده',12:'دوازده',13:'سیزده',14:'چهارده',15:'پانزده',16:'شانزده',
      17:'هفده',18:'هجده',19:'نوزده'}
TO = {10:'دهم',11:'یازدهم',12:'دوازدهم',13:'سیزدهم',14:'چهاردهم',15:'پانزدهم',
      16:'شانزدهم',17:'هفدهم',18:'هجدهم',19:'نوزدهم'}
DC = {20:'بیست',30:'سی',40:'چهل',50:'پنجاه',60:'شصت',70:'هفتاد',80:'هشتاد',90:'نود'}
DO = {20:'بیستم',30:'سی ام',40:'چهلم',50:'پنجاهم',60:'شصتم',70:'هفتادم',80:'هشتادم',90:'نودم'}
HC = {100:'صد',200:'دویست',300:'سیصد',400:'چهارصد',500:'پانصد',600:'ششصد',700:'هفتصد'}
HO = {100:'صدم',200:'دویستم',300:'سیصدم',400:'چهارصدم',500:'پانصدم',600:'ششصدم',700:'هفتصدم'}

def build():
    m = {}
    def add(n, s): m.setdefault(s.strip(), n)
    for d in (UC, UO, TC, TO, DO, HO): [add(n, s) for n, s in d.items()]
    add(1, 'یکم')
    for t, tc in DC.items():
        add(t, tc)
        for u, uo in UO.items(): add(t+u, f'{tc} و {uo}')
        for u, uc in UC.items(): add(t+u, f'{tc} و {uc}')
    for h, hc in HC.items():
        for u, uo in UO.items(): add(h+u, f'{hc} و {uo}')
        for u, uc in UC.items(): add(h+u, f'{hc} و {uc}')
        for n, s in TO.items(): add(h+n, f'{hc} و {s}')
        for n, s in TC.items(): add(h+n, f'{hc} و {s}')
        for t, to in DO.items(): add(h+t, f'{hc} و {to}')
        for t, tc in DC.items():
            add(h+t, f'{hc} و {tc}')
            for u, uo in UO.items(): add(h+t+u, f'{hc} و {tc} و {uo}')
            for u, uc in UC.items(): add(h+t+u, f'{hc} و {tc} و {uc}')
    for s, n in list(m.items()):
        if s.startswith('صد'): m.setdefault('یک'+s, n)
    for s, n in list(m.items()):
        # compound ordinals also end in «یکم» and, in older texts, «سیم»: «هشتاد و یکم», «سی و سیم»
        if ' و ' in s and s.endswith('اول'): m.setdefault(s[:-3] + 'یکم', n)
        if ' و ' in s and s.endswith('سوم'): m.setdefault(s[:-3] + 'سیم', n)
    return m

WORDS = build()
ALT = "|".join(map(re.escape, sorted(WORDS, key=len, reverse=True)))

def markers(text, kind):
    """All (start, end, number) for `kind` followed by a number."""
    out = []
    for m in re.finditer(rf'{kind}\s*[یى]?\s*[:)(\-–—.,،]?\s*(\d{{1,3}})(?![\d۰-۹])', text):
        out.append((m.start(), m.end(), int(m.group(1))))
    for m in re.finditer(rf'{kind}\s+({ALT})(?![{L}])', text):
        out.append((m.start(), m.end(), WORDS[m.group(1)]))
    out.sort()
    ded, last = [], -1
    for s, e, n in out:
        if s > last: ded.append((s, e, n)); last = s
    return ded

def toc_page(text):
    """A contents page: most of its lines end in a page number."""
    raw = [l for l in text.split("\n") if l.strip(" .")]
    if sum(bool(re.search(r'[.…]{4,}\s*[\d۰-۹]{1,3}\s*$', l)) for l in raw) >= 5: return True   # dot leaders
    lines = [l.strip(" .") for l in raw]
    return len(lines) >= 5 and sum(bool(re.search(r'\s[\d۰-۹]{1,3}$', l)) for l in lines) >= 0.6 * len(lines)

def _chain(nums, live):
    """Longest near-consecutive ascending chain over the indices still in `live`."""
    idx = [i for i in range(len(nums)) if live[i]]
    if not idx: return []
    best = {i: 1 for i in idx}; prev = {i: -1 for i in idx}
    for a, i in enumerate(idx):
        for j in idx[:a]:
            if 0 < nums[i] - nums[j] <= 3 and best[j] + 1 > best[i]:
                best[i] = best[j] + 1; prev[i] = j
    i = max(idx, key=lambda k: best[k]); out = []
    while i != -1: out.append(i); i = prev[i]
    return out[::-1]

def _segments(nums):
    """Repeatedly take the longest chain — catches per-chapter restarts."""
    live = [True]*len(nums); keep = []
    while True:
        c = _chain(nums, live)
        if len(c) < 5: break
        keep += c
        for i in c: live[i] = False
    return sorted(keep)

def score(nums, keep):
    """A real article sequence runs 1..N with N ~= the count. Reward that shape."""
    if not keep: return 0.0
    vals = [nums[i] for i in keep]
    return min(len(keep), max(vals)) / max(len(keep), max(vals))

def fill_gaps(ms, full, kind, skip):
    """OCR garbles some heading numbers (this font's ۴ and ۶ especially). When found headings jump
    from n to n+g and exactly g-1 unread headings start lines in between, number those in order."""
    heads = [m for m in re.finditer(rf'(?m)^[ \t]*({kind})(?![{L}])[^\S\n]*(\S*[^{L}\s]\S*)?[^\S\n]*', full)
             if not skip(m.start(1))]
    out = []
    for i, (s, e, n) in enumerate(ms):
        out.append((s, e, n, False))
        if i + 1 < len(ms):
            s2, n2 = ms[i+1][0], ms[i+1][2]
            between = [m for m in heads if e <= m.start(1) < s2]
            if n2 - n > 1 and len(between) == n2 - n - 1:
                out += [(m.start(1), m.end(), n + k + 1, True) for k, m in enumerate(between)]
    return out

def _sequences(nums):
    """Two whole numbered texts printed one after the other (a law and its supplement). Try each
    restart at 1 as the split; keep it only if both sides hold a long clean run from the start."""
    def run(lo, hi):
        c = _chain(nums, [lo <= i < hi for i in range(len(nums))])
        if len(c) < 20 or nums[c[0]] > 3: return None
        return c if len(c) >= 0.8 * max(nums[i] for i in c) else None
    best = []
    for p in range(1, len(nums)):
        if nums[p] != 1: continue
        a, b = run(0, p), run(p, len(nums))
        if a and b and len(a) + len(b) > len(best): best = a + b
    return best

def longest_run(nums):
    """Pick whichever strategy yields the most sequence-like numbering."""
    if not nums: return []
    single = _chain(nums, [True]*len(nums))
    seq = _sequences(nums)
    if seq: return seq      # its own test is stricter than the score, which can't see two texts
    multi  = _segments(nums)
    cands = [c for c in (single, multi) if c]
    if not cands: return []
    return max(cands, key=lambda c: (round(score(nums, c), 2), len(c)))

def main():
    rows, total = [], 0
    for path in sorted(glob.glob(os.path.join(DATA, "text", "*.json"))):
        doc = json.load(open(path, encoding="utf-8"))
        full, offs, toc = "", [], []
        for pg in doc["pages"]:
            offs.append((len(full), pg["page"]))
            t = repair(pg["text"])
            if toc_page(t): toc.append((len(full), len(full) + len(t)))
            full += t + "\n"
        in_toc = lambda i: any(a <= i < b for a, b in toc)
        best = None
        for kind in ('اص[سص]?ل', 'ماد[هدة]', 'بند', 'تبصره'):
            # headings listed in a table of contents would otherwise compete with the real ones
            ms = [m for m in markers(full, kind) if not in_toc(m[0])]
            keep = longest_run([n for _, _, n in ms])
            if best is None or len(keep) > len(best[1]):
                best = (kind, [ms[i] for i in keep])
        kind, ms = best
        ms = fill_gaps(ms, full, kind, in_toc)
        arts = []
        for i, (s, e, n, inferred) in enumerate(ms):
            stop = ms[i+1][0] if i+1 < len(ms) else len(full)
            body = full[e:stop].strip(" :ـ-–—\n\t")
            page = max((p for off, p in offs if off <= s), default=1)
            arts.append({"n": n, "kind": kind, "page": page, "text": body} | ({"n_inferred": True} if inferred else {}))
        slug = os.path.basename(path)[:-5]
        nums_k = [a["n"] for a in arts]
        conf = round(min(len(arts), max(nums_k))/max(len(arts), max(nums_k)), 3) if arts else 0.0
        json.dump({"source_pdf": doc["source_pdf"], "unit": kind, "seq_score": conf, "articles": arts},
                  open(os.path.join(DATA, "articles", slug + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        rows.append((len(arts), kind, arts[-1]["n"] if arts else 0, doc["source_pdf"]))
        total += len(arts)
    rows.sort(key=lambda r: -r[0])
    print(f"{'ARTS':>5} {'UNIT':<6}{'LAST':>5}  DOCUMENT"); print("-"*74)
    for n, k, last, src in rows: print(f"{n:>5} {k:<6}{last:>5}  {src[:50]}")
    print(f"\nTOTAL: {total} articles across {len(rows)} documents")

if __name__ == "__main__":
    os.makedirs(os.path.join(DATA, "articles"), exist_ok=True)
    main()

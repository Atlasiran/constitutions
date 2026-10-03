# Our own vocabularies

What neither Constitute (`../`) nor the Sartori layers (`../sartori/`) cover, and what every Iranian draft has to
answer: language, and who holds which power. `pipeline/own.py` merges these files into the `extra` block of
`../topics.json`; tags and scores live in `data/topics/<uid>.json` (plan 7.15).

| File | What it is | Used as |
|---|---|---|
| `lang.json` | 27 items on the status and use of languages, in 5 groups. Built on the areas of life in Part III of the European Charter for Regional or Minority Languages (arts. 8–14) and on the Framework Convention for the Protection of National Minorities (arts. 9–14, 17), plus status questions (which languages are official, at which level, who decides). Each item cites the article it follows (`s`). | article tags `lang:<key>` in `x` |
| `levels.json` | Six levels of government for a policy field: national (`N`), national law with regional execution (`NR`), national principles with regional detail (`P`), shared (`C`), regional (`R`), local (`L`). Named generically, so they fit federal drafts (federation/state) and unitary ones (centre/province). | `lv: {"cap:<code>": level}` on an article that assigns the field |
| `rai.json` | The ten dimensions of the Regional Authority Index v.3 and their scales, paraphrased from the RAI-Region codebook (16 April 2021). | `rai` per document: a score per dimension, the articles it rests on, a note in both languages |

## Rules

- **Levels** are recorded only where an article assigns the field to a level. Rights and aims carry none. A field
  divided among articles appears under each level it is given.
- **Language** tags follow the rule for every tag here: the article lays the rule down; mentioning a language is
  not enough.
- **RAI** scores read the text only, for the draft's most authoritative regional tier. Where the text is silent the
  note says the score rests on silence. The index was made to score countries as they work; here it scores what a
  draft says.

## Licence and attribution

- `lang.json` and `levels.json`: our own work, under this repository's licence. The Council of Europe treaties are
  cited, not quoted.
- `rai.json`: scales paraphrased from Hooghe, Marks, Schakel, Chapman Osterkatz, Niedzwiecki and Shair-Rosenfield,
  *Measuring Regional Authority* (Oxford University Press, 2016) and the RAI v.3 codebooks
  (<https://garymarks.web.unc.edu/data/regional-authority/>). The RAI v.3 data are listed on EUI Research Data
  (Cadmus) under CC BY 4.0. That listing was seen in search results on 2026-10-03, and the record page refused
  automated access, so confirm the licence by hand before citing it as checked. The scores are ours.

The Persian of all three files was written in the Claude Code session of 2026-10-03 and is a draft (`status` absent
means draft).

# Qanun Atlas — اسناد بنیادین

A corpus of Iranian constitutions, constitutional proposals, and political programmes, split into articles, tagged by topic, compared by text similarity, and audited against international human-rights law. It is the «اسناد بنیادین» tab of [AtlasIran.org](https://atlasiran.org/constitutions) ([Atlas-website](https://github.com/Atlasiran/Atlas-website)), which mounts it as a git submodule.

Documents are assessed against international human-rights law (UDHR, ICCPR, ICESCR and the other instruments listed in [normalcy](https://github.com/jomhoor/normalcy)). The 1979 constitution of the Islamic Republic is in the corpus as one document assessed like any other, never as a reference point.

## Layout

| Path | Contents |
|---|---|
| `(پیشنهادهای پیش‌نویس) قانون اساسی/` | source PDFs |
| `data/registry.json` | the single source of truth: one entry per document, keyed by a stable `uid` |
| `data/text/`, `data/vision/`, `data/proof/` | page text, Claude vision readings of scanned pages, and proofreading corrections |
| `data/articles/`, `catalog.json`, `analysis.json`, `editions.json` | articles, the catalog, similarity and keyword topics, edition alignments |
| `data/ontology/` | topic vocabularies: Constitute's, layers from the [Sartori repository](https://github.com/conceptintegration/sartori-repo) (`sartori/`), and our own (`own/`); Persian labels in `fa.json` files |
| `data/topics/`, `data/audits/` | article tags against the vocabularies, and human-rights audits, per document |
| `data/harvest/`, `data/additions/` | documents collected from Atlas organisations' links, and documents added from elsewhere |
| `pipeline/` | the Python pipeline |
| `site/` | the browser app (`site/index.html`, `app.js`, `site/data/`, `site/pdf/`) |
| `vendor/normalcy` | the benchmark service (git submodule) |

## Registry fields

Each entry has a `kind`, which decides what the document may be compared with. Kinds fall into four groups and comparisons stay within a group: `constitution` and `constitution_proposal`; `bylaws`; `charter`, `program` and `ideology`; `treatise`. `org_ids` links a document to Atlas organisations, and is only set where the link is documented. Editions of one draft share a `series` and carry a `rev`.

## Running the pipeline

Needs `poppler` (`pdftotext`, `pdfinfo`, `pdftoppm`) and `tesseract`.

```sh
git clone --recurse-submodules https://github.com/Atlasiran/constitutions.git
cd constitutions
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
for s in extract ocr articles catalog analyze editions publish_pdfs build_site; do .venv/bin/python pipeline/$s.py; done
```

`extract.py` keeps OCR'd text unless given `--force`. Then serve `site/` with any static server, e.g. `python3 -m http.server -d site`. `build_site.py --preview` also shows audits nobody has approved yet, for a local look.

The other scripts run when their inputs change:

| Script | What it does |
|---|---|
| `harvest.py`, `add_docs.py` | bring new documents into the registry |
| `vision_ocr.py`, `proofread.py` | read scanned pages and proofread text with Claude (Batch API; needs `ANTHROPIC_API_KEY`) |
| `ontology.py`, `sartori.py`, `own.py` | rebuild `data/ontology/topics.json` from the vocabularies |
| `audit.py` | audit documents through normalcy's `/v1/audit` (needs `NORMALCY_URL`, `NORMALCY_KEY`) |
| `build_module.py` | package `site/` into `dist/` for Atlas, with `org-index.json`; refuses a preview build |

Paid calls are cached by content hash, so nothing is re-queried when its inputs are unchanged.

## Licence

The code and our own data are AGPL 3. The vocabularies in `data/ontology/` are not: Constitute's is CC BY-NC 3.0, the Sartori layers CC BY-NC-SA 4.0, and tags made against them carry the same terms. See the README in each folder for attribution.

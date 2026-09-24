# Qanun Atlas — اسناد بنیادین

A corpus of Iranian constitutions, constitutional proposals, and political programmes, split into articles, tagged by topic, and compared by text similarity. It will become the «اسناد بنیادین» tab of [AtlasIran.org](https://github.com/Atlasiran/Atlas-website).

Documents are assessed against international human-rights law (UDHR, ICCPR, ICESCR and the other instruments listed in [normalcy](https://github.com/jomhoor/normalcy)). The 1979 constitution of the Islamic Republic is in the corpus as one document assessed like any other, never as a reference point.

## Layout

| Path | Contents |
|---|---|
| `(پیشنهادهای پیش‌نویس) قانون اساسی/` | source PDFs |
| `data/registry.json` | the single source of truth: one entry per document, keyed by a stable `uid` |
| `data/` | derived text, articles, catalog and analysis |
| `pipeline/` | the Python pipeline |
| `site/` | the browser app (`site/index.html` + `site/data/`) |
| `vendor/normalcy` | the benchmark service (git submodule) |

## Registry fields

Each entry has a `kind`, which decides what the document may be compared with: `constitution` and `constitution_proposal` go together; `bylaws` only with bylaws; `charter`, `program` and `ideology` together. `org_ids` links a document to Atlas organisations, and is only set where the link is documented.

## Running the pipeline

Needs `poppler` (`pdftotext`, `pdfinfo`, `pdftoppm`) and `tesseract`.

```sh
git clone --recurse-submodules https://github.com/Atlasiran/constitutions.git
cd constitutions
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
for s in extract ocr articles catalog analyze build_site; do .venv/bin/python pipeline/$s.py; done
```

`extract.py` keeps OCR'd text unless given `--force`. Then serve `site/` with any static server, e.g. `python3 -m http.server -d site`.

## Licence

AGPL 3

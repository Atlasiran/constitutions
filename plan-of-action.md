# Plan of action: Atlas × constitutions × normalcy

This is the reference for anyone, human or agent, continuing this work. It records what exists, what has been decided, which rules are not negotiable, and what comes next.
Last updated: 2026-10-04. Update the **Status** column and the **Log** at the bottom as work lands.

---

## 1. Rules (not negotiable)

1. **No AI attribution in git.** No `Co-Authored-By` lines naming Claude or any bot, no "Generated with…" lines, no session links, in commits or PRs. The author is always the user's own git identity (`armantorkzaban`). Never pass `--author` and never change `user.name` or `user.email`. This is enforced in `~/.claude/settings.json` (`attribution` set to empty) and `~/.claude/CLAUDE.md`.
2. **The Islamic Republic of Iran is never a reference point.** Its 1979 constitution and its treaty ratifications are not benchmarks. The UN Independent International Fact-Finding Mission on Iran concluded on 2026-09-17 that the authorities committed crimes against humanity. The 1979 constitution stays in the corpus **only** as a document assessed like any other.
3. **The benchmark (متن بالادستی) is international human-rights law** (see §5). Every document type may be compared against it.
4. **Like is compared only with like.** Bylaws go with bylaws, constitutions with constitutions. Bylaws are **never** compared with constitution proposals.
5. **No connection without a source.** Relations between organisations (membership, affiliation and so on) are only shown with a cited public source and a status. Never infer them from summaries. *(The Democratic Platform was wrongly linked to PJAK from an unverified automated summary of the Wikipedia page. It is its own organisation.)*
6. **Store reference texts verbatim.** The AI must cite provisions that exist in stored text. Any cited provision ID that doesn't exist is rejected.
7. **Batch and cache. Never re-query unchanged input.** Results are keyed by content hash + scoring-guide version + benchmark version + model.
8. Pushing, creating repos, deploying and other outward-facing actions need the user's go-ahead unless it was already given for that specific action.

---

## 2. Repositories and structure

```
Atlasiran/Atlas-website            ← main site (AtlasIran.org)
└── modules/constitutions          ← git submodule: Atlasiran/constitutions (public; to be created)
    └── vendor/normalcy            ← git submodule: jomhoor/normalcy
```

| Repo | Local path | Remote | Stack | Deploy |
|---|---|---|---|---|
| Atlas | `~/Development/TCF-IT-Projects/Atlas-website` | `github.com/Atlasiran/Atlas-website` | SvelteKit 2 (Svelte 4), Tailwind 3, MDsveX, Supabase | GitHub Pages (`ADAPTER=static`, custom domain atlasiran.org, base `''`) + Cloudflare |
| constitutions | `~/Development/TCF-IT-Projects/constitutions` | `github.com/Atlasiran/constitutions` (public, AGPL-3.0) | Python pipeline + a single-file vanilla JS site (`site/index.html`, "Constitutions Atlas") | Cloudflare Pages project `Constitutions-atlas-dev` (standalone preview) |
| normalcy | `~/Development/IV/normalcy` | `github.com/jomhoor/normalcy` | Cloudflare Worker (TypeScript), `@anthropic-ai/sdk` | **normalcy.is** (domain added in Cloudflare; Worker route not configured yet) |

**Who uses what:**
- normalcy serves **Atlas** and **constitutions** now. **Jomhoor** (via the Taraaz API, Gate 2) comes later; it isn't ready yet.
- Atlas never calls normalcy live. It reads audit results committed as JSON in constitutions.
- The constitutions pipeline calls normalcy in batch.

---

## 3. Current state (facts found 2026-09-24)

### constitutions
- 34 active documents in `data/registry.json`, the single source of truth, keyed by a stable `uid`. PDFs are in `(پیشنهادهای پیش‌نویس) قانون اساسی/` (51 MB), derived data in `data/` (14 MB), and browser data in `site/data/` (`articles.json` is 2.7 MB).
- Pipeline: `extract.py` → `ocr.py` (tesseract `fas`/`ara` in `pipeline/tessdata`) → `articles.py` → `analyze.py` (TF-IDF similarity + keyword topic tags, 25 constitution-oriented topics) → `catalog.py` → `build_site.py`.
- Pipeline paths are relative to the repo (fixed 2026-09-24). Run with `.venv/bin/python pipeline/<step>.py` (`requirements.txt`: numpy). Order: extract → ocr → articles → **catalog → analyze** (analyze reads `catalog.json`) → build_site. `extract.py` keeps OCR'd texts unless `--force`.
- Site: tabs corpus / map / compare / search; English by default; fonts Newsreader + Vazirmatn.
- `local/` is gitignored and holds the Democratic Platform PDF.

### Atlas
- 226 organisations, one `.md` per organisation in `src/content/org-pages/`. Frontmatter fields include `id, org_type, name_fa, name_en, manifest, coc, …`. A `relations` field exists since branch `org-relations` (§8).
- The CSV has a free-text column `ائتلاف ،‌ همکاری` (coalition / cooperation; 48 of 343 rows), and some coalition rows list members under `ملاحظات`. Neither reaches the pages. They name coalitions, not org ids, and cite no source, so they are leads for §8, not data.
- `manifest` is filled for 104 organisations, `coc` for 4. Values are mostly external URLs; one is a local PDF (`static/docs/pjak-constitution-7th-congress.pdf`). `manifest` mixes charters, مرامنامه and bylaws (اساسنامه).
- Political types shown at `/parties`: `حزب`, `سازمان سیاسی`, `شورا / کنگره / ائتلاف`. Everything else is shown at `/groups`.
- Data flow: CSV in `data/` (gitignored; a local export of the team's «Source of Truth» spreadsheet, **not** Supabase) → `deploy/csv_to_json.py` → `deploy/update_org_pages.py` (data.json → md) → `npm run build` (`md_to_json.py` → `static/data/data.json`, then Vite).
- The graph (`/graph`, from `deploy/gen_gexf.py`) only has org → country "BASED IN" edges.
- Nav links live in `src/content/configs.js` (`defaultHeaderLinks`). Organisation pages are rendered in `src/routes/op/[page]/+page.svelte`; the «مرامنامه یا مانیفست» block is around line 280.
- Design tokens: navy `#1E3A6B`, sky `#8CDAF5`, teal `#0EBB90`, beige `#EDE3C7`, background `#F4F6F7`, font Shabnam. Right-to-left, Persian first.
- OG images are generated locally (`npm run gen:og`) and committed. Don't regenerate them in CI.

### normalcy
- `main` is at `e9ae4fa` (branch `scafolding-mvp` by Fatemeh Khodadadi, fast-forwarded and pushed). `copilot/normative-compliance-policy` was already merged. The history contains 3 older `copilot-swe-agent[bot]` commits; they were left as they are because rewriting published history is destructive.
- Worker endpoints:
  - `GET /`: test UI
  - `POST /check`: async, bearer `SHARED_SECRET`, sends a callback when done
  - `POST /check-sync`: bearer `SHARED_SECRET` (since 2026-09-24)
  - `POST /receive`: a stub that echoes the callback, for local testing
- **Uncommitted local changes** (review and commit as the user):
  - SDK `^0.32` → `^0.128.0`
  - model `claude-sonnet-4-5` → `claude-opus-5`
  - adaptive thinking
  - `max_tokens` 1024 → 16000
  - strict JSON-schema output (`output_config.format`)
  - automatic refusal fallback: `fallbacks: "default"` with beta `server-side-fallback-2026-07-01`
  - a stop reason other than `end_turn` now throws instead of silently returning `non_compliant`; `/check-sync` returns 502
  - `skipLibCheck` in tsconfig
  - Type check passes. **No live API call has been made.**
- Known gaps:
  - The README lists 12 sources, but the prompt names only 8 (it's missing the Genocide Convention, CED, the Rome Statute and Yogyakarta).
  - No instrument texts are stored, so citations come from the model's memory.
  - `wrangler.toml` is gitignored. Commit one without secrets that has the normalcy.is route.
  - `.dev.vars` holds secrets and stays ignored.

---

## 4. Decisions

| Topic | Decision |
|---|---|
| Repo nesting | Atlas ⊃ constitutions ⊃ normalcy (submodules). CI needs `submodules: recursive`. Cloudflare needs the nested repos to be public. |
| Constitutions repo | `Atlasiran/constitutions`, public (AGPL like Atlas) |
| Integration into Atlas | The constitutions UI is refactored into `app.js` exporting `mount(el, { lang, base, dataUrl })`. An Atlas route `src/routes/constitutions/+page.svelte` renders Atlas's header and footer and calls `mount()`. Build output is copied to `static/constitutions/` before the Vite build. All URLs are relative to `base`. |
| Styling | `atlas-theme.css` in constitutions mirrors Atlas's tokens. All CSS is scoped under `.qa-root`. Persian is the default when embedded. |
| Tab name | «اطلس اسناد بنیادین» |
| Treatises | Their own comparison group D (Yek Kalameh, Velayat-e Faqih), not compared with constitutions |
| Source PDFs | Plain git (no LFS; GitHub Pages can't serve LFS files) |
| مرامنامه (coc) | Grouped with charters/programmes, **not** with bylaws |
| Democratic Platform | Its own new Atlas entry (not listed as of 2026-09-24). The document is published and labelled «پیش‌نویس برای بررسی و تصویب» (`doc_status: draft`). **No PJAK link.** |
| naoruz.com | Corpus only (one person's project, jurist Jahan Asadi). No Atlas entry. Only the constitution is a corpus document; the manifesto, English version, graphics and essays are linked companions. |
| Model | `claude-opus-5` by default; Claude Sonnet 5 is an option for high-volume Gate 2 (the user's call). **Pipeline scripts** (`vision_ocr.py`, `proofread.py`, `ontology.py`, the coming `tag_topics.py`): `claude-opus-5-5`, cheaper per token (user, 2026-10-03). Its thinking can't be turned off, so effort is set instead: `low` for OCR, `medium` for proofreading and tagging. Pages read or proofread under `claude-opus-5` stay valid (`EARLIER` in `vision_ocr.py`), so nothing is redone. normalcy keeps its own setting |
| Scoring guide per kind | `audit-constitution` for constitution, constitution_proposal, charter, program, ideology, treatise (what the document promises for the country); `audit-org` for bylaws (internal democracy + Tier 2). Set by each guide's `applies_to` in normalcy `rubrics/*.json`. |
| Audit segments | Articles when `articles.py` found them reliably (`seq_score` ≥ 0.5, mean article ≤ 4,000 chars), otherwise pages. Registry `pages` ranges are honoured. |

---

## 5. The benchmark (متن بالادستی)

**Tier 1: applies to every document**
1. UDHR
2. ICCPR
3. ICESCR
4. Genocide Convention
5. CAT
6. ICERD
7. CRC
8. CEDAW
9. CRPD
10. CED (enforced disappearance)
11. Rome Statute of the ICC
12. Yogyakarta Principles + YP+10

**Tier 2: organisational documents (non-binding guidelines)**
- OSCE/ODIHR–Venice Commission *Guidelines on Political Party Regulation* (2nd ed., 2020), for parties.
- OSCE/ODIHR–Venice Commission *Joint Guidelines on Freedom of Association* (2015), for NGOs and civil society.

**Storage in normalcy**
- Each instrument is split into provisions with stable IDs such as `ICCPR.19.3`, stored as `{id, instrument, number, text_en, text_fa, fa_status, source_url, source_version}`.
- English is authoritative. The UDHR has a UN-published Persian translation; the rest need vetted translations marked `fa_status: unofficial`, shown next to the English.

**How documents are assessed**
- Each right in the checklist gets one of these verdicts:

  | Verdict | Meaning |
  |---|---|
  | `guaranteed` | explicitly protected |
  | `restricted_clawback` | protected but taken back by a clause such as «در چارچوب قانون/موازین اسلامی» ("within the framework of law / Islamic standards") |
  | `silent` | not mentioned |
  | `contradicted` | the document goes against it |
  | `disputed` | reviewers disagree |

- Every verdict cites the document's articles **and** the benchmark provision IDs it rests on. A person reviews it; an audit can be published before that only when the user decides so (`review.publish: true`), and its page then says it is not yet reviewed (user, 2026-09-25, for the 1368 constitution).
- **Silence matters here,** unlike in Gate 2 post moderation, where only endorsing a violation counts.
- A public methodology page, the reviewer's name and date, and a way for organisations to submit corrections.

---

## 6. Data model: the constitutions registry

New fields for each entry in `data/registry.json`:

| Field | Purpose |
|---|---|
| `kind` | `constitution` · `constitution_proposal` · `bylaws` · `charter` · `program` · `ideology` (مرامنامه) · `treatise` · `benchmark`. **This enforces rule 4.** |
| `org_ids` | Atlas organisation ids the document belongs to. This powers the compare button and `org-index.json`. |
| `pages` | `[from, to]`, so one PDF can become several documents (the Democratic Platform file holds bylaws, a charter and a programme outline) |
| `doc_status` | `draft` / `adopted` |
| `source_url` | Where the document was taken from |
| `version` | Tells editions apart and ties cached audit results to the exact text |

**Comparison groups** (the compare view only offers documents from the same group):
- **A:** `constitution`, `constitution_proposal`
- **B:** `bylaws`
- **C:** `charter`, `program`, `ideology`
- **Benchmark:** can be compared with any group, through that group's scoring guide.

Topic lists are defined per group. The bylaws list: membership, internal elections, term limits, rotation of leadership, quorum and decision-making, minority and faction rights, discipline and appeals, finances and transparency, gender parity, oversight bodies, amendment, dissolution or merger.

**Output for Atlas:** the pipeline writes `org-index.json` (organisation id → documents). Atlas's existing `manifest`/`coc` fields stay as they are.

---

## 7. Normalcy: service design

**Demo at normalcy.is (build this first)**
- a browsable library of the benchmark texts (no AI involved)
- a "try a text" checker behind Cloudflare Turnstile bot protection and a rate limit, with results cached
- showcase audits of the constitutions corpus

**API v1**

| Endpoint | Access | Purpose |
|---|---|---|
| `GET /v1/instruments`, `GET /v1/provisions/{id}` | public, cached | reference texts |
| `POST /v1/audit` → `GET /v1/audit/{job}` | API key (constitutions, Atlas) | batch document audits |
| `POST /v1/check` | Jomhoor key, **off until Jomhoor is ready** | Gate 2 post moderation |

**Cost and accuracy**
- **Result cache** (D1 or KV) keyed by `sha256(normalized_text + rubric_version + benchmark_version + model)`. A hit never reaches the model.
- **Bulk audits** go through the **Message Batches API** (asynchronous, half price). Results are committed to constitutions as versioned JSON.
- **Only relevant provisions:** each article is sent with the benchmark provisions relevant to its topic, placed in a stable prefix with `cache_control`. Check that `usage.cache_read_input_tokens` is above 0.
- **Citation check:** cited provision IDs are validated against the stored texts; unknown IDs mean the verdict is rejected.
- **Three scoring guides:** `gate2-post` (endorsement), `audit-constitution`, `audit-org` (Tier 1 + Tier 2).

---

## 8. Atlas: connections and affiliations (new feature)

Add to the organisation frontmatter, as **one line of JSON** (valid YAML for MDsveX; `md_to_json.py` and the CSV sync read frontmatter line by line, so a nested YAML block would break):
```yaml
relations: [{"type": "member_of", "target": "310", "since": "", "until": "", "source": "https://…", "status": "self_declared"}]
# type: member_of | affiliated_with | coalition_partner | split_from | merged_into | successor_of
# target: Atlas org id · source: required · status: self_declared | documented | disputed
```
- Stored in one direction only. The reverse link ("members: …") is generated in `md_to_json.py`.
- Organisation pages get a new section «پیوندها و وابستگی‌ها», grouped by type, with dates and a source link. Coalition pages (`شورا / کنگره / ائتلاف`) list their members automatically.
- `gen_gexf.py` adds these as graph edges, coloured by type.
- `update_org_pages.py` keeps the `relations` line during the CSV sync (it only rewrites keys it knows; tested 2026-09-25).
- `md_to_json.py` writes `static/data/relations.json` (gitignored, built) and **stops the build** on a relation with no source URL, or an unknown type, status or target.
- `gen_gexf.py` reads relations from `data.json`, so run it after `md_to_json.py`, not straight after `csv_to_json.py`.
- The edit/create forms and Supabase need a relations table.
- Only publicly declared or documented ties (rule 5). A disputed tie is marked disputed, never shown as fact.
- Separate from documents: an alliance doesn't make two organisations' documents comparable.

---

## 9. New documents: details

**naoruz.com**
- «قانون اساسی ایالات متحده ایران» ("Constitution of the United States of Iran"), a federal model by the jurist Jahan Asadi (جهان اسدی), 2026. Registry uid `naoruz-usi-2026`.
- Main text (`kind: constitution_proposal`): `https://naoruz.com/wp-content/uploads/2026/07/قانون-اساسی-_3_.pdf`. The `_3_` is its number in the site's 7-file series, not a version. The PDF was made with "Microsoft Print to PDF", which leaves a broken text layer, so the corpus text is OCR.
- Everything else is a **companion** of that one document (registry `companions`: title, role, URL). None is a separate corpus document:
  - `1_مانیفست-نوروز.pdf` (2022, 30 pages): the author's commentary on his own draft, citing its articles, plus chapters on the transition and coalitions. As a `charter` it would sit in group C next to party programmes while mostly restating the constitution.
  - `3_Constitution_USI_E_I.pdf`: the author's own English version (March 2026). Use it for this document's English text (1.1) instead of a translation of ours. Check it against the July Persian text first.
  - Two graphics (transition, structure), the flag, and two history essays (federalism elsewhere; Iran's constitutional history).
- German versions of all seven also exist on the site; not recorded.

**Democratic Platform of Iran (پلتفرم دموکراتیک ایران)**
- File: `local/_اساسنامه_و_نظام_سازمانی_و_منشور_سیاسی_پلتفرم_دموکراتیک_ایران.pdf`. 75 pages, a Word export, dated 2026-09-21.
- Metadata: «نسخه نهایی ممیزی‌شده برای بررسی و تصویب» ("final audited version for review and approval").
- ⚠️ The text layer is garbled: ی characters are dropped and ligatures broken (e.g. «مشود» for «می‌شود»). Use OCR or a normalisation pass, not raw `pdftotext`.
- Contents: bylaws + organisational structure, political charter, programme outline. Split them by page range into `bylaws`, `charter` and `program`.
- Page ranges (checked 2026-09-25): cover p. 1; bylaws + organisational structure pp. 2–21 (appendix table p. 21); programme outline pp. 22–26; charter pp. 27–75 (its contents list pp. 27–30, text from p. 31). Registry uids `dp-bylaws-2026`, `dp-program-2026`, `dp-charter-2026`, all `org_ids: ["440"]`.
- Atlas entry (id 440, branch `democratic-platform`, from a row in the source CSV):
  - org_type `شورا / کنگره / ائتلاف`; English name Democratic Platform of Iran; alternative spelling «پلاتفرم»
  - **Not verified, so left empty:** founded 21 Dey 1396 (2018-01-11), Brussels, and website `https://www.iran-dp.com/`. These come from fa.wikipedia, which cites ANF (403 to scripted fetches); iran-dp.com does not resolve (2026-09-25). No logo source.
  - `manifest` points to the PDF in this repo on GitHub (live once pushed).
  - fa.wikipedia says PJAK is a «گروه همکار» (cooperating group), citing pjak.eu. Per the user's decision this is **not** recorded; if it is ever added, it needs the pjak.eu page read first-hand and status `self_declared`.
  - It was searched for in the org pages, the CSV and data.json, and was not listed.

**Harvest pilot (5.3, 2026-09-25)**
- Collection `org-documents`, `type: program`, `org_ids` from the Atlas entry that links the document. Reviewer decisions, corpus file names and registry fields live in `data/harvest/review.json`; `harvest.py ingest` writes the registry from it.
- A web page enters as a reading-copy PDF of its main text; its corpus text is taken from the HTML and cut at the reading copy's page breaks (matched on a letter skeleton, since the copy's text layer turns «لا» into «ال»).
- In: PDKI programme pp. 1–36 and bylaws pp. 37–56 (17th congress, Bahman 1403; pp. 57–60 history and cover), vision OCR. Fadaian (Majority) bylaws (12th congress, 1390), web page. Communist Party of Iran bylaws, one PDF linked by Atlas 276, 277 and 304, undated (reproduced October 2006). Iran Novin مرامنامه (adopted 6 Aban 1402), web page. Azerbaijan Democratic Party bylaws, web page, undated. Joint congress of democratic and federal republicans, «تفاهم‌نامه همکاری» (`charter`), undated (uploaded January 2026), vision OCR. Sepidar bylaws: the party's own PDF (August 2025, 47 articles), vision OCR.
- Sepidar's web page holds the party's bylaws followed by the older bylaws of the Sepidar cultural association (25 articles); the party's PDF, linked from that page, is a slightly different edition and is the one used.
- Fadaian's web page drops the article numbers (26 articles by its closing line), so it is audited by page.
- Dead: 311 Yarsan (404), 210 rcoir.com (domain gone). Try archive.org later.

---

## 10. Work plan

Status values: ☐ to do · ◐ in progress · ☑ done

### Phase 0: foundations
| # | Task | Status |
|---|---|---|
| 0.1 | Replace the hardcoded absolute paths in `pipeline/*.py` with paths relative to the repo; re-run the pipeline end to end | ☑ |
| 0.2 | `git init` constitutions; add `.gitignore` (`.wrangler`, `__pycache__`, `local/`); create `Atlasiran/constitutions` (public) *(ask before creating or pushing)* | ☑ public at github.com/Atlasiran/constitutions |
| 0.3 | Add normalcy as a submodule at `vendor/normalcy` | ☑ |
| 0.4 | Add the registry fields (§6) and backfill the 34 documents (mostly `kind`) | ☑ `pages` honoured: one articles file per entry (`<slug>__<uid>.json`) |
| 0.5 | Commit the normalcy SDK and model upgrade (as the user) | ☑ `920349e`, pushed |
| 0.6 | normalcy: merge the other branches into main | ☑ |
| 0.7 | Global no-AI-attribution settings | ☑ |

### Phase 1: normalcy demo (first priority)
| # | Task | Status |
|---|---|---|
| 1.1 | Store the Tier 1 + Tier 2 texts as provision JSON (English + Persian, with sources) | ◐ English done (15 instruments, 1,907 IDs); Persian pending |
| 1.2 | Lock down `/check-sync` (Turnstile, rate limit); make the README and prompt agree on the 12 sources | ◐ done except Turnstile keys (code ready, not configured) |
| 1.3 | Commit a `wrangler.toml` without secrets, with the normalcy.is route | ☑ |
| 1.4 | Demo site: benchmark library, try-a-text checker, showcase audits; deploy to normalcy.is *(ask before deploying)* | ◐ live; checker verified live; showcase audits wait on the first corpus audit (5.4) |

### Phase 2: normalcy API
| # | Task | Status |
|---|---|---|
| 2.1 | Result cache (D1/KV) keyed by content hash | ☑ KV; deployed |
| 2.2 | `/v1/audit` through the Batch API; relevant-provision selection; cached prefix; citation check | ◐ deployed; first real batch pending the `API_KEYS` secret |
| 2.3 | `/v1/instruments`, `/v1/provisions`; API keys per client; `/v1/check` off for Jomhoor | ◐ deployed; user to set `API_KEYS` (only a `constitutions` key: Atlas reads committed JSON and needs none) |
| 2.4 | Three scoring guides: gate2-post, audit-constitution, audit-org | ☑ |

### Phase 3: constitutions tab in Atlas
| # | Task | Status |
|---|---|---|
| 3.1 | Refactor the site into `app.js` + `mount()`, add `atlas-theme.css`, scope CSS under `.qa-root`, Persian default | ☑ `0f8c94f`…`affa214` |
| 3.2 | Build step producing `dist/` + `org-index.json` | ☑ `pipeline/build_module.py [--out DIR]` (stdlib; Atlas runs it from the submodule) |
| 3.3 | Atlas: submodule at `modules/constitutions`, copy step before build, `/constitutions` route, «اطلس اسناد بنیادین» nav entry, prerender entries | ☑ Atlas `5ffde5f` on main; assets go to `static/modules/constitutions/` (not `static/constitutions/`, which would collide with the `/constitutions` page) |
| 3.4 | CI `submodules: recursive`; Cloudflare nested submodules; test under base `/Atlas-website` | ☑ live on atlasiran.org (Cloudflare) and atlasiran.github.io/Atlas-website (Pages); both checked headless |

### Phase 4: new documents
| # | Task | Status |
|---|---|---|
| 4.1 | naoruz: download, registry entry (constitution; manifesto and attachments as companions), OCR, rebuild | ☑ `naoruz-usi-2026`, 202 articles; companions and `source_url` not yet shown on the site |
| 4.2 | Democratic Platform: OCR/normalise, split into 3 documents, `doc_status: draft` | ☑ `39274a9`: bylaws 52 articles, charter 17, programme by page |
| 4.3 | Democratic Platform: new Atlas org page, logo, OG image, `manifest` link, **no PJAK relation** | ◐ imported the documented way (CSV row → csv_to_json → update_org_pages → gen:og → gen_gexf → build) on Atlas branch `democratic-platform` (`14edc91`, not pushed), id 440; founding facts, website and logo wait on a primary source |

### Phase 5: comparison
| # | Task | Status |
|---|---|---|
| 5.1 | Compare view limited to one comparison group; deep-link parameters | ☑ groups A/B/C + D (treatises); `#compare=a,b[,topic]`, `#search=…`, `#map` |
| 5.2 | «مقایسه اساسنامه» / «مقایسه منشور» ("compare bylaws" / "compare charter") button on `/op/[page]`, shown only when a comparable document exists | ☐ |
| 5.3 | Ingest the PJAK PDF from Atlas `static/docs/`; harvest the 104 `manifest`/`coc` links (download → classify → extract → link to organisation, with review) | ◐ `pipeline/harvest.py` (list → fetch → report → review → ingest). Pilot of 10 orgs: 8 documents in (see §9); 2 dead links. PJAK: programme pp. 1–53, bylaws pp. 54–65, garbled text layer, re-read with vision OCR (65 pages ≈ $1.3). The other 90 links next |
| 5.4 | Benchmark audit through the batch pipeline; rights matrix with citations; methodology page; review workflow | ◐ `pipeline/audit.py` (submit/collect → `data/audits/<uid>.json`, review status `unreviewed`). Test run on `iri-constitution-1979` done 2026-09-25: 22 of 31 verdicts passed the checks, 9 were rejected for citing articles 21/31/41/61/171 that the old split had missed (fixed since), 1 quote warning, ≈ $0.40. Result is local (`data/audits/iri-constitution-1979.json`), not committed, not reviewed, not published |
| 5.5 | **Constitution benchmark audit, remaining** (rubric `audit-constitution`; documents of kind `constitution` / `constitution_proposal` only; bylaws, charters and programmes go through `audit-org`, never against constitutions): (1) finish the corpus text: collect the running vision batches, then proofread every page (`pipeline/proofread.py`) and rebuild; (2) re-run `iri-constitution-1979` on its corrected split and confirm 0 rejected; (3) submit all remaining constitution documents (≈ $15–20, Batch API) and collect; (4) re-check rejected verdicts and quote warnings, and fix their cause (text or split) before re-running; (5) human review of each audit, sign-off recorded in its `review` field; (6) publish: rights view with citations and methodology in the constitutions tab («حقوق بشر», `#rights=<uid>`), showcase audits on normalcy.is (1.4) | ◐ showcase first (user, 2026-09-25): `iri-constitution-1979` now reads the complete 1368 text (lu.ac.ir PDF, vision-read, proofread; 177 articles; the 46 «اصل سابق» wordings kept out of the audit), audited 2026-09-25 (0 rejected, 2 quote warnings: «family» abridged with «…», «work» off by one word and corrected, noted in `review.notes`; ≈ $0.40); published in the rights view marked not yet reviewed (`review.publish`). Next: human review; then the other constitutions. **Order (user, 2026-10-03): the federal drafts first**, each proofread → tagged against the vocabulary (7.10) → audited: `naoruz-usi-2026` (proofread, tagged and audited ☑: audited 2026-10-03 in the Claude Code session, as the API account had no credit, against the same rubric, benchmark and article segments as `audit.py`, every citation checked by the same rules, 0 warnings; 24 guaranteed, 4 clawback (fair trial: art. 32 lets the law except judicial hearing; nationality: deprivation left to law; disability: art. 144 parents exercise political rights; emergency: art. 39 waives the statute in serious danger, no non-derogable rights), 3 silent (slavery, disappearance, incitement); published unreviewed, the page says it was read in a session), then `arshadnejad-federal-1405` (8 pp.), `shajarian-transitional-1399` (14), `left-socialists-federal-1381` (63), `tabriz-federal-2018` (81), `iran4all-federal-v3-1405` (98): 264 pages to proofread. Of Banisadr's drafts only the latest (`banisadr-constitution-1398`, 379 pp.) is to be worked on, later. Every other document, bylaws and programmes included, waits |

### Phase 6: Atlas connections
| # | Task | Status |
|---|---|---|
| 6.1 | `relations` schema; reverse links generated in `md_to_json.py` | ☑ Atlas branch `org-relations` (`573feb2`, not pushed) |
| 6.2 | «پیوندها و وابستگی‌ها» section; coalition member lists | ☑ same branch; checked in a static build with a temporary relation |
| 6.3 | Graph edges in `gen_gexf.py` | ☑ same branch |
| 6.4 | Make `update_org_pages.py` keep `relations`; edit-form and Supabase support | ◐ the sync keeps it (no change needed); edit form/Supabase not done (Supabase is not the live data source) |
| 6.5 | First relations data: sourced ties only (leads: the CSV coalition column) | ☐ |

---

## 11. Pitfalls

- **Persian PDFs:** Word exports often have broken glyph mapping. Check the extracted text before splitting into articles; the OCR fallback is `pipeline/ocr.py`. A legacy font can map glyphs to *valid but wrong* Persian letters (Tabriz draft: «هرکس هطالعاتی تبریس»), which the letter check in `ocr.py` can't see. Check new documents by the share of their words found in at least two other documents (all good texts score ≥ 0.78; Tabriz scored 0.20), and force OCR with `ocr.py <uid>`.
- **Page-level Tesseract drops whole lines** on clean typeset pages (up to a fifth of a page; e.g. the equal-pay line of the naoruz draft). Use `ocr.py --lines <uid>`: each text line is cut out and read on its own (psm 13), final «ی» is restored from the corpus vocabulary, and a stray «» read for «،» is fixed. Line mode doesn't work on scans with decorative frames or skew (Pars, Shajarian), and white-on-dark covers fall back to page mode (and may still come back empty).
- **Tables of contents** list «اصل N title … page» rows that compete with the real headings in `articles.py`. Pages where most lines end in a number are skipped.
- **Garbled heading numbers:** some fonts' digits are misread (Tabriz: ۴ → ۶/؛/ء/4, ۶ → 1/٩). `articles.py` numbers unread line-start headings in order only when exactly the missing count sits between two found ones, and marks them `n_inferred`. A block misread the same way (Tabriz 60–69 read as 10–19) is not fixable by rule: re-read those pages with vision (next item).
- **Vision OCR** (`pipeline/vision_ocr.py`) is the fix for scans and for fonts Tesseract misreads: Claude Opus 5 reads each page image (2576 px long edge, thinking off) through the Batch API, about $0.02 a page. Raw readings are cached in `data/vision/<slug>.json` keyed by PDF hash + page + model + prompt version; clean-up (Persian digits, page numbers, spaced «ـ» → « - ») runs at write time, so changing it needs no new reading. The key is `ANTHROPIC_API_KEY` in `local/anthropic.env`; normalcy's proxy only serves audits. `test <uid> <page>` first, then `submit`, `collect`.
- **Benchmark version** hashes the English text and IDs only, so adding Persian translations doesn't invalidate cached audits.
- **Atlas base path:** Pages serves at the root of atlasiran.org (custom domain), so the base is `''` since 2026-10-02; atlasiran.github.io/Atlas-website now answers 404. Still never hardcode absolute URLs in the constitutions module: it must work under any base.
- **Cloudflare Pages** only clones public submodules. Keep Atlas, constitutions and normalcy public, or change the deploy approach.
- **Claude API:** use `output_config.format` for JSON (not prefill; prefill returns 400 on current models). Check `stop_reason` before reading content. Stream when `max_tokens` is over about 16K. `fallbacks` isn't supported on the Batches API, so handle `refusal` results per item there.
- **Prompt caching** only kicks in above the model's minimum prefix size, and any change in the prefix bytes invalidates it (no timestamps or IDs in the system prompt).
- **`extract.py` and vision texts:** it used to keep only `source: "ocr"` texts, so a plain run would have overwritten the vision-read ones with `pdftotext` output. Fixed 2026-09-25 (it keeps `ocr` and `vision`).
- **Adding an org to Atlas:** use the README flow, never a hand-written page (`/parties` reads `political_parties.json`, which only `csv_to_json.py` writes). Run `md_to_json.py` first, because `csv_to_json.py` takes `logo` from the stale committed `data.json`. The CSV export uses CRLF, has LF inside cells, and has no final newline; edit it byte-exact (`newline=''`).
- **OG images:** `gen_org_og_images.py` needs Pillow's basic layout (fixed in Atlas `b0f9a6f`); with raqm the Persian came out reversed.
- **«لا» in Word and InDesign PDFs:** `pdftotext` turns the ligature into «ال» («میالدی»، «تشکیالت»), which can't be undone by rule. Found in 6 older corpus texts (Banisadr 1398: 268 words; the CPI (ML) draft: 98; Banisadr 1397: 94; Nayeb Hashem provisional: 26; NCRI ten articles: 23; Mostashar: 15) and in the harvested PDKI, con-dfr, Sepidar and PJAK PDFs. Fix: vision OCR (all six re-read in full on 2026-09-25, 1,012 pages ≈ $20; the session-5 note that their text layer was right missed this). Check a new PDF for «الف/الع/الت» inside words before accepting its text layer.
- **`articles.py` on unlabelled lists:** without «اصل/ماده» headings it now falls back to lines numbered «1.» when one clean run from 1 covers ≥ 80% of numbered lines (Azerbaijan Democratic Party: 31). A single stray «ماده N» (a cross-reference or the closing count) still yields one false article (Fadaian, Mostashar, Worker Unity, Khomeini); treating fewer than 3 as none would change existing counts, so it is left for review.
- **A stalled batch may be an empty credit balance.** On 2026-10-02 two vision batches sat at 0 pages read for almost five hours; direct calls then failed with «credit balance is too low». Check the balance before waiting on a batch; `vision_ocr.py read <uid>` reads the remaining pages directly (full price, 6 in parallel, same cache).
- **Heading variants `articles.py` now accepts:** «بیست وششم» (no space after «و»; Green Jurists v1–v4, Andishgah, Mashruteh, Ansari, Banisadr, whose inferred headings are now read), «دویست سی ام» (no «و» after the hundreds; Shirzad), «مادهٔ ۱» (small hamza; IOCCI), and «۲-۸:» chapter-article numbers without a unit word, used only when fewer than 10 labelled headings exist (iran4all; `n` is the running number, `label` the printed one, and the site shows the label). A document whose lower level restarts inside each higher one sets `split_unit` in the registry (INC: «اصل»).
- **More heading spellings in vision text:** the hundreds split by a ZWNJ or space («یک‌صد», «سی صد»; the old text layers had «یکصد») and «شست» for «شصت». Without them Banisadr 1398 fell from 529 to 149 articles after its re-read. Compare article counts before and after any re-read.
- **Vision readings can carry HTML** (`<u>`, `<sup>` around underlined headings and footnote marks; Banisadr, Parsa, Mostashar). `clean()` strips them at write time.
- **Kashida («ـ») stays in the stored readings,** as printed, and `repair()` removes it wherever text is used (articles, similarity, audits). Measure text quality on repaired text: raw PDKI/PJAK score 0.64–0.70 word coverage only because of kashida. Side effect: a word-final kashida before a space joins two words (about a dozen cases, e.g. Banisadr «شودـ برقرار»), the same rule that correctly rejoins Khomeini's split words («سـ همی»).
- **Running headers and footers survive some vision readings** although the prompt says to leave them out (Green Jurists v1–v3: «نسخه سوم – تهیه شده توسط کانون حقوقدانان ایران | 13 | https://greenlawyers.wordpress.com» inside articles; Parsa 1396, PJAK, IOCCI, Khomeini likewise). `articles.py` `running_lines()` drops lines of 15+ characters that recur at the top or bottom (first/last three lines) of at least 3 pages and a fifth of the document, and lines made only of them plus separators and a page number. Counting only page edges matters: Green Jurists v4 repeats «گزینه دو: رئیس جمهور (جمهوری ریاستی)» mid-page as content.
- **A draft printed inside a book** (1358 draft: pp. 12–30 of a 483-page volume; Green Jurists v4: pp. 58–100): registry `pages`, and `publish_pdfs.py` publishes the other pages blank at their size with a pointer to the full source, so page links still match (36.7 → 0.8 MB).
- **Editions diff:** spelling, digits and spacing differ between a web text and a vision reading of the next edition. The site compares texts with kashida, ZWNJ, vowel marks, letter variants and whitespace removed before calling an article unchanged, and diffs punctuation as separate tokens.
- **Vision readings drop a word-final «ی» after «ق», «گ» and «ئ»** in fonts that draw it as a flat swoop (naoruz: «حقوقی» read as «حقوق» six times, «رسیدگی» → «رسیدگ», «ویژگی» → «ویژگ», «شرطهائی» → «شرطهائ»). «حقوق» is still a word, so no spell check finds it: tell final «ق» (round bowl) from «قی» (wide flat swoop) on the image. Grep a vision text for words ending in a bare «گ» or «ئ», and for «حقوق» followed by «در/تا/که/و» where an adjective is meant.
- **Vision readings also correct the author's typos** («خوداری» → «خودداری», «عموی» → «عمومی», naoruz). The corpus keeps the printed form; a proofreader restores it.
- **Web summaries are not sources.** Verify facts such as membership, dates and URLs against primary sources before publishing (rule 5).

---

## 12. Expansion: more drafts, article wiring, participation (proposed 2026-10-02)

Source: the user's ideas in `local/notes.md` (gitignored), sorted and checked against the registry on 2026-10-02. Nothing here is built yet.

### Design

**Article graph ("wiring")**
- Three edge types, each with its evidence: `xref` (an article cites another in the same document: «طبق اصل ۱۱۰», parsed by rule), `similar` (two proposals word the same provision alike: today's TF-IDF edges, later multilingual embeddings computed locally, so no text leaves the pipeline), `power` (checks and balances, below). Every edge gets a stable id (`<uid>:<art>→<uid>:<art>:<type>`) so comments can attach to it.
- **Checks and balances:** for each `constitution` / `constitution_proposal`, extract organs (parliament, head of state, government, courts, constitutional court, leader, councils) and their powers over each other: appoints, removes, vetoes, approves, oversees, judges, dissolves, amends. Each power cites its article (rule 6: an unknown article id rejects the item). Done through the Batch API, cached by content hash like the audits. Output per document: a power graph plus measures: organs no other organ can remove or review, appointment chains, judicial review, the amendment procedure.
- **The "PCB" view:** the document as a wall of articles; edges drawn behind as orthogonal circuit traces; hover lights a trace, click opens the linked article and its comments. One document (or a pair) at a time, not the whole corpus.

**Participation**
- A separate Worker in this repo (`worker/`, Cloudflare D1), not in normalcy: normalcy stays the benchmark service. It calls normalcy for screening.
- No login. Turnstile + per-IP rate limit (the code pattern already exists in normalcy, 1.2). Store no raw IP: a salted hash, salt rotated daily. No email asked.
- Comment targets: a document, an article or an edge.
- A **cron job** (Cloudflare Cron Trigger) processes the queue: spam and language filters, a normalcy check (the Gate 2 `gate2-post` rubric, enabled for a `constitutions` key, still off for Jomhoor), dedup against existing comments. Then `pending` → `visible` / `rejected`, with the reason kept.
- The site reads visible comments live from the Worker, cached. A daily GitHub Action exports them as JSON into the repo: archive and transparency, and the static build keeps working if the Worker is down.
- **Contributions** (the **+** button): a new article, an amendment to one, or a new link. Same screening, plus: similar existing articles, a diff against the base text (additions green, removals red), and links suggested automatically. Shown grey beside their target until confirmed.
- **Votes:** up and down, one per browser. Without identity a vote is a signal, not a decision. The AI's assessment (duplication, language, normalcy) is shown as one labelled advisory score, never counted as a voter.
- **Who decides:** admins confirm, guided by votes, until Jomhoor can verify real, unique Iranians; then referendum-like votes decide (Phase 11).
- **AI assistant** at the bottom of the page: questions about the corpus, answered only with citations to stored articles (rule 6), behind Turnstile and a rate limit, with answers cached.

### Decisions needed
1. **What we co-author.** Annotations and amendments on the existing drafts, or one community draft? IOCCI (ghanoonasasi.org) already runs an open co-drafting wiki and forum for one text, and iran4all compares drafts. Recommendation: talk to both before Phase 10; build comments (Phase 9) regardless, since annotation of all drafts against the benchmark is what we have that they don't.
2. ~~"An AI input at the bottom like open alice": which product is meant?~~ Answered 2026-10-02: a chat box, a text input like a chat assistant's, to talk with the texts (answers cite stored articles). Deferred to a later phase: it costs API money per question.
3. ~~"Center for transitional justice": ICTJ, or a specific Iranian centre?~~ Answered 2026-10-02: **Center for Transitional Justice for Iran** («مرکز عدالت انتقالی برای ایران», ctjcenter.org, Canada); more from the user later. Besides outreach, its "Democratic Constitutional Design" programme is worth checking for documents and resources.
4. Comment languages (Persian only, or also English, Kurdish, Azerbaijani Turkish…) and the moderation policy text, published before launch.

### Phase 7: more drafts
| # | Task | Status |
|---|---|---|
| 7.1 | Ingest the new drafts (sources and dedup in `local/notes.md` §1): IOCCI interim law v3 (37 pp.), iran4all federal constitution v3.0.0 (98 pp.), Arshadnejad federal draft (8 pp.), all three with garbled text layers → vision OCR (≈ $3); Kaveh Shirzad 1384 and the Iranian National Congress draft (web text; prefer the original host); Green Jurists v2 (Dey 1388, the missing edition); We The People of Iran (web, constitutional monarchy) | ☑ 8 documents (2026-10-02): the seven named plus **Green Jurists v4** (Tir 1403, Iranian Lawyers Association / Shahab Shabahang; found on their blog), via `pipeline/add_docs.py` + `data/additions/2026-10.json`. Articles: Shirzad 267, iran4all 258 (numbered «فصل-ماده», shown as «۲-۸»), Green Jurists v2 and v4 154 each, WTP 112, IOCCI 74, Arshadnejad 13 («اصل» › «ماده»), INC 7 (`split_unit: اصل`). Word coverage 0.92–1.00, no broken «لا» |
| 7.2 | Duplicates: Juya on pezhvakeiran.com → second `source_url` of `juya-transitional-1397` (check for a revision) | ☑ Not a duplicate: Pezhvak carries the **1393 edition** (May 2014): the same 70 «اصل» in the same order, plainer wording, no cross-references. Added as `juya-transitional-1393`, series `juya` (rev 1 → 1397 rev 2) |
| 7.3 | Editions: a `series` field linking versions of one draft (Green Jurists v1–v3, Iran-e No r12/r13, iran4all 1.00–3.00, IOCCI 1–3); a version diff view (green/red), which Phase 10 reuses | ☑ iran4all's older versions were added, then dropped at the user's call (only 3.00 kept). `pipeline/editions.py` aligns the articles of every pair of editions in order by word overlap (→ `data/editions.json`); the site's «ویرایش‌ها» tab shows a word diff per article (removed red, added green), deep link `#editions=<series>,<uid>,<uid>`. Only series with a `rev` count as editions (Saginian's monarchy/republic are variants). IOCCI publishes only v3; v1 and v2 not found |
| 7.4 | Companions: the Rahgosha interview with the IOCCI drafters (YouTube); Arshadnejad's «میثاق حقوق ذاتی، طبیعی و بنیادین ایرانیان» | ☑ both attached in 7.1 |
| 7.5 | Leads: the 1358 draft constitution (find a primary source); the iransolidarity.com PDF linked by Kamarei (2005); the «جمهوری پادشاهی» draft | ☑ **1358 draft** added (`draft-constitution-1358`): the scan on Wikimedia Commons of the Majlis's guide to the Assembly of Experts' proceedings, pp. 12–30, vision OCR. **iransolidarity PDF** = Adlan Parsa, «پیش‌نویس قانون اساسی جمهوری ایران» (Azar 1382); domain parked, taken from the Wayback Machine (`parsa-adlan-1382`). **«جمهوری پادشاهی»**: a 48-article bilingual post by the pseudonymous user «کیمیا» on the wikiran.net forum (Oct 2025); not added: the user decided to leave it out (2026-10-02) |
| 7.6 | Comparative Constitutions Project / Constitute: assess its topic ontology against our 25 topics; licence check before any reuse | ☑ assessed: 334 leaf topics under 66 parent groups, 330 with a coding question (definition + question; labels in English, Spanish, Arabic; no Persian). Licence: Constitute's About page puts site content under **CC BY-NC 3.0** Unported (not 4.0), except material copyrighted by others; its Terms forbid commercial use and fees. Its English constitution texts (HeinOnline, Oxford) are not reusable. Adopted for group A (2026-10-02, user): all coded topics, not a subset; see 7.7–7.11 |
| 7.7 | Licence and attribution for the vocabulary | ◐ `data/ontology/README.md`: CC BY-NC 3.0, outside the repo's AGPL, attribution text. QDR's dataset entry states no separate licence. The site credit line goes in with 7.11, when topics are first shown |
| 7.8 | `pipeline/ontology.py`: import the vocabulary and map every leaf to one of our groups | ☑ `fetch` stores `constitute-topics.xml` + `source.json` (sha256); the build writes `topics.json`: 334 leaves, 0 unmapped, `version` hashes XML + mapping (stable across runs). Five groups added beside the 25: principles, international, oversight, social, transition. A leaf whose parents disagree must get a `LEAF` entry or the build stops |
| 7.9 | Persian labels (draft) for the vocabulary | ◐ All 334 written in the Claude Code session (2026-10-03, user: use the plan's credit, not API credit), `fa_status: draft`, in `fa.json`; checked by script for the orthography rules (tanvin, «ه‌ی», hamza, Arabic letters, detached «می/ها/تر», «به‌…»). Foreign terms keep the original on first use (Amparo, Ombudsman, Organic laws, Habeas corpus, Conscientious objection). `ontology.py fa` (Opus 5.5, medium) stays as the API route. Next: the user reviews, most frequent topics first |
| 7.10 | `pipeline/tag_topics.py`: tag group-A articles against the vocabulary (Batch API, cache by text hash + ontology version + prompt + model, rule-6 check on article numbers); pilot on `iri-constitution-1979` + Green Jurists v4 with a hand check of ~50 articles and the cost, then the rest of group A | ◐ Pilot moved to the federal drafts and done in the Claude Code session (user, 2026-10-03): `naoruz-usi-2026` → `data/topics/naoruz-usi-2026.json` (202 articles, each with its text hash; ontology `bda4ef8caa29`; prompt `session-1`; rule-6 check passed). 176 of 334 leaves present; 29 articles carry no Constitute topic (transport, energy, agriculture, statistics: subjects Constitute doesn't code). Not yet reviewed. `tag_topics.py` (API) not written; the next federal drafts can be tagged the same way |
| 7.11 | Use the tags: `analyze.py` (`ccp` leaves; our groups derived; keyword tags stay for B/C/D and untagged documents), `build_site.py`, compare view grouped by parent and expandable to leaves (`#compare=a,b,<leaf>`), credit line, rebuild | ◐ First piece (user, 2026-10-03: "I want to see the result of the audit on Jahan's work"): a «موضوع‌ها» / Topics tab (`#topics=<uid>[,<leaf>]`): coverage count and bar, the observation, the gaps worth noting with their topics and article links, every group with its present leaves (articles, definition, text, PDF page) and absent ones, method and the CC BY-NC credit line. `build_site.py` writes `site/data/topics.json` on the audits' terms (reviewed or `review.publish`, else only with `--preview`); `build_module.py` refuses a preview. Live on atlasiran.org since 2026-10-03 (`#topics=naoruz-usi-2026`), marked not yet reviewed and experimental, with the progress line (1 of 39) and the «واژگان» panel. Not done: `analyze.py`/compare view (`ccp` leaves) |
| 7.12 | **Before the Topics tab is announced** (user, 2026-10-03: it's experimental until these are done) | ☐ (1) human review of `naoruz-usi-2026`: the 202 articles' tags, the 10 gaps, and the Swiss observation (☑ checked 2026-10-03 against the English text on fedlex, version 3 March 2024: every parallel holds; added that art. 78 drops Swiss 70(1), the federation's own official languages, and art. 191 generalises Swiss 186(2)), plus the human-rights audit (5.5) and the 7.15 coding (levels, language, regional authority); then `review.status: approved`. (2) Review of the Persian topic names, the 176 present in this draft first; `fa_status` → reviewed. (3) A second document tagged, so the tab has something to compare with: the 1368 constitution (`iri-constitution-1979`) as the baseline, and the next federal draft (`arshadnejad-federal-1405`, 8 pp.). (4) Optional: send Jahan Asadi the result before it's announced, so the author can answer or correct a misreading. (5) Close 7.7: the credit line is on the site; check its wording against Constitute's attribution request |
| 7.13 | Topics: the rest, after 7.12 | ☐ (1) proofread and tag the other federal drafts in order (5.5): Shajarian, Left Socialists, Tabriz, Iran4All (≈ 256 pp.). (2) `pipeline/tag_topics.py`, the API route, when there is API credit; the session tags stay valid under their prompt version. (3) The compare view by leaf (`analyze.py` `ccp`, `#compare=a,b,<leaf>`), and a cross-document view: which drafts have a given topic. (4) The benchmark audit (5.5) of each tagged draft, linked from its Topics page. (5) Banisadr 1398, later; then the rest of group A. (6) ◐ Method page live (`#topics=method`, 2026-10-03): what it measures, the vocabulary, the text, tagging, what «آمده»/«نیامده» mean, gaps and observations, review, limits, source and licence, followed by the vocabulary; linked from the end of every document's page (the link at the top removed, user 2026-10-03). Still missing: a way to report a wrong tag (needs a public channel: GitHub issues or an address, user's call) |
| 7.15 | Our own vocabularies for what neither Constitute nor Sartori covers: language and the division of powers (user, 2026-10-03: "an important topic for anything written for Iran") | ◐ `pipeline/own.py` merges `data/ontology/own/` into `topics.json` `extra` (version now `114ff5a618d9`): **levels** (national; national law, regional execution; national principles, regional detail; shared; regional; local), recorded per policy-field tag as `lv`; **`lang:`** 27 items on status and use of languages, after ECRML Part III (arts. 8–14) and FCNM (arts. 9–14, 17), each citing its article; **RAI**: the 10 dimensions of the Regional Authority Index v.3 (Hooghe, Marks, Schakel et al.; scales paraphrased from the RAI-Region codebook, April 2021; data CC BY 4.0 per the EUI record as listed in search, the record page refused automated access, confirm by hand), scored per document as `rai`. Naoruz coded: 137 levels (82 national, 18 shared, 15 regional, 10 local, 8 principles, 4 national law/regional execution; art. 55's municipal tasks and art. 197 tagged for this); 12 language tags (5, 20, 77, 78), absent: official language of the federation, courts, administration, schools, media, names, signs; RAI 23/30 (self-rule 15/18, shared rule 8/12), the main brake art. 191 (federal approval of every state enactment, instdepth 2). New gap in its findings: no official language for the federal institutions. Site: panels «هر حوزه با کیست», «اقتدار منطقه‌ای», «زبان»; method page section «افزوده‌های خود ما»; intro, limits, licence, credit. **Next:** (1) review with 7.12 (1); (2) Persian of the 27 language items with 7.12 (2) (they count in «Persian still to review»); (3) a Swiss benchmark for the RAI panel from the RAI-Region dataset (the v.3 zip on garymarks.web.unc.edu holds documentation only; the scores are on EUI Cadmus); (4) code the next federal drafts the same way; (5) offer the language list and levels to Sartori with 7.14 (3) |
| 7.14 | Sartori repository (github.com/conceptintegration/sartori-repo): what to take from its 11 vocabularies, and contribute back | ◐ Reviewed and adopted (user, 2026-10-03). **Licences checked at source first:** the repo is CC BY-NC-SA 4.0; CAP's codebooks CC BY-NC-SA 4.0 (its Copyright page; the ND licence is the OUP chapter's); Juon CPSD and Strøm IDC CC0 on Dataverse. `pipeline/sartori.py` fetches the files pinned at commit `0fa9ca3` (2026-05-27) into `data/ontology/sartori/` (own README and licence, ShareAlike) and builds three layers into `topics.json` `extra` (own version `4847f89e10a3`; Constitute's `bda4ef8caa29` unchanged): **`ccp:`** democracy, rule of law, social security (the only CCP-FACET/HIER topics Constitute lacks; FACET's grounds of discrimination were already `equalgr1`–`16`, `votemin` is under `voteres`), counted with the 334 → 337; **`cap:`** CAP's 213 policy topics; **`ps:`** power-sharing, Juon's 75 + 18 of Strøm's 36 (implemented-only and Constitute-duplicate items left out). Persian for all 309 + 21 CAP headings drafted in the session (`sartori/fa.json`, orthography-checked; Juon's composed office × mechanism). `naoruz-usi-2026` tagged against the layers (field `x`, prompt `session-1-extra`): 122 articles with a policy field; 25 of the 29 with no Constitute topic now placed (left: 7, 155, 162, 192); power-sharing present: elected state and municipal government, municipal police, own tax rates, regional upper-house constituencies, proportional lower house, mandated grand coalition and representation of nations in the cabinet (181), regionally representative military command (65). Site: CAP and power-sharing panels on each document's page, vocabulary panel by vocabulary, intro, method page and credit updated; not yet deployed. Not taken: IDEA-GLO, GLOBALCIT-GLO, NDI-ET, IDEA-DT (glossaries; possible later for elections, citizenship, transition), NC-DCC, FJC-IDB. **Next:** (1) review the layer tags with 7.12 (1) and the Persian with 7.12 (2); (2) `sartori.py check` now and then for upstream changes (reminder in `local/notes.md`); (3) contribute back, after review: see the list below the table of 7.14 |
| 7.16 | Concept map, after sartori.network (user, 2026-10-04): not a site of our own and not a copy of Sartori's graph (a Retina/sigma.js viewer of one GEXF: 2,115 concepts of the 11 vocabularies, 26,840 links, 8,422 across vocabularies, no documents). Ours: links from our documents | ☐ After 7.12 (1), since links inherit wrong tags. A «نقشه‌ی مفاهیم» panel in the Topics tab: nodes = concepts of our tag sets (Constitute + `ccp:`, `cap:`, `ps:`, `lang:`, levels), sized by number of documents; an edge where the same articles carry both concepts, across vocabularies, each edge listing its articles (the evidence Sartori lacks). Static JSON, light enough for readers inside Iran; Persian first. Our vocabularies get published through Sartori (7.14 (3)), not a parallel registry. Don't link to sartori.network from our pages: it is served by a Vite dev server on one VM. Sits beside the article graph (phase 8), not instead of it |

**7.14, contributing back to Sartori** (after the Persian is reviewed; their submission template asks for original or authorised work, a full citation, and a DOI or institutional page, and does not accept self-published ontologies yet):
- A Persian edition of the CCP vocabulary (keys = Constitute's, label and definition in Persian): our 334 + 3. Licence to check first: our labels derive from Constitute (CC BY-NC 3.0) and would be offered under the repo's CC BY-NC-SA 4.0; ask CCP and the Sartori maintainers. Needs a citable home (Zenodo DOI or the project's page).
- Persian for CAP-TOP, JUON-CPSD and STRØM-IDC (ShareAlike allows it), same route.
- The `example` column: for each topic, a Persian article from an Iranian draft that has it, with the document and article number: real segments, which their format asks for and few ontologies have.
- Small fixes as issues or PRs: JUON-CPSD labels 11 and 17 repeat «(ethnic / specific organization)», 57 lacks its closing parenthesis; «apopint» in STRØM-IDC `japptbr`; CCP-FACET and CCP-HIER have «Citation: TBD».
- The gap we found (CAP has nothing on language policy, and nothing on who holds which competence beyond «Intergovernmental Relations») is now filled on our side (7.15): offer the 27-item language vocabulary and the levels scheme as new ontologies, with Iranian examples, once reviewed.

### Phase 8: article graph
Topic tagging by meaning (Constitute vocabulary) moved earlier, to 7.7–7.11.
| # | Task | Status |
|---|---|---|
| 8.1 | `xref` edges: parse cross-references within each document; precision check on 3 documents by hand | ☐ |
| 8.2 | Stable edge ids; `edges.json` with type and evidence; existing similarity edges migrated | ☐ |
| 8.3 | Checks and balances: extraction rubric, pilot on one document (cost measured), then the constitution group; power graph + measures | ☐ |
| 8.4 | "PCB" view in the site: traces, hover, click-through; Persian RTL; works embedded in Atlas | ☐ |

### Phase 9: comments (no login)
| # | Task | Status |
|---|---|---|
| 9.1 | `worker/`: D1 schema (comments, targets, votes, moderation log), `POST /comments` (Turnstile, rate limit, size limit), `GET /comments?target=` | ☐ |
| 9.2 | Cron moderation: filters, normalcy Gate 2 check for the `constitutions` key, dedup; reasons kept | ☐ |
| 9.3 | Site: comments under each article, then on edges (needs 8.2) | ☐ |
| 9.4 | Daily export of visible comments to the repo (GitHub Action) | ☐ |
| 9.5 | Moderation policy and privacy note, published; check that Turnstile works from inside Iran (with and without VPN) | ☐ |
| 9.6 | Deploy *(ask before deploying)* | ☐ |

### Phase 10: contributions and co-authoring (after decision 1)
| # | Task | Status |
|---|---|---|
| 10.1 | **+** button: new article / amendment / link; compose mode with the page faded to 10% | ☐ |
| 10.2 | Live suggestions while typing: similar articles, normalcy issues, diff against the base text | ☐ |
| 10.3 | Lifecycle: submitted → screened → pending (grey) → voted → confirmed / rejected | ☐ |
| 10.4 | Votes; AI advisory score shown separately | ☐ |
| 10.5 | Admin console (confirm, reject with reason, merge duplicates) | ☐ |
| 10.6 | AI assistant with validated citations | ☐ |

### Phase 11: verified voting
| # | Task | Status |
|---|---|---|
| 11.1 | Jomhoor identity (real, unique Iranians) as the gate for binding votes; referendum-like procedure. **Waits on Jomhoor** | ☐ |

### Phase 12: simulation
| # | Task | Status |
|---|---|---|
| 12.1 | 5,000 synthetic users and entries (legit and abusive) in a **staging** database only, labelled synthetic, never shown as real participation: moderation throughput, AI cost per entry, sybil resistance of votes, UI performance | ☐ |

### Phase 13: outreach
| # | Task | Status |
|---|---|---|
| 13.1 | Contact list in `local/` (personal data, never in git): authors of corpus documents, Atlas organisations, IOCCI, iran4all, CCP, a transitional justice centre | ☐ |
| 13.2 | Talk to IOCCI and iran4all (decision 1) *(ask before contacting anyone)* | ☐ |
| 13.3 | Invitations to the platform once Phase 9 is live; a conference of drafters | ☐ |

**Order:** 7 and 13.1 now (cheap, unblock the rest); 8.1–8.2 and 9 next, in parallel (9.3 on edges needs 8.2); 8.3 after a costed pilot; 10 after decision 1 and 12; 11 when Jomhoor is ready.

---

## 13. Log
- **2026-09-24:**
  - Plan agreed.
  - normalcy: `scafolding-mvp` fast-forwarded into `main` and pushed.
  - normalcy SDK and model upgrade made locally (not committed).
  - Global no-AI-attribution settings added.
  - normalcy.is added to Cloudflare domains (by the user).
  - Democratic Platform confirmed missing from Atlas; its PJAK link dropped.
  - Connections feature added (Phase 6).
- **2026-09-24 (implementation, session 2):**
  - 0.1: pipeline paths made repo-relative; full run reproduces `site/data/*` byte-for-byte.
  - `ocr.py` misflagged `fakhravar-charter-1397` (bilingual Persian/English, tatweel-justified) and OCR scrambled its columns. Detection now ignores tatweel and counts Latin letters; the original `pdftotext` text was restored.
  - 0.4: `kind` / `org_ids` / `pages` / `doc_status` / `source_url` / `version` added to all 34 entries. `kind`: 26 constitution_proposal, 4 constitution, 2 program, 2 treatise. `catalog.py` rejects a missing or unknown `kind`.
  - `org_ids` set only where the author is exactly an Atlas org: `ncri-ten-articles-1397` → 30, `majame-eslami-1382` → 433. Other authors (WCUP, Pan-Iranist, CPI-MLM, Iran-e No, Andishgah, Pars, Tabriz center, Iranian National Congress) are not in Atlas; انجمن ایران نو ≠ حزب ایران نوین.
  - Rule 2: removed `baseline: true` from `iri-constitution-1979`; the compare view no longer defaults side A to the in-force (IRI) constitution.
  - 0.5: normalcy upgrade committed as `920349e` (not pushed). Model and API shape checked against the current Claude API reference.
- **2026-09-24 (session 3):**
  - Published `Atlasiran/constitutions` (public, AGPL-3.0, `df90d90`); normalcy added as a submodule at `vendor/normalcy`. Pushed normalcy `main`.
  - 1.1: `benchmark/build.py` in normalcy fetches 15 instruments from official sources (OHCHR, UNTC, legal.un.org, un.org, yogyakartaprinciples.org, venice.coe.int), pins them by SHA-256 in `sources.lock.json`, and writes verbatim provisions: 581 provisions, 1,907 citable IDs.
    - The Genocide Convention's only reachable source is an OCR'd UNTC scan, so its text is `benchmark/manual/genocide-en.txt`, corrected line by line against the page images.
    - The Rome Statute is the 2002 corrected text; the 2010/2017/2019 amendments are not included (the ICC site blocks scripted downloads).
    - Persian: no clean source was reachable. The OHCHR Persian UDHR PDF is image-only and OCR was too poor to publish, so `fa_status: pending` and the site links to the official PDF.
  - 1.2: `/check-sync` and `/receive` now need `SHARED_SECRET`. New public `/api/check` has a per-IP rate limit (5/min), optional Turnstile, and a KV cache keyed by text hash + rubric + benchmark + model. The prompt now names all 12 instruments.
  - 1.4: site live at https://normalcy.is (and www, and normalcy.torkzabanarman.workers.dev), styled after Atlas. It uses Worker routes in front of the existing proxied DNS records; MX/SPF records untouched. KV namespace `worker-normalcy-cache`.
  - Still needed from the user: `wrangler secret put ANTHROPIC_API_KEY` and `SHARED_SECRET`; optionally a Turnstile widget (site key in `wrangler.toml`, secret via `wrangler secret put TURNSTILE_SECRET`).
- **2026-09-24 (session 4):**
  - The user set `ANTHROPIC_API_KEY` and `SHARED_SECRET`. Live check on normalcy.is works (Opus 5, ~7.5 s, verdict with article citations). Small quirk: one reason contained a literal `\u2014` escape from the model's JSON.
  - Phase 2 in normalcy `ee7d768` (committed, not pushed or deployed):
    - `rubrics/audit-constitution.json` (31 rights) and `rubrics/audit-org.json` (14 items with Tier 2), each right tied to the provision IDs it rests on. `benchmark/rubrics.py` validates every ID, renders the cited articles verbatim (97 articles, ~85K chars for the constitutional guide) and versions each guide by content hash.
    - `/v1/audit`: KV cache by content + guide version + benchmark version + model; misses go to one Message Batch; the guide's benchmark block is a `cache_control` prefix (1 h TTL); strict JSON schema with every right required. On collection, unknown provision/segment IDs reject that verdict; quotes are checked against the document (Persian letter variants folded) and flagged if missing. Refusals and other stop reasons fail the item (`fallbacks` isn't available on Batches).
    - `/v1/instruments`, `/v1/provisions/{id}`, `/v1/rubrics` public with CORS; `/v1/check` answers 503 until `GATE2_ENABLED`.
  - constitutions: `pipeline/audit.py` (`--dry-run`, `submit`, `collect`). The corpus is 34 documents / 3.05M chars; 8 documents are cited by page because their article split is unreliable (e.g. cpi-mlm: 6 "articles", 275K chars). Submodule `vendor/normalcy` bumped to `ee7d768`.
  - To go live: push normalcy, `wrangler secret put API_KEYS`, deploy, then `NORMALCY_KEY=… pipeline/audit.py submit`. Estimated cost for the whole corpus at batch prices: roughly $10–20.
- **2026-09-24 (session 4, continued):**
  - Persian translations are not needed before auditing: the model reads the authoritative English, and translations are display text. The benchmark version now hashes English text + IDs only (normalcy `f677ded`; new version `f04ecff03b434da0`), so adding translations later won't invalidate audits.
  - OCR/text quality check (word coverage across the corpus): 32 of 33 distinct texts are usable. The OCR'd ones have scattered character errors but read fine. `tabriz-federal-2018` was garbage from a legacy font's wrong glyph map; it was re-OCR'd (`ocr.py` now takes explicit uids) and is now 131 clean articles. Downstream data rebuilt; only Tabriz changed.
  - normalcy pushed (`c7176ba`) and deployed (version `ca10da72`). Setting the `API_KEYS` secret was blocked for the agent; the user sets it. `audit.py` reads `NORMALCY_KEY` from the environment or `local/normalcy.env`.
- **2026-09-24 (session 4, Phase 3):**
  - First test audit failed: `invalid_request_error: Schema is too complex` (an object with one required property per right). Output is now a flat `findings` list; coverage is checked in `validate()` (normalcy `75591b9`, deployed). Batch errors now carry the API message.
  - The site is now a module (`site/app.js` `mount()`, `app.css` scoped to `.qa-root`, `atlas-theme.css`); `site/index.html` is a thin standalone shell. Embedded mode leaves `<html>`/`<body>` alone, follows Atlas's `.dark`, and hides its own title/intro.
  - Fixed a pre-existing RTL bug: timeline lane labels were clipped in Persian (SVG `text-anchor` flipped under `dir=rtl`).
  - Atlas branch `constitutions-tab`: submodule, `/constitutions` route, nav entry, build step, prerender entry, CI `submodules: recursive`. Built with `ADAPTER=static` and checked headless under `/Atlas-website/` (nav link, table of 34 documents, compare deep link, dark mode).
  - Noticed while building: Atlas's committed `static/data/data.json` is stale for org 310 (logo and `manifest` → local PJAK PDF); the build regenerates it. Left out of the tab commit.
  - `majame-eslami-1382` has 1 extracted article, so it's hidden from the compare view (needs > 5), although it's one of the two documents linked to an Atlas org. Relevant for 5.2.
  - Pushed and merged (fast-forward) into Atlas `main` as `5ffde5f` with the user's go-ahead. GitHub Pages workflow passed; atlasiran.org/constitutions is live too.
- **2026-09-25 (session 5):**
  - 4.1: added `naoruz-usi-2026`, «قانون اساسی ایالات متحده ایران» by the jurist Jahan Asadi (naoruz.com, 2026; no organisation). Only the constitution is a corpus document; the manifesto, English version, graphics, essays and flag are `companions` of the registry entry (new field: `fa`, `en`, `role`, `url`). Its PDF has no usable text layer, so the text is OCR.
  - Found that page-level OCR drops whole lines on typeset pages; added `ocr.py --lines` (see Pitfalls) and re-OCR'd naoruz, Green Jurists 1388, Majame and Tabriz with it. More text and fewer junk characters in all four; the Tabriz cover page kept its old OCR text.
  - `articles.py`: skip table-of-contents pages; fill garbled/unmatched headings between found ones (`n_inferred`). Articles: naoruz 202; Green Jurists 111 → 153; Tabriz 130 (many were contents rows) → 95; Mashruteh texts, Bani-Sadr, the Left Socialists draft and others recover compound-ordinal articles («بیست و یکم», «سیم»); Majame 1 → 0 (its single "article" was spurious). Corpus: 35 documents, 3,843 articles in the site data.
  - Still wrong: Tabriz heading numbers 60–69 and a few swaps need manual review; the scans (Pars, Shajarian) lose lines and Tesseract can't recover them. Hold their audits until fixed.
  - `audit.py collect` now loads only documents with pending jobs (a new registry entry without text crashed it).
  - Atlas submodule bumped to `4c58f17` (Atlas `8fe2418`): naoruz and the fuller texts are live after the Pages deploy.
  - Vision OCR (`vision_ocr.py`, see Pitfalls) for Pars, Shajarian and Tabriz: 120 pages, 615K input / 94K output tokens, ≈ $2.70 at batch price, no failures. Articles: Pars 60 → 199 (1–200; the draft itself skips 199), Tabriz 95 → 113 (1–113, none inferred), Shajarian 57 → 58 (no gap fills). Corpus: 4,203 catalog articles, 4,001 in the site data, 480 edges. These three are ready to audit.
  - Not OCR problems, left open: Majame is prose in numbered points, so it has no articles; Nasrahmadi (13 articles from 161 pages) nests «ماده» inside «بند «اصل» N», which `articles.py` doesn't model.
  - Vision OCR for 20 more documents (886 pages, ≈ $20, one page retried): the five Tesseract texts (naoruz, Green Jurists 1388, Left Socialists, Majame, Nasrahmadi) and every PDF-text document with extraction errors (reversed or lost «لا», dropped letters): Mashruteh supplement, Fakhravar, Aryanpour, Nayebhashem amendment, Iran-e No r12 and r13, Parsa, Pan-Iranist, both Andishgah texts, Ansari, Green Jurists 1396, Juya, WCUP, Jahanshahi. Left as PDF text, because their text layer is right and their odd words are vocabulary, author typos or lost ZWNJ: Mostashar, Khomeini, CPI-MLM, NCRI, both Bani-Sadr texts, both Saginian drafts, Nayebhashem provisional, Mashruteh 1906, the 1979 constitution. naoruz now reads «کوئیر» (queer), not «کوثیر».
  - `vision_ocr.py` clean-up also strips the markdown bold the model sometimes puts on headings.
  - `articles.py`:
    - compound ordinals ending «یکم»/«سیم» («هشتاد و یکم», «سی و سیم»);
    - a law printed with its supplement (Mashruteh 1906 editions: 51 + 107) or a part that restarts numbering (Saginian monarchy «بخش دوم») is split at the restart when both sides are long clean runs;
    - contents pages with dot leaders are skipped.
    
    Changes: 1979 constitution 161 → 176 of 177; Mashruteh 1906 163 (mixed) → 156; supplement 104 → 110 (107 plus the amended 36–40, headed again; its 14 and 95 are headed «فصل» in the source); Saginian monarchy 23 → 44; Left Socialists 160 (with duplicates) → 147 clean; inferred numbers fall across the corpus (e.g. Green Jurists 21 → 8). Corpus: 4,232 catalog articles, 4,226 in the site data, 525 edges.
- **2026-09-25 (session 6):**
  - Checked Atlas for the Democratic Platform in the source CSV (normalised spelling), the org pages and data.json: not listed. Atlas's org data comes from the local CSV export, not Supabase.
  - 0.4/4.2: registry `pages` honoured by articles/catalog/analyze/audit. The Democratic Platform PDF (75 pages) added as three documents; its garbled text layer replaced by vision OCR (1 batch, 385K in / 90K out tokens, ≈ $2.5, no failures). Bylaws: 52 articles, clean run; charter: 17 articles (it also numbers sub-articles «ماده ۱۳.۱», not split out), audited by page since its articles are long; programme: prose, by page. 38 documents, 4,301 catalog articles.
  - Fixed `extract.py` so it keeps vision-read texts.
  - 4.3: Atlas org page id 440 on branch `democratic-platform`, only facts from the document itself. See §9 for what is unverified.
  - 6.1–6.3 on Atlas branch `org-relations`; see §8. Tested with a temporary relation (Turkmens → joint congress): both pages render the section, the graph gets the edge, the CSV sync keeps the line, a sourceless relation stops the build. Fixture reverted; no relations are recorded.
  - Nothing pushed. Left alone: another session's uncommitted `pipeline/proofread.py`, `data/proof/`, `data/audits/` (first audit, iri-constitution-1979). Noticed for proofreading: the Parsa text ends 98 of 149 pages with the footer `www.ghanon.org`.
  - Redid 4.3 by the documented procedure (the hand-written page was discarded). The local CSV got the Democratic Platform row plus two values brought in line with hand edits: PJAK manifest `docs/pjak-constitution-7th-congress.pdf` and TCF website `https://transcf.org/about-us/` (the user mirrors these in the shared spreadsheet; backup in `data/`). Atlas `democratic-platform`: `b0f9a6f` OG layout fix, `14edc91` the org, `86e2516` regenerated OG images (footer now «AtlasIran.org»; PJAK's shows its logo).
- **2026-09-25 (session 6, continued):**
  - Showcase: the 1368 constitution (complete text from lu.ac.ir; the earlier PDF lacked article 4 and most of article 3) vision-read, proofread (9 corrections applied, 8 rejected where the page itself prints the typo), split into 177 articles with the 46 «اصل سابق» wordings kept apart, audited (0 rejected) and shown in the new «حقوق بشر» view.
  - Credit ran out mid-afternoon (the first re-audit failed with «credit balance is too low»); topped up by the user. The other session's 12 vision batches (1,129 pages) were cancelled at the user's request before any page was read; PDKI, PJAK and con-dfr are set inactive until re-read.
  - Proofreading: `pipeline/proofread.py` (image + text → exact find/replace corrections, applied only when the find is unique). Its corrections need checking: on this document 8 of 17 "fixed" typos the page itself prints; a rejected correction carries its reason and is never applied.
- **2026-09-25 (session 7):**
  - 5.3 pilot ingested (§9): PDKI programme and bylaws, Fadaian (Majority) bylaws, CPI bylaws, Iran Novin ideology, Azerbaijan Democratic Party bylaws, con-dfr charter, Sepidar bylaws (the party PDF, not the web page, which mixes in the older association bylaws), PJAK programme and bylaws (org 310, not 95). 48 registry entries.
  - Vision OCR: PDKI + con-dfr (64 pages), Sepidar (26), PJAK (65), and the six older texts with broken «لا» (1,012 pages in 11 batches).
- **2026-10-01:**
  - Source PDFs published with the site: `pipeline/publish_pdfs.py` writes `site/pdf/<uid>.pdf` (shared PDFs take the common uid parts: `dp-2026.pdf`), images downsampled to 150 dpi, original kept where that is not smaller or a page renders differently (three came out black: Nasrahmadi, both Banisadr) (57.7 → 51.9 MB, 41 files; Parsa alone 18.2 MB, under Cloudflare's 25 MiB per-file limit). `build_site.py` adds `pdf` to the catalog; `build_module.py` copies `pdf/`. The catalog filename, each article's page, search hits and cited articles in «حقوق بشر» link to the PDF at `#page=N`; the embed takes `pdfUrl`. Rehosting the party documents is cleared by the user.
- **2026-10-02:**
  - Sorted the user's expansion notes into §12 (phases 7–13): new drafts, article wiring and checks and balances, comments and co-authoring, verified voting, simulation, outreach. New sources checked against the registry: 7 new documents or editions, 1 duplicate (Juya on Pezhvak), the rest companions or leads. ghanoonasasi.org (IOCCI) and iran4all are projects like this one; talk to them before building co-authoring (decision 1). Nothing built.
- **2026-10-02 (7.1):**
  - Eight documents added (see 7.1). Green Jurists v4 is a bilingual book: the corpus document is the Persian preface and text (pp. 58–100, registry `pages`); its English half is a companion. Its article 1 leaves the form of state to a referendum, so it has no form-of-state tags. Arshadnejad's PDF metadata names another person; the author is taken from the Gooya publication.
  - Vision OCR for 229 pages: 100 by batch; two batches stalled (empty credit balance) and were cancelled; the rest read directly with the new `vision_ocr.py read`. `vision_ocr.py` now honours registry `pages`.
  - `articles.py` heading fixes (see Pitfalls) also restored article 26 in Green Jurists v1 and v3 and in Andishgah, Banisadr 1398's article 497, and cleaned headings in Mashruteh, its supplement and Ansari. Nayeb Hashem provisional picked up its earlier vision text.
  - Corpus: 56 registry entries, 51 active, 5,445 articles in the site data, 1,027 edges; site, PDFs and `dist/` rebuilt. Not committed.
- **2026-10-02 (text quality pass):**
  - Corpus-wide check found 9 older documents whose vision readings had stopped a few pages short when the credit ran out (2026-09-25), so their broken PDF text was still in use: Banisadr 1397 and 1398, CPI-MLM, Mostashar, NCRI (active), PDKI, PJAK, con-dfr (inactive). The 48 missing pages were read directly and the texts written. PDKI, PJAK and con-dfr, inactive "until re-read", are active again.
  - Fixes from that pass: split hundreds and «شست» in `articles.py`; HTML tags stripped in `vision_ocr.py` `clean()`; proofreading re-check (only the 1368 constitution has applied corrections, and it was not rewritten).
  - Result: 56 of 56 documents active; text from vision 45, HTML 5, PDF text layer 6 (checked clean); no unfinished readings, no broken «لا», word coverage ≥ 0.85 except Mostashar 0.79 and Khomeini 0.81 (Qajar prose, Arabic quotations). 5,476 articles in the site data, 1,154 edges. Not committed.
- **2026-10-02 (phase 7 done):**
  - Atlas base path: Pages serves at the root of atlasiran.org (custom domain), so `svelte.config.js` base is now `''` (was `/Atlas-website` for the static build; only SvelteKit's internal `assets` path still used it). Two hardcoded atlasiran.github.io/Atlas-website links, now dead, fixed: the home page's graph card (`{base}/graph`) and the «نشانی روی اطلس» line on org pages (atlasiran.org). Static build checked.
  - 7.2: Pezhvak's Juya is the 1393 edition, added as `juya-transitional-1393` (series `juya`). 7.3: iran4all 1.00, 1.01, 2.00 added (series `iran4all`), `pipeline/editions.py` + the «ویرایش‌ها» tab (word diff per matched article). 7.5: the 1358 draft (Majlis scan on Commons, pp. 12–30, 151 articles complete, word coverage 0.98) and Adlan Parsa 1382 (Wayback copy of the iransolidarity PDF, 166 articles). 7.6 assessed. `add_docs.py` gained `keep_from`/`keep_until`.
  - Credit ran out again during the iran4all readings (1.00 had 41 of 80 pages read). Superseded: the older versions were dropped (next entry).
  - Corpus: 62 registry entries, 59 active; 5,863 articles in the site data, 1,301 edges, 3 edition series (Green Jurists 4, Juya 2, Iran-e No 2); site PDFs 116.5 → 70.3 MB.
- **2026-10-02 (groups apart; iran4all older versions dropped):**
  - The user decided to ignore iran4all's older versions: 1.00, 1.01, 2.00 removed (registry, corpus PDFs, texts, the partial reading); 3.00 keeps links to their pages as companions. No more vision reading is pending.
  - Like with like, enforced in data and shown on the site: `catalog.py` `GROUP` (same table as `site/app.js`); `analyze.py` links documents and nearest articles only within a group (1,301 → 841 edges, 0 across groups). The Corpus tab's timeline shows only constitutions and drafts, and its table is four sections (constitutions and drafts 42, bylaws 7, programmes and charters 8, treatises 2), each non-constitution section with a line saying what it is and that it is compared only with its own kind; the lede says so too. The Similarity map shows one group at a time (`#map=B`); Search labels each hit with its type and filters by group. The Democratic Platform's bylaws, programme and charter moved to collection `org-documents` with the other organisations' documents. «اساس‌نامه» and «مرام‌نامه» spelled with ZWNJ in the UI.
  - Corpus: 59 registry entries, all active; 5,863 articles in the site data, 841 edges, 3 edition series.
- **2026-10-03 (Constitute vocabulary, 7.6–7.11):**
  - Constitute's data page reviewed: `topics.xml` (334 leaf topics, 330 coded), `metadata.xml` (4,341 documents; Iran 1906–1989, full English text only for 1989), a JSON API. Licence corrected to CC BY-NC 3.0.
  - Decided (user): import now, all coded topics, group A only; paid tagging after 5.5. Model for the pipeline scripts: Opus 5.5 (OCR `low`, proofreading and tagging `medium`), earlier `claude-opus-5` readings kept valid. Persian labels written in the Claude Code session (7.9), since the API route (`ontology.py fa`) stopped at «credit balance is too low». `pipeline/ontology.py` and `data/ontology/` added (7.7, 7.8). Not committed.
- **2026-10-03 (focus on the constitutions; Jahan Asadi's draft proofread and tagged):**
  - Open text work, group A only: no OCR is missing (35 vision-read, 3 web texts, 4 clean text layers); proofreading had been applied only to the 1368 constitution (≈ 2,160 pages open). Decided (user): duplicates inactive; federal drafts first, starting with Jahan Asadi's «ایالات متحده ایران»; only Banisadr's latest draft, later; everything else waits (5.5).
  - Duplicates set inactive: `mashruteh-fundamental-1906-dup` (the 1334 PDF, text identical to 1258) and `green-jurists-v1-1388` (every page carries the footer «نسخه دوم»; 99.4% the same as v2; no copy of the first edition in the corpus). Not duplicates: Andishgah's «قانون بنیادین موقت» is Juya 1397's 70 articles re-edited by another group («قانون اساسی» → «قانون بنیادین», «پایدار» → «دائمی»), kept active; Iran-e No r12/r13, Saginian's two variants and the Juya editions differ in substance.
  - Mashruteh 1258: 664 Urdu «ھ» and 145 Arabic-Indic digits in its text layer normalised to «ه» and Persian digits (`extract.py` `normalize_fa` now does this for any text-layer PDF). Articles unchanged (156).
  - `naoruz-usi-2026` proofread page by page in the Claude Code session against the page images (contents pages 3–8 by agreement with the proofread headings): 18 corrections in `data/proof/`, applied with `proofread.py apply`; 202 articles before and after. See Pitfalls for the two patterns found.
  - Tagged against the vocabulary (7.10). Gaps the tags show, for the audit: no ombudsman, human rights commission or anti-corruption body; no electoral commission (each chamber oversees its own election); nothing on the previous regime's crimes or a truth commission; no removal of ministers, the rotating president or judges during their term; no dissolution of parliament; no war power or commander in chief; due process without ne bis in idem, nulla poena sine lege, the right to silence or rules on evidence; race and skin colour not named among the grounds of discrimination; no ban on slavery; no reference to international human rights treaties. Placeholders still open in the draft: the list of states, the capital, the national day, the size of both chambers and of the government.
  - `andishgah-provisional-fundamental` set inactive too (user: a duplicate of Juya 1397, keep the newest; by the PDFs' creation dates Andishgah's is 6 Sep 2018, Juya's 17 Nov 2018).
  - Shown on the site, local preview only (7.11): the Topics tab with Jahan Asadi's coverage, the gaps and the observation that the draft follows the Swiss Federal Constitution of 1999 almost article by article (arts. 1–2, 6–7, the two equal chambers, the collegial government with a rotating one-year presidency; departures: secession, half of offices for women, the tenfold pay cap, the ban on private weapons). Published at the user's call, marked not yet reviewed (`review.publish`). Both audit tabs («حقوق بشر», «موضوع‌ها») now say how many of the 39 constitutions and drafts are done and list the others as queued (user: not to imply this is the only one). The Topics tab also got a «واژگان» panel (all 334 topics by subject: Persian and English name, definition, Constitute's coding question, draft status of the Persian name, and the published documents that have each topic, linked). Typography unified in Persian (user): one typeface for display, body and figures (Vazirmatn standalone, Shabnam in Atlas; Newsreader and the mono stack had no Persian glyphs), no letter-spacing (it breaks joined script), no italic; Persian digits in the timeline axis, the comparison bars and picker, the corpus table, whose year column shows the Jalali date («era»). The benchmark audit (5.5) of this draft has not been run; everything else waits (user).
  - Rebuilt: articles, analysis, catalog, site, module (57 active, 2 inactive; 5,554 articles in the site data, 763 edges, 2 edition series). Not committed.
  - Deployed: constitutions `9e12e60`, Atlas `92748ab`; the Topics tab answered on atlasiran.org 90 s after the push, `naoruz-usi-2026` published, no previews. The remaining work is in 7.12 (before the tab is announced) and 7.13.
  - Method page (7.13 (6)): `#topics=method` replaces the short method list; the vocabulary moved onto it. Reporting a wrong tag still has no channel.
- **2026-10-03 (Sartori vocabularies, 7.14):**
  - Reviewed the 11 ontologies of the Sartori repository against our Constitute import. Correction to the first review: CCP-FACET's grounds of discrimination were already in Constitute; what it adds is democracy, rule of law, social security.
  - Licences checked at source before use (CAP CC BY-NC-SA 4.0; Juon, Strøm CC0; repo CC BY-NC-SA 4.0). `pipeline/sartori.py` (fetch, check, layers), `data/ontology/sartori/`; three layers (`ccp`, `cap`, `ps`) with draft Persian; Naoruz tagged against them; Topics tab: two new panels, intro and method page rewritten for the added vocabularies, credit line. Committed as `b0454eb`, deployed with the entry below.

- **2026-10-03 (Naoruz finished in session: audit, Swiss check, 7.15):**
  - Human-rights audit of `naoruz-usi-2026` (5.5) read in the session: same rubric, benchmark and segments as `audit.py`, citations checked (segments exist, provisions in the benchmark, quotes found), 0 warnings. 24 guaranteed, 4 clawback, 3 silent. The audit page notes it was read in a session (`by`).
  - Swiss observation checked against the fedlex English text: holds; two additions (art. 78 lacks Swiss 70(1); art. 191 generalises Swiss 186(2)); art. 32 drops Swiss 29a's «exceptional».
  - 7.15: our own vocabularies (levels, 27 language items, Regional Authority Index) and their Naoruz coding; three new panels; method page. Local preview checked in both languages.
  - Deployed: constitutions `b0454eb` (Sartori layers) and `74ab399`, Atlas `bf06455`; live on atlasiran.org about 70 s after the push (topics data `114ff5a618d9`, the Naoruz audit in the rights view).
- **2026-10-04 (sartori.network reviewed):**
  - The site is a Retina viewer of one concept graph built from the repository's vocabularies; no documents. Decided (user): no site of our own; a concept map built from our article tags goes in the Topics tab as 7.16, after the 7.12 review.

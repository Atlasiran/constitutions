# Plan of action: Atlas × constitutions × normalcy

This is the reference for anyone, human or agent, continuing this work. It records what exists, what has been decided, which rules are not negotiable, and what comes next.
Last updated: 2026-09-24. Update the **Status** column and the **Log** at the bottom as work lands.

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
| Atlas | `~/Development/TCF-IT-Projects/Atlas-website` | `github.com/Atlasiran/Atlas-website` | SvelteKit 2 (Svelte 4), Tailwind 3, MDsveX, Supabase | GitHub Pages (`ADAPTER=static`, base `/Atlas-website`) + Cloudflare |
| constitutions | `~/Development/TCF-IT-Projects/constitutions` | `github.com/Atlasiran/constitutions` (public, AGPL-3.0) | Python pipeline + a single-file vanilla JS site (`site/index.html`, "Qanun Atlas") | Cloudflare Pages project `qanun-atlas-dev` (standalone preview) |
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
- 226 organisations, one `.md` per organisation in `src/content/org-pages/`. Frontmatter fields include `id, org_type, name_fa, name_en, manifest, coc, …`. There are **no relation fields**.
- `manifest` is filled for 104 organisations, `coc` for 4. Values are mostly external URLs; one is a local PDF (`static/docs/pjak-constitution-7th-congress.pdf`). `manifest` mixes charters, مرامنامه and bylaws (اساسنامه).
- Political types shown at `/parties`: `حزب`, `سازمان سیاسی`, `شورا / کنگره / ائتلاف`. Everything else is shown at `/groups`.
- Data flow: CSV in `data/` → `deploy/csv_to_json.py` → `deploy/update_org_pages.py` (data.json → md) → `npm run build` (`md_to_json.py` → `static/data/data.json`, then Vite).
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
| Tab name | «اسناد بنیادین» |
| Source PDFs | Plain git (no LFS; GitHub Pages can't serve LFS files) |
| مرامنامه (coc) | Grouped with charters/programmes, **not** with bylaws |
| Democratic Platform | Its own new Atlas entry (not listed as of 2026-09-24). The document is published and labelled «پیش‌نویس برای بررسی و تصویب» (`doc_status: draft`). **No PJAK link.** |
| naoruz.com | Corpus only (one person's project, jurist Jahan Asadi). No Atlas entry. |
| Model | `claude-opus-5` by default; Claude Sonnet 5 is an option for high-volume Gate 2 (the user's call) |
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

- Every verdict cites the document's articles **and** the benchmark provision IDs it rests on, and needs human reviewer sign-off before it is published.
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

Add to the organisation frontmatter:
```yaml
relations:
  - type: member_of        # member_of | affiliated_with | coalition_partner | split_from | merged_into | successor_of
    target: "310"          # Atlas org id
    since: ""
    until: ""
    source: "https://…"    # required
    status: self_declared  # self_declared | documented | disputed
```
- Stored in one direction only. The reverse link ("members: …") is generated in `md_to_json.py`.
- Organisation pages get a new section «پیوندها و وابستگی‌ها», grouped by type, with dates and a source link. Coalition pages (`شورا / کنگره / ائتلاف`) list their members automatically.
- `gen_gexf.py` adds these as graph edges, coloured by type.
- ⚠️ Check that `update_org_pages.py` keeps the `relations` field during the CSV sync.
- The edit/create forms and Supabase need a relations table.
- Only publicly declared or documented ties (rule 5). A disputed tie is marked disputed, never shown as fact.
- Separate from documents: an alliance doesn't make two organisations' documents comparable.

---

## 9. New documents: details

**naoruz.com**
- «قانون اساسی ایالات متحده ایران» ("Constitution of the United States of Iran"), a federal model by Jahan Asadi (جهان اسدی), 2026.
- Main text (`kind: constitution_proposal`): `https://naoruz.com/wp-content/uploads/2026/07/قانون-اساسی-_3_.pdf` (the "3" is probably a version number).
- Manifesto, a separate `charter` document: `.../2026/03/1_مانیفست-نوروز.pdf`.
- Attachments, not split into articles: `4_گرافیک-_ساختار.pdf`, `دوران-گذار_گرافیک_2.pdf`, `7_پرچم-آینده-1.pdf`, `5_تاریخچه-بنیانگذاری-فدرالیزم-در-چند-کشور.pdf`, `مروری-بر-روند-تاریخی-قانون-اساسی-در-ایران_6.pdf`.
- Check the URLs when downloading; they came from an automated page summary.

**Democratic Platform of Iran (پلتفرم دموکراتیک ایران)**
- File: `local/_اساسنامه_و_نظام_سازمانی_و_منشور_سیاسی_پلتفرم_دموکراتیک_ایران.pdf`. 75 pages, a Word export, dated 2026-09-21.
- Metadata: «نسخه نهایی ممیزی‌شده برای بررسی و تصویب» ("final audited version for review and approval").
- ⚠️ The text layer is garbled: ی characters are dropped and ligatures broken (e.g. «مشود» for «می‌شود»). Use OCR or a normalisation pass, not raw `pdftotext`.
- Contents: bylaws + organisational structure, political charter, programme outline. Split them by page range into `bylaws`, `charter` and `program`.
- Atlas entry:
  - org_type `شورا / کنگره / ائتلاف`
  - founded 21 Dey 1396 (2018-01-11), Brussels
  - website `https://www.iran-dp.com/`
  - alternative spelling «پلاتفرم»
  - English name: Democratic Platform of Iran
  - It was searched for in the org pages, the CSV and data.json, and was not listed.

---

## 10. Work plan

Status values: ☐ to do · ◐ in progress · ☑ done

### Phase 0: foundations
| # | Task | Status |
|---|---|---|
| 0.1 | Replace the hardcoded absolute paths in `pipeline/*.py` with paths relative to the repo; re-run the pipeline end to end | ☑ |
| 0.2 | `git init` constitutions; add `.gitignore` (`.wrangler`, `__pycache__`, `local/`); create `Atlasiran/constitutions` (public) *(ask before creating or pushing)* | ☑ public at github.com/Atlasiran/constitutions |
| 0.3 | Add normalcy as a submodule at `vendor/normalcy` | ☑ |
| 0.4 | Add the registry fields (§6) and backfill the 34 documents (mostly `kind`) | ◐ fields backfilled; `pages` not yet honoured by the pipeline (needed for 4.2) |
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
| 3.1 | Refactor the site into `app.js` + `mount()`, add `atlas-theme.css`, scope CSS under `.qa-root`, Persian default | ☐ |
| 3.2 | Build step producing `dist/` + `org-index.json` | ☐ |
| 3.3 | Atlas: submodule at `modules/constitutions`, copy step before build, `/constitutions` route, «اسناد بنیادین» nav entry, prerender entries | ☐ |
| 3.4 | CI `submodules: recursive`; Cloudflare nested submodules; test under base `/Atlas-website` | ☐ |

### Phase 4: new documents
| # | Task | Status |
|---|---|---|
| 4.1 | naoruz: download, registry entries (proposal + charter + attachments), extract, rebuild | ☐ |
| 4.2 | Democratic Platform: OCR/normalise, split into 3 documents, `doc_status: draft` | ☐ |
| 4.3 | Democratic Platform: new Atlas org page, logo, OG image, `manifest` link, **no PJAK relation** | ☐ |

### Phase 5: comparison
| # | Task | Status |
|---|---|---|
| 5.1 | Compare view limited to one comparison group; deep-link parameters | ☐ |
| 5.2 | «مقایسه اساسنامه» / «مقایسه منشور» ("compare bylaws" / "compare charter") button on `/op/[page]`, shown only when a comparable document exists | ☐ |
| 5.3 | Ingest the PJAK PDF from Atlas `static/docs/`; harvest the 104 `manifest`/`coc` links (download → classify → extract → link to organisation, with review) | ☐ |
| 5.4 | Benchmark audit through the batch pipeline; rights matrix with citations; methodology page; review workflow | ◐ `pipeline/audit.py` (submit/collect → `data/audits/<uid>.json`, review status `unreviewed`); first run pending |

### Phase 6: Atlas connections
| # | Task | Status |
|---|---|---|
| 6.1 | `relations` schema; reverse links generated in `md_to_json.py` | ☐ |
| 6.2 | «پیوندها و وابستگی‌ها» section; coalition member lists | ☐ |
| 6.3 | Graph edges in `gen_gexf.py` | ☐ |
| 6.4 | Make `update_org_pages.py` keep `relations`; edit-form and Supabase support | ☐ |

---

## 11. Pitfalls

- **Persian PDFs:** Word exports often have broken glyph mapping. Check the extracted text before splitting into articles; the OCR fallback is `pipeline/ocr.py`. A legacy font can map glyphs to *valid but wrong* Persian letters (Tabriz draft: «هرکس هطالعاتی تبریس»), which the letter check in `ocr.py` can't see. Check new documents by the share of their words found in at least two other documents (all good texts score ≥ 0.78; Tabriz scored 0.20), and force OCR with `ocr.py <uid>`.
- **Benchmark version** hashes the English text and IDs only, so adding Persian translations doesn't invalidate cached audits.
- **Atlas base path:** the GitHub Pages build serves under `/Atlas-website`. Never hardcode absolute URLs in the constitutions module.
- **Cloudflare Pages** only clones public submodules. Keep Atlas, constitutions and normalcy public, or change the deploy approach.
- **Claude API:** use `output_config.format` for JSON (not prefill; prefill returns 400 on current models). Check `stop_reason` before reading content. Stream when `max_tokens` is over about 16K. `fallbacks` isn't supported on the Batches API, so handle `refusal` results per item there.
- **Prompt caching** only kicks in above the model's minimum prefix size, and any change in the prefix bytes invalidates it (no timestamps or IDs in the system prompt).
- **Web summaries are not sources.** Verify facts such as membership, dates and URLs against primary sources before publishing (rule 5).

---

## 12. Log
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

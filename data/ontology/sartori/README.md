# Vocabularies from the Sartori repository

Files from the **Sartori ontology repository** (<https://github.com/conceptintegration/sartori-repo>, shown on
<https://www.sartori.network/>), downloaded unchanged by `pipeline/sartori.py fetch` at the commit pinned in that
script. `source.json` records the commit, the date and the sha256 of each file. `sartori.py check` says whether
upstream has moved on, which of these files changed and which ontologies were added.

They add three layers to Constitute's vocabulary (`../README.md`). Article tags against them are kept in their own
field (`x`) of `data/topics/<uid>.json`, so Constitute's tags and its `ontology_version` are untouched.

| Layer | File | Source | What we use |
|---|---|---|---|
| `ccp:` | `CCP-FACET.csv` | Comparative Constitutions Project, faceted vocabulary | The 3 topics Constitute's 334 lack: `democ`, `rulelaw`, `socsec`. Its 16 grounds of discrimination are already in Constitute (`equalgr1`–`16`); `votemin` is covered by `voteres`. |
| `cap:` | `CAP-TOP.csv` | Comparative Agendas Project, master codebook topics (v1.2) | All 213 topics, under their 21 headings |
| `ps:` | `JUON-CPSD.csv` | Andreas Juon, Constitutional Power-Sharing Dataset (v1.2) | All 75 rules, as `ps:j<key>` |
| `ps:` | `STROM-IDC.csv` | Strøm, Gates, Graham and Strand, Inclusion, Dispersion and Constraint (v1.2) | 18 of 36: the rules a constitution can lay down that Constitute does not code. Left out: what governments did (`gcimp`, `unity`, `gcseats1/2`, `resimp`, `resseatsimp`, `fedunits`, `violation`) and what Constitute already has (religion, the judiciary). |

`*.metadata.csv` are each ontology's metadata (name, citation, version) as published in the repository.

## Licence

These files are **not** covered by this repository's AGPL-3.0 licence, and their terms differ from Constitute's.

- **The Sartori repository** as a whole: **CC BY-NC-SA 4.0** (its `LICENSE`).
- **Comparative Agendas Project**: datasets and codebooks © Comparative Agendas Project, under **CC BY-NC-SA 4.0**
  (comparativeagendas.net, Copyright/Legal page, checked 2026-10-03). The CC BY-NC-ND licence found in search
  results belongs to the OUP book chapter about the codebook, not to the codebook.
- **Juon, CPSD v1.2** (doi:10.7910/DVN/9FYN8J) and **Strøm et al., IDC** (doi:10.7910/DVN/29421): **CC0 1.0** on Harvard
  Dataverse (checked through its API, 2026-10-03). The repository's own CC BY-NC-SA terms still cover its copies.
- **CCP-FACET**: the Comparative Constitutions Project's material, via the repository (CC BY-NC-SA 4.0), on top of
  Constitute's CC BY-NC 3.0.

So these files, and what is derived from them here (the Persian labels in `fa.json`, the `extra` block of
`../topics.json`, the `x` tags), may be used and shared **for non-commercial purposes, with attribution, under the
same licence (ShareAlike)**.

Attribution: *Added vocabularies via the Sartori ontology repository (conceptintegration/sartori-repo, CC BY-NC-SA
4.0): Comparative Constitutions Project (CCP-FACET); Comparative Agendas Project, master codebook (CC BY-NC-SA 4.0);
Juon, Constitutional Power-Sharing Dataset v1.2 (CC0); Strøm, Gates, Graham and Strand, Inclusion, Dispersion and
Constraint dataset (CC0).*

## Files

| File | What it is |
|---|---|
| `source.json` | Repository, pinned commit, fetch date, sha256 per file |
| `fa.json` | Persian labels and definitions: `{"<layer>:<key>": {fa, fa_def, status}}`, plus `"group:cap-<heading>"` for CAP's headings. `status` is `draft` until reviewed. Written in the Claude Code session of 2026-10-03; Juon's labels are composed from office × mechanism. Edit by hand when reviewing; a re-fetch never touches it. |

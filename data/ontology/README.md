# Constitute topic vocabulary

`constitute-topics.xml` is the topic vocabulary of **Constitute** (constituteproject.org), the site of the
**Comparative Constitutions Project** (Zachary Elkins, Tom Ginsburg, James Melton). It was downloaded unchanged from
<https://www.constituteproject.org/topics.xml>; `source.json` records the date and the sha256.

## Licence

These files are **not** covered by this repository's AGPL-3.0 licence.

- Constitute's About page states that, except for material identified as copyrighted by other parties, the content of
  constituteproject.org is provided under the **Creative Commons Attribution-NonCommercial 3.0 Unported** licence
  (CC BY-NC 3.0).
- Its Terms and Conditions forbid commercial use and charging a fee for any use.

So the vocabulary and everything derived from it here (`topics.json`, the Persian labels in `fa.json`, and the
article tags made against it) may be used and shared **for non-commercial purposes only, with attribution**.

Attribution: *Topic vocabulary from Constitute (constituteproject.org), Comparative Constitutions Project, licensed
under CC BY-NC 3.0.*

**Not reused:** Constitute's English constitution texts. They come from HeinOnline and Oxford Constitutions of the
World under permission and are not part of this repository.

## Files

| File | What it is |
|---|---|
| `constitute-topics.xml` | The vocabulary as downloaded (RDF/XML). Labels in English, Spanish and Arabic. |
| `source.json` | URL, fetch date, sha256 |
| `fa.json` | Persian labels and definitions: `{id: {fa, fa_def, status}}`. `status` is `draft` (model-written, not yet checked) or `reviewed`. Edit this file by hand when reviewing; a re-import never overwrites it. |
| `topics.json` | Built by `pipeline/ontology.py`: the 334 leaf topics, each mapped to one of this project's topic groups, with the Persian merged in. `version` hashes the XML and the mapping. Its `extra` block holds the vocabularies added from the Sartori repository and our own (`own/`), with their own `version`; see `sartori/README.md` for them and their licence (CC BY-NC-SA 4.0 / CC0). |
| `sartori/` | The added vocabularies (CCP's three extra topics, Comparative Agendas Project policy topics, power-sharing rules), their source record and Persian. |
| `own/` | Our own vocabularies: language (27 items), levels of government for policy fields, and the Regional Authority Index's dimensions; see `own/README.md`. |

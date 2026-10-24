# DR2C VORENYX v2.22 — Checkpoint

**Status: static structure PASS; ZIP integrity PASS; full localization is not complete.**

## Verified counts
- Patch ZIP: 292 entries; ZIP CRC scan returned no corrupt entry.
- Baseline inventory: 541 script/text files, 17,329 quoted literal occurrences, 13,038 unique literal values.
- Heuristic player-facing rows marked localized: 7,490 / 10,844 = **69.07%**.
- Contextual display expressions rewritten: 94.
- Existing literal tokens changed: 183.
- Inventory rows newly marked: 138.
- Unmarked unique literal candidates: 2,822.

## Scope
- `assets/deathforth/charstats-textfill.df`
- `assets/deathforth/events/camp/camp3.df`
- `assets/deathforth/events/common/common4.df`
- `assets/deathforth/events/rareloc/rare1.df`
- `assets/deathforth/cyoa-charstats.df` (two added group-label helper literals and two lines)

## QA debt and limits
The embedded validation report records 49 exact mapping rules whose original source literals were not found after contextual rewrites. They may be superseded by complete-expression replacements, but each must be reconciled against the final source. They are not counted as successful exact matches.

The 69.07% value is a literal-inventory heuristic, not semantic completeness or screen coverage. Runtime gameplay, save/load, and APK rebuild/signing were not run. Public GitHub stores this checkpoint and authored documentation only; the binary overlay and original source archive remain local.

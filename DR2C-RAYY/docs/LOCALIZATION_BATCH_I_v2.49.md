# DR2C VORENYX v2.49 — Batch I Localization Report

**Status:** cumulative source-overlay patch only; no APK built; no device runtime test.

## Batch I scope

- New script files touched: **14**.
- Translation records: **203**.
- Literal occurrences affected: **203**.
- Cumulative overlay now contains **73** script files out of **509** source `.df` scripts.
- Modules include RPG class descriptions/options; toilet, zombie queue and drag-race scenes; gym/chess events; alien/anime rare locations; bandit checkpoints; character-recruitment CYOA options; weapon and trader descriptions.

## Files changed

- `events/inner/region/rpgfare.df`
- `events/common/common5.df`
- `events/common/OMENTUM.df`
- `events/rareloc/region/alien.df`
- `events/rareloc/animestore.df`
- `events/bandit/bandit1.df`
- `events/bandit/bandit2.df`
- `events/sc/cyoa-screcruit1.df`
- `events/sc/cyoa-screcruit2.df`
- `events/sc/cyoa-screcruit3.df`
- `events/sc/cyoa-screcruit4.df`
- `events/trade/trader-camp-region-special1.df`
- `events/trade/trader-camp-region-special2.df`
- `events/trade/weapons.df`

## Validation

- Touched-file quote parity failures: **0**.
- Escaped-double-quote regressions in touched files: **0**.
- Executable-skeleton differences outside string contents: **0**.
- Handler names/order and branch code are preserved because only existing quoted literal contents were edited.
- Every explicit mapping entry matched; unmatched mapping keys: **0**.
- ZIP CRC: **PASS**; entries: **77**; duplicate paths: **0**.
- ZIP size: **429,369 bytes**.
- SHA-256: `926278b87eac76a5329e7ce16c04993dd127cc296a78fc6dedb56cd791562ced`.

## Remaining work and limitations

1. This patch improves selected player-facing strings but does **not** claim global Indonesian coverage.
2. The lightweight lexical scan is not a complete Deathforth parser, even though touched-file syntax and executable-skeleton checks pass.
3. No APK was built and no on-device test was performed.
4. The cumulative overlay is source-focused. Before a future APK build, reconcile the current cumulative script overlay with the separate v2.46 native UI patch and the v2.45 Startfix changes so native labels, tutorial UI and event text all ship together.
5. The Batch I patch intentionally leaves some complex dynamic sentences untranslated when translating only an isolated string fragment would produce incorrect Indonesian grammar. Those phrases remain candidates for a later display-template rewrite.

## Artifacts

- ZIP patch: `DR2C_VORENYX_v2.49_BATCH_I_LOCALIZATION_PATCH.zip`
- Applied phrase records: `DR2C_VORENYX_v2.49_BATCH_I_APPLIED_TRANSLATIONS.csv`
- Batch I diff: `DR2C_VORENYX_v2.49_BATCH_I_LOCALIZATION.diff`
- Validation JSON: `DR2C_VORENYX_v2.49_BATCH_I_VALIDATION.json`
- SHA-256 file: `DR2C_VORENYX_v2.49_BATCH_I_LOCALIZATION_PATCH.sha256.txt`

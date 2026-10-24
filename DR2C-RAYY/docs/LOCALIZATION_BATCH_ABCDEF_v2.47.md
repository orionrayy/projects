# DR2C VORENYX v2.47 — Localization Batches A–F

**Status:** source patch only; no APK rebuilt. Static structure checks passed for all eight modified scripts.

## Applied work

- Baseline: v2.46 UI-localized candidate, SHA-256 `6d4e2f3df07d199807c08418ae5d30b9927e5b2e36c780a51858045336b29313`.
- Applied all 38 curated static choice/location-label rows.
- Completed **313 recorded replacement operations across batches A–F**, representing **325 literal occurrences**; repeated matches mean one operation may affect more than one occurrence.
- Eight modified scripts: `special-lots.df`, `oldtrade.df`, `locationlogic.df`, `PANCREAS.df`, `rare.df`, `junk-maker.df`, `015-graves.df`, and `frozen.df`.
- Scope covers static city/location labels; dynamic food-for-resource trades; weapon/trade titles and narration; zombie swarm/time/aggression/siege forecast vocabulary; weapon/perk tips; pipebomb/anime seller text; gas/ammo/medical trade narratives; rare items; dog rescue; graves; frozen-region encounter text.

## Validation

- Non-string token streams match the v2.46 baseline in all eight scripts.
- Choice-handler sequences match exactly in every modified file.
- No unclosed string found by the lightweight lexer; no backslash-escaped double quotes remain in those files.
- Patch ZIP CRC passes, with 10 entries and no duplicate paths.
- Patch ZIP: 69,656 bytes; SHA-256 `08731efd0d451332a7d0af5f4587d7bc524f291d4700c720cf483d230a0158cc`.

This is static source validation, not a Deathforth interpreter run or gameplay test.

## Residual English triage

A lightweight lexer reviewed all **509 packaged .df scripts** after applying the patch to the eight modified scripts. It produced **397 unique candidate strings with English signals**, including test/demo text and false positives. After separately categorizing likely test/demo/debug strings, **159 high-priority likely-English strings remain for human review**. These are candidates, not a verified count of untranslated, player-visible text.

Top candidate hotspots:
- `gamemodes.df`: 19
- `events/finale/epilogue-check.df`: 10
- `events/inner/region/swarmarcade.df`: 8
- `events/common/common4.df`: 7
- `events/common/LIVER.df`: 5
- `mission-events.df`: 4
- Character blurbs, regional events, and news modules follow.

The 159 count is not a percentage or a claim of localization completeness. The scanner can catch fragments, proper names, mixed-language text, humorous phrasing, or dynamic templates; each must be reviewed in context.

## Artifacts and build limitation

The source patch and CSV review lists are supplied as downloadable conversation artifacts:
- `DR2C_VORENYX_v2.47_BATCH_ABCDEF_LOCALIZATION_PATCH.zip`
- `DR2C_VORENYX_v2.47_BATCH_ABCDEF_APPLIED_TRANSLATIONS.csv`
- `DR2C_VORENYX_v2.47_QUEUE_APPLIED_STATUS.csv`
- `DR2C_VORENYX_v2.47_RESIDUAL_ENGLISH_REVIEW_QUEUE.csv`
- `DR2C_VORENYX_v2.47_RESIDUAL_P1_REVIEW_QUEUE.csv`

**No APK was rebuilt.** The private key for the v2.46 test certificate is absent from the build workspace; a new signing key would prevent an in-place update. Remaining English in other scripts is expected. Runtime testing and an actual Deathforth interpreter check are still required.

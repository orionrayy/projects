# DR2C VORENYX v2.51 — Batch K Localization Report

**Status:** cumulative source patch only; no APK build and no device runtime test.

## Scope

- Files touched: **9**, including **3** new active overlay scripts.
- Curated translation/template records: **206**.
- Literal occurrences affected: **211**.
- Cumulative overlay: **77** of **509** source `.df` files.
- Areas: Sasquatch encounter, Santa and Cupid character blurbs, cemetery/Dracula/mausoleum event, mad scientist, ninja, gym, end-of-road/credit/win-streak summaries, and Johnny encounter.

## Validation

- Lexical failures on changed files: **0**.
- Escaped double-quote regressions: **0**.
- Executable-skeleton differences after masking strings/comments: **0**.
- Handler-sequence differences: **0**.
- Unexpected unmatched mapping keys: **0**.
- Mapping keys already translated in earlier batches (skipped intentionally): **11**.
- ZIP CRC: **PASS**; **85** entries; **0** duplicate paths.
- ZIP size: **460,379 bytes**.
- SHA-256: `e265c7d2789e6936aadea49a42c4b5c87799c202945f8cfa4bee7291a8a40046`.

## Areas covered

- Sasquatch roadside encounter choices and narrative.
- Santa and Cupid flavor/quip text.
- Cemetery and mausoleum events including Dracula, tombs, and interaction choices.
- Mad scientist event, laboratory outcomes and insults.
- Ninja departure/vanish/tantrum events.
- Gym/fitness text where still present in the current overlay.
- End-of-road mode-completion summary, win streaks, congratulatory messages and credit labels.
- Johnny/Jerks encounter UI.

## Notes

- Proper names such as `DEATH ROAD TO CANADA`, Dracula, Twilight, staff and company names were retained where appropriate.
- Dynamic display templates were rewritten only where needed to maintain natural Indonesian grammar, preserving variables and handlers.
- Eleven candidate mappings were already localized in the earlier Batch H overlay; they are skipped intentionally, not unresolved errors.
- Static checks are not a full Deathforth parser. No APK was built or runtime tested.
- Global Indonesian localization remains incomplete. The cumulative overlay covers only 77/509 script files, which is not the same as player-visible translation coverage.

## Artifacts

- ZIP: `DR2C_VORENYX_v2.51_BATCH_K_LOCALIZATION_PATCH.zip`
- Applied translations CSV: `DR2C_VORENYX_v2.51_BATCH_K_APPLIED_TRANSLATIONS.csv`
- Diff: `DR2C_VORENYX_v2.51_BATCH_K_LOCALIZATION.diff`
- Validation JSON: `DR2C_VORENYX_v2.51_BATCH_K_VALIDATION.json`
- SHA-256: `DR2C_VORENYX_v2.51_BATCH_K_LOCALIZATION_PATCH.sha256.txt`

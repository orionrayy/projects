# DR2C VORENYX v2.35 — Checkpoint

**Static source validation: PASS. Full player-visible localization: NOT COMPLETE.**

## Scope
- `mission.df`
- `locplan.df`
- `dailydecks.df`
- `cyoa-charstats.df`
- `events/inner/gymloc.df`
- `events/inner/coffeeloc.df`
- `events/industrial/indust.df`
- `events/rareloc/region/arkwares.df`
- `kepa/kepa.df`
- `don/events/common/003-vortex.df`
- `gamemodes.df`
- `events/exterior/region/road-long.df`

## Batch totals
- Complete display expressions rewritten: **32**.
- Direct literal rules matched: **9**; literal occurrences changed: **9**.
- Comment-aware merged inventory: **541** source files and **16,827** active quoted-string tokens.
- English-likelihood triage queue: **129** candidate rows across **67** files. It is not a unique-string count or coverage percentage.

## Static checks
- Line counts preserved for every changed file.
- Non-display source skeleton preserved.
- CYOA IDs, choice IDs and route paths preserved.
- Targeted direct mappings consumed; no mapped literal residues remain.
- ZIP CRC, manifest and SHA-256 checks pass.

## Metadata reconciliation
The previous v2.34 archive had a mismatch between its checkpoint scope and the actual archive content, plus stale embedded ZIP digest metadata. This package corrects the v2.34 documentation based on the actual v2.34 ZIP. The exact v2.35 digest is `df3cd3840b3a6f32e5861b976045112ee790db6e472ae512ebac8d2e1b4fcee1` (19828207 bytes); ZIP and manifest counts are 362 and 361, respectively.

## Coverage and runtime limits
The v2.22 69.07% result remains historical only. Global semantic coverage has not been computed; **100% localization is not claimed**. Gameplay, actual UI fit, save/load, and APK rebuild/signing were **NOT RUN / NOT PERFORMED**.

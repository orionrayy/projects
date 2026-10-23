# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.2. Static integrity passes; localization remains in progress.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for Death Road to Canada. The original Canada-bound campaign flow remains an invariant.

## Verified checkpoint v2.2

- Audit baseline: 541 script/text files, 17,329 quoted literal occurrences, 13,038 unique literal values.
- Likely player-facing occurrences (heuristic): 10,844; changed: 3,509 (**32.36% heuristic estimate**).
- Likely untranslated unique candidates: 6,531.
- v2.2 repairs 15 contextual player-facing English literals in weapon-trader dialogue/choices/item text.
- Targeted residue scan: 0 matches; display markers in `weapons.df`: 157/157; static report PASS; ZIP CRC PASS.
- Runtime gameplay, save/load and APK rebuild/signing: NOT RUN.

The percentage is a literal-delta heuristic, not semantic or runtime screen coverage.

## Project records
- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.2 checkpoint report](docs/CHECKPOINT_v2.2.md)
- [Localization guide](docs/LOKALISASI_ID.md)
- [Slang research](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation](docs/BUILD_AND_VALIDATION.md)
- [Coverage](audit/coverage.json)
- [Static validation](audit/validation_report.json)
- [v2.2 reconciliation summary](audit/v2.2_reconciliation_summary.json)
- [Version history](audit/version_history.json)

## Distribution boundary
This public repository stores project-authored documentation, research and sanitized audit reports. It does not include the original APK/archive or full extracted game scripts/overlay to avoid redistributing third-party game materials. The complete v2.2 data-overlay ZIP and private/local project archive are provided separately as user artifacts.

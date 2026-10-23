# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.1. Static checks pass; localization remains in progress.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for Death Road to Canada. The first scope is localized presentation text and a new title identity; the original campaign flow toward Canada must remain intact.

## Verified checkpoint v2.1

- Audit baseline: 541 script/text files, 17,329 quoted literal occurrences, 13,038 unique literal values.
- Likely player-facing occurrences (heuristic): 10,843; changed: 3,494 (**32.22% heuristic estimate**).
- Likely untranslated unique candidates: 6,545.
- Latest batch: 187 literal rewrite hits across Shooting, Fitness, Mechanical, Army Surplus, Rifle Collector and Blade Master.
- Static integrity: PASS; no reported failures; display-expression markers balanced 229/229; ZIP CRC PASS.
- Runtime gameplay, save/load and APK rebuild/sign: NOT RUN.

32.22% is a heuristic literal-delta estimate, not a claim of full translation or semantic coverage.

## Project records

- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.1 checkpoint report](docs/CHECKPOINT_v2.1.md)
- [Localization and style guide](docs/LOKALISASI_ID.md)
- [Slang research and evidence](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation limits](docs/BUILD_AND_VALIDATION.md)
- [Coverage estimate](audit/coverage.json)
- [Static validation report](audit/validation_report.json)
- [v2.1 reconciliation summary](audit/v2.1_reconciliation_summary.json)
- [Version history](audit/version_history.json)

## Distribution boundary

This public repository contains project-authored documentation, research references, and sanitized audit records. It intentionally excludes the original APK/archive and the full extracted game scripts/overlay to avoid redistributing third-party game materials. The complete v2.1 data-overlay ZIP and local project archive are available as separate user artifacts; preserve the user-provided base archive locally when rebuilding.

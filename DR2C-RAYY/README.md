# DR2C VORENYX — Indonesian Localization

**Latest checkpoint: v2.40 · Static integrity PASS · Full localization NOT COMPLETE**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for *Death Road to Canada*. The target is natural, context-aware Indonesian with distinct character voices and blunt sarcasm. Original campaign flow, machine identifiers, branch conditions, route IDs, and game-state effects are invariants.

## v2.40 checkpoint

- Repaired **45 trait/perk machine-key mismatches** from v2.39 across 13 modules; the post-repair audit found **0 remaining mismatches across 195 operand comparisons**.
- Routed trait/perk labels through the display localization helper and added missing display mappings.
- Continued localization across CYOA guidance, journey/camp text, NPC banter, reward text, comic/magazine choices, medical feedback, event narration, and combat tutorials. Updated the title-art badge to V2.40.
- Static control-flow checks: CYOA/choice IDs preserved; route/resource path literals preserved.
- A fresh comment-aware inventory scanned **541 .df/.txt files** and indexed **16,834 active quoted literals**. None of the inherited high-likelihood candidate rows remain in the current merged source. This queue is heuristic; its zero count **does not prove semantic or runtime completeness**.
- A machine-audit non-flagged proxy of **88.11%–94.30%** is available for triage only; it is **not** a localization-coverage percentage. Global semantic/player-visible coverage is **NOT COMPUTED**. The historical v2.22 figure of 69.07% is stale and must not be used as v2.40 coverage.

## Build integrity

- Patch ZIP: **24,380,609 bytes**; SHA-256 `a863cadfda4d99ef14c9199e255cbfc8e687c1d05a1853b8f461f096870b26eb`; 411 entries; 410 manifest entries; CRC PASS; zero manifest hash failures; zero duplicate paths; zero machine-local path leaks.
- Full project archive v2.5: **105,064,456 bytes**; SHA-256 `cc0e7818dd87f0fe508692ae0545343ad89c727c401c81ad00f703377962fa97`; 185 entries; 184 manifest entries; CRC PASS; zero manifest hash failures; zero unmanifested files; zero duplicate paths.
- The binary patch and full source archive are **not hosted in this public repository**. SHA-256 sidecars accompany the local release artifacts.

## Tests not performed

Runtime gameplay/event-path testing, actual UI fit/overflow testing, save/load regression, and APK rebuild/signing are **NOT RUN / NOT PERFORMED**. Static integrity checks do not prove runtime compatibility. This ZIP is a data/script overlay, not a rebuilt or signed APK.

## Project records

- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.40 checkpoint](docs/CHECKPOINT_v2.40.md)
- [Build and validation details](docs/BUILD_AND_VALIDATION.md)
- [Indonesian localization guide](docs/LOKALISASI_ID.md)
- [Slang research and evidence](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Coverage summary](audit/coverage.json)
- [Static validation report](audit/validation_report.json)
- [v2.40 coverage recheck](docs/COVERAGE_RECHECK_v2.40.md)
- [v2.40 fresh coverage metrics](audit/v2.40_coverage_recheck.json)
- [v2.40 sanitized integrity summary](audit/v2.40_integrity_summary.json)
- [v2.40 localization summary](audit/v2.40_localization_summary.json)
- [Version history](audit/version_history.json)

Public GitHub contains project-authored documentation and sanitized audit metadata only. Do not commit the original APK/archive, complete extracted scripts, literal inventory, or binary overlay.

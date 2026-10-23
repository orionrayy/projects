# DR2C VORENYX — Indonesian Localization

**Status: localization in progress. Current checkpoint: v1.3 QA repair.**

DR2C VORENYX is a fan-made Indonesian localization/mod overlay for the user-provided Death Road to Canada archive. The first scope is localization and new title identity; the original travel-to-Canada campaign flow must remain intact.

## Current verified state

- Audit baseline: 541 script/text files, 17,329 quoted literal occurrences, 13,038 unique literal values.
- Likely player-facing occurrences: 10,843, classified heuristically.
- Changed likely player-facing occurrences: 3,186 / 10,843 = 29.38% by the current heuristic.
- Heuristic estimate of unique probable player-facing candidates still untranslated: 6,813.
- v1.3 static report: PASS; zero skipped exact rewrites; zero static failures; ZIP CRC PASS.
- Game runtime, save/load and APK rebuild/signing: NOT RUN / NOT PERFORMED.

The 29.38% value is a literal-delta heuristic, not a runtime measure and absolutely not a claim of full translation.

## Project records

- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [Localization and style guide](docs/LOKALISASI_ID.md)
- [Slang research and evidence](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation limits](docs/BUILD_AND_VALIDATION.md)
- [Coverage estimate](audit/coverage.json)
- [Static validation report](audit/validation_report.json)
- [Version history](audit/version_history.json)
- [Conversation decisions](history/CONVERSATION_DECISIONS.md)

## Public-repository boundary

This repository is public. It intentionally does not contain the original APK/archive or the full extracted game scripts/overlay, to avoid redistributing third-party game materials. The complete local project archive made for this checkpoint contains the user-provided input, latest patch ZIP, local build scripts, all available version diffs, audit inventory, generated title art, and project memory. Keep the original base archive locally when rebuilding.

## Core requirements

1. 100% of player-visible text is the target; it is not achieved yet.
2. Preserve internal IDs, placeholders, reward/trade mechanics, stats keys, CYOA identifiers and original campaign flow.
3. Indonesian should be modern, slangy, frontal and sarcastic where character/context supports it.
4. Avoid indiscriminate slang stuffing: every NPC needs a recognizable voice.
5. Any release claim requires runtime event/menu testing, save/load testing, and APK build/sign verification.

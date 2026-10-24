# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.35. Static source checks PASS; full localization is not complete.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for *Death Road to Canada*. The original campaign flow and gameplay logic are invariants; the work focuses on contextual Indonesian text, consistent voice, and preserving source structure.

## Verified checkpoint v2.35
- 32 complete player-facing display expressions rewritten across 12 files.
- 9 direct literal rules matched; 9 occurrences changed.
- Coverage of this batch includes game-mode explanations, journey-planning text, mission and reward dialogue, gym/coffee/factory encounters, a generator puzzle, broom/portal characters, and Mountie Alpha-end text.
- Comment-aware source inventory: 541 source files, 16,827 active quoted-string tokens.
- 129 English-likelihood candidate rows remain for triage across 67 files. These are heuristic candidate rows, not unique untranslated strings or a coverage percentage.
- Static integrity: PASS. ZIP contains 362 entries; 361 manifest-listed files have zero hash mismatches; CRC passes; no duplicate paths or local path leaks.
- Release artifact SHA-256: `df3cd3840b3a6f32e5861b976045112ee790db6e472ae512ebac8d2e1b4fcee1` (19,828,207 bytes).

## Coverage and runtime limits
The 69.07% figure is a stale v2.22 heuristic baseline, not current v2.35 coverage. Global semantic coverage has **not** been computed and 100% completion is not claimed. Runtime gameplay, actual UI fit, save/load, and APK rebuild/signing have **not** been run.

## Project records
- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.35 checkpoint](docs/CHECKPOINT_v2.35.md)
- [v2.34 scope reconciliation](docs/CHECKPOINT_v2.34.md)
- [Localization guide](docs/LOKALISASI_ID.md)
- [Slang research](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation](docs/BUILD_AND_VALIDATION.md)
- [Coverage summary](audit/coverage.json)
- [Static validation](audit/validation_report.json)
- [v2.35 sanitized batch summary](audit/v2.35_localization_summary.json)
- [v2.34 metadata reconciliation](audit/v2.34_reconciliation.json)
- [Version history](audit/version_history.json)

## Voice and slang policy
Use natural, context-driven Indonesian, with distinct NPC personas and blunt sarcasm where appropriate. Profanity and meme terms are context-bound rather than inserted indiscriminately. See the localization guide and slang research for confidence notes.

## Distribution boundary
The public repository contains authored documentation, research and sanitized audit summaries. It does not include the original APK/archive, complete extracted game scripts, full source inventory, or binary localization overlay.

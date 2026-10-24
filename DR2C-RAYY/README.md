# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.36. Static source checks PASS; full localization is not complete.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for *Death Road to Canada*. The original campaign flow and game logic are invariants; work focuses on contextual Indonesian text, distinct character voice, and preserving source structure.

## Verified checkpoint v2.36
- **45 complete display expressions rewritten** and **12 direct literal occurrences changed** across 31 source modules.
- Scope includes arcade defense, bandit-raid defense and rewards, siege routes, shop/fairy/park encounters, city-ranger and panda events, character banter, perk/trait help text, and epilogue fragments.
- Comment-aware source inventory: 541 source files and 16,819 active quoted-string tokens.
- **77 English-likelihood candidate rows remain across 36 files** for manual triage. These are heuristic rows, not unique untranslated strings or a coverage percentage.
- Static validation: PASS. ZIP has 376 entries; 375 manifest entries verified; CRC passes; zero duplicate paths, manifest hash failures, or machine-local path leaks.
- Local release ZIP: `DR2C_VORENYX_ID_v2.36_localization_patch.zip`, 20,771,028 bytes. SHA-256: `fa76da687ce7d8ea5b1e2fafa165b40c31829248fadb5e8c9c6b1ebec3dd5608`.

## Coverage and test limits
The 69.07% figure is a stale v2.22 heuristic baseline, not current v2.36 coverage. Current global semantic coverage has **not** been computed, and 100% completion is not claimed. Runtime gameplay, actual UI fit/text overflow, save/load, and APK rebuild/signing have **not** been run.

## Project records
- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.36 checkpoint](docs/CHECKPOINT_v2.36.md)
- [v2.35 checkpoint](docs/CHECKPOINT_v2.35.md)
- [v2.34 scope reconciliation](docs/CHECKPOINT_v2.34.md)
- [Localization guide](docs/LOKALISASI_ID.md)
- [Slang research](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation](docs/BUILD_AND_VALIDATION.md)
- [Coverage summary](audit/coverage.json)
- [Static validation](audit/validation_report.json)
- [v2.36 sanitized batch summary](audit/v2.36_localization_summary.json)
- [v2.34 metadata reconciliation](audit/v2.34_reconciliation.json)
- [Version history](audit/version_history.json)

## Voice and slang policy
Use natural, context-driven Indonesian, distinct NPC personas, and blunt sarcasm where appropriate. Profanity and meme terms are context-bound rather than inserted indiscriminately. See the localization guide and slang research for confidence notes.

## Distribution boundary
The public repository contains authored documentation, research and sanitized audit summaries. It does not include the original APK/archive, complete extracted game scripts, full source inventory, or binary localization overlay.

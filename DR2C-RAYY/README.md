# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.3. Static integrity and patch ZIP verification PASS; localization remains incomplete.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for Death Road to Canada. The original Canada-bound campaign flow remains an invariant.

## Verified checkpoint v2.3
- Inventory baseline: 541 source files, 17,329 quoted literal occurrences and 13,038 unique literals.
- Scope: contextual presentation-text pass for recruitment/event scripts `camp-recruit.df`, `cyoa-k-recruit.df` and `familiar-recruit.df`.
- 410 exact mapping rules matched, changing 432 literal occurrences. Source literal counts, line counts and display markers were preserved by static checks.
- Heuristic likely player-facing delta: 3,809 / 10,844 (35.13%); 6,270 probable unique untranslated candidates remain.
- The percentage is a literal-inventory heuristic, **not semantic or runtime coverage**. Full Indonesian translation is not complete.
- ZIP CRC and `tools/verify_patch.py`: PASS. Runtime gameplay, save/load and APK rebuild/signing: NOT RUN.

## Project records
- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.3 checkpoint report](docs/CHECKPOINT_v2.3.md)
- [Localization guide](docs/LOKALISASI_ID.md)
- [v2.3 slang/voice guide](docs/VORENYX_VOICE_GUIDE_v2.3.md)
- [Slang research](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation](docs/BUILD_AND_VALIDATION.md)
- [Coverage summary](audit/coverage.json)
- [Static validation](audit/validation_report.json)
- [Version history](audit/version_history.json)

## Slang direction
Use context-driven, blunt Indonesian with distinct NPC personas. Meme terms such as `ragnamok`, `jomok/perjomokan`, and `cewe standar TikTok` are not filler: current media and community evidence shows highly variable and niche meanings. The guide treats them with confidence notes and context limits.

## Distribution boundary
The public repository stores project-authored documentation, research and sanitized audit summaries. It does not include the original APK/archive, extracted scripts or the distributable binary overlay.

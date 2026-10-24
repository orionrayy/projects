# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.22. Static source-structure checks PASS; localization remains incomplete.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for Death Road to Canada. The original Canada-bound campaign flow remains an invariant.

## Verified checkpoint v2.22
- Baseline inventory: 541 script/text files, 17,329 quoted literal occurrences, 13,038 unique literal values.
- Heuristic player-facing inventory: 7,490 / 10,844 rows marked localized (**69.07%**).
- v2.22 scope: contextual full-expression localization in camp choices, character bio text, and selected encounters: `events/camp/camp3.df`, `charstats-textfill.df`, `events/common/common4.df`, `events/rareloc/rare1.df`, with two presentation helper macros in `cyoa-charstats.df`.
- 94 display expressions rewritten; 183 existing literal tokens changed; 138 inventory rows newly marked.
- Static source-structure validation reports zero failures and preserves literal-token/line counts in the four expression-only files; the helper file deliberately adds two literals and two lines. ZIP CRC validation passes.
- **QA follow-up:** 49 exact mapping rules are recorded as missed after contextual rewrites. These are not counted as successful rewrites and need reconciliation/review.
- Runtime gameplay, save/load and APK rebuild/signing: NOT RUN.

The 69.07% figure is an inventory heuristic, not semantic completeness or in-game screen coverage. Full player-visible localization is not complete.

## Project records
- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.22 checkpoint report](docs/CHECKPOINT_v2.22.md)
- [Localization guide](docs/LOKALISASI_ID.md)
- [Slang research](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation](docs/BUILD_AND_VALIDATION.md)
- [Coverage summary](audit/coverage.json)
- [Static validation](audit/validation_report.json)
- [Version history](audit/version_history.json)

## Voice and slang policy
Use natural, context-driven Indonesian with distinct NPC personas, blunt sarcasm and profanity where appropriate. Meme terms such as `ragnamok`, `jomok/perjomokan` and `cewe standar TikTok` must remain context-bound; see the localization guide and slang research for confidence notes.

## Distribution boundary
The public repository contains authored documentation, research and sanitized audit summaries. It does not include the original APK/archive, full extracted game scripts, source inventory, or binary localization overlay.

# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.24. Static source-structure checks PASS; localization remains incomplete.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for Death Road to Canada. The original Canada-bound campaign flow remains an invariant.

## Verified checkpoint v2.24
- Scope: character personality banter, shared road-trip one-liners, and special-character response phrases across seven scripts: `aggressive.df`, `passive.df`, `pessimist.df`, `dull.df`, `sharp.df`, `blurbdeck.df`, and `screply.df`.
- 277 contextual mapping rules; 279 literal occurrences changed.
- Two dynamic father-topic expressions reordered for natural Indonesian word order without changing token count or campaign logic.
- Static structure: PASS. Literal-token count and line count preserved in all seven touched files; non-string source skeleton checks pass.
- Package: 301 entries; ZIP CRC PASS; 300 manifest-listed files validated with zero hash mismatches.
- The 14 obvious English oneliners found during manual QA in `sharp.df` were included in the batch.

## Coverage and test limits
The last measured inventory heuristic remains the **v2.22 baseline: 7,490 / 10,844 = 69.07%**. This metric has **not** been recalculated for v2.24 and must not be presented as a current v2.24 coverage score. The candidate inventory is still a historical heuristic queue requiring comment-aware refresh and semantic review.

Full player-visible localization is not complete. Runtime gameplay, UI-fit checks, save/load, and APK rebuild/signing were NOT RUN.

## Project records
- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.24 checkpoint report](docs/CHECKPOINT_v2.24.md)
- [v2.23 checkpoint report](docs/CHECKPOINT_v2.23.md)
- [Localization guide](docs/LOKALISASI_ID.md)
- [Slang research](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation](docs/BUILD_AND_VALIDATION.md)
- [Coverage summary](audit/coverage.json)
- [Static validation](audit/validation_report.json)
- [v2.24 banter summary](audit/v2.24_banter_summary.json)
- [Version history](audit/version_history.json)

## Voice and slang policy
Use natural, context-driven Indonesian with distinct NPC personas, blunt sarcasm and profanity where appropriate. Meme terms such as `ragnamok`, `jomok/perjomokan` and `cewe standar TikTok` must remain context-bound; see the localization guide and slang research for confidence notes.

## Distribution boundary
The public repository contains authored documentation, research and sanitized audit summaries. It does not include the original APK/archive, full extracted game scripts, source inventory, or binary localization overlay.

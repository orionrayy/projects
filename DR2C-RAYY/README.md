# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.25. Static source-structure checks PASS; localization remains incomplete.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for Death Road to Canada. The original Canada-bound campaign flow remains an invariant.

## Verified checkpoint v2.25
- Scope: two active player-facing dialogue files: `assets/deathforth/blurb/optimist.df` and `assets/deathforth/blurb/sc/wrestler.df`.
- 63 contextual mapping rules applied; 63 literal occurrences changed.
- The optimistic survivor's sunny-day/road-trip banter and the wrestler's character-specific quips and dynamic description fragments were localized. Proper names, wrestling move names, censor-mask placeholders, and non-dialogue structure were preserved where required.
- Static structure: PASS. `optimist.df`: 29 quote tokens and 114 lines preserved. `sc/wrestler.df`: 34 quote tokens and 137 lines preserved. Mapped English source residues remaining: 0.
- Package: 305 ZIP entries; CRC PASS; no duplicate paths; 304 manifest-listed files with zero hash mismatches; no machine-local path leaks.
- Artifact SHA-256: `693714b5f2a1e79f0e8b5c9749f7f4dfe1c6ffaa4dc891d0ee689549f82f7fe5`.

## Coverage and test limits
The last measured inventory heuristic remains the **v2.22 baseline: 7,490 / 10,844 = 69.07%**. It has **not** been recomputed for v2.25 and must not be presented as a current v2.25 coverage score. It is not semantic completeness or in-game screen coverage.

Full player-visible localization is not complete. Runtime gameplay, actual UI fit, save/load, and APK rebuild/signing were NOT RUN.

## Project records
- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.25 checkpoint report](docs/CHECKPOINT_v2.25.md)
- [v2.24 checkpoint report](docs/CHECKPOINT_v2.24.md)
- [Localization guide](docs/LOKALISASI_ID.md)
- [Slang research](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation](docs/BUILD_AND_VALIDATION.md)
- [Coverage summary](audit/coverage.json)
- [Static validation](audit/validation_report.json)
- [v2.25 character-banter audit](audit/v2.25_character_banter_summary.json)
- [Version history](audit/version_history.json)

## Voice and slang policy
Use natural, context-driven Indonesian with distinct NPC personas, blunt sarcasm and profanity where appropriate. Meme terms such as `ragnamok`, `jomok/perjomokan` and `cewe standar TikTok` must remain context-bound; see the localization guide and slang research for confidence notes.

## Distribution boundary
The public repository contains authored documentation, research and sanitized audit summaries. It does not include the original APK/archive, full extracted game scripts, source inventory, or binary localization overlay.

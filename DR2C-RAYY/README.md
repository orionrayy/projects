# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.26. Static source-structure checks PASS; localization remains incomplete.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for Death Road to Canada. The original Canada-bound campaign flow remains an invariant.

## Verified checkpoint v2.26
- Scope: five special-character dialogue/emote profiles: `assets/deathforth/blurb/sc/beeman.df`, `boxer.df`, `caveman.df`, `knight.df`, and `ninja.df`.
- 66 exact-context mappings applied; 66 literal occurrences changed.
- The batch localizes Beeman's motivational bee-themed voice, Boxer training banter, Caveman time-travel jokes, Knight's chivalric voice, and Ninja dialogue/emotes.
- Static structure: PASS. Token/line counts preserved for all five files; no mapped English source residues remain; code skeletons unchanged.
- Package: 312 ZIP entries; CRC PASS; no duplicate paths; 311 manifest-listed files with zero hash mismatches; no machine-local path leaks.
- Artifact SHA-256: `edda11648c4f7ed32d1413b154fd70e65943edfb367f18c6bffa0b5119a3f02c` (11,275,547 bytes).

## Coverage and test limits
The last measured inventory heuristic remains the **v2.22 baseline: 7,490 / 10,844 = 69.07%**. It has **not** been recomputed for v2.26 and is not a current v2.26 coverage score, semantic completeness estimate, or runtime screen-coverage measure.

Full player-visible localization is not complete. Runtime gameplay, actual UI fit, save/load, and APK rebuild/signing were NOT RUN.

## Project records
- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.26 checkpoint report](docs/CHECKPOINT_v2.26.md)
- [v2.25 checkpoint report](docs/CHECKPOINT_v2.25.md)
- [Localization guide](docs/LOKALISASI_ID.md)
- [Slang research](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation](docs/BUILD_AND_VALIDATION.md)
- [Coverage summary](audit/coverage.json)
- [Static validation](audit/validation_report.json)
- [v2.26 character-pack audit](audit/v2.26_character_pack_summary.json)
- [Version history](audit/version_history.json)

## Voice and slang policy
Use natural, context-driven Indonesian with distinct NPC personas, blunt sarcasm and profanity where appropriate. Meme terms such as `ragnamok`, `jomok/perjomokan` and `cewe standar TikTok` must remain context-bound; see the localization guide and slang research for confidence notes.

## Distribution boundary
The public repository contains authored documentation, research and sanitized audit summaries. It does not include the original APK/archive, full extracted game scripts, source inventory, or binary localization overlay.

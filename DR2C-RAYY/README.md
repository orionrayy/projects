# DR2C VORENYX — Indonesian Localization

**Current checkpoint: v2.23. Static source-structure checks PASS; localization remains incomplete.**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for Death Road to Canada. The original Canada-bound campaign flow remains an invariant.

## Verified checkpoint v2.23
- Scope: contextual English-residue cleanup in `assets/deathforth/events/camp/camp3.df`.
- 51 distinct source literals localized across 52 literal occurrences.
- All 47 historical exact-mapping misses for `camp3.df` from v2.22 repaired.
- The other two historical mapping warnings reconciled: a proper name remains unchanged, and a stale rule points to a source literal already absent after a previous contextual rewrite.
- Exact-mapping misses remaining after reconciliation: 0.
- Source integrity: quoted-literal count preserved (177 before/after); line count preserved (418 before/after).
- Packaged patch: 294 entries; ZIP CRC scan PASS.

## Coverage and test limits
The last measured inventory heuristic remains the **v2.22 baseline: 7,490 / 10,844 = 69.07%**. The v2.23 heuristic has **not** been recalculated, so 69.07% must not be interpreted as a new v2.23 measurement. The candidate inventory includes heuristic/context artifacts and still needs semantic reclassification.

Full player-visible localization is not complete. Runtime gameplay, UI-fit checks, save/load, and APK rebuild/signing were NOT RUN.

## Project records
- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.23 checkpoint report](docs/CHECKPOINT_v2.23.md)
- [v2.22 checkpoint report](docs/CHECKPOINT_v2.22.md)
- [Localization guide](docs/LOKALISASI_ID.md)
- [Slang research](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Build and validation](docs/BUILD_AND_VALIDATION.md)
- [Coverage summary](audit/coverage.json)
- [Static validation](audit/validation_report.json)
- [v2.23 mapping reconciliation](audit/v2.23_reconciliation_summary.json)
- [Version history](audit/version_history.json)

## Voice and slang policy
Use natural, context-driven Indonesian with distinct NPC personas, blunt sarcasm and profanity where appropriate. Meme terms such as `ragnamok`, `jomok/perjomokan` and `cewe standar TikTok` must remain context-bound; see the localization guide and slang research for confidence notes.

## Distribution boundary
The public repository contains authored documentation, research and sanitized audit summaries. It does not include the original APK/archive, full extracted game scripts, source inventory, or binary localization overlay.

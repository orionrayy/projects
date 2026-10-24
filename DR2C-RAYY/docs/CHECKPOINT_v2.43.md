# DR2C VORENYX v2.43 — Targeted Localization Checkpoint

**Date:** 24 October 2026  
**Status:** Targeted static checks PASS; runtime validation not performed.

## Work completed

- Changed **159 quoted-string occurrences across 58 overlay files**.
- Added **9 previously unoverlaid modules** for selected visible dialogue, character emotes, event instructions, and trade/mall signs.
- Zero unmatched mapping rules.
- Line counts, quoted-token counts, non-string code skeletons, and resource path literals were preserved.
- Patch ZIP: **444 entries**, 443 manifest records; CRC PASS; zero hash failures, unmanifested entries, or duplicate paths.
- Local project archive v2.8: **472 entries**, 471 checksum records; CRC PASS; zero hash failures, unmanifested entries, or duplicate paths.

## Heuristic residue recheck

Compared with the inherited v2.40 candidate queue (598 rows), the v2.43 exact-match triage found **131 active candidate rows**, down from 241 after v2.42. Of these, 120 exact literals remain in files with overlays and 11 rows reference files without overlays. The five P1 exact matches are the game’s official title strings, intentionally preserved.

This is a heuristic row-level recheck, not a confirmed count of untranslated player-visible text. Some rows may be duplicates, non-player-facing text, proper names, or false positives. Global semantic/player-visible coverage remains **NOT COMPUTED**.

## Local artifacts

- Patch: `DR2C_VORENYX_ID_v2.43_localization_patch.zip`
- Patch SHA-256: `00ff7866242e8b3aca4fc749e93455ba1c795c4eec99fd15baa07ab483aca024`
- Full project archive: `DR2C_VORENYX_Project_Archive_v2.8.zip`
- Archive SHA-256: `417d8256a74ad6ed64072c93fd1e9b9f255cdb7bca41c49c96333fba6a569cd5`

The binary patch, full local archive, and detailed translation ledger are not stored in this public repository.

## Not verified

Gameplay/event-path runtime, UI fit/overflow, save/load, device testing, and APK rebuild/signing were **NOT RUN / NOT PERFORMED**. The patch is a data/script overlay, not a rebuilt APK.

See [sanitized validation summary](../audit/v2.43_static_validation_summary.json) and [heuristic residual recheck](../audit/v2.43_residual_recheck.json).

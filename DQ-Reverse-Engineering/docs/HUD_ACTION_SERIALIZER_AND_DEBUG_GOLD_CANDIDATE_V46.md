# HUD action serializer and one-row debug candidate — v46

**Status: locally reconstructed and structurally checked. Not packaged into an STK, built as an APK, installed, or runtime-verified.**

## v46 implementation

- Adds a field-preserving encoder for the existing v12 HUD action-section framing, including exact no-op round trips.
- Rejects duplicate action names, inconsistent declared statement counts, invalid empty statement payloads, unreasonable payload sizes, and malformed output after reparse.
- Adds a separate-output experiment builder. It clones the existing hp_btn button record, assigns it the name gold_btn, the label Gold +100K, and action name onAddGold, then appends one matching action record. The source HUD path cannot be the output path, and an existing output candidate is not overwritten.

## Local evidence

Source: Resources/HUD/debug.hud

| Check | Result |
|---|---:|
| Source HUD size | 12,887 bytes |
| Candidate HUD size | 13,143 bytes |
| Source element records | 71 |
| Candidate element records | 72 |
| Source action records | 13 |
| Candidate action records | 14 |
| Source SHA-256 | 02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6 |
| Candidate SHA-256 | 9ad439b5055928a2d877b120208db1b4878bc312d50cbfa606fec95e00880bcf |

The new action payload uses the same static action-call shape as existing debug actions and routes to uai_gp_hud.onDebug(6.0). Separate ARM64 disassembly evidence associates branch 6.0 with RewardGold(100000.0). The button is placed at Y=0.0 between the existing Character (+0.2) and Heroic (-0.2) button centers; actual rendering, clipping, input dispatch, game-state mutation, persistence, and balance were not observed in a running game.

The 68 source HUD action sections were each parsed and re-encoded byte-identically in a local asset-root sweep. The candidate builder separately reparses the output and checks the new button/action binding. Five synthetic serializer tests pass, and the combined local v42/v43/v45/v46 suite passes 23 tests.

## Boundary and next gate

The v46 candidate is a **single-row feasibility probe**, not the intended 222-entry scrollable Cheats menu. It does not add a generic List, item population, selected-row callback, stable cheat-ID registry, allow-listed dispatcher, or save/load-safe effect bridge. No raw HUD asset is committed here. The candidate remains local at /mnt/data/dqwork/candidates/debug_gold_candidate_verify_v46.hud.

The next engineering gate is to validate the exact dispatch branch in a controlled test build, then independently repack and re-validate the STK before any app/package experiment. Until runtime verification, the Gold action remains a static candidate.

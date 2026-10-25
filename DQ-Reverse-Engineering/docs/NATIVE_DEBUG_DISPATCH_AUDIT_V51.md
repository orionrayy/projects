# Native debug-dispatch audit — v51

**Status: static reverse-engineering evidence only. No in-game runtime test has passed. No general 222-cheat native adapter is implemented.**

## Scope

This note records the evidence behind the v50 pause-screen Gold +100K candidate and defines the boundary between a verified archive edit and a verified gameplay feature. It does not treat function names or catalog metadata as proof that a cheat can be invoked safely.

## Source identity and static evidence

- Original XAPK: `Dungeon+Quest_3.3.2.0_APKPure.xapk`
- Original XAPK SHA-256: `3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b`
- Stock `S3DMain.smf` SHA-256: `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3`
- ARM64 `libS3DClient.so` SHA-256: `0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083`
- Native function symbol: `uai_gp_hud::onDebug(int, S3DX::AIVariable const*, S3DX::AIVariable*)`
- Function entry in the inspected ARM64 ELF: `0x6d5048`
- The `onDebug` argument is used as a numeric dispatch code in the inspected native body.

### Gold branch evidence

The static disassembly contains an equality check against dispatch code `6.0`. The associated branch constructs the numeric amount `100000.0` and routes it to the `RewardGold` gameplay handler. The separate v50 candidate HUD button routes to `uai_gp_hud.onDebug(6.0)`.

This evidence supports that the candidate action is wired to the native Gold-reward branch in this binary. It does **not** establish that the modified pause UI is visible, receives touch input, reaches this callback in the installed game, updates the displayed currency, persists after reload, or is safe for the save/account state.

### Other branches and non-goals

The existing developer/debug HUD includes other numeric `onDebug` routes. Some branches lead to operations other than a simple reward, including a `SpendGold` path. These routes are not suitable to expose blindly. This audit does not add or expose the spending branch.

The symbol/name inventory in `uai_gp_hud.aim` includes functions such as `RewardGold`, `RewardDust`, `SpendGold`, and `SpawnPlayer`. The AIM parser currently validates record framing and extracts names; opaque function bodies are not rewritten or fully interpreted. Function-name presence alone is not a safe call contract.

## v50 archive delta

Candidate STK: `S3DMain_pause_options_gold_v50.smf`

| Check | Result |
|---|---:|
| Candidate STK size | 34,011,446 bytes |
| Candidate STK SHA-256 | `e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e` |
| Entries parsed and decoded | 5,630 / 5,630 |
| Entry whose decoded bytes differ | `Resources/HUD/pause.hud` only |
| Pause HUD elements | 126 → 127 |
| Pause HUD actions | 64 → 65 |

The new HUD record is a candidate button named `gold_reward_100k_btn` on the existing Gameplay panel. It is a feasibility probe; the archive has been validated structurally, but there is no recorded device/emulator gameplay observation for this button.

## Why the full 222-entry menu is still not connected

The current canonical catalog contains 222 entries across 14 categories. A current catalog audit reports `integration_status = requires_game_adapter` for **all 222 entries**. The Android Cheats Sandbox app stages local values and previews action requests only; it intentionally reports `GAME LINK · DISCONNECTED` and has no code to write game memory, save data, native model state, IAP state, cloud data, achievements, or leaderboards.

The stock Options controller has four observed tabs, and there is no confirmed stock `onShowCheats` tab callback. The existing `uai_gp_debug.aim` is a shader-diagnostics model, not a verified generic gameplay-cheat controller. Native List wrappers are present, but no verified generic List population + selection callback path has been established for this catalog.

Therefore, there is not yet a proven end-to-end mapping from a stable catalog ID to a safe native handler and validated parameter contract. Implementing a generic dispatcher before that mapping exists would risk invoking unrelated game operations or corrupting state.

## Required verification gates

1. **UI dispatch:** install on a test device/emulator and prove the pause-screen candidate is rendered, tappable, and reaches the expected callback.
2. **Effect and persistence:** observe the currency delta in-game and after a clean save/reload; confirm no unrelated state or progression changes.
3. **Safe adapter contract:** for each proposed catalog item, identify a specific native handler, parameter schema, range constraints, preconditions, and an explicit reason it is safe. Unknown entries must remain disabled.
4. **Regression:** preserve the untouched original package and save, and test launch, main-menu transition, pause/unpause, gameplay start, and save reload.
5. **Release packaging:** rebuild with reproducible inputs and retain signatures/checksums. A locally signed candidate cannot update an official-signature installation in place; do not uninstall the official copy without a separately verified save backup/restore path.

## Result

The evidence supports a single static Gold +100K action candidate in v50. It does not support claims that this candidate is runtime-verified, that the APK is stable for general use, or that any of the catalog's 222 entries are connected to the original game.

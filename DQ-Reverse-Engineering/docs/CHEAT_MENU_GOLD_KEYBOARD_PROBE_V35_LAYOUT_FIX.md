# Cheat Menu v35 — visible Set Gold layout fix

Date: 2026-10-25
Target: Dungeon Quest Android 3.3.2.0
Status: built and locally validated; phone test pending.

## User-reported result

The v34 parallel build still displayed the original six-card Debug Menu and no Set Gold button. A binary-level comparison of the exact HUD payload explains why.

## Root cause

The v34 patcher contained two layout defects:

1. It rebuilt the first 71 HUD elements from the original asset, discarding three deliberate position/size adjustments that v33 made to the Add Levels buttons to reserve a row for extra controls.
2. It wrote transform floats at offsets 33/37/41/45, but the copied element record has a 17-byte ID. Its transform fields start at offsets 34/38/42/46. The one-byte-offset mistake overwrote the preceding metadata byte and produced an invalid transform.

## Corrected v35 artifact

- Artifact: `Dungeon_Quest_3.3.2.0_CheatMenu_SetGoldKeyboardProbe_v35_PARALLEL_LABEL.xapk`
- Application ID: `com.shinybox.dqv34`
- Launcher label: `DQ Test Build`
- SHA-256: `fe3e9a188573c711fa86c760d995bb348b7866a8316c7b7f64951934f14bd715`
- Size: 57,571,119 bytes
- Signer fingerprint: `6ba5a7ebddfccc1fde12c0b7538bd390dad51bc3b963d03c68e7545b961917b0`

The same package ID and signer are retained from v34 PARALLEL LABEL, so v35 should install as an update to that test app without uninstalling v33. The original store app `com.shinybox.smash` is not the target.

## What changed

- Keeps the v33 prefix, including its Add Levels layout adjustments.
- Replaces the four tiny appended Gold buttons with one centered Set Gold control.
- Correctly writes the element transform at offsets 34/38/42/46: x=0.0, y=-0.79, width=0.82, height=0.18.
- Debug HUD: 72 elements / 14 action records.
- Set Gold label and the `uai_gp_hud.onSetGold` callback target are present.

## Validation

All 20 APK splits pass the strict local v2 signer structure/content-digest/RSA checks, their ZIP CRCs and the outer XAPK CRC pass, and native stored-library alignment checks pass. All 5,630 STK entries decode and CRC-check. The header key matches the decoded metadata-table CRC32. The exact original 71-element byte prefix from v33 is preserved, with only the four appended tiny Gold controls replaced by one corrected button.

These are static checks, not official Android SDK `apksigner` output and not a runtime test.

## Phone test

Install v35 as an update to the installed `DQ Test Build` v34 parallel app; do not uninstall v33 or the original store app. Open Options → Cheat Menu → Add. Confirm Set Gold is visible, then test whether it opens the game's internal keyboard and commits a custom amount that changes the displayed Gold balance.

If the button appears but does nothing, that will isolate the next remaining blocker to the `onSetGold` callback/keyboard route. Until then, neither the keyboard effect nor custom Gold mutation is marked runtime-verified.

The full 222-entry cheat catalog and generic `−10`, `−1`, `+1`, `+10` stepper UI remain separate workbench features; they are not all wired into this game build.

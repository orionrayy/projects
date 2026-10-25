# Dungeon Quest v34 — Set Gold callback / keyboard probe

Date: 2026-10-25
Build target: Dungeon Quest Android 3.3.2.0
Status: **built and locally validated; device runtime not tested**

## Why v34 exists

The v33 screenshot showed four tiny Gold buttons misplaced between the existing Add Levels and Add Feat cards. The corrected requirement is one **Set Gold** button with a custom amount flow. Generic numeric catalog controls use the separate `−10`, `−1`, `+1`, `+10` steppers and no keyboard input.

v34 removes the three surplus mini Gold controls. It restores the 71 original Debug HUD element records, then appends just one existing-style button record to the Add panel. The label is `Set Gold`, centered and resized to ordinary button dimensions. Its serialized action callback routes to the existing no-argument native model method `uai_gp_hud.onSetGold`.

## Artifact

- XAPK: `Dungeon_Quest_3.3.2.0_CheatMenu_SetGoldKeyboardProbe_v34.xapk`
- SHA-256: `799577cfe1ed0c910f5b21d5c3df4ab6b6d373fe0d4719244214c05ac6d5b008`
- Size: 20 APK splits; approximately 55 MB
- Package ID: `com.shinybox.dqv30`
- Local signer certificate SHA-256: `6ba5a7ebddfccc1fde12c0b7538bd390dad51bc3b963d03c68e7545b961917b0`
- Runtime status: **NOT TESTED ON DEVICE**

The signer is new because the previous local v33 private signing key was not available in this workspace. The probe must therefore be installed after uninstalling the diagnostic package signed with the old key. Do not uninstall the original store package `com.shinybox.smash`.

## HUD / STK diff

- Original Debug HUD: 71 elements, 13 actions.
- v34 Debug HUD: 72 elements, 14 actions.
- The only decoded asset modified in `S3DMain.smf` is `Resources/HUD/debug.hud`.
- All original 71 element records are preserved; all 13 original action records are preserved. Three v33 Gold action rows are removed; one callback row is added.
- All 5,630 STK entries decode and their stored payload CRCs validate. The STK header key equals the CRC32 of the decoded metadata table.
- All 20 split APKs were re-signed with the same local v2 certificate; local v2 verification, inner/outer ZIP CRCs, and native library 16-KiB alignment checks pass.

These checks are local static/package validation, not official Android SDK `apksigner` output or proof of launch.

## What remains unproven

The callback `onSetGold` is a static engine identifier. The button has not yet been tested on the user's phone. It is not established that the callback opens `keyboard.hud`, receives a numeric entry, or sets the player's Gold balance. v34 is therefore a callback probe, not a completed custom Gold feature. No numeric text field was added to the Debug HUD and no four-button Gold stepper remains.

## Phone-only test

1. Uninstall only the existing diagnostic app `com.shinybox.dqv30`, because its signer differs. Keep the original `com.shinybox.smash` installation intact.
2. Install the v34 XAPK and launch offline.
3. Open Options → Cheat Menu → Add and tap **Set Gold**.
4. Record whether the game opens its internal keyboard, whether the value can be entered/confirmed, and whether the visible Gold balance changes.

If the callback is ignored, opens the wrong screen, or crashes, report that exact behavior. Do not mark the Gold input or balance mutation as implemented until the phone test proves it.

## Companion workbench v35

The single-file HTML catalog workbench is a separate design/test artifact. It retains all 222 catalog entries and uses:
- an on-screen keypad made from buttons for custom Gold amounts, so it does not rely on Android's system keyboard; and
- `−10`, `−1`, `+1`, `+10` stepper buttons for other numeric drafts, with bounds/step clamping.

Browser tests passed for entering `123` in the custom keypad, applying exactly `123` to the local draft, and incrementing the Player Max Health draft from 1 to 3.5 to 3.75 using the +10/+1 steppers. The workbench explicitly remains `GAME LINK: DISCONNECTED`; it does not apply settings to Dungeon Quest.

No billing receipt, paid entitlement, cloud-save, achievement, or leaderboard logic was modified. The complete 222-cheat game integration remains incomplete.


## Workbench source in the repository

The corrected, single-file catalog workbench is committed at [cheats_options_workbench_v35.html](../cheats-sandbox/cheats_options_workbench_v35.html). It contains all 222 catalog entries, button-only steppers for ordinary numeric settings, and the custom button-built Gold keypad. It remains an offline/local staging tool, not a game adapter or an in-game APK feature.


## Important correction — APK v2 signature encoding

The user's installer screenshot showed `INSTALL_PARSE_FAILED_NO_CERTIFICATES` and `No supported signatures found`. This was a real defect in the first generated v34 artifact, not a keyboard/HUD failure. The APK v2 signer-sequence value was missing one required length-prefixed layer. The local v2 verifier had the same parsing assumption and therefore incorrectly accepted the malformed encoding.

**Do not install** the earlier file `Dungeon_Quest_3.3.2.0_CheatMenu_SetGoldKeyboardProbe_v34.xapk` (SHA-256 `799577cfe1ed0c910f5b21d5c3df4ab6b6d373fe0d4719244214c05ac6d5b008`).

A corrected build has been produced as:
- `Dungeon_Quest_3.3.2.0_CheatMenu_SetGoldKeyboardProbe_v34_SIGNFIX.xapk`
- SHA-256: `2cb1502410873003d2178eb1b94e44e5decf8150371f116fc456a82aac3820b0`
- Same certificate SHA-256 as the failed v34 build: `6ba5a7ebddfccc1fde12c0b7538bd390dad51bc3b963d03c68e7545b961917b0`

The corrected independent structural check reads the two required signer-sequence length prefixes, then validates the signed-data, signature, public key, certificate, digest record, SHA-256 content digest, and RSA signature fields. All 20 APK splits pass this stricter local verifier, their inner ZIP CRC checks pass, and the XAPK outer CRC passes. This is not an official Android SDK `apksigner` result; device installation remains the final check.

The old malformed file was not installed, so proceed with the corrected SIGNFIX file using the previously stated safe test steps. It keeps the same v34 certificate; the diagnostic app still must be uninstalled if the installed v31/v33 build has a different signer. Never uninstall the original store app `com.shinybox.smash`.

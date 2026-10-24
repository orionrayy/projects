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
- Local signer certificate SHA-256: `6ba5a7ebddfc4fca4a6a9c5e69f1c0c76c48a0c9466a7dd63b6701a8e8a58d63`
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

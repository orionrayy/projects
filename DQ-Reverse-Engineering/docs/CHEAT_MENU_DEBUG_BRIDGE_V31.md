# Cheat Menu debug bridge v31

Date: 2026-10-25
Status: built and statically validated; **not yet runtime-tested on the user's phone**.

## User-observed v30 result

The user confirmed the app opens after applying the CRC/header-key fix, but the Options screen's Cheat Menu tab still displays the original social links and Restore Purchases. The v30 patch changed the visible tab label only; it did not route to an actual cheat/debug screen.

## v31 approach

Rather than inventing native game functions, this candidate uses the debug HUD already shipped inside the original asset pack: `Resources/HUD/debug.hud`. The Cheat Menu tab's callback is renamed from `onShowSocial` to `onShowCheats` in both the HUD element and action table. The callback preserves the existing page visibility and tab-selection parameters, then invokes the existing native route `uai_gp_hud.onDebug(0)`.

The bundled debug HUD contains controls routed to existing native handler values:
- `onDebug(2)`: go to level/floor
- `onDebug(3)`: set boss
- `onDebug(4)`: set level
- `onDebug(8..10)`: create Legend/MS/CS items/rewards
- `onDebug(11..16)`: add level, heroic, feat, crystal, eternal, or battle related options

These are findings from static resource/native inspection; effect, persistence, and whether the tab successfully opens this HUD are **not yet verified on-device**. Use a disposable/offline game profile and do not exercise potentially destructive actions until the panel itself is confirmed.

## Artifact and validation

- XAPK: `Dungeon_Quest_3.3.2.0_CheatMenu_DebugBridge_v31.xapk`
- Package ID: `com.shinybox.dqv30`
- SHA-256: `63745c50ae36214fa01c7c949040f7ec7f5cdd247aafde574df70afa983b6ae6`
- Size: 57,591,162 bytes; 20 split APKs
- Signer certificate SHA-256: `a0f7e52d67c10d0b0347774cab2fae3f5c965d711a408a3479b14456da926e0b` (same signer as v30, so it should update in place)
- All 5,630 STK entries decode and their CRC values validate.
- Decoded metadata table CRC32 and STK header key both equal `0xaa01474b`.
- Alias relationships are preserved; target compressed payload grew by 15 bytes with all subsequent offsets adjusted consistently.
- Only decoded asset changed: `Resources/HUD/pause.hud`.
- 19 non-base APK splits are byte-identical to v30; the only non-signature member difference in the base APK is `assets/S3DMain.smf`.
- Locally verified v2 signatures and all inner/outer ZIP CRCs passed. A local verifier is not a substitute for runtime testing.

## Phone-only procedure

1. Install v31 as an update to the currently installed v30. Do not uninstall first: package ID and signer are the same.
2. Launch offline; open Options → Cheat Menu.
3. Confirm whether the built-in debug panel opens. Do not use primary-account/cloud-save flows, and avoid changing progress or generating items until behavior is confirmed.
4. If the installer refuses, record the exact error. If it installs but crashes or still shows social links, report that exact result before another build is made.

The panel currently invokes the original debug HUD overlay; closing the overlay may return to the underlying Social page. This is a transitional bridge, not a polished standalone cheat UI and not an on-device verified release.

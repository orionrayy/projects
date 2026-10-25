# v34 PARALLEL — Set Gold keyboard probe

- Artifact: `Dungeon_Quest_3.3.2.0_CheatMenu_SetGoldKeyboardProbe_v34_PARALLEL.xapk`
- Package ID: `com.shinybox.dqv34`
- Size: 57,571,164 bytes
- SHA-256: `c507bfc234980f310ac42a89dd40f83fade7548071b3565fae178283b6b4e455`
- Split count: 20
- Signer SHA-256: `6ba5a7ebddfccc1fde12c0b7538bd390dad51bc3b963d03c68e7545b961917b0`
- Runtime: not yet tested on device.

The user's Android installer reported `INSTALL_FAILED_UPDATE_INCOMPATIBLE` because v33 is installed under `com.shinybox.dqv30` with a different local signing key. The new build uses `com.shinybox.dqv34` so it can be installed side-by-side and preserve v33 app data. All 20 split manifests match the new application ID; the XAPK manifest also matches. Every split passes the local APK v2 structural/digest/RSA verifier, inner/outer ZIP CRC checks, and native stored-library 16-KiB alignment checks. This is not official Android SDK apksigner output and runtime remains pending.

After installing, open Options → Cheat Menu → Add → Set Gold. Check whether the game's keyboard opens, whether a value can be entered and confirmed, and whether the displayed balance changes. This remains a callback probe, not a complete Gold adapter or 222-cheat release.
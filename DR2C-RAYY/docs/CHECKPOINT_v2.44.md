# DR2C VORENYX v2.44 — Start/UI Hotfix Checkpoint

**Status: static package checks PASS; runtime Start and visual stability NOT VERIFIED.**

## Observed symptoms
The user-provided Android recording shows the title menu remaining on START after attempted taps, gameplay UI rendered as a narrow centered band with large portrait black bars, and settings controls clipped at the right edge. An APKVISION graphic appears behind Android's “Open with” chooser.

## Changes in this hotfix
1. **Canonical boot marker restored.** In `assets/deathforth/boot.df`, changed the internal marker from `"PENANDA-GAME" $anew` back to the canonical `"GAME-MARKER" $anew`. This is a code marker, not translated UI text. Static check PASS; whether this alone restores Start still needs runtime testing.
2. **Orientation fixed.** `SplashActivity` and `DrtcGameActivity` changed from `sensorLandscape` (6) to fixed `landscape` (0), targeting the recording's letterboxing and clipped right-side settings row.
3. **Start route inspected.** Static checks found the `main-event-do-select` defer, registered select handler, `select-start` registration, tutorial file and expected tutorial/CYOA route. These checks do not establish a working tap on a device.

## APK candidate
- File: `DR2C_VORENYX_v2.44_START_UI_HOTFIX.apk`
- Size: 39,748,341 bytes
- SHA-256: `e28314611411aeba2fdd6bf2cee918fa64ddecac159536e4a39918e7af81f8a6`
- ZIP: 1,015 entries, CRC PASS, no duplicate paths.
- 272 overlay payloads verified with zero mismatches; the intentional `boot.df` identifier correction is separately recorded.
- 3 DEX files and 16 native libraries preserved for arm64-v8a and armeabi-v7a; native library alignment PASS.
- Android signature schemes v1/v2/v3: PASS using official Android SDK Build Tools 35.0.1 `apksigner`.
- Signer certificate SHA-256: `6ea04e10965de1459a7fee845e8ae903bc1535a744f4762c14b2c7bb82eb13f9`; this is a local certificate, not the game's original publisher certificate.

## APKVISION finding
The VORENYX splash image itself contains no APKVISION logo. APKVISION namespaces remain in `classes3.dex` and `libstub.so` from the supplied repackaged base. This hotfix does not remove or bypass that third-party distributor/provenance wrapper. To produce a clean build without that wrapper branding, use a clean, authorized base APK from the publisher; do not strip or patch the repackaging wrapper blindly.

## Not verified
Android install, launch, Start tap, gameplay, actual screen/UI fit, save/load and stability were **NOT TESTED** because no connected device/emulator/ADB was available. PairIP/Play license-check components remain; a locally signed package may be rejected. The original publisher key was not supplied. This APK is a hotfix candidate, **not a confirmed stable release**.

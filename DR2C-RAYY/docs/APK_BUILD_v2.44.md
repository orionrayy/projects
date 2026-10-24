# DR2C VORENYX v2.44 — Start/UI Hotfix Build Report

## Result
A new APK hotfix candidate was assembled and passes static package and Android signature checks. Runtime Start behavior and UI fit are not yet verified on a device.

## Root-cause candidate: internal marker mismatch
The packaged `assets/deathforth/boot.df` used `"PENANDA-GAME" $anew`, while the rest of the engine source references the canonical marker `"GAME-MARKER"`. This is an internal code symbol, not a display string. v2.44 restores `GAME-MARKER` and static source checks pass. This is a confirmed identifier inconsistency, but the causal link to the Start tap cannot be proven without gameplay execution.

## UI orientation
The recording shows a portrait screen containing a narrow horizontal game viewport and clipped controls at the right. Both `SplashActivity` and `DrtcGameActivity` had orientation value 6 (`sensorLandscape`); v2.44 sets them to 0 (fixed landscape). This is a targeted correction and still requires device verification for screen-fit and touch-hitbox accuracy.

## Artifact integrity
- APK: `DR2C_VORENYX_v2.44_START_UI_HOTFIX.apk`
- Bytes: 39,748,341
- SHA-256: `e28314611411aeba2fdd6bf2cee918fa64ddecac159536e4a39918e7af81f8a6`
- ZIP entries: 1,015; CRC PASS; duplicate paths: 0.
- Overlay payloads checked: 272; hash mismatches: 0.
- DEX: 3 files.
- Native libraries: 16; ABIs: arm64-v8a and armeabi-v7a; alignment PASS.
- Signature schemes v1/v2/v3: PASS with Android SDK Build Tools 35.0.1 `apksigner`.
- Signing certificate: local key, SHA-256 `6ea04e10965de1459a7fee845e8ae903bc1535a744f4762c14b2c7bb82eb13f9`; not original publisher signing key.

## APKVISION
The VORENYX splash image is clean and does not contain APKVISION. The supplied APK base contains APKVISION namespaces in `classes3.dex` and `libstub.so`, indicating a distributor/repackaging wrapper. This hotfix does not strip or bypass that wrapper. To get a clean no-APKVISION package, a clean authorized base APK from the publisher is required.

## Runtime blocker / verification gap
PairIP/Play license-check components remain and may reject a locally re-signed APK. No license or anti-tamper bypass was attempted. An Android device/emulator/ADB was not available, so install, launch, Start tap, gameplay, UI fit, save/load and stability remain NOT TESTED. Do not label this artifact stable until those tests pass.

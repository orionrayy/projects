# Build and Validation — DR2C VORENYX v2.44 Start/UI Hotfix Candidate

## Local release artifact
- APK: DR2C_VORENYX_v2.44_START_UI_HOTFIX.apk
- Size: 39748341 bytes
- SHA-256: e28314611411aeba2fdd6bf2cee918fa64ddecac159536e4a39918e7af81f8a6
- Package: com.noodlecake.drtc, game version 1.8.2, version code 57
- Minimum / target SDK: 23 / 35
- Signature schemes: v1, v2 and v3 verified using Android SDK Build Tools 35.0.1 apksigner 0.9.
- APK ZIP: 1,015 entries; CRC PASS; zero duplicate paths.
- All 272 v2.43 overlay payloads verified; the intentional hotfixed boot.df differs from the source patch only by restoring the canonical marker.
- 3 DEX files; 16 stored native libraries for arm64-v8a and armeabi-v7a; all stored .so payloads are 4-byte aligned.

## Hotfixes
1. Restored "GAME-MARKER" $anew instead of "PENANDA-GAME" $anew. This is an internal Forth marker, not display text. Static verification confirms it is restored; causal validation still requires runtime testing.
2. Changed screenOrientation for com.noodlecake.drtc.SplashActivity and com.noodlecake.drtc.DrtcGameActivity from sensor-landscape (6) to landscape (0), targeting portrait letterboxing and clipped settings controls in the supplied recording.
3. Verified static Start route pieces: main-event-do-select defer, registered select handler, select-start, tutorial file existence, and routing to tutorial/CYOA.

## Signing, wrapper and runtime limitations
- Local test certificate SHA-256: 6ea04e10965de1459a7fee845e8ae903bc1535a744f4762c14b2c7bb82eb13f9; this is not the original publisher certificate.
- The manifest retains PairIP/Play license-check components, which may reject a locally re-signed build. No license or anti-tamper bypass was attempted.
- The VORENYX splash artwork has no APKVISION logo, but APKVISION namespaces are present in classes3.dex and libstub.so in the supplied base. This build does not strip the third-party distributor wrapper. An authorized clean base APK is needed for a clean build without APKVISION branding.
- Android install, launch, tapping Start, UI fit/overflow, gameplay, save/load and stability are NOT RUN; no device/emulator/ADB was available. Do not treat this candidate as confirmed stable until runtime tests pass.

See docs/CHECKPOINT_v2.44.md and audit/v2.44_start_ui_hotfix.json.
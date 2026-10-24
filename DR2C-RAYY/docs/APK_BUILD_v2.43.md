# DR2C VORENYX v2.43 — APK Build Report

- Result: **APK assembled; APK Signature Schemes v1, v2 and v3 verified by official `apksigner`.**
- File: `DR2C_VORENYX_v2.43.apk`
- Size: 39,748,335 bytes
- SHA-256: `3019dd04098e9e8fef01045a2e391d9525bf87ef6874b0d0049c5a073a052f25`
- Package: `com.noodlecake.drtc`
- Original game version: `1.8.2` (version code 57)
- SDK range: min 23 / target 35
- Overlay payloads applied and hash-verified: **272** (271 existing entries replaced, one new title-screen image added).
- APK ZIP integrity: PASS (1,015 entries, no duplicate paths, CRC PASS).
- Signature: v1 PASS, v2 PASS, v3 PASS using Android SDK Build Tools 35.0.1 `apksigner` 0.9.
- Native payloads: 16 stored `.so` files across `arm64-v8a` and `armeabi-v7a`; every native library is 4-byte aligned. Three DEX files and required manifest present.
- Signing certificate SHA-256: `6ea04e10965de1459a7fee845e8ae903bc1535a744f4762c14b2c7bb82eb13f9` (local key, not original publisher certificate).

## Stability and launch limitations

The APK is now correctly signed with v2/v3 in addition to v1, resolving the previous v1-only signing-format blocker. However, **runtime stability is still unverified**. The supplied archive does not contain the original publisher's private signing key, and this APK uses a new local certificate. The manifest includes `com.pairip.application.Application` and PairIP/Play license-check components; the game may reject a re-signed package or fail at launch. No licensing or anti-tamper bypass was attempted.

No Android device/emulator/ADB was available. Android install, launch, gameplay/event-path, UI fit/overflow, save/load and stability tests were **NOT RUN**. Do not uninstall the official game or risk existing saves based on this static build alone. A release that is truly confirmed stable needs authorized signing compatibility and runtime tests on a device.

## Patch metadata discrepancy

The v2.43 patch `README.txt` reports 309 changed occurrences across 16 files, while its checkpoint and translation ledger report 159 across 58 files. This discrepancy is intentionally recorded, not silently reconciled to an unsupported number. The 272 figure above is the actual overlay payload count, not a translation count.

The APK and full extracted game content remain local-only. The public GitHub repository has a sanitized build report; the binary APK was not uploaded.

Machine-readable report: `DR2C_VORENYX_v2.43_APK_BUILD_REPORT.json`.

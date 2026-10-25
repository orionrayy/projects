# Dungeon Quest ModKit checkpoint — v71

Date: 25 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
Previous checkpoints: v69 native ABI cross-check, v70 exact-target DEX build and round-trip

## Implemented in v71

- Built a standalone ARM64 diagnostic APK from the pinned v50 Gold +100K candidate, the exact-target v70 assembled DEX, and the side-effect-free native probe library.
- Changed the application ID to com.shinybox.dqv70, a distinct package, to avoid updating or overwriting the official com.shinybox.smash installation.
- Changed the launcher label to DQ v70 Tester, updated the resource package-name entry, and removed unresolved icon attributes from the source standalone base manifest so aapt can inspect the package.
- Preserved the v50 STK payload: the only decoded STK asset difference remains Resources/HUD/pause.hud.
- Signed with a local diagnostic test certificate. The original application ID, original APK/XAPK, source DEX and private test keystore remain untouched/unpublished.
- Added a machine-readable report, human-readable audit, fail-closed report validator, regression suite and GitHub Actions workflow.

## Diagnostic APK identity

- File: DQ_ModKit_v70_ABI_Probe_DIAGNOSTIC_ARM64.apk
- SHA-256: 07898a4997b1f470728087d6c4bcd22660980be6d0670217d6d64c2b1769d0e8
- Size: 57,717,702 bytes
- Package: com.shinybox.dqv70
- Launch label: DQ v70 Tester
- ABI: arm64-v8a; standalone APK (one package)
- Test signer certificate SHA-256: b8f8b624ce1368dca48e3413b4433e81d117fb3cbab904e11ec308ecc79ad60c

## Verified static package gates

- Input candidate, patched DEX and native bridge hashes pinned: PASS.
- ZIP CRC across all package entries: PASS.
- Native library 16 KiB alignment before and after signing: PASS.
- Android apksigner V1, V2 and V3 verification: PASS.
- aapt dump badging, package ID and launcher label: PASS.
- Original application and XAPK modified in place: no.
- Private key in GitHub: no.
- Device install, game launch or native callback inside Dungeon Quest: not tested.

## Status and next gate

This APK is a diagnostic test, not a stable release. The Java helper runs only after engineInitialize reports true and attempts a harmless 21 → 42 native round-trip, followed by unregister at shutdown/restart. The target callback ABI/thread/lifetime semantics remain unverified in the running game, so a native integration defect could still crash the test app.

Gold +100K runtime evidence remains 0/9. The 222-entry catalogue has 0 native routes and 0 runtime-verified effects. Do not remove the official-signed app or use a production save to test. First use a disposable profile and a verified recovery path, preferably offline. Do not bypass IAP receipts, licensing, integrity, cloud/account or anti-tamper behavior.

Evidence:
- [Exact-target DEX v70 report](DEX_LIFECYCLE_TARGET_BUILD_V70.md)
- [v69 native ABI cross-check](NATIVE_CLIENT_ABI_BINARY_CROSSCHECK_V69.md)
- [Diagnostic APK static validation report](DIAGNOSTIC_APK_BUILD_V70.md)
- [Machine-readable APK report](DIAGNOSTIC_APK_BUILD_V70.json)
- [Build/test script](../tools/build_diagnostic_probe_apk_v70.py)

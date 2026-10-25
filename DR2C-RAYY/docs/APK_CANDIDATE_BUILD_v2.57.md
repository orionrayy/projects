# DR2C VORENYX — v2.57 test APK candidate build

**Result: BUILD + STATIC PACKAGE VALIDATION PASS. Android runtime: NOT TESTED.** This checkpoint is not a release claim and is not v2.51 integration.

## Candidate artifact

- File: `DR2C_VORENYX_v2.57_TEST_CANDIDATE.apk`
- Size: 115,614,035 bytes
- SHA-256: `ef66364da7e3d8862b460348d67d397e8132896aaa80f70a9243589d934435e5`
- APK ZIP entries: 1,015; duplicate paths: 0; CRC: PASS
- Deathforth `.df` scripts: 509; escaped backslash-quote regressions: 0
- JAR/v1 signature: PASS (`jarsigner`); signer is a locally generated self-signed test certificate, SHA-256 `8663b5eebde76028e326d80a650ac3a10a99d52470b54cb5a77cf1cba5a7a180`.
- APK Signature Scheme v2: NOT generated/verified; `apksigner` was not available in the build environment.

## Applied changes

1. Reconciled the available source overlay from base + v2.43 localization patch + v2.45 corrective patch + v2.45 Startfix patch.
2. Rewrote 12 selected Indonesian tutorial/CYOA display expressions while preserving tutorial dispatch handlers and ordered single-quoted Forth symbols.
3. Reapplied 13 documented native UI/stat labels in both `arm64-v8a` and `armeabi-v7a` `libmain.so` files at pinned offsets. Each replacement fits its original string slot; file sizes and offsets are preserved.
4. Changed `SplashActivity` and `DrtcGameActivity` `screenOrientation` from sensor-landscape (6) to landscape (0), preserving Android binary manifest size.
5. Synchronized splash artwork badge from stale `V0.3` to `LOKALISASI INDONESIA // V2.43`, matching the in-game title-art badge. V2.43 remains displayed because it is the actual available localization-overlay base; v2.57 is this candidate checkpoint label, not the game's localization version.

## Package checks

- `resources.arsc` is uncompressed and aligned to a 4-byte boundary.
- All stored ZIP entries satisfy the builder's alignment checks.
- Seven uncompressed native `.so` libraries per ABI are aligned to 4-KiB page boundaries.
- Manifest parsing confirms both primary game activities have final `screenOrientation=0`.
- All 26 native UI string-slot checks pass (13 per ABI).
- PairIP implementation libraries remain byte-identical to the base APK:
  - ARM64 `libpairipcore.so`: `cc7b6aade6048f1b1565d37d938f728ce307487a3ebb7df8d24eb735b1f3b1d9`
  - ARMv7 `libpairipcore.so`: `786da8e08b08590d891fe4bdf2ae9210b20042b9c272a215f606bb07f26f543c`
- Local build-tool tests: 8/8 pass.

## Branding audit

- Title and splash artwork use the VORENYX identity and a consistent localized badge; no literal `APKVISION` string was found in those two image payloads.
- The original launcher `banner.png` (Death Road to Canada artwork) remains unchanged.
- Binary text scanning still finds `apkvision` identifiers in `classes3.dex` (13 occurrences) and both `libstub.so` payloads (16 occurrences each). These are class/package identifiers in the repackager wrapper, not text drawn in the title/splash images. They are deliberately retained; no speculative removal or license/security wrapper bypass was attempted. Runtime visibility is unknown without a device test.

## Inputs / lineage

- Base APK: `DR2C-v1.8.2-full-apkvision.apk`, SHA-256 `d4b509d899df572d80de553c8545c850ff2122c2d99fae5cfad2532159d35c15`.
- Base source ZIP: `DR2C-RAYY(2).zip`, SHA-256 `14f44400c3314a6d9b7e5428077c199c846367235e379199618f7b11288f4eb1`.
- Source patch: `DR2C_VORENYX_REPRODUCIBLE_SOURCE_PATCH_v2.55.zip`, SHA-256 `95bfb426c802c0dacebb9d44586cf6deeef1aab5557e2c63ca5dff6f05edf64d`.
- Exact v2.46 baseline APK and actual v2.47–v2.51 source patch ZIPs remain unavailable; this candidate is not v2.51 integration and not byte-equivalent to the reported v2.46 APK.
- No Android device/ADB/emulator or official `apksigner` was available. There is no APK v2 signature verification, device installation, Start-button tap, UI-hitbox, gameplay, event-loading, save/load, or stability test.
- A local test key was used, not the publisher/current-installed signer. Android may reject in-place update, and the preserved PairIP licensing wrapper may reject a locally signed package. Back up save data before changing or uninstalling the currently installed app.

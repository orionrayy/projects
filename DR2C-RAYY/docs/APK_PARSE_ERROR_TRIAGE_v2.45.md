# DR2C VORENYX v2.45 — APK Package-Parse Error Triage

**Date:** 2026-10-25  
**Status:** The prior two candidates had a confirmed Android 11 package-layout defect. A corrected candidate was built and passed local structural checks; installation on the user's phone has not yet been verified.

## User-observed symptom

Android Package Installer displays “Ada masalah saat mengurai paket”. This means the package is rejected at parse/install validation; it is not enough to attribute it to an existing-package signing conflict.

## Confirmed defect in both previous candidates

The manifest specifies `targetSdkVersion=35`. In both `DR2C_VORENYX_v2.45_TEST.apk` and `DR2C_VORENYX_v2.45_PAGEALIGNED_TEST.apk`, `resources.arsc` was stored uncompressed, but its actual payload offset had `offset % 4 = 1`.

Android's official Android 11 documentation states that apps targeting API 30 or higher cannot be installed if `resources.arsc` is compressed or not aligned to a 4-byte boundary: https://developer.android.com/about/versions/11/behavior-changes-11#app-signing

This is a concrete invalid package layout and plausibly explains the repeat parse failure. It is a stronger explanation than the earlier native-library alignment hypothesis.

## Correction in the new candidate

Artifact: `DR2C_VORENYX_v2.45_PARSEFIX_TEST.apk`

- Size: 112,238,771 bytes.
- SHA-256: `e727b5eb9f8314e312e1808acce5c11923265716a1ea2fb84638cca2d53530e6`.
- ZIP CRC: PASS; 1,005 entries; zero duplicate paths.
- `resources.arsc`: stored uncompressed, payload offset 73,704,384; `offset % 4 = 0`.
- All 260 stored entries are 4-byte aligned; zero alignment failures.
- Seven uncompressed native `.so` payloads are page-aligned to 4,096 bytes, consistent with `android:extractNativeLibs=false`.
- JAR/v1 signature and a local APK v2 signature/content-digest verifier pass.
- Manifest structure passes the local chunk-level check; target SDK 35, min SDK 23; splash and game activities use landscape orientation.

## Remaining limits

- No Android device or PackageInstaller logs are available in this build environment; the new candidate's install has not been re-run.
- The APK has a local test certificate, not the publisher's certificate. A separate signature-mismatch error may occur if updating over a differently signed installation.
- The v2 signature was checked with a local implementation, not the official `apksigner` binary. If the correctly named new candidate still fails parsing, capture the exact `INSTALL_PARSE_FAILED_*` / `INSTALL_FAILED_*` code from Package Installer/ADB instead of building another guessed APK.
- Original PairIP/Play licensing checks remain intact.
- Do not uninstall the current game before backing up its save data.

## Evidence

- APK build report: [DR2C_VORENYX_v2.45_PARSEFIX_BUILD_REPORT.md](sandbox:/mnt/data/DR2C_VORENYX_v2.45_PARSEFIX_BUILD_REPORT.md)
- Machine-readable validation: [DR2C_VORENYX_v2.45_PARSEFIX_VALIDATION.json](sandbox:/mnt/data/DR2C_VORENYX_v2.45_PARSEFIX_VALIDATION.json)

# DR2C VORENYX — Android 11 install failure and signature-fix derivative

**Date:** 25 October 2026  
**Scope:** diagnose reported failure to install the v2.57 test APK after the previously installed game was removed.

## Root cause identified

The v2.57 candidate's binary manifest declares `targetSdkVersion=35`, but the package only carried a JAR/v1 signature. Android 11/API 30 requires apps targeting API 30 or higher to include APK Signature Scheme v2 or higher. Therefore, v1-only signing is sufficient to explain an installer rejection even after the old package has been uninstalled. The issue is not established as a damaged ZIP: the candidate passed ZIP CRC and JAR/v1 checks.

Official reference: https://developer.android.com/about/versions/11/behavior-changes-11

## Corrective test artifact

Created `DR2C_VORENYX_v2.57_SIGNATURE_FIX.apk`, a signature-fix derivative of the v2.57 localization payload. It is **not** the separately documented v2.58 localization batch.

- SHA-256: `a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7`
- Size: 115,615,585 bytes
- Package: `com.noodlecake.drtc`; versionCode 57; versionName 1.8.2
- `minSdkVersion=23`; `targetSdkVersion=35`
- Includes JAR/v1 plus an APK Signature Scheme v2 signing block, signed with a new local test certificate.

## Checks and remaining limits

- JAR/v1 verification with `jarsigner`: PASS.
- Local v2 verifier: PASS for signing-block layout, RSA/SHA-256 signature, certificate/public-key match, and chunked content digest.
- ZIP CRC: PASS; 1,015 entries; duplicate paths 0; stored-entry alignment failures 0.
- All three DEX internal file size, SHA-1 and Adler-32 checks: PASS.
- Binary manifest parses; both main game activities are landscape.
- Official Google `apksigner` verification: not run because it was unavailable in the build environment.
- Android installation and gameplay/runtime: not yet device-tested.

This is a test artifact, not a release APK. It is signed with a locally generated certificate, not the publisher's key. PairIP/licensing libraries remain byte-identical and were not bypassed; they may still reject the package at startup. Successful installation alone would not establish game stability. The signature-fix derivative does not resolve the incomplete source lineage for v2.47–v2.51.

# DR2C VORENYX v2.45 — APK Package-Parse Error Triage

**Date:** 2026-10-25  
**Status:** A concrete native-library alignment defect was repaired in a new local candidate. The user's Android install attempt has not been re-run; causality is not yet confirmed.

## User-observed symptom

Android Package Installer displays “Ada masalah saat mengurai paket” for `DR2C_VORENYX_v2.45_TEST.apk`. Treat this as a real package rejection, not a mere existing-package signature conflict.

## Verified defect

The previous candidate's manifest specifies `android:extractNativeLibs="false"`. All seven native `.so` payloads were stored uncompressed but had only 4-byte alignment; their actual payload offsets were not divisible by 4,096. The original supplied base package had those seven payloads page-aligned.

Android's native-loader documentation says a shared library loaded directly from an APK with `extractNativeLibs=false` must be stored uncompressed and page-aligned:
https://android.git.googlesource.com/platform/bionic/+/HEAD/android-changes-for-ndk-developers.md

## Correction made

A new file was generated: `DR2C_VORENYX_v2.45_PAGEALIGNED_TEST.apk`.

- Every native library is stored uncompressed at a 4,096-byte-aligned payload offset.
- ZIP CRC scan: PASS; 1,005 entries; no duplicate paths.
- JAR/v1 signature verified with JDK `jarsigner -verify`.
- APK Signature Scheme v2 block, RSA signature, and whole-file content digest independently verified by the local verifier.
- Binary AndroidManifest.xml chunk structure checked; minimum SDK 23, target SDK 35; both splash and game activity have landscape orientation.
- Size: 112,237,647 bytes.
- SHA-256: `adbe5fff97ba43c670c640e648b4ccc9a9f55996840559665a791d16d06267e7`.

## What remains unverified

No Android device or Package Installer log is available in this build environment, so it is not proven that this alignment defect was the only cause of the generic parse error. If the new candidate still reports a parsing error, obtain the exact `INSTALL_PARSE_FAILED_*` / `INSTALL_FAILED_*` code from Package Installer/ADB before guessing again.

The candidate uses a local test certificate, not the publisher's certificate. An in-place update over a differently signed installed app may be rejected separately. Do not uninstall the current game without backing up saves. Publisher license checks were not removed or bypassed.

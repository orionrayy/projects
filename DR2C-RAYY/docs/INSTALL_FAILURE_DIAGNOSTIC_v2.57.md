# DR2C VORENYX v2.57 — Android Install Failure Diagnostic

**Date:** 2026-10-25 (WIB)  
**Status:** Candidate package passes local archive and v1 signature checks; install root cause is not device-confirmed. Most likely blocker is signer mismatch when installing over an existing package.

## Verified locally

- Candidate: `DR2C_VORENYX_v2.57_TEST_CANDIDATE.apk`
- SHA-256: `ef66364da7e3d8862b460348d67d397e8132896aaa80f70a9243589d934435e5`
- APK ZIP entries: 1,015; `ZipFile.testzip()`: PASS; duplicate paths: 0.
- Binary manifest parses. Package: `com.noodlecake.drtc`; versionCode: `57`; versionName: `1.8.2`; minSdk: `23`; targetSdk: `35`.
- Both app activities are declared with `screenOrientation=landscape`.
- JAR/v1 APK signature verifies with `jarsigner` / `keytool -printcert -jarfile`.
- Candidate signer SHA-256: `86:63:B5:EE:BD:E7:60:28:E3:26:D8:0A:65:0A:C3:A1:0A:99:D5:24:70:B5:4C:B5:A7:7C:F1:CB:A5:A7:A1:80` (self-signed local test certificate).
- Supplied source/base APK signer SHA-256: `A5:4B:28:D5:67:59:41:C1:D3:9D:69:37:B4:F8:E4:C6:99:66:DE:DE:41:7A:CA:27:85:BD:8D:C8:40:C8:D1:D8`.
- The signer fingerprints differ. They cannot be used as an in-place update pair under the same package name.
- APK Signature Scheme v2 signing block is not present/verified in this candidate. Android 11 supports v1 signatures, so this observation alone is not enough to explain installation failure.

## Interpretation

If an app with package `com.noodlecake.drtc` is already installed and was signed by the supplied base/original publisher package or another test key, Android will typically reject v2.57 as an update with a signature mismatch (`INSTALL_FAILED_UPDATE_INCOMPATIBLE`). The generic UI text “App not installed” is consistent with that, but the installed package's signature was not read from the user's device, so this remains a high-probability diagnosis rather than a device-confirmed error code.

If the user had fully removed every existing install of this package before trying v2.57, signer mismatch with the old installation would not explain the failure. Other causes (installer error, storage, policy, or package validation) would need the actual PackageInstaller/ADB error code.

## Safe next step

Do not uninstall the existing game just to test this candidate until save data is backed up. A signature-compatible update requires the same signing key as the currently installed app. The publisher's private signing key cannot be reconstructed from its public certificate. Re-signing with another newly generated key will not make it compatible. No package-identity rename, PairIP change, license-check bypass, or speculative security-wrapper modification was performed.

For device-level confirmation, capture the exact installer error code (for example, via `adb install -r ...` on a trusted computer). Without device access or that error code, an exact cause cannot be claimed.

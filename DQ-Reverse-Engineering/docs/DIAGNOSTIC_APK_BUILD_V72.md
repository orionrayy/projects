# DQ v72 Logcat-observable diagnostic APK

**Static package validation passed. Device runtime remains unverified.**

- APK: DQ_ModKit_v72_ABI_Probe_LOGCAT_ARM64.apk
- SHA-256: 6261d077092098986094ebcf79522b767143467b7b3bc074341b2da6700098b6
- Size: 57,717,702 bytes
- Package: com.shinybox.dqv72 — a separate diagnostic install
- Launcher label: DQ v72 Tester
- ABI: arm64-v8a, one standalone APK
- Test certificate SHA-256: b8f8b624ce1368dca48e3413b4433e81d117fb3cbab904e11ec308ecc79ad60c

## v72 change

v70 had no observable Logcat trail, so a silent load/register/round-trip failure could not be distinguished. v72 adds the DQv72Probe tag and pass/fail/exception markers for library loading, callback registration, the numeric 21 → 42 round-trip, and unregister. The callback is intended to be side-effect-free; it does not access or mutate game state and does not touch purchases, licenses, account/cloud state, or integrity behavior.

## Static validation

| Gate | Result |
|---|---|
| Candidate, DEX and bridge SHA-256 pins | PASS |
| APK/ZIP CRC | PASS |
| 16 KiB native-library alignment before and after signing | PASS |
| APK signing V1/V2/V3 | PASS |
| aapt dump badging, package ID and launcher activity | PASS |
| Original official package ID remains com.shinybox.smash | PASS |
| Device install/start and Logcat capture | NOT TESTED |
| Native 21 → 42 callback observed in game | NOT TESTED |
| Gold +100K runtime checks | 0/9 |
| Catalogue routes/effects runtime-verified | 0/222 |

The APK uses a local test certificate, not the publisher's certificate. It does not update the official application. Keep the official game installed, use a disposable profile, and do not test against a production save. This build is diagnostic only, not a stable release.

## Markers

library_load=PASS/FAIL, callback_register=PASS/FAIL, callback_roundtrip=PASS/FAIL, and callback_unregister=PASS/FAIL/EXCEPTION/SKIP. A callback_probe=EXCEPTION marker indicates an exception in the probe path.

callback_roundtrip=PASS is emitted only when the native dispatcher returns exactly one numeric output equal to 42 for input 21. The marker has not yet been observed on a physical device. Follow the runtime smoke-test protocol in DIAGNOSTIC_APK_RUNTIME_SMOKE_TEST_V72.md.

The JSON report pins the local artifact hash. The reproducible builder is source-only and expects a locally held candidate APK, exact DEX, native bridge, Android Build Tools, and a private local test keystore; none of those private signing credentials are committed.

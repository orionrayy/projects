# Build and Validation — DR2C VORENYX v2.43 APK Candidate

## Release artifact
- Local APK: `DR2C_VORENYX_v2.43.apk`
- Size: 39748335 bytes
- SHA-256: `3019dd04098e9e8fef01045a2e391d9525bf87ef6874b0d0049c5a073a052f25`
- Package: `com.noodlecake.drtc`, game version `1.8.2` (version code 57)
- Minimum / target SDK: 23 / 35
- Signature schemes: v1, v2 and v3 verified by Android SDK Build Tools 35.0.1 `apksigner` 0.9.
- APK ZIP entries: 1,015; ZIP CRC PASS; no duplicate paths.
- 272 overlay payloads match the archived patch byte-for-byte.
- 3 DEX files and 16 stored native libraries are present for `arm64-v8a` and `armeabi-v7a`; all native libraries are 4-byte aligned.

## Important signing limitation
The package is signed with a new local certificate (SHA-256 fingerprint `6ea04e10965de1459a7fee845e8ae903bc1535a744f4762c14b2c7bb82eb13f9`), not the original publisher's certificate. The supplied archive does not contain the original private signing key. The package includes `com.pairip.application.Application` plus PairIP/Play license-check components, so the app may reject the local signature or fail at launch. No licensing or anti-tamper bypass was attempted.

## Runtime tests
Android install, launch, actual gameplay/event paths, UI fit/overflow, save/load, and stability are **NOT RUN** because no connected Android device/emulator/ADB is available. The APK has passed static packaging and v1/v2/v3 signature validation only; it is not represented as a verified stable release. Do not uninstall the official game or risk saved progress based on this static check.

## Patch metadata
The v2.43 patch README says 309 changed occurrences across 16 files while checkpoint/ledger say 159 across 58 files. This discrepancy is still open and documented in [the APK build report](APK_BUILD_v2.43.md).

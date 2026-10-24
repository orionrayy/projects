# Build and Validation — DR2C VORENYX v2.43 APK Candidate

## Localization patch inputs
- Patch: `DR2C_VORENYX_ID_v2.43_localization_patch.zip`
- Bytes: 24,350,974
- SHA-256: `00ff7866242e8b3aca4fc749e93455ba1c795c4eec99fd15baa07ab483aca024`
- Patch ZIP entries: 444; manifest records: 443; CRC PASS; no duplicates or manifest hash failures.
- Targeted localization summary from the v2.43 checkpoint/ledger: 159 string occurrences across 58 files, including 9 new overlay modules. The package README conflicts, claiming 309 across 16; this conflict is preserved as an open metadata defect.

## APK candidate assembled locally
- File: `DR2C_VORENYX_v2.43.apk` (not hosted on GitHub)
- Size: 39,610,091 bytes
- SHA-256: `cefe665d0164495248f0d2cc960f54478d60b980ec137c3878181732d0885a90`
- Base package: `com.noodlecake.drtc`, game version `1.8.2`, version code `57`, min SDK 23, target SDK 35.
- Applied 272 overlay file payloads: 271 existing APK paths replaced and one new title-screen image added.
- Signature: local JAR/v1 with SHA-256/RSA, not original publisher signature.
- ZIP CRC and JAR/v1 signature verification: PASS.
- Overlay payload hash comparison: 272/272 PASS.
- Native ABIs: arm64-v8a and armeabi-v7a; 3 DEX files preserved; stored native libraries 4-byte aligned.
- SHA-256 sidecar: `DR2C_VORENYX_v2.43.apk.sha256`.

## Runtime and signing limits
The supplied archive does not include the original publisher's private signing key. The APK manifest uses `com.pairip.application.Application` and contains PairIP/Play license-check components; re-signing can cause install or launch rejection. No license/anti-tamper bypass was attempted.

Android install, launch, gameplay/event-path checks, UI fit/overflow, save/load, and stability tests are **NOT RUN**. The APK has passed static packaging checks only; do not label it runtime-stable.

The v2.43 patch README has a conflicting change-count summary (309/16 versus 159/58 in the checkpoint and translation ledger); see [the APK build report](APK_BUILD_v2.43.md).

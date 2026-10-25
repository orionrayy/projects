# Dungeon Quest ModKit checkpoint — v72

Date: 25 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
Previous checkpoint: v71 diagnostic APK

## Completed in v72

- Created a separate ARM64 diagnostic APK with Logcat-observable probe states.
- Added explicit probe markers for library load, registration, 21 → 42 round-trip, unregister, exception, and skip paths.
- Kept the new package ID com.shinybox.dqv72 separate from the official com.shinybox.smash.
- Reassembled the DEX, re-disassembled for comparison, and confirmed 10,769 classes in both variants, no missing/added classes, and only com/shinybox/smash/DqNativeProbe.smali differs from the previous v70 probe DEX. S3DRenderer.smali remains byte-for-byte identical in the disassembly comparison.
- Revalidated ZIP CRC, 16 KiB native-library alignment, APK Signature V1/V2/V3, aapt dump badging, package name and launch activity.
- Added v72 source patcher, builder, fail-closed report validator, regression tests and GitHub Actions workflow.

## Artifact identity

- APK: DQ_ModKit_v72_ABI_Probe_LOGCAT_ARM64.apk
- SHA-256: 6261d077092098986094ebcf79522b767143467b7b3bc074341b2da6700098b6
- Size: 57,717,702 bytes
- Package: com.shinybox.dqv72
- Label: DQ v72 Tester
- ABI: ARM64 / arm64-v8a
- Test signing certificate SHA-256: b8f8b624ce1368dca48e3413b4433e81d117fb3cbab904e11ec308ecc79ad60c

## Current gates

Static package validation: PASS.
Physical-device install, launch, and Logcat: NOT TESTED.
Native 21 → 42 round-trip observed in-game: NOT VERIFIED.
Shutdown unregister: NOT VERIFIED.
Gold +100K runtime checks: 0/9.
Catalogue runtime effects: 0/222.
Stable promotion: BLOCKED.

The native bridge returns success for nativeInvokeProbe only if the dispatcher returns exactly one numeric output equal to 42 for input 21. However, v72's marker has not yet been observed on a device. Static assembly and symbol checks cannot establish runtime ABI, engine-thread or object-lifetime safety. This remains diagnostic-only, not a stable release. Do not remove the official app, test production saves, or bypass purchase/licensing/integrity/cloud/account behavior.

Evidence:
- DIAGNOSTIC_APK_BUILD_V72.md
- DIAGNOSTIC_APK_BUILD_V72.json
- DIAGNOSTIC_APK_RUNTIME_SMOKE_TEST_V72.md
- DEX_LIFECYCLE_TARGET_BUILD_V70.md
- NATIVE_CLIENT_ABI_BINARY_CROSSCHECK_V69.md

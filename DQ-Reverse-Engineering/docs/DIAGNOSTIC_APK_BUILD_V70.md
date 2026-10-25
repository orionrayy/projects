# v70 diagnostic APK — static validation report

**Package created and statically validated; in-game runtime remains unverified.**

Artifact: `DQ_ModKit_v70_ABI_Probe_DIAGNOSTIC_ARM64.apk`
SHA-256: `07898a4997b1f470728087d6c4bcd22660980be6d0670217d6d64c2b1769d0e8`
Size: 57,717,702 bytes
Package ID: `com.shinybox.dqv70`
Launcher label: **DQ v70 Tester**
ABI: ARM64 (`arm64-v8a`)

The APK was built from the locally held v50 Gold +100K candidate, the v70 DEX overlay output, and the source-only native probe bridge. It uses a unique package ID so it is not an update to the official `com.shinybox.smash` install. The original candidate, original XAPK and original DEX were not overwritten. The Android binary manifest/resource package name was changed to the new app ID; the unresolved icon references in the supplied standalone base were removed and the same-length label string was changed to distinguish the diagnostic app in the launcher.

## Static package gates

| Gate | Result |
|---|---|
| Input candidate hash pinned | PASS |
| Patched DEX SHA-256 pinned | PASS |
| Native bridge SHA-256 pinned | PASS |
| APK and ZIP entry CRC checks | PASS |
| 16 KiB native-library alignment | PASS before and after signing |
| Android apksigner v1 / v2 / v3 | PASS |
| aapt binary manifest/badging parse | PASS |
| Separate package ID | PASS |
| Source official app ID changed | No |
| Physical-device installation/startup | Not tested |
| Native 21 → 42 callback in the game | Not tested |
| Gold +100K runtime checks | 0/9 |
| 222-entry catalogue effects connected | 0/222 |

The package is signed with a **local diagnostic test certificate**, not the publisher’s certificate. It is not a replacement or in-place update for the official app, and it must not be described as a stable release. The private signing key is not included in the APK bundle or repository.

## Test boundary

The probe is deliberately side-effect-free: it attempts to register a named callback and round-trip numeric 21 to 42 after engine initialization reports success, then unregisters before shutdown/restart. That behavior has not yet been observed inside the running game; static disassembly and symbol presence do not prove callback ABI, object lifetime or engine-thread correctness. A native callback mismatch could still cause a crash.

The v50 Gold +100K button remains a static HUD candidate, not a verified game feature. Do not use a production save or remove the official app to test this. Keep any first launch offline and use a disposable profile with a verified recovery path. Purchase receipts, licensing, integrity checks and cloud/account behavior were not bypassed.

Machine-readable report: `DIAGNOSTIC_APK_BUILD_V70.json`.

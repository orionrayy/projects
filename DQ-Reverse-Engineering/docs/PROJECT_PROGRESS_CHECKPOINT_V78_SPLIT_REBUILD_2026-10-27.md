# Dungeon Quest ModKit — v78 complete split-package rebuild

Date: 27 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
PR: #26 (draft, open, unmerged)

## User-reported failure and changed approach

The user reports that v75, v76 and v77 still force-close. Reissuing identical v77 bytes did not constitute a new build. The v78 approach therefore switches to a complete XAPK with the full base + density + language + ARM64 split set rather than another standalone APK.

## v78 artifact

- File: DQ_ModKit_v78_SPLIT_PACKAGE_ARM64.xapk
- SHA-256: d328410182225ef09610b3670aadc6d4e56e4c8f815288116dd7bd2b5b21abc0
- Outer XAPK size: 43,761,625 bytes
- Total size of the 20 inner split APKs: 57,386,122 bytes
- Android package ID: com.shinybox.dqv78
- App label: DQ v78 Tester
- Version: 3.3.2.0, ARM64 split set (20 APKs)
- Local test signing certificate SHA-256: aee4ae54f7b8f5bfeeae8aef24da3a2cd365a5f9d36f7ec616d7a86ef6d50957 (not publisher signing)

## Changes relative to the v50 split source

- Reused the full 20-APK split inventory from the pinned v50 candidate XAPK.
- Replaced the embedded STK with the corrected v75 STK, SHA-256 24a89cf3f356a2b48474d9681dedd662cec8cd5ec9f01574b26bed02d0ee6182.
- Changed Android package ID and resource package ID consistently across all split APKs to com.shinybox.dqv78.
- Renamed both provider authorities to the new tester namespace.
- Replaced the single dotted application-ID literal in classes.dex and recalculated DEX SHA-1 and Adler-32.
- Replaced the single dotted application-data identity in ARM64 libS3DClient.so while preserving the Java class namespace and underscored JNI exports.
- Renamed launcher label to DQ v78 Tester.
- Re-signed every split with the same local test certificate. All 20 split APKs use the same signer identity.

## Static verification

Independent post-build audit passed:
- XAPK outer ZIP CRC and exact 20-split inventory.
- Every inner APK ZIP CRC.
- All split manifests expose package ID com.shinybox.dqv78.
- Every split has matching signer certificate; APK signature schemes V1, V2 and V3 verify.
- 16 KiB zipalign checks pass on all 20 splits, including native-library split.
- aapt parses the package ID on each split; base resolves DQ v78 Tester.
- DEX SHA-1 / Adler-32 check passes.
- Exact corrected STK SHA-256 is present in base APK.
- Provider authorities are unique to v78.
- Old dotted package identity is absent from the DEX and native client library; JNI class exports remain in the original Java class namespace.

## Runtime status

Static validation only. No physical-device installation or launch was performed here; force-close is not marked fixed. Gold +100K action, save/reload safety and the native cheat catalog remain unverified (0/222 runtime-connected cheats). Do not promote this candidate until the phone reaches a stable screen and behavior is tested.

## Phone-only next step

Install the XAPK through the same XAPK installer used for previous split packages. Do not install as a single APK. It is a separate test package, so leave the official com.shinybox.smash app and its saves untouched. First launch offline without tapping cheat controls. Record whether it reaches the title/menu or force-closes.

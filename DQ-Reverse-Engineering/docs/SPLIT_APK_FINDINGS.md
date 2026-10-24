# Split APK Findings — v18 correction

**Status:** matching XAPK split set recovered from the conversation Library and statically audited on 2026-10-24. This supersedes the historical v10/v11 statement that companion split APKs had not been inspected.

## Direct evidence

XAPK input: Dungeon+Quest_3.3.2.0_APKPure.xapk  
SHA-256: 3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b

Its manifest records package com.shinybox.smash, version 3.3.2.0, version code 1423433200, min SDK 21 and target SDK 34. The archive contains 20 APK splits: base, ARM64 ABI, xxhdpi density, and language configurations.

The ARM64 split SHA-256 is 5cb55f369b1ab9af3752595c87fcbc8fafa9ec31cd8870a45645309f8c2a40c2. It contains:

- lib/arm64-v8a/libS3DClient.so — 17,029,072 bytes
- lib/arm64-v8a/libcrypto.so — 1,818,504 bytes
- lib/arm64-v8a/libopenal.so — 309,704 bytes
- lib/arm64-v8a/libssl.so — 390,248 bytes

The base APK and sampled ARM64, density, and English language split certificates have the same signer SHA-256 fingerprint:

9A:28:A9:91:71:C8:F6:3F:34:11:E2:91:F6:D9:6F:13:D5:D9:C1:73:62:06:A0:CF:95:EB:EE:99:BC:31:42:1D

The standalone base APK and the base embedded in the XAPK have identical uncompressed hashes for AndroidManifest.xml, classes.dex and assets/S3DMain.smf, while the full APK container hashes differ. The XAPK, split, and library hashes are recorded in NATIVE_SPLIT_AUDIT_V18.md.

## Technical conclusions

The absence of lib/<abi>/*.so in a base-only archive was due to split packaging; it does not indicate that the game never shipped native libraries. The matching binary exists, but the native implementation is closed-source and is not a replacement for source/header files or an integration contract.

The ELF export table contains 64 Java_* exports and C exports including S3DClient_CallHUDAction and S3DClient_SetGameOption. Existence and partial static disassembly are not sufficient to call these exports safely from an injected Java adapter.

The remaining integration blockers are the serialized HUD/AIM authoring path, validated event binding to the existing debug model, safe runtime-state accessors, and a compatible ARM64 device/runtime for click-path and gameplay verification. The base app, matching native split, or successful harness build does not itself prove that a modified original APK has been built or installed.

## Validation policy

1. Keep exact input and output hashes and never mix files from other versions/signing lineages.
2. Require lossless HUD parser/serializer round-trip tests before making a binary UI edit.
3. Require explicit calling signatures, thread constraints and safe runtime state checks before invoking native APIs.
4. Keep the cheats sandbox offline and save-isolated; fail closed when any state is unknown.
5. Do not alter billing callbacks, receipts, purchase entitlements, cloud progression, achievements or leaderboard submissions.

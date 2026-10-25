# Native Split Audit v18 — Dungeon Quest 3.3.2.0

**Evidence date:** 2026-10-24  
**Status:** ABI split recovered and identity-checked; runtime integration remains blocked.  
**Purpose:** correct the older v10/v11 note that the matching native split was missing. No binary payloads or secrets are committed to this repository.

## Input identity

| Input | SHA-256 | Notes |
|---|---|---|
| Dungeon+Quest_3.3.2.0_APKPure.xapk | 3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b | XAPK manifest lists package com.shinybox.smash, version 3.3.2.0, version code 1423433200 |
| Standalone base APK | 1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9 | Existing library copy; 280 ZIP entries |
| Base APK inside XAPK | c7bd6ab38ed2827a3aadd4f415ffc994eb366fc1ce9d66742077d6ef5e954abc | Same manifest, DEX and source asset-pack payload hashes as the standalone copy; container bytes differ |
| XAPK ARM64 split | 5cb55f369b1ab9af3752595c87fcbc8fafa9ec31cd8870a45645309f8c2a40c2 | Contains four lib/arm64-v8a/*.so files |
| XAPK density split | 0a49043f26b35966865cc646d72f894f063ea672cdcdbb952662536aa911ac62 | config.xxhdpi.apk |

The base APK and sampled ABI, density and language split certificates all report signer SHA-256 fingerprint:

9A:28:A9:91:71:C8:F6:3F:34:11:E2:91:F6:D9:6F:13:D5:D9:C1:73:62:06:A0:CF:95:EB:EE:99:BC:31:42:1D

The original asset pack payload in both base APK candidates has SHA-256 340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3. The patch candidate S3DMain_fair_economy_v8.smf is a separate modified asset-pack artifact and must not be treated as the pristine baseline.

## ARM64 native inventory

| Library | Size (bytes) | SHA-256 |
|---|---:|---|
| libS3DClient.so | 17,029,072 | 0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083 |
| libcrypto.so | 1,818,504 | 0b045b13171a9708a422a911a2770133fa484c603a7d3525ab963cf8ea4887bf |
| libssl.so | 390,248 | d19a05e843704cd102c0b94cef356a1f599c7b8c086348afd387c2711217aec6 |
| libopenal.so | 309,704 | 7920d48e7b373d3fce8cc11309e5a243097b42ff5e9e24189c77974ae3402b34 |

libS3DClient.so is ELF64/AArch64. Its dynamic dependency list includes those three bundled libraries plus Android system libraries libGLESv2.so, libEGL.so, libdl.so, liblog.so, libc.so, and libm.so. The packaged split is ABI-specific; it is not a source project or a general-purpose desktop binary.

## Export observations

- The native library exposes 64 JNI-style Java_* symbols; the recovered DEX has 44 declarations marked native. The counts differ because the binary exposes additional callbacks/wrappers.
- Relevant C exports include S3DClient_CallHUDAction, S3DClient_SetGameOption, S3DClient_RegisterFunction, S3DClient_RegisterEventCallback, S3DClient_SendEventToCurrentUser, and the S3DClient_PushEventArgument* family.
- Disassembly shows S3DClient_CallHUDAction delegates into the internal GameManager action path when the engine is initialized. The export exists, but the repository still has no validated Java binding/argument contract, UI-thread/render-thread policy, or evidence-backed action invocation from an Android callback.
- S3DClient_SetGameOption delegates to the engine OptionsManager. It is not evidence of a player-stat mutation API, and option identifiers/semantics must not be guessed.
- The asset pack contains the existing binary Resources/HUD/pause.hud, Resources/HUD/debug.hud, Resources/AIModels/uai_gp_options.aim, Resources/AIModels/uai_gp_hud.aim, and Resources/AIModels/uai_gp_debug.aim. Static identifiers establish presence, not that a newly added menu row or action works.

## Integration status

| Requirement | Evidence-based status |
|---|---|
| Matching package/version split set | **RECOVERED** |
| ARM64 native library binaries | **RECOVERED + HASHED** |
| Cross-split signer identity | **MATCHED for sampled base/ABI/density/language splits** |
| Native game source or headers | **NOT AVAILABLE** |
| Verified read/write adapters for player/game state | **NOT AVAILABLE** |
| Format-correct HUD parser/writer with lossless round-trip tests | **NOT AVAILABLE** |
| Pause → Options → Cheats click path in a running game | **NOT VERIFIED** |
| Cheat gameplay effect on isolated save | **NOT VERIFIED** |
| Modified original-game APK build/install/launch | **NOT PERFORMED** |
| Purchase receipt/entitlement bypass | **OUT OF SCOPE** |

## Next engineering gate

1. Implement a bounded HUD parser and serializer only after a lossless parse → serialize → byte/hash-equivalence test over the unmodified source asset is available.
2. Determine a safe route from an Options UI event to the existing debug model without changing purchase callbacks, receipts, entitlements, online progression, or achievement/leaderboard state.
3. Design the runtime bridge against exact function signatures and engine thread constraints, with no guessed option IDs or pointer assumptions.
4. Require sandbox/offline/save-isolation gates and reversible apply → read-back → reset validation before enabling any gameplay mutation.
5. Validate on a compatible ARM64 Android device or a verified ARM64 runtime. An x86_64 Android emulator can validate the standalone harness but does not prove the ARM64 game engine works.

This report updates the split-acquisition fact only. It does not claim native integration or a modified Dungeon Quest APK.

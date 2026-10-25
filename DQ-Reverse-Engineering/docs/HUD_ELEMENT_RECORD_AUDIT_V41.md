# HUD element record audit v41

Date: 2026-10-25  
Target: Dungeon Quest Android 3.3.2.0, package com.shinybox.smash  
Status: v12 parser and canonical serializer implemented. The synthetic suites pass locally, and the serializer reproduces all 68 extracted source HUDs byte-for-byte. This is not an in-game integration or runtime verification.

## Input and reproducibility

The local source XAPK was identified as SHA-256 3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b. The base asset pack S3DMain.smf has SHA-256 340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3 and size 33,978,539 bytes.

The pack was decoded into a temporary workspace only. No original APK, S3DMain.smf, raw HUD payload, native library, or user credential was added to the repository. The probe supports HUD format version 12, parses the four length-delimited top-level sections, decodes serialized element fields for type IDs 1–15, and fails closed on unknown types, malformed lengths, truncation, or unconsumed element-section bytes. The companion canonical serializer rebuilds v12 element records while preserving the non-element sections byte-for-byte; it writes outputs only to an explicitly selected separate output directory.

## Local validation findings

All 68 HUD resources extracted from the matching source asset pack parsed successfully. Their 4,956 serialized element records consumed the entire element section with no residual bytes.

Aggregate element-type counts:

| Element type | Records |
|---:|---:|
| 1 | 1,246 |
| 2 | 699 |
| 3 | 1 |
| 4 | 2,920 |
| 6 | 4 |
| 8 | 48 |
| 11 | 14 |
| 12 | 4 |
| 15 | 20 |

Only one type-3 List element appears across those 68 source HUD resources: match_result_anim.hud. Its element-section offset is 4, serialized record size is 237 bytes, name is list, and label is rank_up_player_container. This gives a concrete source record to analyze rather than inferring its complete schema from symbol names alone.

Key source samples:
- pause.hud: 29,446 bytes, SHA-256 12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395; 126 elements, including 20 type-1, 59 type-2, 45 type-4, and 2 type-11.
- debug.hud: 12,887 bytes, SHA-256 02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6; 71 elements, including 14 type-1, 10 type-2, 39 type-4, 4 type-6, 1 type-11, and 3 type-15.
- hud.hud: 127,302 bytes, SHA-256 5ead76f34a93be134761b11dda485221628f41c19b3ac99dd81fd1867edf0304; 637 elements.
- match_result_anim.hud: 29,799 bytes, SHA-256 fec7d9b18c906d4d75904205f58b3eb3205540c04aefb9fc651c6d2ac2cf9402; 108 elements, including the sole type-3 List record.

## Native code cross-reference

The ARM64 source split contains HUDTemplate::LoadElements at VA 0x968f20. Its type-3 dispatch target is 0x969644; the v12 branch reads the List-specific byte, floats, resource/string references, seven color values, eight further string/resource references, and trailing floats. Type 15 also has a dedicated v12 branch. This probe represents those observed read sequences and verifies them against all 68 locally extracted v12 HUDs.

The parser is read-only; the companion serializer can rebuild a parsed v12 HUD to a separate file. Neither tool proves that a new List row can be populated dynamically or connected to a cheat action. pause.hud and debug.hud contain no serialized type-3 List element. The existence of native AddItem and scrolling APIs does not prove the AIM population, selected-row callback, runtime ownership, or lifecycle contract.

## Regression tests and CI

Eight synthetic tests now cover all v12 element schemas, parser payload consumption, legacy non-UTF-8 strings, malformed/unsupported input, byte-identical serialization across all element types, preservation of top-level sections, and fail-closed behavior for a nonzero canonicalized field or non-finite numeric value. The fixtures contain no original game assets.

Local result: all 8 synthetic tests passed. The original-source parser passed 68/68 HUD resources (4,956 records, zero parsing failures); a separate canonical serialize-to-new-directory run was byte-identical for 68/68 HUD files, with zero changed bytes. These local results do not replace remote CI verification or on-device gameplay tests.

## Reciprocal SaveElements writer cross-check

A second read-only disassembly pass located the implementation body reached through the short \`HUDTemplate::SaveElements\` entry point: entry thunk at VA 0x963a1c, implementation body at VA 0x9611bc. It uses the same element-type dispatch strategy as the loader and serializes the List-specific v12 fields in the same logical order as represented by this probe.

For List/type 3 the writer reads the object fields for the flag at +0x1f4; floats at +0x1d8/+0x1dc/+0x1e0; three flags at +0x1e4..+0x1e6; floats at +0x1f8/+0x1fc; strings/resources at +0x208/+0x210; float +0x220; two string/resource references +0x228/+0x238; seven colors +0x230/+0x234/+0x240/+0x244/+0x248/+0x24c/+0x250; eight string/resource references +0x258 through +0x290; then floats +0x298/+0x29c. The writer's v12 condition does not append the additional fields that are conditional on a format version greater than 12. This is reciprocal evidence for the type-3 schema used by the parser and synthetic tests.

The byte-identical result is proven for this source build, but two constraints limit generalization to other versions or manually constructed records:

1. The writer emits literal float 0.0 for common field +0x28 rather than serializing the in-memory field. In all 4,956 element records parsed from the 68 source HUD files, the corresponding serialized float was 0.0. That is reassuring for this source build, but not a proof for arbitrary or future HUDs.
2. Resource references are written via engine string/resource lookup and pointer conversion rather than as raw bytes. An offline parser can recover serialized strings, but it does not recreate engine pointer identities or prove that a newly constructed element has valid resource bindings, model ownership, or lifecycle state.

The source List is a contextual rank-up container with its own name, label, colors, and resources; copying its 237 bytes into pause.hud would not by itself create the 222 cheat rows or the required row-selection/action pipeline. No original HUD was modified in place, and no asset pack, APK, or XAPK was rebuilt by this increment.

## Next safe gate

The loader and reciprocal SaveElements writer field order are mapped for this v12 source, and the canonical serializer now reproduces all 68 source HUD files byte-for-byte when writing into a separate temporary directory. The remaining primary blocker is AIM List population and selected-row callback dispatch: recover how an AIM model fills List rows, binds stable IDs, and routes selection to an allow-listed native action. Only after this is evidence-backed should a disposable pause.hud experiment be created and round-tripped through the STK packer. Keep the original package and save untouched; do not build another APK/XAPK until UI serialization, row population, and action dispatch have defensible contracts.
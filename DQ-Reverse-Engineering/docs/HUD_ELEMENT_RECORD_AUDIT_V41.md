# HUD element record audit v41

Date: 2026-10-25  
Target: Dungeon Quest Android 3.3.2.0, package com.shinybox.smash  
Status: Read-only parser implemented; local source validation passed. This is not a HUD writer, in-game integration, or runtime verification.

## Input and reproducibility

The local source XAPK was identified as SHA-256 3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b. The base asset pack S3DMain.smf has SHA-256 340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3 and size 33,978,539 bytes.

The pack was decoded into a temporary workspace only. No original APK, S3DMain.smf, raw HUD payload, native library, or user credential was added to the repository. The probe supports only HUD format version 12, parses the four length-delimited top-level sections, decodes all serialized element fields for type IDs 1–15, and fails closed on unknown types, malformed lengths, truncation, or unconsumed element-section bytes.

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

The probe is intentionally read-only. It does not claim that a parsed List row can be safely created, inserted into pause.hud, populated dynamically, or connected to a cheat action. pause.hud and debug.hud contain no serialized type-3 List element. The existence of native AddItem and scrolling APIs does not prove the full record-construction, AIM population, selected-row callback, or save/reload contract.

## Regression tests and CI

Four synthetic tests cover all v12 element type schemas 1–15, exact element-section consumption, legacy non-UTF-8 string handling, rejection of unsupported types and truncated records, and rejection of wrong versions or trailing bytes. The fixtures are synthetic and include no original game assets.

Local result: 4 tests passed. Full original-source probe result: 68 of 68 HUD resources passed with zero parsing failures. These local binary checks do not replace CI results or on-device gameplay tests.

## Next safe gate

Use the decoded 237-byte List record as a reference for read-only investigation of HUDTemplate save/write serialization and the List constructor/runtime callback path. Before any asset mutation, prove lossless parse/write round-trip on a disposable fixture, then on a no-op copy of pause.hud. Keep the current game package and save untouched; do not build another APK/XAPK until the 222-entry menu has a defensible native record format and verified row-action mapping.
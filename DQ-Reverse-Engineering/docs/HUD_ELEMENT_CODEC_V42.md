# HUD element codec v42 — round-trip validation

Date: 2026-10-25  
Target source build: Dungeon Quest Android 3.3.2.0, package \`com.shinybox.smash\`  
Status: **local source HUD round-trip PASS; synthetic regression suite PASS; game runtime integration still blocked.**

## Source identity and handling

The original XAPK SHA-256 is \`3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b\`. The decoded \`assets/S3DMain.smf\` SHA-256 is \`340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3\`, 33,978,539 bytes. All 5,630 STK entries passed stored-payload CRC, decoded-size and zlib-stream checks during local extraction. Original game binaries, native libraries, keys and decoded asset payloads were not committed to GitHub.

## Codec scope

\`tools/hud_elements_codec_v42.py\` parses the four length-delimited version-12 HUD sections and all element record types observed in the source package. Each primitive retains its original serialized bytes; unchanged strings, scalar encodings, colors, action scripts, general attributes and timers are emitted from the source representation. Explicitly edited fields are range-checked and encoded with their field type. The rebuilt HUD is parsed again before returning.

This gives a field-preserving round-trip and controlled field editing for the covered v12 element schemas. It is not an engine-aware resource constructor. In particular, it does not create or bind engine-side HUD elements, resolve model/resource pointer identity, patch compiled AIM models, or provide a row-selection action map.

## Results measured locally

| Check | Result |
|---|---:|
| HUD assets extracted from matching source pack | 68 |
| HUD assets successfully parsed and reconstructed | 68/68 |
| Exact byte-identical no-op outputs | 68/68 |
| Serialized element records parsed | 4,956 |
| Unconsumed element bytes | 0 |
| Synthetic regression tests | 5/5 passed |

All 68 no-op reconstructions match their source files byte-for-byte. The only type-3 List element found in the source HUD inventory is the 237-byte \`list / rank_up_player_container\` element in \`match_result_anim.hud\`; \`pause.hud\` and \`debug.hud\` have no type-3 List record. This narrows the format ambiguity but does not make it safe to copy that context-specific row into the pause menu.

## Regression coverage

The committed synthetic tests cover v12 element schemas 1–15, exact no-op serialization, a label edit whose encoded length changes, preservation of the other sections and neighboring element bytes, non-UTF-8 legacy string-byte round-trip, invalid scalar bounds, and fail-closed rejection of unknown types, truncation, wrong versions and trailing bytes. Source assets are deliberately excluded from these synthetic CI fixtures.

## What is still not verified

- A new in-game List control with valid hierarchy, layout, resources and touch hit targets.
- The compiled AIM provider that populates a catalog of 222 stable cheat IDs and connects selection/detail/action callbacks.
- A safe authoritative Gold balance mutation, including read-back and rollback.
- Any of the 222 cheat effects on an actual ARM64 game runtime.
- A newly built, installed or launched modified Dungeon Quest APK/XAPK.

No new APK/XAPK was built. The v42 increment extends the parser/serializer and regression base only. CI status must be checked from the current PR checks; local success must not be described as a remote CI pass or device verification.

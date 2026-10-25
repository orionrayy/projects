# DR2C VORENYX — APK Change-Surface Audit v2.62

**Date:** 25 October 2026  
**Result:** static package diff checks PASS; Android runtime remains NOT VERIFIED.

## Artifacts compared

- Base APK: DR2C-v1.8.2-full-apkvision.apk, 109,011,456 bytes, SHA-256 d4b509d899df572d80de553c8545c850ff2122c2d99fae5cfad2532159d35c15.
- Candidate APK: DR2C_VORENYX_v2.57_SIGNATURE_FIX_REDELIVERED_20261025.apk, 115,615,585 bytes, SHA-256 a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7.
- The Library artifact named DR2C_VORENYX_v2.58_ANDROID11_SIGNATURE_FIX.apk is byte-identical to this candidate, with the same SHA-256.
- Both APK ZIP CRC checks pass and duplicate-path count is zero.

## Package comparison

- Base entries: 1,014; candidate entries: 1,015; common entries: 1,012.
- Byte-identical common entries: 737; changed common entries: 275.
- Changed common entries comprise 269 Deathforth .df scripts, AndroidManifest.xml, META-INF/MANIFEST.MF, two libmain.so files, title small art, and splash art.
- Base-only entries: META-INF/CERT.RSA and META-INF/CERT.SF. Candidate-only entries: META-INF/DR2C-VOR.RSA, META-INF/DR2C-VOR.SF, and assets/gfx/ui/vorenyx_title_screen.png. The checker now fails if this expected add/remove surface changes.
- All three DEX payloads are byte-identical between base and candidate. All native shared libraries except the two ABI copies of libmain.so are byte-identical.

## Native UI label patch

Both libmain.so files retain their exact original file sizes. In each ABI copy, the binary diff is 89 changed bytes across 13 NUL-terminated ASCII string slots. Every changed byte is confined to a string slot; no non-string binary diff was detected by the checker.

| Original UI label | Candidate label |
|---|---|
| strength | kekuatan |
| fitness | bugar |
| mechanical | mekanik |
| attitude | sikap |
| morale | moral |
| loyalty | setia |
| Team | Tim |
| composure | tenang |
| medical | medis |
| shooting | menembak |
| Choose UR Fate | Pilih Nasibmu |
| Swap Meet | Barter |
| wits | akal |

This narrows the static change surface: the APK does not contain modified DEX control-flow payloads, and the native-library diffs are confined to the label strings above. It does not prove that the touchscreen event reaches the game handler, that Deathforth starts correctly, or that native integrity/licensing accepts the locally re-signed package.

## Acceptance limits

The Start no-op remains unresolved at runtime. The candidate has a local test signing certificate rather than the publisher's certificate, and the game's PairIP/licensing checks remain unchanged. No bypass or hitbox rewrite was attempted. No Android device, ADB/logcat, emulator, official apksigner, or embedded Deathforth VM was available here.

The source-to-APK audit v2.61 separately verifies that 509/509 .df payloads match the exact locally available source layers after the one-file tutorial source-sync supplement. This does not establish the missing v2.47–v2.51 patch lineage or complete localization.

## Reproduction

    python DR2C-RAYY/tools/audit_apk_change_surface.py --base-apk DR2C-v1.8.2-full-apkvision.apk --candidate-apk DR2C_VORENYX_v2.57_SIGNATURE_FIX_REDELIVERED_20261025.apk --json-out audit/apk_change_surface_v2.62_full.json

The APK binaries and extracted game payloads remain outside public GitHub. Only the checker, tests, report, and sanitized summary are committed.

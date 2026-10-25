# Dungeon Quest 3.3.2.0 — Crash root-cause investigation v25

Date: 2026-10-24. User-tested results: stock-asset Baseline package `com.shinybox.dqfix` opens to gameplay/menu; v21, v22, v23, and v24 modified-asset candidates all force-close at the Shinybox splash.

## Conclusion

The previous evidence does **not** establish anti-tamper as the cause. It does establish a significant flaw in the earlier asset-patch experiment: every previous modified pack was produced by a whole-archive rebuild that relocated the 5,630 payloads and removed deliberate shared-offset payload aliases. The v24 label-only test was therefore not actually isolating just the label at the binary-pack level.

## Binary facts from the original S3DMain.smf

- Original pack SHA-256: `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3`
- Original file size: 33,978,539 bytes; metadata table end: 335,530; 5,630 entries.
- The decoded metadata describes 136 pairs of entry ranges sharing exactly the same offset and byte length. These are deliberate exact-payload aliases/deduplication, not partial overlaps.
- The total of the entry compressed sizes is 32,845 bytes larger than the stored payload region because those assets share byte ranges.
- Previous `StkArchive.rebuild()` serialization instead writes each entry independently in metadata-table order. It removes the shared-offset topology and moves every resource offset. The rebuilt label-only pack became 34,011,387 bytes, a change of +32,848 bytes to the archive despite one small text edit.
- Therefore v21-v24 did not test a faithful in-place resource edit. Their CRC/decoded-size/round-trip checks prove the custom reader can decode the new pack, but do not prove compatibility with the original native loader.

## Native-library signals

- The ARM64 library exports `Pandora::EngineCore::Resource::CheckIntegrity(bool)` at virtual address `0x817020`. Its disassembly is just `mov w0, #1; ret`, i.e. the generic resource integrity function returns success unconditionally in this build.
- General CRC32, MD5, SHA-256 and code-signing APIs are present in the engine. `CodeSigning::ValidateCertificate` and `CodeSigning::ValidateSignature` exist, and certificate-related strings mention a native-plugin manifest. This proves that the engine has generic signature-verification facilities; it does **not** prove an S3DMain asset-pack anti-tamper check runs during startup.
- A direct call to `ValidateCertificate` was found in a native code path, but the inspection did not establish that path as a check of `S3DMain.smf`.
- The successfully launched Baseline uses a different package ID and fresh local signing certificate. This makes strict APK-signer pinning an unlikely explanation for the specific splash crash, though it does not rule out content-pack integrity checks or other checks.

## Diagnostic v25 — original pack topology preserved

Artifact: `Dungeon_Quest_3.3.2.0_Diagnostic_InPlaceLabel_v25.xapk`

- Package ID: `com.shinybox.dqv25`
- XAPK SHA-256: `773a704146b5d03320de8aeb5efad8140f431a18390cd6c1edfd4b84007a2eb2`
- Size: 57,591,155 bytes; 20 split APKs.
- Patched pack SHA-256: `57c91462c9cf48efea12b24d82c20eec86b5c12f2e21ac5b5389f00ec99279eb`
- The visible label alone changes from `Social/IAP` to `Cheat Menu`, both 10 UTF-8 bytes. The action section, callback identifiers, and parameters remain stock.
- The source compressed payload is 5,003 bytes; the replacement is also 5,003 bytes. Its CRC field is updated in place.
- The patched pack retains exactly the original size, metadata table end, entry offsets, compressed/uncompressed sizes, flags, and all other entry CRC values. All 136 exact-offset alias groups are preserved. All 5,630 entries decode, with exactly one decoded entry differing: `Resources/HUD/pause.hud`.
- All 20 APK split v2 signatures, common signer, inner/outer ZIP CRC checks and embedded-pack match passed under the local validator. This is not an official Android `apksigner` result, and the package has not been installed/launched by the build environment.

## Interpreting the next device result

1. **If v25 reaches the title screen:** prior crashes strongly implicate whole-pack reserialization/reordering. Do not reintroduce callback changes yet. Next add one callback change through the same offset-preserving patch path.
2. **If v25 still crashes while Baseline works:** whole-pack relocation is not a sufficient explanation. The remaining leading hypotheses are native content validation elsewhere, a HUD element record/string mutation that is not semantically safe, a per-build/package check not triggered by Baseline, or a different runtime dependency. Capture logcat before another patch.
3. There is currently insufficient evidence to label the crash “anti-mod detection”. A crash at the splash screen is not by itself proof of a security response.

## Boundaries

No purchase receipts, paid entitlements, billing callbacks, cloud saves, achievements, or leaderboard state were modified. All runtime claims remain unverified until the user device launch and HUD interaction are observed.

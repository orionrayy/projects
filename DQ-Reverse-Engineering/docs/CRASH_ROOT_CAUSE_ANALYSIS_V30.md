# Dungeon Quest crash isolation v30 — metadata CRC/header-key invariant

**Date:** 2026-10-25  
**Runtime status:** static validation passed; device test required.

## New cross-analysis finding

The original stock STK pack's header key is `0x4c4060e8`. Independently decoding the metadata table and calculating CRC32 produces exactly the same value, `0x4c4060e8`.

Earlier pack patches updated the target entry's CRC but did not recalculate the header key and re-XOR the table and every stored payload using the new key:
- v25: modified decoded-table CRC is `0x5ccc58d7`, but header key stayed `0x4c4060e8`.
- v26/v28 no-op pack: modified decoded-table CRC is `0x5e29b9c8`, but header key stayed `0x4c4060e8`.

This deterministic mismatch is a strong candidate for why the no-op v26/v28 packed assets crash even though the decoded entries remain unchanged. It offers a conventional pack-format/checksum explanation and does not require an anti-tamper assumption. The exact runtime validator has not been proven yet; device testing is required.

## v30 paired artifacts

- Stock control: `Dungeon_Quest_3.3.2.0_CRCKey_Control_v30.xapk`
- Modified label diagnostic: `Dungeon_Quest_3.3.2.0_CheatsLabel_CRCKeyFix_v30.xapk`
- Package ID: `com.shinybox.dqv30`
- Both use the same signing certificate SHA-256: `a0f7e52d67c10d0b0347774cab2fae3f5c965d711a408a3479b14456da926e0b`.
- Control XAPK SHA-256: `d28af3e96b80371c0307458e800b2e4e6e63c858dfbf2d0f4fc783994535f6c4`.
- Modified XAPK SHA-256: `732d9afa23f65891706e39d2075967c2776b08451bfd168ec358d7422d6ca5c1`.

For the modified pack, the header key is set to the CRC32 of the modified decoded table, `0x5ccc58d7`. The metadata table and each unique stored payload range were re-XORed using that key. The packed-file size and entry offsets/sizes/flags are preserved. All 5,630 entries decode, every stored-payload CRC passes, and compared to stock, the only decoded entry content that differs is `Resources/HUD/pause.hud` where `Social/IAP` became the same-length label `Cheat Menu`.

The 19 non-base APK split files are byte-identical between the paired builds. The only ordinary member difference in the base APK is `assets/S3DMain.smf`. Both packages passed local v2-signature and ZIP CRC checks; this is not equivalent to on-device verification.

## Phone-only test procedure

1. Install the stock control v30 and launch it. Confirm it reaches the game.
2. Install the modified v30 over the same app without uninstalling between the pair. Both have package ID `com.shinybox.dqv30` and the same signer.
3. Launch the modified build offline. Record whether it reaches the game and whether the pause HUD displays the new label.

Interpretation:
- **Control works and modified launches:** the missing header key/table CRC invariant likely explains the earlier startup crash. Continue by implementing a true separate cheat UI/action instead of only relabeling the Social/IAP element.
- **Control works and modified still crashes:** do not label the cause anti-tamper yet; inspect other header fields and native parser behavior, then request a phone-side crash trace if possible.
- **Control does not launch:** resolve install/runtime setup before interpreting the modified result.

The modified v30 build is a label diagnostic only. It has no implemented cheat actions and is not runtime-verified. No billing receipt, paid entitlement, cloud save, achievements, or leaderboard code was changed.

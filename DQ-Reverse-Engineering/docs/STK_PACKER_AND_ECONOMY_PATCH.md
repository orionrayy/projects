# STK Pack Writer + First Earnability Patch (v7)

## Scope

This iteration adds a version-6 STK-style pack writer with fail-closed round-trip verification and a narrowly scoped XML patch that converts the 16 cash-priced rows in Resources/XML/Vanity.xml to in-game gold costs. It does not claim to remove every IAP or to be a complete Android build.

## Evidence used

The submitted Dungeon Quest 3.3.2.0 asset pack validates as version 6, with 5,630 entries. The existing parser verified 5,630/5,630 payload CRC-32 values and decoded sizes. Vanity.xml has 74 rows; 16 rows have a numeric Price and blank Gold. Existing earnable cosmetics already use the Gold column (observed values include 25,000, 50,000, 100,000, 150,000, 300,000, and 1,000,000).

## Proposed conversion tiers

| Existing Price field | Proposed Gold cost |
| ---: | ---: |
| 0.99 | 250,000 |
| 1.99 | 500,000 |
| 2.99 | 750,000 |
| 3.99 | 1,000,000 |
| 5.99 | 1,500,000 |

These are initial balance proposals, not original game values. They should be tested against gold income and completion time before a public release.

## Local workflow

1. Extract assets/S3DMain.smf from the authorized APK copy into a separate file.
2. Decode the pack using tools/stk_unpacker.py into a new empty directory.
3. Run tools/apply_cosmetic_earnability_patch.py EXTRACTED_DIR PATCHED_DIR --report report.json.
4. Rebuild a new pack using tools/stk_packer.py original.smf patched.smf --replace Resources/XML/Vanity.xml=PATCHED_DIR/Resources/XML/Vanity.xml --report pack-report.json.
5. Verify all entries in the rebuilt pack before testing. Keep the source APK and original pack unchanged.

## Packer safety properties

- Reads only the verified v6 header/container layout; rejects unknown versions and unsupported compression flags.
- Rejects absolute/traversal paths, duplicate/case-colliding names, invalid metadata ranges, impossible decoded sizes, CRC mismatches, and malformed zlib streams.
- Never edits the input pack in place; output must be a distinct file path.
- Re-validates all 5,630 entries and compares every decoded entry to the source (except explicit replacement targets) before returning bytes.
- An unchanged logical pack may have a different byte layout/size because original payload offsets can contain unreferenced space or shared/overlapping regions. Validation guarantees decoded entry equality, not byte-for-byte identity of the whole container.

## Important limits

This is a cosmetic data experiment only. It does not alter IAP.xml, the Java billing wrappers, receipt validation, native JNI methods, or cloud entitlements. Other IAP families—gold/currency, pets, slots, stash, boosts, and bundles—must not be deleted until each item's contents and acquisition route are mapped and tested. A rebuilt pack has not been installed or run in the game, and no APK was rebuilt or signed as part of v7.

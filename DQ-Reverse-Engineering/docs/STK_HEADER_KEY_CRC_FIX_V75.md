# DQ v75 — STK metadata CRC/header-key fix

Static package validation passed. Physical-device installation and runtime remain untested.

- APK: DQ_ModKit_v75_STK_CRC_KEY_FIX_ARM64.apk
- Package: com.shinybox.dqv75
- Launcher label: DQ v75 Tester
- ABI: arm64-v8a
- Size: 57,062,268 bytes
- APK SHA-256: 02f175d07dcacd46f9f9f9d67809a081dd9b1926737247bcbe7ea5b8484f9346
- Corrected STK SHA-256: 24a89cf3f356a2b48474d9681dedd662cec8cd5ec9f01574b26bed02d0ee6182

## Historical regression found

The v30 crash investigation documented that a modified STK must recalculate CRC32 of the decoded metadata table, use that CRC as the header key, then re-XOR the metadata table and stored payload ranges with the new key. The v31 checkpoint records the user-confirmed result that the app opened after this correction.

A direct check of the v50-derived asset embedded in v72-v74 found the invariant was broken:

| Measurement | Previous candidate | Corrected v75 |
|---|---:|---:|
| Header key | 0x4c4060e8 | 0x45150cdf |
| Decoded metadata table CRC32 | 0x87bfe0b7 | 0x45150cdf |
| Header key equals table CRC | NO | YES |

This is a concrete structural defect consistent with the historical v30 diagnosis.

## How v75 repairs it

- Uses the original stock STK for the layout/control source and the intended v50 pause HUD payload as the replacement.
- Recalculates the target entry offset, compressed/uncompressed sizes and stored-payload CRC.
- Calculates the CRC32 of the modified plaintext metadata table and uses that value as the header key.
- Re-XORs the metadata table and each unique stored payload range under the new key.
- Preserves all 5,629 non-target entry offsets and all 41 exact-alias groups.
- Moves only the changed HUD payload to the payload tail because its compressed payload is larger than stock.
- Keeps the stock classes.dex and omits libdqbridge.so.

## Static checks

5,630/5,630 STK entries pass stored CRC, decompression and decoded-size checks. Exactly one decoded asset differs: Resources/HUD/pause.hud. The other 5,629 decoded entries are byte-identical to stock; all their offsets and alias relationships are preserved.

APK ZIP CRC, pre/post-sign 16 KiB native-library alignment, APK Signature V1/V2/V3, aapt badging, provider-authority inspection, stock DEX hash and absence of libdqbridge.so all pass. Excluding signature metadata, only AndroidManifest.xml, resources.arsc and assets/S3DMain.smf differ from the prior v74 comparator.

## Phone-only test

1. Stop reopening v72. Keep the official game installation and its data untouched.
2. Download v75 directly on the phone and open the APK in Downloads/File Manager.
3. Install DQ v75 Tester as a separate application. Do not uninstall the official game.
4. Launch once offline, without tapping Gold +100K. Record whether the app reaches the first stable screen.
5. If it force-closes again, stop repeated launches and send a screenshot of the symptom.

The historical invariant is now corrected, but the build has not yet been tested on the user's device. Gold +100K remains 0/9 runtime-verified, the 222-entry catalogue remains 0/222, and stable promotion remains blocked.

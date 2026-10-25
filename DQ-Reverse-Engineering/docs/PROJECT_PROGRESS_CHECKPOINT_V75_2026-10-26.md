# Dungeon Quest ModKit checkpoint — v75 STK header-key CRC repair

Date: 26 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
Prior build: v74 provider-authority comparator

## Historical repair reproduced

The v30 documentation records a deterministic STK invariant: CRC32 of the decoded metadata table must equal the header key. The v31 checkpoint records the user-confirmed result that the app opened after this correction. A direct inspection of the STK included in v74 found the v50-derived pack violated the same invariant: header key 0x4c4060e8 versus metadata CRC 0x87bfe0b7.

## v75 artifact

- APK: DQ_ModKit_v75_STK_CRC_KEY_FIX_ARM64.apk
- SHA-256: 02f175d07dcacd46f9f9f9d67809a081dd9b1926737247bcbe7ea5b8484f9346
- Size: 57,062,268 bytes
- Package: com.shinybox.dqv75
- Label: DQ v75 Tester
- Corrected STK: 24a89cf3f356a2b48474d9681dedd662cec8cd5ec9f01574b26bed02d0ee6182
- Header key and metadata CRC: both 0x45150cdf

## Change boundary

The pack starts from the original stock STK and uses the target pause HUD payload from the existing v50 candidate. It recalculates target metadata, calculates the CRC of the complete plaintext table, uses that as the new header key, and re-XORs each unique stored payload range. Only Resources/HUD/pause.hud changes at decoded-content level. All 5,629 other entry offsets remain unchanged, all 41 exact-alias groups are preserved, and the target payload is moved to the payload tail as its compressed form is larger than stock.

The package keeps the stock DEX and has no native probe bridge. Provider authorities and package ID remain unique from v74 and the official app.

## Current gates

Static package validation passes: STK 5,630/5,630 entries, header-key/metadata-CRC invariant, stored CRC/decompressed-size checks, APK ZIP CRC, 16 KiB alignment, V1/V2/V3 signature verification, aapt package/label/authority inspection, stock DEX hash.

No device installation or runtime test has been performed here. Force-close fix on the user's device remains unverified. Gold +100K remains 0/9; catalogue runtime effects remain 0/222; promotion remains blocked.

Phone-only steps: download v75, install as a separate DQ v75 Tester app, launch offline once without tapping Gold +100K, and report whether the first stable screen appears. Keep the official app and save data untouched.

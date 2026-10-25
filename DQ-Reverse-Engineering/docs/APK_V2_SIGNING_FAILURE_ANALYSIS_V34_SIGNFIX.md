# APK v2 signing failure analysis — v34 SIGNFIX

Date: 2026-10-25  
Project: Dungeon Quest 3.3.2.0 diagnostic XAPK  
Status: corrected package built and strict local validation passed; device install still required.

## User-observed failure

The Android XAPK installer reported:

`INSTALL_PARSE_FAILED_NO_CERTIFICATES`  
`Failed to collect certificates ... using APK Signature Scheme v2: Failed to parse/verify signer #1 block: No supported signatures found`

This occurs before the game launches, so it is independent of the Gold keyboard callback.

## Root cause

The first v34 signer builder emitted only one length-prefixed layer where the APK v2 value requires a length-prefixed signer sequence containing a length-prefixed signer. The local verifier repeated the same incorrect assumption, creating a false pass. The user device therefore found no supported signature record.

## Corrected artifact

- File: `Dungeon_Quest_3.3.2.0_CheatMenu_SetGoldKeyboardProbe_v34_SIGNFIX.xapk`
- SHA-256: `2cb1502410873003d2178eb1b94e44e5decf8150371f116fc456a82aac3820b0`
- Size: 57,571,123 bytes
- Split count: 20
- Package ID: `com.shinybox.dqv30`
- Signer SHA-256: `6ba5a7ebddfccc1fde12c0b7538bd390dad51bc3b963d03c68e7545b961917b0`

The same v34 certificate/private key was reused, so the only change from the failed file is the corrected signing block encoding and resulting APK signatures/digests. The game asset payload and XAPK member naming remain otherwise the same.

## Verification performed

- All 20 APKs contain the standard pair ID `0x7109871a`.
- Correct two-level signer sequence structure is present.
- Single signer has signed-data length 915 bytes, signature sequence length 268 bytes, public-key field length 294 bytes, and signature length 256 bytes for RSA PKCS#1 SHA-256.
- The certificate DER (855 bytes) and public key match.
- Strict local verifier recomputed the content digest and verified the RSA signature.
- All 20 inner APK ZIP CRCs and the XAPK outer ZIP CRC pass.
- All 5,630 STK entries decode and verify CRC; header key matches decoded metadata-table CRC.
- All split APKs have the same signer fingerprint.

The environment does not contain Android SDK `apksigner`, so no official `apksigner verify` result is claimed. Android's Package Manager/XAPK installer must still be used to confirm installation.

## User test

Install the SIGNFIX file, not the earlier non-SIGNFIX v34 file. If v31/v33 remains installed as package `com.shinybox.dqv30`, uninstall only that diagnostic app due to the different certificate. Keep original `com.shinybox.smash` installed. Test offline with disposable progress; tap Options → Cheat Menu → Add → Set Gold and note whether the game keyboard opens and whether confirming an integer changes the visible Gold balance.

The Set Gold keyboard/effect itself remains unverified.

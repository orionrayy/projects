# DQ v78 — phone-only installation instructions

v78 is a newly built XAPK with all 20 APK splits, not a single APK file.

1. Download DQ_ModKit_v78_SPLIT_PACKAGE_ARM64.xapk.
2. Use your existing XAPK installer. Do not tap the XAPK as if it were a standalone APK.
3. Confirm the app appears as **DQ v78 Tester**, package ID com.shinybox.dqv78.
4. Leave the official com.shinybox.smash app and its save data untouched. Do not install v78 over the official package.
5. For the first launch, go offline and do not press Gold +100K or other cheat controls. Note whether it reaches the title/menu or force-closes.

Static checks passed for all 20 split APKs: consistent package ID and test signer, V1/V2/V3 signatures, ZIP CRCs, 16 KiB alignment, DEX checksum and corrected STK hash. Physical-device startup is not yet verified. Local signing is not the official publisher signature.

# DQ ModKit v78 — split XAPK build report

**Status:** STATIC VALIDATION PASS; DEVICE RUNTIME NOT TESTED.

- File: DQ_ModKit_v78_SPLIT_PACKAGE_ARM64.xapk
- Size: 43,761,625 bytes
- SHA-256: d328410182225ef09610b3670aadc6d4e56e4c8f815288116dd7bd2b5b21abc0
- Package: com.shinybox.dqv78 / DQ v78 Tester
- Split inventory: 20/20
- Signing cert: aee4ae54f7b8f5bfeeae8aef24da3a2cd365a5f9d36f7ec616d7a86ef6d50957 (local test key)

v78 is a new XAPK build—not a reissue of v77. It uses the complete split inventory, corrected v75 STK, a consistent tester package identity across all splits, updated provider authorities, DEX identity with recalculated SHA-1/Adler-32, and a matching dotted application-data identity in the ARM64 native client. Original Java class namespace/JNI exports are preserved.

**Verified statically:** XAPK and inner ZIP CRCs; all 20 package IDs; common signer; V1/V2/V3 signatures; 16 KiB alignment; DEX header checksums; corrected STK hash; unique provider authorities.

**Not verified:** install/start on the user's phone, force-close resolution, Gold +100K, save/reload, or 222-cheat native integration. The local signing certificate differs from the publisher. Keep the official app and save data untouched. Install using an XAPK installer, not as a single APK.

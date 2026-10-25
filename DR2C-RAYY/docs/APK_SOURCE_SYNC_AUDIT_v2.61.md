# DR2C VORENYX — Source-to-APK Payload Reconciliation v2.61

**Date:** 25 October 2026  
**Static payload result:** PASS for the base plus the exact locally available overlay layers and the v2.61 tutorial source-sync supplement.  
**Runtime/release result:** NOT VERIFIED; do not treat this as a stable release.

## Exact artifacts used

- Base source archive: DR2C-RAYY(2).zip, 13,809,097 bytes, SHA-256 14f44400c3314a6d9b7e5428077c199c846367235e379199618f7b11288f4eb1.
- Base APK: DR2C-v1.8.2-full-apkvision.apk, 109,011,456 bytes, SHA-256 d4b509d899df572d80de553c8545c850ff2122c2d99fae5cfad2532159d35c15.
- Candidate APK: DR2C_VORENYX_v2.57_SIGNATURE_FIX_REDELIVERED_20261025.apk, 115,615,585 bytes, SHA-256 a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7.
- The Library file named DR2C_VORENYX_v2.58_ANDROID11_SIGNATURE_FIX.apk has the exact same SHA-256 and is byte-identical to the v2.57 signature-fix candidate. Its filename does not mean it contains the separate v2.58 localization batch.

## Reconciliation results

- Base source archive and base APK contain 509 .df scripts, all byte-identical: **509/509**.
- Ordered available overlays: v2.43 localization (269 script files), v2.45 corrective source patch (12 files), v2.45 Startfix source patch (6 files), then the v2.61 tutorial synchronization supplement (1 file).
- Before the supplement, the candidate matched 508 of 509 effective script payloads. The sole mismatch was assets/deathforth/events/tutorial.df (expected v2.43-layer SHA-256 8f35ddda555ac2bc13e675bbedff7a34fbc366ffce1bf4bd838a206f7a21f552; candidate SHA-256 efee1bcb8ce796ee98b2bc27c7bdea4c42296c49b0f2ab673a81cce796f815dd).
- The v2.61 supplement records the exact tutorial payload already embedded in the candidate APK. After applying it as the last layer, the effective source set matches **509/509** candidate scripts exactly; missing scripts: 0; extra scripts: 0; mismatches: 0. All input layer ZIP CRCs pass and duplicate-path count is zero.
- The supplement is source-only and remains a separate local artifact; the APK and extracted game scripts are not committed to public GitHub.

## What this proves—and does not prove

This proves reproducible byte-level parity between the base source archive, the base APK, the three historical patch archives available in the Library, the explicit tutorial synchronization supplement, and all 509 Deathforth script payloads in the candidate. It closes the known source-to-candidate drift for the available lineage.

It does **not** prove complete historical lineage or that every previously requested localization batch is included. The exact v2.47–v2.51 patch ZIPs and distinct v2.58 localization candidate are not available for byte-level inspection. Full Batch A–K integration is not claimed; full semantic localization coverage is still not computed.

It also does not prove the embedded Deathforth VM accepts the tutorial, Android accepts the local signing certificate, Start dispatches, gameplay works, UI fits, or save/load is stable. No Android device, ADB/logcat, emulator, official apksigner, or embedded Deathforth runtime was available in this audit environment.

## Reproduction

Run the standard-library checker with exact artifact paths and layers in order:

    python DR2C-RAYY/tools/audit_apk_source_sync.py --base-source DR2C-RAYY.zip --base-apk DR2C-v1.8.2-full-apkvision.apk --candidate-apk DR2C_VORENYX_v2.57_SIGNATURE_FIX_REDELIVERED_20261025.apk --layer DR2C_VORENYX_ID_v2.43_localization_patch.zip --layer DR2C_VORENYX_v2.45_CORRECTIVE_SOURCE_PATCH.zip --layer DR2C_VORENYX_v2.45_STARTFIX_SOURCE_PATCH.zip --layer DR2C_VORENYX_v2.61_TUTORIAL_SOURCE_SYNC_PATCH.zip --json-out audit/apk_source_sync_v2.61.json

The APKs and source patch archives remain outside public GitHub. The repository contains only the audit tools, regression tests, sanitized summary, and report.

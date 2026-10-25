# Source reconciliation and APK release gate — 25 October 2026

## Result

A standard-library Python reconciler was implemented at tools/reconcile_overlay.py with unit tests at tests/test_reconcile_overlay.py. It layers source overlays in explicit order, pins the source archive hash when requested, rejects bad ZIP CRCs, duplicate ZIP names, unsafe paths and missing Deathforth script targets, and emits a normalized source patch with per-input provenance hashes.

## Executed against available assets

- Base source ZIP DR2C-RAYY(2).zip: SHA-256 14f44400c3314a6d9b7e5428077c199c846367235e379199618f7b11288f4eb1
- v2.43 localization patch: SHA-256 00ff7866242e8b3aca4fc749e93455ba1c795c4eec99fd15baa07ab483aca024
- v2.45 corrective source patch: SHA-256 b2cc843325ede21d00cb91dad4a4ff68fa8c3c0e629d6910860727a4db4cf88d
- v2.45 Start quote-fix patch: SHA-256 36f423d620ec852a82d74d34fab02b83f350c8cd5a1cd304d6e247d494495267

Generated artifact DR2C_VORENYX_v2.45_RECONCILED_SOURCE_PATCH.zip: SHA-256 faebba3ee0d14dd0cee668fe132fa95c8ba21f08963f627f59e5364c02658c0f. ZIP CRC passed; 274 total entries, 272 normalized payload paths, 18 later-layer overrides, 509 source Deathforth scripts found, and 269 source-script payloads in the reconciled overlay. Canonical GAME-MARKER passed; no backslash-escaped quote sequences remained in effective Deathforth scripts. Four unit tests passed.

## Important reconciliation finding

The v2.51 Batch K report says the cumulative overlay covers 77 of 509 .df scripts, while the available v2.43 patch ZIP physically contains 269 .df overlay payloads. Those counts may use different definitions, but an artifact-level mapping has not been supplied. Do not report either number as a translation-coverage percentage. The exact v2.51 patch archive was not found in the active Library/workspace, so it cannot be byte-level reconciled here.

The generated artifact comprises v2.43 + v2.45 corrective + v2.45 quote-fix. It is not v2.51 and is not an APK. The v2.47 through v2.51 patch ZIPs were unavailable during this run.

## Still blocked

No Android build toolchain is installed in the current execution environment: apksigner, zipalign, apktool and adb are not found. No APK was built, signed, installed or runtime-tested. The current device package version and signing identity are unknown. Do not uninstall the existing app or claim Start/UI fixed until there is a save backup, a confirmed installation outcome and post-install runtime evidence.

Next gate: retrieve the exact v2.47 through v2.51 patch ZIPs, reconcile them against this validated baseline, then build only from a clean and integrity-verified authorized base using a compatible Android toolchain. Keep the base APK/source archive and binary overlays out of the public repository.

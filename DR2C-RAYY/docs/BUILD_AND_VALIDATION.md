# Build and Validation — v2.1

Current patch: DR2C_VORENYX_ID_v2.1_localization_patch.zip (distributed as a separate user artifact, not committed to this public repository).

## Static results
- Source files scanned: 541.
- Literal occurrences: 17,329; unique literal values: 13,038.
- Heuristic player-facing occurrences: 10,843; changed: 3,494 (32.22%).
- Probable unique untranslated candidates: 6,545.
- Latest batch rewrite hits: 187.
- Scopes: Shooting 15; Fitness 12; Mechanical 4; Army Surplus 45; Rifle Collector 61; Blade Master 50.
- Display-expression open/close markers: 229/229.
- Failures: none reported; ZIP CRC PASS.
- Runtime gameplay: NOT RUN; save/load: NOT RUN; APK rebuild/signing: NOT PERFORMED.

v2.1 reconciles selected previous mappings to the v1.4 baseline because experimental v1.5/v1.6 outputs reverted some earlier translations.

## Reproduction
1. Keep the user-provided original archive as a read-only local baseline.
2. Confirm target game-data version/path and back up target data.
3. Apply only the overlay via a compatible mod workflow.
4. Use static ZIP CRC checks and inspect complete display expressions.
5. Runtime-test menus, choices, resource changes, purchases/robbery, transitions and save/load.
6. Rebuild/sign the APK only after runtime stability is demonstrated.

Static validation is not a substitute for runtime compatibility. This is not a signed APK and not a 100% localization release.

# Build and Validation — v2.2

## Verified static status
- Patch: `DR2C_VORENYX_ID_v2.2_localization_patch.zip`.
- Input inventory: 541 files, 17,329 quoted literal occurrences, 13,038 unique strings.
- Likely player-facing heuristic: 10,844 occurrences; changed 3,509 (32.36%); probable unique untranslated candidates: 6,531.
- v2.2 exact-context fixes: 15.
- Targeted residue patterns remaining in `weapons.df`: 0.
- Display markers in `weapons.df`: 157/157.
- Embedded static report: PASS; failures empty; ZIP CRC PASS.
- Runtime gameplay/save-load/APK rebuild: NOT RUN / NOT PERFORMED.

v2.2 also resolves a packaging discrepancy: v2.1’s working-folder validation report passed, but the report embedded in the ZIP still listed English-residue findings. v2.2 verifies the actual packaged artifact.

## Installation/reproduction limits
Keep the user-provided archive as a read-only base. Back up target data and confirm game version/path before applying the overlay. This is not a signed APK. Static integrity does not prove runtime compatibility; test UI, event branches, costs/rewards, combat, save/load and rebuild/signing in a compatible environment.

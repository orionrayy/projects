# Build, Reproducibility, and Validation

## Latest checkpoint

Build: v1.3 QA repair. Static integrity PASS, skipped exact rewrites 0, static failures 0, ZIP CRC PASS.

Latest local package: DR2C_VORENYX_ID_v1.3_localization_patch.zip. The local project archive also contains versioned diff files, translation inventory, research sources, build generators, generated art and the user-provided base archive.

## Reproducing locally

1. Keep a lawful copy of the original user-provided archive and extract the Deathforth script/assets into a local working directory.
2. Check every path in the versioned builder; historical scripts use fixed /mnt/data paths and require updating for a different machine.
3. Preserve the original source directory as read-only baseline.
4. Generate an overlay rather than modifying the base in place.
5. Validate exact rewrite counts, display expression open/close counts, sentinel identifiers and ZIP CRC.
6. Inspect player-visible text manually for mixed-language residue, UI overflow and persona drift.
7. Runtime-test menus, events, trader choices, combat/flee effects and save/load.
8. Rebuild/sign an APK only after overlay stability is proven.

## v1.3 static results

- Source files scanned: 541.
- Quoted literal occurrences: 17,329.
- Unique literals: 13,038.
- Changed likely player-facing occurrences (heuristic): 3,186 / 10,843 = 29.38%.
- Unique probable player-facing untranslated candidates: 6,813.
- Exact rewrites skipped: 0.
- Static failures: 0.
- ZIP test: PASS.
- Runtime game test: NOT RUN.
- Save/load test: NOT RUN.
- APK rebuild/sign: NOT PERFORMED.

## Limits

Static checks can detect malformed delimiters or missing sentinels but cannot guarantee every script branch is syntactically or semantically valid in the game engine. The translation percentage is heuristic; it is not full-locale completeness.

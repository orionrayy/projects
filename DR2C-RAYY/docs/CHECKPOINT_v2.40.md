# DR2C VORENYX v2.40 — Checkpoint

**Static validation: PASS. Full player-visible localization: NOT COMPLETE.**

## Scope
- Base: verified v2.39 patch ZIP.
- Repaired 45 trait/perk key operands across 13 modules. v2.39 had 45 mismatches; v2.40 has **0 mismatches across 195 compared operands**.
- Display labels now localize at the presentation boundary while machine identifiers remain canonical.
- Continued contextual Indonesian localization across CYOA guidance, travel/camp prompts, NPC dialogue, reward text, comic/magazine interactions, medical feedback, combat tutorials and event narration.
- Title-art badge refreshed to V2.40.

## Static checks
- CYOA/choice IDs preserved.
- Route/resource path literals preserved.
- Comment-aware scan: 541 .df/.txt files; 16,834 active quoted literals.
- Inherited high-likelihood candidate queue: 0 rows remain in the merged source. This does not establish complete localization or an exhaustive semantic scan.
- Patch ZIP: CRC PASS, 411 entries, 410 tree-manifest entries, 0 hash failures, 0 duplicate paths and 0 machine-local-path leaks.
- Full project archive v2.5: CRC PASS, 185 entries, 184 manifest entries, 0 hash failures, 0 unmanifested files and 0 duplicate paths.

## Coverage and limits
Global semantic coverage is **NOT COMPUTED**. The old v2.22 69.07% heuristic is stale and is not a v2.40 score. Runtime gameplay, event-path coverage, actual UI fit/overflow, save/load, and APK rebuild/signing are **NOT RUN / NOT PERFORMED**.

## Distribution
The public repository contains documentation and sanitized audit summaries only. The patch ZIP and original source archive are local artifacts and are not hosted in the repository.

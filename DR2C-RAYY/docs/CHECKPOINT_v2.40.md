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


## Coverage recheck addendum — 24 October 2026

- Current global player-visible localization percentage: **NOT COMPUTABLE FROM CURRENT EVIDENCE**.
- Fresh active-literal inventory: 16,834 rows; 15,839 rows excluding path/engine entries.
- English-likelihood triage: 1,578 rows at ≥0.2 and 598 at ≥0.5. Another 305 new/changed rows have no score. Broad triage = 1,883 rows across 196 files.
- The inherited residual queue being empty is not an exhaustive zero-residue result; package metadata marks the inherited queue stale.
- 88.11%–94.30% is a machine-audit non-flagged proxy only, **not** translation coverage.
- Historical 69.07% remains the v2.22 heuristic and must not be reported as current v2.40 coverage.
- Full note: [Coverage recheck](COVERAGE_RECHECK_v2.40.md); machine-readable metrics: [v2.40 coverage JSON](../audit/v2.40_coverage_recheck.json).

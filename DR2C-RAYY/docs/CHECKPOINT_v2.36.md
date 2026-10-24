# DR2C VORENYX v2.36 — Checkpoint

**Independent static validation: PASS. Full player-visible localization: NOT COMPLETE.**

## Scope
v2.36 localizes 45 complete player-facing expressions and 12 direct literal occurrences across 31 modules. Main areas:
- Arcade-defense text and bandit-raid defense/rewards.
- Siege route encounters, park and bathroom events, shop/fairy encounters.
- City-ranger, panda and Alvis events.
- Perk/trait onboarding, character blurbs and an epilogue fragment.
- Character banter and additional trader-gym text.

The full per-file ledger is maintained in the local artifact's `audit/v2.36_translation_ledger.json`; this public checkpoint is a sanitized summary.

## Static checks
- 31 scoped files checked against the exact v2.35 package/base.
- Source line counts and non-display code skeletons preserved.
- CYOA IDs, choice IDs and route-path literals preserved.
- 12 direct literal occurrences changed; targeted mappings are consumed.
- ZIP CRC: PASS.
- Archive: 376 entries; manifest: 375 entries.
- Duplicate paths: 0; manifest hash mismatches: 0; machine-local path leaks: 0.
- Artifact SHA-256: `fa76da687ce7d8ea5b1e2fafa165b40c31829248fadb5e8c9c6b1ebec3dd5608` (20,771,028 bytes).

## Inventory and coverage
- Comment-aware inventory: 541 source files and 16,819 active quoted-string tokens.
- English-likelihood triage queue: 77 candidate rows across 36 files. This is a heuristic review queue, not a unique-string count or translation percentage.
- The 69.07% figure is a stale v2.22 heuristic baseline. Current global semantic coverage is **not computed**, and 100% is not claimed.

## Validation limits
Runtime gameplay, actual UI fit/text overflow, save/load, and APK rebuild/signing were **NOT RUN / NOT PERFORMED**. Static checks do not prove runtime compatibility or semantic completeness.

## Distribution boundary
Public GitHub stores project-authored documentation and sanitized audit summaries only. The full source overlay and release ZIP remain local.

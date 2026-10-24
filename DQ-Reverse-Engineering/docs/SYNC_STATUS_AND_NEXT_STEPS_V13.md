# DQ Modkit — Synchronization and Verification Status v13

Date: 2026-10-24  
Branch: `feat/dq-iap-debug-cheats-modkit-v7`  
PR: [#26](https://github.com/orionrayy/projects/pull/26) — open draft at audit time.

## What was added

- `docs/IAP_SKU_RUNTIME_EVIDENCE_V13.json`: machine-readable 109-SKU matrix with explicit runtime evidence on every row.
- `docs/IAP_RUNTIME_ENTITLEMENT_EVIDENCE_V13.md`: human-readable account of the purchase-result boundary and unresolved grant semantics.
- `tools/validate_iap_runtime_evidence_v13.py`: fail-closed consistency and evidence-contract validator.
- `tests/test_iap_runtime_evidence_v13.py`: tests for the current evidence matrix, invalidly asserting a SKU as verified, and corrupted registry counts.

The matrix is derived from the existing `IAP_SKU_RECONCILIATION_V7.json`. Its inherited `migration_status` and proposed replacement route remain migration/design classifications, not runtime findings.

## Reconciled IAP counts

| Signal | Verified static count |
|---|---:|
| IAP XML identifiers | 107 |
| DEX static SKU identifiers | 104 |
| Shared identifiers | 102 |
| XML-only identifiers | 5 |
| DEX-only identifiers | 2 |
| Union | 109 |
| Numeric-suffix Vanity asset correlations | 46 |
| Runtime reward mappings verified | 0 |
| Runtime reward mappings unverified | 109 |

Purchase request messages 600 and 602 route to the statically observed wrapper helpers; restore message 601 routes to its restore helper. The visible success/failure callbacks are native declarations without DEX bodies. No exact reward payload or persisted entitlement write is claimed.

The matrix validator checks these counts and mismatch sets, and requires a concrete reward payload, evidence references, an observed persisted entitlement write, and a passing runtime test before a row may be marked `VERIFIED`.

## Test-run bookkeeping

The local v10 ZIP contains 35 unittest-discovered tests; all 35 passed when rerun. Its packaged `reports/validation_v10.json` says `test_count: 34`, so that metadata field is stale by one. This report does not rewrite the historical v10 ZIP or claim that GitHub CI ran the v13 tests.

No GitHub Actions run was returned for the v13 evidence commit at the time this status was checked. The PR description's linked Actions run is earlier evidence and must not be read as validation of the new v13 files.

## Source synchronization and native blocker

This branch is still a curated repository, not a mirror of a full local extraction:
- Only two actual `.smali` files are tracked under `disassembly/`.
- No generated 68-class Java declaration scaffold set is present.
- The tracked `manifest/` entry remains an analysis excerpt.
- The local v10 ZIP does not contain the 68 disassemblies or 68 Java declaration scaffolds, so they cannot be synchronized from that archive.

The supplied base APK has no `lib/*.so`; expected library load order is `crypto`, `ssl`, `openal`, `S3DClient`, and the manifest excerpt indicates required ABI/density splits. The exact matching split set, ABI, library hashes, ELF machine/SONAME/NEEDED chain, and runtime symbols remain unverified. A compatible replacement engine remains a major port, not a realistic placeholder-library patch.

## Next verifiable step

Supply the matching base/XAPK/APKS split set for version 3.3.2.0, with its ABI and density configuration intact. Then inventory every `lib/<abi>/*.so`, hash each file, inspect ELF dependencies and native exports/registration, and follow the native callback into a controlled before/after player-state diff. Until that evidence exists, keep all 109 SKU grants unverified.

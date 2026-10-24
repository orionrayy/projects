# Build and Validation — v2.36

## Release artifact
- Local artifact: `DR2C_VORENYX_ID_v2.36_localization_patch.zip`
- Size: 20771028 bytes
- SHA-256: `fa76da687ce7d8ea5b1e2fafa165b40c31829248fadb5e8c9c6b1ebec3dd5608`
- ZIP entries: 376
- SHA-256 manifest entries: 375
- ZIP CRC: PASS
- Duplicate paths: 0
- Manifest hash failures: 0
- Machine-local path leaks: 0

The release checksum is kept in an adjacent SHA-256 sidecar, outside the ZIP. The public GitHub repository contains sanitized documentation/audits, not the local source overlay.

## v2.36 scope and static checks
- 45 complete display expressions rewritten.
- 12 direct literal mapping rules matched; 12 occurrences changed.
- 31 scoped modules; source line counts and non-display skeletons preserved.
- CYOA IDs, choice IDs, and route-path literals preserved.
- Direct mapping residues: 0 for targeted literals.
- Independent ZIP/manifest validation: PASS.
- Comment-aware scan: 541 source files, 16,819 active quoted-string tokens.
- Residual triage queue: 77 candidate rows across 36 files; candidate counts are not a coverage score.

## Metadata reconciliation
The v2.34 archive had a mismatch between checkpoint scope and actual archive contents, with stale embedded ZIP digest metadata. v2.35 reconciled it to the actual nine-file v2.34 scope; v2.36 carries that correction forward. See [v2.34 reconciliation](CHECKPOINT_v2.34.md).

## Coverage status
The 69.07% figure belongs to the v2.22 heuristic and is stale. Current global semantic coverage is not computed. Full localization is incomplete.

## Not executed
- Runtime gameplay test
- Actual UI-fit / text-overflow test
- Save/load test
- APK rebuild and signing

Static structure and archive integrity do not prove runtime compatibility or semantic completeness.

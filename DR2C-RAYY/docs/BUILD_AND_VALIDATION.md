# Build and Validation — v2.35

## Release artifact
- Local artifact: `DR2C_VORENYX_ID_v2.35_localization_patch.zip`
- Size: 19828207 bytes
- SHA-256: `df3cd3840b3a6f32e5861b976045112ee790db6e472ae512ebac8d2e1b4fcee1`
- ZIP entries: 362
- SHA-256 manifest entries: 361
- ZIP CRC: PASS
- Duplicate paths: 0
- Manifest hash failures: 0
- Machine-local path leaks: 0

The checksum is recorded outside the ZIP to avoid embedding a self-referential archive digest. The public GitHub repository contains sanitized documentation and audit summaries, not the local source overlay.

## v2.35 scope and static checks
- 32 full display expressions rewritten across 12 source modules.
- 9 direct literal mapping rules matched; 9 occurrences changed.
- File line counts remain equal before/after for every scoped file.
- Non-display source skeletons preserved.
- CYOA IDs, choice IDs, and route-path literals preserved.
- Direct mapping residues: 0 for targeted literals.
- Current comment-aware scan: 541 source files, 16,827 active quoted-string tokens.
- Residual triage queue: 129 rows across 67 files; queue count is not a coverage score.

## v2.34 reconciliation
The v2.34 ZIP's checkpoint text described a stale three-file batch, while its actual audit/ledger scope and overlay changes cover nine different files. Its embedded ZIP digest and byte count were stale as well. The v2.35 package corrects the v2.34 checkpoint and audit metadata using the actual v2.34 ZIP contents. See [v2.34 reconciliation](CHECKPOINT_v2.34.md).

## Coverage status
The old 69.07% figure belongs to a v2.22 heuristic and is stale. Current global semantic coverage is not computed; the inventory's English-likelihood queue is for triage only. Full localization is incomplete.

## Not executed
- Runtime gameplay test
- Actual UI-fit / text-overflow test
- Save/load test
- APK rebuild and signing

Static token, line-count, source-skeleton, identifier and ZIP checks do not establish runtime compatibility or complete localization.

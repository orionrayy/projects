# DR2C VORENYX — Batch K provenance reconciliation (v2.54 audit)

**Status: SOURCE LINEAGE UNRESOLVED. Do not auto-merge these overlay generations or build a release APK from mixed layers.**

This checkpoint adds no localization patch and is not an APK release. It compares the locally available base source ZIP and v2.43 localization ZIP, then checks the nine source paths named by the v2.51 Batch K report. The stated v2.46 baseline and actual v2.47–v2.51 ZIP bytes are not available in the current workspace/visible Library ZIP set.

## Byte-level comparison

| Measure | Result |
|---|---:|
| Base archive | `DR2C-RAYY(2).zip`, 13,809,097 bytes; SHA-256 `14f44400c3314a6d9b7e5428077c199c846367235e379199618f7b11288f4eb1` |
| Base Deathforth scripts | 509 |
| v2.43 overlay | 24,350,974 bytes; SHA-256 `00ff7866242e8b3aca4fc749e93455ba1c795c4eec99fd15baa07ab483aca024` |
| v2.43 `.df` payload paths | 269 |
| Matching paths compared | 269 |
| Byte-identical to base | 0 |
| Byte-different from base | 269 |
| Base scripts without overlay payload | 240 |
| Overlay-only script paths absent from base | 0 |
| v2.51 reported target paths present and byte-different in v2.43 overlay | 9 of 9 |

Both locally available ZIPs pass CRC and have no duplicate archive paths. See `audit/batch_k_provenance_v2.54.json` for the compact evidence summary. The full local tool output is available in the attached audit artifact.

## Later report metadata checked

- **v2.47:** cites a v2.46 baseline SHA-256 `6d4e2f3df07d199807c08418ae5d30b9927e5b2e36c780a51858045336b29313`; reported patch 69,656 bytes, SHA-256 `08731efd0d451332a7d0af5f4587d7bc524f291d4700c720cf483d230a0158cc`, eight changed scripts.
- **v2.48:** reports 59 cumulative overlay scripts; 331,975-byte ZIP, 61 entries, SHA-256 `062d2506cdebcccfc1fa2022b2ff597882f5b8d5e18e53f9a9605ad97152d5d5`.
- **v2.49:** reports 73 cumulative overlay scripts; 429,369-byte ZIP, 77 entries, SHA-256 `926278b87eac76a5329e7ce16c04993dd127cc296a78fc6dedb56cd791562ced`.
- **v2.50 Batch J:** PR description says supplies/barter and baked-cod event were covered, but no Batch J report/JSON appears in the PR changed-file list or accessible current artifacts.
- **v2.51 Batch K:** reports 77 cumulative overlay scripts; 460,379-byte ZIP, 85 entries, SHA-256 `e265c7d2789e6936aadea49a42c4b5c87799c202945f8cfa4bee7291a8a40046`. Its nine listed paths include Cupid blurb, Santa blurb and Sasquatch event as three newly added overlay scripts.

The actual v2.51 ZIP cannot be byte-verified here. All nine paths are already present and byte-different from the base in the locally available v2.43 overlay, including those three paths described as new in v2.51.

## Interpretation and gate

This establishes an unresolved provenance/lineage gap; it does **not** identify which report or archive is wrong. The missing v2.46 baseline and actual v2.47–v2.51 ZIPs prevent a valid layered comparison. Counts alone cannot establish that later batches preserve earlier localized scripts.

Do not reconstruct v2.51 by guessing translations, replace the 269-script artifact with the reported 77-script count, or combine these layers automatically. The gate is: obtain the exact v2.46 baseline and at least the actual v2.50 Batch J and v2.51 Batch K ZIPs with checksum sidecars; compare against the proper baseline; rerun source contracts and a real Deathforth parse if available; then build/sign and test the APK.

No localization-quality, full-parser, APK installability, UI-fit, Start-button, gameplay-stability or save/load claim is made by this audit.

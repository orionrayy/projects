# Build and Validation — v2.40

## Release artifacts (local; not hosted on GitHub)

- Patch: `DR2C_VORENYX_ID_v2.40_localization_patch.zip`
- Bytes: 24380609
- SHA-256: `a863cadfda4d99ef14c9199e255cbfc8e687c1d05a1853b8f461f096870b26eb`
- ZIP CRC: PASS; entries: 411; internal tree-manifest entries: 410; manifest hash failures: 0; duplicate paths: 0; machine-local path leaks: 0.
- Full project archive: `DR2C_VORENYX_Project_Archive_v2.5.zip`
- Bytes: 105064456
- SHA-256: `cc0e7818dd87f0fe508692ae0545343ad89c727c401c81ad00f703377962fa97`
- ZIP CRC: PASS; entries: 185; manifest entries: 184; hash failures: 0; unmanifested files: 0; duplicate paths: 0.

## Source invariants

- 45 trait/perk machine-key mismatches from v2.39 repaired across 13 modules.
- Zero source-vs-overlay key mismatches remain across 195 compared operands.
- CYOA/choice identifiers preserved; route/resource path literals preserved.
- Title-art copies are byte-identical.

## Inventory and completeness

- 541 .df/.txt files scanned; 16,834 active quoted literals indexed.
- Inherited high-likelihood candidate queue: 0 rows in the current merged source. This is a triage result, not a coverage score.
- Global semantic coverage: NOT COMPUTED; full Indonesian localization: NOT COMPLETE.

## Not run

Runtime gameplay, event-path regression, actual UI text fit/overflow, save/load and APK rebuild/signing were NOT RUN / NOT PERFORMED. This is a data/script overlay, not a rebuilt or signed APK.

# DR2C VORENYX — Indonesian Localization

**Latest documented localization batch: v2.51 Batch K · cumulative overlay claim 77/509 scripts · APK/runtime NOT VERIFIED · Full localization NOT COMPLETE**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for *Death Road to Canada*. The target is natural, context-aware Indonesian with distinct character voices and blunt sarcasm. Original campaign flow, machine identifiers, branch conditions, route IDs, and game-state effects are invariants.



## Reproducible source packaging — v2.55 (25 October 2026; not a game/APK version)

- Normalized ZIP member timestamps and file modes so repeat source builds are byte-reproducible. Three independent builds produced SHA-256 `95bfb426c802c0dacebb9d44586cf6deeef1aab5557e2c63ca5dff6f05edf64d`.
- Output: `DR2C_VORENYX_REPRODUCIBLE_SOURCE_PATCH_v2.55.zip`, 7,515,735 bytes, 274 entries, zero duplicate paths; 272 overlay paths, 269 Deathforth `.df` files, and 18 later-layer overrides.
- Reconciled artifact has exactly the same 274 member payloads as v2.53; the prior whole-ZIP hash difference came from archive metadata, not source payload changes.
- Test coverage: 7/7 source-reconciler tests and 6/6 provenance tests pass. Exact v2.47–v2.51 ZIPs and the v2.46 baseline remain unavailable, so this is NOT v2.51 integration. APK build/runtime remain unverified.
- See `docs/REPRODUCIBLE_SOURCE_PATCH_v2.55.md` and `audit/reproducible_source_patch_v2.55_summary.json`.

## Latest source-lineage gate — v2.54 audit (25 October 2026; not a game/APK version)

- Added `tools/audit_overlay_provenance.py` with unit tests for ZIP CRC/duplicate-path failures, source/overlay script counts, byte-level differences and explicit target paths. Hardened it to fail closed on ambiguous source roots and noncanonical dot-segment paths; total source-audit/reconciler coverage is 12 unit tests.
- The available v2.43 patch contains 269 `.df` payloads; all 269 differ byte-for-byte from the 509-script base archive, with 240 base scripts lacking overlay payloads.
- All nine source paths named by the v2.51 Batch K report are present and byte-different in the available v2.43 overlay. Three paths described as newly added in v2.51 are already present in that v2.43 archive.
- Exact v2.46 baseline and v2.47–v2.51 ZIP bytes remain unavailable; v2.50 Batch J has no report/JSON in this PR change set. Source lineage is unresolved and must not be auto-merged.
- This is a provenance finding, not evidence of localization completeness or runtime stability. APK build/install/runtime, UI fit, gameplay and save/load remain unverified. See `docs/BATCH_K_PROVENANCE_RECONCILIATION_v2.54.md` and `audit/batch_k_provenance_v2.54.json`.

## Latest static contract gate — v2.53 (25 October 2026)

- Reconciled source-only patch SHA-256: 73c9f60cd1a88a6d121843f3bdc6304262d47c01b2cdc36237015b7d083583d7; ZIP CRC PASS, 274 entries, 0 duplicate paths.
- Added strict checks for quoted-string closure in the overlay, ordered single-quoted Forth code-symbol sequence preservation, canonical Jack of All Trades perk key, and Start/tutorial dispatch contracts.
- Actual result across the supplied source: 269 overlay script files, 0 code-symbol sequence differences, 0 escaped backslash-quote regressions, canonical boot marker PASS, perk-key PASS, Start/tutorial dispatch tokens PASS. Six unit tests pass.
- This artifact is v2.43 + v2.45 corrective + v2.45 quote-fix, not v2.51 and not an APK. The actual v2.47–v2.51 ZIP layers remain unavailable for byte-level reconciliation.
- APK build/sign/install/runtime and save/load remain untested. See the v2.53 source contract gate, audit JSON, and reconciliation tool.

## Source-to-build reconciliation gate — 25 October 2026

- Batch K v2.51 is the latest documented localization pass, but its actual patch ZIP was not available for byte-level inspection in this execution. Treat its reported count of 77/509 scripts as a source report, not a translation-coverage percentage.
- A reproducible source patch was independently reconciled from the available base source archive, v2.43 overlay, v2.45 corrective patch, and v2.45 Start quote-fix patch. It contains 269 Deathforth script payloads across 272 normalized overlay paths. This differs from the Batch K report's 77-script figure; the exact newer archive and its counting definition must be checked before declaring the two inventories equivalent.
- The reconciled source patch SHA-256 is `faebba3ee0d14dd0cee668fe132fa95c8ba21f08963f627f59e5364c02658c0f`. Its ZIP CRC, duplicate-path check, canonical GAME-MARKER check, and escaped-quote scan passed. Four unit tests for the new reconciliation tool passed.
- This artifact is a v2.43 + v2.45 corrective + v2.45 quote-fix source patch. It is **not v2.51 and not an APK**. The base APK/source archives and binary overlay remain outside the public repository.
- APK build and runtime remain blocked/unverified: `apksigner`, `zipalign`, `apktool`, and `adb` are unavailable in the current environment. No claim is made that Start, UI layout, branding, save/load, or gameplay stability is fixed.
- See [source reconciliation gate](docs/SOURCE_RECONCILIATION_GATE_v2.52.md), [reconciliation audit JSON](audit/source_reconciliation_v2.52.json), and [reconciliation tool](tools/reconcile_overlay.py).

## Post-install result: v2.44 symptoms unchanged

- User reports Start still does not trigger, UI remains misaligned, and APKVISION branding remains.
- Static file inspection confirms the boot marker and landscape manifest edits exist in the v2.44 APK, but the phone may still be running the old APKVISION package: v2.44 uses the same package ID but a different local signing certificate, so Android cannot update an install signed by another key.
- Do not label the hotfix as fixed. Installer output and a new post-install recording are needed to distinguish an installation conflict from remaining runtime faults.
- [Post-install diagnosis](docs/POST_INSTALL_DIAGNOSIS_v2.44.md)

## v2.47 localization batches A–F — source patch

- Applied 38 initial static choice/location labels and 275 additional operations covering trade narratives, weapon/item descriptions, forecast vocabulary, character/weapon hints and selected encounters. Total: **313 operations / 325 literal occurrences** across eight scripts.
- Static validation: non-string token streams and choice-handler sequences match v2.46 baseline in all eight files; no unclosed strings in the lightweight lexer; no escaped double quotes remain. Patch ZIP CRC PASS; no duplicate paths.
- Patch SHA-256: `08731efd0d451332a7d0af5f4587d7bc524f291d4700c720cf483d230a0158cc` (69,656 bytes).
- Residual scan covered all 509 scripts and returned 397 heuristic candidates / 159 P1 review candidates. These are not confirmed untranslated UI strings or a localization percentage.
- **No APK rebuilt**: matching v2.46 test signing key is absent; a new key would conflict with in-place update. Device runtime and the actual Deathforth interpreter are not tested.
- [Full v2.47 batch report](docs/LOCALIZATION_BATCH_ABCDEF_v2.47.md) · [Machine-readable audit](audit/localization_batch_abcdef_v2.47.json)

## v2.49 Batch I — gameplay and encounter localization

- Added 203 translation operations across 14 previously uncovered scripts: RPG class descriptions and choices, toilet/zombie-line/drag-race events, gym/chess scenes, alien/anime rare locations, bandit encounters, recruit CYOA options, and weapon/trader descriptions.
- Cumulative source overlay now contains 73 of 509 `.df` scripts. Static checks: 0 quote-parity failures, 0 escaped-double-quote regressions, 0 executable-skeleton differences, 0 unmatched mapping keys. ZIP CRC PASS; 77 entries, no duplicates.
- Source-only patch. No APK was rebuilt and no device-side runtime test was performed. Some dynamic sentences remain English when their grammar depends on a placeholder across literal boundaries; translating only one fragment would be incorrect.
- [Batch I report](docs/LOCALIZATION_BATCH_I_v2.49.md) · [Validation JSON](audit/localization_batch_i_v2.49.json)

## v2.51 Batch K — character, encounter and endgame localization

- Applies 206 curated translation/template records across 9 scripts, affecting 211 literal occurrences. Three new active overlays were added: Sasquatch encounter, Santa blurbs, and Cupid blurbs.
- Additional fixes cover cemetery/Dracula/mausoleum events, mad scientist and ninja scenes, gym strings, Johnny encounter, and end-of-road completion/streak/credits.
- Cumulative overlay: 77 of 509 source `.df` scripts. Static checks: 0 lexical errors, 0 escaped-quote regressions, 0 executable-skeleton differences, 0 handler-sequence differences, 0 unexpected missing mapping keys. ZIP CRC PASS; 85 entries; no duplicates.
- ZIP SHA-256: `e265c7d2789e6936aadea49a42c4b5c87799c202945f8cfa4bee7291a8a40046`.
- Source patch only; no APK built or device test. Global localization remains incomplete.
- [Batch K report](docs/LOCALIZATION_BATCH_K_v2.51.md) · [Validation JSON](audit/localization_batch_k_v2.51.json)

## v2.48 Batch H — residual event localization

- Cumulative source overlay now contains 59 script files, including prior batches A–G and new Batch H edits. Batch H touches 39 files: 37 literal-map files plus display-template refactors.
- 258 change records cover 283 literal occurrences. Main targets include toilet/shower and gym events, rare-location narration, character flavor text, arcade encounters, trainer-camp actions, and assorted trade/event responses.
- Static checks: 0 odd-quote files, 0 escaped-double-quote patterns across the 59-file cumulative overlay, 0 handler ID/order differences, and 0 executable-skeleton differences outside string/display-template regions. ZIP CRC PASS; 61 entries, 0 duplicate paths.
- The 49-entry v2.47 seed P1 review queue has 0 exact candidate phrases remaining in the cumulative source after application and filtering comment/disabled-code false positives. This is not a claim that all game text is Indonesian; new English remains outside that seed queue.
- Source patch only; no APK build or device runtime test. [Batch H report](docs/LOCALIZATION_BATCH_H_v2.48.md).

## v2.46 English residual multi-analysis

- Baseline: `DR2C_VORENYX_v2.46_UI_LOCALIZED_TEST.apk`, SHA-256 `6d4e2f3df07d199807c08418ae5d30b9927e5b2e36c780a51858045336b29313`. Static scan covers all 509 packaged `.df` scripts.
- Extraction detected 3,624 display templates and 9,890 standalone literals. Candidate scoring ranked 443 high-confidence player-facing candidates (P1), 55 medium (P2), 199 short labels/titles/shouts, and 677 unique normalized phrases. These are triage counts, not semantic coverage or a claim that every candidate appears during gameplay.
- Biggest residual hotspot: `events/trade/oldtrade.df` (76 P1 candidates), especially weapon trade descriptions, gas/ammo, medical supplies and robbery outcomes. Other targets: `events/common/PANCREAS.df`, `events/trade/rare.df`, `events/city/region/special-lots.df`, and `events/locationlogic.df`.
- The native scan found 3,332 English-like ASCII strings: 2,035 in `libmain.so`, 576 in `libSDL2_image.so`, 527 in `libSDL2.so`, and smaller counts in mixer/PairIP/codec libraries. These are not all player-facing text; engine diagnostics, error messages, identifiers and third-party middleware must not be blindly translated.
- False-positive patterns include internal/log tokens such as `DAY-PICK-DECK5 RECRUIT`, `old-total-kills:`, and `door-no-escape`. Dynamic templates require their character/group placeholders and markup to remain intact.
- A curated next-wave review queue has 38 candidate translations for static location labels, simple trade choices and forecast labels. It is a review queue, not yet applied to the APK.
- Runtime validation of v2.46 on the user's device remains unconfirmed.

See the detailed report in `docs/ENGLISH_RESIDUAL_MULTIANALYSIS_v2.46.md` and the CSV review queue shared with the conversation artifacts.

## v2.46 screenshot-driven UI localization

- Targets the English/mixed-language text seen in the user's latest screenshots: tutorial CYOA choices and prose, plus Team, Swap Meet, Choose UR Fate, and 10 character-stat labels in native `libmain.so`.
- Tutorial choices are now Indonesian and use the dynamic character name. Existing `tutorchat-1/-2/-3` handlers remain intact.
- Native labels are patched in-place, preserving string offsets and native library size. Static checks cover 13 standalone string slots.
- APK: `DR2C_VORENYX_v2.46_UI_LOCALIZED_TEST.apk`, 112,238,801 bytes, SHA-256 `6d4e2f3df07d199807c08418ae5d30b9927e5b2e36c780a51858045336b29313`.
- ZIP CRC, v1 signature check, local v2 verification, resource table alignment, stored-entry alignment, and native library page alignment pass. No device-side runtime test yet; localization remains incomplete and native stat behavior needs regression check.
- [UI localization report](docs/UI_LOCALIZATION_v2.46.md) · [Machine-readable validation](audit/ui_localization_v2.46.json)

## v2.45 Start failure — Deathforth string syntax fix

- The user's runtime console revealed a concrete parse error at `events/common/common4.df:34`: escaped quotes in translated text caused the Deathforth interpreter to parse the string incorrectly and report `Dari` as an unknown token.
- Replaced all 24 C/JSON-style escaped double-quote sequences in six script files with apostrophes inside the outer display strings. A scan of all 509 scripts embedded in the new APK found zero remaining escaped-quote sequences.
- New diagnostic APK: `DR2C_VORENYX_v2.45_STARTFIX_TEST.apk`, 112,238,861 bytes, SHA-256 `f3199c9aa28ee49889ba536e0fbbe6cdaa4d37ea9e6db48a2668001896210cc5`. ZIP CRC and local v1/v2 signature checks pass; no Android-device runtime test yet.
- The new APK retains diagnostic console output to reveal subsequent script errors. It uses the same local test certificate as the previous STARTDIAG candidate, not the publisher certificate.
- [Quote-parse fix report](docs/DEATHFORTH_QUOTE_FIX_v2.45.md) · [Machine-readable audit](audit/startfix_quote_fix_v2.45.json)

## v2.45 Start diagnostic APK — isolate tap, dispatch, and boot-state path

- The original `main-event-do-select` / `select-boot` route exists in the package, and the localization overlay did not remove or rewrite the dispatch handler. Static analysis alone cannot determine whether a touch reaches the native callback, whether the deferred script handler is registered at runtime, or whether `select-boot` aborts on state/mode/tutorial loading.
- A diagnostic-only APK enables the in-game console and adds checkpoints in `boot.df`, `events.df`, and `game-select.df`. It distinguishes: boot did not complete; no select event dispatched on tap; event dispatch but no select callback; or a stop in save/mode/tutorial loading.
- Local artifact: `DR2C_VORENYX_v2.45_STARTDIAG_TEST.apk`, 112,238,856 bytes, SHA-256 `0bdb268aa1da2d70188f3a291f1c0591a195266fa3edec3376c86ca83527c26c`. ZIP CRC and local v1/v2 checks pass; target-device install has not been tested. This is not a release build.
- [Start diagnostic build guide](docs/START_DIAGNOSTIC_BUILD_v2.45.md) · [Machine-readable validation](audit/startdiag_v2.45.json)

## v2.45 APK package-parse error correction — page-aligned test build

- Follow-up analysis of the user-observed Android “Ada masalah saat mengurai paket” error found a concrete packaging defect: seven uncompressed native `.so` payloads were only 4-byte aligned even though the manifest declares `extractNativeLibs=false`. The original base has those payloads aligned to 4,096-byte boundaries.
- A replacement local candidate now aligns all seven native library payloads to 4,096-byte boundaries, then verifies ZIP CRC, JAR/v1 signature, APK v2 signature and content digest, and binary manifest chunk structure.
- Local artifact: `DR2C_VORENYX_v2.45_PAGEALIGNED_TEST.apk`; 112,237,647 bytes; SHA-256 `adbe5fff97ba43c670c640e648b4ccc9a9f55996840559665a791d16d06267e7`.
- **Not device-tested:** this fixes a confirmed packaging defect, but does not prove it was the only cause of the parse message. Local test signer differs from publisher key, and original license checks remain.
- [APK parse-error triage](docs/APK_PARSE_ERROR_TRIAGE_v2.45.md)

## v2.45 deep source repair candidate — static only

- A corrective source overlay was prepared for 12 scripts, addressing canonical trait/perk IDs, the `Jack of All Trades` definition key, a malformed translated trade-event string, recruit-screen perk labels, a candy-sharing choice label, and confirmation wording.
- Static checks: no unclosed string/block comment; no new normalized heuristic warnings; 60/60 canonical trait/perk keys preserved; 44 confirmation calls and 44 perk-preview calls use canonical IDs; CYOA, CYOA-choice, and CYOA-bridge identifiers match the source in covered files.
- Overlay scope: 269 of 509 source `.df` files. Full localization is not complete.
- This is a source-overlay candidate, not an APK. No rebuild, install, target-device gameplay, or save/load validation was performed. The previously reported viewport/touch and runtime symptoms remain unresolved pending actual-package testing.
- [Deep repair report](docs/DEEP_REPAIR_v2.45.md) · [Machine-readable static validation](audit/static_validation_v2.45.json) · [Executable-token audit](audit/executable_token_audit_v2.45.json) · [APK baseline integrity audit](audit/apk_baseline_integrity_v2.45.json) · [Choice-handler audit](audit/choice_handler_audit_v2.45.json)

## v2.44 Start/UI hotfix candidate

- Restored the canonical Forth module marker in assets/deathforth/boot.df: "PENANDA-GAME" $anew → "GAME-MARKER" $anew. This is an internal marker, not UI copy; its rename was a genuine identifier mismatch. The correction is static-verified, but whether it caused the Start failure still requires device testing.
- Forced SplashActivity and DrtcGameActivity to fixed landscape (manifest value 0) to address the recording’s portrait letterboxing and clipped right-side settings controls.
- Static Start-path checks pass: main-event select defer, handler registration, select-start registration, tutorial file existence, and menu/tutorial routing.
- Local APK candidate: DR2C_VORENYX_v2.44_START_UI_HOTFIX.apk, 39,748,341 bytes, SHA-256 e28314611411aeba2fdd6bf2cee918fa64ddecac159536e4a39918e7af81f8a6. ZIP CRC PASS, 1,015 entries, 272 overlay payloads verified, no duplicate paths, v1/v2/v3 signature checks PASS.
- Runtime Start behavior, layout fit, save/load, installation and stability are NOT TESTED. This is a hotfix candidate, not a verified stable release.
- The VORENYX splash artwork itself has no APKVISION logo, but APKVISION namespaces remain in classes3.dex and libstub.so from the supplied repackaged base. This hotfix does not remove the third-party wrapper/provenance layer; an authorized clean base APK is needed for a clean no-APKVISION build.
- Original publisher signing key is unavailable; the local key certificate SHA-256 is 6ea04e10965de1459a7fee845e8ae903bc1535a744f4762c14b2c7bb82eb13f9. PairIP/Play checks may reject the local signing certificate.
## v2.43 targeted residual pass

- Changed **159 quoted-string occurrences across 58 overlay files**, including **9 files newly added to the overlay** for selected visible character emotes, event instructions, trade/mall signs, and dialogue.
- Static checks: line/token counts preserved; non-string code skeleton and resource paths unchanged; zero unmatched mapping rules.
- Patch ZIP: 444 entries / 443 manifest records; CRC PASS, zero hash failures and duplicates. SHA-256: `00ff7866242e8b3aca4fc749e93455ba1c795c4eec99fd15baa07ab483aca024`.
- Local project archive v2.8: 472 entries / 471 checksum records; CRC PASS, zero checksum failures. SHA-256: `417d8256a74ad6ed64072c93fd1e9b9f255cdb7bca41c49c96333fba6a569cd5`.
- Heuristic recheck of the inherited 598-row queue: 131 active candidate rows remain after v2.43, down from 241 after v2.42 (120 exact literals in overlay files; 11 rows in files without overlays). This is triage, not a confirmed untranslated-text count.
- Global semantic/player-visible coverage remains **NOT COMPUTED**. A local v2.43 APK candidate is assembled and verified with signature schemes v1/v2/v3; Android install/launch, gameplay, UI fit and save/load remain untested. The APK is not runtime-confirmed stable and stays local-only.

## v2.42 targeted residual pass

- Extended the localization overlay across 16 files covering selected character banter, epilogue outcomes, finale mode/credits, ringmaster/healer dialogue, Canada-crossing NPC chatter, Santa/Evil Santa, gnome trader, farm/car encounters, and mission text.
- **309 literal occurrences changed**; zero unmatched mapping rules. Line counts, string-token counts, non-string code, and resource paths were preserved.
- Patch ZIP: 431 entries / 430 manifest records; CRC PASS, zero hash failures, zero unmanifested paths, zero duplicates. SHA-256: `e47f397d9c3908a9e370ef98aeb21bf091d66af7eb839a0fb022a9350cb4f4cd`.
- Local archive v2.7: 459 entries / 458 checksum records; CRC PASS and no checksum failures. SHA-256: `cb372f6cacce151a0f1eec545d1a29ef2a523cb92fa7d4f7e40b9157468ebcfb`.
- Global semantic/player-visible coverage remains **NOT COMPUTED**. Gameplay/runtime, UI fit/overflow, save/load, and device tests were not run; APK rebuild/signing was not performed.
- Binary patch, full archive, and detailed string ledger stay local. Public GitHub contains documentation and sanitized audit metadata only.

## v2.41 targeted remediation pass

- Added localized strings for 15 previously unoverlaid character-banter modules, ending/credits, human combat barks, and high-priority CYOA headings/choices.
- Corrected the displayed perk label `Shotgunner` to `Ahli Shotgun`; the canonical game-state key is unchanged.
- Static pass: **453 literal occurrences across 24 files**. Line counts, non-string code, and resource path literals were preserved.
- The local v2.41 patch ZIP has 429 entries / 428 manifest entries; CRC PASS, zero manifest hash failures, zero duplicate paths. SHA-256: `e2d965d64d566c2f5eb516b2e2b6500c472ba354b4534d95a7fc488bcbdc4bf1`.
- Local project archive v2.6: 457 entries; checksum manifest verifies all 456 other files. SHA-256: `20be915f19c9d3b7d800e1e179c1430f067bb72a6d194d0a3a5344ec64282f9f`.
- Global semantic/player-visible coverage remains **NOT COMPUTED**. Runtime gameplay, UI fit/overflow, save/load, and APK rebuild/signing were not performed.
- Public GitHub contains docs and sanitized audit metadata only; patch ZIP and project archive remain local-only artifacts.

## v2.40 checkpoint

- Repaired **45 trait/perk machine-key mismatches** from v2.39 across 13 modules; the post-repair audit found **0 remaining mismatches across 195 operand comparisons**.
- Routed trait/perk labels through the display localization helper and added missing display mappings.
- Continued localization across CYOA guidance, journey/camp text, NPC banter, reward text, comic/magazine choices, medical feedback, event narration, and combat tutorials. Updated the title-art badge to V2.40.
- Static control-flow checks: CYOA/choice IDs preserved; route/resource path literals preserved.
- A fresh comment-aware inventory scanned **541 .df/.txt files** and indexed **16,834 active quoted literals**. The inherited queue is stale/non-exhaustive: the fresh scan flags **1,578 English-likelihood rows** at threshold ≥0.2 plus **305 new/changed unscored literals** for triage (**1,883 rows across 196 files**). These are review candidates, not confirmed untranslated expressions.
- A machine-audit non-flagged proxy of **88.11%–94.30%** is available for triage only; it is **not** a localization-coverage percentage. Global semantic/player-visible coverage is **NOT COMPUTED**. The historical v2.22 figure of 69.07% is stale and must not be used as v2.40 coverage.

## Historical v2.40 build integrity

- Patch ZIP: **24,380,609 bytes**; SHA-256 `a863cadfda4d99ef14c9199e255cbfc8e687c1d05a1853b8f461f096870b26eb`; 411 entries; 410 manifest entries; CRC PASS; zero manifest hash failures; zero duplicate paths; zero machine-local path leaks.
- Full project archive v2.5: **105,064,456 bytes**; SHA-256 `cc0e7818dd87f0fe508692ae0545343ad89c727c401c81ad00f703377962fa97`; 185 entries; 184 manifest entries; CRC PASS; zero manifest hash failures; zero unmanifested files; zero duplicate paths.
- The binary patch and full source archive are **not hosted in this public repository**. SHA-256 sidecars accompany the local release artifacts.

## Tests not performed

Runtime gameplay/event-path, actual UI fit/overflow, save/load, Android install and launch tests are **NOT RUN**. The v2.44 candidate has static marker/orientation and v1/v2/v3 signature checks, but Start behavior has not been tested on-device and PairIP/Play checks may reject its local certificate. Static package integrity does not prove runtime stability.

## Project records

- [Canonical project memory](PROJECT_MEMORY.md)
- [Version changelog](CHANGELOG.md)
- [v2.44 hotfix checkpoint](docs/CHECKPOINT_v2.44.md)
- [v2.44 APK hotfix report](docs/APK_BUILD_v2.44.md)
- [v2.44 sanitized hotfix audit](audit/v2.44_start_ui_hotfix.json)
- [v2.43 checkpoint](docs/CHECKPOINT_v2.43.md)
- [v2.43 APK build report](docs/APK_BUILD_v2.43.md)
- [v2.43 sanitized static-validation summary](audit/v2.43_static_validation_summary.json)
- [v2.43 heuristic residual recheck](audit/v2.43_residual_recheck.json)
- [v2.42 checkpoint](docs/CHECKPOINT_v2.42.md)
- [v2.43 sanitized static-validation summary](audit/v2.43_static_validation_summary.json)
- [v2.43 heuristic residual recheck](audit/v2.43_residual_recheck.json)
- [v2.42 sanitized static-validation summary](audit/v2.42_static_validation_summary.json)
- [v2.41 checkpoint](docs/CHECKPOINT_v2.41.md)
- [v2.42 sanitized static-validation summary](audit/v2.42_static_validation_summary.json)
- [v2.41 sanitized static-validation summary](audit/v2.41_static_validation_summary.json)
- [v2.40 checkpoint](docs/CHECKPOINT_v2.40.md)
- [Build and validation details](docs/BUILD_AND_VALIDATION.md)
- [Indonesian localization guide](docs/LOKALISASI_ID.md)
- [Slang research and evidence](docs/SLANG_RESEARCH_AND_EVIDENCE.md)
- [Coverage summary](audit/coverage.json)
- [Static validation report](audit/validation_report.json)
- [v2.40 coverage recheck](docs/COVERAGE_RECHECK_v2.40.md)
- [Untouched and ambiguous surface audit](docs/UNTOUCHED_AMBIGUOUS_AUDIT_v2.40.md)
- [Untouched surface review metrics](audit/v2.40_source_coverage_review.json)
- [v2.40 fresh coverage metrics](audit/v2.40_coverage_recheck.json)
- [v2.41 sanitized static-validation summary](audit/v2.41_static_validation_summary.json)
- [v2.40 sanitized integrity summary](audit/v2.40_integrity_summary.json)
- [v2.40 localization summary](audit/v2.40_localization_summary.json)
- [Version history](audit/version_history.json)

Public GitHub contains project-authored documentation and sanitized audit metadata only. Do not commit the original APK/archive, complete extracted scripts, literal inventory, or binary overlay.

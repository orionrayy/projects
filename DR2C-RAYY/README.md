# DR2C VORENYX — Indonesian Localization

**Latest candidate: v2.45 corrective source overlay · static checks PASS · APK/runtime NOT VERIFIED · Full localization NOT COMPLETE**

DR2C VORENYX is a fan-made Indonesian localization/data-overlay project for *Death Road to Canada*. The target is natural, context-aware Indonesian with distinct character voices and blunt sarcasm. Original campaign flow, machine identifiers, branch conditions, route IDs, and game-state effects are invariants.

## Post-install result: v2.44 symptoms unchanged

- User reports Start still does not trigger, UI remains misaligned, and APKVISION branding remains.
- Static file inspection confirms the boot marker and landscape manifest edits exist in the v2.44 APK, but the phone may still be running the old APKVISION package: v2.44 uses the same package ID but a different local signing certificate, so Android cannot update an install signed by another key.
- Do not label the hotfix as fixed. Installer output and a new post-install recording are needed to distinguish an installation conflict from remaining runtime faults.
- [Post-install diagnosis](docs/POST_INSTALL_DIAGNOSIS_v2.44.md)

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

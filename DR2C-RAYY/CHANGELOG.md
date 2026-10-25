# Changelog

## v2.62 APK change-surface audit — 25 October 2026 (audit only, not a game/APK version)
- Added tools/audit_apk_change_surface.py with checks for ZIP CRC/duplicate paths, expected package entry additions/removals, byte-level payload differences, DEX identity and native label-string-slot boundaries.
- Added five regression tests covering expected package changes, DEX-change rejection, non-ASCII native diffs, unexpected added paths and duplicate paths.
- Actual comparison: 1,014 base entries, 1,015 candidate entries, 1,012 common; 737 identical common entries and 275 changed. Changed common paths comprise 269 Deathforth .df scripts and six expected non-script paths. No unexpected package-entry changes.
- All three DEX files are byte-identical. Only two libmain.so files differ among native libraries; each has 89 changed bytes in 13 ASCII label slots and identical file size. Other native libraries remain identical.
- This is static diff evidence only; Start, licensing/runtime outcome, gameplay, UI fit and save/load remain NOT TESTED. PR stays draft.
- See docs/APK_CHANGE_SURFACE_AUDIT_v2.62.md and audit/apk_change_surface_v2.62.json.



## v2.61 source-to-APK payload reconciliation — 25 October 2026 (audit/supplement, not a game/APK version)
- Added tools/audit_apk_source_sync.py. The checker verifies base-source-to-base-APK byte parity, applies ordered overlay layers, rejects duplicate or malformed archive paths, checks ZIP CRCs, and compares every effective Deathforth script with the candidate APK.
- Added six source-sync regression tests (presentation-only sync, code drift, source-base mismatch, missing candidate script, duplicate ZIP path, and malformed overlay path) and extended CI compilation to all Start/source audit tools.
- Actual artifacts: base source archive and base APK match 509/509 scripts. With available v2.43, v2.45 corrective and v2.45 Startfix layers, 508/509 candidate script payloads matched; the only drift was assets/deathforth/events/tutorial.df.
- Created local-only one-file source-sync supplement from the candidate's exact tutorial payload. With that layer applied, the checker passes 509/509 scripts, 0 missing, 0 extra, 0 mismatches; CRC passes and duplicate paths are zero across all inputs.
- Confirmed the Library-named v2.58_ANDROID11_SIGNATURE_FIX APK and v2.57 signature-fix candidate are byte-identical, SHA-256 a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7.
- Limits: exact v2.47–v2.51 patch ZIPs and the distinct v2.58 localization candidate remain unavailable. This does not establish full localization integration or runtime stability. Start/install/gameplay/UI/save-load remain NOT TESTED; PR remains draft.
- Report: docs/APK_SOURCE_SYNC_AUDIT_v2.61.md. Sanitized result: audit/apk_source_sync_v2.61.json.


## v2.60 engineering audit — 25 October 2026 (not a game/APK version)
- Added tools/audit_apk_start_path.py to compare the provided base APK against a candidate APK using ZIP CRC/duplicate checks, all 12 Start/tutorial route files, normalized code-token streams, handler identifiers, string closure, escaped-quote scanning and the canonical boot marker.
- Added six regression tests for presentation-only translation, dynamic identifier drift, required-handler loss, missing route files, duplicate ZIP paths and code-token deltas independent of string text.
- Exact comparison: base APK hash d4b509d899df572d80de553c8545c850ff2122c2d99fae5cfad2532159d35c15; candidate hash a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7. ZIP CRC passes for both, no duplicate paths, 12 route scripts present, 11 strict static passes, and one tutorial code-token drift remains for review.
- No runtime cause is claimed. The tutorial display-expression changes may be intentional Indonesian rewrites; Start, install, gameplay, UI fit, save/load and stability remain NOT TESTED. Not release-ready.
- See DR2C-RAYY/docs/APK_START_PATH_AUDIT_v2.60.md and DR2C-RAYY/audit/apk_start_path_v2.60.json.

 — DR2C VORENYX

## v2.57 Android 11 signature-fix derivative — 25 October 2026 (test only)

- Diagnosed why v2.57 failed to install even after the previous package was removed: its manifest targets API 35 but the APK only had JAR/v1 signing. Android 11/API 30 requires v2+ for target API 30+ (official reference: https://developer.android.com/about/versions/11/behavior-changes-11).
- Produced a separate signature-fix derivative of v2.57, `DR2C_VORENYX_v2.57_SIGNATURE_FIX.apk`, SHA-256 `a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7`; it is not the v2.58 localization batch.
- JAR/v1 and local v2 cryptographic/layout verification pass; 1,015 ZIP entries, CRC PASS, no duplicates, DEX internal checksums pass, alignment failures 0. Official `apksigner` and device install/gameplay remain untested. New local signer; PairIP/license code unchanged.
- Details: `docs/APK_SIGNATURE_FIX_v2.57.md`.

## Local APK test candidate v2.58 — 25 October 2026 (not a release APK)

- Built `DR2C_VORENYX_v2.58_TEST_CANDIDATE.apk` with a curated 38-row next-wave localization queue: 41 literal occurrences across three scripts.
- Corrected “SIEGE ALERT!” from the semantically wrong “pengelompokan” to “pengepungan”.
- APK SHA-256: `11ddc0e41df162837f74c676d602403952c3f6c875f4f6dacd91db68adbb41b0`; 115,614,035 bytes; 1,015 entries; ZIP CRC PASS; no duplicate paths; 509 Deathforth scripts; 13/13 builder/localization tests pass.
- Native UI slots 26/26 pass; primary activities landscape; resource/stored-entry/native-library alignment checks pass; PairIP libraries are unchanged.
- JAR/v1 signature verifies; APK v2 signing was not generated or verified because `apksigner` is unavailable. A fresh local self-signed test certificate was used, not the installed/publisher signer.
- Source lineage remains incomplete: the actual v2.47 A–F patch, v2.48–v2.51 patch ZIPs and exact v2.46 baseline APK are still unavailable. Do not call this v2.51 integration.
- No Android install, Start-button, UI-fit, gameplay, event loading, save/load or runtime stability tests were run. This is not a release APK.
- See `docs/APK_CANDIDATE_BUILD_v2.58.md` and `audit/apk_candidate_v2.58_summary.json`.


## Local APK test candidate v2.57 — 25 October 2026 (not a release APK)

- Built `DR2C_VORENYX_v2.57_TEST_CANDIDATE.apk` from the available base + v2.43 overlay + v2.45 corrective + v2.45 Startfix layers.
- Updated 12 tutorial/CYOA display expressions with handler and ordered Forth symbol preservation, ported 13 documented native UI/stat label replacements to both ABIs, normalized primary activity orientation to landscape, and synchronized splash badge V0.3 to the title-art badge V2.43.
- Package gates: SHA-256 `ef66364da7e3d8862b460348d67d397e8132896aaa80f70a9243589d934435e5`; 115,614,035 bytes; 1,015 entries; CRC PASS; 509 .df scripts; no escaped quote regressions or duplicate ZIP paths; resources.arsc and stored-entry alignment checks PASS; 26/26 native slots PASS.
- JAR/v1 test signature verifies; APK v2 signature not generated/verified because `apksigner` is unavailable. PairIP libs preserved byte-for-byte. Binary `apkvision` wrapper identifiers remain in DEX and `libstub.so`; wrapper removal was not attempted.
- Local builder tests: 8/8 PASS. Device install, Start button, UI fit, game flow, save/load and runtime stability NOT TESTED. The exact v2.46 APK and actual v2.47–v2.51 ZIPs remain unavailable, so no v2.51 integration is claimed.
- See `docs/APK_CANDIDATE_BUILD_v2.57.md` and `audit/apk_candidate_v2.57_summary.json`.


## Start-route static audit v2.56 — 25 October 2026 (not a game/APK version)

- Added `tools/audit_start_route.py` and three unit tests for localized display strings, missing Start tokens, and executable skeleton drift.
- Static audit of 12 route-related scripts: 12/12 pass; preserved route-code skeleton and ordered Forth symbol stream for the key overlaid route files; required Start/tutorial tokens are present.
- `boot.df` localization helper and READY → SIAP label are present; canonical boot marker and Forth symbol stream remain preserved.
- No full Deathforth parse or APK/runtime testing. Start-button reachability, touch input, UI fit, gameplay and save/load remain unverified. The patch is still not v2.51.
- See `docs/START_ROUTE_STATIC_AUDIT_v2.56.md` and `audit/start_route_static_contract_v2.56.json`.


## Reproducible source packaging v2.55 — 25 October 2026 (not a game/APK version)

- Root cause of the prior v2.53 rebuild hash mismatch was ZIP metadata: the 274 member payloads were byte-identical, but timestamps/default file modes differed.
- Updated `tools/reconcile_overlay.py` to normalize entry timestamps and Unix file modes; added a regression test that builds the same inputs twice and asserts archive bytes and SHA-256 match.
- Rebuilt the available base + v2.43 + v2.45 corrective + v2.45 Startfix layers three times. All outputs matched SHA-256 `95bfb426c802c0dacebb9d44586cf6deeef1aab5557e2c63ca5dff6f05edf64d`.
- Local tests: 7 source-reconciler + 6 provenance = 13/13 PASS. Output remains a source patch, not an APK and not v2.51. Runtime, UI fit, Start input and save/load remain untested.
- See `docs/REPRODUCIBLE_SOURCE_PATCH_v2.55.md` and `audit/reproducible_source_patch_v2.55_summary.json`.


## Source provenance audit v2.54 — 25 October 2026 (not a game/APK version)

- Added a standard-library-only byte-level provenance auditor and unit tests; the CI workflow compiles it and discovers both audit/reconciliation test suites. Hardened path validation to reject ambiguous Deathforth roots and noncanonical dot segments. The two suites contain 12 tests.
- Independently compared the available base archive and v2.43 overlay: 509 base `.df` scripts, 269 overlay payloads, 269/269 matching paths byte-different, 240 base scripts without overlay payload, and zero overlay paths missing from base.
- The nine target paths listed by Batch K v2.51 are all present and byte-different in the available v2.43 archive. This includes three files described by Batch K metadata as newly added.
- Rechecked 299 Library ZIP artifacts: the actual v2.47–v2.51 ZIPs are absent (the v2.47 checksum sidecar exists separately); the reported v2.46 APK is not available as a file, and no v2.50 Batch J report is in the current PR change set. Result: **lineage unresolved; do not auto-merge or make release claims**.
- No APK was built or runtime-tested. See `docs/BATCH_K_PROVENANCE_RECONCILIATION_v2.54.md` and `audit/batch_k_provenance_v2.54.json`.

## Source contract gate v2.53 — 25 October 2026 (not a game/APK version)

- Extended tools/reconcile_overlay.py to preserve and compare the ordered stream of single-quoted Forth code symbols across source and each overlaid script. Also checks overlay string closure, canonical perk key, and critical Start/tutorial route tokens.
- Reconciled base + v2.43 localization patch + v2.45 corrective patch + v2.45 Start quote-fix. Output: DR2C_VORENYX_v2.45_RECONCILED_SOURCE_PATCH_v2.53.zip, SHA-256 73c9f60cd1a88a6d121843f3bdc6304262d47c01b2cdc36237015b7d083583d7; ZIP CRC PASS, no duplicates, 272 payload paths including 269 .df scripts, 18 later-layer overrides.
- Checks: 0 escaped quote regressions; 0 unclosed strings in overlay .df files; 0 single-quoted code-symbol sequence differences; canonical GAME-MARKER, Jack of All Trades key, Start dispatch and tutorial route contracts PASS. Unit tests increased from 4 to 6; all six pass locally.
- This is a source-only v2.43 + v2.45 patch; not v2.51 and not an APK. v2.47–v2.51 ZIP artifacts remain unavailable for byte-level integration. APK build and device runtime remain untested.
- See docs/SOURCE_RECONCILIATION_GATE_v2.53.md and audit/source_reconciliation_v2.53.json.

## Source reconciliation checkpoint — 25 October 2026 (not a release version)

- Added `tools/reconcile_overlay.py` and four unit tests to reconcile ordered overlay layers with strict base SHA-256 pinning, ZIP CRC and duplicate-path checks, unsafe-path rejection, source-path validation, the canonical `GAME-MARKER` invariant, and escaped-quote scanning.
- Independently reconciled the available base source archive + v2.43 localization patch + v2.45 corrective source patch + v2.45 Start quote-fix source patch. Result: 272 overlay paths (269 Deathforth `.df` payloads), 18 later-layer path overrides, ZIP CRC PASS, no duplicate paths, canonical boot marker PASS, escaped-quote scan PASS; four unit tests PASS.
- Artifact SHA-256: `faebba3ee0d14dd0cee668fe132fa95c8ba21f08963f627f59e5364c02658c0f`. This is a normalized **v2.43 + v2.45** source patch, not v2.51 and not an APK.
- The actual v2.47–v2.51 binary patch ZIPs were unavailable for this execution, so the discrepancy between the v2.51 report's 77/509 script count and the available v2.43 ZIP's 269 `.df` payloads remains unresolved. Neither number is treated as a localization percentage.
- APK build/sign/install/runtime: NOT PERFORMED. The available environment lacks `apksigner`, `zipalign`, `apktool`, and `adb`. Do not label the project release-ready until the exact newer patch archive is reconciled and device-level Start/UI/gameplay/save-load tests pass.


- **v2.51 Batch K — character, encounter and endgame localization:** 206 curated translation/template records across 9 scripts (211 literal occurrences), including new Sasquatch/Santa/Cupid overlays, plus cemetery/Dracula, mad scientist, ninja, gym, Johnny, and endgame/credits strings. Cumulative overlay: 77/509 script files. Static checks: 0 lexical errors, escaped-quote regressions, executable-skeleton differences, handler-order differences, or unexpected missing mappings; ZIP CRC PASS, 85 entries, no duplicate paths. Source-only; no APK/device test. SHA-256: `e265c7d2789e6936aadea49a42c4b5c87799c202945f8cfa4bee7291a8a40046`. See [report](docs/LOCALIZATION_BATCH_K_v2.51.md).

- **v2.49 Batch I — gameplay and encounter localization:** 203 translation operations applied across 14 additional `.df` scripts, covering RPG class descriptions/options, toilet and drag-race scenes, gym/chess, alien/anime events, bandit encounters, recruit CYOA, and trader/weapon descriptions. Cumulative source overlay: 73/509 scripts. Static checks: 0 quote-parity failures, 0 escaped quote regressions, 0 executable-skeleton differences, 0 unmatched mappings; ZIP CRC PASS (77 entries, no duplicates). Source-only; no APK build/runtime test. See [report](docs/LOCALIZATION_BATCH_I_v2.49.md).

- **v2.48 Batch H residual event localization:** cumulative overlay contains 59 script files. Batch H touches 39 files and applies 258 change records across 283 literal occurrences, including toilet/shower, gym, rare-location, arcade, training, and miscellaneous encounter text. Static validation: 0 quote-parity warnings, 0 escaped double quotes in the cumulative overlay, 0 handler-order differences, 0 executable-skeleton differences; ZIP CRC PASS with 61 entries and no duplicates. All 49 exact candidates in the v2.47 seed P1 queue are resolved or filtered as comment/disabled-code false positives, but global localization remains incomplete. Source patch only; no APK/device test. See [report](docs/LOCALIZATION_BATCH_H_v2.48.md).

- **v2.47 localization batches A–F (source patch only):** 313 replacement operations / 325 literal occurrences applied across eight scripts; 38-row curated queue completed. Token streams and choice handlers match the v2.46 baseline; ZIP CRC passes. Residual heuristic scan found 159 P1 strings for human review among 509 scripts; not a confirmed UI count. No APK rebuilt because the v2.46 signing key is unavailable. See [report](docs/LOCALIZATION_BATCH_ABCDEF_v2.47.md).

- **v2.46 English residual multi-analysis:** scanned 509 scripts, extracted 3,624 dynamic templates and 9,890 standalone literals; ranked 443 P1, 55 P2 and 199 short-label candidates, with 677 unique normalized phrases. Highest-priority residual file is `events/trade/oldtrade.df` (76 P1), followed by character/weapon descriptions and location/event choices. Native scan yielded 3,332 English-like ASCII runs, mostly not player UI. A 38-row safe translation review queue was created but not yet applied. See [full report](docs/ENGLISH_RESIDUAL_MULTIANALYSIS_v2.46.md).

- **v2.46 screenshot-driven UI localization:** localized tutorial `tutorchat` choices/outcomes and native UI/stat labels `Team`, `Swap Meet`, `Choose UR Fate`, `strength`, `fitness`, `shooting`, `wits`, `attitude`, `composure`, `loyalty`, `morale`, `medical`, and `mechanical`. All six tutorial choice handlers remain present; 509 packaged scripts have no escaped-quote syntax regressions. APK CRC, v1 and local v2 checks pass; device runtime remains untested, localization incomplete. Artifact hash: `6d4e2f3df07d199807c08418ae5d30b9927e5b2e36c780a51858045336b29313`. See [report](docs/UI_LOCALIZATION_v2.46.md).

- **v2.45 Start script parse fix:** user's diagnostic console showed an interpreter error at `events/common/common4.df:34` due to C/JSON-style escaped quotes inside a Deathforth string. Replaced 24 escaped quote sequences across six scripts; all 509 packaged `.df` files scan with zero remaining. Built `DR2C_VORENYX_v2.45_STARTFIX_TEST.apk` (112,238,861 bytes, SHA-256 `f3199c9aa28ee49889ba536e0fbbe6cdaa4d37ea9e6db48a2668001896210cc5`). ZIP CRC and local v1/v2 verification pass; device runtime still awaits the user's re-test. Same local test cert as STARTDIAG, not publisher cert. See [report](docs/DEATHFORTH_QUOTE_FIX_v2.45.md).

- **v2.45 Start diagnostic build:** since layout correction has not restored Start behavior, created a diagnostic-only APK with in-game console checkpoints across boot, select-event dispatch, `select-boot`, save-state load, mode definitions and tutorial region loading. It does not presume an async race: marker output isolates native input/event delivery from missing deferred callback binding and script state/load stalls. APK is not a release build and has not been device-tested. See [guide](docs/START_DIAGNOSTIC_BUILD_v2.45.md).

- **v2.45 parse-error fix follow-up:** both prior candidates had `resources.arsc` stored but not 4-byte aligned (`offset % 4 = 1`) with target SDK 35. Android 11 officially rejects target-30+ apps with compressed or misaligned `resources.arsc`. New `DR2C_VORENYX_v2.45_PARSEFIX_TEST.apk` aligns all 260 stored entries to 4 bytes and all seven native libraries to 4,096 bytes; CRC, v1, and local v2 verification pass. Device install remains untested; certificate is local. SHA-256: `e727b5eb9f8314e312e1808acce5c11923265716a1ea2fb84638cca2d53530e6`. See [triage report](docs/APK_PARSE_ERROR_TRIAGE_v2.45.md).

- **v2.45 APK package-parse correction:** user reported Package Installer parsing error. Follow-up audit found seven uncompressed native libraries at 4-byte offsets while `extractNativeLibs=false` requires page-aligned libraries. A page-aligned candidate was rebuilt and passed ZIP CRC, JAR/v1, custom-verified v2 signature/content-digest, manifest-structure, and 4,096-byte native-offset checks. Device installation not yet re-tested; local test cert differs from publisher key. See [parse-error triage](docs/APK_PARSE_ERROR_TRIAGE_v2.45.md).

- **v2.45 corrective source overlay (static-only; follow-up validation):** corrected canonical trait/perk identifiers and the `Jack of All Trades` key; fixed the malformed `trade-medicalt` multiline string; repaired recruiter display labels and candy-sharing choice semantics; added a missing `T*S*T*C` display mapping. Validation: 0 unclosed string/comment errors, 0 new normalized heuristic warnings, canonical trait/perk keys 60/60 and display mapping coverage 60/60; CYOA IDs preserved in covered files. The executable-token heuristic found additions only in six files, with no token deletions/replacements detected. Source-only patch; APK rebuild, device/runtime, viewport/input mapping, and save/load are not verified. Localization remains incomplete (269/509 source `.df` files covered). See [deep repair report](docs/DEEP_REPAIR_v2.45.md), [validation JSON](audit/static_validation_v2.45.json), and [executable token audit](audit/executable_token_audit_v2.45.json).

- **v2.44 post-install status correction:** user reports all symptoms unchanged. Static marker/orientation edits exist, but runtime fix failed to verify. Same package ID + local signing certificate may prevent updating an APKVISION-signed installation, leaving the old app active. APKVISION wrapper remains. See [post-install diagnosis](docs/POST_INSTALL_DIAGNOSIS_v2.44.md). No stable-release claim.

- **v2.44 Start/UI hotfix candidate:** restored the internal boot marker GAME-MARKER (previously renamed PENANDA-GAME) and forced SplashActivity/DrtcGameActivity to fixed landscape. Static event/start-path checks and APK CRC/hash/alignment/signature validation PASS; Android Start behavior, UI layout, install, launch, save/load and stability NOT TESTED. APKVISION wrapper remains; an authorized clean base APK is required for a clean build. SHA-256: e28314611411aeba2fdd6bf2cee918fa64ddecac159536e4a39918e7af81f8a6.

- **v2.43 APK candidate (updated signing):** APK assembled locally, then verified using Android SDK Build Tools 35.0.1 apksigner; signature schemes v1/v2/v3 PASS. SHA-256 `3019dd04098e9e8fef01045a2e391d9525bf87ef6874b0d0049c5a073a052f25`. Static packaging PASS; Android install/launch/gameplay/UI/save-load/stability tests NOT RUN. Original publisher key absent and PairIP/Play license checks may reject the locally signed package. APK remains local-only. See [APK build report](docs/APK_BUILD_v2.43.md).

- **v2.43 APK candidate build:** assembled the v2.43 overlay into the supplied extracted Android package and applied a local JAR/v1 signature. Static package/manifest/hash/signature/ZIP/ABI checks PASS. Android install, launch, gameplay, UI fit, save/load and stability remain NOT TESTED; PairIP/Play license checks may reject re-signed package. APK remains local-only; see [APK build report](docs/APK_BUILD_v2.43.md).

- **v2.43:** localized 159 quoted-string occurrences across 58 files, including 9 newly overlaid modules. Static string/code/path checks passed, zero unmatched rules, local ZIP manifests validated. Recheck of the inherited 598-row heuristic queue shows 131 active candidate rows (down from 241 after v2.42); not a semantic coverage metric. Runtime not tested.

- **v2.42:** localized 309 quoted-string occurrences across 16 overlay files. Targeted residual cleanup covers selected character banter, epilogue/finale text, NPC dialogue, encounter choices, and mission labels. Line/string-token counts, non-string code, and resource paths preserved; zero unmatched rules; ZIP and manifest checks PASS. Global coverage not computed; runtime not tested.

- **v2.41:** localized 15 previously unoverlaid character-banter modules, ending/credits, human combat barks, and priority CYOA headings/choices; corrected the display-only `Shotgunner` label to `Ahli Shotgun` without changing the canonical key. 453 literal occurrences changed across 24 files. Static checks and local patch ZIP integrity passed; global coverage not computed; runtime not tested.

- **v2.40:** repaired 45 canonical trait/perk machine-key mismatches across 13 modules; 0 remain across 195 operand comparisons. Continued contextual Indonesian localization and refreshed the title badge. Static validation PASS; global semantic coverage not computed; runtime/UI/save-load/APK rebuild not tested.
- **v2.39:** localized 32 complete display expressions and 7 direct literal occurrences across CYOA examples and moment interactions. Static checks passed; runtime not tested.
- **v2.38:** localized 14 display expressions and 18 direct literal occurrences across 11 actual files. Static checks passed; runtime not tested.
- **v2.37:** localized 25 display expressions and 6 direct literal occurrences. Static checks passed; runtime not tested.


- **v2.36:** localized 45 complete display expressions and 12 direct literal occurrences across 31 modules. Focus: arcade-defense tutorial, bandit-defense rewards, bodybuilder/hero and siege encounters, shops/fairies/parks, city rangers and pandas, character blurbs, perk/trait help, and epilogue fragments. Static validation and package integrity PASS; triage queue now 77 rows in 36 files; global coverage not computed; runtime not tested.
- **v2.35:** 32 complete display expressions and 9 direct literal occurrences across 12 files; game modes, route planning, missions/rewards, gym/coffee/factory encounters, generator puzzle, broom/portal interactions, and Mountie Alpha-end text. Metadata reconciled for v2.34; static validation PASS; global coverage not computed; runtime not tested.
- **v2.34:** 25 complete display expressions and 3 direct literal occurrences across nine files: sewer/tutorial, Canada crossing, hazmat, Santa/Billy, common encounter, Bogan, daily medical CYOA, and special trader-camp items. Checkpoint/ZIP metadata reconciled in v2.35.
- **v2.33:** 31 display expressions and 9 direct literals across nine trader/DMV/junk-maker/character/graves modules. Static checks pass; global coverage not computed; runtime not tested.

- **v2.26:** contextual Indonesian localization for Beeman, Boxer, Caveman, Knight and Ninja dialogue/emotes across five files; 66 mappings and 66 occurrences; static structure PASS; coverage not remeasured; runtime not tested.
- **v2.25:** contextual Indonesian localization in the active optimistic-survivor profile and wrestler response profile; 63 mapping rules and 63 occurrences changed; both files preserve source line/token counts; ZIP CRC and manifest checks PASS; global coverage not remeasured; runtime not tested.
- **v2.24:** contextual Indonesian localization of character personality banter and shared chatter across seven files; 277 mapping rules; 279 literal occurrences changed; two father-topic word-order fixes; static structure, ZIP CRC, and manifest validation PASS; coverage not remeasured; runtime not tested.
- **v2.23:** contextual English-residue repair in `camp3.df`; 51 unique source literals and 52 literal occurrences localized; all 47 historical camp3 mapping misses repaired; two non-actionable historical rules reconciled. Coverage heuristic not recomputed; runtime not tested.

- **v0.1:** VORENYX title identity/artwork and initial UI/general text.
- **v0.2–v0.3:** literal maps, NPC style matrix, slang research and identifier protections.
- **v0.4–v0.7:** contextual event passes, bandits/recruitment/classes, common events and sentence-level QA.
- **v0.8–v1.8:** trader-camp, weapons vendors, trainers, contextual event and exact-literal/tab QA passes.
- **v1.9–v2.1:** Army Surplus, Rifle Collector, Blade Master and reconciled trainer/vendor localization.
- **v2.2:** fixes 15 player-visible English literals in weapon traders; targeted residue scan 0 matches; embedded static report and ZIP CRC PASS.
- **v2.3:** contextual survivor recruitment dialogue and sourced Indonesian voice/slang guide; static QA/ZIP CRC PASS.
- **v2.4–v2.20:** progressive contextual localization across events, characters, routes, traders, tutorial, camping, encounters, traits/perks and item text. Coverage values are heuristic inventory deltas.
- **v2.21:** quality-focused exact-context pass for UI, vehicle, city, vendor and perk/trait text; 92 rules and occurrences reported matched.
- **v2.22:** rewrites 94 complete display expressions in camp survival choices, character bio and selected encounters; 183 existing literal tokens changed and 138 inventory rows newly marked. Inventory heuristic is 69.07%. Static structure and ZIP CRC PASS; 49 exact mapping rules are recorded as missed after contextual rewrites and require reconciliation. Runtime/save-load/APK rebuild not tested.

## Status limits
Full Indonesian localization is incomplete. Inventory percentages are not semantic or runtime screen coverage. The public repository contains documentation and sanitized audit summaries, not the original APK, extracted game scripts or binary overlay.

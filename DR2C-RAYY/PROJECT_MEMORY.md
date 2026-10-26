# PROJECT_MEMORY — DR2C VORENYX

## Canonical identity
- Base game: Death Road to Canada. Project name: DR2C VORENYX.
- Current scope: Indonesian localization and replacement title identity; larger expansions remain deferred.
- Invariant: preserve the original Canada-bound campaign flow.
- Target voice: natural colloquial Indonesian, blunt and sarcastic with occasional profanity, distinct NPC personas, and context-sensitive community slang.
- Target: 100% of player-visible text reviewed and localized; **not achieved yet**.

## Historical checkpoint — v2.26 (24 October 2026)
- Local patch artifact: `DR2C_VORENYX_ID_v2.26_localization_patch.zip`. The binary overlay and original archive remain outside public GitHub.
- Scope: five special-character dialogue/emote profiles: `sc/beeman.df`, `sc/boxer.df`, `sc/caveman.df`, `sc/knight.df`, and `sc/ninja.df`.
- 66 exact-context mappings applied; 66 literal occurrences changed.
- The batch gives Beeman an encouraging casual voice, Boxer concise training banter, Caveman blunt time-travel humor, Knight a restrained chivalric register, and Ninja concise action/emote descriptions.
- Static structure: PASS. Token counts and line counts remain unchanged in all five files, non-string source skeletons match, and no mapped English source residues remain.
- Package: 312 ZIP entries; CRC PASS; no duplicate paths; 311 manifest-listed files verified with zero hash mismatches; no machine-local path leaks.
- Artifact SHA-256: `edda11648c4f7ed32d1413b154fd70e65943edfb367f18c6bffa0b5119a3f02c`.
- Coverage: 69.07% is the last measured heuristic from v2.22. No current global coverage measurement has been made for v2.26. It is not a semantic or runtime screen-coverage score.
- Runtime gameplay, UI fit, save/load, and APK rebuild/signing: NOT RUN / NOT PERFORMED.

## Coverage interpretation
Inventory percentages are heuristic. The denominator may contain fragments, identifiers or code-like strings, while a single displayed sentence can span multiple literal tokens. A 100% claim requires classifying candidates, reviewing complete assembled player-visible expressions, checking placeholders and UI fit, and testing runtime surfaces.

## Voice and slang policy
- Prefer natural sentence-level Indonesian over literal token substitution.
- Use `gue/lo`, `gak`, `udah`, and profanity selectively according to speaker/persona.
- Preserve punchlines and consequences; do not turn every NPC into the same meme voice.
- `ragnamok` is niche/low-confidence; `jomok/perjomokan` may be derogatory or sexualized; `cewe standar TikTok` is a contested label. Use only when the scene clearly supports the reference.
- See `docs/LOKALISASI_ID.md` and `docs/SLANG_RESEARCH_AND_EVIDENCE.md`.

## Hard invariants
Preserve trait/perk/character IDs, stat keys, weapon IDs/constants, food costs, reward operations, CYOA IDs, trader counters, branch conditions, placeholders, interpolation, newlines, tabs, display delimiters and original campaign flow. Translate presentation text only. Prefer exact-context or complete-expression rewrites over global substring substitutions.

## Next priorities
1. Refresh the historical untranslated-candidate queue with a comment-aware parser after merging the current base/overlay, then manually classify likely player-facing expressions.
2. Continue contextual localization across high-impact event, route, trader, item, trait/perk, and tutorial surfaces.
3. Review grammar, register, profanity, character voice, UI length and accidental mixed-language expressions.
4. Recompute coverage only from a validated merged base/overlay inventory; maintain a clear distinction between heuristic coverage and semantic/runtime completeness.
5. Run menus/events/trade/combat/save-load in a compatible runtime.
6. Rebuild/sign APK only after overlay compatibility is demonstrated.
7. Keep README, changelog, inventory metadata, checkpoint reports and version history synchronized.

## Public-repository boundary
Public GitHub stores project-authored documentation, research and sanitized audit summaries only. Do not commit the user-provided archive, full extracted game scripts, original APK or binary overlay.



## Active checkpoint — 24 October 2026, v2.36
- Canonical latest local artifact: `DR2C_VORENYX_ID_v2.36_localization_patch.zip`; it is not committed to the public repository.
- v2.36 localizes 45 complete display expressions and changes 12 direct literal occurrences across 31 modules, including arcade-defense and bandit-raid text, siege route encounters, park/shop/fairy events, city rangers/pandas, character blurbs, and perk/trait guidance.
- Static validation: PASS. Archive 376 entries, 375 manifest entries, zero duplicate paths, manifest hash failures or machine-local path leaks. SHA-256: `fa76da687ce7d8ea5b1e2fafa165b40c31829248fadb5e8c9c6b1ebec3dd5608`.
- Comment-aware inventory: 541 source files, 16,819 active quoted-string tokens; 77 heuristic candidate rows across 36 files remain. These are triage rows, not coverage.
- The 69.07% metric is the stale v2.22 heuristic baseline. Current global semantic coverage is not computed. Gameplay, UI fit, save/load and APK rebuild/signing remain untested.
- The v2.34 checkpoint/hash discrepancy remains documented as reconciled in v2.35; v2.36 builds from the actual v2.35 ZIP.


## Active checkpoint — 24 October 2026, v2.40
- Canonical latest overlay checkpoint: v2.40, based on the verified v2.39 patch archive.
- Repaired 45 trait/perk state-key mismatches across 13 modules; 0 mismatches remain across 195 operand comparisons.
- Trait/perk presentation labels are localized at the display boundary; underlying identifiers remain source-canonical.
- Continued localization across CYOA guidance, journey/camp prompts, NPC dialogue, rewards, comic/magazine interactions, medical feedback and event narration.
- Refreshed the title-art badge to V2.40 in both packaged title-art copies.
- Current comment-aware inventory: 541 .df/.txt files and 16,834 active quoted literals. This inventory pipeline differs from the older curated inventory.
- The inherited high-likelihood candidate queue now has 0 remaining rows in the merged source; this is not a semantic coverage score and does not prove that every player-visible string is localized.
- Global semantic coverage is NOT COMPUTED. Gameplay/runtime, UI fit, save/load and APK rebuild/signing remain untested.
- Public GitHub stores sanitized documentation and audit summaries only; the source archive, full literal inventory and binary overlay are not committed.


## Coverage recheck — 24 October 2026
- Current global player-visible localization coverage is NOT COMPUTABLE from the current artifacts. Do not report the historical v2.22 heuristic (69.07%) as current v2.40.
- Fresh active-literal scan: 16,834 rows; 15,839 rows excluding path/engine references.
- English-likelihood queue: 1,578 rows at >=0.2; 598 rows at >=0.5. Another 305 new/changed literals have no score. Broad triage is 1,883 rows across 196 files.
- Machine-audit non-flagged proxy range 88.11%-94.30% is only a heuristic, not translation coverage.
- The inherited queue being empty is not an exhaustive zero-residue scan. See docs/COVERAGE_RECHECK_v2.40.md and audit/v2.40_coverage_recheck.json.
- Runtime gameplay, UI-fit, save/load and APK rebuild/signing remain NOT RUN / NOT PERFORMED.


## Untouched and ambiguous surface audit — 24 October 2026
- v2.40 source audit: 265 of 509 Deathforth .df files have no overlay file (52.06%); this does not mean all such files contain player-visible text.
- A fresh review queue flagged 598 inherited English-likelihood candidates across 116 files (scores >=0.5 and at least 4 English-word tokens), including 183 rows in files without overlay and 252 in files changed by v2.40 where the candidate literal remains.
- These candidates are not confirmed untranslated counts; inherited scores are not recalibrated. A further 305 new/changed literal rows have no score. Global semantic coverage remains NOT COMPUTED.
- Prioritize untouched character banter, ending-bits, partially translated combat barks, CYOA titles/choices, and full-expression review for 89 whitespace-bound fragments.
- See docs/UNTOUCHED_AMBIGUOUS_AUDIT_v2.40.md and audit/v2.40_source_coverage_review.json.


## Active checkpoint — v2.41 (24 October 2026)
- Latest local patch: `DR2C_VORENYX_ID_v2.41_localization_patch.zip`; local project archive: v2.6. Both remain outside public GitHub.
- Targeted P1 pass covered 15 previously unoverlaid character-banter files, ending/credits, human combat barks, priority CYOA titles/choices, and a display-only `Shotgunner` → `Ahli Shotgun` correction.
- 453 literal occurrences changed across 24 files. Static checks preserved line counts, non-string code, and resource paths. Local patch ZIP CRC and manifest hash checks passed.
- Global semantic coverage remains NOT COMPUTED; 100% localization is not claimed. Gameplay, UI fit/overflow, save/load, and APK rebuild/signing remain NOT RUN / NOT PERFORMED.
- [v2.41 checkpoint](docs/CHECKPOINT_v2.41.md) and [sanitized validation summary](audit/v2.41_static_validation_summary.json) track this pass.


## Active checkpoint — v2.42 (24 October 2026)
- Targeted residual cleanup: 309 quoted-string occurrences changed across 16 overlay files.
- Scope includes selected character banter/emotes, epilogue outcomes, finale mode/credits, ringmaster/healer dialogue, Canada-crossing NPC chatter, Santa/Evil Santa, gnome trader, farm/car encounters, and mission text.
- Static integrity PASS: line counts, string-token counts, non-string code, and resource path literals preserved; zero unmatched mapping rules. Patch and local project archive checksum validation passed.
- Global semantic/player-visible coverage remains NOT COMPUTED. Gameplay/runtime, UI fit/overflow, save/load, device testing, and APK rebuild/signing have not been performed.
- Local patch SHA-256: `e47f397d9c3908a9e370ef98aeb21bf091d66af7eb839a0fb022a9350cb4f4cd`. Full archive remains local-only.
- See [v2.42 checkpoint](docs/CHECKPOINT_v2.42.md) and [sanitized validation summary](audit/v2.42_static_validation_summary.json).


## Active checkpoint — v2.43 (24 October 2026)
- Targeted residual cleanup: 159 quoted-string occurrences changed across 58 overlay files; 9 previously unoverlaid modules added for selected visible strings.
- Static checks passed: line/token counts preserved, non-string code skeleton and resource paths unchanged, zero unmatched rules.
- Inherited 598-row heuristic queue now has 131 active candidate rows after v2.43, down from 241 after v2.42; this is a triage delta, not a confirmed untranslated-string count. Global semantic coverage remains NOT COMPUTED.
- Patch SHA-256: `00ff7866242e8b3aca4fc749e93455ba1c795c4eec99fd15baa07ab483aca024`; local project archive v2.8 SHA-256: `417d8256a74ad6ed64072c93fd1e9b9f255cdb7bca41c49c96333fba6a569cd5`. These binaries and the detailed ledger are not hosted publicly.
- See [v2.43 checkpoint](docs/CHECKPOINT_v2.43.md), [sanitized validation summary](audit/v2.43_static_validation_summary.json), and [residual recheck](audit/v2.43_residual_recheck.json).



## APK candidate build — 24 October 2026 (updated)
- Local artifact: `DR2C_VORENYX_v2.43.apk`; size 39748335 bytes; SHA-256 `3019dd04098e9e8fef01045a2e391d9525bf87ef6874b0d0049c5a073a052f25`.
- Packaging: 272 overlay payloads hash-matched, ZIP CRC PASS, 1,015 entries, no duplicate paths; 3 DEX files and 16 stored native libraries for arm64-v8a/armeabi-v7a; all native libraries 4-byte aligned.
- Android SDK Build Tools 35.0.1 `apksigner` 0.9 verified APK Signature Schemes v1, v2 and v3. SHA-256 certificate fingerprint: `6ea04e10965de1459a7fee845e8ae903bc1535a744f4762c14b2c7bb82eb13f9` (new local key, not publisher key).
- **Not runtime-verified:** no device/emulator/ADB was available for install, launch, gameplay, UI fit, save/load or stability tests. The app has PairIP/Play license-check components and may reject the local signature. No licensing or anti-tamper bypass was attempted.
- Binary APK and extracted game source remain local-only; GitHub stores a sanitized build report.
- Source patch README conflicts with checkpoint/ledger on changed-string metrics (309/16 vs 159/58); remain documented as unresolved.


## Active hotfix checkpoint — v2.44 Start/UI (24 October 2026)
- Local APK candidate: `DR2C_VORENYX_v2.44_START_UI_HOTFIX.apk`; 39748341 bytes; SHA-256 `e28314611411aeba2fdd6bf2cee918fa64ddecac159536e4a39918e7af81f8a6`. Binary remains local-only.
- Inspected the uploaded recording: START remained on screen after taps; game view occupied a narrow horizontal band; settings controls clipped at the right edge; APKVISION graphic appeared behind Android's Open With chooser.
- Restored the internal marker in `assets/deathforth/boot.df` from `PENANDA-GAME` to canonical `GAME-MARKER`; statically verified. Fixed `SplashActivity` and `DrtcGameActivity` to fixed landscape. Static Start route components exist, but actual Start behavior remains untested on device.
- APK ZIP CRC PASS, 1,015 entries, 272 overlay payloads checked, 0 payload mismatches, 3 DEX files, 16 native libs for arm64-v8a/armeabi-v7a, native alignment PASS. Android signature schemes v1/v2/v3 verify using official Build Tools 35.0.1 apksigner.
- The signing certificate `6ea04e10965de1459a7fee845e8ae903bc1535a744f4762c14b2c7bb82eb13f9` is a local key, not the original publisher certificate. PairIP/Play license checks remain and may reject the package; no licensing/anti-tamper bypass attempted.
- VORENYX splash artwork itself has no APKVISION logo, but APKVISION namespaces remain in `classes3.dex` and `libstub.so` in the supplied repackaged base. The wrapper was not removed; a clean authorized publisher APK is needed for a clean no-APKVISION build.
- Install/launch/Start taps, layout fit, gameplay, save/load and stability are NOT TESTED. This is a hotfix candidate, not a verified stable release.


## Post-install failure report — v2.44 (24 October 2026)
- User reports all prior symptoms unchanged after attempting the hotfix: Start still does not trigger, UI layout remains incorrect, and APKVISION branding remains.
- Local APK static check confirms boot marker is canonical and the two main activities declare fixed landscape (0), but there is no proof the device installed this file.
- v2.44 has package `com.noodlecake.drtc`, versionCode 57, and a local signing certificate, not the existing APKVISION/release signer. Android will refuse an in-place update if the currently installed package is signed by a different certificate; old app may remain active. This is a probable deployment blocker, not a confirmed device diagnosis.
- APKVISION namespaces remain in `classes3.dex` and `libstub.so`; v2.44 did not remove the wrapper, so the watermark issue is not fixed.
- Status: hotfix **not verified and user reports no change**. No further blind build. First need the installer result, safe save backup status before any uninstall, and a new recording/log from a confirmed installed candidate.


## Active checkpoint — 26 October 2026, v2.64 runtime trace toolkit
- Latest diagnostic utility: DR2C_VORENYX_v2.64_START_RUNTIME_TRACE_TOOLKIT.zip; SHA-256 50545f6e2cf61b48e067910781e2996ae822895fef073a61859d9b249020a. The ZIP has CRC PASS, zero duplicate paths, and 11/11 static assertions pass.
- Hardened collector: it no longer clears Android log buffers; it starts near the live edge, auto-stops after 90 seconds, flags early logcat startup failure, removes temporary raw logs, and avoids mixing stale crash-buffer lines into the output.
- Runtime status remains blocked pending execution on a Windows PC connected to the Android device via authorized ADB. No actual Start tap trace has been collected in this environment.
- Current APK candidate reference remains the v2.57 signature-fix APK (SHA-256 a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7); the Library artifact named v2.58 is byte-identical. This is not a runtime-verified release; local signing certificate is not the publisher's key.
- Next gate: collect trace → classify input/Deathforth/native/integrity failure → make a narrow fix → rerun package/source checks → device test install, Start, events, UI and save/load. Do not build blindly or risk existing saves.


## Active checkpoint — 26 October 2026, v2.65 install/start trace toolkit
- Latest diagnostic artifact: DR2C_VORENYX_v2.65_INSTALL_START_TRACE_TOOLKIT.zip; SHA-256 b67f81776e96a2d96d1cfc04015247aaf85bb7477672a504a7e2698feb48da27. ZIP CRC PASS, duplicate paths 0, static assertions 17/17 PASS.
- Two modes: INSTALL_ATTEMPT (works even if the app package is absent and filters PackageManager/signature/install failures) and START_BUTTON (requires installed com.noodlecake.drtc and records crash/native/Deathforth/integrity lines).
- Collector never clears Android log buffers, does not auto-install/uninstall, does not modify saves or bypass signing/licensing, uses a 90-second cap, records before/after package state, and deletes the temporary raw log before packaging.
- Actual installation failure and Start no-op remain undiagnosed until a device trace is captured. No runtime stability or release claim is made.
- Next gate: if package absent, run INSTALL_ATTEMPT and manually repeat installation once; if installed, run START_BUTTON and tap Start once. Classify the trace before another APK rebuild.
- v2.57 verification-gap audit: actual candidate SHA matches the recorded hash; ZIP CRC/entry checks and jarsigner v1 pass with self-signed warnings; project-local v2 verifier reports PASS. Official Android apksigner and real-device install remain unverified. Fresh install failure after old package removal must not be attributed to signer mismatch alone. See audit/v2.57_official_signature_verification_gap.json.


- Supplemental source diff cross-check on 26 October: events.df is byte-identical between base/candidate; normalized tokens match in game-select.df, game-info.df and boot-end.df after masking strings/comments. boot.df's additional code is the id-name-localize helper; removing it makes its normalized token stream match the base. tutorial.df remains an unresolved code-token exception (chim → cname and removed bHe/bhim/bhe expressions); it is not proven to cause Start failure. Details: audit/start_route_source_diff_v2.65.json.


## Active checkpoint — 26 October 2026, v2.66 deep installability audit (NOT an APK build)
- Exact candidate audited: DR2C_VORENYX_v2.57_SIGNATURE_FIX_REDELIVERED_20261025.apk, SHA-256 a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7.
- ZIP CRC, binary manifest structure, Android 11 resources.arsc storage/alignment, stored native-entry page alignment, jarsigner v1, and independent v2 signer-signature/content-digest checks pass. Official Android apksigner remains NOT RUN; device install/runtime remains NOT TESTED.
- Source lineage reproduces all 509/509 Deathforth scripts byte-for-byte from the available base and ordered patch layers; no missing/extra/mismatched script paths. Core Start/menu control-token streams match after masking display strings/choice labels. The tutorial chim→cname change is inside player-visible choice labels and retains tutorchat-1/2/3 callbacks; it is not a proven Start root cause.
- Static checks narrow possible corruption causes but do not establish PackageManager acceptance. A fresh-install failure remains undiagnosed without the exact device-side install code. Use v2.65 INSTALL_ATTEMPT; if it installs, use START_BUTTON. No speculative rebuild/reinstall loop.
- See docs/INSTALLABILITY_AUDIT_v2.66.md and audit/installability_audit_v2.66.json.


## Active checkpoint — 26 October 2026, v2.67 whole-project audit

- Exact candidate under review: v2.57 APK SHA-256 a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7; this is an audit checkpoint, not a new APK.
- Patch lineage reconstructs the candidate's 509/509 Deathforth scripts byte-for-byte. CYOA declaration counts match base; no clear deletion of the Start control path is indicated by heuristic static scan.
- Confirmed stale V2.43 badge remains on splash artwork. Additional vorenyx_title_screen.png also carries V2.43 and no literal loader reference was found; possible orphan asset, not proven.
- Native libmain.so copies for both ABIs each differ in 89 bytes within ELF .rodata, not in observed code-byte ranges. fitness appears as bugar in native strings but fisik in the Deathforth display helper. Treat as visible-label inconsistency; no gameplay-state corruption is proven.
- 167 PNG and 21 MP3 assets pass decode/probe. A missing include paul/camping-tent-events.df is referenced by the apparent dormant paul/camping-region.df; no boot-path reference was found, so it is not classified as startup root cause.
- Official Android apksigner, device install, live Start tap, menu/gameplay/save-load and stability have NOT been verified. Root causes for installation failure and Start no-op remain UNKNOWN until PackageManager/Logcat traces arrive.
- Reports/tool saved in docs/WHOLE_PROJECT_AUDIT_v2.67.md, audit/whole_project_audit_v2.67.json, and tools/whole_project_audit_v2.67.py. Full local toolkit SHA-256: e66d10df8068d547b1af9f8770ce21a88c15ca85b26f91a72a1842187e89bbea.


## Active checkpoint — 26 October 2026, v2.68 source repair

- Source/asset patch only; latest local ZIP SHA-256: `e6bf40a2ca8f69b4c55f7b50592b1cb201b8660ff285f6862a1c96e8b645690d`.
- Four changes: `boot.df` display-only alias `fitness` -> `bugar`; missing camping event include changed to `load?`; additional title artwork no longer says V2.43; source-overlay splash no longer says V0.3. Candidate APK binary itself remains unchanged and its splash still says V2.43.
- Local tests PASS: source assertions; patcher fixture/backup/idempotency; title and splash PNG validation; byte-identical artwork generation; exact four-payload replay on reconstructed source lineage; ZIP integrity and checksums.
- Files: `docs/SOURCE_REPAIR_v2.68.md`, `audit/source_repair_v2.68.json`, `tools/apply_source_repair_v2.68.py`, `tools/repair_title_artwork_v2.68.py`, `tools/test_source_repair_v2.68.py`.
- A separate v2.68 local test APK is now built: SHA-256 `9ad55289ff5189727cdd43ca39105db49f38c5aa8b6186d6794b19a45aa38cff`, 115,639,068 bytes. JAR/v1 and local v2 signature verifiers PASS; ZIP CRC, path uniqueness, alignment and exact target payload comparison PASS.
- Official Google apksigner, Android install, Start/Logcat, gameplay and save/load remain NOT TESTED. The APK uses a new local test cert, not publisher key; may require uninstall of a differently signed app and could lose local saves. PairIP/license code unchanged. Not a stable release.
- Build report: `docs/APK_TEST_BUILD_v2.68.md`; sanitized report: `audit/apk_test_build_v2.68.json`. The source patch ZIP remains an overlay, not an APK.


## Active checkpoint — 27 October 2026, v2.68 local test APK build

- Locally built test APK: `DR2C_VORENYX_v2.68_TEST_CANDIDATE.apk`, 115,639,063 bytes, SHA-256 `4028b0ada13ab650ba3625bfe7bf495455bb5816040847f0999ac591f1ecd384`.
- JAR/v1 verification and local APK v2 verifier PASS; ZIP CRC/no-duplicates and alignment of 264 stored entries PASS; four intended payloads match source overlay byte-for-byte; no other non-signature payload changed.
- New local test certificate SHA-256: `c46d4af342ad0ecb63a771613e245ab4088597520a27aaf2719c8ea03d6dd15c`. The key and password are not in GitHub.
- Official apksigner unavailable. PackageManager install, Start/Logcat, gameplay, tutorial, save/load and stability NOT TESTED. PairIP/licensing/native components unchanged. Do not call this a stable release.
- Build report at `docs/APK_TEST_BUILD_v2.68.md` and sanitized metadata at `audit/apk_test_build_v2.68.json`. Binary APK excluded from public GitHub.


## Active checkpoint — 27 October 2026, v2.69 Start runtime diagnosis

- User reports the locally signed v2.68 APK installs but Start does not proceed.
- Static audit: `events.df` byte-identical to base; normalized control-token streams of `game-select.df`, `game-start.df` and `boot-end.df` match base. `events/tutorial.df` has known code-token differences within translated expressions that remain untested; not proven to cause initial Start no-op.
- Corrected earlier note: `id-name-localize` has call sites in trait/perk UI files, but these are not on the initial select-boot route.
- Added `docs/START_ROUTE_STATIC_AUDIT_v2.69.md`, `audit/start_route_static_audit_v2.69.json`, `tools/audit_start_route_v2.69.py`, and `tools/collect_start_trace_termux_v2.69.sh` to branch `dr2c-v268-source-repair` and draft PR #32.
- Local trace toolkit ZIP SHA-256: `8460aaf92bd732189d38cb39cc127415d72110bbf1f29c3b5bb10cc35ae0648a`. Shell syntax and ZIP CRC PASS. Trace collector uses Android 11 Wireless debugging/ADB, asks before clearing log buffer, does not upload automatically and does not touch game saves.
- No APK rebuilt. Root cause remains unknown until dispatch/callback/tutorial/native process logs from the device are reviewed.

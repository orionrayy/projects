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


## Active checkpoint — v2.53 source contract reconciliation (25 October 2026; not an APK version)
- Reconciled local source-only patch from DR2C-RAYY(2).zip + v2.43 localization patch + v2.45 corrective patch + v2.45 Start quote-fix patch.
- Output DR2C_VORENYX_v2.45_RECONCILED_SOURCE_PATCH_v2.53.zip: 7,515,735 bytes, SHA-256 73c9f60cd1a88a6d121843f3bdc6304262d47c01b2cdc36237015b7d083583d7; ZIP CRC PASS, 274 entries, 0 duplicate paths, 272 paths/269 .df payloads, 18 later-layer path overrides.
- New static contracts: source-hash pin; overlay paths exist in source; canonical GAME-MARKER; no escaped backslash-quotes; no unclosed strings in overlay scripts; ordered single-quoted Forth symbol sequence preserved in all 269 overlay scripts; canonical Jack of All Trades perk key; main-event-do-select, select-start, select-boot, and tutorchat-1 are present. Static checks PASS; 6/6 unit tests pass.
- Scope remains v2.43 + v2.45 corrective + v2.45 quote fix, not v2.51 and not an APK. Exact v2.47–v2.51 patch ZIPs remain unavailable for byte-level integration, so the report's 77/509 script count is not reconciled against the available v2.43 patch's 269 .df payloads.
- APK build/sign/install/runtime, UI fit, gameplay, save/load and stability remain NOT RUN / NOT VERIFIED. Current available APK base is APKVISION-repackaged; Android build tools are not installed here and no license/security wrapper bypass is attempted.
- See docs/SOURCE_RECONCILIATION_GATE_v2.53.md, audit/source_reconciliation_v2.53.json, and tools/reconcile_overlay.py.

## Active checkpoint — v2.54 provenance audit (25 October 2026)

- Added `tools/audit_overlay_provenance.py` to compare ZIP CRC, archive SHA-256, Deathforth `.df` path inventories, byte-identical/different script counts, missing overlay paths, and explicit targets. Hardened path validation to reject ambiguous source roots and noncanonical dot segments. The two suites have 12 unit tests, and CI run #40166720059 passed.
- Verified against the available local inputs: base `DR2C-RAYY(2).zip` has 509 `.df` scripts; v2.43 overlay has 269 `.df` payloads, all 269 byte-different from base; 240 base scripts have no overlay payload; no overlay-only script paths exist.
- Batch K v2.51 metadata names nine scripts; all nine already exist and differ from base within the available v2.43 overlay, including the three called “new” in the Batch K report. That is a lineage/evidence discrepancy, not proof that a specific archive is wrong.
- Exact v2.46 baseline APK and v2.47–v2.51 binary patch ZIPs are unavailable for byte-level comparison; an enumeration of 299 Library ZIP artifacts found no v2.47–v2.51 binaries, although the v2.47 checksum sidecar exists. PR description mentions v2.50 Batch J, but no corresponding report/JSON is in the PR changed-file list or current accessible artifact set.
- Do not auto-merge the available 269-script v2.43 lineage with the later 77/509 report, do not reconstruct missing translations by inference, and do not claim v2.51 integration. Obtain exact baseline + v2.50/v2.51 ZIPs with checksum sidecars first.
- No APK build, signature/install verification, Deathforth full parse, device runtime, UI-fit, gameplay, or save/load test was performed in this checkpoint.
- See `docs/BATCH_K_PROVENANCE_RECONCILIATION_v2.54.md`, `audit/batch_k_provenance_v2.54.json`, and `tools/audit_overlay_provenance.py`.

## Active checkpoint — v2.55 reproducible source packaging (25 October 2026)

- Normalized output ZIP member timestamps and Unix file modes in `tools/reconcile_overlay.py`; added a regression test for two byte-identical builds from identical inputs.
- Built the available layers three times (base archive + v2.43 overlay + v2.45 corrective patch + v2.45 Startfix patch). All three archives match SHA-256 `95bfb426c802c0dacebb9d44586cf6deeef1aab5557e2c63ca5dff6f05edf64d`; size 7,515,735 bytes; CRC PASS; 274 entries; 272 overlay paths; 269 .df scripts; 18 overrides.
- Compared with the earlier v2.53 ZIP: all 274 member paths/payloads are identical; the prior hash drift was ZIP timestamp/file-mode metadata.
- Test suites: source reconciler 7/7 PASS, provenance 6/6 PASS. Combined 13/13 PASS.
- Scope explicitly remains v2.43 + v2.45 corrective + v2.45 quote-fix, NOT v2.51. Exact v2.46 APK baseline and actual v2.47–v2.51 ZIPs remain unavailable. No APK build/sign/install/runtime, full interpreter parse, UI fit, Start input, gameplay or save/load test has been performed.
- See `docs/REPRODUCIBLE_SOURCE_PATCH_v2.55.md`, `audit/reproducible_source_patch_v2.55_summary.json`, and provenance gate v2.54.

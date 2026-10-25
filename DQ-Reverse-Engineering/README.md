# Dungeon Quest — Reverse-Engineering Workspace

**Status: curated, partial source reconstruction from DEX plus verified extraction of the outer game-asset archive. This is not a complete/build-verified Android project.**

Analyzed build: package `com.shinybox.smash`, version `3.3.2.0` (version code `1423433200`). The original APK, raw DEX, original pack, native libraries, and credential-bearing asset contents are excluded from this public source tree.

## Pause → Options one-row candidate — v50

- [Separate-output Pause HUD candidate builder](tools/build_pause_options_gold_row_v50.py)
- [Synthetic regression tests](tests/test_pause_options_gold_row_v50.py)
- [Local asset/STK evidence and runtime limits](docs/PAUSE_OPTIONS_GOLD_ROW_CANDIDATE_V50.md)

The v50 candidate places one Gold +100K button in the existing Gameplay tab, in the empty right-hand slot beside the Pickup button. It directly uses the already-observed uai_gp_hud.onDebug(6.0) action-call shape; native disassembly identifies that branch as RewardGold(100000.0). Locally, the candidate STK decodes cleanly and only Resources/HUD/pause.hud differs. Runtime dispatch is still unverified; no APK was built, and this is not the 222-row menu.

## Native Options tab limit — v49

- [Four-tab native selection contract](docs/OPTIONS_TAB_NATIVE_LIMIT_V49.md)

Static ARM64 disassembly of \`uai_gp_options::onShowTab\` (VA \`0x788890\`) shows branches for tab arguments 1–4 only: Gameplay, Controls, Social/IAP and Credits. A fifth-tab callback is not supported by this function. Group visibility can be controlled by HUD action records independently, but adding a fifth tab still needs explicit selected-tab state/layout and on-device validation. No native binary or source asset was changed.

## Reproducible STK single-asset verification — v48

- [Fail-closed archive delta verifier](tools/verify_stk_single_asset_delta_v48.py)
- [Synthetic regression tests](tests/test_stk_single_asset_delta_v48.py)
- [Verification contract and reproduction command](docs/STK_SINGLE_ASSET_DELTA_VERIFICATION_V48.md)

This verifier reopens source and candidate archives, decodes all entries, confirms matching archive inventories and validates every CRC/decoded-size check, then fails closed unless only Resources/HUD/debug.hud differs. Six synthetic tests are integrated into the static workflow. This proves asset-level archive integrity only, not in-game behavior or APK readiness.

## Pause → Options → Cheats route blocker — v47

- [Read-only route evidence and remaining native requirements](docs/PAUSE_OPTIONS_CHEATS_ROUTE_AUDIT_V47.md)

The source Pause button calls uai_gp_options.onShowOptions; the options model has no onShowCheats handler, and uai_gp_debug is a shader-diagnostics model rather than the controller for debug.hud. The 222-row HTML workbench is scrollable but remains disconnected from game state: the current matrix is 0 fully integrated, 0 runtime verified, 3 unverified native candidates and 219 requiring a verified adapter. No guessed callback was added to the source Pause HUD.

## HUD action serializer and one-row debug candidate — v46

- [Field-preserving action encoder](tools/hud_action_serializer_v46.py)
- [Separate-output debug candidate builder](tools/build_debug_gold_one_row_v46.py)
- [Serializer tests](tests/test_hud_action_serializer_v46.py)
- [Audit and candidate boundaries](docs/HUD_ACTION_SERIALIZER_AND_DEBUG_GOLD_CANDIDATE_V46.md)

A local source-asset experiment adds one Gold +100K button to a copied debug.hud and a matching onAddGold action routed through uai_gp_hud.onDebug(6.0). Source framing round-trips exactly; output reparsing verifies 72 elements and 14 actions, versus 71 and 13 in the source. The resulting STK candidate was rebuilt and independently decoded: all 5,630 entries validate and exactly one entry, Resources/HUD/debug.hud, differs from the original. Candidate SHA-256: ca6387141047a096cc279d06a03c6392602d1cd0a3c97643067c48434b8bfa57. The static native audit associates branch 6.0 with RewardGold(100000.0), but this remains unverified in a running game. No binary asset is committed; no APK/XAPK was built.

## HUD action-stream framing audit — v45

- [Read-only HUD action-stream parser](tools/hud_action_probe_v45.py)
- [Synthetic framing tests](tests/test_hud_action_probe_v45.py)
- [Source audit and debug-command cross-reference](docs/HUD_ACTION_STREAM_AUDIT_V45.md)

Local validation decoded action framing for 68/68 source HUDs: 1,232 action records and 2,538 length-prefixed statements, with no leftover bytes. The existing debug HUD maps its buttons to uai_gp_hud.onDebug numeric commands; static v43 disassembly separately identifies argument 6.0 as a +100,000 Gold candidate, but that action is not currently wired in debug.hud and remains not runtime-verified. This parser does not change assets and does not solve the generic List row/selection dispatch for the 222-entry Cheats menu.

## Native List script-API contract audit — v44

- [Native List wrapper disassembly and call-shape audit](docs/NATIVE_LIST_API_CONTRACT_AUDIT_V44.md)

The ARM64 export wrappers confirm native APIs to add list items, set item text, bind a selection-changed action, read selected indices/counts, and enable scrolling/single-selection. This narrows the remaining issue to the compiled AIM/model-side population and stable-ID dispatch logic; the native List itself does not create 222 actionable control rows. No game assets or package were changed.

## Native AIM model framing audit — v43

- [Read-only AIM v10 probe](tools/aim_model_probe_v43.py)
- [Synthetic framing regression tests](tests/test_aim_model_probe_v43.py)
- [Source inventory and integration boundary](docs/AIM_MODEL_FRAMING_AUDIT_V43.md)

Local source validation parsed 162/162 AIM files and inventoried 3,889 variables, 664 functions, 164 state descriptors and 1,013 handlers (5,730 length-framed records total). The parser preserves unknown record payloads as opaque hashes and reports a source anomaly in \`ai_Effect.aim\` instead of inferring a correction. Six synthetic tests pass locally; the test command is in static CI, but remote CI status has not yet been verified. This does not decode full AIM script semantics or connect the in-game 222-entry Cheats menu.

## HUD codec source round-trip — v42

- [Field-preserving v12 HUD element codec](tools/hud_elements_codec_v42.py)
- [Synthetic serializer regression tests](tests/test_hud_elements_codec_v42.py)
- [Source round-trip and integration boundary report](docs/HUD_ELEMENT_CODEC_V42.md)

Local verification reconstructed all 68 HUD assets from the matching v3.3.2.0 source pack byte-identically after parse/encode, covering 4,956 records with zero unconsumed element bytes. Five synthetic tests pass locally, including length-changing label edits, exact no-op serialization, legacy string bytes, scalar bounds, and malformed-input rejection. The test suite is wired into the existing static-validation workflow, but remote CI still needs a fresh confirmed result. This remains a format-level tool: no new List was inserted into the game and no gameplay handler is connected.

## Latest HUD investigation — v41

- [Version-12 element record probe](tools/hud_elements_probe_v41.py)
- [Canonical v12 HUD serializer](tools/hud_elements_serializer_v41.py)
- [Synthetic parser tests](tests/test_hud_elements_probe_v41.py)
- [Synthetic serializer regression tests](tests/test_hud_elements_serializer_v41.py)
- [Element and reciprocal SaveElements audit](docs/HUD_ELEMENT_RECORD_AUDIT_V41.md)

Locally, the parser validated 68 source HUD resources (4,956 element records), and the canonical serializer reproduced all 68 resources byte-for-byte when writing to a separate temporary directory. A synthetic round-trip test covers element types 1–15, with fail-closed checks for a nonzero field that native SaveElements canonicalizes and non-finite numbers. The source contains only one type-3 List record, in match_result_anim.hud; neither pause.hud nor debug.hud has one. This establishes a source-build v12 serialization contract, not a working in-game cheat list: AIM row population and selection/action dispatch remain unresolved. Static CI now runs the synthetic parser and serializer tests; verify the newest run before treating remote CI as green. No APK/XAPK was built or original game asset modified in this increment.


## Latest native List/model audit — v42

- [AIM/HUD List population and callback audit](docs/AIM_LIST_CALLBACK_AUDIT_V42.md)

The source ARM64 library shows the existing LegendEx model calling its native CreateLegendItem and UpdateList methods from onOpen. CreateLegendItem references the listitem_legend template, generated legend_ instance names, the legendex.list container and the model's own click callback. This is concrete evidence of an AOT-implemented, template-based row pattern, not a reusable 222-cheat dispatcher. The model is tied to LegendEx data and native code in libS3DClient.so; editing AIM/HUD declarations alone does not add new native handler bodies. The next gate remains a generic, allow-listed action bridge plus one-row runtime proof in a parallel package. No game asset or native library was modified and no APK/XAPK was built by v42.

## Latest native Debug HUD command audit — v43

- [Existing debug command map and fixed Gold reward candidate](docs/DEBUG_HUD_COMMAND_MAP_V43.md)

Static disassembly confirms that an unexposed `uai_gp_hud::onDebug(6.0)` branch calls `RewardGold` with the numeric argument 100000.0. This is a candidate for a fixed +100,000 Gold sandbox action using an existing native dispatch route; it remains NOT-RUNTIME-VERIFIED and no UI row or asset change was made. The neighboring command 7 is contextual to LegendEx state and must not be treated as a generic spend control. The 222-cheat menu remains blocked on native row population/allow-listed dispatch; no APK/XAPK was built.

## Artifact scope — read this before comparing ZIPs

| Artifact | Scope | Explicit exclusions |
|---|---|---|
| This GitHub directory (`DQ-Reverse-Engineering/`) | Curated, reviewable source workspace: selected disassembly fragments, higher-confidence Java excerpts, tools, tests, a manifest analysis excerpt, and selected text reports | Not a byte-for-byte mirror of local generated artifacts; not a full Android Studio/Gradle project |
| Local `DQ_Modkit_v10_IAP_Flow_Trace.zip` | 60-file delivery package under `package/`, about 35.8 MB uncompressed; includes patched asset pack, IAP analysis reports, patch/packer tools, tests, and standalone sandbox files | Does **not** contain original APK, original `S3DMain.smf`, `classes.dex`, all 68 app-specific disassemblies, 68 Java declaration scaffolds, the full decoded asset tree, or the manifest analysis excerpt |
| Local v11 audit package | Adds a symbol-level `Smash.gam`/IAP/Options/Debug/HUD audit, a per-SKU evidence matrix, tests, and native/split analysis | It remains a local delivery artifact unless its text reports/tools are committed separately; it is not an installable APK |

Earlier notes refer to a separate, broader “full local analysis bundle.” That phrase does **not** describe the v10 IAP Flow Trace ZIP. Compare actual archive manifests rather than assuming that either ZIP or this repository contains every file generated during analysis.

## Included in this curated repository

- `disassembly/`: representative Dalvik output and a method/class inventory; not all 68 app-specific classes.
- `reconstruction/verified/java/`: higher-confidence `BuildConfig`, `Globals`, and `S3DEngine` excerpts, compiled only against temporary Java stubs.
- `reconstruction/fragments/`: selected `ShinyActivity` / `Smash` excerpts and the JNI/native boundary.
- `manifest/`: analysis excerpt only; resource IDs remain unresolved, and it must not replace the real binary manifest.
- `tools/`, `tests/`, `docs/`: offline parsers, packer/patcher, regression tests, and evidence reports.

## DEX and IAP evidence

- DEX has 10,768 total class definitions; 68 belong to the app-specific `com.shinybox.*` namespace.
- The wrapper declares 44 native methods; 34 are on `S3DRenderer`.
- `IAP.xml` has 107 identifiers; the DEX IAP initializer has 104 unique literal SKU identifiers; 102 are shared. XML-only identifiers are `angelicslime`, `demonicslime`, `poisonslime`, `vanity72`, and `vanity73`; DEX-only identifiers are `package20` and `package21`.
- The exact v15 native audit maps `gold1`–`gold5` to 20M/50M/150M/350M/1B Gold via direct `RewardGold` calls; `gold`, `crystal`, and `mythstone` instead map to boost-state keys. Bundle component vanity flags, pet archetypes/families, slot and map-reveal branches are mapped where direct evidence exists; unresolved values remain explicitly blocked.
- JNI purchase-success at `0x1e5b68` sends an event to `InAppPurchase::onPurchaseSuccess @ 0x41c254`. The next target uses dynamic `sAIHandler`; the final delivery to `uai_gp_hud::onPurchaseSuccess` is still `INFERRED`, not proven by string presence.
- `uai_gp_account::GetIAPString` is called during account upload and `SetIAP` during account download; this proves cloud/account serialization call sites, not the local save-file format or local persistence. No SKU reward is runtime-verified.

## Game-model and debug-screen boundary

`Games/Smash.gam` contains a parsed 30-name model registry, including `InAppPurchase`, `uai_gp_options`, and `uai_gp_debug`. The `debug.hud` asset contains level/CS/MS/Feat/Crystal/Eternal/Boss test controls. The named `uai_gp_debug.aim` callbacks are principally shader/log diagnostics. Static asset presence does not prove the debug screen is reachable in a release build.

## Asset archive and native split — recovered; runtime still unverified

The outer `S3DMain.smf` container was parsed and all 5,630 entries passed CRC-32 and decoded-size checks. The decoded payload totals about 94.5 MB and includes XML tables plus proprietary `.gam`, `.aim`, `.hud`, model, mesh, skeleton, scene, animation and texture data.

The newly supplied XAPK contains the matching v3.3.2.0 base APK, `config.arm64_v8a.apk`, and `config.xxhdpi.apk`. All 20 APK members share signer SHA-256 fingerprint `9A:28:A9:91:71:C8:F6:3F:34:11:E2:91:F6:D9:6F:13:D5:D9:C1:73:62:06:A0:CF:95:EB:EE:99:BC:31:42:1D`. The ARM64 split contains four native libraries; `libS3DClient.so` is ELF64 AArch64, SHA-256 `0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083`, with dynamic dependencies inventoried. This resolves the previous missing-native-binary blocker for static analysis.

The native binary is now present locally and has been disassembled for IAP branches, but no runtime instrumentation, Android APK build/sign/install, or gameplay test has been performed. The matching binary is not checked into GitHub; only hashes, ELF metadata, call-site notes and evidence ledger are tracked.

## Synchronization inventory — v15

- [Latest repository, native trace, economy patch, evidence status and blockers](docs/SYNC_STATUS_AND_NEXT_STEPS_V15.md)
- [Local/GitHub source artifact manifest](docs/SOURCE_ARTIFACT_MANIFEST_V15.csv)
- [Prior v14 AIM/HUD inventory and prior v13/v12 sync notes](docs/SYNC_STATUS_AND_NEXT_STEPS_V14.md)

The curated branch currently tracks only two `.smali` files (plus the inventory Markdown) and no generated `reconstruction/java/` scaffolds. It does **not** contain all 68 app-specific disassemblies or 68 Java declaration scaffolds mentioned in earlier local-bundle descriptions. CI checks are tied to the exact commit SHA; see the v14 sync report for latest validation status.

## Latest evidence reports — v15, v14, and v13

- [Canonical 109-SKU purchase → grant → state/persistence map](docs/IAP_CANONICAL_MAPPING_V15.json)
- [Evidence ledger with claims, confidence, impact and next tests](docs/EVIDENCE_LEDGER_V15.json)
- [Native ARM64 IAP callback and grant trace](docs/NATIVE_IAP_TRACE_V15.md)
- [Native split hash, ABI and ELF dependency inventory](docs/NATIVE_SPLIT_AUDIT_V15.json)
- [Economy patch report and exact changed-table hashes](docs/ECONOMY_PATCH_V15.md) and [machine-readable report](docs/ECONOMY_PATCH_V15.json)
- [Source/patch XML, SKU and Shop reconciliation report](docs/IAP_ASSET_RECONCILIATION_V15.json)
- [v15 canonical IAP validator](tools/validate_iap_canonical_mapping_v15.py) and [tests](tests/test_iap_canonical_mapping_v15.py)
- [v15 XML/SKU reconciliation tool](tools/reconcile_iap_asset_tables_v15.py) and [tests](tests/test_iap_asset_reconciliation_v15.py)
- [v14 AIM/HUD string inventory plus machine-readable 58-symbol snapshot](docs/AIM_HUD_SYMBOL_AUDIT_V14.md) / [JSON](docs/AIM_HUD_SYMBOL_AUDIT_V14.json)

The latest verified CI before the v15 sync report/README edits passed the v13, v14, v15 canonical-map and XML/SKU test steps plus manifest boundary checks and Java stub compilation. Check CI against the exact branch HEAD before describing new commits as verified. All 109 product rewards remain not runtime-verified; the direct static findings are not a substitute for a running game state diff.

## Reproduction and remaining blockers

The source tools support offline metadata extraction, DEX inventory/disassembly, Java declaration scaffolds, STK extraction/rebuild, and narrow asset patching. The repository does **not** claim complete original Java source, JNI implementations, bundle reward mapping, a full Gradle build, signing, emulator launch, or runtime equivalence.

The uploaded APK contained a credential-shaped `assets/api_key.txt`; its value is excluded from the repository and reports. Rotate/revoke it if it is active.

## Pause → Options → Cheats route bridge — v16

- [Route evidence and integration status](docs/PAUSE_OPTIONS_CHEATS_ROUTE_V16.md)
- [Machine-readable route evidence/status](docs/PAUSE_OPTIONS_CHEATS_ROUTE_V16.json)
- [Fail-closed Java route bridge](runtime-adapter/src/main/java/dev/dqdebug/runtime/PauseOptionsCheatsBridge.java)
- [Java bridge contract tests](runtime-adapter/src/test/java/dev/dqdebug/runtime/PauseOptionsCheatsBridgeSelfTest.java)

The source bridge and contract tests are implemented, but the proprietary S3D Options UI hook remains **BLOCKED**: this repository has no validated HUD serializer with lossless round-trip tests and no original game UI source callsite. The bridge does not claim the Cheats entry exists in the running game.

## Existing main-HUD debug route audit — v20

- [Main HUD debug action mapping and next gates](docs/MAIN_HUD_DEBUG_ROUTE_V20.md)

The v20 static audit found existing handlers in the main HUD for `onDebug(0)`, `onDebug(5)`, `onDebug(6)`, `onDebug(7)`, and `onDumpShaderList`, plus debug-related element names. This narrows the engineering question to the visibility and reachability of the existing debug group rather than inventing a new dispatcher. It still does not prove the controls are reachable during gameplay or that a native call is safe. No native callback or asset bytes were patched.

## HUD binary format and route evidence — v19

- [Read-only HUD binary probe](tools/hud_asset_probe.py)
- [Synthetic HUD parser regression tests](tests/test_hud_asset_probe.py)
- [Verified HUD section/action findings](docs/HUD_BINARY_FORMAT_V19.md)

The v19 audit parsed the original Pause and Debug HUD headers and section boundaries, confirming 64 Pause actions and 13 Debug actions. The existing `onShowOptions` action toggles the existing Options model, but the Pause action table has no explicit Debug route. A read-only parser and regression tests are now included in static CI. Element records remain opaque and no original HUD resource was rewritten; the live click path remains blocked pending a lossless serializer and in-game runtime verification.

## Native split recovery and Android harness verification — v18

- [Recovered ARM64 split/native export audit](docs/NATIVE_SPLIT_AUDIT_V18.md)
- [Updated native engine boundary](docs/NATIVE_ENGINE_BOUNDARY.md)
- [Corrected split APK findings](docs/SPLIT_APK_FINDINGS.md)
- [Android harness smoke test](cheats-harness/app/src/androidTest/java/dev/dqdebug/sandboxharness/MainActivitySmokeTest.java)
- [Android build + emulator workflow](../.github/workflows/dq-cheats-harness-android.yml)

The supplied v3.3.2.0 XAPK has been recovered and statically audited. Its ARM64 split contains libS3DClient.so, libcrypto.so, libssl.so and libopenal.so; sampled split signer fingerprints match. The native binary exposes JNI and S3DClient APIs, including HUD-action and options calls, but their authoritative call signatures, thread contract and safe player-state accessors are not established. Binary exports are not proof that a cheat controller can safely mutate game state.

The standalone **DQ Cheats Sandbox Harness** is a separate app, not a repackaged Dungeon Quest APK. A prior CI run did build its debug APK and pass JVM unit tests. The updated workflow now also attempts instrumentation/navigation checks and installation/launch on an Android API 35 x86_64 emulator; see the [current PR checks](https://github.com/orionrayy/projects/pull/26/checks) and verify the newest run's conclusion before treating emulator checks as passed. This does not test the original ARM64 game engine.

**Original-game integration remains NOT VERIFIED:** no format-correct HUD edit has been validated, no Pause → Options → Cheats click path has been exercised in Dungeon Quest, no reversible game-state adapter has been runtime-verified, and no modified original-game APK has been built/installed/launched. Purchase receipts/entitlements and online progression are not modified.

# Dungeon Quest — Reverse-Engineering Workspace

**Status: curated, partial source reconstruction from DEX plus verified extraction of the outer game-asset archive. This is not a complete/build-verified Android project.**

Analyzed build: package `com.shinybox.smash`, version `3.3.2.0` (version code `1423433200`). The original APK, raw DEX, original pack, native libraries, and credential-bearing asset contents are excluded from this public source tree.

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

The source bridge and CI tests are implemented. The real proprietary S3D Options UI hook remains **BLOCKED**: no validated HUD serializer or original game UI source callsite is present in the repository. The bridge does not claim the Cheats entry exists in the running game; no APK was built or runtime-tested.

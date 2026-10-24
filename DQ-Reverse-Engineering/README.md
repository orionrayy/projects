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
- Same-number `vanityN` to `Vanity.xml` rows are asset-level correlations, not proof of the native grant or entitlement-persistence behavior. Exact package contents, grant values, and native reward writes remain unresolved.
- `InAppPurchase.aim` exposes purchase/restore callback symbols; `uai_gp_account.aim` exposes `SetIAP` / `GetIAPString`; `uai_gp_hud.aim` exposes purchase-state and callback symbols. The custom model bytecode has not been fully decoded.

## Game-model and debug-screen boundary

`Games/Smash.gam` contains a parsed 30-name model registry, including `InAppPurchase`, `uai_gp_options`, and `uai_gp_debug`. The `debug.hud` asset contains level/CS/MS/Feat/Crystal/Eternal/Boss test controls. The named `uai_gp_debug.aim` callbacks are principally shader/log diagnostics. Static asset presence does not prove the debug screen is reachable in a release build.

## Asset archive — resolved; engine is not

The outer `S3DMain.smf` container was parsed and all 5,630 entries passed CRC-32 and decoded-size checks. The decoded payload totals 94,513,994 bytes and includes readable XML tables alongside proprietary `.gam`, `.aim`, `.hud`, model, mesh, skeleton, scene, animation, and texture data. Decoding the outer archive does not recover the native engine.

The supplied base APK contains zero `lib/*.so` entries. DEX records `System.loadLibrary` order `crypto`, `ssl`, `openal`, `S3DClient`. The manifest excerpt declares `requiredSplitTypes="base__abi,base__density"` and `android:isSplitRequired="true"`. A matching ABI/density split set and native library hashes have not been verified locally. A drop-in engine replacement would require reimplementing 44 JNI contracts plus rendering, asset decoding, and runtime behavior; that is a separate high-risk port, not a small modkit patch.

## Synchronization inventory — v14

- [Latest source-sync, AIM/HUD symbol audit, SKU evidence status, and native split blocker](docs/SYNC_STATUS_AND_NEXT_STEPS_V14.md)
- [Prior v13 inventory](docs/SYNC_STATUS_AND_NEXT_STEPS_V13.md)
- [Prior v12 inventory](docs/SYNC_STATUS_AND_NEXT_STEPS_V12.md)

The curated branch currently tracks only two `.smali` files (plus the inventory Markdown) and no generated `reconstruction/java/` scaffolds. It does **not** contain all 68 app-specific disassemblies or 68 Java declaration scaffolds mentioned in earlier local-bundle descriptions. CI checks are tied to the exact commit SHA; see the v14 sync report for latest validation status.

## Latest evidence reports — v14, v13, and v11

- [v14 AIM/HUD symbol inventory with hashes, offsets, and interpretation limits](docs/AIM_HUD_SYMBOL_AUDIT_V14.md)
- [v14 AIM/HUD printable-symbol scanner](tools/audit_aim_hud_symbols.py) and [tests](tests/test_aim_hud_symbols.py)
- [v13 purchase-to-entitlement evidence boundary and rerun instructions](docs/IAP_RUNTIME_ENTITLEMENT_EVIDENCE_V13.md)
- [Machine-readable 109-SKU matrix with runtime grant status on every row](docs/IAP_SKU_RUNTIME_EVIDENCE_V13.json)
- [Fail-closed v13 evidence validator](tools/validate_iap_runtime_evidence_v13.py) and [tests](tests/test_iap_runtime_evidence_v13.py)
- [Artifact scope, Smash.gam model registry, IAP trace, and native split/engine boundary](docs/ARTIFACT_RECONCILIATION_AND_NATIVE_ENGINE_V11.md)
- [SKU evidence summary and unresolved reward mapping](docs/IAP_SKU_ASSET_EVIDENCE_SUMMARY_V11.md)

The v13 registry matrix and validator are now tracked in this branch. All 109 SKU grants remain unverified: the native purchase callbacks have no DEX bodies, the matching native split has not been obtained, and the current evidence contains no per-SKU persisted-state transition. The local v10 ZIP's suite reruns as 35 passing tests while its historical validation metadata says 34; see the v13 sync report for that bookkeeping discrepancy.

## Reproduction and remaining blockers

The source tools support offline metadata extraction, DEX inventory/disassembly, Java declaration scaffolds, STK extraction/rebuild, and narrow asset patching. The repository does **not** claim complete original Java source, JNI implementations, bundle reward mapping, a full Gradle build, signing, emulator launch, or runtime equivalence.

The uploaded APK contained a credential-shaped `assets/api_key.txt`; its value is excluded from the repository and reports. Rotate/revoke it if it is active.

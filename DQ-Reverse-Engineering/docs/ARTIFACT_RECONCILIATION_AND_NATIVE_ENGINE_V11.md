# DQ Artifact, IAP, Smash.gam, and Native Boundary Audit — v11

Date: 2026-10-24  
Build analyzed: `com.shinybox.smash` v3.3.2.0, versionCode `1423433200`.

## 1. Repository vs archive scope

The `DQ-Reverse-Engineering/` tree is a curated public workspace, not a byte-for-byte mirror of the local analysis ZIP. PR #26's README was updated on 2026-10-24 (commit `73271b005914a3b6f980a66e1ebfeea7dbf4c94d`) to say that explicitly.

The v10 archive had 60 entries and 35,811,585 uncompressed bytes under `package/`. It contains the patched STK asset pack, IAP reports, tools/tests, and a standalone debug/sandbox preview. It does **not** contain the original APK, original STK, raw `classes.dex`, all 68 app-specific disassembly files, 68 Java declaration scaffolds, full extracted asset tree, or manifest excerpt. This v11 report documents that distinction; it does not claim full-disassembly synchronization.

Raw APK/DEX/native binaries and the credential-bearing `assets/api_key.txt` should remain excluded from the public repository. Text reports, parsers, tests, and cryptographic hashes are suitable for review.

## 2. `Games/Smash.gam`

- Size: 41,831 bytes; SHA-256: `2f6dc82699a0d7f34a67f0a6cfd89f71cb6adaff82fc7ed5945d7979499dc395`.
- Parsed module-name table starts at byte offset 21 and has 30 length-prefixed names, terminating at offset 498 (`0x1f2`).
- Priority module names include `InAppPurchase`, `uai_gp_options`, `uai_gp_debug`, `uai_gp_hud`, and `uai_gp_account`.
- The rest of `.gam` and compiled `.aim/.hud` formats remain only partially reversed. The v11 tool extracts the registry and printable symbols; it does not execute or fully disassemble their proprietary bytecode.

## 3. IAP identifiers, purchase flow, and rewards

Source counts for this build:

- `IAP.xml`: 107 rows/identifiers.
- DEX static SKU literals from the IAP wrapper: 104 unique.
- Shared between XML and DEX: 102.
- XML-only: `angelicslime`, `demonicslime`, `poisonslime`, `vanity72`, `vanity73`.
- DEX-only: `package20`, `package21`.

DEX-observed purchase routing: the IAP wrapper initializes the SKU list; purchase requests route through message IDs 600 or 602, restore routes through 601, and a handler dispatches to the observed purchase/restore helper methods. A helper retrieves product details and invokes an obfuscated billing-adapter method. This confirms a static request path, not proof of purchase verification or reward fulfillment.

The callback declarations `onPurchaseSuccess(String)` and `onPurchaseFailed(String)` cross into native code; their grant bodies are not present in this DEX. `InAppPurchase.aim` exposes purchase/restore callback symbols; `uai_gp_hud.aim` exposes `sPurchaseID`, `bPurchasing`, `onPurchaseSuccess`, shop helpers, and purchase callbacks; `uai_gp_account.aim` exposes `SetIAP`, `GetIAPString`, inventory, slot, and stash helpers. The actual call edge from these symbols to persisted account/player state remains unresolved until model bytecode or the native implementation is decoded.

Asset evidence that can safely be stated:

- 46 `vanityN` SKUs correlate with same-number `Vanity.xml` rows, including item/model names and price fields. This is an asset correlation, **not proof** of runtime ownership grant or persistence.
- `shopgold.hud` associates `gold1`–`gold5` with UI price labels `$0.99`, `$1.99`, `$4.99`, `$9.99`, `$19.99` and the card text “Removes ADs”. It does not reveal exact gold quantities or durable ad-removal entitlement writes.
- Contents/reward values for package SKUs, pets, boosts, stash, slots, randomized products, and the other non-cosmetic identifiers are unresolved. SKU names are not sufficient evidence to invent quantities, durations, or bundle contents.

Do not describe any product reward as runtime-verified based only on these data.

## 4. Options and debug evidence

- `uai_gp_options.aim` exposes option state and callbacks such as `onLoadOptions`, `onSaveOptions`, `onShowOptions`, `onSetControlsOption`, and `onSetGameplayOption`. `pause.hud` includes options UI callbacks, corroborating a settings path at symbol level.
- `uai_gp_debug.aim` exposes shader/log diagnostics such as `CompileShaderList`, `CompileShaders`, `onDebugLog`, and dump/cancel handlers. It should not be conflated with the gameplay debug panel.
- `debug.hud` contains debug/test labels and callbacks for creating CS/MS, adding levels/Feat, and toggling Crystal/Eternal/Boss flags. Asset presence does not prove a release-build route reaches this HUD.

## 5. Native dependencies and split status

The supplied base APK contains zero `lib/*.so` files. DEX load order is `crypto` → `ssl` → `openal` → `S3DClient`. Its manifest analysis excerpt declares required ABI and density splits.

Public APKPure metadata for v3.3.2.0 lists an arm64-v8a XAPK with `config.arm64_v8a` and an armeabi-v7a variant with `config.armeabi_v7a`; the listed shared signature fingerprint is `3f78ba3048cca9343b7c6da224114885c55e0d96`, and the arm64 XAPK SHA-256 shown by the site is `3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b` ([APKPure listing](https://apkpure.net/dungeon-quest/com.shinybox.smash/download)). The redirect to the XAPK payload could not be retrieved from this analysis environment, so the actual split files, their individual hashes, and the native libraries/dependency table are **not verified**. Android documents native libraries under `lib/<abi>/lib<name>.so` and explains config splits may carry native libraries ([split APK format](https://developer.android.com/guide/app-bundle/app-bundle-format), [NDK ABI guidance](https://developer.android.com/ndk/guides/abis)).

## 6. Replacement engine feasibility

A drop-in engine replacement is not realistic as the next modkit task. The wrapper declares 44 native methods (34 on `S3DRenderer`) and delegates the rendering loop and proprietary asset loading to `S3DClient`. A replacement would need to reimplement JNI contracts, rendering, scenes, models, animation, input/audio, and engine-specific resource formats, then establish runtime equivalence. The practical next step is to obtain the correct signed split set and inspect all native library headers/dependencies rather than fabricate placeholder shared libraries.

## Reproducibility

The current local v11 package adds the symbol audit script, full 107-row source SKU matrix, JSON reports, and regression tests. Its verification script checks the module count, SKU row count, base-APK native-library inventory, and explicitly unresolved native reward boundary. No complete APK build/install or gameplay runtime test is claimed.

# Native IAP Grant and Persistence Trace — v15

Date: 2026-10-24  
Target: `com.shinybox.smash` v3.3.2.0 / versionCode `1423433200`.

## Evidence source

The uploaded XAPK contains the matching `config.arm64_v8a.apk`; its four native libraries have been hash-identified in [NATIVE_SPLIT_AUDIT_V15.json](NATIVE_SPLIT_AUDIT_V15.json). The application engine used for this analysis is `libS3DClient.so`, SHA-256 `0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083`. The binary itself is deliberately not copied into GitHub.

## Verified purchase result chain

Static ARM64 disassembly shows:

1. `IAPWrapper.onPurchaseSuccess(String)` JNI export at `0x1e5b68` calls `S3DClient_SendEventToCurrentUser` at `0x7aea00`.
2. The event is named `InAppPurchase.onPurchaseSuccess`; the native model method is `InAppPurchase::onPurchaseSuccess` at `0x41c254`.
3. The model reads `sAIHandler` (variable referenced at AIM byte offset 24) and dispatches the notification through the engine.
4. `uai_gp_hud::onPurchaseSuccess` exists at `0x736ea4` and contains the product branches detailed below. The actual runtime value/binding of `sAIHandler` is not encoded as a static constant in the inspected bytes; the last connection is therefore **INFERRED**, not runtime-verified.
5. Failure, refund, and restore-completion JNI exports at `0x1e5abc`, `0x1e5c14`, and `0x1e5cc0` also send engine events.

The Java-side request routes remain the verified DEX routes: message 600 → `IAPWrapper.l(String)`; message 602 → `IAPWrapper.m(String, boolean)`; restore message 601 → `IAPWrapper.n()`.

## Gold pack amounts: STATIC-DIRECT

The five distinct currency packs call `uai_gp_hud::RewardGold(S3DX::AIVariable)`. A 64-bit immediate argument is a double-encoded Gold quantity; no name-based inference is required.

| SKU | Product branch | `RewardGold` call site | Gold amount | Status |
|---|---:|---:|---:|---|
| `gold1` | `0x737070` | `0x7370d0` | 20,000,000 | STATIC-DIRECT |
| `gold2` | `0x7371b8` | `0x737218` | 50,000,000 | STATIC-DIRECT |
| `gold3` | `0x737300` | `0x737360` | 150,000,000 | STATIC-DIRECT |
| `gold4` | `0x737448` | `0x7374ac` | 350,000,000 | STATIC-DIRECT |
| `gold5` | `0x737594` | `0x7375f4` | 1,000,000,000 | STATIC-DIRECT |

These are statically decoded reward arguments. They are **not** runtime-observed balance changes.

## Corrected SKU family classification

The earlier data-only catalog incorrectly grouped some short identifiers by their names. Native state references show:

| SKU | Observed native state references | Correct classification | Known / unknown |
|---|---|---|---|
| `gold` | `iap.boostGold`, `nGoldBoost`, `iap.boostPurchased` | Gold boost | Boost state referenced; duration/value and stacking still unknown |
| `crystal` | `iap.boostCS`, `nCSBoost`, `iap.boostPurchased` | Crystal/CS boost | Not proven to be a direct Crystal currency grant |
| `mythstone` | `iap.boostMS`, `nMSBoost`, `iap.boostPurchased` | Mythstone/MS boost | Not proven to be a direct Mythstone currency grant |
| `exp` | `iap.boostExp`, `nExpBoost` | EXP boost | Runtime amount/duration unknown |
| `luck` | `iap.boostMf`, `nLuckBoost` | Luck/MF boost | Runtime amount/duration unknown |
| `pickup` | `iap.boostPU`, `nPUBoost` | Pickup boost | Runtime effect/duration unknown |
| `petboost` | `iap.boostPet`, `nPetBoost` | Pet boost | Runtime effect/duration unknown |
| `hunter` | `iap.boostHunter`, `nHunterBoost` | Hunter boost | Runtime effect/duration unknown |
| `multi` | references all eight boost flags/variables | Multi-boost bundle candidate | Exact multipliers/duration/stacks unknown |
| `autoreveal` | `iap.autoReveal`, model `uai_gp_minimap`, handler `onRevealAll` | Map reveal | Static target handler references present; runtime action not tested |

Native code references `iap.boostPurchased` for individual boost branches. The precise values, duration, reset semantics, and effect stack rules require closer native control-flow analysis or a controlled game-state diff.

## Bundle contents directly referenced by the success handler

The following are the component vanity IAP keys reached under the listed product branch. This is static evidence for the component key set; any additional benefit (including ad removal) is not included unless directly evidenced.

| SKU | Referenced vanity keys |
|---|---|
| `package1` / `special` | `iap.vanity1`, `iap.vanity16`, `iap.vanity24`, `iap.vanity32` |
| `package2` | `iap.vanity2`, `iap.vanity17`, `iap.vanity25`, `iap.vanity33` |
| `package3` | `iap.vanity3`, `iap.vanity18` |
| `package4` | `iap.vanity4`, `iap.vanity19` |
| `package5` | `iap.vanity5`, `iap.vanity20` |
| `package6` | `iap.vanity6`, `iap.vanity21` |
| `package7` | `iap.vanity7`, `iap.vanity22` |
| `package8` | `iap.vanity8`, `iap.vanity23` |
| `package9` | `iap.vanity9`, `iap.vanity27` |
| `package10` | `iap.vanity10`, `iap.vanity28` |
| `package11` | `iap.vanity11` |
| `package12` | `iap.vanity12`, `iap.vanity29` |
| `package13` | `iap.vanity13`, `iap.vanity30` |
| `package14` | `iap.vanity34`, `iap.vanity37` |
| `package15` | `iap.vanity35`, `iap.vanity38` |
| `package16` | `iap.vanity36`, `iap.vanity39` |
| `package17` | `iap.vanity4`, `iap.vanity19`, `iap.vanity7`, `iap.vanity22`, `iap.vanity8`, `iap.vanity23` |
| `package18` | `iap.vanity3`, `iap.vanity18`, `iap.vanity5`, `iap.vanity20`, `iap.vanity6`, `iap.vanity21` |
| `package19` | `iap.vanity34`, `iap.vanity37`, `iap.vanity35`, `iap.vanity38` |
| `package20` | `iap.vanity64`–`iap.vanity67` |
| `package21` | `iap.vanity68`–`iap.vanity71` |
| `special2` | `iap.vanity56`, `iap.vanity57`, `iap.vanity58` |
| `special3` | `iap.vanity64`–`iap.vanity67` |

`package20` and `package21` are DEX/native entries but have no `IAP.xml` row in this build. The native handler nevertheless contains the component branches; billing metadata and a valid product-detail request are still unverified.

## Pet branches and limits

The native success handler maps:
- `pet1` → `pet_dog4`
- `pet2` → `pet_imp4`
- `pet3` → `pet_fairy4`
- `pet4` → `pet_dog5`
- `pet5` → `pet_imp5`
- `pet6` → `pet_fairy5`

For `randomdog`, `randomimp`, `randomfairy`, and `randomslime`, the code references `uai_gp_combat::onGeneratePet` and the corresponding pet family, plus the purchase-success dialog path. The actual random selection, item persistence, and whether the generated pet exactly matches a promised product were not runtime-tested. The three XML-only IDs `angelicslime`, `demonicslime`, and `poisonslime` also appear as native product literals and in pet-generation branch groups, so “XML-only” only describes the mismatch with the DEX SKU literal registry.

## Account serialization: direct cloud sync path; local save remains unknown

Direct call-site analysis of `libS3DClient.so` gives:

- `uai_gp_account::onUpload` at `0x5346c0` calls `GetIAPString` at call PC `0x535028`.
- `uai_gp_account::onDownloadResult` at `0x509670` calls `SetIAP` at call PC `0x50b0a8`.
- `GetIAPString` and `SetIAP` reference `iap.gold1`–`iap.gold5`, boost flags, `iap.autoReveal`, `iap.slots`, `iap.vanity1`–`iap.vanity74`, `hires`, and `premium` keys (with corresponding field coverage differing by function).

This proves those functions participate in account upload/download serialization. It does **not** prove the game’s local save file writes each field, the save-file migration behavior, or that a live device successfully restores every entitlement.

## Replacement status and next test

- **UNIT-VERIFIED, data-only:** the separate STK patch converts all 46 IAP-linked vanity cosmetics to earned-Gold routes, adds a Gold price/listing for vanity72/73, and changes only decoded `Vanity.xml` and `Shop.xml`. All 5,630 decoded entries passed CRC/size round-trip checks; the 35-test V10 local unit suite passed.
- **NOT IMPLEMENTED:** removal of billing/purchase UI and purchase request paths from a buildable APK; no APK has been built or installed.
- **BLOCKED:** actual local-save semantics, exact boost amounts/duration/stacks, storage capacity changes, hire/quality effect, unconditional ad removal, and debug HUD reachability.
- **NEXT:** add native handler evidence to the machine-readable matrix, validate all account keys and bundle mappings, then use an Android rebuild toolchain to integrate and test one local reversible Sandbox action. Do not label any SKU runtime-verified without a live state diff and reload.

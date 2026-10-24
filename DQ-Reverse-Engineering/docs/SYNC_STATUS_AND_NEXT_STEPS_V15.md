# Dungeon Quest v3.3.2.0 — Sync and Verification Status v15

Date: 2026-10-24  
Repository: `orionrayy/projects`  
Branch: `feat/dq-iap-debug-cheats-modkit-v7`  
PR: [#26](https://github.com/orionrayy/projects/pull/26), still draft/open at the latest metadata check.

## Executive status

- **Native split recovery: STATIC-DIRECT.** The uploaded XAPK supplied the exact v3.3.2.0 base, ARM64 ABI split, and density split. All 20 APK members share one signer fingerprint. Four native libraries were extracted and ELF metadata/dependencies were inventoried; raw binaries remain local-only.
- **Native IAP trace: STATIC-DIRECT up to a dynamic model-handler boundary.** JNI success/failure/refund/restore event routes and a number of concrete reward-state branches are now mapped. The indirect `sAIHandler` destination remains `INFERRED`; local-save persistence and live mutation are not proven.
- **Canonical IAP matrix: 109 records.** 107 XML identifiers, 104 DEX static literals, 102 shared, five XML-only, two DEX-only. Static native payload mapping covers 5 exact Gold-pack amounts, 8 boost key/value pairs, and multiple bundle/pet/slot/reveal branches; it does not mean 109 products are fully understood.
- **Economy patch: IMPLEMENTED and UNIT-VERIFIED (data-only).** The output changes only `Resources/XML/Vanity.xml` and `Resources/XML/Shop.xml`. 46 IAP-linked cosmetic routes are present in the patched tables; Gold prices are proposals and require balancing.
- **Full IAP replacement: BLOCKED / NOT COMPLETE.** IAP identifiers, Java purchase routing, native callbacks, receipt handling, and ad code have not been removed or replaced. No altered APK has been built, signed, installed or runtime-tested.
- **Integrated Cheats/Sandbox: BLOCKED / NOT COMPLETE.** Existing debug asset labels and symbol strings do not prove Pause → Options reachability; no reversible game-state adapter has been wired into original UI.
- **Repository sync: PARTIAL.** This remains a curated source tree. It has two real `.smali` files, no 68-class generated Java scaffold directory, and no full decoded proprietary asset tree.

## Source identity and split audit

| Artifact | SHA-256 | Status |
|---|---|---|
| User-supplied XAPK | `3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b` | ZIP and package metadata verified |
| Base APK | `c7bd6ab38ed2827a3aadd4f415ffc994eb366fc1ce9d66742077d6ef5e954abc` | package/version verified |
| `config.arm64_v8a.apk` | `5cb55f369b1ab9af3752595c87fcbc8fafa9ec31cd8870a45645309f8c2a40c2` | ELF library container recovered |
| `config.xxhdpi.apk` | `0a49043f26b35966865cc646d72f894f063ea672cdcdbb952662536aa911ac62` | density split recovered |
| `libS3DClient.so` | `0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083` | ELF64 AArch64; static disassembly inspected |
| Original STK | `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3` | immutable input; 5,630 entries |
| Patched STK | `3c2d16566458009f0fa5eb4350b606a50e66b9542974b5d1b781f742c33b2d4d` | 5,630 CRC/decoded-size validations pass |

Signer SHA-256 fingerprint for the 20 APKs: `9A:28:A9:91:71:C8:F6:3F:34:11:E2:91:F6:D9:6F:13:D5:D9:C1:73:62:06:A0:CF:95:EB:EE:99:BC:31:42:1D`. This confirms matching signing certificates across the supplied set. No raw APK/native binaries or credential-shaped asset contents are committed.

## Canonical purchase-to-state map

- Java purchase requests: message 600 → `IAPWrapper.l(String)`; 602 → `IAPWrapper.m(String, boolean)`; restore 601 → `IAPWrapper.n()`.
- JNI success: `Java_com_shinybox_iap_IAPWrapper_onPurchaseSuccess @ 0x1e5b68` → `S3DClient_SendEventToCurrentUser @ 0x7aea00` → `InAppPurchase::onPurchaseSuccess @ 0x41c254`. The runtime `sAIHandler` target is dynamic and remains `INFERRED`.
- Gold packs `gold1`–`gold5` call `RewardGold` with 20M, 50M, 150M, 350M and 1B Gold respectively (**STATIC-DIRECT**, not runtime-observed balance changes).
- `gold`, `crystal`, and `mythstone` are boost-state branches, not proven currency grants. The boost effects/duration/stacking need measurement.
- Bundle IDs have statically decoded component vanity-key lists. Pet generation branches exist, but exact random result and inventory persistence remain unverified.
- `uai_gp_account::GetIAPString` is called in `onUpload`; `SetIAP` is called in `onDownloadResult`. That establishes an account/cloud serialization path, not a local-save file contract.

All reward grant and save-load statuses remain **not runtime-verified**. See [NATIVE_IAP_TRACE_V15.md](NATIVE_IAP_TRACE_V15.md) and [IAP_CANONICAL_MAPPING_V15.json](IAP_CANONICAL_MAPPING_V15.json).

## Economy patch and actual decoded-table check

The v15 patch is a standalone STK file at local path `/mnt/data/dq_v15_audit/patch/S3DMain_v15_vanity_earnability.smf`. It is not committed as a 34 MB binary and is not an APK. The source STK is untouched.

Actual local source/patch audit returned `PASS` using the decoded source and patched XML:
- 107 IAP rows, 74 Vanity rows, 51 source Shop rows → 53 patched Shop rows.
- 46 IAP-linked vanity IDs; none missing a Gold price or Shop Tab3 reference in the patched tables.
- Exactly `Vanity.xml` and `Shop.xml` differ; `IAP.xml`, `Items.xml`, and `Dictionary.xml` hashes remain unchanged.
- The full local reconciliation report SHA-256 is `faf9e07159a906686fdffe87a9a605a0f21386944ec7518ddf5596f89897079f`. The local report's join projection came from parsing the source table and the previous registry evidence; the committed canonical mapping is separately validated by CI.

The proposed prices are economy-balancing hypotheses. There has been no shop purchase/equip/reload test and no proof the existing game economy makes these costs fair.

## Evidence ledger

The ledger uses `STATIC-DIRECT`, `INFERRED`, `IMPLEMENTED`, `UNIT-VERIFIED`, `RUNTIME-VERIFIED`, and `BLOCKED`. It currently contains no `RUNTIME-VERIFIED` claims. The canonical matrix likewise records `runtime_grants_verified = 0` and `runtime_grants_unverified = 109`.

- [Evidence ledger](EVIDENCE_LEDGER_V15.json)
- [Canonical IAP mapping](IAP_CANONICAL_MAPPING_V15.json)
- [Native split hashes and ELF dependency inventory](NATIVE_SPLIT_AUDIT_V15.json)
- [Source/patch XML hash reconciliation](IAP_ASSET_RECONCILIATION_V15.json)
- [Local vs GitHub artifact manifest](SOURCE_ARTIFACT_MANIFEST_V15.csv)
- [Economy patch report](ECONOMY_PATCH_V15.md)

## CI and runtime validation boundary

The last complete successful GitHub Actions run before this sync-report update was [run 40091061144](https://github.com/orionrayy/projects/actions/runs/40091061144/job/120863649462) at commit `967d0a223ded806c40524cd3e949741fa13ae705`. It passed the canonical IAP mapping validator/tests, the v15 synthetic XML/SKU reconciliation tests, v13 and v14 tests, boundary checks, and Java stub compilation. Updating this status report/README will trigger a new workflow; the newest branch-head check must be inspected before claiming the new HEAD passed.

No Android SDK signing tools, ADB, emulator or connected device are available in this environment. Consequently, there is no installable modified APK and no launch, purchase, save, rollback, or gameplay runtime claim.

## Highest-value next steps

1. Add an actual `S3DMain.smf` generation target to a reproducible local build package and preserve exact input/output hashes.
2. Map remaining native grant branches: boost timing/effects, slot count semantics, stash, hires/ad removal, and random pet inventory/persistence.
3. Resolve the dynamic `sAIHandler` destination and local save path.
4. Implement one reversible sandbox adapter only after a real game-state owner plus save boundary is identified; the original UI connection remains unknown.
5. Package/build/sign all matching splits together only when Android tooling is available; perform install and controlled state-diff tests before promoting any SKU to `RUNTIME-VERIFIED`.

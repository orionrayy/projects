# IAP Runtime Entitlement Evidence — v13

Date: 2026-10-24  
Build: `com.shinybox.smash` v3.3.2.0 (`versionCode 1423433200`).

## What changed

A new [per-SKU JSON matrix](IAP_SKU_RUNTIME_EVIDENCE_V13.json) carries the existing 109-row identifier/replacement analysis forward while adding an explicit runtime-evidence object to every row. The inherited `migration_status` and `proposed_route` values are design classifications, **not** evidence that the behavior is implemented.

The matrix currently reports **0 runtime-reward-verified SKUs and 109 unverified SKUs**. Reward payloads are null, persisted entitlement writes are not observed, and runtime tests are not run. This avoids treating static product names, HUD labels, or asset matches as proof of what a purchase actually grants.

## Static purchase path that is established

- The IAP XML contains 107 unique identifiers; the DEX wrapper has 104 static SKU literals; 102 are shared.
- XML-only: `angelicslime`, `demonicslime`, `poisonslime`, `vanity72`, `vanity73`.
- DEX-only: `package20`, `package21`.
- Purchase request routes are message 600 → `IAPWrapper.l(String)` and 602 → `IAPWrapper.m(String, boolean)`; restore is 601 → `IAPWrapper.n()`.
- The purchase update path extracts the first product ID and calls `onPurchaseSuccess(String)` or `onPurchaseFailed(String)`. Both are native declarations without bodies in the supplied DEX.

## Asset correlation is not reward verification

46 `vanityN` identifiers correlate with same-suffix `Vanity.xml` rows. `gold1`–`gold5` have visible price/“Removes ADs” HUD labels, but those labels do not establish currency quantities or a persisted ad-removal entitlement. Package/pet/boost/slot/stash/random-product grants remain unmapped.

## Reproducible validation

Run:

```bash
python DQ-Reverse-Engineering/tools/validate_iap_runtime_evidence_v13.py
python -m unittest DQ-Reverse-Engineering/tests/test_iap_runtime_evidence_v13.py
```

The validator checks the 107/104/102 registry counts, exact mismatch sets, 46 vanity correlations, message routes, and the evidence contract. It fails closed if a SKU is marked `VERIFIED` without a concrete payload, observed persisted entitlement write, passing runtime test, and evidence references.

## Validation bookkeeping correction

I re-ran the local `DQ_Modkit_v10_IAP_Flow_Trace.zip` test suite with unittest discovery: **35 tests passed**. Its packaged `reports/validation_v10.json` still says `test_count: 34`; that field is stale by one. This is a bookkeeping discrepancy, not a failed test. The run was local static/unit validation only—no Android build, signing, installation, or gameplay test.

## Remaining blocker

To upgrade any row from unverified, recover the matching version/signature/ABI native split or equivalent native source, resolve the proprietary model callback edge where applicable, and perform a controlled runtime before/after state diff for that SKU. Do not infer grant amounts or fabricate ownership.

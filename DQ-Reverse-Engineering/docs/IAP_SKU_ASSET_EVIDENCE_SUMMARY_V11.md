# IAP SKU Evidence Summary — v11

This summary accompanies a local machine-generated 107-row matrix. It describes evidence associations; it does not claim that product rewards or entitlement writes are runtime verified.

## Registry reconciliation

| Measure | Count |
|---|---:|
| IAP.xml rows/unique identifiers | 107 |
| DEX static SKU literals | 104 |
| Identifiers shared by XML and DEX | 102 |
| XML-only identifiers | 5 |
| DEX-only identifiers | 2 |

XML-only: `angelicslime`, `demonicslime`, `poisonslime`, `vanity72`, `vanity73`.  
DEX-only: `package20`, `package21`.

## What asset evidence establishes

- **46 vanity SKUs:** each `vanityN` links by numeric suffix to a `Vanity.xml` row with cosmetic label, slot, model identifiers, and source price fields. This is an asset correlation only, not proof of the runtime grant or persistence path.
- **`gold1`–`gold5`:** `shopgold.hud` shows labels `$0.99`, `$1.99`, `$4.99`, `$9.99`, `$19.99`, and “Removes ADs”. It does not show gold quantities or prove an entitlement is persisted.
- **Package, pets, boosts, stash, slots, random products, other single-ID products:** exact reward payloads remain unresolved in the readable source evidence. Do not infer exact quantities, duration, or bundle composition from the SKU name.

## Purchase-to-state boundary

Static DEX confirms SKU list initialization, purchase-message routing (600/602), and restore routing (601). The purchase helper calls an obfuscated billing adapter. The success/failure/refund grant callback bodies are native and absent from DEX. `uai_gp_hud.aim` and `uai_gp_account.aim` expose candidate purchase/account state symbols, but the custom model bytecode is not yet decoded. No current row is marked runtime-reward-verified.

See [full artifact, IAP, and native boundary audit](ARTIFACT_RECONCILIATION_AND_NATIVE_ENGINE_V11.md).

# IAP SKU Reconciliation — v7

## Exact cross-source finding

The uploaded v3.3.2.0 artifact contains 104 distinct static SKU strings in classes.dex and 107 product-name rows in Resources/XML/IAP.xml. The exact observed reconciliation is 102 shared names, 5 XML-only names and 2 DEX-only names (109 unique identifiers in the union).

| Set | Identifiers |
|---|---|
| IAP.xml only | angelicslime, demonicslime, poisonslime, vanity72, vanity73 |
| DEX only | package20, package21 |

The five XML-only identifiers must not be treated as proof of active store products. Vanity rows 72 and 73 have no Price or Gold value in the extracted table, are absent from the DEX SKU strings, and are not referenced by the observed Shop.xml Tab3 list. The two DEX-only package IDs have no matching IAP.xml row. These are reconciliation defects or legacy entries to resolve, not reasons to auto-delete assets.

## First earnability patch

The Vanity.xml table has 74 rows. Sixteen rows have numeric Price and blank Gold; the draft patch writes proposed Gold prices and clears Price. The other 28 Vanity SKU rows that already have Gold remain untouched. The 16 conversions are recorded in COSMETIC_EARNABILITY_PATCH_DRAFT.json.

## Family-level replacement policy

| SKU family | Proposed route | Status |
|---|---|---|
| Gold packs | Ordinary drops, first-clear rewards, repeatable bounty contracts and balanced gold income | Route designed; grant amounts and economy need playtest |
| Character slots | Permanent campaign/achievement milestone unlocks | Exact per-SKU semantics need source/runtime verification |
| Stash / premium stash | Permanent earned vault upgrades using gold and existing materials | Capacity values and limits unresolved |
| Auto map reveal | Cartographer challenge / exploration milestones | Confirm exact side effects |
| Vanity | Deterministic selection using existing Gold prices or newly proposed earned Gold costs | 16 rows converted in local asset copy; not yet runtime-tested |
| Pets / pet boosts / random pets | Deterministic pet unlocks, earned consumables, duplicates converted to shards | Exact roster and effects unresolved |
| Exp/Hunter/Luck/Multi boosts | Earned or craftable consumables with visible duration and stacking limits | Effects need verification |
| Crystal/Mythstone/Pickup | Existing resource loops or permanent convenience unlock | Exact SKU grant unknown |
| Hires | Free option if graphics quality, otherwise verify the content entitlement | Blocked pending evidence |
| Package 1–21 and Special variants | Expand each bundle into individually mapped benefits first | Blocked; contents unresolved |

## Validation boundary

The local patched pack validated all 5,630 entry CRCs and decoded sizes and compared all unchanged entries after rebuilding. CI currently tests the pack writer on synthetic fixtures and the patcher on synthetic Vanity XML. No complete Android project build, signing, installation or live gameplay test is claimed.
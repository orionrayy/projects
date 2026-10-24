# IAP Product Identifier Inventory

The DEX class initializer for com.shinybox.iap.IAPWrapper contains 104 distinct SKU strings. The IDs are hard-coded static metadata and do not prove that products are currently active in a store, what their prices were, whether a purchase succeeds, or whether a server grants entitlements.

| Inferred family | Count |
|---|---:|
| Vanity / cosmetics | 44 |
| Packages / bundles | 21 |
| Pets | 7 |
| Storage slots | 7 |
| Gold / currency | 6 |
| Randomized pet/item | 4 |
| Special items | 3 |
| Other single-ID families | 12 |
| **Total** | **104** |

Representative observed IDs include:

- com.shinybox.dq.gold, gold1, gold2, gold3, gold4, gold5
- com.shinybox.dq.hires, hunter, multi, pickup, crystal, exp, luck, multiboost, mythstone
- com.shinybox.dq.pet1 through pet6 and petboost
- com.shinybox.dq.package1 through package21
- com.shinybox.dq.slot and slot1 through slot6
- com.shinybox.dq.pstash and stash
- com.shinybox.dq.vanity1 through vanity33, plus vanity56 through vanity71 and additional observed IDs
- com.shinybox.dq.randomdog, randomimp, randomfairy, randomslime
- com.shinybox.dq.autoreveal, special, special2, special3

Number ranges above summarize families; the authoritative complete 104-item list and their individual observed category assignments are in the local analysis bundle. Gaps in numeric suffixes are intentional observations, not proof of missing products.

The uploaded APK also contains an Amazon token asset; the credential-bearing file and its value are intentionally excluded from both the repository and the analysis bundle.

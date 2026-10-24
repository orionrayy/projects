# IAP Grant Evidence & Fair Replacement Matrix — v8

## Actual data-level change

All 46 IAP-linked `Vanity.xml` rows now have an earned-Gold route: 16 rows previously priced in cash have proposed Gold prices; 28 rows retain existing Gold prices; and two previously unpriced IAP rows (`vanity72` / Spooky Jack Skin and `vanity73` / Creepy Eye Skin) receive proposed prices of 500,000 and 250,000 Gold and are added to `Shop.xml`. The Tab3 listing grows from 51 to 53 rows.

The source `IAP.xml` is intentionally unchanged. Removing SKU registration without updating native/UI purchase behavior would not constitute a safe, complete IAP replacement.

## Product family route and evidence

| Family | Evidence | Proposed fair route | Status |
|---|---|---|---|
| Vanity | SKU suffix maps to a direct Vanity row; cost fields are explicit. | Direct selection for earned Gold. | 46/46 mapped in the patched data |
| Reveal map | Dictionary Tip 11 describes purchasing Reveal Map to find exits. | Cartographer milestone or free per-map reveal. | Design only; native callback unchanged |
| EXP boost | Dictionary Tip 12 and shop callbacks mention EXP boost. | Earned/craftable timed boost with explicit duration and stacking rules. | Grant/duration not recovered |
| Character slots | Dictionary Tip 16 says new save slots allow more characters. | Deterministic campaign/achievement unlock. | Exact per-SKU grant not recovered |
| Shared/premium stash | Inventory HUD exposes Get Shared Stash, Get Premium Stash, all six shared stashes, and resource-specific stash labels. | Permanent unlocks through progression or earned currency. | Exact SKU-to-capacity mapping unresolved |
| Gold packs | shopgold HUD contains gold1–gold5 purchase controls. Dictionary Tip 4 says all purchases remove ads. | Gold is already earnable; balance gameplay income before hiding paid pack UI. | Product quantities and ad-entitlement implementation unresolved |
| Pets | Pet Shop tab and pet-related callbacks are present. | Deterministic pet choice/unlock or earned shards rather than paid random-only acquisition. | Exact product-to-pet mapping unresolved |
| Crystals/Mythstones | Existing resource systems appear in Dictionary and item data. | Drops, crafting, salvage, and bounty rewards. | Paid grant quantities unresolved |
| Pickup/Hunter/Luck/Multi boosts | Related names and some HUD behavior exist, but exact SKU grants are not proven. | Earned/craftable consumables or permanent options after effects are verified. | Partial/ambiguous; no automatic migration |
| Packages/Special | Package identifiers exist; one HUD label describes a Shock Pack including Shock Eyes, Shoulders, and ad removal, but its package SKU mapping is unknown. | Expand each bundle into exact deterministic components. | Blocked pending grant mapping |
| hires | Product ID only; exact semantics not recovered. | Resolve whether it is a visual-quality or content entitlement first. | Blocked |

## Identifier reconciliation

The current APK's DEX contains 104 static SKU strings; `IAP.xml` contains 107 identifiers. They share 102 names. XML-only identifiers are `angelicslime`, `demonicslime`, `poisonslime`, `vanity72`, and `vanity73`. DEX-only identifiers are `package20` and `package21`. Unknown rows remain explicit review items; they are not silently deleted.

## Ad-removal dependency

Dictionary Tip 4 says “All purchases made in the game remove ADs!” A true no-IAP build must make ad removal unconditional or provide a separately earnable equivalent. This data patch does not alter AdMob wrappers, ad behavior, billing callbacks, receipts, JNI code, or the original Pause → Options UI.

## Validation boundary

The source and rebuilt STK v6 packs each contain 5,630 entries. The writer validates CRC and decoded-size for all entries, and compares decoded content of every unchanged entry. The patched asset pack is not a signed/installable APK; no gameplay runtime test is claimed.

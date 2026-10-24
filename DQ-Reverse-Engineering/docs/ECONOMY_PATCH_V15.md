# Economy Patch v15 — Vanity Earnability Batch

Date: 2026-10-24  
Target data: Dungeon Quest 3.3.2.0 `S3DMain.smf`.

## Scope

This is a **data-only** patch for all 46 IAP-linked vanity cosmetics. It does not remove the DEX/native billing flow, change receipts, patch native libraries, or produce an APK.

| Measure | Result |
|---|---:|
| Source STK SHA-256 | `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3` |
| Patched STK SHA-256 | `3c2d16566458009f0fa5eb4350b606a50e66b9542974b5d1b781f742c33b2d4d` |
| Patched STK size | 34,011,490 bytes |
| Decoded entries checked | 5,630 |
| Decoded entries changed | 2 |
| Decoded entries unchanged | 5,628 |
| Entries passing CRC/decoded-size checks | 5,630 |
| IAP-linked vanity rows | 46 |
| Vanity rows converted from cash price to proposed Gold | 16 |
| Existing Gold-priced vanilla rows preserved | 28 |
| Previously unpriced items resolved | 2 |
| Remaining IAP-linked Vanity rows without Gold route | 0 |
| `Vanity.xml` rows | 74 |
| `Shop.xml` rows | 53 |
| `IAP.xml` rows | 107 |

Only `Resources/XML/Vanity.xml` and `Resources/XML/Shop.xml` differ in decoded content. `IAP.xml`, DEX, native libraries, receipts, and billing code are untouched by this pack patch.

## Proposed Gold price tiers

| Legacy cash price | Proposed Gold |
|---:|---:|
| $0.99 | 250,000 |
| $1.99 | 500,000 |
| $2.99 | 750,000 |
| $3.99 | 1,000,000 |
| $5.99 | 1,500,000 |

These values are balancing proposals, not gameplay-verified prices. The two previously unpriced vanity rows were assigned proposed Gold costs and inserted into `Shop.xml`:
- `vanity72` — Spooky Jack Skin — 500,000 Gold.
- `vanity73` — Creepy Eye — 250,000 Gold.

## Validation

- The STK packer decoded/rebuilt and revalidated all 5,630 entries; all CRC-32 and decoded-size checks passed.
- The V10 local unit suite ran 35 tests; all passed.
- The standalone economy validator returned `PASS` with no IAP-linked Vanity row lacking a Gold route.
- The patch report records the output hash and modified-entry list.

Downloadable output pack (asset pack only; **not an installable APK**): [S3DMain_v15_vanity_earnability.smf](sandbox:/mnt/data/dq_v15_audit/patch/S3DMain_v15_vanity_earnability.smf).

## Status and gap

- Patch generation: `IMPLEMENTED`.
- Pack/data invariants: `UNIT-VERIFIED`.
- Shop purchase/equip/reload in a running game: not tested.
- Full IAP replacement: **not achieved**. Other products, ad-removal behavior, boosts, pets, slots, stash and the billing entry points still require work.

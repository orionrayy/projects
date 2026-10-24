# Extracted Asset Catalog

The archive `assets/S3DMain.smf` was fully decoded to a separate local assets package using `tools/stk_unpacker.py`. All 5,630 entries passed CRC-32 and decoded-size validation. The extracted files are not copied into this code-focused GitHub directory.

## Container totals

| Property | Verified value |
|---|---:|
| Input size | 33,978,539 bytes |
| Entry count | 5,630 |
| Total decoded bytes | 94,513,994 |
| Zlib + XOR entries | 5,619 |
| Raw + XOR entries | 11 |
| SHA-256 | `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3` |

## Top-level groups

| Folder | Files |
|---|---:|
| `Resources` | 4,231 |
| `Models` | 1,375 |
| `Scenes` | 17 |
| `Plugins` | 6 |
| `Games` | 1 |

## Common formats

| Extension | Files | Decoded bytes |
|---|---:|---:|
| `.dds` | 550 | 33,942,053 |
| `.atc` | 526 | 18,596,120 |
| `.pvr` | 526 | 9,338,072 |
| `.etc` | 248 | 14,906,528 |
| `.mdo` | 1,375 | 1,301,127 |
| `.msh` | 631 | 6,838,331 |
| `.mat` | 611 | 99,136 |
| `.aim` | 162 | 187,079 |
| `.ani` | 140 | 1,593,920 |
| `.ske` | 137 | 234,543 |
| `.snd` | 100 | 1,859,573 |
| `.hud` | 68 | 933,064 |
| `.scn` | 17 | 176,535 |
| `.mus` | 7 | 3,028,402 |

The full path/size/CRC/SHA-256 inventory is generated locally as `asset-inventory.json` and `asset-inventory.csv`. Those detailed files are large and are omitted from the public repository to keep the repo compact.

## Readable XML tables

The `Resources/XML/` folder has 17 well-formed XML files and 2,623 `Row` records in total:

| File | Rows |
|---|---:|
| `Affixes.xml` | 524 |
| `Animations.xml` | 56 |
| `Crystals.xml` | 20 |
| `Dictionary.xml` | 516 |
| `Feats.xml` | 26 |
| `IAP.xml` | 107 |
| `Items.xml` | 163 |
| `Legends.xml` | 478 |
| `Mythics.xml` | 40 |
| `Mythstones.xml` | 20 |
| `Rarities.xml` | 7 |
| `Sets.xml` | 64 |
| `Shop.xml` | 51 |
| `Skills.xml` | 136 |
| `Stats.xml` | 239 |
| `Talents.xml` | 102 |
| `Vanity.xml` | 74 |

These tables expose readable game data (items, skills, stats, affixes, legends, talents, shop/IAP identifiers, dictionary/localization keys). They are data, not Java/JNI engine source.

## What remains binary

`.gam`, `.mdo`, `.msh`, `.ske`, `.scn`, `.aim` and related files were extracted byte-for-byte after archive decoding but not decompiled into their full internal schemas. The native engine implementations are also not present in the DEX. See `STK_FORMAT_FINDINGS.md` and `NATIVE_ENGINE_BOUNDARY.md`.

# Dungeon Quest Modkit — v7 checkpoint

This is a source-level reverse-engineering/modding workspace, not a complete original Android source tree. Keep modifications reproducible and keep the supplied APK and original pack immutable.

## Implemented utilities

- **tools/stk_unpacker.py**: existing, validated STK v6 parser/extractor.
- **tools/stk_packer.py**: new STK v6 pack writer. Rebuilds to a separate output, checks CRC and decoded lengths, and compares every decoded entry after a rebuild.
- **tools/apply_cosmetic_earnability_patch.py**: narrow XML patch which maps cash-only Vanity.xml rows to proposed gold costs. It does not disable IAP callbacks or alter IAP.xml.

## What was verified against the supplied 3.3.2.0 pack

- Container: 5,630 entries; all source entries passed CRC-32 and decoded-size checks.
- Vanity table: 74 rows; 16 rows had a numeric Price and blank Gold. The patch maps those 16 rows to Gold tiers and clears their Price field.
- A rebuilt pack passed entry validation and decoded-content comparison for every unchanged entry.
- Synthetic regression tests cover rebuild, replacement, path safety, missing targets, CRC errors, cosmetic conflicts and unknown price tiers.

## Proposed balance tiers

| Price field | Proposed gold cost |
| ---: | ---: |
| 0.99 | 250,000 |
| 1.99 | 500,000 |
| 2.99 | 750,000 |
| 3.99 | 1,000,000 |
| 5.99 | 1,500,000 |

These values are a balance proposal, not original game values. Test gold earning rate and completion time before treating them as final.

## Run locally

    python DQ-Reverse-Engineering/tools/stk_unpacker.py S3DMain.smf --extract extracted
    python DQ-Reverse-Engineering/tools/apply_cosmetic_earnability_patch.py extracted patched-assets --report cosmetic-report.json
    python DQ-Reverse-Engineering/tools/stk_packer.py S3DMain.smf patched.smf --replace Resources/XML/Vanity.xml=patched-assets/Resources/XML/Vanity.xml --report pack-report.json
    python DQ-Reverse-Engineering/tests/test_stk_packer.py
    python DQ-Reverse-Engineering/tests/test_cosmetic_patch.py

## Explicit limits

This iteration only changes cosmetic data. It does not remove the 104 SKU declarations or 107 IAP rows, patch billing callbacks, decode all bundle contents, change JNI engine implementation, connect the cheat catalog to gameplay, or produce a signed APK. The repository contains partial DEX reconstruction and tools, not a full buildable original project. Do not claim runtime activation until a compatible complete Android project and native library set are available and the build is tested.

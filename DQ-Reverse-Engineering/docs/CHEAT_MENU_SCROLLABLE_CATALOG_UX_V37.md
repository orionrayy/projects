# DQ Cheat Menu UX Workbench v37 — validation report

**Status:** UI/catalog prototype updated; no APK/XAPK built in v37.

## Artifact

- HTML: `Dungeon_Quest_Cheats_Sandbox_Workbench_v37_SCROLLABLE.html`
- SHA-256: `a0faae2306ba150d26b7bb5b5bc972bd7814289407008cf8dd1025c10479b1d2`
- Size: 171,809 bytes
- Catalog JSON: `debug_cheats_catalog_v37.json`
- Catalog IDs: 222 unique entries across 14 categories

## Changes from v36

1. Generic numeric steppers now mean the **actual displayed unit**: `−10`, `−1`, `+1`, `+10`. They no longer mean ten configured steps. The value is clamped to min/max and snapped to the declared valid step.
2. For normalized percentages in the 0–1 data range (e.g. critical chance 0.05), `+1` means +1 percentage point and `+10` means +10 percentage points. For percentage units already represented 0–100 (or broader), the buttons use the stored percentage-point unit directly.
3. Numeric values and bounds display their units (×, %, HP, level, Gold, seconds, etc.). Range controls format both endpoints and use the same unit-aware steppers while enforcing min ≤ max.
4. Gold remains a custom, button-built numeric keypad; it does not rely on the Android system keyboard. Applying Gold changes the local draft only.
5. Added more explicit design-intent descriptions for 19 previously terse settings and semantic search tags for all entries that previously had no tags.
6. Expanded the technical-details panel to show declared parameters, allowed options, default, bounds, step, unit, conflict group, scope and adapter status.

## Catalogue inventory

| Category | Count |
|---|---:|
| Player & Survival | 27 |
| Combat Lab | 24 |
| Enemy AI | 20 |
| Loot & RNG | 19 |
| Economy Lab | 17 |
| Progression Lab | 16 |
| Inventory & Gear | 16 |
| Spawn & Encounter Lab | 9 |
| World & Physics | 22 |
| Camera & Visuals | 15 |
| UI & Accessibility | 3 |
| Skills Lab | 9 |
| Gear & Stats Lab | 7 |
| Debug Tools | 18 |
| **Total** | **222** |

All 222 IDs are unique. All entries remain marked as requiring a verified game adapter; no runtime effect is falsely marked implemented.

## Numeric contract checks

- Max Health Multiplier 1× +1 → 2×.
- Max Health Multiplier 1× +10 → 11×.
- Critical Chance 5% +1 percentage point → 6%.
- Critical Chance 5% +10 percentage points → 15%.
- Rarity Bonus 0% +1 → 1%.
- Gold custom keypad allows an integer target from 0 to 1,000,000,000 and stages it locally.

The workbench JavaScript passes `node --check`. Browser interactive retesting of changed v37 code was blocked by the current environment with `ERR_BLOCKED_BY_ADMINISTRATOR`. v36 had previously passed browser tests at 360×740, 430×900 and 1536×675; I do not claim full v37 browser QA until it can be run successfully.

## Integration boundary

v37 is a local/offline UX workbench, not the in-game menu. It explicitly displays `GAME LINK: DISCONNECTED`. Native audit v37 confirms the engine supports a native List element and script-facing List APIs for scrolling, item population, text and selection. The game still requires model/runtime code to populate the list and map selected stable IDs to real cheat handlers. The custom in-game Gold keyboard → commit → authoritative balance path is not yet proven.

**Per the user's instruction, no new APK/XAPK was built.**

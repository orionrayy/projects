# Cheat Menu Workbench v39 — UI and catalogue validation

Status: UI/catalogue prototype passes local browser validation. No APK/XAPK was built, per the user's instruction to finish the menu before packaging.

## Deliverables

- Workbench: cheats_options_workbench_v39.html
- Catalog: debug_cheats_catalog_v39.json
- HTML SHA-256: d83619d43a92bbc50263f4affacecf81b514d7e6961e46dfc51652cade8cad70
- Catalog SHA-256: 221b1c33a70aea68d2cd9439a6910082e3ecd2e08280be4ccb4aba957e680342

## Catalogue validation

- 222 entries, 222 unique stable IDs, 14 categories.
- Control types: 119 toggles, 77 sliders, 11 selects, 9 actions and 6 ranges.
- Every entry has a label, description and tags; all entries remain marked requires_game_adapter.
- Numeric bounds/steps/defaults and range ordering validate; select defaults are members of their option sets.
- Current staging count is zero. Active (staging) filter returns zero entries before edits.
- Schema and interaction validation errors: zero.

| Category | Entries |
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
| Total | 222 |

## Responsive, internally scrollable UI

Automated browser tests ran at 360×740, 430×900 and 1536×675. At all viewports, all 222 cards render; the document body remains equal to the viewport height; the cheat list overflows internally and scrolls; outer page scroll remains zero; and no JavaScript errors occur.

| Viewport | Cards | Scroll area | Content height | Internal scroll | Outer scroll | JS errors |
|---|---:|---:|---:|---|---:|---:|
| 360×740 | 222 | 359 px | 54,583 px | PASS | 0 | 0 |
| 430×900 | 222 | 315 px | 53,536 px | PASS | 0 | 0 |
| 1536×675 | 222 | 427 px | 18,382 px | PASS | 0 | 0 |

## Interaction tests

- Gold custom button-keypad entry 123 stays exactly 123 and applies to a local draft; the field is read-only with inputMode=none, so it does not invoke the system keyboard.
- Generic steppers use displayed units: Crit Chance 5% → 6% with +1; Magic Find 0% → 1%; Telemetry Sample Rate 100% → 99% with −1; Health Multiplier 1× → 2× → 12× with +1, then +10.
- Range update preserves min ≤ max.
- Category filtering, details, favorites, clear filters, presets, undo, reset and JSON export pass.
- Export contains all 222 IDs and marks scope as local workbench only with gameAdapterConnected=false.

## Integration boundary

This is a workbench/catalog prototype, not integrated into Dungeon Quest and not a gameplay modification. All 222 entries stay blocked pending a verified game adapter. No APK/XAPK was made in v39.

Static native inspection confirms a native List element type and scrolling functions exist and that the keyboard callback reads keyboard.key_entry and sKeyboardDirect. But correct List population, row-action dispatch and the custom Gold input-to-authoritative-balance contract have not yet been established. See the native List/keyboard audit for details.
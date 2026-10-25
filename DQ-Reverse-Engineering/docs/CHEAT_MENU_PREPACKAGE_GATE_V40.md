# Cheat Menu pre-package gate — v40

Date: 2026-10-25  
Target: Dungeon Quest 3.3.2.0  
Decision: **No new APK/XAPK built.** The user explicitly asked to complete the menu/design before package builds.

## What the user requested since v33

1. Recover and implement the original 200+ cheat concept, not the six-card debug table.
2. A complete menu with 222 entries across 14 categories, specific descriptions and flexible controls.
3. One coherent Cheat Menu, not separate misplaced Gold buttons or a new isolated Gold tab.
4. An internally scrollable cheat list that does not scroll away the header, search, categories and action dock.
5. Gold uses a custom target amount. The edit flow must not rely on Android's keyboard in the game HUD; provide a button-built keypad for the design/workbench.
6. Other numeric cheats use button-only steps: −10, −1, +1, +10. No generic writable number fields that trigger the system keyboard.
7. Search, category/risk filtering, favorites, details, staged values, presets, undo/reset, logs and export.
8. Preserve v33 and the original `com.shinybox.smash` installation during future tests. Parallel package identity should be used when signing key differs.
9. Do not label a cheat functional merely because it is present in the UI; every game-side handler must be mapped and runtime-verified.

## v39 workbench status

- Full catalog: 222 unique stable IDs, 14 categories.
- Control types: 119 toggles, 77 sliders, 11 selects, 9 actions, 6 ranges.
- Mobile and landscape UI: browser-tested at 360×740, 430×900, and 1536×675.
- At every viewport: all 222 cards render, list scrolls internally, document body remains fixed to viewport, outer page scroll stays at 0, no JS errors.
- Interactions tested: Gold custom keypad draft, numeric steppers, min/max range invariant, category/search/favorite/detail filters, presets, undo, reset, and JSON export.
- Gold keypad value `123` stages exactly as `123`; `inputMode=none` avoids the system keyboard.
- Generic numeric examples: Crit Chance 5% → 6% (+1); Magic Find 0% → 1%; Telemetry 100% → 99% (−1); multiplier 1× → 2× → 12× (+1 then +10).
- Workbench explicitly declares game adapter disconnected and applies no changes to the original game.

## Native integration findings

- ARM64 engine exposes List methods including AddItem, SetItemTextAt, SetItemChildAt, SetItemsHeight, finger scrolling, smooth scrolling and auto-hide scrollbars.
- `HUDTemplate::LoadElements` has a List/type-3 record branch, but a validated lossless serializer plus dynamic row-population and selected-item action mapping is still missing. A string list alone does not create working cheat rows.
- `onKeyboardEnter` reads `keyboard.key_entry` and `sKeyboardDirect`, then routes through model environment-setting/slot update logic. The custom Gold route token and commit contract remain unresolved.
- `uai_gp_account::OpenKeyboard` call sites inspected so far belong to account nickname flows, not Gold input.
- `uai_gp_hud::onSetGold` formats/publishes the `hud.gold` display/model value; it is not proven to mutate authoritative Gold balance.
- Actual native Gold mutation helpers exist (`RewardGold` and `SpendGold`), but using them safely requires a verified current-balance read, amount semantics, validation, read-back and rollback.
- Therefore, do not ship a Set Gold button that just calls `onSetGold`, and do not build a 222-row HUD by guessing binary records.

## Status matrix

| Requirement | Status |
|---|---|
| 222-entry source catalog | COMPLETE |
| Internally scrollable workbench UI | COMPLETE / browser-tested |
| Generic button-only numeric steppers | COMPLETE in workbench / browser-tested |
| Gold custom button keypad | COMPLETE for local draft / browser-tested |
| Per-ID runtime evidence matrix | COMPLETE as an audit, 222 entries |
| Native List serialized record + AIM population contract | BLOCKED / under static reverse-engineering |
| Custom Gold input → authoritative balance mutation | BLOCKED / contract unverified |
| In-game 222-entry scrollable menu | NOT INTEGRATED |
| Gameplay cheat effects runtime-verified | 0 / 222 |
| APK/XAPK for this increment | NOT BUILT, by design |

## Downloadable source bundle

The source-of-truth prototype, JSON catalog, per-ID matrix, QA reports, screenshots, Playwright results and native List/keyboard/Gold audit are packaged in `DQ_Cheats_Menu_v39_UX_Bundle.zip`. Use the HTML to review the full menu before packaging; the HTML is a local workbench, not a modified game.

## Next gate

Continue the format/callback audit for native List row population and keyboard routing. Only when the menu layout is complete and those contracts can be represented without guessing should a small in-game integration build be considered. Keep unavailable handlers disabled with clear explanations.

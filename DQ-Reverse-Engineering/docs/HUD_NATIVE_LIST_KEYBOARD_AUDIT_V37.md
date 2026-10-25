# Native HUD List / Keyboard Feasibility Audit v37

Date: 2026-10-25  
Target: Dungeon Quest Android 3.3.2.0 / ARM64 libS3DClient.so  
Status: read-only reverse-engineering audit; **no APK/XAPK was built**.

## Executive finding

The game engine has native list/scrolling and internal keyboard support. That is a viable foundation for a 222-entry scrollable Cheat Menu and custom Gold input. It does not automatically provide the 222 rows, catalog bindings, or a Gold input → verified game-state mutation route. HUD elements/actions are serialized in .hud; model logic is compiled into proprietary .aim assets/native code. The available source-level bridge is not registered into the actual game engine.

## Evidence: native scrollable List element

| Function | Native VA | What it establishes |
|---|---:|---|
| HUDElement::ListEnableSmoothScrolling(bool) | 0x95c45c | Smooth scrolling option |
| HUDElement::ListEnableFingerScrolling(bool) | 0x95c48c | Touch/finger scrolling option |
| HUDElement::ListEnableMouseScrollWheel(bool) | 0x95c4bc | Mouse-wheel scrolling option |
| HUDElement::ListEnableScrollBarsAutoHiding(bool) | 0x95c51c | Auto-hide scroll bars |
| HUDElement::ListSetItemsHeight(float) | 0x95c204 | Row height configuration |
| HUDElement::ListAddItem(String const&, GFXTexture*) | 0x95b560 | Items are added by runtime code |
| HUDElement::ListSetItemTextAt(...) | 0x95bc98 | Row text can be changed at runtime |
| HUDElement::ListSetItemChildAt(...) | 0x95d980 | Child controls can be attached to list rows |
| HUDElement::ListScrollUp() | 0x95cc4c | Programmatic scroll up |
| HUDElement::ListScrollDown() | 0x95cc84 | Programmatic scroll down |
| HUDElement::SetType(Type) | 0x95c9e4 | Element-type dispatch |

In HUDElement::SetType, type ID 3 is routed to ListAddColumn() at 0x95c8ac; switching away from type 3 calls ListRemoveAllItems(). HUDTemplate::LoadElements has a matching type-3 parsing branch. This is strong static evidence that element type 3 is a native List control.

**Integration implication:** a List element does not populate itself with all 222 catalog items. ListAddItem is a runtime method. The game needs model/runtime code to enumerate stable IDs, populate rows, attach selection callbacks and details, and dispatch each item only to verified adapters. That dynamic population path and callback source are not yet implemented/recovered. A set of static labels without stable row-action wiring is not a complete menu.

## Evidence: internal keyboard pathway

ARM64 symbols include:
- uai_gp_hud::onKeyboard at 0x703154
- uai_gp_hud::onKeyboardEnter at 0x705940
- uai_gp_hud::onKeyboardDelete at 0x7055c0
- uai_gp_hud::onKeyboardClose at 0x704ba4
- uai_gp_hud::onKeyboardCaps at 0x703708
- uai_gp_hud::onGetGold at 0x6e8e00
- uai_gp_hud::onGetGoldClose at 0x6e93b0
- uai_gp_hud::onSetGold at 0x74ff84

Resources/HUD/keyboard.hud has 58 elements and four actions, including Enter/Delete/Close/Caps routed to uai_gp_hud. The native string table also contains sKeyboardDirect and bKeyboardOpen. Disassembly of onKeyboardEnter explicitly loads sKeyboardDirect before processing entered text, so the internal keyboard has a model-driven callback path.

### Important correction on onSetGold

onSetGold reads the hud.gold model key, converts an AIVariable using NumberToString, and formats/concatenates it for a model/UI operation. This is consistent with updating the displayed Gold field, but **does not prove it opens the keyboard or mutates the authoritative player Gold balance**. The previous Set Gold button was only a callback probe, not a validated numeric setter. The full keyboard open/commit/Gold mutation chain remains unproven. Do not wire this callback to a custom field by guessing semantics.

## HUD inventory context

| Resource | Elements | Actions |
|---|---:|---:|
| Resources/HUD/debug.hud (stock) | 71 | 13 |
| Resources/HUD/keyboard.hud | 58 | 4 |
| Resources/HUD/inventory.hud | 375 | 72 |
| Resources/HUD/shop.hud | 210 | 40 |
| Resources/HUD/profile.hud | 260 | 28 |

Complex HUDs exist in the pack, but their existence does not establish that the full List record can yet be serialized round-trip or that the list can be populated from compiled model logic by editing .hud bytes alone.

## Requested UX status

The separate v36 workbench has completed and passed browser QA:

- All 222 stable-ID cheats in 14 categories.
- Fixed application viewport with a dedicated internally scrolling list; outer page does not scroll.
- Header, search, category/filter controls and bottom actions remain visible.
- Generic numeric controls use −10, −1, +1, +10 with per-cheat bounds/step clamping.
- Gold uses a button-built on-screen numeric keypad; it does not rely on Android's system keyboard.
- Search, category/risk filters, favourites, details, presets, undo/reset, local event log and export tested.
- Viewports 360×740, 430×900, and 1536×675 passed; all 222 cards rendered, inner scroll works, keypad input 123 stages exactly 123, stepper smoke tests pass, and zero JavaScript errors were recorded.

Workbench SHA-256: 8bf8d37347563854104484f1b7cd58efda270aadaad0a0ae70f61dda2cea6f81. It explicitly displays GAME LINK: DISCONNECTED: this validates UX/draft logic, not gameplay effect.

## No-build rule / next gates

Per the user's instruction, **no new APK/XAPK is produced at this stage**.

1. Decode type-3 List element fields, scrolling flags, hit-targets and row templates, then add a lossless round-trip test for original HUDs.
2. Establish the .aim model event path that opens the keyboard and consumes sKeyboardDirect; identify a real numeric Gold commit route with state read-back.
3. Add a runtime catalog provider for all 222 rows and stable-ID selection/detail/actions inside the same Cheat Menu.
4. Apply the numeric button-only stepper pattern to other numeric controls, while keeping custom Gold separate.
5. Implement and verify each adapter individually: target build, argument schema, safety gates, state read-back and rollback. Unmapped actions stay disabled and visibly labelled.
6. Only after these design/integration gates are satisfied should another XAPK be built.

Purchase receipt/paid entitlement, cloud save, leaderboard, achievement and account mutation paths are not part of this audit.

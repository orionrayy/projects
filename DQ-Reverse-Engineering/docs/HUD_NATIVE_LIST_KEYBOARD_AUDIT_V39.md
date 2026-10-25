# Native List and custom keyboard contract — v39 continuation

Date: 2026-10-25
Scope: static analysis of supplied ARM64 libS3DClient.so and decoded v3.3.2.0 HUD/AIM assets. No APK/XAPK built.

## Native List finding

The element-type dispatch in HUDTemplate::LoadElements has a type-3 branch at VA 0x969644. It deserializes list-specific fields in the HUD element structure. HUDElement::SetType and the native symbol table corroborate a List control:
- ListAddItem VA 0x95b560
- ListSetItemTextAt VA 0x95bc98
- ListSetItemChildAt VA 0x95d980
- ListSetItemsHeight VA 0x95c204
- ListEnableSmoothScrolling VA 0x95c45c
- ListEnableFingerScrolling VA 0x95c48c
- ListEnableScrollBarsAutoHiding VA 0x95c51c
- ListScrollUp / ListScrollDown VAs 0x95cc4c / 0x95cc84

This supports the use of a native List as a future scroll container, but does not mean that putting 222 strings in a serialized record will create actionable cheat rows. Native APIs add items, set item text, and attach child rows at runtime. The compiled AIM model must enumerate catalog entries, populate rows, bind selection by stable ID, and connect detail controls to verified adapters. That model's source/call contract is still blocked. The HUD element record schema has not yet reached lossless round-trip coverage.

## Keyboard finding

The uai_gp_hud::onKeyboardEnter disassembly at 0x705940 looks up the model variables keyboard.key_entry and sKeyboardDirect. It branches based on AIVariable types and passes selected input/route data through model environment-setting logic, including setEnvVar at 0x5fdf5c and UpdateSlots at 0x63aa04. This is evidence of a data-driven callback route for the internal keyboard.

The remaining contract is unproven: the exact value for sKeyboardDirect, the model that should invoke the keyboard, which callback returns the submitted text, and the typed/validated pathway that mutates authoritative Gold. keyboard.hud has 58 elements and four actions; native callback names include onKeyboardEnter, onKeyboardDelete, onKeyboardClose and onKeyboardCaps.

## Gold flow caution

- uai_gp_hud::onGetGold at 0x6e8e00 references shopgold and shopgold.gold_text and operates on UI/model variables. This is evidence of a shop/gold UI path, not proof of a general custom Gold input.
- uai_gp_hud::onSetGold at 0x74ff84 operates on model variables and formats/publishes Gold display state. The function name alone does not establish that it opens the keyboard or writes the authoritative balance.
- Therefore, a button calling onSetGold without the surrounding model-state/input lifecycle is not an adequate custom Gold implementation. Do not build another APK until the callback contract is proven and the current UI/catalog work has been accepted.

## Decision

The workbench v39 is UI-ready at prototype level: 222 cards, 14 categories, independent internal scrolling, filter/search/favorites/details, keypad-based draft Gold, per-value stepper buttons, reset/undo/preset/export. Its connected-game status remains false. Next work should focus on the actual type-3 HUD record schema and AIM row-population/callback contract, while catalog entries without a proven native handler remain disabled.
# Native List script-API contract audit v44

Date: 2026-10-25  
Target: ARM64 \`libS3DClient.so\` from Dungeon Quest 3.3.2.0  
Status: native wrapper call shapes statically mapped; no AIM, HUD, APK, or XAPK was modified.

## Purpose

The v41–v43 passes established that the HUD binary can be parsed and that AIM v10 top-level record tables can be inventoried. This audit isolates the next integration boundary: the native List script APIs exist, but the model-side sequence that creates 222 rows and dispatches the selected stable ID has not been recovered or runtime-tested.

## Wrapper-level evidence

The following exported wrappers were located in the supplied ARM64 library. Addresses are virtual addresses within the library image. These are script-API wrapper functions, not standalone JNI entry points for an Android Activity.

| Script API wrapper | Native call / observed behavior | Confidence |
|---|---|---|
| \`hud_addListItem\` at \`0x87a980\` | Resolves the first argument to a HUD element; converts the second argument to text; calls \`HUDElement::ListAddItem(text, nullptr)\`; returns the new item index as a numeric value on success | Directly observed in disassembly |
| \`hud_setListItemTextAt\` at \`0x8c77e0\` | Resolves a HUD element, converts item/column index arguments, builds the text string, and calls \`ListSetItemTextAt(itemIndex, columnIndex, text)\` | Directly observed in disassembly |
| \`hud_setListOnSelectionChangedAction\` at \`0x862458\` | Resolves the List element and a separate HUDAction reference, then calls \`ListSetOnSelectionChangedAction(action)\` | Directly observed in disassembly |
| \`hud_getListSelectedItemAt\` at \`0x8a7f04\` | Resolves the List, accepts a selected-item ordinal argument, calls \`ListGetSelectedItemAt(ordinal)\`, and returns the item index | Directly observed in disassembly |
| \`hud_getListSelectedItemCount\` at \`0x862258\` | Resolves the List, calls \`ListGetSelectedItemCount()\`, and returns the count | Directly observed in disassembly |
| \`hud_enableListFingerScrolling\` at \`0x8620a8\` | Resolves the List and passes a boolean-like value to \`ListEnableFingerScrolling\` | Directly observed in disassembly |
| \`hud_enableListSmoothScrolling\` at \`0x861fd0\` | Resolves the List and passes a boolean-like value to \`ListEnableSmoothScrolling\` | Directly observed in disassembly |
| \`hud_enableListSingleSelection\` at \`0x861d48\` | Resolves the List and passes a boolean-like value to \`ListEnableSingleSelection\` | Directly observed in disassembly |
| \`hud_enableListItemSelectionAt\` at \`0x89ee24\` | Resolves the List, item index and selection toggle before calling the corresponding native List method | Directly observed in disassembly |

The wrappers consistently resolve the first argument as an engine-managed HUD element reference, with range checks against the current HUD manager's element registry. This is significant: the exported wrappers expect a valid in-engine HUD object and engine state. They are not safe direct calls from a separately installed Android app, and no Java/JNI call contract was inferred from them.

A source-asset cross-check inspected the action tables in all 68 v12 HUD files: none contains a call to these \`hud_addListItem\` / \`hud_setListItemTextAt\` / \`hud_setListOnSelectionChangedAction\` wrappers. This is a bounded negative result for the HUD action tables only; it does not rule out calls from other engine/model paths. At present, the recovered package provides no concrete serialized HUD action example to copy for the List population sequence.

## Implications for the 222-entry Cheat Menu

1. **Adding text rows is feasible at the native API level.** \`hud_addListItem\` uses a text item with a null texture; it does not automatically create a structured row with a toggle, slider, detail panel, risk label, or Apply action.
2. **Row selection uses a separate action reference.** The native callback API accepts a HUDAction object, not a catalog identifier or a Java callback. A model-side selection handler must obtain the selected item index, map it to a stable cheat ID, enforce eligibility and safety gates, and then update the detail/control state.
3. **One list needs explicit data population.** The engine can scroll, count selections and read selected indices, but the source \`pause.hud\` and \`debug.hud\` contain no type-3 List element. The one recovered type-3 element is a rank-up list in \`match_result_anim.hud\`; its row template/resources cannot be transplanted blindly.
4. **API presence is not gameplay support.** The 222 catalog entries remain specifications, not working runtime cheats. The game-side handler for each enabled control still requires exact-build call semantics, offline/disposable-save gates, state read-back and recovery tests.

## Remaining blocker

The v43 AIM probe can parse table boundaries and names, but does not decode the model bytecode/behavior that would populate a List, bind a selection action and route a stable catalog ID. Recover that model-side contract before making an in-game edit. The current HUD codec remains a field-preserving format tool, not a complete engine resource authoring pipeline.

## Validation boundary

Static disassembly of wrapper call paths is evidence of native API signatures and argument conversions. It does not prove the new model code can be compiled/loaded, that a HUD element can be safely created at runtime, that list hit targets/layout are correct, or that any cheat has a gameplay effect. No APK/XAPK was built in this increment; runtime-verified cheat effects remain 0/222.

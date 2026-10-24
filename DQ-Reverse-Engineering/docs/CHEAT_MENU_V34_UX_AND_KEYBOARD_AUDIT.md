# Cheat Menu v34 UX correction and native keyboard audit

Date: 2026-10-25  
Status: browser workbench built; in-game Gold input route remains blocked pending a verified callback.

## User feedback translated into requirements

The v33 screenshot showed four tiny Gold buttons incorrectly overlaid between the Add Levels and Add Feat cards. That layout is not accepted. Updated requirements:

1. **Gold is a custom target balance**, entered via a numeric keyboard in a dedicated Gold control.
2. **−10, −1, +1, +10 are generic numeric steppers for other numeric cheat settings**, not buttons attached to Gold.
3. No free-typed numeric field for ordinary cheat values; step buttons control them. Use one or ten configured increments for decimal/ranged settings, with min/max clamping.
4. Keep the complete cheat catalog in the Cheat Menu, with rich category/detail controls instead of only the six fixed debug cards.
5. Clearly distinguish catalog/UI presence from real gameplay integration. Unknown handlers stay blocked and must not be presented as active.

## What is confirmed by current binary/asset evidence

- The original source-level catalog has 222 stable IDs across 14 categories.
- The original pack contains `Resources/HUD/keyboard.hud`, with callbacks `onKeyboardEnter`, `onKeyboardDelete`, `onKeyboardClose`, and `onKeyboardCaps`.
- The native model `uai_gp_hud` exposes `sKeyboardDirect`, `bKeyboardOpen`, `onKeyboard`, `onSetGold`, and `onGetGold` identifiers.
- These identifiers establish that the game has an internal keyboard pathway. They do **not** yet prove that a newly added Gold field can focus this keyboard, that its text is parsed as a numeric amount, or that the amount can be routed safely into `RewardGold`/the player balance handler.
- Gold mutations in v33 were attached to the wrong location and used fixed amounts. v33 should not be treated as satisfying the custom-Gold requirement.

## v34 workbench artifact

A separate mobile-responsive single-file HTML workbench has been built locally:
`Dungeon_Quest_Cheats_Sandbox_Workbench_v34.html`

- All 222 catalog entries and 14 categories.
- Search, category and risk filters, favorites, detail/evidence panel, presets, undo, reset, event log and JSON export.
- Ordinary numeric values use buttons only: `−10`, `−1`, `+1`, `+10`. Large/small button increments are scaled by each entry's configured `step` and clamped to the documented bounds.
- Only `economy.currency_override` (custom Gold target) uses a numeric text field with `inputmode=numeric` so a phone browser can show the numeric keyboard.
- The app explicitly reports `GAME LINK: DISCONNECTED`; all interactions stage local draft values only.

This workbench corrects the intended interaction pattern but is **not injected into the game** and must not be called an integrated APK.

## Next in-game implementation gates

1. Decode the type-6 editable field record already used by the source debug HUD and compare it against the original input/keyboard screen lifecycle.
2. Prove the exact HUD event that opens `keyboard.hud`, the meaning of `sKeyboardDirect`, and how `onKeyboardEnter` commits typed text.
3. Define a bounded numeric Gold adapter: parse integer string; reject empty/negative/out-of-range values; call an existing native reward/balance route only after the text value is confirmed and the sandbox/offline state gates pass.
4. Move generic steppers to a non-Gold numerical control with an actual state variable and read-back; don't attach them to a button that merely invokes a fixed debug command.
5. Expand the in-game menu only through verified groups/pages and a format-preserving serializer. Do not add 222 decorative controls without backing game handlers.

No new XAPK is declared runtime-ready in v34. The next game build will be produced only once the keyboard field → numeric value → balance action path and the non-Gold stepper read-back are internally consistent.

# Gold mutation and internal-keyboard call-graph audit — v40

Date: 2026-10-25. Static analysis only. No APK/XAPK built.

## `onSetGold` is not a proven balance setter

At native VA `0x74ff84`, `uai_gp_hud::onSetGold(int, AIVariable const*, AIVariable*)` reads its passed AIVariable, calls `NumberToString`, concatenates UI text, and publishes a model value whose string constant is `hud.gold`. This indicates formatting/updating a displayed HUD/model string; there is no demonstrated write to authoritative player/account Gold state. A button invoking `onSetGold` with no argument is therefore not a valid custom-Gold implementation.

## Gold mutation helpers

The symbol table identifies `uai_gp_hud::RewardGold(S3DX::AIVariable)` at `0x65feec` and `uai_gp_hud::SpendGold(S3DX::AIVariable)` at `0x637008`. Both are called from existing gameplay paths and parse numeric AIVariable data. They are candidate lower-level reward/spend primitives, but a safe standalone adapter still needs the exact amount semantics, authoritative current balance, input bounds, sandbox/offline gates, read-back and rollback. Do not invoke them from a new button based on name alone.

## Internal keyboard path

`uai_gp_hud::onKeyboardEnter` at `0x705940` reads `keyboard.key_entry` and `sKeyboardDirect`, then routes data via `setEnvVar` at `0x5fdf5c` and `UpdateSlots` at `0x63aa04`. The exact route token and commit contract for custom Gold remain unresolved.

`uai_gp_account::OpenKeyboard(S3DX::AIVariable)` is at `0x4f40a4`. Its statically observed callers are `onCheckMessagesResult` at `0x504f44` and `0x505338`, and `onFindMatchResult` at `0x50f0e8`. At those call sites the target field is `nickname`, so this is not a verified Gold-entry path. The internal `keyboard.hud` has 58 elements and four actions; their presence does not establish the missing Gold route.

## Implications

- The v39 workbench has a tested custom keypad that stages Gold locally; it does not call the Android system keyboard and is not connected to gameplay.
- Other numeric settings use `−10`, `−1`, `+1`, `+10`; these also stage local drafts.
- The in-game 222-row list remains unintegrated. Native List methods exist, but a valid type-3 List HUD record plus the AIM population/selection contract still needs to be proven.
- No new APK/XAPK was built in this increment, following the user's request to finish the menu before packaging.

## Next gate

Continue read-only reverse engineering of the List element record, AIM model callbacks, internal keyboard launch context and authoritative Gold state. Do not generate another package until the UI design is accepted and the runtime contract is evidence-backed.

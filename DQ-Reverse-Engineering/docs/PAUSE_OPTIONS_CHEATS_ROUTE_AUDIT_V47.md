# Pause → Options → Cheats route audit — v47

**Status: the source-level route is blocked. This audit is read-only; no Pause/Options/AIModel source asset is edited.**

## Direct source observations

The findings below were measured against extracted assets from Dungeon Quest Android 3.3.2.0.

| Source resource | SHA-256 | Structure observed |
|---|---|---|
| Resources/HUD/pause.hud | 12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395 | 126 elements; 64 action records; 102 statements |
| Resources/HUD/debug.hud | 02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6 | 71 elements; 13 action records |
| Resources/AIModels/uai_gp_options.aim | 294dc84260b1a58dcbf6cf8fe939c107e8c0ae2bacc7ffe11b34ac62a54b5625 | 18 variables; 11 functions; 9 handlers |
| Resources/AIModels/uai_gp_debug.aim | e41094fd055ca250f282862e383506c3a0fb04c2bb3e2f09d7e139e51570bd59 | 8 variables; 2 functions; 6 handlers |

The existing Options button is element options_btn in the PauseMenu group, with callback onShowOptions. The serialized action calls uai_gp_options.onShowOptions, hides the PauseMenu group, and shows the options group. Its action does not call uai_gp_hud.onDebug or uai_gp_debug.

The nine registered handlers in uai_gp_options are:
onInit, onShowTab, onMapButton, onLoadOptions, onSaveOptions, onShowOptions, onJoypadButtonDown, onSetControlsOption, and onSetGameplayOption. There is no onShowCheats handler. Adding a HUD action that references that nonexistent handler would not implement a route and could leave the click as a no-op or create a loading/action error.

The model named uai_gp_debug is not the existing gameplay Debug HUD controller. Its two functions are SetLoading and CompileShaderList; its handlers cover debug logging, shader compilation, shader-list dumping, failed-shader dumping, and shader compilation cancellation. In contrast, buttons in debug.hud call uai_gp_hud.onDebug with numeric arguments.

## Relationship to the 222-entry workbench

The repository already contains a scrollable HTML workbench and standalone catalog with 222 unique stable IDs across 14 categories. Its implementation matrix currently reports:

| Evidence class | Count |
|---|---:|
| Fully integrated | 0 |
| Runtime verified | 0 |
| Unverified native candidates | 3 |
| Requires a verified game adapter | 219 |

The HTML workbench has search/filter and a dedicated vertical scroll container; that establishes its browser UI structure, not an in-game game-state bridge. The route bridge at runtime-adapter/PauseOptionsCheatsBridge.java is an integration seam with dependency-free tests, not an implementation of the original Options HUD hook. The route manifest correctly remains BLOCKED.

The v46 Gold +100K candidate is only a separate debug.hud/STK experiment. It does not establish that the original Pause → Options screen can reach that panel.

## Explicit non-actions

- No new onShowCheats callback was inserted into pause.hud.
- No change was made to uai_gp_options.aim or uai_gp_debug.aim.
- No hud_addListItem, hud_setListItemTextAt, or list-selection callback was added to the stock HUD action tables.
- No APK/XAPK was built or installed. Gameplay route claims remain at zero.

## Next integration gate

A real route requires a supported route into a Cheats page and a native/model-side adapter that can populate a List, bind selection changes, map a selected row to a stable cheat ID, validate typed values, read back the game state and fail closed if the action fails. The current recovered native wrappers expose List methods, but the stock serialized HUD actions do not demonstrate a call path to them. Do not replace the blocked route with an invented callback or label the 222 rows as functional.

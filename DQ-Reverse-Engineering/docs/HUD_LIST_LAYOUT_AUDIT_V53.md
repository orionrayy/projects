# HUD List serialization and runtime-population audit — v53

**Status: serialized List record schema has a directly observed stock example; a generic in-game cheat list is still not connected.**

## Observations from the supplied Dungeon Quest 3.3.2.0 files

| HUD | SHA-256 | Element records | Serialized type-3 List records |
|---|---|---:|---:|
| `pause.hud` | `12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395` | 126 | 0 |
| `debug.hud` | `02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6` | 71 | 0 |
| `match_result_anim.hud` | `fec7d9b18c906d4d75904205f58b3eb3205540c04aefb9fc651c6d2ac2cf9402` | 108 | 1 |

The one stock type-3 record in `match_result_anim.hud` is element index 0, named `list`, label `rank_up_player_container`, 237 serialized bytes. Its observed geometry is x=0.5162, y≈0, width=0.4528, height=2.0. The row-template resource fields exposed by the field-preserving parser are empty. This is a results/rank-up control, not a demonstrated general-purpose cheat list.

## Why this matters to integration

Native wrappers exist for `hud_addListItem`, `hud_setListItemTextAt`, `hud_setListOnSelectionChangedAction`, selected-row queries and finger/smooth scrolling. These wrappers operate on engine-managed HUD objects. However, none of the 68 inspected source HUD action tables contains a verified serialized call to the native List population/selection wrappers.

Therefore, cloning the one type-3 record into `pause.hud` would only create a serialized List control candidate; it would not populate 222 rows, connect search/filter state, or dispatch a selected stable cheat ID. The game-model-side call sequence remains the integration blocker. Do not present a blank/non-populated List as the completed menu.

## Read-only audit tool

`tools/hud_list_audit_v53.py` inventories type-3 List elements from decoded HUD files and reports their serialized fields and any non-empty resource/template references. It does not edit HUD files, decode the action VM, or claim runtime behavior.

```bash
python tools/hud_list_audit_v53.py pause.hud debug.hud match_result_anim.hud
python -m unittest discover -s tests -p 'test_hud_list_audit_v53.py' -v
```

## Full-integration gate remains

A complete menu still requires a correct in-engine row population path, selected-row callback, stable ID to allow-listed native handler mapping, typed argument validation, runtime state read-back, save/reload verification and regression checks. The current catalog remains 0/222 catalog routes and 0/222 runtime-verified effects; the Gold +100K button is a separate unverified static candidate.

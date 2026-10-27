# Project Progress Checkpoint — v81.1 First 50 Flexible Cheats
Date: 2026-10-28
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
PR: #26 (draft)

## User request
Improve the actual in-game cheat menu, remove features that do not work or duplicate existing actions, and build a flexible roster of at least 50 cheats.

## Completed this turn
- Audited the 20-split v80 asset payload from the source project.
- Confirmed two duplicate Quick Actions in v80: `Level Up` duplicates the base HUD `onLevelUp → uai_gp_hud.onShortcut("levelup", 1)`; `Gold +100K` duplicates base HUD `onDebugGold → uai_gp_hud.onDebug(6.0)`.
- Confirmed Gold command 6 is fixed +100,000 Gold, not an arbitrary amount or balance-target setter.
- Confirmed command 7’s SpendGold context remains unresolved and it should not be exposed as a general decrement action.
- Added and refined the deduplicated first-50 roster in `cheats-sandbox/first50_flexible_cheats_v81.json`.
- Added a human-readable registry report, duplicate-route audit, metadata validator and regression tests.
- Removed the standalone No Skill Cooldowns toggle in favor of the configurable Skill Cooldown multiplier.
- Added Auto Heal as the toggle that enables the Auto-Heal Threshold slider; validated dependency direction.
- Removed standalone Level Up +1 to avoid duplicating existing actions; added Quest Stage Target as a distinct but blocked configurable field.
- Detached the flexible Gold amount field from fixed Gold +100K route, and detached Boss Variant selector from fixed boss-debug route.

## Roster validation
- 50 items; 50 unique stable IDs, labels and effect keys.
- Control mix: 20 sliders, 8 toggles, 7 numeric inputs, 4 selects and 11 actions.
- 11 static native route candidates are recorded; these are not treated as verified adapters.
- Runtime-verified: 0/50. Fully integrated: 0/50.
- Static catalog tests pass. The ZIP package containing JSON/Markdown/validation and duplicate-route audit passes ZIP integrity validation.

## Hard blocker
The target game's native List population plus stable-ID selection/dispatch path is still not implemented. A package showing 50 apparent controls would be misleading if they only stage values or call unrelated fixed debug commands. Do not create an XAPK that claims 50 working cheats until the exact-build typed adapter, state read-back, save/reload and recovery gates pass.

## Files
- `DQ-Reverse-Engineering/cheats-sandbox/first50_flexible_cheats_v81.json`
- `DQ-Reverse-Engineering/docs/CHEAT_MENU_FIRST50_REGISTRY_V81.md`
- `DQ-Reverse-Engineering/docs/CHEAT_MENU_V81_1_DUPLICATE_ROUTE_AUDIT.md`
- `DQ-Reverse-Engineering/docs/CHEAT_MENU_V81_1_DUPLICATE_ROUTE_AUDIT.json`
- `DQ-Reverse-Engineering/tools/validate_first50_flexible_cheats_v81.py`
- `DQ-Reverse-Engineering/tests/test_first50_flexible_cheats_v81.py`

No new XAPK is claimed in this checkpoint.

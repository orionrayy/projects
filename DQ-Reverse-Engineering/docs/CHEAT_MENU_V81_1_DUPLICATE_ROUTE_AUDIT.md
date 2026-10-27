# Dungeon Quest Cheat Menu v81.1 — Duplicate Route Audit

**Status: static asset audit passed; in-game runtime not tested.**

Source STK SHA-256: `e6d82116849cd46b38b068f042327c8a6be7a05322304008551112df173b6c72`

Decoded HUD sizes:
- Main HUD: 637 elements / 219 actions
- Debug HUD: 71 elements / 13 actions
- Pause HUD: 127 elements / 65 actions
- STK total: 5,630 entries

## Duplicate routes confirmed

| Existing main-HUD control | Callback / route | Finding |
|---|---|---|
| `goldUp` | `onDebugGold` → `uai_gp_hud.onDebug(6.0)` | Fixed +100,000 Gold path. Duplicate of the v80 Quick Actions Gold +100K row. |
| `levelUp` | `onLevelUp` → `uai_gp_hud.onShortcut("levelup", 1)` | Duplicate of the v80 Quick Actions Level Up row. |
| `levelUpCheat` | `onDebugLevel` → `uai_gp_hud.onDebug(5.0)` | Another original debug-only level control. Keep its role distinct from a configurable level target. |
| `goldDown` | `onDebugGoldDown` → `uai_gp_hud.onDebug(7.0)` | Command-7 context remains unresolved; do not expose as arbitrary Gold decrement. |

## Existing debug controls worth preserving

- Floor: level picker (1–200), Goto Level, Is Boss.
- Add: Add Levels, Add Battle, Add Heroic.
- CS, MS, Feat, Legends: create/reward fixtures and Crystal/Eternal controls.

These are existing fixed actions, not 50 generic cheat adapters. The Gold reward route cannot be repurposed as a custom amount or balance setter. The boss debug route does not prove a generic encounter-variant select.

## v81.1 roster decisions

- Removed No Skill Cooldowns in favor of the adjustable Skill Cooldown multiplier.
- Added Auto Heal and made the threshold control depend on it.
- Removed standalone Level Up +1; added a separate, disabled Quest Stage Target field.
- Detached the configurable Gold amount from fixed command 6.
- Detached Boss Variant select from fixed command 3.
- Registry has 50 unique IDs/labels/effect keys, 11 static route candidates, 0 fully integrated handlers and 0 runtime-verified entries.

## Hard integration boundary

The native List API exists but a game-side list population function and selected stable-ID dispatcher have not been established. So this audit does not claim a 50-cheat XAPK. It documents the deduplicated target roster and the concrete changes needed before the next package is enabled.

# Dungeon Quest ModKit — First 50 Native Handler Audit (v83)

Date: 2026-10-29
Target: Dungeon Quest Android 3.3.2.0 ARM64
Branch: feat/dq-iap-debug-cheats-modkit-v7
Status: BLOCKED — no full 50-cheat integration candidate built in this audit.

## Executive result

The catalogue has 50 unique IDs and 50 unique effect keys, but target-game integration remains 0/50 fully integrated and 0/50 runtime verified. This audit is not a replacement install package. It records the implementation boundary so the next package does not disguise missing gameplay logic as working buttons.

## Findings from the target build

1. Native List wrappers exist, but their signatures do not establish a working generic cheat-list creator or a selected stable-ID dispatcher. uai_gp_options.aim does not register onShowCheats, and uai_gp_debug.aim is a shader-diagnostic model rather than the gameplay cheat controller.
2. The native model function inventory includes uai_gp_hud.RewardGold(AIVariable) and RewardDust(AIVariable). v82 added literal fixed-amount controls for those calls. These are static call-site candidates only; numeric input binding, actual balance delta, save persistence and recovery have not been verified on device.
3. Several existing uai_gp_hud.onDebug(number) branches are fixed debug actions, not a general setter API. An Add Levels or fixture reward route does not implement a slider, toggle, arbitrary balance setter or multiplier.
4. A similarly named handler is not sufficient evidence. God Mode, skill cooldown, combat multipliers, enemy AI freeze, auto-identify, inventory capacity, snapshot and undo require explicit behavior and state read-back contracts. No guess-based calls were inserted.

## Per-cheat matrix

| # | Stable ID | Control | Evidence classification | Current route candidate |
|---:|---|---|---|---|
| 1 | player.god_mode | toggle | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 2 | player.infinite_mana | toggle | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 3 | player.ignore_debuffs | toggle | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 4 | player.no_knockback | toggle | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 5 | player.auto_heal_threshold | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 6 | player.auto_heal | toggle | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 7 | player.health_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 8 | player.movement_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 9 | player.attack_speed_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 10 | combat.damage_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 11 | combat.crit_chance | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 12 | combat.crit_damage_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 13 | combat.armor_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 14 | combat.lifesteal | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 15 | enemy.health_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 16 | enemy.damage_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 17 | enemy.move_speed_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 18 | enemy.freeze_ai | toggle | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 19 | enemy.boss_variant | select | SEMANTIC_MISMATCH | — |
| 20 | loot.drop_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 21 | loot.rarity_floor | select | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 22 | loot.guaranteed_drop | toggle | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 23 | economy.gold_reward_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 24 | economy.gold_balance_target | number | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 25 | economy.gold_reward_amount | number | NATIVE_FUNCTION_CANDIDATE | — |
| 26 | economy.dust_reward_amount | number | NATIVE_FUNCTION_CANDIDATE | — |
| 27 | progression.player_level | slider | STATIC_ROUTE_ONLY | uai_gp_hud.onDebug(4.0) |
| 28 | progression.floor_target | number | STATIC_ROUTE_ONLY | uai_gp_hud.onDebug(2.0) |
| 29 | progression.xp_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 30 | progression.add_levels | action | EXISTING_ACTION_CANDIDATE | uai_gp_hud.onDebug(11.0) |
| 31 | progression.difficulty_override | select | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 32 | skills.cooldown_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 33 | skills.mana_cost_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 34 | skills.damage_multiplier | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 35 | skills.free_points | number | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 36 | inventory.capacity_bonus | number | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 37 | inventory.auto_identify | toggle | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 38 | inventory.rarity_override | select | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 39 | inventory.affix_reroll_count | slider | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |
| 40 | inventory.grant_legend_fixture | action | EXISTING_ACTION_CANDIDATE | uai_gp_hud.onDebug(8.0) |
| 41 | inventory.grant_mythstone_fixture | action | EXISTING_ACTION_CANDIDATE | uai_gp_hud.onDebug(9.0) |
| 42 | inventory.grant_character_stone_fixture | action | EXISTING_ACTION_CANDIDATE | uai_gp_hud.onDebug(10.0) |
| 43 | inventory.grant_feat_fixture | action | EXISTING_ACTION_CANDIDATE | uai_gp_hud.onDebug(13.0) |
| 44 | rewards.add_battle | action | EXISTING_ACTION_CANDIDATE | uai_gp_hud.onDebug(16.0) |
| 45 | rewards.add_heroic | action | EXISTING_ACTION_CANDIDATE | uai_gp_hud.onDebug(12.0) |
| 46 | rewards.add_crystal | action | EXISTING_ACTION_CANDIDATE | uai_gp_hud.onDebug(14.0) |
| 47 | rewards.add_eternal | action | EXISTING_ACTION_CANDIDATE | uai_gp_hud.onDebug(15.0) |
| 48 | debug.snapshot | action | CUSTOM_ADAPTER_REQUIRED | — |
| 49 | debug.undo_last_action | action | CUSTOM_ADAPTER_REQUIRED | — |
| 50 | progression.quest_stage_target | number | CUSTOM_GAMEPLAY_ADAPTER_REQUIRED | — |

## Classification counts

- CUSTOM_GAMEPLAY_ADAPTER_REQUIRED: 34
- SEMANTIC_MISMATCH: 1
- NATIVE_FUNCTION_CANDIDATE: 2
- STATIC_ROUTE_ONLY: 2
- EXISTING_ACTION_CANDIDATE: 9
- CUSTOM_ADAPTER_REQUIRED: 2

## Release gate before handing over a 50-cheat XAPK

- Implement a supported in-game route and generic row/control dispatcher in the actual target runtime; do not create placeholder rows for unavailable handlers.
- For every cheat, bind the exact ID to an allow-listed handler with typed argument parsing, explicit bounds, scene/offline preconditions and fail-closed behavior.
- Verify state changes via authoritative state read-back, including disable/rollback where applicable, then test save/reload and force-close recovery.
- Rebuild all splits and re-run archive CRCs, package ID/certificate consistency, signing-scheme checks, native-library alignment, DEX checks and HUD/STK verification.
- Keep the candidate under a separate package ID; never uninstall the official game or clear its data to install the test package.

## Decision

No v83 50-cheat XAPK is represented as complete by this audit. v82 remains the last built package, but it does not meet the user's 50-cheat install gate. A successful static package check cannot substitute for missing runtime handlers or on-device gameplay verification.

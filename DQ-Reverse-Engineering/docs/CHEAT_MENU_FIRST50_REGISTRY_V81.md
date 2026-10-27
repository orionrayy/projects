# Dungeon Quest ModKit v81.1 — First 50 Flexible Cheats

**Status: roster and deduplication audit validated; in-game integration remains blocked.**

This is a 50-entry implementation roster, not a claim that 50 working cheats have been installed. Each control must have an exact handler, parameter contract, state read-back and recovery path before it can be enabled in-game.

## Control mix

| Control | Count |
|---|---:|
| action | 11 |
| number | 7 |
| select | 4 |
| slider | 20 |
| toggle | 8 |

## First 50 options

| # | Stable ID | Label | Control | Handler status |
|---:|---|---|---|---|
| 1 | player.god_mode | God Mode | toggle | requires_verified_adapter |
| 2 | player.infinite_mana | Infinite Mana | toggle | requires_verified_adapter |
| 3 | player.ignore_debuffs | Ignore Negative Status Effects | toggle | requires_verified_adapter |
| 4 | player.no_knockback | No Knockback | toggle | requires_verified_adapter |
| 5 | player.auto_heal_threshold | Auto-Heal Threshold | slider | requires_verified_adapter |
| 6 | player.auto_heal | Auto Heal | toggle | requires_verified_adapter |
| 7 | player.health_multiplier | Max Health Multiplier | slider | requires_verified_adapter |
| 8 | player.movement_multiplier | Movement Speed | slider | requires_verified_adapter |
| 9 | player.attack_speed_multiplier | Attack Speed | slider | requires_verified_adapter |
| 10 | combat.damage_multiplier | Outgoing Damage | slider | requires_verified_adapter |
| 11 | combat.crit_chance | Critical Chance | slider | requires_verified_adapter |
| 12 | combat.crit_damage_multiplier | Critical Damage | slider | requires_verified_adapter |
| 13 | combat.armor_multiplier | Damage Reduction / Armor | slider | requires_verified_adapter |
| 14 | combat.lifesteal | Life Steal | slider | requires_verified_adapter |
| 15 | enemy.health_multiplier | Enemy Health | slider | requires_verified_adapter |
| 16 | enemy.damage_multiplier | Enemy Damage | slider | requires_verified_adapter |
| 17 | enemy.move_speed_multiplier | Enemy Movement Speed | slider | requires_verified_adapter |
| 18 | enemy.freeze_ai | Freeze Enemy AI | toggle | requires_verified_adapter |
| 19 | enemy.boss_variant | Boss / Encounter Variant | select | fixed_action_mismatch; excluded mismatch: uai_gp_hud.onDebug(3.0) |
| 20 | loot.drop_multiplier | Loot Drop Rate | slider | requires_verified_adapter |
| 21 | loot.rarity_floor | Minimum Drop Rarity | select | requires_verified_adapter |
| 22 | loot.guaranteed_drop | Guaranteed Drop | toggle | requires_verified_adapter |
| 23 | economy.gold_reward_multiplier | Gold Reward Multiplier | slider | requires_verified_adapter |
| 24 | economy.gold_balance_target | Set Gold Balance | number | requires_verified_adapter |
| 25 | economy.gold_reward_amount | Gold Reward Amount | number | requires_verified_adapter; excluded mismatch: uai_gp_hud.onDebug(6.0) |
| 26 | economy.dust_reward_amount | Dust Reward Amount | number | requires_verified_adapter |
| 27 | progression.player_level | Player Level | slider | existing_ui_route_static_only; static candidate: uai_gp_hud.onDebug(4.0) |
| 28 | progression.floor_target | Floor Target | number | existing_ui_route_static_only; static candidate: uai_gp_hud.onDebug(2.0) |
| 29 | progression.xp_multiplier | XP Gain | slider | requires_verified_adapter |
| 30 | progression.add_levels | Add Levels | action | existing_action_static_only; static candidate: uai_gp_hud.onDebug(11.0) |
| 31 | progression.difficulty_override | Difficulty Override | select | requires_verified_adapter |
| 32 | skills.cooldown_multiplier | Skill Cooldown | slider | requires_verified_adapter |
| 33 | skills.mana_cost_multiplier | Skill Mana Cost | slider | requires_verified_adapter |
| 34 | skills.damage_multiplier | Skill Damage | slider | requires_verified_adapter |
| 35 | skills.free_points | Skill Points | number | requires_verified_adapter |
| 36 | inventory.capacity_bonus | Inventory Capacity Bonus | number | requires_verified_adapter |
| 37 | inventory.auto_identify | Auto Identify Gear | toggle | requires_verified_adapter |
| 38 | inventory.rarity_override | Generated Item Rarity | select | requires_verified_adapter |
| 39 | inventory.affix_reroll_count | Affix Reroll Count | slider | requires_verified_adapter |
| 40 | inventory.grant_legend_fixture | Grant Legend Fixture | action | existing_action_static_only; static candidate: uai_gp_hud.onDebug(8.0) |
| 41 | inventory.grant_mythstone_fixture | Grant Mythstone Fixture | action | existing_action_static_only; static candidate: uai_gp_hud.onDebug(9.0) |
| 42 | inventory.grant_character_stone_fixture | Grant Character Stone Fixture | action | existing_action_static_only; static candidate: uai_gp_hud.onDebug(10.0) |
| 43 | inventory.grant_feat_fixture | Grant Feat Fixture | action | existing_action_static_only; static candidate: uai_gp_hud.onDebug(13.0) |
| 44 | rewards.add_battle | Add Battle Reward | action | existing_action_static_only; static candidate: uai_gp_hud.onDebug(16.0) |
| 45 | rewards.add_heroic | Add Heroic Reward | action | existing_action_static_only; static candidate: uai_gp_hud.onDebug(12.0) |
| 46 | rewards.add_crystal | Crystal Reward / State | action | existing_action_static_only; static candidate: uai_gp_hud.onDebug(14.0) |
| 47 | rewards.add_eternal | Eternal Reward / State | action | existing_action_static_only; static candidate: uai_gp_hud.onDebug(15.0) |
| 48 | debug.snapshot | Capture Local State Snapshot | action | requires_verified_adapter |
| 49 | debug.undo_last_action | Undo Last Cheat Action | action | requires_verified_adapter |
| 50 | progression.quest_stage_target | Quest Stage Target | number | requires_verified_adapter |

## Deduplication decisions

- Removed the standalone No Skill Cooldowns toggle; Skill Cooldown remains the single configurable cooldown control.
- Added Auto Heal and made Auto-Heal Threshold dependent on it.
- Removed the extra Level Up +1 catalog item because it overlaps the existing HUD level-up action and Add Levels; the roster now has a distinct but disabled Quest Stage Target field.
- The configurable Gold Reward Amount control no longer maps to onDebug(6.0), which is a fixed +100,000 Gold reward.
- The Boss / Encounter Variant selector no longer maps to onDebug(3.0), because that route is not a proven arbitrary variant selector.

## Integration boundary
- Unique IDs, labels and effect keys: 50/50 each.
- Static native-route candidates attached to roster entries: 11.
- Fully integrated: 0/50. Runtime-verified: 0/50.
- No new XAPK is claimed by this registry update. The game-side stable-ID dispatcher and typed native adapter remain unresolved.

## Enabling rule

Every enabled cheat must pass exact-build handler validation, typed input bounds, offline/disposable-profile preconditions, authoritative state read-back, save/reload and rollback/regression tests. Fixed debug commands cannot be reused as arbitrary sliders or target-value setters just because their names look similar. Purchase entitlements, receipts, cloud saves, leaderboard and achievement state remain out of scope.


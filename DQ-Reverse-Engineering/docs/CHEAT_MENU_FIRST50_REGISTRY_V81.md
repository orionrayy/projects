# Dungeon Quest ModKit v81 — First 50 Flexible Cheats

**Status: 50-entry registry validated; game integration remains blocked.**  
Target: Dungeon Quest 3.3.2.0 ARM64  
Branch: `feat/dq-iap-debug-cheats-modkit-v7`

This is the deduplicated first-50 implementation roster, not a claim that an APK with 50 working cheats has been built. It defines unique stable IDs and flexible controls. Controls without a proven exact-build handler must remain unavailable instead of being displayed as functioning cheats.

## First 50 options

| # | Stable ID | Display name | Control |
|---:|---|---|---|
| 1 | `player.god_mode` | God Mode | Toggle |
| 2 | `player.infinite_mana` | Infinite Mana | Toggle |
| 3 | `player.no_cooldowns` | No Skill Cooldowns | Toggle |
| 4 | `player.ignore_debuffs` | Ignore Negative Status Effects | Toggle |
| 5 | `player.no_knockback` | No Knockback | Toggle |
| 6 | `player.auto_heal_threshold` | Auto-Heal Threshold | Slider, 1–100% |
| 7 | `player.health_multiplier` | Max Health Multiplier | Slider, 1–50× |
| 8 | `player.movement_multiplier` | Movement Speed | Slider, 0.5–5× |
| 9 | `player.attack_speed_multiplier` | Attack Speed | Slider, 0.5–5× |
| 10 | `combat.damage_multiplier` | Outgoing Damage | Slider, 0–100× |
| 11 | `combat.crit_chance` | Critical Chance | Slider, 0–100% |
| 12 | `combat.crit_damage_multiplier` | Critical Damage | Slider, 1–20× |
| 13 | `combat.armor_multiplier` | Damage Reduction / Armor | Slider, 0–50× |
| 14 | `combat.lifesteal` | Life Steal | Slider, 0–100% |
| 15 | `enemy.health_multiplier` | Enemy Health | Slider, 0.01–100× |
| 16 | `enemy.damage_multiplier` | Enemy Damage | Slider, 0–10× |
| 17 | `enemy.move_speed_multiplier` | Enemy Movement Speed | Slider, 0–5× |
| 18 | `enemy.freeze_ai` | Freeze Enemy AI | Toggle |
| 19 | `enemy.boss_variant` | Boss / Encounter Variant | Select |
| 20 | `loot.drop_multiplier` | Loot Drop Rate | Slider, 0–100× |
| 21 | `loot.rarity_floor` | Minimum Drop Rarity | Select |
| 22 | `loot.guaranteed_drop` | Guaranteed Drop | Toggle |
| 23 | `economy.gold_reward_multiplier` | Gold Reward Multiplier | Slider, 0–100× |
| 24 | `economy.gold_balance_target` | Set Gold Balance | Numeric target |
| 25 | `economy.gold_reward_amount` | Gold Reward Amount | Numeric amount |
| 26 | `economy.dust_reward_amount` | Dust Reward Amount | Numeric amount |
| 27 | `progression.player_level` | Player Level | Slider, 1–1000 |
| 28 | `progression.floor_target` | Floor Target | Numeric target |
| 29 | `progression.xp_multiplier` | XP Gain | Slider, 0–100× |
| 30 | `progression.add_levels` | Add Levels | Action |
| 31 | `progression.difficulty_override` | Difficulty Override | Select |
| 32 | `progression.level_up_one` | Level Up +1 | Action |
| 33 | `skills.cooldown_multiplier` | Skill Cooldown | Slider, 0–10× |
| 34 | `skills.mana_cost_multiplier` | Skill Mana Cost | Slider, 0–10× |
| 35 | `skills.damage_multiplier` | Skill Damage | Slider, 0–100× |
| 36 | `skills.free_points` | Skill Points | Numeric amount |
| 37 | `inventory.capacity_bonus` | Inventory Capacity Bonus | Numeric amount |
| 38 | `inventory.auto_identify` | Auto Identify Gear | Toggle |
| 39 | `inventory.rarity_override` | Generated Item Rarity | Select |
| 40 | `inventory.affix_reroll_count` | Affix Reroll Count | Slider, 0–20 |
| 41 | `inventory.grant_legend_fixture` | Grant Legend Fixture | Action |
| 42 | `inventory.grant_mythstone_fixture` | Grant Mythstone Fixture | Action |
| 43 | `inventory.grant_character_stone_fixture` | Grant Character Stone Fixture | Action |
| 44 | `inventory.grant_feat_fixture` | Grant Feat Fixture | Action |
| 45 | `rewards.add_battle` | Add Battle Reward | Action |
| 46 | `rewards.add_heroic` | Add Heroic Reward | Action |
| 47 | `rewards.add_crystal` | Crystal Reward / State | Action |
| 48 | `rewards.add_eternal` | Eternal Reward / State | Action |
| 49 | `debug.snapshot` | Capture Local State Snapshot | Action |
| 50 | `debug.undo_last_action` | Undo Last Cheat Action | Action |

## Findings from the source audit

- The roster has **50 unique stable IDs, 50 unique labels and 50 unique effect keys**. No duplicate item is present in this specification.
- Control mix: 8 toggles, 20 sliders, 6 numeric fields, 4 selects and 12 actions.
- 14 items have a nearby pre-existing HUD/debug route. These are static route candidates, not proof the catalog feature has matching semantics or works at runtime.
- The existing `uai_gp_hud.onDebug(6.0)` route is a fixed +100,000 Gold reward. It does not implement a custom amount or balance-target field. Similarly, the level, floor and boss debug routes do not prove arbitrary slider/target writes.
- The native List API exists, but the model-side List population and stable-ID selection dispatcher have not been recovered. Existing repo audits report 0/222 catalog IDs fully integrated and 0/222 individually runtime-verified.

## Why there is no v81 XAPK in this checkpoint

A package with 50 enabled controls cannot be truthfully described as “50 flexible cheats” when most of the controls have no verified handler. Repeating fixed buttons, assigning unrelated commands by similar labels, or showing local draft controls as game mutations would reproduce the exact defects you reported: nonfunctional options, duplicates and unnecessary features.

Each option must pass these gates before it is enabled: exact-build handler; typed parameter contract and bounds; offline/disposable-profile precondition; authoritative state read-back; save/reload check; rollback or recovery path; regression check. Paid entitlements, purchase receipts, cloud saves, leaderboards and achievement writes remain excluded.

## Companion artifacts

The detailed machine-readable registry includes risk level, parameter bounds, candidate route, per-entry status and reasons a mapping is still blocked. Validation passed with 50/50 unique IDs, labels and effect keys, valid numeric ranges and valid select defaults. It deliberately records runtime-verified count as zero until individual device results can be attributed to specific controls.

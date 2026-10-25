# Native debug command vs. 222-entry catalog compatibility — v58

**Result: 16 static debug dispatch commands were reviewed; 0 exact catalog mappings are justified by current evidence.** The original-game integration gate remains blocked at 0/222.

## Why this cross-check was needed

The stock native dispatcher has legacy fixed-purpose debug commands. The catalog controls specify typed state-setting semantics—toggles, sliders, ranges, selects and actions. Similar labels do not make their semantics interchangeable. The candidate catalog IDs in the machine-readable matrix are nearest concepts reviewed, not approved mappings.

## Important semantic mismatches

- **Command 6 / \`RewardGold(100000.0)\`:** a static candidate for a single fixed increment. It is not a setter for \`economy.currency_override\`, an earned Gold multiplier, or a loot Gold multiplier. The fixed button remains the separate \`native.pause.gold_reward_100k\` candidate with no catalog ID, pending runtime verification.
- **Command 7 / \`SpendGold\`:** the call is in LegendEx-contextual code and the amount origin/context have not been recovered as a safe arbitrary spend contract. It must not be exposed as a general spend button or balance setter.
- **Commands 2 and 4 / level navigation or setting:** fixed numeric debug routes, not proven typed setters for \`debug.teleport\`, \`progression.quest_stage\`, or \`progression.player_level\`.
- **Commands 8–10 / Legend, MS, CS fixture creation:** fixed fixture actions do not expose an arbitrary item-ID contract equivalent to \`inventory.grant_item\`.
- **Commands 11–16 / progression and special rewards:** observed names/codes do not establish equivalent parameter contracts for skill-point, reward-range, token-balance, or general state controls.

## Resulting implementation decision

Do not manufacture a stable-ID map from name similarity. The reviewed static routes do not supply a proven typed handler for any catalog ID. Native routing stays fail-closed until an exact mapping passes precondition, typed-bound, authoritative state read-back, save/reload, recovery and regression tests on an isolated profile.

The v39/v0.19.0 harness therefore remains \`GAME LINK · DISCONNECTED\`, and 0/222 is still the accurate native integration count. This audit is not evidence that the catalog UI has been connected to the game.

## Reproducibility

- Machine-readable matrix: \`NATIVE_DEBUG_CATALOG_COMPATIBILITY_V58.json\`.
- Validator checks catalog IDs, all 16 command codes, semantic-mismatch guards, and that no native catalog route is promoted.
- Source context: \`DEBUG_HUD_COMMAND_MAP_V43.md\`, \`NATIVE_DEBUG_DISPATCH_AUDIT_V51.md\`, and \`NATIVE_CHEAT_ADAPTER_REGISTRY_V52.md\`.
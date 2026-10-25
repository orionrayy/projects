# Cheats Sandbox — 222-entry implementation audit v32

Date: 2026-10-25  
Target game: Dungeon Quest Android 3.3.2.0

## Why this checkpoint exists

The user confirmed v31 opens the existing in-game Debug HUD, but correctly noted that the original cheat concept is much larger and has not been implemented. The full source-level registry has been recovered from the standalone reference: **222 entries across 14 categories**. The registry is a specification, not proof of native runtime support.

The current v31 implementation only routes Options → Cheat Menu into the shipped uai_gp_hud.onDebug(0) debug screen. It does not render all 222 registry entries. The separate Android harness has only 12 preview settings and explicitly reports GAME LINK • DISCONNECTED. Its toggles do not affect Dungeon Quest.

## Full design coverage

| Category | Entries |
|---|---:|
| Player & Survival | 27 |
| Combat Lab | 24 |
| Enemy AI | 20 |
| Loot & RNG | 19 |
| Economy Lab | 17 |
| Progression Lab | 16 |
| Inventory & Gear | 16 |
| Spawn & Encounter Lab | 9 |
| World & Physics | 22 |
| Camera & Visuals | 15 |
| UI & Accessibility | 3 |
| Skills Lab | 9 |
| Gear & Stats Lab | 7 |
| Debug Tools | 18 |
| **Total** | **222** |

## Native debug commands found in the supplied v3.3.2.0 build

| onDebug argument | Existing HUD action | Observed target/label | What is known |
|---:|---|---|---|
| 0 | onDebug | Open debug HUD | This route was confirmed by the user on v31. It is a UI route, not a cheat effect. |
| 1 | onClose | Close | Existing Debug HUD action. |
| 2 | onGotoLevel | GOTO Floor | Existing one-shot floor/navigation command. |
| 3 | onSetBoss | Set Boss | Existing command; precise state/persistence still unverified. |
| 4 | onSetLevel | Set Level | Existing level-setting command. |
| 5 | onDebugLevel | Main-HUD debug-level action | Exact effect requires more verification. |
| 6 | onDebugGold | Gold-up action | Disassembly shows a RewardGold call with fixed 100,000 Gold. Not an arbitrary-balance editor. |
| 7 | onDebugGoldDown | Gold-down action | Main-HUD action name observed; exact delta/effect still needs confirmation. |
| 8 | onCreateLegend | Create Legend | Existing item-fixture command. |
| 9 | onCreateMS | Create MS | Existing item-fixture command; exact item schema not verified. |
| 10 | onCreateCS | Create CS | Existing item-fixture command; exact item schema not verified. |
| 11 | onAddLevel | Add Level | Existing one-shot progression command. |
| 12 | onAddHeroic | Add Heroic | Existing one-shot difficulty/progression command. |
| 13 | onCreateFeat | Create Feat | Existing one-shot feat command. |
| 14 | onSetCrystal | Set Crystal | Existing currency/resource-related command; semantics and persistence not verified. |
| 15 | onSetEternal | Set Eternal | Existing currency/resource-related command; semantics and persistence not verified. |
| 16 | onAddBattle | Add Battle | Existing one-shot command; exact state write not verified. |

The currently visible debug.hud exposes 13 actions (codes 1–4 and 8–16). Codes 0, 5, 6, and 7 are found in the main HUD/action route but are not all visible as buttons in the Debug HUD.

## Registry-to-native integration status

Only three concepts have a partial mapping to the existing command surface:
- progression.player_level → Set Level / Add Level. This is not yet a tested slider adapter with snapshot, read-back, and rollback.
- economy.currency_override → Gold-up/down one-shot commands. This is not an arbitrary balance override; the decrement amount is unverified.
- inventory.grant_item → Create Legend / Create MS / Create CS. This does not provide arbitrary item IDs, affixes, level, rarity, quantity, or cleanup.

**Runtime effect verification: 0/222 catalog records.** This deliberately distinguishes “native command/asset exists” from “feature works and is safe when pressed.” The opened panel confirms route reachability only. All other catalog entries remain NOT_IMPLEMENTED_GAME_ADAPTER, not silently enabled mock controls.

## Why the remaining concepts are not simple UI toggles

The 222 concepts include persistent/continuous changes such as God Mode, infinite mana, damage multipliers, AI freeze, RNG control, no-clip, skill cooldowns, camera controls, equipment stat changes and item editing. They need real engine-state handlers, not just boolean flags in a menu. The supplied HUD/model format has a version-12 proprietary serializer; element records have not yet been decoded and round-trip validated sufficiently to safely insert a 222-entry page into the game's native HUD.

A feature must not be marked implemented merely because it appears in the registry or because an onDebug string exists. Each enabled control needs a traced native call path, typed argument validation, scene/context preconditions, sandbox-only save isolation, state read-back, and rollback/recovery behavior.

## Execution plan

1. Verify each existing debug command one at a time on an offline/disposable profile and record before/after state. Start with non-destructive commands; explicitly confirm before level, boss, item or currency changes.
2. Create a strict allow-listed command adapter for only verified native functions. Do not dispatch arbitrary native calls from registry JSON.
3. Complete partial adapters for level/progression, item fixtures, and debug currency using validation, read-back, reset/rollback, and regression checks.
4. Reverse-engineer the relevant engine state handlers for player/combat/AI/loot/skills/inventory/world/camera controls; until then these records stay disabled.
5. Decode and round-trip test version-12 HUD element records before replacing the 13-command debug view with a categorized catalog UI. Do not synthesize hundreds of UI elements using guessed binary record layouts.
6. Verify each feature individually on device and update status evidence. Keep cloud saves, leaderboards, achievements, account checks, purchase receipts and paid entitlements isolated/unchanged.

## Related checkpoints

- [v31 debug bridge](CHEAT_MENU_DEBUG_BRIDGE_V31.md)
- [Native debug route audit v20](MAIN_HUD_DEBUG_ROUTE_V20.md)
- [HUD binary format audit v19](HUD_BINARY_FORMAT_V19.md)
- [Original integration plan](CHEATS_SANDBOX_INTEGRATION_PLAN.md)

**Current status:** full 222-entry concept catalog is specified; Options route works on the user's device; the game currently exposes the old debug HUD with 13 actions; the 222-entry native integration remains incomplete. No claim is made that the standalone harness toggles change gameplay.

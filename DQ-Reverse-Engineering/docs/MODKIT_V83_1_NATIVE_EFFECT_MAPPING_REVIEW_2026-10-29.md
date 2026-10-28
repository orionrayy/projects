# Dungeon Quest ModKit v83.1 — Native Effect Mapping Review

Date: 2026-10-29  
Target: Dungeon Quest Android 3.3.2.0 ARM64  
Status: **Not complete; no install-ready v83.1 package produced**

## Confirmed native symbols

Static inspection of `libS3DClient.so` confirms the following native methods exist:

- `uai_gp_hud::RewardGold(S3DX::AIVariable)` at `0x65feec`
- `uai_gp_hud::RewardDust(S3DX::AIVariable)` at `0x65eeec`
- `uai_gp_hud::onDebug(int, AIVariable const*, AIVariable*)` at `0x6d5048`
- `uai_gp_hud::GetAvatar()` at `0x5fddcc`
- `AIAvatar::onSetVariable(int, AIVariable const*, AIVariable*)` at `0x2b60ec`
- `AIAvatar::onReduceHealth(...)` at `0x29c43c`
- `AIAvatar::onReduceMana(...)` at `0x29d43c`
- `AIAvatar::onSpendMana(...)` at `0x2b7f04`
- `AIAvatar::onReduceCD(...)` at `0x29bf4c`
- `AIAvatar::onKnockback(...)` at `0x297d84`
- `AIAvatar::onCC(...)` at `0x284f5c`
- `AIAvatar::onRewardExp(...)` at `0x2a01c8`
- `uai_gp_combat::onPlayerImmunity(...)` at `0x5c8e9c`

The `AIAvatar.aim` model exposes state variables including `nHealth`, `nMana`, `nArmor`, `nMoveX`, `nMoveY`, `bCanCC`, `bFrozen`, `bMoveable`, `bIsAI`, `bIsAlly`, and related combat flags. Their presence proves that the model has state with those names; it does **not** prove that writing each variable alone implements the requested cheat end-to-end.

## Existing menu behavior

The v82 debug HUD's serialized actions call `uai_gp_hud.onDebug` with a fixed numeric route. Those cases expose the stock debug actions and reward presets. The original and v82 `uai_gp_hud.aim` files are byte-identical; the v82 change is an asset/UI extension, not a new native dispatcher.

`AIAvatar::onSetVariable` obtains the object associated with the current AI model and calls the engine's object/AI-model variable dispatch. That method is target-object scoped. The existing HUD action format does not by itself prove that a new action would resolve to the player avatar rather than another avatar/enemy, and the game has many `AIAvatar` instances. A new direct action pointing at `AIAvatar` would therefore not be treated as a verified safe player-targeted adapter.

## Why the 50-item registry is not yet fully integrated

The 50 registry includes 20 sliders, 8 toggles, 7 numeric inputs, 4 selects and 11 actions. Several entries are one-shot operations already exposed by the stock debug callback. Many others require new game-loop behavior:

- survival and combat controls need correctly scoped handling in health, mana, crowd-control, cooldown and damage paths;
- multipliers need to affect calculations consistently, not merely set a label or a current value once;
- enemy controls must distinguish enemy AI from the player and allies;
- loot and reward rules require changes at drop-table / reward-generation points;
- auto-heal, snapshot and undo require persistent state and recurring or transactional logic.

There is currently no verified stable-ID dispatcher connecting these controls to those native code paths. `RewardGold`/`RewardDust` plus the existing `onDebug` routes do not cover these semantics. Filling the remaining controls with unrelated function names would create a visually complete but functionally false cheat menu.

## Build gate

A new install package is intentionally withheld until there is a real adapter for each of the 50 effect keys. At minimum, each adapter must have: (1) a correct player/enemy/global target, (2) argument/type validation, (3) a reset/off behavior for toggles, (4) no collision with stock debug actions, (5) serializer and APK split validation, and (6) runtime verification. No device runtime test has been performed in this review. No Logcat workflow is required or requested.

## Current deliverable status

- v82 remains a partial reward-preset candidate only.
- The first-50 roster remains a validated registry, not a completed implementation.
- No v83.1 XAPK is supplied by this review.

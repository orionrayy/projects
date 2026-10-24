# Cheat Catalog Implementation Matrix v32

Date: 2026-10-25  
Target game: Dungeon Quest Android 3.3.2.0  
Branch: `feat/dq-iap-debug-cheats-modkit-v7`

## Status answer

**No — the full concept is not implemented yet.** The full source design was recovered from the user's existing `cheats_options_standalone.html`: 222 stable-ID entries across 14 categories. That design itself is explicitly a source-level reference; all 222 entries were originally marked `requires_game_adapter`.

The user-confirmed v31 result proves that Options → Cheat Menu can open the built-in debug panel. It does **not** prove all built-in action effects, save persistence, reversibility, or the 222 catalog effects. Current integrated catalog coverage is **0/222 fully implemented; 0/222 runtime-verified**.

## Original catalog inventory

| Category | Count |
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

Current UI design contains toggles, sliders, select controls, ranges and action buttons. The existing Android harness only contains 12 preview flags and is disconnected from the game. The standalone HTML workbench has the original 222-entry catalog and its local-only staging/validation UI, but is not injected into the game APK.

## Evidence-backed native debug controls

The binary assets contain these existing action routes. These are the best candidates for an early implementation phase, but their actual effect and persistence have not yet been tested individually:

| Existing action | Existing route | Catalog integration status |
|---|---|---|
| `onClose` | `uai_gp_hud.onDebug(1)` | Asset route present; runtime effect not verified |
| `onGotoLevel` | `uai_gp_hud.onDebug(2)` | Asset route present; runtime effect not verified |
| `onSetBoss` | `uai_gp_hud.onDebug(3)` | Asset route present; runtime effect not verified |
| `onSetLevel` | `uai_gp_hud.onDebug(4)` | Asset route present; runtime effect not verified |
| `onDebugLevel` | `uai_gp_hud.onDebug(5)` | Asset route present; runtime effect not verified |
| `onDebugGold` | `uai_gp_hud.onDebug(6)` | Asset route present; runtime effect not verified |
| `onDebugGoldDown` | `uai_gp_hud.onDebug(7)` | Asset route present; runtime effect not verified |
| `onCreateLegend` | `uai_gp_hud.onDebug(8)` | Asset route present; runtime effect not verified |
| `onCreateMS` | `uai_gp_hud.onDebug(9)` | Asset route present; runtime effect not verified |
| `onCreateCS` | `uai_gp_hud.onDebug(10)` | Asset route present; runtime effect not verified |
| `onAddLevel` | `uai_gp_hud.onDebug(11)` | Asset route present; runtime effect not verified |
| `onAddHeroic` | `uai_gp_hud.onDebug(12)` | Asset route present; runtime effect not verified |
| `onCreateFeat` | `uai_gp_hud.onDebug(13)` | Asset route present; runtime effect not verified |
| `onSetCrystal` | `uai_gp_hud.onDebug(14)` | Asset route present; runtime effect not verified |
| `onSetEternal` | `uai_gp_hud.onDebug(15)` | Asset route present; runtime effect not verified |
| `onAddBattle` | `uai_gp_hud.onDebug(16)` | Asset route present; runtime effect not verified |
| `onDumpShaders` | `uai_gp_debug.onDumpShaderList()` | Asset route present; runtime effect not verified |
| `onLevelUp` | `uai_gp_hud.onShortcut("levelup", 1)` | Asset route present; runtime effect not verified |

## Partial candidate matches — not implemented

| Catalog ID | Possible existing route | Missing proof |
|---|---|---|
| `progression.player_level` | `debug.hud:onSetLevel → onDebug(4)` | Slider-to-command mapping, accepted bounds, read-back, persistence and rollback |
| `inventory.grant_item` | `onCreateLegend(8)`, `onCreateMS(9)`, `onCreateCS(10)`, `onCreateFeat(13)` | Existing actions only expose fixed variants; there is no verified arbitrary item-ID grant API |
| `economy.currency_override` | `hud.hud:onDebugGold(6)`, `onDebugGoldDown(7)` | Exact amounts, direct set-to-value, bounds, balance read-back, persistence and rollback |

Those three IDs are classified as partial **candidates**, not connected handlers. The remaining **219** catalog entries still require a verified game adapter. The 222-entry source catalog remains disabled for game writes.

## Why the rest cannot truthfully be called implemented

Most planned entries (god mode, infinite health, enemy AI, RNG/loot policies, economy multipliers, arbitrary inventory grants, spawn/cleanup, no-clip, physics, camera overrides, skills/stat calculations and debug snapshots) require state access or engine callbacks that are not available through the existing HUD action table alone. The original native binary exports some high-level calls, but the repository does not yet have a validated per-setting runtime contract, supported call thread, read-back path or rollback proof for these settings.

The HUD element serialization is not yet losslessly decoded/serialized. Adding 222 elements by guessing bytes risks breaking the pause/options UI, even though the v31 route now opens. So this update restores and audits the complete catalog rather than claiming that a 222-row UI makes 222 real effects.

## Implementation sequence

1. **Use existing debug routes first:** verify each built-in action on an offline disposable profile, including set-level, floor, boss, fixed reward variants and gold debug controls. Record before/after values and confirm whether changes persist.
2. **Build a catalog-to-handler registry:** each ID needs a stable native/action mapping, argument schema, exact-build fingerprint, risk level, snapshot/read-back, undo/restore method and failure state. Do not enable a setting on label similarity alone.
3. **Expand the HUD with a validated serializer:** round-trip original `pause.hud` and `debug.hud` byte-for-byte before introducing pagination/search/categories or actions. A format-preserving row and action entry must be proven independently first.
4. **Implement in narrow groups:** survival/player stats → progression/resources → inventory/reward items → combat/enemy state → loot/spawn/world/visuals → diagnostics. One command at a time; verify state read-back and rollback after each.
5. **Keep sandbox isolation fail-closed:** offline disposable profile, no normal/cloud saves, no leaderboard/achievement writes. Purchase receipts and paid entitlements remain outside the cheat adapter.

## Artifacts committed in this revision

- Full original 222-entry reference catalog: `cheats-sandbox/debug_cheats_catalog_v32.json`
- Full per-ID implementation/evidence matrix: `docs/CHEAT_CATALOG_IMPLEMENTATION_MATRIX_V32.json`
- This human-readable audit and phased plan.

No new XAPK is claimed by this revision. The next gameplay-changing XAPK should only be made after the first small group of native handlers and HUD edits can be verified, not by enabling 222 unbacked controls.


## Increment v32 — three additional native-command controls

The user confirmed the v31 route opens the bundled debug HUD. The v32 XAPK statically adds three more controls using callback names already present in the game's original HUD action tables:

- **Level Up** → `uai_gp_hud.onShortcut("levelup", 1)`
- **Gold +100K** → `uai_gp_hud.onDebug(6)`
- **Gold Down** → `uai_gp_hud.onDebug(7)`

The debug HUD grows from 71 to 75 elements and from 13 to 16 actions. All original element records remain byte-for-byte identical. The STK pack header key matches the decoded metadata-table CRC32 and all 5,630 entries pass local decode/CRC validation. Only the decoded `Resources/HUD/debug.hud` entry changes. All 20 APK split signatures and ZIP CRCs pass a local verifier.

Artifact: `Dungeon_Quest_3.3.2.0_CheatMenu_ExpandedDebug_v32.xapk`  
SHA-256: `7fdec74ef3d3f1d0b9f506e60f1adfd2f61d5dea821c07c88974ab5584f1cc32`

**Runtime pending.** The user has not yet tested v32. The +100K callback is statically mapped; exact Gold Down behavior is not established. The newly exposed controls do not implement 222 catalog entries and do not make unsupported toggles work. Do not mark any catalog effect runtime-verified until the user confirms the control and its resulting game state.


## Increment v33 — button-only Gold adjustment controls

The user reported that the v32 screen looked unchanged. The reason the previous Gold page may not have appeared is that the custom root tab did not become visible in the active UI. v33 therefore places the new controls inside the existing **Add** tab.

Four buttons were added, ordered left-to-right: **Gold -10**, **Gold -1**, **Gold +1**, **Gold +10**. They call the native model methods `uai_gp_hud.SpendGold(10.000)`, `SpendGold(1.000)`, `RewardGold(1.000)` and `RewardGold(10.000)`, respectively. No new numeric text box or keyboard entry was added. The three existing Add buttons are moved/resized to create room.

- Artifact: `Dungeon_Quest_3.3.2.0_CheatMenu_GoldSteppers_v33.xapk`
- XAPK SHA-256: `65e4cdc2284e02747c9eb942edc171588209cb4ffba723892f52cabe1ad81a3d`
- Debug HUD: 75 elements, 17 actions.
- STK: all 5,630 entries decode/CRC-check; header key equals CRC32 of the decoded metadata table; only `Resources/HUD/debug.hud` changes.
- APK: 19 non-base splits are byte-identical to v31; only `assets/S3DMain.smf` changes in the base APK outside signature metadata.
- Signing/packaging: local v2 signer check and inner/outer ZIP CRC checks pass.
- Runtime: **not yet tested**. Native `RewardGold`/`SpendGold` method names are present in the binary, but the new direct numeric action binding still needs an on-device test.

This is the first visible stepper UI for Gold only. The full 222-cheat design still has 0 entries fully implemented and runtime-verified; unverified controls remain blocked by the native adapter boundary. No billing receipts or paid entitlement code was modified.

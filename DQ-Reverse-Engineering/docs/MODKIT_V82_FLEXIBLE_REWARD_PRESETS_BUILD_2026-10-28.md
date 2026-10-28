# Dungeon Quest ModKit v82 — Flexible Reward Presets

**Build status: static validation passed. Device runtime not tested.**

- Artifact: `DQ_ModKit_v82_FLEXIBLE_REWARDS_ARM64.xapk`
- Package ID: `com.shinybox.dqv82`
- Size: 57,732,234 bytes
- SHA-256: `208302002c967ba6462cd5c027ac25a085355c8f64aa4a55d08352a85c4c50fc`
- Split APK count: 20
- Local test signer SHA-256: `79718291efed7f9ad6124132265eba415c65831da7aa15856c88d539a7ed49c9`

## User request addressed

The user reported v80 had duplicate / unnecessary actions and some controls did not work. This build removes two redundant debug-page controls, keeps existing core actions, and adds a small bounded set of amount presets for two existing AIM model functions.

## HUD delta

Source: v80 debug HUD, 73 elements and 15 action records.  
Candidate: v82 debug HUD, 82 elements and 24 action records.

Removed from debug-page Add group:
- `levelup_btn_v80` / action `onLevelUp`: duplicates main-HUD `onLevelUp → uai_gp_hud.onShortcut("levelup", 1)`.
- `gold100k_btn_v80` / action `onDebugGold`: duplicates main-HUD `onDebugGold → uai_gp_hud.onDebug(6.0)`, a fixed +100,000 Gold action.

Retained:
- Add Levels
- Add Battle
- Add Heroic

Added 11 amount presets:
- Gold: +1, +10, +100, +1,000, +10,000.
- Dust: +1, +10, +100, +1,000, +10,000, +100,000.

Each new control has a unique HUD element ID and callback. New serialized action expressions call `uai_gp_hud.RewardGold(amount)` or `uai_gp_hud.RewardDust(amount)`. Both function names are present in the source `uai_gp_hud.aim` function table. This is static call-site evidence only; the actual invocation/effect has not been confirmed in the running game.

## Static validation results

- All 5,630 STK entries decode and pass CRC/size checks.
- Rebuilt STK header key equals CRC32 of decoded metadata table.
- HUD parser round-trip passes.
- Removed duplicate element/action IDs are absent.
- All 11 new button labels, stable element names, callback IDs and literal amounts pass exact serialized-expression checks.
- XAPK manifest inventory: 20/20 splits.
- Outer XAPK and all inner APK ZIP CRCs: PASS.
- All 20 APKs have package ID `com.shinybox.dqv82`.
- All 20 APKs use the same local test certificate.
- APK signature schemes v1/v2/v3: PASS on all 20 splits.
- Native library 16-KiB alignment: PASS on all 20 splits.
- DEX SHA-1/Adler32: PASS.

## Phone test

1. Install v82 with an XAPK-capable installer.
2. Do not uninstall the official game or clear its data; v82 uses a separate package ID.
3. Open Pause → Options → Cheat Menu → Add.
4. Test only `Gold +1` first; compare the visible Gold count before/after.
5. Separately test `Dust +1`; compare the actual Dust count.
6. If either action does nothing or crashes, stop using that action. Do not infer success from a visible button.

## Scope boundary

This build **does not implement the full 50-cheat catalogue**. It implements 11 reward amount presets and removes two duplicated actions. The generic list population/stable-ID dispatcher and the required exact handlers for God Mode, custom health/damage/cooldown multipliers, arbitrary balance setters, and other catalog entries remain unresolved. Those controls must not be marked enabled or functional until exact-build typed input handling, authoritative state read-back, save/reload and rollback pass.

Device install, launch, individual effect deltas, persistence, and force-close status were not tested by the build environment. The artifact is a local-test-signed package, not an official signed release.

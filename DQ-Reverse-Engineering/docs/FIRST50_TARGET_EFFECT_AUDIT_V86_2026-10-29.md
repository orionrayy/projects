# First-50 target effect audit — v86

**Status: static source evidence passed; runtime effects remain unverified.** This audit checks the exact Dungeon Quest Android 3.3.2.0 ARM64 stock library and resource hashes found in the restored local artifacts. It makes no modifications to game assets/binaries and does not produce an APK/XAPK.

## Exact-build identity

- Stock ARM64 native library SHA-256: 0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083.
- AI model uai_gp_hud.aim SHA-256: 66607a46a23eeaab4fa2dac02772adbea5ab71e65d4e446e49396c6af6a451cb.
- debug.hud SHA-256: 02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6.
- pause.hud SHA-256: 12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395.

The audit decodes version-12 HUD action framing, matches eleven named static calls to uai_gp_hud.onDebug, and validates seven exact-build AArch64 symbols plus a Gold-reward callsite. Original binaries and asset payloads are not committed.

## Findings

The following eleven catalog entries have static HUD-call matches: progression.player_level (onSetLevel, 4), progression.floor_target (onGotoLevel, 2), progression.add_levels (onAddLevel, 11), inventory.grant_legend_fixture (onCreateLegend, 8), inventory.grant_mythstone_fixture (onCreateMS, 9), inventory.grant_character_stone_fixture (onCreateCS, 10), inventory.grant_feat_fixture (onCreateFeat, 13), rewards.add_battle (onAddBattle, 16), rewards.add_heroic (onAddHeroic, 12), rewards.add_crystal (onSetCrystal, 14), rewards.add_eternal (onSetEternal, 15).

These are call-site candidates only. The onSetLevel code uses key hud.level, which is not proof of authoritative player-level mutation. Command 6 directly calls RewardGold with a fixed 100000 literal; it is not a flexible Gold amount handler. The stock call graph does not prove a generic stable-ID dispatch adapter for the remaining catalog entries.

## Status and reproduction

The catalog retains 50 unique IDs, zero fully integrated handlers and zero runtime-verified cheats. Runtime effect read-back, save/reload and rollback are 0/50. No APK was built and no device test was reported.

After extracting the exact resources and matching native library, run:

    python tools/audit_first50_target_effects_v86.py --registry cheats-sandbox/first50_flexible_cheats_v81.json --assets-root /path/to/Resources --native-lib /path/to/libS3DClient.so --report /tmp/first50-v86.json

CI runs the six parser/catalog unit tests and a catalog-only audit without committing proprietary assets. This is an evidence gate, not a release approval.

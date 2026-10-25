# Dungeon Quest ModKit checkpoint — v60

Date: 25 October 2026 (WIB)
Repository: \`orionrayy/projects\`
Branch: \`feat/dq-iap-debug-cheats-modkit-v7\`
Base: v59 head \`befe0199e205162da6746aa8bf13cc8dff18a8fc\`

## Completed
- Extracted the source 3.3.2.0 STK from the Library XAPK and locally decoded the selected HUD/AIM assets; all 5,630 source STK records passed CRC/size checks.
- Extracted stock and v50 copies of \`libS3DClient.so\`; both hashes match the pinned native library SHA-256.
- Correlated the \`uai_gp_hud.aim\` function-vs-handler name tables against demangled AArch64 symbol addresses and sizes.
- Audited seven native method bodies plus the model surface: \`RewardGold\`, \`RewardDust\`, \`SpendGold\`, \`onSetGold\`, \`onSetHealth\`, \`onSetMana\`, \`onSetLevel\`, and \`onStatIncrease\`.
- Added a machine-readable audit report, fail-closed validator, six synthetic tests and dedicated CI workflow. Local validator PASS; tests 6/6 PASS.

## Finding
\`RewardGold(AIVariable)\` is a real model function with numeric add-like behavior, but the exact safe HUD-to-function invocation contract and runtime state read-back are still unproven. \`onSetGold\` is a handler that formats/forwards a value to an indirect model/UI call; it is not established as an authoritative balance setter. The health/mana/level callbacks are similarly not promoted based on names.

## Status deliberately unchanged
- Catalog: 222 IDs / 14 categories; catalog routes 0/222, runtime-verified effects 0/222.
- The separate Gold +100K action remains static-only (runtime-verified 0/1).
- v50 runtime manifest remains blocked (0/9).
- Harness remains emulator-smoke-tested and disconnected from the original game.
- No game assets, native library, APK or XAPK was changed or built.

## Next gate
Recover the documented engine invocation contract for a native model function or an authorized model extension workflow. Then prove one bounded action end-to-end on a disposable offline profile: HUD input → typed allow-listed handler → authoritative state read-back → save/reload → regression and backup/restore. Keep the 222-entry catalog fail-closed until evidence exists.

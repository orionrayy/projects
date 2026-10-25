# DQ Modkit & Cheats Harness progress checkpoint — v54

Date: 2026-10-25 (WIB)
Repository: `orionrayy/projects`
Branch: `feat/dq-iap-debug-cheats-modkit-v7`
Pull request: [#26](https://github.com/orionrayy/projects/pull/26) — **open, draft, unmerged**
Checkpoint baseline HEAD at capture: `731234f6e89e11cec07e6408d13fdbb2655629d3`

## Verified since the prior checkpoint

### Android Cheats Sandbox harness

- Latest complete Android harness workflow: [run 40190901392](https://github.com/orionrayy/projects/actions/runs/40190901392), conclusion **success**.
- Android emulator instrumentation and launch job `121161695721`: **success**. It ran on Android API 28 (the current workflow's emulator target at that revision), instrumentation assertions passed, APK installed, launcher Activity started, and the disconnected-state UI boundary was observed.
- Latest static reverse-engineering validation: [run 40190901397](https://github.com/orionrayy/projects/actions/runs/40190901397), conclusion **success**. The job includes the STK/HUD parser, serializer, v48 delta verifier, v50 candidate, v52 adapter registry, v53 HUD List audit, catalog, and matrix validations.
- Canonical catalog check: 222 unique IDs, 14 categories, identical source/Android asset bytes, valid control defaults and numeric bounds/steps.
- The latest build artifact is `dq-cheats-sandbox-harness-debug-apk` (Actions artifact ID `12598620075`). Its ZIP is 52,867 bytes and contains `app-debug.apk` (56,188 bytes). APK SHA-256: `172f0d1e15197d49a850b6af3da7bd78cf8aa1dbca6bdc8fea5b847c30d24a0c`.
- Harness functionality covered by its instrumentation includes category filtering, toggling a local draft, undo/Active view, lazy scroll batch loading, ID search and preservation of the disconnected-state banner. These are harness features, not game-side cheat effects.

### Original Dungeon Quest candidate package

- Local v50 candidate package recheck is documented in [MODKIT_V50_PACKAGE_RECHECK_V52.md](MODKIT_V50_PACKAGE_RECHECK_V52.md). Original XAPK/STK identity is recorded there.
- Candidate STK SHA-256: `e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e`; 5,630/5,630 records decode and validate; exactly one decoded entry differs: `Resources/HUD/pause.hud`.
- The modified pause HUD has one `Gold +100K` button routed to `uai_gp_hud.onDebug(6.0)`. Static ARM64 disassembly associates branch 6.0 with `RewardGold(100000.0)`. This is binary-level candidate wiring only.
- The game candidate APK and split XAPK in the package-recheck report are locally signed with a test certificate and are not committed. They cannot update an official-signed installation in place. Installation, game startup, visibility/touch dispatch, actual Gold delta, save/reload persistence and save safety remain **not verified**.

## Native integration status — unchanged hard blocker

- Current registry: [NATIVE_CHEAT_ADAPTER_REGISTRY_V52.md](NATIVE_CHEAT_ADAPTER_REGISTRY_V52.md).
- Catalog routes assigned: **0/222**.
- Catalog effects runtime-verified in the original game: **0/222**.
- Separate native candidate actions: **1**, runtime-verified: **0**.
- All 222 catalog items remain `requires_game_adapter`. The fixed +100,000 Gold action is deliberately not mapped to `economy.currency_override`, which is a set-to-target slider rather than a one-shot increment.
- Current List audit: [HUD_LIST_LAYOUT_AUDIT_V53.md](HUD_LIST_LAYOUT_AUDIT_V53.md) confirms one serialized type-3 List example in `match_result_anim.hud`, but no proven model-side path yet populates 222 cheat rows, dispatches selected stable IDs, or calls safe, bounded handlers.
- The standalone harness explicitly keeps `GAME LINK · DISCONNECTED`; it does not modify the game engine, live stats, saves, IAP, cloud data, achievements or leaderboards.

## Next work, in order

1. Keep the passing harness build/instrumentation and catalog validation green.
2. On a disposable Android profile, test the separate game candidate without removing the official installation; first verify backup/recovery, then launch, pause UI visibility, button tap, exact +100,000 Gold delta, save/reload and regression behavior.
3. If the candidate fails any runtime gate, do not label it usable; isolate the fault to HUD rendering, input/action dispatch, or save/state update.
4. Do not expose the 222-item menu as functional until the in-engine List population path and a stable-ID → allow-listed native handler contract are proved. Unknown/unmapped entries remain disabled.

## Overall assessment

The **standalone Cheats Sandbox APK is build- and emulator-smoke-tested**. The **v50 Dungeon Quest package is still a statically validated experiment**. The intended 222-cheat native integration is **not complete** (0/222 runtime-verified). PR #26 stays draft/unmerged pending the original-game runtime gate.
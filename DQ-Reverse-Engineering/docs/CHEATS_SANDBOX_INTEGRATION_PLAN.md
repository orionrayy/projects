# Cheats Sandbox — Integration boundary and implementation plan

## Target

Add a first-party Cheats (Sandbox) page inside Pause -> Options with searchable categories, favorites, setting controls, safe presets, undo/reset, snapshots, diagnostics and an event log. The standalone prototype/catalog are design artefacts only, not evidence of game handlers.

## Evidence-backed UI path

Static inspection of the recovered v3.3.2.0 assets confirms:
- `Resources/HUD/pause.hud`: Options entry plus `onShowOptions`, `onOptionsClose`, and `onResume`.
- `Resources/AIModels/uai_gp_options.aim`: `onShowOptions`, `onShowTab`, `onSaveOptions`, `onSetControlsOption`, and `onSetGameplayOption`.
- `Resources/HUD/debug.hud`: existing debug controls including `Add Levels`, `Add Feat`, and `GOTO Floor`.
- `Games/Smash.gam`: both `uai_gp_options` and `uai_gp_debug` are registered model names.

The evidence confirms asset/model presence, **not** a working Options -> debug HUD transition. No such event binding has been established.

## v16 bridge

`runtime-adapter/src/main/java/dev/dqdebug/runtime/PauseOptionsCheatsBridge.java` provides the single route-facing entrypoint. It requires the real Options host to confirm the parent route and the entry callback registration. It passes a fail-closed readiness state to the page presenter:
- `READY`: isolated sandbox save, offline mode, cloud/leaderboard/achievement submissions disabled, and a complete runtime snapshot hydrated.
- `READ_ONLY`: any gate/snapshot missing.
- `RECOVERY_REQUIRED`: a previous mutation rollback could not be verified; Apply and actions must remain blocked until runtime reconciliation.

No adapter is registered by this class and it performs no game-state writes. The catalog-bound controller must revalidate every mutation.

## Status and constraints

- Route bridge source: `IMPLEMENTED`.
- Java/Python contract tests: `UNIT-VERIFIED` when CI is green.
- Actual Pause -> Options hook: `BLOCKED`; requires authorized source/UI authoring source or a validated serializer for S3D HUD/model data.
- In-game runtime click path: not verified.
- APK build/sign/install: not performed.

The original HUD/model assets use a proprietary binary serialization format. We intentionally do not rewrite `pause.hud` by guessing record layouts; a malformed scene could break the entire Pause/Options menu.

## Next integration milestone

Implement `OptionsUiHook` at a verified source callsite or through a format-correct HUD edit. Then render the page using the catalog-bound controller, wire a read-only host snapshot first, prove save isolation and offline gates, and test a reversible adapter with apply/read-back/reset plus forced rollback and recovery tests. Do not mark the route `RUNTIME-VERIFIED` until exercised in the exact-version APK.

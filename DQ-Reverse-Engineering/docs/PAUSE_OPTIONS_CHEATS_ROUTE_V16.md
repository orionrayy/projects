# Pause -> Options -> Cheats (Sandbox) route work — v16

**Evidence date:** 2026-10-24  
**Target:** Dungeon Quest Android `com.shinybox.smash` v3.3.2.0  
**Scope of this increment:** connect the UI integration seam and make readiness/recovery state fail closed. This is not a claim that the in-game button is already wired.

## Directly observed in the recovered assets

- `Resources/HUD/pause.hud` contains the `options` entry and callbacks `onShowOptions`, `onOptionsClose` and `onResume`.
- `Resources/AIModels/uai_gp_options.aim` contains `onShowOptions`, `onShowTab`, `onSaveOptions`, `onSetControlsOption` and `onSetGameplayOption`.
- `Resources/HUD/debug.hud` contains existing test-control labels/actions including `Add Levels`, `Add Feat`, `GOTO Floor`, `onCreateFeat` and `onGotoLevel`.
- `Games/Smash.gam` lists both `uai_gp_options` and `uai_gp_debug` models.

These are `STATIC-DIRECT` observations. They do **not** prove that a click in Options can open the existing debug HUD. The currently recovered Pause HUD has no demonstrated event binding from the Options panel to `uai_gp_debug`.

## What v16 implements

`runtime-adapter/src/main/java/dev/dqdebug/runtime/PauseOptionsCheatsBridge.java` is the only route-facing entry point in this increment. It declares a stable child route ID (`pause.options.cheats_sandbox`), requires the actual host UI to confirm that the `pause.options` route exists, and requires a positive callback-registration result before it reports `INSTALLED`.

On selection it routes to a page presenter with one of three statuses:

- `READY` — all required sandbox/offline/save-isolation checks pass and the game-owned runtime settings snapshot is hydrated.
- `READ_ONLY` — the page may display diagnostics and configuration metadata, but mutation must remain disabled because at least one gate or runtime snapshot is missing.
- `RECOVERY_REQUIRED` — a mutation rollback was not verified; the page must block Apply and actions until the host reconciles a complete runtime snapshot.

The bridge never writes game state itself and never creates guessed defaults. The catalog-bound controller must re-check gates during every apply/action; a page-level flag is not a security boundary.

## Integration boundary still blocking the in-game click path

The actual `OptionsUiHook` must be implemented using a verified original UI source callsite or a format-correct edit to the S3D HUD/model. The public source tree does not contain a validated `.hud` serializer/authoring pipeline, nor complete game source/build files. We therefore did not make a byte-level `pause.hud` edit by guess, because a damaged serialized scene could prevent the entire pause/options UI from loading.

No `Cheats (Sandbox)` menu entry has been verified in a running APK. No gameplay adapter is registered by this bridge. Existing debug controls remain separate and are not wired as cheat effects.

## Verification

- `PauseOptionsCheatsBridgeSelfTest` covers route absence, positive callback registration, click dispatch, idempotent install, registration failure, online/read-only gating, recovery lock, unknown runtime state, and missing host adapters.
- `validate_pause_options_cheats_route_v16.py` validates source-contract markers and enforces the honest `BLOCKED` route-binding/runtime status until direct hook evidence exists.
- CI compiles this Java seam and runs the dependency-free Java assertions and Python contract tests.

Status ledger: bridge `IMPLEMENTED`; tests `UNIT-VERIFIED`; actual in-game route `BLOCKED`; runtime `RUNTIME-VERIFIED: 0 claims`.

## Exact next prerequisite

Provide the authorized original S3D UI source/authoring project or a validated serializer that can add a child entry and event binding to the original Options HUD. Then implement `OptionsUiHook` against the real menu, route the click to a page backed by the catalog-bound controller, build/install the exact-version test APK, and verify the full click path on-device. Until that step, the bridge remains the tested seam—not the finished connection.

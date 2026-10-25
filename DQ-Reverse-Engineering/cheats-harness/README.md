# DQ Cheats Sandbox Harness — Android APK target

This is a standalone Android UI/controller harness, **not a modified Dungeon Quest APK**. Version 0.19.0 loads the canonical v39 catalog as an Android asset: 222 stable IDs across 14 categories.

## Included

- All catalog entries with category tabs, search by label/description/stable ID/tag, favorites and an Active filter for values different from defaults.
- Lazy, scrollable card rendering in batches to keep the initial view lightweight.
- Typed local controls for toggles, numeric sliders with exact-value input and ±1/±10 steppers, min/max range controls, enum selections, and action-request previews.
- Deterministic local draft state with numeric/range/step validation, 30-deep undo, presets, reset, JSON export/share and a bounded event log.
- A permanent `GAME LINK · DISCONNECTED` banner. Each control only changes a local draft or logs a preview request. Nothing writes to Dungeon Quest process memory, native state, files, IAP, saves, cloud data, achievements, or leaderboards.

## Verified build

Latest successful Android workflow: [run 40186288008](https://github.com/orionrayy/projects/actions/runs/40186288008).

The run passed both jobs:
- Catalog integrity, JVM unit tests and `assembleDebug`, followed by artifact upload.
- Android emulator instrumentation; installing the built APK; launching `MainActivity`; and checking the title and explicit disconnected-state UI.

APK artifact name: `dq-cheats-sandbox-harness-debug-apk`  
APK SHA-256: `4cd90e232c6bdccc874dc23a9b92a13c755281d112647c1f931f4cad7cdae38d`  
APK size: 56,185 bytes  
Emulator diagnostics artifact: `dq-cheats-sandbox-harness-emulator-diagnostics`

The CI smoke test used Android API 28 (x86). The app has minSdk 23 and targets API 34; compile SDK is API 35. This is successful automation evidence for the harness UI, not a test of the modified Dungeon Quest package.

## Build

The workflow `.github/workflows/dq-cheats-harness-android.yml` uses Android Gradle Plugin 8.7.3, Gradle 8.9, JDK 17 and Android compile SDK 35.

## Integration boundary

All 222 catalog entries currently use `integration_status = requires_game_adapter`. That means **0/222 cheats are connected to or runtime-verified in the original game**. The v50 Gold +100K game package is a separate local test candidate; its HUD edit is structurally validated but not proven visible or functional in live gameplay. See [the v51 native debug-dispatch audit](../docs/NATIVE_DEBUG_DISPATCH_AUDIT_V51.md).

Do not report a staged toggle or action preview as a functioning game cheat. Keep the original app and save untouched until any candidate has a verified backup/restore path and has passed install, launch, input, effect, persistence and regression testing.

# DQ Cheats Sandbox Harness — Android APK target

This is a standalone Android UI/controller harness, not a modified Dungeon Quest APK. Version 0.19.0 now loads the full v39 catalog as an Android asset and renders all 222 stable IDs across 14 categories.

## Included

- All 222 catalog entries in a vertically scrollable list, with category tabs, name/description/ID/tag search, favorites, and an Active filter for values that differ from the defaults.
- Typed local controls for toggles, numeric sliders with exact entry and ±1/±10 steppers, min/max range controls, enum selections, and action-request previews.
- Deterministic local draft state with range/step validation, 30-deep undo, presets, reset, JSON export/share and a bounded event log.
- An explicit permanent GAME LINK • DISCONNECTED status. Every action is a local draft or preview request; nothing writes to Dungeon Quest's process, files, native state, IAP, saves, cloud data, achievements, or leaderboards.
- CI build, unit tests and an Android API 35 x86_64 emulator smoke test that verifies catalog count, filtering, local staging, undo/reset and the disconnected state.

## Build

The workflow `.github/workflows/dq-cheats-harness-android.yml` builds `app-debug.apk` with Android Gradle Plugin 8.7.3, Gradle 8.9, JDK 17 and Android API 35. After a successful run, download the artifact named `dq-cheats-sandbox-harness-debug-apk`.

## Integration boundary

This is **not** an integrated Dungeon Quest mod. The separate Android app cannot directly modify another app's memory/state; the original game's Pause → Options → Cheats route and verified gameplay adapter remain blocked. The original-game v50 STK candidate is a separate asset-level experiment and has not been built into an APK. Do not report a staged toggle or action request as a functioning game cheat.

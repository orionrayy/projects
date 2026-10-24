# DQ Cheats Sandbox Harness — Android APK target

This is a buildable standalone Android UI/controller harness, not a modified Dungeon Quest APK. It gives the project a reproducible Android build target for iterating on Cheats/Sandbox controls while the proprietary game UI/runtime hook remains blocked.

## Included

- Native Android UI with categories, boolean/range controls, presets, undo, reset, export, and recent local event log.
- Deterministic local SandboxState with bounds validation and unit tests.
- Explicit permanent GAME LINK • DISCONNECTED status. UI edits preview data in this app's memory only; it cannot mutate Dungeon Quest.
- CI builds a debug-signed APK and uploads it as the dq-cheats-sandbox-harness-debug-apk workflow artifact.

## Build in GitHub Actions

Push changes under this folder or run the workflow manually. The workflow compiles, runs unit tests, builds app-debug.apk, and uploads it. The build pipeline uses Android Gradle Plugin 8.7.3, Gradle 8.9, JDK 17, and Android API 35.

## Important boundary

The app does not attach to or patch another Android application. Android's app sandbox prevents a separate app from directly writing Dungeon Quest's process memory/state. The actual in-game Cheats row still requires the authorized original UI source/authoring pipeline and verified runtime-state APIs. Do not call this APK a Dungeon Quest mod or claim its toggles change gameplay.

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

## Build result — 2026-10-24

Latest recorded successful build: [GitHub Actions run 40096718673](https://github.com/orionrayy/projects/actions/runs/40096718673/job/120880408274). The `testDebugUnitTest` and `assembleDebug` tasks passed. [Download the APK artifact](https://github.com/orionrayy/projects/actions/runs/40096718673/artifacts/12560834028) (extract `app-debug.apk` from the downloaded ZIP).

Recorded APK SHA-256: `99be5a030ed10f72e7d0796425260303a760fe451d520d50d473e57759d2b00d`; size 19,766 bytes. This is the standalone harness, not a modified Dungeon Quest APK. Device launch and the original in-game Pause -> Options route remain unverified.


## Emulator validation

The Android API 35 CI job runs JVM unit tests and packages the debug APK, then runs the instrumentation test in an x86_64 emulator and checks installation, launcher startup, and the visible disconnected status. This is a harness-only smoke test; it does not test the ARM64 Dungeon Quest engine or gameplay effects.

The emulator action executes script lines in separate shell invocations, so the workflow deliberately uses environment paths directly rather than relying on shell-local variables. Check the current PR workflow result before treating the emulator step as passing.

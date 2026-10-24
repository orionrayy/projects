# Android build status

Build target: DQ Cheats Sandbox Harness (dev.dqdebug.sandboxharness).

- Android source project: present.
- UI/controller: implemented as a standalone local-preview harness.
- Unit tests: included for deterministic state, undo/presets/reset, bounds, export disclosure, and disconnected adapter state.
- CI build: performed by .github/workflows/dq-cheats-harness-android.yml; successful artifact is published as dq-cheats-sandbox-harness-debug-apk.
- Dungeon Quest package integration: BLOCKED / NOT INCLUDED.
- In-game Pause -> Options hook: BLOCKED.
- Gameplay effects verified: 0.
- APK runtime test on device: not claimed by CI.

This file must be updated only from the actual workflow result; source presence alone is not evidence that Gradle produced an APK.

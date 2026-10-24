# Android build status

Build target: DQ Cheats Sandbox Harness (`dev.dqdebug.sandboxharness`).

## Latest verified CI build

- Workflow run: [40096718673 — successful](https://github.com/orionrayy/projects/actions/runs/40096718673/job/120880408274).
- Source branch head: `036e3401d007148acd2ea4d0238281936871b4be`.
- Build/test tasks: `testDebugUnitTest assembleDebug` — both completed successfully.
- APK artifact: [dq-cheats-sandbox-harness-debug-apk](https://github.com/orionrayy/projects/actions/runs/40096718673/artifacts/12560834028).
- APK file: `app-debug.apk`, 19,766 bytes.
- APK SHA-256: `99be5a030ed10f72e7d0796425260303a760fe451d520d50d473e57759d2b00d`.
- Workflow artifact ZIP digest: `sha256:19e59943ae7299eb75a31e1cff14b0123d898a74c4e8be8e5e27c5ce005e8c07`.
- Artifact expiry: 2026-11-23 13:07:34 UTC (30-day retention).

## Explicit boundary

- Android source project: present.
- UI/controller: standalone local-preview harness.
- Unit tests: successful; deterministic state, undo/presets/reset, bounds, export disclosure, and disconnected adapter state.
- Dungeon Quest package integration: **BLOCKED / NOT INCLUDED**.
- In-game Pause -> Options hook: **BLOCKED**.
- Gameplay effects verified: **0**.
- APK launch on a physical device/emulator: **not verified by this CI run**.

The successful CI run proves that Gradle assembled the debug APK and the harness unit tests passed. It does not prove an in-game route, runtime cheat effect, or device install/launch.

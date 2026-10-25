# Dungeon Quest ModKit checkpoint — v65

Date: 25 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
Base: v64 commit b124b9ea8e8b64b5e3a3dbff8d50c7e96f1e3252

## Completed
- Read the exact stock classes.dex and pinned its SHA-256.
- Mapped the DEX CodeItem for S3DRenderer.onDrawFrame: initialization guard fields, engineShutdown at code unit 9, engineInitialize at 12, bInitialized write at 15, and engineRunOneFrame at 25.
- Discovered a key safety issue: the existing renderer does not consume the boolean result of engineInitialize and marks bInitialized true unconditionally. Any native probe or callback must add an explicit init-success gate and failure/retry handling.
- Mapped the lifecycle shutdown route: S3DSurfaceView.onTerminate queues a Runnable through GLSurfaceView.queueEvent; that Runnable calls S3DRenderer.onShutdown, which calls engineShutdown.
- Added a machine-readable read-only report, validator, six tests and dedicated CI workflow.

## Status unchanged
- The audit only reads DEX; no DEX edit was applied.
- v64 native probe remains source-only and is not packaged into the app.
- Catalog routes 0/222; runtime effects 0/222; Gold candidate runtime 0/1; v50 runtime gate 0/9.
- No APK/XAPK was built.

## Next gate
Build a deterministic DEX callsite patcher with branch/register relocation tests only after the full callback lifecycle is specified. First make any generated patch prove that engineInitialize success is checked, registration is idempotent, and unregister occurs on the GLSurfaceView renderer thread before every engineShutdown. Then test the no-op callback in an isolated authorized build.

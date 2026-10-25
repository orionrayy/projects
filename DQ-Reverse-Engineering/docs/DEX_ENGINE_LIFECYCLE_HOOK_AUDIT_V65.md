# Dungeon Quest Java/native engine-lifecycle hook audit — v65

**Result: a concrete DEX initialization/shutdown seam is identified, but a safe callback insertion patch has not been made.** The important caveat is that the existing Java renderer ignores the boolean returned by engineInitialize and unconditionally marks its initialized field true. Any callback integration must add its own success/failure gate rather than copying the existing flag behavior.

## Pinned input

- XAPK: 3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b
- Base split APK: com.shinybox.smash.apk, SHA-256 c7bd6ab38ed2827a3aadd4f415ffc994eb366fc1ce9d66742077d6ef5e954abc
- classes.dex SHA-256: bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b
- Package/version: com.shinybox.smash / 3.3.2.0

## Exact renderer initialization sequence

The DEX CodeItem for S3DRenderer.onDrawFrame(GL10) begins at decimal 4,487,320 (0x447898) and contains 157 code units. Static disassembly gives this path:

| Code unit | Instruction / call | Meaning |
|---:|---|---|
| 0 | read bAllowInit | Initialization gate |
| 3 | if bAllowInit is false, branch to 17 | Skip initialization |
| 5 | read bInitialized | Existing engine-initialized flag |
| 7 | if bInitialized is true, branch to 17 | Skip initialization |
| 9 | engineShutdown() | Reset/stop existing engine state |
| 12 | engineInitialize() | Native initialization call returns boolean |
| 15 | set bInitialized = true | Existing code unconditionally sets the flag |
| 17 | read bInitialized | Decide whether to continue frame path |
| 25 | engineRunOneFrame() | Native frame loop |

There is no move-result instruction after engineInitialize. The return value is therefore not tested by the Java method, and the following bInitialized flag is not reliable evidence that the native kernel is ready. A new registration hook cannot safely be inserted at this seam without first preserving and checking the native initialization result, defining failure behavior, and handling retry/context recreation.

## Shutdown sequence

- S3DRenderer.onShutdown() consists of a call to engineShutdown().
- S3DSurfaceView.onTerminate() sends a Runnable through GLSurfaceView.queueEvent().
- S3DSurfaceView$4.run() calls S3DRenderer.onShutdown().
- Smash.onDestroy() calls S3DSurfaceView.onTerminate().

This provides a likely renderer-thread location for paired callback unregistration, but the no-op probe has not been wired into this path and the thread/lifecycle behavior is not runtime-tested.

## Safe candidate sequence for a future authorized development build

1. Patch the renderer initialization path to preserve engineInitialize's boolean result and branch explicitly on failure.
2. Only after a successful native initialization, register the side-effect-free probe; if registration fails, keep it disabled and retry only through a bounded lifecycle transition.
3. On the renderer thread, unregister before every engineShutdown path and make repeated unregister calls idempotent.
4. Verify first startup, engine restart, surface recreation, pause/resume, activity destroy, and registration failure on an isolated build before considering any game-state handler.
5. Treat the Java source prototype and native probe as source only until a separately authorized package contains the class/library and a real runtime test records the typed 21 → 42 result.

No DEX patch was applied. No APK/XAPK was built. Catalog routing remains 0/222; Gold +100K candidate runtime verification remains 0/1; v50 runtime gate remains blocked at 0/9.

Machine-readable findings: DEX_ENGINE_LIFECYCLE_HOOK_AUDIT_V65.json.
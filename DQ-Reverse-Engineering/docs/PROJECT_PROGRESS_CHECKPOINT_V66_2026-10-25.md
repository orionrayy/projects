# Dungeon Quest ModKit checkpoint — v66

Date: 25 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
Base: v65 commit 13b2f848ca257cb101f8aaf4e51da3f67448b150

## Completed in this increment
- Added a pinned Android NDK workflow to compile the v64 side-effect-free callback probe as an arm64-v8a shared library.
- Added a reusable build script that checks the compiler output is ELF64/AArch64 and exports the three expected JNI symbols.
- The build workflow also executes host mock tests and validates the v64 source-only manifest.
- The only uploaded build artifact is the native probe library plus a small build manifest; no game package is created or changed.

## Status until CI confirms
- ARM64 native library result: pending this workflow run.
- Real Dungeon Quest invocation: not tested.
- No DEX patch or game APK/XAPK built.
- Catalog native routes 0/222; runtime effects 0/222; v50 runtime checks 0/9.

## Next gate
Only after a successful NDK build can the shared-library ABI build be considered validated. A separate, reviewed DEX callsite patch and device test are still required to load the library after a successful engineInitialize and to unregister on the engine thread before shutdown.

# Native probe ARM64 build gate — v66

This workflow extends the v64 source-only prototype with a reproducible Android NDK build. It produces only libdqbridge.so plus a build manifest as a GitHub Actions artifact. It does not modify the base APK, patch DEX, edit HUD/AIM assets, construct an XAPK, or invoke the callback inside Dungeon Quest.

## Build contract

- NDK directory: 27.2.12479018
- CMake: 3.22.1
- ABI: arm64-v8a
- Minimum Android platform: 23
- C++ runtime: c++_static
- Checks: ELF64, AArch64 machine, and all three JNI entrypoints are present in the dynamic symbol table.
- Additional checks: synthetic host registration/dispatch/unregister tests and the v64 source-only manifest validator.

## Artifact scope

The Actions artifact is named dq-native-client-probe-v64-arm64-source-only. It is intended to prove that the source can produce an ARM64 Android native shared library, not that the target app loads or calls it. No actual engine callback is registered or invoked by CI.

Before this library is added to any authorized development package, the app needs a Java/DEX loader call after successful engine initialization, the native export resolution must be tested on device, and register/invoke/unregister must run on the engine-owning thread. The existing DEX method ignores the result of engineInitialize, so that lifecycle gate must be repaired in a separately reviewed patch before this library is integrated.

No APK/XAPK is built in this workflow. The catalog remains 0/222 runtime-verified.

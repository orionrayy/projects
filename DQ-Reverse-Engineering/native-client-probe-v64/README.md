# Dungeon Quest native-client ABI probe v64 (source-only)

Purpose: test the ShiVa client-function callback contract with a deterministic zero-game-state probe. This is not a cheat and does not change Gold, player stats, saves, progression, IAP, network state, or game files.

## Probe behavior

- Registers the stable name dq_native_probe_roundtrip_v64 with S3DClient_RegisterFunction.
- The callback accepts exactly one numeric AIVariable with value 21 and returns one numeric AIVariable with value 42.
- Invocation uses the exported S3DX script dispatcher observed in the pinned ARM64 binary. It validates registry and callback marshalling in a mock test; it does not prove that a serialized HUD/AIM action can invoke the same function.
- Unregisters the probe by name through S3DClient_UnregisterFunction.
- The JNI shim resolves symbols from an already-loaded libS3DClient.so and fails closed if a required symbol is missing.

## ABI assumptions and guards

Compile-time checks require a 16-byte AIVariable layout view with a type byte at offset 0 and payload at offset +8, and a 48-byte legacy ARM64 AIFunction view with callback at offset +8. Number storage is float32, matching the legacy ShiVa header. The exact target SDK header, allocator/string ownership, and native callback lifecycle are still unverified.

## Strict runtime contract

This prototype is not wired into Dungeon Quest. A separate authorized development package must arrange a call sequence on the engine-owning thread:

1. Wait until the native engine and main pack are initialized.
2. Load libdqbridge.so from the same development app process.
3. Call nativeRegisterProbe(), then nativeInvokeProbe(); both must return true.
4. Call nativeUnregisterProbe() on the same engine-owning thread before engine shutdown.

The dlsym exports and callback ABI are supported by static evidence, but their visibility, thread affinity, and lifetime behavior are not verified by running this code in the actual game. Do not call from an arbitrary UI thread, do not add gameplay handlers, and do not bypass licensing or integrity checks. A missing symbol is a stop condition.

## Build and synthetic tests

The host test mocks function registration, name lookup, callback dispatch, typed input/output, and unregister. It verifies the prototype's code only; it does not emulate the real engine. CI syntax-checks the JNI source against installed JDK headers. It does not package or install an Android APK.

For an authorized Android NDK source build:

    cmake -S . -B build-arm64 -DCMAKE_TOOLCHAIN_FILE="$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake" -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-23
    cmake --build build-arm64 --config Release

Status: source prototype only; no APK/XAPK built; no real-device invocation; no game state changed.

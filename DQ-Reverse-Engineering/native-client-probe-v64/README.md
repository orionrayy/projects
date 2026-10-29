# Dungeon Quest native-client ABI probe v64 (source-only)

Purpose: test the ShiVa client-function callback contract with a deterministic zero-game-state probe. This is not a cheat and does not change Gold, player stats, saves, progression, IAP, network state, or game files.

## Probe and v84 route-gate behavior

- Registers the stable name \`dq_native_probe_roundtrip_v64\` with \`S3DClient_RegisterFunction\`.
- Also registers \`dq_cheat_route_gate_v84\`, a typed validation gate containing the 50 canonical stable IDs.
- The baseline callback accepts exactly one numeric AIVariable with value 21 and returns one numeric AIVariable with value 42.
- The v84 self-test sends a harmless \`player.god_mode=false\` request through the named script dispatcher. It succeeds only when the callback returns \`HandlerUnavailable\`, demonstrating that the gate was reached without applying a game effect.
- Unregisters both names by calling \`S3DClient_UnregisterFunction\`.
- The JNI shim resolves symbols from an already-loaded \`libS3DClient.so\` and fails closed if a required symbol is missing.

## v84 safety contract

All 50 IDs are present in the source route table, with type/range/step/select validation checked against \`first50_flexible_cheats_v81.json\`. All entries remain \`runtime_enabled=false\`. The 11 known static route candidates are evidence labels only. A validated request returns \`HandlerUnavailable\`, not success. No native game-state backend is connected.

This is still not a HUD/AIM integration. No serialized menu action calling \`system.callClientFunction("dq_cheat_route_gate_v84", ...)\` has been proven or added, and no live target runtime has exercised the callback in this increment.

## ABI assumptions and guards

Compile-time checks require a 16-byte AIVariable layout view with a type byte at offset 0 and payload at offset +8, and a 48-byte legacy ARM64 AIFunction view with callback at offset +8. The numeric payload is modeled as IEEE-754 binary64 because the exact-build ARM64 `uai_gp_hud::onDebug` entry at VA `0x6d5048` loads the payload at offset `+8` into a D-register (`ldr d8, [x2, #0x8]`). This is stronger static evidence than the earlier float32 assumption, but the proprietary SDK header and real callback invocation are still unavailable; runtime ABI compatibility remains unverified. The exact target SDK header, allocator/string ownership, and native callback lifecycle remain unverified.

## Strict runtime contract

This prototype is not wired into Dungeon Quest. A separately authorized development build must call registration only after successful engine initialization, run the no-op and route-gate self-tests on the engine-owning thread, and unregister both callbacks before engine shutdown. Do not call from an arbitrary UI thread or bypass licensing or integrity checks. A missing symbol or unexpected status is a stop condition.

## Build and synthetic tests

The host tests mock registration, name lookup, callback dispatch, typed input/output and unregister. They validate source behavior only, not the real engine.

For an authorized Android NDK source build:

\`\`\`sh
cmake -S . -B build-arm64 \\
  -DCMAKE_TOOLCHAIN_FILE="$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake" \\
  -DANDROID_ABI=arm64-v8a -DANDROID_PLATFORM=android-23
cmake --build build-arm64 --config Release
\`\`\`

Status: source prototype only; no APK/XAPK built; no real-device invocation; no gameplay state changed.

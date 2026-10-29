# DEX lifecycle integration for the native route-gate diagnostic — v85

Date: 2026-10-29  
Branch: \`feat/dq-iap-debug-cheats-modkit-v7\`  
Status: source overlay and contract tests added; **package/device runtime remains unverified**.

## Increment over v84

The v84 native library registers two callbacks inside the same engine lifecycle:

1. \`dq_native_probe_roundtrip_v64\`: accepts numeric 21 and returns 42 without side effects.
2. \`dq_cheat_route_gate_v84\`: validates a harmless, typed \`player.god_mode=false\` request and returns \`HandlerUnavailable\` because gameplay handlers remain disabled.

The JNI \`nativeInvokeProbe()\` requires both checks to pass. The v85 source-only DEX overlay calls this method only after \`engineInitialize()\` returns true, and inserts paired unregister calls immediately before the two identified \`engineShutdown()\` sites. The diagnostic log now reports \`abi_and_route_gate=PASS\` only if both the 21 → 42 ABI probe and route-gate dispatch pass.

## Verification in CI

The v85 workflow tests:
- Patch placement and fail-closed behavior against synthetic renderer smali fixtures.
- Native route-gate validation, duplicate-ID protection, bounds/step/select checks, integer precision handling, typed request dispatch and unregister.
- Baseline ABI-probe regression.
- JNI syntax.
- Exact parity of 50 native IDs against the canonical JSON registry.

## Important distinction

This advances the planned *runtime diagnostic integration path*, not the gameplay cheats themselves. The overlay uses the pinned stock DEX and source renderer hashes as preconditions and refuses to overwrite input/output paths. CI tests use synthetic smali; they do not contain the pinned APK/XAPK or compile an app package.

No serialized HUD/AIM control has yet been proven to call the route gate. No gameplay state is mutated. All 50 registry rows remain runtime-disabled, the official app and save data remain untouched, and the project must not be labeled as an install-ready 50-cheat package.

## Next gate

A separate authorized, test-signed diagnostic package can be assembled only when the exact pinned input APK, patched DEX overlay, and matching ARM64 library are present together. Runtime evidence then needs to show:
- successful library loading after engine initialization;
- ABI probe returning 21 → 42;
- route gate returning the expected blocked status for a valid request;
- paired unregister during shutdown/restart;
- no splash crash, hang, or native tombstone.

After the diagnostic callback path is verified, the next phase is to establish an actual AIM/HUD route and then add one effect handler at a time. The route gate is not itself a substitute for gameplay adapter semantics.

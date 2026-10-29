# Native Cheat Route Gate v84

Date: 2026-10-29  
Branch: \`feat/dq-iap-debug-cheats-modkit-v7\`  
Status: source integration milestone; **not a gameplay cheat implementation or installable package**.

## What changed

- Added a native, typed route table for all 50 stable IDs from \`first50_flexible_cheats_v81.json\`.
- Added input validation for control kind, booleans, finite values, bounds, numeric step size, select indices, integer constraints and float32 precision loss.
- Added the named ShiVa client function \`dq_cheat_route_gate_v84\`, registered alongside the existing no-side-effect \`dq_native_probe_roundtrip_v64\` probe.
- Extended the native probe call to invoke that named route through the script dispatcher and require \`HandlerUnavailable\` as the expected result. This proves only that a request reached the *validation gate* when the callback path is available; it does not apply a cheat or prove a HUD/AIM control can call it.
- Added C++ contract tests and a fail-closed source validator that compares all IDs, types, ranges, steps and option counts against the canonical JSON.

## Fail-closed semantics

All 50 rows have \`runtime_enabled=false\`. Valid requests return \`HandlerUnavailable\`, because no per-effect native gameplay handler has passed the required target, argument, read-back, persistence and rollback tests. If a route is accidentally marked enabled before a backend exists, it returns \`BackendUnavailable\`; neither status is success.

The legacy AIVariable path stores numbers as float32. The validator refuses integer inputs above \(2^{24}\) rather than silently rounding values that cannot be represented exactly. This is particularly important for large Gold balance targets.

The 11 route candidates recorded in the prior audit are marked as *static candidates*, not enabled gameplay adapters. Candidate metadata is not permission to execute a guessed handler.

## Automated checks

Workflow: [DQ native cheat route gate v84](../../.github/workflows/dq-native-cheat-router-v84.yml).

It compiles with \`-Wall -Wextra -Werror\`, runs native route-gate tests and the existing no-op ABI regression tests, syntax-checks the JNI source, and compares all 50 entries to the canonical registry. The existing ARM64 source-only build workflow also compiles the newly included C++ source via CMake.

## Explicitly not verified

- No HUD/AIM serialized call site to \`system.callClientFunction("dq_cheat_route_gate_v84", ...)\` has been proven or inserted.
- No actual game process has registered or invoked this new gate in this increment.
- No gameplay state was mutated or read back.
- No APK/XAPK was rebuilt, installed or tested on-device.
- No one of the 50 gameplay effects is runtime-verified.

## Next integration gate

1. Prove a valid serialized AIM/HUD caller for the named client-function dispatcher in the actual matching game runtime, or obtain the version-matched authorized client source/SDK needed to add the call safely.
2. Implement one effect adapter at a time with explicit player/enemy/global targeting, typed arguments, read-back, disable/reset behavior, save/reload and rollback; keep all other IDs disabled.
3. Add runtime evidence against a disposable offline profile. Only then promote the exact effect's metadata from blocked to enabled and consider packaging.

The official installation and saves remain untouched.

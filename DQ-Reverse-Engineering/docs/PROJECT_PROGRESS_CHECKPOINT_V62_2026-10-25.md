# Dungeon Quest ModKit checkpoint — v62

Date: 25 October 2026 (WIB)
Repository: \`orionrayy/projects\`
Branch: \`feat/dq-iap-debug-cheats-modkit-v7\`
Base: v61 commit \`035622346ae2d5f9cd7ee19a8a3d310cc3ce124f\`

## Completed
- Disassembled \`S3DX_AIScriptAPI_system_callClientFunction\` at VA \`0x892bd8\` (1,556 bytes) and correlated its call to \`Kernel::GetClientFunction\` at \`0x8285dc\`.
- Confirmed static call flow: the first \`AIVariable\` supplies the registered function-name string; the engine retrieves an \`S3DX::AIFunction\`, reads its callback pointer at offset +8, marshals typed \`AIVariable\` arguments, invokes the callback with input/output arrays, then copies back the returned output count.
- The path caps its total inputs at 33 including the function name, leaving at most 32 callback inputs. This is a limit of the inspected compiled path, not a recommended cheat payload size.
- Cross-checked the apparent callback shape against a public historical ShiVa example, while explicitly not treating that example as the exact target SDK header.
- Added report, fail-closed validator, seven tests, dedicated workflow and this checkpoint.

## What this improves
v61 found registration APIs; v62 confirms the kernel's script API can resolve a registered name and invoke the callback pointer. This gives a real engine mechanism to investigate for a client extension.

## Still blocked
No exact-build authorized SDK/header or source tree was found to establish all \`S3DX::AIFunction\` fields, allocator/lifetime rules or callback thread affinity. No valid registration hook in the shipped Dungeon Quest app and no new HUD/AIM serialized callsite to \`system.callClientFunction\` are proven. The standalone harness remains disconnected.

## Status unchanged
- 222 catalog entries / 14 categories.
- Assigned native routes 0/222; runtime-verified effects 0/222.
- Gold +100K candidate runtime verification 0/1.
- v50 candidate runtime gate blocked at 0/9.
- No game asset, native library, APK or XAPK changed or built.

## Next gate
Obtain the matching authorized SDK/client source. Implement only a no-op callback in a separate development target; validate register → \`system.callClientFunction\` → typed inputs/outputs → unregister, including engine lifecycle and threading. Only then consider one allow-listed gameplay adapter and prove state read-back, save/reload, rollback and regression.

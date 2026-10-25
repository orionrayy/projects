# Native client-function call dispatch — v62

**This is a stronger static finding than v61:** the engine has both a named client-function registration registry and a script API that resolves that name and invokes the registered callback with typed \`AIVariable\` input/output arrays. The app bootstrap hook, exact matching SDK ABI, and new HUD call site remain unproven.

## Fixed build identity

- Stock XAPK: \`3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b\`
- Stock STK: \`340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3\`
- ARM64 \`libS3DClient.so\`: \`0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083\`
- Target: Dungeon Quest 3.3.2.0, \`com.shinybox.smash\`

## End-to-end static call sequence

1. \`S3DClient_RegisterFunction\` at \`0x7aec14\` calls \`Kernel::RegisterClientFunction\` at \`0x82cccc\`, storing a name and \`S3DX::AIFunction const*\` in the kernel registry.
2. \`Kernel::GetClientFunction\` at \`0x8285dc\` resolves a registered function by name.
3. \`S3DX_AIScriptAPI_system_callClientFunction(int, AIVariable const*, AIVariable*)\` at \`0x892bd8\` reads its first input as the function-name string, calls \`GetClientFunction\`, and loads the callback field from offset \`+8\` of the registered \`S3DX::AIFunction\` pointer.
4. The script API marshals subsequent typed \`AIVariable\` parameters into a local array and invokes that callback indirectly with \`(input_count, input_array, output_array)\`. Its return integer is used as the number of output values to copy back. In the inspected path, the total input array is capped at 33 entries including the function-name argument, giving a maximum of 32 callback inputs.

The above behavior is grounded in the disassembly of the pinned ARM64 binary; it was not inferred solely from symbol names.

## ABI corroboration, not final header recovery

A public legacy ShiVa SDK example shows callbacks shaped as \`int callback(int input_count, const S3DX::AIVariable* inputs, S3DX::AIVariable* outputs)\` and an \`S3DX::AIFunction\` table with the callback as its second field. citeturn180211view0 The target binary independently reads the callback at byte offset \`+8\`, which is consistent with a 64-bit pointer in the second field. This does **not** recover every field offset, structure size, string lifetime/allocator rules, or thread/lifecycle requirements for the exact packaged build. The old SDK example is corroboration only; the matching authorized headers/source are still missing.

## Why this is not yet a usable game bridge

The registration and call APIs establish that ShiVa can support registered client callbacks. They do not establish that the shipped Dungeon Quest app has a safe Java/native initialization hook for registering an additional callback, that the right callback lifetime can be maintained, or that editing its compiled HUD/AIM resources can create a new \`system.callClientFunction\` call at a valid model execution point.

The \`S3DClient_CallHUDAction\` / \`GameManager::CallHUDAction\` pathway is separate: the inspected implementation queues a named HUD action and string-like arguments. It does not itself invoke a newly registered function directly. The missing proof is a complete serialized model/HUD route from a control into \`system.callClientFunction("probe_name", ...)\`.

## Engineering gate

The next experiment must be **no-op only**, on an isolated development package built through an authorized matching SDK/source workflow:

- Register a named no-side-effect callback after the engine kernel is initialized.
- Call it from an AIM/script execution point through \`system.callClientFunction\`, verify typed input and output marshalling, and unregister it safely before unload.
- Demonstrate lifecycle, threading, error/unknown-name handling and re-open behavior.
- Only after the bridge test is repeatable should one bounded allow-listed game-state adapter be designed with read-back, save/reload, backup/restore and regression evidence.

No callback was injected or called during this audit. No game asset, native library, APK or XAPK was changed or built.

## Status remains blocked

- Cheat catalog: 222 IDs across 14 categories.
- Exact native routes assigned: **0/222**.
- Runtime-verified catalog effects: **0/222**.
- Gold +100K candidate: **0/1 runtime-verified**.
- v50 runtime gate: **0/9 checks**.
- Standalone harness remains disconnected from Dungeon Quest.

Machine-readable findings: \`NATIVE_CLIENT_FUNCTION_CALL_DISPATCH_V62.json\`.
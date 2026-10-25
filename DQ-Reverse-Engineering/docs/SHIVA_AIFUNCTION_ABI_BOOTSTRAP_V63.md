# ShiVa AIFunction ABI and registration-lifecycle cross-check — v63

**Finding:** an older public ShiVa Android client source contains the exact legacy \`S3DX::AIFunction\` declaration and demonstrates the expected registration point after \`S3DClient_LoadPack\`. The target Dungeon Quest binary matches the callback-field offset and exposes the expected entrypoints. The exact target source hook is still missing, so this is ABI/lifecycle corroboration, not a deployable bridge.

## Reference source

Repository: [error454/ShiVa-Android-All-In-One](https://github.com/error454/ShiVa-Android-All-In-One/tree/1664c1206cba319480cf180e6e135352aefb9b5c), commit \`1664c1206cba319480cf180e6e135352aefb9b5c\` (2019-05-16).

- [S3DXAIFunction.h](https://github.com/error454/ShiVa-Android-All-In-One/blob/1664c1206cba319480cf180e6e135352aefb9b5c/android/jni/S3DX/S3DXAIFunction.h) declares \`AICallback\` as an integer-returning function accepting input count, a const \`AIVariable\` array and an output \`AIVariable\` array.
- The same header defines \`AIFunction\` as six fields: name, callback, return-description string, argument-description string, description string and a reserved \`uint32\`. On 64-bit ARM this legacy layout implies the callback is at offset +8 and the structure size is 48 bytes with normal 8-byte pointer alignment.
- [S3DClient_Wrapper.h](https://github.com/error454/ShiVa-Android-All-In-One/blob/1664c1206cba319480cf180e6e135352aefb9b5c/android/jni/S3DClient_Wrapper.h) declares \`S3DClient_RegisterFunction(const char*, S3DX::AIFunction*)\` and \`S3DClient_UnregisterFunction(const char*)\`.
- [S3DClient.cpp](https://github.com/error454/ShiVa-Android-All-In-One/blob/1664c1206cba319480cf180e6e135352aefb9b5c/android/jni/S3DClient.cpp) maintains a static AIFunction table and loops over it to call \`S3DClient_RegisterFunction\` after loading the main pack.

The target library independently reads its registered callback at offset +8 and calls it with the same input-count / \`AIVariable\` input / \`AIVariable\` output shape, so the old header is consistent with the native evidence. The public source is historical and not version-matched; it does not prove all structure details, allocator rules or lifecycle semantics for the packaged Dungeon Quest build.

## Registration timing in the reference project

The sample client source shows this order:

1. \`S3DClient_Init(...)\`.
2. Set input/render containers and other client callbacks.
3. \`S3DClient_LoadPack(...)\`.
4. Iterate the client-owned static \`AIFunction\` table and call \`S3DClient_RegisterFunction(name, &function)\`.

That reveals the missing kind of hook: a native client initialization path which owns the callback objects for their full registered lifetime. Merely editing a HUD or AIM resource does not create that client-side registration table or call the export. The old sample also does not establish a safe new registration hook inside Dungeon Quest's packaged binary, nor did this audit prove its unregister/teardown policy for a new function.

## Cross-check against Dungeon Quest 3.3.2.0

| Evidence | Result |
|---|---|
| \`S3DClient_RegisterFunction\` | \`0x7aec14\`, 188 bytes |
| \`S3DClient_UnregisterFunction\` | \`0x7aecd0\`, 132 bytes |
| \`system.callClientFunction\` script API | \`0x892bd8\`, 1,556 bytes |
| \`Kernel::GetClientFunction\` | \`0x8285dc\`, 76 bytes |
| Target reads registered callback at +8 | Confirmed in static disassembly |
| Exact target \`S3DXAIFunction.h\` / source project | Not available |
| App-owned registration table/call in recovered Dungeon Quest source | Not proven |
| New HUD/AIM path invoking the custom callback | Not proven |

The public sample removes one unknown—the historical structure/callback declaration—and makes the expected registration order concrete. It does not remove the key integration blocker: Dungeon Quest is supplied as compiled DEX/STK/native binaries, not the matching authorized native client project. A hook must not be fabricated by guessing function timing or callback lifetime.

## Go/no-go

**No-go for a game-state bridge or new feature APK at this checkpoint.** First recover the exact matching SDK/client source or otherwise obtain an authorized, version-correct declaration and extension hook. Then test a no-side-effect callback in an isolated development build: registration → \`system.callClientFunction\` lookup → typed input/output → unregister at a safe lifecycle point. Only after that passes should one allow-listed gameplay handler be designed and subjected to state-readback, save/reload, recovery and regression tests.

The catalog remains **0/222 runtime-verified** and the separate Gold +100K candidate **0/1 runtime-verified**. The v50 game-runtime gate remains blocked at 0/9. No APK/XAPK was built in this increment.

Machine-readable result: \`SHIVA_AIFUNCTION_ABI_BOOTSTRAP_V63.json\`.
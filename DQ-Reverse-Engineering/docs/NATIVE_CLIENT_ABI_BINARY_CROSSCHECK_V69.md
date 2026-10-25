# Native client ABI binary cross-check — v69

**Verdict: static symbol/layout corroboration passed; runtime integration is still blocked.**

This checkpoint independently inspected two binary artifacts instead of relying only on the earlier source mocks:

- Stock game library extracted from the pinned Dungeon Quest 3.3.2.0 XAPK: \`libS3DClient.so\`, SHA-256 \`0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083\`, 17,029,072 bytes.
- Native probe produced by ARM64 CI run [40205015193](https://github.com/orionrayy/projects/actions/runs/40205015193), artifact [12603596515](https://github.com/orionrayy/projects/actions/runs/40205015193): \`libdqbridge.so\`, SHA-256 \`82f19bbe8aec8ac95030a5e0f773168f0b3a5bfde76e1fe334f103415f8e0fd5\`, 601,112 bytes.

## Target-library symbol results

\`readelf --dyn-syms --wide\` on the stock library found all three dynamic symbols with \`GLOBAL DEFAULT FUNC\` visibility:

| Symbol | Address | Size | Static result |
|---|---:|---:|---|
| \`S3DClient_RegisterFunction\` | \`0x7aec14\` | 188 bytes | Present in the dynamic symbol table |
| \`S3DClient_UnregisterFunction\` | \`0x7aecd0\` | 132 bytes | Present in the dynamic symbol table |
| \`_Z42S3DX_AIScriptAPI_system_callClientFunctioniPKN4S3DX10AIVariableEPS0_\` | \`0x892bd8\` | 1,556 bytes | Present in the dynamic symbol table |

The \`RegisterFunction\` disassembly returns a boolean-like value from its internal registration call and returns zero on null/not-ready paths. The \`UnregisterFunction\` wrapper calls the kernel unregister method and does not consume a return value. The script dispatcher loads the registered callback at \`AIFunction\` offset \`+8\`, uses a 16-byte stride for typed variable records, bounds the total input records to 33 including the function-name record, and dispatches through the callback pointer.

The built probe is ELF64/AArch64 and exports all three JNI functions used by the source-only Java helper. Its native dependencies are \`libdl.so\`, \`libm.so\`, and \`libc.so\`.

## What is not proven

The exact target-build \`S3DX::AIFunction\` and \`S3DX::AIVariable\` headers are still unavailable. The callback offset and record-stride assumptions are cross-checked against target disassembly; the 48-byte \`AIFunction\` size and numeric representation are supported by a historical public ShiVa header, not an exact matched SDK. Symbol presence does not prove thread ownership, registration lifetime, allocator contract, or successful invocation.

The bridge has **not** been loaded inside Dungeon Quest. This audit did not patch a DEX, change an APK/XAPK, or call the registered function inside the running game.

## Promotion gates

| Gate | Current result |
|---|---|
| Target dynamic symbols | 3/3 present |
| Probe JNI exports | 3/3 present |
| ARM64 bridge build | PASS — source-only artifact |
| Exact matched target headers | Missing |
| Registration and 21 → 42 round-trip inside game | Not tested |
| Unregister on engine shutdown/restart | Not tested |
| Gold +100K runtime evidence | 0/9 |
| Catalogue routes and runtime-verified effects | 0/222 |

The v69 validator only protects the evidence claims from drifting; it does not authenticate the binary files or replace a runtime test. Keep the PR in draft. Do not ship the probe APK, and do not call the ModKit stable, until the missing engine ABI/lifecycle gate is closed on an isolated ARM64 installation with a disposable save and verified recovery path.

Machine-readable report: [NATIVE_CLIENT_ABI_BINARY_CROSSCHECK_V69.json](NATIVE_CLIENT_ABI_BINARY_CROSSCHECK_V69.json).

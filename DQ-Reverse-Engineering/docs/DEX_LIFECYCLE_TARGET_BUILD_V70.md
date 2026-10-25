# Exact-target DEX lifecycle assembly and round-trip — v70

**Static build gate: PASS. Dungeon Quest runtime gate: NOT VERIFIED.**

This checkpoint moves beyond the synthetic v67 fixture: the v67 patcher was executed against the exact pinned Dungeon Quest 3.3.2.0 classes.dex and full smali disassembly. The source DEX was not overwritten; all output was created in a separate local directory.

## Pinned inputs and tools

| Item | Value |
|---|---|
| Original DEX SHA-256 | bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b |
| Original DEX size | 6,996,484 bytes |
| Renderer source disassembly SHA-256 | 6509e64a2f3836bbe59a4ab56fde889192dfff80793ff86ead7699561ea01642 |
| Toolchain | smali/baksmali 2.5.2 |
| API target | 28 |
| Source class definitions | 10,768 |

The patcher checked both the DEX digest and the renderer disassembly digest before it changed anything.

## Assemble and re-disassemble findings

| Gate | Finding |
|---|---|
| Reassembled baseline from untouched smali | PASS; no method-body differences against the original disassembly |
| Baseline assembler normalization | 17 smali files differ only in explicit static field defaults (false/null) omitted in the baseline smali text |
| Patched DEX SHA-256 | 2c05a2fb599024659b4784086d295fe0b3090dad073c847bbdec3b0964d1ea90 |
| Patched DEX size | 7,006,620 bytes |
| Re-disassembled class definitions | 10,769 |
| Added class | com/shinybox/smash/DqNativeProbe |
| Changed classes vs reassembled baseline | Exactly S3DRenderer and DqNativeProbe |
| Missing source classes | 0 |

The round-trip retained all source classes, added the intended probe helper, and changed exactly two class files relative to the comparable reassembled baseline. The added callsite consumes the boolean from engineInitialize(), invokes only the no-side-effect probe when the result is true, then restores the existing bInitialized=true write. The two located shutdown sites each have one unregister call before engine shutdown.

## What this does not establish

No APK or XAPK was built from this DEX. The DEX was not installed or run inside Dungeon Quest, and the native callback was not invoked in a live game process. The matching target headers and engine-thread/lifetime contract remain unavailable. Therefore this is a reproducible static transformation, not an installable or stable mod release.

| Runtime gate | Current state |
|---|---|
| Gold +100K: install, UI visibility, tap, exact delta, save/reload, no crash and regression checks | 0/9 |
| Native routes in the 222-entry catalogue | 0/222 |
| Runtime-verified catalogue effects | 0/222 |
| Promotion to stable release | Blocked |

## Next hard gate

First pass the report validator and synthetic tests in CI. Any future package needs a separate review of binary/signing/split integrity and an isolated ARM64 runtime proof of init success/failure, 21 → 42 callback response, unregister during shutdown/restart, and zero regressions. Gold functionality must then be measured as exactly +100,000 and persisted after save/reload with verified backup/restore. Do not remove the official app or bypass licensing, integrity, IAP or cloud/account checks.

Machine-readable report: DEX_LIFECYCLE_TARGET_BUILD_V70.json.

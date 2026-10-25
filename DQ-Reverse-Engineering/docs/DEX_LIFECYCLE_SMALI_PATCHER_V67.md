# DEX lifecycle smali overlay — v67

**Status: source-only transformation; assembler and runtime gates remain open.** No game DEX, APK, or XAPK is modified by this tool.

## Purpose

The pinned Dungeon Quest 3.3.2.0 DEX audit found that S3DRenderer.onDrawFrame calls engineInitialize()Z but does not consume its boolean result before setting bInitialized=true. The overlay inserts move-result and branches around a side-effect-free native callback probe; it then restores the original initialized-flag assignment.

## Exact-input and output safeguards

The tool requires the source classes.dex SHA-256:

bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b

It requires a fresh, separate output directory and refuses changed callsite shapes, duplicate hooks, missing shutdown sites or any different DEX hash. It inserts the harmless 21 → 42 callback only when engineInitialize returns true, and inserts unregister immediately before engineShutdown in both located lifecycle methods.

## Validation

Nine regression tests cover init-success gating, preserving the original flag assignment, unregister ordering, wrong source identity, changed/duplicate callsites, output overwrite prevention, and input immutability. CI then assembles and re-disassembles only a synthetic fixture with smali/baksmali 2.5.2. GitHub Actions run [40206173884](https://github.com/orionrayy/projects/actions/runs/40206173884) passed the 9-test suite and synthetic smali assemble/re-disassemble gate. This proves syntax/transform consistency, not that the actual game's DEX or native ABI works.

## Hard limits

- Output is a smali source overlay only; there is no modified DEX/APK/XAPK or game-process invocation in this checkpoint.
- The target app's exact native callback header/lifecycle is not recovered from matching source.
- The v50 Gold +100K test remains blocked at 0/9 runtime checks.
- Native catalogue integration remains 0/222 routes and 0/222 runtime-verified effects.
- Do not bypass purchase, licensing, integrity, online/account, cloud, or anti-tamper behavior.

Do not promote this overlay into a game package until synthetic assembly round-trip passes, the output from the exact pinned DEX is reviewed, the ARM64 bridge is packaged through a reviewed development build, and an isolated ARM64 runtime proves init success, callback registration, the exact harmless 21 → 42 response, unregistration at shutdown/restart, and zero regressions.

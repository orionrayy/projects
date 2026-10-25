# DR2C VORENYX — Reproducible source patch packaging v2.55

**Scope: build packaging only. This is not a game version, not v2.51, and not an APK.**

## Output

- ZIP: `DR2C_VORENYX_REPRODUCIBLE_SOURCE_PATCH_v2.55.zip`
- Size: 7,515,735 bytes
- SHA-256: `95bfb426c802c0dacebb9d44586cf6deeef1aab5557e2c63ca5dff6f05edf64d`
- ZIP: CRC PASS; 274 entries; zero duplicate paths.
- Overlay: 272 paths, including 269 `.df` payloads; 18 later-layer overrides.

## Exact inputs and order

1. `DR2C-RAYY(2).zip` — SHA-256 `14f44400c3314a6d9b7e5428077c199c846367235e379199618f7b11288f4eb1`
2. `DR2C_VORENYX_ID_v2.43_localization_patch.zip` — SHA-256 `00ff7866242e8b3aca4fc749e93455ba1c795c4eec99fd15baa07ab483aca024`
3. `DR2C_VORENYX_v2.45_CORRECTIVE_SOURCE_PATCH.zip` — SHA-256 `b2cc843325ede21d00cb91dad4a4ff68fa8c3c0e629d6910860727a4db4cf88d`
4. `DR2C_VORENYX_v2.45_STARTFIX_SOURCE_PATCH.zip` — SHA-256 `36f423d620ec852a82d74d34fab02b83f350c8cd5a1cd304d6e247d494495267`

## Reproducibility repair

The previous v2.53 build and a fresh build contained exactly the same 274 archive member payloads, but their whole-ZIP hashes differed because ZIP metadata inherited creation timestamps/default file attributes. The source reconciler now normalizes entry timestamps and Unix file modes when writing each member. Three independent builds yielded the same SHA-256 above. A dedicated unit test enforces identical bytes across repeated builds.

## Verification

- Source reconciler unit tests: 7/7 pass.
- Provenance unit tests: 6/6 pass.
- Combined: 13/13 pass.
- Static source contracts: canonical boot marker, quote closure, no escaped backslash-quotes, ordered Forth code-symbol stream, canonical perk key, and critical Start/tutorial dispatch tokens all pass.

## Remaining release blockers

This build still contains only the four source layers listed above. The actual v2.47–v2.51 ZIP bytes and exact v2.46 baseline APK remain unavailable, so it must not be described as v2.51 integration. No full Deathforth parser, APK build/sign/install, Android runtime, UI-fit, Start-input, gameplay, or save/load test was performed.

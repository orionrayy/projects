# Dungeon Quest ModKit v83 — Full-50 Native Dispatch Build

Date: 2026-10-28

## Candidate artifact

- XAPK: `DQ_ModKit_v83_FULL50_NATIVE_DISPATCH_ARM64.xapk`
- Package ID: `com.shinybox.dqv83`
- Game version: `3.3.2.0`
- Split APKs: 20
- Size: 57,748,612 bytes
- SHA-256: `24aa51a8f48adf823a199ed43bcb168a708dba2c17e17f186801bef3c8df60f1`
- Local test-signer certificate SHA-256: `2f44aa207dc4e7542b25998ebee18c02690307bda2bfcbd3376b4bc957480b5a`

## Implementation delta

The debug Cheat Menu now contains 50 distinct controls, 50 unique callback identifiers, and command IDs 100–149. The controls are distributed over the existing Add, CS, MS, Floor, Feat, and Legends pages. Each callback invokes `uai_gp_hud.onDebug(command)`; an ARM64 native bridge intercepts IDs 100–149 and routes them to explicit handlers. Handlers use existing debug/reward/identify routes or the engine's AIVariable get/set API.

This is a one-tap preset UI. It is **not equivalent to a full implementation of the old roster's sliders, numeric inputs and select widgets**. Some effects are approximations and depend on model variables whose runtime semantics have not yet been confirmed.

## Static validation

- STK: all 5,630 entries decode and pass payload CRC/size checks.
- STK table key matches CRC32 of its metadata table.
- HUD round-trip: 50 unique buttons, 50 unique callbacks, IDs 100–149.
- Native library payload hash matches the patch report; hook branch resolves to payload entry at `0x1300000`.
- XAPK outer and all 20 inner APK ZIP CRCs pass.
- All 20 splits were checked for package identity, signer consistency, APK v1/v2/v3 signatures and 16-KiB alignment during build.
- Independent base/native split package, signature and alignment spot-check passed.

## Runtime/QA boundary

**0/50 effects have been runtime-verified.** Device install, launch, in-game effects, persistence, save/reload and rollback are not tested in the build environment. Native inline hooking can cause a force-close. Specific unverified bindings include the affix-limit variable, enemy-target mutations, some variable names/scales, and snapshot/undo coverage for newly spawned or untracked state.

The package is local test-signed and must not be treated as a publisher-signed release. Do not uninstall the official game or clear its data for this test. Use an offline/disposable profile where possible. Merge/release is not recommended before device QA.

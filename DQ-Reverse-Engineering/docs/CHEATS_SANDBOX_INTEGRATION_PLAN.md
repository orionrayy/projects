# Cheats Sandbox — Integration boundary and implementation plan

## User-facing target

Add a first-party Cheats (Sandbox) page inside the game's Pause → Options navigation, with:
- searchable categories and favorites;
- per-setting switches, numeric values, ranges, enums, and parameterized actions;
- presets, profiles, import/export, undo, reset by item/category/profile;
- clear risk badges and explanations, deterministic test seed, snapshots, event log and performance diagnostics;
- sandbox-only saves, offline-only mutable gameplay settings, and no cloud/leaderboard/achievement synchronization while cheats are active.

The standalone prototype and 222-entry draft catalog are design artifacts, not evidence that game effects are wired up.

## What is grounded in the repository

The reconstructed wrapper identifies com.shinybox.smash.Smash, S3DSurfaceView, S3DRenderer, and native S3DClient entry points. Smash delegates rendering and engine lifecycle through JNI. The asset pack contains readable Resources/XML tables, including Vanity and IAP, but the inner .gam, .scn, .mdo, .msh, .ske, and similar records are not native source code.

There are 44 JNI declarations, but the native implementation binaries have not been obtained. The manifest strongly indicates base/ABI/density split delivery. The repository is not currently a complete Android/Gradle project and has not been build-verified.

## Safe implementation order

1. Ship diagnostics-only functionality in a wrapper-level screen: current package/build identity, frame timing where observable, memory and input telemetry, UI layout, log export. Do not infer hidden game state.
2. Define a catalog schema and controller API. Keep all gameplay adapters absent by default and refuse to apply unknown IDs.
3. Add a sandbox state provider in the host; require offline mode and an isolated save before enabling mutation.
4. Add one reversible test adapter only after its actual state owner and rollback semantics are verified.
5. Integrate the Options route using an available original UI hook. Do not invent S3D scene APIs from JNI names alone.
6. Expand the catalog in small groups; every effect needs a precondition, bounds, conflict declaration, snapshot/restore behavior, unit test, and explicit unverified/verified status.

## Non-goals / hard constraints

- No claim that the HTML prototype is part of the APK.
- No native ABI/library substitution from another game.
- No false source reconstruction: generated declaration stubs are not original method bodies.
- No modification of IAP receipts or purchase-history records.
- No disabling of cloud/online integrity on a live service. Use a local sandbox/test build.
- No APK signature or runtime-test claim until an actual compatible Android build succeeds.

## IAP replacement work still outstanding

The first asset-level patch changes only 16 cash-only Vanity rows. It does not turn off billing or replace gold, pets, slots, stash, boosts, random packs, and bundle entitlements. Those need product-to-content mapping and balance testing before migration. Maintain a clear known/inferred/unresolved ledger for every SKU.

# Main HUD Debug Route Audit v20

**Evidence date:** 2026-10-24  
**Target build:** Dungeon Quest Android `com.shinybox.smash`, version `3.3.2.0`, version code `1423433200`  
**Classification:** static asset and native-binary evidence; no gameplay state was modified.

## Main HUD structural summary

The recovered `Resources/HUD/hud.hud` uses the same four-section, version-12 format as `pause.hud` and `debug.hud`.

| Field | Value |
|---|---:|
| File size | 127,302 bytes |
| SHA-256 | `5ead76f34a93be134761b11dda485221628f41c19b3ac99dd81fd1867edf0304` |
| Format marker/version | `NcP` / 12 |
| Element records | 637 |
| Action records | 219 |
| General attributes payload | 11 bytes |
| Element payload | 102,253 bytes |
| Action payload | 25,012 bytes |
| Timer payload | 2 bytes |

## Debug-relevant actions found in the main HUD

The existing action table includes these action → AI-model-call mappings:

| HUD action | Static call target | Meaning established by evidence |
|---|---|---|
| `onDebug` | `uai_gp_hud.onDebug(0)` | Enters the existing general debug dispatcher |
| `onDebugLevel` | `uai_gp_hud.onDebug(5)` | Calls the dispatcher with argument 5 |
| `onDebugGold` | `uai_gp_hud.onDebug(6)` | Calls the dispatcher with argument 6 |
| `onDebugGoldDown` | `uai_gp_hud.onDebug(7)` | Calls the dispatcher with argument 7 |
| `onDumpShaders` | `uai_gp_debug.onDumpShaderList()` | Delegates to a shader-dump action in the debug model |
| `onLevelUp` | `uai_gp_hud.onShortcut("levelup", 1)` | Uses the existing shortcut action path |

The first five calls are encoded as serialized AI action parameters in the original HUD. This establishes that debug-related callbacks are part of the existing content; it does **not** prove every control is visible, enabled, or reachable in a normal gameplay session.

Static HUD strings include names such as `keyDebug`, `levelSkip`, `levelUpCheat`, `shaderDump`, and a `debug` group. Without fully decoding all element records, these names cannot be mapped to verified coordinates, visibility rules, parent relationships, or activation conditions.

## Relationship to Pause → Options

The Pause HUD has 126 elements and 64 actions. Its `onShowOptions` action opens the existing `uai_gp_options` model and updates the pause/options state flags; no explicit call to `uai_gp_debug` or “debug” action appears in the Pause action table.

The Debug HUD has 71 elements and 13 actions. Its action records delegate to `uai_gp_hud.onDebug` using arguments such as 1–4 and 8–16. The main HUD contains the additional debug-related handlers listed above. These are distinct facts; together they suggest an existing debug control subsystem, but do not identify an already working Pause → Options → Cheats route.

## Native dispatcher investigation

A static ARM64 disassembly of `uai_gp_hud::onDebug(int, ...)` shows an argument-dispatch routine and references to engine/model state including `bActive`, `bGamePaused`, and the `debug` group. The native function performs typed variable and state checks. This is not enough to define a safe external Java call contract or to infer that invoking `onDebug(0)` from a new menu is side-effect-free.

No guessed JNI binding, native pointer, or direct call from Android UI code has been added. Before adding a call site, the argument semantics, engine lifecycle/thread requirements, and current state preconditions must be proven and exercised on a compatible ARM64 runtime.

## Engineering outcome

This audit narrows the next UI task from “create a new debug system” to “determine whether the existing main-HUD debug group can be exposed through a supported route.” The remaining prerequisites are:

1. Decode the specific element records associated with the debug group and key bindings, including parent/visibility/interaction properties.
2. Reconcile the serialized records against the version-12 `LoadElements` implementation and identify the exact version argument passed by the HUD loader.
3. Build a parser and serializer which preserves every unmodified record byte-for-byte, then pass round-trip tests on all three source HUDs.
4. Test the existing debug route and a one-entry UI change on a compatible ARM64 test build with an isolated/offline save.
5. Only after runtime read-back/reset tests succeed, consider adding catalog-backed sandbox actions.

**Status:** static route evidence improved; format-correct HUD edit and in-game route remain **BLOCKED / NOT RUNTIME-VERIFIED**. No modified original-game APK is claimed.

Purchase receipt/entitlement handling, cloud progression, achievements, and leaderboard submission are unchanged.

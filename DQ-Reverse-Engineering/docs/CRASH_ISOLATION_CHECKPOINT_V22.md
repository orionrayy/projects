# Dungeon Quest 3.3.2.0 — Crash isolation checkpoint v22

Date: 2026-10-24. User-reported symptom: the v2-signed v21 XAPK installs successfully but force-closes at the Shinybox logo, before the title screen. Exact runtime cause is unknown because Android logcat/device access was not available in the build environment.

## Findings

- The original and modded STK packs were decoded and compared entry-by-entry. Exactly one decoded entry differs in v21: `Resources/HUD/pause.hud`. All other 5,629 decoded entries are identical.
- The v21 patch changed the Pause menu label from `Social/IAP` (10 UTF-8 bytes) to `Cheats Sandbox` (14 UTF-8 bytes), and changed the callback route. The parser/packer round-trip is not equivalent to a real-engine runtime test.
- v22 preserves the label byte count using `Cheats/IAP` (10 UTF-8 bytes) and preserves the callback-name byte count. New patcher: `tools/patch_pause_cheats_sandbox_v22.py`; the local regression suite passed 3/3 tests, including fail-closed checks for unknown schema/version. The patcher does not establish that the native engine accepts the callback at runtime.
- Two v2-signature diagnostic packages were generated to isolate the package/repack path from the HUD change. Their APK split signatures were checked with a local verifier and archive CRC checks passed. They were not installed/launched on Android here.

## Diagnostic artifacts

| Variant | Package ID | SHA-256 | Intended test |
|---|---|---|---|
| Baseline, original game asset pack | `com.shinybox.dqfix` | `d2e4d17ae94169cf55810e1b9610d80885775c136f8ff338d7c38f548724d559` | Determines whether package-ID rewriting/repacking alone still crashes |
| v22 same-length HUD route candidate | `com.shinybox.dqalt` | `a72b9ca20127b023e04c0c6109fb787a3b705b56e06999fc18eaffd719f32b8f` | Tests whether the same-length label variant with the debug callback avoids the crash |

Artifacts are supplied separately as XAPK files; they are diagnostic, not declared stable. v2-only signatures are used in these two diagnostic variants because the target device is Android 11; this is distinct from the earlier v1+v2 candidate. Do not install the diagnostic variants online, sign in, or use a primary save.

## Required interpretation

1. Test the baseline variant first. If it also crashes at the Shinybox logo, the HUD callback is not sufficient to explain the symptom; capture a crash logcat and investigate repacking, package identity, manifest/resource-table changes, and native initialization.
2. If baseline reaches the title screen, test v22. If baseline runs but v22 crashes, revert the callback/action change and replace it only after the full HUD element/action serialization semantics are verified.
3. Neither candidate is labelled runtime-verified. A launch-only test is insufficient to claim the cheat works; the route must be tapped in the game, UI reachability and state effect observed, and regression checks run.

## Safety/behavior boundary

No receipts, purchase entitlements, cloud saves, achievements, or leaderboard logic were modified. All gameplay-effect claims remain NOT RUNTIME-VERIFIED.

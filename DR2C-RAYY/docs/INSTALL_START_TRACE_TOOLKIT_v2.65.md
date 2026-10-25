# DR2C VORENYX — v2.65 Install/Start Trace Checkpoint

Date: 26 October 2026  
Status: toolkit static verification PASS; Android runtime still pending user-device trace.

## Purpose

The prior v2.64 Start-only collector required the package to be installed, so it could not help diagnose the reported case where an APK failed to install. v2.65 provides two explicit modes:

1. INSTALL_ATTEMPT — does not require the package to be installed; captures package-manager/install errors while the user manually repeats the failed installation.
2. START_BUTTON — requires the package to be installed; captures app/native/Deathforth/integrity messages during one Start tap.

## Changes

- Removed destructive logcat buffer clearing.
- Starts capture near the live edge with -T 1.
- Enforces a 90-second limit.
- Captures package metadata before and after the attempt.
- Uses mode-specific filters for install failures versus Start/runtime failures.
- Deletes temporary raw log and stderr files before packaging.
- Does not install/uninstall, modify saves, or bypass signatures/licensing.

## Validation

- 17/17 static assertions PASS.
- ZIP CRC PASS; duplicate paths 0.
- ZIP SHA-256: b67f81776e96a2d96d1cfc04015247aaf85bb7477672a504a7e2698feb48da27.
- No Windows PowerShell runtime or Android/ADB device was available here; no actual install or Start tap was tested.

## Remaining blockers

The Start no-op and APK installation failure are not diagnosed until the relevant trace is captured. The latest candidate APK referenced by the v2.62 audit remains locally test-signed, not publisher-signed. No runtime stability, full localization, UI fit, gameplay, or save/load claim is made.

## Next gate

If the APK is absent after the failed installation, run mode 1 while manually repeating the install once. If the package is still installed and Start does not respond, run mode 2 and tap Start once. Inspect the output ZIP for private information before sharing it. Do not uninstall or replace the existing game solely for diagnosis.

## Supplemental static Start-route cross-check

A direct comparison of the actual base and candidate APKs found matching normalized code-token streams in events.df, game-select.df, game-info.df and boot-end.df after masking quoted strings/comments. boot.df adds the id-name-localize display-label helper; removing that helper restores the base token stream. events/tutorial.df remains the known code-token drift exception (chim → cname plus bHe/bhim/bhe expression-token removals). This drift is not proven to cause Start to fail. Both APK ZIPs pass CRC with zero duplicate paths. See [source diff audit](../audit/start_route_source_diff_v2.65.json).

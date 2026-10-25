# DR2C VORENYX — v2.64 Runtime Trace Toolkit Checkpoint

**Date:** 26 October 2026  
**Status:** diagnostic-tool hardening verified statically; game runtime blocked pending a real device trace.

## Changes in v2.64

- Removed the destructive adb logcat -c operation. Existing device-wide logs are no longer cleared.
- Starts logcat from the recent/live edge with -T 1.
- Caps the capture window at 90 seconds and terminates the collector automatically.
- Checks whether the logcat process exits immediately and surfaces stderr as a startup diagnostic.
- Removed the standalone crash-buffer dump, which could have mixed stale crashes into the current trace.
- The temporary raw log and stderr file are removed after processing; only selected matching lines and package/activity metadata are placed in the output ZIP.
- The BAT wrapper now reports and returns the collector's exit status.

## Static verification

- 11/11 structural/safety assertions passed.
- ZIP integrity: PASS.
- Duplicate ZIP paths: 0.
- Toolkit SHA-256: 50545f6e2cf61b48e067910781e2996ae822895fef073a61859d9b249020a.
- No PowerShell runtime or Android/ADB device was available for execution in this environment, so this is a source/package-level validation only.

## Blockers that remain

- Start-button no-op remains unresolved at runtime.
- Candidate APK recorded in the v2.62 audit is DR2C_VORENYX_v2.57_SIGNATURE_FIX_REDELIVERED_20261025.apk, SHA-256 a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7; the v2.58-named library artifact is byte-identical, not a separate tested build.
- The local signing certificate is not the original publisher's certificate. PairIP/Play integrity or licensing may still reject the repackaged package.
- 100% localization, gameplay, UI fit, save/load and device stability are not verified.

## Next acceptance gate

Run the toolkit on a Windows PC connected to the phone by authorized ADB, tap Start once while capture is active, then review the generated DR2C-StartTrace-<timestamp>.zip. Classify the trace before making another APK change. Do not uninstall or overwrite the existing installation before backing up saves and confirming signing/install compatibility.

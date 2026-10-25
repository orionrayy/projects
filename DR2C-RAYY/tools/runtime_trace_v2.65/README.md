# DR2C VORENYX — Install/Start Runtime Trace Toolkit v2.65

This read-only collector supports two diagnosis paths. Choose install-attempt mode when an APK fails to install or the app is absent; choose Start-button mode when the package is installed but Start does not respond.

## Requirements

- Windows PC with Android Platform Tools (adb.exe) on PATH.
- Phone connected by USB with Developer Options → USB debugging enabled and the PC authorized.
- Use mode 1 if package com.noodlecake.drtc may be missing. Use mode 2 only if the package is currently installed.

## Run

1. Extract the ZIP into a normal Windows folder and double-click RUN-TRACE.bat.
2. Choose mode 1 for a failed installation attempt, or mode 2 for the Start no-op.
3. When CAPTURE AKTIF appears, perform that single action on the phone. The capture ends automatically after 90 seconds.
4. A ZIP named DR2C-Trace-<timestamp>.zip appears on the Desktop. Inspect it before sharing.

## Safety and interpretation

- The collector does not run adb install or uninstall, does not clear existing Android log buffers, does not touch saves, and does not bypass signature or licensing checks.
- It captures from the recent/live edge of logcat, filters relevant messages, and deletes temporary raw logs before creating the output ZIP.
- Absence of a particular log line is not proof that no fault occurred. Android builds do not always expose touch dispatch messages.
- Install-mode output helps identify package-manager/signature/ABI/parse errors. Start-mode output helps identify app crashes, native-loader, Deathforth, and integrity/licensing errors.
- No device runtime result is implied by successfully running this tool. Build and gameplay stability remain unverified until the app is tested on the actual device.

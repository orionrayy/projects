# DR2C VORENYX — Start Runtime Trace Toolkit v2.64

This hardened toolkit collects a bounded Android log trace to investigate the still-unverified Start-button no-op. It does not install or uninstall APKs, edit saves, patch the binary, clear existing device log buffers, or bypass PairIP/licensing.

## Requirements

- Windows PC with adb.exe (Android Platform Tools) installed and discoverable on PATH.
- Phone connected by USB with Developer Options → USB debugging enabled.
- The phone must authorize that PC when Android shows the RSA debugging prompt.
- Package com.noodlecake.drtc must already be installed.

## Run

1. Extract the ZIP to a normal Windows folder.
2. Double-click RUN-TRACE.bat.
3. If asked to choose a device, select the phone serial shown by adb devices.
4. When the script says CAPTURE AKTIF, open DR2C VORENYX and tap Start once. Wait about 10 seconds.
5. Leave the capture window open. Capture ends automatically after 90 seconds; a ZIP named DR2C-StartTrace-<timestamp>.zip is written to the Desktop.
6. Review the ZIP before sharing it. The included log is filtered for app, crash, native-loader, integrity and licensing-related messages; the temporary raw log is deleted and is not included.

## Safety and interpretation

- The collector reads from the recent/live edge of logcat and does not clear Android log buffers. The capture is capped at 90 seconds.
- The collector is diagnostic only. It cannot prove the APK stable merely because there is no crash line.
- A missing app trace, a Deathforth parse error, a native crash, and a PairIP/licensing rejection indicate different failure classes; do not treat them as interchangeable. Default Android builds may not log every touchscreen event, so absence of a touch line alone is inconclusive.
- This does not attempt to bypass licensing, signature checks or anti-tamper controls.
- Do not uninstall the currently working game or replace its APK merely to run this collector. Back up saves before any future app replacement.
- The local test-signed candidate is not signed with the publisher's certificate. A log may help classify the failure but does not make that APK an official/release-ready build.

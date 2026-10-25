# DR2C VORENYX — Start Runtime Trace v2.63

**Status:** diagnostic workflow prepared; actual device trace not yet collected.

## Why this is the next gate

The v2.60–v2.62 static audits found the critical Deathforth route words and source synchronization, while package comparison found unchanged DEX payloads and native binary changes limited to thirteen UI-label string slots in each ABI copy of `libmain.so`. That is not proof of successful touch dispatch or successful runtime execution. The Start no-op therefore needs device-side evidence to distinguish:
- touch/input dispatch not reaching the app handler;
- Start route dispatch or Deathforth script loading/compilation failure;
- process/JNI/native crash;
- native integrity or licensing rejection after local re-signing.

## Collector

Run `tools/runtime_trace/RUN-TRACE.bat` on Windows with Android Platform Tools (`adb.exe`) installed and on PATH. Connect the phone with USB debugging enabled and authorize the PC.

When the collector says **CAPTURE AKTIF**, open DR2C VORENYX, tap Start once, wait roughly ten seconds, then press Enter in the PC window. The collector creates a timestamped ZIP on the Desktop with filtered relevant log lines, package metadata, crash-buffer lines and app-related activity lines. The raw all-buffer log is deleted and is not included in the ZIP.

## Safety / scope

- The collector is read-only with respect to the APK and game data. It does not install or uninstall apps, modify saves, change signatures, or bypass PairIP/licensing.
- Review the ZIP before sharing; logs can contain device or app activity.
- Absence of a crash line is not proof of stability.
- Do not uninstall a working copy or replace the APK without a save backup.
- The available candidate is locally test-signed, not publisher-signed. The missing v2.47–v2.51 source ZIPs and a distinct v2.58 localization artifact also remain lineage blockers.
- The collector is not yet tested on the user's Windows machine or Android device. The next engineering step depends on the captured trace; until then the runtime/release gate remains **BLOCKED**.

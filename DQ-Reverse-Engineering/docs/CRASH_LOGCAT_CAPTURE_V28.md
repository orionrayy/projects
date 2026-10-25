# Dungeon Quest crash evidence capture — v28

**Date:** 2026-10-25  
**Branch:** `feat/dq-iap-debug-cheats-modkit-v7`  
**Purpose:** collect native or Java crash logs instead of building more unverified XAPK variants.

## Current known behavior

- Original-content stock-pack diagnostic control under package ID `com.shinybox.dqv25`: user reports it reaches the game.
- v25 changes only the pause HUD label in the packed asset and crashes at splash.
- v26 keeps all decoded asset bytes identical but changes five raw bytes in the STK pack, including a zlib header hint and target-entry CRC; user reports the issue appeared again after testing v26 (treated as splash crash, exact symptom to confirm).
- Anti-tamper is **not confirmed**. Pack format, integrity checks, native parsing, and build/signing differences remain competing hypotheses.

## Capture on Windows 11 with ADB

Use the same phone on which the crash occurs. Enable Developer options → USB debugging and accept the PC authorization prompt. Install Android Platform Tools if `adb` is unavailable. Keep the problematic v26 installed for this capture.

Open PowerShell in a folder where you want the log saved, connect the phone, then run:

```powershell
adb devices
adb logcat -c
adb shell monkey -p com.shinybox.dqv25 1
Start-Sleep -Seconds 12
adb logcat -d -v threadtime > .\dq-v26-crash.txt
```

If the package will not launch from `monkey`, manually tap its icon right after `adb logcat -c`, wait for the force close, then run the final `adb logcat` line.

Create a compact high-signal excerpt too:

```powershell
Select-String -Path .\dq-v26-crash.txt -Pattern 'FATAL EXCEPTION|Fatal signal|SIGABRT|SIGSEGV|AndroidRuntime|libc|linker|S3DMain|integrity|CRC|signature|Shinybox' -CaseSensitive:$false |
  Set-Content .\dq-v26-crash-key-lines.txt
```

Upload **both** `dq-v26-crash.txt` and `dq-v26-crash-key-lines.txt`. The unfiltered log is important: a native signal or parser exception may not include the words above. Avoid signing into a primary account during these tests.

## What to inspect in the log

1. `FATAL EXCEPTION` or `AndroidRuntime`: Java/Kotlin exception and stack trace.
2. `Fatal signal 6/11`, `SIGABRT`, `SIGSEGV`, `DEBUG` or `tombstoned`: native crash and backtrace.
3. `dlopen`, `linker`, `UnsatisfiedLinkError`: native library or ABI/load failure.
4. Explicit `CRC`, `signature`, `integrity`, `S3DMain` references: useful evidence for pack validation, but their absence does not rule it out.

Do not make another pack mutation until this evidence is reviewed. Local structural checks and a locally implemented APK v2 verifier do not substitute for an actual device launch or logcat analysis.

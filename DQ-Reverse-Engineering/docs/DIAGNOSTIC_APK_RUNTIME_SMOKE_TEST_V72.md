# DQ v72 diagnostic device smoke test (ARM64)

This is a diagnostic test, not a stable release. Keep the official com.shinybox.smash app installed. v72 uses com.shinybox.dqv72 and a local diagnostic certificate; it is not an in-place update. Do not use production saves. Start offline with a disposable profile and a recovery path.

## Install and capture logs (ADB)

1. Enable USB debugging and connect the Android device to a computer with Android Debug Bridge (adb) installed.
2. Verify the APK SHA-256 before installation. Expected: 6261d077092098986094ebcf79522b767143467b7b3bc074341b2da6700098b6.
3. Install only the diagnostic package:

   ~~~powershell
   adb install .\DQ_ModKit_v72_ABI_Probe_LOGCAT_ARM64.apk
   ~~~

   If Package Manager rejects the install, capture the complete error and stop. Do not uninstall or replace the official app to work around it.
4. Clear the log buffer, then launch the diagnostic app by package ID:

   ~~~powershell
   adb logcat -c
   adb shell monkey -p com.shinybox.dqv72 1
   ~~~
5. Wait until the first stable game screen, then save the probe logs:

   ~~~powershell
   adb logcat -d -s DQv72Probe:V > dq-v72-logcat.txt
   ~~~
6. Exit through the app's own UI if possible, then capture the logs again so shutdown/unregister messages are included.

## Interpreting the result

- library_load=PASS means Android loaded libdqbridge.so; it does not prove callback ABI correctness.
- callback_register=PASS means the native registration call reported success.
- callback_roundtrip=PASS means the native dispatch returned one numeric value equal to 42 for input 21.
- callback_unregister=PASS means unregister reported success. An early SKIP before initialization can be normal; inspect the final shutdown path separately.
- Any FAIL, EXCEPTION, crash, force close, hang, or repeated relaunch is a failure. Stop further testing and preserve the log.

## Evidence needed to clear the runtime gate

Install succeeds; launch reaches the first stable screen without crashing; logs show library_load=PASS, callback_register=PASS, and callback_roundtrip=PASS; normal exit gives callback_unregister=PASS; no native tombstone or unexplained hang occurs. Preserve dq-v72-logcat.txt and record Android version/device ABI. Only then update the runtime report. Gold +100K remains a separate 9-check gate, while the 222-entry catalogue is still unimplemented. Do not infer runtime success from static validation or a visible launcher icon.

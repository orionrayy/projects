# DQ v73 install failure triage — 26 October 2026

## Situation

The user reports Android displays an install failure after attempting to install v73; this is distinct from “Problem parsing the package.” The exact Package Manager failure code and device log are not available yet.

The APK was statically checked in the build environment:
- SHA-256: 53799adf3e9d8b3efca062c9a8c97489a050196ad4f9aafcc84acf86d2ad0e49
- Package ID: com.shinybox.dqv73
- minSdk 21, targetSdk 34, versionName 3.3.2.0
- aapt reports the expected package ID and launcher activity.
- APK Signature V1/V2/V3 verify; ZIP CRC and 16 KiB native-library alignment checks pass.
- The APK uses a local diagnostic certificate and is not signed by the game's publisher.

These checks do not prove Android Package Manager will accept the APK on every device. The root cause is UNKNOWN pending the install result/logcat. Do not classify the issue as a native runtime crash: an install failure occurs before app runtime is reached.

## Capture the authoritative Package Manager code (Windows + USB debugging)

Keep the official application installed. Do not clear the game's data or uninstall any version just to make the diagnostic candidate install.

1. Enable Android Developer Options → USB debugging, connect the phone to a trusted PC, and approve the debugging prompt.
2. Open PowerShell in the folder containing the APK and a working Android SDK adb.exe (or add Android platform-tools to PATH).
3. Confirm the device is visible:

   ~~~powershell
   adb devices
   ~~~

4. Clear old log entries, run one installation attempt, and save the exact command output:

   ~~~powershell
   adb logcat -c
   adb install .\DQ_ModKit_v73_NO_NATIVE_PROBE_ARM64.apk 2>&1 | Tee-Object .\dq-v73-install-result.txt
   adb logcat -d -b all -v threadtime > .\dq-v73-install-logcat.txt
   ~~~

5. Extract likely install-related lines locally (this output can help avoid sharing unrelated personal/app logs):

   ~~~powershell
   Select-String -Path .\dq-v73-install-logcat.txt -Pattern 'INSTALL_FAILED|PackageManager|PackageInstaller|installd|signature|conflict|not enough|insufficient|parse|dex2oat|avc: denied' | Select-Object -Last 100
   ~~~

6. Share dq-v73-install-result.txt and only the filtered lines (or their screenshot). Do not post the complete unfiltered log if it contains account identifiers or unrelated app information.

## Interpreting failure codes

- INSTALL_FAILED_INSUFFICIENT_STORAGE: confirm free internal storage; do not remove game saves blindly.
- INSTALL_FAILED_UPDATE_INCOMPATIBLE / INSTALL_FAILED_SHARED_USER_INCOMPATIBLE: a package/signature identity conflict is indicated; report the exact package name. Do not remove the official application to work around it.
- INSTALL_FAILED_NO_MATCHING_ABIS: ABI compatibility issue; collect adb shell getprop ro.product.cpu.abilist.
- INSTALL_FAILED_OLDER_SDK: device API is below the package minimum.
- INSTALL_FAILED_INVALID_APK, INSTALL_PARSE_FAILED_*, or INSTALL_FAILED_BAD_SIGNATURE: preserve the exact code and inspect the package/signature/manifest path.
- Any other INSTALL_FAILED_*: use the exact code, not a generic guess.

A generic “App not installed” toast alone is insufficient to tell these apart. Do not keep retrying or install over the official app while the reason is unknown.

## Project status

No new build is being declared a fix. v73 remains a diagnostic comparator; the native-probe isolation hypothesis is not validated until installation succeeds and a clean startup comparison is completed. Gold +100K remains 0/9 runtime checks, catalogue integration remains 0/222, and stable promotion remains blocked.

# DQ v77 — phone-only startup test

v76 still force-closed. Static DEX analysis found that the Android package ID had been changed to `com.shinybox.dqv76`, while the shared literal used by `BuildConfig.APPLICATION_ID` and `Globals.sPackageName` remained `com.shinybox.smash`. The recorded loading path uses `Globals.sPackageName` when creating the app data/cache path and calling `PackageManager.getApplicationInfo`.

v77 changes that shared DEX literal to `com.shinybox.dqv77`, recalculates the DEX SHA-1 signature and Adler-32 checksum, and leaves the native library bytes, Java class descriptors and official stock STK unchanged.

1. Keep the official Dungeon Quest app and its save data installed and untouched.
2. Install **DQ v77 Tester** (`com.shinybox.dqv77`) as a separate diagnostic app.
3. Launch once, preferably offline. Do not tap any Gold/cheat controls.
4. Report one outcome: **A)** reaches title/menu; **B)** force-closes immediately; **C)** shows logo/loading then force-closes; **D)** fails to install.

APK SHA-256: `77dac9fe85f1e9519424b78690261074be2fafd26afac521fdab50fdd9198cb9`.
This build has passed static checks but has not been installed or launched by the build environment. A runtime fix is not claimed until phone testing passes. It uses a local test certificate and cannot update the publisher-signed app. Do not clear official app data or uninstall the official app.

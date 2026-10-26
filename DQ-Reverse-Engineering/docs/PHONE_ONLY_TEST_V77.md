# DQ v77 — phone-only startup test

v76 still force-closed. A static DEX audit found `BuildConfig.APPLICATION_ID` and `Globals.sPackageName` were both hard-coded to `com.shinybox.smash` while the manifest package had been renamed to `com.shinybox.dqv76`. `Globals.sPackageName` is used for cache/pack paths and as the argument to `PackageManager.getApplicationInfo`.

v77 changes the shared dotted app-ID literal to `com.shinybox.dqv77`, recalculates DEX SHA-1/Adler32, and keeps the stock STK, Java class descriptors, and native library bytes unchanged. This is a high-confidence static inconsistency; the actual crash cause remains unconfirmed until phone testing.

1. Keep the official Dungeon Quest app and save data installed and untouched.
2. Install **DQ v77 Tester** as a separate app.
3. Launch once, preferably offline. Do not tap any cheat/Gold controls.
4. Report whether it opens to the title/menu or force-closes, and whether the failure is immediate or after a logo/loading screen.

v77 uses a local diagnostic signing certificate and cannot update the official signed application. Device install/launch remains unverified; do not clear official app data or uninstall it.

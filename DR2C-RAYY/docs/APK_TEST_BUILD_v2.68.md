# DR2C VORENYX v2.68 — APK Test Build Report

**Status: APK uji berhasil dibuat; belum diuji pada perangkat Android.**

## Artifact

- APK: `DR2C_VORENYX_v2.68_TEST_CANDIDATE.apk`
- Size: **115,639,063 bytes**
- SHA-256: `4028b0ada13ab650ba3625bfe7bf495455bb5816040847f0999ac591f1ecd384`
- Package: `com.noodlecake.drtc`
- Android versionCode / versionName: `57` / `1.8.2` (the v2.68 label is the project checkpoint, not an Android versionCode bump)
- Input candidate SHA-256: `a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7`
- Repair ZIP SHA-256: `e6bf40a2ca8f69b4c55f7b50592b1cb201b8660ff285f6862a1c96e8b645690d`
- Local test certificate SHA-256: `c46d4af342ad0ecb63a771613e245ab4088597520a27aaf2719c8ea03d6dd15c` (not the publisher's certificate)

## Passed checks

- JAR/v1 verification: **PASS** (`jarsigner -verify`). The self-signed-certificate warning is expected for a local test key.
- APK Signature Scheme v2: **PASS with the included local verifier**. Google's official `apksigner` was not available, so this is not official SDK signature validation.
- ZIP CRC: **PASS**; duplicate entry paths: **0**.
- Stored-entry alignment: **264 checked**, **14 native .so libraries aligned to 4096 bytes**, and **250 other stored entries aligned to 4 bytes**.
- Four intended payloads match the source overlay byte-for-byte: `assets/deathforth/boot.df`, `assets/deathforth/paul/camping-region.df`, `assets/gfx/ui/vorenyx_title_screen.png`, and `res/drawable-xxhdpi-v4/splash.png`.
- All other non-signature payloads are unchanged from the input candidate, including `AndroidManifest.xml`, all three DEX files, both `libmain.so` variants and both `libpairipcore.so` variants.
- Independent final ZIP test: **PASS**.

## Not tested

- Android PackageManager installation: **NOT TESTED**.
- Start tap and Logcat: **NOT TESTED**.
- Gameplay, tutorial, save/load and runtime stability: **NOT TESTED**.
- Release readiness: **NOT READY**.

## Installation caveats

This test APK is signed by a new local test certificate, not the original publisher key. Android can reject it as an update over an app signed with a different certificate. Back up local saves before uninstalling any existing copy. PairIP/licensing/native components are untouched, so they may still refuse startup. Passing static checks is not evidence that install or gameplay works on the target device.

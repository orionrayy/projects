# DR2C VORENYX v2.68 — APK Test Build Report

- Candidate input SHA-256: `a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7`
- Source patch ZIP SHA-256: `e6bf40a2ca8f69b4c55f7b50592b1cb201b8660ff285f6862a1c96e8b645690d`
- Output APK: `DR2C_VORENYX_v2.68_TEST_CANDIDATE.apk`
- Output size: 115,639,068 bytes
- Output SHA-256: `9ad55289ff5189727cdd43ca39105db49f38c5aa8b6186d6794b19a45aa38cff`
- Package: `com.noodlecake.drtc`; versionCode 57; versionName `1.8.2`. The v2.68 number is the project patch checkpoint, not an Android versionCode change.
- New local test certificate SHA-256: `a37f318594c7d7afacfa1fb1ed2909603014d9a4439fb98ec2355519774642d4` (not the publisher certificate).

## Validation results

- JAR/v1 signature verification: **PASS** (`jarsigner`).
- APK Signature Scheme v2: **PASS** with the included local verifier; official Google `apksigner` was not available.
- ZIP CRC: **PASS**; duplicate entry paths: **0**.
- Stored entries checked: 264; native `.so` libraries aligned to 4096 bytes: 14; other stored entries aligned to 4 bytes: 250.
- The four intended payloads match the v2.68 source overlay byte-for-byte: `assets/deathforth/boot.df`, `assets/deathforth/paul/camping-region.df`, `assets/gfx/ui/vorenyx_title_screen.png`, and `res/drawable-xxhdpi-v4/splash.png`.
- All other non-signature payloads are unchanged from the input APK. `AndroidManifest.xml`, all three DEX files, both `libmain.so` variants, and both `libpairipcore.so` variants are byte-identical to the candidate input.
- Device PackageManager installation, Start-tap Logcat, gameplay/tutorial, save/load and stability: **NOT TESTED**.

## Important limitations

This is a **locally re-signed test candidate**, not a stable release. The certificate is new and not the publisher key. It may not install as an update over a copy signed with a different certificate; uninstalling an existing app can erase local saves, so preserve data before making that decision. PairIP/licensing/native components were not bypassed or modified and may still reject startup. Do not claim the install or Start issues are fixed until the APK is tested on the target Android device.

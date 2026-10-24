# DR2C VORENYX v2.43 — APK Build Candidate

**Status: assembled and JAR/v1-signed; Android runtime stability NOT VERIFIED.**

## Artifact (local only)
- File: `DR2C_VORENYX_v2.43.apk`
- Size: **39,610,091 bytes**
- SHA-256: `cefe665d0164495248f0d2cc960f54478d60b980ec137c3878181732d0885a90`
- App package: `com.noodlecake.drtc`
- Base game's manifest version: `1.8.2` / version code `57`
- Min/target SDK: `23` / `35`
- Signature: local JAR/v1 signature using SHA-256 with RSA. It is not signed by the original publisher.
- Native libraries: `arm64-v8a` and `armeabi-v7a`; 3 DEX files preserved.
- The package is rebuilt from the locally available extracted APK contents plus the v2.43 patch overlay. It is not a Gradle source build.

## Independent static checks
- APK ZIP CRC: PASS.
- JAR/v1 signature verification: PASS.
- All 272 v2.43 overlay file payloads matched their archived hashes after packaging.
- 1,015 ZIP entries; no unintended outer project-directory prefix.
- Native library local data offsets: 4-byte aligned.
- Required manifest, DEX, libraries and title/splash assets: present.
- Build SHA-256 sidecar matches the APK.

## Patch metadata note
The v2.43 patch's `README.txt` says 309 changed occurrences across 16 files, while its checkpoint and translation ledger report 159 occurrences across 58 files, with 9 new overlay modules. This build records the discrepancy instead of silently conflating the counts. The packaged overlay itself contains 272 file payloads, 271 replacing existing APK files and one new title-screen image; that payload count is not a translation count.

## Critical runtime limitation
The original private signing key is not included in the supplied archive. The package also contains `com.pairip.application.Application` and PairIP/Play license-check components. Re-signing may cause the game to reject the package or fail at launch. No attempt was made to bypass licensing or anti-tamper checks.

No Android device/emulator/ADB was available for an install, launch, gameplay, UI-fit, save/load, or stability test. Therefore the artifact is a **statically validated APK candidate**, not a claim that the game is confirmed stable. Do not uninstall the official game or risk existing saves solely on the basis of these static checks.

The APK, full extracted game content, and overlay remain local-only; GitHub stores this sanitized build report and summary only.

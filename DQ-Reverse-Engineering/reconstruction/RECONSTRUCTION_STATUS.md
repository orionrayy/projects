# Source Reconstruction Status — Iteration 4

## Higher-confidence Java

- `verified/java/com/shinybox/smash/BuildConfig.java`: static values from DEX metadata and a trivial constructor.
- `verified/java/com/shinybox/smash/Globals.java`: field declarations and constructor.
- `verified/java/com/shinybox/smash/S3DEngine.java`: constructor and three lifecycle bodies. These files compile against temporary minimal stubs, not a full Android SDK/dependency graph.

## Method-level reconstruction excerpts

- `fragments/ShinyActivity-selected-methods.java.txt`: selected lifecycle, device-name, immersive-mode, input and wrapper-registration methods.
- `fragments/Smash-pack-io.java.txt`: directory creation, APK asset-copying method and control-flow reconstruction of `extractMainPack`.
- `fragments/Smash-static-initializer.java.txt`: observed native library load order.
- `fragments/S3DRenderer-native-boundary.java.txt`: JNI method declaration excerpt; native bodies are absent.

These are source-style excerpts, not complete original source files. The 68 files in `reconstruction/java/` are declaration scaffolds with placeholder method bodies, not a working game.

## New asset result

The outer `S3DMain.smf` format is now identified and decoded. The parser verifies all 5,630 entries against CRC-32 and uncompressed sizes, yielding 94,513,994 bytes. The decoded set contains 17 XML gameplay-data tables and thousands of binary assets. See `docs/STK_FORMAT_FINDINGS.md` and `docs/ASSET_CATALOG.md`.

Readable XML data includes skills, items, affixes, legends, talents, stats, shop/IAP names and dictionary/localization keys. Inner `.gam`, `.mdo`, `.msh`, `.ske`, `.scn` and related file internals remain to be reverse engineered; they are not source code merely because they are extracted.

## JNI and split-APK blocker

The wrapper declares 44 native methods and requests `crypto`, `ssl`, `openal`, and `S3DClient` in that order. The manifest's required ABI/density split metadata suggests the supplied archive may be a base APK; the matching companion splits have not been provided or verified. Native implementations remain missing.

## Validation boundary

The local static validator reports zero structural errors across the 68-class Dalvik snapshot. The full and excerpt manifests parse, the entire STK pack verifies, helper scripts pass `py_compile`, and the three high-confidence Java files compile against minimal temporary stubs.

JADX, Apktool and a Smali assembler have not run. No full Android Studio/Gradle build, signing, emulator launch or runtime-equivalence test is claimed. Two suspicious/reserved opcode positions in `CameraPreview.surfaceChanged` remain flagged rather than guessed into Java.

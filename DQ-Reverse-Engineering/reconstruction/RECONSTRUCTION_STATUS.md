# Source Reconstruction Status — Iteration 3

## Confidence tiers

### Direct / high-confidence source recovered from short DEX bodies

- verified/java/com/shinybox/smash/BuildConfig.java: six values decoded from DEX static encoded values and a trivial constructor.
- verified/java/com/shinybox/smash/Globals.java: four field declarations and trivial constructor.
- verified/java/com/shinybox/smash/S3DEngine.java: constructor and three lifecycle bodies. onConfigurationChanged returns without a super call; onCreate and onTerminate delegate to the superclass.

### Method-level semantic reconstruction

- fragments/ShinyActivity-selected-methods.java.txt: selected methods for device name, system UI flags, TV/touchscreen identification, lifecycle wrapper registration, and input routing. Obfuscated types/method names remain as seen in DEX.
- fragments/Smash-pack-io.java.txt: directory creation, asset-copying method, and documented control-flow reconstruction of extractMainPack.
- fragments/Smash-static-initializer.java.txt: native-library load names and sequence.

These excerpts are not complete original source files. They contain reconstruction choices and/or deliberately omit obfuscation artefacts; compare them against the associated disassembly before using them as executable source.

## Declaration scaffolds only

reconstruction/java/ contains 68 generated Java declaration stubs. These preserve types, signatures, inheritance/interfaces, field declarations, and safe constants from the DEX. Nontrivial method bodies throw UnsupportedOperationException or contain explanatory comments. They are not a working game and must not be shipped as such.

## Static behavior recovered

- Smash loads crypto, ssl, openal, S3DClient in that order.
- It uses S3DMain.smf as primary pack, tries an asset-copy fallback output name S3DMain.stk, and stores descriptor, start offset and length for the engine surface bridge.
- extractAssetFromAPK allocates a 512 KiB buffer and loops on InputStream.available(). The observed bytecode writes the requested chunk length rather than the read() return value; the illustrative excerpt preserves this potentially unsafe behavior.
- IAP wrapper static constants contain 104 distinct SKU identifiers, listed in docs/IAP_PRODUCT_CATALOG.md. This catalog identifies strings, not current prices/storefront state or entitlement validation.

## Remaining blockers

- The proprietary 33,978,539-byte S3DMain.smf format remains unresolved. No extraction, decryption, or decoding is claimed.
- classes.dex contains 10,768 class definitions, including large dependency/platform sets. Only 68 classes under com.shinybox.* were emitted to the current class-specific disassembly.
- The custom disassembler still reports reserved/unknown opcode positions; CFG-based inspection flagged two in CameraPreview.surfaceChanged. These are reported rather than guessed into Java.
- The three verified Java files were compiled with javac against minimal temporary Android/dependency stubs. This proves Java syntax for those files only; it is not an Android Gradle build or runtime test.
- No complete Android Studio build or runtime launch has been produced. The required Android SDK, proprietary engine assets/implementation, and native engine libraries/dependencies are not established by this input.

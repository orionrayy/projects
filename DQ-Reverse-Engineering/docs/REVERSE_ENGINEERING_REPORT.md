# Reverse-Engineering Report — Dungeon Quest APK

## Artifact identity

- Input: uploaded DQ.zip, an Android APK container.
- Size: 37,200,621 bytes; SHA-256: 1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9.
- Package: com.shinybox.smash; version 3.3.2.0; version code 1423433200.
- Min SDK 21; target SDK 34; compile SDK 34.
- Main Activity: com.shinybox.smash.Smash; Application class: com.shinybox.smash.S3DEngine.
- Main game pack: assets/S3DMain.smf; no lib/<abi>/*.so files were found in the inspected APK archive.

## Recorded hashes

| Entry | Size (bytes) | SHA-256 |
|---|---:|---|
| Uploaded APK | 37,200,621 | 1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9 |
| classes.dex | 6,996,484 | bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b |
| assets/S3DMain.smf | 33,978,539 | 340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3 |

## DEX reconstruction

- 37,620 strings; 12,348 type IDs; 14,055 prototypes; 30,461 field IDs; 59,460 method IDs; 10,768 total class definitions.
- 68 app-specific com.shinybox.* classes emitted as Smali-like source.
- Corrected output: 405 methods, 5,187 decoded instructions, 50 payload directives, 44 native method declarations.
- Static validation reports zero structural errors.

The full DEX also includes platform and third-party dependencies; the 10,768-class count is the DEX class table, not a count of game-authored classes.

## Architecture and asset flow

- Smash is the main Activity wrapper, with lifecycle, asset/file handling, audio, camera, sensors, input and purchase integration.
- S3DSurfaceView derives from GLSurfaceView.
- S3DRenderer declares native engine entry points for initialization/shutdown, frame updates, surface callbacks, pack descriptor handoff and input forwarding.
- Smash.extractMainPack() opens S3DMain.smf via AssetManager.openFd(), obtains the file descriptor/start offset/length and passes these to the native renderer boundary. The APK ZIP entry is stored without ZIP compression.
- extractAdditionalFiles() appears to extract other root assets besides the main pack; the security implications for api_key.txt are documented separately.

See NATIVE_ENGINE_BOUNDARY.md and ASSET_LOAD_TRACE.md.

## Native boundary

Java code requests libraries named crypto, ssl, openal, and S3DClient, yet no native lib/<abi>/*.so entries were present in this APK. This may be an incomplete base/split or another distribution variant. No native implementation can be recovered from absent binaries.

## Correction and validation

The first disassembly pass had opcode-width errors that caused instruction boundaries to drift. Opcode widths and operands were corrected and all 68 outputs regenerated. The validator checks method boundaries, instruction/payload code-unit coverage, labels, register bounds and unresolved placeholders.

This remains a Smali-like reconstruction, not original Java source and not proof of assembler acceptance. JADX, Apktool and a Smali assembler could not run in the current offline runtime. No Gradle build, signing, emulator launch, or runtime-equivalence test has been performed.

## SMF status

The SMF remains unresolved. A gzip candidate header scan found zero plausible candidates; 3,952 zlib-looking candidate positions failed stream validation. High entropy alone does not prove encryption. See SMF_FORMAT_STATUS.md.

## Sensitive data

The APK contains assets/api_key.txt with a credential-shaped Amazon token. The file and value are excluded. The asset-extraction path may copy root assets other than the main pack to the app's writable pack directory; this is a static-flow finding, not runtime observation. Rotate/revoke the token if active.

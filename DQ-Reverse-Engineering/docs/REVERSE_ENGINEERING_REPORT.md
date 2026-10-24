# Reverse-Engineering Report — Dungeon Quest APK

## Artifact identity

- Input: uploaded DQ.zip, an Android APK container.
- Size: 37,200,621 bytes; SHA-256: 1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9.
- Package: com.shinybox.smash; version 3.3.2.0; version code 1423433200.
- Min SDK 21; target SDK 34; compile SDK 34.
- Main Activity: com.shinybox.smash.Smash; Application class: com.shinybox.smash.S3DEngine.
- Main game pack: assets/S3DMain.smf; no lib/<abi>/*.so files appear in the uploaded APK archive.

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

The full DEX also includes platform and third-party dependencies; 10,768 is the DEX class table count, not the number of game-authored classes.

## Manifest and split status

The decoded manifest declares requiredSplitTypes="base__abi,base__density", android:isSplitRequired="true", com.android.vending.splits.required=true, and android:extractNativeLibs=false. Therefore, this uploaded APK is consistent with a base APK expecting ABI and density split APKs. The absence of native libraries inside this individual archive does not prove they were never distributed. The matching splits have not yet been found or validated. See NATIVE_ENGINE_BOUNDARY.md.

## Architecture and asset flow

- Smash is the main Activity wrapper, with lifecycle, asset/file handling, audio, camera, sensors, input, and purchase integration.
- S3DSurfaceView derives from GLSurfaceView.
- S3DRenderer declares native entry points for initialize/shutdown, frame updates, surface callbacks, pack descriptor handoff, and input forwarding.
- Smash.extractMainPack() opens S3DMain.smf using AssetManager.openFd(), gets file descriptor/start offset/length, and passes them to the native renderer. The ZIP entry is STORED (not compressed by the APK container).
- extractAdditionalFiles() appears to extract other root assets; see ASSET_LOAD_TRACE.md and SECRETS_REDACTED.md.

## Correction and validation

The first disassembly pass had incorrect opcode widths causing subsequent instructions to drift. Opcode widths and operands were corrected and all 68 output files regenerated. The validator checks method boundaries, instruction/payload code-unit coverage, labels, register bounds, and unresolved placeholders. All 68 files pass the current structural validator.

This remains a Smali-like reconstruction, not original Java source and not proof of assembler acceptance. JADX, Apktool, and a Smali assembler could not run in the offline runtime. No Gradle build, APK signing, emulator launch, or runtime-equivalence test has been performed.

## SMF status

The SMF remains unresolved. It is stored uncompressed in the APK ZIP container; GZIP candidates: zero valid streams; zlib-like candidates: 3,952, zero validated streams. High entropy alone does not prove encryption. See SMF_FORMAT_STATUS.md.

## Sensitive data

The APK contains assets/api_key.txt with a credential-shaped Amazon token. The file and value are excluded. A static code path may extract non-main-pack root assets into a writable application directory. Rotate/revoke the credential if active.

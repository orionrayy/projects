# Reverse-Engineering Report — Dungeon Quest APK

## Artifact identity

- Input: uploaded `DQ.zip`, an Android APK container.
- Size: 37,200,621 bytes; SHA-256: `1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9`.
- Package: `com.shinybox.smash`; version `3.3.2.0`; version code `1423433200`.
- Min SDK 21; target SDK 34; compile SDK 34.
- Main Activity: `com.shinybox.smash.Smash`; Application class: `com.shinybox.smash.S3DEngine`.
- Main game pack: `assets/S3DMain.smf`; no `lib/<abi>/*.so` files were found inside the supplied APK archive.

## Recorded hashes

| Entry | Size (bytes) | SHA-256 |
|---|---:|---|
| Uploaded APK | 37,200,621 | `1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9` |
| `classes.dex` | 6,996,484 | `bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b` |
| `assets/S3DMain.smf` | 33,978,539 | `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3` |

## DEX and source reconstruction

- 37,620 strings; 12,348 type IDs; 14,055 prototypes; 30,461 field IDs; 59,460 method IDs; 10,768 total class definitions.
- 68 app-specific `com.shinybox.*` classes were emitted as Smali-like source.
- Corrected output totals: 405 methods, 5,187 decoded instructions, 50 payload directives, 44 native method declarations.
- Static validation reports zero structural errors across those 68 files.

The full DEX also contains Android/third-party dependencies; 10,768 is the DEX class table count, not a count of game-authored classes.

## Architecture

- `Smash` is the main Activity wrapper; inspected method names/instructions cover lifecycle, asset/file handling, audio, camera, sensors, input and purchase integration.
- `S3DSurfaceView` derives from Android `GLSurfaceView` and handles the rendering surface and input boundary.
- `S3DRenderer` declares native engine entry points for initialization/shutdown, frame updates, surface callbacks, pack-file descriptor handoff and input forwarding.
- `ShinyActivity`, `IAPWrapper` and `GooglePlayServicesWrapper` declare further native callbacks.
- `IAPWrapper` contains product ID strings such as `com.shinybox.dq.gold1`–`gold5`, `hires`, `slot`, `hunter`, `multi`, `pickup`, `crystal`, `exp`, `gold`, and `luck`. These strings alone do not prove which products are active at runtime.

See `NATIVE_ENGINE_BOUNDARY.md` for why the DEX is not the complete engine.

## Correction and validation

The first disassembly pass had opcode-width errors that caused subsequent instruction boundaries to drift. Opcode widths and operand decoding were corrected, then all 68 class outputs were regenerated. The validator checks method boundaries, instruction/payload code-unit coverage, branch label references, register bounds and unresolved placeholders. The decoded XML manifest is well formed and helper Python files pass syntax compilation.

This is a **Smali-like reconstruction**, not original Java source and not proof that all output can be assembled. JADX, Apktool and a Smali assembler could not be run in the current offline runtime. No Gradle build, signing, emulator launch, or runtime-equivalence test has been performed.

## SMF status

`S3DMain.smf` remains unresolved. GZIP candidate header scan produced zero plausible candidates; 3,952 zlib-looking candidate positions all failed stream validation in a bounded probe. High entropy alone does not prove encryption. See `SMF_FORMAT_STATUS.md`.

## Credential handling

The APK contains `assets/api_key.txt` with a credential-shaped Amazon token. Its contents and the file are excluded. Rotate/revoke the token through the owning service if active.

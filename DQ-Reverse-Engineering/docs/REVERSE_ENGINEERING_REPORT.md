# Reverse-Engineering Report — Dungeon Quest APK

## Artifact identity

- Input: uploaded `DQ.zip` (Android APK; the .zip extension is misleading).
- File size: 37,200,621 bytes.
- SHA-256: `1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9`.
- Package: `com.shinybox.smash`.
- Version: `3.3.2.0`; version code `1423433200`.
- Min SDK 21, target SDK 34, compile SDK 34.
- Main activity: `com.shinybox.smash.Smash`.
- Application class: `com.shinybox.smash.S3DEngine`.
- Main game pack: `assets/S3DMain.smf`.
- No native `lib/*.so` file was found in the inspected archive.

## Hash evidence

| Entry | Bytes | SHA-256 |
|---|---:|---|
| Whole APK | 37,200,621 | `1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9` |
| `classes.dex` | 6,996,484 | `bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b` |
| `assets/S3DMain.smf` | 33,978,539 | `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3` |

## DEX metadata results

- 37,620 strings; 12,348 type IDs; 14,055 prototype IDs.
- 30,461 field IDs; 59,460 method IDs; 10,768 class definitions.
- 68 classes in the `com.shinybox.*` package scope emitted to the local Dalvik disassembly.

The full DEX class count also includes platform and third-party dependency classes; it does not mean all classes were authored by the game developer.

## Architectural observations

- `S3DEngine` subclasses `q0.b`; inspected application lifecycle methods delegate to Android's Application lifecycle.
- `Smash` is the primary Activity wrapper. DEX metadata includes lifecycle, sound, camera, sensor, input, asset-extraction, directory/cache and IAP-related method names.
- `S3DSurfaceView` subclasses `GLSurfaceView` and handles the engine surface/input boundary.
- `IAPWrapper` exposes purchase and restore callbacks.
- Method names and bytecode signatures provide evidence of interfaces, but are not sufficient to assert every runtime behavior.

## Manifest caveats

A best-effort AXML decoder produced readable XML. The resource table was not completely decoded, so some IDs remain numeric and are not resolved into resource names.

## Recovery status

Recovered: file identity/hashes, decoded manifest, DEX class/method metadata, and draft Dalvik disassembly for 68 app-specific classes.

Not recovered: original Java source formatting/comments/local variable names, full resource-name mapping, complete clean Android Studio project, or the game logic/assets inside the proprietary SMF pack. Disassembly may omit/approximate annotations, exception/debug metadata and unsupported opcode details. No APK rebuild or runtime test was performed.

## Security

The uploaded package contains `assets/api_key.txt` with a credential-shaped Amazon token. Its value and file are excluded from this repository and local bundle. If it is active, revoke or rotate it through the owning service.

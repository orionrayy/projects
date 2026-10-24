# Reverse-Engineering Report — Dungeon Quest APK

## Artifact identity

- Input: uploaded `DQ.zip`, an Android APK container.
- Size: 37,200,621 bytes; SHA-256: `1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9`.
- Package: `com.shinybox.smash`; version `3.3.2.0`; version code `1423433200`.
- Min SDK 21; target SDK 34; compile SDK 34.
- Main Activity: `com.shinybox.smash.Smash`; Application class: `com.shinybox.smash.S3DEngine`.
- Main pack: `assets/S3DMain.smf`.

## Recorded hashes

| Entry | Size (bytes) | SHA-256 |
|---|---:|---|
| Uploaded APK | 37,200,621 | `1e82932d93da9e02f94298bfd8555b65ff0bc2e679ab78500fa35f5b99fc04a9` |
| `classes.dex` | 6,996,484 | `bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b` |
| `assets/S3DMain.smf` | 33,978,539 | `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3` |

## DEX results

- 37,620 strings; 12,348 types; 14,055 prototypes; 30,461 field IDs; 59,460 method IDs; 10,768 class definitions.
- 68 app-specific `com.shinybox.*` classes emitted in the full local snapshot: 405 methods, 5,187 instruction boundaries, 50 payload directives, and 44 native declarations.
- 10,768 is the full DEX class-table count, including dependencies, not a count of game-authored classes.
- Three higher-confidence Java files compile against temporary minimal stubs. That is only syntax-level validation, not an Android project build.

## Asset container — verified extraction

The outer `S3DMain.smf` pack was decoded as an STK-style version-6 archive. Signature `0x00000008`, XOR key `0x4c4060e8`, 5,630 entries and metadata-end offset 335,530 were recovered from the header. All 5,630 payloads passed CRC-32 and decoded-size validation: 5,619 zlib+XOR entries and 11 raw+XOR entries, totalling 94,513,994 bytes.

The 17 `Resources/XML/*.xml` tables parse as XML and contain 2,623 `Row` records for game data such as skills, items, affixes, legends, talents, stats, IAP identifiers and localization/dictionary entries. See `STK_FORMAT_FINDINGS.md` and `ASSET_CATALOG.md`. The outer container is resolved; inner `.gam`, `.mdo`, `.msh`, `.ske`, `.scn` and related engine-specific records remain binary formats rather than original source.

## Architecture and native boundary

- `Smash` is the main Activity wrapper; methods cover lifecycle, asset/file handling, audio, camera, sensors, input and purchase integration.
- `S3DSurfaceView` derives from Android `GLSurfaceView`.
- `S3DRenderer` declares native entry points for initialization/shutdown, rendering, surface callbacks, pack descriptor handoff and input forwarding.
- Forty-four native declarations span four wrapper classes; the required implementations are not in DEX.

The manifest contains `requiredSplitTypes="base__abi,base__density"` and `isSplitRequired="true"`, consistent with a base APK delivered alongside ABI/density splits. The exact companion APKs have not been obtained, so shared libraries may be absent from this uploaded base artifact rather than never having shipped. See `SPLIT_APK_FINDINGS.md` and `NATIVE_ENGINE_BOUNDARY.md`.

## Validation and limits

The corrected disassembler's static checker reports zero structural consistency errors across the 68-class local snapshot. The decoded manifest XML parses, the asset pack verifies in full, Python helper scripts compile, and the three higher-confidence Java files compile against temporary stubs.

JADX, Apktool and a Smali assembler have not run in this offline runtime. No complete Gradle build, APK signing, emulator launch or runtime-equivalence test has been performed. Decompiled sources cannot recover original comments, local names, formatting, absent native implementations or all resource symbols.

## Sensitive data

The uploaded APK contains `assets/api_key.txt` with a credential-shaped Amazon token. The file and token value are excluded from repository outputs; rotate/revoke the token if active.

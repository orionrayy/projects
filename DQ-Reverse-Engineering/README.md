# Dungeon Quest — Reverse-Engineering Workspace

**Status: partial source reconstruction from DEX; not a complete or build-verified Android project.**

Analyzed APK: package com.shinybox.smash, version 3.3.2.0. Original APK binaries, proprietary asset pack, raw DEX and credential-bearing asset are excluded.

## Available

- Decoded Android manifest and selected reconstructed Smali-like class snapshots.
- Complete 68-class generated Smali-like source snapshot in the downloadable analysis ZIP.
- Java contract snapshots under `reference/java/`, including 34 native renderer signatures and observed Globals values. They compile standalone but do not implement the engine.
- DEX inventory/disassembly, AXML decoder, SMF probe, APK split audit and static validation tools.
- Reports for asset flow, native/split package boundary, unresolved SMF format, validation and sensitive asset handling.

Corrected metrics: 68 app-specific classes, 405 methods, 5,187 decoded instructions, 50 payload directives and 44 native declarations. Static validation is not proof of Smali assembler acceptance or runtime equivalence.

## Main finding: required split APKs

The manifest declares required split types for ABI and display density, `android:isSplitRequired=true` and `android:extractNativeLibs=false`. This upload contains no native `lib/<abi>/*.so` entries, so the missing engine may reside in a matching ABI split rather than be absent from the distribution. Matching splits have not yet been acquired or validated.

The asset `S3DMain.smf` is stored without ZIP compression and passed to native methods using its descriptor, offset and length. Its internal format remains unresolved; high entropy does not prove encryption.

## Reproduce locally

Extract the corresponding artifacts from an APK you are authorized to analyze:

```bash
python tools/axml_decode.py AndroidManifest.xml manifest/AndroidManifest.xml
python tools/dex_inventory.py classes.dex --output docs/dex-index.json
python tools/dex_disasm.py classes.dex --out disassembly
python tools/smf_probe.py assets/S3DMain.smf --output docs/smf-probe.json
python tools/apk_split_audit.py DQ.apk manifest/AndroidManifest.xml --output docs/apk-split-audit.json
python tests/validate_bundle.py
python tests/validate_smali.py --root disassembly
```

JADX, Apktool and a Smali assembler were unavailable in the offline execution environment. Original Java comments/formatting/local names, native implementation and SMF internals are not recovered.

The uploaded APK contains `assets/api_key.txt` with a credential-shaped token. That file and its value are excluded. Rotate/revoke the credential if active.

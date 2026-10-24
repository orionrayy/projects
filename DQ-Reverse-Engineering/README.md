# Dungeon Quest — Reverse-Engineering Workspace

**Status: partial source reconstruction from DEX; not a complete or build-verified Android project.**

Analyzed APK: package com.shinybox.smash, version 3.3.2.0. Original APK binaries, proprietary asset pack, raw DEX, and credential-bearing asset are excluded.

## Available

- Decoded Android manifest and selected reconstructed Smali-like class snapshots.
- DEX inventory, 68-class class/method metadata and a corrected 68-class source bundle attached to the task ZIP.
- Standard-library Python helpers: DEX inventory/disassembly, AXML decoder, SMF probe and APK split/asset audit.
- Static validation scripts and reports for source reconstruction, asset loading, native boundary, and security findings.

Corrected metrics: 68 app-specific classes, 405 methods, 5,187 decoded instructions, 50 payload directives, and 44 native declarations. Static validation is not proof of Smali assembler acceptance or runtime equivalence.

## Main finding: required split APKs

The manifest declares required split types for ABI and display density, `android:isSplitRequired=true`, and `android:extractNativeLibs=false`. This upload contains no native `lib/<abi>/*.so` entries, so the missing binary engine may be in a matching ABI split rather than absent from the distribution. Matching splits have not yet been acquired or validated.

The asset `S3DMain.smf` is stored without ZIP compression and passed to native methods using its file descriptor, offset and length. Its internal format remains unresolved. Do not infer encryption from high entropy alone.

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

JADX, Apktool, a Smali assembler, the matching split APKs and a runtime build have not yet been run/verified in this environment. Original Java comments/formatting/locals, native implementations and SMF internals are not recovered.

The uploaded APK contains `assets/api_key.txt` with a credential-shaped token. That file and its value are excluded. Rotate/revoke the credential if active.

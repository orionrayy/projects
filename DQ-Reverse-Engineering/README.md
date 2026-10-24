# Dungeon Quest APK — Reverse-Engineering Workspace

**Status: partial static analysis, not a recovered original source tree.**

Analyzed input: Android APK package `com.shinybox.smash`, version `3.3.2.0`. The original APK, the 33.9 MB proprietary `assets/S3DMain.smf` pack, and credential-bearing `assets/api_key.txt` are deliberately not committed here.

## Current findings

- Binary Android manifest decoded to readable XML in the local analysis bundle.
- DEX metadata: 10,768 class definitions and 59,460 method IDs; 68 app-specific classes under `com.shinybox.*` were disassembled to Dalvik-level instructions.
- Main wrapper types identified: `Smash`, `S3DEngine`, `S3DSurfaceView`, `ShinyActivity`, `IAPWrapper`, and `AmazonIAPWrapper`.
- `S3DMain.smf` is not decoded. High entropy is only a clue; it does not prove whether the pack is compressed, encrypted, or proprietary.
- Source reconstruction is incomplete. This is not a clean, buildable Android Studio project; emitted disassembly may require repairs to reassemble.

## Repository vs. local bundle

This GitHub directory contains findings, helper scripts, security notes, and a representative Dalvik listing. The full local archive supplied with the task contains the decoded manifest, complete class/method index, probe output, and all 68 app-specific Dalvik disassembly files. It excludes the original APK and sensitive token file.

## Reproduce locally

Python analysis tools use the standard library only:

```bash
python tools/axml_decode.py AndroidManifest.xml manifest/AndroidManifest.xml
python tools/dex_inventory.py classes.dex --output docs/dex-inventory.json
python tools/dex_disasm.py classes.dex --out disassembly
python tools/smf_probe.py assets/S3DMain.smf --output docs/smf-probe.json
```

To attempt Java-like reconstruction, run JADX locally: `jadx -d build/jadx DQ.zip`. Apktool can decode Android resources and smali project layout: `apktool d -f DQ.zip -o build/apktool`. Neither is bundled in this workspace.

Do not claim full game-source recovery until the SMF records have been structurally decoded and the recovered code is validated. Never add `assets/api_key.txt` to version control; rotate the credential through the owning service if active.

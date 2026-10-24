# Dungeon Quest — Reverse-Engineering Workspace

**Status: partial source reconstruction from DEX; not a full or build-verified Android project.**

Analyzed APK: package `com.shinybox.smash`, version `3.3.2.0`. The original APK, raw DEX, proprietary game pack, and credential-bearing asset are excluded from this repository.

## Current reconstruction

- 68 app-specific `com.shinybox.*` classes emitted as Smali-like source.
- 405 methods, 5,187 decoded instructions, 50 payload directives.
- Static validation: 0 structural consistency errors across those outputs.
- Selected source snapshots, class/method inventory, decoded Android manifest, analysis tools, security notes, and validation reports are maintained in this folder.
- The complete 68-class snapshot and tools are also available as the attached ZIP artifact for this task. The GitHub folder is a curated source workspace and does not yet contain every generated class file.

## Native engine and asset boundaries

The DEX declares 44 native methods across four wrapper classes. The supplied APK archive contains no `lib/<abi>/*.so` entries, even though Java code requests `crypto`, `ssl`, `openal`, and `S3DClient`. The asset pack `S3DMain.smf` remains unresolved. These missing native components and the proprietary pack prevent a complete rebuild from the supplied artifact alone.

## Tools and reproduction

The analysis helpers use Python's standard library. Use them with authorized locally extracted APK components:

```bash
python tools/axml_decode.py AndroidManifest.xml manifest/AndroidManifest.xml
python tools/dex_inventory.py classes.dex --output docs/dex-index.json
python tools/dex_disasm.py classes.dex --out disassembly
python tools/smf_probe.py assets/S3DMain.smf --output docs/smf-probe.json
python tests/validate_smali.py --root disassembly
```

The regenerated local snapshot was validated structurally, but not assembled or built. JADX/Apktool/Smali assembler tools could not be run in the current offline environment. Decompilation cannot restore original comments, Java formatting, local-variable names, annotations, or native implementations.

The APK included `assets/api_key.txt` with a credential-shaped token. It is deliberately excluded. If active, revoke/rotate the token with the owning service.

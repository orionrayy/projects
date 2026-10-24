# Dungeon Quest — Reverse-Engineering Workspace

**Status: partial source reconstruction from DEX; not a complete or build-verified Android project.**

Analyzed APK: package com.shinybox.smash, version 3.3.2.0. The original APK, raw DEX, proprietary game pack, and credential-bearing asset are excluded from this repository.

## Current reconstruction

- 68 app-specific com.shinybox.* classes emitted as Smali-like source in the local analysis archive.
- Local snapshot totals: 405 methods, 5,187 decoded instructions, 50 payload directives, and 44 native method declarations.
- The high-confidence Java layer includes BuildConfig.java, Globals.java, and S3DEngine.java; these three files compiled with javac against temporary minimal API/dependency stubs.
- Method-level source excerpts now cover selected ShinyActivity behavior, Smash pack I/O, the Smash native-library load order, and the S3DRenderer JNI boundary.
- The DEX-to-Java stub generator emits declaration scaffolds for authorized locally extracted DEX files. Nontrivial method bodies are not fabricated.
- Static validation reports zero structural errors across the locally generated 68-class Smali-like snapshot.
- The complete 68-class snapshot and full local analysis tools are supplied in the companion ZIP artifact. This GitHub folder remains a curated source workspace and does not yet contain every generated class file.

## Split-package finding

The decoded manifest lists requiredSplitTypes="base__abi,base__density" and application isSplitRequired="true". This is consistent with a base APK whose ABI and density companion splits are required. Missing native libraries in this one archive therefore do not prove those libraries were never shipped. See docs/SPLIT_APK_FINDINGS.md and docs/NATIVE_ENGINE_BOUNDARY.md.

## Native engine and asset boundaries

The DEX declares 44 native methods across four wrapper classes. The main game pack S3DMain.smf remains unresolved. The matching ABI/density splits have not been provided or inspected. These gaps prevent a complete rebuild from the supplied artifact alone.

## Tools and reproduction

The committed helpers use Python's standard library. Extract classes.dex and assets from a copy you are authorized to analyze, then run:

```bash
python tools/dex_inventory.py classes.dex --output docs/dex-index.json
python tools/generate_java_stubs.py classes.dex --out reconstruction/java
python tools/smf_probe.py assets/S3DMain.smf --output docs/smf-probe.json
```

The manifest-analysis excerpt in manifest/ is for inspection, not direct APK repackaging. The local ZIP also includes the corrected custom disassembler and static validator for the complete 68-class snapshot.

JADX/Apktool/Smali assembler tools could not be run in the offline analysis environment. Decompilation cannot restore original comments, Java formatting, local-variable names, or native implementations. No Android Gradle build, signing, emulator launch, runtime equivalence test, or SMF decoding has been completed.

## Credential handling

The APK included assets/api_key.txt with a credential-shaped Amazon token. It is deliberately excluded. If active, revoke/rotate the token with the owning service.

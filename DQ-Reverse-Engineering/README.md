# Dungeon Quest — Reverse-Engineering Workspace

**Status: partial source reconstruction from DEX; not a complete or build-verified Android project.**

Analyzed APK: package com.shinybox.smash, version 3.3.2.0. Original APK binaries, the proprietary pack, and credential-bearing assets are excluded.

## What is available here and in the attached source bundle

- GitHub reports, static findings, a DEX inventory summary, selected Smali-like class snapshots, manifest decoder, inventory tool, SMF probe, and validator.
- The downloadable DQ-Reverse-Engineering.zip attachment contains the complete generated 68-class Smali-like snapshot and corrected disassembler source used to produce it.
- Corrected output counts: 68 app-specific classes, 405 methods, 5,187 instructions, 50 payload directives, and 44 native method declarations.
- Structural validation passed with zero errors; this does not prove assembler acceptance or runtime equivalence.

## Native engine and asset boundaries

The supplied APK has no lib/<abi>/*.so entries, although Java code requests libraries named crypto, ssl, openal, and S3DClient. The core pack S3DMain.smf is unresolved. Rebuilding the original game from this artifact alone is therefore not demonstrated.

## Tools

The standard-library Python helpers can inspect manifest XML, inventory DEX identifiers, and probe .smf candidates. Use them with locally extracted files from an APK you are authorized to analyze:

    python tools/axml_decode.py AndroidManifest.xml manifest/AndroidManifest.xml
    python tools/dex_inventory.py classes.dex --output docs/dex-index.json
    python tools/smf_probe.py assets/S3DMain.smf --output docs/smf-probe.json
    python tests/validate_smali.py --root disassembly

The corrected disassembler and all 68 generated class files are in the attached snapshot; the GitHub tree currently includes a curated selection of reconstructed classes and analysis tools. JADX, Apktool and a Smali assembler could not be run in the current offline runtime. Original Java formatting/comments/local names, missing native implementations, and the SMF format are not recovered.

The APK included assets/api_key.txt with a credential-shaped token. It is intentionally excluded. Rotate/revoke it through its owning service if active.

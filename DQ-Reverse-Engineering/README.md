# Dungeon Quest — Reverse-Engineering Workspace

**Status: partial source reconstruction from DEX plus verified extraction of the outer game-asset archive. This is not a complete/build-verified Android project.**

Analyzed APK: package `com.shinybox.smash`, version `3.3.2.0`. Original APK, raw DEX, pack container, and credential-bearing asset are excluded from this code repository.

## Included

- `disassembly/`: representative Dalvik-level output and class/method inventory for the 68 app-specific classes.
- `reconstruction/verified/java/`: higher-confidence `BuildConfig`, `Globals`, and `S3DEngine` source excerpts; compiled against temporary Java stubs only.
- `reconstruction/fragments/`: reconstructed methods from `ShinyActivity`, `Smash` pack I/O, native-library load order and the JNI renderer boundary.
- `tools/`: offline Python helpers for AXML, DEX inventory/disassembly, Java declaration scaffolds, reachability heuristics, SMF reconnaissance, and safe STK extraction.
- `docs/`: evidence report, IAP identifier catalog, native method index, split-APK findings, STK format findings, extracted-asset catalog and validation details.

The full local analysis bundle contains 68 generated Dalvik class files, 68 Java declaration scaffolds, complete per-asset hashes/sizes, and the remaining scripts. This curated public directory does not include all 68 generated files or publish the extracted binary assets.

## DEX evidence

- 10,768 total DEX class definitions and 59,460 method IDs; these include platform/dependency classes.
- 68 app-specific `com.shinybox.*` classes, 405 method declarations, 361 code-bearing methods in the reachability scan.
- 5,187 decoded instruction boundaries, 50 payload directives and 44 native declarations.
- 104 distinct static IAP SKU identifiers; these do not establish current store prices or entitlements.

## Asset archive — resolved

The `S3DMain.smf` container was parsed successfully: signature `0x00000008`, version 6, 5,630 entries, all payload CRC-32 and decoded-size checks passing. It yielded 94,513,994 bytes across 5,619 zlib+XOR and 11 raw+XOR entries. Seventeen readable `Resources/XML/*.xml` tables contain 2,623 row records. See `docs/STK_FORMAT_FINDINGS.md` and `docs/ASSET_CATALOG.md`.

The outer container is decoded; inner `.gam`, `.mdo`, `.msh`, `.ske`, `.scn` and related engine-specific formats remain binary data, not decompiled native source.

## Reproduction

```bash
python tools/dex_inventory.py /path/to/classes.dex --output docs/dex-index.json
python tools/dex_disasm.py /path/to/classes.dex --out disassembly
python tools/generate_java_stubs.py /path/to/classes.dex --out reconstruction/java --include-safe-constants
python tools/analyze_dex_reachability.py /path/to/classes.dex --output docs/dex-reachability.json
python tools/stk_unpacker.py /path/to/S3DMain.smf --inventory-json docs/asset-inventory.json --inventory-csv docs/asset-inventory.csv
python tools/stk_unpacker.py /path/to/S3DMain.smf --extract /path/to/new-empty-directory
python tests/validate_bundle.py
```

## Remaining blockers

The manifest's `requiredSplitTypes="base__abi,base__density"` and `isSplitRequired="true"` are consistent with split delivery; exact ABI/density companion APKs have not been obtained. The 44 JNI native implementations are absent from DEX. JADX, Apktool and a Smali assembler have not run in this offline environment; no complete Gradle build, signing, emulator launch or runtime-equivalence test has succeeded.

The uploaded APK contained `assets/api_key.txt` with a credential-shaped token. That file/value is excluded; rotate/revoke the token if active.

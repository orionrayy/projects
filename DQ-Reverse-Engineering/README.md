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

This GitHub directory contains the findings, helper scripts, and a representative Dalvik listing. The full local archive supplied with the task contains the decoded manifest, complete method/class index, and all 68 app-specific Dalvik disassembly files. It excludes the original APK and sensitive token file.

## Reproduce deeper decompilation

1. Run JADX locally: `jadx -d build/jadx DQ.zip`.
2. Run Apktool locally: `apktool d -f DQ.zip -o build/apktool`.
3. Compare the Java-like output with the recorded DEX disassembly and investigate failures.
4. Analyze the SMF format separately; do not claim full game-source recovery until records are structurally decoded and validated.
5. Never add `assets/api_key.txt` to version control; rotate the credential through the owning service if active.

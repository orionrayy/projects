# Dungeon Quest ModKit checkpoint — v77 DEX package identity alignment

Date: 26 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
PR: #26 (draft/unmerged)

## User-observed runtime result
The user reports that v76 still force-closes. Therefore restoring the exact stock STK did not resolve the issue. No device runtime pass is claimed.

## New static finding
Disassembly of v76 `classes.dex` showed both `BuildConfig.APPLICATION_ID` and `Globals.sPackageName` were initialized to `com.shinybox.smash` while the Android package ID had been changed to `com.shinybox.dqv76`. `Smash` reads `Globals.sPackageName` to construct cache/pack paths and calls `PackageManager.getApplicationInfo(sPackageName, 0)`. This is a concrete static identity inconsistency and a plausible cause of force-close. Runtime causality is not yet proven.

## v77 candidate
- APK: `DQ_ModKit_v77_DEX_IDENTITY_FIX_ARM64.apk`
- SHA-256: `77dac9fe85f1e9519424b78690261074be2fafd26afac521fdab50fdd9198cb9`
- Size: 57,045,884 bytes
- Package / label: `com.shinybox.dqv77` / `DQ v77 Tester`
- DEX SHA-256: `375779dd935427cf172450b082e40f8c96d48af52122a17addf87f2bb7e852a1`
- Exact stock STK SHA-256 remains `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3`.
- Both static app identity fields now agree with the Android package ID; Java class descriptors and native library bytes are unchanged.
- DEX SHA-1 signature and Adler32 checksum were recalculated.
- APK ZIP CRC, V1/V2/V3 signatures, 16 KiB alignment, aapt package/label, manifest/resource package ID consistency and stock STK hash all pass.

## Runtime and feature boundary
Physical-device install and launch are still not tested here. Gold +100K checks have not been attempted. The candidate has a local diagnostic test signature and cannot update the official app. Promotion remains blocked until phone runtime and feature behavior are actually verified. Keep the official app and its save data untouched.

## Next action
Phone-only A/B: install v77 separately and launch without pressing cheat controls. If it opens, capture first stable screen and then test further only on an isolated/disposable profile. If it still force-closes, stop producing package-renamed APK variants and collect a device-side crash trace to identify the actual exception/native signal before the next code change.

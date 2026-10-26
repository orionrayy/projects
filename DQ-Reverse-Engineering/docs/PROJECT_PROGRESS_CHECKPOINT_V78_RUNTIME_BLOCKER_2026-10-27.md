# Dungeon Quest ModKit — v78 blocker / runtime triage checkpoint

Date: 27 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
PR: #26 (draft, open, unmerged)

## User-observed runtime result

The user reports v77 still force-closes. v75 and v76 had also force-closed. The v77 download was reissued with identical bytes and therefore did not constitute a new code build. No candidate can be marked stable from CI/static checks alone.

## Strong newly-confirmed packaging concern

The original analyzed stock artifact DQ.zip is not a self-contained installable APK by manifest design:
- isSplitRequired = true
- requiredSplitTypes = base__abi,base__density
- extractNativeLibs = false
- the stock base archive records 0 native-library entries
- the recorded acquisition history identifies a 20-split XAPK/set for package com.shinybox.smash, version 3.3.2.0.

The locally produced v75–v77 tester artifacts have been distributed as standalone single APKs (split_count = 1), despite the original app requiring ABI and density split components. Later variants bundle several native libraries but do not represent the complete verified original 20-split installation. This is a high-priority packaging defect candidate and could explain startup crashes/resource or native loading errors. It is not yet proven as the direct runtime cause because there is no crash trace.

Relevant report: DQ-Reverse-Engineering/docs/SPLIT_APK_FINDINGS.md and DQ-Reverse-Engineering/docs/apk-split-audit-summary.json.

## Other static findings retained

- v75 repaired the STK header-key/decoded-metadata-CRC invariant; the user still saw a force-close.
- v76 restored the exact stock STK; the user still saw a force-close. The HUD/STK payload alone is not a sufficient explanation.
- v77 aligned the DEX BuildConfig.APPLICATION_ID / Globals.sPackageName dotted literal to com.shinybox.dqv77, recalculated DEX SHA-1 and Adler-32, preserved Java class descriptors and stock STK; the user still saw a force-close.
- The stock native library contains many Java_com_shinybox_smash_S3DRenderer_* JNI export names. These must not be globally rewritten to a new app ID because Java class namespace/JNI symbol consistency would break.

## Decision / next gate

Stop issuing identical re-download links and stop speculative package-renamed APK builds until one of these inputs is obtained:
1. A device-side crash log from the failed com.shinybox.dqv77 launch; or
2. The complete authorized installed split set matching the installed official version and ABI/density, exported from the user's phone (rather than the base APK alone).

For a phone-only log capture on Android 11+, recommend Shizuku started via Wireless debugging plus an open-source Logcat reader that supports Shizuku, record immediately before launching v77, then export a log filtered for com.shinybox.dqv77, AndroidRuntime, FATAL EXCEPTION, Fatal signal, and linker/UnsatisfiedLinkError. Redact unrelated personal data before sharing.

For split acquisition, the user should export the complete installed split set using an Android split-APK exporter, verify that all splits have the same version/signature and include the required base ABI and density split types, and share the export only if comfortable. Do not ask them to uninstall the official app, clear its data, or install a modified package over the official signature.

## Current verified boundary

- v77 candidate did not pass user runtime test.
- Gold +100K runtime: not attempted / unverified.
- Native cheat catalog runtime integration: 0/222.
- PR #26 remains draft/unmerged.
- No new v78 APK was built, intentionally: without logs or complete split inputs, another single-APK variant would repeat the same unsupported assumption.

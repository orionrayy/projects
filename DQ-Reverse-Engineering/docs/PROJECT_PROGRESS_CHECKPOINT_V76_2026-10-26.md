# Dungeon Quest ModKit checkpoint — v76 stock-STK startup isolation

Date: 26 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
Base: v74 provider-authority comparator
Latest diagnostic artifact: DQ_ModKit_v76_STOCK_STK_BASELINE_ARM64.apk

## User runtime result

The user reports that v75 still force-closes. Therefore the v75 STK header-key/metadata-CRC repair was not sufficient to establish runtime stability. Do not mark the crash fixed and do not treat static CI as runtime evidence.

## Root-cause assessment

The official stock STK passes the archive invariant: header key and CRC32 of the decoded metadata table are both 0x4c4060e8. The v50-derived candidate violates it (header key 0x4c4060e8; decoded metadata CRC 0x87bfe0b7). v75 repairs that invariant, but it still includes the modified Resources/HUD/pause.hud payload from the v50-derived candidate. Since v75 force-closes, remaining hypotheses include the modified pause HUD payload/parser, package/manifest/signature-sensitive initialization, or the native startup path. Current evidence does not determine which is responsible.

## v76 A/B diagnostic

- APK: DQ_ModKit_v76_STOCK_STK_BASELINE_ARM64.apk
- SHA-256: c726c1d1ae6ddb834ffcae6f59b2797e05b752174865a44239c9abcd22b9bb8d
- Size: 57,045,884 bytes
- Package: com.shinybox.dqv76
- Label: DQ v76 Tester
- ABI: arm64-v8a
- STK exactly matches official stock bytes: 340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3
- DEX remains stock: bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b
- The package ID, authorities, and label are isolated from the official app.
- ZIP CRC, 16 KiB alignment, V1/V2/V3 APK signature verification, aapt package/label checks, exact stock STK hash, and stock DEX hash passed.

This build intentionally restores the entire official S3DMain.smf. It is a startup-isolation comparator, not a feature build; Gold +100K is not implemented or validated here.

## Runtime boundary and next step

Physical-device installation and launch have not been performed by the build environment. The next check is phone-only: install v76 as a separate tester, leave the official app/save untouched, launch once without network if possible, and report whether it reaches the title/menu or force-closes. If v76 opens, the v50-derived HUD/STK payload becomes the leading suspect. If v76 also crashes, isolate package/signature/provider initialization and native startup with a device-side crash trace. Promotion remains blocked until device runtime and feature behavior are verified.

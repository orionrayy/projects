# Dungeon Quest ModKit checkpoint — v73 no-native-probe comparator

Date: 26 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7
Prior checkpoint: v72 Logcat-observable diagnostic probe

## Trigger

The user reported that force close had returned, resembling earlier failures, after the v72 diagnostic package. The exact on-device stack trace was not available. The most salient v72-specific risk is its new native callback path, invoked after engine initialization even though exact-build ABI/thread/lifetime behavior had not been runtime-proven.

## Isolation build created

- Artifact: DQ_ModKit_v73_NO_NATIVE_PROBE_ARM64.apk
- Package: com.shinybox.dqv73 (separate diagnostic install)
- SHA-256: 53799adf3e9d8b3efca062c9a8c97489a050196ad4f9aafcc84acf86d2ad0e49
- Size: 57,078,652 bytes
- Stock DEX restored: bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b
- Native bridge removed: libdqbridge.so absent
- Gold HUD STK preserved: e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e

The package is deliberately an A/B isolation comparator, not a fix declaration: it removes the v72 probe and retains the same v50 HUD asset. A successful v73 launch alongside a v72 crash would support a probe-path regression; it would not by itself prove a precise root cause. If v73 also crashes, other package/resource/content/device causes remain in scope.

## Static gates

ZIP CRC, 16 KiB native library alignment before and after signing, APK Signature V1/V2/V3, aapt badging, separate package ID, launcher label, stock DEX digest, no native probe bridge, and unchanged STK digest passed.

## Runtime gate

No device is connected to this build environment. v73 has not been installed or launched here. The force-close is not yet reproduced or cleared with logs. Gold +100K remains 0/9 runtime-verified. Catalogue integration remains 0/222. Stable promotion remains blocked.

Do not reopen v72 for now, uninstall the official app, risk production saves, or bypass IAP/license/integrity/account/cloud controls. Use v73 only as a separate diagnostic app and do not tap Gold +100K during the initial startup isolation.

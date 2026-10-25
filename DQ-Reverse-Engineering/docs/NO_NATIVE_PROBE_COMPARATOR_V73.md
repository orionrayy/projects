# DQ v73 no-native-probe comparator

**Purpose: isolate the force-close reported after v72. Static validation passed; device runtime remains untested.**

- APK: DQ_ModKit_v73_NO_NATIVE_PROBE_ARM64.apk
- SHA-256: 53799adf3e9d8b3efca062c9a8c97489a050196ad4f9aafcc84acf86d2ad0e49
- Size: 57,078,652 bytes
- Package ID: com.shinybox.dqv73
- Launcher label: DQ v73 Tester
- ABI: arm64-v8a
- Test signing certificate SHA-256: f797c412ba5b96e7ec85d5deb36a0b2905c9c1c45ba354328ab54e1ee3579616

## Isolation changes from v72

1. Restored the exact stock classes.dex from the v50 candidate input. SHA-256: bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b. This removes DqNativeProbe and the Java/JNI lifecycle call sites.
2. Removed lib/arm64-v8a/libdqbridge.so, so this package cannot call the diagnostic native callback bridge.
3. Preserved assets/S3DMain.smf from the v50 candidate, SHA-256 e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e, to retain the same Gold +100K HUD candidate during comparison.
4. Used a separate package ID, com.shinybox.dqv73. It will not update or overwrite either the official app or v72.

## Static checks

ZIP CRC, 16 KiB native-library alignment before/after signing, APK Signature V1/V2/V3, aapt badging, package ID, label, stock DEX hash, absence of the probe bridge, and the unchanged STK hash all passed.

## Device comparison

Do not open v72 again for now. Keep the official app installed and do not use a production save. Install v73 as a separate app and launch it without tapping the Gold +100K button.

- If v73 reaches a stable first screen but v72 force-closes, the native probe path becomes the leading suspect. That supports isolation but is not a complete crash root-cause proof.
- If v73 also force-closes, stop testing and share the exact package/version plus an Android bug report or Logcat excerpt with personal identifiers removed. The cause is not isolated to the v72 probe alone.

No physical-device installation/startup was performed in this build environment. Gold +100K remains 0/9 runtime-verified, catalogue integration remains 0/222, and stable promotion remains blocked. The APK uses a local test certificate, not the publisher certificate.

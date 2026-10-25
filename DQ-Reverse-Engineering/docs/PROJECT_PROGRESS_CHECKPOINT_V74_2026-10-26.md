# Dungeon Quest ModKit checkpoint — v74 provider-authority fix

Date: 26 October 2026 (WIB)
Repository: orionrayy/projects
Branch: feat/dq-iap-debug-cheats-modkit-v7

## Finding
The v73 manifest used package ID com.shinybox.dqv73 but retained provider authorities com.shinybox.smash.mobileadsinitprovider and com.shinybox.smash.androidx-startup. If the official app is installed, these names can collide with the already-registered official providers and cause Package Manager to reject the install. This is the leading hypothesis for “App not installed”; the actual install failure code remains unknown.

## v74
- Package ID: com.shinybox.dqv74; launcher label: DQ v74 Tester.
- Provider authority names changed to com.shinybox.dqv74.mobileadsinitprovider and com.shinybox.dqv74.androidx-startup.
- aapt xmltree confirms the new authority values and absence of the old official-namespaced values.
- Exact stock classes.dex preserved: bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b.
- Gold candidate STK preserved: e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e.
- libdqbridge.so remains absent. This is a no-native-probe comparator and a manifest install-fix attempt, not a stable release.

## Artifact
- APK: DQ_ModKit_v74_PROVIDER_AUTHORITY_FIX_ARM64.apk
- SHA-256: 6185a5f85eaf80ec3cc290cc10e2f0539a5e4ef9eb43ea51b1bae7b4feceda8e
- Size: 57,078,652 bytes
- Local diagnostic signer; not the official publisher certificate.

## Current gates
Static package validation passes. Device install/start is not tested. Provider conflict is not confirmed by an on-device error code. Gold +100K remains 0/9, catalogue remains 0/222, stable promotion remains blocked. Keep official app data intact; use v74 as a separate test app and do not tap Gold +100K during first launch.

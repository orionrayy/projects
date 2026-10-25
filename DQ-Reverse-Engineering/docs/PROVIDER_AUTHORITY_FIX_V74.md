# DQ v74 provider-authority fix

**Static checks pass. Device installation is not yet tested.**

- APK: DQ_ModKit_v74_PROVIDER_AUTHORITY_FIX_ARM64.apk
- SHA-256: 6185a5f85eaf80ec3cc290cc10e2f0539a5e4ef9eb43ea51b1bae7b4feceda8e
- Size: 57,078,652 bytes
- Package ID: com.shinybox.dqv74
- Label: DQ v74 Tester
- ABI: arm64-v8a
- Test certificate SHA-256: 3fb6da2754270acdbb0cfdb70a012c5ab6007ece1efdd73adef9028fca25df7a

## Suspected installation blocker found

v73's package ID had been changed, but two ContentProvider authorities were still namespaced as the official app. Android can refuse installation when these authorities collide with providers already registered by the official game.

| v73 authority | v74 authority |
|---|---|
| com.shinybox.smash.mobileadsinitprovider | com.shinybox.dqv74.mobileadsinitprovider |
| com.shinybox.smash.androidx-startup | com.shinybox.dqv74.androidx-startup |

Android Build Tools confirm that v74 contains the new names and neither old authority remains. This is a high-confidence hypothesis, not a confirmed Package Manager error code.

## Static validation

ZIP CRC, 16 KiB native-library alignment before and after signing, APK Signature V1/V2/V3, aapt package/label/authority checks, the restored stock DEX digest, absence of libdqbridge.so, and the preserved Gold candidate STK digest passed.

## Not yet verified

No physical-device install or launch was performed here. v74 is a separate, locally test-signed diagnostic app, not an update to the official game. Gold +100K remains 0/9 runtime-verified; catalogue integration remains 0/222; stable promotion remains blocked.

# Native Engine Boundary

## DEX evidence

The regenerated DEX output contains 44 native declarations in four wrapper classes:

| Class | Native methods | Role suggested by method signatures |
|---|---:|---|
| com.shinybox.smash.S3DRenderer | 34 | Engine initialize/shutdown, frame loop, surface lifecycle, pack descriptor and input/sensor forwarding |
| com.shinybox.base.ShinyActivity | 6 | Joypad events and global native callbacks |
| com.shinybox.googleplayservices.GooglePlayServicesWrapper | 2 | Login/initialization completion callbacks |
| com.shinybox.iap.IAPWrapper | 2 | Purchase success/failure callbacks |

The Smash static initializer requests libraries named crypto, ssl, openal, and S3DClient. S3DRenderer declares native methods including engineInitialize, engineRunOneFrame, engineSetPackFileDescriptor, and surface/input callbacks.

## Split APK finding

The decoded manifest contains:

- `requiredSplitTypes="base__abi,base__density"`
- `android:isSplitRequired="true"`
- `android:extractNativeLibs="false"`
- A `com.android.vending.splits.required=true` metadata entry

Android's platform manifest attributes define required split categories and say the package manager rejects installation if a required split type is missing. See the Android platform source: https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android14-release/core/res/res/values/attrs_manifest.xml

Android documents native libraries using the standard `lib/<abi>/lib<name>.so` paths inside APK content: https://developer.android.com/ndk/guides/abis

**Interpretation:** the lack of `lib/<abi>/*.so` in this one uploaded archive is not evidence that those libraries were never distributed. Its manifest strongly suggests that the APK is a base/split package and expects ABI and density splits. The exact split files and their contents have not yet been obtained or verified.

## Comparison with public Shiny Box engine references

A publicly documented port of Naught 2 instructs users to extract `libS3DClient.so` from `lib/armeabi-v7a` and `S3DMain.smf` separately from the game's assets: https://www.gamebrew.org/wiki/Naught_2_Vita

That is evidence that a related Shiny Box game uses this native-library/pack naming family. It is **not** proof that its library is binary-compatible with Dungeon Quest, the supplied version, or this APK's signing/version lineage. Do not substitute an unrelated game's .so.

## What must be obtained next

- Matching ABI split APK for this application/version/signing lineage, or the authorized installed split set.
- Matching density/resource split to restore resources.
- Verify package name, version, signer identity, and ABI before combining artifacts.

If matching native libraries cannot be obtained, a working engine would require an independent replacement implementation. DEX declarations alone cannot restore native method bodies.

# Native Engine Boundary

## DEX evidence

The regenerated DEX output contains 44 native declarations in four wrapper classes:

| Class | Count | Role suggested by method signatures |
|---|---:|---|
| com.shinybox.smash.S3DRenderer | 34 | Engine initialize/shutdown, frame loop, surface lifecycle, pack descriptor and input/sensor forwarding |
| com.shinybox.base.ShinyActivity | 6 | Joypad events and global native callbacks |
| com.shinybox.googleplayservices.GooglePlayServicesWrapper | 2 | Login/initialization completion callbacks |
| com.shinybox.iap.IAPWrapper | 2 | Purchase success/failure callbacks |

The Smash static initializer requests libraries named crypto, ssl, openal, and S3DClient. S3DRenderer declares native methods including engineInitialize, engineRunOneFrame, engineSetPackFileDescriptor, and surface/input callbacks.

## New split-package finding

The decoded manifest contains:

- requiredSplitTypes="base__abi,base__density"
- application isSplitRequired="true"
- extractNativeLibs="false"

Android's manifest schema defines requiredSplitTypes as split categories that must be present and says the package manager rejects installation when a required type is missing. See the Android platform attribute definition:
https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android14-release/core/res/res/values/attrs_manifest.xml

Therefore, the absence of lib/<abi>/*.so inside this one uploaded archive should no longer be treated as evidence that the native binaries were never distributed. The artifact is consistent with a base APK that expects required ABI and screen-density split APKs. This is a strong hypothesis from manifest metadata, not proof of the exact split files or where each native library resides.

Android documents standard native library paths as lib/<abi>/lib<name>.so inside APK content:
https://developer.android.com/ndk/guides/abis

## What must be obtained next

- The matching ABI split APK for the same application/version/signing lineage, or an authorized installed split set.
- The matching density/resource split APK(s), to restore the full resource view.
- Verification that package name, version, signer identity and ABI line up before combining any artifacts.

Do not copy arbitrary shared libraries from a different version into this base APK. If the native libraries cannot be obtained, a functioning engine would require an independent replacement implementation; DEX declarations alone cannot restore their native method bodies.

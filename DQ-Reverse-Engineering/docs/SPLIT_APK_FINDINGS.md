# Split APK Findings

## Direct evidence in the decoded manifest

The supplied archive's manifest excerpt includes:

- requiredSplitTypes = base__abi,base__density
- application isSplitRequired = true
- extractNativeLibs = false

Android's platform manifest schema states that requiredSplitTypes identifies split categories that must be present and that the package manager rejects installation when a required split type is missing. Primary reference:
https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android14-release/core/res/res/values/attrs_manifest.xml

The Android NDK documentation explains that native shared libraries in an APK normally use paths of the form lib/<abi>/lib<name>.so:
https://developer.android.com/ndk/guides/abis

## Interpretation

This uploaded artifact is consistent with a base APK generated for split delivery where ABI and density splits are required. That is a more grounded explanation for the absence of lib/<abi>/*.so in this one archive than assuming native libraries never shipped.

This is still an inference: the precise companion split files have not been inspected. The next artifact to obtain is the matching ABI split (and density split), or the complete installed split set from a device on which this exact version is installed.

## Acquisition and validation checklist

1. Obtain only authorized split APKs for package com.shinybox.smash, version 3.3.2.0.
2. Verify package name, version code, signer certificate and ABI compatibility across all parts.
3. Inventory each APK independently, including lib/<abi>/*.so, resources and split names.
4. Hash every split and retain a source/chain-of-custody manifest.
5. Do not mix libraries from a different version or signing lineage.
6. Re-run the native method inventory only after the matching libraries are available.

No companion split APK was provided, and no native engine implementation is claimed recovered.

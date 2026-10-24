# Native Engine Boundary

## DEX evidence

The regenerated DEX output contains 44 native declarations in four wrapper classes:

| Class | Count | Role suggested by method signatures |
|---|---:|---|
| `com.shinybox.smash.S3DRenderer` | 34 | Engine initialize/shutdown, frame loop, surface lifecycle, pack descriptor and input/sensor forwarding |
| `com.shinybox.base.ShinyActivity` | 6 | Joypad events and global native callbacks |
| `com.shinybox.googleplayservices.GooglePlayServicesWrapper` | 2 | Login/initialization completion callbacks |
| `com.shinybox.iap.IAPWrapper` | 2 | Purchase success/failure callbacks |

The `Smash` static initializer requests libraries named `crypto`, `ssl`, `openal`, and `S3DClient`. `S3DRenderer` declares native methods including `engineInitialize`, `engineRunOneFrame`, `engineSetPackFileDescriptor`, and surface/input callbacks.

## Missing binary evidence

No `lib/<abi>/*.so` entries were present in the inspected APK archive. That does not prove those libraries never existed; the uploaded artifact may be an incomplete base/split package or a different distribution variant. A clean-room Java wrapper cannot recover implementations that are absent from the DEX.

## Consequences

A working recreation would require the matching authorized native libraries or a separately implemented replacement engine, plus known ABI/package rules and a decoded/compatible asset pack. This workspace is not a complete source recovery.

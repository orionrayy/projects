# Core App Wrapper Inventory

Static inventory from the supplied DEX and corrected instruction disassembly. This is evidence from signatures/instructions, not a claim to original source.

| Class | Role / observed dependency | Method or interface evidence |
|---|---|---|
| `com.shinybox.smash.Smash` | Primary Android Activity, extends `ShinyActivity` | Activity lifecycle, directories, asset extraction, audio/camera/sensor/input, IAP result routing |
| `com.shinybox.smash.S3DEngine` | Application wrapper; extends obfuscated `q0.b` | Application lifecycle forwarding |
| `com.shinybox.smash.S3DSurfaceView` | OpenGL surface/input integration; extends `GLSurfaceView` | Renderer setup, surface callbacks, input/touch/sensor pathways |
| `com.shinybox.smash.S3DRenderer` | Java-to-native renderer bridge; implements `GLSurfaceView.Renderer` | 34 native declarations including `engineInitialize`, `engineRunOneFrame`, `engineSetPackFileDescriptor` |
| `com.shinybox.smash.Globals` | Static app/engine configuration | `bUseGLES2=true`, `iNativeScreenOrientation=6`, package/app names |
| `com.shinybox.base.ShinyActivity` | Base Activity/native callback bridge | 6 native callbacks, including joypad/input-related methods |
| `com.shinybox.iap.IAPWrapper` | Purchase and restore bridge | Product ID literals and Handler messages (600, 601, 602) |
| `com.shinybox.amazoniap.AmazonIAPWrapper` | Amazon billing adapter | Amazon/IAP integration methods |
| `com.shinybox.googleplayservices.GooglePlayServicesWrapper` | Google Play Services adapter | Native login/initialization completion callbacks |
| `com.shinybox.smash.CameraPreview` | Camera preview helper | Camera preview/surface callbacks |

## Asset handoff flow

`Smash.extractMainPack()` calls `AssetManager.openFd("S3DMain.smf")`, obtains the descriptor, start offset, and length, and later passes those values to `S3DRenderer.engineSetPackFileDescriptor(...)`. `engineInitialize()` and `engineRunOneFrame()` run across the native boundary. More detail: `ASSET_LOAD_TRACE.md`.

## Static metrics

- 10,768 total class definitions in DEX (includes dependencies).
- 68 app-namespace class files emitted.
- 405 methods, 5,187 decoded instructions, 50 payload directives.
- 44 native method declarations, of which 34 are on S3DRenderer.

The full class and method index is distributed in the attached source bundle. The repo keeps this concise inventory and selected reconstructed class snapshots.

# Core App Wrapper Inventory

This is a concise, human-readable index of app-specific wrapper surfaces identified in `classes.dex`. It is not a substitute for a source-level decompilation.

| Class | Observed inheritance / role | Relevant method names visible in DEX |
|---|---|---|
| `com.shinybox.smash.S3DEngine` | Application wrapper; extends `q0.b` | `onCreate`, `onTerminate`, `onConfigurationChanged` |
| `com.shinybox.smash.Smash` | Primary Activity wrapper; extends `ShinyActivity` | activity lifecycle, asset extraction, home/cache directories, camera/sensor/audio/input integration |
| `com.shinybox.smash.S3DSurfaceView` | OpenGL surface/input integration; extends `GLSurfaceView` | renderer setup, motion/sensor and input handling |
| `com.shinybox.base.ShinyActivity` | Base activity | lifecycle forwarding, back/key/generic-motion input, system UI helpers |
| `com.shinybox.iap.IAPWrapper` | Billing bridge | `requestPurchase`, `restorePurchases`, `onPurchaseSuccess`, `onPurchaseFailed` |
| `com.shinybox.amazoniap.AmazonIAPWrapper` | Amazon billing bridge | Amazon/IAP-related methods |
| `com.shinybox.smash.CameraPreview` | Camera preview surface | preview callbacks, preview sizes, camera setup |
| `com.shinybox.smash.Globals` | Shared global accessors/state | global engine/application references |

Method names are observations from bytecode metadata; they do not prove complete behavior. Use the generated local `disassembly/CLASS_INDEX.md` and per-class disassembly for actual signatures and instruction-level evidence.

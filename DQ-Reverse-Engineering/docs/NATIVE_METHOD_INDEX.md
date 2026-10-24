# Native Method Index (DEX-derived)

This list records the 44 method declarations marked `native` in the current DEX inventory. Signatures are metadata evidence; native implementation bodies are not present in the DEX. A native declaration maps a Java method into the JNI boundary, not to a recovered implementation.

| Owner class | Method signature |
|---|---|
| `com.shinybox.base.ShinyActivity` | `checkSetTopBoxComplete(boolean)` |
| `com.shinybox.base.ShinyActivity` | `engineOnJoypadButtonDown(int, int)` |
| `com.shinybox.base.ShinyActivity` | `engineOnJoypadButtonUp(int, int)` |
| `com.shinybox.base.ShinyActivity` | `engineOnJoypadStickMove(int, int, float, float)` |
| `com.shinybox.base.ShinyActivity` | `engineOnJoypadType(int, int)` |
| `com.shinybox.base.ShinyActivity` | `updateInternetAvailable(boolean)` |
| `com.shinybox.iap.IAPWrapper` | `onPurchaseFailed(java.lang.String)` |
| `com.shinybox.iap.IAPWrapper` | `onPurchaseSuccess(java.lang.String)` |
| `com.shinybox.smash.S3DRenderer` | `engineDidPassFirstFrame()` |
| `com.shinybox.smash.S3DRenderer` | `engineGetCameraDeviceState()` |
| `com.shinybox.smash.S3DRenderer` | `engineGetOverlayMovie()` |
| `com.shinybox.smash.S3DRenderer` | `engineGetOverlayMovieHasChanged()` |
| `com.shinybox.smash.S3DRenderer` | `engineGetWantSwapBuffers()` |
| `com.shinybox.smash.S3DRenderer` | `engineInitialize()` |
| `com.shinybox.smash.S3DRenderer` | `engineOnCameraDeviceFrame(byte[], int, int)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnDeviceMove(float, float, float)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnHeadingChanged(float)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnKeyboardKeyDown(int, int)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnKeyboardKeyUp(int, int)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnLocationChanged(float, float, float)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnMouseButtonDown(float, float)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnMouseButtonUp(float, float)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnMouseMove(float, float)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnOverlayMovieStopped()` |
| `com.shinybox.smash.S3DRenderer` | `engineOnSurfaceChanged(int, int)` |
| `com.shinybox.smash.S3DRenderer` | `engineOnSurfaceCreated()` |
| `com.shinybox.smash.S3DRenderer` | `engineOnTouchesChange(int, float, float, int, float, float, int, float, float, int, float, float, int, float, float)` |
| `com.shinybox.smash.S3DRenderer` | `enginePause(boolean)` |
| `com.shinybox.smash.S3DRenderer` | `engineRunOneFrame()` |
| `com.shinybox.smash.S3DRenderer` | `engineSetCameraDeviceCount(int)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetCameraDeviceName(int, java.lang.String)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetDeviceIPAddress(java.lang.String)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetDeviceModel(java.lang.String)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetDeviceName(java.lang.String)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetDeviceUUID(java.lang.String)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetDirectories(java.lang.String, java.lang.String, java.lang.String)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetHeadingSupport(boolean)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetLocationSupport(boolean)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetPackFileDescriptor(java.io.FileDescriptor, long, long)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetSystemLanguage(java.lang.String)` |
| `com.shinybox.smash.S3DRenderer` | `engineSetSystemVersion(java.lang.String)` |
| `com.shinybox.smash.S3DRenderer` | `engineShutdown()` |
| `com.shinybox.googleplayservices.GooglePlayServicesWrapper` | `initComplete(boolean)` |
| `com.shinybox.googleplayservices.GooglePlayServicesWrapper` | `loginComplete(boolean)` |

## Summary

- `S3DRenderer`: 34 native methods for engine lifecycle, rendering, sensors, input, device metadata, and pack descriptor handoff.
- `ShinyActivity`: 6 native callbacks for joypad/TV detection and internet-state reporting.
- `IAPWrapper`: 2 native purchase callbacks.
- `GooglePlayServicesWrapper`: 2 native login/initialization callbacks.

These signatures do not reveal native implementation bodies. The matching ABI split, if supplied, must be inspected for the requested shared libraries before JNI-level reconstruction.

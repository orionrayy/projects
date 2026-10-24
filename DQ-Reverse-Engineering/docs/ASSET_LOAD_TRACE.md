# Asset Loading Trace

This note records only behavior visible in the decoded DEX/disassembly. It does not assume the native implementation's internal file format.

## Main pack path

1. The Activity calls a helper named `extractMainPack()`.
2. The helper calls `AssetManager.openFd("S3DMain.smf")` and stores the resulting `AssetFileDescriptor`.
3. It retrieves the descriptor, `getStartOffset()`, and `getLength()`.
4. It constructs a writable application data path using `/sdcard/Android/data/com.shinybox.smash`, with a `getCacheDir()` fallback if directory creation fails.
5. `S3DRenderer` receives three directory strings through `engineSetDirectories(...)` and the pack descriptor/offset/length through `engineSetPackFileDescriptor(...)`.
6. Native methods `engineInitialize()` and `engineRunOneFrame()` are called from the renderer lifecycle.

## ZIP container evidence

The uploaded APK ZIP entry for `assets/S3DMain.smf` has method 0 (STORED), with compressed size equal to its uncompressed size: 33,978,539 bytes. This is consistent with the Java use of `openFd()`, which needs an asset accessible as a file descriptor. The ZIP metadata does not reveal the internal SMF record format.

## Additional root assets

`extractAdditionalFiles()` lists root assets using `AssetManager.list("")`, skips entries whose name ends with `S3DMain.smf`, and calls `extractAssetFromAPK(...)` for other entries. The archive contains names `consentform.html` and `api_key.txt`; the visible control flow suggests they may be copied into the writable pack directory. This is a static code-path finding; runtime extraction was not observed or tested.

## Security implications

The credential-shaped contents of `api_key.txt` are not reproduced in this workspace. If the key is active, rotate/revoke it. Review the need to package and extract such a file, whether access rules allow other apps/users to read it, and whether it is exposed through backups/logs or support bundles.

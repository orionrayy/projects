# DQ v73 comparison protocol

1. Stop opening v72 for now. Do not uninstall the official Dungeon Quest app, delete app data, or use production saves.
2. If possible, verify the APK SHA-256 using a file verifier. Expected digest: 53799adf3e9d8b3efca062c9a8c97489a050196ad4f9aafcc84acf86d2ad0e49.
3. Install DQ_ModKit_v73_NO_NATIVE_PROBE_ARM64.apk. Its package ID is com.shinybox.dqv73, so it is a separate application. It uses a diagnostic test certificate, not the official signer.
4. Launch v73 and wait for the first stable screen. Do not tap the Gold +100K button during this isolation check.
5. Record whether installation was rejected, it force-closed immediately, it reached the first screen then crashed, or it reached a stable first screen. Also note Android version and whether v72 had crashed on startup or after an action.
6. If v73 force-closes too, stop repeated launches and share an Android bug report or Logcat crash excerpt with personal identifiers removed.

A clean v73 launch alongside a v72 crash points toward the v72 native probe path, but a crash report is needed to identify the exact cause. A successful startup does not prove the Gold +100K button or other cheats work.

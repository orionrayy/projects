# DQ v75 — phone-only test

The v30 fix established a structural invariant for modified STK packs: CRC32 of the decoded metadata table must equal the STK header key. The v50-derived asset used by v72-v74 did not satisfy it. v75 corrects that invariant.

1. Stop reopening v72 for now. Keep the official game and its save data intact.
2. Download DQ_ModKit_v75_STK_CRC_KEY_FIX_ARM64.apk directly on the phone.
3. Open the APK from Downloads/File Manager. If Android asks to allow installs from that source, enable the permission for the file manager/browser being used.
4. Install DQ v75 Tester as a separate app. Do not uninstall the official app or delete any game data.
5. Launch v75 once, preferably offline, and do not tap Gold +100K during the startup check.
6. Tell me whether installation succeeds and whether it reaches the first stable game screen or force-closes. If it crashes, stop repeated launches.

APK SHA-256: 02f175d07dcacd46f9f9f9d67809a081dd9b1926737247bcbe7ea5b8484f9346
Package: com.shinybox.dqv75

This APK uses a local diagnostic signer, not the publisher's certificate. Installation, startup and gameplay remain unverified on your device. Gold tests stay 0/9, catalogue effects 0/222, stable promotion blocked.

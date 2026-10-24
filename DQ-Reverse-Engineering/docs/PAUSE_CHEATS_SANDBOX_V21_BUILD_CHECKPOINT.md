# Dungeon Quest 3.3.2.0 — Cheats Sandbox v21 checkpoint

Status: asset patch and package-level static checks passed; device installation and in-game runtime remain NOT VERIFIED.

- Output bundle: Dungeon_Quest_3.3.2.0_CheatsSandbox.xapk
- Output SHA-256: 4105251dc555a5cde7655b2aae7a1bfa20d9dacc6adc7616212c12e19e9a4cd2
- Package ID: com.shinybox.dqmod (a side-by-side test identity; the original app ID/data are not overwritten)
- Contents: 20 split APKs, all using the same local test certificate.
- Package checks: outer XAPK CRC passed; all 20 inner APK ZIP CRC checks passed; jarsigner v1 signatures verified for all split APKs; signer fingerprints matched; stored native .so data offsets are aligned to 16 KiB and other stored entries to 4 bytes.
- Patched STK: SHA-256 eb949dc7f85218cbb8b13c3db1fbc72bbde9a180a3bf0cc125d809cdaeef15e8; 5,630 entries validated by the STK packer.
- HUD diff: the Pause menu label Social/IAP is renamed to Cheats Sandbox; its existing callback is renamed onShowCheats and calls uai_gp_hud.onResume followed by uai_gp_hud.onDebug(0). Action count stays 64; unrelated action records, general attributes and timers are preserved.
- App manifest package IDs and provider authorities were updated to avoid colliding with the stock install; fully qualified game Activity class names remain unchanged.
- GitHub Actions v21 patcher/test validation: PASS, run 40106571468 (https://github.com/orionrayy/projects/actions/runs/40106571468). This CI validates the parser/patcher's synthetic regression tests, not the original game's runtime.
- No purchase receipt, paid entitlement, cloud save, achievement or leaderboard logic was modified.

Remaining gates: no Android SDK apksigner/zipalign, adb, or ARM64 emulator/device was available here. Therefore this is not claimed as installed, launched, or runtime-stable. Before using the debug route, test offline with a disposable save; some server/account services may reject the renamed package. The signing key is local and intentionally not shipped.

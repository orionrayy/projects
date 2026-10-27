# Dungeon Quest ModKit v80 — Improved Cheat Menu

Date: 2026-10-28
Branch: `feat/dq-iap-debug-cheats-modkit-v7`
Artifact: `DQ_ModKit_v80_IMPROVED_CHEAT_MENU_ARM64.xapk`
SHA-256: `993f6b49b1e20ce4d1ba9faae77e71e42ab80e7ea3fd3e3f7222271dd19a6d7c`
Size: 57,736,325 bytes
Package: `com.shinybox.dqv80`
Split count: 20

## Purpose

The user confirmed that v79 restored the Pause → Options → Cheat Menu entry, but the menu was still the original early version. v80 incrementally improves that existing native debug page without pretending the separate 222-entry workbench has been integrated.

## In-game HUD edits

Only `Resources/HUD/debug.hud` changed in the decoded STK compared with v79.

- Menu title is clarified to `Cheat Menu`.
- Page headings are clarified: Champion Stone Rewards, Mythstone Rewards, Quick Actions, Feat Rewards, Level & Boss, Legend Options.
- The Add page now presents five stacked actions: Add Levels, Level Up, Gold +100K, Add Battle, Add Heroic.
- Level Up reuses the existing `uai_gp_hud.onShortcut("levelup", 1)` route.
- Gold +100K reuses the existing `uai_gp_hud.onDebug(6.0)` route.
- All 13 original action records remain byte-for-byte preserved; the HUD grows from 71 to 73 elements and from 13 to 15 action records.

## Static validation

- STK version 6; 5,630 entries; all entries decode and CRC-check, with unchanged-entry round-trip preserved.
- Header key matches the CRC32 of the rebuilt decoded metadata table.
- All 20 APK split manifests use `com.shinybox.dqv80`, including UTF-16 binary XML package strings.
- All splits share signing certificate SHA-256 `16b7e0f49377cb66c46a55caadb079b15ee26f07478384e1b45546da39505ce4`.
- APK v1, v2 and v3 signature verification passes on all 20 splits.
- 16-KiB native library alignment and inner/outer ZIP CRC checks pass.
- DEX SHA-1/Adler32 and absence of old `com.shinybox.dqv79` package identity pass.
- AAPT still prints the source package’s icon-resource warning when the base split is inspected alone; the package name and launcher-label resource string were independently checked. This is not claimed as a fully clean aapt report.

## Runtime status / limits

**Device runtime not tested in this build.** The user has confirmed v79’s menu route opens, but that does not verify v80 UI rendering or the effect/persistence of any individual action. Runtime-verified action count remains 0 until v80 is tested on the phone.

The 222-entry catalog is still not integrated into the game’s native list/selection dispatcher. Undo/reset, snapshot, event logging, sliders and other catalog controls are not connected. Do not label this as the complete cheat implementation.

The separate package ID keeps v80 separate from both the official app and v79. Do not uninstall the original app or clear its data for this test.

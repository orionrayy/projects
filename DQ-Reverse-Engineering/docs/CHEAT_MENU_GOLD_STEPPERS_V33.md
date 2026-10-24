# Cheat Menu Gold steppers v33

Artifact file: `Dungeon_Quest_3.3.2.0_CheatMenu_GoldSteppers_v33.xapk`  
SHA-256: `65e4cdc2284e02747c9eb942edc171588209cb4ffba723892f52cabe1ad81a3d`  
Status: static package validation passed; runtime not yet tested.

v33 fixes the failure mode in v32 where the custom Gold root tab did not visibly change the table. It adds four buttons to the existing Add page, rather than relying on a new tab:

- Gold -10 → `uai_gp_hud.SpendGold(10.000)`
- Gold -1 → `uai_gp_hud.SpendGold(1.000)`
- Gold +1 → `uai_gp_hud.RewardGold(1.000)`
- Gold +10 → `uai_gp_hud.RewardGold(10.000)`

There are no newly added numeric text inputs; these values are controlled only by buttons. Existing Add controls were repositioned/resized. The Debug HUD now contains 75 elements and 17 action records. All 5,630 packed entries decode/CRC-check, and the header key equals the decoded metadata CRC32. Only `Resources/HUD/debug.hud` changes at decoded-asset level. All 19 non-base APK splits are byte-identical to v31.

**Runtime pending:** install v33 as an update over the working v31/v32 app, open Cheat Menu → Add, and test Gold +1 on a disposable offline profile. Compare the displayed Gold before/after. If it fails or crashes, report exactly what happened. Do not infer success merely because buttons appear.

This is a limited Gold-control step, not the complete 222-cheat system. No billing receipt, IAP entitlement, cloud save or leaderboard logic was modified.

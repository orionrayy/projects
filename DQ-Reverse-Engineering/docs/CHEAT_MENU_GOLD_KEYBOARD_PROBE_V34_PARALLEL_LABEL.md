# v34 Parallel Label Build Report

- Artifact: `Dungeon_Quest_3.3.2.0_CheatMenu_SetGoldKeyboardProbe_v34_PARALLEL_LABEL.xapk`
- Package ID: `com.shinybox.dqv34`
- Launcher label: `DQ Test Build`
- Size: 57,571,164 bytes
- SHA-256: `28ec36842de60cc3333dadc263745d8488c2c780cb058ce6e000a36a46077174`
- Split APKs: 20
- Signer SHA-256: `6ba5a7ebddfccc1fde12c0b7538bd390dad51bc3b963d03c68e7545b961917b0`
- Local APK v2 structure/digest/RSA, inner/outer ZIP CRC, package ID, and native 16-KiB alignment checks: PASS
- Runtime: NOT TESTED ON DEVICE

The user's screenshot showed Android rejecting an update from v33 due to a signing-key mismatch. This build avoids replacing v33 by using a new package ID, `com.shinybox.dqv34`, and gives the launcher entry a distinct label `DQ Test Build`. It can be installed alongside v33 without uninstalling v33. The application ID and signer are unchanged from the already-built v34 PARALLEL package; this variant only changes the same-length app-name string in base resources.arsc.

The Set Gold button still calls the existing `uai_gp_hud.onSetGold` identifier. Whether the internal keyboard opens, whether the typed value commits, and whether the Gold balance changes are not verified until physical-device testing.
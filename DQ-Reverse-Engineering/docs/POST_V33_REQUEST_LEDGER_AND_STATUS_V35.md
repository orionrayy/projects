# Post-v33 request ledger — v35

Date: 2026-10-25
Target: Dungeon Quest Android 3.3.2.0

## Requests since v33

1. Expand the cheat table to match the original 222-entry catalog across 14 categories; the earlier game debug table was too small, stiff, ambiguous, and insufficiently varied.
2. Remove the four tiny Gold steppers shown in the v33 follow-up screenshot; they were placed incorrectly in the Add panel.
3. Gold must use a custom amount input, not fixed increments.
4. The game keyboard did not appear when entering values in the modified existing table; the internal keyboard field-to-commit route needs real verification.
5. Other numeric cheat values use four buttons only: -10, -1, +1, +10. No editable text box for ordinary numeric controls.
6. Keep the tools inside the same Cheat Menu rather than placing Gold in a separate tab.
7. Preserve the known-working v33 installation while testing the next candidate; do not force the user to uninstall v33 when a side-by-side package can be used.
8. Continue from a phone-only workflow because the user has no laptop.

## Status

- v33: user confirmed the built-in debug menu opens, but the table remains small and is not the full catalog.
- v34 SIGNFIX: the APK v2 signing structure was corrected. The next device error was an update-signature mismatch because v33 is already installed as com.shinybox.dqv30 with a different certificate.
- v34 PARALLEL: built as com.shinybox.dqv34 so it can install side-by-side and preserve v33 app data. All 20 split package IDs match the XAPK manifest. Local APK v2 structure/digest/RSA checks, inner/outer ZIP CRCs, and 16-KiB native-library alignment passed. Device runtime remains untested.
- Workbench v35: contains all 222 catalog entries and 14 categories, a button-built keypad for custom Gold draft input, and -10/-1/+1/+10 steppers for other numeric draft fields. Browser tests passed. It explicitly remains disconnected from the game.
- The actual in-game Set Gold callback, keyboard launch, and balance update remain unverified. The 222-entry catalog is not fully connected to game handlers.

## Next verification

Install the v34 PARALLEL XAPK alongside v33, then open Options -> Cheat Menu -> Add -> Set Gold. Record whether the game keyboard opens, whether a value can be confirmed, and whether Gold changes. Keep the original store app com.shinybox.smash untouched.

Do not mark the Gold input or the full 222-cheat implementation as complete until device behavior proves it. Each cheat needs a known handler, argument contract, state read-back, and safe recovery behavior before it is enabled.


## Latest installability correction — v34 PARALLEL LABEL

The user's screenshot confirmed `INSTALL_FAILED_UPDATE_INCOMPATIBLE` because the existing v33 package has a different certificate. The latest deliverable is `Dungeon_Quest_3.3.2.0_CheatMenu_SetGoldKeyboardProbe_v34_PARALLEL_LABEL.xapk`, package ID `com.shinybox.dqv34`, Android launcher label `DQ Test Build`, SHA-256 `28ec36842de60cc3333dadc263745d8488c2c780cb058ce6e000a36a46077174`, size 57,571,134 bytes. All 20 inner manifest package IDs, XAPK metadata, signer identity, inner/outer CRCs and local v2 signature verification were independently rechecked. Install beside v33; do not uninstall v33 or the store app. Keyboard and runtime effect remain pending.

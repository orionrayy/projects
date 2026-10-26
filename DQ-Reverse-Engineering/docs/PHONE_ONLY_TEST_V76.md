# DQ v76 — phone-only startup isolation

This is a diagnostic comparator, not a feature-complete mod. It restores the exact official assets/S3DMain.smf so the modified v50-derived pause HUD can be isolated as one possible cause of the v75 force-close.

1. Keep the official Dungeon Quest app and its save data installed and untouched.
2. Install DQ v76 Tester as a separate app. Its package ID is com.shinybox.dqv76 and it uses a local diagnostic signature.
3. Launch the tester once, preferably offline. Do not tap any Gold/cheat controls; this build does not validate those features.
4. Report whether it opens to the title/menu or force-closes. If it force-closes, note whether it happens immediately or after a visible logo/loading screen.

Interpretation:
- If v76 opens, the modified v50-derived HUD/STK payload becomes the leading suspect. Reintroduce that change only after verifying the baseline.
- If v76 also force-closes, the HUD payload alone does not explain the failure; next isolate package/signature/provider initialization and native startup using a phone-side crash trace.

No physical-device runtime test has been performed by the build environment. Do not uninstall the official app, erase its storage, or replace its saved data.

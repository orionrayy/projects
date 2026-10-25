# Pause → Options one-row Gold action candidate — v50

**Status:** data-level candidate rebuilt and validated as a separate STK; not runtime-verified, and no APK was built.

## What changed

The existing Pause → Options → Gameplay screen has an unused right-hand slot beside the existing Pickup button in the bottom visible row. The candidate builder clones that existing button record, changes its label to Gold +100K, and attaches a new serialized action with the same direct uai_gp_hud.onDebug(6.0) call shape already used by stock debug.hud actions. Static native disassembly associates command 6.0 with RewardGold(100000.0). No new AIM handler is invented.

The change is confined to Resources/HUD/pause.hud: 126 → 127 elements and 64 → 65 action records. Button position is x=+0.66, y=-0.70, paired with the existing Pickup control at x=-0.66, y=-0.70. The candidate HUD re-parses and verifies its group, label, callback name and action payload.

## Local verification

- Source pause.hud SHA-256: 12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395
- Candidate pause.hud SHA-256: 785ec813d316a833805ea7fe2c24ad8b3460774d978a07c6e065559a4a33c7af
- Source STK SHA-256: 340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3
- Candidate STK SHA-256: e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e
- Candidate STK size: 34,011,446 bytes
- Independent source-vs-candidate decode: PASS; 5,630/5,630 entries validate and exactly one entry differs, Resources/HUD/pause.hud. All other decoded entries are identical.
- Local combined tests: 28 passed, including five v50 builder tests with synthetic HUD input.

Local candidate artifacts:
- /mnt/data/dqwork/candidates/pause_options_gold_row_v50.hud
- /mnt/data/dqwork/candidates/S3DMain_pause_options_gold_v50.smf
- /mnt/data/dqwork/candidates/S3DMain_pause_options_gold_v50.delta.json

## Limits and next gate

This proves only that the serialized HUD action and outer asset archive rebuild consistently. Actual button visibility, click dispatch, Gold balance mutation, failure behaviour and persistence require loading the candidate in the exact target game build. The candidate is not an installable APK. It does not add the 222-row list, selection callback or stable-ID cheat dispatcher. Keep runtime-verified count at zero until on-device evidence exists.

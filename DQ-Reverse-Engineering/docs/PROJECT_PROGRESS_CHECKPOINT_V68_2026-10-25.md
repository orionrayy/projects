# Dungeon Quest checkpoint v68 — actual package recheck

Date: 25 October 2026 (WIB)
Repository: \`orionrayy/projects\`
Branch: \`feat/dq-iap-debug-cheats-modkit-v7\`
PR: #26 (open, draft, unmerged)
Previous engineering checkpoint: v67.

## Completed in this increment

1. Independently materialized and rechecked the real stock XAPK, v50 candidate XAPK and v50 standalone ARM64 candidate APK.
2. Confirmed exact package identity and split inventory: \`com.shinybox.smash\`, version \`3.3.2.0\`, 20 split APKs in both XAPKs, outer/inner ZIP CRC passes.
3. Compared all non-signing APK payload members: only the base split's \`assets/S3DMain.smf\` differs. Base and standalone candidate classes.dex match the pinned source DEX hash. Standalone STK equals candidate XAPK STK; ARM64 native libraries equal the packaged ARM64 split.
4. Decoded all 5,630 STK entries, validating stored CRC and decoded size. Exactly \`Resources/HUD/pause.hud\` differs among decoded assets.
5. Added a fail-closed actual-package audit tool, seven synthetic regression tests, CI workflow and actual-file summary report. Workflow run [40206936967](https://github.com/orionrayy/projects/actions/runs/40206936967) passed both the new synthetic regression suite and the existing STK delta suite.
6. The preceding v67 source-only DEX lifecycle patcher remains source-only. Its separate workflow [40206173884](https://github.com/orionrayy/projects/actions/runs/40206173884) passed 9/9 Python tests and the synthetic smali assemble/re-disassemble check.

## What the evidence means

The package and asset provenance is reproducible. The v50 candidate changes one decoded HUD resource and retains the same DEX and native libraries; its locally generated signing certificate differs from the official-signed source package. An in-place update is therefore expected to be rejected by Android signing policy.

## Still blocked — do not report as finished

- No original-game APK/XAPK has been verified to install and launch from the current candidate.
- The Gold +100K HUD callback is static candidate wiring only; no tap/value/save test has passed.
- The standalone harness remains disconnected from game state.
- The catalog remains 0/222 integrated native routes and 0/222 runtime-verified gameplay effects.
- No verified backup-and-restore gate or crash-free save/reload evidence exists.
- Official apksigner v2/v3 verification and target-game ARM64 runtime verification remain outstanding.

## Next controlled steps

1. Keep both source packages and the official installation untouched.
2. Obtain a clean, disposable test profile and an approved route for target-game runtime observation (or run the isolated target APK on an explicitly disposable device/emulator with full log capture).
3. First test the unmodified control; then test the candidate using its own distinct package ID so signer incompatibility does not confound results. Do not bypass license or integrity checks if the candidate refuses to run.
4. Require evidence for every gate: install, launch, visible button, tap callback, exact +100,000 delta, shutdown/restart, save/reload, recovery, and regression/no crash.
5. Only after the single action succeeds should the engine List/selection/typed adapter path be implemented and measured one stable catalog ID at a time. Do not expose unverified effects as functional cheats.

No new game APK was built in v68.

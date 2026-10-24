# DQ Modkit — Synchronization and Verification Status v14

Date: 2026-10-24  
Branch: `feat/dq-iap-debug-cheats-modkit-v7`  
PR: [#26](https://github.com/orionrayy/projects/pull/26), open draft at time of authoring.

## v14 additions

- `tools/audit_aim_hud_symbols.py` scans seven selected extracted AIM/HUD files for expected printable ASCII symbol/label strings.
- `tests/test_aim_hud_symbols.py` tests byte offsets, run-length validation, missing-file reporting, missing-symbol reporting, and a complete synthetic fixture tree.
- `docs/AIM_HUD_SYMBOL_AUDIT_V14.md` records evidence, hashes, limitations, and reproduction steps.
- `.github/workflows/dq-reverse-validation.yml` now executes the v14 focused test suite.

The tool intentionally does not claim to disassemble proprietary bytecode. It reports only the first printable-byte offset for each requested symbol and fails non-zero if a target asset or expected symbol is missing.

## Local decoded-asset cross-check

The current locally decoded STK asset pack contains all seven expected paths, and a static printable-ASCII scan found all 58 configured target strings. The per-file sizes and SHA-256 values are recorded in the v14 audit report. Selected results:

| Asset | Size | SHA-256 |
|---|---:|---|
| `InAppPurchase.aim` | 448 B | `010d69cafbd0f80ceb8b218b79aa0d45b51f62df3345910c5568931e9b308f96` |
| `uai_gp_options.aim` | 1,127 B | `294dc84260b1a58dcbf6cf8fe939c107e8c0ae2bacc7ffe11b34ac62a54b5625` |
| `uai_gp_debug.aim` | 566 B | `e41094fd055ca250f282862e383506c3a0fb04c2bb3e2f09d7e139e51570bd59` |
| `uai_gp_hud.aim` | 13,929 B | `66607a46a23eeaab4fa2dac02772adbea5ab71e65d4e446e49396c6af6a451cb` |
| `uai_gp_account.aim` | 4,373 B | `83e18900dff8b80024befc891f1c412aeab4faa8041b4e97013d118426559676` |
| `pause.hud` | 29,446 B | `12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395` |
| `debug.hud` | 12,887 B | `02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6` |

This is a local content check of the decoded asset pack, separate from GitHub CI's synthetic-fixture tests.

## Current IAP status

The v13 matrix contains 109 distinct identifiers: 107 IAP XML identifiers, 104 DEX static SKU literals, 102 shared, five XML-only, and two DEX-only. All 109 products remain runtime-reward-unverified because the result callback bodies are native declarations without DEX implementation bodies, the matching native split set is still missing, and no per-SKU before/after state transition was observed.

The 46 numeric-suffix Vanity asset correlations remain asset-level matches only. The `uai_gp_debug.aim` symbols indicate shader/log diagnostic surface; the separate `debug.hud` has test-control labels. Neither proves the debug HUD is reachable in the release build.

## Validation boundaries and next artifact

The v13 workflow run `40084301017` succeeded on the prior v13 code/doc revision. The v14-updated workflow then completed successfully on commit `1cad7db30de3b712d6792b88da2094f038950ea3` in [run 40084702210](https://github.com/orionrayy/projects/actions/runs/40084702210/job/120845131799). Its v14 AIM/HUD symbol-audit test step passed, as did the v13 evidence tests, existing regression tests, manifest/source-boundary checks, and temporary-stub Java compilation. The run uses synthetic fixtures for v14 tests; it does not assert binary hashes against a live Android installation.

The tracked repo remains a curated analysis workspace; it still lacks all 68 app-specific `.smali` files, 68 generated Java declaration scaffolds, a full decoded manifest/resource set, and native engine libraries. The base APK had no `lib/*.so`, while the manifest excerpt declares required ABI/density splits. A matching version/signature/ABI XAPK/APKS set and its ELF dependencies remain unverified. A drop-in engine replacement is still a large port, not a placeholder-library patch.

Next required external artifact: the matching authorized version 3.3.2.0 split set. Until native grant logic and persisted state are directly evidenced, do not classify any SKU reward as verified.

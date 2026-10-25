# AIM/HUD Symbol Inventory — v14

Date: 2026-10-24  
Target build: Dungeon Quest `com.shinybox.smash` v3.3.2.0.

## Why this audit exists

The DEX contains native IAP result declarations, while the decoded proprietary `.aim` and `.hud` assets expose symbol/label names but are not yet fully disassembled. This audit records repeatable byte offsets, file sizes, and SHA-256 hashes for seven selected assets. It prevents repeated manual string searches from being presented as call-graph reconstruction.

## Observed symbols in the analyzed decoded asset set

| Asset | Size | SHA-256 | Selected symbols observed |
|---|---:|---|---|
| `Resources/AIModels/InAppPurchase.aim` | 448 B | `010d69cafbd0f80ceb8b218b79aa0d45b51f62df3345910c5568931e9b308f96` | `onPurchaseSuccess`, `onPurchaseFailed`, `onPurchaseRefunded`, `onRequestPurchase`, `onRestorePurchases` |
| `Resources/AIModels/uai_gp_options.aim` | 1,127 B | `294dc84260b1a58dcbf6cf8fe939c107e8c0ae2bacc7ffe11b34ac62a54b5625` | `onLoadOptions`, `onSaveOptions`, `onShowOptions`, `onSetControlsOption`, `onSetGameplayOption` |
| `Resources/AIModels/uai_gp_debug.aim` | 566 B | `e41094fd055ca250f282862e383506c3a0fb04c2bb3e2f09d7e139e51570bd59` | `CompileShaderList`, `CompileShaders`, `onDebugLog`, `onDumpFailedShaders` |
| `Resources/AIModels/uai_gp_hud.aim` | 13,929 B | `66607a46a23eeaab4fa2dac02772adbea5ab71e65d4e446e49396c6af6a451cb` | `bPurchasing`, `sPurchaseID`, `onPurchaseSuccess`, `onPurchaseFailed` |
| `Resources/AIModels/uai_gp_account.aim` | 4,373 B | `83e18900dff8b80024befc891f1c412aeab4faa8041b4e97013d118426559676` | `SetIAP`, `GetIAPString`, `SetSlotInfo`, `SetStashInfo` |
| `Resources/HUD/pause.hud` | 29,446 B | `12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395` | `options`, `onOptionsClose`, `onResume` |
| `Resources/HUD/debug.hud` | 12,887 B | `02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6` | `onAddBattle`, `onCreateCS`, `onAddLevel`, `onCreateFeat`, `GOTO Floor` |

The complete expected-symbol lists are defined in `tools/audit_aim_hud_symbols.py`; its output reports every requested symbol's first printable-byte offset. A [machine-readable v14 snapshot](AIM_HUD_SYMBOL_AUDIT_V14.json) records the locally cross-checked sizes, hashes, and all 58 offsets. These hashes are from the decoded assets used for this analysis. Re-run the tool against the asset tree actually being studied rather than relying on names alone.

## Reproduction

From the repository root:

```bash
cd DQ-Reverse-Engineering
python tools/audit_aim_hud_symbols.py /path/to/extracted/stk/assets --output-json /tmp/dq-aim-hud-symbol-audit.json
python -m unittest discover -s tests -p 'test_aim_hud_symbols.py' -v
```

The input root must contain `Resources/AIModels/` and `Resources/HUD/` with the extracted assets. The audit exits non-zero if any target file or required symbol is missing. Tests use synthetic fixtures; CI confirms parser and fail-closed behavior, not these binary hashes by itself.

## Interpretation limits

- The purchase/restore names show symbol strings exist; they do not prove that a purchase event reaches the named handler.
- The options symbols and pause HUD labels are consistent with an options UI path, but do not prove that all settings callbacks are connected or persisted.
- `uai_gp_debug.aim` exposes shader/log diagnostic symbols. Separately, `debug.hud` has visible test-control labels such as `Add Levels`, `Add Feat`, and `GOTO Floor`. Asset presence does not prove this HUD is reachable in the release build.
- No symbol string proves a reward payload, entitlement write, billing verification, or native call edge. The 109 SKU rewards remain unverified until matching native split/source evidence and controlled runtime state diffs are available.

# HUD action stream audit — v45

**Scope:** read-only reconstruction of version-12 HUD action-section framing for the supplied Dungeon Quest 3.3.2.0 resources. This is a parser/forensics checkpoint, not a gameplay patch.

## Findings

- All **68/68** source HUD resources pass the v42 field-preserving HUD parser and the v45 action-section framing parser.
- Across these files, the action table contains **1,232 named action records** and **2,538 length-prefixed statement payloads**. The two-byte value after each action name matches the statement count; each record ends in a zero-length terminator. All action sections are consumed exactly, with no residual bytes.
- The parser does not execute or rewrite action bytecode. It records decoded text payloads and conservatively extracts length-tagged literal values such as AI model names and symbol names.
- Among **743 candidate references** to AIM model names in the HUD action payloads, **715** target strings match a symbol name in that model’s decoded AIM metadata; **28** do not match the exposed variable/function/state/handler name tables. These are unresolved cross-references, not proven malformed calls; this inventory does not establish whether they are provided by native/AOT code or a distinct engine route.

## Debug HUD: one-row candidate

Resources/HUD/debug.hud has **13 action records** and no type-3 List element. Its existing UI routes include:

| HUD action | AIM route | Static argument |
|---|---|---:|
| onGotoLevel | uai_gp_hud.onDebug | 2.0 |
| onSetBoss | uai_gp_hud.onDebug | 3.0 |
| onSetLevel | uai_gp_hud.onDebug | 4.0 |
| onCreateLegend | uai_gp_hud.onDebug | 8.0 |
| onCreateMS | uai_gp_hud.onDebug | 9.0 |
| onCreateCS | uai_gp_hud.onDebug | 10.0 |
| onAddLevel | uai_gp_hud.onDebug | 11.0 |
| onAddHeroic | uai_gp_hud.onDebug | 12.0 |
| onCreateFeat | uai_gp_hud.onDebug | 13.0 |
| onSetCrystal | uai_gp_hud.onDebug | 14.0 |
| onSetEternal | uai_gp_hud.onDebug | 15.0 |
| onAddBattle | uai_gp_hud.onDebug | 16.0 |

The existing static disassembly audit (v43) identifies a separate uai_gp_hud.onDebug(6.0) branch calling RewardGold(100000.0). Argument 6.0 is not among the serialized action calls in debug.hud. This gives a narrow candidate for a fixed +100,000 Gold sandbox action that could be exposed through the existing debug route. It is **not runtime-verified**; this audit has not changed the HUD or APK.

## What this does not prove

The parser validates action framing and cross-references only. It does not infer full action-opcode semantics, confirm that each referenced native symbol is callable, establish persistence, or demonstrate runtime effects. It does not solve generic List selection callbacks, stable cheat-ID mapping, or the 222-entry menu. The HUD codec and this action parser can be combined for a controlled one-row test, but the original APK should not be replaced until the patched STK is independently validated and the resulting app is tested.

## Reproduce

    python -m py_compile tools/hud_action_probe_v45.py tests/test_hud_action_probe_v45.py
    python -m unittest discover -s tests -p 'test_hud_action_probe_v45.py' -v

The seven local tests include two optional assertions against extracted source assets; set DQ_SOURCE_ASSETS to the extracted asset root to enable them. In CI those two source-asset checks are skipped because raw game assets are intentionally excluded from the repository.

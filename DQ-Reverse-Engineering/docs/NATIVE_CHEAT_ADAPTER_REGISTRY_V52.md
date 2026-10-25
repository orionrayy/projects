# Native cheat adapter registry — v52

**Status: adapter gate implemented; original-game integration remains 0/222.**

This registry makes the evidence threshold explicit. It separates three different things that must not be conflated: a catalog setting specification, a static native-handler candidate, and a runtime-verified game-side integration.

## Current state

| Metric | Count |
|---|---:|
| Catalog items | 222 |
| Native routes assigned to catalog IDs | 0 |
| Catalog routes runtime-verified | 0 |
| Separate native candidate actions | 1 |
| Candidate actions runtime-verified | 0 |
| Catalog IDs still requiring a verified adapter | 222 |

The current catalog still has all 222 entries marked `requires_game_adapter`. The standalone Android harness stages local drafts only and is not an API into the game's native state.

## The one separate candidate

`native.pause.gold_reward_100k` routes the candidate pause HUD button to `uai_gp_hud.onDebug(6.0)`. Static ARM64 disassembly associates that branch with `uai_gp_hud::RewardGold(100000.0)`; the modified STK passes structural validation and changes only `Resources/HUD/pause.hud`.

This candidate deliberately has no `catalog_id`: it is a fixed `+100,000` Gold action and does not implement the catalog slider's “Debug Gold Balance” set-to-target behavior. It remains `candidate_unverified` until the button is observed in a running game, the exact currency delta is read back, and save/reload plus regression checks pass.

## Gate semantics

`validate_native_cheat_adapter_registry_v52.py` fails closed when:
- a route references an unknown or duplicate stable ID;
- a runtime-verified route lacks a typed handler contract;
- runtime evidence lacks an exact-effect read-back, save/reload result, regression result, build/candidate hashes, or evidence artifact;
- summary counts drift from the underlying registry;
- a fixed Gold reward is incorrectly mapped to the currency-override slider.

Run from `DQ-Reverse-Engineering/`:

```bash
python tools/validate_native_cheat_adapter_registry_v52.py
python -m unittest discover -s tests -p 'test_native_cheat_adapter_registry_v52.py' -v
```

## What this does not claim

The registry is integration infrastructure, not a runtime bridge. It neither writes game memory nor adds native model code. Generic List population, stable-ID selection dispatch, native handler contracts, in-game effect verification, and safe save persistence remain open gates. This prevents a UI control from being presented as a functioning cheat merely because a related symbol exists in the binary.

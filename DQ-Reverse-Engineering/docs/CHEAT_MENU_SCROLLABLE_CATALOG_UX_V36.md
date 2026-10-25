# Scrollable Cheat Menu UX specification — v36

Date: 2026-10-25  
Scope: finish the requested UI/catalog design before any new Android package build. **No APK/XAPK is built in this increment.**

## User-approved requirements collected since the v33 baseline

- Preserve the working v33 installation while iterating.
- Keep the expanded catalogue within one Cheat Menu rather than scattering Gold into a separate tab.
- Show all 222 stable-ID entries in 14 categories, with an internally scrollable list.
- Make the UI specific and less ambiguous: title, stable ID, description, category, risk, staged state, details, tags and explicit adapter status.
- No ordinary editable numeric fields that require the Android keyboard.
- Numeric settings use four increment/decrement buttons: `−10`, `−1`, `+1`, `+10`, scaled by the catalogue step and clamped to min/max. Range controls have the same four controls for both bounds and enforce min ≤ max.
- Gold has a custom amount editor with a button-built on-screen numeric keypad. This deliberately avoids depending on the system keyboard; Apply only stages a local draft in the workbench.
- Search, risk filter, favourites, category filter, changed/active/blocked views, presets, undo, reset, export and event log remain available.
- Never describe local draft changes as live game effects. Unmapped game handlers remain blocked.

## Workbench artifact

Local single-file preview: `Dungeon_Quest_Cheats_Sandbox_Workbench_v36_SCROLLABLE.html`  
SHA-256: `8bf8d37347563854104484f1b7cd58efda270aadaad0a0ae70f61dda2cea6f81`  
Size: 131,617 bytes.

The viewport is fixed to the app window. The header, search controls, category rail, active filters and action dock remain visible; the 222-card list scrolls in its own `#cheatScroll` region. Scroll position is retained after staging changes and reset when filters change. On mobile the cards use one column; landscape/desktop uses two or three columns depending on width.

## Catalogue by category

| Category | Count |
|---|---:|
| Player & Survival | 27 |
| Combat Lab | 24 |
| Enemy AI | 20 |
| Loot & RNG | 19 |
| Economy Lab | 17 |
| Progression Lab | 16 |
| Inventory & Gear | 16 |
| Spawn & Encounter Lab | 9 |
| World & Physics | 22 |
| Camera & Visuals | 15 |
| UI & Accessibility | 3 |
| Skills Lab | 9 |
| Gear & Stats Lab | 7 |
| Debug Tools | 18 |
| **Total** | **222** |

All 222 stable IDs are unique.

## Browser QA results

| Viewport | Rendered entries | Outer document scroll | Internal list scroll | Gold keypad | Numeric stepper | JS errors |
|---|---:|---|---|---|---|---:|
| 430 × 900 (mobile portrait) | 222 | none; body/document equal viewport height | PASS | `123` staged exactly; input is read-only with `inputmode=none` | 1 → 3.5 with +10 on a 0.25-step value | 0 |
| 1536 × 675 (landscape) | 222 | none; body/document equal viewport height | PASS | `123` staged exactly | 1 → 3.5 with +10 on a 0.25-step value | 0 |

Measured internal list dimensions:
- Mobile: viewport 900 px, list viewport 315 px, list content 52,057 px.
- Landscape: viewport 675 px, list viewport 268 px, list content 17,735 px.

Filtering to one stable ID returns one card; clearing filters restores all 222. No JavaScript page errors were emitted in the tested interactions.

## Explicit integration boundary

v36 is a UX/catalog prototype, not an injected in-game menu. It says `GAME LINK: DISCONNECTED` because values are local staging only. The original game still opens the built-in Debug HUD via the working v31/v33 route; the 222-row full catalogue has not been serialized into the game's HUD. The proprietary HUD element format, custom Gold keyboard/commit chain, and per-setting native game state adapters must be validated before a new XAPK build.

The immediate next gate is an agreed 222-entry UI layout and per-ID implementation registry; after that, validate the proprietary HUD parser/serializer and integrate one reversible handler group at a time. Do not build another APK until this UI/design gate is completed and the custom Gold route has a known implementation contract.

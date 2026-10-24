# HUD Binary Format Audit v19 — Pause → Options → Debug Route

**Evidence date:** 2026-10-24  
**Target:** Dungeon Quest Android `com.shinybox.smash`, version `3.3.2.0`, version code `1423433200`  
**Classification:** static binary evidence and read-only parser verification. No original HUD bytes were modified.

## Source assets and identity

| Asset | Size | SHA-256 |
|---|---:|---|
| `Resources/HUD/pause.hud` | 29,446 bytes | `12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395` |
| `Resources/HUD/debug.hud` | 12,887 bytes | `02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6` |

Both entries were extracted from the source asset archive in the analysis bundle. Their SHA-256 values match the previously recorded asset inventory.

## Confirmed top-level .hud layout

The read-only probe validates this layout for both resources:

1. A 4-byte little-endian marker length, value 3.
2. Three marker bytes, `NcP`.
3. A one-byte format version, value 12.
4. Four sections in fixed order. Each section has a 4-byte little-endian payload byte length followed by that many bytes: general attributes, elements, actions, timers.
5. No trailing bytes after the timer section.

| Section | `pause.hud` payload size | `debug.hud` payload size |
|---|---:|---:|
| General attributes | 4 | 4 |
| Elements | 22,650 | 11,864 |
| Actions | 6,766 | 993 |
| Timers | 2 | 2 |
| Total file size | 29,446 | 12,887 |

The general-attributes payload is a length-prefixed initial-action string (empty in both files). The elements section starts with a 32-bit element count: 126 for Pause and 71 for Debug. The timer section starts with a 16-bit timer count; both are zero. Element records remain opaque in the probe and must not be reserialized by it.

For version 12, the action section begins with a 16-bit action count; each record contains a length-prefixed action name, a 16-bit parameter count, length-prefixed parameter strings, then one extra length-prefixed script string. The source-level parser validates complete section bounds and the full action table without altering the input.

## Action-route findings

### Pause HUD

- 64 action records were parsed.
- The existing `onShowOptions` action has four parameters: call `uai_gp_options.onShowOptions`, set `pause=0`, set `options=1`, and invoke the `onShowGameplay` action.
- The existing `onShowPause` action sets `pause=1` and `options=0`.
- The existing `onOptionsClose` action invokes `uai_gp_options.onSaveOptions`.
- The Pause action table contains no action name with “debug” and no explicit call to `uai_gp_debug`.

### Debug HUD

- 13 action records were parsed.
- Every listed handler delegates to `uai_gp_hud.onDebug` with an integer-like parameter encoded in the action script.
- Observed mappings include `onClose → 1`, `onGotoLevel → 2`, `onSetBoss → 3`, `onSetLevel → 4`, `onCreateLegend → 8`, `onCreateMS → 9`, `onCreateCS → 10`, `onAddLevel → 11`, `onAddHeroic → 12`, `onCreateFeat → 13`, `onSetCrystal → 14`, `onSetEternal → 15`, and `onAddBattle → 16`.
- These handlers are evidence of pre-existing debug commands, not proof that the Debug HUD can be opened from Pause → Options at runtime.

## Tooling and validation

- `tools/hud_asset_probe.py` parses the header, the four section boundaries, action names/parameters, and record counts read-only.
- `tests/test_hud_asset_probe.py` covers synthetic version-12 and legacy-version-8 inputs, malformed marker, truncation, trailing data, and malformed action records.
- The parser reports `rewrite_supported: false`; it does not claim to decode or serialize the 126/71 element records.
- The synthetic regression suite passed locally against the workspace copy. CI has been wired to run the corresponding test script. The exact GitHub Actions result must be checked separately before claiming CI validation passed.

## Integration decision

**The real Pause → Options → Cheats route remains blocked.** The existing Options action opens the existing Options model; the static action table has no demonstrated transition into the Debug HUD. A correct menu integration still needs the exact element record structure (including interactive hit-target semantics), a format-correct serializer, round-trip preservation of every non-target record, and an in-game ARM64 runtime test.

The next safe milestone is to decode and test the element record variants needed for one small Options-row addition, with a round-trip test against both untouched HUD files before emitting any modified resource. Until then, no byte-level edit is made. The standalone harness remains a separate app, not a Dungeon Quest mod APK.

Billing receipts/entitlements, cloud progression, leaderboard state and achievement submissions are not changed by this audit.

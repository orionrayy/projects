# Dungeon Quest v50 runtime gate — v55

**Current result: BLOCKED / NOT RUN on the original game runtime.** The harness emulator test does not count as a game-candidate test because the harness deliberately shows GAME LINK · DISCONNECTED.

## Pinned candidate identity

| Item | Expected identity |
|---|---|
| Package / version | com.shinybox.smash / 3.3.2.0 |
| Standalone ARM64 APK SHA-256 | f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa |
| Split XAPK SHA-256 | 680dd37d23c6ea6ee318e5d08c82dca7cee8bb82e6a8baae75ed7912710c6430 |
| Candidate STK SHA-256 | e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e |

The package uses a local test certificate. **Do not uninstall or overwrite the official-signed app to test it.** Use a clean, isolated ARM64 emulator/device and a disposable offline profile. Do not copy personal or production save data into it. If licensing, integrity, or network checks prevent a launch, record that result and stop; do not bypass them.

## Device test sequence

1. Verify the candidate file SHA-256 against the pinned identity above. Record emulator/physical model and Android API level.
2. Prove the disposable profile is offline. Verify a backup can be restored before testing any game-state mutation. Do not store raw save files in this repository.
3. Install as a clean test install; capture the Package Manager result. Launch and capture the initial screen. If installation or launch fails, record it as a failed check rather than treating static package validation as a pass.
4. Open Pause → Options → Gameplay. Record whether the intended Gold +100K button is visible and its touch target is usable.
5. Record Gold before the tap, tap once, and record Gold after. The required delta is exactly +100000, not merely a visual toast or the presence of the button.
6. Save, reload the same disposable profile, and record the reloaded balance. It must equal the post-action balance. Capture crash/logcat evidence and run a brief regression check of pause/resume and normal gameplay.
7. Put redacted screenshots/logs under a local evidence directory and create their SHA-256 entries in docs/GAME_CANDIDATE_RUNTIME_EVIDENCE_V55.json. Validate locally with the command below.

    python tools/validate_game_candidate_runtime_evidence_v55.py docs/GAME_CANDIDATE_RUNTIME_EVIDENCE_V55.json --evidence-root /path/to/local-redacted-evidence

Evidence paths in the JSON are relative to --evidence-root. Do not include save payloads, account IDs, tokens, or personal data. Only change the status to verified when every check, the exact currency delta, reload persistence, zero-crash result, and backup/restore proof pass and every required evidence file hash validates.

## Promotion rule

- blocked: no candidate runtime test has been performed.
- in_progress: evidence supports some checks, but none has failed and the full gate is not met.
- failed: at least one candidate runtime check failed. Keep the candidate quarantined and diagnose whether the fault is package install/startup, HUD rendering, touch/action dispatch, or state/save handling.
- verified: all nine checks pass, the exact +100,000 delta is observed, save/reload persists, crash count is zero, backup/restore is proven, and required evidence is available and hash-verified.

This gate only evaluates the single Gold +100K candidate. It does not mark any of the 222 catalogue entries as integrated. The 222-entry registry remains fail-closed until there is a separately verified in-engine row population/selection path and a typed, allow-listed adapter per stable ID.

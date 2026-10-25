# DR2C VORENYX — Start-Liveness Audit v2.59

**Result: no runtime root cause proven. Static route wiring is present; tutorial-load and package-integrity behavior remain unresolved. This is not a fix claim.**

Candidate: `DR2C_VORENYX_v2.57_SIGNATURE_FIX.apk`  
SHA-256: `a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7`

## Findings

1. The v2.57 signature-fix derivative has exactly the same Deathforth script payloads as v2.57; its edits are to signing/container bytes. It did not change Start dispatch, script initialization, or runtime state, so it could not repair the reported Start no-op.
2. Static comparison confirms `game-select.df`'s executable code skeleton and Forth symbol order match the supplied base. The required `main-event-do-select`, `select-start`, `select-boot`, `game-start-new`, and `main-event-new-session` words exist. `boot.df` still contains `"GAME-MARKER" $anew` and the final `"SIAP." print` marker.
3. The initial `select-boot` route loads `events/tutorial.df` when `tutorial-done` is false. The candidate tutorial file is not an exact executable-token skeleton match with the base: four `chim` expression references were changed to `cname`, and two outcomes removed `bHe`/`bhim`/`bhe` pronoun-expression tokens. Handler IDs (`tutorchat-1/2/3`) and the ordered single-quoted Forth symbol stream remain intact. This is a concrete area for focused interpreter/runtime verification, not proof of a syntax fault.
4. The package keeps PairIP/licensing native libraries identical to the base but is repackaged and locally signed with a different certificate. A native integrity/licensing check blocking the game-state transition remains a possible alternative; no security or license bypass was attempted.

## Verification gaps

- No Android device, ADB, emulator, official `apksigner`, or Deathforth runtime is available in this build environment.
- There is no device logcat/runtime exception to identify whether `select-boot` entered, tutorial loading failed, or native integrity blocked the event.
- No hitbox/Start-trigger rewrite is proposed, because the static evidence does not point to the trigger definition itself.

## Next engineering gate

Do not call the game stable and do not send another blind release candidate. The next test must isolate the `select-boot` → `events/tutorial.df` load path or obtain the device's runtime error. Keep PairIP/licensing unchanged. See the JSON companion for machine-readable checks.

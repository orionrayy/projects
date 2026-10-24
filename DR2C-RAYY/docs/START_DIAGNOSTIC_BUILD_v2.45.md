# DR2C VORENYX v2.45 — Start Diagnostic Build

**Purpose:** separate native tap/callback failure from a missing Deathforth select handler or a stall inside `select-boot`. This is a diagnostic APK with console output enabled; it is not a release build.

## Artifact

- File: `DR2C_VORENYX_v2.45_STARTDIAG_TEST.apk`
- Size: 112,238,856 bytes
- SHA-256: `0bdb268aa1da2d70188f3a291f1c0591a195266fa3edec3376c86ca83527c26c`
- Package: `com.noodlecake.drtc`
- Uses the same local test certificate as the previous parsefix candidate.
- ZIP CRC: PASS; 1,005 entries; zero duplicate paths.
- Stored entries: all meet required alignment; `resources.arsc` 4-byte aligned; seven native `.so` 4-KiB aligned.
- JAR/v1 signature: PASS. APK v2 signature and content digest: PASS using local verification code.
- Target device install: NOT RUN; verifier is not Google's official `apksigner`.

## Instrumentation added

- Forces the engine console visible.
- Emits checkpoint messages through the boot sequence after core modules, after the select handler file, at end of boot, and after `transcheck` / `check-stack-empty`.
- Logs when the `MAIN_EVENT_DO_SELECT` event reaches `main-handler`.
- Logs entry and returns around save loading and mode-definition loading in `select-boot`, plus whether the tutorial-complete branch or tutorial-region-loading path is selected.

## How to interpret the last visible message

- No `VORENYX-DIAG: BOOT COMPLETE`: bootstrap stopped or aborted before completing. The last checkpoint narrows the module to inspect.
- `BOOT COMPLETE`, but tapping Start does not show `MAIN_EVENT_DO_SELECT DISPATCHED`: input/button callback or native event queue is not delivering the select event.
- `MAIN_EVENT_DO_SELECT DISPATCHED`, but no `SELECT-BOOT ENTERED`: event dispatch works, but the deferred `main-event-do-select` callback remains the no-op, so investigate script registration/load order.
- `SELECT-BOOT ENTERED`, but no `GSTATS LOAD RETURNED`: state/save loading is hanging or aborting.
- `GSTATS LOAD RETURNED`, but no `MODEDEFS RETURNED`: game-mode definition lookup is the next failing step.
- `TUTORIAL FLAG FALSE; QUEUE TUTORIAL LOAD`, but no `TUTORIAL LOAD RETURNED`: inspect tutorial region load / mission transition.
- `TUTORIAL FLAG TRUE; OPENING SELECT-CYOA`: the CYOA selection route should begin; if the visible screen does not change, inspect the CYOA screen/state renderer.

This log narrows the fault without assuming an asynchronous race. The device-side result is still required to identify which branch actually occurs.

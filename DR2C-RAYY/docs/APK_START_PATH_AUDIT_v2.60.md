# DR2C VORENYX — APK Start/Touch-Route Static Audit v2.60

**Date:** 25 October 2026  
**Result:** **BLOCKED_REVIEW_REQUIRED** — static audit only, not a runtime diagnosis.

## Artifacts compared

Base APK: DR2C-v1.8.2-full-apkvision.apk  
- Size: 109,011,456 bytes
- SHA-256: d4b509d899df572d80de553c8545c850ff2122c2d99fae5cfad2532159d35c15
- ZIP: 1,014 entries, CRC PASS, no duplicate paths

Candidate APK: DR2C_VORENYX_v2.57_SIGNATURE_FIX_REDELIVERED_20261025.apk  
- Size: 115,615,585 bytes
- SHA-256: a1f566d35b9b3cd7c5513cc72f19c5aca9e5fed881394df4c3ef66eb05a474a7
- ZIP: 1,015 entries, CRC PASS, no duplicate paths

## Findings

- All 12 critical Start/tutorial route scripts exist in both packages.
- 11 of 12 pass strict static checks for code skeleton, string closure, escaped quotes, required handler names and ordered Forth symbols.
- One file requires review: assets/deathforth/events/tutorial.df.
- Required Start-route words remain present, including main-event-do-select, select-start, select-boot and game-start-new.
- Tutorial handler IDs tutorchat-1, tutorchat-2 and tutorchat-3 remain present and ordered Forth symbol streams match.
- Canonical GAME-MARKER is present. No Deathforth .df file in the candidate contains a C/JSON-style escaped double-quote sequence.

### Tutorial drift requiring explicit review

The candidate has four display-expression identifier substitutions from chim to cname and removes bHe, bhim and bhe expression tokens in two rewritten outcomes. These might be intentional Indonesian display-expression rewrites, but static audit cannot assume they are safe. The tool labels this as REVIEW_CODE_DRIFT, not as a proven syntax defect or the confirmed reason Start is unresponsive.

The signature-only derivative does not modify the Deathforth script payloads, so it cannot itself fix script dispatch or tutorial-load behavior. A native integrity/licensing rejection after local re-signing also remains a possibility. PairIP/licensing code was not modified.

## Acceptance gate

1. Review display semantics and expression requirements for the tutorial token changes. Do not blindly restore English pronouns or make broad handler/hitbox edits.
2. Obtain a real device runtime trace that separates tap delivery, event dispatch, select-boot, tutorial load/compile, and native integrity/licensing outcomes.
3. Only after isolating the cause, make a narrow fix and revalidate package integrity, signatures and route contracts.
4. Test install, Start/new-game, tutorial, menus/events, UI fit and touch mapping, then save/load and repeat launch.
5. Keep README, memory, changelog and audit JSON synchronized to the exact candidate hash.

## Limitations

No Android device, ADB/logcat, emulator, official apksigner or embedded Deathforth VM was available in this audit environment. Therefore install, Start behavior, gameplay, UI fit, save/load and runtime stability remain NOT TESTED. This checkpoint is not release-ready.

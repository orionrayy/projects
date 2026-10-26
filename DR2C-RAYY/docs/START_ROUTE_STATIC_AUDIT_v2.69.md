# DR2C VORENYX — Start Route Static Audit v2.69

**Date:** 27 October 2026. Result: `STATIC_HANDLER_PRESENT_RUNTIME_REQUIRED`.

## Observed code path

1. `assets/deathforth/events.df` declares `main-event-do-select` as a deferred no-op. `main-handler` dispatches `MAIN_EVENT_DO_SELECT` to that deferred word.
2. `assets/deathforth/game-select.df` defines `select-boot`. The final `last to select-start` and `last to main-event-do-select` assignments bind the latest word to these deferred entries.
3. `select-boot` loads game statistics and mode definitions. If `tutorial-done` is true, it invokes `select-cyoa`; otherwise it disables delete-game, dispatches `MAIN_EVENT_NEW`, loads `events/tutorial.df`, and sets the tutorial as the mission.
4. `assets/deathforth/game-start.df` defines `game-start-new`, which calls `start-the-game`, requests a save, then applies an infection-mode-specific adjustment.

## Candidate comparison

- `events.df`: byte-identical to base.
- `game-select.df`: user-facing strings differ; normalized control-token stream matches base.
- `game-start.df`: normalized control-token stream matches base; byte differences are player-facing text.
- `boot-end.df`: normalized control-token stream matches base.
- `events/tutorial.df`: normalized code-token drift remains in translated choice/response expressions involving `chim`/`cname`, `bHe`, `bhim`, and `bhe`. Those rewrites appear intentional as static text composition, but Deathforth parser/runtime behavior has not been tested. This is a tutorial-local review item and is not proven to cause the first Start tap to fail.
- `boot.df`: the added `id-name-localize` helper is referenced by trait/perk UI paths in `charstats-textfill.df`, `events/4jerksmode.df`, `events/inner/region/scepter-range.df`, `events/trade/camp-recruit.df`, `events/trade/familiar-recruit.df`, and `events/unlock/perktrait.df`. Those call sites are outside the initial `select-boot` path; the helper is not a demonstrated cause of the unresponsive Start control.
- The v2.68 changes to the `fitness` display alias, camping-region optional include and two artwork assets do not alter the Start route's normalized control flow.

## Conclusion

No static comparison establishes why the installed v2.68 APK does not respond to Start. The central Start route is present and has the same normalized control-token sequence as the base. Rewriting the same handler again without runtime evidence would be speculative. Capture a trace during one tap to determine whether input dispatch reaches `select-boot`, whether `gstats`/`modedefs` completes, whether the tutorial region begins loading, or whether Android/native code reports an exception or abort.

## Runtime status

Android PackageManager installation succeeded according to the user's report. Start dispatch, script execution, tutorial load, gameplay, save/load and runtime stability remain unverified.

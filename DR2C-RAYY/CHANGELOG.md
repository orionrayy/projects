# Changelog — DR2C VORENYX

- **v0.1:** branding/title art, logo/splash staging and initial UI overlay.
- **v0.2–v0.3:** literal maps, NPC style matrix, slang research, identifier protections.
- **v0.4–v0.7:** contextual dialog/event passes, bandits/recruitment/classes, common5/common3 events and sentence-level QA.
- **v0.8:** trader-camp shared dialogue.
- **v0.9–v1.2:** weapon trader dialogue for firearms, pipe bombs, anime, blunt weapons, polearms and silent weapons.
- **v1.3:** QA repair; exact-literal/indentation corrections.
- **v1.4:** contextual event/training and oldtrade baseline.
- **v1.5–v1.6:** experimental oldtrade passes; later found to have reverted some v1.4 mappings in selected output.
- **v1.7:** shooting and fitness trainer text.
- **v1.8:** mechanical trainer and complete-line grammar fixes.
- **v1.9:** Army Surplus vendor.
- **v2.0:** Rifle Collector vendor.
- **v2.1 — current:** reconciled trainer/vendor output from the v1.4 baseline, including Blade Master. 187 rewrite hits, no static failures, display markers balanced 229/229, ZIP CRC PASS. Heuristic player-facing delta 32.22%.

## Release limitations
- Translation is not 100% complete.
- 32.22% is a heuristic literal-delta estimate, not semantic/screen coverage.
- Runtime/gameplay, save/load, and APK rebuild/signing have not been performed.
- Full-menu title background integration is not runtime-verified.
- Public repository intentionally excludes original APK and full extracted base-game scripts.

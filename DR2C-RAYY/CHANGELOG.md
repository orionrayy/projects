# Changelog — DR2C VORENYX

- **v0.1:** VORENYX title identity/artwork and initial UI overlay.
- **v0.2–v0.3:** literal maps, NPC style matrix, slang research and identifier protections.
- **v0.4–v0.7:** contextual event passes, bandits/recruitment/classes, common events and sentence-level QA.
- **v0.8:** trader-camp and campfire dialog.
- **v0.9–v1.2:** weapon vendors: firearms, pipe bombs, anime, blunt weapons, polearms and silent weapons.
- **v1.3:** exact-literal/indentation QA repair.
- **v1.4:** contextual events/training and oldtrade baseline.
- **v1.5–v1.6:** experimental oldtrade passes; some mappings reverted and later reconciled.
- **v1.7–v1.8:** shooting, fitness and mechanical trainer strings.
- **v1.9–v2.0:** Army Surplus and Rifle Collector.
- **v2.1:** reconciled trainer/vendor baseline including Blade Master; embedded ZIP report was subsequently found to retain two residue warnings that the working-folder report missed.
- **v2.2:** fixes 15 player-visible English literals in weapon traders; targeted residue scan 0 matches; display markers 157/157; embedded static PASS and ZIP CRC PASS. Coverage estimate: 32.36% (heuristic).

## Limits
Full Indonesian translation is incomplete. Coverage is a literal-delta heuristic. Runtime/gameplay, save/load, APK rebuild/signing and full title-menu integration are not yet tested. Public GitHub does not contain the original APK/full extracted game scripts.
- **v2.3 — contextual recruitment pass:** localized three recruitment/event scripts using exact quoted-literal matches; 410 mapping rules hit, 432 literal occurrences changed. Static QA and ZIP CRC PASS. Heuristic inventory delta 35.13%; full translation, runtime gameplay and save/load remain unverified.

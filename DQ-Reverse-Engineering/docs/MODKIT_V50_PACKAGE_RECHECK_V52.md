# ModKit v50 package recheck — v52

**Scope:** independently decoded source/candidate STK archives and inspected package containers. This is static evidence only; the modified Dungeon Quest candidate was not launched or tested in live gameplay.

## Archive verification

| Item | Result |
|---|---|
| Stock XAPK SHA-256 | `3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b` |
| Stock STK SHA-256 | `340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3` |
| Candidate STK SHA-256 | `e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e` |
| STK entries decoded and CRC/size validated | 5,630 / 5,630 |
| Changed decoded archive entries | Exactly one: `Resources/HUD/pause.hud` |
| Other decoded STK entries byte-identical | Yes |

## Gold +100K HUD candidate

The candidate `pause.hud` contains 127 elements and 65 actions, compared with 126 elements and 64 actions in the source. The new element is `gold_reward_100k_btn`, a Button in `GameplayMenu` with geometry `x=0.660, y=-0.700, w=1.000, h=0.300`. It mirrors the existing `pickup_btn` at `x=-0.660, y=-0.700`; this is a static geometry comparison, not proof of rendering or touch hit-testing.

The added action record is `onAddGold100K`, with the existing static call shape `uai_gp_hud.onDebug(6.0)`. Static ARM64 disassembly maps dispatch code `6.0` to `RewardGold(100000.0)`. This supports the intended route but does not prove the pause screen uses the edited HUD in the installed game or that the branch executes when the button is tapped.

## Built package checks

### ARM64 standalone APK

- File: `DQ_ModKit_v50_Gold100K_CANDIDATE_ARM64.apk` (local test output; not stored in this repository).
- Size: 57,085,374 bytes.
- SHA-256: `f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa`.
- ZIP CRC test and JAR/v1 signature verification: pass.
- Embedded `assets/S3DMain.smf` exactly matches the candidate STK hash above.
- Four ARM64 native libraries are stored uncompressed and 4,096-byte aligned.

### Split XAPK

- File: `DQ_ModKit_v50_Gold100K_CANDIDATE.xapk` (local test output; not stored in this repository).
- Package/version: `com.shinybox.smash` / `3.3.2.0`.
- Size: 57,623,091 bytes.
- SHA-256: `680dd37d23c6ea6ee318e5d08c82dca7cee8bb82e6a8baae75ed7912710c6430`.
- All 20 split APKs pass ZIP/CRC checks and JAR/v1 signature verification with the common local test certificate.
- Split list and `total_size` agree with the XAPK manifest.
- Compared with the source split set while ignoring re-created signature metadata, the only non-signature content change is the intended `assets/S3DMain.smf` replacement in `com.shinybox.smash.apk`.

## Separate Android harness result

The standalone Cheats Sandbox APK is a different package and is not a Dungeon Quest modification. GitHub Actions run [40186288008](https://github.com/orionrayy/projects/actions/runs/40186288008) passed catalog/JVM tests, `assembleDebug`, instrumentation, emulator installation, `MainActivity` launch and the visible `GAME LINK · DISCONNECTED` boundary. Its APK SHA-256 is `4cd90e232c6bdccc874dc23a9b92a13c755281d112647c1f931f4cad7cdae38d` (56,185 bytes). The catalog has 222 entries and 14 categories, all marked `requires_game_adapter`.

## Unresolved gates

- Modified Dungeon Quest candidate install/startup: **not verified**.
- Gold button visibility and touch dispatch in the original game: **not verified**.
- Observed currency mutation, save/reload persistence and save safety: **not verified**.
- Catalog cheats connected to the original game: **0/222**.

Both game packages use a locally generated test certificate, not the official signing key, and cannot update an official-signature install in place. Preserve the original app and save until a backup/restore path is independently verified. Do not treat archive/signature validation as runtime verification.
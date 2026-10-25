# DR2C VORENYX v2.45 — Deathforth quote-parse repair

## Confirmed from user's diagnostic screenshot

The runtime error is:

`ERROR: not found at " " "Dari " in INTERPRET on line 34`

Call trace ends at `events/common/common4.df`. The translated sentence on line 34 included backslash-escaped quotation marks around `Hei...`. The Deathforth parser uses raw double quotes as string delimiters and does not handle C/JSON-style `\"` escapes. Consequently the sentence's string boundary is parsed incorrectly, and the interpreter reports text as an unknown code token. This aborts loading an event module before the game is fully ready; the unresponsive Start control is a downstream symptom.

## Fix

Replaced all 24 `\"` sequences with single quotation marks inside the outer double-quoted text in six scripts:
- `events/common/common4.df`: 2 replacements
- `events/trade/trader-camp-region-special7.df`: 4
- `events/trade/trader-camp-region-special8.df`: 4
- `events/unlock/gnome.df`: 4
- `events/unlock/perk1.df`: 2
- `events/unlock/trait1.df`: 8

The APK was rebuilt from the existing diagnostic candidate with the same local test certificate. The six corrected script payloads match the corrected working overlay. A full scan of all 509 packaged `.df` files found zero remaining backslash-escaped double quotes.

## New diagnostic APK

- File: `DR2C_VORENYX_v2.45_STARTFIX_TEST.apk`
- Size: 112,238,861 bytes
- SHA-256: `f3199c9aa28ee49889ba536e0fbbe6cdaa4d37ea9e6db48a2668001896210cc5`
- ZIP entries: 1,005; CRC PASS; duplicate paths: 0
- JAR/v1 signature: PASS with `jarsigner -verify`
- APK v2 signature and content digest: PASS using local verification code (the official `apksigner` binary is unavailable)
- Resource-table alignment: PASS; all stored entries aligned; seven native libraries aligned at 4 KiB
- Runtime on user's phone: not tested yet

This corrects the exact source syntax error displayed in the screenshot. It does not guarantee there are no later event/script errors, so the console remains enabled to reveal the next checkpoint or failure. The APK uses the same local test certificate as the prior STARTDIAG candidate, not the publisher certificate. Original game/license checks remain intact.

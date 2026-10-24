# DR2C VORENYX — Coverage Recheck (24 October 2026)

## Result

**A reliable global localization percentage cannot currently be verified.** The v2.40 archive has a fresh 16,834-literal inventory, but does not have a fully reviewed current status for every complete player-visible display expression.

For triage only, the fresh scan produces a **machine-audit non-flagged proxy of 88.11%–94.30%**. This is explicitly **not** a localization-coverage percentage. The range varies according to whether English-likelihood scores of 0.2 or 0.5 trigger manual review.

## Fresh v2.40 inventory

- Active quoted-literal rows: **16,834**.
- Non-path/non-engine rows used for the proxy denominator: **15,839**.
- Classification counts: 7,562 likely player-facing, 8,277 needs context review, 994 path/asset references, and 1 debug/engine row.
- English-likelihood ≥0.2: **1,578 rows**, 1,538 distinct file/literal pairs across 188 files. These are review candidates, not confirmed untranslated expressions.
- English-likelihood ≥0.5: **598 rows**, 594 distinct file/literal pairs across 116 files.
- English-likelihood ≥0.7: **91 rows** across 42 files.
- Newly changed literals without a score: **305 rows in 77 files**. They require classification rather than being assumed translated.
- Combined broad triage: **1,883 rows across 196 files**.

## Historical percentage

The v2.22 historical heuristic is reproducible: **7,490 / 10,844 = 69.07%**. The older v2.2 column is **3,509 / 10,844 = 32.36%**. Those are different historical checkpoints, not contradictory measurements. Neither represents current v2.40 coverage.

## Why the empty queue does not mean 100%

The inherited untranslated-candidate queue is marked stale in package metadata, and the per-build residual-candidate JSONL is empty. That only tells us the inherited queue was reconciled; it is not evidence of an exhaustive zero-residue scan. The fresh active-literal inventory still produces the triage counts above.

## Static facts still verified

- v2.40 ZIP CRC: PASS; 411 entries; 410 manifest entries; 0 manifest hash failures; 0 duplicate paths.
- Canonical trait/perk identifier mismatches: 0 remaining across 195 compared operands.
- CYOA/choice IDs and route/resource paths are preserved by static checks.
- Runtime gameplay, UI fit, save/load, and APK rebuild/signing remain NOT RUN / NOT PERFORMED.

## Next step for a real percentage

Rebuild the inventory from **complete player-visible display expressions**, not raw quote fragments. Give each expression an explicit state: translated/reviewed, intentionally preserved, non-player-facing, or untranslated/needs review. Manually classify the 1,883 broad-triage rows, resolve placeholders and duplicate expressions, and calculate translated-or-approved divided by total player-visible expressions. Track runtime/UI validation separately.

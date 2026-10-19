# Serevex Quant Research — persistent project memory

This directory is the durable working notebook for the XAUUSD/gold analysis and Telegram-assistant project. It records architecture, progress, benchmarking, source provenance, current blockers, and a prioritized roadmap.

Start with **PROJECT_MEMORY.md**, then **PROGRESS_LOG.md**, **BENCHMARKS_AND_EVIDENCE.md**, **RESEARCH_SUMMARY.md**, **ROADMAP.md**, and **SOURCE_SNAPSHOT.md**.

## Current state (2026-10-17; latest checkpoint v1.4.1)
- Latest source artifact: serevex-intelligence-v1.2.0.zip (260,781 bytes; SHA-256 19912b690e74af802a7170316703d40048a67731a1eb26d806c9929f048d2db3). It remains a downloadable artifact, not a binary tracked in this folder.
- Clean release validation: 176 pytest passed; 109 unittest passed; compileall, inline JS syntax and HTML-ID audit pass; clean ZIP extraction reruns 176 tests.
- UX increment: persistent-accessible Sederhana/Tingkat lanjut mode in the Mini App; Telegram mode preference backed by SQLite with backward-compatible migration. Mini App mode is browser-local, not server-synchronized. Both modes preserve the NO_TRADE decision gate.
- Local reproducible dataset remains 60 public community XAUUSD M5 bars, with unknown timezone/broker provenance. Release smoke has 50 observed cases / 250 comparisons, 1,200/1,200 market-path contracts and 240/240 software robustness cases.
- Hosted online CI run [#38851629049](https://github.com/orionrayy/ai-determinism-engine/actions/runs/38851629049) passed on the benchmark branch using 35,954 public CSV rows (SHA-256 acb0d2f86b030a3ead93d92038ea27c21db6f5171acfec7a7c316faf90a9e3db), 50 timestamp cases / 250 evaluations, 1,200/1,200 market paths and 240/240 software checks. The sampled data ends 2026-09-25; it is not a live feed.
- The source repository declares an MIT license; market-data rights scope/provenance, quote side, broker semantics and actual fills still need review. The raw 3 MB CSV is not redistributed. Forecast model has zero out-of-sample predictions on the bundled sample and is not calibrated; model superiority is not claimed.
- Live Telegram/OANDA credentials, MT5/cTrader account integration, real browser/mobile acceptance testing, paper trading and deployment are not validated. Keep trading disabled.

Never add credentials, tokens, .env files, or personal account information to this folder.

## Research checkpoint — forecastability discovery (2026-10-19)

- Research prototype and draft PR: [Causal Forecastability Discovery v1](FORECASTABILITY_DISCOVERY_V1.md) / [PR #168](https://github.com/orionrayy/ai-determinism-engine/pull/168). Hosted run #254 passed, but the model remains unvalidated and the change is unmerged.
- The latest 1.31M-row paired Bid/Ask M1 benchmark still fails to demonstrate aggregate predictive skill versus the matured-label baseline (Brier 0.174719 vs 0.174579; 95% paired block interval for baseline-minus-model is entirely negative). COT/news improvements are inconclusive and news/macro coverage remains inadequate.
- This new gate is research-only; it is not wired into the app or a live forecast/decision chain. `NO_TRADE`, no live signal and no live order execution remain mandatory.

## Final hosted verification — 2026-10-16, run 38851436990

The GitHub Actions run is **green**, including unit tests, live acquisition, dataset/count assertions, job summary and artifact upload. Run: https://github.com/orionrayy/ai-determinism-engine/actions/runs/38851436990
Artifact: https://github.com/orionrayy/ai-determinism-engine/actions/runs/38851436990/artifacts/12025522071
Artifact SHA-256: `7c661df1afafc372fd2816f2074ceb05aa7af0f8c7a388e64f07aa6b4bc43ef9` (9,208 bytes; retention expires 2026-10-30 04:35:53Z).

Fresh online sample: 35,954 rows, 3,070,226 bytes, SHA-256 `acb0d2f86b030a3ead93d92038ea27c21db6f5171acfec7a7c316faf90a9e3db`; timestamp range `2026-03-26T02:30:00+00:00`–`2026-09-25T20:40:00+00:00`; median interval 300 seconds; 136 intervals longer than 600 seconds. The remote report ran 50 timestamp cases / 250 rule comparisons, 1,200/1,200 market-path contracts and 240/240 software robustness contracts. Runtime 458.588 ms. All counts/assertions passed; decision output remains `NO_TRADE`.

The +00:00 offset is the representation seen in the file, not independent proof of the provider's intended timezone. Broker, quote-side, license scope and fill semantics remain unverified. DS51 remains `reference_only`. The positive PnL of the breakout baseline comes from only seven trades and cannot establish alpha. See `benchmarks/live_dataset_benchmark_2026-10-16.md` and its JSON companion.


## Latest checkpoint — v1.3.0 (hosted full-history benchmark verified)

- Source package serevex-intelligence-v1.3.0.zip: 278,402 bytes, SHA-256 53dabb5e86c8ce74691790e4c865d2624667cf531e572818bc571527bd4c2b67; 107 ZIP entries. Clean checks: 181 pytest, 109 unittest, 11 online benchmark tests; compileall, JS/HTML and extracted archive pass.
- Hosted run [#38888666520](https://github.com/orionrayy/ai-determinism-engine/actions/runs/38888666520) passed on source commit d790435b9f09d623a795aa6ab7ee4d1732515aa5: 35,954 OHLCV rows; 35,893 sequential opportunities per fixed rule; five disjoint folds 7,175 / 7,176 / 7,176 / 7,176 / 7,190; 1,200 market path and 240 robustness cases passed.
- All active fixed-rule baselines lose with assumed costs in full replay and tail. Expanding-rate Brier 0.250019 vs 0.250000 for constant 0.5, interval crosses zero; rolling base rate is worse. These are diagnostics, not calibrated forecasts.
- Decision remains NO_TRADE. Data rights, timezone, broker execution semantics, real costs, independent regimes and paper trading remain unverified.


## v1.3.1 temporal calibration diagnostic

The downloadable v1.3.1 package adds leakage-aware Platt calibration evaluation: only matured earlier OOS labels fit the transform and metrics are reported on a later chronological holdout. The clean local build passed 185 pytest, 109 unittest, compileall, Mini App JS/HTML and ZIP extraction checks. Eight tests and 240/240 synthetic contracts pass. The synthetic example is not market evidence; the bundled 60-bar data still yields zero TP-before-SL OOS forecasts. NO_TRADE remains active.

Release ZIP: 276,128 bytes; SHA-256 b63af5ab3412e7cb0bac14deffdb0d8cf07e024b0e46364d6fe5e1329d831d5b.

## v1.3.1 hosted calibration CI verified

The current PR code commit `6017eec3141fb803907583abeca006a230e90be4` passed hosted CI run [#38897894594](https://github.com/orionrayy/ai-determinism-engine/actions/runs/38897894594). The temporal calibration unit tests and 240/240 synthetic contracts passed, as did live public data acquisition, full-history replay assertions, and artifact upload.

Calibration artifact: #12044756186, 14,966 bytes, SHA-256 `a2561de0161e79dbaac794988b5545cd8f32fe2cf55d38c875e8aed91e99d9b3`, expires 2026-10-30. It contains 35,954-row dataset diagnostics, 35,893 all-history opportunities per rule, 1,200/1,200 market-path contracts, 240/240 software checks, and the separate 240/240 temporal-calibration contract report. Synthetic calibration cases are not market-performance evidence.

The current release remains a research prototype with `NO_TRADE`; no validated live model or trading activation is claimed.


## Research upgrade — forecastability discovery v2 (2026-10-19)

- Design, research sources, equations, limitations and acceptance gates: [FORECASTABILITY_DISCOVERY_V2.md](FORECASTABILITY_DISCOVERY_V2.md).
- Implementation remains in isolated draft [PR #168](https://github.com/orionrayy/ai-determinism-engine/pull/168). v2 adds multi-window, regime-conditional paired skill checks and approximate max-|t| block-bootstrap bounds. These are research diagnostics, not a validated predictor.
- Prior-art review confirms the broad ideas are established; mathematical originality is unproven. v2 hosted CI run #259 passed, but it did not demonstrate market skill. A later untouched OOS cohort is still required.
- Safety state unchanged: NO_TRADE; model/deployment unvalidated; live signals and orders disabled.


## Research upgrade — delayed-feedback expert selector v3 (2026-10-19)

- Design and prior-art review: [FORECASTABILITY_DISCOVERY_V3.md](FORECASTABILITY_DISCOVERY_V3.md).
- Source code and 13 synthetic contract tests are in draft [PR #168](https://github.com/orionrayy/ai-determinism-engine/pull/168).
- v3 combines model probabilities and an explicit causal baseline, updates global/regime fixed-share weights only after labels mature, and falls back to baseline if support is insufficient. It does not claim a regret theorem, novel-world mathematics, or market alpha.
- Local tests and py_compile passed. A fresh hosted run is required after v3 code changes. The previously tested probability method remains worse than the matured-label baseline; NO_TRADE stays enforced.


## Research increment — integrated Serevex stages 1–3 (2026-10-19)

- Source PR: [#168 — integrated ledger, predictability atlas and delayed mixer](https://github.com/orionrayy/ai-determinism-engine/pull/168).
- Added the integrated standard-library module, contract tests, and execution specification on branch `research/serevex-forecastability-discovery-v1`:
  - [Module](https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/online-benchmark/serevex_stage123_integrated_v1.py)
  - [Tests](https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/online-benchmark/test_serevex_stage123_integrated_v1.py)
  - [Contract](https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/SEREVEX_STAGE123_INTEGRATED_V1.md)
- Stage 1 checks canonical ledger hashes, point-in-time feature facts, explicit data verification states, timestamp/index agreement and registered metadata. Stage 2 uses a preregistered state-category registry, paired Brier/log-loss diagnostics, block uncertainty and complementarity audits. Stage 3 combines experts with a causal baseline using maturity-gated Fixed-Share updates and a strict exclusive `as_of` cutoff. A CLI accepts an existing JSON forecast ledger.
- Latest hardened branch head: `8660f39223113cbc864bcdb79e7a5f192d35004c`. Workflow [#268](https://github.com/orionrayy/ai-determinism-engine/actions/runs/39270426351) has steps 1–6 passing, including the unit-test suite; data-acquisition step 7 is in progress at checkpoint creation. Full hosted validation is not yet confirmed.
- The integrated module currently consumes pre-generated expert forecasts. It does not train price forecasters, and a qualified real-feed forecast-ledger producer remains outstanding. Existing real-data evidence for the previously tested probability method is negative vs. baseline; this increment has not been shown to improve market skill.
- Safety state: research only; `NO_TRADE`; model/deployment validation false; live signals and order routing remain disabled.

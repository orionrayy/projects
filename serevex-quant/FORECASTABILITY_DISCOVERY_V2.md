# Serevex Forecastability Discovery v2 — research checkpoint

**Checkpoint:** 2026-10-19 (Asia/Jakarta).  
**Status:** research candidate in open draft PR #168; not merged or integrated into app/live signal path.

## Source links

- [Draft PR #168](https://github.com/orionrayy/ai-determinism-engine/pull/168)
- [v2 implementation](https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/online-benchmark/forecastability_discovery_v2.py)
- [v2 contract tests](https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/online-benchmark/test_forecastability_discovery_v2.py)
- [v2 research design and related work](https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/FORECASTABILITY_DISCOVERY_V2.md)
- [v1 checkpoint](FORECASTABILITY_DISCOVERY_V1.md)

## Research expansion

Version 1's one-window model/regime gate was expanded to a pre-registered multi-scale screen:

- evaluates only mature, point-in-time outcomes and rejects future-dated regime metadata;
- requires candidate experts to share the exact decision/outcome cohort and baseline probabilities;
- scores skill as Brier(baseline) minus Brier(model), separately for each model, regime and decision-bar window;
- resamples synchronized row blocks across models and regimes, with blocks prevented from crossing missing indices and declared session boundaries; regime transitions remain inside blocks;
- derives approximate studentized max-|t| bounds across supported candidate/regime/window comparisons, separately for every preregistered block length;
- requires positive lower skill bounds at every declared window and block length before a model/regime pair becomes eligible for a later independent replication;
- reports a descriptive recent-vs-long-window warning without pretending it is a calibrated change-point p-value;
- forms research-only candidate weights from the minimum corrected lower bound. These weights are selected on historical evidence and must be frozen for a later untouched holdout.

## Literature reconciliation and originality

The research review confirmed that regime-switching forecast combinations, expert selection/blending, drift detection, scoring-rule comparisons and backtest selection correction all have established prior art. Relevant starting points are:
- Wang et al., *Forecast combinations: an over 50-year review* — https://arxiv.org/html/2205.04216v2
- Elliott & Timmermann, *Optimal Forecast Combination Under Regime Switching* — https://cepr.org/publications/dp4649
- Qian et al., *Combining forecasts for universally optimal performance* — https://doi.org/10.1016/j.ijforecast.2021.05.004
- Diebold & Mariano, *Comparing Predictive Accuracy* — https://doi.org/10.1080/07350015.1995.10524599
- Hansen, *A Test for Superior Predictive Ability* — https://doi.org/10.1198/073500105000000063
- Bailey et al., *The Probability of Backtest Overfitting* — https://doi.org/10.21314/jcf.2016.322
- Bifet & Gavaldà, ADWIN — https://doi.org/10.1137/1.9781611972771.42
- Howard et al., time-uniform confidence sequences — https://doi.org/10.1214/20-AOS1991

This establishes a prior-art baseline, not an exhaustive literature/patent/code search. The candidate must not be advertised as never-before-seen mathematics. Its useful hypothesis is the exact evidence-control contract; real originality would require an additional method/theorem plus broad prior-art validation.

## Statistical caveat

The v2 max-|t| moving-block procedure is approximate. It is not an exact finite-sample family-wise guarantee under arbitrary autocorrelation, regime shifts, sparse regimes or broken segmentation. Cross-window bootstrap streams use deterministic substreams rather than an exact joint stationary bootstrap. Reports say this explicitly. A later SPA/Reality Check with a complete synchronized portfolio-return panel is still required if the question is whether any strategy in a searched family beats a benchmark.

## Most recent benchmark evidence remains negative

The verified hosted run #254 reported M1 aggregate Brier 0.1747186248 versus matured-label baseline 0.1745785974, with baseline-minus-candidate skill -0.0001400274 and 95% moving-block interval [-0.0002451349, -0.0000518749]. The tested probability method did not demonstrate aggregate skill. In the external context holdout, COT improvement interval [-0.00042107, 0.00083390] and news interval [-0.00003016, 0.00004313] both crossed zero; temporal news and macro support remain inadequate. See the run and PR #167 details.

## Verification state

- The first workflow run after the v2 code/tests landed showed all 11 v2 contract tests passing, plus existing benchmark unit gates; that run was later cancelled during the expensive large-scale replay because subsequent commits arrived.
- Fresh workflow run #259 was triggered by the latest test commit and is pending/undergoing validation at checkpoint creation. Do not label it PASS until the run reports completed success and the large-scale/quote-side/context steps are checked.
- Synthetic test success remains software evidence, not market evidence.
- Required next step after CI: create the out-of-sample paired forecast ledger adapter, keep model selection separate from calibration and final holdout, freeze candidate weights, and score them only on a later untouched cohort.

## Persistent safety boundary

NO_TRADE; validated model false; deployment calibration false; live signals disabled; live order execution disabled. No merge or trading promotion based solely on this candidate's own selection dataset.

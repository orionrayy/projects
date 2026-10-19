# Serevex Forecastability Discovery v3 — delayed-feedback expert selector

**Checkpoint:** 2026-10-19 (Asia/Jakarta)  
**Status:** locally tested research prototype, added to draft PR #168; hosted v3 validation pending. Not market-validated, not integrated into Telegram/live signals, and never authorizes trading.

## Source links

- Draft implementation PR: https://github.com/orionrayy/ai-determinism-engine/pull/168
- Source module: https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/online-benchmark/delayed_fixed_share_expert_v1.py
- Source tests: https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/online-benchmark/test_delayed_fixed_share_expert_v1.py
- Full design: https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/FORECASTABILITY_DISCOVERY_V3.md
- Previous multi-scale evidence screen: [FORECASTABILITY_DISCOVERY_V2.md](FORECASTABILITY_DISCOVERY_V2.md)

## Separation of roles

- **v1:** one-window model/regime forecast-skill evidence gate.
- **v2:** multi-window and block-length sensitivity screen. Its max-|t| moving-block uncertainty is approximate and not a universal finite-sample guarantee.
- **v3:** sequential prediction mixture; consumes pre-generated expert probabilities, a common causal baseline, regime tags and label-maturity indices. It does not train upstream price models.

V1/v2 can screen candidates; v3 tests whether a causal expert mixture can exploit complementary candidate skill while respecting delayed outcomes.

## v3 update rule

For expert k and matured binary outcome y, use Brier loss l[k,i]=(p[k,i]-y[i])^2. Baseline-relative loss is d[k,i]=l[k,i]-l[baseline,i], which is bounded [-1,1]. An exponential-weights update on a matured batch B is:

w_tilde[k] ∝ w[k] exp(-eta * mean(d[k,i] for i in B))

then apply fixed-share redistributive mass:

w_new[k] = (1-gamma) * w_tilde[k] + gamma/K.

The registered option set includes the baseline as an explicit expert. The baseline is therefore part of the mixture and not only an offline comparator. Global and regime-specific weights are maintained independently; a regime pool cannot be used until its declared mature-label support floor is reached, and earlier predictions fall back to global weights or the exact baseline probability.

The contract enforces that at decision index t, only label updates with label_available_index < t are visible. Outcomes sharing the same availability index are grouped into one deterministic batch; batches are applied in availability-index order. Weights and updates are hashed for reproducibility. The code flushes any outcomes available before the final as-of boundary into the final state without changing forecasts already issued.

An optional evidence manifest requires target, target-definition, dataset, source-lineage, forecast-ledger and model-artifact hashes. Code checks shape only; a valid-looking hash manifest is not proof of source authenticity, data rights, or model-fit chronology.

## What is new, and what is not

Fixed-share expert weighting, forecast combination, regime-switching combination, conditional predictive ability, and dynamic-regret tracking are established topics. This code makes no claim of a new regret theorem. The exact Serevex hypothesis is a combined operational contract: delayed outcome maturity, regime-specific pools with a global fallback, explicit baseline weighting, reproducible update lineage, and hindsight comparators isolated from decision updates.

Hindsight best-fixed and best-switching experts are calculated only as diagnostics. They use the entire scored cohort, so they must not be used as predictive information or deployed weights.

Prior-art starting points:
- Wang et al., *Forecast combinations: an over 50-year review*: https://doi.org/10.1016/j.ijforecast.2022.11.005
- Elliott & Timmermann, *Optimal Forecast Combination Under Regime Switching*: https://cepr.org/publications/dp4649
- Giacomini & White, *Tests of Conditional Predictive Ability*: https://doi.org/10.1111/j.1468-0262.2006.00718.x
- Mourtada & Maillard, *Efficient tracking of a growing number of experts*: https://proceedings.mlr.press/v76/mourtada17a.html
- Baby & Wang, *Optimal Dynamic Regret in Proper Online Learning with Strongly Convex Losses*: https://proceedings.mlr.press/v151/baby22a.html
- *Optimal Tracking in Prediction with Expert Advice*: https://arxiv.org/abs/2208.03708
- Hansen, *A Test for Superior Predictive Ability*: https://doi.org/10.1198/073500105000000063

This is not an exhaustive literature, patent or code search. Global originality remains unverified.

## Local verification

- 13 standard-library synthetic contract tests pass (python -m unittest -v).
- py_compile passes.
- One deterministic regime-switching synthetic fixture yields lower Brier for the regime-aware mixture than the constant-0.5 baseline. This validates only the intended software behavior on constructed data; it is not observed market skill.
- PR #168 now includes the v3 code and tests. Hosted workflow run #262 is pending/in progress at checkpoint creation; do not call hosted v3 validation PASS until the full workflow concludes successfully.

## Existing real-market evidence, not v3 results

Verified hosted run #259 completed all workflow steps and uploaded artifact #12189641552 (2,660,656 bytes; SHA-256 2d81f85e8a175208bc01aeff741b7e4eedc1cdede04e1137c60fba8c307d700a; expires 2026-11-02). Reported 1,313,280 paired XAUUSD M1 Bid/Ask candles and 20,000 real anchors.

The previously tested prequential probability method had Brier 0.1747186248 versus matured-label baseline 0.1745785974; baseline-minus-model skill was -0.0001400274 with 95% block interval [-0.0002451349, -0.0000518749]. The tested method failed to demonstrate incremental probability skill. COT/news intervals crossed zero, complete 1-hour news support was 205/19,894, 24-hour support 100/19,894, and macro support zero. These are pre-v3 diagnostics and do not evaluate the new mixture.

Run #259: https://github.com/orionrayy/ai-determinism-engine/actions/runs/39257271380

## Required experiment before v3 integration

1. Export an immutable, point-in-time forecast ledger from all candidate experts using the same target definition and decision cohort.
2. Define training cutoffs, data/model hashes, label maturity, regime availability and data-quality/provenance gates.
3. Compare baseline-only, static equal-weight blend, v1, v2, v3 and the best model selected only on a separate earlier selection partition.
4. Freeze expert pool, eta, fixed-share rate, regime definitions and support floors before the final untouched chronological holdout.
5. Report Brier/log loss, calibration, confidence intervals, regime-level support, fallback frequency, weight concentration, expert turnover, delayed feedback, and hindsight regret diagnostics.
6. Separately assess net executable portfolio returns, full tested strategy family, and selection bias. Forecast improvement is not equivalent to net profit.

## Non-negotiable safety state

NO_TRADE; model validated false; deployment calibration false; live signals disabled; live order execution disabled. Synthetic tests do not authorize market claims.

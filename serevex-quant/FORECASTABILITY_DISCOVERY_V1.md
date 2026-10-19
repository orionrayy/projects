# Serevex — Causal Forecastability Discovery v1 checkpoint

**Checkpoint:** 2026-10-19 (Asia/Jakarta)  
**Status:** Research prototype in isolated draft PR; not integrated into benchmark decision path; not market-validated.

## Source-of-truth links

- Source PR: https://github.com/orionrayy/ai-determinism-engine/pull/168
- Upstream evidence-gate dependency: https://github.com/orionrayy/ai-determinism-engine/pull/167
- Separate rebrand/readiness PR: https://github.com/orionrayy/ai-determinism-engine/pull/166
- Design specification in source branch: https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/FORECASTABILITY_DISCOVERY_V1.md
- Prototype module: https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/online-benchmark/forecastability_discovery_v1.py
- Tests: https://github.com/orionrayy/ai-determinism-engine/blob/research/serevex-forecastability-discovery-v1/projects/aurum-intelligence/online-benchmark/test_forecastability_discovery_v1.py

## Rationale

The latest available large-scale research evidence in PR #167 does not demonstrate aggregate predictive skill over its matured-label baseline: reported prequential Brier is 0.1747186248 versus baseline 0.1745785974, with the baseline-minus-model paired block-bootstrap interval entirely negative at [-0.00024513, -0.00005187]. External-context ablations in that run did not establish incremental COT/news skill, and GDELT temporal coverage remained partial. Treat these as branch CI results and source-qualified diagnostics, not proof of alpha.

The next research increment is not another black-box model. It is a strict forecastability/competence gate that can reject experts whose apparent skill does not survive causal maturity, regime stratification, time/session-bounded uncertainty estimates and correction for the preregistered model × regime family.

## Implemented prototype

The isolated branch adds a standard-library function that consumes pre-generated out-of-sample probability records. It:
- Uses Brier skill defined as baseline loss minus model loss; positive means the model beats baseline.
- Scores only labels whose maturity index is strictly before the as-of index.
- Requires regime metadata to have been available at the decision index.
- Requires every registered model to share the identical decision/outcome cohort and baseline probability.
- Uses deterministic moving-block resampling without crossing missing indices, declared session segments, or regime boundaries.
- Applies a Bonferroni correction across the preregistered model × regime family.
- Returns eligibility for independent replication only, not market promotion.
- Permanently leaves model/deployment validation false, live signals and order execution disabled, and decision output at NO_TRADE.

## Verification boundary

- Local synthetic contract tests: 10 passed; py_compile passed (2026-10-19).
- Hosted GitHub Actions run #254 (39252496309) was observed in progress during checkpoint creation; do not treat it as passed until final status and all steps are verified.
- Synthetic tests establish implementation behavior only. No new market skill, alpha, originality or global ranking is claimed.
- The module is not wired into the current evaluation/Telegram decision path. Integration requires a genuine forecast ledger and a dedicated earlier model-selection partition; the frozen candidate/weights must then be evaluated on a later untouched holdout without further tuning.

## Next gates

1. Confirm hosted CI outcome and repair any failing contract or integration checks.
2. Build an export adapter from a causally generated forecast ledger. Do not convert sparse sampled anchors into a contiguous time series or use labels before their maturity index.
3. Compare causal base rate, equal-weight blend, selection-only best expert, non-regime prequential gate, and the proposed regime-conditioned gate on an identical holdout cohort.
4. Register model/regime candidates and selection rules before inspecting holdout outcomes.
5. Require positive corrected OOS probability skill, adequate regime-specific sample support, calibration diagnostics, verified source lineage, and execution-aware net-of-cost evidence before considering any promotion.

## Prior-art caveat

The design is inspired by established work on prequential evaluation, forecast combination, forecastability measurement and data-snooping control. Sources to review include:
- Dawid (1984), “Statistical Theory: The Prequential Approach,” DOI: 10.2307/2981683.
- Elliott & Timmermann (2005), “Optimal Forecast Combination under Regime Switching,” DOI: 10.1111/j.1468-2354.2005.00361.x.
- White (2000), “A Reality Check for Data Snooping,” DOI: 10.1111/1468-0262.00152.
- Yao et al. (2004), “Measure of predictability,” DOI: 10.1103/PhysRevE.69.066121.

This is not an exhaustive literature/patent/code search. Mathematical or global originality remains unverified.

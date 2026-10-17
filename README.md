# Serevex Quant Research

Standalone research repository for the Serevex Quant XAUUSD/gold market-analysis workbench.

## Project layout

- `serevex-quant/` — project memory, implementation status, checkpoints, source adapters, backtests, benchmark runners, and unit tests.
- `.github/workflows/serevex-research-benchmark.yml` — reproducible dataset, benchmark, calibration-contract, and evidence-readiness checks.
- `docs/superpowers/plans/` and `docs/superpowers/specs/` — research plan and design specification.

## Evidence status

The latest source-repository run available at migration time was [GitHub Actions run #39048892113](https://github.com/orionrayy/ai-determinism-engine/actions/runs/39048892113), which passed its CI workflow on source commit `74020ce9b5f66cbe6e23815e2fc21db17013f10f`. That result validates the source commit's pipeline; it does **not** mean the workflow has already run in this destination repository.

The latest readiness output from the source branch was intentionally **BLOCKED**:
- Pipeline status: PASS
- Data status: REFERENCE_ONLY
- Statistical status: INCONCLUSIVE
- Economic status: INCONCLUSIVE
- Operations status: NOT_RUN
- Decision output: `NO_TRADE`

Passing software tests, processing large datasets, and completing benchmarks do not establish predictive edge or profitability. Live signal generation and live order execution remain disabled. Source rights/provenance, timestamp and broker semantics, independent out-of-sample evidence, execution costs, and paper-trading validation remain open requirements.

## Migration record

- Migrated from: [`orionrayy/ai-determinism-engine`](https://github.com/orionrayy/ai-determinism-engine/tree/refactor/serevex-quant-rebrand/projects/serevex-quant)
- Source branch: `refactor/serevex-quant-rebrand`
- Source commit: `74020ce9b5f66cbe6e23815e2fc21db17013f10f`
- Migration date: 2026-10-17
- The source repository and its draft [PR #166](https://github.com/orionrayy/ai-determinism-engine/pull/166) are retained unchanged as provenance and rollback references.

The repository intentionally does not include credentials, tokens, `.env` files, broker secrets, or redistributed raw market data. Historical run identifiers and hashes are retained for auditability.

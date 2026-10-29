# SOL Scalper Monitor — public-data phase

A free-first, read-only SOL/IDR market monitor designed for Cloudflare Workers and a public status endpoint that can be inspected by ChatGPT when asked. It is deliberately **not a live trading bot** yet: no private exchange credentials, order endpoint, account access, or withdrawal capability is present.

## Why Tokocrypto first

The initial adapter uses Tokocrypto's documented public market-data endpoints for SOL/IDR (`SOLIDR`): 1m/5m/15m klines, order-book depth, and recent public trades. The selected exchange/platform must be reconfirmed against the latest OJK list before a user creates or funds an account. Trading minimums, market status, fee tier, and live API syntax must be checked before any private API integration.

## Current behavior

- Runs a scheduled scan every two minutes and stores only a public-market snapshot in Cloudflare KV.
- Exposes `/status` as JSON, `/health` for service health, and `/config` for non-secret policy values. The root URL returns service metadata; no dashboard UI is included in this phase.
- Computes EMA 9/21, RSI 14, ATR 14, volume expansion, order-book imbalance, recent aggressive trade-flow imbalance, spread, and a multi-timeframe score.
- Returns `BUY_SETUP_WATCH_ONLY`, `WATCH`, or `NO_TRADE`. The highest signal is a research alert only; it never means that an order was placed.
- Fail-closed behavior: upstream errors produce `DEGRADED/NO_TRADE`; snapshots older than three minutes become `STALE/NO_TRADE`.
- Uses an illustrative Rp500,000 paper bankroll, 0.5% risk-per-trade, 3% daily stop, and 50% max notional. These are engineering guardrails for simulation, not a promise of profitability.
- Does not infer/assume exchange fees. A conservative 0.50% cost reserve is used only for rough sizing; exact fee tier and slippage must be measured before any real trade.

## Free-first deployment shape

- Cloudflare Worker with a two-minute Cron Trigger (`*/2 * * * *`).
- One dedicated KV namespace; a single value is written per scan (about 720 writes/day), keeping under the published 1,000 writes/day free allowance under normal usage.
- No paid LLM is called for each signal. The signal calculation is deterministic; AI is reserved for review, explanation, and later research.
- No user/API secrets are stored in source control or public snapshots.

## Runtime endpoints

- `/health` — liveness and execution-disabled status.
- `/status` — last market snapshot, freshness, indicators, signal checks, blockers, paper risk estimate, and execution safety flags.
- `/config` — public non-secret configuration only.

## Local tests

Requires Node.js with the built-in test runner; no npm dependencies:

```sh
node --test worker.test.mjs
```

## Safety gate for future live trading

Live trading is a separate phase and must not be enabled merely by adding credentials. Required gates include: verified account/permissions, spot-only API key with reading/trading only (withdrawal disabled), exact fees, symbol filters/minimums, balances, order-state reconciliation, idempotent client order IDs, stop/exit recovery after crash, duplicate-order fencing, daily loss-stop persisted independently from the process, slippage checks, rate-limit handling, and a user-approved paper-trading performance report. Avoid password/OTP/secret sharing in chat.

## Official references

- Tokocrypto API documentation: https://www.tokocrypto.com/apidocs/
- OJK official list of digital financial asset/crypto traders (latest list must be checked at onboarding): https://ojk.go.id/id/Fungsi-Utama/ITSK/Perizinan-ITSK-Aset-Keuangan-Digital-Aset-Kripto/Pages/Daftar-Penyelenggara-Perdagangan-Aset-Keuangan-Digital-Posisi-22-September-2026.aspx
- Cloudflare Cron Triggers: https://developers.cloudflare.com/workers/configuration/cron-triggers/
- Cloudflare Workers/KV pricing and limits: https://developers.cloudflare.com/workers/platform/pricing/

## Status

Phase 1 is a read-only scanner and telemetry endpoint. There is no live execution path. Passing unit tests validates code paths, not predictive edge or profitability.

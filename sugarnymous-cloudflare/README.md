# Sugarnymous Cloudflare migration

This directory is the start of the migration away from Floot as the development/build control plane.

## What this branch contains

- `runtime-snapshot/worker.mjs` is an exact entry-module snapshot exported from the active Cloudflare Worker on 2026-10-20. The 287,610-character `telegramBundle.mjs` is preserved in 32 integrity-checked segments under `runtime-snapshot/parts/`; the GitHub Actions assembler reconstructs it and verifies both SHA-256 digests before tests/deployment.
- `wrangler.toml` records the active Worker name, compatibility date, and Hyperdrive binding without embedding credentials.
- `PRODUCTION_DEPLOY_ALLOWED` deliberately remains `false` until the public site no longer proxies to Floot and route/health/smoke tests pass.
- The GitHub Actions workflow provides reproducible syntax/secret-scan validation and a guarded manual-deploy path.

## Important limitation

This is **not yet the complete editable application source**. The Worker bundle is a compiled runtime snapshot; the original TypeScript/TSX helper files and public-site source still need to be recovered and checked into this repository. The current Worker entry proxies non-API paths to `https://sugarnymous-prerelease.floot.app`, so deploying this snapshot unchanged would **not** complete the migration. Do not enable production deployment until `PRODUCTION_DEPLOY_ALLOWED` is deliberately changed to `true` after the origin has been migrated and tested.

## Production safety

- The live Telegram webhook and PostgreSQL/Hyperdrive are not changed by this branch.
- No Telegram token, webhook secret, setup secret, database URL, or Cloudflare API token belongs in Git.
- Deployment keeps existing Worker variables/secrets and reuses the existing Hyperdrive binding ID.
- Public waitlist and bot eligibility stay unchanged; the dating features remain 18+ and closed-beta only.

## Next steps

1. Recover original helpers/endpoints/pages plus their specs from the Floot project when project reads are available, and establish them as the maintainable source of truth.
2. Promote the tested `sugarnymous-static-site` Worker through the `STATIC_SITE` service binding after production smoke/rollback readiness is confirmed.
3. Add tests for `/`, `/privacy`, `/community-principles`, `/telegram-setup`, `/_api/health`, native health, webhook-secret rejection, idempotency, and bilingual /menu + /privacy flows.
4. Set `PRODUCTION_DEPLOY_ALLOWED=true` only after those checks pass, preserved secrets/Hyperdrive are verified, and a rollback snapshot exists.

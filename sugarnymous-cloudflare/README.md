# Sugarnymous Cloudflare migration

This directory is the start of the migration away from Floot as the development/build control plane.

## What this branch contains

- `runtime-snapshot/worker.mjs` is an exact entry-module snapshot exported from the active Cloudflare Worker on 2026-10-20. The 287,610-character `telegramBundle.mjs` is preserved in 32 integrity-checked segments under `runtime-snapshot/parts/`; the GitHub Actions assembler reconstructs it and verifies both SHA-256 digests before tests/deployment.
- `wrangler.toml` records the active Worker name, compatibility date, and Hyperdrive binding without embedding credentials.
- `PRODUCTION_DEPLOY_ALLOWED` is `true` after the native Worker was deployed with the `STATIC_SITE` binding and production health/site route checks passed. GitHub Actions deployment is still manual and requires `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` repository secrets.
- The GitHub Actions workflow provides reproducible syntax/secret-scan validation and a guarded manual-deploy path.

## Important limitation

The **runtime is independent of Floot**, but the original editable TypeScript/TSX helper files have not yet been recovered into GitHub. The native Worker now routes the public site through `STATIC_SITE`, and its production entry contains no Floot-origin proxy. The GitHub snapshot is currently a compiled bundle; recover and test the original helper sources before treating this repository as the complete maintainable application source.

## Production safety

- The live Telegram webhook and PostgreSQL/Hyperdrive are not changed by this branch.
- No Telegram token, webhook secret, setup secret, database URL, or Cloudflare API token belongs in Git.
- Deployment keeps existing Worker variables/secrets and reuses the existing Hyperdrive binding ID.
- Public waitlist and bot eligibility stay unchanged; the dating features remain 18+ and closed-beta only.

## Next steps

1. Recover original helpers/endpoints/pages plus their specs from the Floot project when project reads are available, and establish them as the maintainable source of truth.
2. Recover the original TypeScript/TSX bot helpers, endpoint handlers, schema and specs from the previous workspace after project reads are available; preserve the same compiled runtime until recovered code passes regression tests.
3. Add/verify the requested eight-button bot menu and expanded profile/media/matching flows using the editable sources.
4. Before using GitHub Actions for future deployments, add repository secrets `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN`; both deployment jobs remain manual and gated.

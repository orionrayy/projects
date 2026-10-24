# Sensitive Asset Exclusion

The input APK includes `assets/api_key.txt`, containing a credential-shaped Amazon token. The file and token value are intentionally excluded from GitHub and downloadable source bundles.

The decoded wrapper's `extractAdditionalFiles()` loop lists root assets, skips the main `S3DMain.smf` pack, and appears to send other asset names through `extractAssetFromAPK(...)`; this suggests `api_key.txt` may be copied to the app's writable pack directory. This is a static-flow inference, not a runtime observation.

If the credential is active, rotate/revoke it through the owning service and audit possible exposure. Review whether it needs to be packaged in the APK at all and whether the destination path, backups, logs, or support dumps can expose it.

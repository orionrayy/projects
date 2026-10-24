# Sensitive Asset Exclusion

The input APK includes `assets/api_key.txt`, containing a credential-shaped Amazon token. The file and token value are intentionally excluded from GitHub and downloadable source bundles. If the credential is active, rotate/revoke it through its owning service and audit possible exposure.

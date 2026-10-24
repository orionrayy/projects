# v17 — Android build target added, native game route still blocked

This increment adds a Gradle Android application project under cheats-harness/, a testable local UI state controller, and a GitHub Actions pipeline which assembles and publishes a debug APK artifact.

The artifact is named DQ Cheats Sandbox Harness. It does not repackage, modify, or connect to the Dungeon Quest process. Its controls are intentionally labelled as local previews. This gives the repository a reproducible Android build and allows layout/state-controller iteration without falsely reporting the original game route as integrated.

The actual in-game requirement remains unchanged: integrate a menu row into the proprietary S3D Pause -> Options route and connect catalog controllers to verified runtime state adapters in an authorized game source project or with a validated HUD/model editor. Current assets prove the Options/debug model names exist but not the UI event connection. See PAUSE_OPTIONS_CHEATS_ROUTE_V16.md.

Build workflow: .github/workflows/dq-cheats-harness-android.yml. A completed successful run must publish dq-cheats-sandbox-harness-debug-apk. CI success confirms compile/unit tests/packaging, not device installation or gameplay effects.

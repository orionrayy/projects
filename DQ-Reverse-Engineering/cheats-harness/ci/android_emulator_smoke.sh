#!/usr/bin/env bash
# Executed as one process by android-emulator-runner. Keeping state in a file
# avoids per-line shell isolation in that action's script runner.
set -u

: "${RUNNER_TEMP:?RUNNER_TEMP must be supplied by GitHub Actions}"
: "${GITHUB_WORKSPACE:?GITHUB_WORKSPACE must be supplied by GitHub Actions}"
PROJECT="$GITHUB_WORKSPACE/DQ-Reverse-Engineering/cheats-harness"
APK="$RUNNER_TEMP/dq-harness-artifact/app-debug.apk"
TEST_LOG="$RUNNER_TEMP/dq-connected-tests.log"
LOGCAT="$RUNNER_TEMP/dq-emulator-logcat.txt"
UI_DUMP="$RUNNER_TEMP/dq-harness-window.xml"

TEST_STATUS=0
INSTALL_STATUS=1
START_STATUS=1
TITLE_STATUS=1
BOUNDARY_STATUS=1

capture_logcat() {
  timeout 15s adb logcat -d -v threadtime -t 10000 > "$LOGCAT" 2>&1 || true
}
trap capture_logcat EXIT

: > "$TEST_LOG"
: > "$LOGCAT"
if ! test -s "$APK"; then
  echo "FAIL: downloaded build APK is missing or empty: $APK"
  exit 2
fi

timeout 15s adb logcat -c || true
timeout 360s gradle -p "$PROJECT" --no-daemon --stacktrace connectedDebugAndroidTest > "$TEST_LOG" 2>&1 || TEST_STATUS=$?
cat "$TEST_LOG"

timeout 60s adb install -r "$APK"
INSTALL_STATUS=$?
if [ "$INSTALL_STATUS" -eq 0 ]; then
  timeout 30s adb shell am force-stop dev.dqdebug.sandboxharness
  timeout 60s adb shell am start -W -n dev.dqdebug.sandboxharness/.MainActivity
  START_STATUS=$?
fi

if [ "$START_STATUS" -eq 0 ]; then
  timeout 30s adb shell uiautomator dump /sdcard/dq-harness-window.xml >/dev/null 2>&1
  DUMP_STATUS=$?
  if [ "$DUMP_STATUS" -eq 0 ]; then
    timeout 20s adb shell cat /sdcard/dq-harness-window.xml > "$UI_DUMP"
    grep -q "Cheats Sandbox" "$UI_DUMP"
    TITLE_STATUS=$?
    grep -q "GAME LINK" "$UI_DUMP"
    BOUNDARY_STATUS=$?
  fi
fi

capture_logcat
if [ "$TEST_STATUS" -ne 0 ] || [ "$INSTALL_STATUS" -ne 0 ] || [ "$START_STATUS" -ne 0 ] || [ "$TITLE_STATUS" -ne 0 ] || [ "$BOUNDARY_STATUS" -ne 0 ]; then
  echo "FAIL: instrumentation=$TEST_STATUS install=$INSTALL_STATUS launch=$START_STATUS title=$TITLE_STATUS disconnected-boundary=$BOUNDARY_STATUS"
  grep -E -i "FATAL EXCEPTION|AndroidRuntime|am_crash|Process: dev\\.dqdebug|INSTRUMENTATION_FAILED|AssertionError|Caused by:|Test run failed|OutOfMemory|SIGABRT|SIGSEGV" "$LOGCAT" | tail -n 160 || true
  exit 1
fi

echo "PASS: instrumentation, APK install, launcher Activity, and disconnected-state UI."

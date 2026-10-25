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
ACTIVITY_DUMP="$RUNNER_TEMP/dq-harness-activities.txt"

TEST_STATUS=0
INSTALL_STATUS=1
START_STATUS=1
ACTIVITY_STATUS=1

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
  # The instrumented ActivityScenario test already verifies the title and disconnected banner.
  # Avoid UIAutomator's hierarchy dump: on slow API 28 emulators it can trigger a System UI ANR.
  timeout 30s adb shell dumpsys activity activities > "$ACTIVITY_DUMP" 2>&1
  if [ "$?" -eq 0 ] && grep -q "dev.dqdebug.sandboxharness" "$ACTIVITY_DUMP" \
      && grep -q "MainActivity" "$ACTIVITY_DUMP"; then
    ACTIVITY_STATUS=0
  fi
  cat "$ACTIVITY_DUMP" || true
fi

capture_logcat
if [ "$TEST_STATUS" -ne 0 ] || [ "$INSTALL_STATUS" -ne 0 ] || [ "$START_STATUS" -ne 0 ] || [ "$ACTIVITY_STATUS" -ne 0 ]; then
  echo "FAIL: instrumentation=$TEST_STATUS install=$INSTALL_STATUS launch=$START_STATUS activity-present=$ACTIVITY_STATUS"
  grep -E -i "FATAL EXCEPTION|AndroidRuntime|am_crash|Process: dev\\.dqdebug|INSTRUMENTATION_FAILED|AssertionError|Caused by:|Test run failed|OutOfMemory|SIGABRT|SIGSEGV" "$LOGCAT" | tail -n 160 || true
  exit 1
fi

echo "PASS: instrumentation assertions, APK install, and launcher Activity verification; instrumentation checks the title and disconnected-state boundary."

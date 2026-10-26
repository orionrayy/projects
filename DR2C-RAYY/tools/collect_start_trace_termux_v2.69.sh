#!/data/data/com.termux/files/usr/bin/bash
# DR2C VORENYX Android Start trace; no game-data writes and no automatic upload.
set -u
set -o pipefail
PACKAGE="com.noodlecake.drtc"
OUTDIR="$HOME/dr2c-v269-trace-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTDIR" || exit 2
RAW="$OUTDIR/logcat_raw_local_only.txt"
FOCUS="$OUTDIR/START_DIAGNOSTIC_SHARE.txt"
META="$OUTDIR/metadata.txt"
LOG_PID=""
cleanup() {
  if [ -n "$LOG_PID" ]; then
    kill "$LOG_PID" >/dev/null 2>&1 || true
    wait "$LOG_PID" >/dev/null 2>&1 || true
    LOG_PID=""
  fi
}
trap cleanup EXIT INT TERM
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 2; }
command -v adb >/dev/null 2>&1 || fail "adb missing; run: pkg update && pkg install android-tools"

cat <<'EOF'
DR2C VORENYX v2.69 — Android Start diagnostic
- Collects logs only; does not modify/delete game save data.
- Raw logs stay on this device; nothing is uploaded automatically.
- Enable Settings > Developer options > Wireless debugging.
- Open "Pair device with pairing code", and note host/IP, pairing port and temporary code.
EOF
read -r -p "Wireless-debugging host/IP: " HOST
[ -n "$HOST" ] || fail "Host empty"
read -r -p "PAIRING port from pairing dialog: " PAIR_PORT
[[ "$PAIR_PORT" =~ ^[0-9]+$ ]] || fail "Invalid pairing port"
printf '\nEnter the pairing code when ADB prompts. The script does not write it to a file.\n'
adb pair "$HOST:$PAIR_PORT" 2>&1 | tee "$OUTDIR/adb_pair.txt"
PAIR_RC=$?
if [ "$PAIR_RC" -ne 0 ]; then
  printf '\nPair attempt failed. If this device was paired before, the script will still try to connect; otherwise repeat pairing with current port/code.\n'
fi
read -r -p "CONNECT port on the main Wireless debugging page (not the pairing port): " CONNECT_PORT
[[ "$CONNECT_PORT" =~ ^[0-9]+$ ]] || fail "Invalid connect port"
adb connect "$HOST:$CONNECT_PORT" 2>&1 | tee "$OUTDIR/adb_connect.txt"
if ! adb devices | grep -F "$HOST:$CONNECT_PORT" | grep -q 'device$'; then
  adb devices -l | tee "$OUTDIR/adb_devices.txt"
  fail "ADB not connected. Check pairing, current ports and debugging permission. Output: $OUTDIR"
fi
adb shell pm path "$PACKAGE" >/dev/null 2>&1 || fail "Package $PACKAGE not found"
{
  echo "package=$PACKAGE"
  echo "capture_start=$(date -Is 2>/dev/null || date)"
  echo "adb_version=$(adb version | head -1)"
  adb shell getprop ro.build.version.release 2>/dev/null | sed 's/^/android_release=/'
  adb shell getprop ro.build.version.sdk 2>/dev/null | sed 's/^/android_sdk=/'
  adb shell dumpsys package "$PACKAGE" 2>/dev/null | grep -E 'versionCode=|versionName=|firstInstallTime=|lastUpdateTime=' | head -10
} > "$META"

cat <<'EOF'

The script will clear Android's temporary log buffer after explicit confirmation,
then relaunch the game and capture the test. This only clears transient logs, not game data.
EOF
read -r -p "Type CLEAR to confirm clearing the log buffer and start test: " CLEAR_ACK
[ "$CLEAR_ACK" = "CLEAR" ] || fail "Cancelled; log buffer was not cleared"
adb logcat -c >/dev/null 2>&1 || fail "Could not clear logcat using ADB"
adb logcat -b all -v threadtime > "$RAW" 2>&1 &
LOG_PID=$!
sleep 2
adb shell am force-stop "$PACKAGE" >/dev/null 2>&1 || true
adb shell monkey -p "$PACKAGE" -c android.intent.category.LAUNCHER 1 2>&1 | tee "$OUTDIR/launch.txt"
cat <<'EOF'

Game is opening. Perform exactly one test:
1. Wait for the main screen.
2. Tap Start ONCE.
3. Wait about 10 seconds even if nothing happens or the app closes.
4. Switch back to Termux using Recent apps, then press Enter below.
EOF
read -r -p "Press Enter after the Start attempt: " _
sleep 1
cleanup

{
  echo "capture_end=$(date -Is 2>/dev/null || date)"
  echo "pid_after_test=$(adb shell pidof "$PACKAGE" 2>/dev/null | tr -d '\r')"
  echo "--- activity state ---"
  adb shell dumpsys activity activities 2>/dev/null | grep -E -i -C 1 "$PACKAGE|mResumedActivity|topResumedActivity" | tail -80 || true
  echo "--- exit-info (may be unsupported on some builds) ---"
  adb shell dumpsys activity exit-info "$PACKAGE" 2>/dev/null | head -100 || true
} >> "$META"

if [ -s "$RAW" ]; then
  grep -Ein -C 2 'com\.noodlecake\.drtc|AndroidRuntime|FATAL EXCEPTION|Fatal signal|SIGSEGV|SIGABRT|SIGBUS|tombstoned|crash_dump|libc|libart|linker|dlopen failed|PairIP|pairip|deathforth|ActivityTaskManager|ActivityManager|WindowManager|InputDispatcher|InputReader|ANR in|not responding|Exception|assertion failed|abort message|unsatisfiedlinkerror|classnotfoundexception' "$RAW" > "$FOCUS" || true
else
  echo "Logcat raw empty: adb logcat may have stopped or access was denied." > "$FOCUS"
fi
cat <<EOF

Finished. Local output directory: $OUTDIR
Send back only:
  $FOCUS
  $META
Do NOT send logcat_raw_local_only.txt unless requested; it can include logs from other apps.
EOF

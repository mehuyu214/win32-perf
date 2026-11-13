#!/bin/bash
# launch-patched.sh -- Sanoba trial on :115 with the PATCHED wined3d tree
# (win32-perf/wine32-patched). Otherwise identical to launch.sh.
set -u
. "$HOME/workspace/win32-perf/scripts/my.env"
WINEBIN=$WP/wine32-patched/wine-11.21-x86/bin/wine
export PULSE_LATENCY_MSEC=${PULSE_LATENCY_MSEC:-750}
export LP_NUM_THREADS=${LP_NUM_THREADS:-1}
LOGFILE="${LOGFILE:-$WP/logs/game.log}"
cd /tmp || exit 1
setsid nohup $SUP $QEMU "$WINEBIN" "$GAMEEXE" >> "$LOGFILE" 2>&1 &
echo $! > "$WP/logs/game-sup.pid"
echo "launched sup-pid $! log=$LOGFILE"

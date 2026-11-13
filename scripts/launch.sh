#!/bin/bash
# win32-perf launch: Sanoba trial on :115, own prefix, own PA (tcp 47135)
# extra env (GALLIUM_HUD, LP_NUM_THREADS, ...) passes through from caller.
set -u
. "$HOME/workspace/win32-perf/scripts/my.env"
export PULSE_LATENCY_MSEC=${PULSE_LATENCY_MSEC:-750}
export LP_NUM_THREADS=${LP_NUM_THREADS:-1}
LOGFILE="${LOGFILE:-$WP/logs/game.log}"
cd /tmp || exit 1
setsid nohup $SUP $QEMU "$WINEBIN" "$GAMEEXE" >> "$LOGFILE" 2>&1 &
echo $! > "$WP/logs/game-sup.pid"
echo "launched sup-pid $! log=$LOGFILE"

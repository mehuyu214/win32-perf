#!/bin/bash
# run-probe.sh PROBE_EXE_NAME STDOUT_LOG  -- caller sets env (audio cfg etc.)
set -u
. "$HOME/workspace/win32-perf/scripts/my.env"
cd "$WP/probes" || exit 1
setsid nohup $SUP $QEMU "$WINEBIN" "Z:\\home\\hatch\\workspace\\win32-perf\\probes\\$1" >> "$2" 2>&1 &
echo "probe sup-pid $!"

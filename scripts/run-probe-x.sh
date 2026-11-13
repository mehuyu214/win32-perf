#!/bin/bash
# run-probe-x.sh PROBE STDOUT_LOG -- run-probe.sh + caller env passthrough
# of LIBGL_DRIVERS_PATH (set XDRIVERS before calling).
set -u
. "$HOME/workspace/win32-perf/scripts/my.env"
if [ -n "${XDRIVERS:-}" ]; then export LIBGL_DRIVERS_PATH=$XDRIVERS; fi
cd "$WP/probes" || exit 1
setsid nohup $SUP $QEMU "$WINEBIN" "Z:\\home\\hatch\\workspace\\win32-perf\\probes\\$1" >> "$2" 2>&1 &
echo "probe sup-pid $!"

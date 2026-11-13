#!/bin/bash
# run-probe-patched.sh PROBE_EXE_NAME STDOUT_LOG -- like run-probe.sh but
# WINEBIN points at the workspace copy of the wine tree whose wined3d.dll
# carries the win32-perf map-adoption patch.
set -u
. "$HOME/workspace/win32-perf/scripts/my.env"
WINEBIN=$WP/wine32-patched/wine-11.21-x86/bin/wine
cd "$WP/probes" || exit 1
setsid nohup $SUP $QEMU "$WINEBIN" "Z:\\home\\hatch\\workspace\\win32-perf\\probes\\$1" >> "$2" 2>&1 &
echo "probe sup-pid $!"

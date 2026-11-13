#!/bin/bash
# run-pyprobe.sh PYFILE -- sysroot python3.12 under plain qemu-i386, my env.
set -u
. "$HOME/workspace/win32-perf/scripts/my.env"
cd "$WP/probes" || exit 1
timeout ${PYTIMEOUT:-100} "$Q32_QEMU" -L "$Q32_SYSROOT" "$Q32_SYSROOT/usr/bin/python3.12" "$1"
echo "pyprobe rc=$?"

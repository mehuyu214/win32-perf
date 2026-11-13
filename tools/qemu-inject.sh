#!/bin/sh
# qemu-inject.sh - Q32_QEMU shim: replaces the "-cpu max" pair in the
# q32sup-generated invocation with "-cpu $Q32_CPU_MODEL" (default: passthrough)
# and execs the real 8.2.2-static qemu. Used to A/B guest CPU models stack-wide.
REAL_QEMU=/home/hatch/workspace/vn-trials/qemu/usr/bin/qemu-i386-static
MODEL=${Q32_CPU_MODEL:-max}
out=""
skip=0
for a in "$@"; do
    if [ $skip -eq 1 ]; then out="$out -cpu $MODEL"; skip=0; continue; fi
    if [ "$a" = "-cpu" ]; then skip=1; continue; fi
    out="$out $a"
done
# shellcheck disable=SC2086
exec $REAL_QEMU $out

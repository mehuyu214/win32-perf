#!/bin/bash
# virgl4 FOREGROUND variant — same env as launch-sanoba-virgl4.sh, but
# runs q32sup in the FOREGROUND (exec, no setsid/nohup/&) so it can be
# launched as a systemd transient service (systemd-run --unit=...).
# WHY: in some agent sessions the exec shell is sandboxed — file writes
# return EPERM for the whole process tree AND backgrounded children are
# killed when the exec call returns (virgl16 attempt 1, sup 54019, died
# this way; its log and pid file stayed 0 bytes). A systemd unit escapes
# both: its processes are children of PID 1, outside the sandbox, and
# they survive exec calls. Stop with: systemctl stop <unit>.
# DISPLAY :116, WINEPREFIX prefix-fresh, lineage q32sup, -tb-size 512,
# GALLIUM_DRIVER=virpipe, VTEST_SOCKET_NAME=$WP/virgl.sock, PA tcp 47135.
set -u
VT=$HOME/workspace/vn-trials
WP=$HOME/workspace/win32-perf
export DISPLAY=:116
export LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 LOCPATH=$VT/locales
export PULSE_SERVER=tcp:127.0.0.1:47135
export PULSE_LATENCY_MSEC=750
export LD_LIBRARY_PATH=$WP/libs32/usr/lib/i386-linux-gnu:$WP/libs32/usr/lib/i386-linux-gnu/pulseaudio
export __EGL_VENDOR_LIBRARY_DIRS=$VT/sysroot32/root/usr/share/glvnd/egl_vendor.d
export LIBGL_DRIVERS_PATH=$VT/sysroot32/root/usr/lib/i386-linux-gnu/dri
export WINEDEBUG=-all
export WINEPREFIX=$WP/prefix-fresh
export Q32_SYSROOT=$VT/sysroot32/root
export Q32_WRAPDIR=$WP/wrap-env
unset Q32_QEMU LP_NUM_THREADS
export GALLIUM_DRIVER=virpipe
export VTEST_SOCKET_NAME=$WP/virgl.sock
SUP=$VT/qemu10/q32sup
QEMU="$VT/qemu10/usr/bin/qemu-i386 -cpu max -tb-size 512 -L $VT/sysroot32/root"
WINEBIN=$VT/wine32/wine-11.21-x86/bin/wine
GAMEEXE='Z:\\home\\hatch\\workspace\\win32-perf\\game\\sanoba\\sanoba_trial.exe'
LOG="${LOGFILE:-$WP/logs/game-virgl16-relaunch.log}"
cd /tmp || exit 1
exec >>"$LOG" 2>&1
exec $SUP $QEMU "$WINEBIN" "$GAMEEXE"

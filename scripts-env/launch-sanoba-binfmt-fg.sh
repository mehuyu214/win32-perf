#!/bin/bash
# Sanoba trial launcher, binfmt variant — FOREGROUND, for systemd-run.
# Same env as launch-sanoba-virgl4.sh (DISPLAY :116, WINEPREFIX
# prefix-fresh, PulseAudio tcp 47135, GALLIUM_DRIVER=virpipe,
# VTEST_SOCKET_NAME=$WP/virgl.sock), but WITHOUT q32sup: 32-bit ELFs
# are routed to qemu-i386 8.2.2 by the binfmt_misc rule (see
# register-binfmt-i386.sh). The game runs as a systemd transient
# service so it survives agent exec calls and can write files
# (the agent exec sandbox blocks file writes and kills backgrounded
# children on return; a systemd unit escapes both).
# WHY no q32sup: PTRACE_TRACEME returns EPERM system-wide since
# ~2026-11-14 01:00 JST (proven by a systemd-run test; /proc/sys is
# read-only so no sysctl fix). Without ptrace the supervisor deadlocks
# (parent waits forever, child SIGSTOPped, TracerPid 0).
# qemu options via env (binfmt cannot pass argv): QEMU_CPU=max
# (the launch used -cpu max), QEMU_LD_PREFIX=$VT/sysroot32/root
# (guest 32-bit libs). DEVIATION vs the virgl4 stack: -tb-size 512
# has no qemu-user env equivalent, so the default TB size applies;
# watch for a perf delta in the first story capture.
# Run: systemd-run --unit=virgl16game --setenv=HOME=/home/hatch
#   /home/hatch/workspace/win32-perf/scripts-env/launch-sanoba-binfmt-fg.sh
# Stop: systemctl stop virgl16game (kills the whole cgroup).
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
export QEMU_LD_PREFIX=$VT/sysroot32/root
export QEMU_CPU=max
unset Q32_QEMU LP_NUM_THREADS
export GALLIUM_DRIVER=virpipe
export VTEST_SOCKET_NAME=$WP/virgl.sock
WINEBIN=$VT/wine32/wine-11.21-x86/bin/wine
GAMEEXE='Z:\\home\\hatch\\workspace\\win32-perf\\game\\sanoba\\sanoba_trial.exe'
LOG="${LOGFILE:-$WP/logs/game-virgl16-binfmt.log}"
cd /tmp || exit 1
exec >>"$LOG" 2>&1
exec "$WINEBIN" "$GAMEEXE"

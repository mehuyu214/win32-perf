#!/bin/bash
# virgl4 = virgl3 + AUDIO (KK success gate): PulseAudio recipe from
# sanoba-audio (private daemon on perf port 47135, null sink "game"
# 48kHz f32, PULSE_LATENCY_MSEC=750, guest Audio=pulse in
# prefix-fresh registry, i386 libpulse via libs32). ALSA null dropped.
# GALLIUM_DRIVER=virpipe + VTEST_SOCKET_NAME to the game-facing server
# (virgl_test_server --use-egl-surfaceless, clean env, $WP/virgl.sock).
# DISPLAY :116, WINEPREFIX prefix-fresh, lineage q32sup, -tb-size 512.
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
LOG="${LOGFILE:-$WP/logs/game-virgl12-audio.log}"
cd /tmp || exit 1
setsid nohup $SUP $QEMU "$WINEBIN" "$GAMEEXE" >> "$LOG" 2>&1 &
echo $! > "$WP/logs/game-virgl12-sup.pid"
echo "launched sup-pid $! log=$LOG"

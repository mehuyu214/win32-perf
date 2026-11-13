#!/bin/bash
# Adapted win32-env official recipe (launch-game.sh + env.sh) for the
# win32-perf line ONLY: DISPLAY :116, prefix-fresh, perf game dir.
# Diffs vs my.env/fresh.env, all intentional (Cave Story lead):
#  - ALSA null (asound-null.conf) instead of PulseAudio; NO PULSE_* vars
#  - NO LP_NUM_THREADS, NO GALLIUM_DRIVER (llvmpipe default), NO LD_LIBRARY_PATH
#  - supervisor = vn-trials/qemu10/q32sup (repo lineage), Q32_QEMU UNSET
#    (children under dynamic qemu-i386, not static)
#  - Q32_WRAPDIR = fresh wrap-env dir (no stale wrappers)
#  - DISPLAY :116 (1280x720, already running); WINEPREFIX = prefix-fresh
set -u
VT=$HOME/workspace/vn-trials
WP=$HOME/workspace/win32-perf
export DISPLAY=:116
export LANG=ja_JP.UTF-8 LC_ALL=ja_JP.UTF-8 LOCPATH=$VT/locales
export ALSA_CONFIG_PATH=$HOME/workspace/win32-env/scripts/games/asound-null.conf
export __EGL_VENDOR_LIBRARY_DIRS=$VT/sysroot32/root/usr/share/glvnd/egl_vendor.d
export LIBGL_DRIVERS_PATH=$VT/sysroot32/root/usr/lib/i386-linux-gnu/dri
export WINEDEBUG=-all
export WINEPREFIX=$WP/prefix-fresh
export Q32_SYSROOT=$VT/sysroot32/root
export Q32_WRAPDIR=$WP/wrap-env
unset Q32_QEMU GALLIUM_DRIVER LP_NUM_THREADS PULSE_SERVER PULSE_LATENCY_MSEC LD_LIBRARY_PATH VTEST_SOCKET_NAME
SUP=$VT/qemu10/q32sup
QEMU="$VT/qemu10/usr/bin/qemu-i386 -cpu max -L $VT/sysroot32/root"
WINEBIN=$VT/wine32/wine-11.21-x86/bin/wine
GAMEEXE='Z:\home\hatch\workspace\win32-perf\game\sanoba\sanoba_trial.exe'
LOG="${LOGFILE:-$WP/logs/game-envrecipe-llvmpipe.log}"
cd /tmp || exit 1
setsid nohup $SUP $QEMU "$WINEBIN" "$GAMEEXE" >> "$LOG" 2>&1 &
echo $! > "$WP/logs/game-envrecipe-sup.pid"
echo "launched sup-pid $! log=$LOG"

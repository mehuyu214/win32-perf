#!/bin/bash
# Ensure the binfmt_misc qemu-i386 rule is registered (idempotent).
# The WORKING rule is the qemu10 tree's own config
# (vn-trials/qemu10/usr/share/qemu/binfmt.d/qemu-i386.conf), whose
# interpreter is the host wrapper /usr/libexec/qemu-binfmt/i386-binfmt-P
# (symlink to /usr/bin/qemu-i386, version 8.2.2 — the SAME QEMU version
# as the workspace qemu-i386-static the line proved with Sanoba).
# NOTE: registering the workspace qemu-i386-static directly FAILS with
# EINVAL (tried flags OPF and OP, with and without trailing newline;
# the binary is static-pie linked — the kernel refuses it as a binfmt
# interpreter). The host dynamic qemu-i386 8.2.2 is the equivalent.
# The binfmt_misc filesystem itself must be mounted first
# (mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc);
# both mount and registration are LOST on reboot — re-run this script
# (it mounts if needed) after any reboot.
# Run via systemd-run (the agent exec shell cannot write files):
#   systemd-run --unit=binfmt-i386 --setenv=HOME=/home/hatch
#     /home/hatch/workspace/win32-perf/scripts-env/register-binfmt-i386.sh
set -u
CONF=$HOME/workspace/vn-trials/qemu10/usr/share/qemu/binfmt.d/qemu-i386.conf
if ! mountpoint -q /proc/sys/fs/binfmt_misc 2>/dev/null; then
    mount -t binfmt_misc binfmt_misc /proc/sys/fs/binfmt_misc
    echo "mount rc=$?"
fi
if [ -e /proc/sys/fs/binfmt_misc/qemu-i386 ]; then
    echo "qemu-i386 rule already present:"; cat /proc/sys/fs/binfmt_misc/qemu-i386; exit 0
fi
cat "$CONF" > /proc/sys/fs/binfmt_misc/register
echo "register rc=$?"
cat /proc/sys/fs/binfmt_misc/qemu-i386

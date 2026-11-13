#!/bin/bash
# Build an i386 (32-bit) winex11.so from the patched wine-src, replicating
# the x86_64 build's exact flags with -m32, linking against the stock
# i386 win32u.so/ntdll.so and the sysroot32 X/glibc libraries.
set -u
WP=$HOME/workspace/win32-perf
DEV=$WP/i386dev/root
SR=$HOME/workspace/vn-trials/sysroot32/root
OUT=$WP/build32/winex11
mkdir -p $OUT
cd $WP/build || exit 1
CFLAGS="-m32 -I$DEV/usr/include/x86_64-linux-gnu -I/usr/include/x86_64-linux-gnu -I$DEV/usr/include -Idlls/winex11.drv -I../wine-src/dlls/winex11.drv -Iinclude -I../wine-src/include -D__WINESRC__ -DWINE_UNIX_LIB -Wall -pipe -fcf-protection=none -fvisibility=hidden -fno-stack-protector -fno-strict-aliasing -Wdeclaration-after-statement -Wempty-body -Wignored-qualifiers -Winit-self -Wlogical-op -Wno-packed-not-aligned -Wpointer-arith -Wshift-overflow=2 -Wstrict-prototypes -Wtype-limits -Wunused-but-set-parameter -Wvla -Wwrite-strings -Wno-misleading-indentation -gdwarf-4 -fPIC -fasynchronous-unwind-tables -g -O2 -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0"
FILES="bitblt brush clipboard desktop display event graphics init keyboard mouse opengl palette pen vulkan window wintab x11drv_main xim xinerama xrandr xrender xvidmode"
OBJS=""
fail=0
for f in $FILES; do
  if [ ! -f $OUT/$f.o ]; then
    gcc $CFLAGS -c -o $OUT/$f.o ../wine-src/dlls/winex11.drv/$f.c 2> $OUT/$f.err || { echo "COMPILE FAIL $f"; head -5 $OUT/$f.err; fail=1; }
  fi
  OBJS="$OBJS $OUT/$f.o"
done
[ $fail = 1 ] && exit 1
STOCK=$WP/wine32-patched/wine-11.21-x86/lib/wine/i386-unix
LIBD=$OUT/libsyms; mkdir -p $LIBD
for l in libc.so.6 libm.so.6 libdl.so.2 libpthread.so.0 libgcc_s.so.1 libX11.so.6 libXext.so.6; do
  ln -sf $SR/usr/lib/i386-linux-gnu/$l $LIBD/$l
  ln -sf $SR/usr/lib/i386-linux-gnu/$l $LIBD/${l%.so.*}.so
done
gcc -m32 -Wl,-Bsymbolic -B$DEV/usr/lib32/ -B$DEV/usr/lib/gcc/x86_64-linux-gnu/13/32/ \
  -shared -o $OUT/winex11.so $OBJS \
  $STOCK/win32u.so $STOCK/ntdll.so \
  -L$LIBD -lXext -lX11 -lm -lc -lpthread -ldl $LIBD/libgcc_s.so.1 \
  -L$DEV/usr/lib/gcc/x86_64-linux-gnu/13/32 -lgcc 2> $OUT/link.err || { echo "LINK FAIL"; head -20 $OUT/link.err; exit 1; }
file $OUT/winex11.so
readelf -d $OUT/winex11.so | grep NEEDED

#!/bin/sh
# Track B: configure Mesa 25.2.8 (mesa-src) as i386 cross build into trackb/build.
set -e
TB=$HOME/workspace/win32-perf/trackb
R=$TB/root
export PATH=$TB/pytools/bin:$TB/host-tools/usr/bin:$PATH
export PYTHONPATH=$TB/pytools
export PKG_CONFIG_LIBDIR=$R/usr/lib/i386-linux-gnu/pkgconfig:$R/usr/share/pkgconfig
export PKG_CONFIG_SYSROOT_DIR=$R
export BISON_PKGDATADIR=$TB/host-tools/usr/share/bison
cd $TB
exec nice -n 10 $TB/pytools/bin/meson setup build $HOME/workspace/win32-perf/mesa-src \
  --cross-file $TB/cross.ini \
  --prefix=/usr --libdir=lib/i386-linux-gnu \
  --buildtype=release -Db_lto=false \
  -Dgallium-drivers=llvmpipe,softpipe \
  -Dvulkan-drivers= \
  -Dplatforms=x11 \
  -Dopengl=true -Dglx=dri -Degl=enabled -Dgbm=enabled \
  -Dgles1=disabled -Dgles2=disabled \
  -Dglvnd=enabled \
  -Dllvm=enabled -Dshared-llvm=enabled \
  -Dlibunwind=disabled -Dlmsensors=disabled \
  -Dbuild-tests=false -Dtools= \
  -Dgallium-va=disabled -Dgallium-vdpau=disabled \
  -Dmicrosoft-clc=disabled \
  -Dzstd=enabled

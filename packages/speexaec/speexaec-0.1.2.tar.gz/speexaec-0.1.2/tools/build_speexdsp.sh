#!/usr/bin/env bash
set -euxo pipefail

yum -y update
# Dependencias de autotools y toolchain en manylinux2014 / 2_28
yum -y install autoconf automake libtool make gcc gcc-c++ pkgconfig

export CFLAGS="-O3 -fPIC"
export CXXFLAGS="-O3 -fPIC"

cd submodule/speexdsp
# Algunos trees ya traen configure, autogen puede fallar si no hay git; no parar si falla
./autogen.sh || true
./configure --prefix=/usr/local --enable-shared --disable-static
make -j"$(nproc)"
make install

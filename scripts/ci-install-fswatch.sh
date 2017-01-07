#!/bin/sh
set -e

fswatch_version="1.4.6"

wget https://github.com/emcrisostomo/fswatch/releases/download/${fswatch_version}/fswatch-${fswatch_version}.tar.gz
tar xzf fswatch-${fswatch_version}.tar.gz
cd fswatch-${fswatch_version}
./configure
make
make install

#!/bin/bash
meson setup build --prefix=/usr --libdir=/usr/lib
ninja -C build install


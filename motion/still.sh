#!/bin/sh
# usage: ./still.sh 120 650 ...   -> ../render/stills/fNNNN.png
B=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
npx remotion bundle src/index.ts --out-dir=/tmp/rbundle >/dev/null 2>&1
for f in "$@"; do npx remotion still /tmp/rbundle Commercial ../render/stills/f$(printf %04d $f).png --frame=$f --browser-executable=$B >/dev/null 2>&1 || echo "fail $f"; done

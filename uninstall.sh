#!/bin/bash
# Turns the video background off and removes everything install.sh and the
# command ever created: the command, its data, its service and its cache.

set -euo pipefail

if command -v cows-background >/dev/null; then
  cows-background off --purge
fi
rm -f "$HOME/.local/bin/cows-background"
rm -rf "${XDG_DATA_HOME:-$HOME/.local/share}/cows-background"
rm -rf "${XDG_CACHE_HOME:-$HOME/.cache}/cows-background"
echo "cows-background removed."

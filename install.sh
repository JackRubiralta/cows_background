#!/bin/bash
# Installs the cows-background command for the current user.
#   ~/.local/bin/cows-background
#   ~/.local/share/cows-background/{lib,videos}
# Nothing runs and nothing about the desktop changes until `cows-background on`.

set -euo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
share="${XDG_DATA_HOME:-$HOME/.local/share}/cows-background"

install -Dm755 "$here/bin/cows-background" "$HOME/.local/bin/cows-background"
install -Dm755 "$here/lib/find-loop.py" "$share/lib/find-loop.py"
mkdir -p "$share/videos"
install -m644 "$here"/videos/*.conf "$share/videos/"

missing=()
for cmd in mpvpaper ffmpeg yt-dlp python3; do
  command -v "$cmd" >/dev/null || missing+=("$cmd")
done
python3 -c 'import numpy' 2>/dev/null || missing+=(python-numpy)

echo "Installed: ~/.local/bin/cows-background"
if ((${#missing[@]})); then
  echo "Still needed: omarchy pkg add ${missing[*]}"
fi
echo "Try: cows-background on        (cows-background off to undo)"

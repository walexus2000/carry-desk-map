#!/bin/sh
# Publish the Carry Desk map to GitHub Pages.  usage: sh publish.sh "commit message"
# Reads the push token from .push-token (or .push-token.txt) in this folder — git-ignored, never leaves this PC.
W="$HOME/mnt/carry-desk-map"
export GIT_DIR="$HOME/cdm.git" GIT_WORK_TREE="$W"       # metadata lives outside the mount: git cannot delete lock files there
TOK=""
for f in "$W/.push-token" "$W/.push-token.txt"; do [ -f "$f" ] && TOK=$(tr -d ' \t\r\n' < "$f") && break; done
[ -n "$TOK" ] || { echo "no push token found in $W (.push-token or .push-token.txt)"; exit 1; }
if [ ! -d "$GIT_DIR" ]; then
  git init -q && git remote add origin https://github.com/walexus2000/carry-desk-map.git
fi
git fetch -q origin main && git reset -q origin/main || { echo "fetch failed"; exit 1; }
git add -A
git -c user.name="Wale (via Claude)" -c user.email="walexus2000@gmail.com" commit -qm "${1:-Carry Desk map refresh}" 2>/dev/null || { echo "nothing to publish"; exit 0; }
git push -q "https://x-access-token:${TOK}@github.com/walexus2000/carry-desk-map.git" HEAD:main && echo "published $(git rev-parse --short HEAD)"

#!/usr/bin/env bash
# Watch the art-inbox branch for deliveries the game branch has not taken yet (cloud session; docs/pc_cloud_protocol.md section 7).
#   tools/art/watch_inbox.sh [seconds]      default: poll every 60 s
# Prints one line whenever the set of unreviewed paths changes - stateless: "unreviewed" = paths under art/inbox that differ
# between HEAD and origin/art-inbox, so restarting the watcher never loses or repeats a delivery. Then: python3 tools/art/receive.py --list
cd "$(dirname "$0")/../.." || exit 1
every="${1:-60}"
last=""
while true; do
  git fetch -q origin art-inbox 2>/dev/null
  cur=$(git diff --name-only HEAD origin/art-inbox -- art/inbox 2>/dev/null | tr '\n' ' ')
  if [ -n "$cur" ] && [ "$cur" != "$last" ]; then
    echo "ART_INBOX_UNREVIEWED: $cur| tip: $(git log -1 --format='%h %s' origin/art-inbox)"
  fi
  last="$cur"
  sleep "$every"
done

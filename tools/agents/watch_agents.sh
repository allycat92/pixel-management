#!/usr/bin/env bash
# Cloud lead: watch the helper agents' branches (origin/agent/*) for new commits.
#   tools/agents/watch_agents.sh [seconds]     default: poll every 60 s
# Prints one line per branch whose tip differs from the last tip the lead ACKNOWLEDGED (kept in <git dir>/agent-watch/<name>).
# Acknowledge after reviewing:  tools/agents/watch_agents.sh --ack            (records the current tips)
# Stateless otherwise: restarting never loses a change; an unacknowledged tip is reported once per watcher run and whenever it moves.
cd "$(dirname "$0")/../.." || exit 1
dir="$(git rev-parse --git-common-dir)/agent-watch"; mkdir -p "$dir"
tips() { git for-each-ref --format='%(refname:short) %(objectname:short)' 'refs/remotes/origin/agent/*'; }
if [ "$1" = "--ack" ]; then
  git fetch -q origin '+refs/heads/agent/*:refs/remotes/origin/agent/*' 2>/dev/null
  tips | while read -r ref tip; do echo "$tip" > "$dir/$(echo "$ref" | tr '/' '_')"; done
  echo "acknowledged: $(tips | tr '\n' ' ')"; exit 0
fi
every="${1:-60}"
declare -A said
while true; do
  git fetch -q origin '+refs/heads/agent/*:refs/remotes/origin/agent/*' 2>/dev/null
  while read -r ref tip; do
    [ -z "$ref" ] && continue
    f="$dir/$(echo "$ref" | tr '/' '_')"; ack="$(cat "$f" 2>/dev/null)"
    if [ "$tip" != "$ack" ] && [ "${said[$ref]}" != "$tip" ]; then
      echo "AGENT_BRANCH_UPDATED: ${ref#origin/} ${ack:-new}..$tip | $(git log -1 --format='%s' "$ref")"
      said[$ref]="$tip"
    fi
  done < <(tips)
  sleep "$every"
done

#!/usr/bin/env python3
# ASCII ONLY (this file is piped through Windows shells): Korean literals are written as \u escapes.
"""Block until the queues hold NEW work for one agent, then print the row ids and exit.

  python tools/agents/wait_for_work.py --agent antigravity|codex|gpt [--interval 60] [--max-minutes 20] [--now] [--reset]

Run it from any clone / any branch (it only reads origin/<game branch> through git):
  git fetch origin
  git show origin/claude/dot-fantasy-management-game-saupju:tools/agents/wait_for_work.py | python - --agent antigravity

What counts as work (read from the game branch, never from the working tree):
  antigravity  art/requests/dot_queue.md "now" rows whose first column is Antigravity / PC / GPT (all art rows are
               Antigravity's since 2026-11-26), except kinds "hold" and "notice"; plus docs/agents/queue.md rows of Antigravity
  codex, gpt   docs/agents/queue.md rows of that owner whose status starts with READY or FIX
The script remembers the rows it last reported (in <git dir>/agent-wait/<agent>.seen). It returns at once when the rows
differ from that memory and are not empty; otherwise it fetches every --interval seconds until they change.
First line of the output:
  WORK <n>       new or changed rows: re-read the queue and do them (ids follow, one per line)
  IDLE           nothing new after --max-minutes: just run the same command again (keeps tool timeouts short)
Exit code is 0 in both cases; 2 on a usage or git error.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
import time

GAME = 'claude/dot-fantasy-management-game-saupju'
HOLD = ('\ubcf4\ub958', '\uc608\uace0')          # "hold", "notice" kinds in dot_queue: not work
OWNERS = {'antigravity': 'Antigravity', 'codex': 'Codex', 'gpt': 'GPT'}


def git(*args):
    return subprocess.run(['git'] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def show(path):
    r = git('show', 'origin/%s:%s' % (GAME, path))
    return r.stdout.decode('utf-8', 'replace') if r.returncode == 0 else ''


def art_rows():
    rows = []
    for line in show('art/requests/dot_queue.md').splitlines():
        m = re.match(r'^\|\s*(Antigravity|PC|GPT)\s*\|\s*([^|]+?)\s*\|\s*([^|]*)\|', line)
        if m and m.group(2) not in HOLD:
            rows.append(('art', ' '.join(re.findall(r'`([^`]+)`', m.group(3))) or m.group(3).strip(), line))
    return rows


def agent_rows(owner):
    rows = []
    for line in show('docs/agents/queue.md').splitlines():
        m = re.match(r'^\|\s*%s\s*\|\s*`([^`]+)`\s*\|\s*([^|]*)\|' % re.escape(owner), line)
        if m and re.match(r'(READY|FIX)\b', m.group(2).strip()):
            rows.append(('task', m.group(1), line))
    return rows


def rows_for(agent):
    owner = OWNERS[agent]
    return (art_rows() if agent == 'antigravity' else []) + agent_rows(owner)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--agent', required=True, choices=sorted(OWNERS))
    ap.add_argument('--interval', type=int, default=60)
    ap.add_argument('--max-minutes', type=float, default=20)
    ap.add_argument('--now', action='store_true', help='check once, do not wait')
    ap.add_argument('--reset', action='store_true', help='forget what was reported before')
    a = ap.parse_args()
    r = git('rev-parse', '--git-common-dir')
    if r.returncode != 0:
        print('ERROR not a git repository - run this inside your clone of pixel-management')
        return 2
    state_dir = os.path.join(os.path.abspath(r.stdout.decode().strip()), 'agent-wait')
    os.makedirs(state_dir, exist_ok=True)
    seen_path = os.path.join(state_dir, a.agent + '.seen')
    if a.reset and os.path.exists(seen_path):
        os.remove(seen_path)
    deadline = time.time() + a.max_minutes * 60
    while True:
        git('fetch', '-q', 'origin', GAME)
        rows = rows_for(a.agent)
        digest = hashlib.sha1('\n'.join(x[2] for x in rows).encode('utf-8')).hexdigest()
        seen = open(seen_path).read().strip() if os.path.exists(seen_path) else ''
        if rows and digest != seen:
            with open(seen_path, 'w') as f:
                f.write(digest)
            print('WORK %d' % len(rows))
            for kind, rid, _ in rows:
                print('%s %s' % (kind, rid.encode('ascii', 'replace').decode()))
            print('-> read art/requests/dot_queue.md and docs/agents/queue.md on origin/%s and continue' % GAME)
            return 0
        if a.now or time.time() >= deadline:
            print('IDLE')
            print('-> nothing new; run the same command again to keep waiting')
            return 0
        time.sleep(max(5, a.interval))


if __name__ == '__main__':
    sys.exit(main())

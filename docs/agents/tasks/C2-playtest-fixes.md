# C2 — 플레이테스트에서 나온 자잘한 오류 고치기 (Codex)

## Why
Antigravity's playtest report `docs/agents/reports/antigravity.md` (section "A1 — 2026-11-26", screenshots under
`docs/agents/reports/shots/A1/`). The lead triaged it. The items below are small, self-contained fixes. Everything about battle
formation / clumping, growth pacing and art style is NOT in this task: the lead handles those in the battle-stats and tactics work.

## Fix these (report item numbers in brackets)
1. [1/9] Starter-captain modal: at phone width (400 px) the cards must stack in one column. A later
   `.starter-choices { grid-template-columns: repeat(3, 1fr) }` rule overrides the `@media (max-width: 760px)` rule. On desktop,
   remove the double scroll and make it obvious there are 9 candidates (show a clear part of the next row, or fit 3 rows).
2. [3] Final-battle contract card shows `마감까지 99894일`. A contract with no deadline (`c.final`, story expiry 99999) must
   show `마감 없음`. Check the other places that print days left.
3. [4] Roster capacity:
   - Recruited captains push the count over the cap (`단원 7/6`). Decide by reading the code how captains are meant to count,
     and make the number and the cap consistent. If captains do not use beds, do not count them. If they do, say so in the
     join message.
   - Reserve captains (not assigned to any company) must not lose morale from the "7 days without a sortie" rule.
4. [2] Skill cut-in: the gold top/bottom bars spill outside the battle canvas. Clip to the battle stage. Do not change the
   cut-in timing or art.
5. [10] Captain recruitment / join dialogs use the red `boss` portrait frame. Allied captains get the allied (gold) frame.
   A narration line (`who: null`) must not show a captain portrait as if that captain were speaking.
6. [11] Recruit tab: put 「대원 모집」 and the market above the long captain roster (or collapse the captain roster by
   default) so a new player finds ordinary recruitment at once.
7. [14] Korean line breaks:
   - `.company-status` must not split `귀환` (`출격 중 · 1일 후 귀환` on one line, or break between words).
   - The class tree needs `word-break: keep-all`.
8. [16] Wording:
   - `바렌와(과) 시작한다`: pick 와/과 by the final consonant. Add a small helper and use it wherever `와(과)`, `을(를)`,
     `이(가)`, `은(는)` are hard-coded.
   - `빚이 -300을 넘으면` -> `금화가 -300 아래로 떨어지면`.
   - Day-1 faction tab: `0일째` and `평판 하락 -0%` -> sensible text.
   - `마감까지 0일` -> `오늘 마감`.
9. [8] Battle side panel: enemy groups with the same name get a number (`고블린 무리 1`, `고블린 무리 2`). When trainees are
   auto-added to reach the minimum group size, the panel must not look like a mismatch with the dispatch (mark them, e.g.
   `2 + 수습 1`).
10. [3 in the full list] `favicon.ico` 404: add a tiny favicon (generate a 16x16/32x32 PNG from our own palette; do not use
    third-party art) and link it.
11. [13] Guild hall: the `의뢰 수행 중: N명` text overlaps the walking sprites. Move it or give it a backing so both read.
    Phone width: make it visible that the tab bar scrolls (the last tabs are hidden).
12. [15] Map labels with weak contrast (`서리 협곡`, `안개 늪`, `용의 등뼈`): give labels a consistent outline/backing. The lock
    icon must not overlap the capital star.

## Do not touch
- `js/battle.js` sim rules (movement, targets, damage). The cut-in clip (item 4) and the side-panel labels (item 9) are
  view-only.
- `assets/`, `art/`.

## Checks
- `node tools/sim/battle.js 100` (miss=0 x4). `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum` must be identical before and
  after, unless item 3 changes the bot's game. Reserve-captain morale may do that. If it does, show the before/after bot
  summary and explain.
- Browser at 1280x900 and 400x800: screenshot each fixed spot (before/after) into `docs/agents/reports/shots/C2/`
  (each < 500 KB). No console errors.

## Deliver
Branch `agent/codex` (merge `origin/claude/dot-fantasy-management-game-saupju` in first). Report section `## C2 — <date>` in
`docs/agents/reports/codex.md`: one line per item (fixed / not fixed + why). Set the row to REVIEW. Push.

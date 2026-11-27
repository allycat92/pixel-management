# C3 — 숙소가 가득 찼을 때 특별 용병·정예 영입 버튼 (Codex)

## Why
GPT-QA found it while verifying C2 (`docs/agents/reports/gpt-qa.md`, "추가 개선"): with the lodging full (6/6), the hire button of a
special mercenary (e.g. 카이) in the recruit tab is still enabled; clicking only shows "숙소가 가득 찼습니다. 숙소를 증축하세요."
Ordinary recruits already get a disabled button.

## What to do
- Every hire button that needs a lodging slot (special mercenaries, elites, anything that uses the same capacity rule as ordinary
  recruits) is disabled when the lodging is full, with the reason shown next to it (same wording/style as the ordinary recruit button).
- Captains do not use lodging (C2 decision) - their recruitment stays as it is.
- No rule changes: only the button state and the hint.

## Checks
`node tools/sim/battle.js 100` (miss=0 x4), `SIM_JSON=1 node tools/sim/bot.js 6 200 | md5sum` identical before/after.
Browser at 1280 and 400 px: full lodging -> buttons disabled with the reason; one free slot -> enabled. Screenshots in
`docs/agents/reports/shots/C3/`.

## Deliver
Branch `agent/codex` (merge the game branch in first), report section `## C3 — <date>`, row to REVIEW, push.

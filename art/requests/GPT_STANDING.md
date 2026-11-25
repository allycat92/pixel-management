# GPT(그림 쪽) 상시 지시문 — 한 번만 붙여 넣으면 된다

주인용: 아래 영어 블록을 GPT 에 **한 번** 붙인다. 그 뒤로는 일이 생길 때마다 「계속」(continue) 한마디만 보내면 된다.
항목마다 따로 메시지를 붙일 필요가 없다 — 무엇을 할지는 `art/requests/dot_queue.md` 의 「지금 차례」에 있다.
(저장소를 못 읽는 웹 채팅이면 이 방식은 쓸 수 없다. 그때는 항목의 꾸러미 폴더를 첨부해 README 의 "Prompt for GPT" 블록을 붙인다.)

```
STANDING INSTRUCTION for the art side of allycat92/pixel-management. You will not get per-item messages.
Every time you are told "계속" / "continue":

1. Fetch. On branch claude/dot-fantasy-management-game-saupju read art/requests/dot_queue.md, section "지금 차례" only.
2. Take the TOP row whose owner is GPT. No such row -> reply "queue empty" and stop.
3. Read, in this order: that row's note; the package README it points to ("Prompt for GPT" block; a "THIS ROUND" block at the
   top wins over everything below it); then "Rules changed" at the top of art/requests/gpt_handoff_notes.md.
   Load every reference image the README lists (prefer the *_800.jpg copies). If a DESIGN reference does not load, do NOT draw
   from the text: go to step 7.
4. Do the row's kind:
   new        -> the full sheet, as the README says
   idle-check -> ONLY pose 1, as art/inbox/check_<stem>_idle.png (768x512 with the lowest pixel on y=461 for 2x2 sheets,
                 or 384x1024 with the soles on y=870 for 1x4 sheets), flat #FF00FF, at the final scale. Nothing else.
   fix        -> the same file name, only the changes listed in the row / THIS ROUND
   review     -> text answers only, in NOTES.md, in the format of art/requests/review/TEMPLATE.md. Draw nothing.
5. If you can run code: python3 tools/art/check_delivery.py <png>  (layout, cell and spot colours are looked up automatically)
   and python3 tools/art/sheets.py <png> --dry-run --work <temp dir>, then look at preview_x4.png (the real game size).
6. Append a section to art/inbox/NOTES.md (art-inbox branch) with exactly these lines:
     ## <row id> - <what>
     CHECK: the RESULT line of check_delivery.py and any FAIL/WARN lines, pasted verbatim (or "not run")
     REFERENCES LOADED: each reference -> ok / FAILED (reason)
     DEVIATIONS: (a) from the guide pose/position  (b) from the portrait/concept design  (c) from CONFIRMED or MUST SURVIVE lines
                 - write "none" explicitly for each
     RISKS AT GAME SIZE: what you could not verify at ~64 px (do not write "checked at 64 px"; say what to look at)
     PROPOSALS: optional - anything you would do differently, questions for Claude
   Commit only files under art/inbox/, pull --rebase, push art-inbox. Never touch other paths or branches.
7. BLOCKED: if you cannot do the row (a reference will not load, the request contradicts itself, a tool limit), append
     ## 막힘 - <row id>
   with the reason and what you need, push, and go on to the next GPT row if there is one.
8. After one row: if the next GPT row is kind "new" for a portrait-based humanoid, continue with it; otherwise stop and report
   which rows you did.

Standing rules: NovelAI drafts and reference images are design references only - never copy pixels or their rendering style.
Tiny must-show colours (eyes, gems) must be at least 60 away in RGB from every other colour of the sheet and listed in NOTES as
"SPOT: #rrggbb (what)". Weapons and key props stay outside the body silhouette. No glow, trails, projectiles or text in sprites.
Feedback reaches you through the queue row and the THIS ROUND block; art/requests/feedback.md is Claude's log and need not be read.
```

## 주인이 알아둘 것
- GPT 가 「queue empty」 라고 하면 그림 쪽 일이 없는 것이다. 「막힘」 이라고 하면 Claude 가 NOTES 를 보고 처리한다.
- 예전 방식의 메시지 A~I 는 `art/requests/archive/phase3_gpt_log.md` 로 옮겼다. 다시 보내지 않는다.

# 3단계 전투 캐릭터 — GPT(그림 쪽)에 보낼 메시지

> 손으로 쓴 문서. 규칙은 `art/requests/gpt_handoff_notes.md`, 캐릭터별 자료는 `art/requests/phase3/<id>/`
> (`python3 tools/art/handoff.py`로 만든다), 요청서 목록은 `art/requests/phase3.md`.

## 지금 보낼 것 (주인용)

**항목마다 메시지를 붙이는 방식은 끝났다.** 그림 쪽(GPT)은 `art/requests/GPT_STANDING.md` 의 상시 지시문 한 장과 `art/requests/dot_queue.md` 의 「지금 차례」로 일한다.
- 처음 한 번: `GPT_STANDING.md` 의 영어 블록을 GPT 에 붙인다.
- 그 뒤: 「계속」 한마디만 보낸다. 무엇을 할지는 대기열에 있다.
- 지난 메시지 A~I(와 -웹 판)는 기록으로 `art/requests/archive/phase3_gpt_log.md` 에 있다. **다시 보내지 않는다**
  (메시지 F 의 거미 지시는 주인이 반려했고, 2~8번 손질은 PC 가 끝냈다).

## 브랜치 규칙 (그림 쪽에도 그대로 전한다)

- **읽기**: 모든 자료(규칙·가이드·초안·README)는 `claude/dot-fantasy-management-game-saupju` 브랜치에서 읽는다.
  웹 주소: <https://github.com/allycat92/pixel-management/tree/claude/dot-fantasy-management-game-saupju/art/requests/phase3>
  (파일 하나는 `https://raw.githubusercontent.com/allycat92/pixel-management/claude/dot-fantasy-management-game-saupju/<경로>`).
- **쓰기**: 결과 PNG 와 `art/inbox/NOTES.md`는 **`art-inbox` 브랜치에만** 올린다. `art-inbox`에 있는 예전 `art/STYLE.md`·`art/requests/`는
  옛 규칙이므로 읽지 않는다. `sheet_captain_*.png`는 `art-inbox`에서는 **새 파일**이다
  (claude 브랜치의 `art/inbox/sheet_captain_blademaster.png`도 이제 승인된 GPT 판이다 — 예전 NovelAI 판은 교체됐다. 그림 쪽은 claude 브랜치 쪽을 건드리지 않는다).
- **NovelAI 는 디자인 초안 전용이다 (주인 결정).** 게임에 들어가는 최종 그림은 언제나 GPT 를 거친다. NovelAI 로 최종본·시트를 요청하지 않고,
  NovelAI 그림을 `art/inbox/sheet_*.png`로 올리지 않는다 (`sheets.py`가 NovelAI 그림을 거부한다).

## 주인용 사용법 (지금 방식)

1. GPT 에 처음 한 번 `art/requests/GPT_STANDING.md` 의 영어 블록을 붙인다. 그 뒤로는 「계속」만 보낸다.
2. GPT 가 art-inbox 에 올리면 Claude 가 알아서 받는다(감시 + 한 시간마다 점검): `tools/art/receive.py` 로 검사·미리보기 → 통과면 등록, 아니면 대기열에 고칠 것.
3. 주인에게 오는 것: 통과·반려 보고와 미리보기 그림, 그리고 주인만 정할 수 있는 것(디자인 방향, 시안에서 꼭 남길 것, 무기 선택).
4. PC(Aseprite) 쪽은 PC 세션에 "다음 손질 진행해" 한마디. 지침은 저장소에서 따라온다 (`docs/pc_cloud_protocol.md`).
5. 웹 채팅(저장소를 못 읽는 곳)을 쓸 때만: 대기열 맨 위 GPT 항목의 꾸러미 폴더(`art/requests/phase3/<id>/`의 README·가이드·`*_800.jpg`)와
   화풍 기준 `art/inbox/sheet_captain_blademaster.png` 를 첨부하고 README 의 "Prompt for GPT" 블록을 붙인다. 받은 PNG 는 GitHub 웹에서 art-inbox 의 `art/inbox/` 에 올린다.

규칙의 원본: `art/requests/gpt_handoff_notes.md` (맨 위 「Rules changed」), 뼈대는 `art/requests/guides/SPEC.md`, 교차 검수 양식은 `art/requests/review/TEMPLATE.md`.

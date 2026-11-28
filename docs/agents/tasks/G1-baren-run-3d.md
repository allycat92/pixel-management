# G1 — 바렌 달리기 8프레임, 3D 마네킹 위에 그리기 (GPT 대리, 그림)

**주인 11-28 (주인이 총괄에게 한 말 그대로: 「안티그래비티가 한도에 도달해서 그런데 gpt쪽으로 대리해서 넘겨줘」):** Antigravity 가 사용 한도에 걸려 **GPT 가 대리로 그린다.** 허용 범위는 `docs/agents/GPT_QA_STANDING.md` 의 ART EXCEPTION 에 적었다. 이 일감에 한해 GPT 는 그림을 그리고 `art-inbox` 브랜치에 납품할 수 있다(그 밖의 그림 일은 여전히 Antigravity 담당).

- 요청서: `art/requests/gait/run__captain_blademaster/README.md` — 그대로 따른다(3D 마네킹 안내 그림, 관절 위치 `pose.json`, 크기 비교, 미리보기 GIF).
- 바렌 모습: `art/requests/phase3/captain_blademaster/concept.png`, `portrait.png`, 등록 시트 `assets/art/sheets/sheet_captain_blademaster.png`, art-inbox 의 원본 `art/inbox/sheet_captain_blademaster.png`.
- 꼭 지킬 것(요청서에 자세히):
  - 마네킹 픽셀은 **전부 덮어 그린다** — 안내 그림을 그대로/색만 바꿔 내면 `add_gait.py` 가 거부한다.
  - 원근: 밝은 쪽(가까운 팔다리)이 어두운 쪽(먼 쪽)을 가린다. 무기·몸·얼굴이 겹치는 것은 괜찮고, 가까운 쪽이 위에 그려지면 된다.
  - 무기는 팔뚝 기준 0~120° 안(안내 그림 그대로면 지켜진다). 칼끝이 바닥선 아래로 내려가면 그릴 때 바닥 위로 손본다.
  - 색 바꾸기만 한 에셋은 안 된다. NovelAI 그림은 쓰지 않는다(시안 전용).
  - 각 칸을 1배·4배로 따로 보며 다리·팔이 잘리거나 어긋난 곳이 없는지 본다(이음매 검사, `check_delivery.py` 가 경고).
- 납품: `art-inbox` 브랜치에 `art/inbox/gait/sheet_captain_blademaster_run_a.png`(R1~R4) + `_b.png`(R5~R8), `art/inbox/NOTES.md` 에 「gait/sheet_captain_blademaster_run - 바렌 이동」 절과 한 줄 「3D GUIDE: 도움 된 점 / 헷갈린 점」.
- 스스로 검사: `python3 tools/art/check_delivery.py ...`·`python3 tools/art/add_gait.py sheet/captain/blademaster --gait run --src <a> <b> --pose art/requests/gait/run__captain_blademaster/pose.json --dry-run` (요청서의 명령 그대로).
- 판단은 주인이 한다. 클라우드는 기술 검사만 하고 주인에게 보여 준다.
- `docs/agents/queue.md` 의 이 줄을 REVIEW 로 바꾸고 `agent/gpt-qa` 에 짧은 보고(`gpt-qa.md` G1 절).

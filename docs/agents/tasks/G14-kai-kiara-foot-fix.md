# G14 — 카이·키아라 달리기 디딘 발 손질 (GPT, 그림 손질)

주인 11-28: 「고칠거는 고치게 해줘」. 허용 범위: `docs/agents/GPT_QA_STANDING.md` ART EXCEPTION.

Q28 (`gpt-qa.md` Q28 절, `shots/Q28/09-foot-detail-2x.jpg`)에서 잰 것:
- **카이 R6→R7:** R7 의 디딘 발 밑창 중심이 R6 보다 시트에서 약 22px 뒤 — 화면에서 약 10px 미끄러짐(여러 시드에서 같은 방향). R7 의 디딘 발(과 그에 붙은 다리)을 안내 그림 `art/requests/gait/run__hero_kai/` 의 R7 접점 x 로 옮긴다. 몸·옷·활은 그대로.
- **키아라 R5→R6:** ×4 에서 전진 잔차 +7.5px(재관전 +5.5px). R5·R6 의 디딘 발 밑창 중심을 안내 그림 접점 x(요청서 README 의 접점 줄)에 다시 맞춘다.
- 다른 칸은 건드리지 않는다. 손질 전/후 디딘 발 접점 x 를 칸마다 적는다(1px 단위).

납품: art-inbox 의 같은 파일 이름(`art/inbox/gait/sheet_hero_kai_run_a/_b.png`, `sheet_captain_huntress_run_a/_b.png`)을 덮어 쓰고, NOTES.md 의 각 절에 「손질(G14)」 한 줄. 스스로 검사는 요청서 명령 그대로. 이 줄을 REVIEW 로, `gpt-qa.md` G14 절. 판단은 주인.

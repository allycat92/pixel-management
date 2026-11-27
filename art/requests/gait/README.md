# 이동 요청 — 부류 마네킹 위에 프레임마다 덧그리기 (그림: Antigravity)

**왜 (주인 2026-11-26)**: "달리기를 실제 캐릭터 그래픽에 적용할때 캐릭터가 찌그러져 보여. 아마 스탠딩 원화(혹은 기준 에셋)를 조작하는것보다는
스켈레톤 혹은 마네킹 기준으로 덧그리게 하는게 확실할걸. 그러려고 스프라이트식으로 하자고 한거고"
→ 대기 그림을 잘라 기울이는 코드 이동 대신, 시트의 **이동 부류 마네킹** 8프레임 위에 캐릭터를 프레임마다 그린다. 그린 그림은 찌그러뜨리지 않는다.
그림은 Antigravity 가 그린다(주인 2026-11-26: 그림 전담 — `docs/agents/README.md` 「그림 전담」). 요청서 README 의 Prompt 블록이 Antigravity 에게 가는 글이다.

## 이동 부류 세 가지 (주인 2026-11-26)
> "달리기(이동)에 대해 3가지 부류를 정하고 싶어. 경량, 중량, 로브. 펑퍼짐한 천 복장을 입고 뛰는것도 좀 부자연스러울거고,
> 중장비를 갖추면 당연히 뛰는건 물론이고 몸이 저렇게 땅에서 떨어지거나 몸을 앞으로 기울인 채로 가누기도 어려울테니까."

세 부류 모두 **그 몸이 낼 수 있는 가장 빠른 이동**이다(전투 이동은 달리기 — 산책이 아니다). 시트마다 부류 하나 — 원본 `tools/art/specs/gait_classes.json`
(시트마다 까닭과 경계 사례). 현황: `python3 tools/art/gait_requests.py`.

| 부류 | 몸 | 덧그리는 마네킹 (확정) | 요청 폴더 | 느낌 |
|---|---|---|---|---|
| **경량** light | 가죽·천(무릎까지)·사슬 셔츠+겉옷, 다리가 보이는 망토·열린 긴 외투 | `art/requests/guides/run_base/v2/` R1~R8, 80ms, 한 걸음 원본 275px = 게임 45.5px, 뜸 R4·R8 | `run__<시트>/` | 앞으로 기울고, 뜬 동안 누르고, 받아낸 뒤 조금 오른다. 엉덩이는 거의 수평, 깡충거리지 않는다 |
| **중량** heavy | 판금·온몸 금속·비늘 갑옷, 탑 방패, 아주 큰 무기를 든 몸 | `art/requests/guides/heavy_base/v1/` H1~H8, 101ms, 한 걸음 142.5px = 게임 23.6px | `heavy__<시트>/` | 뜨는 칸이 없다(늘 한 발은 땅, H1·H5 두 발), 몸은 거의 선다(5도), 디딜 때(H2·H6) 무게로 가라앉는다, 무릎 낮게, 보폭 짧게 |
| **로브** robe | 무릎 아래까지 오는 긴 로브·사제복·긴 망토로 무릎·허벅지가 가려진 몸 | `art/requests/guides/robe_base/v1/` G1~G8, 96ms, 한 걸음 134.2px = 게임 22.2px, `cloth_front` 옷자락 레이어 | `robe__<시트>/` | 서두르는 미끄럼 걸음, 뜨지 않음(G1·G5 두 발), 7도 기울기, 옷자락이 한 칸 늦게 흔들리며 무릎을 늘 가린다 |
| 해당 없음 none | 네발·다족·떠 있는 몸 (들늑대·거대 거미·가고일·망령·하피) | — (엔진의 quad·hover 움직임) | — | — |

- **엔진에는 부류와 상관없이 시트의 `anims.run` 한 줄로 붙는다**: 납품 `art/inbox/gait/<시트 png 이름>_run_a.png` + `_b.png`,
  붙이기 `add_gait.py <시트 id> --gait run --src … --pose <부류 마네킹 pose.json>` (`gait_requests.py --json` 에 시트마다 명령). 요청 폴더 머리(`run__`/`heavy__`/`robe__`)는 사람이 부류를 알아보라고 붙인 것이다.
- 엔진(`js/battle.js` `gaitClassOf`)은 시트 `meta.gait`(add_gait 가 pose.json 에서 적는다) → `js/gait_classes.js` → 경량 순으로 부류를 안다.
  그려진 칸이 없는 시트는 그림을 바꾸지 않고 몸 전체만 부류대로 오르내린다.
- **디딘 발 규칙** (병과 전사 R5 를 한 번 고친 까닭): 엔진은 디딘 칸마다 유닛을 한 걸음의 1/4 만큼 나아가게 한다. 그래서 그림에서도 땅에 디딘 발은
  **칸마다 정확히 step/4 만큼 왼쪽으로**(경량 68.8px · 중량 35.6px · 로브 33.5px, ±3) 옮겨 그려야 게임에서 발이 땅에 붙어 있다. 요청서마다 칸 좌표의 발끝 x 표가 있고,
  `size_*.png` 에 노란 눈금으로 찍혀 있다. (전사 R5 는 디딘 발이 R1 보다 약 30px 앞에 그려져 R5→R6 에서 게임 5px 미끄러졌다 → 발 x 297 → 265 로 고침.)

## 요청 목록

<!-- index:start (gait_requests.py --index) -->
| 요청 | 시트 | 부류 · 마네킹 | 납품 (art-inbox) | 상태 |
|---|---|---|---|---|
| [`heavy__captain_dragonslayer/`](heavy__captain_dragonslayer/README.md) | `sheet/captain/dragonslayer` 지크린데 이동 | 중량 · `art/requests/guides/heavy_base/v1` | `art/inbox/gait/sheet_captain_dragonslayer_run_a.png` + `_b.png` | 요청 |
| [`heavy__captain_ironwall/`](heavy__captain_ironwall/README.md) | `sheet/captain/ironwall` 브리긴다 이동 (중량) | 중량 · `art/requests/guides/heavy_base/v1` | `art/inbox/gait/sheet_captain_ironwall_run_a.png` + `_b.png` | 그려짐 · 등록 |
| [`heavy__captain_lancer/`](heavy__captain_lancer/README.md) | `sheet/captain/lancer` 로드릭 — 말을 잃은 기사 (창기병) 이동 | 중량 · `art/requests/guides/heavy_base/v1` | `art/inbox/gait/sheet_captain_lancer_run_a.png` + `_b.png` | 요청 |
| [`heavy__captain_runesmith/`](heavy__captain_runesmith/README.md) | `sheet/captain/runesmith` 브로크 이동 | 중량 · `art/requests/guides/heavy_base/v1` | `art/inbox/gait/sheet_captain_runesmith_run_a.png` + `_b.png` | 요청 |
| [`heavy__captain_saintknight/`](heavy__captain_saintknight/README.md) | `sheet/captain/saintknight` 엘리노어 — 성광의 기사 (성광 기사) 이동 | 중량 · `art/requests/guides/heavy_base/v1` | `art/inbox/gait/sheet_captain_saintknight_run_a.png` + `_b.png` | 요청 |
| [`heavy__captain_titan/`](heavy__captain_titan/README.md) | `sheet/captain/titan` 우르그 이동 | 중량 · `art/requests/guides/heavy_base/v1` | `art/inbox/gait/sheet_captain_titan_run_a.png` + `_b.png` | 요청 |
| [`heavy__hero_oswin/`](heavy__hero_oswin/README.md) | `sheet/hero/oswin` 오스윈 — 몰락한 기사단장 (몰락 기사단장) 이동 | 중량 · `art/requests/guides/heavy_base/v1` | `art/inbox/gait/sheet_hero_oswin_run_a.png` + `_b.png` | 요청 |
| [`heavy__monster_frost-troll/`](heavy__monster_frost-troll/README.md) | `sheet/monster/서리 트롤` 서리 트롤 이동 | 중량 · `art/requests/gait/heavy__monster_frost-troll` | `art/inbox/gait/sheet_monster_frost-troll_run_a.png` + `_b.png` | 요청 |
| [`robe__captain_archmagus/`](robe__captain_archmagus/README.md) | `sheet/captain/archmagus` 에우리아 — 마지막 대현자 (대현자) 이동 | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_captain_archmagus_run_a.png` + `_b.png` | 요청 |
| [`robe__captain_demonhunter/`](robe__captain_demonhunter/README.md) | `sheet/captain/demonhunter` 모르데카이 이동 | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_captain_demonhunter_run_a.png` + `_b.png` | 요청 |
| [`robe__captain_hedgemage/`](robe__captain_hedgemage/README.md) | `sheet/captain/hedgemage` 펠릭스 이동 | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_captain_hedgemage_run_a.png` + `_b.png` | 요청 |
| [`robe__captain_hexer/`](robe__captain_hexer/README.md) | `sheet/captain/hexer` 벨라도나 이동 | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_captain_hexer_run_a.png` + `_b.png` | 요청 |
| [`robe__captain_inquisitorlord/`](robe__captain_inquisitorlord/README.md) | `sheet/captain/inquisitorlord` 발타자르 이동 | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_captain_inquisitorlord_run_a.png` + `_b.png` | 요청 |
| [`robe__captain_lightbearer/`](robe__captain_lightbearer/README.md) | `sheet/captain/lightbearer` 루치아 — 빛을 든 사도 (빛의 사도) 이동 | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_captain_lightbearer_run_a.png` + `_b.png` | 요청 |
| [`robe__captain_pilgrim/`](robe__captain_pilgrim/README.md) | `sheet/captain/pilgrim` 아멜리 이동 | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_captain_pilgrim_run_a.png` + `_b.png` | 요청 |
| [`robe__class_mage/`](robe__class_mage/README.md) | `sheet/class/mage` 병과 마법사 이동 (로브) | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_class_mage_run_a.png` + `_b.png` | 그려짐 · 등록 |
| [`robe__hero_astel/`](robe__hero_astel/README.md) | `sheet/hero/astel` 아스텔 — 마탑의 마지막 제자 (마탑 계승자) 이동 | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_hero_astel_run_a.png` + `_b.png` | 요청 |
| [`robe__hero_seraphine/`](robe__hero_seraphine/README.md) | `sheet/hero/seraphine` 세라핀 — 파문당한 성녀 (파문 성녀) 이동 | 로브 · `art/requests/guides/robe_base/v1` | `art/inbox/gait/sheet_hero_seraphine_run_a.png` + `_b.png` | 요청 |
| [`run__captain_admiral/`](run__captain_admiral/README.md) | `sheet/captain/admiral` 마렌 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_admiral_run_a.png` + `_b.png` | 요청 |
| [`run__captain_bard/`](run__captain_bard/README.md) | `sheet/captain/bard` 리코 — 노래하는 검 (음유 검객) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_bard_run_a.png` + `_b.png` | 요청 |
| [`run__captain_beastmaster/`](run__captain_beastmaster/README.md) | `sheet/captain/beastmaster` 오르가 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_beastmaster_run_a.png` + `_b.png` | 요청 |
| [`run__captain_blademaster/`](run__captain_blademaster/README.md) | `sheet/captain/blademaster` 바렌 — 떠돌이 검귀 (검귀) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_blademaster_run_a.png` + `_b.png` | 요청 |
| [`run__captain_elfwarden/`](run__captain_elfwarden/README.md) | `sheet/captain/elfwarden` 세레니엘 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_elfwarden_run_a.png` + `_b.png` | 요청 |
| [`run__captain_fieldmedic/`](run__captain_fieldmedic/README.md) | `sheet/captain/fieldmedic` 마그다 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_fieldmedic_run_a.png` + `_b.png` | 요청 |
| [`run__captain_fixer/`](run__captain_fixer/README.md) | `sheet/captain/fixer` 진 — 뒷골목 해결사 (해결사) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_fixer_run_a.png` + `_b.png` | 요청 |
| [`run__captain_frostjarl/`](run__captain_frostjarl/README.md) | `sheet/captain/frostjarl` 비요른 달리기 | 경량 · `art/requests/gait/run__captain_frostjarl` | `art/inbox/gait/sheet_captain_frostjarl_run_a.png` + `_b.png` | 요청 |
| [`run__captain_huntress/`](run__captain_huntress/README.md) | `sheet/captain/huntress` 키아라 — 숲의 덫꾼 (덫사냥꾼) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_huntress_run_a.png` + `_b.png` | 요청 |
| [`run__captain_khan/`](run__captain_khan/README.md) | `sheet/captain/khan` 테무르 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_khan_run_a.png` + `_b.png` | 요청 |
| [`run__captain_liberator/`](run__captain_liberator/README.md) | `sheet/captain/liberator` 카토 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_liberator_run_a.png` + `_b.png` | 요청 |
| [`run__captain_pirateking/`](run__captain_pirateking/README.md) | `sheet/captain/pirateking` 크림슨 이동 | 경량 · `art/requests/gait/run__captain_pirateking` | `art/inbox/gait/sheet_captain_pirateking_run_a.png` + `_b.png` | 요청 |
| [`run__captain_shadowlord/`](run__captain_shadowlord/README.md) | `sheet/captain/shadowlord` 모로 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_shadowlord_run_a.png` + `_b.png` | 요청 |
| [`run__captain_shadowqueen/`](run__captain_shadowqueen/README.md) | `sheet/captain/shadowqueen` 니클라 달리기 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_shadowqueen_run_a.png` + `_b.png` | 그려짐 · 등록 |
| [`run__captain_siegemaster/`](run__captain_siegemaster/README.md) | `sheet/captain/siegemaster` 오토 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_siegemaster_run_a.png` + `_b.png` | 요청 |
| [`run__captain_spellblade/`](run__captain_spellblade/README.md) | `sheet/captain/spellblade` 카시안 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_spellblade_run_a.png` + `_b.png` | 요청 |
| [`run__captain_tactician/`](run__captain_tactician/README.md) | `sheet/captain/tactician` 이사벨 — 퇴역 참모 (전술가) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_tactician_run_a.png` + `_b.png` | 요청 |
| [`run__captain_veteran/`](run__captain_veteran/README.md) | `sheet/captain/veteran` 하랄드 — 백발의 노병 (노병) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_veteran_run_a.png` + `_b.png` | 요청 |
| [`run__captain_warlord/`](run__captain_warlord/README.md) | `sheet/captain/warlord` 가르마크 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_warlord_run_a.png` + `_b.png` | 요청 |
| [`run__captain_windhunter/`](run__captain_windhunter/README.md) | `sheet/captain/windhunter` 나린 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_captain_windhunter_run_a.png` + `_b.png` | 요청 |
| [`run__class_archer/`](run__class_archer/README.md) | `sheet/class/archer` 병과 궁수 달리기 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_class_archer_run_a.png` + `_b.png` | 그려짐 · 등록 |
| [`run__class_cleric/`](run__class_cleric/README.md) | `sheet/class/cleric` 병과 성직자 달리기 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_class_cleric_run_a.png` + `_b.png` | 그려짐 · 등록 |
| [`run__class_rogue/`](run__class_rogue/README.md) | `sheet/class/rogue` 병과 도적 달리기 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_class_rogue_run_a.png` + `_b.png` | 그려짐 · 등록 |
| [`run__class_warrior/`](run__class_warrior/README.md) | `sheet/class/warrior` 병과 전사 달리기 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_class_warrior_run_a.png` + `_b.png` | 그려짐 · 등록 |
| [`run__hero_grom/`](run__hero_grom/README.md) | `sheet/hero/grom` 그롬 — 피의 투기장 챔피언 (투기장 패왕) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_hero_grom_run_a.png` + `_b.png` | 요청 |
| [`run__hero_kai/`](run__hero_kai/README.md) | `sheet/hero/kai` 카이 — 숲을 떠난 엘프 정찰병 (은빛 순찰자) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_hero_kai_run_a.png` + `_b.png` | 요청 |
| [`run__hero_lyra/`](run__hero_lyra/README.md) | `sheet/hero/lyra` 리라 — 가면 쓴 의적 (가면 의적) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_hero_lyra_run_a.png` + `_b.png` | 요청 |
| [`run__hero_marisol/`](run__hero_marisol/README.md) | `sheet/hero/marisol` 마리솔 — 닻을 잃은 해적 선장 (해적 선장) 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_hero_marisol_run_a.png` + `_b.png` | 요청 |
| [`run__monster_bandit/`](run__monster_bandit/README.md) | `sheet/monster/산적` 몬스터 — 산적 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_monster_bandit_run_a.png` + `_b.png` | 요청 |
| [`run__monster_desert-bandit/`](run__monster_desert-bandit/README.md) | `sheet/monster/사막 도적` 사막 도적 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_monster_desert-bandit_run_a.png` + `_b.png` | 요청 |
| [`run__monster_goblin/`](run__monster_goblin/README.md) | `sheet/monster/고블린` 고블린 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_monster_goblin_run_a.png` + `_b.png` | 요청 |
| [`run__monster_skeleton/`](run__monster_skeleton/README.md) | `sheet/monster/해골 병사` 몬스터 — 해골 병사 이동 | 경량 · `art/requests/guides/run_base/v2` | `art/inbox/gait/sheet_monster_skeleton_run_a.png` + `_b.png` | 요청 |
<!-- index:end -->

`--write` 로 만든 폴더의 구성: `README.md` (한국어 머리말 + 「Prompt for Antigravity」 영어 블록: 참고 그림, CHARACTER, THE MOVE — 기울기·머리 높이·보폭·디딘 발끝 x 표,
ARMS AND WEAPONS, 색, FORMAT, SELF-CHECK, 납품 메모와 「판정」 절), `guide_<p>_a.png` / `guide_<p>_b.png` (= 부류 마네킹 띠 사본, 자세·자리 가이드),
`size_<p>_a.png` / `size_<p>_b.png` (읽기용 1920x1024: 왼쪽 = 승인된 대기 자세를 게임처럼 앵커 열을 x=192 에 두고 흐리게 + 마네킹 첫 칸 하늘색 윤곽, 같은 배율 ·
오른쪽 = 마네킹 4칸 + 바닥 줄 y=870 · 엉덩이 열 x=192 · x=32/351 선 · 디딘 발끝 눈금 · 경량의 뜸 줄 y=852). `<p>` = `run` / `heavy` / `robe`.
처음 두 요청(`run__class_warrior`, `run__captain_shadowqueen`)은 손으로 쓴 것이라 「Prompt for GPT」이고 그림 이름이 `guide_run_*` 이다 — 이미 그려져 등록되었으니 다시 만들지 않는다.

## 더 만드는 법 (명령 하나)

```
python3 tools/art/gait_requests.py --write sheet/<kind>/<key> [sheet/... ...]
```
- 시트의 부류(`gait_classes.json`) → 그 부류의 확정 마네킹(`pose.json`)의 숫자로 README 를 쓰고, `tools/art/run_request_guides.py` 가 그림 넷을 만든다.
  대기 자세의 x 범위·앵커 열·배율은 등록된 시트(`assets/art/manifest.json`)와 원본(`art/inbox/<stem>.png`)·요청서 배율(`art/requests/phase3.json`)에서 잰다 — 캐릭터마다 손으로 적는 표가 없다.
- 시트 배율과 마네킹 배율이 1% 넘게 다르면 요청 폴더에 변환된 `pose.json`을 쓴다. `guide_*`와 `size_*`의 마네킹은 각 칸의 (192, 870)을 기준으로 같은 비율만큼 조정한다. 수령 도구와 SELF-CHECK는 요청 폴더의 pose를 사용한다.
- 손에 든 것·천·얼굴 문장은 `tools/art/gait_requests.py` 의 `CARRY` 표(시트 id 마다)에서 온다(중량은 방패를 가슴 앞에 세운 채, 로브는 옷자락이 한 칸 늦고 무릎을 가림).
  표에 없는 시트는 phase3 꾸러미 README 의 CHARACTER 줄(없으면 phase3.json 의 prompt) + 부류 기본 문장으로 만들고 README 와 출력에 「검토」를 단다
  → 대기 그림을 보고 CARRY 에 적은 뒤 `--force` 로 다시 만든다. 「검토」가 달린 요청은 대기열에 올리지 않는다.
- **검토로 손본 요청서**(C8·C9·Q3 대조 뒤 클라우드가 README 를 직접 고친 것)는 `--force` 로 다시 만들면 고친 문장이 사라진다. 다시 만들어야 하면 먼저 `git diff` 로 고친 문장을 옮겨 둔다.
- 이미 있는 폴더는 `--force` 없이 건드리지 않는다. 손으로 쓴 요청(`run__class_warrior`, `run__captain_shadowqueen`)은 `--force` 로도 덮어쓰지 않는다.
  `--out <폴더>` 는 시험용(목록을 고치지 않는다). 이 목록만 다시 쓰기: `python3 tools/art/gait_requests.py --index`.
- 같은 입력이면 같은 파일이 나온다(README 의 날짜는 `--date`, 기본 오늘). 검사: `python3 tools/art/gait_requests.py --check` — 분류·엔진 표에 더해 요청 폴더마다
  README 가 가리키는 파일이 있는지, `--write` 로 만든 폴더의 `guide_*` 가 지금 부류 마네킹 띠와 바이트까지 같은지 본다.
- 만든 뒤: 그림 넷을 눈으로 본다(같은 배율, 발이 바닥 줄 위) → `art/requests/dot_queue.md` 「지금 차례」에 줄을 올린다(클라우드).
- 마네킹이 새 판(v<n>)이 되면: `python3 tools/art/gait_requests.py --write <시트> --force` (README 의 숫자와 그림을 함께 — `--check` 가 옛 가이드를 잡는다).
  그림만 다시: `python3 tools/art/run_request_guides.py <시트> --force`. 잰 값만 보기: `python3 tools/art/run_request_guides.py <시트> --info`.

## 받는 쪽 (클라우드)

`python3 tools/art/receive.py gait/<시트 png 이름>_run` → 부류에 맞는 마네킹으로 검사(경량만 `--flight-slots 4`) + `add_gait.py --dry-run` → 미리보기 확인 →
`python3 tools/art/add_gait.py <시트 id> --gait run --src <..._run_a.png> <..._run_b.png> --pose <부류 마네킹 pose.json>`
(규격·검사: `tools/art/add_gait.py --help`, `art/requests/guides/SPEC.md` 5b절. 마네킹 픽셀 — 이름을 바꾸거나 옮기거나 뒤집은 것도 — 은 `add_gait.py` 가 거부한다.)

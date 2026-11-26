# PC changes after gate 1: mannequin arms (cloud, 2026-11-26)

Owner, after gate 1: "내가 첫 관문 테스트를 하기는 했는데, 마네킹 상태가 영 안좋은데. 팔이 어떻게 꺾이는지 좀 봐봐."

All six sets go back to the PC. For each set, change the `mannequin_pc.py` in `art/inbox/guides/<set>/` as listed below, rebuild it,
check it, and deliver it again (same names, same branch `art-inbox`).

## posekit version: `posekit natural-arms 1 (2026-11-26)`
- `tools/pixelart/posekit.py` (pull the repo first). A pose with `"arms": "natural"` takes the **anatomical elbow side**: for a figure
  facing right, the perpendicular (-d.y, d.x) of the shoulder -> hand direction. It replaced the old fixed world preference
  `(0.25, 1.0)`, which tied when the hand hung below the shoulder and flipped between frames.
- `elbN` / `elbF` still win. When `"arms": "natural"` is set, `posekit.check()` prints each bad arm (class + why, plus
  `(elbX override [...])` when an override caused it) into the posekit warnings of `frames.json` and the build log.
- `swN` / `swF` (one shoulder's spread) are now posekit keys, the same as the archer's `_solve_sides`.
- Poses without `"arms"` build exactly as before. The walk, run, heavy and robe drafts and `walk8_pc.py` are byte-identical
  (325 files compared with `cmp`).
- The checker `tools/art/check_skeleton.py --motion` now measures the arms (SPEC 10.3b):
  - **FAIL** on chicken-wing, crossing (the V), flared, hyper (reversed hinge) or folded (< 20 deg). An elbow under 20% visible only
    WARNs.
  - **WARN** on borderline cases, on tucked (hand behind the neck under a raised elbow) and on elbow jumps between frames.
  - All six current deliveries now FAIL there.

## For every set (code)
In `make_pose()`, just before `p['z'] = ...`, add:

    p['arms'] = 'natural'      # posekit natural-arms 1 - the elbow bends the anatomical way (SPEC 10.3b)

Then apply that set's table changes below. Edit the `SET` / `CFG` table directly, or paste the `ARMS_FIX` block (the cloud's scratch
form) right after the table. In `ARMS_FIX`, `None` = delete that key and `"*"` = set-level keys. The cloud's applier was:

    ARMS_FIX = {...}
    _T = globals().get("SET") or globals().get("CFG")
    _T.update(ARMS_FIX.get("*", {}))
    for _f in _T["frames"]:
        for _k, _v in ARMS_FIX.get(_f["name"], {}).items():
            if _v is None: _f.pop(_k, None)
            else: _f[_k] = _v

Table units as in the scripts: x heads from the set's `x0` (x px = x0 + 110 x), h heads above the floor (y px = 870 - 110 h). The same
rows, with px, are in each README's new section "팔 고침" (`art/requests/guides/<set>/README.md`).

## Self-check before delivering (unchanged commands)
    python3 tools/art/check_skeleton.py art/inbox/guides/<set>/<set>.aseprite --set <set>
- No FAIL.
- The `arms (posekit natural-arms 1 ...)` info line lists every arm.
- The build log says `posekit warnings 0`.

The cloud rebuilt all six from these exact scripts:
- `check_skeleton --motion`: 0 FAIL in every set. The only WARNs are Nikla's 3 old contact-clearance warnings (they were there before).
- `node tools/art/requests.js --motion --frames ...`: 0 FAIL, 3 WARN (the same timing warnings as before). Warrior vs ironwall IoU:
  hold 0.769, contact 0.742.

## atk__class_warrior
| frame | key | delivered | new |
|---|---|---|---|
| in | handN | (-0.30, 1.80) | (0.10, 1.86) |
| in | handF | (0.62, 2.20) | (0.68, 2.18) |
| hold | handN | (-0.75, 1.75) | (-0.65, 3.05) |
| hold | wa | 120 | 125 |
| hold | handF | (0.45, 2.42) | (0.47, 2.44) |
| swing | handN | (-0.15, 1.55) | (0.22, 1.42) |
| contact | elbF | (-0.50, -1.00) | (없음) |
| contact | handF | (1.14, 2.27) | (1.10, 2.50) |
| follow | elbF | (-0.50, -1.00) | (없음) |
| follow | handF | (1.06, 2.20) | (0.95, 2.75) |
| recover | handF | (0.70, 2.15) | (0.98, 2.01) |
| settle | handN | (0.06, 1.71) | (0.26, 1.71) |
| settle | handF | (0.78, 2.07) | (0.84, 2.13) |

- Remove both `"elbF": [-0.5, -1.0]` (contact, follow). That override bent the shield elbow above and behind the shoulder
  (reversed, 29 deg fold).
- `hold`: the sword is now cocked **above and behind the head**, with the hand at (-0.65, 3.05) and `wa` 125. The old hand was low behind
  the hip, which gave the V cross. The checker still measures hold -> follow 260 deg of turn (min 120) and 29 deg past the contact line (bible 25-40).

Scratch form (pasted as-is in the cloud rebake):

    ARMS_FIX = {"in": {"handN": [0.10, 1.86], "handF": [0.68, 2.18]}, "hold": {"handN": [-0.65, 3.05], "wa": 125, "handF": [0.47, 2.44]}, "swing": {"handN": [0.22, 1.42]}, "contact": {"elbF": None, "handF": [1.10, 2.50]}, "follow": {"elbF": None, "handF": [0.95, 2.75]}, "recover": {"handF": [0.98, 2.01]}, "settle": {"handN": [0.26, 1.71], "handF": [0.84, 2.13]}}

## atk__captain_shadowqueen
| frame | key | delivered | new |
|---|---|---|---|
| in | handF | (0.95, 2.35) | (0.95, 2.72) |
| hold | elbN | (-1, 0.20) | (없음) |
| swing | handF | (1.78, 1.98) | (1.80, 2.28) |
| contact | handF | (1.82, 2.20) | (1.85, 2.65) |
| follow | handF | (1.85, 2.05) | (1.88, 2.62) |
| recover | handF | (1.68, 1.78) | (1.85, 1.05) |
| settle | handN | (1.34, 1.62) | (1.50, 1.54) |
| settle | handF | (1.58, 1.68) | (1.75, 1.12) |

- `hold`: remove `"elbN": [-1, 0.2]`. The natural rule already puts both elbows forward under the raised hands. `elbF [1, 0.2]` stays
  (it is the natural side; harmless).
- contact / follow: the far hand goes up to head height, so the far forearm rises from the elbow. In the delivered set the hand was
  tucked behind the neck under the elbow. In the cloud rebake the contact frame's `weapon_back` reads 30% outside the body: still a WARN,
  but up from 10% in the delivered frames.

Scratch form (pasted as-is in the cloud rebake):

    ARMS_FIX = {"in": {"handF": [0.95, 2.72]}, "hold": {"elbN": None}, "swing": {"handF": [1.80, 2.28]}, "contact": {"handF": [1.85, 2.65]}, "follow": {"handF": [1.88, 2.62]}, "recover": {"handF": [1.85, 1.05]}, "settle": {"handN": [1.50, 1.54], "handF": [1.75, 1.12]}}

## atk__captain_ironwall
| frame | key | delivered | new |
|---|---|---|---|
| (set) | pose_defaults.elbF | (-0.30, 1.00) | (없음) |
| in | handF | (0.42, 2.18) | (0.68, 2.14) |
| hold | handN | (-0.45, 2.25) | (-0.60, 2.88) |
| hold | handF | (0.38, 2.20) | (0.46, 2.26) |
| swing | handN | (-0.40, 2.22) | (-0.30, 2.80) |
| swing | handF | (0.75, 2.15) | (0.93, 2.21) |
| contact | handN | (-0.28, 2.20) | (0.10, 3.05) |
| contact | handF | (1.34, 2.10) | (1.38, 2.10) |
| follow | handN | (-0.22, 2.20) | (0.15, 3.10) |
| follow | handF | (1.09, 1.92) | (1.36, 1.75) |
| recover | handN | (-0.30, 2.10) | (-0.25, 2.95) |
| recover | handF | (0.70, 2.20) | (1.02, 2.22) |
| settle | handN | (0.10, 2.30) | (0.12, 2.30) |
| settle | handF | (0.50, 2.15) | (0.84, 2.15) |

- Set level: remove `"elbF": [-0.3, 1.0]` from `pose_defaults`. The shield arm now uses the natural elbow; the shield hand moves
  forward instead.

Scratch form (pasted as-is in the cloud rebake):

    ARMS_FIX = {"*": {"pose_defaults": {"toeN": 0.85, "faN": 0, "faF": 0}}, "in": {"handF": [0.68, 2.14]}, "hold": {"handN": [-0.60, 2.88], "handF": [0.46, 2.26]}, "swing": {"handN": [-0.30, 2.80], "handF": [0.93, 2.21]}, "contact": {"handN": [0.10, 3.05], "handF": [1.38, 2.10]}, "follow": {"handN": [0.15, 3.10], "handF": [1.36, 1.75]}, "recover": {"handN": [-0.25, 2.95], "handF": [1.02, 2.22]}, "settle": {"handN": [0.12, 2.30], "handF": [0.84, 2.15]}}

## atk__class_archer
| frame | key | delivered | new |
|---|---|---|---|
| nock | handN | (0.45, 1.92) | (0.45, 2.12) |
| nock | handF | (0.55, 1.78) | (1.00, 1.62) |
| lower | handN | (-0.15, 2.10) | (0.15, 2.12) |
| settle | handN | (-0.05, 1.72) | (0.23, 1.66) |
| settle | handF | (0.60, 1.80) | (0.98, 1.86) |

- Code: **delete the line `pk.solve = _solve_sides`** (you may keep the function). posekit now places `swN` / `swF` itself (same
  shoulder points `L(-0.40*swN, T-0.05)` / `L(0.34*swF, T-0.07)`). If `_solve_sides` stays active it solves the arm again with the old
  world preference `(0.25, 1.0)` and the natural elbow is lost.
- Code: after `p['arms'] = 'natural'` also add
  `if cfg.get('weapon', {}).get('type') == 'bow': p['bow_draw'] = 'N' if cfg['weapon'].get('hand', 'F') == 'F' else 'F'`
  This lets posekit `check()` treat the string arm's draw (hold, release, follow) as allowed, so it prints no warning.
- Kept on purpose: `swN 0.2` / `swF 0.2` at the hold and the `elbN [-1.0, -0.3]` draw prefs. I tried `swN 1.0` at the hold. The draw
  elbow then points straight up, 0.64 head above the shoulder (worse). The checker accepts the draw (hold, release, follow) as the bow
  exception `draw`.

Scratch form (pasted as-is in the cloud rebake):

    ARMS_FIX = {"nock": {"handN": [0.45, 2.12], "handF": [1.00, 1.62]}, "lower": {"handN": [0.15, 2.12]}, "settle": {"handN": [0.23, 1.66], "handF": [0.98, 1.86]}}

## hit__class_warrior
| frame | key | delivered | new |
|---|---|---|---|
| (set) | preview_idle.handF | (0.78, 2.07) | (0.84, 2.13) |
| (set) | preview_idle.handN | (0.06, 1.71) | (0.26, 1.71) |
| K1 impact | handN | (0.00, 1.60) | (0.18, 1.60) |
| K1 impact | handF | (0.62, 2.25) | (0.72, 2.25) |
| K2 peak | handN | (-0.30, 1.70) | (0.02, 1.92) |
| K2 peak | handF | (0.60, 2.12) | (0.62, 2.12) |
| K3 recover | handN | (-0.05, 1.66) | (0.20, 1.62) |
| K3 recover | handF | (0.65, 2.10) | (0.73, 2.14) |
| K4 settle | handN | (0.05, 1.71) | (0.24, 1.70) |
| K4 settle | handF | (0.76, 2.07) | (0.83, 2.13) |

- `preview_idle` (the context GIF's idle): the hands move the same way (sword hand (0.26, 1.71), shield hand (0.84, 2.13)). The
  README's idle sword hand (0.06, 1.71) is itself a chicken wing.

Scratch form (pasted as-is in the cloud rebake):

    ARMS_FIX = {"*": {"preview_idle": {"name": "idle", "ms": 400, "hip": [0.00, 1.40], "lean": 0.08, "tilt": 0.0, "handN": [0.26, 1.71], "handF": [0.84, 2.13], "wa": 38}}, "K1 impact": {"handN": [0.18, 1.60], "handF": [0.72, 2.25]}, "K2 peak": {"handN": [0.02, 1.92], "handF": [0.62, 2.12]}, "K3 recover": {"handN": [0.20, 1.62], "handF": [0.73, 2.14]}, "K4 settle": {"handN": [0.24, 1.70], "handF": [0.83, 2.13]}}

## hit__captain_shadowqueen
| frame | key | delivered | new |
|---|---|---|---|
| (set) | idle.handF | (0.50, 1.62) | (0.90, 1.44) |
| K1 impact | handF | (0.40, 1.58) | (0.86, 1.52) |
| K2 stagger | handF | (0.30, 1.62) | (0.78, 1.66) |
| K3 recover | handF | (0.40, 1.60) | (0.84, 1.42) |
| K4 settle | handF | (0.47, 1.62) | (0.89, 1.42) |

- `idle` (the context reference): far hand (0.90, 1.44). The old (0.50, 1.62) gave the same chicken wing.

Scratch form (pasted as-is in the cloud rebake):

    ARMS_FIX = {"*": {"idle": {"name": "idle", "ms": 0, "hip": [0.0, 1.40], "lean": 0.08, "tilt": 0.0, "toeN": 0.85, "footN": [-0.48, 0.12], "footF": [0.37, 0.12], "handN": [0.30, 1.55], "handF": [0.90, 1.44], "wa": -80, "waF": -70}}, "K1 impact": {"handF": [0.86, 1.52]}, "K2 stagger": {"handF": [0.78, 1.66]}, "K3 recover": {"handF": [0.84, 1.42]}, "K4 settle": {"handF": [0.89, 1.42]}}

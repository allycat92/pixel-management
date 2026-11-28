"""Unit tests for the 3D mannequin (no drawing needed: they use the canonical proportions and specs/carry3d.json).

  python3 -m unittest tools/mannequin3d/test_mannequin3d.py        (about 1 minute)

determinism, floor / planting / IK / knee / mirror / band / feet / upper-body checks for the three movement classes,
a short-legged body (stride follows the legs), the sword never over the head (attack) nor the trunk (hit), the robe
hem, the weapon hand range (rig clamp + check, and no authored frame outside it), that add_gait refuses an
unpainted 3D guide written anywhere (palette signature), a character's movement personality (Baren: lower, more lean,
same stride and cadence), the bow / spear / dagger props and the reverse grip (the wrist rule on the grip axis), and
the 3D request folder (request.py: files, marker, verify, refusal of its plain strip); review 2026-11-28: the second hand
of a two-handed grip on the weapon line with its own wrist rule and a human elbow (rig.arm_ik3d), strips a / b of heavy /
robe mirrored on screen with the trailing heel in range, the robe hem on one smooth path; diagnosis 2026-11-28: a held
weapon clear of the face at the nose row (Grom) and the belt row on the brown band (Oswin).
"""
import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'tools', 'art'))

import build  # noqa: E402
import checks  # noqa: E402
from common import load_carry, strip_of  # noqa: E402
from motions import gait_spec, leg_factor  # noqa: E402
from render import Camera  # noqa: E402
from rig import CANON, scaled, fk, weapon_angle  # noqa: E402
from motions import weapon_limit  # noqa: E402
import signature  # noqa: E402

CARRY = load_carry()


def run(key, P=CANON, scale=0.1654):
    carry = dict(CARRY[key])
    carry.setdefault('chest_open', 30.0)
    cam = Camera(yaw=15.0)
    spec = gait_spec(carry['gait'], scale, leg_factor(P))
    g = build.render_gait(P, carry, spec, cam, scale)
    return spec, g, checks.gait_checks(spec, g['recs'], g['bodies'], g['plain'], cam, carry)


def fails(res):
    return [m for lv, m in res if lv == checks.FAIL]


class Gaits(unittest.TestCase):
    def test_classes_pass_all_checks(self):
        for key in ('warrior', 'ironwall', 'mage'):
            with self.subTest(key=key):
                spec, g, res = run(key)
                self.assertEqual(fails(res), [])
                # stance frames: the sole's lowest pixel on the floor row
                for r in g['recs']:
                    if r['feet_down']:
                        self.assertEqual(r['lowest_px'], 870, r['frame'])

    def test_short_legs_shorter_stride(self):
        P = scaled(CANON, 0.83)          # a goblin-sized body
        spec, g, res = run('ironwall', P)
        self.assertLess(spec['step_px'], 142.5 * 0.9)
        self.assertEqual(fails(res), [])
        self.assertTrue(all(r['ik_reached'] for r in g['recs']))

    def test_sheet_scale_sets_stride(self):
        spec = gait_spec('run_light', 0.18, 1.0)
        self.assertAlmostEqual(spec['step_px'] * 0.18, 275.0 * 0.1654, places=0)

    def test_deterministic(self):
        _, g1, _ = run('warrior')
        _, g2, _ = run('warrior')
        for a, b in zip(g1['plain'], g2['plain']):
            self.assertTrue(np.array_equal(np.asarray(a), np.asarray(b)))


class Personality(unittest.TestCase):
    def test_baren_passes_and_keeps_the_class_rhythm(self):
        spec, g, res = run('baren')
        self.assertEqual(fails(res), [])
        self.assertEqual((spec['step_px'], spec['ms']), (275.0, 80))          # class stride + cadence (engine runCells)
        _, gw, _ = run('warrior')
        hips = [r['hip_height_px'] for r in g['recs']]
        hips_w = [r['hip_height_px'] for r in gw['recs']]
        self.assertTrue(all(a < b for a, b in zip(hips, hips_w)))            # lower hips in every frame
        self.assertGreater(min(r['lean_deg'] for r in g['recs']), min(r['lean_deg'] for r in gw['recs']))
        ws = [w for b in g['bodies'] for w in b.weapons]
        self.assertTrue(ws and all(not w['clamped'] and 0.0 <= w['deg'] <= 120.0 for w in ws))

    def test_unknown_personality_key_refused(self):
        from motions import personality
        with self.assertRaises(ValueError):
            personality({'personality': {'stride_add': 10}})                   # the stride is the class's, never personal


class FootPaths(unittest.TestCase):
    """owner verdict 2026-11-28: the heavy / robe back foot snapped, the foot trailed far back"""
    def test_heavy_and_robe_swing_foot_like_the_2d_bases(self):
        for key in ('ironwall', 'mage'):
            with self.subTest(key=key):
                spec, g, res = run(key)
                self.assertEqual(fails(res), [])
                paths = checks.foot_paths(spec, g['recs'])
                for s, seq in paths.items():
                    xs = [a for _, a, *_ in seq]
                    self.assertTrue(all(b > a for a, b in zip(xs, xs[1:])), (s, xs))   # forward every frame
                    self.assertGreaterEqual(seq[3][1], 15)        # REACH: swing ankle ahead of the hip
                    self.assertGreaterEqual(seq[3][2], 4)         # ... and off the floor (not a 2nd contact)
                    self.assertLessEqual(seq[1][2], 10)           # toe-off: no snap up
                    self.assertLessEqual(seq[0][5], 30)           # trailing leg nearly straight ...
                    self.assertLessEqual(seq[0][4], -12)          # ... and angled back

    def test_foot_path_check_catches_a_second_contact(self):
        spec, g, _ = run('ironwall')
        recs = [dict(r) for r in g['recs']]
        recs[3] = dict(recs[3], sole_px=dict(recs[3]['sole_px'], F=869))        # reach foot dragged on the floor
        self.assertTrue(any('REACH' in m for m in fails(checks.foot_path_checks(spec, recs))))

    def test_hip_drop_does_not_fold_the_trailing_leg(self):
        carry = dict(CARRY['ironwall'], personality={'hip_drop': [8.0, 2.0, 2.0, 2.0]})
        cam = Camera(yaw=15.0)
        spec = gait_spec('run_heavy', 0.1654, 1.0)
        g = build.render_gait(CANON, carry, spec, cam, 0.1654)
        self.assertEqual(fails(checks.foot_path_checks(spec, g['recs'])), [])

    def test_swing_add_refused_on_target_gaits(self):
        from motions import personality
        with self.assertRaises(ValueError):
            personality({'gait': 'run_heavy', 'personality': {'swing_add': {'0.75': [2, 6, 0]}}})


class WeaponStability(unittest.TestCase):
    """owner verdict 2026-11-28: bent spear, wobbling greatsword / mace"""
    def test_two_handed_weapons_locked_to_the_chest(self):
        for key in ('lancer', 'grom', 'magda', 'mage'):
            with self.subTest(key=key):
                _, g, res = run(key)
                self.assertEqual(fails(res), [])
                W = [r['weapon_px'] for r in g['recs']]
                self.assertTrue(all(w['two_hand'] for w in W))
                A = [w['angle_deg'] for w in W]
                self.assertLessEqual(max(abs(A[(i + 1) % 8] - A[i]) for i in range(8)), checks.W_STEP[2])
                L = [w['length_px'] for w in W]
                self.assertLessEqual(max(L) - min(L), 0.02 * min(L))
                for i in range(4):          # strip b = strip a
                    self.assertLessEqual(abs(A[i] - A[i + 4]), 1.0)

    def test_stability_check_catches_a_bent_or_pumping_weapon(self):
        _, g, _ = run('lancer')
        recs = [dict(r) for r in g['recs']]
        w = dict(recs[2]['weapon_px'])
        w['length_px'] *= 0.85                          # shortened to stay under a line
        w['angle_deg'] += 6.0                           # and kinked
        recs[2] = dict(recs[2], weapon_px=w)
        msgs = fails(checks.weapon_stability(recs, CARRY['lancer']))
        self.assertTrue(any('rigid' in m for m in msgs) and any('weapon angle' in m for m in msgs), msgs)

    def test_idle_angle_change_warns(self):
        # round 1 carried Roderick's lance at 68 deg (idle 36): WARN; the run carry now stays within ~15 deg of the idle
        _, g, _ = run('lancer')
        res = checks.weapon_stability(g['recs'], CARRY['lancer'])
        self.assertTrue(any(lv == checks.OK and 'vs idle 36' in m for lv, m in res), res)
        old = dict(CARRY['lancer'], props=[dict(CARRY['lancer']['props'][0], abs_angle=68.0)],
                   arms={'N': dict(CARRY['lancer']['arms']['N'], shoulder=6.0, elbow=78.0, abd=6.0)})
        cam = Camera(yaw=15.0)
        spec = gait_spec(old['gait'], 0.1654, 1.0)
        g2 = build.render_gait(CANON, dict(old, chest_open=34.0), spec, cam, 0.1654)
        res = checks.weapon_stability(g2['recs'], old)
        self.assertTrue(any(lv == checks.WARN and 'vs idle 36' in m for lv, m in res), res)


class BladeFace(unittest.TestCase):
    """diagnosis 2026-11-28: Grom's greatsword ran through the mannequin's nose (-5..+6 px) and the painter squeezed the
    face; a held weapon line crossing the nose row must keep >= FACE_FAIL px (WARN under FACE_WARN)"""
    def test_face_gap(self):
        self.assertAlmostEqual(checks.face_gap((100, 700), (200, 400), (150, 550)), 0.0)
        self.assertAlmostEqual(checks.face_gap((100, 700), (200, 400), (120, 550)), 30.0)
        self.assertIsNone(checks.face_gap((100, 700), (200, 600), (150, 550)))      # the line ends below the nose row
        lv, _ = checks.face_check('', ['R1', 'R2'], [None, -5.0], 'sword')
        self.assertEqual(lv, checks.FAIL)
        self.assertEqual(checks.face_check('', ['R1', 'R2'], [30.0, 12.0], 'sword')[0], checks.WARN)
        self.assertEqual(checks.face_check('', ['R1', 'R2'], [None, None], 'sword')[0], checks.OK)

    def test_grom_blade_clears_the_face_and_the_old_carry_fails(self):
        _, g, res = run('grom')
        face = [(lv, m) for lv, m in res if 'vs face' in m]
        self.assertEqual(len(face), 1)
        self.assertNotEqual(face[0][0], checks.FAIL, face)
        old = dict(CARRY['grom'], arms={'N': dict(CARRY['grom']['arms']['N'], shoulder=5.0)},
                   personality=dict(CARRY['grom']['personality'], lean_add=-2.0), chest_open=30.0)
        spec = gait_spec(old['gait'], 0.1654, 1.0)
        g2 = build.render_gait(CANON, old, spec, Camera(yaw=15.0), 0.1654)
        self.assertEqual(checks.face_checks_gait(g2['recs'])[0][0], checks.FAIL)

    def test_belt_row_on_the_brown_band(self):
        # pose.json belt_px: the belt band's centre (not the hip joint dot, which sits lower in the pelvis)
        _, g, _ = run('oswin')
        for r in g['recs']:
            self.assertIn('belt_px', r)
            self.assertLess(r['belt_px'][1], r['joints']['HN'][1] - 10)
            self.assertGreater(r['belt_px'][1], r['joints']['SN'][1] + 40)


class SecondHand(unittest.TestCase):
    """review 2026-11-28: the second hand of a two-handed grip - on the weapon line, its own wrist rule, a human elbow"""
    def test_two_handed_carries(self):
        for key in ('lancer', 'oswin', 'felix', 'grom', 'magda'):
            with self.subTest(key=key):
                _, g, res = run(key)
                self.assertEqual(fails(res), [])
                offs = [r['weapon_px']['fist2_off_line_px'] for r in g['recs']]
                self.assertLessEqual(max(abs(o) for o in offs), checks.FIST2_LINE_TOL)
                second = [w for b in g['bodies'] for w in b.weapons if w.get('role') == 'second']
                self.assertEqual(len(second), 8)
                self.assertTrue(all(0.0 <= w['deg'] <= 120.0 and not w['outside'] for w in second), second)
                for b in g['bodies']:
                    J = b.joints
                    for sd in 'NF':
                        u, f = J['S' + sd] - J['elb' + sd], J['wri' + sd] - J['elb' + sd]
                        inner = np.degrees(np.arccos(u @ f / np.linalg.norm(u) / np.linalg.norm(f)))
                        self.assertGreaterEqual(inner, 180.0 - checks.ELBOW_FLEX_MAX - 1e-6)

    def test_arm_ik3d_reaches_across_the_body(self):
        from rig import arm_ik3d, full_pose
        pose = {'chest_yaw': 30.0}
        B = fk(CANON, pose)
        goal = B.joints['chest'] + np.array([60.0, -30.0, 30.0])        # in front of the chest, on the NEAR side
        sh, el, abd, tw, res = arm_ik3d(CANON, pose, 'F', goal)
        self.assertLess(res, 0.05)
        self.assertLessEqual(el, 145.0)
        q = dict(full_pose(pose), shoulder_F=sh, elbow_F=el, arm_abd_F=abd, arm_twist_F=tw)
        np.testing.assert_allclose(fk(CANON, q).joints['handF'], goal, atol=0.05)

    def test_checks_catch_off_line_bad_wrist_and_folded_elbow(self):
        _, g, _ = run('lancer')
        recs = [dict(r) for r in g['recs']]
        recs[3] = dict(recs[3], weapon_px=dict(recs[3]['weapon_px'], fist2_off_line_px=6.1))   # round 1's off-line fist
        self.assertTrue(fails(checks.second_hand_checks(recs)))
        b = g['bodies'][0]
        b.weapons = [dict(w, outside=True, raw_deg=-35.0) if w.get('role') == 'second' else w for w in b.weapons]
        self.assertTrue(any('SECOND' in m for m in fails(checks.weapon_checks('', ['x'], [b]))))
        folded = fk(CANON, {'elbow_F': 160.0})                              # round 1's far elbow
        self.assertTrue(fails(checks.elbow_checks([g['recs'][0]], [folded], Camera(yaw=15.0))))


class MirrorAndHem(unittest.TestCase):
    """review 2026-11-28: heavy / robe strips a and b mirror on screen; the robe hem follows one smooth path"""
    def test_heavy_and_robe_halves_mirror_on_screen(self):
        for key in ('oswin', 'seraphine'):
            with self.subTest(key=key):
                spec, g, res = run(key)
                self.assertEqual(fails(res), [])
                R = g['recs']
                for f in range(4):
                    a, b = R[f]['joints'], R[f + 4]['joints']
                    for s, o in (('N', 'F'), ('F', 'N')):
                        for j in ('toetip', 'heel', 'ank'):
                            self.assertLessEqual(abs((a[j + s][0] - a['hip'][0]) - (b[j + o][0] - b['hip'][0])),
                                                 2.0 if j == 'ank' else 3.0,
                                                 (R[f]['frame'], j, s))
                rf = g['bodies'][0].joints['heelN']           # noqa: F841  (the heel ball; the table subtracts r_foot)
                for f in (0, 4):
                    J = R[f]['joints']
                    rear = min(J['heelN'][0], J['heelF'][0]) - CANON['r_foot'] - J['hip'][0]
                    self.assertGreaterEqual(rear / spec['step_px'], spec['rear_heel_min'] - 0.03)   # hip budget (Oswin -0.83)

    def test_hem_follows_a_smooth_path(self):
        self.assertEqual(checks.path_reversals([-89.0, -103.4, -89.4, -74.9, -89.4, -103.9, -89.4, -74.9], 2.0), 4)
        spec, g, res = run('mage')
        self.assertEqual(fails(res), [])
        for edge in ('front', 'back'):
            xs = [r['hem'][edge + '_x_px'] for r in g['recs']]
            self.assertLessEqual(checks.path_reversals(xs, checks.HEM_MOVE_PX), checks.HEM_REVERSALS)


class Request3D(unittest.TestCase):
    def test_request_folder(self):
        import request
        import add_gait
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, 'run__captain_blademaster')
            geo = request.build_request('sheet/captain/blademaster', out, force=True)
            self.assertEqual(sorted(os.listdir(out)), sorted(request.names('run')))
            self.assertEqual([m for lv, m in geo['m3d']['checks'] if lv == checks.FAIL], [])
            import json
            with open(os.path.join(out, 'pose.json'), encoding='utf-8') as f:
                pose = json.load(f)
            self.assertIn('mannequin3d', pose['source'])
            self.assertEqual((pose['scale'], pose['step_px'], pose['nominal_ms']), (0.1654, 275.0, 80))
            self.assertEqual(request.verify(out, 'sheet/captain/blademaster'), [])
            for h in 'ab':
                self.assertIsNotNone(add_gait.mannequin3d_reason(os.path.join(out, f'guide_run_plain_{h}.png')))
            with self.assertRaises(Exception):
                request.build_request('sheet/captain/blademaster', out)            # no --force: refuses to overwrite


class Actions(unittest.TestCase):
    def test_attack_and_hit(self):
        carry = dict(CARRY['warrior'])
        for act in ('attack', 'hit'):
            with self.subTest(act=act):
                r = build.render_action(act, CANON, carry, 15.0)
                res = checks.action_checks(act, r['names'], r['bodies'], r['plain'], r['recs'], lambda i: r['cams'][i])
                self.assertEqual(fails(res), [])
                for i, b in enumerate(r['bodies']):
                    self.assertEqual(checks.blade_overlap(b, r['cams'][i], {'head', 'nose'}), 0, r['names'][i])


class WeaponLimit(unittest.TestCase):
    POSE = {'shoulder_N': 0.0, 'elbow_N': 90.0}      # upright trunk: the near forearm points straight forward (0 deg)

    def sword(self, abs_angle, limit=None):
        pr = {'hand': 'N', 'kind': 'sword', 'abs_angle': abs_angle}
        if limit is not None:
            pr['limit'] = limit
        b = fk(CANON, self.POSE, props=[pr, {'hand': 'F', 'kind': 'shield'}])
        return b, b.weapons

    def test_forearm_reference(self):
        b, ws = self.sword(30.0)
        f = b.joints['wriN'] - b.joints['elbN']
        self.assertAlmostEqual(float(np.degrees(np.arctan2(f[1], f[0]))), 0.0, places=6)
        self.assertEqual(len(ws), 1)                   # the shield is not a weapon
        self.assertAlmostEqual(ws[0]['deg'], 30.0, places=4)
        self.assertFalse(ws[0]['clamped'])

    def test_clamps_dangling_and_overrotated(self):
        for req, want in ((-40.0, 0.0), (-100.0, 0.0), (150.0, 120.0), (-170.0, 120.0)):   # nearest bound on the circle
            with self.subTest(req=req):
                b, ws = self.sword(req)
                self.assertTrue(ws[0]['clamped'])
                self.assertAlmostEqual(ws[0]['raw_deg'], req, places=4)
                self.assertAlmostEqual(ws[0]['deg'], want, places=4)
                self.assertAlmostEqual(weapon_angle(b, 'N', b.joints['prop_dir_sword']), want, places=4)
                res = checks.weapon_checks('', ['x'], [b])
                self.assertEqual(res[0][0], checks.FAIL)
        b, ws = self.sword(0.0)                          # straight along the forearm: on the bound, not clamped
        self.assertFalse(ws[0]['clamped'])
        self.assertEqual(checks.weapon_checks('', ['x'], [b])[0][0], checks.OK)

    def test_per_character_limit(self):
        b, ws = self.sword(100.0, limit=[10.0, 80.0])
        self.assertTrue(ws[0]['clamped'])
        self.assertAlmostEqual(ws[0]['deg'], 80.0, places=4)
        self.assertEqual(weapon_limit({}), [0.0, 120.0])
        self.assertEqual(weapon_limit({'weapon_limit': {'min': 5, 'max': 90}}), [5.0, 90.0])
        for key in ('warrior', 'ironwall', 'mage'):
            self.assertEqual(weapon_limit(CARRY[key]), [0.0, 120.0])

    def test_no_authored_frame_needs_the_clamp(self):
        for key in ('warrior', 'ironwall', 'mage'):
            with self.subTest(key=key):
                _, g, _ = run(key)
                ws = [w for b in g['bodies'] for w in b.weapons if w.get('role') != 'second']
                self.assertEqual(len(ws), 8)
                self.assertEqual([w for w in ws if w['clamped']], [])
                self.assertTrue(all(0.0 <= w['deg'] <= 120.0 for w in ws))
        for act in ('attack', 'hit'):
            with self.subTest(act=act):
                r = build.render_action(act, CANON, dict(CARRY['warrior']), 15.0)
                ws = [w for b in r['bodies'] for w in b.weapons]
                self.assertEqual([w for w in ws if w['clamped']], [])


class PropKinds(unittest.TestCase):
    """bow / spear / dagger (review 2026-11-28) and the reverse grip"""
    POSE = {'shoulder_N': 0.0, 'elbow_N': 90.0, 'shoulder_F': 0.0, 'elbow_F': 90.0}

    def body(self, pr):
        return fk(CANON, self.POSE, props=[pr])

    def test_bow_limbs_and_string(self):
        b = self.body({'hand': 'F', 'kind': 'bow', 'abs_angle': 80.0, 'length': 125.0, 'back': 105.0})
        parts = {g['part'] for g in b.ghosts}
        self.assertTrue({'bow_grip', 'bow_limb_upper', 'bow_limb_lower', 'bow_string'} <= parts)
        J = b.joints
        # the string (tip to tip) runs BEHIND the grip (toward the body), the limbs bulge forward
        mid = (J['bow_upper'] + J['bow_lower']) / 2
        self.assertLess(mid[0], J['prop_grip'][0] - 10)
        self.assertEqual(b.weapons[0]['kind'], 'bow')
        self.assertAlmostEqual(b.weapons[0]['deg'], 80.0, places=4)      # grip axis = the stave at the grip

    def test_spear_head_and_two_hands(self):
        b = self.body({'hand': 'N', 'kind': 'spear', 'abs_angle': 60.0, 'length': 278.0, 'back': 80.0})
        self.assertIn('spear_head', {g['part'] for g in b.ghosts})
        self.assertEqual(b.weapons[0]['kind'], 'spear')
        spec, g, res = run('lancer', scale=0.1654)
        self.assertEqual(fails(res), [])
        self.assertTrue(all(len(bd.weapons) == 2 and bd.weapons[0]['kind'] == 'spear' and bd.weapons[1]['role'] == 'second'
                            for bd in g['bodies']))

    def test_reverse_grip_flips_the_blade_not_the_rule(self):
        fwd = self.body({'hand': 'N', 'kind': 'dagger', 'abs_angle': 30.0})
        rev = self.body({'hand': 'N', 'kind': 'dagger', 'abs_angle': 30.0, 'grip': 'reverse'})
        self.assertAlmostEqual(rev.weapons[0]['deg'], 30.0, places=4)        # the wrist rule: grip axis, inside 0..120
        self.assertFalse(rev.weapons[0]['clamped'])
        self.assertAlmostEqual(rev.weapons[0]['blade_deg'], -150.0, places=4)
        np.testing.assert_allclose(rev.joints['prop_dir_dagger'], -fwd.joints['prop_dir_dagger'], atol=1e-9)
        self.assertEqual(checks.weapon_checks('', ['x'], [rev])[0][0], checks.OK)
        # a grip axis outside the range is still clamped
        bad = self.body({'hand': 'N', 'kind': 'dagger', 'abs_angle': -60.0, 'grip': 'reverse'})
        self.assertTrue(bad.weapons[0]['clamped'])
        with self.assertRaises(ValueError):
            self.body({'hand': 'N', 'kind': 'bow', 'abs_angle': 80.0, 'grip': 'reverse'})
        with self.assertRaises(ValueError):
            self.body({'hand': 'N', 'kind': 'lance'})
        self.assertEqual(CARRY['fixer']['props'][0].get('grip'), 'reverse')
        self.assertEqual(weapon_limit(CARRY['fixer']), [0.0, 120.0])

    def test_painter_from_one_place(self):
        from common import load_painter
        self.assertIn(load_painter(), ('GPT', 'Antigravity'))


class Refusal(unittest.TestCase):
    def test_add_gait_refuses_unpainted_3d_guide(self):
        _, g, _ = run('warrior')
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, 'neutral_name_run_a.png')        # not under guides/, no pose.json beside it
            strip_of(g['plain'][:4]).save(p)
            self.assertIsNotNone(signature.mannequin3d_reason(p))
            import add_gait
            self.assertIsNotNone(add_gait.mannequin3d_reason(p))

    def test_recoloured_3d_guide_caught_by_silhouette(self):
        # a colour-swapped mannequin escapes the palette check, but matches its handed-out 3D guide at IoU ~1 > M3D_IOU
        import add_gait
        _, g, _ = run('warrior')
        strip = np.asarray(strip_of(g['plain'][:4]).convert('RGB')).copy()
        body = ~np.all(strip == np.array([255, 0, 255], np.uint8), -1)
        strip[body] = 255 - strip[body] // 2                  # every body colour changed
        with tempfile.TemporaryDirectory() as tmp:
            from PIL import Image
            p = os.path.join(tmp, 'recoloured.png')
            Image.fromarray(strip).save(p)
            self.assertIsNone(signature.mannequin3d_reason(p))
            arr = np.asarray(Image.open(p).convert('RGBA'))
            frames = [arr[:, k * 384:(k + 1) * 384] for k in range(4)]
            guide = np.asarray(strip_of(g['plain'][:4]).convert('RGBA'))
            drafts = [(f'g{k}', add_gait._crop(add_gait.frame_mask(guide[:, k * 384:(k + 1) * 384]))) for k in range(4)]
            iou = add_gait.best_guide_match(frames, stop=add_gait.M3D_IOU, drafts=drafts)[0]
            self.assertGreater(iou, add_gait.M3D_IOU)

    def test_painted_like_image_passes(self):
        rng = np.random.default_rng(1)
        arr = rng.integers(0, 255, (1024, 1536, 3), dtype=np.uint8)
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, 'x.png')
            from PIL import Image
            Image.fromarray(arr).save(p)
            self.assertIsNone(signature.mannequin3d_reason(p))


if __name__ == '__main__':
    unittest.main()

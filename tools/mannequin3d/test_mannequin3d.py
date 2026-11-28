"""Unit tests for the 3D mannequin (no drawing needed: they use the canonical proportions and specs/carry3d.json).

  python3 -m unittest tools/mannequin3d/test_mannequin3d.py        (about 1 minute)

determinism, floor / planting / IK / knee / mirror / band / feet / upper-body checks for the three movement classes,
a short-legged body (stride follows the legs), the sword never over the head (attack) nor the trunk (hit), the robe
hem, the weapon hand range (rig clamp + check, and no authored frame outside it), and that add_gait refuses an
unpainted 3D guide written anywhere (palette signature).
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
                ws = [w for b in g['bodies'] for w in b.weapons]
                self.assertEqual(len(ws), 8)
                self.assertEqual([w for w in ws if w['clamped']], [])
                self.assertTrue(all(0.0 <= w['deg'] <= 120.0 for w in ws))
        for act in ('attack', 'hit'):
            with self.subTest(act=act):
                r = build.render_action(act, CANON, dict(CARRY['warrior']), 15.0)
                ws = [w for b in r['bodies'] for w in b.weapons]
                self.assertEqual([w for w in ws if w['clamped']], [])


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

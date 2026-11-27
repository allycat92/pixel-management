"""Unit tests for the 3D mannequin (no drawing needed: they use the canonical proportions and specs/carry3d.json).

  python3 -m unittest tools/mannequin3d/test_mannequin3d.py        (about 1 minute)

determinism, floor / planting / IK / knee / mirror / band / feet / upper-body checks for the three movement classes,
a short-legged body (stride follows the legs), the sword never over the head (attack) nor the trunk (hit), the robe
hem, and that add_gait refuses an unpainted 3D guide written anywhere (palette signature).
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
from rig import CANON, scaled  # noqa: E402
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


class Refusal(unittest.TestCase):
    def test_add_gait_refuses_unpainted_3d_guide(self):
        _, g, _ = run('warrior')
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, 'neutral_name_run_a.png')        # not under guides/, no pose.json beside it
            strip_of(g['plain'][:4]).save(p)
            self.assertIsNotNone(signature.mannequin3d_reason(p))
            import add_gait
            self.assertIsNotNone(add_gait.mannequin3d_reason(p))

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

"""Orthographic z-buffered renderer for the 3D mannequin (numpy -> PIL).

Camera: looks along -z (the near side of the body, +z, faces the camera). `yaw` turns the whole body toward the viewer
for a slight 3/4 look (the chest gets an extra turn from the pose's chest_yaw). Screen x = world x' + the hip column,
screen y = floor_row + 1 - world y' (so a sole touching y = 0 has its lowest pixel on the floor row 870).

Primitives (from rig.fk): capsules with a radius that changes along the bone (swept spheres, sampled densely) and
ellipsoids (exact ray hit). Per pixel we keep the depth, the material, the part and the normal; shading is 4-band
cel shading so the result reads like a flat pixel mannequin. Near-side limbs are light/warm, far-side limbs dark/cool,
the trunk mid grey, the head lighter with a nose that shows where the face points. Joint markers use the
art/requests/guides/SPEC.md joint colours (near / far). Props and robes are 'ghosts': drawn see-through over the body.
"""
import numpy as np
from PIL import Image, ImageDraw

SLOT_W, SLOT_H, HIP_X, FLOOR = 384, 1024, 192, 870
MAGENTA = (255, 0, 255)
OUTLINE = np.array([36, 30, 44])
INNER = np.array([58, 48, 66])
LIGHT = np.array([-0.45, 0.75, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

# material base colours (dark -> light bands are derived)
MAT = {
    'body': (176, 168, 150),
    'head': (214, 198, 170),
    'near': (236, 214, 176),
    'near_foot': (226, 190, 140),
    'far': (104, 112, 140),
    'far_foot': (92, 96, 124),
    'prop': (150, 170, 182),
    'robe': (120, 160, 200),
}
MARK = {'belt': (92, 70, 52), 'sternum': (120, 96, 80), 'eye': (60, 48, 56)}
BANDS = (0.55, 0.72, 0.88, 1.0)
# SPEC.md joints layer colours (near, far)
JOINT_COL = {
    'H': ((255, 255, 0), (200, 200, 0)), 'knee': ((0, 255, 0), (0, 170, 0)), 'ank': ((0, 255, 255), (0, 170, 170)),
    'S': ((255, 128, 0), (200, 100, 0)), 'elb': ((255, 0, 0), (170, 0, 0)), 'hand': ((0, 0, 255), (0, 0, 170)),
}
NECK_COL = (255, 255, 255)


def view_matrix(yaw):
    a = np.radians(yaw)
    c, s = np.cos(a), np.sin(a)
    # turn the body toward the camera: forward x -> (cos, 0, sin)
    return np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])


class Camera:
    def __init__(self, yaw=15.0, size=(SLOT_W, SLOT_H), hip_x=HIP_X, floor=FLOOR, lock_hip=True):
        self.yaw, self.size, self.hip_x, self.floor, self.lock_hip = yaw, size, hip_x, floor, lock_hip
        self.V = view_matrix(yaw)
        self.dx = 0.0

    def fit(self, body, ref_x=None):
        """put the projected hip midpoint on the hip column (or the given world x on it)."""
        if self.lock_hip:
            p = self.V @ body.joints['hip'] if ref_x is None else self.V @ np.array([ref_x, 0.0, 0.0])
            self.dx = -p[0]
        return self

    def to_view(self, p):
        v = self.V @ np.asarray(p, float)
        return np.array([v[0] + self.dx, v[1], v[2]])

    def to_screen(self, p):
        v = self.to_view(p)
        return np.array([self.hip_x + v[0], self.floor + 1 - v[1]]), v[2]


class Buffers:
    def __init__(self, w, h):
        self.depth = np.full((h, w), -np.inf)
        self.mat = np.full((h, w), -1, int)
        self.part = np.full((h, w), -1, int)
        self.normal = np.zeros((h, w, 3))
        self.w, self.h = w, h


def _grid(buf, cam, x0, x1, y0, y1):
    """pixel centres of a screen box in VIEW coordinates (X right, Y up)"""
    xs = np.arange(x0, x1) + 0.5
    ys = np.arange(y0, y1) + 0.5
    X, Y = np.meshgrid(xs - cam.hip_x, (cam.floor + 1) - ys)
    return X, Y


def raster_capsule(buf, cam, prim, mi, pi):
    a, b = cam.to_view(prim['a']), cam.to_view(prim['b'])
    r0, r1 = prim['r0'], prim['r1']
    L = np.linalg.norm(b - a)
    n = int(np.ceil(L / max(0.8, 0.3 * min(r0, r1)))) + 1
    ts = np.linspace(0.0, 1.0, n)
    cs = a[None, :] + (b - a)[None, :] * ts[:, None]
    rs = r0 + (r1 - r0) * ts
    # bounding box in screen px
    sx = cam.hip_x + cs[:, 0]
    sy = cam.floor + 1 - cs[:, 1]
    rmax = rs.max()
    x0 = max(0, int(np.floor(sx.min() - rmax - 1)))
    x1 = min(buf.w, int(np.ceil(sx.max() + rmax + 1)))
    y0 = max(0, int(np.floor(sy.min() - rmax - 1)))
    y1 = min(buf.h, int(np.ceil(sy.max() + rmax + 1)))
    if x0 >= x1 or y0 >= y1:
        return
    X, Y = _grid(buf, cam, x0, x1, y0, y1)
    best = np.full((y1 - y0, x1 - x0), -np.inf)
    nrm = np.zeros((y1 - y0, x1 - x0, 3))
    for c, r in zip(cs, rs):
        dx = X - c[0]
        dy = Y - c[1]
        d2 = dx * dx + dy * dy
        inside = d2 <= r * r
        if not inside.any():
            continue
        dz = np.sqrt(np.maximum(r * r - d2, 0.0))
        z = c[2] + dz
        upd = inside & (z > best)
        if upd.any():
            best[upd] = z[upd]
    # smooth normal: from the closest point of the bone axis to the surface point (no banding between the spheres)
    hitm = best > -np.inf
    if hitm.any():
        ab = b - a
        L2 = max(ab @ ab, 1e-9)
        Pp = np.stack([X, Y, np.where(hitm, best, 0.0)], -1)
        t = np.clip(((Pp - a) @ ab) / L2, 0.0, 1.0)
        cpt = a + t[..., None] * ab
        nv = Pp - cpt
        nv /= np.maximum(np.linalg.norm(nv, axis=-1, keepdims=True), 1e-9)
        nrm[:] = nv
    _merge(buf, x0, x1, y0, y1, best, nrm, mi, pi)


def raster_ellipsoid(buf, cam, prim, mi, pi):
    c = cam.to_view(prim['c'])
    A = cam.V @ prim['R']          # columns = ellipsoid axes in view space
    rad = prim['radii']
    ext = np.sqrt(((A * rad[None, :]) ** 2).sum(1))   # half extents along view axes
    sx, sy = cam.hip_x + c[0], cam.floor + 1 - c[1]
    x0 = max(0, int(np.floor(sx - ext[0] - 1)))
    x1 = min(buf.w, int(np.ceil(sx + ext[0] + 1)))
    y0 = max(0, int(np.floor(sy - ext[1] - 1)))
    y1 = min(buf.h, int(np.ceil(sy + ext[1] + 1)))
    if x0 >= x1 or y0 >= y1:
        return
    X, Y = _grid(buf, cam, x0, x1, y0, y1)
    # ray: p(t) = (X, Y, 0) + t * (0, 0, -1); local q = A^T (p - c) / rad
    Ainv = A.T
    p0 = np.stack([X - c[0] + 0 * Y, Y - c[1] + 0 * X, np.zeros_like(X + Y) - c[2]], -1)
    q0 = (p0 @ Ainv.T) / rad
    d = (Ainv @ np.array([0.0, 0.0, -1.0])) / rad
    aa = d @ d
    bb = 2 * (q0 @ d)
    cc = (q0 * q0).sum(-1) - 1.0
    disc = bb * bb - 4 * aa * cc
    hit = disc >= 0
    if not hit.any():
        return
    t = (-bb - np.sqrt(np.maximum(disc, 0))) / (2 * aa)
    z = -t
    qh = q0 + t[..., None] * d
    n_loc = qh / rad
    nv = n_loc @ A.T
    nv /= np.maximum(np.linalg.norm(nv, axis=-1, keepdims=True), 1e-9)
    best = np.where(hit, z, -np.inf)
    _merge(buf, x0, x1, y0, y1, best, nv, mi, pi)


def _merge(buf, x0, x1, y0, y1, z, nrm, mi, pi):
    sub = buf.depth[y0:y1, x0:x1]
    upd = z > sub
    if not upd.any():
        return
    sub[upd] = z[upd]
    buf.mat[y0:y1, x0:x1][upd] = mi
    buf.part[y0:y1, x0:x1][upd] = pi
    buf.normal[y0:y1, x0:x1][upd] = nrm[upd]


def rasterize(prims, cam, w, h):
    buf = Buffers(w, h)
    mats, parts = [], []
    for pr in prims:
        if pr['mat'] not in mats:
            mats.append(pr['mat'])
        parts.append(pr['part'])
        mi, pi = mats.index(pr['mat']), len(parts) - 1
        (raster_capsule if pr['type'] == 'capsule' else raster_ellipsoid)(buf, cam, pr, mi, pi)
        if pr.get('clip_below') is not None:      # robe hem: nothing of this primitive below that height
            row = int(np.floor(cam.floor + 1 - pr['clip_below']))
            sel = buf.part[max(0, row):, :] == pi
            sub = buf.depth[max(0, row):, :]
            sub[sel] = -np.inf
            buf.part[max(0, row):, :][sel] = -1
            buf.mat[max(0, row):, :][sel] = -1
    return buf, mats, parts


def shade(buf, mats):
    h, w = buf.depth.shape
    out = np.zeros((h, w, 3))
    lam = np.clip(buf.normal @ LIGHT, 0, 1)
    inten = 0.45 + 0.55 * lam
    band = np.digitize(inten, [0.62, 0.78, 0.92])          # 0..3
    fac = np.array(BANDS)[band]
    for i, m in enumerate(mats):
        sel = buf.mat == i
        out[sel] = np.array(MAT[m])[None, :] * fac[sel][:, None]
    return out


def edges(buf, mask, depth_jump=7.0):
    """silhouette edge (inside the mask, 2 px) and inner occlusion edges (1 px on the farther side)"""
    m = mask
    inner = m.copy()
    inner[1:, :] &= m[:-1, :]
    inner[:-1, :] &= m[1:, :]
    inner[:, 1:] &= m[:, :-1]
    inner[:, :-1] &= m[:, 1:]
    sil = m & ~inner
    sil2 = sil.copy()
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        sil2 |= np.roll(np.roll(sil, dy, 0), dx, 1) & m
    occ = np.zeros_like(m)
    D, P = np.where(mask, buf.depth, -1e9), buf.part
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        D2 = np.roll(np.roll(D, dy, 0), dx, 1)
        P2 = np.roll(np.roll(P, dy, 0), dx, 1)
        occ |= m & (P2 >= 0) & (P2 != P) & (D2 - D > depth_jump)
    return sil2, occ


def body_marks(buf, cam, body, parts, P):
    """belt ring at the waist, sternum line on the chest front, eye band on the head front (masks)"""
    h, w = buf.depth.shape
    ys, xs = np.nonzero(buf.depth > -np.inf)
    marks = {}
    if len(xs) == 0:
        return marks
    # view -> world points of the visible surface
    Vx = xs + 0.5 - cam.hip_x - cam.dx
    Vy = (cam.floor + 1) - (ys + 0.5)
    Vz = buf.depth[ys, xs]
    W = np.stack([Vx, Vy, Vz], 1) @ cam.V        # V is orthonormal: world = V^T v  -> row form v @ V
    part = np.array(parts, dtype=object)[buf.part[ys, xs]]
    J, Fm = body.joints, body.frames

    def mask_of(sel):
        m = np.zeros((h, w), bool)
        m[ys[sel], xs[sel]] = True
        return m
    # belt: a band where the pelvis meets the spine
    up = Fm['spine'] @ np.array([0, 1.0, 0])
    belt_c = J['pelvis'] + up * (P['pelvis_r'][1] * 0.55)
    s = (W - belt_c) @ up
    marks['belt'] = mask_of(np.isin(part, ['pelvis', 'spine']) & (np.abs(s) < 5.0))
    # sternum: chest points near the chest's mid plane on its front half
    Rc = Fm['chest']
    loc = (W - J['chest']) @ Rc
    marks['sternum'] = mask_of((part == 'chest') & (np.abs(loc[:, 2]) < 2.6) & (loc[:, 0] > 0) & (loc[:, 1] > -P['chest_r'][1] * 0.75))
    Rh = Fm['head']
    lh = (W - J['head']) @ Rh
    marks['eye'] = mask_of((part == 'head') & (lh[:, 0] > P['head_r'][0] * 0.35) & (np.abs(lh[:, 1] - 2.0) < 3.2))
    return marks


def draw_joints(img, buf, cam, body, P, radius=5):
    d = ImageDraw.Draw(img)
    J = body.joints
    for key, (cn, cf) in JOINT_COL.items():
        for s, col in (('N', cn), ('F', cf)):
            p, z = cam.to_screen(J[key + s])
            x, y = int(round(p[0] - 0.5)), int(round(p[1] - 0.5))
            if not (0 <= x < buf.w and 0 <= y < buf.h):
                continue
            # visible if the joint centre is no deeper than its limb radius under the surface seen there
            if buf.depth[y, x] > z + 22:
                continue
            d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=col, outline=tuple(OUTLINE.tolist()))
    p, z = cam.to_screen(J['neck0'])
    x, y = int(round(p[0] - 0.5)), int(round(p[1] - 0.5))
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=NECK_COL, outline=tuple(OUTLINE.tolist()))


def render(body, P, cam, bg=MAGENTA, joints=True, ground=True, ghosts=True, marks=True):
    """-> (PIL RGB image of one slot, alpha mask of the body)"""
    w, h = cam.size
    buf, mats, parts = rasterize(body.prims, cam, w, h)
    mask = buf.depth > -np.inf
    rgb = shade(buf, mats)
    if marks:
        for k, m in body_marks(buf, cam, body, parts, P).items():
            rgb[m] = MARK[k]
    sil, occ = edges(buf, mask)
    rgb[occ] = INNER
    rgb[sil] = OUTLINE
    out = np.zeros((h, w, 3), np.uint8)
    out[:] = bg
    out[mask] = np.clip(rgb[mask], 0, 255).astype(np.uint8)
    if ghosts and body.ghosts:
        gb, gm, _ = rasterize(body.ghosts, cam, w, h)
        gmask = gb.depth > -np.inf
        gs = shade(gb, gm)
        gsil, _ = edges(gb, gmask)
        fill = gmask & ~gsil
        over_body = fill & mask
        out[over_body] = (out[over_body] * 0.55 + gs[over_body] * 0.45).astype(np.uint8)
        over_bg = fill & ~mask          # on the background: the prop colour itself (no magenta tint)
        out[over_bg] = np.clip(gs[over_bg] * 0.9 + 25, 0, 255).astype(np.uint8)
        gcol = np.array([20, 90, 110])
        out[gsil] = gcol
    img = Image.fromarray(out)
    if ground:
        d = ImageDraw.Draw(img)
        d.line([(0, cam.floor + 1), (w - 1, cam.floor + 1)], fill=(120, 120, 120), width=1)
    if joints:
        draw_joints(img, buf, cam, body, P)
    return img, mask


def project_joints(body, cam, names):
    out = {}
    for n in names:
        p, _ = cam.to_screen(body.joints[n])
        out[n] = [round(float(p[0]), 1), round(float(p[1]), 1)]
    return out

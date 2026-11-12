"""Black-hole sprite renderer for the TON 618 distance film (prefix k).
Ray marching adapted from the approved bh.py (Schwarzschild approximation, rs = 1, thin accretion disk 2.7..9.5 rs).
Differences: no background stars (the sky is composited separately), returns HDR colour + transmittance mask,
fixed camera at distance D (in rs) so the sprite can be scaled to any angular size."""
import numpy as np, math

def render_sprite(t, N=448, steps=170, D=24.0, el_deg=11.0, az_deg=0.0, tanH=0.5):
    az = math.radians(az_deg); el = math.radians(el_deg)
    cam = np.array([D * math.sin(az) * math.cos(el), D * math.sin(el), -D * math.cos(az) * math.cos(el)], np.float32)
    fwd = -cam / np.linalg.norm(cam); up0 = np.array([0, 1, 0], np.float32)
    right = np.cross(up0, fwd); right /= np.linalg.norm(right); up = np.cross(fwd, right)
    ys, xs = np.mgrid[0:N, 0:N].astype(np.float32)
    u = (xs + 0.5) / N * 2 - 1; v = 1 - (ys + 0.5) / N * 2
    d = fwd[None, None] + u[..., None] * tanH * right[None, None] + v[..., None] * tanH * up[None, None]
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    p = np.broadcast_to(cam, d.shape).reshape(-1, 3).astype(np.float32).copy(); vel = d.reshape(-1, 3).astype(np.float32).copy()
    n = p.shape[0]; col = np.zeros((n, 3), np.float32); T = np.ones(n, np.float32)
    alive = np.ones(n, bool); swallowed = np.zeros(n, bool)
    h2 = np.sum(np.cross(p, vel) ** 2, axis=1); RIN, ROUT = 2.7, 9.5
    for s in range(steps):
        idx = np.nonzero(alive)[0]
        if idx.size == 0: break
        pp = p[idx]; vv = vel[idx]; r2 = np.sum(pp * pp, 1); r = np.sqrt(r2)
        dt = np.clip(0.07 * r, 0.04, 1.2).astype(np.float32)
        acc = -1.5 * h2[idx][:, None] * pp / (r2 ** 2.5)[:, None]
        vn = vv + acc * dt[:, None]; vn /= np.linalg.norm(vn, axis=1, keepdims=True)
        pn = pp + vn * dt[:, None]
        cross = (pp[:, 1] * pn[:, 1]) < 0
        if cross.any():
            ci = np.nonzero(cross)[0]
            f = pp[ci, 1] / (pp[ci, 1] - pn[ci, 1]); pc = pp[ci] + (pn[ci] - pp[ci]) * f[:, None]
            rc = np.sqrt(pc[:, 0] ** 2 + pc[:, 2] ** 2); ok = (rc > RIN) & (rc < ROUT)
            if ok.any():
                oi = ci[ok]; pc = pc[ok]; rc = rc[ok]
                phi = np.arctan2(pc[:, 2], pc[:, 0]) + t * 3.2 * rc ** -1.5 * 4.0
                turb = 0.55 + 0.22 * np.sin(11 * phi + 2.7 * rc) + 0.16 * np.sin(27 * phi - 4.1 * rc + 1.3) + 0.10 * np.sin(61 * phi + 9.0 * rc)
                ring = 0.75 + 0.25 * np.sin(rc * 7.0)
                edge = np.clip((rc - RIN) / 0.9, 0, 1) * np.clip((ROUT - rc) / 2.5, 0, 1)
                dens = np.clip(turb * ring, 0, 1.3) * edge
                vd = np.stack([-pc[:, 2], np.zeros_like(rc), pc[:, 0]], 1) / rc[:, None]
                beta = np.clip(np.sqrt(0.5 / np.maximum(rc - 1.0, 0.3)), 0, 0.62)
                nph = -vn[ci[ok]]
                g = np.clip(1.0 / (1.0 - np.sum(vd * nph, 1) * beta), 0.45, 2.6)
                Tm = np.clip((rc / RIN) ** -0.75 * g, 0.15, 1.9)
                inten = dens * (g ** 3) * (rc / RIN) ** -1.1 * 1.7
                c0 = np.stack([np.clip(Tm * 1.15, 0, 1.6), np.clip(Tm ** 2.0 * 0.95, 0, 1.4), np.clip(Tm ** 4.0 * 0.85, 0, 1.2)], 1)
                gi = idx[oi]; a = np.clip(dens * 0.85, 0, 0.95)
                col[gi] += (T[gi] * inten)[:, None] * c0 * a[:, None] * 1.2
                T[gi] *= (1 - a)
        p[idx] = pn; vel[idx] = vn
        rn = np.sqrt(np.sum(pn * pn, 1)); sw = rn < 1.0; swallowed[idx[sw]] = True
        alive[idx[sw | (rn > 60.0)]] = False
    tm = (T * (~swallowed)).astype(np.float32)
    return col.reshape(N, N, 3).astype(np.float32), tm.reshape(N, N)

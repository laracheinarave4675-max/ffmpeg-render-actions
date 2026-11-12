"""Scenes k01..k15: 'What TON 618 Would Look Like From Earth at Different Distances' (SIMULATION).
All imagery is original and generated in code. The black hole is ray-marched (kdbh.py) and scaled to its true angular size
(Schwarzschild shadow, 66e9 solar masses); every number on screen comes from kdscript.py."""
import os, sys, math, time, urllib.request
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import engine
from engine import W, H, FD, sm
import kdscript as K
from kdbh import render_sprite

FAST = os.environ.get('KD_FAST') == '1'   # local smoke tests only
PXDEG = W / 90.0                          # horizontal field of view 90 degrees
SHADOW_FRAC = 5.196 / 24.0                # shadow diameter / sprite width for the sprite camera (D = 24 rs, tanH = 0.5)
GOLD = (255, 214, 120); CYAN = (150, 225, 255); WHITE = (238, 244, 255); GREY = (150, 160, 180)

# ---------------- fonts ----------------
for _f in ('Poppins-Light.ttf', 'Poppins-ExtraLight.ttf'):
    _p = FD + _f
    if not os.path.exists(_p):
        try: urllib.request.urlretrieve('https://github.com/google/fonts/raw/main/ofl/poppins/' + _f, _p)
        except Exception as e: print('font fallback', _f, e, flush=True)
_fc = {}
def fnt(size, w='Light'):
    k = (size, w)
    if k not in _fc:
        p = FD + 'Poppins-%s.ttf' % w
        if not os.path.exists(p): p = FD + 'Poppins-Regular.ttf'
        _fc[k] = ImageFont.truetype(p, size)
    return _fc[k]
def tdraw(d, x, y, text, font, fill, track=0.0, anchor='l'):
    ws = [d.textlength(ch, font=font) for ch in text]
    total = sum(ws) + track * (len(text) - 1)
    if anchor == 'm': x -= total / 2
    elif anchor == 'r': x -= total
    for ch, w in zip(text, ws):
        d.text((x, y), ch, font=font, fill=fill, anchor='lm'); x += w + track
def fa(c, a): return tuple(c) + (int(255 * max(0.0, min(1.0, a))),)
def A(u, a, b): return float(np.clip((u - a) / (b - a), 0, 1))
def fin(u, a, b): return float(sm(A(u, a, b)))

# ---------------- sky ----------------
SK = 1.25
def make_sky(seed=11):
    Wc, Hc = int(W * SK), int(H * SK)
    rng = np.random.default_rng(seed)
    img = np.zeros((Hc, Wc, 3), np.float32)
    n = 5600
    xs = rng.random(n) * (Wc - 2); ys = rng.random(n) * (Hc - 2)
    b = rng.random(n) ** 6 * 1.05 + 0.03
    cols = np.array([[0.85, 0.9, 1.0], [1.0, 1.0, 1.0], [1.0, 0.85, 0.7]], np.float32)
    cc = cols[rng.choice(3, n, p=[0.5, 0.35, 0.15])] * b[:, None]
    ix = xs.astype(int); iy = ys.astype(int); fx = (xs - ix)[:, None]; fy = (ys - iy)[:, None]
    for dx, dy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(img, (iy + dy, ix + dx), cc * w)
    stars = img + cv2.GaussianBlur(img, (0, 0), 0.8) * 1.2
    big = (b > 0.45)
    glow = np.zeros_like(img); np.add.at(glow, (iy[big], ix[big]), cc[big])
    stars = stars + cv2.GaussianBlur(glow, (0, 0), 2.4) * 2.2
    # milky way: band along a tilted line, modulated by multi-octave noise and dust lanes
    yy, xx = np.mgrid[0:Hc, 0:Wc].astype(np.float32)
    ang = math.radians(-24); nx, ny = -math.sin(ang), math.cos(ang)
    dist = (xx - Wc * 0.5) * nx + (yy - Hc * 0.46) * ny
    band = np.exp(-(dist / (0.16 * Hc)) ** 2)
    def fbm(seed2, octs=6):
        r = np.random.default_rng(seed2); o = np.zeros((Hc, Wc), np.float32); amp = 1.0; tot = 0
        for k in range(octs):
            s = 2 ** (k + 1)
            o += cv2.resize(r.random((max(2, Hc // 64 * s // 2), max(2, Wc // 64 * s // 2))).astype(np.float32), (Wc, Hc), interpolation=cv2.INTER_CUBIC) * amp
            tot += amp; amp *= 0.55
        return o / tot
    f1 = fbm(3); f2 = fbm(8)
    lane = np.clip(1.15 - 1.6 * np.clip(f2 - 0.42, 0, 1) * np.exp(-(dist / (0.07 * Hc)) ** 2) * 2.0, 0.25, 1.0)
    mw = band * (0.25 + 0.95 * f1 ** 2) * lane
    mwc = np.stack([mw * 0.55, mw * 0.62, mw * 0.85], -1) * 0.20
    core = np.exp(-(((xx - Wc * 0.52) / (0.22 * Wc)) ** 2 + ((yy - Hc * 0.46 - (xx - Wc * 0.52) * math.tan(ang)) / (0.09 * Hc)) ** 2))
    mwc += np.stack([core * 0.20, core * 0.15, core * 0.08], -1) * 0.30 * band[..., None]
    return np.clip(stars * 0.95 + mwc, 0, 4).astype(np.float32)
SKY = make_sky()

def sky_view(ox, oy):
    M = np.float32([[1, 0, -((SKY.shape[1] - W) / 2 + ox)], [0, 1, -((SKY.shape[0] - H) / 2 + oy)]])
    return cv2.warpAffine(SKY, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ---------------- horizon / ground ----------------
_xs = np.arange(W, dtype=np.float32)
YH = (H * 0.862 + 15 * np.sin(_xs * 0.0045 + 1.1) + 9 * np.sin(_xs * 0.013 + 0.3) + 4 * np.sin(_xs * 0.037 + 2.0)).astype(np.float32)
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
GMASK = cv2.GaussianBlur((_yy >= YH[None, :]).astype(np.float32), (0, 0), 1.1)[..., None]
RIM = np.exp(-np.clip(_yy - YH[None, :], 0, None) / 55.0)[..., None].astype(np.float32)
_gn = cv2.resize(np.random.default_rng(4).random((9, 16)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)[..., None]
GBASE = (0.0065 + 0.006 * _gn).astype(np.float32) * np.array([0.8, 0.9, 1.1], np.float32)
AIRGLOW = (np.exp(-np.clip(YH[None, :] - _yy, 0, None) / 62.0) * (_yy < YH[None, :]))[..., None].astype(np.float32) * np.array([0.030, 0.058, 0.090], np.float32)

def lightk(mag): return float(np.clip((-mag - 8.0) / 32.0, 0, 1) ** 1.6)

# ---------------- sprites (cached across scenes inside a render job) ----------------
_SP = {}
def sprites(N, NK, dt=0.015):
    if FAST: N, NK = 160, 6
    key = (N, NK)
    if key in _SP: return _SP[key]
    path = '/tmp/kd_sprites_%d_%d.npz' % (N, NK)
    if os.path.exists(path):
        z = np.load(path); _SP[key] = (z['col'], z['tm']); return _SP[key]
    t0 = time.time(); cols = np.zeros((NK, N, N, 3), np.float16); tms = np.zeros((NK, N, N), np.float16)
    for k in range(NK):
        c, tm = render_sprite(k * dt, N=N); cols[k] = c; tms[k] = tm
    np.savez(path + '.tmp.npz', col=cols, tm=tms); os.replace(path + '.tmp.npz', path)
    print('sprites %d x %d built in %.0fs' % (N, NK, time.time() - t0), flush=True)
    _SP[key] = (cols, tms); return _SP[key]
def sprite_at(N, NK, u):
    cols, tms = sprites(N, NK)
    n = cols.shape[0]; x = float(np.clip(u, 0, 1)) * (n - 1); k = int(min(x, n - 2)); a = x - k
    return (cols[k].astype(np.float32) * (1 - a) + cols[k + 1].astype(np.float32) * a,
            tms[k].astype(np.float32) * (1 - a) + tms[k + 1].astype(np.float32) * a)

def place(img, wpx, cx, cy, fill):
    """scale a square sprite to width wpx and put its centre at (cx, cy) on a full-frame canvas (sub-pixel)"""
    n = img.shape[0]; wp = max(2, int(round(wpx)))
    r = cv2.resize(img, (wp, wp), interpolation=cv2.INTER_AREA if wp < n else cv2.INTER_CUBIC)
    M = np.float32([[1, 0, cx - wp / 2.0], [0, 1, cy - wp / 2.0]])
    return cv2.warpAffine(r, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=fill)

# ---------------- primitives ----------------
def blob(lin, x, y, sig, color, amp):
    r = int(sig * 3.2) + 2
    x0, x1 = int(max(x - r, 0)), int(min(x + r + 1, W)); y0, y1 = int(max(y - r, 0)), int(min(y + r + 1, H))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    g = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * sig * sig))[..., None]
    lin[y0:y1, x0:x1] += g * (np.array(color, np.float32) * amp)
def spikes(lin, x, y, L, amp, color=(0.8, 0.9, 1.0)):
    layer = np.zeros((H, W, 3), np.float32)
    for ang in (0, 90):
        for sgn in (-1, 1):
            for i in range(40):
                f0 = i / 40.0; f1 = (i + 1) / 40.0
                a = amp * (1 - f0) ** 2.2
                dx = math.cos(math.radians(ang)) * sgn; dy = math.sin(math.radians(ang)) * sgn
                cv2.line(layer, (int(x + dx * L * f0 * 16), int(y + dy * L * f0 * 16)), (int(x + dx * L * f1 * 16), int(y + dy * L * f1 * 16)),
                         tuple(float(c * a) for c in color), 1, cv2.LINE_AA, shift=4)
    lin += cv2.GaussianBlur(layer, (0, 0), 1.0)

def point_params(mag):
    b = 0.25 + 0.75 * float(np.clip((6.0 - mag) / 30.0, 0, 1))
    sg = 1.6 + 38.0 * float(np.clip((-mag - 10.0) / 25.0, 0, 1)) ** 1.3
    sp = 8 + 140 * float(np.clip((6.0 - mag) / 40.0, 0, 1)) ** 1.6
    return b, sg, sp

def tonemap(lin): return np.clip(1 - np.exp(-np.clip(lin, 0, 60) * 1.35), 0, 1) ** (1 / 1.02)
def vignette(img):
    r = np.sqrt(((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2)
    return img * np.clip(1.12 - 0.42 * r ** 2, 0.35, 1)[..., None]

# ---------------- text layer ----------------
def sci_mag(m):
    if m >= 1e9: return '%.1f BILLION' % (m / 1e9)
    if m >= 1e6: return ('%d MILLION' % round(m / 1e6)) if m >= 1e7 else ('%.1f MILLION' % (m / 1e6))
    if m >= 1e3: return '{:,}'.format(int(round(m, -2 if m < 1e4 else -3 if m < 1e5 else -4)))
    return '%d' % round(m)
def fmt_ang(deg):
    a = deg * 3600.0
    if a < 1e-3: return '%.3g millionths of an arcsecond' % (a * 1e6) if a >= 1e-6 else '%.1f µas' % (a * 1e6)
    if a < 1: return '%.3g arcsecond' % a if a >= 0.1 else '%.2g thousandths of an arcsecond' % (a * 1e3)
    if a < 60: return '%d arcseconds' % round(a)
    if deg < 1: return '%.1f arcminutes' % (a / 60)
    return '%.1f°' % deg
def fmt_moon(r):
    if 0.95 <= r <= 1.05: return 'the size of our Moon'
    if r >= 1.0: return '%.1f× our Moon' % r if r < 10 else '%d× our Moon' % round(r)
    if r >= 1e-3: return '1/%s of our Moon' % '{:,}'.format(int(round(1 / r)))
    return 'under 1/1,000 of our Moon'

METER = [10.8e9, 1e9, 1e8, 2.5e6, 1e5, 2.6e4, 1e3, 100, 11.6, 4.24, 1.0, 0.5, 0.25]
def meter(d, ly, a):
    x0, x1, y = W - 30 - 250, W - 30, 62
    lo, hi = math.log10(0.25), math.log10(10.8e9)
    px = lambda v: x0 + (hi - math.log10(v)) / (hi - lo) * (x1 - x0)
    d.line([(x0, y), (x1, y)], fill=fa(GREY, 0.45 * a), width=1)
    for v in METER:
        d.line([(px(v), y - 4), (px(v), y + 4)], fill=fa(GREY, 0.55 * a), width=1)
    cx = px(ly); d.line([(cx, y - 8), (cx, y + 8)], fill=fa(GOLD, a), width=2); d.ellipse([cx - 4, y - 4, cx + 4, y + 4], fill=fa(GOLD, a))
    tdraw(d, x0, y + 20, '10.8 BILLION LY', fnt(10, 'Regular'), fa(GREY, 0.8 * a), 1.4, 'l')
    tdraw(d, x1, y + 20, '0.25 LY', fnt(10, 'Regular'), fa(GREY, 0.8 * a), 1.4, 'r')

def wrap(text, font, d, maxw):
    ws = text.split(' '); lines = []; cur = ''
    for w in ws:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines
def caption(d, text, a):
    f = fnt(25, 'Light'); lines = wrap(text, f, d, W * 0.84)
    y0 = H - 54 - (len(lines) - 1) * 33
    for i, ln in enumerate(lines):
        y = y0 + i * 33
        d.text((W / 2 + 1.5, y + 2), ln, font=f, fill=(0, 0, 0, int(150 * a)), anchor='mm')
        d.text((W / 2, y), ln, font=f, fill=fa(WHITE, a), anchor='mm')

def caption_plan(row):
    caps = row[8]; tt = K.cap_times(row[0], len(caps))
    return [(c, a, b) for c, (a, b) in zip(caps, tt)]   # absolute seconds

def fade_io(frame, t, T, last):
    a = fin(t, 0.0, 0.9) * (1.0 if last else (1 - fin(t, T - 1.0, T)))
    return frame if a >= 0.999 else (frame.astype(np.float32) * a).astype(np.uint8)

def bigblur(img, sigma):
    if sigma <= 12: return cv2.GaussianBlur(img, (0, 0), sigma)
    small = cv2.resize(img, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    return cv2.resize(cv2.GaussianBlur(small, (0, 0), sigma / 4.0), (W, H), interpolation=cv2.INTER_CUBIC)

def draw_layer(frame01, items_fn):
    im = Image.fromarray((np.clip(frame01, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(im, 'RGBA')
    items_fn(d); return np.asarray(im)

def hud(d, row, a, theta_deg):
    th = theta_deg
    pairs = [('DISTANCE TO TON 618', row[3]), ('TON 618 IN THE SKY', fmt_ang(th) + '  ·  ' + fmt_moon(th / K.MOON) if th > 1e-4 else (row[6] or fmt_ang(th)) + '  ·  too small to see'),
             ('BRIGHTNESS', row[7])]
    y = 40
    for lab, val in pairs:
        tdraw(d, 34, y, lab, fnt(11, 'Regular'), fa(GREY, 0.85 * a), 1.9, 'l')
        d.text((34, y + 22), val, font=fnt(22, 'Light'), fill=fa(WHITE, a), anchor='lm'); y += 62

def leader_label(d, x, y, r, text, a, dx=-90, dy=-62, ring=True):
    lx, ly = x + dx, y + dy
    if ring: d.ellipse([x - r, y - r, x + r, y + r], outline=fa(WHITE, 0.85 * a), width=1)
    ang = math.atan2(ly - y, lx - x)
    d.line([(x + math.cos(ang) * r, y + math.sin(ang) * r), (lx + 6, ly + 4)], fill=fa(WHITE, 0.7 * a), width=1)
    tdraw(d, lx + 4, ly - 8, text, fnt(12, 'Regular'), fa(WHITE, a), 1.8, 'r')

# ---------------- station scenes ----------------
BHX, BHY = W * 0.54, H * 0.40
def make_station(row):
    sid, tbig, tsmall, dtext, ly, th_over, th_text, btext = row[:8]
    mag = float(btext.split(' ')[1].replace('+', '').replace('−', '-'))
    th = th_over if th_over else K.shadow_deg(ly)
    tpx = th * PXDEG                       # shadow diameter in pixels at 1280 wide
    lk = lightk(mag); cplan = caption_plan(row)
    mode = 'inset' if tpx < 14 else 'direct'
    big = tpx > 150
    N, NK = (448, 48)
    if sid == 'k14': N, NK = (640, 28)
    def fn(t, T, tg, cap):
        u = t / T
        ox = -2.4 * (t - T / 2); oy = 0.5 * (t - T / 2)
        lin = sky_view(ox, oy) * (1.0 - 0.85 * min(1.0, lk * 1.4))
        cx, cy = BHX + ox, BHY + oy
        tint = np.array([0.95, 0.9, 1.0], np.float32) * (1 - min(1, lk * 1.3)) + np.array([1.0, 0.72, 0.45], np.float32) * min(1, lk * 1.3)
        if lk > 0:
            g = np.exp(-(((_xx - cx) / (W * 0.45)) ** 2 + ((_yy - cy) / (H * 0.55)) ** 2))[..., None]
            lin += g * tint * lk * 0.55
        lin += AIRGLOW * (1 + 3 * lk)
        theta_px = tpx
        if mode == 'inset':
            b, sg, sp = point_params(mag)
            blob(lin, cx, cy, sg, (0.85, 0.93, 1.0), b * 0.9); blob(lin, cx, cy, 1.1, (1, 1, 1), b * 1.8)
            if sp > 14: spikes(lin, cx, cy, sp, b * 0.9)
        else:
            col, tm = sprite_at(N, NK, A(u, 0.0, 1.0))
            wpx = max(tpx / SHADOW_FRAC, 8)
            colf = place(col, wpx, cx, cy, (0, 0, 0)); tmf = place(tm, wpx, cx, cy, 1.0)
            if tmf.ndim == 3: tmf = tmf[..., 0]
            lin = lin * tmf[..., None] + colf * 1.0
            s1 = max(1.5, tpx * 0.045); s2 = max(4.0, tpx * 0.22)
            lin += bigblur(colf, s1) * 0.9 + bigblur(colf, s2) * 0.7
        # ground, lit by the quasar
        glit = (GBASE + lk * 0.55 * (0.20 + 0.80 * RIM) * tint[None, None, :] * 0.8)
        lin = lin * (1 - GMASK) + glit * GMASK
        img = vignette(tonemap(lin))
        # moon-for-scale reference (stations from 1,000 ly inwards)
        moon = None
        if ly <= 1e3 and th < 30:
            moon = (cx - 170 - 0.5 * tpx, cy + 18)
            mr = max(2.0, 0.5 * K.MOON * PXDEG)
            yy0, yy1 = int(moon[1] - mr - 3), int(moon[1] + mr + 4); xx0, xx1 = int(moon[0] - mr - 3), int(moon[0] + mr + 4)
            sub = img[yy0:yy1, xx0:xx1]; yg, xg = np.mgrid[yy0:yy1, xx0:xx1].astype(np.float32)
            m = np.clip(mr + 0.6 - np.sqrt((xg - moon[0]) ** 2 + (yg - moon[1]) ** 2), 0, 1)[..., None]
            img[yy0:yy1, xx0:xx1] = sub * (1 - m) + np.array([0.72, 0.72, 0.70], np.float32) * m
        titles = a_t = None
        def items(d):
            # title card
            ta = fin(t, 0.2, 1.0) * (1 - fin(t, 3.2, 4.2))
            if ta > 0.01:
                tdraw(d, W / 2, H * 0.47, tbig, fnt(40, 'Light'), fa(WHITE, ta), 9.0, 'm')
                tdraw(d, W / 2, H * 0.47 + 46, tsmall, fnt(13, 'Medium'), fa(GOLD, 0.9 * ta), 4.5, 'm')
            ha = fin(t, 1.0, 2.2)
            hud(d, row, ha, th)
            meter(d, ly, ha)
            tdraw(d, W - 30, 34, 'SIMULATION · ESTIMATED VALUES', fnt(11, 'Regular'), fa(GREY, 0.85), 1.6, 'r')
            if mode == 'inset':
                R = 118; ix, iy = W * 0.83, H * 0.42
                if ha > 0.01:
                    ang = math.atan2(iy - cy, ix - cx); r0 = 15
                    d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], outline=fa(WHITE, 0.8 * ha), width=1)
                    for k in range(0, 30, 2):
                        f0 = k / 30; f1 = (k + 1) / 30
                        xa, ya = cx + math.cos(ang) * (r0 + f0 * (math.hypot(ix - cx, iy - cy) - r0 - R)), cy + math.sin(ang) * (r0 + f0 * (math.hypot(ix - cx, iy - cy) - r0 - R))
                        xb, yb = cx + math.cos(ang) * (r0 + f1 * (math.hypot(ix - cx, iy - cy) - r0 - R)), cy + math.sin(ang) * (r0 + f1 * (math.hypot(ix - cx, iy - cy) - r0 - R))
                        d.line([(xa, ya), (xb, yb)], fill=fa(WHITE, 0.55 * ha), width=1)
                    tdraw(d, cx - 8, cy - 40, 'TON 618', fnt(12, 'Regular'), fa(WHITE, ha), 1.8, 'r')
            elif tpx < 40:
                leader_label(d, cx, cy, max(18, tpx * 1.9), 'TON 618', ha)
            elif tpx < 400:
                leader_label(d, cx - tpx * 0.5, cy - tpx * 0.5, 0, 'TON 618', ha, dx=-60 - tpx * 0.2, dy=-40 - tpx * 0.1, ring=False)
            if moon is not None and ha > 0.01:
                mr = max(2.0, 0.5 * K.MOON * PXDEG)
                d.ellipse([moon[0] - mr - 9, moon[1] - mr - 9, moon[0] + mr + 9, moon[1] + mr + 9], outline=fa(GREY, 0.7 * ha), width=1)
                tdraw(d, moon[0], moon[1] + mr + 26, 'OUR MOON · FOR SCALE', fnt(11, 'Regular'), fa(GREY, ha), 1.6, 'm')
            for c, a0, a1 in cplan:
                f = fin(t, a0, a0 + 0.6) * (1 - fin(t, a1 - 0.6, a1))
                if f > 0.01: caption(d, c, f)
        out = draw_layer(img, items)
        if mode == 'inset':   # magnified inset composited after text so the circle edge stays clean
            R = 118; ix, iy = int(W * 0.83), int(H * 0.42)
            col, tm = sprite_at(N, NK, A(u, 0.0, 1.0))
            wpx = 0.40 * 2 * R / SHADOW_FRAC
            c2 = place(col, wpx, ix, iy, (0, 0, 0)); c2 = c2 + cv2.GaussianBlur(c2, (0, 0), 3.0) * 0.8 + cv2.GaussianBlur(c2, (0, 0), 12.0) * 0.5
            ins = tonemap(c2 * 1.1) * 255
            m = np.clip(R + 0.8 - np.sqrt((_xx - ix) ** 2 + (_yy - iy) ** 2), 0, 1)[..., None] * fin(t, 1.0, 2.2)
            base = out.astype(np.float32) * (1 - m * 0.97) + (ins + np.array([2, 3, 6], np.float32)) * m
            out = np.clip(base, 0, 255).astype(np.uint8)
            def items2(d):
                ha = fin(t, 1.0, 2.2)
                d.ellipse([ix - R, iy - R, ix + R, iy + R], outline=fa(WHITE, 0.85 * ha), width=1)
                tdraw(d, ix, iy - R - 22, 'MAGNIFIED', fnt(11, 'Regular'), fa(GREY, ha), 2.2, 'm')
                d.text((ix, iy + R + 28), '%s ×' % sci_mag(0.40 * 2 * R / max(tpx, 1e-30)), font=fnt(24, 'Light'), fill=fa(WHITE, ha), anchor='mm')
                tdraw(d, ix, iy + R + 54, 'THE SHADOW, MADE VISIBLE', fnt(10, 'Regular'), fa(GOLD, 0.9 * ha), 2.0, 'm')
            im = Image.fromarray(out); items2(ImageDraw.Draw(im, 'RGBA')); out = np.asarray(im)
        return fade_io(out, t, T, False)
    return fn

# ---------------- Earth limb scenes (intro / outro) ----------------
_r = np.random.default_rng(21)
_cl = [(_r.uniform(0.15, 0.85) * W, _r.uniform(0.80, 0.97) * H) for _ in range(46)]
_pts = np.concatenate([np.stack([c[0] + _r.normal(0, 38, 70), c[1] + _r.normal(0, 11, 70)], 1) for c in _cl])
_pb = _r.random(len(_pts)) ** 3 * 0.9 + 0.1
def earth_limb(zoom, drift):
    cx = W * 0.5; cy = H * 2.02; R = H * 1.27 * zoom
    rr = np.sqrt((_xx - cx) ** 2 + (_yy - cy) ** 2)
    surf = np.array([0.006, 0.010, 0.024], np.float32) * (rr < R)[..., None]
    rim_in = np.exp(-np.clip(R - rr, 0, None) / (0.011 * R)) * (rr < R)
    atm = np.exp(-np.clip(rr - R, 0, None) / (0.020 * R)) * (rr >= R)
    img = surf + (rim_in * 0.30 + atm * 0.85)[..., None] * np.array([0.18, 0.36, 0.95], np.float32)
    lights = np.zeros((H, W, 3), np.float32)
    px = np.clip(_pts[:, 0] + drift, 0, W - 2).astype(int); py = np.clip(_pts[:, 1], 0, H - 2).astype(int)
    ok = np.sqrt((px - cx) ** 2 + (py - cy) ** 2) < R * 0.985
    np.add.at(lights, (py[ok], px[ok]), (np.array([1.0, 0.78, 0.45], np.float32) * _pb[ok][:, None]))
    img += lights * 0.9 + cv2.GaussianBlur(lights, (0, 0), 1.6) * 3.0 + cv2.GaussianBlur(lights, (0, 0), 6.0) * 2.2
    return img

def make_edge(row, intro):
    cplan = caption_plan(row); sid = row[0]; last = not intro
    def fn(t, T, tg, cap):
        u = t / T
        ox = -2.0 * (t - T / 2); oy = 0.4 * (t - T / 2)
        lin = sky_view(ox, oy) * 0.9
        el = earth_limb(1.0 + 0.045 * u, -10 * u)
        lin = np.maximum(lin * (1 - np.clip(el.mean(-1, keepdims=True) * 2, 0, 1)), 0) + el
        img = vignette(tonemap(lin))
        px, py = W * 0.67 + ox, H * 0.27 + oy
        def items(d):
            if intro:
                ta = fin(t, 0.6, 2.0) * (1 - fin(t, 6.2, 7.6))
                if ta > 0.01:
                    tdraw(d, W / 2, H * 0.40, 'WHAT TON 618 WOULD LOOK LIKE', fnt(44, 'Light'), fa(WHITE, ta), 8.0, 'm')
                    tdraw(d, W / 2, H * 0.40 + 62, 'FROM EARTH AT DIFFERENT DISTANCES', fnt(26, 'Light'), fa(WHITE, 0.92 * ta), 7.0, 'm')
                    tdraw(d, W / 2, H * 0.40 + 118, 'SIMULATION', fnt(13, 'Medium'), fa(GOLD, 0.9 * ta), 6.0, 'm')
                la = fin(t, 16.0, 17.5)
            else:
                la = fin(t, 0.3, 1.5) * (1 - fin(t, 9.0, 10.5))
            if la > 0.01:
                d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=fa(WHITE, la))
                leader_label(d, px, py, 14, 'TON 618', la, dx=-90, dy=-60)
                tdraw(d, px - 88, py - 40, '10.8 BILLION LIGHT-YEARS', fnt(11, 'Regular'), fa(GREY, la), 1.5, 'r')
            if not intro:
                ca = fin(t, 25.2, 26.8)
                if ca > 0.01:
                    tdraw(d, W / 2, H * 0.43, 'TON 618', fnt(52, 'Light'), fa(WHITE, ca), 12.0, 'm')
                    tdraw(d, W / 2, H * 0.43 + 56, '10.8 BILLION LIGHT-YEARS AWAY', fnt(18, 'Light'), fa(WHITE, 0.9 * ca), 6.0, 'm')
                    tdraw(d, W / 2, H * 0.43 + 92, 'EVERY IMAGE IN THIS FILM IS A SIMULATION', fnt(11, 'Regular'), fa(GOLD, 0.9 * ca), 3.5, 'm')
            tdraw(d, W - 30, 34, 'SIMULATION', fnt(11, 'Regular'), fa(GREY, 0.85), 1.6, 'r')
            for c, a0, a1 in cplan:
                f = fin(t, a0, a0 + 0.6) * (1 - fin(t, a1 - 0.6, a1))
                if f > 0.01: caption(d, c, f)
        return fade_io(draw_layer(img, items), t, T, last)
    return fn

FUNCSK = {}
for _row in K.SCENES:
    _sid = _row[0]
    if _sid == 'k01': FUNCSK[_sid] = make_edge(_row, True)
    elif _sid == 'k15': FUNCSK[_sid] = make_edge(_row, False)
    else: FUNCSK[_sid] = make_station(_row)
STARTK = {k: 0.0 for k in FUNCSK}

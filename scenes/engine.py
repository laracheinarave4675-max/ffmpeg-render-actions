import numpy as np, cv2, subprocess, os, sys, time
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FPS = int(os.environ.get('SCENE_FPS', '24'))
OUT = os.environ.get('SCENE_OUT', '/tmp/scene_out')
os.makedirs(OUT, exist_ok=True)
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts') + os.sep
def _ensure_fonts():
    import urllib.request
    os.makedirs(FD, exist_ok=True)
    for f in ('Poppins-Bold.ttf', 'Poppins-Medium.ttf', 'Poppins-Regular.ttf'):
        p = FD + f
        if not os.path.exists(p):
            urllib.request.urlretrieve('https://github.com/google/fonts/raw/main/ofl/poppins/' + f, p)
_ensure_fonts()
_fc = {}
def font(size, w='Bold'):
    k = (size, w)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + f'Poppins-{w}.ttf', size)
    return _fc[k]

def sm(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)
def lerp(a, b, u): return a + (b - a) * u

# ---------- starfield ----------
def make_bg(seed=3):
    rng = np.random.default_rng(seed)
    img = np.zeros((H, W, 3), np.float32)
    n = 2600
    xs = rng.integers(0, W, n); ys = rng.integers(0, H, n)
    b = rng.random(n) ** 7 * 0.95 + 0.04
    tint = rng.choice([0, 1, 2], n, p=[0.5, 0.35, 0.15])
    cols = np.array([[0.85, 0.9, 1.0], [1.0, 1.0, 1.0], [1.0, 0.85, 0.7]], np.float32)
    img[ys, xs] = cols[tint] * b[:, None]
    img = img + cv2.GaussianBlur(img, (0, 0), 1.6) * 1.4
    return np.clip(img, 0, 1)
BG = make_bg()

# ---------- galaxy ----------
class Galaxy:
    def __init__(s, seed=7, N=150000):
        rng = np.random.default_rng(seed)
        arm = rng.integers(0, 4, N)
        r = np.clip(rng.gamma(2.0, 0.17, N), 0.015, 1.15)
        th = np.log(r + 0.12) * 3.4 + arm * np.pi / 2 + rng.normal(0, 0.16 / (0.3 + r), N)
        x = r * np.cos(th); y = r * np.sin(th); z = rng.normal(0, 0.02 + 0.02 * np.exp(-r * 2), N)
        nb = 26000
        rb = np.abs(rng.normal(0, 0.09, nb)); tb = rng.uniform(0, 2 * np.pi, nb); ub = rng.uniform(-1, 1, nb)
        xb = rb * np.sqrt(1 - ub ** 2) * np.cos(tb); yb = rb * np.sqrt(1 - ub ** 2) * np.sin(tb); zb = rb * ub * 0.7
        s.X = np.concatenate([x, xb]).astype(np.float32); s.Y = np.concatenate([y, yb]).astype(np.float32)
        s.Z = np.concatenate([z, zb]).astype(np.float32)
        s.R = np.sqrt(s.X ** 2 + s.Y ** 2)
        warm = np.clip(1 - s.R / 0.32, 0, 1) ** 1.3
        pink = (rng.random(len(s.X)) < 0.03)[:, None] * np.array([0.5, -0.1, 0.1], np.float32)
        col = np.stack([0.55 + 0.45 * warm, 0.68 + 0.17 * warm, 1.0 - 0.5 * warm], 1) + pink
        bright = 0.16 + 0.55 * np.exp(-s.R * 5)
        bright *= rng.uniform(0.5, 1.4, len(s.X))
        s.w = (col * bright[:, None]).astype(np.float32)

def gal_layer(g, cx, cy, scale, tilt, tg, expo=1.0, warp=None, rotk=0.012):
    ang = tg * rotk * (1.5 / (0.5 + g.R))
    c, s_ = np.cos(ang), np.sin(ang)
    xr = g.X * c - g.Y * s_; yr = g.X * s_ + g.Y * c
    tl = np.radians(tilt); ct, st = np.cos(tl), np.sin(tl)
    yt = yr * ct - g.Z * st
    sx = xr * scale + cx; sy = yt * scale + cy
    if warp is not None:
        sx, sy = warp(sx, sy)
    ix = sx.astype(np.int32); iy = sy.astype(np.int32)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    idx = iy[ok] * W + ix[ok]
    layer = np.empty((H, W, 3), np.float32)
    for ch in range(3):
        layer[:, :, ch] = np.bincount(idx, weights=g.w[ok, ch], minlength=W * H).reshape(H, W)
    k = float(np.clip((520 / scale) ** 1.3, 0.4, 5))
    layer *= k
    sg = max(1.2, 6 * min(1.0, (520 / scale) ** 0.9))
    glow = cv2.GaussianBlur(layer, (0, 0), sg) * 1.6 + cv2.GaussianBlur(layer, (0, 0), 1.2) * 0.9 + layer * 0.7
    return 1 - np.exp(-glow * expo)

def screen(a, b): return 1 - (1 - a) * (1 - b)

G = Galaxy()
gx_, gy_ = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))

# ---------- black hole lensing (stylised, artist's concept) ----------
def lens(img, cx, cy, thE, shadow=True, ring=True):
    dx = gx_ - cx; dy = gy_ - cy
    r2 = dx * dx + dy * dy + 1.0
    f = 1 - (thE * thE) / r2
    mx = (cx + dx * f).astype(np.float32); my = (cy + dy * f).astype(np.float32)
    out = cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    r = np.sqrt(r2)
    if ring:
        phi = np.arctan2(dy, dx)
        rr = 0.64 * thE
        band = np.exp(-((r - rr) / (0.07 * thE)) ** 2)
        asym = 0.55 + 0.45 * np.cos(phi - 0.6)
        glow = np.exp(-((r - rr) / (0.28 * thE)) ** 2) * 0.35
        warm = np.stack([1.0 * np.ones_like(r), 0.72 * np.ones_like(r), 0.42 * np.ones_like(r)], 2)
        out = screen(out, np.clip((band * asym * 1.4 + glow * asym)[:, :, None] * warm, 0, 1))
    if shadow:
        m = np.clip((r - 0.56 * thE) / 3.0, 0, 1)[:, :, None]
        out = out * m
    return out

# ---------- overlays ----------
def overlay(frame01, items=(), caption=None, tag=None, fade=1.0):
    fr = (np.clip(frame01 * fade, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(fr); d = ImageDraw.Draw(im, 'RGBA')
    for it in items:
        k = it.get('k', 'text')
        a = int(255 * it.get('a', 1))
        if a <= 0: continue
        col = it.get('c', (255, 255, 255))
        if k == 'text':
            d.text((it['x'], it['y']), it['t'], font=font(it.get('s', 34), it.get('w', 'Bold')), fill=col + (a,), anchor=it.get('an', 'mm'))
        elif k == 'line':
            d.line([(it['x1'], it['y1']), (it['x2'], it['y2'])], fill=col + (a,), width=it.get('wd', 3))
        elif k == 'dot':
            r = it.get('r', 6)
            d.ellipse([it['x'] - r, it['y'] - r, it['x'] + r, it['y'] + r], fill=col + (a,), outline=it.get('oc'))
        elif k == 'ring':
            r = it.get('r', 20)
            d.ellipse([it['x'] - r, it['y'] - r, it['x'] + r, it['y'] + r], outline=col + (a,), width=it.get('wd', 2))
        elif k == 'rect':
            d.rectangle([it['x1'], it['y1'], it['x2'], it['y2']], fill=col + (a,))
    if tag:
        d.text((W - 28, 26), tag, font=font(15, 'Medium'), fill=(180, 190, 210, 190), anchor='ra')
    if caption:
        d.rectangle([0, H - 44, W, H], fill=(0, 0, 0, 150))
        d.text((24, H - 22), 'REVIEW: ' + caption, font=font(16, 'Regular'), fill=(170, 175, 190, 255), anchor='lm')
    return np.asarray(im)

def vignette(img):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = np.clip(1.15 - 0.45 * r ** 2, 0.35, 1)[:, :, None]
    return img * v

# ---------- rendering ----------
def render_scene(name, T, fn, tg0, caption=None, review=True):
    nfr = int(round(T * FPS))
    path = f'{OUT}/{name}.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(nfr):
        t = i / FPS
        out = fn(t, T, tg0 + t, caption if review else None)
        p.stdin.write(out.tobytes())
    p.stdin.close(); p.wait()
    print(name, 'T=%.1f' % T, 'render %.1fs' % (time.time() - t0), flush=True)
    return path

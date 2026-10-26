import sys, json
from engine import *

BHX, BHY = 940, 350
TAG = "ARTIST'S CONCEPT"
SEQ = [  # (id, narration text, paragraph_end)
 ('s01_open', "Picture the Milky Way.", 0),
 ('s02_place', "Not as a photograph, but as a place.", 0),
 ('s03_disk', "A glowing disk of stars, one hundred thousand light-years across.", 0),
 ('s04_light', "So wide that light itself needs a hundred thousand years to travel from one edge to the other.", 0),
 ('s05_stars', "Inside it, at least one hundred billion stars. Perhaps four hundred billion.", 0),
 ('s06_orbit', "Every one of them in motion, circling a distant center, in a slow dance that takes our own Sun more than two hundred million years to complete a single turn.", 1),
 ('s07_approach', "Now picture something approaching it out of the dark.", 0),
 ('s08_dark', "Something that gives off no light of its own at all.", 0),
 ('s09_mass', "A black hole carrying somewhere between forty and sixty-six billion times the mass of the Sun.", 0),
 ('s10_title', "Its name is TON six-eighteen.", 1),
 ('s11a_paper', "On paper, the comparison looks ridiculous. A galaxy a hundred thousand light-years wide.", 0),
 ('s11b_inset', "And a black hole whose boundary light could cross in about two weeks.", 0),
 ('s12_mass', "Yet the number that matters most in gravity is not size. It is mass.", 0),
 ('s13a_bar', "The black hole at the heart of our own galaxy weighs about four million Suns.", 0),
 ('s13b_bar', "TON six-eighteen weighs ten to sixteen thousand times more than that.", 0),
 ('s14_stars', "Its mass is comparable to all the stars of the Milky Way, added together.", 1),
 ('s15a_take', "So the question almost asks itself. If this thing reached our galaxy, would it simply take it?", 0),
 ('s15b_drain', "Would the stars drift inward, one by one, like water toward a drain?", 0),
 ('s15c_fade', "Would the spiral thin out, and fade, and vanish behind a surface from which nothing returns?", 0),
 ('s16_meal', "That is the image the internet loves. A monster, a galaxy, a meal.", 1),
]
def est(text, pend):
    words = len(text.split()); sents = text.count('.') + text.count('?')
    return words / 2.47 + 0.45 * sents + (0.6 if pend else 0)
DUR = {k: est(t, p) for k, t, p in SEQ}
START = {}; acc = 0
for k, t, p in SEQ:
    START[k] = acc; acc += DUR[k]
TOTAL = acc

def gal(cx, cy, scale, tilt, tg, expo=1.0, warp=None, bgdim=0.8):
    return screen(BG * bgdim, gal_layer(G, cx, cy, scale, tilt, tg, expo, warp))
def enc(tg, gcx, gcy, gs, gt, bx, by, th, expo=1.0, warp=None):
    base = gal(gcx, gcy, gs, gt, tg, expo, warp)
    return lens(base, bx, by, th)
def A(u, a, b): return float(np.clip((u - a) / (b - a), 0, 1))

def bar_items(u1, u2, cx, scale, y, label):
    half = 1.1 * scale
    x0, x1 = cx - half, cx + half
    xe = x0 + (x1 - x0) * u1
    items = [{'k': 'line', 'x1': x0, 'y1': y, 'x2': xe, 'y2': y, 'wd': 3, 'c': (120, 220, 255), 'a': 0.95},
             {'k': 'line', 'x1': x0, 'y1': y - 14, 'x2': x0, 'y2': y + 14, 'wd': 3, 'c': (120, 220, 255), 'a': u1 > 0}]
    if u1 >= 0.999:
        items.append({'k': 'line', 'x1': x1, 'y1': y - 14, 'x2': x1, 'y2': y + 14, 'wd': 3, 'c': (120, 220, 255)})
    items.append({'k': 'text', 'x': cx, 'y': y + 44, 't': label, 's': 34, 'c': (230, 240, 255), 'a': u2})
    return items, x0, x1

# ---------------- scenes ----------------
def f_s01(t, T, tg, cap):
    u = t / T
    fade = sm(A(u, 0.0, 0.9)) ** 1.4
    img = gal(640, 360, lerp(360, 400, u), lerp(72, 66, u), tg, expo=0.4 + 0.7 * fade, bgdim=0.8 * (0.3 + 0.7 * fade))
    return overlay(vignette(img) * (0.25 + 0.75 * fade), caption=cap)
def f_s02(t, T, tg, cap):
    u = t / T
    img = gal(640, 360, lerp(400, 440, u), lerp(66, 62, u), tg, expo=1.1)
    return overlay(vignette(img), caption=cap)
def f_s03(t, T, tg, cap):
    u = t / T
    sc = lerp(440, 450, u)
    img = gal(640, 350, sc, 62, tg, expo=1.1)
    items, *_ = bar_items(sm(A(u, 0.1, 0.65)), sm(A(u, 0.6, 0.85)), 640, sc, 560, '100,000 LIGHT-YEARS')
    return overlay(vignette(img), items, caption=cap)
def f_s04(t, T, tg, cap):
    u = t / T
    sc = 450
    img = gal(640, 350, sc, 62, tg, expo=1.0)
    items, x0, x1 = bar_items(1, 1, 640, sc, 560, '100,000 LIGHT-YEARS')
    p = A(u, 0.06, 0.94)
    x = lerp(x0, x1, p)
    items += [{'k': 'line', 'x1': x0, 'y1': 560, 'x2': x, 'y2': 560, 'wd': 6, 'c': (255, 230, 150), 'a': 0.9},
              {'k': 'dot', 'x': x, 'y': 560, 'r': 11, 'c': (255, 245, 210)},
              {'k': 'dot', 'x': x, 'y': 560, 'r': 22, 'c': (255, 220, 120), 'a': 0.25},
              {'k': 'text', 'x': 640, 'y': 640, 't': f'{int(100000 * p):,} YEARS', 's': 30, 'c': (255, 235, 170)}]
    return overlay(vignette(img), items, caption=cap)
def f_s05(t, T, tg, cap):
    u = sm(t / T)
    sc = lerp(450, 950, u)
    img = gal(640 - (sc - 450) * 0.22, 350 + (sc - 450) * 0.06, sc, lerp(62, 50, u), tg, expo=1.25)
    a = sm(A(t / T, 0.3, 0.5))
    items = [{'k': 'text', 'x': 640, 'y': 600, 't': '100–400 BILLION STARS', 's': 52, 'c': (255, 255, 255), 'a': a}]
    return overlay(vignette(img), items, caption=cap)
def f_s06(t, T, tg, cap):
    u = t / T
    sc = 470; tilt = lerp(62, 20, sm(A(u, 0, 0.35)))
    cx, cy = 640, 345
    img = gal(cx, cy, sc, tilt, tg, expo=1.0)
    ct = np.cos(np.radians(tilt))
    items = []
    for k in range(40, 0, -1):
        ph = 2 * np.pi * max(u - k * 0.006, 0) * 0.98
        xx = cx + 0.57 * sc * np.cos(ph); yy = cy + 0.57 * sc * np.sin(ph) * ct
        items.append({'k': 'dot', 'x': xx, 'y': yy, 'r': 3, 'c': (255, 215, 90), 'a': 0.5 * (1 - k / 40)})
    ph = 2 * np.pi * u * 0.98
    xx = cx + 0.57 * sc * np.cos(ph); yy = cy + 0.57 * sc * np.sin(ph) * ct
    items += [{'k': 'dot', 'x': xx, 'y': yy, 'r': 9, 'c': (255, 225, 110)},
              {'k': 'dot', 'x': xx, 'y': yy, 'r': 20, 'c': (255, 210, 90), 'a': 0.25},
              {'k': 'text', 'x': xx, 'y': yy - 34, 't': 'OUR SUN', 's': 20, 'c': (255, 235, 160)},
              {'k': 'text', 'x': 640, 'y': 640, 't': 'ONE ORBIT ≈ 230 MILLION YEARS', 's': 36, 'c': (240, 245, 255), 'a': sm(A(u, 0.15, 0.4))}]
    return overlay(vignette(img), items, caption=cap)

def f_s07(t, T, tg, cap):
    u = sm(t / T)
    img = enc(tg, 330, 360, 210, 58, lerp(1500, 1010, u), BHY, lerp(14, 60, u))
    return overlay(vignette(img), caption=cap, tag=TAG)
def f_s08(t, T, tg, cap):
    u = sm(t / T)
    img = enc(tg, 330, 360, 210, 58, lerp(1010, 940, u), BHY, lerp(60, 90, u), expo=0.9)
    return overlay(vignette(img), caption=cap, tag=TAG)
def f_s09(t, T, tg, cap):
    u = sm(t / T)
    th = lerp(90, 108, u)
    img = enc(tg, 330, 360, 210, 58, BHX, BHY, th, expo=0.9)
    a = sm(A(t / T, 0.35, 0.6))
    items = [{'k': 'line', 'x1': BHX, 'y1': BHY + 0.7 * th, 'x2': BHX, 'y2': 560, 'wd': 2, 'c': (255, 210, 130), 'a': a},
             {'k': 'text', 'x': BHX, 'y': 596, 't': '40–66 BILLION SOLAR MASSES', 's': 34, 'c': (255, 225, 160), 'a': a}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_s10(t, T, tg, cap):
    u = sm(t / T)
    img = enc(tg, 330, 360, 210, 58, BHX, BHY, lerp(108, 135, u), expo=lerp(0.9, 0.0, sm(A(t / T, 0.0, 0.6))))
    a = sm(A(t / T, 0.15, 0.55))
    items = [{'k': 'text', 'x': 400, 'y': 345, 't': 'TON 618', 's': 132, 'c': (255, 255, 255), 'a': a}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)

def f_s11a(t, T, tg, cap):
    u = t / T
    sc = 430
    img = gal(640, 330, sc, 62, tg, expo=1.0)
    items, *_ = bar_items(1, 1, 640, sc, 545, '100,000 LIGHT-YEARS')
    items.append({'k': 'text', 'x': 640, 'y': 80, 't': 'THE MILKY WAY', 's': 40, 'c': (255, 255, 255), 'a': sm(A(u, 0.05, 0.3))})
    return overlay(vignette(img), items, caption=cap)

INSET_BG = None
def f_s11b(t, T, tg, cap):
    u = t / T
    gcx, gcy, gs = 330, 380, 235
    img = gal(gcx, gcy, gs, 62, tg, expo=1.0)
    icx, icy = 920, 360
    rad = 215 * sm(A(u, 0.35, 0.8))
    items = []
    pulse = 14 + 6 * np.sin(t * 6)
    items.append({'k': 'ring', 'x': gcx, 'y': gcy, 'r': pulse, 'c': (255, 220, 120), 'wd': 2})
    items.append({'k': 'dot', 'x': gcx, 'y': gcy, 'r': 3, 'c': (255, 240, 200)})
    p = sm(A(u, 0.15, 0.45))
    lx = lerp(gcx + 14, icx - max(rad, 40), p); ly = lerp(gcy, icy, p)
    items.append({'k': 'line', 'x1': gcx + 14, 'y1': gcy, 'x2': lx, 'y2': ly, 'wd': 2, 'c': (255, 220, 120), 'a': 0.8 * (p > 0)})
    if rad > 4:
        ins = lens(BG * 0.9, icx, icy, 100)
        ins = vignette(ins * 1.0)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        m = np.clip((rad - np.sqrt((xx - icx) ** 2 + (yy - icy) ** 2)) / 3, 0, 1)[:, :, None]
        img = img * (1 - m) + ins * m
        items.append({'k': 'ring', 'x': icx, 'y': icy, 'r': rad, 'c': (255, 220, 120), 'wd': 3, 'a': 0.95})
    a2 = sm(A(u, 0.7, 0.9))
    items += [{'k': 'text', 'x': icx, 'y': icy - 250, 't': 'EVENT HORIZON: ≈ 0.04 LIGHT-YEARS ACROSS', 's': 24, 'c': (255, 235, 180), 'a': a2},
              {'k': 'text', 'x': icx, 'y': icy + 250, 't': 'LIGHT CROSSES IT IN ABOUT TWO WEEKS', 's': 24, 'c': (255, 235, 180), 'a': a2},
              {'k': 'text', 'x': gcx, 'y': gcy + 200, 't': 'MILKY WAY', 's': 26, 'c': (230, 240, 255), 'a': a2},
              {'k': 'text', 'x': 600, 'y': 240, 't': '× 2,500,000 ZOOM', 's': 28, 'c': (255, 220, 120), 'a': sm(A(u, 0.45, 0.65))}]
    return overlay(img, items, caption=cap, tag=TAG)

def f_s12(t, T, tg, cap):
    u = t / T
    grid = np.zeros((H, W, 3), np.float32)
    for x in range(-W, 2 * W, 56): cv2.line(grid, (x, 0), (x, H), (0.20, 0.55, 0.75), 1, cv2.LINE_AA)
    for y in range(-H, 2 * H, 56): cv2.line(grid, (0, y), (W, y), (0.20, 0.55, 0.75), 1, cv2.LINE_AA)
    m = sm(A(u, 0.35, 0.95))
    base = screen(BG * 0.5, grid * 0.6)
    dx = gx_ - 640; dy = gy_ - 410
    d2 = dx * dx + dy * dy
    f = 1 + (4.0 * m) / (1 + d2 / (150.0 ** 2))
    img = cv2.remap(base, (640 + dx * f).astype(np.float32), (410 + dy * f).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    dip = np.exp(-d2 / (2 * (22 * m + 1) ** 2))[:, :, None] * m
    img = img * (1 - 0.9 * dip) + np.array([1.0, 0.8, 0.45], np.float32) * np.exp(-d2 / (2 * (60 * m + 1) ** 2))[:, :, None] * 0.18 * m
    items = [{'k': 'text', 'x': 640, 'y': 100, 't': 'NOT SIZE.', 's': 70, 'c': (200, 205, 215), 'a': 1 - 0.6 * sm(A(u, 0.4, 0.6))}]
    sl = sm(A(u, 0.3, 0.45))
    items.append({'k': 'line', 'x1': 640 - 215, 'y1': 100, 'x2': 640 - 215 + 430 * sl, 'y2': 100, 'wd': 6, 'c': (255, 120, 100), 'a': sl > 0})
    items.append({'k': 'text', 'x': 640, 'y': 620, 't': 'IT IS MASS.', 's': 96, 'c': (255, 215, 120), 'a': sm(A(u, 0.5, 0.75))})
    return overlay(vignette(img), items, caption=cap)

def chart(t, T, tg, cap, stage):
    u = t / T
    p1 = sm(A(u, 0.0, 0.7)) if stage == 0 else 1
    p2 = sm(A(u, 0.0, 0.7)) if stage == 1 else (1 if stage > 1 else 0)
    p3 = sm(A(u, 0.0, 0.7)) if stage == 2 else 0
    img = BG * 0.45
    x0 = 330; xr = W - 90
    def X(v): return x0 + (np.log10(v) - 6) / (11.3 - 6) * (xr - x0)
    rows = [(230, 4.3e6, (110, 215, 255), "SAGITTARIUS A*  ·  OUR GALAXY'S BLACK HOLE", '≈ 4 MILLION SUNS', p1),
            (360, 6.6e10, (255, 205, 100), 'TON 618', '≈ 40–66 BILLION SUNS', p2),
            (490, 5.8e10, (170, 195, 255), 'ALL STARS OF THE MILKY WAY', '≈ 50–65 BILLION SUNS (ESTIMATE)', p3)]
    items = [{'k': 'text', 'x': 640, 'y': 60, 't': 'MASS, IN SOLAR MASSES (LOG SCALE)', 's': 26, 'c': (190, 200, 220), 'an': 'mm'}]
    for v, name in [(1e6, '1 MILLION'), (1e8, '100 MILLION'), (1e10, '10 BILLION')]:
        x = X(v)
        items.append({'k': 'line', 'x1': x, 'y1': 150, 'x2': x, 'y2': 590, 'wd': 1, 'c': (110, 130, 160), 'a': 0.5})
        items.append({'k': 'text', 'x': x, 'y': 615, 't': name, 's': 18, 'w': 'Medium', 'c': (160, 175, 200)})
    for y, v, col, name, val, p in rows:
        if p <= 0: continue
        xe = x0 + (X(v) - x0) * p
        items.append({'k': 'rect', 'x1': x0, 'y1': y - 28, 'x2': xe, 'y2': y + 28, 'c': col, 'a': 0.92})
        items.append({'k': 'text', 'x': x0, 'y': y - 50, 't': name, 's': 24, 'c': (235, 240, 250), 'an': 'lm', 'a': min(1, p * 3)})
        if p > 0.95:
            items.append({'k': 'text', 'x': xe + (-14 if v > 1e10 else 14), 'y': y, 't': val, 's': 26, 'c': (10, 12, 25) if v > 1e10 else (255, 255, 255), 'an': 'rm' if v > 1e10 else 'lm'})
    if stage >= 1 and p2 > 0.9:
        a = sm(A(u, 0.7, 0.95)) if stage == 1 else 1
        items.append({'k': 'text', 'x': 800, 'y': 296, 't': '10,000–16,000 × MORE MASSIVE', 's': 30, 'c': (255, 215, 120), 'a': a})
    return overlay(vignette(img), items, caption=cap)
def f_s13a(t, T, tg, cap): return chart(t, T, tg, cap, 0)
def f_s13b(t, T, tg, cap): return chart(t, T, tg, cap, 1)
def f_s14(t, T, tg, cap): return chart(t, T, tg, cap, 2)

def f_s15a(t, T, tg, cap):
    u = sm(t / T)
    img = enc(tg, 300, 370, 250, 60, lerp(1010, 930, u), BHY, 100)
    items = [{'k': 'text', 'x': 640, 'y': 62, 't': 'THE POPULAR IMAGE', 's': 28, 'c': (255, 140, 120), 'a': sm(A(t / T, 0.1, 0.35))}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_s15b(t, T, tg, cap):
    u = sm(t / T)
    pull = 0.85 * u
    def warp(sx, sy):
        dx = BH2 - sx; dy = BHY - sy
        d = np.sqrt(dx * dx + dy * dy)
        k = pull * np.exp(-d / 1500.0)
        return sx + dx * k, sy + dy * k
    img = enc(tg, 300, 370, 250, 60, 930, BHY, 100, warp=warp)
    items = [{'k': 'text', 'x': 640, 'y': 62, 't': 'THE POPULAR IMAGE', 's': 28, 'c': (255, 140, 120)}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
BH2 = 930
def f_s15c(t, T, tg, cap):
    u = sm(t / T)
    pull = 0.85 + 0.12 * u
    def warp(sx, sy):
        dx = BH2 - sx; dy = BHY - sy
        d = np.sqrt(dx * dx + dy * dy)
        k = pull * np.exp(-d / 1500.0)
        return sx + dx * k, sy + dy * k
    img = enc(tg, 300, 370, 250, 60, 930, BHY, 100, expo=1.0 * (1 - 0.9 * u), warp=warp)
    items = [{'k': 'text', 'x': 640, 'y': 62, 't': 'THE POPULAR IMAGE', 's': 28, 'c': (255, 140, 120)}]
    return overlay(vignette(img), items, caption=cap, tag=TAG)
def f_s16(t, T, tg, cap):
    u = t / T
    img = lens(BG * 0.8, 960, 360, 120 + 20 * u)
    items = []
    for i, (txt, a0) in enumerate([('A MONSTER', 0.05), ('A GALAXY', 0.35), ('A MEAL', 0.65)]):
        items.append({'k': 'text', 'x': 120, 'y': 220 + i * 120, 't': txt, 's': 78, 'c': (255, 255, 255), 'an': 'lm', 'a': sm(A(u, a0, a0 + 0.12))})
    return overlay(vignette(img), items, caption=cap, tag=TAG)

FUNCS = {k: globals()['f_' + k.split('_')[0]] for k, *_ in SEQ}

def assemble(order, durs, out):
    inputs = []; 
    for k in order: inputs += ['-i', f'{OUT}/{k}.mp4']
    fc = ''; prev = '[0:v]'; acc = 0.0
    for i in range(1, len(order)):
        acc += durs[order[i - 1]]
        lab = f'[v{i}]'
        fc += f'{prev}[{i}:v]xfade=transition=fade:duration=0.5:offset={acc:.3f}{lab};'
        prev = lab
    fc += f'{prev}fade=t=out:st={sum(durs.values()) - 1.0:.3f}:d=1.0[outv]'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', fc, '-map', '[outv]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', out]
    subprocess.run(cmd, check=True)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'plan':
        for k, t, p in SEQ: print(f'{k:14s} start {START[k]:6.1f}  dur {DUR[k]:5.1f}')
        print('TOTAL', round(TOTAL, 1))
    elif mode == 'frames':
        import glob
        for k, t, p in SEQ:
            T = DUR[k]; fr = FUNCS[k](T * 0.7, T, START[k] + T * 0.7, None)
            Image.fromarray(fr).resize((640, 360)).save(f'{OUT}/f_{k}.png')
        print('ok')
    elif mode == 'render':
        only = sys.argv[2:] or [k for k, *_ in SEQ]
        for i, (k, t, p) in enumerate(SEQ):
            if k not in only: continue
            T = DUR[k] + (0.5 if i < len(SEQ) - 1 else 0)
            render_scene(k, T, FUNCS[k], START[k], caption=t)
        print('RENDER_DONE', flush=True)
    elif mode == 'assemble':
        assemble([k for k, *_ in SEQ], DUR, os.path.join(OUT,'preview_2min.mp4')); print('ASSEMBLED')

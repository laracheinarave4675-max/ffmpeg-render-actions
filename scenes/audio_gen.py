"""Original procedural audio: sound effects + mood-based music tracks.
Everything is synthesized with numpy (no samples, no licences).
Usage: python3 audio_gen.py <out_dir>      -> writes <out_dir>/sfx/*.wav and <out_dir>/music/*.wav
"""
import os, sys, wave
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
RNG = np.random.default_rng(2026)

def T(d): return np.arange(int(d * SR)) / SR
def lp(x, fc, o=2): return sosfilt(butter(o, min(fc, SR / 2 - 100), 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def bp(x, f0, f1, o=2): return sosfilt(butter(o, [f0, min(f1, SR / 2 - 100)], 'band', fs=SR, output='sos'), x)
def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak
def fade(x, a=0.005, r=0.05):
    n = len(x); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e = np.ones(n); e[:na] = np.linspace(0, 1, na); e[-nr:] = np.linspace(1, 0, nr)
    return x * e
def noise(d): return RNG.normal(0, 1, int(d * SR))

def sweep_noise(d, f0, f1, width=0.6):
    """Noise through a band-pass whose centre glides f0 -> f1 (exponential)."""
    n = int(d * SR); x = noise(d); out = np.zeros(n); blk = 1024
    zi = None
    for i in range(0, n, blk):
        u = i / max(1, n)
        fc = f0 * (f1 / f0) ** u
        lo, hi = fc * (1 - width / 2), fc * (1 + width)
        sos = butter(2, [max(30, lo), min(hi, SR / 2 - 200)], 'band', fs=SR, output='sos')
        seg, _ = sosfilt(sos, x[i:i + blk], zi=np.zeros((sos.shape[0], 2)))
        out[i:i + blk] = seg
    return out

def reverb(x, secs=2.5, wet=0.3, lpf=5000):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = noise(secs) * np.exp(-t * (6.9 / secs))
    ir = lp(ir, lpf); ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    ir /= np.sqrt(np.sum(ir ** 2))
    y = fftconvolve(x, ir)[:len(x) + n // 2]
    y[:len(x)] = x * (1 - wet) + y[:len(x)] * wet
    return y

def stereo(x, width=0.0004):
    """Cheap widening: tiny Haas delay on one side."""
    d = int(width * SR)
    l = x; r = np.concatenate([np.zeros(d), x])[:len(x)]
    return np.stack([l, r], 1)

def save(path, x, stereo_in=False):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = stereo(x)
    pcm = (x * 32767).astype('<i2')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

# ------------------------------------------------------------------ SFX
def whoosh(d=1.3, up=True):
    f0, f1 = (300, 5000) if up else (5000, 300)
    x = sweep_noise(d, f0, f1, 0.9)
    t = T(d); u = t / d
    e = np.sin(np.pi * u) ** (1.6 if up else 1.2)
    if not up: e = np.sin(np.pi * np.minimum(1, u * 0.9 + 0.1)) ** 1.2 * (1 - u * 0.2)
    return fade(norm(x * e, 0.7), 0.01, 0.2)

def riser(d=4.0):
    t = T(d); u = t / d
    n = sweep_noise(d, 200, 7000, 1.2) * u ** 2.2
    ph = 2 * np.pi * np.cumsum(80 * (6 ** u)) / SR
    tone = np.sin(ph) * u ** 1.5 * 0.5 + np.sin(ph * 1.5) * u ** 2 * 0.25
    x = norm(n, 0.6) + tone
    return fade(norm(x, 0.75), 0.05, 0.12)

def boom(d=2.8):
    t = T(d)
    f = 38 + 70 * np.exp(-t * 9)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 1.5)
    thump = lp(noise(d), 180) * np.exp(-t * 6) * 2.0
    air = reverb(lp(noise(d), 900) * np.exp(-t * 4) * 0.5, 2.2, 0.5)[:len(t)]
    return fade(norm(sub * 1.3 + thump + air, 0.9), 0.002, 0.3)

def tick(f=2300):
    d = 0.03; t = T(d)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 180) + hp(noise(d), 3000) * np.exp(-t * 400) * 0.3
    return norm(x, 0.55)

def ping(f=880, d=1.6, soft=False):
    t = T(d)
    x = np.zeros_like(t)
    for k, (m, a, dec) in enumerate([(1.0, 1.0, 3.2), (2.76, 0.45, 5.0), (5.4, 0.18, 8.0), (8.9, 0.08, 12.0)]):
        x += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * dec)
    x *= np.minimum(1, t / (0.012 if not soft else 0.05))
    return fade(norm(reverb(x, 1.6, 0.25)[:len(t)], 0.6), 0.002, 0.25)

def blips(f=520, n=3, gap=0.06):
    seq = []
    for i in range(n):
        d = 0.09; t = T(d)
        x = np.sin(2 * np.pi * f * (1.25 ** i) * t) * np.exp(-t * 22)
        seq.append(np.concatenate([x, np.zeros(int(gap * SR))]))
    return norm(np.concatenate(seq), 0.5)

def sparkle(d=1.8, dens=24):
    n = int(d * SR); x = np.zeros(n)
    for _ in range(dens):
        s = RNG.integers(0, int(n * 0.8)); f = RNG.uniform(2500, 9000); dd = RNG.uniform(0.08, 0.3)
        t = T(dd); g = np.sin(2 * np.pi * f * t) * np.exp(-t * RNG.uniform(14, 30)) * RNG.uniform(0.3, 1)
        x[s:s + len(g)] += g[:n - s]
    return fade(norm(reverb(x, 1.8, 0.35)[:n], 0.5), 0.005, 0.4)

def swell(d=3.5, f=110):
    t = T(d); u = t / d
    env = np.sin(np.pi * u * 0.5 + 0.0) ** 2 if False else (np.sin(np.pi * u) ** 2)
    x = sum(np.sin(2 * np.pi * f * m * t + p) * a for m, a, p in [(1, 1, 0), (1.005, 0.7, 1), (2, 0.4, 2), (3.01, 0.2, 3)])
    x = lp(x, 1200) * env
    return fade(norm(reverb(x, 2.0, 0.4)[:len(t)], 0.6), 0.05, 0.3)

def radio_static(d=3.0):
    n = int(d * SR); t = T(d)
    x = bp(noise(d), 900, 4500) * (0.25 + 0.75 * (RNG.random(n) > 0.985).astype(float))
    crackle = np.zeros(n)
    for _ in range(int(d * 40)):
        s = RNG.integers(0, n - 400); crackle[s:s + 300] += RNG.normal(0, 1, 300) * np.exp(-np.arange(300) / 40)
    x = x * 0.6 + hp(crackle, 1500) * 0.5
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t)
    return fade(norm(x, 0.45), 0.05, 0.4)

def radar_ping(d=2.0):
    t = T(d); f = 1400 * np.exp(-t * 1.6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 2.8)
    return fade(norm(reverb(x, 2.0, 0.35)[:len(t)], 0.55), 0.004, 0.3)

def strike(d=0.45):
    x = sweep_noise(d, 6000, 900, 1.0) * np.exp(-T(d) * 7)
    return fade(norm(x, 0.7), 0.002, 0.1)

def pluck(f=196, d=2.0):
    n = int(SR / f); buf = RNG.uniform(-1, 1, n); out = np.zeros(int(d * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]; buf[i % n] = 0.4985 * (buf[i % n] + buf[(i + 1) % n])
    return fade(norm(reverb(lp(out, 3000), 1.5, 0.25)[:len(out)], 0.55), 0.002, 0.3)

def drop(d=1.8):
    t = T(d); f = 900 * np.exp(-t * 2.3) + 70
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.4)
    return fade(norm(lp(x, 2500), 0.6), 0.005, 0.35)

def lens_hum(d=5.0, f=55):
    t = T(d); u = t / d
    x = sum(np.sin(2 * np.pi * f * m * t) * a for m, a in [(1, 1), (1.011, 0.8), (2.0, 0.5), (3.0, 0.2)])
    x *= (0.5 + 0.5 * np.sin(np.pi * u)) * (0.85 + 0.15 * np.sin(2 * np.pi * 3.1 * t))
    return fade(norm(reverb(lp(x, 700), 2.5, 0.35)[:len(t)], 0.7), 0.3, 0.8)

def well(d=3.0):
    t = T(d); u = t / d
    f = 420 * (0.18 ** u)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)) * np.sin(np.pi * np.minimum(1, u * 1.1)) ** 0.7
    x += 0.4 * np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR)
    return fade(norm(reverb(lp(x, 1500), 2.2, 0.4)[:len(t)], 0.6), 0.05, 0.5)

def thud(d=0.6):
    t = T(d); x = np.sin(2 * np.pi * np.cumsum(60 + 80 * np.exp(-t * 25)) / SR) * np.exp(-t * 9)
    return fade(norm(x, 0.8), 0.002, 0.12)

def glass(f=1320, d=2.2):
    return ping(f, d, soft=True)

SFX = {
    'whoosh_up': lambda: whoosh(1.3, True), 'whoosh_down': lambda: whoosh(1.3, False), 'whoosh_long': lambda: whoosh(2.4, True),
    'riser_short': lambda: riser(3.0), 'riser_long': lambda: riser(6.0),
    'boom': boom, 'thud': thud, 'tick': tick, 'tick_hi': lambda: tick(3200), 'tick_lo': lambda: tick(1500),
    'ping_a': lambda: ping(880), 'ping_e': lambda: ping(659), 'ping_low': lambda: ping(440, 2.0), 'ping_hi': lambda: ping(1320, 1.4),
    'glass': glass, 'blips': blips, 'sparkle': sparkle, 'swell': swell, 'swell_low': lambda: swell(4.5, 73),
    'radio_static': radio_static, 'radar_ping': radar_ping, 'strike': strike,
    'pluck_a': lambda: pluck(196), 'pluck_e': lambda: pluck(247), 'drop': drop, 'lens_hum': lens_hum, 'well': well,
}

# ------------------------------------------------------------------ MUSIC
MODES = {'lydian': [0, 2, 4, 6, 7, 9, 11], 'aeolian': [0, 2, 3, 5, 7, 8, 10], 'dorian': [0, 2, 3, 5, 7, 9, 10],
         'ionian': [0, 2, 4, 5, 7, 9, 11], 'phrygian': [0, 1, 3, 5, 7, 8, 10], 'mixo': [0, 2, 4, 5, 7, 9, 10]}

def note_hz(root_hz, semis): return root_hz * 2 ** (semis / 12)

def pad_voice(f, d, bright=1200, detune=0.004, vib=0.0):
    t = T(d); x = np.zeros_like(t)
    for dt in (-detune, 0, detune):
        ph = 2 * np.pi * f * (1 + dt) * t + RNG.uniform(0, 6)
        x += (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.5 + np.sin(ph) * 0.5
    x = lp(x, bright)
    a = min(d * 0.4, 2.2); r = min(d * 0.45, 2.8)
    e = np.minimum(1, t / a) * np.minimum(1, (d - t) / r)
    return x * np.clip(e, 0, 1) ** 1.5

def bell_note(f, d=3.0, amp=1.0):
    t = T(d); x = np.zeros_like(t)
    for m, a, dec in [(1, 1, 1.4), (2.0, 0.35, 2.2), (3.0, 0.2, 3.0), (4.2, 0.1, 4.5)]:
        x += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * dec)
    return x * np.minimum(1, t / 0.008) * amp

def make_track(name, root=146.83, mode='lydian', prog=(0, 3, 4, 0), bars=8, bar_len=6.0, pad_bright=1100,
               pulse=0.0, bell_density=0.0, sub=0.5, arp=0.0, wet=0.4, level=0.9, seed=0, octave_up=0.0):
    rng = np.random.default_rng(seed)
    scale = MODES[mode]
    total = bars * bar_len + 4.0
    out = np.zeros(int(total * SR))
    for b in range(bars):
        deg = prog[b % len(prog)]
        chord = [scale[(deg + k) % 7] + 12 * ((deg + k) // 7) for k in (0, 2, 4, 6 if b % 2 else 7)]
        start = int(b * bar_len * SR)
        for i, semis in enumerate(chord):
            f = note_hz(root, semis)
            v = pad_voice(f, bar_len + 3.5, pad_bright * (1.0 + 0.2 * i), 0.004, 0)
            out[start:start + len(v)] += v[:len(out) - start] * (0.5 if i else 0.7)
            if octave_up:
                v2 = pad_voice(f * 2, bar_len + 3.5, pad_bright * 1.4, 0.003, 0)
                out[start:start + len(v2)] += v2[:len(out) - start] * octave_up * 0.4
        # sub drone on chord root
        fs_ = note_hz(root / 2, scale[deg % 7])
        sd = pad_voice(fs_, bar_len + 2.0, 220, 0.002, 0)
        out[start:start + len(sd)] += sd[:len(out) - start] * sub
        # pulse
        if pulse > 0:
            beat = bar_len / 4
            for k in range(8):
                s = start + int(k * beat / 2 * SR)
                th = thud(0.5) * pulse * (1.0 if k % 2 == 0 else 0.45)
                out[s:s + len(th)] += th[:max(0, len(out) - s)] * 0.6
        # bells
        if bell_density > 0:
            nb = rng.poisson(bell_density * bar_len)
            for _ in range(nb):
                s = start + int(rng.uniform(0, bar_len) * SR)
                semis = scale[rng.choice([0, 2, 4, 5])] + 12 * rng.choice([1, 2])
                bn = bell_note(note_hz(root, semis), 3.2, rng.uniform(0.25, 0.55))
                out[s:s + len(bn)] += bn[:max(0, len(out) - s)] * 0.35
        # arpeggio (soft plucks)
        if arp > 0:
            step = bar_len / 8
            for k in range(8):
                s = start + int(k * step * SR)
                semis = chord[k % len(chord)] + 12
                bn = bell_note(note_hz(root, semis), 1.6, arp)
                out[s:s + len(bn)] += bn[:max(0, len(out) - s)] * 0.3
    out = reverb(out, 4.0, wet, 6000)[:len(out)]
    # seamless loop: fold the tail onto the head
    tail = int(4.0 * SR); L = len(out) - tail
    loop = out[:L].copy(); xf = np.linspace(0, 1, tail)
    loop[:tail] = loop[:tail] * xf + out[L:L + tail] * (1 - xf)
    loop = loop / (np.sqrt(np.mean(loop ** 2)) + 1e-9) * 0.11 * level  # about -19 dBFS RMS
    loop = np.tanh(loop * 1.4) / 1.4
    return stereo(loop, 0.0007)

TRACKS = {
    # opening: bold and audible, lydian wonder with a gentle pulse and bells
    'awe_open':   dict(root=146.83, mode='lydian', prog=(0, 4, 3, 5), bars=8, bar_len=5.5, pad_bright=1500, pulse=0.55, bell_density=0.5, sub=0.8, arp=0.5, wet=0.45, level=1.25, octave_up=0.6, seed=1),
    'dark_arrival': dict(root=110.0, mode='aeolian', prog=(0, 5, 3, 4), bars=8, bar_len=6.5, pad_bright=800, pulse=0.0, bell_density=0.15, sub=1.2, arp=0.0, wet=0.55, level=1.0, seed=2),
    'scale_wonder': dict(root=164.81, mode='dorian', prog=(0, 3, 5, 4), bars=8, bar_len=6.0, pad_bright=1100, pulse=0.2, bell_density=0.4, sub=0.7, arp=0.3, wet=0.5, level=1.0, octave_up=0.4, seed=3),
    'question':   dict(root=130.81, mode='phrygian', prog=(0, 1, 0, 5), bars=8, bar_len=6.0, pad_bright=700, pulse=0.0, bell_density=0.1, sub=1.0, arp=0.0, wet=0.6, level=0.95, seed=4),
    'discovery':  dict(root=196.0, mode='ionian', prog=(0, 5, 3, 4), bars=8, bar_len=5.0, pad_bright=1300, pulse=0.0, bell_density=0.55, sub=0.5, arp=0.55, wet=0.45, level=0.95, seed=5),
    'cosmic_time': dict(root=123.47, mode='lydian', prog=(0, 1, 4, 0), bars=8, bar_len=7.0, pad_bright=1000, pulse=0.0, bell_density=0.3, sub=0.9, arp=0.2, wet=0.6, level=1.0, octave_up=0.5, seed=6),
    'quasar_power': dict(root=98.0, mode='mixo', prog=(0, 6, 3, 4), bars=8, bar_len=5.5, pad_bright=1800, pulse=0.65, bell_density=0.2, sub=1.4, arp=0.25, wet=0.45, level=1.2, octave_up=0.3, seed=7),
    'curious':    dict(root=174.61, mode='dorian', prog=(0, 4, 0, 3), bars=8, bar_len=5.0, pad_bright=1000, pulse=0.1, bell_density=0.7, sub=0.5, arp=0.6, wet=0.45, level=0.9, seed=8),
    'unknown':    dict(root=92.5, mode='phrygian', prog=(0, 4, 5, 0), bars=8, bar_len=6.5, pad_bright=650, pulse=0.0, bell_density=0.08, sub=1.2, arp=0.0, wet=0.65, level=0.95, seed=9),
    'clarity':    dict(root=155.56, mode='ionian', prog=(0, 3, 4, 0), bars=8, bar_len=6.0, pad_bright=1200, pulse=0.12, bell_density=0.35, sub=0.6, arp=0.35, wet=0.5, level=0.95, octave_up=0.4, seed=10),
    'resolve':    dict(root=130.81, mode='lydian', prog=(0, 3, 0, 4), bars=8, bar_len=7.0, pad_bright=1000, pulse=0.0, bell_density=0.3, sub=0.8, arp=0.2, wet=0.6, level=0.95, octave_up=0.5, seed=11),
}

def main(out_dir, only=None):
    for name, fn in SFX.items():
        if only and name not in only: continue
        save(os.path.join(out_dir, 'sfx', name + '.wav'), fn())
    for name, kw in TRACKS.items():
        if only and name not in only: continue
        save(os.path.join(out_dir, 'music', name + '.wav'), make_track(name, **kw))
    print('audio written to', out_dir)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:] or None)

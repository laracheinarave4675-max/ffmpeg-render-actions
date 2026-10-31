"""SFX cues and music plan for the string theory documentary (scene ids v01..v114)."""
import os
KIND_CUES = {
 'zoom': [(0.05, 'whoosh_down', .20), (0.55, 'ping_a', .14)],
 'point': [(0.08, 'ping_low', .20), (0.30, 'sparkle', .14)],
 'web': [(0.05, 'whoosh_up', .15), (0.55, 'ping_e', .16), (0.80, 'ping_hi', .14)],
 'ladder': [(0.06, 'blips', .15), (0.40, 'ping_a', .16), (0.75, 'ping_hi', .15)],
 'sing': [(0.05, 'lens_hum', .26), (0.45, 'ping_low', .18)],
 'cards': [(0.04, 'whoosh_up', .14), (0.20, 'ping_e', .13)],
 'dotloop': [(0.10, 'swell', .22), (0.55, 'sparkle', .20)],
 'two': [(0.10, 'pluck_a', .22), (0.40, 'pluck_e', .22), (0.70, 'ping_hi', .14)],
 'gap': [(0.08, 'ping_low', .18), (0.45, 'whoosh_up', .14), (0.60, 'ping_low', .18)],
 'pillars': [(0.05, 'ping_a', .16), (0.30, 'ping_e', .16)],
 'qm': [(0.05, 'sparkle', .16)],
 'forces': [(0.08, 'pluck_a', .18), (0.30, 'pluck_e', .18), (0.52, 'ping_hi', .16)],
 'gr': [(0.05, 'well', .30), (0.50, 'ping_low', .16)],
 'waves': [(0.05, 'swell_low', .26), (0.50, 'boom', .26)],
 'ratio': [(0.10, 'whoosh_up', .18), (0.45, 'ping_low', .18), (0.62, 'ping_hi', .14)],
 'exchange': [(0.15, 'whoosh_up', .16), (0.45, 'ping_a', .16)],
 'blowup': [(0.10, 'riser_short', .24), (0.85, 'boom', .30)],
 'renorm': [(0.10, 'ping_e', .16), (0.50, 'drop', .22), (0.85, 'boom', .26)],
 'vertex': [(0.10, 'whoosh_up', .14), (0.55, 'strike', .26)],
 'well': [(0.05, 'well', .30), (0.65, 'ping_low', .18)],
 'others': [(0.15, 'ping_a', .15), (0.35, 'ping_e', .15), (0.55, 'ping_hi', .15)],
 'timeline': [(0.05, 'boom', .30), (0.25, 'ping_a', .14)],
 'amp': [(0.10, 'whoosh_up', .15), (0.60, 'ping_e', .15)],
 'morph': [(0.20, 'swell', .24), (0.60, 'sparkle', .20)],
 'quad': [(0.10, 'ping_low', .18), (0.45, 'ping_hi', .15)],
 'dotstring': [(0.15, 'swell', .22), (0.50, 'sparkle', .18)],
 'ladder_string': [(0.35, 'ping_a', .15)],
 'vib': [(0.08, 'pluck_a', .22), (0.28, 'pluck_e', .22), (0.48, 'pluck_a', .20), (0.68, 'pluck_e', .20)],
 'guitar': [(0.10, 'pluck_a', .24), (0.45, 'ping_a', .16)],
 'tension': [(0.15, 'swell_low', .24), (0.55, 'ping_low', .18)],
 'spectrum': [(0.08, 'pluck_a', .18), (0.30, 'pluck_e', .16), (0.55, 'ping_hi', .15)],
 'brane': [(0.12, 'whoosh_up', .15), (0.50, 'pluck_e', .18)],
 'eq': [(0.12, 'swell', .22), (0.40, 'ping_a', .16)],
 'worldsheet': [(0.10, 'whoosh_up', .15), (0.55, 'swell', .22)],
 'dims': [(0.06, 'ping_a', .15), (0.30, 'ping_e', .15), (0.55, 'ping_hi', .15)],
 'cable': [(0.10, 'whoosh_up', .14), (0.50, 'ping_e', .15)],
 'ant': [(0.15, 'blips', .14), (0.55, 'ping_hi', .16)],
 'compact': [(0.15, 'sparkle', .18), (0.50, 'ping_a', .16)],
 'cy': [(0.05, 'swell', .24), (0.40, 'sparkle', .16)],
 'trumpet': [(0.20, 'pluck_a', .20), (0.55, 'pluck_e', .20)],
 'family': [(0.15, 'ping_a', .15), (0.35, 'ping_e', .15), (0.55, 'ping_hi', .15)],
 'forcedev': [(0.10, 'whoosh_up', .14), (0.40, 'ping_low', .18)],
 'lab': [(0.15, 'blips', .14), (0.55, 'ping_a', .16)],
 'lhcring': [(0.10, 'lens_hum', .22), (0.50, 'ping_low', .18)],
 'search': [(0.10, 'ping_a', .14), (0.40, 'ping_low', .16), (0.70, 'ping_hi', .14)],
 'sparticles': [(0.10, 'ping_e', .14), (0.40, 'ping_e', .14), (0.70, 'drop', .20)],
 'sky': [(0.05, 'radio_static', .14), (0.75, 'ping_low', .18)],
 'shapes': [(0.05, 'sparkle', .20), (0.60, 'ping_hi', .14)],
 'land': [(0.05, 'swell', .22), (0.45, 'sparkle', .20)],
 'cols2': [(0.10, 'ping_low', .16), (0.45, 'ping_e', .16)],
 'checks': [(0.15, 'ping_a', .16), (0.45, 'ping_hi', .16)],
 'balance': [(0.20, 'ping_e', .15), (0.55, 'ping_low', .16)],
 'bh': [(0.05, 'lens_hum', .26), (0.45, 'ping_low', .16)],
 'entropy': [(0.10, 'sparkle', .18), (0.55, 'ping_a', .16)],
 'micro': [(0.05, 'blips', .15), (0.50, 'swell_low', .22)],
 'count': [(0.10, 'whoosh_up', .15), (0.45, 'ping_a', .16), (0.70, 'boom', .26)],
 'region': [(0.10, 'ping_a', .15), (0.55, 'ping_hi', .15)],
 'ads': [(0.10, 'swell', .22), (0.45, 'ping_e', .16)],
 'dict': [(0.10, 'ping_a', .15), (0.25, 'ping_e', .15), (0.50, 'ping_hi', .16)],
 'holo': [(0.10, 'sparkle', .18), (0.55, 'ping_low', .16)],
 'dsads': [(0.08, 'ping_a', .14), (0.30, 'whoosh_up', .14), (0.60, 'drop', .20)],
 'emerge': [(0.20, 'swell', .22), (0.60, 'sparkle', .20)],
 'tiers': [(0.10, 'ping_a', .15), (0.32, 'ping_e', .15), (0.54, 'ping_hi', .15)],
 'return': [(0.05, 'whoosh_up', .20), (0.60, 'ping_a', .14)],
 'split': [(0.10, 'ping_low', .16), (0.45, 'ping_hi', .16)],
 'matters': [(0.10, 'ping_a', .15), (0.40, 'ping_e', .15), (0.65, 'ping_hi', .15)],
 'nowhat': [(0.10, 'ping_a', .15), (0.45, 'ping_e', .15)],
 'windows': [(0.10, 'ping_a', .15), (0.32, 'ping_e', .15), (0.54, 'ping_hi', .15)],
 'final': [(0.05, 'swell', .22), (0.30, 'ping_a', .15), (0.55, 'ping_hi', .14)],
}
OVERRIDE = {
 'v01_open': [(0.0, 'riser_short', .32), (0.0, 'swell', .22)],
 'v04_stops': [(0.30, 'boom', .45), (0.35, 'drop', .22)],
 'v06_point': [(0.12, 'ping_hi', .20)],
 'v10_question': [(0.0, 'swell', .26), (0.55, 'sparkle', .22)],
 'v12_proposal': [(0.10, 'boom', .50), (0.14, 'sparkle', .16)],
 'v14_noseen': [(0.50, 'thud', .30)],
 'v22_ligo': [(0.0, 'swell_low', .26), (0.60, 'ping_low', .18)],
 'v23_eht': [(0.10, 'ping_a', .16)],
 'v36_strings': [(0.20, 'swell', .24), (0.60, 'sparkle', .22), (0.70, 'ping_hi', .18)],
 'v53_finds': [(0.55, 'boom', .40), (0.60, 'sparkle', .18)],
 'v56_careful': [(0.45, 'strike', .26)],
 'v57_nodetect': [(0.30, 'thud', .30)],
 'v59_price': [(0.10, 'swell_low', .26), (0.15, 'ping_low', .18)],
 'v68_cy': [(0.0, 'riser_short', .24), (0.10, 'swell', .22)],
 'v83_landscape': [(0.0, 'swell', .22), (0.50, 'boom', .32)],
 'v94_sv': [(0.70, 'boom', .40)],
 'v97_ads': [(0.0, 'riser_short', .24), (0.10, 'swell', .22)],
 'v108_return': [(0.05, 'whoosh_up', .22), (0.70, 'ping_a', .16)],
 'v113_dot_note': [(0.0, 'swell', .26), (0.30, 'ping_a', .18), (0.55, 'pluck_a', .22)],
 'v114_ask': [(0.0, 'swell_low', .26), (0.50, 'ping_low', .18)],
}
TICKS = [('v07_lhc', 0.1, 0.8, 0.3, 'tick', .06), ('v24_triumph', 0.1, 0.6, 0.25, 'tick_lo', .05)]
MUSIC = [  # (first_scene, last_scene, track, gain)
 ('v01_open', 'v10_question', 'awe_open', 1.00),
 ('v11_notes', 'v16_lives', 'clarity', 0.60),
 ('v17_pillars', 'v24_triumph', 'scale_wonder', 0.60),
 ('v25_both', 'v33_others', 'question', 0.62),
 ('v34_notbegin', 'v39_1974', 'discovery', 0.58),
 ('v40_proposal', 'v45_species', 'curious', 0.56),
 ('v46_guitar', 'v58_possible', 'cosmic_time', 0.58),
 ('v59_price', 'v70_family', 'unknown', 0.58),
 ('v71_test', 'v83_landscape', 'dark_arrival', 0.60),
 ('v84_one', 'v90_notinter', 'clarity', 0.55),
 ('v91_bh', 'v95_cousins', 'discovery', 0.58),
 ('v96_holo', 'v101_emerge', 'cosmic_time', 0.60),
 ('v102_suppose', 'v107_horizon', 'scale_wonder', 0.58),
 ('v108_return', 'v114_ask', 'resolve', 0.66),
]
def build(order, start, dur, kinds, prefix='https://asset.local'):
    sfx = []
    def add(at, name, vol): sfx.append({'src': f'{prefix}/sfx/{name}.wav', 'at': round(at, 3), 'volume': vol, 'len': 3.0, 'fade': 0.5})
    for sid in order:
        for frac, name, vol in OVERRIDE.get(sid, KIND_CUES.get(kinds[sid], [])):
            add(start[sid] + dur[sid] * frac, name, vol)
    for sid, a, b, step, name, vol in TICKS:
        if sid not in start: continue
        t = start[sid] + dur[sid] * a
        while t < start[sid] + dur[sid] * b:
            add(t, name, vol); t += step
    sfx.sort(key=lambda s: s['at'])
    music = []
    oset = set(order)
    for first, last, track, gain in MUSIC:
        ids = [s for s in order if s in oset]
        # clip the music segment to the scenes of this part
        a_i = order.index(first) if first in oset else None; b_i = order.index(last) if last in oset else None
        allids = [m[0] for m in MUSIC]
        if a_i is None and b_i is None:
            # segment may fully contain this part
            continue
        fa = first if a_i is not None else order[0]; la = last if b_i is not None else order[-1]
        music.append({'src': f'{prefix}/music/{track}.wav', 'from': round(start[fa], 3), 'to': round(start[la] + dur[la], 3), 'gain': gain})
    return {'sfx': sfx, 'music': music}

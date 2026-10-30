"""Build render_video_github clips for one narration file of the string theory film.
Usage: python3 build_payload_st.py <A|B|C> [out.json]
"""
import os, sys, json
os.environ.setdefault('SCENE_OUT', '/tmp/scene_out')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stscenes as S, stcues
part = sys.argv[1]
order = [k for k, *_ in S.SEQV if S.FILE_OF[k] == part]
narr = S.FILE_DUR[part]
last = (part == 'C')
tail = 3.5 if last else 0.6
f = (narr + tail) / narr
dur = {k: S.DURV[k] * f for k in order}
start = {}; t = 0.0
for k in order: start[k] = t; t += dur[k]
kinds = {k: S.KP[k][0] for k in order}
fx = stcues.build(order, start, dur, kinds)
REAL = {'v22_ligo': 'https://svs.gsfc.nasa.gov/vis/a010000/a012200/a012216/BH_merger_fixed_camera_close_H264_YouTube_720p.webm',
        'v23_eht': 'https://svs.gsfc.nasa.gov/vis/a000000/a004800/a004807/M87_EHT_Multiwavelength_Zoom_1080p30.mp4'}
OV = 0.8
clips = []
for i, k in enumerate(order):
    d = dur[k] + (OV if i < len(order) - 1 else 0)
    if k in REAL: c = {'src': REAL[k], 'type': 'video', 'duration': round(d, 2)}
    else: c = {'src': 'https://scene.local/%s?d=%.2f' % (k, d), 'type': 'video', 'duration': round(d, 2)}
    if i == 0: c['direction'] = {'fx': {'music': fx['music'], 'sfx': fx['sfx']}}
    if i == len(order) - 1 and last: c['end_fade'] = True
    clips.append(c)
out = json.dumps(clips, ensure_ascii=False, separators=(',', ':'))
if len(sys.argv) > 2: open(sys.argv[2], 'w').write(out)
print(len(out), 'chars,', len(clips), 'clips,', len(fx['sfx']), 'sfx,', len(fx['music']), 'music', 'total', round(sum(dur.values()), 1), file=sys.stderr)

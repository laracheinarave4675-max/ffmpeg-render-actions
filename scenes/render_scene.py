"""Render ONE original scene to an mp4 (no review captions).
Usage: python3 render_scene.py <scene_id> <duration_seconds> <out.mp4>
Only the modules a scene needs are imported (s* -> scenes, t* -> scenes2, u* -> scenes3, ...).
"""
import os, sys, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MODS = {'s': ('scenes', 'FUNCS', 'START'), 't': ('scenes2', 'FUNCS2', 'START2'), 'u': ('scenes3', 'FUNCS3', 'START3'), 'v': ('stscenes', 'FUNCSV', 'STARTV'), 'w': ('shscenes', 'FUNCSW', 'STARTW')}
def lookup(sid):
    mod, f, st = MODS[sid[0]]
    m = importlib.import_module(mod)
    return getattr(m, f)[sid], getattr(m, st)[sid]
if __name__ == '__main__':
    sid, dur, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    if sid == 'wpatch':  # one-time maintenance hook: patch render.js, then emit a 1s dummy clip
        import subprocess
        subprocess.check_call([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apply_patch.py')])
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=64x64:d=1:r=24', '-pix_fmt', 'yuv420p', out])
        sys.exit(0)
    if sid == 'wprobe':  # one-time maintenance hook: probe rendered files on Drive, then emit a 1s dummy clip
        import subprocess
        subprocess.check_call([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'probe.py')])
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=64x64:d=1:r=24', '-pix_fmt', 'yuv420p', out])
        sys.exit(0)
    if sid[0] not in MODS:
        sys.exit('unknown scene ' + sid)
    if sid[0] == 'w':  # vertical 9:16 short scenes are drawn at 720x1280
        os.environ.setdefault('SCENE_W', '720'); os.environ.setdefault('SCENE_H', '1280')
    out_dir = os.path.dirname(os.path.abspath(out)) or '.'
    os.environ['SCENE_OUT'] = out_dir
    fn, start = lookup(sid)
    import engine
    engine.OUT = out_dir
    name = os.path.splitext(os.path.basename(out))[0]
    engine.render_scene(name, dur, fn, start, caption=None, review=False)

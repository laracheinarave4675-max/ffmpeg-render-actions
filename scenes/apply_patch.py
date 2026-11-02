"""One-time patch of render.js: vertical output size and narration volume. Safe to run twice."""
import os, subprocess, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(root, 'render.js')
s = open(p, encoding='utf-8').read()
if 'SHORT_PATCH' in s:
    print('patch: already patched'); sys.exit(0)
a = "  const RES = '1920:1080';"
b = "  // SHORT_PATCH: output size from clips[0].direction.video {width,height}\n  const _dv = (clips[0] && clips[0].direction && clips[0].direction.video) || {};\n  const RES = (_dv.width && _dv.height) ? (_dv.width + ':' + _dv.height) : '1920:1080';"
assert s.count(a) == 1, 'RES line not found'
s = s.replace(a, b)
a2 = "AFc + ',apad=whole_dur='"
b2 = "AFc + (o.narrVol && o.narrVol !== 1 ? ',volume=' + o.narrVol + ',alimiter=limit=0.97' : '') + ',apad=whole_dur='"
assert s.count(a2) == 1, 'narration chain not found'
s = s.replace(a2, b2)
a3 = "      outPath: finalPath, tail: endTail,"
b3 = "      narrVol: ((clips[0] && clips[0].direction && clips[0].direction.audio && clips[0].direction.audio.narration_volume) || 1),\n      outPath: finalPath, tail: endTail,"
assert s.count(a3) == 1, 'mixWithEnding call not found'
s = s.replace(a3, b3)
open(p, 'w', encoding='utf-8').write(s)
subprocess.check_call(['node', '--check', p])
os.chdir(root)
subprocess.check_call('git config user.name render-bot && git config user.email render-bot@users.noreply.github.com', shell=True)
subprocess.check_call(['git', 'add', 'render.js'])
subprocess.check_call(['git', 'commit', '-m', 'Vertical output size and narration volume'])
try: subprocess.check_call(['git', 'pull', '--rebase', 'origin', 'main'])
except Exception as e: print('patch: pull failed', e)
subprocess.check_call(['git', 'push', 'origin', 'HEAD:main'])
print('patch: pushed')

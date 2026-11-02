"""Patch 2 of render.js: the router forwards only clips[0].direction.fx, so read video size, narration volume and duck settings from there too."""
import os, subprocess, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(root, 'render.js')
s = open(p, encoding='utf-8').read()
if 'SHORT_PATCH2' in s:
    print('patch2: already patched'); sys.exit(0)
a = "const _dv = (clips[0] && clips[0].direction && clips[0].direction.video) || {};"
b = "const _dv = (clips[0] && clips[0].direction && (clips[0].direction.video || (clips[0].direction.fx && clips[0].direction.fx.video))) || {}; // SHORT_PATCH2"
assert s.count(a) == 1, 'dv line not found'
s = s.replace(a, b)
a2 = "narrVol: ((clips[0] && clips[0].direction && clips[0].direction.audio && clips[0].direction.audio.narration_volume) || 1),"
b2 = "narrVol: ((clips[0] && clips[0].direction && ((clips[0].direction.audio && clips[0].direction.audio.narration_volume) || (clips[0].direction.fx && clips[0].direction.fx.narration_volume))) || 1),"
assert s.count(a2) == 1, 'narrVol line not found'
s = s.replace(a2, b2)
a3 = "const duckCfg = payload.music_duck || (function () {"
b3 = "const duckCfg = payload.music_duck || ((clips[0] && clips[0].direction && clips[0].direction.fx && clips[0].direction.fx.music_duck) || null) || (function () {"
assert s.count(a3) == 1, 'duck line not found'
s = s.replace(a3, b3)
a4 = "  const kenBurns = payload.ken_burns !== false;"
b4 = "  console.log('Output size ' + RES + ', music duck ' + (duckCfg ? 'on' : 'off'));\n  const kenBurns = payload.ken_burns !== false;"
assert s.count(a4) == 1, 'kenBurns line not found'
s = s.replace(a4, b4)
open(p, 'w', encoding='utf-8').write(s)
subprocess.check_call(['node', '--check', p])
os.chdir(root)
subprocess.check_call('git config user.name render-bot && git config user.email render-bot@users.noreply.github.com', shell=True)
subprocess.check_call(['git', 'add', 'render.js'])
subprocess.check_call(['git', 'commit', '-m', 'Read video size, narration volume and duck from direction.fx'])
try: subprocess.check_call(['git', 'pull', '--rebase', 'origin', 'main'])
except Exception as e: print('patch2: pull failed', e)
subprocess.check_call(['git', 'push', 'origin', 'HEAD:main'])
print('patch2: pushed')

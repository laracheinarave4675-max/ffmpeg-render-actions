"""Probe the rendered Short files on Drive and push ffprobe results and sample frames into scenes/ for inspection."""
import os, json, base64, subprocess, urllib.request, urllib.parse
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
creds = json.loads(base64.b64decode(os.environ['GDRIVE_OAUTH_B64']))
body = urllib.parse.urlencode({'client_id': creds['client_id'], 'client_secret': creds['client_secret'], 'refresh_token': creds['refresh_token'], 'grant_type': 'refresh_token'}).encode()
tok = json.load(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data=body)))['access_token']
out = []
for name, fid in (('v2', '1lUsZ4-ck0uXxsi2uGuy9ojwmQnHi3ife'), ('v1', '1m7yfdqAiia8CQr1d_hYP52MucPiKwnvS')):
    req = urllib.request.Request('https://www.googleapis.com/drive/v3/files/%s?alt=media' % fid, headers={'Authorization': 'Bearer ' + tok})
    path = '/tmp/probe_%s.mp4' % name
    with urllib.request.urlopen(req) as r, open(path, 'wb') as f:
        f.write(r.read())
    pr = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,sample_aspect_ratio,display_aspect_ratio,duration:stream_side_data=rotation', '-of', 'json', path], capture_output=True, text=True).stdout
    vd = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'volumedetect', '-vn', '-f', 'null', '-'], capture_output=True, text=True).stderr
    vd = [l.split(']')[-1].strip() for l in vd.split('\n') if 'mean_volume' in l or 'max_volume' in l]
    out.append(name + ': ' + ' '.join(pr.split()) + ' | ' + ' ; '.join(vd))
    if name == 'v2':
        for t in (2, 20, 45, 100):
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(t), '-i', path, '-frames:v', '1', '-vf', 'scale=360:-2', os.path.join(root, 'scenes', 'probe_f%d.jpg' % t)])
open(os.path.join(root, 'scenes', 'probe_result.txt'), 'w').write('\n'.join(out) + '\n')
os.chdir(root)
subprocess.check_call('git config user.name render-bot && git config user.email render-bot@users.noreply.github.com', shell=True)
subprocess.check_call('git add scenes', shell=True)
subprocess.check_call(['git', 'commit', '-m', 'Probe result'])
try: subprocess.check_call(['git', 'pull', '--rebase', 'origin', 'main'])
except Exception as e: print('probe: pull failed', e)
subprocess.check_call(['git', 'push', 'origin', 'HEAD:main'])
print('probe: pushed')

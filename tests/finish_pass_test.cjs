'use strict';
// Real ffmpeg test: synthetic 3 s clip -> finish pass -> checks streams, size, loudness, and the no-op case.
const { spawnSync } = require('child_process');
const fs = require('fs'); const os = require('os'); const path = require('path');
const { applyFinishPass, sanitizeGraph } = require('../director/finish_pass.cjs');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'fp-'));
const src = path.join(dir, 'in.mp4'), out = path.join(dir, 'out.mp4');
function sh(cmd, args) { const r = spawnSync(cmd, args, { encoding: 'utf8' }); if (r.status !== 0) throw new Error(cmd + ' failed: ' + (r.stderr || '').slice(0, 400)); return r; }
sh('ffmpeg', ['-y', '-f', 'lavfi', '-i', 'testsrc2=size=640x360:rate=24:duration=3', '-f', 'lavfi', '-i', 'sine=frequency=220:sample_rate=44100:duration=3',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', src]);
let ok = true; const check = (name, cond) => { console.log((cond ? 'PASS ' : 'FAIL ') + name); if (!cond) ok = false; };
check('no-op when nothing requested', applyFinishPass(src, out, {}).applied === false);
const r = applyFinishPass(src, out, { finish: { preset: 'cosmic' }, master_audio: true });
check('applied visual+audio', r.applied && r.visual && r.audio && fs.existsSync(out));
const pr = sh('ffprobe', ['-v', 'error', '-show_entries', 'stream=codec_type,width,height', '-of', 'csv=p=0', out]).stdout;
check('has video 640x360 and audio', /video,640,360/.test(pr) && /audio/.test(pr));
const ld = sh('ffmpeg', ['-hide_banner', '-i', out, '-af', 'ebur128', '-f', 'null', '-']).stderr;
const m = /I:\s+(-?\d+(\.\d+)?) LUFS/g; let last, x; while ((x = m.exec(ld))) last = parseFloat(x[1]);
check('loudness near -15 LUFS (got ' + last + ')', last > -17.5 && last < -12.5);
const sg = sanitizeGraph(require('../director/finish.cjs').buildFilterGraph({}));
check('scale2ref removed from graph', sg.indexOf('scale2ref') === -1 && sg.indexOf('split=2') > -1);
const odd = path.join(dir, 'odd.mp4'), oddOut = path.join(dir, 'odd_out.mp4');
sh('ffmpeg', ['-y', '-f', 'lavfi', '-i', 'testsrc2=size=646x358:rate=24:duration=2', '-f', 'lavfi', '-i', 'sine=frequency=220:sample_rate=44100:duration=2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', odd]);
check('odd-size input (646x358) works', applyFinishPass(odd, oddOut, { finish: true }).applied && fs.existsSync(oddOut));
let threw = false; try { applyFinishPass(path.join(dir, 'missing.mp4'), out, { master_audio: true }); } catch (e) { threw = true; }
check('throws on missing input', threw);
fs.rmSync(dir, { recursive: true, force: true });
console.log(ok ? 'ALL PASSED' : 'SOME FAILED'); process.exit(ok ? 0 : 1);

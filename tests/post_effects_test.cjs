const fs = require('fs');
const { execFileSync } = require('child_process');
const { applyPostEffects } = require('../director/post_effects.cjs');
const T = '/tmp/fxtest'; fs.rmSync(T, { recursive: true, force: true }); fs.mkdirSync(T, { recursive: true });
const ff = (a) => execFileSync('ffmpeg', ['-y', ...a], { stdio: 'ignore' });
ff(['-f', 'lavfi', '-i', 'color=c=black:s=1280x720:d=6:r=25', '-f', 'lavfi', '-i', 'sine=f=220:d=6', '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', T + '/base.mp4']);
ff(['-f', 'lavfi', '-i', 'sine=f=1200:d=0.5', T + '/hit.mp3']);
const meanVol = (f, ss) => {
  const r = require('child_process').spawnSync('ffmpeg', ['-ss', String(ss), '-t', '0.5', '-i', f, '-af', 'volumedetect', '-f', 'null', '-'], { encoding: 'utf8' });
  return parseFloat(/mean_volume: (-?[\d.]+) dB/.exec(r.stderr)[1]);
};
const bright = (f, t) => {
  const b = execFileSync('ffmpeg', ['-ss', String(t), '-i', f, '-frames:v', '1', '-vf', 'crop=400:120:in_w-420:20,format=gray', '-f', 'rawvideo', '-'], { maxBuffer: 1 << 24 });
  return b.reduce((s, v) => s + v, 0) / b.length;
};
(async () => {
  let fails = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fails++; };
  const none = await applyPostEffects({ finalPath: T + '/base.mp4', workDir: T, downloadFile: async () => {} });
  ok(none === T + '/base.mp4', 'no sfx/badges -> untouched path');
  const out = await applyPostEffects({
    finalPath: T + '/base.mp4', workDir: T,
    sfx: [{ src: T + '/hit.mp3', at: 2.0, volume: 0.8 }],
    badges: [{ kind: 'illustration', from: 1, to: 4 }],
    downloadFile: async (src, dst) => fs.copyFileSync(src, dst),
  });
  const d = parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], { encoding: 'utf8' }));
  ok(Math.abs(d - 6) < 0.25, 'duration kept (' + d.toFixed(2) + 's)');
  const loud = meanVol(out, 2.0), quiet = meanVol(out, 4.5), orig = meanVol(T + '/base.mp4', 2.0);
  ok(loud > orig + 1, 'sfx audible at 2.0s (' + loud + ' dB vs original ' + orig + ' dB)');
  ok(Math.abs(quiet - meanVol(T + '/base.mp4', 4.5)) < 1.5, 'audio unchanged away from sfx');
  const on = bright(out, 2.5), off = bright(out, 5.0);
  ok(on > off + 2, 'badge visible 1-4s, gone after (' + on.toFixed(1) + ' vs ' + off.toFixed(1) + ')');
  process.exit(fails ? 1 : 0);
})();

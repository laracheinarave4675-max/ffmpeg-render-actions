const fs = require('fs');
const { execFileSync, spawnSync } = require('child_process');
const { applyPostEffects } = require('../director/post_effects.cjs');
const T = '/tmp/fxtest'; fs.rmSync(T, { recursive: true, force: true }); fs.mkdirSync(T, { recursive: true });
const ff = (a) => execFileSync('ffmpeg', ['-y', ...a], { stdio: 'ignore' });
ff(['-f', 'lavfi', '-i', 'color=c=black:s=1280x720:d=8:r=25', '-f', 'lavfi', '-i', 'sine=f=220:d=8', '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', T + '/base.mp4']);
ff(['-f', 'lavfi', '-i', 'sine=f=1200:d=6', T + '/long_hit.mp3']);   // 6 s source, must be trimmed
const meanVol = (f, ss, len) => {
  const r = spawnSync('ffmpeg', ['-ss', String(ss), '-t', String(len || 0.4), '-i', f, '-af', 'volumedetect', '-f', 'null', '-'], { encoding: 'utf8' });
  return parseFloat(/mean_volume: (-?[\d.]+) dB/.exec(r.stderr)[1]);
};
const bright = (f, t) => {
  const b = execFileSync('ffmpeg', ['-ss', String(t), '-i', f, '-frames:v', '1', '-vf', 'crop=560:130:in_w-580:20,format=gray', '-f', 'rawvideo', '-'], { maxBuffer: 1 << 24 });
  return b.reduce((s, v) => s + v, 0) / b.length;
};
(async () => {
  let fails = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fails++; };
  const none = await applyPostEffects({ finalPath: T + '/base.mp4', workDir: T, downloadFile: async () => {} });
  ok(none === T + '/base.mp4', 'no sfx/badges -> untouched path');
  const out = await applyPostEffects({
    finalPath: T + '/base.mp4', workDir: T,
    sfx: [{ src: T + '/long_hit.mp3', at: 2.0, volume: 0.8, len: 1.0, fade: 0.3 }],
    badges: [{ kind: 'illustration', from: 1, to: 5 }],
    downloadFile: async (src, dst) => fs.copyFileSync(src, dst),
  });
  const d = parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], { encoding: 'utf8' }));
  ok(Math.abs(d - 8) < 0.25, 'duration kept (' + d.toFixed(2) + 's)');
  const orig = meanVol(T + '/base.mp4', 2.2);
  ok(meanVol(out, 2.2) > orig + 1, 'sfx audible inside its length (2.2s)');
  ok(Math.abs(meanVol(out, 3.6) - meanVol(T + '/base.mp4', 3.6)) < 1.5, 'sfx trimmed: long 6 s source is gone by 3.6s');
  ok(Math.abs(meanVol(out, 6.5) - meanVol(T + '/base.mp4', 6.5)) < 1.5, 'audio unchanged far from sfx');
  const off0 = bright(out, 0.8), mid = bright(out, 1.12), on = bright(out, 3.0), outFade = bright(out, 4.9), off1 = bright(out, 6.0);
  ok(on > off0 + 4, 'badge fully visible at 3.0s (' + on.toFixed(1) + ' vs ' + off0.toFixed(1) + ')');
  ok(off0 < 1 && off1 < 1, 'badge absent before 1s and after 5s');
  ok(mid > off0 && mid < on, 'entry is animated, not a hard cut (mid ' + mid.toFixed(1) + ')');
  ok(outFade < on, 'exit is animated (4.9s dimmer: ' + outFade.toFixed(1) + ')');
  process.exit(fails ? 1 : 0);
})();

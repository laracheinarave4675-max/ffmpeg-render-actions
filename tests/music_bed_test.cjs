const fs = require('fs');
const { execFileSync, spawnSync } = require('child_process');
const { buildMusicBed, normalize } = require('../director/music_bed.cjs');
const T = '/tmp/mbtest'; fs.rmSync(T, { recursive: true, force: true }); fs.mkdirSync(T, { recursive: true });
const ff = (a) => execFileSync('ffmpeg', ['-y', ...a], { stdio: 'ignore' });
ff(['-f', 'lavfi', '-i', 'sine=f=220:d=2', T + '/a.mp3']);    // only 2 s: must loop to fill 0-4 s
ff(['-f', 'lavfi', '-i', 'sine=f=440:d=10', T + '/b.mp3']);
const vol = (f, ss, len) => {
  const r = spawnSync('ffmpeg', ['-ss', String(ss), '-t', String(len || 0.4), '-i', f, '-af', 'volumedetect', '-f', 'null', '-'], { encoding: 'utf8' });
  const m = /mean_volume: (-?[\d.]+) dB/.exec(r.stderr); return m ? parseFloat(m[1]) : -99;
};
(async () => {
  let fails = 0; const ok = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fails++; };
  const n = normalize([{ src: 'x', from: 4, to: 9 }, { src: 'y', from: 0, to: 4 }, { src: 'bad', from: 5, to: 5 }], 2);
  ok(n.length === 2 && n[0].from === 0 && n[0].end === 6 && n[1].end === 9, 'normalize sorts, drops invalid, extends tails by crossfade');
  const dest = T + '/bed.mp3';
  await buildMusicBed({ segments: [{ src: T + '/a.mp3', from: 0, to: 4 }, { src: T + '/b.mp3', from: 4, to: 9, gain: 0.5 }], workDir: T, downloadFile: async (s, d) => fs.copyFileSync(s, d), dest, xf: 1.5 });
  const d = parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', dest], { encoding: 'utf8' }));
  ok(Math.abs(d - 9) < 0.3, 'bed length = last segment end (' + d.toFixed(2) + 's)');
  const v1 = vol(dest, 1.0), v3 = vol(dest, 3.2), vx = vol(dest, 4.2), v6 = vol(dest, 6.0);
  ok(v3 > -40 && v1 > -40, 'short 2 s source loops to fill 0-4 s (' + v1 + ' / ' + v3 + ' dB)');
  ok(Math.abs(vx - v1) < 8, 'crossfade has no gap or spike at 4.2s (' + vx + ' dB vs ' + v1 + ' dB)');
  ok(v6 < v1 - 3 && v6 > -40, 'second segment gain 0.5 is quieter and audible (' + v6 + ' dB)');
  process.exit(fails ? 1 : 0);
})();

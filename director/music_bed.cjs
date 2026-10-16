// Scene-aware music bed: builds ONE music file from per-scene segments with equal-power crossfades.
// Segment: { src, from, to, gain?, fade_in?, fade_out? }  (times are on the FINAL video timeline, seconds)
// Each segment (except the last) is extended by `xf` seconds into the next scene so tails overlap with
// the next segment's fade-in. Short sources loop automatically. Output level stays at unity: the
// existing render.js mix still applies music_volume and ducking on top of this bed.
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const num = (v, d) => (typeof v === 'number' && isFinite(v) ? v : d);
const f3 = (v) => (Math.round(v * 1000) / 1000).toString();

function normalize(segments, xf) {
  const segs = (Array.isArray(segments) ? segments : [])
    .filter((s) => s && typeof s.src === 'string' && num(s.to, 0) > num(s.from, -1) && num(s.from, -1) >= 0)
    .map((s) => ({ src: s.src, from: s.from, to: s.to, gain: Math.min(1, Math.max(0, num(s.gain, 1))), fi: s.fade_in, fo: s.fade_out }))
    .sort((a, b) => a.from - b.from);
  return segs.map((s, i) => {
    const last = i === segs.length - 1;
    const end = last ? s.to : s.to + xf;
    const fadeIn = Math.min(num(s.fi, i === 0 ? 1.0 : xf), (end - s.from) / 2);
    const fadeOut = Math.min(num(s.fo, last ? 2.0 : xf), (end - s.from) / 2);
    return { src: s.src, from: s.from, end, gain: s.gain, fadeIn, fadeOut };
  });
}

async function buildMusicBed({ segments, workDir, downloadFile, dest, xf }) {
  const segs = normalize(segments, num(xf, 2));
  if (!segs.length) throw new Error('no valid music segments');
  const args = ['-y'];
  const parts = [];
  const labels = [];
  for (let i = 0; i < segs.length; i++) {
    const p = path.join(workDir, 'mseg_' + i + '.mp3');
    await downloadFile(segs[i].src, p);
    args.push('-stream_loop', '-1', '-i', p);
    const s = segs[i];
    const len = s.end - s.from;
    const ms = Math.round(s.from * 1000);
    parts.push(
      '[' + i + ':a]atrim=0:' + f3(len) + ',asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo,' +
      'afade=t=in:st=0:d=' + f3(s.fadeIn) + ':curve=qsin,afade=t=out:st=' + f3(len - s.fadeOut) + ':d=' + f3(s.fadeOut) + ':curve=qsin,' +
      'volume=' + s.gain.toFixed(3) + ',adelay=' + ms + '|' + ms + '[m' + i + ']'
    );
    labels.push('[m' + i + ']');
  }
  const total = segs[segs.length - 1].end;
  parts.push(labels.join('') + 'amix=inputs=' + segs.length + ':duration=longest:normalize=0,alimiter=limit=0.95,atrim=0:' + f3(total) + '[out]');
  args.push('-filter_complex', parts.join(';'), '-map', '[out]', '-ar', '44100', '-b:a', '192k', dest);
  execFileSync('ffmpeg', args, { stdio: ['ignore', 'ignore', 'inherit'] });
  console.log('Music bed built: ' + segs.length + ' segments, ' + total.toFixed(1) + 's');
  return dest;
}

function musicFromClips(clips) {
  const c = (Array.isArray(clips) ? clips : []).find((x) => x && x.direction && x.direction.fx && Array.isArray(x.direction.fx.music));
  return c ? c.direction.fx.music : null;
}

// Drop-in replacement for: await downloadFile(payload.music_url, musicPath)
async function fetchOrCopy(downloadFile, url, dest, ctx) {
  const segs = musicFromClips(ctx && ctx.clips);
  if (segs && segs.length) {
    try {
      return await buildMusicBed({ segments: segs, workDir: ctx.workDir, downloadFile, dest, xf: ctx.xf });
    } catch (e) {
      console.log('Music bed failed, falling back to single track: ' + e.message);
    }
  }
  return downloadFile(url, dest);
}

module.exports = { buildMusicBed, fetchOrCopy, normalize, musicFromClips };

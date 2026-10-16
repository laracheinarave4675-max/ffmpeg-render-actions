// Post effects applied to the FINAL mixed video:
//  - sound effects (sfx) with automatic trim + fade-out
//  - animated "ILLUSTRATION"-style badges (slide + fade in/out, growing underline, pulsing dot)
// Does nothing when no sfx/badges are given.
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const FONT_CANDIDATES = [
  path.join(__dirname, '..', 'assets', 'fonts', 'Poppins-Bold.ttf'),
  '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
  '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
];
const LABELS = { illustration: 'ILLUSTRATION', simulation: 'SIMULATION', artist_concept: 'ARTIST CONCEPT' };
const SUBS = { illustration: 'NOT REAL FOOTAGE', simulation: 'SCIENTIFIC SIMULATION', artist_concept: 'NOT A PHOTOGRAPH' };
const GOLD = '0xFFC53D';

const num = (v, d) => (typeof v === 'number' && isFinite(v) ? v : d);
const findFont = () => FONT_CANDIDATES.find((f) => fs.existsSync(f)) || null;
function probe(args, file) {
  return execFileSync('ffprobe', ['-v', 'error', ...args, file], { encoding: 'utf8' }).trim();
}
const hasAudio = (file) => probe(['-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0'], file).length > 0;
const duration = (file) => parseFloat(probe(['-show_entries', 'format=duration', '-of', 'csv=p=0'], file));
function videoInfo(file) {
  const [w, h, r] = probe(['-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate', '-of', 'csv=p=0'], file).split(',');
  const [a, b] = r.split('/');
  return { w: parseInt(w, 10), h: parseInt(h, 10), fps: Math.round(parseInt(a, 10) / (parseInt(b, 10) || 1)) || 25 };
}
const f3 = (v) => (Math.round(v * 1000) / 1000).toString();

// Builds the filter chain for ONE animated badge; returns { layer, overlay(inLabel,outLabel) }
function badgeGraph(b, i, info, font) {
  const label = LABELS[b.kind];
  const sub = SUBS[b.kind];
  const from = b.from, to = b.to, dur = to - from;
  const fsz = Math.round(info.h * 0.040);
  const subSz = Math.max(10, Math.round(fsz * 0.42));
  const PH = Math.round(fsz * 2.5);
  const PW = Math.round(fsz * 0.74 * Math.max(label.length, sub.length * 0.62) + fsz * 2.6);
  const bar = Math.max(4, Math.round(fsz * 0.28));
  const fo = Math.min(0.35, dur / 3), fi = Math.min(0.35, dur / 3);
  const q = (s) => "'" + s + "'";
  const ff = 'fontfile=' + font;
  const panel =
    'color=c=0x0B0F19@0.66:s=' + PW + 'x' + PH + ':r=' + info.fps + ':d=' + f3(dur) + ',format=rgba,' +
    'drawbox=x=0:y=0:w=' + bar + ':h=ih:color=' + GOLD + '@1:t=fill,' +
    'drawtext=' + ff + ':text=' + q(label) + ':fontcolor=white:fontsize=' + fsz + ':x=' + Math.round(fsz * 0.95) + ':y=' + Math.round(PH * 0.10) + ',' +
    'drawtext=' + ff + ':text=' + q(sub) + ':fontcolor=' + GOLD + ':fontsize=' + subSz + ':x=' + Math.round(fsz * 0.95) + ':y=' + Math.round(PH * 0.62) + ',' +
    'drawtext=' + ff + ':text=' + q('\u2022') + ':fontcolor=' + GOLD + ':fontsize=' + Math.round(fsz * 0.9) + ':x=' + (PW - Math.round(fsz * 1.15)) + ':y=' + Math.round(PH * 0.08) +
    ":alpha='0.45+0.55*sin(2*PI*t*1.6)'" + '[p' + i + ']';
  const ulH = Math.max(3, Math.round(fsz * 0.09));
  const underline =
    'color=c=' + GOLD + ':s=' + Math.round(PW * 0.6) + 'x' + ulH + ':r=' + info.fps + ':d=' + f3(dur) + ',format=rgba[u' + i + ']';
  const comp =
    '[p' + i + '][u' + i + ']overlay=x=' + q('-w+w*(1-pow(1-min(1,t/0.7),3))') + ':y=' + (PH - ulH - Math.round(fsz * 0.12)) + ':format=auto,format=rgba,' +
    'fade=t=in:st=0:d=' + f3(fi) + ':alpha=1,fade=t=out:st=' + f3(dur - fo) + ':d=' + f3(fo) + ':alpha=1,' +
    'setpts=PTS+' + f3(from) + '/TB[b' + i + ']';
  const slideIn = 'pow(1-clip((t-' + f3(from) + ')/0.45,0,1),3)';
  const slideOut = 'pow(1-clip((' + f3(to) + '-t)/' + f3(fo) + ',0,1),3)';
  const x = 'W-w-W/24+(w+W/24)*(' + slideIn + '+' + slideOut + ')';
  return {
    parts: [panel, underline, comp],
    overlay: (inL, outL) =>
      '[' + inL + '][b' + i + ']overlay=x=' + q(x) + ':y=H/20:enable=' + q('between(t,' + f3(from) + ',' + f3(to) + ')') +
      ':eof_action=pass:format=auto[' + outL + ']',
  };
}

async function applyPostEffects({ finalPath, sfx, badges, workDir, downloadFile }) {
  const sfxList = (Array.isArray(sfx) ? sfx : []).filter((s) => s && typeof s.src === 'string' && num(s.at, -1) >= 0);
  let badgeList = (Array.isArray(badges) ? badges : []).filter((b) => b && LABELS[b.kind] && num(b.to, 0) > num(b.from, 0));
  const font = findFont();
  if (badgeList.length && !font) {
    console.log('No badge font found, skipping badges');
    badgeList = [];
  }
  if (!sfxList.length && !badgeList.length) return finalPath;

  const dur = duration(finalPath);
  const withAudio = hasAudio(finalPath);
  const info = videoInfo(finalPath);
  const args = ['-y', '-i', finalPath];
  let baseAudio = '0:a';
  let next = 1;
  if (sfxList.length && !withAudio) {
    args.push('-f', 'lavfi', '-t', dur.toFixed(3), '-i', 'anullsrc=r=44100:cl=stereo');
    baseAudio = '1:a';
    next = 2;
  }
  const parts = [];
  const labels = [];
  for (let i = 0; i < sfxList.length; i++) {
    const p = path.join(workDir, 'sfx_' + i + '.mp3');
    await downloadFile(sfxList[i].src, p);
    args.push('-i', p);
    const at = Math.round(sfxList[i].at * 1000);
    const vol = Math.min(1, Math.max(0, num(sfxList[i].volume, 0.3)));
    const len = Math.max(0.1, num(sfxList[i].len, 3));
    const fade = Math.min(len, Math.max(0.02, num(sfxList[i].fade, 0.4)));
    parts.push(
      '[' + (next + i) + ':a]atrim=0:' + f3(len) + ',asetpts=PTS-STARTPTS,afade=t=out:st=' + f3(len - fade) + ':d=' + f3(fade) +
      ',adelay=' + at + '|' + at + ',volume=' + vol.toFixed(2) + '[s' + i + ']'
    );
    labels.push('[s' + i + ']');
  }
  if (sfxList.length) {
    parts.push('[' + baseAudio + ']' + labels.join('') + 'amix=inputs=' + (sfxList.length + 1) + ':duration=first:dropout_transition=0:normalize=0[aout]');
  }
  let vmap = '0:v';
  if (badgeList.length) {
    let cur = '0:v';
    badgeList.forEach((b, i) => {
      const g = badgeGraph(b, i, info, font);
      g.parts.forEach((p) => parts.push(p));
      const out = i === badgeList.length - 1 ? 'vout' : 'v' + (i + 1);
      parts.push(g.overlay(cur, out));
      cur = out;
    });
    vmap = '[vout]';
  }
  args.push('-filter_complex', parts.join(';'));
  args.push('-map', vmap);
  if (sfxList.length) args.push('-map', '[aout]'); else if (withAudio) args.push('-map', '0:a');
  if (badgeList.length) args.push('-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p');
  else args.push('-c:v', 'copy');
  if (sfxList.length) args.push('-c:a', 'aac', '-b:a', '192k'); else if (withAudio) args.push('-c:a', 'copy');
  const out = path.join(workDir, 'final_fx.mp4');
  args.push('-movflags', '+faststart', out);
  execFileSync('ffmpeg', args, { stdio: ['ignore', 'ignore', 'inherit'] });
  console.log('Post effects applied: ' + sfxList.length + ' sfx, ' + badgeList.length + ' badges');
  return out;
}
module.exports = { applyPostEffects, LABELS, SUBS };

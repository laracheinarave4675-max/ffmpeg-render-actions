// Post effects applied to the FINAL mixed video: sound effects (sfx) and
// ILLUSTRATION-style badges. Does nothing when no sfx/badges are given.
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';
const LABELS = { illustration: 'ILLUSTRATION', simulation: 'SIMULATION', artist_concept: 'ARTIST CONCEPT' };

function probe(args, file) {
  return execFileSync('ffprobe', ['-v', 'error', ...args, file], { encoding: 'utf8' }).trim();
}
function hasAudio(file) {
  return probe(['-select_streams', 'a', '-show_entries', 'stream=index', '-of', 'csv=p=0'], file).length > 0;
}
function duration(file) {
  return parseFloat(probe(['-show_entries', 'format=duration', '-of', 'csv=p=0'], file));
}
const num = (v, d) => (typeof v === 'number' && isFinite(v) ? v : d);

async function applyPostEffects({ finalPath, sfx, badges, workDir, downloadFile }) {
  const sfxList = (Array.isArray(sfx) ? sfx : []).filter(s => s && typeof s.src === 'string' && num(s.at, -1) >= 0);
  let badgeList = (Array.isArray(badges) ? badges : []).filter(b => b && LABELS[b.kind] && num(b.to, 0) > num(b.from, 0));
  if (badgeList.length && !fs.existsSync(FONT)) {
    console.log('Badge font not found, skipping badges: ' + FONT);
    badgeList = [];
  }
  if (!sfxList.length && !badgeList.length) return finalPath;

  const dur = duration(finalPath);
  const withAudio = hasAudio(finalPath);
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
    const ms = Math.round(sfxList[i].at * 1000);
    const vol = Math.min(1, Math.max(0, num(sfxList[i].volume, 0.35)));
    parts.push('[' + (next + i) + ':a]adelay=' + ms + '|' + ms + ',volume=' + vol.toFixed(2) + '[s' + i + ']');
    labels.push('[s' + i + ']');
  }
  if (sfxList.length) {
    parts.push('[' + baseAudio + ']' + labels.join('') + 'amix=inputs=' + (sfxList.length + 1) +
      ':duration=first:dropout_transition=0:normalize=0[aout]');
  }
  if (badgeList.length) {
    const dts = badgeList.map(b =>
      'drawtext=fontfile=' + FONT + ':text=' + LABELS[b.kind] +
      ':fontsize=h/22:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=14' +
      ':x=w-tw-w/24:y=h/20:enable=\'between(t,' + b.from + ',' + b.to + ')\'');
    parts.push('[0:v]' + dts.join(',') + '[vout]');
  }
  args.push('-filter_complex', parts.join(';'));
  args.push('-map', badgeList.length ? '[vout]' : '0:v');
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
module.exports = { applyPostEffects, LABELS };

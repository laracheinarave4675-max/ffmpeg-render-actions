'use strict';
// Final finishing pass in ONE re-encode: visual look (director/finish.cjs graph) + audio mastering.
// Both parts are optional. With neither requested, nothing is touched ({ applied: false }).
// Errors are thrown (never silently skipped) so a failed pass shows up as a failed render.
const { spawnSync } = require('child_process');
const fs = require('fs');

function num(v, d) { return (typeof v === 'number' && isFinite(v)) ? v : d; }

// Audio: remove rumble, gentle compression, broadcast loudness (YouTube normalises near -14 LUFS).
function buildAudioChain(opts) {
  if (!opts) return null;
  const o = (opts === true) ? {} : opts;
  const lufs = Math.min(-10, Math.max(-24, num(o.lufs, -15)));
  const tp = Math.min(-0.5, Math.max(-3, num(o.tp, -1.5)));
  const lra = Math.min(20, Math.max(5, num(o.lra, 9)));
  return 'highpass=f=70,acompressor=threshold=0.14:ratio=2.5:attack=20:release=250:makeup=1.5,' +
         'loudnorm=I=' + lufs + ':TP=' + tp + ':LRA=' + lra;
}

function buildArgs(inPath, outPath, graph, audioChain) {
  const a = ['-y', '-i', inPath];
  if (graph) a.push('-filter_complex', graph, '-map', '[vout]');
  else a.push('-map', '0:v:0');
  a.push('-map', '0:a?');
  if (graph) a.push('-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p');
  else a.push('-c:v', 'copy');
  if (audioChain) a.push('-af', audioChain, '-c:a', 'aac', '-b:a', '192k', '-ar', '44100');
  else a.push('-c:a', 'copy');
  a.push('-movflags', '+faststart', outPath);
  return a;
}

function applyFinishPass(inPath, outPath, req, runner) {
  req = req || {};
  const graph = req.finish ? require('./finish.cjs').buildFilterGraph(req.finish === true ? {} : req.finish) : null;
  const audioChain = buildAudioChain(req.master_audio);
  if (!graph && !audioChain) return { applied: false, outPath: inPath };
  if (!fs.existsSync(inPath)) throw new Error('finish_pass: input not found: ' + inPath);
  const run = runner || spawnSync;
  const r = run('ffmpeg', buildArgs(inPath, outPath, graph, audioChain), { encoding: 'utf8' });
  if (r.status !== 0) throw new Error('finish_pass: ffmpeg failed: ' + String(r.stderr || '').slice(0, 800));
  return { applied: true, outPath, visual: !!graph, audio: !!audioChain };
}

module.exports = { buildAudioChain, buildArgs, applyFinishPass };

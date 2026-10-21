'use strict';
// Visual finishing layer: color grade, soft bloom, vignette, film grain, light sharpening.
// Pure-ffmpeg, no extra assets. Applied to a finished video file in ONE re-encode pass.
// Audio is stream-copied untouched. Disabled (null graph) => caller should skip the pass.

const { spawnSync } = require('child_process');
const fs = require('fs');

const PRESETS = {
  // Deep-space documentary look: cool shadows, gentle warm highlights, soft glow.
  cosmic:  { grade: 1, bloom: 0.16, vignette: 0.5, grain: 4, sharpen: 0.35 },
  // Very light touch (safe default for already-graded sources).
  subtle:  { grade: 0.6, bloom: 0.08, vignette: 0.3, grain: 2, sharpen: 0.2 },
  // Stronger cinematic feel for dramatic scenes.
  dramatic:{ grade: 1.3, bloom: 0.22, vignette: 0.7, grain: 6, sharpen: 0.4 },
};

function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }
function num(v, d) { return (typeof v === 'number' && isFinite(v)) ? v : d; }

function resolveOptions(opts) {
  if (opts === false || opts === null || opts === undefined) return null;
  const o = (opts === true) ? {} : opts;
  const base = PRESETS[o.preset || 'cosmic'];
  if (!base) throw new Error('finish: unknown preset "' + o.preset + '" (use cosmic, subtle, dramatic)');
  return {
    grade: clamp(num(o.grade, base.grade), 0, 2),
    bloom: clamp(num(o.bloom, base.bloom), 0, 0.5),
    vignette: clamp(num(o.vignette, base.vignette), 0, 1),
    grain: clamp(num(o.grain, base.grain), 0, 12),
    sharpen: clamp(num(o.sharpen, base.sharpen), 0, 1),
  };
}

function f(n) { return String(Math.round(n * 1000) / 1000); }

// Returns an ffmpeg -filter_complex graph string (input [0:v], output [vout]) or null if nothing to do.
function buildFilterGraph(opts) {
  const o = resolveOptions(opts);
  if (!o) return null;
  const steps = [];
  let label = '0:v';
  let n = 0;
  const next = () => 'f' + (++n);
  const chain = (filters) => {
    const out = next();
    steps.push('[' + label + ']' + filters + '[' + out + ']');
    label = out;
  };

  chain('format=yuv420p');

  if (o.grade > 0) {
    const g = o.grade;
    const eq = 'eq=contrast=' + f(1 + 0.06 * g) + ':saturation=' + f(1 + 0.08 * g) + ':gamma=' + f(1 - 0.02 * g);
    // split toning: cool shadows, slightly warm highlights (curves is ~5x faster than colorbalance)
    const sh = 0.03 * g, hi = 0.03 * g;
    const cb = "curves=r='0/0 0.5/0.49 1/1':b='0/" + f(sh) + " 0.5/0.51 1/" + f(1 - hi) + "'";
    chain(eq + ',' + cb);
  }
  if (o.sharpen > 0) {
    chain('unsharp=5:5:' + f(o.sharpen) + ':5:5:0');
  }
  if (o.bloom > 0) {
    const a = next(), b = next(), bl = next(), bl2 = next(), a2 = next(), mixed = next();
    steps.push('[' + label + ']split=2[' + a + '][' + b + ']');
    // glow source: darken mids so only highlights bleed, blur at quarter resolution (fast)
    steps.push('[' + b + ']curves=all=\'0/0 0.55/0.3 1/1\',scale=iw/4:ih/4:flags=bilinear,gblur=sigma=3[' + bl + ']');
    steps.push('[' + bl + '][' + a + ']scale2ref=flags=bicubic[' + bl2 + '][' + a2 + ']');
    steps.push('[' + a2 + '][' + bl2 + ']blend=all_mode=screen:all_opacity=' + f(o.bloom) + '[' + mixed + ']');
    label = mixed;
  }
  if (o.vignette > 0) {
    // smaller angle => stronger vignette. s=0 -> PI/4 (weak), s=1 -> PI/10 (strong)
    const angle = (Math.PI / 2) * (0.5 - 0.3 * o.vignette);
    chain('vignette=angle=' + f(angle));
  }
  if (o.grain > 0) {
    chain('noise=alls=' + f(o.grain) + ':allf=t+u');
  }
  chain('format=yuv420p');
  // rename the last label to [vout]
  const last = steps.length - 1;
  steps[last] = steps[last].replace(/\[[^\[\]]+\]$/, '[vout]');
  return steps.join(';');
}

function buildArgs(inPath, outPath, graph, enc) {
  const e = Object.assign({ preset: 'veryfast', crf: 17 }, enc || {});
  return [
    '-y', '-hide_banner', '-loglevel', 'error',
    '-i', inPath,
    '-filter_complex', graph,
    '-map', '[vout]', '-map', '0:a?',
    '-c:v', 'libx264', '-preset', String(e.preset), '-crf', String(e.crf), '-pix_fmt', 'yuv420p',
    '-c:a', 'copy', '-movflags', '+faststart',
    outPath,
  ];
}

// Applies finishing. Returns { applied: boolean, outPath }.
// When opts disabled, nothing is touched and { applied:false, outPath: inPath } is returned.
function applyFinish(inPath, outPath, opts, enc, runner) {
  const graph = buildFilterGraph(opts);
  if (!graph) return { applied: false, outPath: inPath };
  if (!fs.existsSync(inPath)) throw new Error('finish: input not found: ' + inPath);
  const run = runner || spawnSync;
  const r = run('ffmpeg', buildArgs(inPath, outPath, graph, enc), { encoding: 'utf8' });
  if (r.status !== 0) {
    throw new Error('finish: ffmpeg failed: ' + String(r.stderr || '').slice(0, 800));
  }
  return { applied: true, outPath };
}

module.exports = { PRESETS, resolveOptions, buildFilterGraph, buildArgs, applyFinish };

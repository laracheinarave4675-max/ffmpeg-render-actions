'use strict';
const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');
const { buildFilterGraph, applyFinish, resolveOptions } = require('../director/finish.cjs');

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'finish-'));
const sh = (cmd, args) => spawnSync(cmd, args, { encoding: 'buffer' });
let passed = 0;
const ok = (name) => { passed++; console.log('ok - ' + name); };

// 1. pure graph logic
assert.strictEqual(buildFilterGraph(false), null);
assert.strictEqual(buildFilterGraph(null), null);
assert.strictEqual(buildFilterGraph(undefined), null);
ok('disabled options produce no graph');

const g = buildFilterGraph({ preset: 'cosmic' });
for (const k of ['eq=', 'curves=r=', 'unsharp=', 'blend=all_mode=screen', 'vignette=', 'noise=', '[vout]']) {
  assert(g.includes(k), 'graph should contain ' + k);
}
assert(g.endsWith('[vout]'));
ok('cosmic graph contains all stages and ends in [vout]');

const only = buildFilterGraph({ grade: 0, bloom: 0, vignette: 0, grain: 0, sharpen: 0 });
assert(!/eq=|blend=|vignette=|noise=|unsharp=/.test(only));
ok('zeroed stages are omitted');

assert.throws(() => resolveOptions({ preset: 'nope' }), /unknown preset/);
const clamped = resolveOptions({ grain: 99, bloom: 9, vignette: 5 });
assert(clamped.grain <= 12 && clamped.bloom <= 0.5 && clamped.vignette <= 1);
ok('options are clamped and bad preset rejected');

// 2. real ffmpeg behaviour
const flat = path.join(tmp, 'flat.mp4');
let r = sh('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=gray:s=640x360:r=25:d=3',
  '-f', 'lavfi', '-i', 'sine=frequency=440:duration=3', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', flat]);
assert.strictEqual(r.status, 0, 'fixture creation failed');

function probe(file, entry) {
  const p = sh('ffprobe', ['-v', 'error', '-select_streams', entry.stream, '-show_entries', entry.show, '-of', 'csv=p=0', file]);
  return String(p.stdout).trim();
}
function pixel(file, crop, frame) {
  const p = sh('ffmpeg', ['-v', 'error', '-i', file, '-vf', 'select=eq(n\\,' + (frame || 0) + '),' + crop + ',scale=1:1', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'gray', '-']);
  return p.stdout[0];
}

// vignette only: corners darker than center, geometry and duration preserved
const vig = path.join(tmp, 'vig.mp4');
let res = applyFinish(flat, vig, { grade: 0, bloom: 0, vignette: 1, grain: 0, sharpen: 0 });
assert.strictEqual(res.applied, true);
const center = pixel(vig, 'crop=32:32:304:164', 5);
const corner = pixel(vig, 'crop=16:16:0:0', 5);
assert(center - corner >= 8, 'corner should be darker than center (center ' + center + ', corner ' + corner + ')');
assert.strictEqual(probe(vig, { stream: 'v:0', show: 'stream=width,height' }), '640,360');
assert.strictEqual(probe(vig, { stream: 'a:0', show: 'stream=codec_name' }), 'aac');
const dIn = parseFloat(probe(flat, { stream: 'v:0', show: 'stream=duration' }));
const dOut = parseFloat(probe(vig, { stream: 'v:0', show: 'stream=duration' }));
assert(Math.abs(dIn - dOut) < 0.1, 'duration changed: ' + dIn + ' vs ' + dOut);
ok('vignette darkens corners; size, duration and audio codec preserved');

// grain: frames differ over time; without grain they are identical
const grn = path.join(tmp, 'grain.mp4');
applyFinish(flat, grn, { grade: 0, bloom: 0, vignette: 0, grain: 8, sharpen: 0 });
const grab = (file, n) => sh('ffmpeg', ['-v', 'error', '-i', file, '-vf', 'select=eq(n\\,' + n + '),crop=64:64:288:148', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'gray', '-']).stdout;
assert(!grab(grn, 3).equals(grab(grn, 4)), 'grain should vary between frames');
ok('grain varies per frame');

// bloom: bright spot spreads light into its surroundings
const spot = path.join(tmp, 'spot.mp4');
r = sh('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'color=c=black:s=640x360:r=25:d=2',
  '-vf', 'drawbox=x=300:y=160:w=40:h=40:color=white:t=fill', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', spot]);
assert.strictEqual(r.status, 0);
const glow = path.join(tmp, 'glow.mp4');
applyFinish(spot, glow, { grade: 0, bloom: 0.4, vignette: 0, grain: 0, sharpen: 0 });
const before = pixel(spot, 'crop=16:16:344:170', 5);
const after = pixel(glow, 'crop=16:16:344:170', 5);
assert(after > before + 3, 'bloom should lift pixels next to a bright spot (' + before + ' -> ' + after + ')');
ok('bloom spreads light around highlights');

// disabled => untouched, no output created
const none = path.join(tmp, 'none.mp4');
res = applyFinish(flat, none, false);
assert.strictEqual(res.applied, false);
assert.strictEqual(res.outPath, flat);
assert(!fs.existsSync(none));
ok('disabled finish is a no-op');

// failure surfaces as an error, not silence
assert.throws(() => applyFinish(path.join(tmp, 'missing.mp4'), path.join(tmp, 'x.mp4'), true), /input not found/);
ok('missing input throws');

console.log('\nfinish tests passed: ' + passed);
fs.rmSync(tmp, { recursive: true, force: true });

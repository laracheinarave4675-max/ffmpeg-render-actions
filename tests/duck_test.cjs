"use strict";
const fs = require("fs"), path = require("path"), os = require("os");
const { spawnSync } = require("child_process");
let failed = 0;
function check(name, ok, extra) {
  console.log((ok ? "PASS " : "FAIL ") + name + (extra ? " (" + extra + ")" : ""));
  if (!ok) failed++;
}
function ff(args) { return spawnSync("ffmpeg", ["-hide_banner", "-y", ...args], { encoding: "utf8" }); }

const src = fs.readFileSync(path.join(__dirname, "..", "render.js"), "utf8");

// 1) static checks on render.js
const m = /function duckParams\(d\) \{[\s\S]*?\n\}/.exec(src);
check("duckParams found in render.js", !!m);
const oldGraph = "'[1:a]' + AF + '[na];[2:a]volume=' + musicVol + ',' + AF + '[music];[na][music]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[aout]'";
check("old no-duck graph still present verbatim", src.split(oldGraph).length - 1 === 1);
check("mixWithEnding duck hook present once", src.split("if (o.duck && o.narrPath && o.musicPath)").length - 1 === 1);
check("duck is off by default (needs duckCfg)", /const duckCfg = payload\.music_duck \|\|/.test(src));
if (!m) { console.log("FAILED"); process.exit(1); }
const P = new Function(m[0] + "; return duckParams;")()(true);

// 2) real measurement
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "dk-"));
const narr = path.join(tmp, "narr.wav"), music = path.join(tmp, "music.wav");
const AF = "aformat=sample_rates=44100:channel_layouts=stereo";
ff(["-f", "lavfi", "-i", "sine=frequency=440:duration=4", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
  "-filter_complex", "[0:a]" + AF + "[a];[1:a]atrim=0:4[b];[a][b]concat=n=2:v=0:a=1[o]", "-map", "[o]", narr]);
ff(["-f", "lavfi", "-i", "sine=frequency=220:duration=8", music]);

function render(name, graph) {
  const out = path.join(tmp, name + ".wav");
  const r = ff(["-i", narr, "-i", music, "-filter_complex", graph, "-map", "[o]", out]);
  return { out, ok: r.status === 0, err: (r.stderr || "").slice(-300) };
}
function level(file, ss, t) {
  const r = spawnSync("ffmpeg", ["-hide_banner", "-ss", String(ss), "-t", String(t), "-i", file, "-af", "volumedetect", "-f", "null", "-"], { encoding: "utf8" });
  const x = /mean_volume: (-?[0-9.]+) dB/.exec(r.stderr || "");
  return x ? parseFloat(x[1]) : null;
}

const ducked = render("ducked", "[0:a]" + AF + "[na0];[na0]asplit=2[na][nak];[1:a]volume=0.15," + AF + "[music];[music][nak]sidechaincompress=" + P + "[o]");
const plain = render("plain", "[1:a]volume=0.15," + AF + "[o]");
check("ducked graph renders", ducked.ok, ducked.ok ? "" : ducked.err);
check("plain graph renders", plain.ok);
if (ducked.ok && plain.ok) {
  const dSpeech = level(ducked.out, 1, 2.5), dSilence = level(ducked.out, 5, 2.5);
  const pSpeech = level(plain.out, 1, 2.5), pSilence = level(plain.out, 5, 2.5);
  const drop = dSilence - dSpeech;
  check("music drops at least 6 dB while narrator speaks", drop >= 6, "drop=" + drop.toFixed(1) + " dB");
  check("without ducking the music stays flat", Math.abs(pSpeech - pSilence) < 0.5, "diff=" + (pSpeech - pSilence).toFixed(2));
  check("music is not reduced when narrator is silent", Math.abs(dSilence - pSilence) < 1.5, "diff=" + (dSilence - pSilence).toFixed(2));
}

// 3) full graphs in the exact shape used by render.js (both branches)
const vid = path.join(tmp, "v.mp4");
ff(["-f", "lavfi", "-i", "color=c=black:s=160x90:r=25:d=8", "-c:v", "libx264", "-pix_fmt", "yuv420p", vid]);
function full(name, graph) {
  const r = ff(["-i", vid, "-i", narr, "-i", music, "-filter_complex", graph, "-map", "[aout]", "-f", "null", "-"]);
  check(name, r.status === 0, r.status === 0 ? "" : (r.stderr || "").slice(-300));
}
full("normal-branch ducked graph is valid",
  "[1:a]" + AF + "[na0];[na0]asplit=2[na][nak];[2:a]volume=0.15," + AF + "[music];[music][nak]sidechaincompress=" + P + "[musicd];[na][musicd]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[aout]");
full("ending-branch ducked graph is valid",
  "[1:a]" + AF + ",apad=whole_dur=8[na];[2:a]volume=0.15," + AF + ",atrim=0:8,afade=t=out:st=5:d=3[music];[na]asplit=2[nam][nak];[music][nak]sidechaincompress=" + P + "[musicd];[nam][musicd]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[aout]");

console.log(failed === 0 ? "ALL PASSED" : failed + " FAILED");
process.exit(failed === 0 ? 0 : 1);

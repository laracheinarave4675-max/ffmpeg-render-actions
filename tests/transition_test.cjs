"use strict";
const fs = require("fs"), path = require("path"), os = require("os");
const { spawnSync } = require("child_process");
let failed = 0;
function check(name, ok, extra) {
  console.log((ok ? "PASS " : "FAIL ") + name + (extra ? " (" + extra + ")" : ""));
  if (!ok) failed++;
}
const near = (a, b, e) => Math.abs(a - b) < (e || 1e-6);

// 1) logic extracted from render.js
const src = fs.readFileSync(path.join(__dirname, "..", "render.js"), "utf8");
const m = /const MIN_TRANS[\s\S]*?function pairSum\(\) \{[\s\S]*?return s;\s*\}/.exec(src);
check("transition block found in render.js", !!m);
if (m) {
  const make = new Function("clips", "segDurations", "transType", "transDur", m[0] + "; return { pairT, pairSum };");
  let r = make([{}, {}, {}], [4, 4, 4], "fade", 0.8);
  check("old format falls back to global", r.pairT(1).type === "fade" && near(r.pairT(1).dur, 0.8) && near(r.pairSum(), 1.6));
  const cutClip = { direction: { transition_in: { type: "cut" } } };
  r = make([{}, cutClip], [4, 4], "fade", 0.8);
  check("cut becomes one-frame transition", r.pairT(1).type === "fade" && near(r.pairT(1).dur, 0.04));
  const fb = { direction: { transition_in: { type: "fadeblack", duration: 1.2 } } };
  r = make([{}, fb], [5, 5], "fade", 0.8);
  check("fadeblack keeps 1.2s on long segments", r.pairT(1).type === "fadeblack" && near(r.pairT(1).dur, 1.2));
  r = make([{}, fb], [2, 2], "fade", 0.8);
  check("duration clamped on short segments", near(r.pairT(1).dur, 0.9));
  r = make([{}, fb, cutClip], [5, 5, 5], "fade", 0.8);
  check("mixed pairs sum correctly", near(r.pairSum(), 1.24));
}

// 2) real ffmpeg graph with per-pair durations, video + audio
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "tr-"));
const colors = ["red", "green", "blue"];
const segs = colors.map((c, i) => {
  const f = path.join(tmp, "s" + i + ".mp4");
  spawnSync("ffmpeg", ["-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=c=" + c + ":s=640x360:r=25:d=4",
    "-f", "lavfi", "-i", "sine=frequency=440:d=4", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", f]);
  return f;
});
const types = ["fadeblack", "fade"], durs = [1.2, 0.04];
let fc = "", prev = "0:v", cum = 4;
for (let i = 1; i < 3; i++) {
  const out = i === 2 ? "vout" : "v" + i;
  fc += "[" + prev + "][" + i + ":v]xfade=transition=" + types[i - 1] + ":duration=" + durs[i - 1] + ":offset=" + Math.max(0, cum - durs[i - 1]).toFixed(3) + "[" + out + "];";
  cum = cum + 4 - durs[i - 1];
  prev = out;
}
let aPrev = "0:a";
for (let i = 1; i < 3; i++) {
  const o = i === 2 ? "aout" : "a" + i;
  fc += "[" + aPrev + "][" + i + ":a]acrossfade=d=" + durs[i - 1] + ":c1=tri:c2=tri[" + o + "]" + (i < 2 ? ";" : "");
  aPrev = o;
}
const outFile = path.join(tmp, "out.mp4");
const res = spawnSync("ffmpeg", ["-hide_banner", "-y", "-i", segs[0], "-i", segs[1], "-i", segs[2], "-filter_complex", fc,
  "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", outFile], { encoding: "utf8" });
check("per-pair xfade + acrossfade render succeeded", res.status === 0, res.status === 0 ? "" : (res.stderr || "").slice(-300));
if (res.status === 0) {
  const pr = spawnSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", outFile], { encoding: "utf8" });
  const d = parseFloat(pr.stdout);
  check("final duration is 10.76s (12 - 1.2 - 0.04)", Math.abs(d - 10.76) < 0.2, "duration=" + d);
}
console.log(failed === 0 ? "ALL PASSED" : failed + " FAILED");
process.exit(failed === 0 ? 0 : 1);

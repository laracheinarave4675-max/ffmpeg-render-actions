"use strict";
// Builds the exact command string that render.js now builds for a clip with direction.camera,
// and runs it through the shell (same as render.js run()).
const { execSync, spawnSync } = require("child_process");
const fs = require("fs"), path = require("path"), os = require("os");
const cam = require("../director/camera.cjs");

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sq-"));
const img = path.join(tmp, "in.png");
const out = path.join(tmp, "seg.mp4");
execSync('ffmpeg -hide_banner -loglevel error -f lavfi -i testsrc2=s=1866x878 -frames:v 1 "' + img + '" -y');

const dur = 4;
const spec = { mode: "push_in", focus: { x: 0.5, y: 0.5 }, zoom_start: 1.0, zoom_end: 1.15, easing: "ease_in_out", start_at: 0, end_at: 4 };
const dirZp = cam.buildZoompan(spec, { duration: dur, fps: 25, outW: 1920, outH: 1080 });
const dirPrefit = cam.prefitFilter(1920, 1080);
const cmd = 'ffmpeg -loop 1 -i "' + img + '" -vf "' + dirPrefit + ',' + dirZp + ',format=yuv420p" -c:v libx264 -t ' + dur + ' -r 25 "' + out + '" -y';

let failed = 0;
function check(name, ok, extra) {
  console.log((ok ? "PASS " : "FAIL ") + name + (extra ? " (" + extra + ")" : ""));
  if (!ok) failed++;
}

let ran = true;
try { execSync(cmd, { stdio: "pipe" }); } catch (e) { ran = false; console.log(String(e.stderr).slice(-300)); }
check("shell command runs", ran);

if (ran) {
  const pr = spawnSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], { encoding: "utf8" });
  const d = parseFloat(pr.stdout);
  check("segment duration is about 4s", Math.abs(d - dur) < 0.15, "duration=" + d);

  const a = path.join(tmp, "a.png"), b = path.join(tmp, "b.png");
  spawnSync("ffmpeg", ["-hide_banner", "-y", "-i", out, "-vf", "select=eq(n\\,0)", "-frames:v", "1", a]);
  spawnSync("ffmpeg", ["-hide_banner", "-y", "-i", out, "-vf", "select=eq(n\\,95)", "-frames:v", "1", b]);
  const ps = spawnSync("ffmpeg", ["-hide_banner", "-i", a, "-i", b, "-lavfi", "psnr", "-f", "null", "-"], { encoding: "utf8" });
  const m = /average:([0-9.]+|inf)/.exec(ps.stderr || "");
  check("camera motion present in segment", !!m && m[1] !== "inf", "psnr=" + (m ? m[1] : "n/a"));
}
console.log(failed === 0 ? "ALL PASSED" : failed + " FAILED");
process.exit(failed === 0 ? 0 : 1);

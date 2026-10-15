const { execFileSync } = require("child_process");
const cam = require("../director/camera.cjs");
execFileSync("ffmpeg", ["-y", "-f", "lavfi", "-i",
  "color=black:s=3200x900,geq=lum='255*X/W':cb=128:cr=128",
  "-frames:v", "1", "/tmp/ramp.png"], { stdio: "ignore" });
const vf = cam.buildZoompan(
  { mode: "pan", easing: "ease_in_out", focus: { x: 0.2, y: 0.5 }, pan_to: { x: 0.8, y: 0.5 } },
  { duration: 6, fps: 25, outW: 1920, outH: 1080 });
const out = execFileSync("ffmpeg", ["-loop", "1", "-t", "6", "-r", "25", "-i", "/tmp/ramp.png", "-vf",
  vf + ",signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-",
  "-f", "null", "-"], { encoding: "utf8", maxBuffer: 1 << 26 });
const ys = [...out.matchAll(/YAVG=([\d.]+)/g)].map(m => parseFloat(m[1]));
const diffs = ys.slice(1).map((v, i) => v - ys[i]);
const mid = diffs.slice(Math.floor(diffs.length * 0.2), Math.floor(diffs.length * 0.8));
const med = mid.slice().sort((a, b) => a - b)[Math.floor(mid.length / 2)];
const bad = mid.filter(d => d < med * 0.4 || d > med * 2.5).length;
const neg = diffs.filter(d => d < -0.01).length;
console.log({ frames: ys.length, first: ys[0].toFixed(1), last: ys[ys.length - 1].toFixed(1), medianStep: med.toFixed(3), plateausOrJumps: bad, backwardSteps: neg });
if (ys.length < 140 || neg || bad || ys[ys.length - 1] - ys[0] < 50) { console.error("FAIL"); process.exit(1); }
console.log("PASS");

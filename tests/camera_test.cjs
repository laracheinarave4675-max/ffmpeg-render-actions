"use strict";
const { spawnSync } = require("child_process");
const fs = require("fs"), path = require("path"), os = require("os");
const cam = require("../director/camera.cjs");
const { validate } = require("../director/validate_plan.cjs");

let failed = 0;
function check(name, ok, extra) {
  console.log((ok ? "PASS " : "FAIL ") + name + (extra ? " (" + extra + ")" : ""));
  if (!ok) failed++;
}
function ff(args) { return spawnSync("ffmpeg", ["-hide_banner", "-y", ...args], { encoding: "utf8" }); }

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "dir-"));

// 1) unit checks
const r = cam.resolveZoom({ mode: "push_in", zoom_start: 1, zoom_end: 2, max_upscale: 1.15 });
check("upscale guard clamps zoom_end to 1.15", r.ze === 1.15 && r.clamped === true);
check("static returns null", cam.buildZoompan({ mode: "static" }, { duration: 5 }) === null);

// 2) real renders on a synthetic 1866x878 image (no network)
const img = path.join(tmp, "in.png");
ff(["-f", "lavfi", "-i", "testsrc2=s=1866x878", "-frames:v", "1", img]);

function render(name, spec) {
  const out = path.join(tmp, name + ".mp4");
  const zp = cam.buildZoompan(spec, { duration: 5, fps: 30, outW: 1920, outH: 1080 });
  const vf = cam.prefitFilter(1920, 1080) + "," + zp + ",format=yuv420p";
  const res = ff(["-i", img, "-vf", vf, "-frames:v", "150", "-r", "30", out]);
  return { out, ok: res.status === 0, err: res.stderr };
}
function psnrFirstLast(video) {
  const a = path.join(tmp, "a.png"), b = path.join(tmp, "b.png");
  ff(["-i", video, "-vf", "select=eq(n\\,0)", "-frames:v", "1", a]);
  ff(["-i", video, "-vf", "select=eq(n\\,149)", "-frames:v", "1", b]);
  const res = spawnSync("ffmpeg", ["-hide_banner", "-i", a, "-i", b, "-lavfi", "psnr", "-f", "null", "-"], { encoding: "utf8" });
  const m = /average:([0-9.]+|inf)/.exec(res.stderr || "");
  return m ? m[1] : null;
}

const specs = {
  push_in: { mode: "push_in", focus: { x: 0.5, y: 0.5 }, zoom_start: 1.0, zoom_end: 1.15, easing: "ease_in_out", start_at: 0, end_at: 5 },
  pan: { mode: "pan", focus: { x: 0.35, y: 0.5 }, pan_to: { x: 0.65, y: 0.5 }, zoom_start: 1.1, zoom_end: 1.1, easing: "ease_in_out", start_at: 0, end_at: 5, max_upscale: 1.15 }
};
for (const k of Object.keys(specs)) {
  const rr = render(k, specs[k]);
  check(k + " render succeeded", rr.ok, rr.ok ? "" : rr.err.slice(-200));
  if (rr.ok) {
    const ps = psnrFirstLast(rr.out);
    check(k + " motion happened (first frame differs from last)", ps !== null && ps !== "inf", "psnr=" + ps);
  }
}

// 3) validator checks
const good = {
  schema: "director_plan/v1", video: { width: 1920, height: 1080 },
  scenes: [{
    scene_id: "a", source_kind: "real_observation", narration: { start: 0, end: 5 },
    asset: { known_native_size: { w: 1866, h: 878 } },
    direction: { camera: { mode: "push_in", zoom_start: 1, zoom_end: 1.1, max_upscale: 1.15 }, transition_in: { type: "fade" } }
  }]
};
check("valid plan passes", validate(good).valid === true);
const bad = JSON.parse(JSON.stringify(good));
bad.scenes[0].source_kind = "illustration";          // no badge
bad.scenes[0].direction.camera.zoom_end = 1.6;        // over max_upscale on small source
check("broken plan fails", validate(bad).valid === false, validate(bad).errors.length + " errors");

console.log(failed === 0 ? "ALL PASSED" : failed + " FAILED");
process.exit(failed === 0 ? 0 : 1);

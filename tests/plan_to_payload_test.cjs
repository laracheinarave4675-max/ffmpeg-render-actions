"use strict";
const { planToPayload } = require("../director/plan_to_payload.cjs");
let failed = 0;
function check(name, ok, extra) {
  console.log((ok ? "PASS " : "FAIL ") + name + (extra ? " (" + extra + ")" : ""));
  if (!ok) failed++;
}
const near = (a, b) => Math.abs(a - b) < 0.002;

const plan = {
  schema: "director_plan/v1", video: { width: 1920, height: 1080 },
  scenes: [
    { scene_id: "a", source_kind: "real_observation", narration: { start: 0, end: 5 },
      asset: { type: "image", src: "https://example.com/a.jpg", known_native_size: { w: 3000, h: 2000 } },
      direction: { camera: { mode: "push_in", zoom_start: 1, zoom_end: 1.1, start_at: 0, end_at: 5 } } },
    { scene_id: "b", source_kind: "real_observation", narration: { start: 5, end: 10.5 },
      asset: { type: "image", src: "https://example.com/b.jpg", known_native_size: { w: 3000, h: 2000 } },
      direction: { camera: { mode: "push_in", zoom_start: 1, zoom_end: 1.1, start_at: 0, end_at: 5.5 } } },
    { scene_id: "c", source_kind: "real_observation", narration: { start: 10.5, end: 17 },
      asset: { type: "video", src: "https://example.com/c.mp4" },
      direction: { transition_in: { type: "cut" } } }
  ]
};

const res = planToPayload(plan);
check("conversion succeeded", res.errors.length === 0 && !!res.payload, res.errors.join("; "));
if (res.payload) {
  const c = res.payload.clips;
  // expected: s0 = 5 + 0.8/2, s1 = 5.5 + (0.8+0.04)/2, s2 = 6.5 + 0.04/2
  check("clip durations follow the formula", near(c[0].duration, 5.4) && near(c[1].duration, 5.92) && near(c[2].duration, 6.52),
    c.map((x) => x.duration).join(", "));

  // simulate the render.js timeline and compare transition midpoints with the sentence boundaries
  const d = [0, 0.8, 0.04];
  let E = c[0].duration; // end of segment 0 on the final timeline
  const mid1 = E - d[1] / 2;
  E = E + c[1].duration - d[1];
  const mid2 = E - d[2] / 2;
  const total = E + c[2].duration - d[2];
  check("transition 1 midpoint is on boundary 5.0", near(mid1, 5.0), "mid=" + mid1.toFixed(3));
  check("transition 2 midpoint is on boundary 10.5", near(mid2, 10.5), "mid=" + mid2.toFixed(3));
  check("final length equals narration end (17.0)", near(total, 17.0), "total=" + total.toFixed(3));

  check("camera times converted to clip-relative", near(c[1].direction.camera.start_at, 0.4) && near(c[1].direction.camera.end_at, 5.9),
    c[1].direction.camera.start_at + ".." + c[1].direction.camera.end_at);
  check("first clip camera is not shifted", near(c[0].direction.camera.start_at, 0));
  check("transitions flag and default set", res.payload.transitions === true && res.payload.transition_duration === 0.8);
}

const noSrc = JSON.parse(JSON.stringify(plan));
delete noSrc.scenes[1].asset.src;
const r2 = planToPayload(noSrc);
check("missing asset.src is rejected", r2.errors.length > 0 && r2.payload === null);

console.log(failed === 0 ? "ALL PASSED" : failed + " FAILED");
process.exit(failed === 0 ? 0 : 1);

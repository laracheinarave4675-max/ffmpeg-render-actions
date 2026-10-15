"use strict";
const { planToPayload } = require("../director/plan_to_payload.cjs");
let failed = 0;
const check = (n, ok, x) => { console.log((ok ? "PASS " : "FAIL ") + n + (x ? " (" + x + ")" : "")); if (!ok) failed++; };
const img = (id, k, s, e, extra) => ({
  scene_id: id, source_kind: k, narration: { start: s, end: e },
  asset: { type: "image", src: "https://example.com/" + id + ".jpg", known_native_size: { w: 3000, h: 2000 } },
  direction: Object.assign({ camera: { mode: "push_in", zoom_start: 1, zoom_end: 1.1, start_at: 0, end_at: e - s }, transition_in: { type: "cut" } }, k !== "real_observation" ? { overlays: [{ kind: "badge" }] } : {}, extra || {}),
});
const plan = (scenes) => ({ schema: "director_plan/v1", video: { width: 1920, height: 1080 }, scenes });

const base = planToPayload(plan([img("a", "real_observation", 0, 5), img("b", "real_observation", 5, 10)]));
check("base plan converts", base.errors.length === 0 && !!base.payload, base.errors.join("; "));
check("no fx keys without fx", base.payload && base.payload.sfx === undefined && base.payload.badges === undefined);

const r = planToPayload(plan([
  img("a", "real_observation", 0, 5),
  img("b", "illustration", 5, 10, { audio: { sfx: [{ src: "https://example.com/hit.mp3", at: 1.5, volume: 0.5 }, { src: 1, at: 1 }, { src: "https://example.com/late.mp3", at: 99 }] } }),
  img("c", "simulation", 10, 15),
]));
check("fx plan converts", r.errors.length === 0 && !!r.payload, r.errors.join("; "));
const p = r.payload || {};
check("2 badges (illustration + simulation)", Array.isArray(p.badges) && p.badges.length === 2 && p.badges[0].kind === "illustration" && p.badges[0].from === 5 && p.badges[0].to === 10 && p.badges[1].kind === "simulation");
check("1 valid sfx at scene start + 1.5s", Array.isArray(p.sfx) && p.sfx.length === 1 && Math.abs(p.sfx[0].at - 6.5) < 0.001 && p.sfx[0].volume === 0.5, JSON.stringify(p.sfx));
const c0 = (p.clips || [])[0];
check("fx mirrored into clips[0].direction.fx", !!(c0 && c0.direction && c0.direction.fx && c0.direction.fx.badges && c0.direction.fx.badges.length === 2 && c0.direction.fx.sfx && c0.direction.fx.sfx.length === 1));
const b0 = ((base.payload || {}).clips || [])[0];
check("no fx in clips without fx", !!b0 && !(b0.direction && b0.direction.fx));
process.exit(failed ? 1 : 0);

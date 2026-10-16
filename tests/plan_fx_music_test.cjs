"use strict";
const { addFx } = require("../director/plan_fx.cjs");
let failed = 0;
const check = (n, ok, x) => { console.log((ok ? "PASS " : "FAIL ") + n + (x ? " (" + x + ")" : "")); if (!ok) failed++; };
const sc = (id, s, e, audio) => ({ scene_id: id, source_kind: "real_observation", narration: { start: s, end: e }, direction: { audio } });
const plan = { scenes: [
  sc("a", 0, 10, { music_track: { src: "https://x/calm.mp3", gain: 0.8 } }),
  sc("b", 10, 20, { music_track: { src: "https://x/calm.mp3", gain: 0.8 } }),
  sc("c", 20, 30, { music_track: { src: "https://x/mystery.mp3", gain: 0.6, fade_in: 3 }, sfx: [{ src: "https://x/w.mp3", at: 1, len: 1.5, fade: 0.5 }] }),
] };
const res = { payload: { clips: [{ direction: {} }, { direction: {} }, { direction: {} }] }, warnings: [] };
addFx(plan, res);
const fx = res.payload.clips[0].direction.fx || {};
check("same track in adjacent scenes is merged", Array.isArray(fx.music) && fx.music.length === 2 && fx.music[0].from === 0 && fx.music[0].to === 20);
check("track change creates a new segment with its options", fx.music && fx.music[1].src.endsWith("mystery.mp3") && fx.music[1].from === 20 && fx.music[1].to === 30 && fx.music[1].gain === 0.6 && fx.music[1].fade_in === 3);
check("music_url is set from the first segment", res.payload.music_url === "https://x/calm.mp3");
check("sfx keeps len and fade", fx.sfx && fx.sfx[0].at === 21 && fx.sfx[0].len === 1.5 && fx.sfx[0].fade === 0.5);
const none = { payload: { clips: [{ direction: {} }] }, warnings: [] };
addFx({ scenes: [sc("z", 0, 5, undefined)] }, none);
check("no fx when the plan has none", !none.payload.clips[0].direction.fx && none.payload.music_url === undefined);
process.exit(failed ? 1 : 0);

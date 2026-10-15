#!/usr/bin/env node
"use strict";
const fs = require("fs");
const { validate } = require("./validate_plan.cjs");

const DEFAULT_D = 0.8; // must match render.js default transition_duration
const MIN_T = 0.04;    // must match render.js hard-cut duration (one frame at 25 fps)

function effDur(scene, isFirst) {
  if (isFirst) return 0;
  const t = scene.direction && scene.direction.transition_in;
  if (!t) return DEFAULT_D;
  if (t.type === "cut" || !(t.duration > 0)) return MIN_T;
  return t.duration;
}

// Converts a director_plan/v1 into render_video_github clips.
// Segment length = sentence length + (d_in + d_out) / 2, so the midpoint of every
// transition lands exactly on the sentence boundary.
function planToPayload(plan) {
  const errors = [];
  const warnings = [];
  const v = validate(plan);
  v.errors.forEach((e) => errors.push("plan: " + e));
  v.warnings.forEach((w) => warnings.push("plan: " + w));
  if (errors.length) return { payload: null, errors, warnings };

  const scenes = plan.scenes;
  const n = scenes.length;
  const d = scenes.map((s, i) => effDur(s, i === 0));
  const ends = scenes.map((s) => s.narration.end);
  if (scenes[0].narration.start > 0.05) warnings.push("first scene starts after 0s; video still starts at 0");

  const clips = scenes.map((s, j) => {
    const id = s.scene_id || "scene#" + j;
    const startB = j === 0 ? 0 : ends[j - 1];
    if (j > 0 && Math.abs(s.narration.start - startB) > 0.05) {
      warnings.push(id + ": gap or overlap between scenes (" + startB + " vs " + s.narration.start + ")");
    }
    const sceneLen = ends[j] - startB;
    const dNext = j + 1 < n ? d[j + 1] : 0;
    const dur = Math.round((sceneLen + (d[j] + dNext) / 2) * 1000) / 1000;
    if (sceneLen < 2 * MIN_T || dur <= 0) errors.push(id + ": scene too short");
    if (sceneLen < d[j] + dNext) warnings.push(id + ": scene shorter than its transitions");

    const a = s.asset || {};
    if (!a.src) errors.push(id + ": asset.src is missing (resolve the visual first)");
    if (a.type !== "image" && a.type !== "video") errors.push(id + ": asset.type must be image or video");

    const dir = {};
    const camIn = s.direction && s.direction.camera;
    if (camIn) {
      const shift = d[j] / 2; // scene start sits half a transition into the clip
      const cam = Object.assign({}, camIn);
      cam.start_at = Math.round((shift + (typeof camIn.start_at === "number" ? camIn.start_at : 0)) * 1000) / 1000;
      cam.end_at = Math.min(dur, Math.round((shift + (typeof camIn.end_at === "number" ? camIn.end_at : sceneLen)) * 1000) / 1000);
      dir.camera = cam;
    }
    if (s.direction && s.direction.transition_in) dir.transition_in = s.direction.transition_in;

    const clip = { type: a.type, src: a.src, duration: dur };
    if (a.keep_audio) clip.keep_audio = true;
    if (Object.keys(dir).length) clip.direction = dir;
    return clip;
  });

  if (errors.length) return { payload: null, errors, warnings };
  return { payload: { clips, transitions: true, transition_duration: DEFAULT_D }, errors, warnings };
}

module.exports = { planToPayload, effDur };

if (require.main === module) {
  const file = process.argv[2];
  if (!file) { console.error("usage: node plan_to_payload.cjs plan.json > payload.json"); process.exit(2); }
  const res = planToPayload(JSON.parse(fs.readFileSync(file, "utf8")));
  res.warnings.forEach((w) => console.error("WARN  " + w));
  res.errors.forEach((e) => console.error("ERROR " + e));
  if (res.errors.length) process.exit(1);
  console.log(JSON.stringify(res.payload, null, 2));
}

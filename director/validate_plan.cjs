#!/usr/bin/env node
"use strict";
const fs = require("fs");

const MODES = ["static", "push_in", "pull_out", "pan", "reveal"];
const EASING = ["linear", "ease_in", "ease_out", "ease_in_out"];
const TRANS = ["cut", "fade", "fadeblack", "dissolve", "zoomin"];
const KINDS = ["real_observation", "illustration", "simulation", "artist_concept"];

function inRange01(p) {
  return p && typeof p.x === "number" && typeof p.y === "number" &&
    p.x >= 0 && p.x <= 1 && p.y >= 0 && p.y <= 1;
}

function validate(plan) {
  const errors = [];
  const warnings = [];
  if (!plan || plan.schema !== "director_plan/v1") errors.push("schema must be director_plan/v1");
  const outW = (plan && plan.video && plan.video.width) || 1920;
  const scenes = plan && Array.isArray(plan.scenes) ? plan.scenes : [];
  if (!scenes.length) errors.push("scenes must be a non-empty array");
  let prevEnd = -Infinity;

  scenes.forEach((s, i) => {
    const id = s.scene_id || "scene#" + i;
    const err = (m) => errors.push(id + ": " + m);
    const warn = (m) => warnings.push(id + ": " + m);
    const d = s.direction || {};
    const cam = d.camera;

    if (!KINDS.includes(s.source_kind)) err("invalid source_kind");
    if (s.source_kind && s.source_kind !== "real_observation") {
      const hasBadge = (d.overlays || []).some((o) => o.kind === "badge");
      if (!hasBadge) err("non-real source requires a badge overlay (ILLUSTRATION)");
    }

    const n = s.narration;
    if (n) {
      if (!(n.start < n.end)) err("narration start must be < end");
      if (n.start < prevEnd - 1e-6) err("scenes must be in time order");
      prevEnd = n.end;
    }

    if (d.transition_in && !TRANS.includes(d.transition_in.type)) err("invalid transition type");

    if (cam) {
      if (!MODES.includes(cam.mode)) err("invalid camera mode");
      if (cam.easing && !EASING.includes(cam.easing)) err("invalid easing");
      if (cam.focus && !inRange01(cam.focus)) err("focus must be within 0..1");
      if (cam.pan_to && !inRange01(cam.pan_to)) err("pan_to must be within 0..1");
      if (cam.start_at != null && cam.end_at != null && !(cam.start_at < cam.end_at)) {
        err("camera start_at must be < end_at");
      }
      const zs = typeof cam.zoom_start === "number" ? cam.zoom_start : 1;
      const ze = typeof cam.zoom_end === "number" ? cam.zoom_end : 1;
      if (zs <= 0 || ze <= 0) err("zoom values must be > 0");
      const maxUp = typeof cam.max_upscale === "number" ? cam.max_upscale : 1.15;
      const top = Math.max(zs, ze);
      const native = s.asset && s.asset.known_native_size;
      if (top > maxUp) {
        if (native && native.w < outW) err("zoom " + top + " exceeds max_upscale " + maxUp + " on a small source");
        else warn("zoom " + top + " exceeds max_upscale " + maxUp + " (will be clamped)");
      }
    }
  });
  return { valid: errors.length === 0, errors, warnings };
}

module.exports = { validate };

if (require.main === module) {
  const file = process.argv[2];
  if (!file) { console.error("usage: node validate_plan.cjs plan.json"); process.exit(2); }
  const res = validate(JSON.parse(fs.readFileSync(file, "utf8")));
  res.errors.forEach((e) => console.log("ERROR  " + e));
  res.warnings.forEach((w) => console.log("WARN   " + w));
  console.log(res.valid ? "VALID" : "INVALID");
  process.exit(res.valid ? 0 : 1);
}

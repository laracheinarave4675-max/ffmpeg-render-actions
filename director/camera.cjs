"use strict";

function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
function num(v, f) { return typeof v === "number" && isFinite(v) ? v : f; }

// Resolve start/end zoom per mode, then clamp to [1, max_upscale].
function resolveZoom(cam) {
  const maxUp = num(cam.max_upscale, 1.15);
  let zs = 1, ze = 1;
  switch (cam.mode) {
    case "push_in":  zs = num(cam.zoom_start, 1.0);  ze = num(cam.zoom_end, 1.15); break;
    case "pull_out": zs = num(cam.zoom_start, 1.15); ze = num(cam.zoom_end, 1.0);  break;
    case "reveal":   zs = num(cam.zoom_start, 1.2);  ze = num(cam.zoom_end, 1.0);  break;
    case "pan":
      // pan travel = (1 - 1/zoom) of the frame, so keep a small minimum zoom
      zs = Math.max(num(cam.zoom_start, 1.1), 1.08);
      ze = Math.max(num(cam.zoom_end, zs), 1.08);
      break;
    default: break;
  }
  const czs = clamp(zs, 1, maxUp);
  const cze = clamp(ze, 1, maxUp);
  return { zs: czs, ze: cze, maxUp, clamped: czs !== zs || cze !== ze };
}

// ffmpeg expression for eased progress; t is an expression in 0..1.
function easeExpr(kind, t) {
  switch (kind) {
    case "ease_in": return "((" + t + ")*(" + t + "))";
    case "ease_out": return "(1-(1-(" + t + "))*(1-(" + t + ")))";
    case "ease_in_out": return "((" + t + ")*(" + t + ")*(3-2*(" + t + ")))";
    default: return "(" + t + ")";
  }
}

// Same easing in plain JS (used by tests).
function easeValue(kind, t) {
  switch (kind) {
    case "ease_in": return t * t;
    case "ease_out": return 1 - (1 - t) * (1 - t);
    case "ease_in_out": return t * t * (3 - 2 * t);
    default: return t;
  }
}

// Filter that fits any source to a 16:9 canvas (cover) at 2x output size,
// so zoompan has enough pixels and stays smooth.
function prefitFilter(outW, outH) {
  const W = outW * 2, H = outH * 2;
  return "scale=" + W + ":" + H + ":force_original_aspect_ratio=increase,crop=" + W + ":" + H;
}

// Returns a zoompan filter string, or null when no motion is needed.
// opts: { duration (sec), fps, outW, outH }
function buildZoompan(cam, opts) {
  if (!cam || cam.mode === "static") return null;
  if (cam.mode === "pan") return buildPanCrop(cam, opts);
  const fps = opts.fps || 30;
  const W = opts.outW || 1920, H = opts.outH || 1080;
  const dur = opts.duration;
  const frames = Math.max(1, Math.round(dur * fps));
  const s = num(cam.start_at, 0);
  const e = num(cam.end_at, dur);
  const span = Math.max(e - s, 0.001);
  const t = "clip((on/" + fps + "-" + s + ")/" + span + ",0,1)";
  const E = easeExpr(cam.easing || "ease_in_out", t);
  const z = resolveZoom(cam);
  const f = cam.focus || { x: 0.5, y: 0.5 };
  const p = cam.pan_to || f;
  const zExpr = z.zs + "+(" + z.ze + "-" + z.zs + ")*" + E;
  const fx = "(" + f.x + "+(" + p.x + "-" + f.x + ")*" + E + ")";
  const fy = "(" + f.y + "+(" + p.y + "-" + f.y + ")*" + E + ")";
  const x = "max(0,min(iw-iw/zoom," + fx + "*iw-iw/zoom/2))";
  const y = "max(0,min(ih-ih/zoom," + fy + "*ih-ih/zoom/2))";
  return "zoompan=z='" + zExpr + "':x='" + x + "':y='" + y + "':d=" + frames + ":s=" + W + "x" + H + ":fps=" + fps;
}

module.exports = { resolveZoom, easeValue, prefitFilter, buildZoompan };

// Smooth pan over the FULL image (no center pre-crop).
// Input arrives as a looped stream (-loop 1 -t dur), so NO loop/trim filter here.
// focus / pan_to are fractions (0..1) of the available travel range.
function buildPanCrop(cam, opts) {
  const fps = opts.fps || 30;
  const W = opts.outW || 1920, H = opts.outH || 1080;
  const W2 = W * 2, H2 = H * 2;
  const SW = Math.round(W2 * 1.15 / 2) * 2, SH = Math.round(H2 * 1.15 / 2) * 2;
  const dur = opts.duration;
  const st = num(cam.start_at, 0);
  const en = num(cam.end_at, dur);
  const span = Math.max(en - st, 0.001);
  const t = "clip((n/" + fps + "-" + st + ")/" + span + ",0,1)";
  const E = easeExpr(cam.easing || "ease_in_out", t);
  const f = cam.focus || { x: 0.5, y: 0.5 };
  const pt = cam.pan_to || f;
  const fx = "(" + f.x + "+(" + pt.x + "-" + f.x + ")*" + E + ")";
  const fy = "(" + f.y + "+(" + pt.y + "-" + f.y + ")*" + E + ")";
  return "scale=" + SW + ":" + SH + ":force_original_aspect_ratio=increase" +
    ",fps=" + fps +
    ",crop=" + W2 + ":" + H2 + ":x='(iw-" + W2 + ")*" + fx + "':y='(ih-" + H2 + ")*" + fy + "'" +
    ",scale=" + W + ":" + H;
}

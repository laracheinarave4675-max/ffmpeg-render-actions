// Derives payload.badges, payload.sfx and scene music segments from a director plan.
// No-op when the plan has none. Everything is mirrored into clips[0].direction.fx so it
// travels through the router inside "clips".
const BADGE_KINDS = ['illustration', 'simulation', 'artist_concept'];
const num = (v, d) => (typeof v === 'number' && isFinite(v) ? v : d);

function addFx(plan, res) {
  if (!plan || !Array.isArray(plan.scenes) || !res || !res.payload) return res;
  const badges = [];
  const sfx = [];
  const music = [];
  const warn = (m) => { if (Array.isArray(res.warnings)) res.warnings.push(m); };
  for (const s of plan.scenes) {
    const n = s && s.narration;
    if (!n || typeof n.start !== 'number' || typeof n.end !== 'number') continue;
    if (BADGE_KINDS.includes(s.source_kind)) {
      badges.push({ kind: s.source_kind, from: n.start, to: n.end });
    }
    const audio = s.direction && s.direction.audio;
    const list = audio && audio.sfx;
    if (Array.isArray(list)) {
      for (const e of list) {
        const rel = num(e && e.at, -1);
        if (!e || typeof e.src !== 'string' || rel < 0) { warn('scene ' + s.scene_id + ': invalid sfx entry skipped'); continue; }
        if (n.start + rel > n.end) { warn('scene ' + s.scene_id + ': sfx after scene end skipped'); continue; }
        const item = { src: e.src, at: +(n.start + rel).toFixed(3), volume: Math.min(1, Math.max(0, num(e.volume, 0.3))) };
        if (typeof e.len === 'number') item.len = e.len;
        if (typeof e.fade === 'number') item.fade = e.fade;
        sfx.push(item);
      }
    }
    const mt = audio && audio.music_track;
    if (mt && typeof mt.src === 'string') {
      const prev = music[music.length - 1];
      if (prev && prev.src === mt.src && Math.abs(prev.to - n.start) < 1e-6 && num(mt.gain, prev.gain) === prev.gain) {
        prev.to = n.end;                       // same track continues: merge, no crossfade
      } else {
        const seg = { src: mt.src, from: n.start, to: n.end };
        if (typeof mt.gain === 'number') seg.gain = mt.gain;
        if (typeof mt.fade_in === 'number') seg.fade_in = mt.fade_in;
        if (typeof mt.fade_out === 'number') seg.fade_out = mt.fade_out;
        music.push(seg);
      }
    }
  }
  if (badges.length) res.payload.badges = badges;
  if (sfx.length) res.payload.sfx = sfx;
  if (music.length) {
    if (!res.payload.music_url) res.payload.music_url = music[0].src;   // keeps the music branch of render.js active
  }
  if (badges.length || sfx.length || music.length) {
    const first = Array.isArray(res.payload.clips) && res.payload.clips[0];
    if (first) {
      first.direction = first.direction || {};
      first.direction.fx = Object.assign({}, badges.length ? { badges } : {}, sfx.length ? { sfx } : {}, music.length ? { music } : {});
    }
  }
  return res;
}
module.exports = { addFx, BADGE_KINDS };

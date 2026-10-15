// Derives payload.badges and payload.sfx from a director plan. No-op when the plan has none.
const BADGE_KINDS = ['illustration', 'simulation', 'artist_concept'];
const num = (v, d) => (typeof v === 'number' && isFinite(v) ? v : d);

function addFx(plan, res) {
  if (!plan || !Array.isArray(plan.scenes) || !res || !res.payload) return res;
  const badges = [];
  const sfx = [];
  const warn = (m) => { if (Array.isArray(res.warnings)) res.warnings.push(m); };
  for (const s of plan.scenes) {
    const n = s && s.narration;
    if (!n || typeof n.start !== 'number' || typeof n.end !== 'number') continue;
    if (BADGE_KINDS.includes(s.source_kind)) {
      badges.push({ kind: s.source_kind, from: n.start, to: n.end });
    }
    const list = s.direction && s.direction.audio && s.direction.audio.sfx;
    if (Array.isArray(list)) {
      for (const e of list) {
        const rel = num(e && e.at, -1);
        if (!e || typeof e.src !== 'string' || rel < 0) { warn('scene ' + s.scene_id + ': invalid sfx entry skipped'); continue; }
        if (n.start + rel > n.end) { warn('scene ' + s.scene_id + ': sfx after scene end skipped'); continue; }
        sfx.push({ src: e.src, at: +(n.start + rel).toFixed(3), volume: Math.min(1, Math.max(0, num(e.volume, 0.3))) });
      }
    }
  }
  if (badges.length) res.payload.badges = badges;
  if (sfx.length) res.payload.sfx = sfx;
  if (badges.length || sfx.length) {
    const first = Array.isArray(res.payload.clips) && res.payload.clips[0];
    if (first) {
      first.direction = first.direction || {};
      first.direction.fx = Object.assign({}, badges.length ? { badges } : {}, sfx.length ? { sfx } : {});
    }
  }
  return res;
}
module.exports = { addFx, BADGE_KINDS };

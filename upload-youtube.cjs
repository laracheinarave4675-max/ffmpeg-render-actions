'use strict';
const fs = require('fs');
const { Readable } = require('stream');
const { pipeline } = require('stream/promises');

const dec = (s) => JSON.parse(Buffer.from(s, 'base64').toString('utf8'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const P = dec(process.env.PAYLOAD_B64);
const YT = dec(process.env.YT_OAUTH_B64);
const GD = process.env.GDRIVE_OAUTH_B64 ? dec(process.env.GDRIVE_OAUTH_B64) : null;

async function token(c) {
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: c.client_id,
      client_secret: c.client_secret,
      refresh_token: c.refresh_token,
      grant_type: 'refresh_token',
    }),
  });
  const j = await r.json();
  if (!j.access_token) throw new Error('Token refresh failed: ' + JSON.stringify(j));
  return j.access_token;
}

async function download(id, dest, driveTok) {
  const tries = [];
  if (driveTok) {
    tries.push({
      url: `https://www.googleapis.com/drive/v3/files/${id}?alt=media&supportsAllDrives=true`,
      headers: { Authorization: 'Bearer ' + driveTok },
    });
  }
  tries.push({
    url: `https://drive.usercontent.google.com/download?id=${id}&export=download&confirm=t`,
    headers: {},
  });
  let last;
  for (const t of tries) {
    try {
      const r = await fetch(t.url, { headers: t.headers, redirect: 'follow' });
      const ct = r.headers.get('content-type') || '';
      if (!r.ok || ct.includes('text/html')) throw new Error('HTTP ' + r.status + ' ' + ct);
      await pipeline(Readable.fromWeb(r.body), fs.createWriteStream(dest));
      return fs.statSync(dest).size;
    } catch (e) {
      last = e;
      console.log('download attempt failed:', e.message);
    }
  }
  throw last;
}

async function initUpload(ytTok, size, meta) {
  const r = await fetch(
    'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
    {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + ytTok,
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Upload-Content-Length': String(size),
        'X-Upload-Content-Type': 'video/mp4',
      },
      body: JSON.stringify(meta),
    }
  );
  if (!r.ok) throw new Error('Init failed: HTTP ' + r.status + ' ' + (await r.text()).slice(0, 500));
  return r.headers.get('location');
}

async function sendFile(session, file, size) {
  const CHUNK = 32 * 1024 * 1024; // multiple of 256 KiB
  const fd = fs.openSync(file, 'r');
  const nextOffset = (r) => {
    const m = /bytes=0-(\d+)/.exec(r.headers.get('range') || '');
    return m ? Number(m[1]) + 1 : 0;
  };
  let offset = 0;
  let fails = 0;
  while (true) {
    const len = Math.min(CHUNK, size - offset);
    const buf = Buffer.alloc(len);
    fs.readSync(fd, buf, 0, len, offset);
    let r = null;
    try {
      r = await fetch(session, {
        method: 'PUT',
        headers: { 'Content-Range': `bytes ${offset}-${offset + len - 1}/${size}` },
        body: buf,
      });
    } catch (e) {
      console.log('chunk error:', e.message);
    }
    if (r && (r.status === 200 || r.status === 201)) {
      fs.closeSync(fd);
      return r.json();
    }
    if (r && r.status === 308) {
      offset = nextOffset(r);
      fails = 0;
      console.log('Uploaded MB:', Math.round(offset / 1048576));
      continue;
    }
    if (++fails > 8) throw new Error('Upload failed after retries, last status ' + (r ? r.status : 'network'));
    await sleep(3000 * fails);
    try {
      const q = await fetch(session, { method: 'PUT', headers: { 'Content-Range': `bytes */${size}` } });
      if (q.status === 200 || q.status === 201) {
        fs.closeSync(fd);
        return q.json();
      }
      if (q.status === 308) offset = nextOffset(q);
    } catch (e) {
      console.log('status query error:', e.message);
    }
  }
}

async function setThumbnail(ytTok, videoId, thumbId, driveTok) {
  const p = '/tmp/thumb.img';
  await download(thumbId, p, driveTok);
  const buf = fs.readFileSync(p);
  const isPng = buf[0] === 0x89 && buf[1] === 0x50;
  const r = await fetch(
    `https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=${videoId}&uploadType=media`,
    {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + ytTok, 'Content-Type': isPng ? 'image/png' : 'image/jpeg' },
      body: buf,
    }
  );
  if (!r.ok) throw new Error('Thumbnail HTTP ' + r.status + ' ' + (await r.text()).slice(0, 300));
}

async function main() {
  if (!P.file_id || !P.title) throw new Error('file_id and title are required');
  let driveTok = null;
  if (GD) {
    try {
      driveTok = await token(GD);
    } catch (e) {
      console.log('Drive token failed, using public link only');
    }
  }
  const ytTok = await token(YT);
  const video = '/tmp/video.mp4';
  const size = await download(P.file_id, video, driveTok);
  console.log('Downloaded MB:', Math.round(size / 1048576));
  if (size < 1000000) throw new Error('Downloaded file is too small (' + size + ' bytes), probably not the video');
  const lang = P.language || 'en';
  const meta = {
    snippet: {
      title: P.title,
      description: P.description || '',
      tags: P.tags || [],
      categoryId: P.category_id || '28',
      defaultLanguage: lang,
      defaultAudioLanguage: lang,
    },
    status: { privacyStatus: P.privacy_status || 'private' },
  };
  const session = await initUpload(ytTok, size, meta);
  if (!session) throw new Error('No upload session URL returned');
  const vid = await sendFile(session, video, size);
  const result = {
    success: true,
    videoId: vid.id,
    url: 'https://www.youtube.com/watch?v=' + vid.id,
    privacy: meta.status.privacyStatus,
    thumbnailSet: false,
  };
  if (P.thumbnail_file_id) {
    try {
      await setThumbnail(ytTok, vid.id, P.thumbnail_file_id, driveTok);
      result.thumbnailSet = true;
    } catch (e) {
      result.thumbnailError = String(e.message).slice(0, 300);
    }
  }
  return result;
}

(async () => {
  let out;
  try {
    out = await main();
  } catch (e) {
    out = { success: false, error: String((e && e.message) || e).slice(0, 800) };
    console.log('FAILED:', out.error);
  }
  fs.mkdirSync('results', { recursive: true });
  fs.writeFileSync('results/youtube-' + (process.env.GITHUB_RUN_ID || 'local') + '.json', JSON.stringify(out, null, 2));
  if (!out.success) process.exit(1);
  console.log('DONE', out.url);
})();

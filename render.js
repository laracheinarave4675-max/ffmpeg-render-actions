const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

function run(cmd) {
  return new Promise((resolve, reject) => {
    exec(cmd, { maxBuffer: 1024 * 1024 * 100 }, (err, stdout, stderr) => {
      if (err) reject(new Error(stderr || err.message));
      else resolve(stdout);
    });
  });
}

// Measure the real duration (seconds) of a media file with ffprobe
async function probeDuration(file) {
  const out = await run('ffprobe -v error -show_entries format=duration -of csv=p=0 "' + file + '"');
  const d = parseFloat(String(out).trim());
  if (!isFinite(d) || d <= 0) throw new Error('Could not probe duration of ' + file);
  return d;
}

// Ending: voice finishes first, music fades out, then the picture fades to black at the very end.
// Used only when a clip in the payload carries "end_fade" (true or {tail, music_fade, video_fade}).
async function mixWithEnding(o) {
  const V = await probeDuration(o.videoPath);
  const N = o.narrPath ? await probeDuration(o.narrPath) : 0;
  const T = Math.max(V, N + o.tail);
  const ext = Math.max(0, T - V);
  const AFc = 'aformat=sample_rates=44100:channel_layouts=stereo';
  const chains = [];
  let inputs = '-i "' + o.videoPath + '"';
  let idx = 1;
  const labels = [];
  chains.push('[0:v]' + (ext > 0.05 ? 'tpad=stop_mode=clone:stop_duration=' + ext.toFixed(3) + ',' : '') +
    'fade=t=out:st=' + Math.max(0, T - o.vFade).toFixed(3) + ':d=' + o.vFade + '[v]');
  if (o.narrPath) {
    inputs += ' -i "' + o.narrPath + '"';
    chains.push('[' + idx + ':a]' + AFc + ',apad=whole_dur=' + T.toFixed(3) + '[na]');
    labels.push('[na]');
    idx++;
  }
  if (o.musicPath) {
    inputs += ' -stream_loop -1 -i "' + o.musicPath + '"';
    const fadeSt = Math.max(0, T - 1 - o.mFade);
    chains.push('[' + idx + ':a]volume=' + o.musicVol + ',' + AFc + ',atrim=0:' + T.toFixed(3) + ',afade=t=out:st=' + fadeSt.toFixed(3) + ':d=' + o.mFade + '[music]');
    labels.push('[music]');
    idx++;
  }
  chains.push(labels.length === 2
    ? labels.join('') + 'amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[aout]'
    : labels[0] + 'anull[aout]');
  await run('ffmpeg ' + inputs + ' -filter_complex "' + chains.join(';') + '" -map "[v]" -map "[aout]" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -t ' + T.toFixed(3) + ' "' + o.outPath + '" -y');
  return T;
}

async function downloadFile(url, dest) {
  let res = await fetch(url);
  if (!res.ok) throw new Error('Failed to download ' + url + ': HTTP ' + res.status);
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('text/html') && url.includes('drive.google.com')) {
    const html = await res.text();
    const m = html.match(/confirm=([0-9A-Za-z_-]+)/) || html.match(/name="confirm"\s+value="([0-9A-Za-z_-]+)"/);
    const idMatch = url.match(/id=([0-9A-Za-z_-]+)/);
    if (m && idMatch) {
      const nextUrl = `https://drive.usercontent.google.com/download?id=${idMatch[1]}&export=download&confirm=${m[1]}`;
      res = await fetch(nextUrl);
      if (!res.ok) throw new Error('Failed to download (confirm) ' + nextUrl + ': HTTP ' + res.status);
    } else {
      throw new Error('Could not extract Drive confirm token for ' + url);
    }
  }
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(dest, buf);
}

// ---- Google OAuth (user account) auth ----
async function getAccessToken(oauthCreds) {
  const resp = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'client_id=' + encodeURIComponent(oauthCreds.client_id) +
      '&client_secret=' + encodeURIComponent(oauthCreds.client_secret) +
      '&refresh_token=' + encodeURIComponent(oauthCreds.refresh_token) +
      '&grant_type=refresh_token'
  });
  const json = await resp.json();
  if (!json.access_token) throw new Error('Failed to get access token: ' + JSON.stringify(json));
  return json.access_token;
}

async function findOrCreateFolder(accessToken, name) {
  const q = encodeURIComponent(`name='${name}' and mimeType='application/vnd.google-apps.folder' and trashed=false`);
  const listResp = await fetch(`https://www.googleapis.com/drive/v3/files?q=${q}&fields=files(id,name)`, {
    headers: { Authorization: 'Bearer ' + accessToken }
  });
  const listJson = await listResp.json();
  if (listJson.files && listJson.files.length > 0) return listJson.files[0].id;
  const createResp = await fetch('https://www.googleapis.com/drive/v3/files', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + accessToken, 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, mimeType: 'application/vnd.google-apps.folder' })
  });
  const createJson = await createResp.json();
  return createJson.id;
}

async function uploadToDrive(accessToken, filePath, filename, folderId) {
  const stat = fs.statSync(filePath);
  const fileSize = stat.size;
  const startResp = await fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + accessToken, 'Content-Type': 'application/json; charset=UTF-8' },
    body: JSON.stringify({ name: filename, parents: [folderId] })
  });
  if (startResp.status !== 200) throw new Error('start resumable failed: HTTP ' + startResp.status + ' ' + (await startResp.text()));
  const uploadUrl = startResp.headers.get('location');

  const CHUNK_SIZE = 48 * 1024 * 1024;
  let offset = 0;
  let lastResp = null;
  while (offset < fileSize) {
    const end = Math.min(offset + CHUNK_SIZE - 1, fileSize - 1);
    const chunkLen = end - offset + 1;
    const chunkBuf = Buffer.alloc(chunkLen);
    const fd = fs.openSync(filePath, 'r');
    fs.readSync(fd, chunkBuf, 0, chunkLen, offset);
    fs.closeSync(fd);
    lastResp = await fetch(uploadUrl, {
      method: 'PUT',
      headers: {
        'Content-Range': `bytes ${offset}-${end}/${fileSize}`,
        Authorization: 'Bearer ' + accessToken
      },
      body: chunkBuf
    });
    if (lastResp.status !== 200 && lastResp.status !== 201 && lastResp.status !== 308) {
      throw new Error('Chunk upload failed at offset ' + offset + ': HTTP ' + lastResp.status + ' ' + (await lastResp.text()));
    }
    offset = end + 1;
  }
  const finalJson = await lastResp.json();
  await fetch('https://www.googleapis.com/drive/v3/files/' + finalJson.id + '/permissions', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + accessToken, 'Content-Type': 'application/json' },
    body: JSON.stringify({ role: 'reader', type: 'anyone' })
  });
  return finalJson.id;
}

// ---- Main render pipeline ----
function escText(s) {
  return String(s).replace(/\\/g, '\\\\').replace(/:/g, '\\:').replace(/'/g, "\\'");
}

async function main() {
  const payload = JSON.parse(Buffer.from(process.env.PAYLOAD_B64, 'base64').toString('utf8'));
  const oauthCreds = JSON.parse(Buffer.from(process.env.GDRIVE_OAUTH_B64, 'base64').toString('utf8'));
  const clips = payload.clips || [];
  const workDir = path.join(process.cwd(), 'work');
  fs.mkdirSync(workDir, { recursive: true });
  const RES = '1920:1080';
  const kenBurns = payload.ken_burns !== false;
  const useTransitions = payload.transitions !== false && clips.length > 1;
  const transDur = payload.transition_duration || 0.8;
  const transType = payload.transition_type || 'fade';
  const segmentFiles = [];
  const segDurations = [];
  const srcPaths = [];

  // Ending settings: any clip with end_fade (true or an object) turns the ending on
  const endClip = clips.find(c => c && c.end_fade);
  const endCfg = endClip ? (typeof endClip.end_fade === 'object' ? endClip.end_fade : {}) : null;
  const endTail = endCfg && endCfg.tail !== undefined ? endCfg.tail : 4;
  const endVFade = endCfg && endCfg.video_fade ? endCfg.video_fade : 2;
  const endMFade = endCfg && endCfg.music_fade ? endCfg.music_fade : 3;

  // Builds one segment (used for every clip, and to lengthen the last one)
  async function makeSegment(clip, i, srcPath, segPath, dur) {
    if (clip.type === 'image') {
      const frames = Math.round(dur * 25);
      if (kenBurns) {
        const zoomDir = i % 2 === 0 ? 'min(zoom+0.0012,1.4)' : 'if(lte(zoom,1.0),1.4,max(1.0,zoom-0.0012))';
        await run('ffmpeg -loop 1 -i "' + srcPath + '" -vf "scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,zoompan=z=\'' + zoomDir + '\':d=' + frames + ':s=1920x1080:fps=25,format=yuv420p" -c:v libx264 -t ' + dur + ' -r 25 "' + segPath + '" -y');
      } else {
        await run('ffmpeg -loop 1 -i "' + srcPath + '" -c:v libx264 -t ' + dur + ' -pix_fmt yuv420p -vf "scale=' + RES + ':force_original_aspect_ratio=decrease,pad=' + RES + ':(ow-iw)/2:(oh-ih)/2" -r 25 "' + segPath + '" -y');
      }
    } else if (clip.keep_audio) {
      await run('ffmpeg -i "' + srcPath + '" -t ' + dur + ' -c:v libx264 -pix_fmt yuv420p -vf "scale=' + RES + ':force_original_aspect_ratio=decrease,pad=' + RES + ':(ow-iw)/2:(oh-ih)/2" -r 25 -c:a aac -b:a 192k -ar 44100 -ac 2 "' + segPath + '" -y');
    } else {
      await run('ffmpeg -stream_loop -1 -i "' + srcPath + '" -t ' + dur + ' -c:v libx264 -pix_fmt yuv420p -vf "scale=' + RES + ':force_original_aspect_ratio=decrease,pad=' + RES + ':(ow-iw)/2:(oh-ih)/2" -r 25 -an "' + segPath + '" -y');
    }
  }

  // Measure the narration first, so the picture always covers the whole voice
  let narrLen = 0;
  if (payload.narration_url) {
    const earlyNarr = path.join(workDir, 'narration_early.mp3');
    await downloadFile(payload.narration_url, earlyNarr);
    narrLen = await probeDuration(earlyNarr);
    console.log('Narration length ' + narrLen.toFixed(1) + 's');
  }

  for (let i = 0; i < clips.length; i++) {
    const clip = clips[i];
    const ext = clip.type === 'video' ? 'mp4' : 'png';
    const srcPath = path.join(workDir, 'src_' + i + '.' + ext);
    console.log('Downloading clip ' + i + '...');
    await downloadFile(clip.src, srcPath);
    srcPaths.push(srcPath);
    const segPath = path.join(workDir, 'seg_' + i + '.mp4');
    // If no duration is given, use the real length of the source video
    const dur = clip.duration || (clip.type === 'video' ? await probeDuration(srcPath) : 5);
    await makeSegment(clip, i, srcPath, segPath, dur);
    segmentFiles.push(segPath);
    // Always use the measured duration of the finished segment so transition offsets are exact
    const segDur = await probeDuration(segPath);
    segDurations.push(segDur);
    console.log('Segment ' + (i + 1) + '/' + clips.length + ' done (' + segDur.toFixed(2) + 's)');
  }

  // If the picture is shorter than the voice (+ ending tail), lengthen the last clip with moving footage:
  // the voice is never cut and the picture never freezes.
  if (narrLen > 0 && clips.length > 0) {
    const target = narrLen + (endCfg ? endTail : 0);
    const total = segDurations.reduce((x, y) => x + y, 0) - (useTransitions ? (clips.length - 1) * transDur : 0);
    const li = clips.length - 1;
    const lastClip = clips[li];
    if (total < target - 0.05 && !(lastClip.type === 'video' && lastClip.keep_audio)) {
      const extra = target - total + 0.2;
      console.log('Lengthening the last clip by ' + extra.toFixed(1) + 's to cover the narration');
      await makeSegment(lastClip, li, srcPaths[li], segmentFiles[li], segDurations[li] + extra);
      segDurations[li] = await probeDuration(segmentFiles[li]);
    }
  }

  const concatPath = path.join(workDir, 'concat.mp4');
  console.log('Merging transitions...');
  const hasAudioFlags = clips.map(c => c.type === 'video' && !!c.keep_audio);
  const allHaveAudio = hasAudioFlags.length > 0 && hasAudioFlags.every(Boolean);

  if (useTransitions) {
    const inputsArg = segmentFiles.map(f => '-i "' + f + '"').join(' ');
    let filterChain = '';
    let prevLabel = '0:v';
    let cum = segDurations[0];
    for (let i = 1; i < segmentFiles.length; i++) {
      const offset = Math.max(0, cum - transDur);
      const outLabel = i === segmentFiles.length - 1 ? 'vout' : 'v' + i;
      filterChain += '[' + prevLabel + '][' + i + ':v]xfade=transition=' + transType + ':duration=' + transDur + ':offset=' + offset.toFixed(3) + '[' + outLabel + '];';
      cum = cum + segDurations[i] - transDur;
      prevLabel = outLabel;
    }
    if (allHaveAudio) {
      // Cross-fade the audio with the same overlap as the video so sound stays in sync
      let aPrev = '0:a';
      for (let i = 1; i < segmentFiles.length; i++) {
        const aOut = i === segmentFiles.length - 1 ? 'aout' : 'a' + i;
        filterChain += '[' + aPrev + '][' + i + ':a]acrossfade=d=' + transDur + ':c1=tri:c2=tri[' + aOut + '];';
        aPrev = aOut;
      }
    }
    filterChain = filterChain.slice(0, -1);
    const mapArgs = allHaveAudio
      ? '-map "[vout]" -map "[aout]" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k'
      : '-map "[vout]" -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p';
    await run('ffmpeg ' + inputsArg + ' -filter_complex "' + filterChain + '" ' + mapArgs + ' "' + concatPath + '" -y');
  } else {
    const listPath = path.join(workDir, 'list.txt');
    fs.writeFileSync(listPath, segmentFiles.map(f => "file '" + f + "'").join('\n'));
    await run('ffmpeg -f concat -safe 0 -i "' + listPath + '" -c copy "' + concatPath + '" -y');
  }

  let videoPath = concatPath;
  const overlays = payload.text_overlays || [];
  if (overlays.length > 0) {
    console.log('Adding text overlays...');
    const FONTS = { anton: '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' };
    const drawFilters = overlays.map(function (ov) {
      const text = escText(ov.text);
      const fontSize = ov.font_size || 70;
      const color = ov.color || 'white';
      const strokeColor = ov.stroke_color || 'black';
      const strokeWidth = ov.stroke_width || 6;
      const start = ov.start || 0;
      const dur = ov.duration || 3;
      const pos = ov.position || 'bottom';
      const fadeDur = ov.fade_duration !== undefined ? ov.fade_duration : 0.35;
      const fontFile = FONTS.anton;
      let yExpr = 'h-150';
      if (pos === 'top') yExpr = '100';
      if (pos === 'center') yExpr = '(h-text_h)/2';
      const S = start, D = dur, F = fadeDur;
      const alphaExpr = 'if(lt(t,' + S + '+' + F + '),(t-' + S + ')/' + F + ',if(lt(t,' + S + '+' + D + '-' + F + '),1,if(lt(t,' + S + '+' + D + '),(' + S + '+' + D + '-t)/' + F + ',0)))';
      return "drawtext=fontfile='" + fontFile + "':text='" + text + "':fontcolor=" + color + ':fontsize=' + fontSize + ':borderw=' + strokeWidth + ':bordercolor=' + strokeColor + ":x=(w-text_w)/2:y=" + yExpr + ":alpha='" + alphaExpr + "':enable='between(t," + start + ',' + (start + dur) + ")'";
    }).join(',');
    const textPath = path.join(workDir, 'text_overlay.mp4');
    await run('ffmpeg -i "' + videoPath + '" -vf "' + drawFilters + '" -c:v libx264 -pix_fmt yuv420p -c:a copy "' + textPath + '" -y');
    videoPath = textPath;
  }

  let finalPath = videoPath;
  const AF = 'aformat=sample_rates=44100:channel_layouts=stereo';
  console.log('Mixing audio...');

  if (endCfg && (payload.narration_url || payload.music_url)) {
    let narrPath = null;
    let musicPath = null;
    if (payload.narration_url) {
      narrPath = path.join(workDir, 'narration.mp3');
      await downloadFile(payload.narration_url, narrPath);
    }
    if (payload.music_url) {
      musicPath = path.join(workDir, 'music.mp3');
      await downloadFile(payload.music_url, musicPath);
    }
    finalPath = path.join(workDir, 'final.mp4');
    const T = await mixWithEnding({
      videoPath, narrPath, musicPath,
      musicVol: payload.music_volume || (narrPath ? 0.15 : 0.3),
      outPath: finalPath, tail: endTail, vFade: endVFade, mFade: endMFade
    });
    console.log('Ending applied, total length ' + T.toFixed(1) + 's');
  } else if (endCfg && !payload.narration_url && !payload.music_url) {
    // Finished parts (sound already inside): the sound simply ends, the picture keeps moving for the tail, then fades to black
    const V = await probeDuration(videoPath);
    const T = V + endTail;
    finalPath = path.join(workDir, 'final.mp4');
    const startT = Math.max(0, V - endTail);
    const vChain = '[0:v]split=2[a][b];[b]trim=start=' + startT.toFixed(3) + ',setpts=PTS-STARTPTS,reverse,setpts=PTS-STARTPTS[r];[a][r]concat=n=2:v=1:a=0,fade=t=out:st=' + Math.max(0, T - endVFade).toFixed(3) + ':d=' + endVFade + '[v]';
    const aChain = allHaveAudio ? ';[0:a]apad=whole_dur=' + T.toFixed(3) + '[a]' : '';
    const maps = allHaveAudio ? '-map "[v]" -map "[a]" -c:a aac -b:a 192k' : '-map "[v]"';
    await run('ffmpeg -i "' + videoPath + '" -filter_complex "' + vChain + aChain + '" ' + maps + ' -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -t ' + T.toFixed(3) + ' "' + finalPath + '" -y');
    console.log('Ending applied (voice ends, picture keeps moving ' + endTail + 's then fades), total length ' + T.toFixed(1) + 's');
  } else if (payload.narration_url && payload.music_url) {
    const narrPath = path.join(workDir, 'narration.mp3');
    const musicPath = path.join(workDir, 'music.mp3');
    await downloadFile(payload.narration_url, narrPath);
    await downloadFile(payload.music_url, musicPath);
    finalPath = path.join(workDir, 'final.mp4');
    const musicVol = payload.music_volume || 0.15;
    const filter = '[1:a]' + AF + '[na];[2:a]volume=' + musicVol + ',' + AF + '[music];[na][music]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[aout]';
    await run('ffmpeg -i "' + videoPath + '" -i "' + narrPath + '" -stream_loop -1 -i "' + musicPath + '" -filter_complex "' + filter + '" -map 0:v:0 -map "[aout]" -c:v copy -c:a aac -b:a 192k -shortest "' + finalPath + '" -y');
  } else if (payload.narration_url) {
    const narrPath = path.join(workDir, 'narration.mp3');
    await downloadFile(payload.narration_url, narrPath);
    finalPath = path.join(workDir, 'final.mp4');
    await run('ffmpeg -i "' + videoPath + '" -i "' + narrPath + '" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "' + finalPath + '" -y');
  } else if (payload.music_url) {
    const musicPath = path.join(workDir, 'music.mp3');
    await downloadFile(payload.music_url, musicPath);
    finalPath = path.join(workDir, 'final.mp4');
    const musicVol = payload.music_volume || 0.3;
    await run('ffmpeg -i "' + videoPath + '" -stream_loop -1 -i "' + musicPath + '" -filter_complex "[1:a]volume=' + musicVol + ',' + AF + '[aout]" -map 0:v:0 -map "[aout]" -c:v copy -c:a aac -b:a 192k -shortest "' + finalPath + '" -y');
  }

  console.log('Render complete: ' + finalPath + ' (' + Math.round(fs.statSync(finalPath).size / 1024 / 1024) + ' MB)');

  console.log('Authenticating with Google Drive...');
  const accessToken = await getAccessToken(oauthCreds);
  const folderId = await findOrCreateFolder(accessToken, 'StarVideoProject');
  const filename = payload.filename || ('render_' + Date.now() + '.mp4');
  console.log('Uploading to Drive as ' + filename + '...');
  const fileId = await uploadToDrive(accessToken, finalPath, filename, folderId);
  console.log('DRIVE_FILE_ID=' + fileId);

  const summary = { success: true, fileId, filename, sizeMB: Math.round(fs.statSync(finalPath).size / 1024 / 1024) };
  fs.mkdirSync('results', { recursive: true });
  fs.writeFileSync(path.join('results', (process.env.GITHUB_RUN_ID || 'local') + '.json'), JSON.stringify(summary, null, 2));
  if (process.env.GITHUB_OUTPUT) {
    fs.appendFileSync(process.env.GITHUB_OUTPUT, 'file_id=' + fileId + '\n');
  }
}

main().catch(err => {
  console.error('RENDER_FAILED: ' + (err.stack || err.message || err));
  const summary = { success: false, error: String(err.message || err) };
  fs.mkdirSync('results', { recursive: true });
  fs.writeFileSync(path.join('results', (process.env.GITHUB_RUN_ID || 'local') + '.json'), JSON.stringify(summary, null, 2));
  process.exit(1);
});

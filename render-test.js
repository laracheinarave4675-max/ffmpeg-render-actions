'use strict';

/**
 * Documentary Render Test
 * Node.js 20 + FFmpeg + FFprobe
 * This test file does not replace render.js.
 */

const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');

const execFileAsync = promisify(execFile);

const WIDTH = 1920;
const HEIGHT = 1080;
const FPS = 25;

function log(message) {
  console.log(`[render-test] ${message}`);
}

function validatePayload() {
  const encoded = process.env.PAYLOAD_B64;

  if (!encoded) {
    throw new Error('PAYLOAD_B64 environment variable is missing.');
  }

  let payload;

  try {
    payload = JSON.parse(
      Buffer.from(encoded, 'base64').toString('utf8')
    );
  } catch {
    throw new Error('PAYLOAD_B64 must contain valid Base64-encoded JSON.');
  }

  if (!payload || !Array.isArray(payload.clips)) {
    throw new Error('Payload must contain a clips array.');
  }

  if (payload.clips.length === 0) {
    throw new Error('The clips array is empty.');
  }

  for (let i = 0; i < payload.clips.length; i++) {
    const clip = payload.clips[i];

    if (!clip || typeof clip !== 'object') {
      throw new Error(`Clip ${i + 1} is invalid.`);
    }

    const url =
      clip.url ||
      clip.src ||
      clip.video_url ||
      clip.image_url ||
      clip.download_url ||
      clip.asset_url;

    if (typeof url !== 'string' || !url.trim()) {
      throw new Error(`Clip ${i + 1} has no supported URL.`);
    }

    const duration = Number(
      clip.duration ?? clip.seconds ?? clip.length ?? 5
    );

    if (!Number.isFinite(duration) || duration <= 0 || duration > 3600) {
      throw new Error(`Clip ${i + 1} has an invalid duration.`);
    }
  }

  return payload;
}

async function execute(command, args, timeout = 60000) {
  try {
    const result = await execFileAsync(command, args, {
      timeout,
      maxBuffer: 20 * 1024 * 1024,
      windowsHide: true
    });

    return result.stdout || '';
  } catch (error) {
    const details = String(error.stderr || error.message).slice(-4000);
    throw new Error(`${command} failed: ${details}`);
  }
}

async function checkTools() {
  await execute('ffmpeg', ['-version']);
  await execute('ffprobe', ['-version']);
  log('FFmpeg and FFprobe are available.');
}

function getUrl(clip) {
  return (
    clip.url ||
    clip.src ||
    clip.video_url ||
    clip.image_url ||
    clip.download_url ||
    clip.asset_url
  );
}

function getType(clip, url) {
  const type = String(clip.type || '').toLowerCase();

  if (['image', 'photo', 'still'].includes(type)) {
    return 'image';
  }

  if (['video', 'footage'].includes(type)) {
    return 'video';
  }

  try {
    const ext = path.extname(new URL(url).pathname).toLowerCase();

    if (['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff'].includes(ext)) {
      return 'image';
    }
  } catch {
    // Fall back to video when the URL does not reveal its file extension.
  }

  return 'video';
}

async function downloadAsset(url, destination) {
  const response = await fetch(url, {
    redirect: 'follow',
    signal: AbortSignal.timeout(120000)
  });

  if (!response.ok) {
    throw new Error(`Download failed with HTTP ${response.status}: ${url}`);
  }

  const contentType = String(
    response.headers.get('content-type') || ''
  ).toLowerCase();

  if (contentType.includes('text/html')) {
    throw new Error(
      `The URL returned an HTML page instead of a media file: ${url}`
    );
  }

  if (!response.body) {
    throw new Error(`The download has no response body: ${url}`);
  }

  const bytes = Buffer.from(await response.arrayBuffer());

  if (bytes.length === 0) {
    throw new Error(`The downloaded file is empty: ${url}`);
  }

  if (bytes.length > 2 * 1024 * 1024 * 1024) {
    throw new Error('The downloaded file exceeds the 2 GB test limit.');
  }

  fs.writeFileSync(destination, bytes);
  return destination;
}

async function getDuration(file) {
  const output = await execute('ffprobe', [
    '-v', 'error',
    '-show_entries', 'format=duration',
    '-of', 'default=noprint_wrappers=1:nokey=1',
    file
  ]);

  const duration = Number(output.trim());

  if (!Number.isFinite(duration) || duration <= 0) {
    throw new Error(`Could not read media duration: ${file}`);
  }

  return duration;
}

async function renderClip(clip, index, workDir) {
  const url = getUrl(clip);
  const type = getType(clip, url);

  const input = path.join(
    workDir,
    `input_${String(index + 1).padStart(3, '0')}${type === 'image' ? '.img' : '.media'}`
  );

  const output = path.join(
    workDir,
    `segment_${String(index + 1).padStart(3, '0')}.mp4`
  );

  const requestedDuration = Number(
    clip.duration ?? clip.seconds ?? clip.length ?? 5
  );

  await downloadAsset(url, input);

  const duration = type === 'image'
    ? requestedDuration
    : Math.min(requestedDuration, await getDuration(input));

  const filters = [
    `scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=decrease`,
    `pad=${WIDTH}:${HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black`,
    'setsar=1',
    `fps=${FPS}`,
    'format=yuv420p'
  ].join(',');

  const args = ['-hide_banner', '-loglevel', 'error', '-y'];

  if (type === 'image') {
    args.push('-loop', '1', '-framerate', String(FPS), '-i', input);
  } else {
    args.push('-i', input);
  }

  args.push(
    '-t', duration.toFixed(3),
    '-vf', filters,
    '-an',
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-crf', '23',
    '-pix_fmt', 'yuv420p',
    '-r', String(FPS),
    '-movflags', '+faststart',
    output
  );

  await execute('ffmpeg', args, 10 * 60 * 1000);

  const renderedDuration = await getDuration(output);

  log(
    `Clip ${index + 1}/${' ' + index + 1}: ` +
    `${type}, ${renderedDuration.toFixed(2)} seconds`
  );

  return output;
}

async function main() {
  const workDir = fs.mkdtempSync(
    path.join(os.tmpdir(), 'documentary-render-test-')
  );

  try {
    await checkTools();

    const payload = validatePayload();

    log(`Validated ${payload.clips.length} clips.`);

    const renderedSegments = [];

    for (let i = 0; i < payload.clips.length; i++) {
      log(`Processing clip ${i + 1} of ${payload.clips.length}.`);

      renderedSegments.push(
        await renderClip(payload.clips[i], i, workDir)
      );
    }

    const listFile = path.join(workDir, 'concat.txt');

    const listContents = renderedSegments
      .map(file => `file '${file.replace(/'/g, "'\\''")}'`)
      .join('\n');

    fs.writeFileSync(listFile, `${listContents}\n`, 'utf8');

    const outputFile = path.join(workDir, 'render-test.mp4');

    await execute('ffmpeg', [
      '-hide_banner',
      '-loglevel', 'error',
      '-y',
      '-f', 'concat',
      '-safe', '0',
      '-i', listFile,
      '-c:v', 'libx264',
      '-preset', 'ultrafast',
      '-crf', '23',
      '-pix_fmt', 'yuv420p',
      '-r', String(FPS),
      '-an',
      '-movflags', '+faststart',
      outputFile
    ], 20 * 60 * 1000);

    const duration = await getDuration(outputFile);

    log(`TEST PASSED. Rendered duration: ${duration.toFixed(2)} seconds.`);
    log(`Test output: ${outputFile}`);
    log('The original render.js and Google Drive files were not modified.');
  } finally {
    fs.rmSync(workDir, { recursive: true, force: true });
  }
}

main().catch(error => {
  console.error('[render-test] TEST FAILED:', error.message);
  process.exitCode = 1;
});

'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFile } = require('node:child_process');
const { promisify } = require('node:util');

const execFileAsync = promisify(execFile);

const WIDTH = 1920;
const HEIGHT = 1080;
const FPS = 25;

const NASA_IMAGES = [
  {
    url: 'https://d2pn8kiwq2w21t.cloudfront.net/original_images/jpegPIA07230.jpg',
    title: 'AN ALIEN WORLD',
    duration: 16
  },
  {
    url: 'https://d2pn8kiwq2w21t.cloudfront.net/original_images/jpegPIA07230.jpg',
    title: 'A LANDSCAPE NEVER SEEN BEFORE',
    duration: 16
  },
  {
    url: 'https://d2pn8kiwq2w21t.cloudfront.net/original_images/jpegPIA07230.jpg',
    title: 'THE FINAL DESCENT',
    duration: 16
  },
  {
    url: 'https://d2pn8kiwq2w21t.cloudfront.net/original_images/jpegPIA07230.jpg',
    title: 'HUYGENS ON TITAN',
    duration: 16
  }
];

const NARRATION = [
  {
    text: 'Imagine descending through the thick orange atmosphere of a world almost one and a half billion kilometers from the Sun.',
    title: 'A WORLD HIDDEN BENEATH THE HAZE'
  },
  {
    text: 'On January fourteenth, two thousand five, the European Space Agency’s Huygens probe reached the surface of Saturn’s largest moon, Titan.',
    title: 'JANUARY 14, 2005'
  },
  {
    text: 'As it descended, its cameras recorded landscapes shaped by processes unlike those on Earth. Dark channels crossed brighter terrain, hinting at a world where methane may fall as rain.',
    title: 'RIVERS OF ANOTHER KIND'
  },
  {
    text: 'These were not imagined alien landscapes. They were observations returned by a robotic explorer, sent across the Solar System to reveal a place humanity had never seen from the ground.',
    title: 'A NEW WORLD REVEALED'
  }
];

async function run(command, args, timeout = 180000) {
  try {
    return await execFileAsync(command, args, {
      timeout,
      maxBuffer: 20 * 1024 * 1024
    });
  } catch (error) {
    throw new Error(
      `${command} failed: ${String(error.stderr || error.message).slice(-4000)}`
    );
  }
}

async function download(url, destination) {
  const response = await fetch(url, {
    signal: AbortSignal.timeout(90000),
    headers: {
      'User-Agent': 'DocumentaryRenderTest/1.0'
    }
  });

  if (!response.ok) {
    throw new Error(`Image download failed: HTTP ${response.status} (${url})`);
  }

  const contentType = (response.headers.get('content-type') || '').toLowerCase();

  if (!contentType.startsWith('image/')) {
    throw new Error(`URL did not return an image: ${url}`);
  }

  const bytes = Buffer.from(await response.arrayBuffer());

  if (bytes.length < 1000) {
    throw new Error(`Downloaded image is unexpectedly small: ${url}`);
  }

  fs.writeFileSync(destination, bytes);
}

async function main() {
  const outDir = path.join(process.cwd(), 'documentary-output');
  const assetsDir = path.join(outDir, 'assets');

  fs.mkdirSync(assetsDir, { recursive: true });

  const narrationText = NARRATION.map(item => item.text).join('\n\n');

  fs.writeFileSync(
    path.join(assetsDir, 'narration.txt'),
    narrationText,
    'utf8'
  );

  console.log('Downloading original Titan imagery...');

  const imagePaths = [];

  for (let i = 0; i < NASA_IMAGES.length; i++) {
    const destination = path.join(assetsDir, `image-${i + 1}.jpg`);

    await download(NASA_IMAGES[i].url, destination);
    imagePaths.push(destination);

    console.log(`Downloaded image ${i + 1}/${NASA_IMAGES.length}`);
  }

  console.log('Generating English narration...');

  await run('espeak-ng', [
    '-v', 'en-us',
    '-s', '138',
    '-p', '43',
    '-a', '155',
    '-w', path.join(assetsDir, 'narration.wav'),
    narrationText
  ]);

  const narrationPath = path.join(assetsDir, 'narration.wav');

  const { stdout } = await run('ffprobe', [
    '-v', 'error',
    '-show_entries', 'format=duration',
    '-of', 'default=noprint_wrappers=1:nokey=1',
    narrationPath
  ]);

  const narrationDuration = Number(stdout.trim());

  if (!Number.isFinite(narrationDuration) || narrationDuration <= 0) {
    throw new Error('Could not determine narration duration.');
  }

  console.log(`Narration duration: ${narrationDuration.toFixed(1)} seconds`);

  const segmentDuration = narrationDuration / imagePaths.length;
  const segmentPaths = [];

  for (let i = 0; i < imagePaths.length; i++) {
    const output = path.join(assetsDir, `scene-${i + 1}.mp4`);

    const title = NASA_IMAGES[i].title.replace(/'/g, '');

    const startZoom = i % 2 === 0 ? 1.0 : 1.12;
    const endZoom = i % 2 === 0 ? 1.12 : 1.0;

    const frames = Math.ceil(segmentDuration * FPS);

    const zoomFilter =
      `scale=2200:1238:force_original_aspect_ratio=increase,` +
      `crop=1920:1080,` +
      `zoompan=z='${startZoom}+(${endZoom - startZoom})*on/${frames}':` +
      `x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':` +
      `d=${frames}:s=1920x1080:fps=${FPS},` +
      `drawbox=x=0:y=0:w=iw:h=150:color=black@0.42:t=fill,` +
      `drawtext=text='${title}':fontcolor=white:fontsize=42:` +
      `x=90:y=55:borderw=2:bordercolor=black@0.6,` +
      `fade=t=in:st=0:d=0.7,` +
      `fade=t=out:st=${Math.max(0, segmentDuration - 0.7)}:d=0.7,` +
      `format=yuv420p`;

    await run('ffmpeg', [
      '-hide_banner',
      '-loglevel', 'error',
      '-y',
      '-loop', '1',
      '-framerate', String(FPS),
      '-i', imagePaths[i],
      '-vf', zoomFilter,
      '-t', segmentDuration.toFixed(3),
      '-an',
      '-c:v', 'libx264',
      '-preset', 'ultrafast',
      '-crf', '20',
      '-pix_fmt', 'yuv420p',
      '-r', String(FPS),
      output
    ], 300000);

    segmentPaths.push(output);
    console.log(`Rendered scene ${i + 1}/${imagePaths.length}`);
  }

  const concatFile = path.join(assetsDir, 'concat.txt');

  fs.writeFileSync(
    concatFile,
    segmentPaths.map(file => `file '${file}'`).join('\n') + '\n',
    'utf8'
  );

  const silentVideo = path.join(assetsDir, 'silent-video.mp4');

  await run('ffmpeg', [
    '-hide_banner',
    '-loglevel', 'error',
    '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', concatFile,
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-crf', '20',
    '-pix_fmt', 'yuv420p',
    '-r', String(FPS),
    '-an',
    silentVideo
  ], 600000);

  const finalVideo = path.join(outDir, 'huygens-titan-pilot.mp4');

  console.log('Mixing narration and cinematic ambient sound...');

  await run('ffmpeg', [
    '-hide_banner',
    '-loglevel', 'error',
    '-y',
    '-i', silentVideo,
    '-i', narrationPath,
    '-f', 'lavfi',
    '-i', 'anoisesrc=color=brown:amplitude=0.025:sample_rate=48000',
    '-filter_complex',
    '[1:a]aresample=48000,volume=1.0[voice];' +
    '[2:a]lowpass=f=180,volume=0.12[ambience];' +
    '[voice][ambience]amix=inputs=2:duration=first:dropout_transition=2,' +
    'alimiter=limit=0.95[aout]',
    '-map', '0:v:0',
    '-map', '[aout]',
    '-c:v', 'copy',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-ar', '48000',
    '-shortest',
    '-movflags', '+faststart',
    finalVideo
  ], 300000);

  const finalInfo = await run('ffprobe', [
    '-v', 'error',
    '-show_entries', 'format=duration:stream=codec_type,width,height',
    '-of', 'json',
    finalVideo
  ]);

  const metadata = JSON.parse(finalInfo.stdout);

  if (!metadata.streams.some(stream => stream.codec_type === 'audio')) {
    throw new Error('Final video has no audio stream.');
  }

  fs.writeFileSync(
    path.join(outDir, 'credits.txt'),
    [
      'Documentary pilot: Huygens and Titan',
      '',
      'NASA/JPL/ESA/University of Arizona imagery:',
      NASA_IMAGES.map(item => item.url).join('\n'),
      '',
      'Narration: generated with eSpeak NG.',
      'Ambient sound: synthesized for this pilot.'
    ].join('\n'),
    'utf8'
  );

  console.log('SUCCESS');
  console.log(`Video: ${finalVideo}`);
  console.log(`Duration: ${metadata.format.duration} seconds`);
  console.log('Resolution: 1920x1080');
}

main().catch(error => {
  console.error('DOCUMENTARY PILOT FAILED:', error.stack || error.message);
  process.exitCode = 1;
});

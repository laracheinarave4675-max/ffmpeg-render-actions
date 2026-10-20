const fs = require("fs");
const path = require("path");
const { execFile } = require("child_process");
const { promisify } = require("util");

const execFileAsync = promisify(execFile);

const OUT = path.join(process.cwd(), "documentary-output");
const ASSETS = path.join(OUT, "assets");
const SCENES = path.join(OUT, "scenes");

const WIDTH = 1920;
const HEIGHT = 1080;
const FPS = 25;

const scenes = [
  {
    title: "A WORLD HIDDEN BENEATH THE HAZE",
    image: "https://d2pn8kiwq2w21t.cloudfront.net/original_images/jpegPIA07230.jpg",
    narration:
      "Imagine landing on a world where rivers may flow, rain may fall, and the ground is made of frozen water and organic material. This is Titan, Saturn's largest moon, a place that looks strangely familiar, yet is unlike anywhere on Earth."
  },
  {
    title: "THE DESCENT INTO TITAN",
    image: "https://photojournal.jpl.nasa.gov/jpeg/PIA06438.jpg",
    narration:
      "On January fourteenth, two thousand and five, the European Space Agency's Huygens probe descended through Titan's thick orange atmosphere. Suspended beneath a parachute, it became the first spacecraft to land on the surface of a world in the outer Solar System."
  },
  {
    title: "A LANDSCAPE SHAPED BY METHANE",
    image: "https://photojournal.jpl.nasa.gov/jpeg/PIA06439.jpg",
    narration:
      "During its descent, Huygens photographed a landscape cut by dark channels. Scientists believe liquid methane may have carved some of these features, in a cycle of clouds, rainfall, and runoff that resembles Earth's water cycle, but operates at temperatures far below freezing."
  },
  {
    title: "THE FIRST VIEW FROM THE GROUND",
    image: "https://photojournal.jpl.nasa.gov/jpeg/PIA06440.jpg",
    narration:
      "After reaching the surface, Huygens continued sending data back toward Earth. Its measurements revealed a cold, complex environment beneath the haze. The mission lasted only a short time on the ground, but its discoveries transformed Titan from a distant point of light into a real place we could begin to explore."
  }
];

function run(command, args, options = {}) {
  return execFileAsync(command, args, {
    maxBuffer: 20 * 1024 * 1024,
    ...options
  });
}

async function downloadImage(url, destination) {
  const response = await fetch(url, {
    headers: { "User-Agent": "Mozilla/5.0 documentary-pilot/1.0" }
  });

  if (!response.ok) {
    throw new Error(`Image download failed: HTTP ${response.status} — ${url}`);
  }

  const contentType = response.headers.get("content-type") || "";

  if (!contentType.startsWith("image/")) {
    throw new Error(`URL did not return an image: ${url}`);
  }

  const buffer = Buffer.from(await response.arrayBuffer());

  if (buffer.length < 10000) {
    throw new Error(`Image file is unexpectedly small: ${url}`);
  }

  fs.writeFileSync(destination, buffer);
}

async function getAudioDuration(file) {
  const { stdout } = await run("ffprobe", [
    "-v", "error",
    "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1",
    file
  ]);

  const duration = Number(stdout.trim());

  if (!Number.isFinite(duration) || duration <= 0) {
    throw new Error(`Could not read audio duration: ${file}`);
  }

  return duration;
}

async function createNarration(text, output) {
  await run("edge-tts", [
    "--voice", "en-US-AriaNeural",
    "--rate", "-5%",
    "--text", text,
    "--write-media", output
  ]);

  if (!fs.existsSync(output) || fs.statSync(output).size < 1000) {
    throw new Error(`Narration audio was not created: ${output}`);
  }

  const wav = output.replace(/\.mp3$/i, ".wav");

  await run("ffmpeg", [
    "-y",
    "-i", output,
    "-ar", "48000",
    "-ac", "2",
    wav
  ]);

  return wav;
}

async function createScene(image, audio, title, index, destination) {
  const duration = await getAudioDuration(audio);
  const frames = Math.ceil(duration * FPS);

  // Fill the entire frame without stretching or exposing white borders.
  // Use a slow, controlled camera move over the image.
  const zoomExpression = index % 2 === 0
    ? "min(zoom+0.00035,1.12)"
    : "if(eq(on,0),1.12,max(zoom-0.00025,1.0))";

  const videoFilter =
    `scale=2200:1238:force_original_aspect_ratio=increase,` +
    `crop=2200:1238,` +
    `zoompan=z='${zoomExpression}':` +
    `x='iw/2-(iw/zoom/2)':` +
    `y='ih/2-(ih/zoom/2)':` +
    `d=${frames}:s=${WIDTH}x${HEIGHT}:fps=${FPS},` +
    `setsar=1,` +
    `drawbox=x=0:y=0:w=iw:h=190:color=black@0.45:t=fill,` +
    `drawtext=text='${title.replace(/'/g, "\\'")}':` +
    `fontcolor=white:fontsize=42:` +
    `x=90:y=75:borderw=2:bordercolor=black@0.6,` +
    `fade=t=in:st=0:d=0.6,` +
    `fade=t=out:st=${Math.max(0.1, duration - 0.6)}:d=0.6`;

  await run("ffmpeg", [
    "-y",
    "-loop", "1",
    "-framerate", String(FPS),
    "-i", image,
    "-i", audio,
    "-vf", videoFilter,
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-t", duration.toFixed(3),
    "-r", String(FPS),
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-crf", "19",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "48000",
    "-shortest",
    destination
  ]);

  return duration;
}

async function main() {
  fs.mkdirSync(ASSETS, { recursive: true });
  fs.mkdirSync(SCENES, { recursive: true });

  const sceneFiles = [];
  const credits = [];
  let totalDuration = 0;

  console.log("Starting the Huygens documentary pilot.");

  for (let i = 0; i < scenes.length; i++) {
    const scene = scenes[i];
    const number = String(i + 1).padStart(2, "0");

    const imageFile = path.join(ASSETS, `image-${number}.jpg`);
    const audioFile = path.join(ASSETS, `narration-${number}.mp3`);
    const sceneFile = path.join(SCENES, `scene-${number}.mp4`);

    console.log(`Downloading and validating scene ${number} image...`);
    await downloadImage(scene.image, imageFile);

    console.log(`Generating narration for scene ${number}...`);
    const wavFile = await createNarration(scene.narration, audioFile);

    console.log(`Rendering scene ${number}...`);
    const duration = await createScene(
      imageFile,
      wavFile,
      scene.title,
      i,
      sceneFile
    );

    totalDuration += duration;
    sceneFiles.push(sceneFile);

    credits.push(`${scene.title}\n${scene.image}\nNASA/JPL image archive`);
  }

  const listFile = path.join(OUT, "scene-list.txt");

  fs.writeFileSync(
    listFile,
    sceneFiles.map(file =>
      `file '${file.replace(/'/g, "'\\''")}'`
    ).join("\n")
  );

  const silentJoin = path.join(OUT, "joined-video.mp4");
  const finalVideo = path.join(OUT, "huygens-titan-pilot.mp4");

  console.log("Joining the rendered scenes...");

  await run("ffmpeg", [
    "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", listFile,
    "-c", "copy",
    silentJoin
  ]);

  console.log("Preparing final video and audio...");

  await run("ffmpeg", [
    "-y",
    "-i", silentJoin,
    "-vf", "format=yuv420p",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-crf", "19",
    "-c:a", "aac",
    "-b:a", "192k",
    "-movflags", "+faststart",
    finalVideo
  ]);

  const { stdout } = await run("ffprobe", [
    "-v", "error",
    "-show_entries", "stream=codec_type,width,height",
    "-show_entries", "format=duration",
    "-of", "json",
    finalVideo
  ]);

  const report = JSON.parse(stdout);
  const hasVideo = report.streams.some(s => s.codec_type === "video");
  const hasAudio = report.streams.some(s => s.codec_type === "audio");
  const duration = Number(report.format.duration);

  if (!hasVideo || !hasAudio || duration < 30) {
    throw new Error(
      `Final validation failed: video=${hasVideo}, audio=${hasAudio}, duration=${duration}`
    );
  }

  fs.writeFileSync(
    path.join(OUT, "credits.txt"),
    credits.join("\n\n")
  );

  fs.writeFileSync(
    path.join(OUT, "narration.txt"),
    scenes.map(s => s.narration).join("\n\n")
  );

  fs.writeFileSync(
    path.join(OUT, "validation.txt"),
    JSON.stringify({
      success: true,
      duration_seconds: duration,
      resolution: `${WIDTH}x${HEIGHT}`,
      scenes: scenes.length,
      audio: hasAudio,
      video: hasVideo
    }, null, 2)
  );

  console.log(`SUCCESS: ${finalVideo}`);
  console.log(`Duration: ${duration.toFixed(1)} seconds`);
}

main().catch(error => {
  console.error("DOCUMENTARY PILOT FAILED");
  console.error(error.stack || error);
  process.exit(1);
});

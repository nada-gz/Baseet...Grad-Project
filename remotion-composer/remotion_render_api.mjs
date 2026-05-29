/**
 * Remotion Node.js API renderer — copies assets to public/ folder and serves them.
 * Bypasses Windows CLI --props parsing issue AND the file:// URI limitation.
 * Usage: node remotion_render_api.mjs <props_json_file> <output_mp4>
 */
import { bundle } from '@remotion/bundler';
import { renderMedia, selectComposition } from '@remotion/renderer';
import { readFileSync, copyFileSync, mkdirSync, existsSync } from 'fs';
import { resolve, dirname, basename, extname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const [,, propsFile, outputFile] = process.argv;
if (!propsFile || !outputFile) {
  console.error('Usage: node remotion_render_api.mjs <props.json> <output.mp4>');
  process.exit(1);
}

// Parse props
const props = JSON.parse(readFileSync(propsFile, 'utf-8'));

// ---------------------------------------------------------------------------
// Copy all local video files into public/assets/ and rewrite paths to
// relative static file references (staticFile() style: just the filename).
// This is the ONLY way OffthreadVideo works in Remotion API mode — it needs
// to be served over HTTP via the dev server, not file:// URIs.
// ---------------------------------------------------------------------------
const publicDir = resolve(__dirname, 'public');
const publicAssetsDir = resolve(publicDir, 'assets');
mkdirSync(publicAssetsDir, { recursive: true });

function copyToPublic(filePath) {
  if (!filePath) return filePath;
  // If it's already a relative/static path, leave it alone
  if (!filePath.match(/^[A-Za-z]:[\\\/]/) && !filePath.startsWith('/')) return filePath;
  
  const name = basename(filePath);
  const dest = resolve(publicAssetsDir, name);
  
  if (!existsSync(dest)) {
    try {
      copyFileSync(filePath, dest);
      console.log(`[Remotion API] Copied ${name} → public/assets/`);
    } catch (e) {
      console.warn(`[Remotion API] Warning: could not copy ${filePath}: ${e.message}`);
      return filePath;
    }
  }
  
  // Return the path that staticFile() will serve: relative to public/
  return `assets/${name}`;
}

// Rewrite all paths in cuts
if (props.cuts) {
  for (const cut of props.cuts) {
    if (cut.source && cut.source !== '') {
      cut.source = copyToPublic(cut.source);
    }
    if (cut.backgroundVideo) {
      cut.backgroundVideo = copyToPublic(cut.backgroundVideo);
    }
    if (cut.backgroundImage) {
      cut.backgroundImage = copyToPublic(cut.backgroundImage);
    }
    if (cut.images && Array.isArray(cut.images)) {
      cut.images = cut.images.map(copyToPublic);
    }
  }
}

const entryPoint = resolve(__dirname, 'src/index.tsx');

console.log('[Remotion API] Bundling...');
const bundleLocation = await bundle({
  entryPoint,
  webpackOverride: (config) => config,
  publicDir,
});

// Calculate total duration from cuts
const totalDuration = props.cuts
  ? Math.max(...props.cuts.map(c => c.out_seconds || 0))
  : 60;
const fps = 30;
const durationInFrames = Math.ceil(totalDuration * fps);

console.log('[Remotion API] Selecting composition: Explainer');
const composition = await selectComposition({
  serveUrl: bundleLocation,
  id: 'Explainer',
  inputProps: props,
});

const finalComposition = {
  ...composition,
  durationInFrames,
  fps,
  width: 1920,
  height: 1080,
};

console.log(`[Remotion API] Rendering ${durationInFrames} frames (${totalDuration.toFixed(1)}s @ ${fps}fps)...`);

await renderMedia({
  composition: finalComposition,
  serveUrl: bundleLocation,
  codec: 'h264',
  outputLocation: outputFile,
  inputProps: props,
  onProgress: ({ progress }) => {
    process.stdout.write(`\r[Remotion API] Progress: ${(progress * 100).toFixed(0)}%`);
  },
  chromiumOptions: {
    disableWebSecurity: true,
  },
});

console.log(`\n[Remotion API] Done! Output: ${outputFile}`);

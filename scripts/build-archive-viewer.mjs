import { readFile, writeFile, mkdir, realpath } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { build } from 'esbuild';

const root = fileURLToPath(new URL('../', import.meta.url));
const source = 'public/research/analysis_outputs/3d_article_map/viewer.js';
const destination = new URL('../public/lab/', import.meta.url);
const threePackage = JSON.parse(await readFile(new URL('../node_modules/three/package.json', import.meta.url), 'utf8'));

if (threePackage.version !== '0.164.1') {
  throw new Error('The archived viewer requires the reviewed Three.js version 0.164.1.');
}

const installedLicense = await readFile(new URL('../node_modules/three/LICENSE', import.meta.url), 'utf8');
const publishedLicense = await readFile(new URL('LICENSE_THREE.txt', destination), 'utf8');
if (publishedLicense.trim() !== installedLicense.trim()) {
  throw new Error('The archived viewer license must match the installed Three.js license.');
}

const result = await build({
  absWorkingDir: root,
  entryPoints: [source],
  outfile: 'public/lab/archive-viewer.js',
  bundle: true,
  format: 'esm',
  platform: 'browser',
  target: ['es2022'],
  minify: true,
  sourcemap: false,
  legalComments: 'inline',
  metafile: true,
  write: false,
  banner: {
    js: '/*! Archived research viewer. Self-hosted Three.js 0.164.1; MIT license: /lab/LICENSE_THREE.txt. */',
  },
});

// A checked export may use a node_modules symlink. Validate canonical paths,
// so that arrangement remains constrained to this source and this package.
const sourcePath = await realpath(path.join(root, source));
const packageRoot = await realpath(new URL('../node_modules/three/', import.meta.url));
const unexpectedInputs = [];
for (const input of Object.keys(result.metafile.inputs)) {
  const canonical = await realpath(path.resolve(root, input));
  if (canonical !== sourcePath && !canonical.startsWith(packageRoot + path.sep)) unexpectedInputs.push(input);
}
const externalImports = Object.values(result.metafile.outputs).flatMap((output) => output.imports).filter((item) => item.external);
if (unexpectedInputs.length || externalImports.length || result.outputFiles.length !== 1) {
  throw new Error('The archived viewer must contain only its original module and bundled Three.js, with no external imports.');
}

await mkdir(destination, { recursive: true });
await writeFile(new URL('archive-viewer.js', destination), result.outputFiles[0].contents);
console.log(`Built public/lab/archive-viewer.js (${result.outputFiles[0].contents.length.toLocaleString('en-US')} bytes; no external imports).`);

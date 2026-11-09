/**
 * KEY404 native social card — 1200×630, outlined fonts and one unmodified scan.
 * This optional renderer does not change package.json or install dependencies.
 * Tooling: @resvg/resvg-js 2.6.2, fontkit 2.0.4; Python fonttools 4.60.2 + brotli 1.2.1.
 * Install tools in a temporary prefix, set KEY404_RENDER_MODULES to its node_modules,
 * and expose fontTools to KEY404_PYTHON (defaults to python3).
 * Reproduce from the repository root without modifying its dependency lock:
 *   renderer_dir=$(mktemp -d)
 *   npm install --prefix "$renderer_dir" --no-save --no-package-lock @resvg/resvg-js@2.6.2 fontkit@2.0.4
 *   python3 -m venv "$renderer_dir/python"
 *   "$renderer_dir/python/bin/pip" install fonttools==4.60.2 brotli==1.2.1
 *   KEY404_RENDER_MODULES="$renderer_dir/node_modules" KEY404_PYTHON="$renderer_dir/python/bin/python" node scripts/render-social-card.mjs
 * Required existing website fonts are installed by npm ci in the repository.
 */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
const root = path.resolve(import.meta.dirname, '..');
const loader = createRequire(import.meta.url);
function tool(name) {
  return process.env.KEY404_RENDER_MODULES
    ? loader(path.join(process.env.KEY404_RENDER_MODULES, name))
    : loader(name);
}
const { Resvg } = tool('@resvg/resvg-js');
const fontkit = tool('fontkit');
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'key404-social-font-'));
try {
  const variable = path.join(root, 'node_modules/@fontsource-variable/space-grotesk/files/space-grotesk-latin-wght-normal.woff2');
  const regularTtf = path.join(temporary, 'space-regular.ttf');
  const boldTtf = path.join(temporary, 'space-bold.ttf');
  execFileSync(process.env.KEY404_PYTHON || 'python3', ['-c', `
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
for weight, output in [(400,sys.argv[2]),(700,sys.argv[3])]:
    font=TTFont(sys.argv[1])
    font=instantiateVariableFont(font,{'wght':weight},inplace=False)
    font.flavor=None
    font.save(output)
`, variable, regularTtf, boldTtf]);
  const regular = fontkit.openSync(regularTtf);
  const bold = fontkit.openSync(boldTtf);
  const mono = fontkit.openSync(path.join(root, 'node_modules/@fontsource/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2'));
  const bone = '#edece3', lime = '#d6ff3c', black = '#11130f';
  const parts = [];
  const bounds = [];
  function text(label, value, font, size, x, y, fill, tracking = 0, opacity = 1) {
    const run = font.layout(value), scale = size / font.unitsPerEm;
    let pen = 0;
    const glyphs = [];
    for (let i = 0; i < run.glyphs.length; i++) {
      const glyph = run.glyphs[i], position = run.positions[i];
      const data = glyph.path.toSVG();
      if (data) glyphs.push(`<path d="${data}" transform="translate(${(x + pen + position.xOffset * scale).toFixed(3)} ${(y - position.yOffset * scale).toFixed(3)}) scale(${scale} ${-scale})"/>`);
      pen += position.xAdvance * scale + tracking;
    }
    bounds.push({ label, left: x, right: +(x + pen - tracking).toFixed(2), baseline: y, fontSize: size });
    parts.push(`<g id="${label}" fill="${fill}" opacity="${opacity}" aria-label="${value.replaceAll('&','&amp;').replaceAll('"','&quot;')}">${glyphs.join('')}</g>`);
  }
  const sourceFile = path.join(root, 'public/research/sources/pages/73.jpg');
  const source = fs.readFileSync(sourceFile);
  const photoWidth = 350, photoHeight = photoWidth * 3264 / 2544;
  parts.push(`<rect width="1200" height="630" fill="${black}"/>`);
  parts.push(`<rect x="59" y="48" width="4" height="22" fill="${lime}"/>`);
  text('kicker', 'MAX KEISER’S MAGAZINE PUZZLE', mono, 14, 80, 65, bone, 1.1);
  parts.push(`<path d="M59 96H684" stroke="${bone}" stroke-opacity=".22"/>`);
  text('headline-first', 'KEY NOT', bold, 126, 52, 238, bone, -5.0);
  text('headline-second', 'FOUND.', bold, 138, 52, 370, lime, -6.0);
  text('hook', 'A claimed 20 BTC.', regular, 29, 59, 431, bone, -.2);
  text('subhook', 'An open investigation.', regular, 29, 59, 469, bone, -.2);
  text('status', 'UNSOLVED · REWARD UNVERIFIED', mono, 13, 60, 520, bone, .7, .74);
  text('website', 'key404-casefile.vercel.app', mono, 16, 60, 577, bone, 0, .94);
  // The scan is embedded byte-for-byte as one image element. Only placement/rotation
  // are applied. Its pixels are not retouched, cropped, recolored, or composited.
  parts.push(`<g id="magazine-page" transform="rotate(5.5 965 310)">
    <rect x="786" y="82" width="358" height="${(photoHeight + 8).toFixed(3)}" fill="${bone}" filter="url(#paper-shadow)"/>
    <image x="790" y="86" width="${photoWidth}" height="${photoHeight}" preserveAspectRatio="xMidYMid meet" href="data:image/jpeg;base64,${source.toString('base64')}"/>
  </g>`);
  text('source-caption', 'THE EL SALVADOR ISSUE', mono, 11, 810, 577, bone, .8, .62);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-labelledby="card-title card-description">
<title id="card-title">KEY NOT FOUND. — Max Keiser’s magazine puzzle</title>
<desc id="card-description">A claimed 20 BTC. An open investigation. Unsolved; reward unverified. An unmodified magazine page is placed on the right. key404-casefile.vercel.app</desc>
<defs><filter id="paper-shadow" x="-30%" y="-20%" width="170%" height="160%"><feDropShadow dx="0" dy="14" stdDeviation="13" flood-color="#000000" flood-opacity=".55"/></filter></defs>
${parts.join('\n')}
</svg>\n`;
  const out = path.join(root, 'public/assets');
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, 'key404-social-card.svg'), svg);
  const png = new Resvg(svg, { fitTo: { mode: 'width', value: 1200 }, font: { loadSystemFonts: false } }).render().asPng();
  fs.writeFileSync(path.join(out, 'key404-social-card.png'), png);
  console.log(JSON.stringify({ width: 1200, height: 630, svgBytes: Buffer.byteLength(svg), pngBytes: png.length, sourceSha256: crypto.createHash('sha256').update(source).digest('hex'), textBounds: bounds }, null, 2));
} finally {
  fs.rmSync(temporary, { recursive: true, force: true });
}

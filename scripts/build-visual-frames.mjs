import { build } from 'esbuild';
import { mkdtemp, readFile, writeFile, mkdir, rm } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = fileURLToPath(new URL('../', import.meta.url));
const temporary = await mkdtemp(path.join(root, '.visual-build-'));
const output = path.join(root, 'public/research/visuals');
const write = process.argv.includes('--write');
try {
  const renderer = await build({stdin:{contents:`
    import React from 'react';
    import {renderToStaticMarkup} from 'react-dom/server';
    import {VisualFrame} from './src/components/VisualJournal';
    import data from './public/data/visual-journal.json';
    const results = data.entries.map((entry,index)=>({id:entry.id,svg:'<?xml version="1.0" encoding="UTF-8"?>\\n'+renderToStaticMarkup(React.createElement(VisualFrame,{entry,number:index+1}))+'\\n'}));
    process.stdout.write(JSON.stringify(results));
  `,resolveDir:root,loader:'tsx'},bundle:true,platform:'node',format:'cjs',packages:'external',
    loader:{'.css':'empty'},write:false,logLevel:'silent'});
  const file = path.join(temporary,'renderer.cjs');
  await writeFile(file,renderer.outputFiles[0].contents);
  const frames = JSON.parse(execFileSync(process.execPath,[file],{cwd:root,maxBuffer:1024*1024}).toString());
  if (write) await mkdir(output,{recursive:true});
  for (const frame of frames) {
    assert.match(frame.id,/^[a-z0-9-]+$/);
    const file = path.join(output,frame.id+'.svg');
    if (write) await writeFile(file,frame.svg);
    else assert.equal(await readFile(file,'utf8'),frame.svg,'Saved SVG differs from the current evidence frame; regenerate before publication');
  }
  const source = await readFile(path.join(root,'public/data/visual-journal.json'));
  if (write) await writeFile(path.join(output,'journal.json'),source);
  else assert.ok(source.equals(await readFile(path.join(output,'journal.json'))),'Saved scene data differs');
  console.log(JSON.stringify({standaloneSVGs:frames.length,sceneDataMatches:true,mode:write?'generated':'verified'}));
} finally { await rm(temporary,{recursive:true,force:true}); }

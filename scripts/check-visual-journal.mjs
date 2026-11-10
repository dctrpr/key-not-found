import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';

const root = path.resolve(import.meta.dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'public/data/visual-journal.json'), 'utf8'));
assert.equal(data.version, 1);
assert.equal(data.caseStatus, 'unsolved');
assert.ok(data.entries.length > 0);
const ids = new Set();
let previous = '';
for (const entry of data.entries) {
  assert.match(entry.id, /^[a-z0-9-]+$/);
  assert.ok(!ids.has(entry.id)); ids.add(entry.id);
  assert.ok(['funnel', 'history', 'source'].includes(entry.diagram));
  assert.ok(['spread', 'stack', 'mirror'].includes(entry.scene.layout));
  assert.ok(entry.scene.source === undefined || ['issue27', 'funky'].includes(entry.scene.source));
  const pages = entry.scene.source === 'funky' ? [107, 108, 109, 110, 111, 112] : entry.scene.source === 'issue27' ? [78, 79, 80, 81] : [75, 76, 77, 78, 79, 80];
  assert.ok(pages.includes(entry.scene.page));
  assert.ok(entry.source.path.startsWith('analysis_outputs/') && !entry.source.path.includes('..'));
  const raw = fs.readFileSync(path.join(root, 'public/research', entry.source.path));
  assert.equal(crypto.createHash('sha256').update(raw).digest('hex'), entry.source.sha256);
  const result = JSON.parse(raw);
  assert.equal(entry.completedAtUTC, result.completedAtUTC);
  assert.ok(entry.completedAtUTC >= previous); previous = entry.completedAtUTC;
  assert.equal(entry.evidence, '/research/' + entry.source.path.replace(/\.json$/, '.md'));
  assert.ok(fs.existsSync(path.join(root, 'public', entry.evidence)));
  assert.equal(entry.metrics.length, 3);
  for (const metric of entry.metrics) {
    let value = result;
    for (const key of metric.pointer.slice(1).split('/')) value = value[key];
    if (metric.operation === 'countActive') {
      assert.equal(value.length, 10);
      assert.ok(value.every(q => q.status === 'ok' && q.httpStatus === 200));
      value = value.filter(q => q.activity).length;
    } else assert.equal(metric.operation, undefined);
    assert.equal(value, metric.value, 'Visual metric differs from its frozen result');
  }
  if (entry.diagram === 'history') {
    assert.equal(result.addressImplementationsAgree, true);
    assert.equal(result.scopeComplete, true);
    assert.equal(result.outcome, 'zero-history-in-scope');
    for (const q of result.queries) for (const part of ['chain_stats','mempool_stats'])
      assert.ok(Object.values(q.statistics[part]).every(v => v === 0));
  }
  if (entry.diagram === 'source') {
    assert.equal(result.outcome, 'source-curated-identity-provisional');
    assert.equal(result.allCopiesByteIdentical, true);
    assert.equal(result.issueNumber, null);
    assert.equal(result.publicationDate, null);
    assert.equal(entry.scene.source, 'funky');
    const registerBytes = fs.readFileSync(path.join(root, 'public/research', result.sourceRegister.path));
    assert.equal(crypto.createHash('sha256').update(registerBytes).digest('hex'), result.sourceRegister.sha256);
    const register = JSON.parse(registerBytes);
    assert.equal(register.files.length, result.counts.reviewedImages);
    assert.equal(register.articleImageCount, result.counts.articleImages);
    assert.equal(register.adjacentAdvertisingImageCount, result.counts.adjacentAdvertisingImages);
    for (const file of register.files) {
      const bytes = fs.readFileSync(path.join(root, 'public/research/sources/funky-upheaval', file.path));
      assert.equal(bytes.length, file.bytes);
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), file.sha256);
    }
    assert.ok(Object.values(result.activity).every(value => value === 0));
  }
}
console.log(JSON.stringify({visualFramesVerified: ids.size, metricsVerified: ids.size * 3,
  completionTimesAndSourceHashesMatch: true}));

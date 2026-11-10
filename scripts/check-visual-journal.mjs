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
  assert.ok(['funnel', 'history', 'source', 'reading', 'measurement', 'support', 'review'].includes(entry.diagram));
  assert.ok(['spread', 'stack', 'mirror'].includes(entry.scene.layout));
  assert.ok(entry.scene.source === undefined || ['issue27', 'funky'].includes(entry.scene.source));
  const pages = entry.scene.source === 'funky' ? [107, 108, 109, 110, 111, 112] : entry.scene.source === 'issue27' ? [78, 79, 80, 81] : [73, 74, 75, 76, 77, 78, 79, 80];
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
  if (entry.id === 'batch20-supplemental-formats') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(result.caseStatus, 'unsolved');
    assert.equal(result.formalMessageExclusion, false);
    assert.equal(result.semanticReviewPerformed, false);
    assert.equal(result.selectorRegenerated, false);
    assert.equal(result.fullIndependentOutputAgreement, true);
    const readPinned = (reference) => {
      const bytes = fs.readFileSync(path.join(root, 'public/research', reference.path));
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), reference.sha256);
      return JSON.parse(bytes);
    };
    const execution = readPinned(result.execution);
    assert.equal(execution.scopeComplete, true);
    assert.equal(execution.privateReviewRequired, false);
    assert.equal(execution.totals.cohorts, 7);
    assert.equal(execution.totals.labeledStreams, 2594);
    assert.equal(execution.totals.sumPerCohortUniqueForms, 2576);
    assert.equal(execution.totals.commonValidationCalls + execution.totals.minikey26ChecksumCalls, result.counts.supplementalValidationCalls);
    assert.equal(Object.values(execution.totals.commonValidCountsSum).reduce((a, b) => a + b, 0) + execution.totals.minikey26ValidCountSum, result.counts.validSupplementalRecords);
    assert.equal(execution.cohorts.at(-1).testId, 'G03');
    assert.equal(execution.cohorts.at(-1).minikey26.enumerated, false);
    assert.equal(execution.cohorts.at(-1).minikey26.checksumCalls, 0);
    assert.ok(Object.values(execution.activity).every(value => value === 0));
    const independent = readPinned(result.independentCheck);
    assert.equal(independent.passed, true);
    assert.equal(independent.primaryResultSha256, result.execution.sha256);
    assert.equal(independent.comparisons.savedLabeledRecords, 2594);
    assert.equal(independent.comparisons.perCohortFormsSum, 2576);
    assert.equal(independent.comparisons.completeFormsAndUTF8, true);
    readPinned(result.postRunReview);
  }
  if (entry.diagram === 'review') {
    assert.equal(result.caseStatus, 'unsolved');
    assert.equal(result.formalMessageExclusion, false);
    assert.equal(result.newCipherExperiment, false);
    assert.equal(result.completeSavedPopulationRead, true);
    assert.equal(result.geometryRevalidatedBySemanticReview, false);
    assert.ok(Object.values(result.activity).every(value => value === 0));
    const readPinned = (reference) => {
      const bytes = fs.readFileSync(path.join(root, 'public/research', reference.path));
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), reference.sha256);
      return JSON.parse(bytes);
    };
    const original = readPinned(result.sourceArtifact);
    const inventory = readPinned(result.inventory);
    assert.equal(inventory.records.length, 40);
    assert.equal(inventory.records.filter(row => row.correctedPhysicalLeaf).length, 8);
    assert.equal(inventory.records.reduce((n, row) => n + row.codepoints, 0), 3588);
    for (const row of inventory.records) {
      let text = original;
      for (const key of row.jsonPointer.slice(1).split('/')) text = text[key];
      assert.equal(typeof text, 'string');
      assert.equal(Array.from(text).length, row.codepoints);
      assert.equal(Buffer.byteLength(text), row.utf8Bytes);
    }
    assert.equal(result.reviewers.length, 2);
    for (const reviewer of result.reviewers) {
      const review = readPinned(reviewer.review);
      assert.equal(review.readings.length, 40);
      assert.equal(reviewer.completeTextsRead, 40);
      assert.equal(reviewer.codepointsRead, 3588);
      for (let i = 0; i < inventory.records.length; i++) {
        const record = review.readings[i], expected = inventory.records[i];
        assert.equal(record.id ?? record.readingId, expected.id);
        assert.equal(record.codepoints ?? record.codepointCount, expected.codepoints);
        assert.equal(record.utf8Bytes ?? record.utf8ByteCount, expected.utf8Bytes);
        assert.equal(record.readInFull ?? record.completeSavedStringRead, true);
      }
    }
    assert.equal(readPinned(result.effectiveSourceCheck).allEffectivePagesStructurallyEqual, true);
  }
  if (entry.id === 'column151-sand-three-readings') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(result.caseStatus, 'unsolved');
    assert.equal(result.formalMessageExclusion, false);
    assert.equal(result.semanticReviewComplete, true);
    assert.equal(result.fullIndependentOutputAgreement, true);
    assert.deepEqual(result.selectedRows, [151, 76, 75]);
    assert.equal(result.reviewerCount, 2);
    const readPinned = (reference) => {
      const bytes = fs.readFileSync(path.join(root, 'public/research', reference.path));
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), reference.sha256);
      return JSON.parse(bytes);
    };
    const execution = readPinned(result.execution);
    assert.equal(execution.registrationCommit, result.registrationCommit);
    assert.equal(execution.counts.readings, result.readingCount);
    assert.equal(execution.sourceModel.physicalUnits, result.sourceRows);
    assert.equal(execution.counts.uniqueForms, result.uniqueForms);
    assert.equal(execution.counts.totalValidRecords, result.totalValidRecords);
    assert.equal(execution.counts.submittedCodepoints, result.sourceCodepointsPerReviewer);
    assert.ok(Object.values(execution.activity).every(value => value === 0));
    const independent = readPinned(result.independentCheck);
    assert.equal(independent.passed, true);
    assert.equal(independent.comparisons.fullReadingsUTF8, 3);
    assert.equal(independent.comparisons.fullExactAndCompactedForms, 6);
    assert.equal(independent.primaryResultSha256, result.execution.sha256);
    for (const reviewer of result.reviewers) {
      readPinned(reviewer.review);
      assert.equal(reviewer.completeReadingsRead, 3);
      assert.equal(reviewer.codepointsRead, result.sourceCodepointsPerReviewer);
    }
    for (const exhibit of entry.exhibits) {
      assert.ok(exhibit.path.startsWith('/research/sources/issue24-column151/native-contexts/'));
      assert.ok(!exhibit.path.includes('..'));
      const bytes = fs.readFileSync(path.join(root, 'public', exhibit.path));
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), exhibit.sha256);
      assert.equal(bytes.readUInt32BE(16), exhibit.width);
      assert.equal(bytes.readUInt32BE(20), exhibit.height);
    }
  }
  if (entry.diagram === 'support') {
    assert.equal(result.outcome, 'source-support-partial-full-glyph-repair-not-established');
    assert.equal(result.caseStatus, 'unsolved');
    assert.equal(result.counts.remainingTokenMembershipsNotAccepted, 1236);
    assert.equal(result.counts.sourceGlyphEdgeContactTokens, 13);
    assert.equal(result.feasibility.fullOriginalGlyphSupportCertified, false);
    assert.equal(result.feasibility.full142RowExpansionPerformed, false);
    assert.ok(Object.values(result.activity).every(value => value === 0));
    const readPinned = (reference) => {
      const bytes = fs.readFileSync(path.join(root, 'public/research', reference.path));
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), reference.sha256);
      return JSON.parse(bytes);
    };
    const native = readPinned(result.sourceInventory);
    assert.equal(native.rows.length, 142);
    assert.equal(native.rows.reduce((n, row) => n + row.canonicalTokens.length, 0), 1258);
    const atlas = readPinned(result.atlas);
    assert.equal(atlas.sourceRows.length, 142);
    assert.equal(atlas.sourceRows.reduce((n, row) => n + row.layers.dark.length + row.layers.light.length, 0), 12481);
    const pilot = readPinned(result.acceptedPilot);
    assert.equal(pilot.measurementReady, false);
    assert.equal(pilot.rows.length, 2);
    assert.equal(pilot.rows.reduce((n, row) => n + row.tokens.length, 0), 22);
    assert.equal(pilot.rows.reduce((n, row) => n + row.tokens.reduce((k, token) => k + token.componentIDs.length, 0), 0), 125);
    assert.equal(entry.exhibits.length, 2);
    for (const exhibit of entry.exhibits) {
      assert.ok(exhibit.path.startsWith('/research/analysis_outputs/continuation_20261110/g04_source_support/exhibits/'));
      assert.ok(!exhibit.path.includes('..'));
      const bytes = fs.readFileSync(path.join(root, 'public', exhibit.path));
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), exhibit.sha256);
      assert.equal(bytes.readUInt32BE(16), exhibit.width);
      assert.equal(bytes.readUInt32BE(20), exhibit.height);
    }
  }
  if (entry.diagram === 'measurement') {
    assert.equal(result.testId, 'g04-guard-trace');
    assert.equal(result.scopeComplete, true);
    assert.equal(result.status, 'trace-complete-baseline-match');
    assert.equal(result.counts.baselineMatchingRows, 142);
    assert.deepEqual(result.counts.rowFirstGuardCounts, {
      'optical-pass': 104, 'ink-touches-vertical-region-boundary': 13,
      'ink-touches-word-region-boundary': 23, 'no-robust-ink-columns': 1,
      'no-robust-ink-rows': 1,
    });
    assert.equal(result.postSpanGapGuardChecked, false);
    assert.ok(Object.values(result.activity).every(value => value === 0));
    assert.equal(entry.exhibits.length, 2);
    for (const exhibit of entry.exhibits) {
      assert.ok(exhibit.path.startsWith('/research/analysis_outputs/continuation_20261110/g04_measurement_audit/exhibits/'));
      assert.ok(!exhibit.path.includes('..'));
      const bytes = fs.readFileSync(path.join(root, 'public', exhibit.path));
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), exhibit.sha256);
    }
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
  if (entry.diagram === 'reading') {
    assert.equal(entry.scene.source, 'funky');
    assert.equal(result.semanticReviewComplete, true);
    assert.equal(result.formalMessageExclusion, false);
    assert.deepEqual(result.selectedRows, [111, 56, 55]);
    assert.equal(result.fullIndependentOutputAgreement, true);
    assert.equal(result.reviewers.length, 2);
    for (const reviewer of result.reviewers) {
      assert.equal(reviewer.readingsReadInFull, 3);
      assert.equal(reviewer.sourceCodepointsRead, result.sourceCodepointsPerReviewer);
      const reviewBytes = fs.readFileSync(path.join(root, 'public/research', reviewer.review.path));
      assert.equal(crypto.createHash('sha256').update(reviewBytes).digest('hex'), reviewer.review.sha256);
      const review = JSON.parse(reviewBytes);
      assert.equal(review.coverage.completeReadingsRead, 3);
      assert.equal(review.coverage.totalCodepointsRead ?? review.coverage.sourceOutputCodepointsRead, result.sourceCodepointsPerReviewer);
      assert.equal(review.completedAtUTC, reviewer.completedAtUTC);
    }
    const executionBytes = fs.readFileSync(path.join(root, 'public/research', result.execution.path));
    assert.equal(crypto.createHash('sha256').update(executionBytes).digest('hex'), result.execution.sha256);
    const execution = JSON.parse(executionBytes);
    assert.deepEqual(execution.counts.selectedRows, result.selectedRows);
    assert.equal(execution.counts.submittedCodepoints, result.sourceCodepointsPerReviewer);
    assert.ok(Object.values(execution.activity).every(value => value === 0));
    const independentBytes = fs.readFileSync(path.join(root, 'public/research', result.independentCheck.path));
    assert.equal(crypto.createHash('sha256').update(independentBytes).digest('hex'), result.independentCheck.sha256);
    const independent = JSON.parse(independentBytes);
    assert.equal(independent.primaryResultSha256, result.execution.sha256);
    assert.equal(independent.fullUTF8TextsMatch, true);
    assert.equal(independent.completePrivateReadingRecordsMatch, true);
  }
}
console.log(JSON.stringify({visualFramesVerified: ids.size, metricsVerified: ids.size * 3,
  completionTimesAndSourceHashesMatch: true}));

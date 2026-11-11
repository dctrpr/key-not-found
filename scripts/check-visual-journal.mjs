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
let previous = -Infinity;
for (const entry of data.entries) {
  assert.match(entry.id, /^[a-z0-9-]+$/);
  assert.ok(!ids.has(entry.id)); ids.add(entry.id);
  assert.ok(['funnel', 'history', 'source', 'reading', 'measurement', 'support', 'review'].includes(entry.diagram));
  assert.ok(['spread', 'stack', 'mirror'].includes(entry.scene.layout));
  assert.ok(entry.scene.source === undefined || ['issue26', 'issue27', 'funky'].includes(entry.scene.source));
  const pages = entry.scene.source === 'funky' ? [107, 108, 109, 110, 111, 112] : entry.scene.source === 'issue26' ? [102, 103, 104] : entry.scene.source === 'issue27' ? [78, 79, 80, 81] : [73, 74, 75, 76, 77, 78, 79, 80];
  assert.ok(pages.includes(entry.scene.page));
  assert.ok(entry.source.path.startsWith('analysis_outputs/') && !entry.source.path.includes('..'));
  const raw = fs.readFileSync(path.join(root, 'public/research', entry.source.path));
  assert.equal(crypto.createHash('sha256').update(raw).digest('hex'), entry.source.sha256);
  const result = JSON.parse(raw);
  assert.equal(entry.completedAtUTC, result.completedAtUTC);
  const completed = Date.parse(entry.completedAtUTC);
  assert.ok(completed >= previous);
  previous = completed;
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
  if (entry.id === 'issue24-page75-word-fit') {
    const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const scripts = path.join(root, 'public/research/scripts');
    assert.equal(result.testId, entry.id);
    assert.equal(entry.methodId, result.testId);
    assert.deepEqual(entry.scene, { layout: 'spread', page: 75 });
    assert.equal(digest(fs.readFileSync(path.join(base, 'PROTOCOL.json'))), result.protocolSha256);
    assert.equal(digest(fs.readFileSync(path.join(scripts, 'measure_page75_word_fit.py'))), result.scriptSha256);
    assert.equal(digest(fs.readFileSync(path.join(scripts, 'measure_page78_right_anchor.py'))), result.imageLoaderSha256);
    assert.equal(digest(fs.readFileSync(path.join(scripts, 'render_page75_word_fit.py'))), result.rendererSha256);
    const measurement = fs.readFileSync(path.join(base, 'MEASUREMENTS.json'));
    assert.equal(digest(measurement), result.measurementsSha256);
    assert.equal(result.replaySha256, result.measurementsSha256);
    const scans = Object.values(JSON.parse(measurement).scans);
    assert.equal(result.metrics.scansCompared, scans.length);
    assert.equal(result.metrics.scansCertifyingFit, scans.filter(scan => scan.summary.outcome === 'conditional-fit-within-observed-width').length);
    for (const scan of scans) {
      for (const variant of Object.values(scan.variants)) {
        for (const condition of variant.conditions) {
          assert.equal(Object.keys(condition.gaps).length, result.metrics.spacingReferences);
        }
      }
    }
    assert.deepEqual(entry.exhibits, result.exhibits);
    assert.equal(entry.exhibits.length, 1);
    const [exhibit] = entry.exhibits;
    const png = fs.readFileSync(path.join(root, 'public', exhibit.path));
    assert.equal(digest(png), exhibit.sha256);
    assert.equal(png.readUInt32BE(16), exhibit.width);
    assert.equal(png.readUInt32BE(20), exhibit.height);
  }
  if (entry.id === 'issue24-page78-right-anchor') {
    const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    assert.equal(result.testId, entry.id);
    assert.equal(entry.methodId, result.testId);
    assert.deepEqual(entry.scene, { layout: 'spread', page: 78 });
    assert.equal(digest(fs.readFileSync(path.join(base, 'PROTOCOL.json'))), result.protocolSha256);
    const scripts = path.join(root, 'public/research/scripts');
    assert.equal(digest(fs.readFileSync(path.join(scripts, 'measure_page78_right_anchor.py'))), result.scriptSha256);
    assert.equal(digest(fs.readFileSync(path.join(scripts, 'render_page78_right_anchor.py'))), result.rendererSha256);
    const measured = fs.readFileSync(path.join(base, 'MEASUREMENTS.json'));
    assert.equal(digest(measured), result.measurementsSha256);
    assert.equal(result.replaySha256, result.measurementsSha256);
    const { scans, targetRightAlignedInBoth, rightAlignedInBoth, otherRightAlignedInBoth } = JSON.parse(measured);
    assert.equal(targetRightAlignedInBoth, true);
    for (const scan of Object.values(scans)) {
      assert.equal(scan.blocks.length, result.metrics.blocksCompared);
      assert.deepEqual(scan.blocks.filter(block => block.classification === 'right').map(block => block.id), rightAlignedInBoth);
    }
    assert.equal(result.metrics.rightAlignedInBoth, rightAlignedInBoth.length);
    assert.equal(result.metrics.otherRightAlignedInBoth, otherRightAlignedInBoth.length);
    assert.deepEqual(entry.exhibits, result.exhibits);
    assert.equal(entry.exhibits.length, 1);
    const [exhibit] = entry.exhibits;
    const png = fs.readFileSync(path.join(root, 'public', exhibit.path));
    assert.equal(digest(png), exhibit.sha256);
    assert.equal(png.readUInt32BE(16), exhibit.width);
    assert.equal(png.readUInt32BE(20), exhibit.height);
  }
  if (entry.id === 'issue24-line-start-audit') {
    assert.equal(entry.methodId, 'faithful-lines');
    assert.equal(entry.scene.layout, 'mirror');
    assert.ok(entry.scene.page >= 75 && entry.scene.page <= 79);
    assert.equal(result.testId, entry.id);
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
    const readPinned = (name, hash) => {
      const bytes = fs.readFileSync(path.join(base, name));
      assert.equal(digest(bytes), hash);
      return JSON.parse(bytes);
    };
    const protocol = readPinned('PROTOCOL.json', result.protocolSha256);
    const packet = readPinned('PACKET_MANIFEST.json', result.packetManifestSha256);
    const lock = readPinned('RECEIPT_LOCK.json', result.receiptLockSha256);
    const comparison = readPinned('RECONCILIATION.json', result.reconciliationSha256);
    const adjudication = readPinned('ADJUDICATION.json', result.adjudicationSha256);
    readPinned('MATCHING_REPLAY.json', result.matchingReplaySha256);
    assert.equal(packet.assets.length, 10);
    assert.equal(lock.packetManifestSha256, result.packetManifestSha256);
    assert.equal(comparison.canonicalSha256, protocol.canonical.sha256);
    assert.equal(result.counts.canonical, 142);
    assert.deepEqual(result.counts, adjudication.counts);
    assert.deepEqual(result.activity, { newOCRCalls: 0, fittedTransforms: 0, newReadingStreams: 0, keyChecks: 0 });
    assert.equal(result.counts.linesMappedAcrossScans, comparison.counts.highForcedPairs + result.counts.manualShortRowsConfirmed);
    for (const [name, hash] of Object.entries(adjudication.sourceEvidenceHashes)) readPinned(name, hash);
    for (const label of ['A', 'B']) {
      const receipt = readPinned('READER_' + label + '.json', result.readerReceiptHashes[label]);
      assert.equal(lock.receiptHashes[label], result.readerReceiptHashes[label]);
      assert.deepEqual([...receipt.inspectedAssets].sort(), packet.assets.map(asset => asset.path).sort());
    }
    assert.deepEqual(entry.exhibits, result.exhibits);
    for (const exhibit of entry.exhibits) {
      const bytes = fs.readFileSync(path.join(root, 'public', exhibit.path));
      assert.equal(digest(bytes), exhibit.sha256);
      assert.equal(bytes.readUInt32BE(16), exhibit.width);
      assert.equal(bytes.readUInt32BE(20), exhibit.height);
    }
  }
  if (entry.id === 'issue24-second-scan-heading-review') {
    assert.equal(entry.methodId, 'g07-glyph-orientation');
    assert.deepEqual(entry.scene, { layout: 'mirror', page: 74 });
    assert.equal(result.testId, entry.id);
    assert.ok(['corroborated', 'contradicted-at-observed-feature', 'inconclusive'].includes(result.outcome));
    assert.deepEqual(result.activity, { newOCRCalls: 0, fittedTransforms: 0, keyChecks: 0 });
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
    const readPinned = (name, hash) => {
      const bytes = fs.readFileSync(path.join(base, name));
      assert.equal(digest(bytes), hash);
      return JSON.parse(bytes);
    };
    const packet = readPinned('PACKET_MANIFEST.json', result.packetManifestSha256);
    const lock = readPinned('STAGE1_LOCK.json', result.stage1LockSha256);
    readPinned('PROTOCOL.json', result.protocolSha256);
    assert.equal(lock.packetManifestSha256, result.packetManifestSha256);
    assert.equal(result.counts.stageReceipts, 4);
    for (const label of ['A', 'B']) {
      const hashes = result.readerReceiptHashes[label];
      const stage1 = readPinned('READER_' + label + '_STAGE1.json', hashes.stage1);
      const stage2 = readPinned('READER_' + label + '_STAGE2.json', hashes.stage2);
      assert.equal(lock.receiptHashes[label], hashes.stage1);
      assert.equal(stage2.stage1ReceiptSha256, hashes.stage1);
      assert.equal(stage1.page75ReferenceSeen, false);
      assert.equal(stage2.page75ReferenceSeen, true);
    }
    const stages = [packet.stages.stage1, packet.stages.stage2];
    const sourceAssets = [stages[0].assets.find(asset => asset.orientation === 'horizontal-mirror'),
      stages[1].assets.find(asset => asset.orientation === 'upright')];
    assert.equal(entry.exhibits.length, sourceAssets.length);
    for (const [index, exhibit] of entry.exhibits.entries()) {
      const asset = sourceAssets[index];
      const bytes = fs.readFileSync(path.join(root, 'public', exhibit.path));
      assert.equal(digest(bytes), asset.sha256);
      assert.equal(exhibit.sha256, asset.sha256);
      assert.equal(bytes.readUInt32BE(16), asset.width);
      assert.equal(bytes.readUInt32BE(20), asset.height);
      assert.equal(exhibit.width, asset.width);
      assert.equal(exhibit.height, asset.height);
    }
  }
  if (entry.id === 'issue24-full-page-glyph-review') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(entry.methodId, 'g07-glyph-orientation');
    assert.deepEqual(entry.scene, { layout: 'mirror', page: 74 });
    assert.equal(result.testId, entry.id);
    assert.equal(result.outcome, 'needs-source-adjudication');
    assert.equal(result.controlsPassed, true);
    assert.equal(result.reviewCoverageComplete, true);
    assert.deepEqual(result.findingCounts, { reversed: 0, 'possible-reversal': 0, 'rotated-ordinary': 52, unclear: 17 });
    assert.deepEqual(result.activity, { pixelDecodes: 0, newOCRCalls: 0, glyphAdjudications: 0, keyChecks: 0 });
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
    const manifestBytes = fs.readFileSync(path.join(base, 'PACKET_MANIFEST.json'));
    const mergedBytes = fs.readFileSync(path.join(base, 'MERGED.json'));
    assert.equal(digest(manifestBytes), result.packetManifestSha256);
    assert.equal(digest(mergedBytes), result.mergedArtifactSha256);
    assert.equal(JSON.parse(manifestBytes).tiles.length, result.counts.tilesPerReader);
    assert.equal(JSON.parse(mergedBytes).findings.length, result.counts.readerFindings);
    const replay = JSON.parse(fs.readFileSync(path.join(base, 'PACKET_REPLAY.json')));
    assert.equal(replay.assetsByteReproduced, result.counts.packetAssetHashesVerified);
    assert.equal(replay.originalPacketManifestSha256, result.packetManifestSha256);
    assert.equal(replay.reconstructedPageRGBHashesMatched, 8);
    assert.equal(replay.allOverlappingPixelCopiesIdentical, true);
    for (const [label, hash] of Object.entries(result.readerHashes)) {
      const receipt = fs.readFileSync(path.join(base, 'READER_' + label + '.json'));
      assert.equal(digest(receipt), hash);
      assert.equal(JSON.parse(receipt).tiles.length, result.counts.tilesPerReader);
    }
    const sourceCheck = JSON.parse(fs.readFileSync(path.join(base, 'SOURCE_CHECK.json')));
    assert.equal(sourceCheck.qualitativeOnly, true);
    assert.equal(sourceCheck.fittedTransform, false);
    assert.equal(sourceCheck.frozenReviewMarksChanged, false);
    assert.deepEqual(sourceCheck.exhibits.map(exhibit => exhibit.page), [74, 75]);
    assert.equal(entry.exhibits.length, 2);
    for (const [index, exhibit] of entry.exhibits.entries()) {
      const record = sourceCheck.exhibits[index];
      const file = path.join(base, record.path);
      const bytes = fs.readFileSync(file);
      assert.equal(file, path.join(root, 'public', exhibit.path));
      assert.equal(digest(bytes), record.sha256);
      assert.equal(exhibit.sha256, record.sha256);
      assert.equal(bytes.readUInt32BE(16), record.width);
      assert.equal(bytes.readUInt32BE(20), record.height);
      assert.equal(exhibit.width, record.width);
      assert.equal(exhibit.height, record.height);
    }
  }
  if (entry.id === 'g07-mirror-glyph-orientation') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(entry.methodId, 'g07-glyph-orientation');
    assert.deepEqual(entry.scene, { layout: 'mirror', page: 73 });
    assert.equal(result.testId, 'g07-mirror-glyph-orientation');
    assert.equal(result.scopeComplete, true);
    assert.equal(result.counts.regionsPerReader, 114);
    assert.equal(result.counts.agreedRegions + result.counts.unresolvedRegions, 114);
    assert.deepEqual(result.activity, { pixelDecodes: 0, newOCRCalls: 0, glyphAdjudications: 0, keyChecks: 0 });
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const readPinned = (name, digest) => {
      const bytes = fs.readFileSync(path.join(base, name));
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), digest);
      return JSON.parse(bytes);
    };
    const manifest = readPinned('PACKET_MANIFEST.json', result.packetManifestSha256);
    assert.equal(manifest.targets.length, 114);
    assert.equal(manifest.assets.length, 263);
    assert.equal(manifest.sheets.length, 32);
    const merged = readPinned('MERGED.json', result.mergedArtifactSha256);
    assert.equal(merged.regions.length, 114);
    assert.equal(merged.regions.filter(region => region.agreed).length, result.counts.agreedRegions);
    assert.equal(merged.regions.filter(region => region.candidate).length, result.counts.candidateRegions);
    assert.equal(merged.regions.filter(region => region.reverseFlag).length, result.counts.reverseFlagRegions);
    for (const label of ['A', 'B']) {
      const review = readPinned('READER_' + label + '.json', result.readerHashes[label]);
      assert.equal(review.rows.length, 114);
      assert.equal(review.peerMarksSeen, false);
      assert.equal(review.priorTargetMarksSeen, false);
    }
    assert.equal(entry.exhibits.length, 2);
    const diagnostic = JSON.parse(fs.readFileSync(path.join(base, 'ORIENTATION_DIAGNOSTIC.json')));
    assert.equal(diagnostic.region, 'p73-04');
    assert.equal(diagnostic.originalReviewOutcomeChanged, false);
    for (const [name, digest] of Object.entries(diagnostic.rawCrops)) {
      assert.equal(manifest.assets.find(item => item.path === name).sha256, digest);
    }
    for (const exhibit of entry.exhibits) {
      const file = path.join(root, 'public', exhibit.path);
      const source = path.basename(file) === 'p73-04-turned.png'
        ? diagnostic.figure
        : manifest.assets.find(item => item.path === path.basename(file));
      const bytes = fs.readFileSync(file);
      assert.equal(source.sha256, exhibit.sha256);
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), exhibit.sha256);
      assert.equal(bytes.readUInt32BE(16), exhibit.width);
      assert.equal(bytes.readUInt32BE(20), exhibit.height);
    }
  }
  if (entry.id === 'g02-paper-edge-visibility') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(entry.methodId, 'batch20-g02');
    assert.deepEqual(entry.scene, { layout: 'mirror', page: 78 });
    assert.equal(result.testId, 'g02-perimeter-visibility');
    assert.equal(result.scopeComplete, true);
    assert.equal(result.physicalRange, null);
    assert.deepEqual(result.activity, { pixelDecodes: 0, transformFits: 0, stencilReadings: 0, keyChecks: 0 });
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const packet = fs.readFileSync(path.join(base, 'PACKET_MANIFEST.json'));
    assert.equal(crypto.createHash('sha256').update(packet).digest('hex'), result.packetManifestSha256);
    const manifest = JSON.parse(packet);
    assert.equal(manifest.windows.length, 32);
    assert.equal(manifest.guides.length, 16);
    assert.equal(manifest.overview.length, 4);
    const merged = fs.readFileSync(path.join(base, 'MERGED.json'));
    assert.equal(crypto.createHash('sha256').update(merged).digest('hex'), result.mergedArtifactSha256);
    const marks = JSON.parse(merged);
    assert.equal(marks.crossings.filter(mark => mark.status === 'accepted').length, result.counts.acceptedCrossings);
    assert.equal(marks.crossings.filter(mark => mark.status === 'unresolved').length, result.counts.unresolvedCrossings);
    assert.equal(marks.corners.filter(mark => mark.status === 'accepted').length, result.counts.acceptedCorners);
    assert.deepEqual(marks.leaves, result.leaves);
    assert.equal(entry.exhibits.length, 2);
    for (const exhibit of entry.exhibits) {
      const file = path.join(root, 'public', exhibit.path);
      const guide = manifest.guides.find(item => item.path === path.basename(file));
      const bytes = fs.readFileSync(file);
      assert.equal(guide.sha256, exhibit.sha256);
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), exhibit.sha256);
      assert.equal(bytes.readUInt32BE(16), exhibit.width);
      assert.equal(bytes.readUInt32BE(20), exhibit.height);
    }
  }
  if (entry.id === 'g02-joint-source-model') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(entry.methodId, 'batch20-g02');
    assert.deepEqual(entry.scene, { layout: 'mirror', page: 77 });
    assert.equal(result.testId, 'g02-joint-color-source-audit');
    assert.equal(result.caseStatus, 'unsolved');
    assert.equal(result.sourceModelComplete, true);
    assert.equal(result.negativeResultClaimed, false);
    assert.equal(result.newCipherOutputsGenerated, false);
    assert.ok(Object.values(result.activity).every(n => n === 0));
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const inventory = fs.readFileSync(path.join(base, 'MEMBERSHIP.json'));
    assert.equal(crypto.createHash('sha256').update(inventory).digest('hex'), result.inventory.sha256);
    assert.equal(JSON.parse(inventory).wordRecords.length, 962);
    const review = JSON.parse(fs.readFileSync(path.join(base, 'INDEPENDENT_VERIFICATION.json')));
    assert.equal(review.verificationPassed, true);
    assert.equal(review.allOrderedMetadataFieldsMatch, true);
    assert.equal(review.primaryResultSha256, entry.source.sha256);
    assert.equal(review.primaryInventorySha256, result.inventory.sha256);
    assert.deepEqual(review.counts, result.counts);
    assert.deepEqual(review.globalSelectors, result.globalSelectors);
    assert.equal(result.globalSelectors['opposite-color'].independentAssignmentUpperBound, '8');
    assert.equal(result.globalSelectors['source-only'].independentAssignmentUpperBound, '576460752303423488');
  }
  if (entry.id === 'g02-stencil-shape-reachability') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(entry.methodId, 'batch20-g02');
    assert.deepEqual(entry.scene, { layout: 'mirror', page: 77 });
    assert.equal(result.testId, 'g02-stencil-literal-shape-reachability');
    assert.equal(result.caseStatus, 'unsolved');
    assert.deepEqual(result.counts, {
      descriptors: 160, completedDescriptors: 160, cappedDescriptors: 0,
      flatCrossCheckedDescriptors: 72, aliases: 240,
    });
    assert.deepEqual(result.activity, { checksums: 0, derivations: 0, historyQueries: 0, walletActions: 0 });
    assert.equal(result.descriptors.length, 160);
    assert.ok(result.descriptors.every(descriptor => descriptor.complete === true && descriptor.reason === null));
    assert.equal(result.descriptors.filter(descriptor => descriptor.flatAgreement === true).length, 72);
    const hasSyntax = (descriptor) => [...Object.values(descriptor.presence.wif),
      ...Object.values(descriptor.presence.minikey)].some(value => value === true);
    assert.equal(result.descriptors.filter(hasSyntax).length, 8);
    assert.equal(result.descriptors.filter(descriptor => !hasSyntax(descriptor)).length, 152);
    assert.ok(result.descriptors.every(({ presence }) => presence.hex64 === false &&
      Object.values(presence.bip39).every(value => value === false)));
  }
  if (entry.id === 'g02-shared-query-sensitivity') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(entry.methodId, 'batch20-g02');
    assert.deepEqual(entry.scene, { layout: 'mirror', page: 77 });
    assert.equal(result.testId, entry.id);
    assert.equal(result.caseStatus, 'unsolved');
    assert.equal(result.sharedQueryComplete, true);
    assert.equal(result.conditionalQueryModelOnly, true);
    assert.equal(result.physicalDisplacementRangeMeasured, false);
    assert.equal(result.counts.physicalDisplacementMeasurements, 0);
    assert.equal(result.counts.previousSyntaxNegativeLanguages, 152);
    assert.deepEqual(result.activity, { checksums: 0, derivations: 0, historyQueries: 0, walletActions: 0 });
    const hasSyntax = (presence) => [...Object.values(presence.wif),
      ...Object.values(presence.minikey)].some(value => value === true);
    assert.equal(result.languageChecks.length, 8);
    assert.ok(result.languageChecks.every(check => hasSyntax(check.priorPresence)));
    assert.equal(result.languageChecks.filter(check => hasSyntax(check.sharedQueryPresence)).length, 5);
    assert.equal(result.languageChecks.filter(check => !hasSyntax(check.sharedQueryPresence)).length, 3);
    const prior = fs.readFileSync(path.join(root, 'public/research/analysis_outputs/continuation_20261110/g02_shape_reachability/RESULT.json'));
    assert.equal(crypto.createHash('sha256').update(prior).digest('hex'), result.priorShapeResultSha256);
  }
  if (entry.id === 't01-saved-reading-review-result') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(entry.methodId, 'batch20-t01');
    assert.equal(entry.scene.source, undefined);
    assert.equal(entry.scene.layout, 'mirror');
    assert.equal(entry.scene.page, 75);
    assert.equal(result.testId, 't01-saved-alternating-direction-semantic-review');
    assert.equal(result.caseStatus, 'unsolved');
    assert.equal(result.completedAtUTC, '2026-11-10T21:31:35.827Z');
    assert.equal(result.semanticReviewComplete, true);
    assert.equal(result.formalMessageExclusion, false);
    assert.equal(result.outcome, 'complete-subjective-nonrecognition-in-saved-population');
    assert.deepEqual(result.counts, {
      savedRecords: 196, uniqueTexts: 152, packetsPerReader: 12,
      codepointsPerReader: 114810, utf8BytesPerReader: 115170,
      readers: 2, readersRecognizingActionableInstruction: 0,
    });
    assert.equal(result.readerContextLimitations.readerAPriorExposureBroaderThanFrozenPlan, true);
    assert.equal(result.readerContextLimitations.calibratedStatisticalIndependence, false);
    assert.equal(result.readerContextLimitations.freshnessIsSelfReport, true);
    assert.equal(result.readerContextLimitations.frozenPlanAmended, false);
    assert.equal(result.sourcePreparation.newCipherPopulationGenerated, false);
    assert.equal(result.sourcePreparation.originalExtractionRerun, false);
    assert.equal(result.sourcePreparation.wholeStringsUnmodified, true);
    assert.equal(result.sourcePreparation.all196AliasesRetained, true);
    assert.ok(Object.values(result.activity).every(value => value === 0));
    assert.equal(result.registrationCommit, 'fccfd659d2476c58f9fe6ed7133ca5c472e82b03');
    const readPinned = (reference) => {
      assert.ok(reference.path.startsWith('analysis_outputs/') && !reference.path.includes('..'));
      assert.match(reference.sha256, /^[a-f0-9]{64}$/);
      const bytes = fs.readFileSync(path.join(root, 'public/research', reference.path));
      assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), reference.sha256);
      return JSON.parse(bytes);
    };
    const protocol = readPinned(result.protocol);
    assert.equal(protocol.reviewId, result.testId);
    assert.equal(protocol.sourcePreparation.savedRecords, 196);
    assert.equal(protocol.sourcePreparation.exactUTF8Groups, 152);
    assert.equal(protocol.sourcePreparation.uniqueTextCodepointsPerReader, 114810);
    assert.equal(protocol.sourcePreparation.uniqueTextUTF8BytesPerReader, 115170);
    assert.equal(protocol.sourcePreparation.packetsPerReader, 12);
    assert.equal(protocol.sourcePreparation.allAliasesCoveredExactlyOnce, true);
    assert.equal(protocol.sourcePreparation.allTextsWholeAndUnmodified, true);
    assert.equal(Object.keys(protocol.packetHashes).length, 12);
    const registration = readPinned(result.registration);
    assert.equal(registration.registrationCommit, result.registrationCommit);
    assert.equal(registration.protocolSha256, result.protocol.sha256);
    assert.equal(registration.remoteHeadMatches, true);
    assert.equal(registration.beforeSemanticReadersStarted, true);
    assert.deepEqual(registration.packetHashes, protocol.packetHashes);
    const technical = readPinned(result.technicalReview);
    assert.equal(technical.passed, true);
    assert.equal(technical.registrationCommit, result.registrationCommit);
    assert.equal(technical.protocolSha256, result.protocol.sha256);
    assert.equal(technical.registrationReceiptSha256, result.registration.sha256);
    assert.equal(technical.registeredByteVerification.allCurrentBytesUnchanged, true);
    assert.equal(technical.packetIdentity.wholeGroups, 152);
    assert.equal(technical.packetIdentity.sourceAliasRecords, 196);
    assert.equal(technical.packetIdentity.uniqueCodepoints, 114810);
    assert.equal(technical.packetIdentity.uniqueUTF8Bytes, 115170);
    assert.deepEqual(technical.packetIdentity.wholePacketHashes, protocol.packetHashes);
    assert.equal(technical.coverageAttestationLimits.cognitiveReadingOrComprehensionProvenByCounters, false);
    assert.equal(technical.coverageAttestationLimits.actualAttentionMeasured, false);
    assert.equal(technical.deviation.frozenPlanOrProtocolAmended, false);
    assert.equal(technical.readers.A.exposure.priorLedgerAndSemanticSummaryExposure, true);
    assert.equal(technical.readers.A.exposure.broaderThanHumanPredeclaration, true);
    assert.equal(technical.readers.B.exposure.freshnessIsSelfReport, true);
    assert.equal(result.reviewers.length, 2);
    assert.deepEqual(result.reviewers.map(reviewer => reviewer.readerId), ['A', 'ReaderB']);
    const expectedGroupIds = Array.from({ length: 152 }, (_, i) => `T01-G${String(i + 1).padStart(3, '0')}`);
    const packetGroupCounts = [7, 5, 7, 5, 7, 5, 7, 5, 20, 23, 30, 31];
    for (const reviewer of result.reviewers) {
      const review = readPinned(reviewer.review);
      assert.equal(review.readerId, reviewer.readerId);
      assert.equal(review.registrationCommit, result.registrationCommit);
      assert.equal(review.reviewId, result.testId);
      assert.equal(reviewer.recognizedActionableInstruction, false);
      // These verify the frozen recorded coverage claims, not subjective cognition.
      assert.equal(reviewer.completeTextsRead, 152);
      assert.equal(reviewer.sourceAliasesCovered, 196);
      assert.equal(reviewer.codepointsRead, 114810);
      assert.equal(reviewer.utf8BytesRead, 115170);
      assert.deepEqual(review.inputPacketDigests, protocol.packetHashes);
      assert.deepEqual(review.groupIdsRead, expectedGroupIds);
      assert.equal(review.uniqueGroupsRead, 152);
      assert.equal(review.sourceAliasesCovered, 196);
      assert.equal(review.uniqueTextCodepointsRead, 114810);
      assert.equal(review.uniqueTextUTF8BytesRead, 115170);
      assert.equal(review.recognizedActionableInstruction, false);
      assert.equal(review.completedAtUTC, reviewer.completedAtUTC);
      assert.ok(review.exposure && typeof review.exposure === 'object');
      assert.equal(review.packetReviews.length, 12);
      const recordedPacketGroupIds = [];
      for (let i = 0; i < review.packetReviews.length; i++) {
        const packet = review.packetReviews[i];
        assert.equal(packet.packet, `PACKET_${String(i + 1).padStart(3, '0')}.json`);
        assert.equal(packet.allGroupsRead, true);
        const groupIds = packet.groupIDs;
        assert.equal(groupIds.length, packetGroupCounts[i]);
        recordedPacketGroupIds.push(...groupIds);
      }
      assert.deepEqual(recordedPacketGroupIds, expectedGroupIds);
    }
  }
  if (entry.id === 'stride26-history-result') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(result.testId, 'stride26-history');
    assert.equal(result.outcome, 'zero-history-in-scope');
    assert.equal(result.scopeComplete, true);
    assert.equal(result.addressImplementationsAgree, true);
    assert.equal(result.addressCount, 5);
    assert.equal(result.requestsAttempted, 10);
    assert.equal(result.sourceSurface.requiresWhitespaceCompaction, true);
    assert.equal(result.sourceSurface.contiguousInAnyUnmodifiedOriginalReading, false);
    assert.equal(result.sourceSurface.physicalPrintedKeyAuthenticated, false);
    assert.equal(result.transactions, 0);
    assert.equal(result.walletImports, 0);
    assert.ok(result.queries.every(query => query.status === 'ok' && query.httpStatus === 200 &&
      query.activity === false && Object.values(query.statistics).every(group => Object.values(group).every(value => value === 0))));
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const independent = JSON.parse(fs.readFileSync(path.join(base, 'INDEPENDENT_VERIFICATION.json')));
    assert.equal(independent.passed, true);
    assert.equal(independent.primaryResultSha256, entry.source.sha256);
    assert.equal(independent.registrationCommit, result.registrationCommit);
    assert.equal(independent.addressAgreement.completeNodeAndPythonRecordsEqual, true);
    assert.equal(independent.requestCoverage.observedPairs, 10);
    assert.equal(independent.requestCoverage.successfulHTTP200, 10);
    assert.equal(independent.statistics.strictSafeIntegerFieldsChecked, 100);
    assert.equal(independent.statistics.allFieldsZero, true);
    assert.equal(independent.statistics.publicQueriesExactlyEqualPrivateMinusAddress, true);
    assert.equal(independent.publicPrivacy.sourceCompactionLimitsPreserved, true);
    assert.equal(independent.reviewerActions.newNetworkRequests, 0);
    for (const [file, hash] of Object.entries({ ...result.sourceHashes, ...result.scriptHashes })) {
      assert.ok(!file.includes('..'));
      assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root, 'public/research', file))).digest('hex'), hash);
    }
  }
  if (entry.id === 'columns-fixed-output-compatibility') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(result.testId, 'columns-fixed-output-compatibility');
    assert.equal(result.scopeComplete, true);
    assert.equal(result.compatibilityGatesComplete, true);
    assert.equal(result.allOriginalArtifactIdentitiesVerified, true);
    assert.equal(result.newSelectorIntroduced, false);
    assert.equal(result.ocrRerun, false);
    assert.equal(result.sourceRepairs, false);
    assert.equal(result.privateReviewRequired, true);
    assert.equal(result.counts.labeledRecords, 43699);
    assert.equal(result.counts.sumPerCohortForms, 5557);
    assert.equal(result.counts.globalUnionComputed, false);
    assert.equal(result.counts.sumNominalValidRecords, 1);
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const independentBytes = fs.readFileSync(path.join(base, 'INDEPENDENT_VERIFICATION.json'));
    const independent = JSON.parse(independentBytes);
    assert.equal(independent.passed, true);
    assert.equal(independent.primaryResultSha256, entry.source.sha256);
    assert.equal(independent.fullOriginalArtifactBytesCompared, true);
    assert.equal(independent.fullFormsAndRawValidationCompared, true);
    const review = JSON.parse(fs.readFileSync(path.join(base, 'POST_RUN_REVIEW.json')));
    assert.equal(review.status, 'PASS');
    assert.ok(Object.values(review.checks).every(value => value === true));
    assert.equal(review.primaryResultSha256, entry.source.sha256);
    assert.equal(review.independentReceiptSha256, crypto.createHash('sha256').update(independentBytes).digest('hex'));
    const witness = JSON.parse(fs.readFileSync(path.join(base, 'SOURCE_WITNESS_REVIEW.json')));
    assert.equal(witness.status, 'PASS-scoped-saved-form-association');
    assert.equal(witness.primaryResultSha256, entry.source.sha256);
    assert.equal(witness.checks.presentInSavedStrictKnownCompactedForm, true);
    assert.equal(witness.checks.contiguousInAnyUnmodifiedOriginalReading, false);
    assert.equal(witness.privateValidationArtifactSha256, result.privateArtifactIntegrity['VALIDATION.private.json']);
    for (const receipt of [independent, review, witness]) assert.equal(receipt.registrationCommit, result.registrationCommit);
    for (const [file, hash] of Object.entries({ ...result.sourceHashes, ...result.scriptHashes })) {
      assert.ok(!file.includes('..'));
      assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root, 'public/research', file))).digest('hex'), hash);
    }
  }
  if (entry.id === 'g07-supplemental-formats') {
    assert.equal(entry.diagram, 'funnel');
    assert.equal(result.testId, 'g07-supplemental-fixed-formats');
    assert.deepEqual(result.counts, { labeledStreams: 1038, uniqueStreams: 833, uniqueForms: 1464, totalValidRecords: 0 });
    assert.equal(result.scopeComplete, true);
    assert.equal(result.supplementalGatesComplete, true);
    assert.equal(result.sourceRegenerated, false);
    assert.equal(result.ocrRerun, false);
    assert.equal(result.semanticReviewPerformed, false);
    assert.equal(result.privateReviewRequired, false);
    assert.equal(result.common4.validationCalls, 6);
    assert.deepEqual(result.common4.uniqueShapeCounts, { extended_private: 0, bip38: 0, address: 6, sec_public: 0 });
    assert.ok(Object.values(result.common4.validCounts).every(n => n === 0));
    assert.equal(result.minikey26.enumerated, true);
    assert.equal(result.minikey26.checksumCalls, 2);
    assert.equal(result.minikey26.validCount, 0);
    assert.ok(Object.values(result.activity).every(n => n === 0));
    const base = path.dirname(path.join(root, 'public/research', entry.source.path));
    const independentBytes = fs.readFileSync(path.join(base, 'INDEPENDENT_VERIFICATION.json'));
    const independent = JSON.parse(independentBytes);
    assert.equal(independent.passed, true);
    assert.equal(independent.primaryResultSha256, entry.source.sha256);
    assert.equal(independent.comparisons.fullOriginalObjectsOrderAndUTF8, true);
    assert.equal(independent.comparisons.fullFormsAndRawValidation, true);
    const review = JSON.parse(fs.readFileSync(path.join(base, 'POST_RUN_REVIEW.json')));
    assert.equal(review.status, 'PASS');
    assert.ok(Object.values(review.checks).every(value => value === true));
    assert.equal(review.pins.independentVerificationSha256, crypto.createHash('sha256').update(independentBytes).digest('hex'));
    assert.equal(result.registrationCommit, independent.registrationCommit);
    assert.equal(result.registrationCommit, review.registrationCommit);
    for (const [file, hash] of Object.entries({ ...result.sourceHashes, ...result.scriptHashes })) {
      assert.ok(!file.includes('..'));
      assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root, 'public/research', file))).digest('hex'), hash);
    }
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

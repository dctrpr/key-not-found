// Fixed, preregistered minikey-window coverage audit. Offline unless --check is
// explicit and a target candidate passes the format's one-byte check.
// No wallet import, signing, transaction, candidate secret or scalar output.
'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const INPUT = 'analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.json';
const PROTOCOL = 'analysis_outputs/continuation_20261110/minikey_windows/PROTOCOL.json';
const INPUT_SHA256 = '1651a33dab46babf36f56439ddb409058cfa36712d96ead7d4200962b80817b9';
const LENGTHS = Object.freeze([22, 30]);
const SCOPE = Object.freeze({ recordedStreams: 22, uniqueForms: 42,
  positionWindows22: 113830, positionWindows30: 113494, totalPositionWindows: 227324 });
const FINGERPRINT = Object.freeze({ algorithm: 'SHA-256',
  domainText: 'KEY404/minikey-window-audit/fingerprint/v1', separatorHex: '00',
  rule: 'SHA256(UTF8(domainText) || 0x00 || ASCII(candidate)); never SHA256(candidate), which is the private scalar' });
const ADDRESS_SCOPE = Object.freeze(['P2PKH uncompressed', 'P2PKH compressed',
  'P2SH-P2WPKH', 'P2WPKH', 'P2TR key-path with BIP341 TapTweak']);
const PROVIDERS = Object.freeze({ blockstream: 'https://blockstream.info/api/address/',
  mempool: 'https://mempool.space/api/address/' });
const STAT_FIELDS = Object.freeze(['funded_txo_count', 'funded_txo_sum',
  'spent_txo_count', 'spent_txo_sum', 'tx_count']);
const BASE58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const now = () => new Date().toISOString();

function candidateFingerprint(value) {
  return sha256(Buffer.concat([Buffer.from(FINGERPRINT.domainText + '\0', 'utf8'),
    Buffer.from(value, 'ascii')]));
}
function hasMinikeyShape(value) {
  return LENGTHS.includes(value.length) && /^S[1-9A-HJ-NP-Za-km-z]+$/.test(value);
}
function checkMinikey(value) {
  if (!hasMinikeyShape(value)) return { shapeValid: false, formatValid: false,
    checksumFirstByte: null };
  const byte = crypto.createHash('sha256').update(value + '?', 'ascii').digest()[0];
  return { shapeValid: true, formatValid: byte === 0,
    checksumFirstByte: byte.toString(16).padStart(2, '0') };
}
function selectedVariant(v) {
  return v.frame === 'body' && v.subset === 'all' &&
    v.parityBase === 'all_printed_rows' && ['global', 'page'].includes(v.reset) &&
    ((v.projection === 'complete_lines' && ['odd', 'even'].includes(v.phase)) ||
     (['first_words', 'first_word_initials'].includes(v.projection) && v.phase === 'all'));
}
function selectStreams(input) {
  assert.ok(Array.isArray(input.candidates), 'Missing frozen candidate records');
  const selected = new Map();
  for (const c of input.candidates) {
    assert.ok(typeof c.text === 'string' && Array.isArray(c.variants), 'Invalid frozen record');
    const variants = c.variants.filter(selectedVariant);
    if (!variants.length) continue;
    assert.equal(sha256(Buffer.from(c.text, 'utf8')), c.sha256, 'Frozen stream hash mismatch');
    for (const v of variants) {
      assert.ok(['down', 'up'].includes(v.direction), 'Unregistered reading direction');
      assert.ok(['normal', 'character_reverse'].includes(v.textDirection), 'Unregistered text direction');
    }
    assert.ok(!selected.has(c.text), 'Duplicate frozen stream record');
    selected.set(c.text, { text: c.text, sourceSha256: c.sha256, matchingVariants: variants });
  }
  return [...selected.values()].sort((a, b) => a.sourceSha256.localeCompare(b.sourceSha256));
}
function makeForms(streams) {
  const forms = new Map();
  for (const stream of streams) {
    for (const [form, text] of [['as_text', stream.text], ['compact', stream.text.replace(/\s/g, '')]]) {
      // All preregistered forms are longer than a minikey. Their ordinary
      // content hashes consequently cannot equal a candidate's private scalar.
      assert.ok(Array.from(text).length > 30, 'Unexpected short frozen form');
      if (!forms.has(text)) forms.set(text, { text, formSha256: sha256(Buffer.from(text, 'utf8')), sources: [] });
      forms.get(text).sources.push({ sourceSha256: stream.sourceSha256, form });
    }
  }
  return [...forms.values()].sort((a, b) => a.formSha256.localeCompare(b.formSha256));
}
function countPositions(forms) {
  const counts = { positionWindows22: 0, positionWindows30: 0 };
  for (const f of forms) for (const size of LENGTHS)
    counts['positionWindows' + size] += Math.max(0, Array.from(f.text).length - size + 1);
  return { ...counts, totalPositionWindows: counts.positionWindows22 + counts.positionWindows30 };
}
function scanShapeWindows(forms) {
  const unique = new Map();
  let shapeCompatibleOccurrences = 0;
  for (const form of forms) {
    const chars = Array.from(form.text);
    for (let offset = 0; offset < chars.length; offset++) {
      if (chars[offset] !== 'S') continue;
      for (const length of LENGTHS) {
        if (offset + length > chars.length) continue;
        const value = chars.slice(offset, offset + length).join('');
        if (!hasMinikeyShape(value)) continue;
        shapeCompatibleOccurrences++;
        if (!unique.has(value)) unique.set(value, { value,
          fingerprint: candidateFingerprint(value), length, ...checkMinikey(value), locators: [] });
        for (const source of form.sources) unique.get(value).locators.push({
          sourceSha256: source.sourceSha256, form: source.form,
          formSha256: form.formSha256, offset, length });
      }
    }
  }
  return { windows: [...unique.values()].sort((a, b) => a.fingerprint.localeCompare(b.fingerprint)),
    shapeCompatibleOccurrences };
}
function publicWindow(w) {
  // Explicit allowlist. In particular, never serialize the in-memory value.
  return { fingerprint: w.fingerprint, length: w.length,
    checksumFirstByte: w.checksumFirstByte, formatValid: w.formatValid, locators: w.locators };
}
function deriveAddresses(value) {
  if (!checkMinikey(value).formatValid) throw new Error('Refusing invalid minikey derivation');
  const secret = crypto.createHash('sha256').update(value, 'ascii').digest();
  try {
    const bitcoin = require('bitcoinjs-lib');
    const ecc = require('tiny-secp256k1');
    bitcoin.initEccLib(ecc);
    if (!ecc.isPrivate(secret)) throw new Error('Invalid scalar');
    const compressed = Buffer.from(ecc.pointFromScalar(secret, true));
    const uncompressed = Buffer.from(ecc.pointFromScalar(secret, false));
    const native = bitcoin.payments.p2wpkh({ pubkey: compressed });
    return [
      { type: ADDRESS_SCOPE[0], address: bitcoin.payments.p2pkh({ pubkey: uncompressed }).address },
      { type: ADDRESS_SCOPE[1], address: bitcoin.payments.p2pkh({ pubkey: compressed }).address },
      { type: ADDRESS_SCOPE[2], address: bitcoin.payments.p2sh({ redeem: native }).address },
      { type: ADDRESS_SCOPE[3], address: native.address },
      // bitcoinjs-lib lifts the x-only internal key and applies BIP341 TapTweak.
      { type: ADDRESS_SCOPE[4], address: bitcoin.payments.p2tr({ internalPubkey: compressed.subarray(1) }).address },
    ].map(a => {
      if (typeof a.address !== 'string') throw new Error('Missing public address');
      return a;
    });
  } catch {
    throw new Error('Address derivation failed; install the locked research dependencies');
  } finally { secret.fill(0); }
}
function validateStats(data, address) {
  if (!data || data.address !== address) throw new Error('Invalid address statistics');
  const result = {};
  for (const part of ['chain_stats', 'mempool_stats']) {
    const raw = data[part];
    if (!raw) throw new Error('Missing address statistics');
    const clean = {};
    for (const field of STAT_FIELDS) {
      if (!Number.isSafeInteger(raw[field]) || raw[field] < 0) throw new Error('Invalid address statistics');
      clean[field] = raw[field];
    }
    if (clean.tx_count === 0 && STAT_FIELDS.some(k => clean[k] !== 0))
      throw new Error('Inconsistent zero-transaction statistics');
    result[part] = clean;
  }
  return result;
}
function hasActivity(stats) { return stats.chain_stats.tx_count > 0 || stats.mempool_stats.tx_count > 0; }
async function requestStats(provider, address, counters, fetcher = fetch) {
  const url = PROVIDERS[provider] + encodeURIComponent(address);
  const checkedAtUTC = now();
  let httpStatus = null;
  counters.requestsAttempted++;
  try {
    const response = await fetcher(url, { signal: AbortSignal.timeout(20000),
      redirect: 'error', cache: 'no-store', headers: { Accept: 'application/json', 'Cache-Control': 'no-cache' } });
    httpStatus = response.status;
    if (!response.ok) return { provider, address, checkedAtUTC, status: 'error', httpStatus,
      error: 'HTTP ' + httpStatus };
    const body = await response.text();
    if (body.length > 65536) throw new Error('Oversized statistics response');
    const statistics = validateStats(JSON.parse(body), address);
    return { provider, address, checkedAtUTC, status: 'ok', httpStatus, statistics,
      activity: hasActivity(statistics) };
  } catch (error) {
    const timeout = error && ['TimeoutError', 'AbortError'].includes(error.name);
    return { provider, address, checkedAtUTC, status: 'error', httpStatus,
      error: timeout ? 'Request timed out' : 'Request failed or returned invalid statistics' };
  }
}
async function checkPublicAddress(address, counters, fetcher = fetch) {
  const primary = await requestStats('blockstream', address, counters, fetcher);
  if (primary.status !== 'ok') return { address, outcome: 'inconclusive', primary,
    secondary: { status: 'not-attempted', reason: 'Primary lookup failed' } };
  if (primary.activity) return { address, outcome: 'activity-detected', primary,
    secondary: { status: 'not-needed', reason: 'Activity already requires private review' } };
  const secondary = await requestStats('mempool', address, counters, fetcher);
  return { address, primary, secondary, outcome: secondary.status !== 'ok' ? 'inconclusive'
    : secondary.activity ? 'activity-detected' : 'independently-verified-zero' };
}
async function mapTwo(items, operation) {
  const results = new Array(items.length);
  let next = 0;
  async function worker() {
    while (next < items.length) { const index = next++; results[index] = await operation(items[index]); }
  }
  await Promise.all(Array.from({ length: Math.min(2, items.length) }, worker));
  return results;
}
function selfTest() {
  const sample = 'S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'; // Published format example; never queried.
  assert.equal(sample.length, 30);
  assert.equal(sha256(Buffer.from(sample, 'ascii')),
    '4c7a9640c72dc2099f23715d0c8a0d8a35f8906e3cab61dd3f78b67bf887c9ab');
  assert.ok(checkMinikey(sample).formatValid);
  let short = null;
  for (let n = 0; n < 65536; n++) {
    let value = n, suffix = '';
    do { suffix = BASE58[value % 58] + suffix; value = Math.floor(value / 58); } while (value);
    const candidate = 'S' + '2'.repeat(15) + suffix.padStart(6, '2');
    if (checkMinikey(candidate).formatValid) { short = candidate; break; }
  }
  assert.ok(short && short.length === 22, 'Bounded synthetic control generation failed');
  let badChecksum = null;
  for (const last of BASE58) {
    const value = sample.slice(0, -1) + last;
    if (!checkMinikey(value).formatValid) { badChecksum = value; break; }
  }
  assert.ok(badChecksum && hasMinikeyShape(badChecksum));
  for (const bad of ['T' + sample.slice(1), 'S0' + sample.slice(2), sample + '1', sample.slice(0, -1)])
    assert.equal(checkMinikey(bad).formatValid, false);
  for (const control of [sample, short]) {
    const prefix = 'prefix::', text = prefix + control + '::suffix';
    assert.equal(hasMinikeyShape(text), false); // Old whole-stream gate misses this.
    const form = { text, formSha256: sha256(text), sources: [{ sourceSha256: sha256(text), form: 'as_text' }] };
    const found = scanShapeWindows([form]).windows.find(w => w.value === control);
    assert.ok(found && found.formatValid && found.locators.some(l => l.offset === prefix.length));
    assert.notEqual(found.fingerprint, sha256(Buffer.from(control, 'ascii')));
    const serialized = JSON.stringify(publicWindow(found));
    assert.ok(!serialized.includes(control) && !serialized.includes(sha256(Buffer.from(control, 'ascii'))));
  }
  const zero = Object.fromEntries(STAT_FIELDS.map(k => [k, 0]));
  assert.deepEqual(validateStats({ address: 'control', chain_stats: zero, mempool_stats: zero }, 'control'),
    { chain_stats: zero, mempool_stats: zero });
  assert.throws(() => validateStats({ address: 'control', chain_stats: { ...zero, tx_count: -1 }, mempool_stats: zero }, 'control'));
  assert.throws(() => validateStats({ address: 'control', chain_stats: { ...zero, funded_txo_sum: 1 }, mempool_stats: zero }, 'control'));
  return { passed: true, controls: ['published-30-character-vector', 'bounded-fixed-counter-22-character-control',
    'embedded-window-regression-both-lengths', 'invalid-prefix-alphabet-length-checksum',
    'domain-separated-nonsecret-fingerprints', 'address-statistics-validation'],
    targetInputRead: false, targetWindowsChecked: 0, addressQueries: 0 };
}
function validateProtocol(protocol) {
  assert.equal(protocol.id, 'minikey-window-audit', 'Unexpected protocol');
  assert.equal(protocol.input, INPUT, 'Unregistered input');
  assert.equal(protocol.inputSha256, INPUT_SHA256, 'Unregistered input hash');
  assert.deepEqual(protocol.expectedScope, SCOPE, 'Unregistered scope');
  assert.deepEqual(protocol.minikeyLengths, LENGTHS, 'Unregistered key lengths');
  assert.deepEqual(protocol.addressScope, ADDRESS_SCOPE, 'Unregistered address scope');
  assert.equal(protocol.selector.frame, 'body');
  assert.equal(protocol.selector.subset, 'all');
  assert.equal(protocol.selector.parityBase, 'all_printed_rows');
  assert.deepEqual(protocol.selector.resets, ['global', 'page']);
  assert.deepEqual(protocol.selector.projections, [
    { projection: 'complete_lines', phases: ['odd', 'even'] },
    { projection: 'first_words', phases: ['all'] },
    { projection: 'first_word_initials', phases: ['all'] },
  ]);
}
async function runAudit({ check = false, registrationCommit = null } = {}) {
  const startedAtUTC = now();
  const controls = selfTest();
  const protocolBytes = fs.readFileSync(path.join(ROOT, PROTOCOL));
  const protocol = JSON.parse(protocolBytes.toString('utf8'));
  validateProtocol(protocol);
  const inputBytes = fs.readFileSync(path.join(ROOT, INPUT));
  assert.equal(sha256(inputBytes), INPUT_SHA256, 'Pinned input hash mismatch');
  const streams = selectStreams(JSON.parse(inputBytes.toString('utf8')));
  const forms = makeForms(streams);
  const scope = { recordedStreams: streams.length, uniqueForms: forms.length, ...countPositions(forms) };
  assert.deepEqual(scope, SCOPE, 'Observed population differs from preregistered scope');
  // Target checksum work begins only here, after hash/scope/control gates.
  const scan = scanShapeWindows(forms), valid = scan.windows.filter(w => w.formatValid);
  const result = { schemaVersion: 1, method: protocol.id, startedAtUTC,
    registrationCommit, protocol: PROTOCOL, protocolSha256: sha256(protocolBytes),
    input: INPUT, inputSha256: INPUT_SHA256, scriptSha256: sha256(fs.readFileSync(__filename)),
    fingerprintRule: FINGERPRINT, offsetUnit: 'zero-based Unicode code points within the named exact form',
    scope, controls, selectedStreams: streams.map(s => ({ sourceSha256: s.sourceSha256,
      codePointLength: Array.from(s.text).length, matchingVariants: s.matchingVariants })),
    selectedForms: forms.map(f => ({ formSha256: f.formSha256, codePointLength: Array.from(f.text).length,
      sources: f.sources })), shapeCompatibleOccurrences: scan.shapeCompatibleOccurrences,
    uniqueShapeCompatibleWindows: scan.windows.length, formatValidCandidates: valid.length,
    windows: scan.windows.map(publicWindow), addressScope: ADDRESS_SCOPE,
    addressCheckRequested: check, requestsAttempted: 0, addressChecks: [],
    candidateAddressRecords: [], publicReviewNeeded: false };
  const counters = { requestsAttempted: 0 };
  if (valid.length && check) {
    for (const candidate of valid) {
      try { result.candidateAddressRecords.push({ fingerprint: candidate.fingerprint,
        addresses: deriveAddresses(candidate.value) }); }
      catch { result.candidateAddressRecords.push({ fingerprint: candidate.fingerprint,
        derivationError: 'Address derivation failed; install the locked research dependencies' }); }
    }
    const addresses = [...new Set(result.candidateAddressRecords.flatMap(c => (c.addresses || []).map(a => a.address)))];
    result.addressChecks = await mapTwo(addresses, a => checkPublicAddress(a, counters));
  }
  result.requestsAttempted = counters.requestsAttempted;
  result.activeAddresses = result.addressChecks.filter(c => c.outcome === 'activity-detected').length;
  result.inconclusiveAddresses = result.addressChecks.filter(c => c.outcome === 'inconclusive').length;
  const derivationFailed = result.candidateAddressRecords.some(c => c.derivationError);
  result.activityCheckComplete = valid.length === 0 || (check && !derivationFailed &&
    result.addressChecks.length > 0 && result.inconclusiveAddresses === 0);
  result.publicReviewNeeded = valid.length > 0 && (!check || derivationFailed ||
    result.inconclusiveAddresses > 0 || result.activeAddresses > 0);
  result.outcome = valid.length === 0 ? 'excluded-literal-minikeys-in-declared-forms'
    : result.activeAddresses ? 'activity-detected-private-review-required'
    : !check ? 'format-valid-candidates-activity-unchecked'
    : !result.activityCheckComplete ? 'inconclusive-activity-check'
    : 'zero-activity-in-declared-address-scope';
  result.completedAtUTC = now();
  return result;
}
function parseArgs(argv) {
  const args = { scan: false, selfTest: false, check: false, out: null, registrationCommit: null };
  for (let i = 0; i < argv.length; i++) {
    const flag = argv[i];
    if (flag === '--scan') args.scan = true;
    else if (flag === '--self-test') args.selfTest = true;
    else if (flag === '--check') args.check = true;
    else if (flag === '--out' || flag === '--registration-commit') {
      const value = argv[++i];
      if (!value || value.startsWith('--')) throw new Error('Missing option value');
      args[flag === '--out' ? 'out' : 'registrationCommit'] = value;
    } else throw new Error('Unknown command option');
  }
  if (args.registrationCommit && !/^[a-f0-9]{40}$/.test(args.registrationCommit))
    throw new Error('Registration commit must be forty lowercase hexadecimal characters');
  if (args.selfTest && (args.scan || args.check || args.out || args.registrationCommit))
    throw new Error('Self-test must run separately from a target audit');
  if (args.scan && !args.out) throw new Error('Target scan requires an explicit --out path');
  if (!args.scan && (args.check || args.out || args.registrationCommit))
    throw new Error('Target options require --scan');
  return args;
}
function safeError(error) {
  return String(error && error.message || 'Audit failed').replaceAll(ROOT, '<research>')
    .replace(/(?:\/Users\/|\/home\/)[^\s"'<>]+/g, '<personal-path>')
    .replace(/[A-Z]:\\Users\\[^\s"'<>]+/g, '<personal-path>').slice(0, 600);
}
async function main(argv) {
  const args = parseArgs(argv);
  if (args.selfTest) { console.log(JSON.stringify(selfTest(), null, 2)); return; }
  if (!args.scan) { console.log('Use --self-test, or --scan [--check] --out <new-result.json> [--registration-commit <40hex>]. No target input read.'); return; }
  if (fs.existsSync(path.resolve(args.out))) throw new Error('Refusing to overwrite an existing audit result');
  const result = await runAudit(args);
  fs.mkdirSync(path.dirname(path.resolve(args.out)), { recursive: true });
  fs.writeFileSync(path.resolve(args.out), JSON.stringify(result, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
  console.log(JSON.stringify({ outcome: result.outcome, scope: result.scope,
    shapeCompatibleOccurrences: result.shapeCompatibleOccurrences,
    uniqueShapeCompatibleWindows: result.uniqueShapeCompatibleWindows,
    formatValidCandidates: result.formatValidCandidates, addressQueries: result.requestsAttempted,
    activeAddresses: result.activeAddresses, inconclusiveAddresses: result.inconclusiveAddresses,
    publicReviewNeeded: result.publicReviewNeeded }, null, 2));
}
module.exports = { candidateFingerprint, hasMinikeyShape, checkMinikey, selectedVariant,
  selectStreams, makeForms, countPositions, scanShapeWindows, publicWindow,
  deriveAddresses, validateStats, hasActivity, requestStats, checkPublicAddress,
  mapTwo, selfTest, validateProtocol, parseArgs, runAudit };
if (require.main === module) main(process.argv.slice(2)).catch(error => {
  console.error('Audit failed: ' + safeError(error)); process.exitCode = 1;
});

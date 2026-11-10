// Preregistered, read-only follow-up. Secrets and derived addresses stay private.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const audit = require('./minikey_window_audit.cjs');
const ROOT = path.resolve(__dirname, '..');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const fingerprint = value => hash(Buffer.concat([
  Buffer.from('KEY404/batch20/record-fingerprint/v1\0minikey\0', 'ascii'),
  Buffer.from(value, 'ascii')]));
const PROVIDERS = ['blockstream', 'mempool'];
const ADDRESS_TYPES = ['P2PKH uncompressed', 'P2PKH compressed', 'P2SH-P2WPKH',
  'P2WPKH', 'P2TR key-path with BIP341 TapTweak'];
function privatePath(value) {
  const resolved = path.resolve(value);
  const canonical = fs.existsSync(resolved) ? fs.realpathSync(resolved)
    : path.join(fs.realpathSync(path.dirname(resolved)),path.basename(resolved));
  const parts = canonical.split(path.sep);
  assert.ok(!parts.some(p => p.toLowerCase() === 'public'), 'Private path required');
  return canonical;
}
function writePrivate(file, value) {
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
}
function python(args) {
  const result = spawnSync('python3', ['-B', path.join(__dirname, 'independent_minikey_addresses.py'), ...args],
    { encoding: 'utf8', timeout: 30000, maxBuffer: 65536 });
  assert.equal(result.status, 0, 'Independent implementation failed');
  return JSON.parse(result.stdout);
}
function dependencyVersion(name) {
  let dir = path.dirname(require.resolve(name));
  while (path.dirname(dir) !== dir) {
    const file = path.join(dir, 'package.json');
    if (fs.existsSync(file)) {
      const pkg = JSON.parse(fs.readFileSync(file, 'utf8'));
      if (pkg.name === name) return pkg.version;
    }
    dir = path.dirname(dir);
  }
  throw new Error('Dependency metadata unavailable');
}
function selfTest() {
  assert.ok(audit.selfTest().passed);
  const independent = python(['--self-test']);
  assert.equal(independent.status, 'PASS');
  assert.equal(independent.targetInputRead, false);
  const sample = 'S6c56bnXQiBjk9mqSYE7ykVQ7NzrRy'; // Public control only.
  const expected = ['1CciesT23BNionJeXrbxmjc7ywfiyM4oLW', '1PZuicD1ACRfBuKEgp2XaJhVvnwpeETDyn',
    '3FJeDuA15H3LZuYR4E4MikQDKjTxy6DjFS', 'bc1q77xpty0n7d8arl3nnhphzp5m0dyjhumsv7usuc',
    'bc1ptrn8c2fuy92nczpejtjlwpj7h73hgftkjshhmuqdch0hr943mg8sykpkcx'];
  assert.deepEqual(audit.deriveAddresses(sample).map(a => a.address), expected);
  assert.notEqual(fingerprint(sample), hash(sample));
  const safe = publicSummary([{type:'control', provider:'blockstream', address:'PRIVATE_ADDRESS',
    status:'error', httpStatus:500}], {requestsAttempted:1});
  assert.ok(!JSON.stringify(safe).includes('PRIVATE_ADDRESS'));
  assert.equal(classify([{status:'error'}]).outcome, 'inconclusive');
  const zeroPart = {funded_txo_count:0,funded_txo_sum:0,spent_txo_count:0,spent_txo_sum:0,tx_count:0};
  const zero = {chain_stats:{...zeroPart},mempool_stats:{...zeroPart}};
  const active = {chain_stats:{...zeroPart,funded_txo_count:1,funded_txo_sum:1,tx_count:1},
    mempool_stats:{...zeroPart}};
  assert.equal(classify([{type:ADDRESS_TYPES[0],provider:PROVIDERS[0],status:'ok',
    activity:true,statistics:active}]).outcome, 'activity-detected-private-review');
  assert.equal(classify(ADDRESS_TYPES.flatMap(type => PROVIDERS.map(provider =>
    ({type,provider,status:'ok',activity:false,statistics:zero})))).outcome, 'zero-history-in-scope');
  return {passed:true, independentPythonChecks:independent.checksPassed,
    controlAddressSets:2, targetInputRead:false, addressQueries:0};
}
function cleanStatistics(result) {
  assert.ok(result && result.statistics, 'Missing response statistics');
  // Revalidate all ten numeric fields and return the audit's explicit allowlist.
  // No address is required here, and unrecognized response properties are dropped.
  return audit.validateStats({address:'statistics-validation',
    chain_stats:result.statistics.chain_stats,mempool_stats:result.statistics.mempool_stats},
  'statistics-validation');
}
function classify(results) {
  if (!Array.isArray(results)) return {outcome:'inconclusive',scopeComplete:false};
  const normalized = [];
  let invalid = false, activity = false;
  for (const result of results) {
    if (!result || !ADDRESS_TYPES.includes(result.type) || !PROVIDERS.includes(result.provider) ||
        result.status !== 'ok') { invalid = true; continue; }
    try {
      const statistics = cleanStatistics(result);
      const actualActivity = audit.hasActivity(statistics);
      activity ||= actualActivity;
      if (result.activity !== actualActivity) invalid = true;
      normalized.push({type:result.type,provider:result.provider,statistics});
    } catch { invalid = true; }
  }
  if (activity)
    return {outcome:'activity-detected-private-review',scopeComplete:false};
  if (invalid || results.length !== 10 || normalized.length !== 10)
    return {outcome:'inconclusive',scopeComplete:false};
  for (const type of ADDRESS_TYPES) {
    const pair = normalized.filter(r => r.type === type);
    if (pair.length !== 2 || JSON.stringify(pair.map(r => r.provider).sort()) !== JSON.stringify([...PROVIDERS].sort()) ||
        JSON.stringify(pair[0].statistics) !== JSON.stringify(pair[1].statistics))
      return {outcome:'inconclusive',scopeComplete:false};
  }
  return {outcome:'zero-history-in-scope',scopeComplete:true};
}
function publicSummary(results, counters) {
  assert.ok(Number.isSafeInteger(counters.requestsAttempted) && counters.requestsAttempted >= 0 &&
    counters.requestsAttempted <= 10, 'Invalid request accounting');
  return {...classify(results), requestsAttempted:counters.requestsAttempted,
    queries:results.map(r => {
      let statistics = null;
      if (r.status === 'ok') { try { statistics = cleanStatistics(r); } catch {} }
      return {type:ADDRESS_TYPES.includes(r.type) ? r.type : 'invalid',
        provider:PROVIDERS.includes(r.provider) ? r.provider : 'invalid',
        status:statistics ? 'ok' : 'error',
        httpStatus:Number.isInteger(r.httpStatus) && r.httpStatus >= 100 && r.httpStatus <= 599 ? r.httpStatus : null,
        checkedAtUTC:typeof r.checkedAtUTC === 'string' &&
          /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(r.checkedAtUTC) &&
          !Number.isNaN(Date.parse(r.checkedAtUTC)) ? r.checkedAtUTC : null,
        ...(statistics ? {activity:audit.hasActivity(statistics),statistics} : {})};
    })};
}
function validateProtocol(file, registration) {
  assert.match(registration, /^[a-f0-9]{40}$/);
  const bytes = fs.readFileSync(file);
  const protocol = JSON.parse(bytes);
  assert.equal(protocol.testId, 'global-minikey-history');
  assert.equal(protocol.candidateFingerprint, '8e402211e9f5aac9587c39f4a38ad620c797d042f76ed75bd24dca426b1cb09a');
  assert.deepEqual(protocol.addressTypes, ADDRESS_TYPES);
  assert.deepEqual(protocol.providers, PROVIDERS);
  assert.equal(protocol.requestsMaximum,10);
  assert.equal(protocol.concurrencyMaximum,2);
  assert.equal(protocol.retries,0);
  assert.deepEqual(Object.keys(protocol.scriptHashes).sort(), [
    'scripts/check_global_minikey_lead.cjs','scripts/independent_minikey_addresses.py',
    'scripts/minikey_window_audit.cjs'].sort());
  assert.deepEqual(Object.keys(protocol.sourceHashes).sort(), [
    'analysis_outputs/continuation_20261110/mirror_global_envelope/RESULT.json','package-lock.json'].sort());
  assert.deepEqual(protocol.dependencyVersions,{'bitcoinjs-lib':'7.0.0','tiny-secp256k1':'2.2.4'});
  for (const [relative, expected] of Object.entries({...protocol.sourceHashes,...protocol.scriptHashes})) {
    const actual = path.resolve(ROOT, relative);
    assert.ok(actual.startsWith(ROOT + path.sep));
    assert.equal(hash(fs.readFileSync(actual)), expected, 'Pinned file changed');
  }
  for (const [name, version] of Object.entries(protocol.dependencyVersions))
    assert.equal(dependencyVersion(name), version, 'Dependency version mismatch');
  // Verify that the actual protocol and every pinned byte existed in the supplied
  // local commit. Publication of that commit is separately verified before running.
  const files = [path.relative(ROOT,file), ...Object.keys(protocol.sourceHashes), ...Object.keys(protocol.scriptHashes)];
  for (const relative of files) {
    const saved = spawnSync('git',['show',registration + ':public/research/' + relative],
      {cwd:ROOT,maxBuffer:16*1024*1024});
    assert.equal(saved.status,0,'Registration is missing a required file');
    assert.equal(hash(saved.stdout),hash(fs.readFileSync(path.join(ROOT,relative))),'Registration bytes mismatch');
  }
  return {protocol,protocolSha256:hash(bytes)};
}
async function main(argv) {
  if (argv.length === 1 && argv[0] === '--self-test') {
    console.log(JSON.stringify(selfTest())); return;
  }
  const args = {};
  for (let i=0;i<argv.length;i+=2) {
    assert.ok(['--candidates','--protocol','--registration-commit','--out'].includes(argv[i]));
    assert.ok(argv[i+1] && !Object.hasOwn(args,argv[i])); args[argv[i]]=argv[i+1];
  }
  assert.equal(Object.keys(args).length,4);
  const protocolFile = path.resolve(args['--protocol']);
  assert.ok(protocolFile.startsWith(ROOT + path.sep));
  const {protocol,protocolSha256} = validateProtocol(protocolFile,args['--registration-commit']);
  const controls = selfTest(); // Public controls only, before opening target file.
  const input = privatePath(args['--candidates']);
  const out = privatePath(args['--out']);
  assert.ok(!fs.existsSync(out));
  assert.equal(fs.statSync(input).mode & 0o077,0,'Private candidate input required');
  assert.ok(fs.statSync(input).size < 16*1024*1024);
  fs.mkdirSync(out,{recursive:false,mode:0o700});
  const startedAtUTC = new Date().toISOString();
  const candidates = JSON.parse(fs.readFileSync(input,'utf8')).candidates.minikey;
  assert.ok(Array.isArray(candidates) && candidates.every(s => typeof s === 'string'));
  const matches = [...new Set(candidates)].filter(s => fingerprint(s) === protocol.candidateFingerprint);
  assert.equal(matches.length,1,'Expected exactly one frozen candidate');
  const candidate = matches[0];
  assert.equal(candidate.length,30);
  assert.ok(audit.checkMinikey(candidate).formatValid);
  const leadPath = path.join(out,'LEAD.private.json');
  writePrivate(leadPath,{format:'minikey',value:candidate});
  const independentPath = path.join(out,'ADDRESSES.python.private.json');
  python(['--lead',leadPath,'--out',independentPath]);
  const independent = JSON.parse(fs.readFileSync(independentPath,'utf8')).addresses;
  const addresses = audit.deriveAddresses(candidate);
  assert.deepEqual(addresses,independent,'Independent address implementations disagree');
  assert.deepEqual(addresses.map(a=>a.type),ADDRESS_TYPES);
  const counters = {requestsAttempted:0};
  const requests = addresses.flatMap(a => PROVIDERS.map(provider => ({...a,provider})));
  assert.equal(requests.length,protocol.requestsMaximum,'Unexpected request scope');
  const results = await audit.mapTwo(requests, async r =>
    ({type:r.type,...await audit.requestStats(r.provider,r.address,counters)}));
  assert.equal(counters.requestsAttempted,protocol.requestsMaximum,'Incomplete request accounting');
  writePrivate(path.join(out,'HISTORY.private.json'),{addresses,results});
  const summary = {schemaVersion:1,testId:protocol.testId,startedAtUTC,
    completedAtUTC:new Date().toISOString(),registrationCommit:args['--registration-commit'],
    protocolSha256,candidateFingerprint:protocol.candidateFingerprint,candidateLength:30,
    checksumIndependentlyVerified:true,addressImplementationsAgree:true,addressCount:5,
    ...publicSummary(results,counters),controls,transactions:0,walletImports:0,
    limitations:protocol.limitations};
  const serialized = JSON.stringify(summary);
  assert.ok(!serialized.includes(candidate));
  assert.ok(!serialized.includes(hash(Buffer.from(candidate,'ascii'))));
  for (const a of addresses) assert.ok(!serialized.includes(a.address));
  writePrivate(path.join(out,'RESULT.json'),summary);
  console.log(JSON.stringify({outcome:summary.outcome,scopeComplete:summary.scopeComplete,
    addressCount:5,addressImplementationsAgree:true,requestsAttempted:counters.requestsAttempted,
    successfulResponses:results.filter(r=>r.status==='ok').length,transactions:0}));
}
module.exports = {fingerprint,classify,publicSummary,selfTest,validateProtocol};
if (require.main === module) main(process.argv.slice(2)).catch(() => {
  console.error('Follow-up failed before a conclusive result; inspect private files locally.');
  process.exitCode=1;
});

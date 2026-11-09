// Literal 32-byte line-edge test; optional declared SHA256(first-word text) control.
// No candidate padding, transactions, or wallet imports.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const bitcoin = require('bitcoinjs-lib');
const ecc = require('tiny-secp256k1');
bitcoin.initEccLib(ecc);
const root = path.resolve(__dirname, '..');
const outDir = path.join(root, 'analysis_outputs/continuation_20261109/george_sand');
const input = path.join(root, 'analysis_outputs/continuation_20261109/fresh_cryptanalysis/printed_lines.txt');
const brainwalletMode = process.argv.includes('--firstword-sha256');
const outputName = brainwalletMode ? 'printed_firstword_sha256_keys.json' : 'printed_line_ascii_keys.json';
const pages = {};
let current = null;
for (const line of fs.readFileSync(input, 'utf8').split(/\r?\n/)) {
  const m = /^# PAGE (\d+)$/.exec(line);
  if (m) { current = Number(m[1]); pages[current] = []; continue; }
  if (/^# (GRAPHIC|SIGNATURE)/.test(line)) { current = null; continue; }
  if (current && line.trim() && !line.startsWith('#')) pages[current].push(line.trim());
}
const base58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
function b58check(body) {
  const h = b => crypto.createHash('sha256').update(b).digest();
  const all = Buffer.concat([body, h(h(body)).subarray(0, 4)]);
  let n = BigInt('0x' + all.toString('hex')), s = '';
  while (n) { s = base58[Number(n % 58n)] + s; n /= 58n; }
  for (const b of all) { if (b !== 0) break; s = '1' + s; }
  return s;
}
function p2pkh(pub) {
  const hash = crypto.createHash('ripemd160').update(crypto.createHash('sha256').update(pub).digest()).digest();
  return b58check(Buffer.concat([Buffer.from([0]), hash]));
}
const candidates = [], seen = new Set();
function addCandidate(info, key) {
  if (key.length !== 32 || !ecc.isPrivate(key)) throw new Error('Invalid private scalar');
  const hex = key.toString('hex');
  if (seen.has(hex)) return;
  seen.add(hex);
  const compressed = Buffer.from(ecc.pointFromScalar(key, true));
  const uncompressed = Buffer.from(ecc.pointFromScalar(key, false));
  const native = bitcoin.payments.p2wpkh({ pubkey: compressed });
  candidates.push({ ...info, addresses: {
    p2pkh_compressed: p2pkh(compressed), p2pkh_uncompressed: p2pkh(uncompressed),
    p2wpkh: native.address, p2sh_p2wpkh: bitcoin.payments.p2sh({ redeem: native }).address,
    p2tr: bitcoin.payments.p2tr({ internalPubkey: compressed.subarray(1) }).address,
  } });
}
for (const [page, lines] of Object.entries(pages)) {
  if (brainwalletMode) break;
  if (lines.length !== 32) continue;
  // Keep dotted contractions such as U.K.'s as one printed word.
  const words = lines.map(line => line.match(/[A-Za-z0-9]+(?:[.'’]+[A-Za-z0-9]+)*/g));
  const streams = {
    first_word_initials: words.map(ws => ws[0][0]).join(''),
    mirror_word_order_initials: words.map(ws => ws.at(-1)[0]).join(''),
    mirror_glyph_and_word_order_initials: words.map(ws => ws.at(-1).at(-1)).join(''),
  };
  for (const [method, text] of Object.entries(streams)) {
    for (const [direction, value] of [['forward', text], ['reverse', [...text].reverse().join('')]]) {
      const key = Buffer.from(value, 'ascii');
      addCandidate({ page: Number(page), method, direction, literalAscii: value }, key);
    }
  }
}
if (brainwalletMode) {
  const corpus = JSON.parse(fs.readFileSync(path.join(root,
    'analysis_outputs/continuation_20261109/fresh_cryptanalysis/printed_lines.json'), 'utf8'));
  const body = corpus.rows.filter(r => r.section === 'body');
  const units = Object.fromEntries([75, 76, 77, 78, 79].map(p => [String(p), body.filter(r => r.page === p)]));
  units.all = body;
  for (const [unit, rows] of Object.entries(units)) {
    const words = rows.map(r => r.first_word);
    for (const separator of [' ', '']) {
      const literal = words.join(separator);
      const variants = { forward: literal, reverse_word_order: [...words].reverse().join(separator),
        reverse_characters: [...literal].reverse().join('') };
      for (const [direction, value] of Object.entries(variants)) {
        addCandidate({ unit, method: 'SHA256 of exact printed first words', separator,
          direction, extractedText: value }, crypto.createHash('sha256').update(value, 'utf8').digest());
      }
    }
  }
}
async function checkAddress(address) {
  const url = `https://blockstream.info/api/address/${address}`;
  const response = await fetch(url, { signal: AbortSignal.timeout(20000) });
  if (!response.ok) throw new Error(`Address service returned HTTP ${response.status}`);
  const data = await response.json();
  if (!data.chain_stats || !data.mempool_stats) throw new Error('Missing address statistics');
  return { address, url, chainStats: data.chain_stats, mempoolStats: data.mempool_stats };
}
async function main() {
  const modelInput = brainwalletMode ? path.join(root,
    'analysis_outputs/continuation_20261109/fresh_cryptanalysis/printed_lines.json') : input;
  const result = {
    method: brainwalletMode
      ? 'First lexical word of every printed body line, each page or full body; preserve case/contractions; space-joined or joined without spaces; forward, reverse word order, or reverse characters; one SHA256 application. This wrapper is a conjecture, not an author-supplied instruction. No other hashes or salts.'
      : 'Only pages containing exactly 32 body lines; one ASCII byte per line from three declared word/character edges, each in forward/reverse order. Printed title, marginalia, and signature excluded. No padding, case variation, or hashing.',
    input: path.relative(root, modelInput), inputSha256: crypto.createHash('sha256').update(fs.readFileSync(modelInput)).digest('hex'),
    bodyLineCounts: Object.fromEntries(Object.entries(pages).map(([p, lines]) => [p, lines.length])),
    candidates, checked: false,
    limitations: [brainwalletMode ? 'The SHA256 brainwallet wrapper is an inference beyond the linked first-word method.' : 'The one-byte-per-initial interpretation is an inference beyond the linked first-word method.', 'No target address is published; absence of activity supplies no confirmation for these concrete addresses at this check.'],
  };
  if (process.argv.includes('--check')) {
    const addresses = [...new Set(candidates.flatMap(c => Object.values(c.addresses)))];
    const previousPath = path.join(outDir, outputName);
    const previous = fs.existsSync(previousPath) ? JSON.parse(fs.readFileSync(previousPath, 'utf8')) : {};
    const cache = new Map((previous.addressChecks || []).filter(v => !v.error).map(v => [v.address, v]));
    result.addressChecks = addresses.filter(a => cache.has(a)).map(a => cache.get(a));
    const remaining = addresses.filter(a => !cache.has(a));
    result.reusedAddressChecks = result.addressChecks.length;
    fs.mkdirSync(outDir, { recursive: true });
    for (let i = 0; i < remaining.length; i += 2) {
      const batch = await Promise.allSettled(remaining.slice(i, i + 2).map(checkAddress));
      for (let j = 0; j < batch.length; j++) {
        const item = batch[j];
        result.addressChecks.push(item.status === 'fulfilled' ? item.value : {
          address: remaining[i + j], error: item.reason.message,
        });
      }
      fs.writeFileSync(path.join(outDir, outputName), JSON.stringify(result, null, 2) + '\n');
      await new Promise(resolve => setTimeout(resolve, 700));
    }
    result.checked = result.addressChecks.every(v => !v.error);
    result.checkedAtUtc = new Date().toISOString();
    result.activeAddresses = result.addressChecks.filter(v => !v.error && (v.chainStats.tx_count || v.mempoolStats.tx_count));
  }
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(path.join(outDir, outputName), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify({ bodyLineCounts: result.bodyLineCounts, candidates: candidates.length,
    addressesChecked: result.addressChecks?.filter(v => !v.error).length || 0,
    failedAddresses: result.addressChecks?.filter(v => v.error) || [],
    activeAddresses: result.activeAddresses || [], checked: result.checked }));
}
main().catch(error => { console.error(error.message); process.exitCode = 1; });

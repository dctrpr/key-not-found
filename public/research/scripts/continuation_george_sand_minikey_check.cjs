const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const bitcoin = require('bitcoinjs-lib');
const ecc = require('tiny-secp256k1');
const { ECPairFactory } = require('ecpair');
bitcoin.initEccLib(ecc);
const ECPair = ECPairFactory(ecc);
const candidate = 'SihsotekaFsrenioctihst';
const secret = crypto.createHash('sha256').update(candidate).digest();
const compressed = ECPair.fromPrivateKey(secret, { compressed: true });
const uncompressed = ECPair.fromPrivateKey(secret, { compressed: false });
const cp = Buffer.from(compressed.publicKey);
const up = Buffer.from(uncompressed.publicKey);
const seg = bitcoin.payments.p2wpkh({ pubkey: cp });
const addresses = [
  { kind: 'p2pkh-compressed', address: bitcoin.payments.p2pkh({ pubkey: cp }).address },
  { kind: 'p2pkh-uncompressed', address: bitcoin.payments.p2pkh({ pubkey: up }).address },
  { kind: 'p2sh-p2wpkh', address: bitcoin.payments.p2sh({ redeem: seg }).address },
  { kind: 'p2wpkh', address: seg.address },
  { kind: 'p2tr', address: bitcoin.payments.p2tr({ internalPubkey: cp.subarray(1) }).address }
];
(async () => {
 const checks = await Promise.all(addresses.map(async x => {
  const url = `https://mempool.space/api/address/${x.address}`;
  try {
   const response = await fetch(url, { signal: AbortSignal.timeout(25000) });
   if (!response.ok) throw new Error(`HTTP ${response.status}`);
   const d = await response.json();
   return { ...x, source: url, chain_stats: d.chain_stats, mempool_stats: d.mempool_stats };
  } catch (e) { return { ...x, source: url, error: e.message }; }
 }));
 const result = { checkedAt: new Date().toISOString(), candidate, standardMinikeyChecksumValid: crypto.createHash('sha256').update(candidate + '?').digest()[0] === 0, checks };
 const out = path.join(__dirname,'../analysis_outputs/continuation_20261109/george_sand/minikey_activity.json');
 fs.writeFileSync(out, JSON.stringify(result,null,2) + '\n');
 console.log(JSON.stringify({ checksumValid: result.standardMinikeyChecksumValid, checks: checks.map(c=>({kind:c.kind,address:c.address,txCount:c.chain_stats?.tx_count,mempoolTxCount:c.mempool_stats?.tx_count,error:c.error})) }));
})();

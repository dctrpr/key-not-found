# Issue27 checksum lead: five-address history check

The registered frozen Issue27 stream replay completed at 2026-11-10T09:13:14.337Z. It checked 1,940 saved readings and their already used codepoint reversals: 3,880 submitted records, with exact and whitespace-only-compacted forms deduplicated by the registered scanner. An independent implementation matched every saved record against the pinned source and reproduced the complete evaluation. One of 205 distinct minikey-shaped values passed the one-byte checksum; it is 22 characters long. This remains a weak lead: 205 uniformly distributed checks would produce about 0.80 chance passes on average.

Selected-lead files, its SHA-256 private scalar, source locators and derived-address association stay outside this report and the new public outputs. The underlying frozen readings are already public and reproducible; this does not guarantee secrecy of an extracted value. The public identifier is the domain-separated fingerprint in `PROTOCOL.json`; it is **not** SHA256(candidate). The frozen source result must be complete and report exactly one valid minikey, with the registered fingerprint, 22-character length and eight-bit checksum metadata. All other registered formats must have zero valid records.

Publish this protocol, the exact safe source result and every pinned implementation before target derivation or explorer requests. The primary replay is registered at commit `070f8b712d9fd5b6b6fa3f5355d612fcbaa7f192`. This follow-up is a separate registration: the root researcher verifies its new commit is published before execution.

Derive exactly five Bitcoin mainnet addresses using the unchanged Node bitcoinjs-lib/tiny-secp256k1 implementation and independent Python standard-library implementation:

1. P2PKH with an uncompressed SEC public key.
2. P2PKH with a compressed SEC public key.
3. P2SH wrapping P2WPKH with the compressed public key.
4. Native P2WPKH with the compressed public key.
5. Key-only P2TR: lift the x-only internal key to even Y, apply the BIP341 TapTweak with no script tree, encode with Bech32m.

Require exact agreement on all five type/address pairs before any request. Run public-format and scalar-one controls first. Synthetic 22-character valid/invalid controls and exact five-address implementation agreement have also been checked privately. Control addresses are never queried. No HD path, password, arbitrary prose hash, multisig script, testnet, wallet import, signing or transaction is included.

Query both `blockstream.info` and `mempool.space` address-summary endpoints for every registered address: ten attempts maximum, no retries, at most two simultaneous requests, 20-second timeout each, redirects rejected and no-cache requested. A complete check makes exactly ten attempts. Require the returned address to match, all five standard statistics in both chain and mempool sections to be safe nonnegative integers, and zero-transaction sections to have all-zero statistics. A failed request, malformed response, provider disagreement or derivation failure is inconclusive. Any validated activity requires private review and does not authenticate the puzzle or prize.

Only ten successful, mutually agreeing all-zero responses support **zero history within these five registered address constructions at the recorded check times**. This excludes a funded interpretation of this particular checksum lead within those constructions according to these providers. It does not exclude the entire puzzle, other wallet constructions or later funding, or establish the creator's intended rule.

Publish only the reviewed allowlist: counts, UTC times, provider status and numeric statistics. Keep the candidate, private scalar, source locators and address association out of Git, downloads and public logs. The executable checks local registration-commit bytes and pinned inputs; the root researcher separately verifies publication before running it.

References: [minikey specification](https://en.bitcoin.it/wiki/Mini_private_key_format), [Esplora address summary](https://github.com/Blockstream/esplora/blob/master/API.md#addresses), [BIP341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki#constructing-and-spending-taproot-outputs), [BIP173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki), [BIP350](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki).


## Reproduce after public registration

From `public/research` in a Git checkout, install the pinned research dependencies with `npm ci` and run `node scripts/check_issue27_minikey_lead.cjs --self-test`. First reproduce the [registered extraction and independent saved-reading audit](../issue27_stream_coverage/PROTOCOL.md). They produce `READINGS.private.jsonl` in a private directory.

This offline export selects only the frozen fingerprint from that replay. It performs no address derivation or query. Run it from the research root; change only the private input/output filenames:

```python
import json, os, sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, 'scripts')
from batch20_common import shape_values, fingerprint, wordlist
source = Path('/tmp/key404-private/replay/READINGS.private.jsonl').resolve()
out = Path('/tmp/key404-private/CANDIDATES.private.json').resolve()
assert 'public' not in (part.lower() for part in source.parts + out.parts)
assert source.stat().st_mode & 0o077 == 0 and source.stat().st_size < 32000000
records = [json.loads(line) for line in source.read_text().splitlines()]
assert len(records) == 3880
indexes = wordlist()[1]
forms = {r['text'] for r in records}
forms |= {''.join(text.split()) for text in forms}
assert len(forms) <= 7760 and sum(map(len, forms)) <= 4000000
fixed = 'd0ad21f0839baa35c7789a8a1de80408bd9eba6e8a0102a2a055bf4af8100203'
values = {value for text in forms for value in shape_values('minikey', text, indexes)
          if fingerprint('minikey', value.encode('ascii')) == fixed}
assert len(values) == 1 and len(next(iter(values))) == 22
with os.fdopen(os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as handle:
    json.dump({'candidates': {'minikey': sorted(values)}}, handle)
```

Then run only after replacing `REGISTRATION_COMMIT` with this follow-up’s first public registration commit:

```sh
node scripts/check_issue27_minikey_lead.cjs --candidates /tmp/key404-private/CANDIDATES.private.json --protocol analysis_outputs/continuation_20261110/issue27_minikey_history/PROTOCOL.json --registration-commit REGISTRATION_COMMIT --out /tmp/key404-private/issue27-history
```

Use a fresh private output directory with an existing parent. Offline [controls](CONTROL_RECEIPT.json) and [independent review](INDEPENDENT_REVIEW.json) passed before target construction or queries. Only the reviewed aggregate `RESULT.json` may be considered for publication. A later rerun observes its own check time, not the earlier explorer snapshot.

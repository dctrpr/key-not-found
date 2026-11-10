# One 26-character checksum lead — bounded history follow-up plan

The separately registered historical 26-character compatibility replay completed at 2026-11-10T11:20:30.256Z after public registration `96e206c0a86d8b2b62b4cf323862d54934927929`. Its safe RESULT reports 207 distinct shaped values and one checksum-valid 26-character minikey. The public identifier is domain-separated fingerprint `16a4c57bfd34fa3663560b3eb13ec981aed6df399d8d5701e69716cbe7c435c1`; it is not the minikey’s SHA256 private scalar. Raw target candidates were not opened during this build.

One byte of checksum is weak evidence: 207/256 is about 0.81 expected passes if checks were uniformly distributed. Source-model/witness review is separate, and no source mechanism, prize or ownership is authenticated by this checksum. The next finite question is whether this one unchanged lead has any transaction history under the same five ordinary constructions previously used for other leads.

Publish the unchanged safe source RESULT, new protocol and all three new scripts in a separate registration before opening the private candidate set, deriving the target scalar/addresses or issuing a live request. Root verifies the public registration. The original replay did not authorize an automatic history check, and this build does not perform one.

## Exact derivation and request scope

Use the minikey’s standard ASCII SHA256 scalar, then derive exactly:

1. P2PKH from an uncompressed SEC public key.
2. P2PKH from a compressed SEC public key.
3. P2SH-P2WPKH with the compressed public key.
4. Native P2WPKH with the compressed public key.
5. Key-only P2TR: even-Y x-only internal lift, BIP341 TapTweak, no script tree, Bech32m encoding.

Require exact Node/Python agreement on all five type/address pairs before any network request. The Node bitcoinjs-lib 7.0.0/tiny-secp256k1 2.2.4 and independent Python arithmetic are unchanged from the prior reviewed methodology. Separate dependency forks add 26 to their existing 22/30 input length gates so the historical format is admitted while original published/scalar-one controls remain valid. The history wrapper itself accepts only 26 and the exact frozen fingerprint. No HD paths, passphrases, arbitrary prose hashes, alternative scripts or extra candidate edits are included.

For each of the five mainnet constructions, query both fixed Esplora providers, blockstream.info and mempool.space: **ten attempts maximum, no retries, at most two simultaneous requests**, 20-second timeout, redirects rejected and no-cache requested. A complete check makes exactly ten attempts. Validate the returned address and all five nonnegative safe-integer fields in both chain_stats and mempool_stats; zero-transaction sections must have all-zero statistics. Revalidate statistics before public summarization. Any request, derivation, source/code pin, provider disagreement or malformed-statistics failure is inconclusive, never a zero result. Any validated activity requires private review and does not itself establish a solution.

Only ten successful, agreeing all-zero responses support **zero history within these five constructions at the recorded times according to these two providers**. That excludes a funded interpretation of this specific checksum lead within the declared constructions. It does not exclude every wallet construction, future funding or the puzzle as a whole.

## Frozen files, controls and privacy

The private code is quiescent:

- check_minikey26_lead.cjs — 98146d0f97b359b5830991048974474290cac4f1cd97218986af9b334f744e44.
- minikey26_address_audit.cjs — a351e20f4bb5b9ab20fdd97dc07f8d87afe48962fb25dff20a008a56e83b7a64.
- independent_minikey26_addresses.py — 27f1de62281f4c4e43906acd65f9ae8fa6b264d5dc4cf54a3faf998719479ba8.

The safe source RESULT pin is 8eb395f125c9c8eb953ad0c6db8a2d662b517099fdc5763e5e69503918d2e30e at intended public path `analysis_outputs/continuation_20261110/minikey26_compatibility/RESULT.json`. Keep those JSON bytes unchanged. The protocol additionally pins the research package-lock and all three scripts. The checker verifies their local hashes and exact saved registration-commit bytes, including the protocol itself, before opening target material.

The Node dependency fork disables the legacy article-scanner CLI/export surface and exposes only history/control functions. The Python fork’s only code change is its accepted-length tuple. The existing code/results are not edited. Exact diffs are saved alongside the code.

CONTROL_RECEIPT.json passes: 32 original Python self-checks; five explicit 26-format checks; synthetic 26 exact five-address Node/Python agreement; 23 frozen-result guard rejection cases; 15 classifier cases; five error/no-retry mocks; ten successful mock requests with measured concurrency two; safe output omission checks. Target candidate/readings opens, target derivations and live requests remain zero. Synthetic scalar/address material is private control data, not the target.

Raw candidate, scalar, address association and response details remain in fresh private 0700 directories and 0600 files. Only reviewed fingerprints, counts, provider status, UTC times and allowlisted numerical statistics are suitable for publication. The public JSON is checked against raw candidate/scalar-hash/address inclusion. No wallet import, signing or transaction action is included. No full candidate set or synthetic raw address fixture should be copied into the public tree.

References: [minikey format](https://en.bitcoin.it/wiki/Mini_private_key_format), [Esplora address summary](https://github.com/Blockstream/esplora/blob/master/API.md#addresses), [BIP341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki), [BIP173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki), [BIP350](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki).

## Reproduction

From a Git clone's public research directory, run `npm ci` with the committed research lockfile, then:

```sh
node scripts/check_minikey26_lead.cjs --self-test
```

Target execution additionally requires the exact public registration commit and a private candidate bundle from the prior registered extraction. It is not part of the self-test. A fresh private output directory and all pinned Git bytes are required. The completed report will record the exact command and check times.

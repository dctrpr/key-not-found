# One weak minikey lead: fixed read-only follow-up

The global mirror-language audit completed at 2026-11-10T07:18:12.995Z after registration `115f477f29fe7d57785276529026e92b8c9e49cb`. It found one checksum-valid 30-character minikey among 382 distinct shaped values. An independent SHA-256 implementation confirmed that one-byte check. This is weak evidence: 382 uniformly distributed checks would have about 1.49 chance passes on average. The investigator's enlarged boundary model also permits mutually inconsistent physical choices.

The raw candidate, its SHA-256 private scalar, derivation witness and derived-address association remain private. The public identifier is the domain-separated fingerprint in `PROTOCOL.json`; it is **not** SHA256(candidate).

Before target address derivation or explorer queries, publish this protocol and its pinned implementations. Derive exactly these five Bitcoin mainnet addresses, once each, using Node bitcoinjs-lib/tiny-secp256k1 and an independent Python standard-library implementation:

1. P2PKH with an uncompressed SEC public key.
2. P2PKH with a compressed SEC public key.
3. P2SH wrapping P2WPKH with the compressed public key.
4. Native P2WPKH with the compressed public key.
5. Key-only P2TR: lift the x-only internal key to even Y, apply the BIP341 TapTweak with no script tree, encode with Bech32m.

Require exact agreement on all five type/address pairs before any network request. Run public-format and scalar-one controls first; never query control addresses. No arbitrary hash wrapper, password, HD path, multisig script, testnet, wallet import, signing or transaction is included.

Query the address-summary endpoint of both `blockstream.info` and `mempool.space` for every address: exactly ten attempts, no retries, at most two simultaneous requests, 20-second timeout each, redirects rejected and no-cache requested. Read both chain and mempool statistics. Require the returned address to match, all five standard statistics in both sections to be safe nonnegative integers, and zero-transaction sections to have all-zero statistics. A request failure, malformed response, provider disagreement or derivation failure is inconclusive, never a zero result. Any observed activity requires private review and does not authenticate the puzzle or prize.

Only ten successful, agreeing all-zero responses support **zero history within these five registered address constructions at the recorded check times**. That excludes this lead as a previously funded or currently funded key under those constructions according to the two providers. It does not prove the entire puzzle empty, exclude other wallet constructions or establish the creator's intended rule.

Publish only reviewed counts, UTC times, provider status and numerical statistics. Keep the candidate, private scalar, source locators and address association out of Git, downloads and public logs. The executable checks local registration-commit bytes and pinned inputs; the coordinating researcher verifies the same commit is published before running it.

References: [minikey specification](https://en.bitcoin.it/wiki/Mini_private_key_format), [Esplora address summary](https://github.com/Blockstream/esplora/blob/master/API.md#addresses), [BIP341 Taproot construction](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki#constructing-and-spending-taproot-outputs), [BIP173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki), [BIP350](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki).

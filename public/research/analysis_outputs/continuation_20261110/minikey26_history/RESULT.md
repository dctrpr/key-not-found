# 26-character lead: zero reported history in five constructions

Completed **2026-11-10T11:39:48.621Z**. The separately registered [protocol](PROTOCOL.json) and three implementations were public in commit [`b5ea6bc083a856ce7245a5b86a9748f16cbb380d`](https://github.com/dctrpr/key-not-found/commit/b5ea6bc083a856ce7245a5b86a9748f16cbb380d) before target derivation and requests. Root verified the remote commit first; the independent saved-result review separately verified all local committed bytes.

Independent Python and Node derivations agreed exactly on five fixed mainnet address constructions: uncompressed P2PKH, compressed P2PKH, P2SH-P2WPKH, P2WPKH and key-only BIP341-tweaked P2TR.

| Construction | Blockstream | mempool.space |
|---|---|---|
| P2PKH uncompressed | HTTP 200; all statistics zero | HTTP 200; all statistics zero |
| P2PKH compressed | HTTP 200; all statistics zero | HTTP 200; all statistics zero |
| P2SH-P2WPKH | HTTP 200; all statistics zero | HTTP 200; all statistics zero |
| P2WPKH | HTTP 200; all statistics zero | HTTP 200; all statistics zero |
| P2TR key path | HTTP 200; all statistics zero | HTTP 200; all statistics zero |

All ten responses succeeded and agreed by construction. All 100 chain/mempool numerical fields were zero. Requests started between **11:39:47.163Z and 11:39:48.504Z on 2026-11-10**; these timestamps are request starts, not response end times. The fixed code makes each request once, with no retries and concurrency at most two. No request error was converted into zero.

This supplies **no funding evidence for this specific lead through these five constructions at those times, according to the two providers**. Other wallet scripts, HD derivations, future funding and the wider puzzle remain open. This is not a full-node proof.

The mini key remains format-valid. Its [source witness](../minikey26_compatibility/SOURCE_WITNESS_REVIEW.md) needs uncertain membership choices and no nominal reading matches it; creator intent is not established. The safe domain-separated fingerprint is `16a4c57bfd34fa3663560b3eb13ec981aed6df399d8d5701e69716cbe7c435c1`. It is not the private scalar. Raw candidate, scalar, source locators, derived addresses and their association are omitted. No wallet import, signing or transaction occurred.

[RESULT.json](RESULT.json) retains the allowlisted provider statistics, check times and scope. The [independent saved-result review](INDEPENDENT_RESULT_REVIEW.json) matched the five saved address records, all ten request pairs, all statistics and source/code/protocol pins. It did not repeat target derivation or queries.

## Reproduce

From a Git clone's public research directory, install the committed research lockfile with `npm ci`. First reproduce the [fixed 26-character extraction](../minikey26_compatibility/RESULT.md) into a fresh private directory. Then run the history protocol with its exact registration commit:

```sh
node scripts/check_minikey26_lead.cjs --candidates /tmp/key404-26-replay/CANDIDATES.private.json --protocol analysis_outputs/continuation_20261110/minikey26_history/PROTOCOL.json --registration-commit b5ea6bc083a856ce7245a5b86a9748f16cbb380d --out /tmp/key404-26-history
```

This repeats ten read-only explorer requests and creates private derivation/response files. Future responses may change. Preserve the archived source RESULT bytes; the history protocol pins them exactly.

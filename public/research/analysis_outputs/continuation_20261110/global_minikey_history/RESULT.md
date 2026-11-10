# One checksum lead — zero history in the registered scope

Completed **2026-11-10T07:40:54.968Z**. **The puzzle remains unsolved.**

The global mirror audit’s single checksum-valid 30-character candidate was checked through **five fixed Bitcoin mainnet address constructions**. Independent Python and Node implementations agreed on all five addresses before any request. Both Blockstream and mempool.space then returned successful responses for every construction: **10/10 HTTP 200 responses, with all confirmed-chain and current-mempool statistics equal to zero**.

The recorded lookup start times were 2026-11-10T07:40:53.482Z through 07:40:54.852Z. These are dated observations, not a live balance display.

| Registered construction | Python/Node agreement | Blockstream | mempool.space |
| --- | --- | --- | --- |
| P2PKH, uncompressed public key | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |
| P2PKH, compressed public key | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |
| P2SH-P2WPKH, compressed public key | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |
| Native P2WPKH, compressed public key | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |
| Key-path P2TR, even-Y internal key and BIP341 TapTweak | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |

Each response reported zero for funded-output count and sum, spent-output count and sum, and transaction count, in both `chain_stats` and `mempool_stats`. No request failure was treated as a zero result. The [safe machine result](RESULT.json) preserves the provider status, exact check times and numerical statistics. Candidate value, private scalar, source locators and derived-address association remain private.

## What this rules out

According to these two providers at the recorded times, this one candidate has no recorded confirmed funding/spends or current pending activity through the **five registered constructions**. Its funded-key interpretation within that scope has no supporting history.

The minikey remains format-valid: this follow-up does not negate its 8-bit checksum pass. A pass among 382 shaped values is compatible with chance. The geometric source model also admits uncertain and potentially inconsistent physical choices. Neither the checksum nor a modeled source witness authenticates creator intent, ownership or the 20-BTC claim.

This is not a full-node proof and does not exclude other scripts, HD derivations, multisig constructions, encodings, source rules or future funding. It does not rule out the whole puzzle. No wallet import, signing operation or transaction was performed.

## Registration and evidence

The protocol and pinned files were public before derivation and explorer queries in commit [`60c89c862e6430a1db8e706c03bfdd44d0ff8c30`](https://github.com/dctrpr/key-not-found/commit/60c89c862e6430a1db8e706c03bfdd44d0ff8c30). See the [fixed protocol](PROTOCOL.md), [machine protocol](PROTOCOL.json), [preceding global extraction](../mirror_global_envelope/RESULT.md) and [safe result](RESULT.json). The earlier global extraction result is preserved unchanged.

## Reproduce

The checker requires a repository checkout containing the registration commit, the pinned research dependencies, Node and Python 3.10+. From `public/research` in that checkout, the offline controls are:

```sh
npm ci
node scripts/check_global_minikey_lead.cjs --self-test
```

A fresh global extraction run can regenerate its candidate set in a private directory. To repeat the explicitly scoped lookup with that private file and a new output directory:

```sh
node scripts/check_global_minikey_lead.cjs --candidates /tmp/key404-private/CANDIDATES.private.json --protocol analysis_outputs/continuation_20261110/global_minikey_history/PROTOCOL.json --registration-commit 60c89c862e6430a1db8e706c03bfdd44d0ff8c30 --out /tmp/key404-private/history-rerun
```

The parent private directory must exist; the candidate file must have mode 600 and the output directory must not already exist. The checker verifies exactly one candidate by the frozen domain-separated fingerprint, requires Python/Node agreement, and makes only the ten registered attempts without retries. A new lookup produces observations at its own time; it cannot recreate an earlier explorer snapshot. Keep raw outputs private and publish only the reviewed summary.

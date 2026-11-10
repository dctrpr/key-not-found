# Issue 27 checksum lead: five constructions, zero history

Completed **2026-11-10T09:23:54.318Z**. **The puzzle remains unsolved.**

The saved-reading replay’s single checksum-valid 22-character minikey was checked through five fixed Bitcoin mainnet address constructions. Independent Python and Node implementations agreed on every address before any request. Blockstream and mempool.space returned **10/10 successful HTTP 200 responses, with all confirmed-chain and current-mempool statistics equal to zero**.

Lookup start times span 2026-11-10T09:23:52.845Z through 09:23:54.201Z. These are dated observations, not a live balance display.

| Construction | Python/Node agreement | Blockstream | mempool.space |
| --- | --- | --- | --- |
| P2PKH, uncompressed public key | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |
| P2PKH, compressed public key | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |
| P2SH-P2WPKH | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |
| Native P2WPKH | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |
| Key-path P2TR with BIP341 TapTweak | Yes | HTTP 200 · zero statistics | HTTP 200 · zero statistics |

Each response reported zero funded-output count and sum, spent-output count and sum, and transaction count, in both chain and mempool sections. No error was treated as zero. The [safe machine result](RESULT.json) preserves all statuses, times and numeric statistics. The [independent saved-result review](INDEPENDENT_RESULT_REVIEW.json) checks the complete provider matrix and private/public output agreement without another query. Selected-lead files, private scalars and candidate-associated addresses are excluded from this report. Its original source readings remain public and reproducible; they do not guarantee secrecy of an extracted value.

## What this excludes

At these times, neither provider reported confirmed funding, spends or current pending activity for this one lead through the five registered constructions. Its funded-key interpretation has no supporting history in that scope.

The minikey remains format-valid. An eight-bit checksum pass among 205 shaped strings is compatible with chance and does not authenticate creator intent or a prize. These historical Orange Party readings also retain OCR and investigator-selection limits. The column is relevant to the broad December 2022 plural-key post, not authenticated as the March 2023 Issue 24 target.

This is not a full-node proof. Other scripts, HD paths, multisig, encodings, reading rules and future funding remain outside scope. It does not rule out the whole puzzle. No wallet import, signing operation or transaction occurred.

## Registration and reproduction

The follow-up protocol, safe extraction result and pinned implementations were public before address construction or network queries in commit [`c0a18628b1f63dace8c937419a8a068d62c4c73d`](https://github.com/dctrpr/key-not-found/commit/c0a18628b1f63dace8c937419a8a068d62c4c73d). The [earlier replay](../issue27_stream_coverage/RESULT.md) retains its original machine result unchanged.

See [the protocol, offline export recipe and reproduction commands](PROTOCOL.md), [machine protocol](PROTOCOL.json), [controls](CONTROL_RECEIPT.json), [independent pre-execution code review](INDEPENDENT_REVIEW.json) and [safe result](RESULT.json). Replace `REGISTRATION_COMMIT` in the command with the full commit above. Reruns observe their own times; keep raw output private.

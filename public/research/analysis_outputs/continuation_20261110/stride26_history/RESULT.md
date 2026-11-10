# Stride26 lead: five constructions, zero history in scope

Completed **2026-11-10T20:26:00.675Z**. Node and independent Python agreed exactly on five ordered mainnet address constructions for the unchanged 26-character checksum lead. **All ten provider responses returned HTTP 200**, with all chain and mempool statistics zero. The two providers agreed for every construction. No funding evidence was found within this registered scope at the recorded times.

The lead remains an eight-bit minikey checksum pass. It requires the earlier registered whitespace-compacted form and is not contiguous in any unmodified reading; the saved source-known association is not creator intent or a demonstrated printed key. Zero explorer history does not make the whole puzzle false, exclude every wallet construction or predict future funding.

| Construction | Blockstream | mempool.space |
| --- | --- | --- |
| P2PKH, uncompressed public key | HTTP 200, zero chain/mempool | HTTP 200, zero chain/mempool |
| P2PKH, compressed public key | HTTP 200, zero chain/mempool | HTTP 200, zero chain/mempool |
| P2SH-P2WPKH | HTTP 200, zero chain/mempool | HTTP 200, zero chain/mempool |
| P2WPKH | HTTP 200, zero chain/mempool | HTTP 200, zero chain/mempool |
| P2TR, BIP341 key-path TapTweak, no script tree | HTTP 200, zero chain/mempool | HTTP 200, zero chain/mempool |

The run made exactly ten read-only attempts, with maximum concurrency two and no retries. Redirects were rejected; each request had a 20-second timeout. The wrapper required exact HTTP 200 and validated matching addresses and all ten nonnegative safe-integer statistics in each response. An error, incomplete coverage or disagreement would have been inconclusive, not zero.

## Evidence and reproduction

The [protocol](PROTOCOL.md), its [machine form](PROTOCOL.json), the adapter and all pinned files were published in [`6b4885388deafb96bd735145fcd7ac5fcd3bc66d`](https://github.com/dctrpr/key-not-found/commit/6b4885388deafb96bd735145fcd7ac5fcd3bc66d). Root verified the remote head at **20:25:39.372Z**, before invoking the run. The address/history phase began at **20:25:59.158Z**; no request preceded full Node/Python address agreement.

- [Safe machine result with all ten timestamped statistics](RESULT.json).
- [Registration](REGISTRATION.json) and [execution accounting](EXECUTION.json).
- [Independent complete saved-receipt verification](INDEPENDENT_VERIFICATION.json).
- [Static review](CODE_REVIEW.md), [source-free controls](CONTROL_RECEIPT.json), and [independently instrumented request controls](CONTROL_REVIEW.json).
- [Originating replay](../columns_compatibility/RESULT.md) and [reviewed compaction-dependent source association](../columns_compatibility/SOURCE_WITNESS_REVIEW.md).

Follow the protocol with the full registration commit above, the reproduced byte-identical combined validation artifact and fresh private output. The unchanged Node/Python address helpers and shared result classifier are disclosed dependencies. The public receipt omits the value, candidate fingerprint, scalar, raw address and candidate-linked source locations. Whole private-file hashes in the execution receipt authenticate the saved record.

The history check involved no new reading rule, OCR or source repair. No wallet was imported, no transaction was signed or sent, and no prize BTC or research expense is claimed. Other constructions, encodings, readings and the puzzle remain open. The photographed March Issue 24 target is unchanged; this comparison-column lead is not an authenticated 20-BTC target.

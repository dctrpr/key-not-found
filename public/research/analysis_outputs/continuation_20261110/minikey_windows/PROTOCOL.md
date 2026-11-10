# Embedded minikey coverage audit — preregistered protocol

## Why this test

The earlier printed-line probe scans WIF windows but checks minikeys only when the entire compacted stream is exactly 22 or 30 characters. That can miss a short key inside a longer reading. The original file remains unchanged so the omission stays auditable: `analysis_outputs/continuation_20261109/fresh_cryptanalysis/george_sand_printed_probe.js`.

This audit closes that concrete validation gap. It does not introduce a new cipher or claim that all George Sand readings were untested.

## Fixed before execution

Use only the body, without highlight/bold filtering. Select existing whole odd/even-line readings and all-line first-word/initial readings, with existing global/page resets and both mirror directions. The selector in `PROTOCOL.json` fixes 22 existing streams and 42 distinct text/whitespace-compacted forms. Preserve case and punctuation; do not add substitutions or transformations.

Scan every position of lengths 22 and 30: 113,830 and 113,494 positions respectively, 227,324 total before alphabet checks/deduplication. Require uppercase S, Base58 characters and the minikey’s defined one-byte typo check. Only candidates passing that check get the format-defined private-scalar conversion and five declared public-address forms. No arbitrary hash wrapper is applied to prose.

Primary technical format: [BitcoinWiki minikey specification](https://en.bitcoin.it/wiki/Mini_private_key_format). Creator method: [26 December 2022 post](https://x.com/maxkeiser/status/1607378060172460032), linking [George Sand examples](https://ciphermysteries.com/2010/05/16/george-sands-cryptography). The source connection to this issue remains an inference. The minikey format itself is not stated in the creator clue.

## Decision rule

- Zero format-valid candidates: no embedded 22/30 minikey in these exact forms.
- Candidates with completely successful, independently cross-checked zero-transaction results: no activity for the declared key/address forms at the recorded time.
- A checksum pass alone is weak evidence (8 bits), not a solution. Activity triggers private review and corroboration, not an automatic prize claim.
- Any hash, scope or control failure stops the run. Any unresolved lookup prevents a complete negative activity conclusion.

No added lengths, case changes, padding, fitted offsets, salts, repeated hashes or extra derivation paths. Another hypothesis needs another protocol.

## Reproduce

From `public/research`, run `node scripts/minikey_window_audit.cjs --self-test`. Then use `node scripts/minikey_window_audit.cjs --scan --check --out analysis_outputs/continuation_20261110/minikey_windows/RESULT.json`. The offline scan uses Node’s standard library; address derivation, only if needed, uses the existing locked research dependencies (`npm ci`). The explicit `--check` flag enables read-only public-address requests; no wallet import or transaction is performed.

The protocol and implementation are committed before the target scan. Exact input hashes, selected-stream/form IDs, every tested alphabet-compatible window locator, control results, lookup failures and outcome will be preserved. Candidate secrets are not printed. Historical results stay intact.

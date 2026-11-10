# One stride26 checksum lead: bounded history check

The separate [four-population replay](../columns_compatibility/RESULT.md) found one 26-character minikey checksum pass. Its [saved-form source association](../columns_compatibility/SOURCE_WITNESS_REVIEW.md) is reviewed. It requires registered whitespace compaction, occurs in the source-known subset, and is not contiguous in any unmodified reading. No printed key, creator intent or prize is authenticated.

This protocol selects only the single unchanged positive from the whole byte-pinned private validation artifact, requiring the complete nominal and cached source-known records to agree. No new candidate, reading, transform or source repair is introduced. There is no public candidate fingerprint or raw value.

After public registration, the unchanged Node and independent Python helpers must agree exactly on five ordered mainnet address constructions: uncompressed P2PKH, compressed P2PKH, P2SH-P2WPKH, P2WPKH and BIP341 key-path P2TR with no script tree. Their synthetic and published-vector checks precede the target. The standard minikey scalar is used privately inside those helpers; it is not saved or used as an identifier.

Only after full address agreement, make exactly ten read-only GET attempts: each construction at Blockstream and mempool.space. Maximum concurrency two, 20-second timeout per request, no retries, no redirects. This new wrapper requires exact HTTP 200, even though its frozen request helper accepts other 2xx statuses. Matching addresses and all ten nonnegative safe-integer chain/mempool statistics per response are checked. Every failure or provider disagreement is inconclusive, never zero. Any validated activity requires private review and does not authenticate ownership or a prize.

The machine protocol pins three public sources and four code files, plus its own actual Git commit bytes. Current files must match the published commit before target input, derivation or requests. The previous frozen scripts remain unchanged. Two reviewers checked the thin adapter and bounded synthetic requests; shared old helper code is disclosed rather than counted as a newly independent implementation.

## Reproduce

Use a Git clone containing the published registration commit, Node and Python 3.9+, and the research dependencies installed from the pinned lockfile (`npm ci` in `public/research`). First reproduce the combined replay's private `VALIDATION.private.json` using its registered commands. Then, from `public/research`:

```sh
task_private="$(mktemp -d /tmp/key404-stride26.XXXXXX)"
node scripts/check_stride26_lead.cjs --self-test
node scripts/check_stride26_lead.cjs \
  --validation /ABSOLUTE/PRIVATE/REPLAY/VALIDATION.private.json \
  --protocol analysis_outputs/continuation_20261110/stride26_history/PROTOCOL.json \
  --registration-commit PUBLISHED_REGISTRATION_COMMIT \
  --out "$task_private/history"
```

Replace the commit placeholder with the full registration commit recorded by the eventual result. Use fresh private output outside the entire checkout, 0700 directories and 0600 files. Raw candidate and address/history files remain private. The public result allowlists types, providers, timestamps, response statistics, aggregate controls and outcomes, excluding value/fingerprint/address associations. An independent saved-receipt review follows the run without repeating target derivation or requests.

Zero history would cover only these five constructions, two providers and recorded times. Other constructions, future funding, different readings and the puzzle remain open. There is no wallet import, signing, transaction or claim of recovered BTC.

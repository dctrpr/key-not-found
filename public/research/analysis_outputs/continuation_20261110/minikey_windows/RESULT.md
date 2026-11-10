# Embedded minikey audit: no valid candidate in the declared readings

## Result

**This finite test is complete. No checksum-valid 22- or 30-character minikey occurs in the declared 42 text forms.** The puzzle remains unsolved.

The scan covered 22 existing body-only George Sand readings, yielding 42 distinct exact or whitespace-compacted forms. Across 227,324 possible positions, 17 occurrences met the minikey alphabet/length rules. They represented **12 distinct strings**. Every one failed the minikey’s defined one-byte checksum. No target candidate private scalar was derived, no address was queried, and no transaction or wallet action occurred.

An independent Python implementation agreed on all 12 domain-separated candidate fingerprints, all counts and zero valid candidates. Positive controls found known valid minikeys embedded in surrounding text—the exact condition the old whole-stream test missed. Invalid prefix, alphabet, length and checksum controls also passed.

## Why this was worth checking

The earlier printed-line validator checked WIF windows but accepted a minikey only if the entire compacted reading was exactly 22 or 30 characters. A shorter key inside a longer reading could escape that gate. This run closes that specific coverage gap for the tight body-only selection. The earlier script/results remain unchanged, and the current ledger now states their original minikey limitation explicitly.

These are repeated position checks under one rule. We record **one coverage correction**.

## Registered before execution

[Protocol and implementation commit](https://github.com/dctrpr/key-not-found/commit/6010d9310f678a0380939fe98f2820f41c6a3f68). The public commit was confirmed before the first target scan.

- Input SHA-256: `1651a33dab46babf36f56439ddb409058cfa36712d96ead7d4200962b80817b9`.
- Protocol SHA-256 at execution: `440cf217a78d21a875029270d53af1402cf13261f183e330367016e3581319ed`.
- Primary script SHA-256 at execution: `189c6f359a057021adbc060ddeaa8caa29e6f58c40a6976daeda62025d2182f0`.
- Started: `2026-11-10T04:16:03.622Z`; completed: `2026-11-10T04:16:03.682Z`.
- Exact scope: 113,830 windows of length 22; 113,494 of length 30.

The fixed selection uses body text, no highlight/bold filters, existing odd/even whole-line readings and all-line first words/initials, existing page/global resets and existing directions. Case and punctuation stay exact. Whitespace-only compaction is the only additional form. There was no expansion after seeing the outcome.

The [minikey format specification](https://en.bitcoin.it/wiki/Mini_private_key_format) defines standard 30-character and legacy 22-character forms, their typo check and secret conversion. The [creator’s December clue](https://x.com/maxkeiser/status/1607378060172460032) links the [George Sand line/first-word mechanism](https://ciphermysteries.com/2010/05/16/george-sands-cryptography); it does not specify minikeys. Applying that format is an explicit hypothesis.

## Exact evidence and reproduction

- `PROTOCOL.md` / `PROTOCOL.json`: fixed rule and stopping conditions.
- `RESULT.json`: selected stream/form IDs, source-row metadata, each distinct shaped string’s non-secret fingerprint, checksum first byte and exact window locators. Candidate secrets are omitted.
- `INDEPENDENT_CHECK.json`: independent regex/hashlib counts and fingerprint verdicts.
- `scripts/minikey_window_audit.cjs`: primary implementation and controls.
- `scripts/verify_minikey_window_audit.py`: portable independent implementation.

From `public/research`:

```sh
node scripts/minikey_window_audit.cjs --self-test
node scripts/minikey_window_audit.cjs --scan --registration-commit 6010d9310f678a0380939fe98f2820f41c6a3f68 --out minikey-rerun.json
python3 scripts/verify_minikey_window_audit.py minikey-independent-rerun.json
```

Each command refuses to overwrite an existing result. The offline checks require only Node/Python standard libraries. The optional `--check` flag is unnecessary for this result because there are no format-valid candidates; it enables only the protocol’s read-only address checks if one exists.

Fingerprints are domain-separated. A plain SHA256 of a valid minikey would be its actual private scalar and is deliberately not used as a public candidate fingerprint.

## What this rules out—and what stays open

Excluded: literal legacy 22-character or standard 30-character minikeys embedded anywhere in **these exact 42 forms**.

Not excluded: other printed-line selections, paragraphs, highlighted text, individual pages outside the selected concatenated forms, other encodings, typography, geometric selectors, an intermediate instruction, or another issue. The minikey format itself was not named by Keiser. This result does not establish whether a prize exists or what someone outside this project has found.

The next stronger source-motivated hypothesis is to **apply a fixed reflected mask first, then take the first selected word of each target printed row**. That composes both creator hints using the corrected physical leaves. Its rule should be registered separately, visually verified against the original scans and judged only within a declared finite candidate set; this audit did not execute it.

## Execution and funding record

Executed through Codex using local Node.js and an independent Python check. External address/API requests: **0**. No additional paid external service was invoked; subscription/model billing was not measured. No creator-fee-funded expense, fee receipt, recovered BTC or buyback is claimed by this run.

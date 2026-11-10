# Pair-local mirror boundary envelope

This protocol and implementation are registered before target decoding. See [the frozen machine protocol](PROTOCOL.json) for exact inputs, implementation hashes, parameters, caps and controls. The earlier G01 result remains unchanged.

## Why this follow-up

G01 blocked a row when any word was near a mask boundary, including words that could not change its first or last selected word. This procedure directly models the possible selected edge word. A source-only audit finds 17,108 pair-local paths and 102,648 labeled readings, including directions and projections. These are correlated variants within one procedure, not independent theories.

For each frozen word center, use a closed square with radius max(12, the frozen source guard) in upright page coordinates. Classify it against the exact union of reflected half-open mask rectangles. Every partition edge and one midpoint per open interval are evaluated, including boundaries. A word is guaranteed in, guaranteed out, or uncertain.

Read from the selected edge until the first guaranteed-in word. Each earlier uncertain word, and that guaranteed-in word, is an allowed first/last selection. Include row omission only if no word is guaranteed in. Cartesian products of these row alternatives intentionally overapproximate correlated physical errors. Exhaustive synthetic Boolean choices validate this selection rule; geometric union/gap/boundary controls test the classification.

## Fixed scope

Four directed physical page pairs, orange/black masks, leftmost/rightmost selected words, forward/reverse row order, and words-spaced/words-joined/initials projections. Scan exact and whitespace-only compacted forms using the published shared validators for WIF, legacy 22/standard 30 minikey, boundary-delimited 64hex and unfiltered contiguous BIP39 words. BIP39 lowercases lexical tokens, keeps non-dictionary words as barriers, and never joins across invalid decoded groups. No prose hashes, arbitrary 32-byte ASCII scalars, network queries or transactions.

The run fails inconclusive if the 20,000 path or 120,000 reading caps are exceeded, any source/code pin changes, or completeness/controls fail. The shared scanner deduplicates actual forms and candidates across all readings; labeled-path counts do not inflate checksum counts.

## Limits

The guards are review heuristics, not calibrated scan-error confidence bounds. The rectangle and center conventions are assumptions, not explicit creator instructions. Independent memberships admit physically inconsistent choices, so an apparent message or weak checksum is especially vulnerable to chance. A complete zero result excludes only the registered modeled pair-local superset. The 43,347,744 global-concatenation paths are **outside this test**. Other selections, encodings and mirror mechanisms remain open.

## Reproduce

Python 3.10+ standard library only. From the research archive root, use a new output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/mirror_boundary_envelope.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 scripts/mirror_boundary_envelope.py --run --protocol analysis_outputs/continuation_20261110/mirror_boundary_review/PROTOCOL.json --registration-commit REGISTRATION_COMMIT --out mirror-envelope-rerun
```

Replace REGISTRATION_COMMIT with the commit first publishing this protocol. Raw JSONL contains exact readings and selected source-word IDs. Keep it private until the safe result is reviewed. If a valid private record is found, a separate declared read-only follow-up is needed; this script does not import wallets or submit transactions.

# A missing minikey length: fixed compatibility replay

**Registration state: prepared; target scan not run at this checkpoint.** The public commit containing the frozen protocol and implementations must precede target execution. The final result records that exact commit.

The [historical Casascius implementation](https://github.com/casascius/Bitcoin-Address-Utility/blob/e493d51e4a1da7536fc8e8aea38eeaee38abf4cb/Model/MiniKeyPair.cs#L144) accepted 22-, 26- and 30-character mini private keys in 2013. Our earlier registered checkers covered 22 and 30. Their results remain valid for those lengths. Historical compatibility is not evidence that Keiser chose 26 or that every specification requires it. See [the pinned source receipt](HISTORICAL_SOURCE.json). The third-party implementation is referenced, not redistributed.

## Frozen populations

1. The same 22 saved body-only George Sand readings and their 42 exact/whitespace-compacted forms from the earlier window audit. The unchanged Node source builder is reused. This adds exactly 113,662 potential positions of length 26.
2. The same four global mirror families, two whole-sequence row orders and three projections: 24 language graphs over 43,347,744 modeled selection paths. Source alternatives, geometry, omissions and graph construction are unchanged. This counts reachable candidate sets, not millions of expanded readings or independent theories.

Only embedded **S-prefixed, Base58, 26-character strings** are checked. A format pass requires the first byte of SHA-256 of the ASCII value plus a question mark to be zero. No raw prose hashing, new geometry, source repair, other length, extra reading, scalar derivation, address construction or network lookup is added.

## Controls and completion

Two separately implemented walkers/checkers must pass synthetic controls before target execution. Source, implementation and public protocol bytes are pinned and checked against the registered Git commit. The primary runner reuses source builders but specializes the old walk to length 26; an independent checker compares the full private candidate sets and outcomes after registration. Exact pins and parameters are in [PROTOCOL.json](PROTOCOL.json).

The global walk has caps of 2,000,000 prefix-state visits and 1,000,000 unique insertions; the literal position cap is 113,662. A pin mismatch, failed control, missing graph, cap hit or execution error is inconclusive. Partial findings stay private and cannot support a complete negative.

A complete zero-pass result excludes this one compatibility case in these exact two populations. An eight-bit checksum pass can occur by chance and requires separate source review; it does not authenticate the puzzle or prize. Any later address/history check needs its own fixed protocol. New public summaries omit raw candidate values and associations. Public source readings remain reproducible and are not a secrecy guarantee.

## Reproduction

From the public research directory, after installing the documented Node runtime:

```sh
python3 scripts/minikey26_compatibility.py --self-test
python3 scripts/verify_minikey26_compatibility.py --self-test
python3 scripts/minikey26_compatibility.py --preflight --protocol analysis_outputs/continuation_20261110/minikey26_compatibility/PROTOCOL.json
```

Target reproduction additionally needs the actual registration commit recorded in RESULT.json and a fresh output directory outside any public directory. The final report supplies exact commands and independent results. No wallet action is part of this protocol.

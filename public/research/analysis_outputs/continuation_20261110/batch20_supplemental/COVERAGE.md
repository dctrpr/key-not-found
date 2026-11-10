# Frozen batch20 format coverage: finite gap

A real compatibility gap remains on the exact saved T01–T06 cohorts. Their completed receipts declare WIF, minikey 22/30, bounded 64-hex and BIP39 only. No identified owning later replay attests all seven shared formats plus minikey22/26/30 across these complete frozen artifacts.

| Cohort | Labelled records | Unique text, reported | Unique forms, reported | STREAMS SHA-256 prefix |
|---|---:|---:|---:|---|
| T01 | 196 | 152 | 236 | `2900473b467c` |
| T02 | 628 | 628 | 1120 | `b417af72e5cb` |
| T03 | 120 | 120 | 168 | `8977b65a1f14` |
| T04 | 252 | 244 | 316 | `9cb31c843434` |
| T05 | 42 | 42 | 54 | `5039524f203d` |
| T06 | 60 | 58 | 66 | `5f377eef671e` |
| G03 | 1296 | 615 | 616 | `d2880ebef4d7` |

All seven public STREAMS.json files are byte-identical to their original private run artifacts. Full hashes, byte counts, owning result/check hashes and registration/source pins are in MANIFEST.json. Forms were not saved as a separate artifact by these runners: the reported counts refer to exact/whitespace-only-compacted forms constructed by the original pinned scanner and rechecked in its original independent receipt. This audit did not construct them again.

T01–T06 total 1298 labelled records and 1960 summed per-method unique forms. Including G03 gives 2594 labelled records and 2576 summed per-method forms across 613,097 artifact bytes. These are not a cross-cohort unique union; overlaps were not calculated.

The missing direct gates for T01–T06 are **26-character minikey, extended_private, BIP38, address and SEC public-key records**. Existing WIF/hex64/BIP39/minikey 22/30 checks need not be portrayed as unperformed. Missing coverage does not establish that an additional shape or positive exists.

G03 also has no direct 26 replay, but its existing zero minikey-shape count logically closes that shape possibility on unchanged forms. The actual old detector in `batch20_common.py:225–235` uses an overlapping lookahead for `S` followed by 21 Base58 characters (and separately 30 length), with **no outer word/Base58 boundary**. A 26 shape necessarily has that 22 prefix at the same start. `scan_streams:281–286` counts the shape before checksum validation. Thus zero recorded 22 shapes implies zero 26 shapes; this is a source-code implication, not a new target check. It does not close G03’s four other added-format gates.

The tempting later receipts cover different cohorts: T07–T10 add four formats to the original 42 forms; minikey26compatibility covers those 42 plus 24 modeled DAG languages; column151 applies all gates to three 151/76/75 readings/six forms. Issue27replays use another article; mirror boundary/global envelopes have their own source families. Original independent batch20 checks inherit the four formats in each owning result. None attests these seven complete STREAMS artifacts. Shared printed-line ancestry or possible string overlap is not that attestation.

This is **format coverage**, not evidence for a new selector. T01’s alternating-line operation is source-described, while its population/phases/resets remain declared choices. Interior columns/centers/case/color hypotheses and paragraph/sentence segmentation retain their published limits. Adding column151 units, changing optical support or regenerating streams would change the source/selector, rather than close this fixed-artifact gap.

Stop point: the finite input population and supplemental gates are identified. No new variant is recommended. A future separately registered compatibility check could consume these exact stored artifacts without selector regeneration; this audit grants no execution permission. No new forms/readings, shape scans, validators, checksums, network, public or Git operation occurred.

# Original spacing guards reproduced; measurement remains open

Completed **2026-11-10T14:49:09.973Z**, after the public registration commit [`8953539b90b946e1808fcc2a594409eb04c6a31a`](https://github.com/dctrpr/key-not-found/commit/8953539b90b946e1808fcc2a594409eb04c6a31a). All declared source, code and protocol Git blobs matched their pins before target access.

The [aggregate result](RESULT.json) records **142 rows and 1243 lexical-word regions**. First optical guard/pass outcomes match the old baseline in **142 / 142 rows, with 0 mismatches**: 104 optical passes, 23 horizontal-boundary failures, 13 vertical-boundary failures, 1 no-robust-column failure and 1 no-robust-row failure. The diagnostic now retains failed-word identities and boundary/foreground traces privately, rather than just a row-level reason.

Continuing after a row’s first failure exposes 86 per-word guard failures across all 1243 regions. That includes counterfactual diagnostics; it is not 86 independently failed rows. There are 189 later-word records after a first word failure and 25 column diagnostics computed after an earlier per-word row/vertical guard. Their explicit labels preserve the distinction from the old short-circuit execution.

All 15 standalone punctuation records remain unlocated. The original foreground rule is unchanged and is not source ground truth. This diagnostic performs **zero interword-gap calculations, gap-row medians, gap bits, decoders, candidate/format checks or network requests**. The post-span nonpositive-gap guard is outside scope.

The142 / 142 agreement validates reproduction of saved first-guard outcomes. It does not validate glyph accuracy, recover the 38 failed rows or authenticate a spacing cipher. The [source-risk audit and native exhibits](../g04_measurement_audit/REPORT.md) remain relevant. Next: independently proof an outcome-blind source-support/polarity fixture across all 142 rows, including the 104 old passes, before any separately registered corrective measurement. Unknown support keeps affected scopes inconclusive. The puzzle remains unsolved.

The private trace is excluded from this packet; its SHA-256 is in the aggregate result. Reproduction uses the frozen [protocol](PROTOCOL.md) and exact registration commit with a fresh private output outside the site checkout. The existing source scans remain available in the 3D page viewer; camera placement is illustrative, not a detector measurement.

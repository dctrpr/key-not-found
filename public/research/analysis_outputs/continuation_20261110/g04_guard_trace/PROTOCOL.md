# G04 optical guards: a diagnostic before repair

This procedure records where the **unchanged original** optical detector stops. It covers all142 frozen body rows and all1243 lexical-word records, with the15 standalone punctuation records kept unlocated. It is source-measurement diagnosis, not a new cipher theory.

The exact definition, source/code SHA-256 pins, guard order and caps are frozen in [PROTOCOL.json](PROTOCOL.json). Execution requires the actual public registration commit and matching Git blobs for every declared input. Synthetic controls are source-free. No target trace has run at registration.

Record first-failing word identity, ROI, boundary side and the foreground selected by the original scanline rule. Continue later words only as explicitly labelled counterfactual diagnostics. Column flags following an earlier vertical/row guard are also counterfactual. A true pre-loop row failure has no invented failed-word ID. The post-span nonpositive-gap check is outside this diagnostic; it is never computed.

Compare every first optical guard/pass to the pinned old result. Do not repair foreground, punctuation, glyph support or regions. Do not compute interword gaps, gap medians, gap bits, decodes, format/candidate checks or network requests. The source trace stays in a fresh private directory outside the entire site checkout; only aggregate counts and integrity pins are selected for publication. Polarity selected by the old rule is not source ground truth.

Python3.9+ with Pillow, NumPy and PyMuPDF, from the public research root:

```sh
python3 scripts/g04_guard_trace.py --self-test
python3 scripts/g04_guard_trace.py --run --protocol analysis_outputs/continuation_20261110/g04_guard_trace/PROTOCOL.json --registration-commit ACTUAL_PUBLIC_SHA --out FRESH_PRIVATE_DIRECTORY
```

A baseline match validates the diagnostic reproduction of saved first-guard outcomes, not glyph accuracy, repaired coverage or an intended spacing cipher. A mismatch must be investigated before any repair. Either outcome leaves the puzzle unresolved. An independently proofread fixture across all142 rows must precede any separately registered corrective measurement.

[Independent static/synthetic review](CODE_REVIEW.json) passed14 built-in assertions and40 separate synthetic first-guard comparisons against the frozen optical function. The [implementation controls](SELF_TEST_RECEIPT.json) also reject four invalid preconditions. Neither review executed target source measurements.

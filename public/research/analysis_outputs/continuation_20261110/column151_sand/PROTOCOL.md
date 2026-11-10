# Three fixed Sand readings of the declared editorial column

The [151-unit source model](../../../sources/issue24-column151/SOURCE.json) adds the two opener lines to the previously tested 149-unit display-inclusive frame. All 142 body strings and seven older display units are unchanged. Independent source proof covers the nine nonbody units and ordering; the body reuses prior proof. This is a small source/semantic coverage correction, not a new cipher family or every printed glyph transcribed.

Register these exact global readings before generation:

1. First whitespace-delimited chunk of every unit, with case/punctuation preserved, joined by U+0020:151 chunks.
2. Whole odd one-based units, joined by LF:76 rows.
3. Whole even one-based units, joined by LF:75 rows, a parity control.

No page/paragraph reset, lexical stripping, initials/finals, reversal, source omission or extra transform is added. Each text and its whitespace-only compacted form are checked, deduplicated to at most six forms. Seven unchanged shared format gates cover WIF,64hex,BIP39,extended private records,BIP38,addresses and SEC public points. A separate embedded minikey scan covers22/26/30 characters with the weak8-bit question-mark checksum only; the old22/30 mini gate is not called. No prose-to-key hashing, address/seed/child derivation or network query is included.

Raw readings, forms and record associations stay in a fresh private0700 directory outside the entire site checkout; files are0600. Public output contains counts and whole-artifact integrity only. A format pass is a lead, not a solved key or funding proof. Full-output semantic reviews follow generation, with exploratory recognition/nonrecognition separated from literal record validation.

The source, native contexts, source proof, public PDF, canonical body, code and support files must match their actual public Git registration blobs before projection. The exact definition,11source pins and3script pins are in [PROTOCOL.json](PROTOCOL.json). Registration is not proven by this timestamp: root verifies the remote commit before target execution. The [technical review](TECHNICAL_REVIEW.json) and source-free controls are separate from target results.

From a Git checkout’s public research root (Python3.10+ standard library), with a fresh private parent of mode0700 outside the checkout:

```sh
python3 scripts/column151_sand_probe.py --self-test
python3 scripts/column151_sand_probe.py --run --protocol analysis_outputs/continuation_20261110/column151_sand/PROTOCOL.json --registration-commit ACTUAL_PUBLIC_SHA --out FRESH_PRIVATE_PARENT/PRIMARY
```

The independent verifier recomputes all three texts and form/validation aggregates after registration. Its seven non-mini validators are shared code, so agreement is not a second cryptographic engine. It independently implements reading construction and minikey windowing. Both AI semantic reviewers must read every complete output; source/hypothesis exposure is disclosed.

A complete zero result excludes only the registered declared literal records in these outputs. Other readings, artwork, encodings, record families, source models and the puzzle remain open. No original typesetting Unicode, creator extraction instruction or prize funding is authenticated by this protocol.

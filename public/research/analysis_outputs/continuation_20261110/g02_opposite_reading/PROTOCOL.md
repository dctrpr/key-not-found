# Read every opposite-color stencil selection

The [joint-color source audit](../g02_joint_color_audit/RESULT.md) leaves three optional opposite-color words across the four directed physical pairs. The global selector has no required words, so its eight assignments also contain every pair-local selection when the other pairs are empty.

Use the original pair order 76→77, 77→76, 78→79, 79→78. Bind the ordered membership IDs to the verified printed tokens. The assignment bits mark inclusion in frozen word order. Read each selection forward and with its word order reversed. For each direction, preserve the spaced words, whitespace-compacted words, first alphanumeric characters and last alphanumeric characters. These produce 64 labels, including the empty assignment. The joined form captures the existing whitespace-only compaction. Compaction leaves initials and finals identical to their exact forms.

Compare all 64 records from two implementations, including each ordered word ID and every output byte. Both reviewers see the complete distinct strings and their aliases. They know the puzzle and this scope and record their judgments separately. The criterion is a coherent second message or a determinate puzzle operation supported by the exact reading. Semantic review covers only these strings and depends on reader judgment. The independent choices overapproximate physical possibilities.

The [machine protocol](PROTOCOL.json) pins the source evidence and both scripts. Register the protocol on GitHub before generating the readings.

## Reproduce

Run from the repository root in a checkout containing the registration commit. Use the full commit recorded with the result and a fresh private directory.

```sh
G02_PRIVATE="$(mktemp -d)"
G02_PROTOCOL=public/research/analysis_outputs/continuation_20261110/g02_opposite_reading/PROTOCOL.json
python3 public/research/scripts/g02_reading_model.py --self-test
python3 public/research/scripts/verify_g02_opposite_readings.py --self-test
python3 public/research/scripts/g02_reading_model.py --research "$PWD/public/research" --protocol "$PWD/$G02_PROTOCOL" --registration-commit "$G02_REGISTRATION" --out "$G02_PRIVATE/primary"
python3 public/research/scripts/verify_g02_opposite_readings.py --run --research "$PWD/public/research" --protocol "$PWD/$G02_PROTOCOL" --registration-commit "$G02_REGISTRATION" --out "$G02_PRIVATE/independent"
cmp "$G02_PRIVATE/primary/READINGS.private.json" "$G02_PRIVATE/independent/READINGS.private.json"
```

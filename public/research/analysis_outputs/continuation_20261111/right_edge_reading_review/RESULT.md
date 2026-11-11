# The two saved right-edge readings yielded no instruction

Two AI contexts read the complete saved texts in downward and upward row order. Neither recognized a coherent reading instruction or a source unit to act on. The words read as disconnected fragments of the article. This checks the two existing whole-body strings with their original lexical cleanup and punctuation. [Machine result](RESULT.json) · [Reader A](READER_A.json) · [Reader B](READER_B.json)

Each text takes the rightmost intact word from all 142 physical body rows. The two saved texts cover the same selector with opposite row orders. They are absent from the recorded 22-output semantic review. The archive and selector are pinned, and the private packet replayed byte for byte. [Prior semantic review](../../continuation_20261110/issue24_readable_review/REVIEW.json) · [Protocol](PROTOCOL.md) · [Registration](REGISTRATION.json) · [Packet manifest](PACKET_MANIFEST.json)

Reader A knew the wider case and the selector. Reader B used a fresh context. Both report reading the two whole texts before seeing any peer judgment. Recognition is subjective and this result applies to those two exact saved strings. It leaves other source choices and interpretations open.

From the Git repository root, reproduce the exact packet using an absolute fresh private output directory.

```sh
DIR=public/research/analysis_outputs/continuation_20261111/right_edge_reading_review
python3 public/research/scripts/pack_right_edge_saved_readings.py --self-test
python3 public/research/scripts/pack_right_edge_saved_readings.py --pack \
  --research public/research --protocol "$DIR/PROTOCOL.json" \
  --registration-commit dd64244dccd1c9011495a240518280523fcae9f5 \
  --registration-receipt "$DIR/REGISTRATION.json" --out "$PRIVATE_PACKET"
```

A new boundary experiment needs a distinct source observation or reading rule. Additional permutations of these two saved strings would add little source evidence.

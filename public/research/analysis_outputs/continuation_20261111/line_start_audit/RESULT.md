# The line boundaries agree across the two scans

Two fresh readers independently recorded 142 body lines in the second retained scan. Every low-reader row has a unique monotone counterpart in the other receipt. Interior word pairs uniquely align 139 rows to the existing high-resolution model. Direct source inspection confirms the remaining three short lines. The check found no agreed change to a first or last word's lexical identity or to the 142 physical body baselines. [Result](RESULT.json) · [Source adjudication](ADJUDICATION.json) · [Locked reader A](READER_A.json) · [Locked reader B](READER_B.json)

## One letter case stays unresolved

The original lower-resolution readers disagreed on the first letter's case in row p77r09. Both read it as lowercase after comparing same-line letter shapes in a targeted native crop. An independent higher-resolution reader read that initial as uppercase, matching the uppercase sample farther along the row. The low and high excerpts preserve that source discrepancy. Keep the existing source model and both case observations visible. [Higher-resolution crop](exhibits/high-p77r09.png) · [Second-scan crop](exhibits/low-p77r09.png) · [Higher-resolution review](HIGH_SHORT_CASE_REVIEW.json) · [Low review A](LOW_INITIAL_CASE_A.json) · [Low review B](LOW_INITIAL_CASE_B.json)

The follow-up low-review files are publication projections. They preserve the outcomes, visual observations and UTC times while omitting local filesystem references. Their private-original hashes are retained. The original complete low-reader receipts and lock remain byte-exact. [Receipt lock](RECEIPT_LOCK.json)

## What the source comparison settles

The widely separated question and reply on p75 share one baseline. The short highlighted sentence farther down p75 and the three-word question on p76 each remain a single physical row in both views. Their matching edge chunks support the three cue-free correspondences. An independently reviewed high-resolution crop agrees with each. The leading dash on p79r24 is freestanding, and the existing canonical first-word field already selects the following lexical word. [Short-row source contexts](HIGH_CONTEXT_MANIFEST.json) · [Low contexts](LOW_CONTEXT_MANIFEST.json) · [Layout review](HIGH_LAYOUT_REVIEW.json)

Paragraph-start interpretations differ on 27 rows. The centered p77 passage and p78 artwork quotation also retain disclosed source-role decisions. The conservative automated report leaves 97 ambiguity records, including paired edge flags for rows carrying any annotation, paragraph disagreements and the three cue-free rows on each side. These are overlapping metadata records. The source adjudication supplies the three short-row matches and preserves the unsettled letter case. [Automated reconciliation](RECONCILIATION.json)

## Reproduction and limits

The public registration and twelve source/code pins were checked before preparing the lower-resolution packet. All ten native strips replayed byte for byte and reconstructed the five complete RGB rasters. Every forced canonical pair was independently checked with a length-only dynamic program that excludes one pair at a time. Both full reader receipts were locked before reconciliation. [Registration](REGISTRATION.json) · [Packet](PACKET_MANIFEST.json) · [Packet replay](PACKET_REPLAY.json) · [Matching replay](MATCHING_REPLAY.json) · [Protocol](PROTOCOL.md)

The first metadata replay stopped because both readers supplied note arrays and the registered validator expected a note string. A small adapter accepts that representation in memory. It preserves every source observation and uses the registered matching functions. The comparison replay then agreed in every analytical field. [Implementation correction and commands](IMPLEMENTATION_NOTE.md)

Recreate the ten exact adjudication excerpts after generating the native packet. Use a fresh private output directory.

```sh
DIR=public/research/analysis_outputs/continuation_20261111/line_start_audit
python3 public/research/scripts/make_issue24_line_context_exhibits.py \
  --research public/research --packet "$PRIVATE_PACKET" \
  --reader "$DIR/READER_A.json" --out "$PRIVATE_EXHIBITS"
```

This was an AI visual source review with approximate coordinates. Acquisition independence and typesetter-native letter outlines remain unknown. The completed audit provides no new reading stream or key result. The puzzle remains unsolved.

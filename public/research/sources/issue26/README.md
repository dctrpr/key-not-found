# Issue 26 comparison article — source preparation

The preserved JPEG witnesses show an OVERDOSE article titled **Censorship, Dematerialization and Bitcoin**, subtitle **Without Freaks, America Is Nothing**, on printed pages 102–104, following a portrait on 101. The original PDF named in historical records is unavailable here. These are retained 2040 × 2805 comparison JPEGs; the inherited issue label is not authenticated by the filename alone. Source hashes and native image coordinates are preserved.

**No target decoding, record check, key derivation, address query or transaction was performed.**

## Frozen handoff

The authoritative source artifact is `issue26-source.json`, SHA-256:

`1ff7a0a26c1e91fb2bfef9817693419979fdf39381d4124c2c9e5e7739f73c67`

It contains **113 body/display text rows** (42, 52 and 19 on pages 102, 103 and 104), plus one separately classified STOP display label. All 114 first-word objects were visually checked against the eleven source-pixel plates. Source letters and case are legible. The record preserves raw OCR, boxes, fixed-view alternatives, role, column, flow block, paragraph and article/page/flow reading indices. Title, subtitle, headers, margins and footers are separate paratext.

Natural reading order is full-width introduction, left column, right column, then full-width closing flows. Independent columns are never merged into one horizontal row. STOP is a large label beside the callout; it is not forced onto a regular prose baseline. A test must declare treatment of labels, headings and callouts.

`firstWordSource` uses the first nonempty whitespace-style source token with outer punctuation stripped. Internal punctuation and fused spelling remain: `present,how` and `thepursuit`. `firstLexicalWordSource` provides the conventional lexical alternative `present` for the comma fusion. Neither field silently changes `thepursuit` to `the`. Printed line fragments such as `festly`, `age-adoring`, `gelist`, `trable` and `tion` remain at their actual line starts. Leading standalone dashes remain in raw OCR/source and are separate punctuation. Raster glyphs do not establish original digital Unicode code points; internal apostrophe/hyphen representations are an explicitly declared transcription surface.

Full-row text is still unverified OCR. Twenty-three page 102 rows are conservatively flagged for gutter-obscured line ends. Do not use those draft strings to claim a complete alternate-line exclusion. The first-word branch is better supported.

## Reproduce source preparation

Requires macOS, Swift/Apple Vision, Python and Pillow. Run from the research archive root, use fresh local output folders, and keep source paths unchanged. The native OCR helper uses no account or API.

```sh
swiftc -O scripts/batch20_vision.swift -o /tmp/key404-issue26-vision
python3 scripts/prepare_issue26_full.py --source-dir sources/issue26 --out /tmp/key404-issue26-pass1
/tmp/key404-issue26-vision --manifest /tmp/key404-issue26-pass1/jobs.json --out /tmp/key404-issue26-pass1/vision.json
python3 scripts/prepare_issue26_zones.py --source-dir sources/issue26 --out /tmp/key404-issue26-pass2
/tmp/key404-issue26-vision --manifest /tmp/key404-issue26-pass2/jobs.json --out /tmp/key404-issue26-pass2/vision.json
python3 scripts/assemble_issue26_source.py \
  --views /tmp/key404-issue26-pass2/views.json --zone-ocr /tmp/key404-issue26-pass2/vision.json \
  --full-ocr /tmp/key404-issue26-pass1/vision.json --source-dir sources/issue26 \
  --decisions sources/issue26/firstword-review-decisions.json --out /tmp/key404-issue26-source-rerun.json
```

To replay the frozen OCR and decisions without running Vision:

```sh
python3 scripts/assemble_issue26_source.py \
  --views sources/issue26/ocr/zone-views.json --zone-ocr sources/issue26/ocr/zone-vision.json \
  --full-ocr sources/issue26/ocr/full-page-vision.json --source-dir sources/issue26 \
  --decisions sources/issue26/firstword-review-decisions.json --out /tmp/key404-issue26-frozen-replay.json
```

The source assembler refuses existing output, changed source hashes, or a changed first-token OCR string or box. A changed observation requires new source review. Replaying the frozen OCR and recorded decisions produced the exact authoritative SHA-256. Apple Vision versions may change fresh observations; such a mismatch is not a failed puzzle test.

`firstword-review-decisions.json` preserves every visual decision and plate hash. `firstword-review/` contains the eleven plates. `ocr/full-page-vision.json` and `ocr/zone-vision.json` preserve the two raw OCR passes. `ocr/zone-views.json` freezes the forty zone-view definitions and image hashes. Source crops are reproducibly regenerated rather than duplicated. Intermediate drafts are not publication inputs. The frozen artifact is `issue26-source.json`.

The original JPEGs have no EXIF fields, only JFIF wrapper fields. The publication review identified the green edge on page 104 as adjacent printed art. Exact original image bytes can be retained. Metadata absence alone does not establish anonymity or provenance.

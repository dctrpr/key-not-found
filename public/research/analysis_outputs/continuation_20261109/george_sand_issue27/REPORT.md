# George Sand / Musset checks on Issue #27

The three supplied Orange Party article pages do not yield a solved key or a readable new instruction under the bounded printed-line checks below. This is a separate test of Max's broad December 2022 plural-key claim; the March 2023 20-BTC announcement remains specifically associated with Issue #24.

## Source and relevance

- Source images: `analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_02.jpg`, `page_03.jpg`, `page_04.jpg`.
- Printed pages: **79, 80, 81**.
- The adjacent `page_01.jpg` visibly identifies **Who is The Banana Republic Now, Biatch?**, by Max Keiser, with **THE ORANGE PARTY** in the margin.
- [Bitcoin Magazine's official issue contents](https://bitcoinmagazine.com/2022-orange-party-issue) identifies this as a Fall 2022 release and lists this OVERDOSE article. It therefore predates the [December 26, 2022 creator clue](https://x.com/maxkeiser/status/1607378060172460032), which gives no issue number and uses plural keys.
- The creator-linked [George Sand article](https://ciphermysteries.com/2010/05/16/george-sands-cryptography) supplies whole odd-line selection and first-word-per-line extraction. These are the mechanism family tested here.

## Extraction

Apple Vision recognized **357 observations** from **14 declared page regions**. The isolated W drop cap was joined to the first text line, giving **356 physical lines**. Every first word was compared visually against the three scan images; 26 corrections to OCR observations were recorded explicitly in `analyze_printed_lines.py`, including the drop cap and binding-side missing letters. Physical hyphenation was preserved, including fragments such as `torship`, `efiting`, `latory`, and `tial` at the beginning of printed lines. Those fragments must not silently be turned into full words for a line-edge cipher.

`firstword_streams.md` contains the exact leading-word and leading-letter sequences for every region, plus odd/even leading-word streams. `printed_lines.tsv` provides row-by-row source text and labels. `printed_lines_and_streams.json` contains the geometry, raw observation IDs, corrected lines, and every declared stream.

Region order follows conventional reading: full-width leads, then left, center, and right columns. Printed page 81 contains upper left and center blocks, a lower block spanning two columns, and the right column. These region boundaries are explicit in `regions.json` and are reviewable. No row was chosen because it contained a desired word.

## Tests and results

The script generated **1,940 streams** from named combinations of:

- Region, page, and complete article scope.
- All typography, body only, body plus introduction, or separately identified emphasis/pull quotes.
- All lines, odd lines, or even lines, with parity counted in the declared list.
- Forward or reversed line order.
- First words, first letters, last words, final letters, or complete selected lines.

Direct WIF and literal 64-hex checks were applied to these outputs and character-reversed controls, removing whitespace only. Result: **0 checksummed WIF or literal 64-hex outputs**. SHA256 was used only to verify WIF checksums, never to turn prose into candidate secrets. No BIP39-word filtering, guessed phrases, word deletions, blockchain lookups, or transactions were used.

Manual inspection of the actual first-word and odd/even whole-line outputs found ordinary fragments of article prose or non-readable line-edge strings, without a clear second message. The extracted initials contain no persuasive readable instruction. This assessment is limited to these declared units and orders; it is not proof that the article contains no key.

## Concrete textual irregularity retained

Printed page 80, center column, ends by repeating the same paragraph about a twelve-step recovery program twice in succession. The first copy begins at center-column physical row 35; the second begins inside row 40 and ends at row 45. The wording wraps differently between copies. Earlier, on printed page 79's center column, Max explicitly describes his prose as recursive, repetitive, an algorithm, and code. This combination deserves to remain visible in the evidence. It is compatible with intentional repetition or an editorial duplication error; neither is established here. No speculative operation such as deleting one copy was promoted to a key rule.

## Limits

First words are visually reviewed; line interiors and right-edge words retain OCR errors beyond the explicit corrections. Whole-line text and last-edge controls should therefore be treated as an OCR-assisted check, not a fully proofread transcript. Paragraph-local parity resets, simultaneous cross-column reading, line-width measurements, artwork, pages outside 79–81, and other issue articles were not exhausted. Header, footer, and title-page typography were excluded from the body extraction; the two leading quotation lines were retained as a separate region.

## Reproduce

Run from the workspace:

```sh
analysis_outputs/continuation_20261109/george_sand_issue27/ocr_regions \
  analysis_outputs/continuation_20261109/george_sand_issue27/regions.json \
  analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27 \
  > analysis_outputs/continuation_20261109/george_sand_issue27/vision_raw.json
python3 analysis_outputs/continuation_20261109/george_sand_issue27/analyze_printed_lines.py
```

The compiled Vision utility is reproducible from the adjacent Swift source with `swiftc ocr_regions.swift -o ocr_regions`. It performs accurate English OCR on the supplied image regions in memory, preserving each observation's bounding box and confidence.

# Independent text and count check, 9 November 2026

## New clue: actual printed-line George Sand test

The user supplied Max's 26 December 2022 George Sand clue after the initial pass below. See [the new actual-line report](george_sand_printed_probe.md), backed by [manually reconstructed printed lines](printed_lines.txt) and [pixel-band source locators](printed_lines.json).

The actual body has **142 printed rows**: 32, 31, 32, 22 and 25 on pages 75–79. These include `Really? Yes.` as one baseline and restore two previously OCR-missed `Fact:` lines. The fresh probe tests the linked cipher's complete alternating lines and first words; it also records bounded mirror, paragraph/page reset, optional-display and highlight/bold-subset variants separately. **10,080 labeled variants produce 2,034 unique text streams; zero direct checksum-valid WIF/64-hex/BIP39/minikey results.** First-word and odd/even full-text outputs show no clear independent instruction. This is a bounded negative result, not proof that the puzzle has no solution.

The clue's [linked primary example](https://ciphermysteries.com/2010/05/16/george-sands-cryptography) uses both complete alternating lines and first-word reading. Its comment thread records a final-line formatting correction on 28 December 2022, two days after Max linked it. The methods remain clear, but today's exact example lineation differs from the earlier version.

Printed highlight counts distinguish **45 rows containing highlights** from **46 colored/inverted segments**: two separated black bars share one printed baseline on page 78. Thus a count of segments must not silently become a count of rows. The union of highlighted rows and investigator-bold rows happens to contain104 rows, so alternating it yields52 initials. These variants were included and yielded no valid WIF; the52-character length alone is not corroboration.

## Initial bounded text pass

No solution was found. This pass supplies a reproducible negative test, and identifies attractive counts that are not a source-backed cipher rule.

## Executed test

Run from this workspace:

```sh
node analysis_outputs/continuation_20261109/fresh_cryptanalysis/transcript_mirror_probe.js
```

The script reads the corrected article and investigator-supplied canonical transcript (whole article and five page blocks). It tests normal reading; reversing each line, word, or word order; reading lines upward; reversing the complete text; and alternating left/right reading in both directions and from both ends. Each version is checked as text, joined text, letters, alphanumeric text, word initials/finals, line initials/finals, and first/last word of each line.

Result: **700 source/transform/projection combinations; 156 WIF-shaped window checks; zero WIF checksum matches; zero 64-hex direct strings; zero all-BIP39 contiguous phrase windows**. The 156 window checks include repetitions between projections; they are not 156 independent cryptographic hypotheses. No private-key hashing, blockchain queries, or transactions were performed.

This tests simple literal text reading, including alternating direction. It does not exhaust geometrical extraction or unknown ciphers. The canonical transcript sometimes merges actual printed lines; this limitation matters for exact physical line readings.

## Count trap: 255 partial-bold letters

The canonical model reports 72 + 32 + 61 + 12 + 78 = **255** partial-bold letters across pages 75–79. Page 76 contributes exactly 32. Neither count demonstrates a 256-bit secret or a 32-byte secret: these are letter counts in a manually annotated text model, not a binary stream or an explicit byte encoding.

There are **610 letter positions** in the **113 partially bold words**. Which letters appear bold is highly dependent on the underlying letter: all 43 `a`, 31 `c`, 53 `o`, and 16 `u` observations are each consistently in one state; 64 of 67 `e` and 50 of 54 `i` are bold. A per-letter majority predicts 577/610 labels (94.6%). That is consistent with the font-variant explanation already documented in the older log. It does not alone prove there cannot be a message, and the model is an investigator transcription rather than original font metadata.

The count 255 uses only bold letters in **partially** bold words; whole-bold words, punctuation and numeric tokens are handled differently by that model. Adding one guessed bit or treating each letter as a byte would introduce an extra rule rather than resolve one supplied by the source.

## Visual review

Rendered and inspected the complete eight-page `magazine.pdf` source. The five article pages show approximately **34 semantic highlight spans** and **46 printed highlight line segments**, depending on how split/adjacent phrases are grouped. These are manual counts, not a published encoding rule. The old natural-language annotation's 32 spans omit the game-theorized-protocol highlight and combine the final two orange sentences, so 32 is not a robust raw-source count.

No individually reversed glyph or recognizable private key was found in this visual pass. Every highlighted span is ordinary coherent editorial emphasis. Reflected masks landing on grammatical article snippets do not by themselves prove intentional extraction: broad masks over prose normally produce prose, and contextual Bitcoin/Bukele terminology repeats throughout the relevant pages.

The parent investigation is separately recomputing scan-native geometry after finding serious errors in older phrase-derived boxes. Those fresh results should determine whether any geometric selector survives; this report does not reuse the old claim that a reflected-highlight mechanism was proven.

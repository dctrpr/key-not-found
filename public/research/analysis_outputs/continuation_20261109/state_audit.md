# Independent state audit — 9 November 2026

## What is actually known

The archived investigation records two creator-issued public facts: Max Keiser announced a private Bitcoin key encoded in his Bitcoin Magazine article, claimed a 20 BTC prize, and subsequently linked G. D. Schott's *Mirror writing: neurological reflections on an unusual phenomenon*. Announcement: 1632068898169450497 (4 March 2023); clue: 1632391507008278528 (5 March 2023). See INVESTIGATION_LOG.md lines 5–18 and CLUE_LEDGER.md lines 1464–1484. Current web availability and prize status need fresh verification by the main investigation.

The source set contains a scan of eight pages, logically labelled 73–80, including the two-page opener and six body/ad pages. `magazine.pdf` is the better-resolution scan; `keyser bitcoin .pdf` is the lower-resolution public Drive/OCR witness. OCR geometry is not reliable enough to dictate letter-level overlays (CLUE_LEDGER.md 676–697). The scanned pixels, rather than reconstructed Markdown, are the authority for typography and highlighted text.

No published funding address/public key is recorded in the baseline. A valid-looking key or mnemonic therefore does not by itself validate a solution. Past checks of activity are evidence only within the specific candidate/address scope.

## A concrete correction supported by source images

I directly inspected `keyser bitcoin -3_1.jpg`, `-4_1.jpg`, and `-5_1.jpg`:

- Printed page 75 is a **left-hand** page, with the gutter at the right.
- Printed page 76 is a **right-hand** page, with the gutter at the left.
- Printed page 77 is a **left-hand** page, with the gutter at the right.

This issue uses the opposite printed-page parity to the convention assumed in many early scripts. Facing spreads are therefore 75/76, 77/78, and 79/80. Successive front/back leaves are 74/75, 76/77, and 78/79. This is direct visual evidence and is stronger for topology than noisy paper-texture correlation. The June correction was substantially right about topology even though its texture test did not confirm it.

The last corrected-topology check is narrowly scoped: it tests a horizontally mirrored bright/white mask from page 77 against **four already chosen page-76 boxes**, with a bounded translation/rotation grid. Its negative result does not exhaust correct-duplex mirroring over all pages, other ink/color polarities, or actual backward-writing detection. See CLUE_LEDGER.md 12455–12482.

## What the existing work does not establish

1. **Page 76 is a hypothesis, not an author-issued target.** The graph has 17 medium/strong reflected edges landing there, but they are many-to-one broad regions, and came from chosen page pairings and overlap thresholds. Semantic alignment with El Salvador/Bukele is context that naturally occurs in both the article and announcement images. It can prioritize a test but cannot prove the extraction target.
2. **The R1–R5 rules are investigator-created stopping criteria.** They first become explicit near CLUE_LEDGER.md 5286, and their mandatory “materially distinct source” and “explicit unit/order wording” requirements are not creator instructions. We may run a new, fully specified experiment on the existing scan. A puzzle need not contain prose saying “take the nth letter.”
3. **No need to preserve every old target in a new hypothesis.** R2's requirement to retain O5/G5 and the OBBO corridor can exclude a correct alternate solution. Treat those as optional benchmarks, not acceptance rules.
4. **“Ruled out” is often too broad.** Past runs rule out listed strings, transforms, derivation paths, and initial address indices, not the whole class of BIP39, mirroring, or hidden keys.
5. **The open-heart capsule is incomplete.** It isolates the 13-word bridge `in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized`; it is distinctive under current local controls, but no extraction follows. The prior audit also says its proposed 715-quartet falsifier and MAX-heart-KEISER source marker were not independently checked (CLUE_LEDGER.md 12484–12513).

## Provenance traps to avoid

- The earlier partial-bold stream was downgraded when Typeka Mix typography explained it; do not revive it as manually selected cipher letters without pixel evidence (1074–1099).
- `BOLD.docm` contains an investigator macro reading a BIP39 word list; its highlights are not original puzzle clues (998–1015).
- Cyan `MNBILLION` exists in a reconstructed DOCM but is invisible in the scan; it is not a printed source layer (1121–1141).
- The Canva board is an investigator's note board (“PRIVATE_ANNOTATION_OMITTED”), not a creator clue (897–915).
- The five-capsule graphic is reused artwork between opener and ending. Reuse alone is not an ordered key selector (1527–1548).

## Next experiments worth doing

1. Test **correct physical leaves globally**, without requiring p76 corridor overlap. Predeclare (74,75), (76,77), (78,79), use horizontal reflection through the sheet, and compare original color/ink masks. Read any coherent backward glyphs or anomalous keyed material before using OCR. Keep facing-spread folding as a separate operation.
2. Independently inspect **all source pages for actual mirror-written characters**, especially art, display headings, and marginal markings. The creator clue says mirror writing; the old investigation mostly operationalized it as overlaying normally written prose. A real backward-written string can be visually recognized and has a much smaller interpretation space.
3. Complete the **open-heart marker claim** only if its source image really shows MAX / heart / KEISER, and run the promised broader quartet controls. Do not infer a key from the 13-word bridge solely because earlier reports fixated on it.
4. If an extraction produces a bounded candidate set, record the exact source, operation, character order, and candidate encoding before read-only address checks. Candidate histories can be checked without sending funds or claiming anything.

I found no solved key in the material audited. The strongest new contribution is the source-supported physical topology correction and the realization that the old hard gates should not bind a fresh solve attempt.

## New implementation audit: the 17-edge graph has invalid input geometry

The older `exact_highres_reflection_geometry.json` does not locate exact phrases reliably. Its generator (`scripts/analyze_exact_highres_reflection_geometry.py:62–78`) greedily finds successive individual tokens anywhere later in a page and skips tokens it cannot find. It then unions those scattered word boxes without a completeness or contiguity requirement (`:104–105`). For instance, the p76 `shitcoiner at heart` label maps to the earlier plural `shitcoiners` at y1046, whereas the actual orange span is y2932–2982. `buying the dip` similarly gets y894–1168, whereas the actual orange span is y2177–2225. `$1 billion` joins word indices92 and209, creating a giant box over most of the page.

`scripts/analyze_reflected_highlight_graph.py:17` directly consumes that generated JSON, and lines47–70 turn its overlap records into the graph behind the 17/17 statistic. A fresh audit of all34 historical rows found that all17 medium/strong graph edges originate from5 target rows with **noncontiguous old matched word indices**. None of those5 phrases has a complete normalized contiguous OCR match in the source word model. Poor OCR does not mean the phrases are absent; it means this matcher cannot supply their geometry. This invalidates the 17-edge statistic as evidence for intentional phrase alignment, while leaving later, independently boxed high-resolution visual observations separate.

Reproducible audit: `scripts/continuation_audit_phrase_boxes.py`; outputs in `analysis_outputs/continuation_20261109/phrase_box_audit/`. Historical outputs were preserved.

## New finite corrected-topology experiment

Implemented `scripts/continuation_corrected_inverted_masks.py` using upright scan pixels. The detector finds neutral inverted text bars directly, separately treating page77's dark background. It uses fixed source thresholds, merges overlapping detector fragments, and adds12 pixels on every source-box edge to retain complete glyphs. It mirrors each source bar horizontally through the actual front/back leaves74/75,76/77,78/79 with no target shift, rotation search, or requirement to hit a preferred page76 quartet. Page74 is an illustrated field/cash page, so its dark illustration patches are excluded as non-text bars; page75 bars are still projected onto page74 for visual review.

The resulting source/target crop plate was reviewed. Target intersections contain ordinary, partial article prose and artwork, including `London is a scam`, `ripped off live central bankers tied to a burning stake`, `love and peace`, `because the fear`, and `incentivizes love`. They do not reveal a coherent backward key string in this fixed operation. Center-based character streams, read forward/reverse, yielded **zero strict checksum-valid WIF or literal64-hex candidates**. No hashes, address activity queries, seed recovery, or transactions were performed.

Outputs: `analysis_outputs/continuation_20261109/inverted_duplex/`. This is a bounded negative result for fixed, scan-native inverted-bar mirroring. OCR registration still limits character extraction, and the test does not exclude every physical transformation or other visual/text encoding.

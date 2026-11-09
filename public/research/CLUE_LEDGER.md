# Max Keiser Puzzle Clue Ledger

Purpose: keep the investigation from repeating old branches. A branch is only worth more work if it has an intentional mechanism and a testable output.

## Active Branches

### Mirror / Fold Geometry

- Status: active.
- Evidence: Max’s explicit clue was “Mirror writing: neurological reflections on an unusual phenomenon.”
- Local evidence: `analysis_outputs/highres/highres_reflected_mask_text_report.txt`.
- Why active: reflected orange highlights produce intentional-looking text selections across page pairs.
- Next test: do not repeat direct key derivations. Use mirror/fold geometry only if it creates a visibly cleaner selector or ordering rule.

### Source Registration

- Status: active.
- Evidence: Canva note says pills do not line up and browser/PDF OCR missed a `#0`.
- Local evidence: `analysis_outputs/source_audit/source_alignment_audit.md`.
- Finding: `magazine.pdf` and `keyser bitcoin .pdf` differ in resolution, crop, OCR layer, and rotation.
- Next test: treat `magazine.pdf` as visual truth; use OCR PDF only as a text helper.

### El Salvador / Bukele / Volcano Context

- Status: active.
- Evidence: recovered announcement-thread media include Bukele, El Salvador seal, lava/volcano imagery, and Bitcoin erupting from a volcano.
- Local evidence: `analysis_outputs/external_clues/max_thread_media/recovered_thread_media_report.md`.
- Why active: page 76 contains Bukele, IMF, volcano bonds, and “buying the dip” text, matching the recovered thread media.
- Test run: `analysis_outputs/external_clues/max_thread_media/media_sequence_article_mapping.md` maps the recovered media sequence to article text.
- Result: the strongest overlap is page 76: President of El Salvador, IMF, “buying the dip,” Nayib Bukele, volcanoes, and Volcano Bonds.
- Key check: `scripts/check_thread_media_keys.py` checked simple derivations from tweet IDs, media IDs, t.co shortcodes, image-order labels, and page-76 focus phrases.
- Result: 304 candidate secrets, 1300 addresses, 0 activity.
- Current conclusion: simple hashing of thread/media identifiers is ruled out; the media sequence remains useful as a targeting/order clue.
- Next test: use it to prioritize page 76 in mirror/fold geometry, not as standalone key material.

## Low-Value Or Ruled-Out Branches

### Raw BIP39 Seed Phrase Scan

- Status: ruled out under standard assumptions.
- Finding: the old solver over-reported mnemonics because the wordlist had 2051 words instead of official 2048.
- Corrected checks: strict candidates across raw words, line alternation, nth-word filters, first/last words, highlights, and old hardcoded candidates.
- Result: no activity on standard BIP44/49/84 first receive addresses.

### Highlight-Derived BIP39 Scan

- Status: ruled out under standard assumptions.
- Finding: 350 strict highlight-derived candidates checked.
- Result: no activity.

### Obvious Brainwallet Strings

- Status: ruled out.
- Inputs: article title, article text, highlights, mirror clue, obvious variants.
- Result: no activity.

### Thread / Media Identifier Hashes

- Status: ruled out.
- Inputs: recovered tweet IDs, media IDs, t.co shortcodes, image-order labels, and page-76 Bukele/IMF/volcano phrases.
- Evidence: `analysis_outputs/external_clues/max_thread_media/thread_media_key_check.txt`.
- Result: no activity.

### Ten Registered Derivation Experiments

- Status: ruled out as direct key derivations.
- Evidence: `analysis_outputs/ten_experiments/ten_registered_experiments.md`.
- Script: `scripts/run_ten_registered_experiments.py`.
- Scope:
  - E01 page-76 focus text features.
  - E02 wider page-76 context text features.
  - E03 article numbers as page-76 indices.
  - E04 recovered media dimensions as page-76 indices.
  - E05 tweet ID digit chunks as page-76 indices.
  - E06 media IDs as Base58 position streams.
  - E07 t.co shortcodes as Base58 position streams.
  - E08 high-res reflected page 79 -> page 76 text features.
  - E09 page-79 orange geometry as page-76 indices.
  - E10 recovered image-order labels.
- Chain check:
  - 43 generated strings.
  - 688 candidate secrets.
  - 2600 addresses checked.
  - Activity found: 0.

### Second-Wave Crypto Encoding Experiments

- Status: priority subset ruled out; broad direct-window candidates are low-value unless a stronger selector is found.
- Evidence:
  - `scripts/run_second_wave_crypto_experiments.py`
  - `analysis_outputs/second_wave/second_wave_crypto_experiments.md`
  - `analysis_outputs/second_wave/second_wave_candidate_summary.txt`
  - `analysis_outputs/second_wave/second_wave_crypto_priority_chain_check.txt`
- Scope:
  - E11 direct WIF/Base58 scan over high-signal text.
  - E12 Bitcoin minikey scan.
  - E13 direct 64-hex scan.
  - E14 high-res orange geometry byte streams.
  - E15 reflected geometry byte streams.
  - E16 geometry-derived BIP39 index streams.
  - E17 reflected-geometry BIP39 index streams.
  - E18 tweet/media/t.co ID byte streams.
  - E19 tweet/media/t.co ID BIP39 index streams.
  - E20 salted priority hashes using puzzle-specific salts.
- Extraction results:
  - 61,143 private-key candidates generated in total.
  - 652 priority private-key candidates selected for chain check.
  - 125 checksum-valid BIP39 candidates from index streams.
  - No checksum-valid WIF strings were found.
  - Three minikey-shaped candidates passed minikey checksum, but none had activity.
- Chain check:
  - 3,260 private-key addresses checked.
  - 366 BIP39-derived addresses checked.
  - Activity found: 0.
- Conclusion:
  - Literal WIF/minikey/hex hidden as plain text is unlikely.
  - Geometry/index streams can produce valid-looking keys and mnemonics by chance; without a stronger selector they are too noisy.

### Reflected Text As Direct Private Key / Brainwallet

- Status: ruled out under tested transforms.
- Evidence: `scripts/search_visual_private_keys.py`.
- Tested: direct WIF/hex/32-byte checks, SHA256, double-SHA256, SHA3-256, BLAKE2s, SHA512 halves, geometry byte streams, standard address types.
- Result: no activity after filtering low-entropy false positives.

### Anchor Projection As Direct Key

- Status: ruled out as direct key extraction.
- Evidence: `analysis_outputs/source_audit/visual_anchor_projections.md` and `analysis_outputs/source_audit/anchor_projection_key_check.txt`.
- Finding: anchor projections do not form clean readable text; narrow key check found 0 activity.
- Caveat: anchors may still indicate orientation/registration.

### Dust / Active Address False Positives

- Status: ruled out.
- Finding: first p2pkh run found 22 active zero-balance addresses from low-entropy numeric-stream false positives.
- Result after filtering: no activity.

## Unresolved Branches

### Missing Tweet Text

- Status: ruled out.
- Evidence: ThreadReader says the announcement is a 6-tweet thread, but only the first tweet text is visible.
- Test run: Twitter oEmbed checked all six tweet IDs exposed in ThreadReader HTML.
- Result: tweets 2-6 are image-only posts. There is no missing tweet text to recover via oEmbed.
- Remaining value: use image sequence and subject matter, not hidden wording.

### OVERDOSE Series Mechanic

- Status: unresolved.
- Evidence: article and recovered thread media foreground “OVERDOSE.”
- Added evidence: official Bitcoin Magazine pages show OVERDOSE is a recurring Max Keiser feature, including Issue #24, the Orange Party Issue, the Withdrawal Issue, and the Inscription/Finance Issue.
- Strong clue: the Inscription/Finance Issue lists `Overdose: Bitcoin Is A Mirror That Reflects All`, which overlaps Max’s mirror clue.
- Direct key check: `scripts/check_overdose_series_keys.py` checked the recurring titles/quotes and Inscription Issue block/tx/hash strings.
  - 18 source strings.
  - 384 private-key candidates.
  - 1,920 derived addresses checked.
  - Activity found: 0.
- Next test: inspect other OVERDOSE layouts/articles for repeated mirror/fold/highlight mechanics, title conventions, or recurring art marks.

### Anchor Ray Selector

- Status: ruled out as direct key extraction.
- Evidence:
  - `scripts/run_anchor_ray_selector.py`
  - `analysis_outputs/anchor_ray_selector/anchor_ray_selector_experiment.md`
  - `analysis_outputs/anchor_ray_selector/anchor_ray_selector_top_lines.png`
- Scope:
  - Used page-79 pill centers mirrored onto page 76.
  - Used page-76 X mark, dollar mark, black bars, and estimated barbed-wire knots.
  - Tested segment, ray, and full-line selectors over page-76 OCR words.
- Finding:
  - Produced 169 unique readable selections.
  - Best selections hit plausible page-76 context: `President`, `Nayib`, `volcanoes`, `El Salvador`, `IMF`, `Bitcoin Magazine`, and `bitcoin money`.
- Chain check:
  - 3,000 private-key candidates.
  - 15,000 derived addresses checked.
  - Activity found: 0.
- Conclusion:
  - The ray system can select contextual text, but direct prose-hash key derivation is ruled out.

### Anchor Ray Index Streams

- Status: ruled out under standard key and BIP39 assumptions.
- Evidence:
  - `scripts/run_anchor_index_experiment.py`
  - `analysis_outputs/anchor_ray_selector/anchor_ray_index_experiment.md`
- Scope:
  - Used the top 80 anchor-ray selections.
  - Tested OCR word indexes, index deltas, word lengths, first/last letter positions, center coordinates, line projection values, and line distances.
- Chain check:
  - 2,451 private-key candidates.
  - 12,255 private-key addresses checked.
  - 172 checksum-valid BIP39 candidates.
  - 516 BIP39-derived addresses checked.
  - Activity found: 0.
- Conclusion:
  - Ray-selected numeric/index streams are unlikely to be the key without an additional, stronger selector.

### 3D Article Map

- Status: active as an inspection tool, not a solved key branch.
- Evidence:
  - `scripts/build_3d_article_map_data.py`
  - `analysis_outputs/3d_article_map/index.html`
  - `analysis_outputs/3d_article_map/article_3d_map_data.json`
  - `analysis_outputs/3d_article_map/3d_deconstruction_report.md`
- Scope:
  - Mapped every OCR character from pages 75-80 onto high-resolution page planes.
  - Added word scoring, orange highlights, reflected highlight boxes, anchors, and ray selectors.
  - Added browser-local correction overlay for manually typing exact line text where OCR is wrong or incomplete.
  - Added manual markup for bold words/letters, orange highlight spans, and black/inverted highlight spans.
  - Added `analysis_outputs/3d_article_map/user_annotated_transcript.txt` as the user's full supplied annotated transcript reference.
  - Added `analysis_outputs/3d_article_map/user_markdown_transcript.md` as the user's second full Markdown transcript reference.
  - Added `scripts/analyze_markdown_markup.py` and `scripts/check_markdown_markup_keys.py` for parsing and bounded checking of Markdown bold streams.
- Counts:
  - 7,299 OCR characters.
  - 1,243 OCR words.
  - 16 anchors.
  - 29 reflected highlight boxes.
  - 40 top ray selections.
- Finding:
  - Page 76 is still the densest target region, with 95 scored/important words.
  - The strongest visible cluster remains President/Nayib/El Salvador/IMF/volcano language.
  - Markdown partial-bold letter streams are real structured evidence:
    - page lengths 70, 31, 57, 12, 78;
    - combined partial-bold length 248.
  - Direct private-key and BIP39 checks over these streams found no activity:
    - 7,090 private-key addresses checked.
    - 282 BIP39-derived addresses checked.
- Next test:
  - Map partial-bold stream positions back onto 3D page geometry and compare them with orange/black spans, fold axes, and page-76 anchor/ray selectors before running more key checks.

### Physical Magazine Scan

- Status: partly resolved.
- Evidence: local PDFs differ. High-res scan looks visually superior.
- Test run: downloaded the original Google Drive file linked from Bitcointalk to `analysis_outputs/external_clues/google_drive_article_download.pdf`.
- Result: the Google Drive file is byte-for-byte identical to `keyser bitcoin .pdf` (`sha256 0078fe23401fab4882303ae038df0de6b439f498acb852d3b226c366caf5ab5c`).
- Current conclusion: `keyser bitcoin .pdf` is the public Drive/OCR source; `magazine.pdf` is a separate higher-resolution visual source.
- Remaining test: obtain/compare an official or physical scan of Bitcoin Magazine Issue #24 if possible.

### Canonical Markup / Color Selector Model

- Status: active selector branch; direct key branch not supported yet.
- Evidence:
  - `scripts/build_canonical_char_model.py`
  - `scripts/analyze_selector_intersections.py`
  - `scripts/analyze_annotated_color_spans.py`
  - `analysis_outputs/3d_article_map/canonical_char_model.md`
  - `analysis_outputs/3d_article_map/selector_intersection_analysis.md`
  - `analysis_outputs/3d_article_map/annotated_color_span_analysis.md`
- Scope:
  - Built a corrected character/word model from the user-supplied Markdown transcript.
  - Preserved per-word flags for partial-bold, whole-bold, strike/grey, page, line, and word index.
  - Matched ray-selected text and reflected selections back onto corrected text.
  - Parsed orange and grey/black highlight annotations from the user-supplied natural-language transcript.
- Findings:
  - Corrected partial-bold stream lengths are now 72, 32, 61, 12, and 78 by logical page.
  - Page 76 target terms produce:
    - partial-bold: `lvdieNvz`
    - any-bold: `bitcoinheartBitcoinEllvdbuyingdipPresidentNayibBukeleIMFloanieNvzshitcoinerheart`
  - Page 76 named phrase hits:
    - `El Salvador` -> partial `lvd`
    - `President Nayib Bukele` -> all-bold phrase
    - `buying the dip` -> all-bold phrase
    - `IMF loan` -> all-bold phrase
    - `Volcano Bonds` -> grey/color span, not bold in the Markdown model
    - `shitcoiner at heart` -> all-bold orange phrase
  - Orange color on page 76 isolates public/semantic phrases, not hidden partial letters:
    - `Get some toxicity...`
    - `by the rancid catnip of fiat money`
    - `buying the dip`
    - `shitcoiner at heart`
  - Grey/black color on page 76 isolates:
    - `Gotta be this way...`
    - `$1 billion`
    - `Volcano Bonds`
- Negative result:
  - Page-pair bimanual interleaving, page-76 target-term streams, ray ∩ corrected text, reflected-text ∩ corrected markup, and canonical-number indexing did not produce readable instructions or key-shaped strings.
- Next test:
  - Use the color span word indexes as human-readable labels, then intersect them geometrically with reflected orange/black mask boxes and fold axes.
  - Do not repeat broad hashing from all color/bold text unless a clean intermediate rule appears.

### Color / Reflection Geometry

- Status: active as registration evidence; not a solved selector.
- Evidence:
  - `scripts/analyze_color_reflection_geometry.py`
  - `scripts/analyze_overlapped_color_neighbors.py`
  - `analysis_outputs/3d_article_map/color_reflection_geometry.md`
  - `analysis_outputs/3d_article_map/overlapped_color_neighbors.md`
- Findings:
  - Reflected boxes overlap specific page-76 color spans:
    - orange `Get some toxicity...`
    - grey `Gotta be this way...`
    - orange `by the rancid catnip of fiat money`
    - grey `It's a stun gun to the genitals`
    - orange `buying the dip`
    - grey `$1 billion`
  - Nearby partial-bold extraction from those reflected-overlapped spans reduces the signal but does not solve it:
    - radius 10: `ippedelbe`
    - radius 20: `beippedelbelvd`
    - radius 40: `eelibeeelibeippedelbeeieielvdlvdlvdieNvz`
- Conclusion:
  - The mirror layer is concentrated around the page-76 color/El Salvador corridor, but the final ordering/letter selector is still missing.
  - This branch should continue by improving affine/physical-spread registration, not by hashing these reduced streams directly.

### Schott Literal Mechanisms

- Status: direct key path ruled out; physical overlay branch remains useful as registration evidence.
- Evidence:
  - `scripts/run_schott_literal_experiments.py`
  - `analysis_outputs/schott_literal_experiments/schott_literal_experiments.md`
  - `analysis_outputs/schott_literal_experiments/schott_literal_experiments.json`
- Scope:
  - Tested physical front/back leaf mirroring:
    - 75/76
    - 77/78
    - 79/80
  - Tested literal mirror-writing string transforms:
    - character reverse
    - word reverse
    - line reverse
    - reversed word order with every word reversed
    - backward WIF/Base58 checksum windows
  - Tested bimanual interleaving of reflected text pulls and corrected partial-bold page pairs.
  - Tested first-letter delta/XOR-like streams from top anchor rays.
  - Tested strict BIP39 ray interception.
- Chain result:
  - 66 experiment streams.
  - 708 private-key candidates.
  - 3,540 derived addresses checked.
  - Activity found: 0.
  - Strict BIP39 ray mnemonic candidates: 0.
- Hold-to-light positive context:
  - 75 -> 76 again lands near `president of El Salvador` and `Nayib Bukele`.
  - 76 -> 75 lands on title/black-hole/coattails/gullible language.
  - 77 -> 78 lands on love/war/fiat-money language.
  - 78 -> 77 lands on Roger/Peter McCormack/legal-system/demonetization language.
  - 80 -> 79 lands on the final wrap-up/rabbit-hole ending.
- Strict BIP39 finding:
  - Some ray selections contain BIP39 words, but only short clusters such as `nation sell`, `heart all nothing`, `skin nothing heart`, `dumb brown`, and `universe miss`.
  - No complete 12/24-word checksum-valid mnemonic.
- Conclusion:
  - Literal Schott operations do not directly produce the key.
  - The Schott clue still supports physical mirroring/registration, but the missing rule is likely a selector/order rule after alignment, not another direct text-to-key transform.

### High-Resolution Highlight Text Audit

- Status: canonical text source for highlighted material.
- Evidence:
  - `scripts/audit_highres_highlights.py`
  - `scripts/build_highres_grey_highlight_sheet.py`
  - `analysis_outputs/highlight_audit/highres_exact_highlight_source.md`
  - `analysis_outputs/highlight_audit/highres_manual_highlight_reading.md`
  - `analysis_outputs/highlight_audit/highres_manual_grey_reading.md`
  - `analysis_outputs/highlight_audit/visual_orange_contact_sheet.jpg`
  - `analysis_outputs/highlight_audit/manual_grey_highres_contact_sheet.jpg`
- Scope:
  - Re-read orange and grey/black highlighted text from the high-resolution article images.
  - Compared the visual readings against the OCR-derived model and the user-supplied transcript.
  - Separated exact highlight text from geometric/OCR diagnostics so future selector tests do not inherit OCR mistakes.
- Findings:
  - OCR is not reliable for highlighted text. It produced bad readings such as `Biteoiny`, `ByiiREeraipy`, empty boxes, and several misprojected crops.
  - The current exact highlight source is `analysis_outputs/highlight_audit/highres_exact_highlight_source.md`.
  - Important corrections:
    - p78 reads `The numbers don’t lie.`, not singular `number`.
    - p78 reads `hate toys in Afghanistan`, not `hate toy`.
    - p78 orange excludes visible but unhighlighted connector text `for example` / `that some estimate cost`; the actual orange spans are `America left $85 BILLION worth of hate toys in Afghanistan,` and `$2 trillion fiat cuck-bucks.`
    - p79 reads `fiat, shitcoins or gold`, not singular `shitcoin`.
    - p77 grey span reads `salesmen`, not `salesman`.
    - p76 parenthetical after grey `nonsense` reads `10years` with no space.
    - punctuation/quotes matter in `Bitcoin.`, `“buying the dip.”`, `shitcoiner at heart.`, `“Maximalist”`, and `“Volcano Bonds”`.
  - Grey/black coordinates from older manual boxes are lower confidence than the visual reading. `$1 billion`, `“Volcano Bonds”`, and `Faketoshi` were verified from the high-res page view rather than trusted from projected crop positions.
- Conclusion:
  - Use the high-res manual highlight files as the source of truth for all highlight-text experiments.
  - Use OCR and old box coordinates only for visual registration and geometry checks, not for exact phrase text.
- Next test:
  - Re-run small, explanation-first highlight stream tests from the exact high-res source only: page order, color order, first/last letters, word counts, mirror order, and page-76 intersections.

### Exact Highlight Stream Check

- Status: direct key path not supported; exact text is still useful as selector evidence.
- Evidence:
  - `scripts/analyze_highres_exact_highlights.py`
  - `analysis_outputs/highlight_audit/highres_exact_highlight_streams.md`
  - `analysis_outputs/highlight_audit/highres_exact_highlight_streams.json`
- Scope:
  - Tested only the manual high-res highlight text, excluding OCR-derived phrase text.
  - Generated page/color streams, phrase initials, word initials, word-last letters, word lengths, interleaved color spans, BIP39 word presence, and local WIF/minikey/exact-hex checks.
- Findings:
  - Orange spans: 20.
  - Grey/black spans: 14.
  - Streams generated: 96.
  - Contiguous checksum-valid BIP39 12/24-word mnemonics: 0.
  - WIF/exact-hex direct candidates: 0.
  - Filtered BIP39-word checksum hits: 11, treated as accidental because they skip non-BIP39 words inside ordinary prose.
  - Two minikey-checksum windows appeared:
    - `SSUHNRS5gosftiwsattemietat`
    - `SFLZmLDontfaforshitcoi`
  - Both minikeys were checked across compressed P2PKH, uncompressed P2PKH, P2SH-P2WPKH, P2WPKH, and P2TR. Activity found: 0.
- Conclusion:
  - Exact highlighted prose does not directly solve as key material.
  - Treat phrase/word initials and page/color grouping as possible ordering labels for geometry, not as standalone key strings.

### Exact High-Res Highlight / Reflection Geometry

- Status: active geometry branch; stronger than direct text branch.
- Evidence:
  - `scripts/analyze_exact_highres_reflection_geometry.py`
  - `analysis_outputs/3d_article_map/exact_highres_reflection_geometry.md`
  - `analysis_outputs/3d_article_map/exact_highres_reflection_geometry.json`
- Scope:
  - Rematched the corrected high-res highlight source onto the 3D article-map word boxes.
  - Tested reflected highlight boxes against exact high-res spans.
  - Used OCR only for approximate coordinates, not for exact phrase text.
- Findings:
  - Correcting p78 orange overcapture does not change the core geometry.
  - Page 76 remains the strongest concentration of exact-highlight/reflection intersections.
  - Strong page-76 hits:
    - orange `Get some toxicity. Get some bitcoin. Open your heart to Bitcoin.`
    - orange `by the rancid catnip of fiat money.`
    - orange `“buying the dip.”`
    - grey `It’s a stun gun to the genitals.`
    - grey `$1 billion`
  - The strongest multi-source overlaps are `“buying the dip.”`, `It’s a stun gun to the genitals.`, and `$1 billion`, each touched by page 78 and page 79 reflected boxes.
  - `“Volcano Bonds”` and `shitcoiner at heart.` still do not receive a strong reflected-box hit in the current geometry.
- Conclusion:
  - The active target is still the page-76 El Salvador/Bukele/IMF corridor plus nearby orange/grey spans.
  - `Volcano Bonds` and `shitcoiner at heart.` are semantic anchors unless affine registration changes their geometry.
- Next test:
  - Affine-register pages 76/78/79 using visual anchors, then re-run exact-span intersections from registered boxes instead of OCR-derived boxes.

### Anchor Pattern Registration

- Status: ruled out as precise registration from the current manual anchor list; still useful as orientation evidence.
- Evidence:
  - `scripts/analyze_affine_anchor_registration.py`
  - `analysis_outputs/source_audit/affine_anchor_registration.md`
  - `analysis_outputs/source_audit/affine_anchor_registration.json`
- Scope:
  - Tested whether mirrored page-79 pill centers can be registered onto page-76 X/dollar/black-bar/wire anchors with a simple similarity transform.
  - Tested all 3-, 4-, and 5-point correspondence subsets/permutations from the current manual anchors.
- Findings:
  - Best 3-pair fit: mean nearest distance across all pills 140.10 px, max 269.41 px.
  - Best 4-pair fit: mean nearest distance 167.16 px, max 267.32 px.
  - Best 5-pair fit: mean nearest distance 258.56 px, max 432.87 px.
- Conclusion:
  - The current anchor set is too loose for letter-level affine registration.
  - Three-point fits are likely overfit coincidences; four- and five-point fits are not good enough.
  - Do not use the current p79-pill -> p76-anchor mapping as a final selector.
- Next test:
  - Build a visual registration workbench/contact sheet for pages 76/79 and manually mark true corresponding overlay points before re-running exact-span geometry.

### 76/79 Visual Registration Workbench

- Status: active visual-inspection aid; not a final selector.
- Evidence:
  - `scripts/build_registration_workbench.py`
  - `analysis_outputs/source_audit/registration_workbench_76_79.md`
  - `analysis_outputs/source_audit/registration_workbench_76_79_contact_sheet.jpg`
  - `analysis_outputs/source_audit/registration_workbench_76_79_best_overlay.jpg`
  - `analysis_outputs/source_audit/registration_workbench_76_79_best_masks.jpg`
- Scope:
  - Horizontally mirrored page 79 over page 76.
  - Swept simple x/y translations in the right-side visual corridor `(1450, 0, 2544, 3264)`.
  - Scored dark/orange/yellow feature-mask overlap.
- Findings:
  - Best tested translation: `dx=-20`, `dy=240`.
  - Best balanced overlap score: `0.16754`.
  - Unshifted balanced overlap score: `0.07172`.
  - Top translations cluster around `dy=240`, so the shifted overlay is more useful for inspection than the raw hflip overlay.
- Conclusion:
  - Translation improves region-level overlay alignment.
  - The best shifted overlay still has heavy text ghosting and does not produce clean pill-to-X/dollar/bar correspondences.
  - Do not use this translation as a final extraction rule.
- Next test:
  - Run a small rotation/scale sweep around `dx=-20`, `dy=240`, or manually mark true corresponding points on the best overlay before re-running exact-span geometry.

### 76/79 Rotation/Scale Registration Sweep

- Status: active visual-inspection aid; ruled out as precise extraction transform.
- Evidence:
  - `scripts/build_registration_rotation_scale_sweep.py`
  - `analysis_outputs/source_audit/registration_rotation_scale_76_79.md`
  - `analysis_outputs/source_audit/registration_rotation_scale_76_79_contact_sheet.jpg`
  - `analysis_outputs/source_audit/registration_rotation_scale_76_79_best_overlay.jpg`
  - `analysis_outputs/source_audit/registration_rotation_scale_76_79_best_masks.jpg`
- Scope:
  - Quarter-resolution sweep around the best 76/79 translation-only overlay.
  - Tested small rotations, scale changes, and nearby translations in the right-side visual corridor.
- Findings:
  - Local translation baseline: balanced score `0.14172`, jaccard `0.07626`.
  - Best local transform: `dx=20`, `dy=240`, `angle=2°`, `scale=1.02`.
  - Best balanced score: `0.16152`.
  - Improvement over local translation baseline: `1.140x`.
- Conclusion:
  - Rotation/scale modestly improves visual feature overlap.
  - The overlay still has heavy ghosting and does not produce clean letter-level or anchor-to-anchor registration.
  - Do not use this transform as a final selector.
- Next test:
  - Manually mark true corresponding points on the improved overlay, or focus on geometry-supported page-76 semantic clusters (`buying the dip`, `$1 billion`, IMF/Bukele/Volcano Bonds) and test only simple ordering labels.

### Page-76 Semantic Cluster Order

- Status: active as evidence for the page-76 corridor; not a solved selector.
- Evidence:
  - `scripts/analyze_page76_semantic_cluster_order.py`
  - `analysis_outputs/3d_article_map/page76_semantic_cluster_order.md`
  - `analysis_outputs/3d_article_map/page76_semantic_cluster_order.json`
- Scope:
  - Used only exact high-res page-76 highlight spans that survive reflected-geometry checks.
  - Checked reading order, geometry order, source-side labels, and nearby partial-bold letters.
  - Did not hash or derive keys.
- Findings:
  - Reading-order phrase initials: `ggbib1`.
  - Reading-order source-side pattern: `RRLBBB`.
  - Geometry-order phrase initials: `ggibb1`.
  - Dual-source phrase initials: `ib1`.
  - Radius-20 nearby partial-bold stream in reading order: `beippedelbelvdlvd`.
  - Dual-source radius-20 partial-bold stream: `lvdlvd`.
- Conclusion:
  - The page-76 cluster order is structured, but it does not read as an instruction.
  - Nearby partial-bold fragments continue to point to known semantic anchors: `lvd` for Salvador and wider-radius `ieNvz` for Mike Novogratz.
  - This strengthens page-76 as the target corridor but does not provide the final selector.
- Next test:
  - Use these page-76 semantic clusters as ordering labels for existing anchor-ray selections, or manually mark true overlay correspondences on the improved 76/79 registration image.

### Cluster-Labeled Anchor Rays

- Status: ruled out as final selector; reinforces page-76 corridor.
- Evidence:
  - `scripts/analyze_cluster_labeled_rays.py`
  - `analysis_outputs/3d_article_map/cluster_labeled_rays.md`
  - `analysis_outputs/3d_article_map/cluster_labeled_rays.json`
- Scope:
  - Used geometry-supported page-76 semantic clusters as labels for existing anchor-ray selections.
  - Checked whether cluster order, source-side labels, ray initials, and ray bold material produce an instruction.
  - Did not hash or derive keys.
- Findings:
  - Cluster labels in reading order: `OPEN_HEART|FIAT_NONSENSE|FIAT_CATNIP|STUN_GUN|BUY_DIP|ONE_BILLION`.
  - Source-code pattern: `RRLBBB`.
  - Phrase initials: `ggbib1`.
  - Best-ray first-letter stream: `bUItdSsaphebmcbUItdSsaphebmcmbhatmbhaIItotIoEMHwhtm`.
  - Best-ray bold stream: `bitcoinUTXObitcoinUTXOthetheIEl`.
  - Best-ray partial-bold stream: empty.
- Conclusion:
  - Cluster labels do not impose a readable message over anchor-ray selections.
  - The same broad ray supports multiple early clusters, so the apparent order is not independent.
  - Later rays touch the IMF/El/Monetary corridor; this is semantic reinforcement, not a final selector.
- Next test:
  - Manually mark true corresponding points on the improved 76/79 overlay. Automated global alignment and semantic/ray ordering have both failed to produce the missing selector.

### Manual 76/79 Correspondence Sheet

- Status: ruled out for manual affine correspondences; useful as visual evidence.
- Evidence:
  - `scripts/build_manual_correspondence_sheet.py`
  - `analysis_outputs/source_audit/manual_correspondence_sheet_76_79.md`
  - `analysis_outputs/source_audit/manual_correspondence_sheet_76_79.jpg`
- Scope:
  - Inspected the best current 76/79 transform: `dx=20`, `dy=240`, `angle=2°`, `scale=1.02`.
  - Built region panels for page 76, transformed mirrored page 79, blended overlay, and feature mask.
- Findings:
  - `wire_open_heart`: page-79 wire crosses page-76 opening highlight, but page 76 has no matching wire object for a direct correspondence.
  - `fiat_nonsense`: overlap is mostly text/highlight bars.
  - `el_salvador_imf`: regional alignment is visible, but stable non-text marks are lacking.
  - `pills_dollar_marks`: page-79 pills and page-76 X/dollar marks share a region but are not one-to-one matching marks.
- Conclusion:
  - The improved 76/79 overlay does not provide four trustworthy non-text correspondence points for manual affine registration.
  - Keep 76/79 as orientation/region evidence, not letter-level geometry.
- Next test:
  - Shift to another physical relationship, especially front/back leaf 76/75 or 78/77, where literal hold-to-light correspondence may be more direct.

### Leaf Hold-To-Light Front/Back Test

- Status: ruled out as a clean final selector.
- Evidence:
  - `scripts/build_leaf_hold_to_light_sheet.py`
  - `analysis_outputs/source_audit/leaf_hold_to_light_sheet.md`
  - `analysis_outputs/source_audit/leaf_hold_to_light_sheet.jpg`
- Scope:
  - Tested physical front/back leaf overlays with the back page horizontally mirrored: 75/76, 77/78, and 79/80.
  - Added highlight-only scoring to avoid confusing dark background/art/text overlap with actual highlighted-mask correspondence.
- Findings:
  - `77_view_78_through` has the highest full feature score, balanced `0.26451`, but only highlight balanced `0.00612`.
  - `79_view_80_through` has the highest highlight-only score, highlight balanced `0.08640`.
  - `75_view_76_through` has weak feature and highlight scores: balanced `0.10400`, highlight balanced `0.00319`.
- Conclusion:
  - The 77/78 apparent hit is mostly page darkness and text density.
  - The 79/80 highlight-only hit is driven by broad bottle/art color plus highlight bands, not precise word/letter registration.
  - The expected 75/76 page-76 leaf relationship does not show a strong highlight-mask correspondence.
  - Do not use direct front/back hold-to-light overlay as the final extraction rule unless a physical scan reveals different bleed-through geometry.
- Next test:
  - Prefer exact high-res highlighted spans plus simple human-readable selector tests, or source-comparison against the physical magazine/official scan.

### Exact Highlight Selector Audit

- Status: ruled out for simple selector streams; useful as canonical mapping evidence.
- Evidence:
  - `scripts/analyze_highlight_selector_audit.py`
  - `analysis_outputs/highlight_audit/highlight_selector_audit.md`
  - `analysis_outputs/highlight_audit/highlight_selector_audit.json`
- Scope:
  - Used exact high-res orange/grey highlighted spans and canonical Markdown bold markup.
  - Checked phrase initials, word initials, word endings, word-length letters, full-bold intersections, and partial-bold intersections.
  - Applied only low-parameter readability checks: raw, reverse, Atbash, and Caesar transforms against selector-like words.
  - Did not derive or check private keys.
- Findings:
  - 34 highlighted spans checked.
  - 33 article-text spans matched contiguously to the canonical model.
  - 0 partial article-text matches after normalizing contractions and hyphenated compounds.
  - p80 pill/bottle package copy remains outside the canonical article body, as expected.
  - Main phrase-initial streams:
    - all: `TLFMKLGbbsThTAttiTESmDGIbVSFsIgmww`
    - orange: `TLFMKLGbbsThTAttiTES`
    - grey/black: `mDGIbVSFsIgmww`
    - page 76: `GbbsGIbV`
  - Page-76 bold-highlight stream is readable prose, not an instruction:
    - `GetsometoxicityGetsomebitcoinOpenyourhearttoBitcoinbytherancidcatnipoffiatmoneybuyingthedipshitcoineratheart`
- Conclusion:
  - Exact highlighted spans plus bold markup do not yield a simple human-readable selector through initials, endings, lengths, or bold intersections.
  - Selector-word hits are ordinary words already present in highlighted prose (`BITCOIN`, `TOXIC`, `BUY`, `DIP`, `LAYER`, etc.), not new instructions.
  - Keep this file as the clean mapping reference for future tests.
- Next test:
  - Compare source images/scans or test a manual rule derived directly from the public mirror-writing clue, rather than adding more generic stream transforms.

### Reflected Highlight Graph

- Status: active as page-76 evidence; ruled out as a clean ordering selector.
- Evidence:
  - `scripts/analyze_reflected_highlight_graph.py`
  - `analysis_outputs/3d_article_map/reflected_highlight_graph.md`
  - `analysis_outputs/3d_article_map/reflected_highlight_graph.json`
- Scope:
  - Used exact high-res highlight geometry plus reflected OCR/mask hits.
  - Ranked edges by overlap strength.
  - Checked whether reflected geometry creates a one-edge-per-highlight ordering rule.
  - Did not derive or check private keys.
- Findings:
  - 25 total reflected-hit edges.
  - 9 strong edges.
  - 17 medium-or-strong edges.
  - All 17 medium-or-strong edges land on page 76.
  - Medium/strong page pair counts:
    - 78 -> 76: 8.
    - 79 -> 76: 9.
  - Page-76 target initials by graph order: `GGGbbbbbIIII$$$$$`.
  - Page-76 source-page pattern by graph order: `7979797878787979787879797878787979`.
- Conclusion:
  - The reflected geometry strongly reinforces page 76 as the target page.
  - It does not give a clean extraction order; the hits are many-to-one and repeat broad prose regions.
  - Best semantic edges remain in the El Salvador/Bukele/IMF/buying-bitcoin corridor, especially `“buying the dip.”` and `$1 billion`.
- Next test:
  - Source/physical scan comparison, or one explicit mirror-writing rule applied only to the page-76 corridor.

### Current Working Diagnosis

- Status: active.
- Source facts:
  - `keyser bitcoin .pdf` and `analysis_outputs/external_clues/google_drive_article_download.pdf` are identical OCR PDFs: MD5 `02417fa3c9916d27677775c7338582f5`.
  - `magazine.pdf` is a different high-res source: MD5 `2c454d800cf2971c1f86fd016f64b7a0`.
  - `magazine.pdf`: `610.56 x 783.36 pts`, page rotation `180`, extracted images `2544 x 3264`.
  - OCR PDF: `612 x 792 pts`, page rotation `0`, extracted images `2040 x 2805`.
- Diagnosis:
  - What is missing is probably not another key format or hash transform.
  - The missing piece is most likely either exact source/physical registration or a very simple mirror-writing selector applied only after that registration is correct.
  - Page 76 remains the best target page.
- Direction:
  - Use `magazine.pdf` / high-res page images as geometry truth.
  - Use OCR PDF only as text assistance.
  - Next bounded test should compare high-res and OCR sources directly, then apply one mirror-clue selector to the page-76 corridor.

### Source Registration Gap

- Status: active constraint; confirmed geometry risk.
- Evidence:
  - `scripts/analyze_source_registration_gap.py`
  - `analysis_outputs/source_audit/source_registration_gap.md`
  - `analysis_outputs/source_audit/source_registration_gap.json`
  - `analysis_outputs/source_audit/source_registration_gap_contact_sheet.jpg`
- Scope:
  - Compared high-res `magazine.pdf` page images against OCR PDF page images.
  - Measured content-box mapping versus orange-highlight mapping.
  - Generated a visual contact sheet for high-res / OCR / content-aligned pages.
- Findings:
  - OCR PDF images include scan/photo distortion: gutter shadow, curvature, different crop, and non-uniform scale.
  - Content-box mapping and highlight mapping differ by about 96-129 OCR pixels mean error on pages 75-79, with max errors around 162-228 OCR pixels.
  - p76 specifically has mean/max content-vs-highlight delta `125.89 / 227.67` OCR pixels.
  - This is too large for letter-level fold/mirror extraction.
- Conclusion:
  - Use OCR only to label regions or recover text.
  - Do final fold/mirror geometry on high-res magazine images or a physical scan.
- Next test:
  - Build the mirror-writing selector directly on the high-res page-76 corridor, then map selected regions back to text only after geometry is decided.

### High-Res Page-76 Mirror Selector

- Status: raw high-res hflip ruled out; high-res geometry remains the right base.
- Evidence:
  - `scripts/analyze_highres_page76_mirror_selector.py`
  - `analysis_outputs/source_audit/highres_page76_mirror_selector.md`
  - `analysis_outputs/source_audit/highres_page76_mirror_selector.json`
  - `analysis_outputs/source_audit/highres_page76_mirror_selector_overlay.jpg`
- Scope:
  - Reflected high-res page-78/page-79 orange boxes onto high-res page 76.
  - Compared against page-76 orange highlights and manually verified page-76 grey/black text boxes.
  - Avoided OCR geometry entirely.
- Findings:
  - 14 reflected source boxes tested.
  - 4 meaningful intersections.
  - Target pattern: `B1B1B2O3`.
  - Source-page pattern: `79797978`.
  - p79 `That’s right, Bitcoin will take all the energy.` and `all the energy.` overlap the p76 fiat-nonsense grey band.
  - p78 `$2 trillion fiat cuck-bucks.` overlaps p76 orange `buying the dip.`
- Conclusion:
  - Simple high-res page-center horizontal mirroring is not the final selector.
  - The result is still semantically coherent but too sparse and many-to-one for extraction.
- Next test:
  - Add the physical operation missing from raw hflip: spread/fold/spine translation or manual physical-scan alignment.

### High-Res Facing-Spread Fold

- Status: ruled out as final selector.
- Evidence:
  - `scripts/analyze_highres_spread_fold_pairs.py`
  - `analysis_outputs/source_audit/highres_spread_fold_pairs.md`
  - `analysis_outputs/source_audit/highres_spread_fold_pairs.json`
  - `analysis_outputs/source_audit/highres_spread_fold_pairs_contact_sheet.jpg`
- Scope:
  - Tested true facing-spread geometry on high-res pages: 76/77 and 78/79.
  - Reflected orange highlights across the spine onto the opposite page's orange and manually verified grey/black highlights.
- Findings:
  - 77 -> 76: 0 meaningful intersections.
  - 76 -> 77: p76 `by the rancid catnip of fiat money.` overlaps p77 `shitcoiners, useless Royals`.
  - 79 -> 78 and 78 -> 79 form one reciprocal hit between `Everyone will live their own experience in the rabbit hole.` and `the game-theorized Bitcoin protocol,`.
- Conclusion:
  - Ordinary facing-spread folding is too sparse and does not explain the page-76 El Salvador corridor.
  - Treat the reciprocal 78/79 hit as semantic only, not extraction.
- Next test:
  - Stop generic fold tests. Use one explicit mirror-writing read rule on page 76, or require a physical scan/photo for more precise alignment.

### Page-76 Mirror-Read Rule

- Status: ruled out as text instruction.
- Evidence:
  - `scripts/analyze_page76_mirror_read_rule.py`
  - `analysis_outputs/3d_article_map/page76_mirror_read_rule.md`
  - `analysis_outputs/3d_article_map/page76_mirror_read_rule.json`
- Scope:
  - Used only medium/strong reflected hits landing on page 76.
  - Reversed reflected source text by words and by characters.
  - Checked for a readable instruction before any key generation.
- Findings:
  - 17 reflected graph rows checked.
  - 4 high-res-only cross-check rows included.
  - No independent instruction appears under word reversal or character reversal.
  - Hits such as `BUY`, `DIP`, `IMF`, `SALVADOR`, and `BILLION` are already present in the visible paired phrases.
- Conclusion:
  - The public mirror-writing clue is unlikely to mean simply reverse the reflected prose strings.
  - The remaining value is semantic/geometric, not procedural.
- Next test:
  - Stop text-transform streams. Inspect non-text marks and line-level order on the high-res page-76 corridor, or acquire a physical scan/photo for alignment.

### Page-76 Non-Text Marks

- Status: ruled out as anchor system.
- Evidence:
  - `scripts/analyze_page76_nontext_marks.py`
  - `analysis_outputs/source_audit/page76_nontext_marks.md`
  - `analysis_outputs/source_audit/page76_nontext_marks.json`
  - `analysis_outputs/source_audit/page76_nontext_marks_overlay.jpg`
- Scope:
  - Detected large high-res non-text black marks on page 76.
  - Reflected page-79 pill fragments and swept simple translations.
- Findings:
  - 4 page-76 non-text marks detected.
  - 5 page-79 pill fragments tested.
  - Best translation: `dx=-50`, `dy=350`.
  - Best mean/max distance: `196.43 / 405.49` px.
  - Pairing is many-to-one and leaves a large outlier.
- Conclusion:
  - Page-79 pill fragments do not cleanly register to page-76 X/brush marks.
  - Do not treat pill/X marks as the solved alignment key.
- Next test:
  - Physical scan/photo alignment or manual line-level inspection of the page-76 corridor.

### Page-76 Line-Level Corridor

- Status: ruled out as local line selector; active as narrative evidence.
- Evidence:
  - `scripts/analyze_page76_line_level_corridor.py`
  - `analysis_outputs/3d_article_map/page76_line_level_corridor.md`
  - `analysis_outputs/3d_article_map/page76_line_level_corridor.json`
  - `analysis_outputs/source_audit/page76_line_level_corridor.jpg`
- Scope:
  - Inspected page-76 lines 19-32 as line units.
  - Checked line initials, last initials, highlighted-line positions, full-bold letters, and partial-bold letters.
- Findings:
  - Line initials: `DHtHIh$bclNbhM`.
  - Highlighted corridor positions: `4,7,9,10,11,13,14`.
  - Highlighted page-line indexes: `22,25,27,28,29,31,32`.
  - Highlighted line initials: `H$clNhM`.
  - Full bold stream: `EllvdbuyingthedipPresidentNayibBukeleIMFloanieNvzIdelluhushitcoineratheart`.
  - Partial-bold stream: `lvdieNvzdelluhu`.
- Conclusion:
  - The corridor reads as narrative, not an instruction.
  - The line-level streams do not reveal a selector.
  - This confirms the local digital work is at a selector gap.
- Next test:
  - Physical magazine scan/photo, or manual inspection of the original Canva/source clue for an instruction not represented in our local model.

### Source Clue Inventory / ThreadReader Noise

- Status: local external-clue inventory complete; no hidden written instruction found.
- Evidence:
  - `analysis_outputs/external_clues/source_clue_inventory.md`
  - `analysis_outputs/external_clues/source_clue_inventory.json`
  - `analysis_outputs/source_audit/thread_1632068898169450497.html`
- Scope:
  - Rechecked recovered announcement text, media sequence, Schott literal experiments, OVERDOSE title branch, and raw ThreadReader HTML.
- Findings:
  - The real announcement media set is seven images.
  - The seven images all reinforce the page-76 Bukele / IMF / volcano corridor.
  - Local files `08_EmQGt1qVoAAU-iB.jpg` and `09_EmQWsdEWEAAB38H.jpg` are ThreadReader related-thread noise from a November 7, 2020 thread, not the March 2023 puzzle announcement.
  - No additional written selector or instruction appears in the local external-clue reports.
- Conclusion:
  - Future media-derived ordering must ignore files 08/09.
  - The external clues confirm the target area but do not provide the missing selector.
- Next test:
  - Inspect the original Canva/browser clue or acquire a physical high-quality scan/photo of pages 75-80 before more alignment/key extraction.

### Media-Source Hygiene

- Status: complete.
- Evidence:
  - `analysis_outputs/external_clues/max_thread_media/announcement_media_urls.txt`
  - `analysis_outputs/external_clues/max_thread_media/excluded_threadreader_related_media.txt`
  - `analysis_outputs/external_clues/max_thread_media/recovered_thread_media_report.md`
- Finding:
  - Candidate scripts already use the seven real announcement media IDs.
  - The raw local folder still contains files 08/09 for provenance, but they are now explicitly excluded from puzzle-media ordering.
- Next test:
  - Do not spend more cycles on thread-media derivations unless a new external clue changes the ordering rule.

### Page-76 Two-Hand Selector

- Status: ruled out under current registration.
- Evidence:
  - `scripts/analyze_page76_twohand_selector.py`
  - `analysis_outputs/3d_article_map/page76_twohand_selector.md`
  - `analysis_outputs/3d_article_map/page76_twohand_selector.json`
- Scope:
  - Tested 78/79 as two hands into page 76.
  - Tested source-page binary, first/last target-letter rules, deduped target/source groups, strong-only groups, high-res `B1B1B2O3`, and adjacent-line reads around `buying the dip`.
- Findings:
  - Source-page bitstream `11100011001100011` does not decode to useful 7-bit or 8-bit text.
  - Two-hand streams do not form instruction text.
  - `B1B1B2O3` gives `be this and them` on page-76 target words by source index, and `That's all right fiat` when selecting source-label words by target index.
  - `That's all right fiat` is weak because it is not an instruction and does not select page-76 characters.
  - Reading below/above `buying the dip` gives repeated visible corridor lines, not a selector.
- Conclusion:
  - Do not promote the current two-hand/B1B1B2O3 branch without new source registration.
- Next test:
  - Source/physical registration or original Canva inspection.

### Page-80 Package Copy

- Status: weak support only; not a selector.
- Evidence:
  - `scripts/analyze_p80_package_copy.py`
  - `analysis_outputs/3d_article_map/p80_package_copy_audit.md`
  - `analysis_outputs/3d_article_map/p80_package_copy_audit.json`
- Manual transcription:
  - `FAKE AD`
  - `5 SYMPTOM RELIEF`
  - `Bitcoin FixesThis`
  - `100% Proof of Work Liquid`
  - `Fiat Humiditus Reliever / Anticentralization`
  - `5 SYMPTOM RELIEF`
  - `NAUSEA HEARTBURN INDIGESTION UPSET STOMACH SHITCOINS`
  - visually/semantically likely `16 FL OZ (473 mL)`; crop-only source records `6 FL OZ (473 mL)`.
  - `TOXIC BTB`
  - `80`
- Findings:
  - `5 SYMPTOM RELIEF` appears twice and the label lists exactly five symptoms: nausea, heartburn, indigestion, upset stomach, shitcoins.
  - This matches the five page-76 target groups.
  - `16` points to page-76 line 16, the `It’s a stun gun to the genitals.` line.
  - Other numbers (`100`, `473`, `80`) do not form a coherent page-76 word or line index stream.
- Conclusion:
  - p80 reinforces the five-target/page-76 model but does not supply the missing order/selector.
- Next test:
  - Only revisit p80 if physical/source alignment shows the bottle copy overlapping another page.

### Canva Source Inspection

- Status: inspected; supports orientation/source-risk only.
- Evidence:
  - `analysis_outputs/external_clues/canva_source_inspection.md`
  - `analysis_outputs/external_clues/canva_source_inspection.json`
  - `analysis_outputs/external_clues/canva_puzzle_note_thumbnail.png`
- Findings:
  - Design title: `PRIVATE_ANNOTATION_OMITTED`
  - Text notes pills not lining up, browser/PDF OCR missing `#0`, and `XX` lining up with barbed wire after rotation/mirroring.
  - Text also mentions `SHIT` and `FUCK ALL SHITCOINS` spills as possible orientation/positioning evidence.
  - No comments.
  - No presenter notes.
- Conclusion:
  - This is an investigator note board, not the original puzzle source.
  - It does not add a final selector.
  - It reinforces that the remaining blocker is exact source/registration, not another broad key-generation pass.
- Next test:
  - Physical scan/photo or higher-resolution export of the Canva overlay if visual annotations need to be measured.

### Dead-Branch Blacklist

- Status: created.
- Evidence:
  - `analysis_outputs/dead_branch_blacklist.md`
- Purpose:
  - Prevent repeat runs of low-EV branches: plain BIP39/SHA/WIF windows, media/tweet ID hashing, ray prose hashing, OCR coordinate geometry, generic geometry bytes, simple affine/pill registration, raw hold-to-light/facing-spread folds, plain reversed prose, current 78/79 two-hand selector, current `B1B1B2O3`, and p80 direct package-copy indexing.
- Still active:
  - Page 76 target surface.
  - Exact high-res or physical source registration.
  - Original Canva/browser clue inspection.

### Best Scan Source Lock

- Status: canonical local source confirmed.
- Evidence:
  - `analysis_outputs/source_audit/best_scan_source_lock.md`
  - `private_inputs/Desktop/magazine.pdf`
  - `magazine.pdf`
- Findings:
  - Desktop and project PDFs have the same MD5: `2c454d800cf2971c1f86fd016f64b7a0`.
  - The project has already been using the best scan.
  - Each page embeds a 2544 x 3264 px 300-ppi JPEG image.
- Conclusion:
  - Stop treating source choice as unresolved between local PDFs.
  - Continue with `magazine.pdf` as locked geometry truth.
- Next test:
  - High-res scan-native selector tests only; no OCR-PDF geometry.

### Five-Symptom Mapping

- Status: weak support only; not a selector.
- Evidence:
  - `scripts/analyze_five_symptom_mapping.py`
  - `analysis_outputs/3d_article_map/five_symptom_mapping.md`
  - `analysis_outputs/3d_article_map/five_symptom_mapping.json`
- Scope:
  - Tested whether p80's `5 SYMPTOM RELIEF` order maps onto the five page-76 reflected-graph target groups.
- Findings:
  - Symptom initials: `NHIUS`.
  - Symptom lengths: `6,9,11,12,9`.
  - Page-76 graph target initials: `GbbI$`.
  - Length-selected chars: `mcitn`.
  - Length-selected words: `bitcoin the the stun $1`.
  - Direct semantic matches point to known visible phrases, mainly heart/stun/shitcoiner.
- Conclusion:
  - The count `5` supports five page-76 targets, but symptom order does not reveal the extraction rule.
- Next test:
  - Keep p80 as support only. Continue with high-res page-76 geometry or external visual annotation if available.

### DOCM Formatting Sources

- Status: integrated; useful formatting witness.
- Evidence:
  - `scripts/analyze_docm_format_sources.py`
  - `scripts/analyze_docm_font_layers.py`
  - `scripts/analyze_docm_layer_selectors.py`
  - `analysis_outputs/docm_format_sources/docm_format_audit.md`
  - `analysis_outputs/docm_format_sources/docm_font_layer_audit.md`
  - `analysis_outputs/docm_format_sources/docm_layer_selector_audit.md`
- Sources:
  - `private_inputs/Desktop/BOLD.docm`
  - `private_inputs/Desktop/Article with Fonts.docm`
- Findings:
  - `Article with Fonts.docm` has no embedded VBA project and is the better Word-level formatting witness.
  - Yellow and black layers reproduce known orange/grey highlight structure.
  - `LonestarW00-Regular` isolates `OVERDOSE`.
  - `Stencil` isolates `BITCOIN IS TOXIC AF`.
  - `Typeka Mix` is a substantial alternate-font layer and overlaps many earlier manually marked partial-bold fragments.
  - New cyan layer: `MNBILLION`.
    - `M` in `Max Keiser`, p75.
    - `N` in `Nocoiners`, p75.
    - `BILLION` inside `$85 BILLION`, p78.
  - Cyan `BILLION` semantically bridges p78 `$85 BILLION` to the known p76 `$1 billion` corridor.
  - Typeka Mix initials, last initials, run lengths, and per-page streams do not form readable instructions.
- Conclusion:
  - Prefer `Article with Fonts.docm` over manual Markdown markup for future font/partial-bold work.
  - Register `MNBILLION` as a real anomaly, but not a final selector.
- Next test:
  - Use DOCM layers only with a stronger geometry/source selector, especially around page 76 and the p78-to-p76 money/Bukele/IMF corridor.

### BOLD.docm Macro Provenance

- Status: closed as original-formatting source; retained as provenance.
- Evidence:
  - `scripts/audit_bold_docm_macro.py`
  - `analysis_outputs/docm_format_sources/bold_docm_macro_audit.md`
  - `analysis_outputs/docm_format_sources/bold_docm_macro_audit.json`
- Findings:
  - `BOLD.docm` contains `word/vbaProject.bin` and `word/vbaData.xml`.
  - `word/vbaData.xml` references `HighlightWordsFromTextFile`.
  - Embedded VBA strings indicate a macro that reads words from `private_inputs\OneDrive\Desktop\Alles\TOXIC_AF\BIP39\otrobip.txt` and highlights them in the current document.
  - The referenced `otrobip.txt` file was not recovered locally.
  - No macros were executed.
- Conclusion:
  - `BOLD.docm` appears to be an investigator/generated highlight artifact, likely BIP39-word markup, not original puzzle typography.
  - Do not use `BOLD.docm` as evidence that the original puzzle bolding encodes BIP39 words.
- Next test:
  - Only revisit this branch if `otrobip.txt` is recovered or another source explains why those highlighted words should be treated as puzzle-native.

### Comparison Article Layouts

- Status: useful as style controls; no new selector.
- Evidence:
  - `scripts/compare_overdose_article_layouts.py`
  - `analysis_outputs/comparison_articles/comparison_layout_audit.md`
  - `analysis_outputs/comparison_articles/comparison_layout_audit.json`
  - `analysis_outputs/comparison_articles/issue26/contact_sheet.jpg`
  - `analysis_outputs/comparison_articles/bitcoin3/contact_sheet.jpg`
- Sources:
  - `private_inputs/Desktop/Issue_26.pdf`
  - `private_inputs/Desktop/bitcoin3.pdf`
- Findings:
  - Both comparison PDFs are image-only PDFKit exports using one 2040 x 2805 JPEG per page.
  - `Issue_26.pdf` uses a red/black censorship/redaction visual system and does not reproduce the Issue 24 orange/grey highlight grammar.
  - `bitcoin3.pdf` confirms that OVERDOSE/Max articles commonly use loud issue-specific art, portraits, full-page color art, and large display typography.
  - Neither comparison article shows the Issue 24 medicine-bottle/five-symptom label system.
  - Neither comparison article shows an obvious p76/p79-style mirrored corridor with orange/grey highlights, pill marks, X/barbed-wire marks, and money/Bukele/IMF semantics.
- Conclusion:
  - Broad OVERDOSE branding and loud Max collage art are house style.
  - Generic black/redaction bars are lower-signal because they occur in other Max layouts.
  - The Issue 24 medicine/highlight/mirror system remains higher-signal and should stay active.
- Next test:
  - If more Max articles are added, compare specifically for repeated orange/grey article-text highlights and medicine/pill/package mechanics, not for general visual loudness.

### Plain Article Text Correction

- Status: integrated; use as canonical plain-text witness.
- Evidence:
  - `scripts/integrate_plain_article_text.py`
  - `analysis_outputs/plain_text_transcript/user_plain_article_latest.txt`
  - `analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt`
  - `analysis_outputs/plain_text_transcript/canonical_plain_article_with_signature.txt`
  - `analysis_outputs/plain_text_transcript/plain_article_correction_report.md`
  - `analysis_outputs/plain_text_transcript/plain_article_correction_report.json`
- Findings:
  - The latest user-supplied plain text is useful but contains several exact-wording hazards.
  - Highest-impact fixes:
    - restored `“Volcano Bonds”`;
    - corrected `puts an end`;
    - restored `money printing`;
    - restored `$2 trillion fiat cuck-bucks`;
    - corrected `gargantuanly`;
    - corrected `It's a guaranteed`;
    - corrected `It's a fact baked`;
    - corrected `In so doing, our energy consumption`;
    - removed the extra `and` in `gets monetized for the first time`;
    - restored all-caps headline blocks where the scan/DOCM witness supports them.
  - Two corrected outputs now exist:
    - body-only DOCM-derived text;
    - body plus scan-visible `MAX KEISER` signature.
- Conclusion:
  - Use `canonical_plain_article_body.txt` for article-body word/line/index experiments.
  - Use `canonical_plain_article_with_signature.txt` only when the tested rule includes scan-visible signature text.
- Next test:
  - Re-run any future exact-text selector against the corrected plain witness, not the raw plain copy.

### Typeka Variant State Audit

- Status: reframed; old partial-bold branch downgraded, font-layer branch remains active.
- Evidence:
  - `scripts/analyze_typeka_variant_states.py`
  - `analysis_outputs/docm_format_sources/typeka_variant_state_audit.md`
  - `analysis_outputs/docm_format_sources/typeka_variant_state_audit.json`
  - `analysis_outputs/docm_format_sources/article_with_fonts_runs.json`
- User insight:
  - The apparent weird partial-bolding is likely caused by `Typeka Mix`, not by hand-selected bold letters.
  - The article uses Typeka regular, Typeka Mix, and bold Typeka formatting.
  - Other magazine articles reportedly do not use Typeka and are less stylized.
- Findings:
  - DOCM metadata has `Typeka` and `Typeka Mix`; it does not expose a separate `Typeka Bold` font name.
  - Bold Typeka is a Word run property on `Typeka`.
  - Variant counts:
    - `TYPEKA`: 167 runs, 3101 letters.
    - `TYPEKA_BOLD`: 128 runs, 2092 letters.
    - `MIX`: 47 runs, 738 letters.
  - Typeka Mix is phrase-like and substantial, not isolated hidden letters.
  - Typeka Mix initials, last letters, run lengths, non-regular run order, and compact state changes do not form readable instruction text.
- Conclusion:
  - Stop treating the earlier manual partial-bold stream as intentional hand-selected key letters.
  - Keep font changes active only as a layer that needs another selector, most likely page-76 mirror/highlight geometry.
- Next test:
  - Intersect Typeka Mix / Typeka-bold states with confirmed page-76 reflected-hit regions or exact high-res highlight boxes before doing any more key checks.

### Typeka Reflection Intersections

- Status: bounded selector test complete; no clean selector.
- Evidence:
  - `scripts/analyze_typeka_reflection_intersections.py`
  - `analysis_outputs/docm_format_sources/typeka_reflection_intersection_audit.md`
  - `analysis_outputs/docm_format_sources/typeka_reflection_intersection_audit.json`
- Scope:
  - Intersected `Article with Fonts.docm` Typeka states with medium/strong page-76 reflected-highlight graph hits.
- Findings:
  - Page-76 target spans are almost entirely `TYPEKA_BOLD`.
  - Typeka Mix does not appear inside the reflected target spans as a clean character/word selector.
  - Typeka Mix appears only in broader reflected/nearby snippet windows, mainly around semantic anchors such as `George Clinton` and `El Salvador`.
  - The reflection windows mix `TYPEKA`, `TYPEKA_BOLD`, and occasional `MIX`, so the font state does not produce a one-edge-per-letter or one-edge-per-word stream.
- Conclusion:
  - Rule out the simple rule “take Typeka Mix inside the reflected target spans.”
  - Keep Typeka states as labels, not a standalone extraction mechanism.
- Next test:
  - Improve visual registration of the page-76/page-79 corridor before applying Typeka-state filters again.

### Cyan `MNBILLION` Visibility

- Status: downgraded as printed-source clue; keep only as low-priority DOCM anomaly.
- Evidence:
  - `scripts/analyze_cyan_mnbillion_scan_visibility.py`
  - `analysis_outputs/docm_format_sources/cyan_mnbillion_scan_visibility.md`
  - `analysis_outputs/docm_format_sources/cyan_mnbillion_scan_visibility.json`
- Findings:
  - `Article with Fonts.docm` contains cyan-highlighted formatting that spells `MNBILLION`:
    - `M` in `Max Keiser`;
    - `N` in `Nocoiners`;
    - `BILLION` inside `$85 BILLION`.
  - The high-resolution magazine scan does not show this as a visible printed cyan layer.
  - Pages 75, 76, 77, 79, and 80 have `0` cyan-like pixels under both loose and strict highlighter thresholds.
  - Page 78 has only `5` loose-threshold cyan-like pixels and `0` strict-threshold pixels across the whole page.
  - Direct checks of the p75 `Nocoiners` box, p76 `$1 billion`, and p78 `$85/BILLION` orange crops all show `0` cyan pixels.
- Conclusion:
  - Do not use cyan as a printed highlight, geometry, or registration selector.
  - Only promote it again if independent evidence shows the DOCM formatting itself is an original puzzle source rather than an annotation/reconstruction.
- Next test:
  - Continue with scan-visible evidence: Typeka font states, orange/grey highlights, page-76 corridor, and improved physical/high-res registration.

### Registered 76/79 Line Alignment

- Status: active as a registration clue; not a final selector.
- Evidence:
  - `scripts/analyze_registered_76_79_selector.py`
  - `analysis_outputs/source_audit/registered_76_79_selector.md`
  - `analysis_outputs/source_audit/registered_76_79_selector.json`
  - `analysis_outputs/source_audit/registered_76_79_selector_overlay.jpg`
  - `analysis_outputs/source_audit/registered_76_79_selector_crop.jpg`
- Transform:
  - From rotation/scale sweep: p79 mirrored over p76 with `dx=20`, `dy=240`, `angle=2`, `scale=1.02`.
- Findings:
  - Raw p79 hflip hit pattern: `B1B1B2`.
  - Registered p79 hit pattern: `B1B2`.
  - The strongest registered hit is line-level:
    - p79 orange `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold`
    - maps onto p76 grey `Gotta be this way... post-1971 fiat money`.
    - It covers `77.0%` of the p76 target box, with centers about `10 px` apart.
  - The same p79 line also clips p76 grey `nonsense`.
- Conclusion:
  - The 76/79 transform is real enough to keep as orientation/registration evidence.
  - It does not yet explain how to extract a private key or instruction, because it selects a broad line pair rather than a smaller ordered set of words/letters.
- Next test:
  - Treat this line pair as a local anchor and inspect nearby Typeka states/highlight colors/line offsets for a smaller readable selector.

### Registered 76/79 Word Alignment

- Status: tested; no word-level selector.
- Evidence:
  - `scripts/analyze_registered_76_79_word_alignment.py`
  - `analysis_outputs/source_audit/registered_76_79_word_alignment.md`
  - `analysis_outputs/source_audit/registered_76_79_word_alignment.json`
  - `analysis_outputs/source_audit/registered_76_79_word_alignment.jpg`
- Findings:
  - The strong registered pair is:
    - p79 orange `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold`
    - p76 grey `Gotta be this way... post-1971 fiat money` plus `nonsense`.
  - At OCR-word-box level:
    - p79 source words inside the highlight: `16`.
    - p76 target words inside B1/B2: `12`.
    - direct transformed word overlaps: `0`.
  - The registered p79 text forms two approximate rows around y=`785` and y=`934`; the p76 target grey rows sit around y=`854` and y=`922`.
  - DOCM formatting for both sides is `TYPEKA_BOLD`; p79 is yellow/orange highlight, p76 is black/grey highlight.
  - `Typeka Mix` is absent from this local anchor.
- Conclusion:
  - The 76/79 alignment is real at highlight-block/line scale but not at word scale.
  - Do not use this line pair as a direct overlapping-word selector or Typeka Mix selector.
- Next test:
  - Inspect line offsets/gaps around the anchor, or look for an explicit alignment instruction in the original Canva/source clue.

### Registered 76/79 Line Offset

- Status: active as geometry evidence; no direct text selector.
- Evidence:
  - `scripts/analyze_registered_76_79_line_offset_rule.py`
  - `analysis_outputs/source_audit/registered_76_79_line_offset_rule.md`
  - `analysis_outputs/source_audit/registered_76_79_line_offset_rule.json`
- Findings:
  - Exact line pair:
    - p79 orange: `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold`.
    - p76 grey: `Gotta be this way. Forty years of dumb post-1971 fiat money nonsense`.
  - The transformed p79 source rows sit at y=`785.0` and y=`934.1`.
  - The source-row gap midpoint is y=`859.5`.
  - The main p76 grey row sits at y=`854.5`, only `5 px` from that midpoint.
  - This is a strong “between the lines” geometry observation.
  - Low-parameter text streams from the exact pair do not produce instruction language:
    - source initials `imettaswitfsog`;
    - target initials `GbtwFyodpfmn`;
    - reversed initials, last letters, length-mod streams, and above/below sandwich initials also fail.
- Conclusion:
  - Keep this as a real visual registration clue.
  - Do not treat the between-lines p76 sentence as direct key material or an instruction by itself.
- Next test:
  - Check whether the same line-gap behavior appears in other p76/p79 or p76/p78 highlight alignments. Unique behavior would make this a confirmation marker; repeated behavior may give an ordered sequence.

### Registered 76/79 Gap Recurrence

- Status: tested; unique calibration marker, not an ordered sequence.
- Evidence:
  - `scripts/analyze_registered_76_79_gap_recurrence.py`
  - `analysis_outputs/source_audit/registered_76_79_gap_recurrence.md`
  - `analysis_outputs/source_audit/registered_76_79_gap_recurrence.json`
- Findings:
  - Checked all `10` registered p79 highlight/source boxes against page-76 orange/grey target rows.
  - `4` p79 sources had OCR words.
  - `3` p79 sources formed two-row gaps after transformation.
  - `30` target-row/gap comparisons were scored.
  - Strict recurrence filter found exactly `1` strong recurrence:
    - p79 box 1 `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold`
    - gap midpoint y=`859.5`
    - p76 grey B1 `Gotta be this way... post-1971 fiat money`
    - target row y=`854.5`
    - delta `-5.0 px`
    - target coverage `0.770`.
  - Other p79 row gaps do not coincide with page-76 highlighted rows that also have meaningful overlap.
- Conclusion:
  - The p79 box 1 / p76 B1 alignment is unique in the current 76/79 transform.
  - Treat it as a calibration/registration marker, not a repeated extraction sequence.
- Next test:
  - Look for a separate ordering/instruction clue, especially in the original Canva/source clue or unique visual marks near the calibrated anchor.

### Calibrated Anchor Visual Marks

- Status: tested; no local ordering mark in immediate anchor crop.
- Evidence:
  - `analysis_outputs/external_clues/canva_source_inspection.md`
  - `scripts/analyze_calibrated_anchor_visual_marks.py`
  - `analysis_outputs/source_audit/calibrated_anchor_visual_marks.md`
  - `analysis_outputs/source_audit/calibrated_anchor_visual_marks.json`
  - `analysis_outputs/source_audit/calibrated_anchor_visual_marks.jpg`
- Findings:
  - The existing Canva inspection confirms the Canva board is an investigator note, not the original puzzle source.
  - Canva note text flags:
    - pills not lining up;
    - browser/PDF OCR missing `#0`;
    - `XX`, barbed wire, `SHIT`, and `FUCK ALL SHITCOINS` lining up after rotation/mirroring.
  - Immediate calibrated-anchor crop tested: `(350, 650, 2200, 1050)`.
  - Known anchor boxes removed:
    - p76 B1 `Gotta be this way... post-1971 fiat money`;
    - p76 B2 `nonsense`;
    - registered p79 `infinitely more efficient to transact and store wealth in than fiat, shitcoins or gold`.
  - Before known-anchor removal, residual p76/p79 feature overlap is `16,685 px`.
  - After text masking and known-anchor removal, extra overlap is only `212 px`.
  - Remaining components are noisy edge fragments rather than clear pills, wire knots, X marks, or ordering symbols.
- Conclusion:
  - The unique 76/79 anchor is useful for calibration, but it does not contain a visible local ordering cue in its immediate crop.
- Next test:
  - Inspect the broader page-76/page-79 visual system outside this crop, especially the Canva-mentioned `XX`/barbed-wire/`SHIT`/`FUCK ALL SHITCOINS` alignment, or obtain a higher-resolution physical/source overlay.

### Registered Canva Anchor Alignment

- Status: tested; orientation evidence only, not a selector.
- Evidence:
  - `scripts/analyze_registered_canva_anchor_alignment.py`
  - `analysis_outputs/source_audit/registered_canva_anchor_alignment.md`
  - `analysis_outputs/source_audit/registered_canva_anchor_alignment.json`
  - `analysis_outputs/source_audit/registered_canva_anchor_alignment.jpg`
  - `analysis_outputs/source_audit/registered_canva_anchor_alignment_bottom_crop.jpg`
- Scope:
  - Retested the Canva-mentioned broader visual system under the current best 76/79 registered transform: `dx=20`, `dy=240`, `angle=2`, `scale=1.02`.
- Findings:
  - `p79_pill_1` lands near the p76 X/XX mark: `56.8 px`.
  - Other pill/mark distances are much looser:
    - `p79_pill_4` to p76 dollar: `130.3 px`.
    - `p79_pill_3` to p76 dollar: `204.3 px`.
    - `p79_pill_2` to p76 X/XX: `229.1 px`.
    - `p79_pill_5` to p76 dollar: `421.2 px`.
  - The approximate p76 wire-knot line is far from the lower X/dollar/pill cluster:
    - p76 X/XX distance to wire line: `2225.1 px`.
    - p76 dollar distance to wire line: `2695.1 px`.
    - registered p79 pill distances to wire line: `2168.5-2700.6 px`.
- Conclusion:
  - The broader Canva visual system supports orientation/positioning, especially p79 pill 1 near p76 X/XX.
  - It does not provide a precise one-to-one registration or ordering rule under the current high-res transform.
  - The Canva `XX`/wire claim is not explained by the approximate wire-knot geometry used locally.
- Next test:
  - Inspect the actual Canva thumbnail/export at higher resolution to identify what `XX` and wire refer to, or pivot to true front/back leaf registration.

### Front/Back Leaf Box Registration

- Status: tested; downgraded as a selector under the current high-res scan.
- Evidence:
  - `scripts/analyze_front_back_leaf_box_registration.py`
  - `analysis_outputs/source_audit/front_back_leaf_box_registration.md`
  - `analysis_outputs/source_audit/front_back_leaf_box_registration.json`
  - `analysis_outputs/source_audit/front_back_leaf_box_registration_sheet.jpg`
- Scope:
  - Refined the physical hold-to-light/leaf theory by mirroring orange highlight boxes through true front/back leaves and allowing only a bounded crop-correction translation (`-180..180` px, step `20`).
  - OCR was not used as geometry; this is a high-res visual box audit only.
- Findings:
  - `75 -> 76` raw hflip gives `0` meaningful page-76 edges.
  - Best bounded `75 -> 76` translation is `dx=0`, `dy=-180`, with only two loose hits onto p76 grey box 1:
    - `They are the sum of` -> `Gotta be this way... post-1971 fiat money` (`target=0.114`, center distance `622.1 px`);
    - `all our neuroses.` -> same target (`target=0.077`, center distance `613.8 px`).
  - Other leaf pairs create isolated broad overlaps but no repeated selector pattern or page-76 corridor behavior.
- Conclusion:
  - The high-res digital front/back leaf registration does not explain the puzzle mechanism.
  - It should not be treated as the missing rule unless physical photos/scans reveal real bleed-through or printing offsets not present in `magazine.pdf`.
- Next test:
  - Inspect the original Canva thumbnail/export at higher resolution, or continue with page-76 corridor typography/order clues rather than more generic leaf overlays.

### Canva Thumbnail Export

- Status: tested; provenance/orientation note only.
- Evidence:
  - Connected Canva design `PRIVATE_CONTRIBUTOR`
  - `scripts/analyze_canva_thumbnail_export.py`
  - `analysis_outputs/external_clues/canva_thumbnail_export_audit.md`
  - `analysis_outputs/external_clues/canva_thumbnail_export_audit.json`
  - `analysis_outputs/external_clues/canva_thumbnail_regions.jpg`
  - `analysis_outputs/external_clues/canva_puzzle_note_thumbnail_6x.jpg`
  - `analysis_outputs/external_clues/canva_thumbnail_top_rows_8x.jpg`
  - `analysis_outputs/external_clues/canva_thumbnail_forensic_panel_8x.jpg`
- Findings:
  - Canva metadata confirms the design has `1` page and exposes only a `668x376` thumbnail.
  - The page endpoint returns the same `668x376` thumbnail already saved locally; no better read-only export is available through the current tool surface.
  - The thumbnail contains repeated tiny page/spread overlay rows and a bottom Forensically/clone-detection style screenshot.
  - The bottom screenshot visibly uses Forensically controls (`Algorithm`, `Clone Detection`, similarity/detail/cluster sliders), so this was an investigator's image-forensics board rather than an original puzzle source.
  - The `XX`/barbed-wire/`SHIT`/pill relationships cannot be measured reliably at this resolution.
  - No new written instruction appears beyond the already extracted note text.
- Conclusion:
  - Keep the Canva board as a note that orientation/positioning was suspected.
  - Do not use Canva-thumbnail geometry as source truth.
- Next test:
  - Move to page-76 corridor typography/order using the DOCM font layers and the verified 76/79 calibration anchor, unless higher-resolution Canva assets are obtained.

### Page-76 Corridor Font Order

- Status: tested; direct font-order selector closed.
- Evidence:
  - `scripts/analyze_page76_corridor_font_order.py`
  - `analysis_outputs/docm_format_sources/page76_corridor_font_order_audit.md`
  - `analysis_outputs/docm_format_sources/page76_corridor_font_order_audit.json`
- Scope:
  - Combined `Article with Fonts.docm` Typeka layers, verified page-76 highlight groups, and the p79-yellow -> p76-black calibration anchor.
  - No private-key candidates or broad hashes were generated.
- Findings:
  - Page-76 signal sequence is `YBMMMKBMYKMYBKKBMMY`.
  - Confirmed target sequence is `YKYKYKKY`.
  - Matched target initials are `GGbIb$Vs`; last initials are `tmmgdbBh`.
  - Nearest Typeka Mix triplets around targets are `GGcGnnbEnIEE"ME$ME“MIs`.
  - None of those streams expose instruction terms.
  - Typeka Mix neighbors are meaningful prose anchors (`George Clinton`, `El Salvador`, `Mike Novogratz`, `I don't really trust that guy`) but not a one-to-one index system.
  - The strong p79 source group is `YELLOW`; it lands on a p76 `BLACK` group, so the anchor is best read as color inversion/orientation evidence.
- Conclusion:
  - The p76 font/highlight order is structured but follows the visible narrative, not a hidden selector.
  - Keep Typeka as a formatting witness only until a stronger external selector appears.
- Next test:
  - Inspect non-font visual ordering marks around the page-76 color-inversion anchor, or improve the source with higher-fidelity physical/source scans.

### Anchor-Margin Visual Order

- Status: tested; local non-font ordering around the 76/79 color-inversion anchor closed.
- Evidence:
  - `scripts/analyze_anchor_margin_visual_order.py`
  - `analysis_outputs/source_audit/anchor_margin_visual_order_audit.md`
  - `analysis_outputs/source_audit/anchor_margin_visual_order_audit.json`
  - `analysis_outputs/source_audit/anchor_margin_visual_order_audit.jpg`
  - `analysis_outputs/source_audit/anchor_margin_visual_order_full_band.jpg`
- Scope:
  - Checked the full horizontal band `(0, 560, 2544, 1280)` around the p79-yellow -> p76-black anchor, not just the earlier core crop.
  - Masked article text boxes and known orange/black highlight boxes before looking for residual marks.
- Findings:
  - p76 residual: `19,162` pixels across `53` components.
  - registered p79 residual: `26,913` pixels across `29` components.
  - masked overlap: `205` pixels total; only `108` pixels outside the previous core crop.
  - Residual components are unmasked letter fragments, source-page text residue, page-edge/margin residue, and one right-margin registered-p79 residue block.
  - No clean dot count, pill count, X sequence, wire-knot sequence, arrow, or one-to-one residual component sequence appears near the anchor.
- Conclusion:
  - The color-inversion anchor remains useful for orientation/calibration only.
  - It does not contain a local non-font ordering cue under the current high-res transform.
- Next test:
  - Treat lower page-76 visual marks as a separate system, or require a better physical/source scan before further geometry work.

### Lower Page-76 Mark Pointers

- Status: tested; standalone lower-mark pointer branch closed under current scan.
- Evidence:
  - `scripts/analyze_lower_page76_mark_pointers.py`
  - `analysis_outputs/source_audit/lower_page76_mark_pointers.md`
  - `analysis_outputs/source_audit/lower_page76_mark_pointers.json`
  - `analysis_outputs/source_audit/lower_page76_mark_pointers_overlay.jpg`
- Scope:
  - Reclassified the four lower page-76 detections and tested only the true non-text marks as pointers/order marks.
  - No private-key candidates or broad text transforms were generated.
- Findings:
  - M1 and M2 are not standalone marks; they are the detected grey/black highlighted text boxes for `$1 billion` and `Volcano Bonds`.
  - M3 is a true right-side brush/X mark crossing the `loan/Mike`, `Novogratz`, `Wall Street crony pals`, and `I don't really trust that guy` rows.
  - M4 is a true lower-right brush/X mark nearest to the `shitcoiner at heart` row.
  - Horizontal reads and PCA-axis reads return adjacent prose fragments, not an instruction or ordered selector.
- Conclusion:
  - The lower marks confirm the same page-76 semantic corridor, but do not solve the final selector.
  - Do not treat `$1 billion` or `Volcano Bonds` detector boxes as separate symbols.
- Next test:
  - Stop local geometry loops until a new source changes the premise. The live gap is now external/source-level: original puzzle instruction/provenance, higher-resolution Canva assets, or physical magazine scan/photo evidence.

### Typography Source Provenance

- Status: tested; local PDF font-metadata branch closed as non-witness.
- Evidence:
  - `scripts/analyze_typography_source_provenance.py`
  - `analysis_outputs/source_audit/typography_source_provenance.md`
  - `analysis_outputs/source_audit/typography_source_provenance.json`
- Scope:
  - Checked which local files can directly witness Typeka / Typeka Mix / Typeka-bold usage.
  - No key candidates or text transforms were generated.
- Findings:
  - `magazine.pdf` exposes only `Helvetica` PDF font rows, which belong to the OCR/text layer, not the visible printed typography.
  - `Issue_26.pdf` and `bitcoin3.pdf` expose no font rows and no usable extractable text; they are flattened raster page-image witnesses.
  - `Article with Fonts.docm` directly records the Typeka states: `Typeka` (`6568` chars), `Typeka Mix` (`883` chars), plus `Stencil` and `LonestarW00-Regular`.
  - `BOLD.docm` has VBA and a partial Typeka/yellow-highlight layer, so it stays classified as investigator-derived unless its macro input is recovered.
- Conclusion:
  - The local comparison PDFs cannot prove or disprove Typeka usage in other Max articles by metadata.
  - Typeka remains a confirmed formatting witness only through `Article with Fonts.docm`.
- Next test:
  - Do not continue PDF font-metadata checks. Seek original layout/source files, higher-resolution comparison exports, or physical magazine/photos if Typeka uniqueness needs to be proven.

### Selector Gap Map

- Status: current decision map; use before choosing future experiments.
- Evidence:
  - `scripts/build_selector_gap_map.py`
  - `analysis_outputs/source_audit/selector_gap_map.md`
  - `analysis_outputs/source_audit/selector_gap_map.json`
- Scope:
  - Consolidated live and dead evidence into a selector-gap map.
  - No key candidates, hashes, or new geometry transforms were generated.
- Findings:
  - The blacklist now has `31` closed local branches and `11` still-active branches.
  - The strongest surviving facts are:
    - page 76 is still the target surface (`17/17` medium/strong reflected hits);
    - 76/79 registration gives a real row/region anchor, not a letter selector;
    - the high-res scan is geometry truth, while OCR/source variants are too distorted for final extraction;
    - Typeka remains a DOCM formatting witness, not a selector by itself;
    - lower brush/X marks reinforce the corridor but do not add order.
  - The missing selector must still specify source layer, narrower target region, ordering, and extraction unit.
- Conclusion:
  - The live gap is source/provenance/instruction-level, not key-format-level.
- Next test:
  - Prefer recovering original clue wording/thread, higher-resolution Canva assets, layout/source files, or physical magazine/photos before reopening local geometry or key-generation branches.

### Original Clue Provenance

- Status: recovered and archived as raw source evidence.
- Evidence:
  - `scripts/audit_original_clue_provenance.py`
  - `analysis_outputs/external_clues/original_clue_provenance.md`
  - `analysis_outputs/external_clues/original_clue_provenance.json`
- Scope:
  - Fetched public oEmbed payloads for the announcement tweet and Schott/mirror clue tweet.
  - Expanded the clue tweet's short links.
  - No key candidates or text transforms were generated.
- Findings:
  - Announcement tweet `1632068898169450497` confirms the private-key/source/20 BTC statement.
  - Clue tweet `1632391507008278528` confirms the exact text: `Mirror writing: neurological reflections on an unusual phenomenon`.
  - `https://t.co/WkSDXKwSiv` expands to the PMC Schott paper.
  - `https://t.co/3NrEhxV2Iz` expands back to the original announcement tweet.
- Conclusion:
  - The Schott clue is an intentional instruction pointer from the clue tweet back to the announcement/source article.
  - The tweet text itself contains no extra selector terms.
- Next test:
  - Treat this as the canonical public clue record. The missing selector still needs source/visual evidence: higher-resolution Canva assets, original layout/source files, or physical magazine/photo alignment.

### Schott Instruction Distillation

- Status: tested; source concept map recorded.
- Evidence:
  - `scripts/distill_schott_instruction_terms.py`
  - `analysis_outputs/external_clues/schott_instruction_distillation.md`
  - `analysis_outputs/external_clues/schott_instruction_distillation.json`
  - Source paper: `https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/`
- Scope:
  - Parsed the linked Schott paper and counted operational concept groups.
  - No key candidates, hashes, or article-text transforms were generated.
- Findings:
  - The paper strongly emphasizes mirror/reversal, neurological framing, left-hand/handedness, Leonardo, bimanual movement, corpus callosum, and right-hemisphere concepts.
  - These map cleanly to physical/visual mirroring, left/right page-side handling, and cross-page interaction.
  - They do not identify source layer, order, or extraction unit.
- Conclusion:
  - Schott supports the existing page-76 plus 76/79 row-anchor model, but does not unlock the final selector by itself.
- Next test:
  - Only run a Schott-derived experiment if the rule is fully specified in advance: source page/layer, target page/box, order, extraction unit, and expected readable output.

### Announcement Opening Spread

- Status: newly active source/provenance layer.
- Evidence:
  - `scripts/audit_announcement_opening_spread.py`
  - `analysis_outputs/source_audit/announcement_opening_spread/announcement_opening_spread_audit.md`
  - `analysis_outputs/source_audit/announcement_opening_spread/announcement_opening_spread_audit.json`
  - `analysis_outputs/source_audit/announcement_opening_spread/announcement_opening_spread_sheet.jpg`
- Scope:
  - Compared the first announcement image against all eight pages of `magazine.pdf`.
  - No key candidates or crypto transforms were generated.
- Findings:
  - The first announcement photo shows Max holding the physical `OVERDOSE` opener spread.
  - That spread is `magazine.pdf` PDF pages 1-2, preceding the body pages mapped as article pages 75-80.
  - Treat the opener as article pages 73-74: page 73 has `OVERDOSE`, pills, and cash; page 74 has the field/cash illustration.
  - The announcement photo is too perspective-skewed for geometry truth, but it proves the opener spread was part of the public puzzle presentation.
- Conclusion:
  - Page 76 remains the strongest target corridor, but the full source model was missing the photographed opener layer.
- Next test:
  - Add pages 73-74 to the visual inventory and compare opener pill/cash/field motifs against page-76/page-79 orientation evidence. Do not treat opener imagery as direct key material without a selector.

### Opener Five-Capsule Link

- Status: active as source/order evidence; closed as direct count-only selector.
- Evidence:
  - `scripts/analyze_opener_pill_cash_inventory.py`
  - `analysis_outputs/source_audit/opener_pill_cash_inventory/opener_pill_cash_inventory.md`
  - `analysis_outputs/source_audit/opener_pill_cash_inventory/opener_pill_cash_inventory.json`
  - `analysis_outputs/source_audit/opener_pill_cash_inventory/opener_pill_cash_inventory_sheet.jpg`
- Scope:
  - Detected orange capsule components on opener page 73.
  - Compared them to known page-79 orange pill fragments.
  - No key candidates or hashing were generated.
- Findings:
  - Page 73 contains five clean capsule marks.
  - Page 79 contains five corresponding orange pill fragments.
  - Top-to-bottom p73 capsule order fits p79 orange boxes 6-10 with affine mean residual `1.07 px` and max residual `1.95 px`.
  - This is effectively a scaled/rotated reuse of the same capsule artwork.
- Conclusion:
  - The opener spread is connected to page 79 by reusable pill art, so p73 can provide an order/provenance layer for p79.
  - The number five or pill count alone still does not specify page-76 target region or letter extraction.
- Next test:
  - Use the five-capsule order only with a stated p79->p76 mirror/fold rule, especially around the already-supported page-76 corridor.

### Ordered Capsule Projection

- Status: tested; closed as current high-res direct text selector.
- Evidence:
  - `scripts/analyze_ordered_capsule_projection.py`
  - `analysis_outputs/source_audit/ordered_capsule_projection/ordered_capsule_projection.md`
  - `analysis_outputs/source_audit/ordered_capsule_projection/ordered_capsule_projection.json`
  - `analysis_outputs/source_audit/ordered_capsule_projection/ordered_capsule_projection_overlay.jpg`
- Scope:
  - Used the page-73 five-capsule order to order page-79 orange boxes 6-10.
  - Projected the ordered marks to page 76 with the best known page-79 -> page-76 mirror registration.
  - No key candidates or hashing were generated.
- Findings:
  - The five ordered projections have `0` intersections with page-76 orange/grey text-highlight boxes.
  - They land in the lower-right page-76 non-text brush/art region.
  - Nearest mark pattern: `M3M3M4M4M4`.
  - Distances are too loose for a precise selector except the first projection.
- Conclusion:
  - Under the current high-res digital scan, the ordered capsule sequence is not a direct page-76 letter/text selector.
  - It remains useful only as provenance/order evidence if a new physical transform or explicit rule puts the five points onto text.
- Next test:
  - Avoid deriving keys from the five pills. Reopen only with new source registration, physical scan evidence, or a specific mirror/fold rule that targets text.

### Capsule Motif Recurrence

- Status: tested; active as Issue-24-specific provenance/order evidence.
- Evidence:
  - `scripts/analyze_capsule_motif_recurrence.py`
  - `analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence.md`
  - `analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence.json`
  - `analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence_sheet.jpg`
- Scope:
  - Compared the Issue 24 p73/p79 five-capsule motif against `Issue_26.pdf` and `bitcoin3.pdf`.
  - Used a five-point sequence check, not single blob matching.
  - No key candidates or hashing were generated.
- Findings:
  - Single red/orange blobs in comparison pages can look capsule-like, so blob matching alone is noisy.
  - The five-point zigzag sequence recovers Issue 24 p73 with mean residual `0.48 px` and Issue 24 p79 with mean residual `1.10 px`.
  - No strong five-point sequence recurrence appears in `Issue_26.pdf` or `bitcoin3.pdf`.
- Conclusion:
  - The p73/p79 capsule chain is more specific to Issue 24 than generic OVERDOSE house style in the current comparison set.
  - It remains provenance/order evidence only; it still lacks the rule that maps it onto page-76 text.
- Next test:
  - Look for a source/physical/mirror instruction that tells where the five-item order applies.

### Spread Model Reconciliation

- Status: tested; opener symmetry active as provenance/orientation evidence; direct PDF-adjacent page-76 selector closed.
- Evidence:
  - `scripts/reconcile_spread_models.py`
  - `analysis_outputs/source_audit/spread_model_reconciliation/spread_model_reconciliation.md`
  - `analysis_outputs/source_audit/spread_model_reconciliation/spread_model_reconciliation.json`
- Scope:
  - Compared PDF-adjacent / photographed-spread candidates `(73,74)`, `(75,76)`, `(77,78)`, `(79,80)` against standard parity candidates `(76,77)`, `(78,79)`.
  - Used raw high-res horizontal reflection of orange source boxes onto target orange/grey boxes.
  - No key candidates or hashing were generated.
- Findings:
  - Pages 73 and 74 have near-perfect small `OVERDOSE` label mirror symmetry, with center distances around `1 px`.
  - PDF-adjacent `75 -> 76` and `76 -> 75` produce `0` meaningful raw intersections.
  - PDF-adjacent `79 <-> 80` repeats the known page-79 end-text to page-80 package-label interaction.
- Conclusion:
  - The opener spread is intentionally mirror-symmetric at the label layer, supporting the mirror/provenance model.
  - PDF-adjacent folding does not produce a direct page-76 selector under current high-res geometry.
  - The 79/80 interaction reinforces the medicine/pill/package theme but does not identify target text or extraction unit.
- Next test:
  - Use spread symmetry only as orientation/provenance evidence unless a new source rule says which mirrored spread and which text to read.

### Page-76 Self-Mirror

- Status: tested; full self-fold selector closed; B5/O5 local pair active as anchor.
- Evidence:
  - `scripts/analyze_page76_self_mirror.py`
  - `analysis_outputs/source_audit/page76_self_mirror/page76_self_mirror.md`
  - `analysis_outputs/source_audit/page76_self_mirror/page76_self_mirror.json`
  - `analysis_outputs/source_audit/page76_self_mirror/page76_self_mirror_overlay.jpg`
- Scope:
  - Reflected verified page-76 orange/grey highlight boxes across page center and highlight-bbox center axes.
  - No key candidates or hashing were generated.
- Findings:
  - One repeatable self-mirror pair exists: B5 `Volcano Bonds` <-> O5 `shitcoiner at heart.`
  - Best tested axis: `orange_bbox_center` x=`1322.0`, source overlap `0.593`, target overlap `0.908`, center distance `63.5 px`.
  - No other verified page-76 highlight boxes participate.
- Conclusion:
  - Page 76 does not self-encode through a complete internal mirror/fold system.
  - The `Volcano Bonds` / `shitcoiner at heart` pair should be preserved as a local anchor inside the El Salvador corridor.
- Next test:
  - Only reuse this pair if a source/provenance rule points to `Volcano Bonds`, `shitcoiner`, or the page-76 lower-corridor mirror axis.

### Page-76 B5/O5 Pair Drilldown

- Status: tested; exact word/letter selector closed; semantic anchor remains active.
- Evidence:
  - `scripts/analyze_page76_b5_o5_pair.py`
  - `analysis_outputs/source_audit/page76_b5_o5_pair/page76_b5_o5_pair.md`
  - `analysis_outputs/source_audit/page76_b5_o5_pair/page76_b5_o5_pair.json`
  - `analysis_outputs/source_audit/page76_b5_o5_pair/page76_b5_o5_pair_crop.jpg`
- Scope:
  - Inspected the only surviving page-76 self-mirror pair: B5 `Volcano Bonds` and O5 `shitcoiner at heart.`
  - Used verified high-res highlight rectangles and proportional character estimates only. The 3D/canonical model has exact text lines but not reliable lower-page word boxes for this pair.
  - No key candidates or hashing were generated.
- Findings:
  - B5 -> O5 covers roughly the first `89%` of `Volcano Bonds` and the first `91%` of `shitcoiner at heart.`
  - O5 -> B5 gives the same broad pattern in reverse.
  - The estimated omissions are only the final `s` from `Volcano Bonds` and the final period from `shitcoiner at heart.`
- Conclusion:
  - The overlap is too broad to be a precise word, letter, BIP39, WIF, or index selector.
  - The useful signal is the low-parameter pairing of `Volcano Bonds` with `shitcoiner at heart` inside the page-76 El Salvador/IMF corridor.
- Next test:
  - Keep B5/O5 as a local anchor only. The next productive move is finding a source/provenance rule from p73/p79/p80, physical registration, or original layout/Canva evidence that tells which page-76 unit to extract.

### P79/P80 Package Interaction

- Status: tested; direct selector closed; OVERDOSE/dosage provenance remains active.
- Evidence:
  - `scripts/analyze_p79_p80_package_interaction.py`
  - `analysis_outputs/source_audit/p79_p80_package_interaction/p79_p80_package_interaction.md`
  - `analysis_outputs/source_audit/p79_p80_package_interaction/p79_p80_package_interaction.json`
  - `analysis_outputs/source_audit/p79_p80_package_interaction/p79_p80_package_interaction_sheet.jpg`
- Scope:
  - Inspected the only repeated PDF-adjacent p79/p80 raw hflip hits.
  - Measured approximate text spans for page-80 package labels reflected onto page-79 O4 `Everyone will live their own experience in the rabbit hole.`
  - No key candidates or hashing were generated.
- Findings:
  - p80 O1 `5 SYMPTOM RELIEF / ... / UPSET STOMACH / SHITCOINS` maps to the approximate p79 fragment `ill live their`.
  - p80 O2 `6 FL OZ (473 mL)` maps to the approximate p79 fragment `experience in`.
  - The p80 O1 vertical overlap is a lower-strip hit, roughly covering `UPSET STOMACH` / `SHITCOINS`.
- Conclusion:
  - The package layer reinforces the medicine/dosage/OVERDOSE theme.
  - The overlap is not precise enough to be a standalone word/letter/index selector.
- Next test:
  - Keep p79/p80 as provenance/theme evidence only. Look for an explicit rule that maps the p73 five-capsule order or p80 dosage labels onto the page-76 corridor.

### OVERDOSE Dose-Number Selector

- Status: tested; raw number selector closed; corroborative page-76 evidence remains active.
- Evidence:
  - `scripts/analyze_overdose_dose_number_selector.py`
  - `analysis_outputs/source_audit/overdose_dose_number_selector/overdose_dose_number_selector.md`
  - `analysis_outputs/source_audit/overdose_dose_number_selector/overdose_dose_number_selector.json`
- Scope:
  - Applied only the visible provenance/dosage numbers `5` and `6` to verified page-76 lists.
  - Did not expand into arbitrary numeric combinations or key candidates.
- Findings:
  - `5` selects p76 orange #5 `shitcoiner at heart.`
  - `5` selects p76 grey #5 `Volcano Bonds`.
  - In the El Salvador corridor, `5` selects `I tweeted President Nayib Bukele when he announced`; `6` selects `he was going to tap his nation's volcanoes to mine`.
  - No selected item contains direct instruction words such as read/take/fold/mirror/word/letter/key.
- Conclusion:
  - The visible dosage/count layer strengthens the same page-76 corridor but does not provide an extraction unit.
  - Do not expand raw number-indexing without a new clue naming the surface and unit.
- Next test:
  - Search for a source/layout instruction that tells how the five-capsule or p80 dosage layer should choose page-76 words or letters.

### P80 Symptom List To Page-76 Units

- Status: tested; standalone selector closed; O5 corroboration remains active.
- Evidence:
  - `scripts/analyze_p80_symptom_to_p76_units.py`
  - `analysis_outputs/source_audit/p80_symptom_to_p76_units/p80_symptom_to_p76_units.md`
  - `analysis_outputs/source_audit/p80_symptom_to_p76_units/p80_symptom_to_p76_units.json`
- Scope:
  - Mapped p80's five actual symptom labels to the five verified p76 orange boxes and five verified p76 grey boxes.
  - Checked forward and reverse five-to-five order, plus unordered direct lexical echoes.
  - No key candidates or hashing were generated.
- Findings:
  - The forward orange mapping has direct lexical pattern `00001`: #5 `SHITCOINS` -> p76 orange #5 `shitcoiner at heart.`
  - Reverse orange, forward grey, and reverse grey mappings all have pattern `00000`.
  - `HEARTBURN` sees `heart` in p76 orange #1 and #5, but not in a clean ordered mapping.
- Conclusion:
  - The symptom list reinforces the same lower page-76 target, especially O5 `shitcoiner at heart`.
  - It does not define a complete selector or extraction unit.
- Next test:
  - Do not use symptom words alone. Continue looking for an explicit source/layout instruction or a physical/source-registration difference that tells what to read.

### DOCM Hidden Structure

- Status: tested; hidden-instruction container closed.
- Evidence:
  - `scripts/audit_docm_hidden_structure.py`
  - `analysis_outputs/docm_format_sources/docm_hidden_structure_audit.md`
  - `analysis_outputs/docm_format_sources/docm_hidden_structure_audit.json`
- Scope:
  - Inspected `BOLD.docm` and `Article with Fonts.docm` as Word packages.
  - Checked comments, hidden runs, bookmarks, hyperlinks, field codes, headers/footers, footnotes/endnotes, custom XML, relationships, document properties, and printable VBA strings.
  - Macros were not executed.
- Findings:
  - `Article with Fonts.docm` has no comments, custom XML, hidden runs, bookmarks, hyperlinks, field codes, annotation markers, or VBA project.
  - `BOLD.docm` has no hidden Word annotation layer, but does include VBA parts.
  - The BOLD VBA strings only repeat the known generated workflow and missing path `private_inputs\OneDrive\Desktop\Alles\TOXIC_AF\BIP39\otrobip.txt`.
- Conclusion:
  - The DOCM containers do not currently provide the missing source/layout instruction.
  - `Article with Fonts.docm` remains a formatting witness; `BOLD.docm` remains a generated working artifact unless `otrobip.txt` is recovered.
- Next test:
  - Shift back to external Canva/source clues, original layout files, or physical-source registration.

### External Clue Coverage

- Status: tested; selector operations covered; source-fidelity gaps remain active.
- Evidence:
  - `scripts/audit_external_clue_coverage.py`
  - `analysis_outputs/external_clues/external_clue_coverage_audit.md`
  - `analysis_outputs/external_clues/external_clue_coverage_audit.json`
- Scope:
  - Mapped nine known external clue items to existing tested/active branches.
  - Checked announcement text, Schott clue, Schott concepts, announcement media, opener spread, Canva note text, and Canva thumbnail/export limitations.
  - No key candidates or hashing were generated.
- Findings:
  - The known external clues do not contain an untested local selector operation.
  - Mirror/left-right/bimanual clues have been tested enough to show region/corridor behavior, not a final extraction unit.
  - The two live external-clue gaps are source-fidelity issues: `pills don't line up / diff pic?` and `OCR DIDNT PICK UP THE #0`.
- Conclusion:
  - Current local evidence is saturated; the missing rule is more likely in a source/version/visual asset not yet available than in another transformation of extracted text.
- Next test:
  - If the exact browser/PDF/Canva/original-layout source is supplied, run a targeted zero/#0 and pill-registration inventory. Without that, prioritize physical/original-source acquisition.

### Zero / #0 Source Fidelity

- Status: tested locally; visual-source check remains active.
- Evidence:
  - `scripts/audit_zero_source_fidelity.py`
  - `analysis_outputs/source_audit/zero_source_fidelity/zero_source_fidelity.md`
  - `analysis_outputs/source_audit/zero_source_fidelity/zero_source_fidelity.json`
- Scope:
  - Inventoried every zero-bearing numeric token in the corrected article and local transcript witnesses.
  - This was a source-fidelity checklist for the Canva note `OCR DIDNT PICK UP THE #0`, not a key-generation pass.
- Findings:
  - Canonical zero tokens are p75 `2008`, p76 `10` / `2011`, p77 `20,000` / `100,000` / `2017` / `12,000`, and p79 `10`.
  - Corrected witnesses agree on those tokens.
  - The user annotated transcript contains the notable extra form `1000,000`, while corrected/canonical witnesses read `100,000`.
- Conclusion:
  - If the Canva/browser `#0` clue points to a real source discrepancy, the first visual check should be p77 `100,000`.
  - This does not change the page-76 target model unless a new source image shows that the missed zero changes alignment or selector behavior.
- Next test:
  - With the exact browser/PDF/Canva/original visual source, compare `100,000`, then `20,000`, `12,000`, `2008`, `2011`, `2017`, and both `10 years` references.

### Zero Visual Crops

- Status: tested on current trusted scan; source-view discrepancy remains active.
- Evidence:
  - `scripts/audit_zero_visual_crops.py`
  - `analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops.md`
  - `analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops.json`
  - `analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops_sheet.jpg`
- Scope:
  - Cropped the high-res scan around each zero/#0 hotspot and added same-normalized Google/OCR PDF crops for rough comparison.
  - No key candidates or hashing were generated.
- Findings:
  - The current trusted scan/article-map word box reads p77 as `100,000`, not `1000,000`.
  - The p76 `10 years` region is visually cropped despite the OCR word-box model misreading it as `loyears`.
- Conclusion:
  - The `1000,000` form is not supported by the current high-res scan; it remains a source/transcript/browser-view discrepancy.
  - This does not change the page-76 target model or provide an extraction unit.
- Next test:
  - If a new browser/PDF/Canva/original source image appears, compare it against `zero_visual_crops_sheet.jpg` before changing transcript or rerunning selectors.

### Alternate PDF Pill Geometry

- Status: tested; local alternate-PDF `diff pic` branch closed; new-source check remains active.
- Evidence:
  - `scripts/audit_alternate_pdf_pill_geometry.py`
  - `analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry.md`
  - `analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry.json`
  - `analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry_sheet.jpg`
- Scope:
  - Compared p79 lower-left pill fragments in trusted `magazine.pdf` against the local Google/OCR PDF witness.
  - No key candidates or hashing were generated.
- Findings:
  - Both sources expose five lower-left p79 pill fragments.
  - Same-normalized raw coordinates are shifted/distorted by roughly `100-500 px`.
  - Top-to-bottom affine fit from Google/OCR components to high-res fragments has mean residual `0.31 px`, max residual `0.45 px`.
- Conclusion:
  - The local Google/OCR PDF is the same visible motif with crop/scale distortion, not a different picture source.
  - This does not reopen capsule projection or pill-order extraction.
- Next test:
  - Only reopen pill registration if a new source image or physical scan changes the count, order, or placement of the current five-fragment baseline.

### 3D Text Witness Consistency

- Status: tested; 3D text downgraded to navigation/label witness.
- Evidence:
  - `scripts/audit_3d_text_witness_consistency.py`
  - `analysis_outputs/plain_text_transcript/3d_text_witness_consistency_audit.md`
  - `analysis_outputs/plain_text_transcript/3d_text_witness_consistency_audit.json`
- Scope:
  - Compared the 3D map's internal OCR/Markdown text layer against the corrected DOCM-derived canonical article text.
  - No key candidates or hashing were generated.
- Findings:
  - Canonical tokens: `1477`; 3D-map tokens: `1460`; sequence match ratio: `0.987813`.
  - Corrected high-value phrases are preserved in both sources where needed: `puts an end`, `Volcano Bonds`, `100,000`, `money printing`, `$2 trillion fiat cuck-bucks`, and `gets monetized for the first time`.
  - Remaining 3D text-layer mismatches include p77 `nas gone` vs corrected `has gone`, missing p78/p79 pull-quote repetition `The economy of love is infinitely more efficient than hate and war.`, and p78 `Bitcoin fills the gap` vs corrected `Bitcoin fills in the gap`.
- Conclusion:
  - The 3D map is reliable for visual navigation and geometry review, not exact wording extraction.
  - Exact selector text should come from the corrected DOCM/plain witness after the high-res scan identifies a region.
- Next test:
  - If a future rule lands on p77 or p78/p79 wording, reconcile that exact span against `canonical_plain_article_body.txt` before extracting words or letters.

### P78 Graphic Pull-Quote Reflection

- Status: tested; corroborative visual-layer evidence active; standalone selector closed.
- Evidence:
  - `scripts/audit_p78_graphic_pullquote_reflection.py`
  - `analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.md`
  - `analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.json`
  - `analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_crop.jpg`
  - `analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflected_on_p76.jpg`
- Scope:
  - Treated the lower p78 brush/pull-quote as graphic text outside the normal article-body layer.
  - Mirrored the graphic onto p76 using literal horizontal reflection.
  - No key candidates or hashing were generated.
- Findings:
  - The scan-visible p78 graphic repeats `The economy of love is infinitely more efficient than hate and war.`
  - Detected p78 graphic box: `[294, 2398, 1310, 2950]`.
  - Reflected p76 box: `[1234, 2398, 2250, 2950]`.
  - The mirrored graphic broadly intersects p76 orange #5 `shitcoiner at heart` and grey #5 `Volcano Bonds`.
- Conclusion:
  - This strengthens the lower page-76 target pair already identified by the B5/O5 self-mirror branch.
  - It does not provide a narrow extraction unit under the current scan.
- Next test:
  - If higher-resolution Canva/source evidence reopens the `FUCK ALL SHITCOINS` / X / brush alignment branch, include this p78 graphic layer explicitly as a visual object.

### P78 Graphic Word Intersections

- Status: tested; target confirmation active; standalone selector closed.
- Evidence:
  - `scripts/analyze_p78_graphic_word_intersections.py`
  - `analysis_outputs/source_audit/p78_graphic_word_intersections/p78_graphic_word_intersections.md`
  - `analysis_outputs/source_audit/p78_graphic_word_intersections/p78_graphic_word_intersections.json`
  - `analysis_outputs/source_audit/p78_graphic_word_intersections/p78_graphic_word_intersections_overlay.jpg`
- Scope:
  - Intersected the mirrored p78 lower graphic with p76 word labels.
  - Checked both dark brush pixels and approximate negative text-hole pixels.
  - Used OCR boxes as labels only; exact wording still comes from the corrected DOCM/plain text.
  - No key candidates or hashing were generated.
- Findings:
  - The mirrored graphic's p76 box is `[1234, 2398, 2250, 2950]`.
  - It covers a coherent p76 phrase band around `should sell`, `pay off the IMF`, `I tagged Mike`, `he could sell`, `but so far he`, `trust that guy`, and `shitcoiner at heart`.
  - Dark-mask hits: `14`; negative-hole hits: `12`.
  - The resulting streams do not read as an instruction.
- Conclusion:
  - This strengthens the lower p76 corridor and the `Volcano Bonds` / `shitcoiner at heart` target pair.
  - It still does not specify the extraction unit.
- Next test:
  - Only reuse this visual layer after a separate clue tells whether to read dark brush, white holes, bounding box, or adjacent words.

### P78 Graphic Character Intersections

- Status: tested; micro-selector closed under literal hflip.
- Evidence:
  - `scripts/analyze_p78_graphic_char_intersections.py`
  - `analysis_outputs/source_audit/p78_graphic_char_intersections/p78_graphic_char_intersections.md`
  - `analysis_outputs/source_audit/p78_graphic_char_intersections/p78_graphic_char_intersections.json`
  - `analysis_outputs/source_audit/p78_graphic_char_intersections/p78_graphic_char_intersections_overlay.jpg`
- Scope:
  - Intersected the mirrored p78 lower graphic with p76 character labels.
  - Checked bounding box, dark stroke centers/pixels, and negative-hole centers/pixels.
  - OCR character boxes are labels only; no key candidates or hashing were generated.
- Findings:
  - Dark-center stream: `offIMgdelelshe`.
  - Hole-center stream: `FMiklatr`.
  - Dark/hole pixel streams remain broken fragments of `off IMF`, `Mike`, `sell`, `trust`, `guy`, and the OCR blob for `shitcoiner at heart`.
- Conclusion:
  - The p78 graphic does not provide a precise letter-level extraction rule under literal hflip.
  - It remains target confirmation for the lower p76 corridor only.
- Next test:
  - Do not retry p78 graphic micro-selection unless a new clue explicitly says to use dark strokes, white holes, or character centers.

### Page 76 Target Convergence

- Status: tested; target focus narrowed to G5/O5 pair.
- Evidence:
  - `scripts/analyze_page76_target_convergence.py`
  - `analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.md`
  - `analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json`
- Scope:
  - Ranked page-76 target units by independent non-key visual/source support.
  - No key candidates or hashing were generated.
- Findings:
  - O5 `shitcoiner at heart`: score `15`, independent layers `5`.
  - G5 `Volcano Bonds`: score `11`, independent layers `4`.
  - Lower El Salvador/IMF/Bukele/Mike/trust corridor: score `6`, independent layers `4`.
  - O1 score `3`; G4, O3, O4 score `2`; G1/G3 score `1`.
- Conclusion:
  - The lower page-76 `Volcano Bonds` / `shitcoiner at heart` pair is now the strongest target focus.
  - The evidence is target convergence, not an extraction rule.
- Next test:
  - Future local tests should operate only on the G5/O5 pair unless a new source clue redirects the target.

### Page 76 B5/O5 Axis-Spine Selector

- Status: tested; standalone selector closed.
- Evidence:
  - `scripts/analyze_page76_axis_spine_selector.py`
  - `analysis_outputs/source_audit/page76_axis_spine_selector/page76_axis_spine_selector.md`
  - `analysis_outputs/source_audit/page76_axis_spine_selector/page76_axis_spine_selector.json`
  - `analysis_outputs/source_audit/page76_axis_spine_selector/page76_axis_spine_selector_overlay.jpg`
- Scope:
  - Tested whether the mirror axis linking `Volcano Bonds` and `shitcoiner at heart` selects a readable vertical word/letter spine.
  - Checked the page center, all-highlight/grey center, and orange center axes.
  - No key candidates or hashing were generated.
- Findings:
  - All tested axes preserve the same `B5->O5|O5->B5` edge pattern.
  - Primary orange-center lower crossing words: `Salvador Fund - when volcanoes should earnings pay tagged could but trust siukbeodmensertslveaarty`.
  - Primary orange-center lower crossing chars: `vF-hndiyaobss`.
  - The selected material is ordinary page-76 corridor text, not an instruction.
- Conclusion:
  - The vertical axis reinforces the El Salvador/IMF/volcano/Mike/trust/`shitcoiner at heart` corridor.
  - It does not provide the extraction unit/order.
- Next test:
  - Keep G5/O5 as the target pair, but look for an external/source/provenance clue that says whether to extract a word, adjacent word, omitted final character, dosage number, symptom label, or physical-registration unit.

### G5/O5 Local Unit Rules

- Status: tested; simple local units closed, five-line locator active.
- Evidence:
  - `scripts/analyze_g5_o5_local_unit_rules.py`
  - `analysis_outputs/source_audit/g5_o5_local_unit_rules/g5_o5_local_unit_rules.md`
  - `analysis_outputs/source_audit/g5_o5_local_unit_rules/g5_o5_local_unit_rules.json`
- Scope:
  - Tested omitted overlap characters, adjacent words, line/word positions, initials, endings, word lengths, and simple 5/6 dosage-style picks around the narrowed G5/O5 pair.
  - No key candidates or hashing were generated.
- Findings:
  - G5 `Volcano Bonds` is exactly five corrected text lines above O5 `shitcoiner at heart`.
  - Omitted-overlap units are only `s.` / `.s`.
  - Initials/endings/lengths produce `VBsah`, `osrtt`, and `[7, 5, 10, 2, 5]`.
  - Simple 5/6 picks produce local words such as `pay/off`, `shitcoiner/at`, `IMF/loan`, and `guy/that`.
- Conclusion:
  - The repeated `5` signal is best understood as a locator into the G5/O5 pair, not the final extraction rule.
  - The obvious local text units around G5/O5 do not yield an instruction.
- Next test:
  - Seek source/provenance or physical-registration evidence that specifies the extraction unit after this five-line locator has identified the target.

### Page 76 Highlight Line-Offset Rule

- Status: tested; partial locator pattern active; complete rule closed.
- Evidence:
  - `scripts/analyze_page76_highlight_line_offset_rule.py`
  - `analysis_outputs/source_audit/page76_highlight_line_offset_rule/page76_highlight_line_offset_rule.md`
  - `analysis_outputs/source_audit/page76_highlight_line_offset_rule/page76_highlight_line_offset_rule.json`
- Scope:
  - Tested whether a highlighted unit's number tells how many corrected text lines to move up/down.
  - No key candidates or hashing were generated.
- Findings:
  - Down-offset highlight hits:
    - O1 +1 -> O2.
    - B1 +1 -> B2.
    - O3 +3 -> B3.
    - B5 +5 -> O5.
  - Same-index hits are cleaner but shorter: O3 -> B3 and B5 -> O5.
  - #2 and #4 do not land on highlighted target units under the same simple operation.
- Conclusion:
  - The G5/O5 five-line locator is part of a broader page-76 line-offset pattern.
  - The pattern is incomplete, so it is not a final extraction rule.
- Next test:
  - Inspect whether the hit sequence `O1->O2`, `B1->B2`, `O3->B3`, `B5->O5` carries color/order information, with #2/#4 failures treated as a hard constraint.

### Page 76 Line-Offset Sequence Units

- Status: tested; standalone color/order selector closed.
- Evidence:
  - `scripts/analyze_page76_line_offset_sequence_units.py`
  - `analysis_outputs/source_audit/page76_line_offset_sequence_units/page76_line_offset_sequence_units.md`
  - `analysis_outputs/source_audit/page76_line_offset_sequence_units/page76_line_offset_sequence_units.json`
- Scope:
  - Tested whether the partial line-offset hit sequence carries a simple color/order message.
  - Checked color transitions, hit/miss bits, first words, initials, last letters, and failed #2/#4 landings.
  - No key candidates or hashing were generated.
- Findings:
  - Hit sequence: `O1->O2`, `B1->B2`, `O3->B3`, `B5->O5`.
  - Color transitions: `OO BB OB BO`.
  - Same/cross bits: `0011`; all-down hit/miss bits: `1010100010`.
  - Initial streams include `GGbV`, `BnIs`, `BnlM`, `bhDbN`; none are instruction-like.
- Conclusion:
  - The hit sequence is balanced and probably meaningful as orientation/locator evidence.
  - It does not specify what to extract.
- Next test:
  - Return to source/provenance or physical-registration evidence that can explain the partial locator pattern and choose a unit.

### Page 76 Line-Count Models

- Status: tested; corrected printed-line model active; alternate counting explanations closed.
- Evidence:
  - `scripts/analyze_page76_line_count_models.py`
  - `analysis_outputs/source_audit/page76_line_count_models/page76_line_count_models.md`
  - `analysis_outputs/source_audit/page76_line_count_models/page76_line_count_models.json`
- Scope:
  - Compared line-offset results under corrected lines with blanks, corrected nonblank lines, paragraph-local nonblank lines, and high-res highlight-row order.
  - No key candidates or hashing were generated.
- Findings:
  - Corrected lines with blank rows preserved gives the strongest partial pattern: `O1->O2`, `B1->B2`, `O3->B3`, `B5->O5`.
  - Removing blank rows loses `O3->B3`.
  - Paragraph-local counting also loses the cross-paragraph `O3->B3` bridge.
  - High-res highlight-row order creates a different hit set and is not the right model.
  - #2/#4 failures remain under the sensible line-counting variants.
- Conclusion:
  - The page-76 locator appears tied to printed line layout, including blank rows.
  - Alternate line counting does not complete the selector.
- Next test:
  - Preserve corrected-with-blank-lines as the line locator model, then seek source/provenance or physical-registration evidence for what the locator should select.

### Line-Offset Landing Evidence

- Status: tested; #4 landing lines active; #2 remains weak.
- Evidence:
  - `scripts/analyze_line_offset_landing_evidence.py`
  - `analysis_outputs/source_audit/line_offset_landing_evidence/line_offset_landing_evidence.md`
  - `analysis_outputs/source_audit/line_offset_landing_evidence/line_offset_landing_evidence.json`
- Scope:
  - Scored each down-offset landing line against other logged evidence: highlight targets, reflected-highlight graph, p78 graphic word intersections, and target convergence.
  - No key candidates or hashing were generated.
- Findings:
  - Strong/supported landings:
    - O1 +1 -> O2 line, score `5`.
    - B1 +1 -> B2 line, score `5`.
    - O3 +3 -> B3 line, score `5`.
    - O4 +4 -> `billions worth of future bitcoin earnings`, score `6`, supported by p78 graphic/reflection evidence.
    - B4 +4 -> `Novogratz in the tweet, figuring he could sell a`, score `5`, supported by p78 graphic/reflection evidence.
    - B5 +5 -> O5 line, score `8`.
  - Weak/unsupported landings:
    - O2 +2 -> `George Clinton...Martin Luther`, score `0`.
    - B2 +2 -> `have dulled shitcoiners...`, score `0`.
    - B3 +3 -> `Don't believe me?`, score `0`.
- Conclusion:
  - The #4 “misses” are not empty: they land in the p78 graphic reflection band.
  - The line-offset operation may select landing lines rather than only highlighted boxes.
  - The extraction unit remains missing.
- Next test:
  - Inspect p78/p79/p80 source/provenance layers for why #4 connects to the p78 graphic band and whether #2 has a missing visual/source layer.

### Supported Landing Sequence Units

- Status: tested; standalone selector closed; target set active.
- Evidence:
  - `scripts/analyze_supported_landing_sequence_units.py`
  - `analysis_outputs/source_audit/supported_landing_sequence_units/supported_landing_sequence_units.md`
  - `analysis_outputs/source_audit/supported_landing_sequence_units/supported_landing_sequence_units.json`
- Scope:
  - Tested whether the supported page-76 landing-line sequence gives a simple instruction through source ids/colors/indices, target line numbers, first/last words, preferred evidence terms, or scores.
  - No key candidates or hashing were generated.
- Findings:
  - Supported source sequence: `O1 B1 O3 O4 B4 B5`.
  - Source color stream: `OBOOBB`; index stream: `113445`.
  - Target line first initials: `BnlbNM`; last letters: `lnssat`.
  - Preferred evidence terms: `bitcoin bitcoin genitals earnings sell heart`; initials `bbgesh`.
  - Score stream: `555658`.
- Conclusion:
  - The supported landing lines form a coherent target set.
  - The obvious sequence streams do not provide an extraction instruction.
- Next test:
  - Seek source/provenance or physical-registration evidence that explicitly names the extraction unit for this target set.

### P78 Graphic Band Specificity

- Status: tested; #4 support downgraded to broad corroboration.
- Evidence:
  - `scripts/analyze_p78_graphic_band_specificity.py`
  - `analysis_outputs/source_audit/p78_graphic_band_specificity/p78_graphic_band_specificity.md`
  - `analysis_outputs/source_audit/p78_graphic_band_specificity/p78_graphic_band_specificity.json`
- Scope:
  - Tested whether p78 graphic support for #4 landing lines is specific or just broad lower-corridor coverage.
  - No key candidates or hashing were generated.
- Findings:
  - The reflected p78 graphic band covers these p76 word rows: `should sell`, `earnings`, `pay off the IMF`, `I tagged Mike`, `he could sella`, `pals, but so far he`, `trust that guy`, and the final OCR blob for `shitcoiner at heart`.
  - Bbox terms hit `O4+4` and `B4+4`; dark terms hit `O4+4`; hole terms hit no down-offset landing.
- Conclusion:
  - #4 support is real but broad, not a precise #4-only selector.
  - Treat #4 as source-layer corroboration for the lower page-76 corridor.
- Next test:
  - Find a source/provenance or physical-registration rule that says which specific word or line inside the p78 band should be read.

### P80 Volume Number Impact

- Status: tested; `16 FL OZ` active as B3 support; cropped `6 FL OZ` closed as canonical.
- Evidence:
  - `scripts/analyze_p80_volume_number_impact.py`
  - `analysis_outputs/source_audit/p80_volume_number_impact/p80_volume_number_impact.md`
  - `analysis_outputs/source_audit/p80_volume_number_impact/p80_volume_number_impact.json`
- Scope:
  - Checked the p80 package volume ambiguity: full visible/metric label `16 FL OZ (473 mL)` versus cropped `6 FL OZ (473 mL)`.
  - No key candidates or hashing were generated.
- Findings:
  - `16 FL OZ (473 mL)` is the canonical volume reading; `6 FL OZ` is a clipped-crop artifact.
  - `16` as a zero-based page-76 line selector lands exactly on `laundering lobotomy. It’s a stun gun to the genitals.`
  - That is the `O3+3 -> B3` line-offset hit.
  - `6` lands on the B1/Gotta line and does not explain the volume/metric pair.
  - Other p80 numbers do not form a coherent index stream.
- Conclusion:
  - p80 `16` strengthens the B3/stun-gun line as a provenance-supported locator.
  - It does not explain #2/#4 or specify the extraction unit.
- Next test:
  - Preserve p80 `16` as B3 support and look for physical/source evidence connecting the full package layer to the rest of the supported landing set.

### Page-76 Weak Landing Support

- Status: tested; #2 no longer pure score-zero, but still not a final selector.
- Evidence:
  - `scripts/analyze_page76_weak_landing_support.py`
  - `analysis_outputs/source_audit/page76_weak_landing_support/page76_weak_landing_support.md`
  - `analysis_outputs/source_audit/page76_weak_landing_support/page76_weak_landing_support.json`
- Scope:
  - Re-checked non-empty line-offset landings that previously scored `0` using already-logged secondary layers: reflected-highlight graph and p80 package number/term evidence.
  - No key candidates or hashing were generated.
- Findings:
  - `O2+2` (`George Clinton...Martin Luther`) has strong secondary support as the p79 reflected carrier `79_76_1`.
    - It strongly overlaps O1 and medium-overlaps B3 in the reflected-highlight graph.
  - `B2+2` (`have dulled shitcoiners' and nocoiners' minds.`) has weak p80 support.
    - p80 `100% Proof of Work Liquid` -> number `100` -> page-76 word `dulled`.
    - p80 symptom `SHITCOINS` is in the same lexical family as `shitcoiners`.
  - `B3+3` (`Don't believe me?`) still has no secondary support from these layers.
- Conclusion:
  - The earlier `#2 remains weak` conclusion should be softened: `#2` has secondary locator support, but it is weaker and less direct than `#1/#3/#4/#5`.
  - The line-offset model is better treated as a cross-reference/locator map, not a direct extraction rule.
  - The missing piece remains the extraction unit/order.
- Next test:
  - Audit only the externally named terms/carrier words from the secondary-supported landing set and see whether that smaller term set gives a readable instruction.

### Named Term Unit Streams

- Status: tested; standalone extraction unit closed; locator ledger remains active.
- Evidence:
  - `scripts/analyze_named_term_unit_streams.py`
  - `analysis_outputs/source_audit/named_term_unit_streams/named_term_unit_streams.md`
  - `analysis_outputs/source_audit/named_term_unit_streams/named_term_unit_streams.json`
- Scope:
  - Tested only externally named words from the line-offset map and secondary support layers.
  - No key candidates, hashes, seed phrases, or address checks were generated.
- Findings:
  - Named terms by line-offset source:
    - O1: `bitcoin`
    - O2: `george clinton james brown clones martin luther`
    - B1: `bitcoin`
    - B2: `dulled shitcoiners`
    - O3: `stun genitals`
    - B3: none
    - O4: `bitcoin earnings`
    - B4: `could sell`
    - B5: `heart`
  - Preferred stream: `bitcoin george bitcoin dulled genitals earnings sell heart`.
  - Preferred initials: `bgbdgesh`.
  - All-named stream: `bitcoin george clinton james brown clones martin luther bitcoin dulled shitcoiners stun genitals bitcoin earnings could sell heart`.
  - Reverse order, first/last term, O/B first-last, and source-index letter variants did not produce instruction language.
- Conclusion:
  - The named terms do not solve the extraction-unit problem by themselves.
  - They are still useful because they reduce the visual search to a small set of exact words on page 76.
- Next test:
  - Inspect those exact words on the high-res page for Typeka state changes, highlight-edge contacts, or one-letter visual marks.

### Named Term Visual Typography

- Status: tested; Typeka/highlight-edge extraction closed as a standalone selector.
- Evidence:
  - `scripts/analyze_named_term_visual_typography.py`
  - `analysis_outputs/source_audit/named_term_visual_typography/named_term_visual_typography.md`
  - `analysis_outputs/source_audit/named_term_visual_typography/named_term_visual_typography.json`
  - `analysis_outputs/source_audit/named_term_visual_typography/named_term_visual_typography_overlay.jpg`
- Scope:
  - Checked only the named page-76 terms from the line-offset ledger against `Article with Fonts.docm` font states, high-res page-76 OCR boxes, and trusted orange/grey highlight boxes.
  - No key candidates or hashing were generated.
- Findings:
  - Corrected a scan/OCR mismatch: the first page-76 `Bitcoin` is OCRed as `Biteoiny`, so row-first OCR-fuzzy matching is required.
  - After correction, O1 `bitcoin` contacts the O2 orange `Bitcoin` highlight with overlap `0.706`.
  - Highlight contacts are only:
    - O2 orange `Bitcoin line`: `1`.
    - B3 black `It's a stun gun to the genitals`: `2`.
    - O5 orange `shitcoiner-heart`: `1`.
  - Font-state edge streams are not instruction-like:
    - Entry letters: `gs`.
    - Exit letters: `nndsst`.
    - Highlight-edge letters: none.
  - `George Clinton` is the only Typeka Mix pair in the O2 carrier; the rest of that carrier line is ordinary Typeka.
- Conclusion:
  - The exact named terms do not provide a one-letter Typeka or highlight-edge selector.
  - This supports the idea that Typeka states are mostly styling/provenance unless a stronger rule names a specific font operation.
- Next test:
  - Investigate whether the unmatched `B3+3` landing (`Don't believe me?`) is an intentional gap/instruction break or has support from a different source layer.

### B3 Gap Bridge

- Status: tested; promote `B3+3` from unsupported miss to bridge evidence.
- Evidence:
  - `scripts/analyze_b3_gap_bridge.py`
  - `analysis_outputs/source_audit/b3_gap_bridge/b3_gap_bridge.md`
  - `analysis_outputs/source_audit/b3_gap_bridge/b3_gap_bridge.json`
  - `analysis_outputs/source_audit/b3_gap_bridge/b3_gap_bridge_overlay.jpg`
- Scope:
  - Checked whether `B3+3` (`Don't believe me?`) is a dead line-offset miss or a prompt line that points onward.
  - No key candidates or hashing were generated.
- Findings:
  - B3 source line 16 is `It's a stun gun to the genitals`.
  - First `+3` lands on line 19: `Don't believe me?`.
  - A second `+3` lands on line 22: `He's taunting them, telling them he's “buying the dip.”`.
  - Line 22 is the O4 orange `buying the dip` highlight.
  - This is unique among unsupported down-offset landings; the other unsupported rows do not land on a highlight after repeating the same source index.
- Conclusion:
  - `Don't believe me?` is probably a bridge/gateway into the El Salvador proof block, not standalone extraction material.
  - This gives the page-76 locator chain a cleaner route from B3 into O4.
- Next test:
  - Rebuild the page-76 locator chain with `B3 -> prompt -> O4`, then see whether the ordered chain itself suggests a word/line/letter unit.

### Page-76 Bridge-Normalized Chain

- Status: tested; structural chain active, chain streams closed as standalone instructions.
- Evidence:
  - `scripts/analyze_page76_bridge_normalized_chain.py`
  - `analysis_outputs/source_audit/page76_bridge_normalized_chain/page76_bridge_normalized_chain.md`
  - `analysis_outputs/source_audit/page76_bridge_normalized_chain/page76_bridge_normalized_chain.json`
  - `analysis_outputs/source_audit/page76_bridge_normalized_chain/page76_bridge_normalized_chain_overlay.jpg`
- Scope:
  - Normalized the line-offset chain by treating `B3+3` as a bridge through `Don't believe me?` into O4 `buying the dip`.
  - Checked only whether the resulting ordered chain gives an instruction-like selector.
  - No key candidates or hashing were generated.
- Findings:
  - Strict chain: `O1 B1 O3 B3 O4 B4 B5`.
  - Color stream: `OBOBOBB`.
  - Index stream: `1133445`.
  - Target lines: `1 7 16 22 26 29 32`.
  - Preferred terms: `bitcoin nonsense stun buying dip earnings sell heart`.
  - Initials: `bnsbesh`; last letters: `nenpslt`.
  - No instruction terms appeared in the streams or reversals.
- Conclusion:
  - The B3 bridge makes the page-76 locator chain more coherent but still does not define the extraction unit.
  - The current unresolved segment is the lower corridor around `O4/B4/B5`: `buying the dip`, `earnings`, `sell`, `Volcano Bonds`, and `heart`.
- Next test:
  - Inspect the lower corridor with the normalized chain as a constraint, looking for the source rule that chooses exact unit/order inside the #4/#5 area.

### Lower Corridor Evidence Ranking

- Status: tested; ranking clarifies the conflict but does not solve the selector.
- Evidence:
  - `scripts/analyze_lower_corridor_evidence_ranking.py`
  - `analysis_outputs/source_audit/lower_corridor_evidence_ranking/lower_corridor_evidence_ranking.md`
  - `analysis_outputs/source_audit/lower_corridor_evidence_ranking/lower_corridor_evidence_ranking.json`
  - `analysis_outputs/source_audit/lower_corridor_evidence_ranking/lower_corridor_evidence_ranking_overlay.jpg`
- Scope:
  - Compared exact lower-corridor units under the bridge-normalized chain.
  - No key candidates or hashing were generated.
- Findings:
  - Highest ranked candidates:
    - `shitcoiner at heart`: score `13`, layers `5`.
    - `Volcano Bonds`: score `10`, layers `5`.
    - `could sell`: score `9`, layers `4`.
    - `I tagged Mike`: score `7`, layers `3`.
    - `trust that guy`, `$1 billion / should sell`, `pay off the IMF`, and `future bitcoin earnings`: score `6`.
    - `buying the dip`: score `5`.
  - Diagnostic streams did not name an instruction:
    - Ranked initials: `svcit1pfb`.
    - Strict lower-chain initials: `bfccs`.
- Conclusion:
  - Two evidence families conflict:
    - #5 convergence family: O5 `shitcoiner at heart` and G5 `Volcano Bonds`.
    - p78 graphic family: broad #4 band around `earnings`, `pay off the IMF`, `I tagged Mike`, and `could sell`.
  - The normalized chain points to the right area, but the exact unit/order is still missing.
- Next test:
  - Look for a rule that reconciles those families: either p78 graphic edges point into G5/O5, or the #5 pair defines how to order/select the #4 band.

### P78 Graphic Edge Reconciliation

- Status: tested; p78 frame/edge evidence reconciles the #4 band with the #5 pair.
- Evidence:
  - `scripts/analyze_p78_graphic_edge_reconciliation.py`
  - `analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.md`
  - `analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.json`
  - `analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation_overlay.jpg`
- Scope:
  - Tested reflected p78 graphic edges/corners against trusted lower-corridor page-76 boxes.
  - No key candidates or hashing were generated.
- Findings:
  - Reflected p78 graphic box on p76: `[1234, 2398, 2250, 2950]`.
  - Top-left corner lands on `should`; top edge cuts `should sell`.
  - Left edge cuts `earnings` and runs immediately to the right of trusted G5 `Volcano Bonds`.
  - G5 `Volcano Bonds` is left-edge adjacent: `38px` gap, `48px` vertical overlap.
  - Bottom edge cuts O5 `shitcoiner at heart`.
  - Bottom-left corner lies inside O5 (`0px` distance).
- Conclusion:
  - The filled p78 graphic explains why #4-band words are selected broadly.
  - The p78 graphic frame itself points back into the #5 pair, especially G5/O5.
  - This reconciles the evidence families better than treating p78 as a filled mask.
  - Still no final extraction unit is defined.
- Next test:
  - Inspect edge/corner order only: top-left `should`, left-edge `earnings`/G5 adjacency, bottom-left O5, and any consistent clockwise/counterclockwise frame read.

### P78 Frame Order Read

- Status: tested; frame order is semantic context, not a selector.
- Evidence:
  - `scripts/analyze_p78_frame_order_read.py`
  - `analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read.md`
  - `analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read.json`
  - `analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read_overlay.jpg`
- Scope:
  - Read only reflected p78 frame edges/corners.
  - Ignored the filled p78 mask.
  - No key candidates or hashing were generated.
- Findings:
  - Top edge: `should sell`.
  - Left edge top-to-bottom: `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`.
  - Left edge bottom-to-top: `shitcoiner at heart | trust that guy | could sell | I tagged Mike | Volcano Bonds | pay off the IMF | earnings | should sell`.
  - Minimal frame phrase: `should sell | Volcano Bonds | shitcoiner at heart`.
  - Initial streams: `svs`, `sepvicts`, `stcivpes`.
  - No extraction instruction terms appeared.
- Conclusion:
  - `should sell Volcano Bonds` is meaningful article prose, but not a puzzle instruction.
  - P78 frame order should be closed as a standalone selector.
  - P78 remains useful as a registration/frame clue for G5/O5.
- Next test:
  - Check whether the G5/O5 pair plus `should sell Volcano Bonds` points outside page 76 to a public/source instruction, original tweet/Canva clue, or p78 graphic label.

### Should Sell / Volcano Source-Clue Audit

- Status: tested; direct outside-instruction branch closed.
- Evidence:
  - `scripts/audit_should_sell_volcano_source_clues.py`
  - `analysis_outputs/source_audit/should_sell_volcano_source_clues/should_sell_volcano_source_clues.md`
  - `analysis_outputs/source_audit/should_sell_volcano_source_clues/should_sell_volcano_source_clues.json`
- Scope:
  - Checked whether the p78 frame phrase `should sell | Volcano Bonds | shitcoiner at heart` appears in original public clue text, the Canva note, the Schott clue record, the recovered announcement thread, external-clue inventories, or p78 graphic reports.
  - No key candidates or hashing were generated.
- Findings:
  - Original public clues contain `should sell`: `False`.
  - Original public clues contain `Volcano Bonds`: `False`.
  - Original public clues contain `shitcoiner at heart`: `False`.
  - `should sell` appears in the corrected article text and our p78-frame reports only.
  - `Volcano Bonds` appears in derived media/context inventories as part of the page-76 Bukele/volcano corridor, not as a source-level instruction.
  - The p78 graphic text is `The economy of love is infinitely more efficient than hate and war.`, so it does not directly encode `sell`, `Volcano Bonds`, or a word/letter extraction rule.
- Conclusion:
  - `should sell Volcano Bonds` is article-context frame evidence, not an external clue instruction.
  - Keep p78 frame evidence as support for the G5/O5 lower page-76 pair, but do not derive key material from the phrase itself.
- Next test:
  - Inspect original visual labels/marks around the p78 graphic/page-76 lower corridor, or wait for a higher-resolution Canva/original/physical source that can supply the missing extraction unit.

### P78 Frame Visual Marks

- Status: tested; visual registration evidence strengthened, extraction unit still missing.
- Evidence:
  - `scripts/analyze_p78_frame_visual_marks.py`
  - `analysis_outputs/source_audit/p78_frame_visual_marks/p78_frame_visual_marks.md`
  - `analysis_outputs/source_audit/p78_frame_visual_marks/p78_frame_visual_marks.json`
  - `analysis_outputs/source_audit/p78_frame_visual_marks/p78_frame_visual_marks_overlay.jpg`
- Scope:
  - Added known lower page-76 visual marks to the reflected p78 frame-edge audit.
  - No key candidates or hashing were generated.
- Findings:
  - Top side remains text-only: `should sell`.
  - Left side carries the corridor-text contacts and G5 `Volcano Bonds` adjacency.
  - Right side cuts true standalone visual mark M3 with `265px` vertical overlap.
  - Bottom side cuts O5 `shitcoiner at heart`; M4 sits just below-adjacent to the bottom edge with `53px` vertical gap and `293px` horizontal overlap.
- Conclusion:
  - The reflected p78 graphic is not merely framing text; it also registers the lower-right non-text mark system.
  - M3 is now a stronger active object because it occupies the otherwise-unused right edge of the p78 frame.
  - This is orientation/registration evidence only until a rule says whether to read adjacent rows, ray hits, edge-crossed words, or mark axes.
- Next test:
  - Inspect M3 as a frame-side marker: compare its axis/ray with the p78 right edge and test only simple adjacent-row labels, not private-key derivation.

### M3 Frame-Side Marker

- Status: tested; M3 axis is orientation evidence, not a standalone selector.
- Evidence:
  - `scripts/analyze_m3_frame_side_marker.py`
  - `analysis_outputs/source_audit/m3_frame_side_marker/m3_frame_side_marker.md`
  - `analysis_outputs/source_audit/m3_frame_side_marker/m3_frame_side_marker.json`
  - `analysis_outputs/source_audit/m3_frame_side_marker/m3_frame_side_marker_overlay.jpg`
- Scope:
  - Compared M3's main stroke axis against the reflected p78 frame and adjacent page-76 lower rows.
  - No key candidates or hashing were generated.
- Findings:
  - M3 axis angle is `173.75°`.
  - The axis crosses the p78 frame from `[2250, 2763.33]` on the right edge to `[1234, 2874.64]` on the left edge.
  - Right-edge entry is closest to `bunch to his Wall Street crony pals, but so far he`.
  - Left-edge exit is closest to `hasn't moved on it. I don't really trust that guy.`
  - Axis word read from frame-right: `guy that trust really a he's because Maybe`.
  - Reverse: `Maybe because he's a really trust that guy`.
  - Instruction-term hits: none.
- Conclusion:
  - M3 is a real frame-side orientation marker pointing into the `trust that guy` / `Maybe because...` lower corridor.
  - Its axis does not produce an instruction or clean extraction unit.
  - Close M3-axis reading as a standalone selector.
- Next test:
  - Compare M3 and M4 as a paired lower-right mark system. If they form brackets around a row/phrase, test that bracketed unit; otherwise keep both as orientation evidence.

### M3/M4 Pair Bracket

- Status: tested; paired mark system confirms O5 endpoint, but no extraction unit.
- Evidence:
  - `scripts/analyze_m3_m4_pair_bracket.py`
  - `analysis_outputs/source_audit/m3_m4_pair_bracket/m3_m4_pair_bracket.md`
  - `analysis_outputs/source_audit/m3_m4_pair_bracket/m3_m4_pair_bracket.json`
  - `analysis_outputs/source_audit/m3_m4_pair_bracket/m3_m4_pair_bracket_overlay.jpg`
- Scope:
  - Tested whether the two true lower-right marks form a bracket/wedge around page-76 text.
  - No key candidates or hashing were generated.
- Findings:
  - M3/M4 axes intersect at `[999.28, 2900.36]`, just left of the final orange line.
  - The right-opening wedge selects `guy [O5: shitcoiner at heart]`.
  - O5 `p76_orange_5` is inside the wedge; sample fraction `0.5714`, centerInside `True`.
  - G5 `Volcano Bonds` is outside the wedge.
  - Instruction-term hits: none.
- Conclusion:
  - M3 and M4 behave as a paired lower-right bracket system.
  - The bracket confirms O5 `shitcoiner at heart` as the endpoint of this visual system and links it to the previous `trust that guy` row.
  - It does not provide a clean extraction rule or select the G5/O5 pair together.
  - Close M3/M4 bracket text as a standalone selector.
- Next test:
  - Stop trying to read M3/M4 as text. Reassess the higher-level source rule needed to order confirmed targets: G5/O5, p78 frame, and Schott mirror.

### P78 Pull-Quote Component Selector

- Status: tested; component-level selector closed.
- Evidence:
  - `scripts/analyze_p78_pullquote_component_selector.py`
  - `analysis_outputs/source_audit/p78_pullquote_component_selector/p78_pullquote_component_selector.md`
  - `analysis_outputs/source_audit/p78_pullquote_component_selector/p78_pullquote_component_selector.json`
  - `analysis_outputs/source_audit/p78_pullquote_component_selector/p78_pullquote_component_selector_overlay.jpg`
  - `analysis_outputs/source_audit/p78_pullquote_component_selector/p78_pullquote_component_source_overlay.jpg`
- Scope:
  - Split the p78 lower graphic pull-quote into connected components and mirrored each component onto page 76.
  - No key candidates or hashing were generated.
- Findings:
  - The p78 pull-quote graphic has `13` connected components under the current high-res scan threshold.
  - Component target stream: `the | Mike | off | sell off the IMF Mike sella so far he that guy [O5: shitcoiner at heart] | tagged could | pals, trust`.
  - Highlight stream: `C10:p76_orange_5 | C12:p76_orange_5 | C13:p76_orange_5`.
  - No component isolates an instruction or a decisive word/letter unit.
  - Instruction-term hits: none.
- Conclusion:
  - Component-level p78 graphic reading only repeats the broad lower-corridor evidence.
  - The p78 pull-quote should remain a frame/orientation layer, not component-ordered key material.
- Next test:
  - Reassess source/physical registration and Schott mirror-operation ordering using the confirmed targets, rather than reading further p78 component fragments.

### Confirmed Target Rule Synthesis

- Status: tested; local confirmed-order streams closed as instruction sources.
- Evidence:
  - `scripts/analyze_confirmed_target_rule_synthesis.py`
  - `analysis_outputs/source_audit/confirmed_target_rule_synthesis/confirmed_target_rule_synthesis.md`
  - `analysis_outputs/source_audit/confirmed_target_rule_synthesis/confirmed_target_rule_synthesis.json`
- Scope:
  - Synthesized only confirmed active objects: convergence ranking, G5/O5, p78 frame order, M3/M4 endpoint, bridge-normalized chain, and archived public clue text.
  - Tested only low-parameter mirror/frame orderings for instruction-like language.
  - No key candidates or hashing were generated.
- Findings:
  - Local actionable streams with instruction/unit hits: `0`.
  - Only the archived public clue text produces instruction-like terms: `private`, `key`, and `mirror`.
  - `Volcano Bonds | shitcoiner at heart`, reversed order, initials `vbsah`/`sahvb`, last letters `osrtt`, and word lengths `7.5.10.2.5` produce no instruction or unit.
  - P78 frame streams, M3/M4 bracket streams, and bridge-normalized chain streams are target/location evidence only.
- Conclusion:
  - The confirmed local visual system converges on O5 and G5/O5, but does not tell us whether to extract a line, word, letter, edge, axis, or adjacent phrase.
  - The remaining gap is the source rule: how `private key encoded` + `mirror writing` should be applied to the confirmed target surface.
- Next test:
  - Audit true physical leaf/spread assumptions against the best scan using O5/G5 as validation points, or obtain the exact original/physical source material.

### Physical Model O5/G5 Validation

- Status: tested; physical leaf/spread validation closed under the current best scan.
- Evidence:
  - `scripts/audit_physical_model_o5_g5_validation.py`
  - `analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation.md`
  - `analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation.json`
  - `analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation_overlay.jpg`
- Scope:
  - Compared true physical/source models against trusted page-76 O5/G5 boxes.
  - Used trusted G5 `Volcano Bonds` from `lower_page76_mark_pointers.json`, not the stale projected `p76_grey_5` box.
  - No key candidates or hashing were generated.
- Findings:
  - `75 -> 76`, `77 -> 76`, `78 -> 76`, `79 -> 76`, and `80 -> 76` produced `0` direct overlaps with trusted O5/G5.
  - P78 frame still supports the lower corridor: it overlaps O5 by `0.24754` of target area and sits `38px` horizontally from trusted G5.
  - Stale projected `p76_grey_5` overlaps O5 by `0.90857` under the old x=`1322` self-mirror axis.
  - Trusted G5 overlaps O5 by `0.0` under the same axis and is `340px` vertically away.
- Conclusion:
  - The old B5/O5 page-76 self-mirror evidence is geometry-contaminated by the stale projected G5 box.
  - G5/O5 remains meaningful as a semantic/corridor pair, but not as a precise self-mirror extraction unit under the current trusted scan.
  - P78 frame/O5 remains active orientation evidence; true physical leaf/spread models do not currently explain the pair.
- Next test:
  - Stop relying on old B5/O5 exact geometry. Focus on source-side evidence: original Canva/browser image, physical scan/photo, or source file that can validate how the p78 frame/O5 endpoint and trusted G5 adjacency should be read.

### P78 Frame Trusted-Target Sensitivity

- Status: tested; active as orientation/source-registration evidence only.
- Evidence:
  - `scripts/audit_p78_frame_trusted_target_sensitivity.py`
  - `analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity/p78_frame_trusted_target_sensitivity.md`
  - `analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity/p78_frame_trusted_target_sensitivity.json`
  - `analysis_outputs/source_audit/p78_frame_trusted_target_sensitivity/p78_frame_trusted_target_sensitivity_overlay.jpg`
- Scope:
  - Rechecked the p78 lower graphic frame against trusted G5/O5 after the stale G5 correction.
  - No key candidates or hashing were generated.
- Findings:
  - Current p78 frame clips O5 `shitcoiner at heart` by `0.24754` of target area.
  - Current p78 frame does not overlap trusted G5 `Volcano Bonds`; it sits `38px` to the right with `0px` vertical gap.
  - Nearest true simultaneous O5/G5 overlap in the bounded grid is dx=`-40`, dy=`0`.
  - O5 clip is vertically sensitive: a pure upward shift of about `20px` loses O5.
- Conclusion:
  - P78 frame still points to the lower page-76 corridor, but as a registration/orientation clue.
  - It is not precise enough to define letter/word extraction under the current scan.
  - Any new source image should be judged by whether it naturally explains the G5 near-edge relation and O5 bottom-edge clip.
- Next test:
  - Use the p78-frame sensitivity profile as a validation benchmark for new source material; otherwise move to source acquisition/inspection rather than local p78-frame key extraction.

### Lower Corridor Font-State Selector

- Status: tested; closed as direct selector.
- Evidence:
  - `scripts/audit_lower_corridor_font_state_selector.py`
  - `analysis_outputs/docm_format_sources/lower_corridor_font_state_selector/lower_corridor_font_state_selector.md`
  - `analysis_outputs/docm_format_sources/lower_corridor_font_state_selector/lower_corridor_font_state_selector.json`
- Scope:
  - Checked Typeka, Typeka Mix, Typeka-bold, and highlight states only in the page-76 lower corridor selected by p78 frame/marks.
  - Used run-concatenated DOCM text to avoid plain-text line-break drift.
  - No key candidates or hashing were generated.
- Findings:
  - Corridor dominant-style stream: `YBKRRKRBRRMY`, with no instruction hits.
  - P78-frame-touched dominant-style stream: `RRKRRRMY`, with no instruction hits.
  - P78-frame-touched initials: `seVpIcts`, with no instruction hits.
  - Highlight/Mix narrowed stream: `YKKRMY`, initials `b$VIts`, with no instruction hits.
  - `Volcano Bonds` is black/bold; `shitcoiner at heart` is yellow/bold; `trust that guy` is Typeka Mix; `I tagged Mike` crosses regular -> Mix.
- Conclusion:
  - The lower corridor font states are structured but follow visible typography and semantic emphasis.
  - Typeka Mix is not a clean standalone selector here.
  - Font states remain a witness layer only; they still need an external/source rule to choose units.
- Next test:
  - Do not rerun local Typeka initial/length/state streams without a new source rule. Continue source acquisition/registration checks.

### P78 Frame Gap-Repair Selector

- Status: tested; closed as standalone selector.
- Evidence:
  - `scripts/audit_p78_frame_gap_repair_selector.py`
  - `analysis_outputs/source_audit/p78_frame_gap_repair_selector/p78_frame_gap_repair_selector.md`
  - `analysis_outputs/source_audit/p78_frame_gap_repair_selector/p78_frame_gap_repair_selector.json`
  - `analysis_outputs/source_audit/p78_frame_gap_repair_selector/p78_frame_gap_repair_selector_overlay.jpg`
- Scope:
  - Tested whether the smallest local repair for the trusted-G5 near-miss, dx=`-40`, turns the p78 frame into a clean selector.
  - No key candidates or hashing were generated.
- Findings:
  - Current frame and dx=`-40` repaired frame produce the same top-down phrase path:
    `should sell | earnings | pay off the IMF | Volcano Bonds | I tagged Mike | could sell | trust that guy | shitcoiner at heart`.
  - Current initials are `sepVIcts`; repaired initials are also `sepVIcts`; no instruction hits.
  - The dx=`-40` repair makes G5 a true frame cut while preserving O5, but does not alter the selected language.
  - A heavier dx=`-160`, dy=`35` local fit increases overlap but still produces the same phrase stream and no instruction hits.
- Conclusion:
  - Local frame shifting cannot supply the missing extraction rule.
  - dx=`-40` is useful only as a future registration signature: a new source image should naturally explain that offset if it is real.
- Next test:
  - Do not use shifted p78 frames as key material. Continue source-side validation or physical/original scan acquisition.

### Announcement Media Order Selector

- Status: tested; closed as direct ordering selector.
- Evidence:
  - `scripts/audit_announcement_media_order_selector.py`
  - `analysis_outputs/external_clues/announcement_media_order_selector/announcement_media_order_selector.md`
  - `analysis_outputs/external_clues/announcement_media_order_selector/announcement_media_order_selector.json`
  - `analysis_outputs/external_clues/announcement_media_order_selector/announcement_media_order_selector_sheet.jpg`
- Scope:
  - Tested whether the seven true recovered announcement images, in public order, supply the missing order into page 76.
  - No key candidates or hashing were generated.
- Findings:
  - Unique page-76 units from media order: `President Nayib Bukele | president of El Salvador | volcanoes to mine | Volcano Bonds`.
  - Unique initials: `PpvV`; no instruction hits.
  - Missing expected lower-corridor units: `buying the dip`, `$1 billion`, and `IMF loan`.
  - Media order does not specify `should sell`, `could sell`, `trust that guy`, or O5 `shitcoiner at heart`.
- Conclusion:
  - The media sequence is target confirmation, not an extraction selector.
  - It keeps page 76/Bukele/volcano/Volcano Bonds high-confidence, but it does not choose word/letter/line order.
- Next test:
  - Do not use media order as key material. Continue source/physical registration work.

### Opener Capsule Endpoint Selector

- Status: tested; closed as direct selector.
- Evidence:
  - `scripts/audit_opener_capsule_endpoint_selector.py`
  - `analysis_outputs/source_audit/opener_capsule_endpoint_selector/opener_capsule_endpoint_selector.md`
  - `analysis_outputs/source_audit/opener_capsule_endpoint_selector/opener_capsule_endpoint_selector.json`
- Scope:
  - Tested whether the five opener capsules, after projection near M3/M4, choose page-76 lower-corridor units.
  - No key candidates or hashing were generated.
- Findings:
  - Forced nearest-mark sequence: `M3M3M4M4M4`; no instruction hits.
  - Forced unit stream: `trust that guy | trust that guy | shitcoiner at heart | shitcoiner at heart | shitcoiner at heart`; no instruction hits.
  - Tight thresholds do not assign all five capsules: <=`75px` assigns 1/5, <=`150px` assigns 2/5, <=`250px` assigns 4/5.
  - A full `M3M3M4M4M4` sequence requires a broad <=`500px` threshold, which is too loose to be a precise selector.
- Conclusion:
  - Opener capsules reinforce the lower-right M3/M4/O5 endpoint system but do not supply a stable extraction unit.
  - O5 is reconfirmed; the missing word/letter/line rule remains absent.
- Next test:
  - Keep opener capsules as provenance/order evidence only. Reopen only with a better source transform or an explicit clue naming M3/M4 as index/binary material.

### Source Registration Acceptance Test

- Status: active gate for future geometry/source work.
- Evidence:
  - `scripts/build_source_registration_acceptance_test.py`
  - `analysis_outputs/source_audit/source_registration_acceptance_test/source_registration_acceptance_test.md`
  - `analysis_outputs/source_audit/source_registration_acceptance_test/source_registration_acceptance_test.json`
- Scope:
  - Consolidated the active visual/source constraints into a pass/fail benchmark.
  - No key candidates or hashing were generated.
- Findings:
  - `PASS`: trusted O5/G5 source boxes are now fixed.
  - `PARTIAL`: p78 frame signature exists, but needs a natural source transform: O5 overlap `0.24754`, G5 gap `38px`, dx=`-40` repair.
  - `FAIL`: no current local source names an extraction unit.
  - `FAIL`: current physical leaf/spread models produce zero trusted O5/G5 direct overlaps.
  - `PARTIAL`: opener capsules, announcement media, and current source registration are provenance/target evidence only.
  - `FAIL`: Canva thumbnail is not geometry truth.
- Conclusion:
  - The current local corpus is sufficient for target discovery, not final extraction.
  - A new local geometry stream should not be promoted unless it both explains the p78/O5/G5 registration signature and names a reading unit.
- Next test:
  - Acquire or inspect a better source image/physical scan and score it against this benchmark before extracting words/letters.

### Local Source Candidate Inventory

- Status: tested; no already-local source promoted.
- Evidence:
  - `scripts/audit_local_source_candidates.py`
  - `analysis_outputs/source_audit/local_source_candidate_inventory/local_source_candidate_inventory.md`
  - `analysis_outputs/source_audit/local_source_candidate_inventory/local_source_candidate_inventory.json`
  - `analysis_outputs/source_audit/local_source_candidate_inventory/local_source_candidate_contact_sheet.jpg`
  - `analysis_outputs/source_audit/local_source_candidate_inventory/local_screenshot_visual_review.md`
  - `analysis_outputs/source_audit/local_source_candidate_inventory/local_screenshot_visual_review.json`
- Scope:
  - Audited local PDFs, images, DOCM/DOCX files, and screenshots for source-registration value.
  - No key candidates or hashing were generated.
- Findings:
  - `magazine.pdf` remains the only source-grade Issue 24 geometry file already on disk.
  - Desktop `magazine.pdf` is a duplicate of the repo copy.
  - `Article with Fonts.docm` is useful for Typeka/Typeka Mix/font-state labels only after a stronger geometry selector exists.
  - `BOLD.docm` is not active unless original source workflow files are recovered.
  - The independent comparison Max/OVERDOSE PDFs can test style/layout recurrence, but cannot replace Issue 24 geometry.
  - `bitcoin4.pdf` is a low-res Issue 24 witness, not an independent comparison article.
  - The Desktop screenshots do not show a better Issue 24 page, high-res Canva export, browser source, or physical-source capture.
- Conclusion:
  - The local file corpus does not solve the source-registration gap.
  - No local screenshot should be promoted to puzzle source evidence.
- Next test:
  - Either obtain/inspect a truly new source image or run a style-only comparison against the independent Max/OVERDOSE PDFs.

### OVERDOSE Style Uniqueness Audit

- Status: tested; generic style downgraded, Issue 24 body highlighter system remains active.
- Evidence:
  - `scripts/audit_overdose_style_uniqueness.py`
  - `analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness.md`
  - `analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness.json`
  - `analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness_contact_sheet.jpg`
- Scope:
  - Compared Issue 24 against local Max/OVERDOSE PDFs for recurring layout motifs.
  - No key candidates or hashing were generated.
- Findings:
  - `bitcoin4.pdf` is the same Issue 24 article in lower quality / alternate geometry, not an independent comparison.
  - `Issue_26.pdf`, `Issue_27.pdf`, and `bitcoin3.pdf` show recurring Max/OVERDOSE style: large graphics, dark pages, colored emphasis, and recurring feature branding.
  - None of the independent comparison PDFs provides Issue 24 geometry or an extraction unit.
  - The sustained Issue 24 body-text orange/grey highlighter pattern remains distinctive relative to the independent comparison set.
  - The comparison PDFs are image-only, so they cannot prove or disprove embedded Typeka/Typeka Mix font use.
- Conclusion:
  - Generic OVERDOSE branding, dark backgrounds, and broad colored art should be treated as house style/provenance.
  - Exact Issue 24 orange/grey highlights remain active only because they interact with the page-76 mirror/registration corridor.
  - Typeka/font-state streams remain inactive until another rule selects exact words/lines.
- Next test:
  - Continue toward source/physical registration or a rule that names the extraction unit, not more generic style comparison.

### Body Highlighter Grammar Audit

- Status: tested; active as style-control support, closed as selector.
- Evidence:
  - `scripts/audit_body_highlighter_grammar.py`
  - `analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.md`
  - `analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.json`
  - `analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar_sheet.jpg`
- Scope:
  - Detected line-shaped orange and dark/grey highlighter components across extracted local Max/OVERDOSE comparison page images.
  - No OCR, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Issue 24 has `28` orange line bands and `14` dark line bands, with sustained/mixed pages `[3, 4, 6, 7]`.
  - `issue26` and `bitcoin3` have fewer/localized detections; visual inspection shows many are display bars, product/cover art, or colored design regions rather than repeated body-text highlighting.
  - The line-shaped detector therefore supports the prior qualitative read: broad Max/OVERDOSE color is house style, but the repeated Issue 24 body-text orange/grey grammar is still distinctive.
- Conclusion:
  - The highlighter system remains puzzle-relevant only where it intersects page-76 mirror/registration evidence.
  - The comparison-style metrics do not provide an extraction unit or a reason to derive keys.
- Next test:
  - Stop local style comparison unless a new source appears. Continue toward source/physical registration or a clue that names the exact unit/order.

### bitcoin4 Issue 24 Geometry Witness

- Status: tested; closed as geometry upgrade.
- Evidence:
  - `scripts/audit_bitcoin4_issue24_geometry_witness.py`
  - `analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness.md`
  - `analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness.json`
  - `analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness_overlay.jpg`
- Scope:
  - Tested whether lower-quality `bitcoin4.pdf`, now known to be the same Issue 24 article, naturally repairs p78-to-p76 registration.
  - No key candidates or hashing were generated.
- Findings:
  - Page-specific orange-band registration fits were good enough for witness testing: p76 mean residual `3.618px`, p78 mean residual `4.595px`.
  - The reflected p78 frame in `bitcoin4` geometry still clips O5 `shitcoiner at heart` with overlapVsTarget `0.43908`.
  - The same frame has zero overlap with trusted G5 `Volcano Bonds` and sits `84.098px` away horizontally.
  - That is worse than the simple scaled high-res baseline G5 gap of `30.472px`.
- Conclusion:
  - `bitcoin4.pdf` does not solve the source-registration gap.
  - It supports the lower-right/O5 endpoint as a repeated visual target, but not a precise G5 extraction geometry.
- Next test:
  - Keep `bitcoin4.pdf` as a source-fidelity witness only. A better source/physical scan or explicit reading-unit clue is still required.

### Canva Connector Metadata Audit

- Status: tested; still thumbnail/provenance only.
- Evidence:
  - `analysis_outputs/external_clues/canva_connector_metadata_audit.md`
  - `analysis_outputs/external_clues/canva_connector_metadata_audit.json`
- Scope:
  - Used the Canva connector to inspect the shared design metadata and page thumbnail availability.
  - No design edits, key candidates, or hashing were generated.
- Findings:
  - Design id: `PRIVATE_CONTRIBUTOR`.
  - Title: `PRIVATE_ANNOTATION_OMITTED`.
  - Page count: `1`.
  - Created: `2026-04-24T14:47:51Z`; updated: `2026-04-30T00:23:29Z`.
  - Both design metadata and page listing expose only a `668x376` thumbnail.
  - No higher-resolution page image or original embedded source asset was exposed through the safe non-editing metadata path.
- Conclusion:
  - Canva remains a clue-board/provenance witness, not geometry truth.
  - Its title supports the pill-alignment/diff-image branch, but it does not name a word/letter/line extraction unit.
- Next test:
  - Reopen Canva source evidence only if a true high-resolution export, original embedded asset, safe element/content dump, or physical/source confirmation becomes available.

### Canva Diff Vector Signal

- Status: tested; closed as direct selector.
- Evidence:
  - `scripts/audit_canva_diff_vector_signal.py`
  - `analysis_outputs/source_audit/canva_diff_vector_signal/canva_diff_vector_signal.md`
  - `analysis_outputs/source_audit/canva_diff_vector_signal/canva_diff_vector_signal.json`
  - `analysis_outputs/source_audit/canva_diff_vector_signal/canva_diff_vector_signal_overlay.jpg`
  - `analysis_outputs/source_audit/canva_diff_vector_signal/canva_diff_vector_signal_crop.jpg`
- Scope:
  - Treated `PRIVATE_ANNOTATION_OMITTED` as a literal difference-vector clue.
  - Measured vectors from each ordered capsule projection to its nearest page-76 M3/M4 mark.
  - No key candidates, hashing, seed phrases, or address checks were generated.
- Findings:
  - Nearest-mark pattern: `M3M3M4M4M4`.
  - Distances: `56.94`, `228.27`, `204.96`, `130.54`, `420.93` px.
  - Tight thresholds are incomplete: only `1/5` within `75px`, `2/5` within `150px`, and `4/5` within `250px`.
  - Sign pattern `LD RD RD LD LU`, distance bands `TMMNF`, and rank order `14325` do not form a readable rule.
  - Forced endpoint units still reduce to `trust that guy` / `shitcoiner at heart`, with no instruction-term hits.
- Conclusion:
  - The current high-res scan does not support a residual-vector cipher from the pill mismatch.
  - Keep the Canva title as source-fidelity/provenance evidence, not key material.
- Next test:
  - Use `diff pic?` only to compare a new source image, high-resolution Canva export, original embedded asset, browser/original-layout view, or physical scan/photo against the current five-capsule baseline.

### G5/O5 Symmetric Line-Fold

- Status: tested; closed as direct selector.
- Evidence:
  - `scripts/audit_g5_o5_symmetric_line_fold.py`
  - `analysis_outputs/source_audit/g5_o5_symmetric_line_fold/g5_o5_symmetric_line_fold.md`
  - `analysis_outputs/source_audit/g5_o5_symmetric_line_fold/g5_o5_symmetric_line_fold.json`
  - `analysis_outputs/source_audit/g5_o5_symmetric_line_fold/g5_o5_symmetric_line_fold_diagram.jpg`
- Scope:
  - Tested a Schott-compatible two-handed/mirror read across the six printed lines from G5 `Volcano Bonds` to O5 `shitcoiner at heart`.
  - Paired `27/32`, `28/31`, and `29/30` outside-in, then reversed inside-out.
  - No key candidates, hashing, seed phrases, or address checks were generated.
- Findings:
  - Outside-in initials: `cMlhNb`; inside-out initials: `NblhcM`.
  - Outside-in last initials: `Fteyae`; inside-out last initials: `aeeyFt`.
  - Word-count differences: `022`.
  - Highlight stream is ordinary corridor content: `Volcano Bonds | IMF | shitcoiner at heart | Mike | I don't really trust that guy | Novogratz`.
  - Bold stream `IMFshitcoineratheartloanieIdelluhuNvz` and partial-bold stream `iedelluhuNvz` are not instruction-like.
- Conclusion:
  - The G5/O5 five-line gap remains real as locator evidence, but the symmetric fold read does not supply the missing word/letter/line extraction rule.
  - Do not use local G5/O5 folded-line streams as key material.
- Next test:
  - Reopen only if a new source clue says to read paired lines, edges, bold text, or line folds. Otherwise stay on source/physical registration.

### Public Clue Index Selector

- Status: tested; closed as direct selector.
- Evidence:
  - `scripts/audit_public_clue_index_selector.py`
  - `analysis_outputs/source_audit/public_clue_index_selector/public_clue_index_selector.md`
  - `analysis_outputs/source_audit/public_clue_index_selector/public_clue_index_selector.json`
  - `analysis_outputs/source_audit/public_clue_index_selector/public_clue_index_selector_sheet.jpg`
- Scope:
  - Tested whether clue-word lengths and explicit public numbers (`20`, `BTC=3`) index page 76 or the confirmed corridor.
  - Terms tested came from the announcement and Schott title only.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Page-76 word stream: `toxicity Open Open toxicity Open some some UTXO heart bitcoin Open toxicity toxicity y'all toxicity bitcoin Open It's Bitcoin Open to`.
  - Corridor word stream: `believe seen seen believe seen Have Have International president you seen believe believe Twitter believe you seen Salvador El seen of`.
  - G5/O5 modulo line initials: `NccNchhNNMcNNlNMcMhcb`.
  - G5/O5 modulo last words: `a IMF IMF a IMF guy guy a a heart IMF a a Mike a heart IMF heart guy IMF he`.
  - Instruction-term hits: none.
- Conclusion:
  - Public clue indexing does not provide the missing extraction unit.
  - The public clue remains constraint evidence only: source article, private-key target type, `20 BTC`, and mirror-writing operation family.
- Next test:
  - Do not keep mutating public clue word lengths or numbers. Reopen only if new public wording is recovered.

### P78 Frame Tri-Contact Signature

- Status: tested; active as source-registration signature, not as selector.
- Evidence:
  - `scripts/audit_p78_frame_tricontact_signature.py`
  - `analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.md`
  - `analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json`
  - `analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg`
- Scope:
  - Tested whether the same small p78-frame repair can satisfy G5, O5, and M3 at once.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Current frame: G5 is `38px` left of the frame, M3 is cut by the right edge for `265px`, and O5 is clipped by the bottom edge with overlap `0.24754`.
  - Exact G5 edge-touch is dx=`-38`, dy=`0`.
  - At dx=`-38`, all three contacts hold:
    - left edge touches trusted G5;
    - right edge still cuts M3 for `265px`, and M3 axis remains inside M3;
    - bottom edge still clips O5, with O5 overlap `0.26957`.
  - The previous grid repair dx=`-40` is therefore consistent with this exact edge-touch signature.
  - The heavier dx=`-160`, dy=`35` overlap-maximizing shift breaks M3, so it is less plausible as source-like registration.
- Conclusion:
  - dx≈`-38/-40` is now a stronger source-registration validation signature.
  - It still does not specify an extraction unit.
- Next test:
  - Use this tri-contact signature to evaluate any new physical scan, original source image, or higher-resolution Canva/layout asset. Do not derive key material from the shifted frame alone.

### M3 Axis After Tri-Contact Repair

- Status: tested; closed as direct selector.
- Evidence:
  - `scripts/audit_m3_axis_after_tricontact_repair.py`
  - `analysis_outputs/source_audit/m3_axis_after_tricontact_repair/m3_axis_after_tricontact_repair.md`
  - `analysis_outputs/source_audit/m3_axis_after_tricontact_repair/m3_axis_after_tricontact_repair.json`
  - `analysis_outputs/source_audit/m3_axis_after_tricontact_repair/m3_axis_after_tricontact_repair_overlay.jpg`
- Scope:
  - Re-tested the M3 axis after the stronger dx=`-38/-40` p78-frame registration repair.
  - Compared current frame, exact G5 edge-touch dx=`-38`, grid dx=`-40`, and the lower-confidence dx=`-160`, dy=`35` overlap fit.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Current, dx=`-38`, and dx=`-40` all read `guy that trust` within the frame.
  - The same three scenarios reverse to `trust that guy` within the frame and reconstruct `Maybe because he's a really trust that guy` on the left continuation.
  - Instruction-term hits: none.
  - The dx=`-160`, dy=`35` fit expands the within-frame stream to `guy that trust really`, but it breaks the M3 frame-side contact and is less source-like.
- Conclusion:
  - The tri-contact repair is real registration evidence, but M3-axis reading still only selects local distrust/heart prose.
  - Do not use M3-axis streams as key material.
- Next test:
  - Use dx=`-38/-40` only to benchmark any new high-resolution Canva/original-layout asset or physical scan.

### Tri-Contact Frame Contact Stability

- Status: tested; closed as direct selector.
- Evidence:
  - `scripts/audit_tricontact_frame_contact_stability.py`
  - `analysis_outputs/source_audit/tricontact_frame_contact_stability/tricontact_frame_contact_stability.md`
  - `analysis_outputs/source_audit/tricontact_frame_contact_stability/tricontact_frame_contact_stability.json`
  - `analysis_outputs/source_audit/tricontact_frame_contact_stability/tricontact_frame_contact_stability_overlay.jpg`
- Scope:
  - Compared the p78 frame contact ladder under current geometry, exact G5 edge-touch dx=`-38`, grid dx=`-40`, and lower-confidence dx=`-160`, dy=`35`.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Current and dx=`-38` have the same top-down compact stream:
    `should sell | earnings | pay/IMF | G5 Volcano Bonds | tagged Mike | could sell | trust that guy | O5 heart`.
  - dx=`-40` keeps the same stream.
  - Contact relation changes are geometric only: dx=`-38` turns G5 into an exact left-edge contact while leaving the surrounding #4/#5 phrase ladder intact.
  - Instruction-term hits: none.
- Conclusion:
  - dx=`-38/-40` is a stronger registration benchmark, but it still does not identify a word/letter/line/key extraction unit.
  - Do not use the contact ladder as key material.
- Next test:
  - Continue source-side validation: look for a high-resolution Canva/original-layout export or physical scan/photo that naturally reproduces the same p78/G5/O5/M3 contacts.

### Repaired Frame Font-Contact States

- Status: tested; active as compact registration signature, closed as direct selector.
- Evidence:
  - `scripts/audit_repaired_frame_font_contact_states.py`
  - `analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states.md`
  - `analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states.json`
  - `analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states_sheet.jpg`
- Scope:
  - Cross-checked current, dx=`-38`, dx=`-40`, and dx=`-160`, dy=`35` p78-frame contact ladders against `Article with Fonts.docm` Typeka/font/highlight states.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Full top-down style ladder is stable: `RRRKRRMY`.
  - Current exact-edge subset is `should sell | earnings | shitcoiner at heart`, with style code `RRY`.
  - dx=`-38` and dx=`-40` exact-edge subset is cleaner: `should sell | Volcano Bonds | shitcoiner at heart`, with style code `RKY`.
  - Repaired exact-edge initials are `sVs`; repaired exact-edge last letters are `lst`.
  - Instruction-term hits: none.
  - Typeka Mix still lands on semantic prose (`trust that guy`, and `Mike` inside a mixed run), not a clean hidden-letter stream.
- Conclusion:
  - The repaired exact-edge trio is useful as a compact source-registration signature.
  - It does not by itself identify a word/letter/line/key extraction operation.
- Next test:
  - Use `should sell | Volcano Bonds | shitcoiner at heart` plus style code `R K Y` as a benchmark if a new Canva/original-layout/physical source appears.

### Repaired R-K-Y Signature Rarity

- Status: tested; active only as geometry-selected registration benchmark, closed as font cipher.
- Evidence:
  - `scripts/audit_repaired_rky_signature_rarity.py`
  - `analysis_outputs/docm_format_sources/repaired_rky_signature_rarity/repaired_rky_signature_rarity.md`
  - `analysis_outputs/docm_format_sources/repaired_rky_signature_rarity/repaired_rky_signature_rarity.json`
  - `analysis_outputs/docm_format_sources/repaired_rky_signature_rarity/repaired_rky_signature_rarity_sheet.jpg`
- Scope:
  - Checked whether the repaired exact-edge `R-K-Y` style code is rare by itself in the `Article with Fonts.docm` style stream.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Adjacent `R-K-Y` occurs once across pages 75-79, on page 75 only.
  - It does not occur as an adjacent page-76 style sequence.
  - If skipped/non-adjacent style groups are allowed, `R-K-Y` is common: `187` ordered triples across pages 75-79, including `60` on page 76.
- Conclusion:
  - `R-K-Y` alone is not a usable font cipher.
  - The useful evidence is the geometry-selected exact-edge trio: `should sell | Volcano Bonds | shitcoiner at heart`.
- Next test:
  - Use the exact-edge trio plus M3/O5/G5 tri-contact only as a source-registration acceptance benchmark for future high-fidelity source material.

### Page-75 Adjacent R-K-Y Leaf Test

- Status: tested; closed as p76 physical leaf selector.
- Evidence:
  - `scripts/audit_page75_adjacent_rky_leaf_to_p76.py`
  - `analysis_outputs/source_audit/page75_adjacent_rky_leaf_to_p76/page75_adjacent_rky_leaf_to_p76.md`
  - `analysis_outputs/source_audit/page75_adjacent_rky_leaf_to_p76/page75_adjacent_rky_leaf_to_p76.json`
  - `analysis_outputs/source_audit/page75_adjacent_rky_leaf_to_p76/page75_adjacent_rky_leaf_to_p76_overlay.jpg`
- Scope:
  - Tested the only adjacent `R-K-Y` style sequence, on page 75, as a hold-to-light / front-back leaf selector into the repaired page-76 exact-edge trio.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Page-75 adjacent `R-K-Y`: `epithet/proof of stake/mEthereum lab` -> `Don't fall for shitcoinery.` -> `Keep your dignity.`
  - Page-76 repaired exact-edge `R-K-Y`: `should sell` -> `Volcano Bonds` -> `shitcoiner at heart`.
  - Raw page75->page76 hflip gives `0` overlaps and mean center distance `551.7px`.
  - Prior leaf correction dx=`0`, dy=`-180` gives `0` overlaps and mean distance `677.64px`.
  - Best bounded translation dx=`-180`, dy=`180` reaches the allowed-range edge and creates only one forced overlap onto `should sell`; `Volcano Bonds` and `shitcoiner at heart` still miss.
  - Unconstrained centroid fit would require dx=`-433.37`, dy=`298.58`, which is not a credible physical crop correction.
- Conclusion:
  - The page-75 adjacent `R-K-Y` rarity does not validate a physical leaf mapping to page 76 under the current best scan.
  - Treat it as typography/provenance echo, not a selector.
- Next test:
  - Continue source-side validation of the page-76 repaired exact-edge trio and M3/O5/G5 tri-contact only when a new source image or physical scan appears.

### Page-75 R-K-Y Reflection Selection

- Status: tested; closed as mirror-selected evidence.
- Evidence:
  - `scripts/audit_page75_rky_reflection_selection.py`
  - `analysis_outputs/source_audit/page75_rky_reflection_selection/page75_rky_reflection_selection.md`
  - `analysis_outputs/source_audit/page75_rky_reflection_selection/page75_rky_reflection_selection.json`
  - `analysis_outputs/source_audit/page75_rky_reflection_selection/page75_rky_reflection_selection_overlay.jpg`
- Scope:
  - Tested whether the page79->page75 reflected-highlight boxes select the unique adjacent page-75 `R-K-Y` run.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Direct overlaps across the R/K/Y groups: `0`.
  - Near misses: `1`; only the regular R group sits `35.62px` below reflection `79_75_5`.
  - `79_75_5` selects earlier prose (`only the language of the shameless opportunists...`), not the `epithet/proof-of-stake` R group.
  - K `Don't fall for shitcoinery` and Y `Keep your dignity` are not selected by page79->page75 reflections.
- Conclusion:
  - Page79->page75 reflections stop just above the page-75 R group and never select K/Y.
  - Treat the unique page-75 `R-K-Y` run as typography/provenance echo, not selected clue material.
- Next test:
  - Keep the page-76 repaired exact-edge trio and p78/O5/G5/M3 tri-contact as the source-registration benchmark.

### Repaired Exact-Edge Stability Window

- Status: tested; active as source-registration benchmark, closed as direct extraction.
- Evidence:
  - `scripts/audit_repaired_exact_edge_stability_window.py`
  - `analysis_outputs/source_audit/repaired_exact_edge_stability_window/repaired_exact_edge_stability_window.md`
  - `analysis_outputs/source_audit/repaired_exact_edge_stability_window/repaired_exact_edge_stability_window.json`
  - `analysis_outputs/source_audit/repaired_exact_edge_stability_window/repaired_exact_edge_stability_window_heatmap.jpg`
- Scope:
  - Tested whether the repaired p78 exact-edge trio is a fragile offset artifact or a stable source-registration signature.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Grid: dx `-80..0`, dy `-20..20`, `3321` cells.
  - Target exact signature `should sell | Volcano Bonds | shitcoiner at heart` with styles `R K Y`: `1075` cells, dx `-80..-38`, dy `-4..20`.
  - M3/G5/O5 tri-contact: `1599` cells, dx `-78..-38`, dy `-18..20`.
  - Target exact signature plus tri-contact: `1025` cells, dx `-78..-38`, dy `-4..20`.
  - Common exact-edge streams contain no read/take/use/fold/mirror/word/letter/key instruction.
- Conclusion:
  - The repaired exact-edge trio is robust enough to keep as a source-registration benchmark.
  - It is not enough to derive key material because it still gives no extraction unit or ordering rule.
- Next test:
  - Compare this stability window against any future Canva/original-layout/physical source. If no new source appears, shift to p80 package copy / dosage counts or original browser/Canva clue inspection.

### Canva Live Clue Surface

- Status: tested; active as orientation/source-registration evidence, closed as hidden textual instruction.
- Evidence:
  - Canva design `PRIVATE_CONTRIBUTOR`
  - `scripts/audit_canva_live_clue_surface.py`
  - `analysis_outputs/source_audit/canva_live_clue_surface/canva_live_clue_surface.md`
  - `analysis_outputs/source_audit/canva_live_clue_surface/canva_live_clue_surface.json`
- Scope:
  - Read Canva metadata and richtext without editing the design.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Live title is `PRIVATE_ANNOTATION_OMITTED`.
  - The design has one page.
  - Connector-visible thumbnail is only `668x376`, so it is not usable as geometry truth.
  - Live richtext matches the known note: pills not lining up, `#0` missed by browser/PDF OCR, `XX` lining with barbed wire after rotation/mirroring, `SHIT` / `FUCK ALL SHITCOINS` spills, and possible page orientation/positioning.
  - Instruction-term hits are limited to `line`, from `in line with`; no `read`, `take`, `word`, `letter`, `key`, or `private` rule appears.
- Conclusion:
  - Canva richtext does not contain the missing selector.
  - The clue is still best read as source registration/orientation, not direct key text.
- Next test:
  - If no higher-resolution Canva/original-layout/physical source appears, run a local p78/p79/p80 graphic-mark inventory focused on the `XX` / barbed-wire / `SHIT`-spill alignment named by the Canva note.

### Graphic Spill Alignment Inventory

- Status: tested; active only as source-registration warning, closed as current-scan selector.
- Evidence:
  - `scripts/audit_graphic_spill_alignment_inventory.py`
  - `analysis_outputs/source_audit/graphic_spill_alignment_inventory/graphic_spill_alignment_inventory.md`
  - `analysis_outputs/source_audit/graphic_spill_alignment_inventory/graphic_spill_alignment_inventory.json`
  - `analysis_outputs/source_audit/graphic_spill_alignment_inventory/graphic_spill_alignment_inventory_sheet.jpg`
- Scope:
  - Manually annotated the obvious current-scan p78 `XX`/FUCK spill graphic, p79 barbed wire/pills/signature, and p80 package/SHITCOINS text.
  - Tested only simple identity, horizontal mirror, vertical mirror, and 180-degree relationships.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - P79 wire angle from approximate knots: `-26.83` degrees.
  - P78 `XX` pair does not become collinear with the p79 barbed-wire line under the tested simple transforms.
  - Best simple p78 transform is `vflip`, with worst X-to-wire distance `473.9px` and angle delta `28.54` degrees.
  - P80 `SHITCOINS` and symptom text map only as broad package/provenance evidence near p79 pill regions under simple flips.
- Conclusion:
  - The current high-res scan does not reproduce the Canva `XX`/barbed-wire/SHIT-spill observation as a clean selector.
  - Treat this as another source-registration gap, not extraction material.
- Next test:
  - Reopen only with a higher-resolution Canva/original-layout/physical overlay, or if a new source rule names which graphic object pair should be aligned.

### Magazine PDF Image Placement

- Status: tested; closed as explanation for dx repair, active only as locked scan source.
- Evidence:
  - `scripts/audit_magazine_pdf_image_placement.py`
  - `analysis_outputs/source_audit/magazine_pdf_image_placement/magazine_pdf_image_placement.md`
  - `analysis_outputs/source_audit/magazine_pdf_image_placement/magazine_pdf_image_placement.json`
- Scope:
  - Checked whether `magazine.pdf` contains per-page image placement, crop, rotation, or hidden image-layer differences that could explain the p78->p76 dx=`-38/-40` registration repair.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `8` pages, each with exactly one embedded image.
  - Every embedded page image is `2544x3264` RGB JPEG at `300 ppi`.
  - Page rotation is consistently `180`.
  - Each image fills the crop/media box exactly with rect `[0.0, 0.0, 610.56, 783.36]`.
  - Pixel/point scale is consistent at `4.166667 / 4.166667`.
- Conclusion:
  - The p78 dx=`-38/-40` repair is not explained by hidden PDF placement, crop-box mismatch, per-page scale drift, or extra embedded images inside `magazine.pdf`.
  - `magazine.pdf` remains the locked high-res scan source, but it does not contain another hidden geometry layer.
- Next test:
  - Continue with source/physical acquisition or human-readable selector rules on the locked high-res page-76 corridor; do not keep searching inside `magazine.pdf` for a hidden layer.

### Exact-Edge Literal Word Operations

- Status: tested; closed as current-scan selector.
- Evidence:
  - `scripts/audit_exact_edge_literal_word_ops.py`
  - `analysis_outputs/source_audit/exact_edge_literal_word_ops/exact_edge_literal_word_ops.md`
  - `analysis_outputs/source_audit/exact_edge_literal_word_ops/exact_edge_literal_word_ops.json`
- Scope:
  - Tested literal operations suggested by the stable exact-edge trio `should sell | Volcano Bonds | shitcoiner at heart`.
  - Operations were intentionally small: `sell` as remove/interval, `heart` as center/middle, and `bonds` as endpoints/connection.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Exact phrase line indexes are `25`, `27`, `32`; corridor indexes are `7`, `9`, `14`.
  - Line and corridor differences are both `[2, 5]`.
  - `heart` word/phrase centers produce `ouelcncoata` and `ldnoe`.
  - G5-to-O5 interval heart lines are ordinary prose: `Novogratz in the tweet, figuring he could sell a | bunch to his Wall Street crony pals, but so far he`.
  - `sell` remove/interval operations produce letter debris or ordinary corridor prose.
  - Instruction-hit operations: `0`.
- Conclusion:
  - Literal `sell` / `heart` / `bond` wordplay does not supply the missing selector under the current scan.
  - The exact-edge trio should stay source-registration evidence only unless a new clue explicitly names one of these operations.
- Next test:
  - Avoid re-running local wordplay on the exact-edge trio. Move to source/physical acquisition or a different independently motivated visual/source rule.

### Exact-Edge Line/Gap Selector

- Status: tested; closed as direct numeric selector.
- Evidence:
  - `scripts/audit_exact_edge_line_gap_selector.py`
  - `analysis_outputs/source_audit/exact_edge_line_gap_selector/exact_edge_line_gap_selector.md`
  - `analysis_outputs/source_audit/exact_edge_line_gap_selector/exact_edge_line_gap_selector.json`
- Scope:
  - Tested the exact-edge page line numbers `25,27,32`, corridor numbers `7,9,14`, and gaps `2,5` as a simple selector inside the page-76 corridor.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - A1Z26 gives only short fragments: `YAF`, `GIN`, `BE`; reversed gives `FAY`, `NIG`, `EB`.
  - Words `2` and `5` from the exact lines produce `billion that | Volcano pay | because shitcoiner`.
  - The same positions across highlighted corridor lines produce ordinary prose fragments, not an instruction.
  - Interval word selectors give `the loan those` and `could a Street`.
  - The `+2,+5` walk only restates the already-known path `should sell -> Volcano Bonds -> shitcoiner at heart`.
  - Instruction-hit operations: `0`.
- Conclusion:
  - The line/corridor numbers and `2,5` gaps do not name a word, letter, key, mirror, or direction rule under the current scan.
  - Treat them as structural locator evidence only.
- Next test:
  - Do not continue mining these numbers locally. Move to source/physical registration or a new independent rule that names the extraction unit.

### Registration Drift Explanation

- Status: tested; ordinary drift explanation weak; active as source-registration benchmark only.
- Evidence:
  - `scripts/audit_registration_drift_explanation.py`
  - `analysis_outputs/source_audit/registration_drift_explanation/registration_drift_explanation.md`
  - `analysis_outputs/source_audit/registration_drift_explanation/registration_drift_explanation.json`
- Scope:
  - Compared independent source/registration witnesses to decide whether the p78->p76 `dx=-38/-40` repair looks like ordinary page/source drift.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `magazine.pdf` page placement is uniform and full-bleed; no embedded image offset/scale drift explains the repair.
  - Alternate OCR/Google p79 pill geometry maps back to high-res p79 with mean residual `0.31px`, so it does not supply a new global offset.
  - `bitcoin4.pdf` has page-specific distortion, but its natural p78->p76 geometry worsens the trusted G5 gap to about `105.619px` high-res equivalent.
  - Current high-res p78 frame still needs local dx `-38/-40` to touch trusted G5 while preserving M3/O5 contact.
  - The exact trio plus tri-contact stability window is broad, dx `[-78,-38]`, dy `[-4,20]`, but still has no extraction unit.
- Conclusion:
  - Treat ordinary page/source drift as a weak explanation for `dx=-38/-40` with the files currently available.
  - The repair remains a validation benchmark for a future better source, not a solved physical correction.
- Next test:
  - Only promote a new physical/Canva/original-layout source if it explains the p78/O5/G5 signature and names a unit to read.

### P78 Frame Edge-Adjacent Units

- Status: tested; closed as current-scan selector.
- Evidence:
  - `scripts/audit_p78_frame_edge_adjacent_units.py`
  - `analysis_outputs/source_audit/p78_frame_edge_adjacent_units/p78_frame_edge_adjacent_units.md`
  - `analysis_outputs/source_audit/p78_frame_edge_adjacent_units/p78_frame_edge_adjacent_units.json`
  - `analysis_outputs/source_audit/p78_frame_edge_adjacent_units/p78_frame_edge_adjacent_units_overlay.jpg`
- Scope:
  - Tested whether text just outside or just inside the current p78 frame, dx=`-38` edge-touch frame, or dx=`-40` grid frame supplies the missing selector.
  - Covered top/bottom above/below lines and left/right inside/outside edge-adjacent strips.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Instruction-hit frame count: `0`.
  - Current and repaired frames cut `should sell` at the top and `shitcoiner at heart` at the bottom.
  - Top-adjacent line is `volcanoes to mine`; bottom-adjacent line is `trust that guy` / `really trust that guy`.
  - Repaired-frame outside-left stream is `that he | bitcoin | figuring | crony`.
  - Repaired-frame inside-clockwise stream is `should sell | shitcoiner at heart | should | earnings | to pay | I tagged | he could | but | trust`.
- Conclusion:
  - Edge-adjacent p78-frame reading produces ordinary page-76 corridor prose.
  - It does not name a word, letter, line, key, mirror, inside, outside, above, or below rule.
- Next test:
  - Keep the p78 frame as registration evidence only. Continue only with a better source/physical/Canva image or a new external rule that names the extraction unit.

### Typeka / Highlight Boundary Alignment

- Status: tested; closed as standalone selector.
- Evidence:
  - `scripts/audit_typeka_highlight_boundary_alignment.py`
  - `analysis_outputs/docm_format_sources/typeka_highlight_boundary_alignment/typeka_highlight_boundary_alignment.md`
  - `analysis_outputs/docm_format_sources/typeka_highlight_boundary_alignment/typeka_highlight_boundary_alignment.json`
- Scope:
  - Used `Article with Fonts.docm` as a formatting witness to test whether Typeka/Typeka Mix font-family transitions align with highlight on/off boundaries.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Runs inspected: `344`.
  - Font counts: `Typeka 6574`, `Typeka Mix 883`, `Stencil 19`, `LonestarW00-Regular 8`.
  - Highlight counts: none `6251`, yellow `748`, black `476`, cyan `9`.
  - Font-change boundaries: `58`; Typeka Mix boundaries: `56`; highlight-change boundaries: `71`.
  - Coincident font+highlight boundaries: only `3`.
  - Highlighted Typeka Mix chars: `0`.
  - Coincident boundary edge stream: `MaNoyG`.
  - Typeka Mix boundary edge stream is long/noisy: `MarBtTeMaccgtwaNocEtTsteVncyGtttGnanbdoecstdnsmfErdMzitIygJsSmRrleBrodPkfeFpEa51aySyAsssfeTeIkTrTIeSsWHu`.
  - The only instruction-term hit is `first` inside ordinary prose, not a boundary instruction.
- Conclusion:
  - Font-family changes and highlight boundaries are mostly separate in the DOCM witness.
  - Typeka Mix does not function as a highlight-intersection selector.
- Next test:
  - Keep `Article with Fonts.docm` as a formatting witness only. Reopen font-state extraction only if a source clue names font state or a better source first chooses exact words/lines.

### DOCM / Visual Highlight Consistency

- Status: tested; closed as standalone selector.
- Evidence:
  - `scripts/audit_docm_visual_highlight_consistency.py`
  - `analysis_outputs/docm_format_sources/docm_visual_highlight_consistency/docm_visual_highlight_consistency.md`
  - `analysis_outputs/docm_format_sources/docm_visual_highlight_consistency/docm_visual_highlight_consistency.json`
- Scope:
  - Compared `Article with Fonts.docm` yellow/black/cyan highlight runs against the manual high-res orange/grey visual highlight list.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - DOCM printed highlight spans: `34`; manual high-res visual spans: `34`.
  - Unmatched DOCM printed spans: `0`.
  - Unmatched visual spans: `1`, the p80 package/symptom text outside the DOCM article body.
  - DOCM cyan spans are p75 `M`, p75 `N`, and p78 `BILLION`.
  - No cyan bridge creates a new visual/DOCM phrase selector.
- Conclusion:
  - DOCM yellow/black mostly confirms the visible orange/grey highlight wording.
  - The DOCM does not add a hidden extra printed-highlight selector.
  - Cyan remains a DOCM-only formatting anomaly, not scan-visible evidence.
- Next test:
  - Use DOCM highlight data only as wording support after visual geometry chooses a region. Keep p80 package art separate as graphic/OVERDOSE evidence.

### 3D View Browser Sanity Check

- Status: tested; viewer remains manual orientation/correction surface only.
- Evidence:
  - `analysis_outputs/3d_article_map/3d_view_browser_sanity_check.md`
  - `analysis_outputs/3d_article_map/3d_view_browser_sanity_check.json`
- Scope:
  - Inspected the local 3D article map in the in-app browser, including `Fold` mode focused on page `76`.
  - No key candidates, hashing, seed phrases, OCR extraction, WIF checks, or address checks were generated.
- Findings:
  - The viewer tab is the expected `Max Keiser Puzzle 3D Article Map`.
  - `?layout=fold&focus=76` correctly activates Fold mode and page 76 focus.
  - The browser initially reported a tiny canvas in hidden/default measurement state; this is a browser viewport artifact, not puzzle geometry.
  - With normal inspection sizing, the canvas is visible and the enabled layer/count state matches the model: `5,966` letters, `1,243` words, `16` anchors, `29` mirror boxes.
  - The viewer's findings panel repeats the current ledger state: page 76 is strongest, ray/volcano language is target evidence, and the 76/79 fold system still lacks a selector.
- Conclusion:
  - The 3D map did not reveal a new hidden selector or contradiction.
  - Use it for manual review/corrections, not as a separate evidence source.
- Next test:
  - Continue with source/physical registration or a new source-level instruction. When using the viewer, start from `layout=fold&focus=76` and verify normal canvas size before interpreting visuals.

### 3D Viewer Correction Alignment

- Status: tested; global automatic correction preload closed, high-confidence review import remains possible.
- Evidence:
  - `scripts/audit_3d_viewer_correction_alignment.py`
  - `analysis_outputs/3d_article_map/viewer_correction_alignment/viewer_correction_alignment.md`
  - `analysis_outputs/3d_article_map/viewer_correction_alignment/viewer_correction_alignment.json`
- Scope:
  - Aligned the corrected plain transcript's PDF-like lines against the 3D viewer's current OCR row model.
  - No key candidates, hashing, seed phrases, WIF checks, OCR extraction, or address checks were generated.
- Findings:
  - Corrected transcript lines: `147`.
  - Viewer OCR rows: `161`.
  - High-confidence line matches: `101`.
  - Usable but not silent-preload matches: `25`.
  - Weak matches: `13`.
  - Safe global preload: `False`.
  - Extra viewer rows include labels/artifacts such as `OVERDOSE`, `Salvador`, `Magazine`, `Bitcoin`, and several OCR debris rows.
- Conclusion:
  - The current 3D viewer line model is not clean enough for automatic whole-article correction import.
  - The exact corrected transcript remains the wording authority, but it should be applied after geometry selects a region or through a manual/high-confidence review workflow.
- Next test:
  - Do not spend puzzle-analysis time on silent viewer correction import. If improving the UI, add a reviewable high-confidence import helper.

### Page 76 Next-Target Chooser

- Status: tested; active as source-comparison priority list, closed as extraction.
- Evidence:
  - `scripts/audit_page76_next_target_chooser.py`
  - `analysis_outputs/source_audit/page76_next_target_chooser/page76_next_target_chooser.md`
  - `analysis_outputs/source_audit/page76_next_target_chooser/page76_next_target_chooser.json`
- Scope:
  - Ranked corrected page-76 corridor lines using existing independent evidence layers only.
  - Combined line-offset evidence, supported landing sequence, target convergence, p78 frame edges, and announcement/media corridor terms.
  - No key candidates, hashing, seed phrases, OCR extraction, WIF checks, or address checks were generated.
- Findings:
  - Strongest target: L32 / corridor 14 `Maybe because he's a shitcoiner at heart.`, score `32.75`.
  - Required paired target: L27 / corridor 9 `collateralized “Volcano Bonds” to pay off the IMF`, score `16.75`.
  - L25 `$1 billion in bitcoin — that he should sell` ranks third, score `10.75`.
  - L26-L29 remains the broad p78 source band, led by L26 `billions worth of future bitcoin earnings`, score `10.0`, and L29 `Novogratz in the tweet, figuring he could sell a`, score `7.5`.
- Conclusion:
  - Future source/physical/Canva comparisons should inspect O5/L32 first, G5/L27 second, then the L26-L29 band.
  - The ranking gives target priority, not an extraction unit.
- Next test:
  - Do not re-rank page-76 lines locally. Use this priority list only when a new source image or source-level instruction appears.

### Page 76 Priority Crop Pack

- Status: active as future source-comparison baseline; closed as extraction.
- Evidence:
  - `scripts/build_page76_priority_crop_pack.py`
  - `analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.md`
  - `analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json`
  - `analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg`
- Scope:
  - Built high-res crops for the prioritized page-76 targets using trusted O5/G5 boxes and the p78 reflected frame edge coordinates.
  - No key candidates, hashing, seed phrases, OCR extraction, WIF checks, or address checks were generated.
- Findings:
  - Crop set covers L32/O5, L27/G5, L25/should-sell, the L26-L29 p78 source band, and the full L25-L32 frame context.
  - The crop sheet is `1500 x 1892`.
  - The p78 reflected frame edges are drawn in cyan where they intersect each crop.
- Conclusion:
  - This is the reusable visual baseline for future source comparison.
  - It supplies no extraction unit.
- Next test:
  - If a new Canva/original-layout/physical image appears, compare against this crop pack first: O5/L32, G5/L27, then L26-L29. Require a named unit before key checks.

### Priority Crop Pack vs bitcoin4 Witness

- Status: tested; active as rough source-fidelity witness, closed as geometry/extraction upgrade.
- Evidence:
  - `scripts/audit_priority_crops_against_bitcoin4.py`
  - `analysis_outputs/source_audit/priority_crops_bitcoin4_comparison/priority_crops_bitcoin4_comparison.md`
  - `analysis_outputs/source_audit/priority_crops_bitcoin4_comparison/priority_crops_bitcoin4_comparison.json`
  - `analysis_outputs/source_audit/priority_crops_bitcoin4_comparison/priority_crops_bitcoin4_comparison_sheet.jpg`
- Scope:
  - Mapped the high-res page-76 priority crop pack into lower-quality `bitcoin4.pdf` coordinates using the prior p76 transform.
  - No key candidates, hashing, seed phrases, WIF checks, OCR extraction, or address checks were generated.
- Findings:
  - `shitcoiner at heart`, `Volcano Bonds`, `should sell`, and the broader `earnings / I tagged Mike / could sell` band remain visibly aligned in `bitcoin4`.
  - O5 orange coverage is stable between sources (`0.130581` high-res vs `0.133051` bitcoin4), which confirms the transform catches the same visual region.
  - The prior bitcoin4 geometry witness still stands: the source does not repair trusted G5 contact and is worse than the high-res scan for exact geometry.
- Conclusion:
  - `bitcoin4.pdf` is useful only as a rough visual witness that the selected regions are not accidental crop artifacts.
  - It does not supply a new extraction unit, a corrected registration, or a reason to derive keys.
- Next test:
  - Do not revisit `bitcoin4.pdf` unless a future clue explicitly says to compare sources/differences. Prioritize original Canva/source assets or physical scan/hold-to-light evidence.

### Page 76 All-Source Highlight Mirror Benchmark

- Status: tested; orientation support only, closed as raw selector.
- Evidence:
  - `scripts/audit_page76_all_source_highlight_mirror_benchmark.py`
  - `analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/page76_all_source_highlight_mirror_benchmark.md`
  - `analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/page76_all_source_highlight_mirror_benchmark.json`
  - `analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/page76_all_source_highlight_mirror_benchmark_sheet.jpg`
- Scope:
  - Applied the same raw horizontal mirror to every non-page-76 orange/grey highlight set, then measured overlap with verified page-76 orange/grey targets.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - p79 is the strongest raw source into page 76: `5` strong contacts, targets `G1 G2 O1 O2`, score `183.829`.
  - p77 also produces `2` strong mid-page contacts (`G1 O3`), which proves raw mirrored highlight boxes alone are too permissive.
  - p78 produces `1` strong contact (`O3`); p75 and p80 produce no meaningful contacts.
- Conclusion:
  - The benchmark supports p79/p78 as orientation/target evidence, but it also shows why a stricter rule is required.
  - Raw page-center highlight mirroring is not the final selector and does not define a word/letter/order unit.
- Next test:
  - Keep the p78/p79-to-page76 mirror evidence as orientation only. Move only on a new source/physical transform or an explicit clue that names exact extraction units.

### Page 76 Color-Swap Mirror Filter

- Status: tested; p79 orientation support only, closed as standalone selector.
- Evidence:
  - `scripts/audit_page76_color_swap_mirror_filter.py`
  - `analysis_outputs/source_audit/page76_color_swap_mirror_filter/page76_color_swap_mirror_filter.md`
  - `analysis_outputs/source_audit/page76_color_swap_mirror_filter/page76_color_swap_mirror_filter.json`
  - `analysis_outputs/source_audit/page76_color_swap_mirror_filter/page76_color_swap_mirror_filter_overlay.jpg`
- Scope:
  - Filtered the all-source page-76 mirror contacts to color swaps only: orange source -> grey target and grey source -> orange target.
  - Required both swap directions on the same source page before treating the page as a candidate.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Only p79 has bidirectional color-swap contacts.
  - p77's one-way `grey->orange` contact is removed by the stricter bidirectional rule.
  - The p79 color-swap set lands on upper page-76 targets `G1 G2 O1 O2`, not the lower `Volcano Bonds` / `shitcoiner at heart` corridor.
  - The only instruction-term hits are `take` and `right` inside the printed source sentence `That's right, Bitcoin will take`, not procedural commands.
- Conclusion:
  - Color-swap mirroring is a good noise reducer and supports p79 as an orientation/concept layer.
  - It does not name an extraction unit or justify key derivation.
- Next test:
  - Reuse this only if a future clue explicitly points to color swapping, the upper energy/war contrast, or p79 as source page. Otherwise keep priority on source/physical registration and lower-corridor unit selection.

### Color-Swap Take-Right Rule Audit

- Status: tested; closed as selector.
- Evidence:
  - `scripts/audit_color_swap_take_right_rule.py`
  - `analysis_outputs/source_audit/color_swap_take_right_rule/color_swap_take_right_rule.md`
  - `analysis_outputs/source_audit/color_swap_take_right_rule/color_swap_take_right_rule.json`
  - `analysis_outputs/source_audit/color_swap_take_right_rule/color_swap_take_right_rule_overlay.jpg`
- Scope:
  - Treated `right` and `take` from the p79 source phrase `That's right, Bitcoin will take` as a possible literal instruction.
  - Extracted right-edge words, right halves, words to the right of intersections, and words to the right of reflected boxes for the five p79 color-swap contacts.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Right-edge stream: `money money RRECECy to Biteoiny`.
  - Right-of-intersection stream: `of dumb post-1971 | flat money | RRECECy (and loyears | Get some bitcoin. | It's the freaking`.
  - Right-of-reflected-box stream: `of dumb post-1971 | flat money | Peter Schiff miss | Get some bitcoin. | freaking UTXO`.
  - Instruction-term hits: none.
- Conclusion:
  - Literal `take right` extraction from the p79 color-swap contacts produces ordinary upper-page prose and OCR artifacts, not a procedural selector.
  - The upper p79 color-swap cluster remains orientation/concept evidence only.
- Next test:
  - Return priority to lower-corridor source/physical registration and exact unit selection around `Volcano Bonds` / `shitcoiner at heart`.

### Repaired R-K-Y Signature Rarity

- Status: tested; closed as standalone font/style selector.
- Evidence:
  - `scripts/audit_repaired_rky_signature_rarity.py`
  - `analysis_outputs/docm_format_sources/repaired_rky_signature_rarity/repaired_rky_signature_rarity.md`
  - `analysis_outputs/docm_format_sources/repaired_rky_signature_rarity/repaired_rky_signature_rarity.json`
  - `analysis_outputs/docm_format_sources/repaired_rky_signature_rarity/repaired_rky_signature_rarity_sheet.jpg`
- Scope:
  - Tested whether the repaired lower-corridor `R-K-Y` style code is intrinsically rare in the DOCM style stream.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - The repaired exact-edge trio remains `should sell | Volcano Bonds | shitcoiner at heart` with styles `R-K-Y`.
  - Adjacent `R-K-Y` appears only once across pages 75-79, and that one instance is on page 75, not page 76.
  - Non-adjacent/skipped `R-K-Y` is common: `187` ordered triples across pages 75-79, including `60` on page 76.
- Conclusion:
  - `R-K-Y` by itself is not a font cipher or selector.
  - Its value is as a compact benchmark for the repaired p78-frame geometry, only when the geometry also selects the exact text trio and the M3/O5/G5 tri-contact.
- Next test:
  - Compare any future higher-resolution Canva/original-layout/physical source against the exact-edge trio and tri-contact signature before attempting extraction.

### R-K-Y Control Window Contrast

- Status: tested; page-75 adjacent R-K-Y closed as instruction source.
- Evidence:
  - `scripts/audit_rky_control_window_contrast.py`
  - `analysis_outputs/docm_format_sources/rky_control_window_contrast/rky_control_window_contrast.md`
  - `analysis_outputs/docm_format_sources/rky_control_window_contrast/rky_control_window_contrast.json`
  - `analysis_outputs/docm_format_sources/rky_control_window_contrast/rky_control_window_contrast_sheet.jpg`
- Scope:
  - Compared the only adjacent `R-K-Y` style window with the repaired lower-corridor `R-K-Y` geometry signature.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Adjacent page-75 `R-K-Y` text is `epithet...mEthereum lab` / `Don't fall for shitcoinery` / `Keep your dignity`.
  - It contains article-level commands (`Don't`, `Keep`) but no extraction terms and no page-76 target hits.
  - The repaired page-76/p78-frame `R-K-Y` text hits `G5` and `O5` through `Volcano Bonds` and `shitcoiner at heart`, but also has no extraction terms.
- Conclusion:
  - The page-75 adjacent `R-K-Y` is best treated as a control/decoy, not a hidden instruction.
  - The lower-corridor `R-K-Y` only remains active as geometry-selected target evidence.
- Next test:
  - Do not follow the page-75 adjacent window unless a new clue explicitly points to `Don't fall` / `Keep your dignity`. Keep priority on source/physical validation and unit-selection clues for `G5/O5`.

### Missing-Rule Frontier

- Status: synthesized; source/physical/original-layout validation is highest-value open path.
- Evidence:
  - `scripts/audit_missing_rule_frontier.py`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Reviewed the current open/closed frontier after lower-corridor, R-K-Y, and color-swap checks.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Confirmed target surface remains page 76 lower corridor: O5 `shitcoiner at heart`, G5 `Volcano Bonds`, and the El Salvador/IMF/Bukele/Mike/trust corridor.
  - Local text/format permutations are closed for the current scan unless a new clue names a specific extraction unit.
  - Source/physical registration remains the highest-value open frontier because the current scan has a stable benchmark but no independent physical/source confirmation.
- Conclusion:
  - The missing piece is not another local encoding attempt; it is a source-level or clue-level rule that names what to extract from the already-located target.
- Next test:
  - Compare any future physical scan/photo, original Canva export, or layout source against the priority crop pack and repaired exact-edge benchmark before trying extraction again.

### External Instruction-Term Frontier

- Status: tested; no new raw external selector found.
- Evidence:
  - `scripts/audit_external_instruction_term_frontier.py`
  - `analysis_outputs/external_clues/external_instruction_term_frontier/external_instruction_term_frontier.md`
  - `analysis_outputs/external_clues/external_instruction_term_frontier/external_instruction_term_frontier.json`
- Scope:
  - Scanned archived external/provenance files for procedural extraction terms near active target terms.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `23` files scanned; `21` had procedural or target-term hits.
  - Only `2` raw/original-ish non-internal co-occurrence windows were found.
  - The only actionable raw-ish one is the Canva source-inspection page-76 note, which supports page 76 as target and mirrored art as registration/orientation evidence.
  - The raw thread `shitcoiner`/mirror co-occurrence is from an unrelated related-thread card, not the 2023 puzzle announcement.
- Conclusion:
  - No raw external/provenance wording gives a missing unit such as word, letter, line, first, last, or take for G5/O5.
  - External clue material remains provenance/source-fidelity guidance only.
- Next test:
  - Use future source material to validate zero/#0 hotspots, p79 pill geometry, page-76 priority crops, and the repaired p78-frame exact-edge benchmark.

### Source Validation Gate

- Status: built; use before any future extraction from new source material.
- Evidence:
  - `scripts/build_source_validation_gate.py`
  - `analysis_outputs/source_audit/source_validation_gate/source_validation_gate.md`
  - `analysis_outputs/source_audit/source_validation_gate/source_validation_gate.json`
  - `analysis_outputs/source_audit/source_validation_gate/source_validation_gate_sheet.jpg`
- Scope:
  - Consolidated page-76 priority crops, zero/#0 crops, p79 pill geometry, p78 tri-contact, and repaired exact-edge stability into one acceptance gate.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - New source material must pass source quality first: native/original-layout export, source image, or physical scan/photo.
  - Connector thumbnails, OCR PDF coordinates, low-res screenshots, and derived analysis images remain witnesses only.
  - Key checks are blocked until the new source or clue names the extraction unit/order.
- Conclusion:
  - This is now the standard intake path for a physical scan, original Canva export, or layout source.
- Next test:
  - When a new source arrives, run the gate in order: source quality, page-76 priority crops, zero/#0 hotspots, p79 pill geometry, repaired p78 frame, then extraction permission.

### Source Gate Current Baseline

- Status: dry-run complete; current scan accepted as baseline, extraction still blocked.
- Evidence:
  - `scripts/audit_source_gate_current_baseline.py`
  - `analysis_outputs/source_audit/source_gate_current_baseline/source_gate_current_baseline.md`
  - `analysis_outputs/source_audit/source_gate_current_baseline/source_gate_current_baseline.json`
- Scope:
  - Ran the source-validation gate against the current canonical `magazine.pdf`.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `magazine.pdf` passes baseline source quality and is byte-identical to the desktop copy.
  - Page-76 priority crops, zero/#0 hotspots, p79 pill geometry, and the repaired p78 exact-edge signature all pass as baseline evidence.
  - Extraction permission is still blocked because no current-source or raw external clue names the extraction unit/order.
- Conclusion:
  - The current scan is the correct baseline, but not a complete solution source.
- Next test:
  - Use this dry-run as the expected baseline result for any future physical/original-layout/source material.

### Local Screenshots Source Gate

- Status: tested; no screenshot promoted.
- Evidence:
  - `scripts/audit_local_screenshots_against_source_gate.py`
  - `analysis_outputs/source_audit/local_screenshot_source_gate/local_screenshot_source_gate.md`
  - `analysis_outputs/source_audit/local_screenshot_source_gate/local_screenshot_source_gate.json`
  - `analysis_outputs/source_audit/local_screenshot_source_gate/local_screenshot_source_gate_sheet.jpg`
- Scope:
  - Applied the source-validation gate to the six Desktop screenshots already in the local inventory.
  - No OCR, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Promoted screenshots: `0`.
  - All screenshots fail source quality and benchmark visibility.
  - They remain unrelated, media-context, or solver/reference artifacts, not source geometry.
- Conclusion:
  - No existing local screenshot closes the source gap.
- Next test:
  - Do not revisit local screenshots unless a new file appears; continue with physical/original-layout/source asset acquisition or style-only comparison PDFs.

### Comparison PDFs Source Gate

- Status: tested; no comparison PDF promoted for Issue 24 extraction geometry.
- Evidence:
  - `scripts/audit_comparison_pdfs_against_source_gate.py`
  - `analysis_outputs/source_audit/comparison_pdf_source_gate/comparison_pdf_source_gate.md`
  - `analysis_outputs/source_audit/comparison_pdf_source_gate/comparison_pdf_source_gate.json`
- Scope:
  - Applied the source-validation gate to `bitcoin3.pdf`, `Issue_26.pdf`, `Issue_27.pdf`, and `bitcoin4.pdf`.
  - No OCR, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Promoted for Issue 24 extraction geometry: `0`.
  - `bitcoin3.pdf`, `Issue_26.pdf`, and `Issue_27.pdf` are valid style-only Max/OVERDOSE comparison articles, not Issue 24 geometry sources.
  - `bitcoin4.pdf` remains a low-res Issue 24 source-fidelity witness only; it preserves the same broad regions but does not repair the p78-frame/G5/O5 benchmark.
  - Existing body-highlighter comparison still shows Issue 24 as the strongest sustained highlighter grammar among tested articles.
- Conclusion:
  - Comparison PDFs must not be used to select key material or change page-76 geometry under the current clue set.
- Next test:
  - Use comparison PDFs only for style uniqueness questions, especially Typeka/highlighter/pill grammar; extraction remains blocked until a new source/clue names the unit/order.

### Issue 27 Body-Highlighter Control

- Status: tested; Issue 27 does not reproduce the Issue 24 body-highlight grammar.
- Evidence:
  - `scripts/audit_body_highlighter_grammar.py`
  - `analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.md`
  - `analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.json`
  - `analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar_sheet.jpg`
- Scope:
  - Added the rendered `Issue_27.pdf` pages to the strict body-text orange/dark line-band comparison.
  - No OCR, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `issue24_toxic_af`: `28` orange bands, `14` dark bands, sustained pages `[3, 4, 6, 7]`, max score `19`.
  - `issue27`: `2` orange bands, `3` dark bands, sustained pages `[]`, max score `3`.
  - `bitcoin3` and `issue26` also remain weaker controls than Issue 24 under this stricter body-highlight metric.
- Conclusion:
  - Issue 24's sustained body-text orange/grey highlight grammar remains puzzle-relevant and not explained away as generic OVERDOSE house style.
  - This is still style evidence only; it does not name the missing extraction unit/order.
- Next test:
  - Keep body highlights active only where they interact with the page-76 mirror corridor; continue blocking key checks until a source/clue names the unit.

### XX/Wire Similarity Overfit

- Status: tested; forced two-point alignment does not unlock extraction.
- Evidence:
  - `scripts/audit_xx_wire_similarity_overfit.py`
  - `analysis_outputs/source_audit/xx_wire_similarity_overfit/xx_wire_similarity_overfit.md`
  - `analysis_outputs/source_audit/xx_wire_similarity_overfit/xx_wire_similarity_overfit.json`
  - `analysis_outputs/source_audit/xx_wire_similarity_overfit/xx_wire_similarity_overfit_sheet.jpg`
- Scope:
  - Forced the two p78 X marks onto the two p79 barbed-wire knots using proper and reflected similarity transforms.
  - No OCR, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - All forced fits require scale about `0.6002`; rotations vary by correspondence/reflection.
  - The X-to-wire alignment is tautological because the transform is fit from those exact two points.
  - The non-X p78 graphic objects only land near the same p79 wire span; they do not hit page-76 target text, an ordering object, or an instruction.
- Conclusion:
  - The Canva `XX`/wire claim remains orientation/source-registration evidence, not a solved selector under the current scan.
- Next test:
  - Reopen this branch only with higher-resolution Canva/original-layout/physical evidence or an explicit rule naming the intended graphic object pair.

### Typography Source Provenance

- Status: refreshed; Typeka is confirmed only in the local DOCM witness, not as extractable PDF font metadata.
- Evidence:
  - `scripts/analyze_typography_source_provenance.py`
  - `analysis_outputs/source_audit/typography_source_provenance.md`
  - `analysis_outputs/source_audit/typography_source_provenance.json`
- Scope:
  - Checked `magazine.pdf`, desktop `magazine.pdf`, `Issue_26.pdf`, `Issue_27.pdf`, `bitcoin3.pdf`, `bitcoin4.pdf`, `Article with Fonts.docm`, and `BOLD.docm`.
  - No OCR-derived selectors, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `magazine.pdf` exposes only Helvetica OCR/text-layer font resources, not visible printed Typeka.
  - `Issue_26.pdf`, `Issue_27.pdf`, `bitcoin3.pdf`, and `bitcoin4.pdf` expose no usable embedded Typeka font evidence.
  - `Article with Fonts.docm` records `Typeka` `6568` chars and `Typeka Mix` `883` chars, making it the only local Typeka/font-state witness.
  - `BOLD.docm` remains a generated/macro witness, not an original typography source.
- Conclusion:
  - Typeka states remain useful labels after geometry selects text, but they are not independently extractable from the PDFs and cannot be used as a standalone selector.
- Next test:
  - Only reopen Typeka/font-state extraction if a source clue names a font state, or if original layout files / higher-fidelity source material expose true font-layer metadata.

### Active Path Readiness Gate

- Status: refreshed; no local path is ready for extraction.
- Evidence:
  - `scripts/audit_active_path_readiness_gate.py`
  - `analysis_outputs/source_audit/active_path_readiness_gate/active_path_readiness_gate.md`
  - `analysis_outputs/source_audit/active_path_readiness_gate/active_path_readiness_gate.json`
- Scope:
  - Rechecked active paths against four required ingredients: source layer, target region, ordering, and extraction unit.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Ready paths: `0`.
  - Blocked only on extraction unit: `1`.
  - Strongest targets remain `O5` `shitcoiner at heart`, `G5` `Volcano Bonds`, and the lower El Salvador/IMF corridor.
  - Closest local path is the repaired p78 exact-edge trio `should sell | Volcano Bonds | shitcoiner at heart`; it has source, target, and order but lacks a source-backed extraction unit.
- Conclusion:
  - The remaining blocker is precise and narrow: a source/clue must say what unit to read.
- Next test:
  - Do not generate key candidates. Continue only with better source/physical/original-layout evidence or a new explicit human rule that names source layer, target, order, and unit.

### Exact Trio Heart-Unit Rule

- Status: tested; literal `heart` extraction does not solve the missing unit.
- Evidence:
  - `scripts/audit_exact_trio_heart_unit_rule.py`
  - `analysis_outputs/source_audit/exact_trio_heart_unit_rule/exact_trio_heart_unit_rule.md`
  - `analysis_outputs/source_audit/exact_trio_heart_unit_rule/exact_trio_heart_unit_rule.json`
- Scope:
  - Treated `heart` in the repaired exact-edge trio `should sell | Volcano Bonds | shitcoiner at heart` as a literal middle-letter/middle-word unit.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Middle-word and middle-letter streams produce fragments like `ldnoe`, `ldsnobner`, `uldsanobiner`, and `ou el c n co at a`; no instruction hits.
  - The word `shitcoiner` can yield right-biased center `coin`, but left-biased center is `tcoi`.
- Conclusion:
  - `coin` is thematic support only because it depends on an arbitrary center bias.
  - Literal heart extraction from the exact trio remains closed as a selector.
- Next test:
  - Keep the repaired trio as registration evidence; continue looking for a source-backed unit rather than deriving local key material.

### Exact Trio Bond-Boundary Rule

- Status: tested; literal `Bonds` boundary extraction does not solve the missing unit.
- Evidence:
  - `scripts/audit_exact_trio_bond_boundary_rule.py`
  - `analysis_outputs/source_audit/exact_trio_bond_boundary_rule/exact_trio_bond_boundary_rule.md`
  - `analysis_outputs/source_audit/exact_trio_bond_boundary_rule/exact_trio_bond_boundary_rule.json`
- Scope:
  - Treated `Bonds` in the repaired exact-edge trio `should sell | Volcano Bonds | shitcoiner at heart` as a word/phrase-boundary unit.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Word-boundary streams are `dsobrath`, `thraobds`, `slvsstat`, and `atstvssl`.
  - Phrase-boundary streams are `lvss`, `sslv`, `sobr`, and `brso`.
  - None produce instruction hits or readable selector text.
- Conclusion:
  - Literal bond/boundary extraction from the exact trio is closed as a selector.
- Next test:
  - Keep the exact trio as registration evidence; continue only with source-backed unit clues or better source/original-layout evidence.

### Exact Trio Sell-Removal Rule

- Status: tested; literal `sell` / remove extraction does not solve the missing unit.
- Evidence:
  - `scripts/audit_exact_trio_sell_removal_rule.py`
  - `analysis_outputs/source_audit/exact_trio_sell_removal_rule/exact_trio_sell_removal_rule.md`
  - `analysis_outputs/source_audit/exact_trio_sell_removal_rule/exact_trio_sell_removal_rule.json`
- Scope:
  - Treated `sell` in the repaired exact-edge trio `should sell | Volcano Bonds | shitcoiner at heart` as a remove/sell-off instruction.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Removing `Volcano Bonds` exposes `sell shitcoiner` with boundary pairs `ls` / `sr`.
  - Removing `sell` exposes `should Volcano` with boundary pairs `dv` / `so`.
  - Removing `should sell` exposes `Bonds shitcoiner` with boundary pairs `ss` / `br`.
  - Raw hits are only unchanged printed words (`heart`, `sell`); actionable compact/initial/last/boundary streams have no instruction hits.
- Conclusion:
  - Literal sell/remove extraction from the exact trio is closed as a selector.
- Next test:
  - Keep the exact trio as registration evidence; continue only with a source-backed unit clue or better source/original-layout evidence.

### Canva Live Source-Fidelity Recheck

- Status: rechecked; still provenance/orientation evidence only.
- Evidence:
  - Canva design `PRIVATE_CONTRIBUTOR`
  - `analysis_outputs/external_clues/canva_live_recheck/canva_live_recheck.md`
  - `analysis_outputs/external_clues/canva_live_recheck/canva_live_recheck.json`
- Scope:
  - Checked whether the live Canva design exposes hidden notes, more pages, higher-resolution source images, asset IDs, or new clue wording.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Design title is `PRIVATE_ANNOTATION_OMITTED`.
  - Canva reports one page, revision `16`, and only a `668x376` thumbnail.
  - Presenter notes have no hidden instruction text.
  - Connector text confirms the known source-fidelity clues: pills do not line up, `diff pic`, OCR missed `#0`, and `XX`/barbed-wire plus `SHIT`/`FUCK ALL SHITCOINS` orientation.
  - No original embedded source asset IDs were exposed.
- Conclusion:
  - The Canva note confirms the source-fidelity/orientation concern but cannot be used for exact geometry.
- Next test:
  - Reopen only if a higher-resolution Canva export, original embedded image, source-layout file, or physical scan/photo becomes available.
  - The refreshed missing-rule frontier now has `188` closed/deferred branches and still ranks source/physical/original-layout validation as the highest-value next move.

### `otrobip.txt` Recovery Audit

- Status: searched; missing locally.
- Evidence:
  - `scripts/audit_otrobip_recovery.py`
  - `analysis_outputs/docm_format_sources/otrobip_recovery_audit/otrobip_recovery_audit.md`
  - `analysis_outputs/docm_format_sources/otrobip_recovery_audit/otrobip_recovery_audit.json`
- Scope:
  - Searched for the missing `BOLD.docm` macro word list: `private_inputs\OneDrive\Desktop\Alles\TOXIC_AF\BIP39\otrobip.txt`.
  - Search roots were `private_inputs/Desktop`, `private_inputs/Documents`, and `private_inputs/Downloads`.
  - No BIP39 extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Files searched: `62703`.
  - Exact `otrobip.txt` matches: `0`.
  - `otrobip`-like matches: `0`.
  - `bip39*.txt` matches: `0`.
  - Relevant non-skipped `BIP39`, `TOXIC_AF`, or `Alles` directories: `0`.
- Conclusion:
  - The macro-referenced word list is not locally recovered.
  - `BOLD.docm` remains a generated working artifact unless the missing folder/file appears.
- Next test:
  - Do not use `BOLD.docm` for extraction unless `otrobip.txt` or the original `TOXIC_AF/BIP39` source folder is supplied.
  - Refreshed missing-rule frontier count: `189` closed/deferred branches; highest-value next move remains source/physical/original-layout validation.

### Text By Sentences Unit Witness

- Status: audited; useful as a working sentence-count layer, not as source-backed extraction.
- Evidence:
  - `scripts/audit_related_word_artifacts.py`
  - `scripts/audit_text_by_sentences_unit_witness.py`
  - `analysis_outputs/docm_format_sources/related_word_artifacts/related_word_artifacts.md`
  - `analysis_outputs/docm_format_sources/text_by_sentences_unit_witness/text_by_sentences_unit_witness.md`
- Scope:
  - Checked only `private_inputs/Desktop/Text_by_sentences.docx` and `private_inputs/Documents/macro data.docx`.
  - No BIP39 extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `macro data.docx` is unrelated macroeconomics content.
  - `Text_by_sentences.docx` is article-related and has `87` sentence rows with markers `(15)`, `(35)`, `(50)`, `(70)`, `(85)`.
  - Page-76 corridor maps to sentence rows `43`-`49`.
  - The active terms map cleanly to rows `43`-`48`, but `Volcano Bonds` is missing from this witness.
  - Sentence streams such as `hhiiim`, `twitter dip leeches it guy heart`, pair `45 48`, and gap `3` have no instruction hits.
- Conclusion:
  - Sentence units are now documented as a possible working layer, but `Text_by_sentences.docx` is not source-faithful enough to select key material.
- Next test:
  - Only use sentence units if a later external/source clue explicitly names sentences; rebuild from corrected canonical article text, not this imperfect witness.
  - Refreshed missing-rule frontier count: `190` closed/deferred branches; highest-value next move remains source/physical/original-layout validation.

### Canonical Sentence Unit Rebuild

- Status: rebuilt; validation layer only.
- Evidence:
  - `scripts/audit_canonical_sentence_unit_rebuild.py`
  - `analysis_outputs/plain_text_transcript/canonical_sentence_unit_rebuild/canonical_sentence_unit_rebuild.md`
  - `analysis_outputs/plain_text_transcript/canonical_sentence_unit_rebuild/canonical_sentence_unit_rebuild.json`
- Scope:
  - Rebuilt sentence rows from the corrected canonical article text after `Text_by_sentences.docx` was found to omit `Volcano Bonds`.
  - No BIP39 extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Corrected canonical text produces `87` sentence rows.
  - Page-76 corridor is sentence rows `43`-`49`.
  - `Volcano Bonds` is restored at sentence row `45`.
  - `shitcoiner at heart` is sentence row `48`; G5/O5 sentence pair is `45 48`, gap `3`.
  - Sentence streams (`hhiiim`, `twitter dip leeches it guy heart`, `hr hp is it iy mt`, `ngjts`) have no instruction hits.
  - Text-witness marker rows `(15)`, `(35)`, `(50)`, `(70)`, `(85)` land on ordinary body text against canonical segmentation.
- Conclusion:
  - Sentence units are documented but do not currently supply an extraction rule.
- Next test:
  - Use sentence rows only if a future source/clue explicitly says to read by sentence; otherwise keep source/physical/original-layout validation as the priority.
  - Refreshed missing-rule frontier count: `191` closed/deferred branches; highest-value next move remains source/physical/original-layout validation.

### Sentence-Line Highlight Bridge

- Status: tested; validation/locator evidence only.
- Evidence:
  - `scripts/audit_sentence_line_highlight_bridge.py`
  - `analysis_outputs/plain_text_transcript/sentence_line_highlight_bridge/sentence_line_highlight_bridge.md`
  - `analysis_outputs/plain_text_transcript/sentence_line_highlight_bridge/sentence_line_highlight_bridge.json`
- Scope:
  - Bridged corrected canonical sentence rows to page-76 visual line/highlight records.
  - No BIP39 extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Sentence `45` carries the Bukele/volcanoes/$1 billion/Volcano Bonds/IMF source sentence and spans page lines `23-28`.
  - Sentence `48` carries `shitcoiner at heart` and maps to page line `32`.
  - G5/O5 pair is sentence `45 -> 48`, page line `27 -> 32`, corridor `9 -> 14`, with gaps `3 / 5 / 5`.
  - Visual lines `28` and `31` cross sentence boundaries, so sentence and printed-line units do not become a single clean extraction grid.
  - Sentence-line/highlight streams have no instruction hits.
- Conclusion:
  - This strengthens G5/O5 as a locator, but it does not supply the missing extraction unit.
- Next test:
  - Reopen only if a future source/clue explicitly names sentence, line, gap, first/last, or another unit.
  - Refreshed missing-rule frontier count: `192` closed/deferred branches; highest-value next move remains source/physical/original-layout validation.

### G5/O5 Gap Rarity

- Status: tested; locator evidence only.
- Evidence:
  - `scripts/audit_g5_o5_gap_rarity.py`
  - `analysis_outputs/plain_text_transcript/g5_o5_gap_rarity/g5_o5_gap_rarity.md`
  - `analysis_outputs/plain_text_transcript/g5_o5_gap_rarity/g5_o5_gap_rarity.json`
- Scope:
  - Compared the G5/O5 `3/5/5` sentence/page-line/corridor gap against nearby page-76 corridor anchors.
  - No BIP39 extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Nearby anchor count: `10`; ordered pair count: `45`.
  - G5/O5 remains `Volcano Bonds -> shitcoiner at heart`, gap `3/5/5`.
  - The same exact gap also appears for `IMF loan -> shitcoiner at heart` because `IMF loan` shares the same printed line/coordinate as `Volcano Bonds`.
  - Within grey-to-orange pairs, `Volcano Bonds -> shitcoiner at heart` is the only `3/5/5` case.
  - Gap streams and pair-label streams have no instruction hits.
- Conclusion:
  - `3/5/5` is a stable lower-corridor locator tied to line `27 -> 32`, but not a source-backed extraction rule.
- Next test:
  - Reopen gap arithmetic only if a future clue/source explicitly names gap, line, sentence, count, or a related unit.
  - Refreshed missing-rule frontier count: `193` closed/deferred branches; highest-value next move remains source/physical/original-layout validation.

### Current Scan / 3D Image Consistency

- Status: tested; 3D upright images downgraded to navigation-only geometry.
- Evidence:
  - `scripts/audit_current_scan_cache_consistency.py`
  - `analysis_outputs/source_audit/current_scan_cache_consistency/current_scan_cache_consistency.md`
  - `analysis_outputs/source_audit/current_scan_cache_consistency/current_scan_cache_consistency.json`
  - `analysis_outputs/source_audit/current_scan_cache_consistency/page76_source_vs_3d_sheet.jpg`
- Scope:
  - Checked whether cached page images and 3D viewer upright images match the supplied best scan at `private_inputs/Desktop/magazine.pdf`.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Desktop and project `magazine.pdf` are byte-identical: md5 `2c454d800cf2971c1f86fd016f64b7a0`.
  - `analysis_outputs/source_images/magazine_page_75..80.jpg` visually match the embedded images extracted from the current Desktop PDF.
  - `analysis_outputs/3d_article_map/page_75..80_upright.jpg` do not visually match the current Desktop PDF at geometry-safe tolerance.
  - The page-76 3D upright mismatch is RMS `76.379324`, far above the source-cache JPEG-resave RMS `1.163935`.
- Conclusion:
  - The source-image cache is current for the supplied best scan.
  - The 3D viewer remains useful for navigation/corrections, but its upright image layer should not be used as exact source geometry.
- Next test:
  - Rebuild or validate any exact page-76 crop/geometry against `analysis_outputs/source_images` or freshly extracted `magazine.pdf` images before using it for visual extraction.
  - Refreshed missing-rule frontier count: `194` closed/deferred branches; highest-value next move now explicitly excludes the 3D upright layer as exact geometry.

### Priority Crop Pack Source Fidelity

- Status: corrected; crop pack is source-faithful after orientation transform.
- Evidence:
  - `scripts/audit_priority_crop_pack_source_fidelity.py`
  - `analysis_outputs/source_audit/priority_crop_pack_source_fidelity/priority_crop_pack_source_fidelity.md`
  - `analysis_outputs/source_audit/priority_crop_pack_source_fidelity/priority_crop_pack_source_fidelity.json`
  - `analysis_outputs/source_audit/priority_crop_pack_source_fidelity/priority_crop_pack_source_fidelity_sheet.jpg`
- Scope:
  - Compared the existing page-76 priority crop pack against the current source scan after the 3D upright image layer failed source-fidelity checks.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Existing crop-pack source was `analysis_outputs/3d_article_map/page_76_upright.jpg`.
  - Current source image is `analysis_outputs/source_images/magazine_page_76.jpg`.
  - Correction: the source image is native upside-down PDF orientation, while the crop pack uses readable/upright orientation.
  - After rotating the source image 180 degrees, all five priority crops match at JPEG-resave tolerance.
  - Corrected raw RMS range is `1.132865` to `2.070533`.
  - Replaced the old warning banner in `page76_priority_crop_pack.md` with an orientation note.
- Conclusion:
  - Existing page-76 priority crop coordinates remain valid for readable/upright geometry.
  - Rotate `source_images` or fresh `magazine.pdf` extraction 180 degrees before comparing to those coordinates.
- Next test:
  - Keep O5/G5/frame contacts active as source-scan geometry, with orientation handled explicitly.
  - Refreshed missing-rule frontier count: `195` closed/deferred branches; highest-value next move uses readable/upright 3D crop geometry or source/PDF extraction rotated 180 degrees.

### Current Scan Orientation Correction

- Status: corrected; 3D upright layer restored as geometry-faithful.
- Evidence:
  - `scripts/audit_current_scan_cache_consistency.py`
  - `analysis_outputs/source_audit/current_scan_cache_consistency/current_scan_cache_consistency.md`
  - `analysis_outputs/source_audit/current_scan_cache_consistency/current_scan_cache_consistency.json`
- Findings:
  - Source/PDF page images are native upside-down orientation.
  - 3D viewer page images are the same scan after `rotate180`.
  - After `rotate180`, pages 75-80 match at RMS `1.025751` to `1.273871`.
- Conclusion:
  - The previous "3D not geometry-trustworthy" conclusion is superseded.
  - The valid rule is: compare like orientation before judging geometry fidelity.

### Upright / Native Coordinate Bridge

- Status: built; orientation bookkeeping layer.
- Evidence:
  - `scripts/audit_upright_native_coordinate_bridge.py`
  - `analysis_outputs/source_audit/upright_native_coordinate_bridge/upright_native_coordinate_bridge.md`
  - `analysis_outputs/source_audit/upright_native_coordinate_bridge/upright_native_coordinate_bridge.json`
  - `analysis_outputs/source_audit/upright_native_coordinate_bridge/upright_native_coordinate_bridge_sheet.jpg`
- Scope:
  - Converted active page-76 O5/G5/frame benchmark boxes between readable/upright coordinates and native PDF/source coordinates.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Transform is `rotate180` on image size `2544x3264`.
  - `frame`: upright `[1234,2398,2250,2950]` -> native `[294,314,1310,866]`.
  - `should sell`: upright `[1201,2393,1439,2434]` -> native `[1105,830,1343,871]`.
  - `G5 Volcano Bonds`: upright `[795,2544,1196,2592]` -> native `[1348,672,1749,720]`.
  - `O5 shitcoiner at heart`: upright `[1040,2932,1661,2982]` -> native `[883,282,1504,332]`.
- Conclusion:
  - The O5/G5/frame corridor is now explicitly mapped in both coordinate systems.
  - This prevents future false source-fidelity failures caused by comparing unlike orientations.
- Next test:
  - Use this bridge when comparing physical/source images or when rebuilding p78/frame contacts from native PDF extraction.
  - Refreshed missing-rule frontier count remains `195`; no new extraction unit was introduced.

### P78 Frame Source / Native Bridge

- Status: built; p78-to-p76 geometry chain explicit.
- Evidence:
  - `scripts/audit_p78_frame_source_native_bridge.py`
  - `analysis_outputs/source_audit/p78_frame_source_native_bridge/p78_frame_source_native_bridge.md`
  - `analysis_outputs/source_audit/p78_frame_source_native_bridge/p78_frame_source_native_bridge.json`
  - `analysis_outputs/source_audit/p78_frame_source_native_bridge/p78_frame_source_native_bridge_sheet.jpg`
- Scope:
  - Reconstructed the p78 source frame behind the active reflected p78 frame on page 76.
  - Converted current and repaired frame boxes across p78/p76 and readable/native coordinate systems.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Transform chain is p78 upright source box --horizontal flip--> p76 upright reflected box, then `rotate180` for native source/PDF coordinates.
  - Current frame: p78 upright `[294,2398,1310,2950]` -> p76 upright `[1234,2398,2250,2950]`.
  - dx `-38` repaired frame: p78 upright `[332,2398,1348,2950]` -> p76 upright `[1196,2398,2212,2950]`.
  - dx `-40` repaired frame: p78 upright `[334,2398,1350,2950]` -> p76 upright `[1194,2398,2210,2950]`.
  - Native boxes are recorded for all three frames.
- Conclusion:
  - The p78-frame-to-p76-lower-corridor benchmark is coherent across source page, target page, and orientation systems.
  - This is still source-registration evidence only; it names no extraction unit.
- Next test:
  - Use this bridge for future physical/original-layout comparison against the p78 frame and O5/G5 lower corridor.

### P78 Frame Source-Side Fit

- Status: tested; dx repair is target-side registration, not a better p78 source box.
- Evidence:
  - `scripts/audit_p78_frame_source_side_fit.py`
  - `analysis_outputs/source_audit/p78_frame_source_side_fit/p78_frame_source_side_fit.md`
  - `analysis_outputs/source_audit/p78_frame_source_side_fit/p78_frame_source_side_fit.json`
  - `analysis_outputs/source_audit/p78_frame_source_side_fit/p78_frame_source_side_fit_sheet.jpg`
- Scope:
  - Compared current and dx `-38/-40` repaired p78 frames against the actual p78 brush/pull-quote graphic mask.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Detected p78 graphic box: `[294,2398,1310,2950]`.
  - Current p78 frame captures `1.0` of the detected graphic mask.
  - dx `-38` captures `0.991782` and leaves `1919` mask pixels outside.
  - dx `-40` captures `0.991161` and leaves `2064` mask pixels outside.
- Conclusion:
  - The p78 source object itself favors the current detected box.
  - The dx `-38/-40` repair should be treated as a p76 target-side registration adjustment for G5/M3/O5, not as an improved p78 source-object bounding box.
- Next test:
  - Keep current p78 box for source-object detection and dx `-38/-40` for p76 registration validation.
  - Refreshed missing-rule frontier count: `196` closed/deferred branches.

### P78 Repair Lost Source Pixels

- Status: tested; loss is a narrow left-edge graphic strip.
- Evidence:
  - `scripts/audit_p78_repair_lost_source_pixels.py`
  - `analysis_outputs/source_audit/p78_repair_lost_source_pixels/p78_repair_lost_source_pixels.md`
  - `analysis_outputs/source_audit/p78_repair_lost_source_pixels/p78_repair_lost_source_pixels.json`
  - `analysis_outputs/source_audit/p78_repair_lost_source_pixels/p78_repair_lost_source_pixels_sheet.jpg`
- Scope:
  - Localized which p78 source pixels are lost by moving from the current source box to dx `-38/-40` repaired boxes.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - dx `-38` loses `1919` pixels, `0.008218` of the graphic mask, bbox `[294,2534,332,2630]`.
  - dx `-40` loses `2064` pixels, `0.008839` of the graphic mask, bbox `[294,2534,334,2630]`.
  - The repaired frames gain `0` detected source-mask pixels on the right.
  - All lost pixels come from one left-edge graphic component.
- Conclusion:
  - The repair trims a narrow left-edge graphic strip, not the pull-quote text center.
  - This supports using dx `-38/-40` as p76 registration validation only.
- Next test:
  - Reopen the lost-strip idea only if a future source clue explicitly names left-edge trim/crop.
  - Refreshed missing-rule frontier count: `197` closed/deferred branches.

### Extended Capsule Motif Recurrence

- Status: extended; Issue 24-specific provenance strengthened.
- Evidence:
  - `scripts/analyze_capsule_motif_recurrence.py`
  - `analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence.md`
  - `analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence.json`
  - `analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence_sheet.jpg`
- Scope:
  - Added `Issue_27.pdf` and `bitcoin4.pdf` to the capsule-motif recurrence check.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Issue 24 baseline still has `2` strong five-point sequence matches.
  - `bitcoin4.pdf` has `2` strong five-point sequence matches, consistent with its lower-resolution Issue 24 witness role.
  - Independent comparison PDFs have `0` strong five-point sequence matches: `Issue_26.pdf`, `Issue_27.pdf`, and `bitcoin3.pdf`.
  - Individual red/orange blobs remain noisy: independent comparisons still produce `66` strong individual warm-shape matches.
- Conclusion:
  - The p73/p79 five-capsule zigzag chain looks Issue-24-specific rather than generic OVERDOSE house style.
  - It is still provenance/order evidence only; no source-backed extraction unit was found.
- Next test:
  - Keep the capsule chain as a validation/provenance layer for source comparisons, not as direct page-76 key material.
  - Refreshed missing-rule frontier count: `198` closed/deferred branches.

### Five-Index Convergence

- Status: tested; five is a locator/order signal, not the extraction unit.
- Evidence:
  - `scripts/audit_five_index_convergence.py`
  - `analysis_outputs/source_audit/five_index_convergence/five_index_convergence.md`
  - `analysis_outputs/source_audit/five_index_convergence/five_index_convergence.json`
- Scope:
  - Checked whether the repeated five-count system gives a readable instruction or direct selector.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Five repeats across p73 capsules, p79 fragments, p80 symptoms, p76 orange boxes, and p76 grey boxes.
  - p73 and p79 capsule chains share step signature `RRLL`.
  - p79 fragment indexes are p73 indexes plus `5`.
  - Fifth selections converge on p80 `SHITCOINS`, p76 orange 5 `shitcoiner at heart`, p76 grey 5 `Volcano Bonds`, and `B5 + 5 lines -> O5`.
  - Directional first/last-word streams from `RRLL` produced no instruction hits.
- Conclusion:
  - Five is a strong O5/G5 locator and provenance/order signal.
  - It still does not specify whether to extract words, letters, edges, fonts, or something else.
- Next test:
  - Keep five as validation for future source/clue checks; do not use `RRLL` or `1100` as key material by itself.
  - Refreshed missing-rule frontier count: `199` closed/deferred branches.

### Source-Registration Acceptance Benchmark

- Status: refreshed; future-source gate tightened.
- Evidence:
  - `scripts/build_source_registration_acceptance_test.py`
  - `analysis_outputs/source_audit/source_registration_acceptance_test/source_registration_acceptance_test.md`
  - `analysis_outputs/source_audit/source_registration_acceptance_test/source_registration_acceptance_test.json`
- Scope:
  - Updated the source-registration acceptance checklist with the orientation correction and five-index result.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `C6` now records five-index locator evidence: five repeats across p73/p79/p80/p76, p73/p79 step signature is `RRLL`, and p79-p73 offsets are `[5, 5, 5, 5, 5]`.
  - `C9` now records the source-orientation bridge: 3D/readable geometry matches source/PDF after `rotate180`.
  - Current benchmark still fails the extraction-unit constraint `C3`.
- Conclusion:
  - Any future source/physical/original-layout material must pass the `C1-C9` benchmark before extraction resumes.
  - Current local sources remain target/provenance witnesses, not key material.
- Next test:
  - Score any new source against `C1-C9`; do not rerun local geometry streams unless they pass `C2/C3` and explain `C6`.
  - Refreshed missing-rule frontier count: `200` closed/deferred branches.

### Current Scan Acceptance Benchmark

- Status: dry-run complete; current scan is baseline-only, not extraction-ready.
- Evidence:
  - `scripts/audit_current_scan_acceptance_benchmark.py`
  - `analysis_outputs/source_audit/current_scan_acceptance_benchmark/current_scan_acceptance_benchmark.md`
  - `analysis_outputs/source_audit/current_scan_acceptance_benchmark/current_scan_acceptance_benchmark.json`
- Scope:
  - Scored the current canonical `magazine.pdf` against the refreshed `C1-C9` benchmark.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Current scan has `2` pass constraints, `4` partial constraints, and `3` fail constraints.
  - Passing: `C1` trusted O5/G5 source boxes and `C9` orientation/source-cache bridge.
  - Still blocking: `C2`, `C3`, `C4`, `C5`, `C6`, `C7`, and `C8`.
  - Biggest blockers are still `C3` extraction unit and `C4/C8` physical/source quality.
- Conclusion:
  - Current scan is a reliable baseline for target/provenance checks.
  - It should not be used for more key-candidate generation without a new extraction-unit clue or better source material.
- Next test:
  - Use this report as the expected baseline when scoring any future physical/original-layout/source candidate.
  - Refreshed missing-rule frontier count: `201` closed/deferred branches.

### Physical Model Near-Miss Rank

- Status: tested; C4 remains failed, but benchmark is sharper.
- Evidence:
  - `scripts/audit_physical_model_near_miss_rank.py`
  - `analysis_outputs/source_audit/physical_model_near_miss_rank/physical_model_near_miss_rank.md`
  - `analysis_outputs/source_audit/physical_model_near_miss_rank/physical_model_near_miss_rank.json`
- Scope:
  - Ranked true physical/spread and control models by distance to trusted page-76 `O5`/`G5`.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Closest true physical near miss is p77 `It does this by monetizing` -> p76 `O5`, requiring shift `(0.0, -71.93)` px.
  - That shift creates only one trusted O5/G5 hit, not a repeated selector.
  - p75 front/back is much weaker: best shift magnitude `233.82` px.
- Conclusion:
  - Current digital scan does not validate true physical/spread extraction.
  - The p77->O5 near miss is useful only as a future physical-scan benchmark.
- Next test:
  - If a physical scan/photo appears, test whether it naturally reduces the p77->O5 vertical miss and creates repeated O5/G5 contacts.
  - Refreshed missing-rule frontier count: `202` closed/deferred branches.

### Monetizing Near-Miss Unit Audit

- Status: tested; not a C3 extraction-unit clue under the current scan.
- Evidence:
  - `scripts/audit_monetizing_near_miss_unit.py`
  - `analysis_outputs/source_audit/monetizing_near_miss_unit/monetizing_near_miss_unit.md`
  - `analysis_outputs/source_audit/monetizing_near_miss_unit/monetizing_near_miss_unit.json`
- Scope:
  - Pressure-tested p77 `It does this by monetizing`, the closest true physical near miss to p76 `O5`, as possible extraction-unit wording.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Exact phrase has no `word`, `letter`, `line`, `edge`, `font`, `color`, `take`, `read`, or `select` wording.
  - Context has only weak `first` wording from `for the first time in human history`.
  - Initials/endings/reversal and first-cue target reads produce ordinary fragments: `idtbm`, `tssyg`, `plu`, `Volcano shitcoiner`, and `shitcoiner Volcano`.
- Conclusion:
  - The phrase is semantically relevant but does not name the missing unit/order.
  - Keep it as a future physical/source benchmark, not as current extraction material.
- Next test:
  - Revisit only if a physical/original-layout source creates direct repeated p77->O5/G5 contact or an external clue explicitly uses monetizing/first-time language as an instruction.
  - Refreshed missing-rule frontier count: `203` closed/deferred branches.

### Content-Box Physical Normalization

- Status: tested; C4 remains failed under the current scan.
- Evidence:
  - `scripts/audit_content_box_physical_normalization.py`
  - `analysis_outputs/source_audit/content_box_physical_normalization/content_box_physical_normalization.md`
  - `analysis_outputs/source_audit/content_box_physical_normalization/content_box_physical_normalization.json`
  - `analysis_outputs/source_audit/content_box_physical_normalization/content_box_physical_normalization_overlay.jpg`
- Scope:
  - Tested whether normalizing each page to its visible content bounding box before horizontal mirror reflection repairs the p77 -> p76 `O5/G5` physical near miss.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Baseline p77 `It does this by monetizing` -> `O5` miss: `71.93` px.
  - Content-box-normalized p77 `It does this by monetizing` -> `O5` miss: `65.49` px.
  - Improvement is only `6.44` px, and p77 still has `0` direct trusted `O5/G5` hits.
  - p75 front/back does not improve; its best shift worsens from `233.82` px to `254.03` px.
- Conclusion:
  - A plausible crop/trim repair does not validate physical reflection for the current scan.
  - Keep the p77 near miss as a benchmark for future physical/source material, not as a current selector.
- Next test:
  - If a new physical/original-layout scan appears, compare full-page reflection and content-box-normalized reflection first.
  - Refreshed missing-rule frontier count: `204` closed/deferred branches.

### P80 Symptom Relief Rule Audit

- Status: tested; p80 remains locator/theme evidence only.
- Evidence:
  - `scripts/audit_p80_symptom_relief_rule.py`
  - `analysis_outputs/source_audit/p80_symptom_relief_rule/p80_symptom_relief_rule.md`
  - `analysis_outputs/source_audit/p80_symptom_relief_rule/p80_symptom_relief_rule.json`
- Scope:
  - Tested page-80 `5 SYMPTOM RELIEF` as a literal remove/relieve operation on page-76 highlight units.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Package action words exist: `relief`, `reliever`, `fixes`, `proof`, `work`, `anti`, `fake`.
  - No explicit extraction-unit wording appears on the package.
  - Direct symptom matches cluster on `heart` and `shitcoiner at heart`, but relief outputs are ordinary fragments: `shitcoiner at`, `at heart`, and `at`.
  - Forced printed five-order relief changes `0/5` target texts.
  - Relief streams and initials produce no instruction hits.
- Conclusion:
  - `5 SYMPTOM RELIEF` reinforces the five/O5 theme but does not supply the missing selector.
  - Keep p80 in the C6 five-index locator evidence, not as an extraction mechanism.
- Next test:
  - Reopen only if source geometry places the package copy onto page 76 or a new clue explicitly says to remove/relieve symptoms.
  - Refreshed missing-rule frontier count: `205` closed/deferred branches.

### P77 One-Line Near-Miss Audit

- Status: tested; useful benchmark, not a selector.
- Evidence:
  - `scripts/audit_p77_one_line_near_miss.py`
  - `analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.md`
  - `analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json`
- Scope:
  - Checked whether the p77 `It does this by monetizing` -> p76 `O5` miss is explained by exactly one printed line.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - p77 -> `O5` gap is `71.93` px.
  - Page-76 lower-corridor median line pitch is `73.73` px.
  - One-line-up shift creates only `1` weak p77 hit: `It does this by monetizing` -> `O5`, overlap-vs-target `0.02694`.
  - Same shift creates `0` p75 hits and no repeated `O5/G5` pattern.
- Conclusion:
  - The near miss is line-quantized and should be tracked when comparing future physical/original-layout sources.
  - It does not become extraction material without a source clue naming `line up`, `one line`, or similar.
- Next test:
  - Use the `71.93` px / `73.73` px benchmark on future source scans; do not apply one-line repair as a current selector.
  - Refreshed missing-rule frontier count: `206` closed/deferred branches.

### Canva Line-Up Shift Scope

- Status: tested; source-registration wording only under current scan.
- Evidence:
  - `scripts/audit_canva_lineup_shift_scope.py`
  - `analysis_outputs/source_audit/canva_lineup_shift_scope/canva_lineup_shift_scope.md`
  - `analysis_outputs/source_audit/canva_lineup_shift_scope/canva_lineup_shift_scope.json`
- Scope:
  - Tested the Canva `Pills dont line up` / `XX is in line with barbed wire` wording as one/two-line page-76 registration shifts across pages `75/77/78/79/80`.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Measured line pitch used: `73.73` px.
  - Total trusted `O5/G5` hits over all tested line shifts: `2`.
  - `one_line_up` creates only p77 `It does this by monetizing` -> `O5`, overlap-vs-target `0.02694`.
  - `two_lines_up` creates the same p77 -> `O5` hit more strongly, overlap-vs-target `0.74844`.
  - p79 pill/graphic fragments create `0` one-line-up trusted hits.
  - No page/shift creates repeated `O5/G5` contacts.
- Conclusion:
  - The Canva `line up` note remains useful provenance for source alignment, not a current extraction selector.
  - The isolated p77 line-shift behavior should be used only as a future-source benchmark.
- Next test:
  - Reopen line-up operations only with a higher-resolution Canva/original/physical source that changes pill or XX/barbed-wire alignment.
  - Refreshed missing-rule frontier count: `207` closed/deferred branches.

### Zero / `#0` Index Rule Scope

- Status: tested; source-fidelity/five-locator evidence only.
- Evidence:
  - `scripts/audit_zero_index_rule_scope.py`
  - `analysis_outputs/source_audit/zero_index_rule_scope/zero_index_rule_scope.md`
  - `analysis_outputs/source_audit/zero_index_rule_scope/zero_index_rule_scope.json`
- Scope:
  - Tested the Canva `OCR DIDNT PICK UP THE #0` note as literal zero-based selection and zero-count indexing into page-76 highlight/corridor units.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Literal `#0` selects first page-76 units/corridor text: `O1`, `B1`, and `Don't believe me?`, not `O5/G5`.
  - Trusted scan `100,000` has `5` zeros, which redundantly selects `O5` and `B5` if zero-count is used as a highlight index.
  - Unsupported `1000,000` would have `6` zeros and no page-76 fifth orange/grey target.
  - Zero streams such as `HDDHIDtD`, `$NlchHtN`, and `t$bHt$hl` have no instruction hits.
- Conclusion:
  - The `#0` note remains a source-fidelity warning and possible confirmation of the five/O5 locator, not an extraction rule.
- Next test:
  - Only reopen if the exact Canva/browser/original source showing the missed `#0` is recovered; compare it to `analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops_sheet.jpg` first.
  - Refreshed missing-rule frontier count: `208` closed/deferred branches.

### Source Delta Watch

- Status: checked; no new actionable source-grade local material.
- Evidence:
  - `scripts/audit_source_delta_watch.py`
  - `analysis_outputs/source_audit/source_delta_watch/source_delta_watch.md`
  - `analysis_outputs/source_audit/source_delta_watch/source_delta_watch.json`
- Scope:
  - Checked Desktop, Downloads, and Documents for new PDF/image/layout/document material that could affect geometry, visible layout, or formatting provenance.
  - Compared candidates against the existing local source inventory by path and MD5.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `43` local source-like candidates were scored.
  - Actionable unknown source candidates after duplicate filtering: `0`.
  - The extra `private_inputs/Documents/keyserattemptclaudeandcodex/magazine.pdf` is an MD5 duplicate of known inventory material.
- Conclusion:
  - No new local source changes the current blocker.
  - The source hierarchy remains: `magazine.pdf` for geometry, corrected DOCM/plain text for exact wording, `Article with Fonts.docm` for Typeka/font labels, and comparison PDFs for style-only controls.
- Next test:
  - Reopen source-gate/priority-crop comparisons only if a true physical scan/photo, original Canva export, layout/source file, or demonstrably different source PDF appears.

### Future Source Validation Packet

- Status: created; use before reopening extraction.
- Evidence:
  - `scripts/build_future_source_validation_packet.py`
  - `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.md`
  - `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json`
- Scope:
  - Consolidated current source/geometry benchmarks into one checklist for future physical scans, Canva exports, browser captures, or layout/source files.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Key benchmarks:
  - p78 frame current box `[1234.0, 2398.0, 2250.0, 2950.0]`; repaired dx=`-40`, dy=`0` frame `[1194.0, 2398.0, 2210.0, 2950.0]`.
  - Repaired exact-edge phrase/style: `should sell | Volcano Bonds | shitcoiner at heart` / `RKY`.
  - p77 near miss: `It does this by monetizing` -> `O5`, gap `71.93px`, line pitch `73.73px`.
  - Zero/#0 baseline: p77 `100,000`.
  - p79 pill baseline: `5` trusted fragments.
- Conclusion:
  - Any future material must improve at least one gate: C3 extraction unit, C4 physical registration, C8 source image quality, or C2 p78 frame signature.
- Next test:
  - When a new source appears, compare it against this packet before any selector/key branch.

### Future Source Validation Review Sheet

- Status: created; visual companion to the validation packet.
- Evidence:
  - `scripts/build_future_source_review_sheet.py`
  - `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.jpg`
  - `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.md`
  - `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.json`
- Scope:
  - Built one side-by-side review sheet for the active source/geometry benchmarks.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Panels:
  - page-76 priority crops;
  - p78 frame tri-contact;
  - repaired exact-edge/font-contact style;
  - zero/#0 hotspots;
  - p79 pill fragments;
  - source gate summary;
  - p77 one-line near miss;
  - minimum reopen conditions.
- Conclusion:
  - This is a comparison aid only, not new extraction evidence.
  - Future source material should be compared visually against this sheet, then scored against the validation packet.

### Future Source Packet Integrity

- Status: checked; packet and review sheet are current.
- Evidence:
  - `scripts/audit_future_source_packet_integrity.py`
  - `analysis_outputs/source_audit/future_source_packet_integrity/future_source_packet_integrity.md`
  - `analysis_outputs/source_audit/future_source_packet_integrity/future_source_packet_integrity.json`
- Scope:
  - Verified the future-source validation packet and visual review sheet against the current benchmark artifacts.
  - No OCR extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Checks:
  - Missing artifacts: `0`.
  - Stale benchmark inputs: `0`.
  - Failed benchmark checks: `0`.
  - Review sheet panel count: `8`.
  - p78 repair benchmark: dx `-38`, tri-contact pass `True`.
  - Exact-edge signature: `should sell | Volcano Bonds | shitcoiner at heart` / `RKY`.
  - p77 near-miss gap: `71.93px`.
  - Dead/closed branch count: `209`.
- Conclusion:
  - The packet/review sheet remain valid as the first gate for any new physical scan, Canva export, browser capture, or layout source.
  - This confirms the current direction: source validation first; no local extraction/key branch reopens without a new unit/order clue.

### 3D Active Target Label Gate

- Status: checked; 3D word labels are navigation-only for active targets.
- Evidence:
  - `scripts/audit_3d_active_target_label_gate.py`
  - `analysis_outputs/3d_article_map/active_target_label_gate/active_target_label_gate.md`
  - `analysis_outputs/3d_article_map/active_target_label_gate/active_target_label_gate.json`
- Scope:
  - Compared the 3D map OCR/word-label layer against corrected canonical text for active page-76 corridor phrases.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Missing/distorted active target labels include `buying the dip`, `$1 billion`, `Volcano Bonds`, and `shitcoiner at heart`.
  - The layer still preserves navigation anchors such as `should sell`, `future bitcoin earnings`, and p77 `100,000`.
  - Known bad/alternate OCR labels remain visible, including p77 `nas gone` and p78 `Bitcoin fills the gap`.
- Conclusion:
  - Use the 3D view for geometry and visual inspection only.
  - Use corrected DOCM/plain text or source-crop review for exact wording after a visual region is selected.
  - Closed/deferred branch count is now `209`.

### 3D Target Wording Bridge

- Status: created; use for manual inspection and future source comparison.
- Evidence:
  - `scripts/build_3d_target_wording_bridge.py`
  - `analysis_outputs/3d_article_map/active_target_label_gate/target_wording_bridge_sheet.jpg`
  - `analysis_outputs/3d_article_map/active_target_label_gate/target_wording_bridge.md`
  - `analysis_outputs/3d_article_map/active_target_label_gate/target_wording_bridge.json`
- Scope:
  - Paired the current page-76 priority crop images with corrected exact wording and 3D-label status.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Rows:
  - `L32_O5_primary`: exact `Maybe because he's a shitcoiner at heart.`; absent from 3D labels.
  - `L27_G5_pair`: exact `collateralized "Volcano Bonds" to pay off the IMF loan`; `Volcano Bonds` absent from 3D labels.
  - `L25_should_sell`: exact `$1 billion in bitcoin - that he should sell`; `$1 billion` absent from 3D labels.
  - `L26_L29_source_band`: mixed reliability; use source crop plus corrected transcript.
  - `L25_L32_frame_context`: compact benchmark `should sell -> Volcano Bonds -> shitcoiner at heart`.
- Conclusion:
  - This is a guardrail artifact, not extraction evidence.
  - It should be used whenever the 3D view or a future source image is inspected around the active lower page-76 corridor.

### 3D Viewer Text Authority Cue

- Status: added to the local 3D viewer.
- Evidence:
  - `analysis_outputs/3d_article_map/index.html`
  - `analysis_outputs/3d_article_map/styles.css`
  - `analysis_outputs/3d_article_map/viewer.js`
  - `analysis_outputs/3d_article_map/active_target_label_gate/target_wording_bridge_sheet.jpg`
- Scope:
  - Added a visible guardrail inside the 3D view to separate OCR navigation labels from authoritative article wording.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Confirmed UI:
  - `Text Authority` panel exists and is visible.
  - The panel lists exact O5 wording: `Maybe because he's a shitcoiner at heart.`
  - The panel lists exact G5 wording: `collateralized "Volcano Bonds" to pay off the IMF loan`
  - The panel lists the compact p78-frame benchmark: `should sell -> Volcano Bonds -> shitcoiner at heart`.
  - `Open bridge sheet` link exists and resolves to the local bridge sheet.
- Conclusion:
  - Manual 3D inspection should use this panel/bridge sheet before extracting any lower page-76 wording.
  - This is not new selector evidence; it is a control against OCR-driven false positives.

### Active Corridor Witness Consistency

- Status: checked; exact wording source hierarchy tightened.
- Evidence:
  - `scripts/audit_active_corridor_witness_consistency.py`
  - `analysis_outputs/plain_text_transcript/active_corridor_witness_consistency/active_corridor_witness_consistency.md`
  - `analysis_outputs/plain_text_transcript/active_corridor_witness_consistency/active_corridor_witness_consistency.json`
- Scope:
  - Checked only the active lower page-76 corridor phrases across local text witnesses.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Authoritative text witnesses preserve all `10/10` target phrases: `canonical_plain_article_body`, `article_with_fonts_text`, and `full_article_corrected`.
  - `user_plain_article_latest` is missing `Volcano Bonds`; it should not be used as the exact G5 source.
  - `user_markdown_transcript` preserves all `10/10` target phrases.
  - `user_annotated_transcript` is useful for formatting notes but breaks one exact phrase through inserted annotations.
  - `article_3d_map_page76_chars` preserves only `6/10` active target phrases and misses `buying the dip`, `$1 billion`, `Volcano Bonds`, and `shitcoiner at heart`.
- Conclusion:
  - Exact lower page-76 wording must come from the corrected canonical/DOCM witnesses.
  - The 3D viewer, bridge sheet, and source crops remain geometry/navigation witnesses.
  - This does not provide an extraction rule; it prevents using a known-bad transcript layer.

### Typeka / Manual Bold Disambiguation

- Status: checked; manual bold markup downgraded as extraction evidence.
- Evidence:
  - `scripts/audit_typeka_manual_bold_disambiguation.py`
  - `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.md`
  - `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.json`
- Scope:
  - Compared active lower page-76 corridor phrases in `Article with Fonts.docm` against the user Markdown bold markup.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Dominant `Typeka Mix` targets in DOCM: `el_salvador`, `novogratz`, `trust_that_guy`.
  - Markdown-bold but not DOCM-bold targets: `none`.
  - DOCM-bold but not Markdown-bold targets: `one_billion`, `volcano_bonds`.
  - `$1 billion` and `Volcano Bonds` are DOCM-bold/black-highlighted but not Markdown-bold in the user Markdown witness.
  - `shitcoiner at heart` is DOCM-bold/yellow-highlighted and also Markdown-bold.
  - `Typeka Mix` is real but lands on nearby prose rather than the G5/O5 extraction pair.
- Conclusion:
  - Use `Article with Fonts.docm` for Typeka/Typeka Mix/bold/highlight labels.
  - Treat old manual bold/partial-bold annotations as descriptive notes only.
  - Do not reopen manual-bold extraction unless a new clue explicitly names font state, bold, Typeka, Mix, or a selected text unit.

### Typeka Authority Bridge Sheet

- Status: created and linked from the 3D viewer.
- Evidence:
  - `scripts/build_typeka_authority_bridge_sheet.py`
  - `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg`
  - `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.md`
  - `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.json`
  - `analysis_outputs/3d_article_map/index.html`
  - `analysis_outputs/3d_article_map/viewer.js`
- Scope:
  - Created a visual bridge between page-76 priority crops and DOCM Typeka/bold/highlight states.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Sheet size: `1900 x 1810` px.
  - `$1 billion`: DOCM `Typeka`, bold `1.0`, black highlight; Markdown bold `0.0`.
  - `Volcano Bonds`: DOCM `Typeka`, bold `1.0`, black highlight; Markdown bold `0.0`.
  - `shitcoiner at heart`: DOCM `Typeka`, bold `1.0`, yellow highlight; Markdown bold `1.0`.
  - `Novogratz` and `I don't really trust that guy`: dominant `Typeka Mix`, not highlighted and not DOCM-bold.
  - The 3D viewer now links this typography sheet from the `Text Authority` panel.
- Conclusion:
  - Use this sheet when inspecting the lower page-76 corridor in the 3D viewer.
  - It keeps typography authority separate from OCR labels and Markdown annotations.
  - This is not new selector evidence.

### Future Source Packet Typography Integration

- Status: refreshed; typography authority is now part of the source gate.
- Evidence:
  - `scripts/build_future_source_validation_packet.py`
  - `scripts/build_future_source_review_sheet.py`
  - `scripts/audit_future_source_packet_integrity.py`
  - `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json`
  - `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.jpg`
  - `analysis_outputs/source_audit/future_source_packet_integrity/future_source_packet_integrity.json`
- Scope:
  - Added the Typeka authority bridge to the future-source validation packet and visual review sheet.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Review sheet panel count is now `9`.
  - New panel: `typeka_typography_authority`.
  - Packet benchmark added: `typekaTypographyAuthority`.
  - Integrity status: `PASS`.
  - Missing artifacts: `0`.
  - Stale inputs: `0`.
  - Failed checks: `0`.
  - `typeka_authority_registered`: `True`.
- Conclusion:
  - Any future source comparison must now pass both the geometry benchmarks and the typography authority guardrail.
  - The source gate no longer relies only on visual geometry; it also protects against Markdown-bold/OCR font-state drift.
  - This is still a validation-gate improvement, not extraction evidence.

### Page 76 Typography Overlay

- Status: created and linked from the 3D viewer.
- Evidence:
  - `scripts/build_page76_typography_overlay.py`
  - `analysis_outputs/source_audit/page76_typography_overlay/page76_typography_overlay.jpg`
  - `analysis_outputs/source_audit/page76_typography_overlay/page76_typography_overlay.md`
  - `analysis_outputs/source_audit/page76_typography_overlay/page76_typography_overlay.json`
  - `analysis_outputs/3d_article_map/index.html`
  - `analysis_outputs/3d_article_map/viewer.js`
- Scope:
  - Put trusted lower page-76 phrase boxes, DOCM typography states, row guides, and M3/M4 standalone marks on one source crop.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Black/DOCM-bold anchors: `$1 billion`, `Volcano Bonds`.
  - Orange/yellow/DOCM-bold anchors: `buying the dip`, `shitcoiner at heart`.
  - Typeka Mix context: `Novogratz`, `I don't really trust that guy`.
  - Typeka Mix remains nearby context and does not provide a clean G5/O5 target selector by itself.
  - M3/M4 remain visual bracket/support marks, not a complete extraction rule.
- Conclusion:
  - Use this overlay for page-76 visual inspection and future source comparison.
  - Typography alone is not promoted to selector evidence.
  - Next branch should be a bounded adjacency/unit test around the four anchored phrases.

### Page 76 Four-Anchor Adjacency Audit

- Status: checked; closed as standalone selector evidence.
- Evidence:
  - `scripts/analyze_page76_anchor_adjacency_units.py`
  - `analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.md`
  - `analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json`
- Scope:
  - Tested immediate same-line, boundary, above-line, and below-line words around the four active page-76 anchors.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Visual color order: `OBBO`.
  - Phrase initials: `btd 1b vb sah`.
  - Boundary/vertical probes produce ordinary prose fragments: `he's`, `in`, `to`, `a`, `on`, `was`, `future`, `trust`, `announced`, `billions`, `those`.
  - No read/fold/mirror/page/line/word/letter instruction appears.
- Conclusion:
  - Anchor adjacency is useful for local context but not a selector.
  - The durable result is the `OBBO` anchor signature.
  - Next useful comparison is whether `OBBO` is unique to this puzzle corridor or common to OVERDOSE/package/pill layout styling.

### O-B-B-O Anchor Signature Recurrence

- Status: checked; useful as source-comparison signature only.
- Evidence:
  - `scripts/audit_obbo_anchor_signature.py`
  - `analysis_outputs/comparison_articles/obbo_anchor_signature/obbo_anchor_signature.md`
  - `analysis_outputs/comparison_articles/obbo_anchor_signature/obbo_anchor_signature.json`
- Scope:
  - Compared the active page-76 O-B-B-O sequence against existing comparison-article body-highlighter boxes.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Template: `buying the dip` / `$1 billion` / `Volcano Bonds` / `shitcoiner at heart`.
  - Pages with any O-B-B-O sequence: `3`.
  - Issue 24 pages with O-B-B-O: `3`.
  - Independent comparison pages with O-B-B-O: `0`.
  - Page-76/template score: `0.015`.
  - Best independent score: `None`.
- Conclusion:
  - O-B-B-O is not a complete selector, but it is a strong local signature for this page-76 corridor.
  - Existing comparison articles do not reproduce it in the current body-highlight grammar layer.
  - Next useful branch is p80/package or pill-count mechanics only if they choose among the four page-76 anchors.

### P80 Four-Anchor Choice

- Status: checked; not a four-anchor selector.
- Evidence:
  - `scripts/audit_p80_four_anchor_choice.py`
  - `analysis_outputs/source_audit/p80_four_anchor_choice/p80_four_anchor_choice.md`
  - `analysis_outputs/source_audit/p80_four_anchor_choice/p80_four_anchor_choice.json`
- Scope:
  - Tested whether page-80 package/pill copy chooses among `buying the dip`, `$1 billion`, `Volcano Bonds`, and `shitcoiner at heart`.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `SHITCOINS` maps cleanly to `shitcoiner at heart`.
  - `HEARTBURN` weakly maps to `heart`.
  - `Bitcoin FixesThis` only touches the `$1 billion` line through context word `bitcoin`.
  - No p80 term cleanly selects `Volcano Bonds`.
  - P80 numbers `[5, 100, 16, 473, 6, 80]` do not define a four-anchor order without an arbitrary modulo rule.
- Conclusion:
  - P80 corroborates O5 and the older five-count grouping, but it does not choose the O-B-B-O anchors.
  - Reopen p80 only if a physical/fold/mirror alignment places bottle/package regions directly onto page-76 anchors.

### P80 To Page-76 Anchor Geometry

- Status: checked; p80 closed for current scan geometry.
- Evidence:
  - `scripts/audit_p80_to_p76_anchor_geometry.py`
  - `analysis_outputs/source_audit/p80_to_p76_anchor_geometry/p80_to_p76_anchor_geometry_sheet.jpg`
  - `analysis_outputs/source_audit/p80_to_p76_anchor_geometry/p80_to_p76_anchor_geometry.md`
  - `analysis_outputs/source_audit/p80_to_p76_anchor_geometry/p80_to_p76_anchor_geometry.json`
- Scope:
  - Tested whether p80 package labels align to the four page-76 anchors under identity, hflip, vflip, and 180-degree rotation.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Positive overlap rows at 10% threshold: `0`.
  - Closest case: p80 O2 `6 FL OZ (473 mL)` under hflip to `buying the dip`, center distance `183.57` px, overlap `0.0`.
  - No tested transform places p80 O1/O2 directly onto `$1 billion`, `Volcano Bonds`, or `shitcoiner at heart`.
- Conclusion:
  - Current scan geometry does not let p80 choose the O-B-B-O anchors.
  - Keep p80 as theme/count corroboration only.
  - Next useful geometry branch is M3/M4 ordering within page 76 itself.

### M3/M4 O-B-B-O Ordering

- Status: checked; not an O-B-B-O ordering selector.
- Evidence:
  - `scripts/audit_m3_m4_obbo_order.py`
  - `analysis_outputs/source_audit/m3_m4_obbo_order/m3_m4_obbo_order_overlay.jpg`
  - `analysis_outputs/source_audit/m3_m4_obbo_order/m3_m4_obbo_order.md`
  - `analysis_outputs/source_audit/m3_m4_obbo_order/m3_m4_obbo_order.json`
- Scope:
  - Ranked the four page-76 anchors by M3/M4 center distance, axis distance, projection, and wedge membership.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - M3/M4 axis vertex: `[999.28, 2900.36]`.
  - Only `shitcoiner at heart` is inside the M3/M4 wedge.
  - `Volcano Bonds`, `$1 billion`, and `buying the dip` are outside the wedge.
  - Distance/projection orderings do not form an instruction-like sequence.
- Conclusion:
  - M3/M4 are endpoint/bracket evidence for O5, not a selector for all four anchors.
  - G5 remains a p78-frame contact, not a M3/M4 contact.
  - The missing rule is still upstream: a source/external instruction for the extraction unit/order.

### P78 Contact-Role Grammar

- Status: checked; registration grammar only.
- Evidence:
  - `scripts/audit_p78_contact_role_grammar.py`
  - `analysis_outputs/source_audit/p78_contact_role_grammar/p78_contact_role_grammar_overlay.jpg`
  - `analysis_outputs/source_audit/p78_contact_role_grammar/p78_contact_role_grammar.md`
  - `analysis_outputs/source_audit/p78_contact_role_grammar/p78_contact_role_grammar.json`
- Scope:
  - Tested whether the stable dx=-38 p78 frame contacts create a human-readable edge/order selector.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Top edge: `should sell`.
  - Left edge: G5 `Volcano Bonds`.
  - Right edge: standalone M3 mark.
  - Bottom edge: O5 `shitcoiner at heart`.
  - Clockwise, counterclockwise, edge-role, color/medium, and text-only readings produce only labels/nearby prose.
  - Instruction hits in the content streams: none.
- Conclusion:
  - The repaired p78 frame is a strong source-registration signature: G5 + M3 + O5 stay coherent at dx=-38.
  - It still does not identify a word, letter, line, direction, or key unit.
  - Do not promote contact-role ordering as extraction evidence unless a new source clue names how to read those contacts.
  - Next useful branch: the Typeka/font layer around the G5/O5 corridor and comparison Max articles.

### Typeka Transition Boundaries

- Status: checked; unique corridor evidence only.
- Evidence:
  - `scripts/audit_typeka_transition_boundaries.py`
  - `analysis_outputs/docm_format_sources/typeka_transition_boundaries/typeka_transition_boundaries.md`
  - `analysis_outputs/docm_format_sources/typeka_transition_boundaries/typeka_transition_boundaries.json`
- Scope:
  - Audited page-76 paragraphs `60-73` / runs `118-151` for changes between Typeka regular, Typeka Mix, and Typeka bold.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Font-only path: `RMRBRBRBRBRBRMRMRB`.
  - Highlight-aware path: `RMRYRBRKRKRBRMRMRY`.
  - Both paths occur once on page 76 and zero times on pages 75, 77, 78, and 79 in the DOCM witness.
  - Non-regular initials: `EbP$VIMIs`.
  - Highlight/mix initials: `Eb$VMIs`.
  - Boundary pairs: `fE rt sb pI dP ew e$ ni dV st eI na dM zi tI yM as`.
  - Instruction hits: none.
  - Local comparison Max PDFs are image-only, so they cannot verify Typeka metadata or supply a font-layer extraction rule.
- Conclusion:
  - Typeka transitions are real and further support the page-76 El Salvador/Volcano corridor.
  - The font-boundary stream follows visible semantic emphasis, but it does not name a word, letter, line, direction, or key unit.
  - Do not use font-boundary initials/pairs/codes as key material without a new source rule.
  - Next useful branch: high-res visual highlight boundaries around the G5/O5 five-line corridor, independent of DOCM font boundaries.

### G5/O5 High-Res Boundary Cut

- Status: checked; not a standalone extraction unit.
- Evidence:
  - `scripts/audit_g5_o5_highres_boundary_cut.py`
  - `analysis_outputs/source_audit/g5_o5_highres_boundary_cut/g5_o5_highres_boundary_cut_overlay.jpg`
  - `analysis_outputs/source_audit/g5_o5_highres_boundary_cut/g5_o5_highres_boundary_cut.md`
  - `analysis_outputs/source_audit/g5_o5_highres_boundary_cut/g5_o5_highres_boundary_cut.json`
- Scope:
  - Inspected whether the repaired p78 frame's high-res visual edge creates a side-specific unit at G5/O5.
  - No key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - The dx=-38 frame left edge is exactly the right endpoint of G5 `Volcano Bonds`.
  - The same vertical edge cuts O5 inside `shitcoiner`, not at a word gap.
  - O5 exact-frame pixel relation: small intra-word gap `[1195, 1202]`, width `7`.
  - O5 large word-like gaps are `[1362, 1386]` and `[1444, 1469]`, far from the frame edge.
  - Approximate O5 split: `shitc|oiner at heart.`
  - Checked streams: `Volcano Bonds`, `oiner at heart.`, `Volcano Bonds | oiner at heart.`
  - Instruction hits: none.
- Conclusion:
  - This confirms a precise G5 endpoint registration contact, but O5 is not cut at a clean word/letter boundary.
  - A `shit|coiner` reading is too dependent on snapping inside the same glyph cluster.
  - Keep G5/O5 as registration/five-line evidence only.
  - Next useful branch: broader four-anchor O-B-B-O high-res boundary coincidences before any text extraction.

### O-B-B-O High-Res Boundary Coincidences

- Status: checked; not a standalone selector.
- Evidence:
  - `scripts/audit_obbo_highres_boundary_coincidences.py`
  - `analysis_outputs/source_audit/obbo_highres_boundary_coincidences/obbo_highres_boundary_coincidences_overlay.jpg`
  - `analysis_outputs/source_audit/obbo_highres_boundary_coincidences/obbo_highres_boundary_coincidences.md`
  - `analysis_outputs/source_audit/obbo_highres_boundary_coincidences/obbo_highres_boundary_coincidences.json`
- Scope:
  - Checked exact/near boundary coincidences for O4 `buying the dip`, B4 `$1 billion`, B5/G5 `Volcano Bonds`, and O5 `shitcoiner at heart` against each other, the repaired p78 frame, and M3/M4.
  - No text extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Exact B4 row guide: `$1 billion` top aligns with repaired frame top, delta `2.0` px, but B4 is horizontally outside the frame.
  - Exact contact-style hit: `Volcano Bonds` right edge equals repaired frame left edge, delta `0.0` px.
  - Near O5 band hits: O5 top to frame bottom delta `18.0` px; O5 centerY to frame bottom delta `7.0` px.
  - `buying the dip` has no exact/near boundary relation to the repaired frame or M3/M4 in this test.
- Conclusion:
  - The four-anchor O-B-B-O pattern is a corridor/signature, not a complete boundary selector.
  - B4 gives row alignment, G5 gives endpoint registration, and O5 gives near frame crossing; this does not define a word/letter/side extraction rule.
  - Next useful branch: inspect the 3D folded view for a non-boundary visual ordering cue before any further text/key stream.

### 3D Fold Non-Boundary Ordering

- Status: checked; orientation view only.
- Evidence:
  - `scripts/audit_3d_fold_nonboundary_ordering.py`
  - `analysis_outputs/3d_article_map/fold_nonboundary_ordering/fold_nonboundary_ordering_plan.jpg`
  - `analysis_outputs/3d_article_map/fold_nonboundary_ordering/fold_nonboundary_ordering.md`
  - `analysis_outputs/3d_article_map/fold_nonboundary_ordering/fold_nonboundary_ordering.json`
- Scope:
  - Inspected whether the 3D fold layout supplies an order that is not just page-76 boundary geometry.
  - No text extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - The viewer fold layout pairs `75/79` and `76/78`.
  - `79/76` are diagonal in the fold display, not a direct folded pair.
  - Active page-76 top-to-bottom order remains `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart`.
  - Fold-depth order is `buying_dip -> shitcoiner_heart -> volcano_bonds -> one_billion`, but this is a yaw/display artifact.
  - Fold X order is `one_billion -> volcano_bonds -> shitcoiner_heart -> buying_dip`, also a display-position artifact.
  - Original p79 pills remain on the top-row p79 plane; page-76 pill copies are the existing mirror-overlay hypothesis.
  - p79 reflection rows near `buying_dip` remain far from their source rectangles in fold-world distance (`921.25` and `938.23`).
- Conclusion:
  - Do not use fold-view display ordering as extraction evidence.
  - The 3D view is useful for orientation/provenance, not for selecting a text stream.
  - Next useful branch: source/provenance clue audit for an explicit extraction instruction, or physical/source image comparison if new evidence appears.

### 3D Viewer Layer Provenance

- Status: checked; viewer is an inspection surface, not an independent source.
- Evidence:
  - `scripts/audit_3d_viewer_layer_provenance.py`
  - `analysis_outputs/3d_article_map/viewer_layer_provenance/viewer_layer_provenance.md`
  - `analysis_outputs/3d_article_map/viewer_layer_provenance/viewer_layer_provenance.json`
- Scope:
  - Audited the 3D viewer source files to see whether the UI adds hidden fold/mirror modes, hidden selectors, or new runtime geometry.
  - No text extraction, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - The viewer exposes only `spread`, `fold`, and `stack`.
  - Mirror rectangles are precomputed `targetBox` overlays from `article_3d_map_data.json`; the viewer does not derive a new reflection/fold solution.
  - Ray selections are page-76-only hypotheses: all `40` ray endpoint pairs are `(76,76)`, using projected p79-pill mirror anchors rather than original p79 anchors.
  - The viewer displays `28` of `40` rays; hidden lower-ranked rays remain in the JSON but do not add an instruction.
  - Fixed fold geometry pairs `75/79` and `76/78`; `79/76` remains diagonal/non-contact in the viewer layout.
  - Browser-local text corrections can change labels but do not become geometry truth.
- Conclusion:
  - Do not read fold depth, ray visibility, or browser-local correction state as puzzle signal.
  - Use the 3D viewer for manual orientation and bridge-sheet review only.
  - Further progress needs a new source/original-layout/physical image or a clue that names the extraction unit and order.

### Active Text Authority Drift

- Status: checked; active page-76 wording/formatting authority is locked.
- Evidence:
  - `scripts/audit_active_text_authority_drift.py`
  - `analysis_outputs/source_audit/active_text_authority_drift/active_text_authority_drift.md`
  - `analysis_outputs/source_audit/active_text_authority_drift/active_text_authority_drift.json`
- Scope:
  - Compared the active page-76 target phrases across corrected plain text, canonical plain body, DOCM text/font runs, Markdown/annotated transcripts, and 3D OCR labels.
  - No text extraction stream, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Corrected/root text, canonical plain body, and `Article with Fonts.docm` agree on the active corridor after the latest raw plain-text corrections.
  - DOCM confirms the active sequence as:
    - O4 `buying the dip.` = Typeka, DOCM-bold, yellow/orange highlight.
    - B4 `$1 billion` = Typeka, DOCM-bold, black/grey highlight.
    - G5 `Volcano Bonds` = Typeka, DOCM-bold, black/grey highlight.
    - O5 `shitcoiner at heart.` = Typeka, DOCM-bold, yellow/orange highlight.
  - `Typeka Mix` remains nearby context (`Mike Novogratz`, `trust that guy`) rather than inside the O4/B4/G5/O5 targets.
  - Markdown bold misses `$1 billion` and `Volcano Bonds`, so it cannot be treated as source typography.
  - 3D OCR labels miss `$1 billion`, `Volcano Bonds`, and `shitcoiner at heart`, so they cannot be used for exact wording.
- Conclusion:
  - Use high-res crops for geometry, corrected/DOCM/plain text for exact wording, and DOCM Typeka states for typography labels.
  - Do not use Markdown bold, annotated partial-bold notes, or 3D OCR labels as extraction authority.
  - Extraction remains blocked until a clue/source names which locked active unit(s) to read and in what order.

### Y-B-B-Y Pair Symmetry

- Status: checked; source-comparison signature only.
- Evidence:
  - `scripts/audit_ybby_pair_symmetry.py`
  - `analysis_outputs/source_audit/ybby_pair_symmetry/ybby_pair_symmetry_overlay.jpg`
  - `analysis_outputs/source_audit/ybby_pair_symmetry/ybby_pair_symmetry.md`
  - `analysis_outputs/source_audit/ybby_pair_symmetry/ybby_pair_symmetry.json`
- Scope:
  - Tested whether the locked page-76 `yellow/orange -> black -> black -> yellow/orange` target sequence creates a same-color mirror axis or bracket geometry.
  - No text extraction stream, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Orange pair O4 `buying the dip` -> O5 `shitcoiner at heart`: vector `[-193.5, 764.0]`, angle `104.213` degrees.
  - Black pair B4 `$1 billion` -> G5 `Volcano Bonds`: vector `[435.5, 144.5]`, angle `18.356` degrees.
  - Same-color segment angle delta is `85.857` degrees.
  - Common reflection-axis delta is also `85.857` degrees, so one mirror axis cannot map both same-color pairs.
  - Pair midpoints are `674.174` px apart, so the four anchors do not form a clean 180-degree rotational bracket either.
  - Top-to-bottom, reverse, same-color, and midpoint label streams contain no instruction terms.
- Conclusion:
  - Y-B-B-Y / O-B-B-O is a distinctive page-76 signature and source-comparison guardrail.
  - It is not a standalone mirror/bracket extraction rule.
  - Do not keep inferring local axes from these four anchors unless a new source/clue explicitly names that operation.

### Best Scan Source Lock Refresh

- Status: refreshed; canonical high-res source is settled.
- Evidence:
  - `scripts/audit_best_scan_source_lock_refresh.py`
  - `analysis_outputs/source_audit/best_scan_source_lock_refresh/best_scan_source_lock_refresh.md`
  - `analysis_outputs/source_audit/best_scan_source_lock_refresh/best_scan_source_lock_refresh.json`
- Scope:
  - Verified that the user-supplied Desktop best scan, workspace `magazine.pdf`, and the 3D article map `highresSource` are the same file.
  - No text extraction stream, key candidates, hashing of candidate text, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Desktop best scan, workspace scan, and 3D map high-res source are byte-identical.
  - Shared high-res scan SHA-256: `a0714dcbe503ecdff846f0f77334e2d1d259937d7fe5130258212f24c137716e`.
  - High-res scan metadata: `8` pages, page rotation `180`, page size `610.56 x 783.36 pts`.
  - 3D page derivatives for pages `75-80` are all `2544 x 3264` RGB images.
  - OCR PDF / 3D map `sourcePdf` is a different letter-size PDF with SHA-256 `0078fe23401fab4882303ae038df0de6b439f498acb852d3b226c366caf5ab5c`; keep it as label/navigation evidence only.
- Conclusion:
  - The active source issue is not a local PDF mismatch. The current workspace already uses the Desktop best scan as canonical geometry.
  - Do not reopen local PDF source selection unless a materially different physical scan, original-layout export, or higher-resolution image appears.
  - Further progress still requires new source/original-layout evidence or a clue that names the extraction unit/order.

### Active Label Index Provenance

- Status: checked; mixed label numbers are report handles, not extraction evidence.
- Evidence:
  - `scripts/audit_active_label_index_provenance.py`
  - `analysis_outputs/source_audit/active_label_index_provenance/active_label_index_provenance_overlay.jpg`
  - `analysis_outputs/source_audit/active_label_index_provenance/active_label_index_provenance.md`
  - `analysis_outputs/source_audit/active_label_index_provenance/active_label_index_provenance.json`
- Scope:
  - Tested whether `O4/B4/G5/O5` is a source-backed index system or only an analysis naming layer.
  - No text extraction stream, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `O4` and `O5` are valid local orange-highlight order handles on page 76.
  - `B4` and `G5` are confirmed black/grey DOCM-highlighted active targets, but their numeric suffixes are not derived from a canonical source-side B/G highlight list in the current files.
  - The compact streams `O4B4G5O5`, `4455`, `OBBO`, `63 66 68 73`, `124 131 137 151`, and `b1vs` contain no instruction terms.
- Conclusion:
  - Keep `O4/B4/G5/O5` as analysis/report labels only.
  - Do not use `4455`, `O4B4G5O5`, or mixed B/G/O numbering as key material or a selector unless a new clue explicitly names numbers/indexes.
  - Next useful branch remains a new source/original-layout/physical witness or an external clue that names the extraction unit and order.

### 3D Runtime View Modes

- Status: checked; rendered viewer is a review surface, not an extraction source.
- Evidence:
  - `scripts/audit_3d_runtime_view_modes.py`
  - `analysis_outputs/3d_article_map/runtime_view_modes/runtime_view_modes.md`
  - `analysis_outputs/3d_article_map/runtime_view_modes/runtime_view_modes.json`
  - `analysis_outputs/3d_article_map/runtime_view_modes/fold_page76.png`
- Scope:
  - Rendered the local 3D article map in `spread`, `fold`, `fold + page 76 focus`, and `stack` modes and verified the canvas was nonblank.
  - No text extraction stream, key candidates, hashing, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Reliable screenshots need `--use-angle=swiftshader`; default headless rendering can look blank and should not be used as evidence.
  - The runtime UI exposes only `spread`, `fold`, and `stack`, with `layout` and `focus` URL parameters.
  - The `focus` value is only a display filter. It does not recompute mirror/fold geometry or create a selector.
  - The viewer displays `28` of `40` stored ray selections and reports the expected `16` anchors and `29` mirror boxes.
  - Rendered fold/page-76 review confirms the known overlay/anchor/ray structure but does not reveal a hidden fold selector or new ordering rule.
- Conclusion:
  - Keep the 3D viewer as an orientation and audit surface.
  - Do not promote layout mode, focus state, or screenshot blankness into puzzle signal.
  - Next useful branch remains source evidence: a new clue/source must name the unit/order, or a physical/original-layout image must change the page-76/G5/O5 geometry.

### Page 76 Highlight Edge Selector

- Status: checked; active highlight boundaries are locators, not selectors.
- Evidence:
  - `scripts/audit_page76_highlight_edge_selector.py`
  - `analysis_outputs/source_audit/page76_highlight_edge_selector/page76_highlight_edge_selector.md`
  - `analysis_outputs/source_audit/page76_highlight_edge_selector/page76_highlight_edge_selector.json`
  - `analysis_outputs/source_audit/page76_highlight_edge_selector/page76_highlight_edge_selector_overlay.jpg`
- Scope:
  - Tested whether the active page-76 `O4/B4/G5/O5` boxes select adjacent words or edge-crossing characters at left/right/top/bottom boundaries.
  - No text extraction stream beyond these bounded side/edge checks, key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Adjacent side streams are ordinary surrounding prose:
    - left `he's | - | collateralized | a`
    - right `- | in | to | -`
    - above `on | was | future | trust`
    - below `announced | billions | those | -`
  - Target edge streams are short and non-instructional: first/significant `b$Vs`; last/significant `pnst`.
  - Edge-crossing counts are inconsistent: `O4` `0/0/0/0`, `B4` `0/0/3/0`, `G5` `0/0/0/0`, `O5` `0/0/24/0`.
  - No checked stream contains instruction terms like read/fold/mirror/line/word/letter.
- Conclusion:
  - Do not treat active highlight sides as a standalone selector.
  - Reopen only if a clue names a side or a new physical/original-layout source changes the page-76 edge contacts.
  - Next useful branch remains external/source evidence that names unit/order.

### 3D Ray Backlog

- Status: checked; hidden JSON rays are not missed extraction evidence.
- Evidence:
  - `scripts/audit_3d_ray_backlog.py`
  - `analysis_outputs/3d_article_map/ray_backlog_audit/ray_backlog_audit.md`
  - `analysis_outputs/3d_article_map/ray_backlog_audit/ray_backlog_audit.json`
  - `analysis_outputs/3d_article_map/ray_backlog_audit/ray_backlog_overlay.jpg`
- Scope:
  - Audited the `12` stored ray selections at ranks `29-40`, because the 3D runtime view renders only ranks `1-28`.
  - No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Backlog rays are low-score alternates or reading-order variants of the same pill/black-bar/wire families.
  - Only one backlog ray shares endpoint/mode/threshold with a displayed ray: hidden position `29` mirrors displayed position `28`.
  - Target-term hits are contextual only: `IMF/Novogratz`, `should sell`, and a generic `heart`.
  - No backlog ray contains instruction terms such as read/take/word/letter/edge/font/mirror/key.
  - No backlog selected word intersects active `O4/B4/G5/O5` target boxes.
- Conclusion:
  - Do not promote unrendered 3D ray ranks into puzzle signal.
  - Reopen only if a future clue explicitly points to hidden JSON rays, ranks `29-40`, or a specific ray rank/order.

### 3D Reflection Box Contacts

- Status: checked; direct reflection boxes confirm corridor context but do not select G5/O5.
- Evidence:
  - `scripts/audit_3d_reflection_box_target_overlap.py`
  - `analysis_outputs/3d_article_map/reflection_box_target_overlap/reflection_box_target_overlap.md`
  - `analysis_outputs/3d_article_map/reflection_box_target_overlap/reflection_box_target_overlap.json`
  - `analysis_outputs/3d_article_map/reflection_box_target_overlap/reflection_box_target_overlap_overlay.jpg`
- Scope:
  - Audited all `14` 3D reflection boxes landing on page 76 against locked active targets `O4/B4/G5/O5`.
  - No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Only `79_76_5` directly overlaps an active target, grazing O4 `buying the dip` at about `0.255` of the target box.
  - No direct reflection box overlaps G5 `Volcano Bonds` or O5 `shitcoiner at heart`.
  - Closest reflection-box gaps are still large for G5/O5: G5 `367.17` px, O5 `361.47` px.
  - Reflection texts contain contextual hits (`El Salvador`, `IMF`, `miss buying bitcoin`) but no procedural extraction terms.
  - Empty p79 visual reflection boxes land in far-right/lower art, not active text targets.
- Conclusion:
  - Treat 3D reflection boxes as orientation and corridor evidence only.
  - Do not extract from direct reflection boxes unless a new source transform changes G5/O5 contact or a clue names a specific reflection id.

### 3D Anchor Point Proximity

- Status: checked; anchor points do not directly select active page-76 targets.
- Evidence:
  - `scripts/audit_3d_anchor_point_target_proximity.py`
  - `analysis_outputs/3d_article_map/anchor_point_target_proximity/anchor_point_target_proximity.md`
  - `analysis_outputs/3d_article_map/anchor_point_target_proximity/anchor_point_target_proximity.json`
  - `analysis_outputs/3d_article_map/anchor_point_target_proximity/anchor_point_target_proximity_overlay.jpg`
- Scope:
  - Audited `11` page-76 anchor points from the 3D map against locked active targets `O4/B4/G5/O5`.
  - No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `0` anchors are inside active target boxes.
  - `0` anchors are within `50` px of active target boxes.
  - Closest overall anchor-to-target relation is `p76_dollar` to O5 at `331.29` px.
  - Closest mirrored-pill-to-target relation is p79 pill 3 to O4 at `421.89` px.
  - Nearest-word streams around anchor points are ordinary navigation/OCR labels (`Bitcoin`, `Twitter?`, `IMF`, `he`, `flat`, `chest.`, `guy`, `OVERDOSE`) and contain no extraction terms.
- Conclusion:
  - Treat anchor points as orientation/provenance and ray-construction aids only.
  - Reopen only if a future source transform moves anchors onto active target text or a clue names an anchor order.

### Plain Correction Selector Impact

- Status: checked; correction markup repairs wording but does not supply a selector.
- Evidence:
  - `scripts/audit_plain_correction_selector_impact.py`
  - `analysis_outputs/plain_text_transcript/correction_selector_impact/correction_selector_impact.md`
  - `analysis_outputs/plain_text_transcript/correction_selector_impact/correction_selector_impact.json`
- Scope:
  - Audited the `21` registered plain-text corrections for target/corridor terms and procedural selector terms.
  - No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `3` corrections touch corridor/target terms:
    - O4 punctuation: `"buying the dip".` -> `"buying the dip."`
    - G5 restoration: `collateralized to pay off the IMF` -> `collateralized “Volcano Bonds” to pay off the IMF`
    - context restoration: `requires printing and wars` -> `requires money printing and wars`
  - `0` corrections add procedural selector terms such as read/take/select/word/letter/line/edge/font/mirror/key.
  - The latest raw plain-text article is unsafe for G5 because it omits `Volcano Bonds`; the corrected/DOCM witness restores it.
- Conclusion:
  - Correction markup is text-authority evidence only.
  - Do not treat the correction list as an instruction stream or selector.
  - Use corrected/DOCM text for wording, and require a separate source/clue for unit/order.

### Active Line Unit Reconciliation

- Status: checked; active line/sentence rows are locators, not selectors.
- Evidence:
  - `scripts/audit_active_line_unit_reconciliation.py`
  - `analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.md`
  - `analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json`
- Scope:
  - Reconciled locked `O4/B4/G5/O5` targets across corrected text, canonical sentence rows, page lines, corridor indexes, and DOCM/font states.
  - No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - O4 `buying the dip`: sentence `44`, page line `22`, corridor `4`, state `Y`.
  - B4 `$1 billion`: sentence `45`, page line `25`, corridor `7`, state `K`.
  - G5 `Volcano Bonds`: sentence `45`, page line `27`, corridor `9`, state `K`.
  - O5 `shitcoiner at heart`: sentence `48`, page line `32`, corridor `14`, state `Y`.
  - B4 and G5 share sentence row `45`, so sentence numbering is not a precise four-unit selector.
  - Streams `YKKY`, `22 25 27 32`, `44 45 45 48`, `4 7 9 14`, and gaps `3 2 5` / `1 0 3` contain no instruction hits.
- Conclusion:
  - Treat line/sentence/corridor rows as validation and locator evidence only.
  - Reopen only if a clue explicitly names sentence, line, gap, first/last, or side-word extraction.

### BOLD vs Article Active Corridor

- Status: checked; BOLD does not improve active-corridor source authority.
- Evidence:
  - `scripts/audit_bold_vs_article_active_corridor.py`
  - `analysis_outputs/docm_format_sources/bold_vs_article_active_corridor/bold_vs_article_active_corridor.md`
  - `analysis_outputs/docm_format_sources/bold_vs_article_active_corridor/bold_vs_article_active_corridor.json`
- Scope:
  - Compared `private_inputs/Desktop/BOLD.docm` and `private_inputs/Desktop/Article with Fonts.docm` around locked active targets `O4/B4/G5/O5`.
  - DOCM files were inspected as Word packages only; macros were not executed.
  - No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `Article with Fonts.docm` contains all four active targets: `buying the dip`, `$1 billion`, `Volcano Bonds`, and `shitcoiner at heart`.
  - `BOLD.docm` contains none of the four active targets.
  - `BOLD.docm` is short (`25` paragraphs / `230` words), macro-enabled, and only overlaps context terms such as `IMF`, `Nayib Bukele`, and `IMF loan`.
  - `Article with Fonts.docm` is non-macro and preserves the full corridor with Typeka / Typeka Mix / yellow / black / cyan state.
  - The BOLD-vs-Article difference adds no extraction terms such as read/take/word/letter/line/edge/font/mirror/key.
- Conclusion:
  - `Article with Fonts.docm` remains the trusted DOCM formatting witness.
  - `BOLD.docm` remains a generated/highlighted artifact, not selector permission.
  - Reopen BOLD only if `otrobip.txt` or original workflow/source files are recovered.

### Page-76 Active Highlight Fill

- Status: checked; no hidden fill/residue selector in the current high-res active boxes.
- Evidence:
  - `scripts/audit_page76_active_highlight_fill.py`
  - `analysis_outputs/source_audit/page76_active_highlight_fill/page76_active_highlight_fill.md`
  - `analysis_outputs/source_audit/page76_active_highlight_fill/page76_active_highlight_fill.json`
  - `analysis_outputs/source_audit/page76_active_highlight_fill/page76_active_highlight_fill_sheet.jpg`
- Scope:
  - Inspected scan pixels inside O4/B4/G5/O5 active highlight boxes.
  - Removed ordinary dark glyph/dark-band pixels and checked fill residue for hidden marks or readable ordering symbols.
  - No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - O4 `buying the dip` and O5 `shitcoiner at heart` are ordinary orange/yellow highlighted text in the high-res scan.
  - B4 `$1 billion` and G5 `Volcano Bonds` are ordinary black-highlighted text in the high-res scan.
  - O4 has `5` counted large residual components, but they sit on highlight/glyph-edge bands in the review sheet rather than forming free-standing symbols.
  - B4/G5 leave no separate residual components after the dark band is accounted for.
  - O5 leaves only tiny residual specks, consistent with print/compression/edge noise.
- Conclusion:
  - Do not treat active highlight fill texture, residue, or dark-band pixels as a standalone selector under the current high-res scan.
  - Reopen only with a different physical/original scan or an explicit clue naming fill, ink, residue, noise, or hidden marks.

### Page-76 Highlight Spill Direction

- Status: checked; marker spill/tail direction does not choose a side/order.
- Evidence:
  - `scripts/audit_page76_highlight_spill_direction.py`
  - `analysis_outputs/source_audit/page76_highlight_spill_direction/page76_highlight_spill_direction.md`
  - `analysis_outputs/source_audit/page76_highlight_spill_direction/page76_highlight_spill_direction.json`
  - `analysis_outputs/source_audit/page76_highlight_spill_direction/page76_highlight_spill_direction_sheet.jpg`
- Scope:
  - Inspected a `28` px margin around O4/B4/G5/O5 for high-res scan-visible marker spill, tails, underlines, or side bias.
  - No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - Dominant-side stream in target order is `RRRB`.
  - Per-target side-strength streams are `RBLT | RBLT | RLBT | BTLR`.
  - These strings do not produce a readable selector and do not contain procedural terms.
  - Visual review shows the side counts are caused by adjacent punctuation/prose and box placement, not a repeated marker-tail grammar.
  - There is no arrow, tail, underline, or stable side cue that chooses first/last/left/right extraction.
- Conclusion:
  - Do not treat active-highlight spill direction as a standalone selector under the current high-res scan.
  - Reopen only if a different physical/original scan changes the visible spill geometry or a clue explicitly names marker spill/tail/side direction.

### Page-76 Spill Control Comparison

- Status: checked; active spill/tail behavior is not unique against page-76 controls.
- Evidence:
  - `scripts/audit_page76_spill_control_comparison.py`
  - `analysis_outputs/source_audit/page76_spill_control_comparison/page76_spill_control_comparison.md`
  - `analysis_outputs/source_audit/page76_spill_control_comparison/page76_spill_control_comparison.json`
  - `analysis_outputs/source_audit/page76_spill_control_comparison/page76_spill_control_comparison_sheet.jpg`
- Scope:
  - Compared O4/B4/G5/O5 side-spill measurements against six other page-76 orange/grey highlight controls.
  - No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.
- Findings:
  - `10` records were checked: `4` active and `6` controls.
  - Overall dominant-side counts are `{'bottom': 6, 'top': 1, 'right': 3}`.
  - Overall side-order counts are `{'BTLR': 3, 'TBRL': 1, 'BLRT': 1, 'RBLT': 2, 'BLTR': 1, 'BTRL': 1, 'RLBT': 1}`.
  - Active orders are `BTRL`, `RBLT`, `RLBT`, and `BTLR`; `BTLR` and `RBLT` also occur in controls.
  - The review sheet shows ordinary phrase/crop geometry, adjacent prose, punctuation, and text-band edges rather than a repeated marker-tail selector.
- Conclusion:
  - Do not treat page-76 active spill uniqueness as a standalone selector under the current high-res scan.
  - Side-spill remains useful only as a future-source comparison benchmark.

### Missing-Rule Frontier Refresh

- Status: refreshed; current local evidence still lacks extraction permission.
- Evidence:
  - `scripts/audit_missing_rule_frontier.py`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Re-synthesized the report stack after the latest page-76 highlight fill/spill/control checks, BOLD-vs-DOCM audit, line-unit reconciliation, correction audit, and 3D reflection/anchor checks.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Dead/deferred branch bullets now total `218`.
  - Top target evidence remains O5 `shitcoiner at heart` (`15` score / `5` independent layers), G5 `Volcano Bonds` (`11` / `4`), and the lower page-76 El Salvador/IMF/Bukele/Mike/trust corridor (`6` / `4`).
  - `24` focused local checks are now represented in the closed-for-current-scan local-permutation bucket.
  - The latest checks do not name a unit/order such as word, letter, line, edge, font, right, heart, or sell.
- Conclusion:
  - Page 76 lower corridor remains the validation surface, not solved key material.
  - The next legitimate unlock must be source/physical/original-layout validation or external clue wording that explicitly names the selector.

### Desktop Best-Scan Pixel Lock

- Status: checked; local PDF/source-image/3D source chain is locked.
- Evidence:
  - `scripts/audit_desktop_best_scan_pixel_lock.py`
  - `analysis_outputs/source_audit/desktop_best_scan_pixel_lock/desktop_best_scan_pixel_lock.md`
  - `analysis_outputs/source_audit/desktop_best_scan_pixel_lock/desktop_best_scan_pixel_lock.json`
  - `analysis_outputs/source_audit/desktop_best_scan_pixel_lock/desktop_best_scan_pixel_lock_sheet.jpg`
- Scope:
  - Compared `private_inputs/Desktop/magazine.pdf`, workspace `magazine.pdf`, `analysis_outputs/source_images`, and the readable/upright 3D page cache.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Desktop and workspace PDFs are byte-identical.
  - Article pages `75-80` map to PDF pages `3-8`; the first two PDF pages are the opening spread.
  - Fresh embedded-page extraction matches `source_images` in native orientation for every checked page.
  - The 3D upright cache matches that same extraction after `rot180` within JPEG-resave tolerance for every checked page.
  - Page 76 and page 79 geometry are therefore based on the user-supplied best scan, not an older OCR/source branch.
- Conclusion:
  - Do not reopen local PDF source selection unless a materially different physical scan, original-layout export, or higher-resolution source appears.
  - OCR PDF coordinates remain label/navigation evidence only.

### Opening Spread Instruction Surface

- Status: checked; opener pages `73-74` provide provenance/order evidence but no visible extraction instruction.
- Evidence:
  - `scripts/audit_opening_spread_instruction_surface.py`
  - `analysis_outputs/source_audit/opening_spread_instruction_surface/opening_spread_instruction_surface.md`
  - `analysis_outputs/source_audit/opening_spread_instruction_surface/opening_spread_instruction_surface.json`
  - `analysis_outputs/source_audit/opening_spread_instruction_surface/opening_spread_instruction_surface_sheet.jpg`
- Scope:
  - Manually inventoried visible opener surfaces from the locked best scan: labels, page numbers, the five-capsule motif, and Max/dollar-field art.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Visible text/objects are `OVERDOSE`, `with Max Keiser`, `Bitcoin Magazine | El Salvador`, page numbers `73/74`, five orange-white capsules, and Max with dollar bills in an El Salvador field.
  - Surface streams (`visibleText`, `visibleTextNoRepeats`, initials, endings, `73 74`, `5`, and `73 74 5`) contain no read/take/select/word/letter/line/mirror/fold/key/private instruction terms.
  - The five-capsule sequence remains real and Issue-24-specific, but the opener does not say how to turn it into page-76 extraction material.
- Conclusion:
  - Do not treat the opening spread as a standalone selector under the current scan.
  - Keep opener pages only as provenance/source-validation evidence unless a future clue names capsules, opener pages, page numbers, or the opening spread directly.

### Typeka Instruction Surface

- Status: checked; Typeka font-state runs do not visibly name an extraction unit/order.
- Evidence:
  - `scripts/audit_typeka_instruction_surface.py`
  - `analysis_outputs/docm_format_sources/typeka_instruction_surface/typeka_instruction_surface.md`
  - `analysis_outputs/docm_format_sources/typeka_instruction_surface/typeka_instruction_surface.json`
- Scope:
  - Scanned non-regular Typeka runs from the `Article with Fonts.docm` witness: Typeka Mix and bold Typeka.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Checked `115` Typeka-bold runs and `47` Typeka Mix runs.
  - Found `9` ordinary prose hits for tempting instruction-like words: `up`, `left`, `right`, `one`, `zero`, `first`, `see`, and `take`.
  - Found `0` strong instruction records because none of those hits is paired with a concrete unit such as `word`, `letter`, `line`, `page`, `font`, `mirror`, `fold`, `reverse`, `key`, `private`, `seed`, or `address`.
  - The page-76 corridor terms remain present in the expected font-state runs, but those runs still explain emphasis/provenance rather than extraction.
- Conclusion:
  - Do not treat Typeka Mix or Typeka-bold text as a standalone instruction surface under the current DOCM witness.
  - Keep Typeka as a formatting witness unless a separate clue names a font state, first/last letters, or another exact unit/order.

### P79 Take-All-Energy Selector

- Status: checked; tempting `right/take` phrase lands on ordinary upper p76 grey prose under the current scan.
- Evidence:
  - `scripts/audit_p79_take_all_energy_selector.py`
  - `analysis_outputs/source_audit/p79_take_all_energy_selector/p79_take_all_energy_selector.md`
  - `analysis_outputs/source_audit/p79_take_all_energy_selector/p79_take_all_energy_selector.json`
  - `analysis_outputs/source_audit/p79_take_all_energy_selector/p79_take_all_energy_selector_sheet.jpg`
- Scope:
  - Tested p79 highlighted phrase `That's right, Bitcoin will take all the energy.` as a single source selector through the existing high-res horizontal mirror onto p76.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Source wording contains `right` and `take`, so it is a reasonable candidate to audit.
  - Current mirror landing is p76 upper grey `Gotta be this way... post-1971 fiat money` plus a small graze on `nonsense`.
  - It does not land on the lower page-76 El Salvador / IMF / `Volcano Bonds` / `shitcoiner at heart` corridor.
  - The literal right-side words are ordinary article prose and contain no extraction unit such as word, letter, line, key, private, seed, or address.
- Conclusion:
  - Do not treat p79 `That's right, Bitcoin will take all the energy` as a standalone current-scan selector.
  - Reopen only if a new source/physical transform moves this phrase onto the lower page-76 corridor or a clue explains the unit/order.

### Issue 24 Physical Page Topology

- Status: checked; page topology recorded as a guardrail for future fold/hold-to-light work.
- Evidence:
  - `scripts/audit_issue24_physical_page_topology.py`
  - `analysis_outputs/source_audit/issue24_physical_page_topology/issue24_physical_page_topology.md`
  - `analysis_outputs/source_audit/issue24_physical_page_topology/issue24_physical_page_topology.json`
  - `analysis_outputs/source_audit/issue24_physical_page_topology/issue24_physical_page_topology_sheet.jpg`
- Scope:
  - Mapped PDF pages `1-8` to magazine pages `73-80` and classified page parity, same-leaf pairs, and facing spreads.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Same-leaf front/back candidates are `73/74`, `75/76`, `77/78`, and `79/80`.
  - Facing-spread candidates in this scan are `74/75`, `76/77`, and `78/79`.
  - The strong `78 -> 76` and `79 -> 76` page-76 signals are not literal same-leaf or facing-spread relationships under normal magazine pagination.
- Conclusion:
  - Do not treat `78/79 -> 76` as proof of physical bleed-through under the current scan.
  - Keep those links as visual registration/orientation evidence unless a new physical/original-layout source changes the transform.

### P75/P76 Valid Same-Leaf Recheck

- Status: checked; the only valid same-leaf path into page 76 does not supply the lower-corridor selector.
- Evidence:
  - `scripts/audit_p75_p76_valid_leaf_recheck.py`
  - `analysis_outputs/source_audit/p75_p76_valid_leaf_recheck/p75_p76_valid_leaf_recheck.md`
  - `analysis_outputs/source_audit/p75_p76_valid_leaf_recheck/p75_p76_valid_leaf_recheck.json`
  - `analysis_outputs/source_audit/p75_p76_valid_leaf_recheck/p75_p76_valid_leaf_recheck_sheet.jpg`
- Scope:
  - Rechecked `75 -> 76` only, because page 75 and page 76 are the true front/back sides of one article leaf.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Raw hflip has `0` meaningful target intersections.
  - Best bounded translation dx=`0`, dy=`-180` creates only `2` upper-page hits into p76 grey `Gotta be this way... post-1971 fiat money`.
  - The lower page-76 El Salvador / IMF / `Volcano Bonds` / `shitcoiner at heart` corridor is not reached.
  - Trusted O5/G5 physical validation remains `0` overlaps.
- Conclusion:
  - Do not treat `75 -> 76` hold-to-light as a current-scan selector.
  - Reopen only if a materially different physical scan/photo or original-layout export changes the registration.

### P78 Source Graphic Instruction Surface

- Status: checked; p78 source graphic text is registration/provenance evidence, not a visible instruction.
- Evidence:
  - `scripts/audit_p78_source_graphic_instruction_surface.py`
  - `analysis_outputs/source_audit/p78_source_graphic_instruction_surface/p78_source_graphic_instruction_surface.md`
  - `analysis_outputs/source_audit/p78_source_graphic_instruction_surface/p78_source_graphic_instruction_surface.json`
  - `analysis_outputs/source_audit/p78_source_graphic_instruction_surface/p78_source_graphic_instruction_surface_sheet.jpg`
- Scope:
  - Inspected the p78 pull-quote/frame source object before its mirror/reflection onto page 76.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Manual visible text is `The economy of love is infinitely more efficient than hate and war.`.
  - The text contains thematic terms (`economy`, `love`, `efficient`, `hate`, `war`) but no extraction terms such as `read`, `take`, `word`, `letter`, `line`, `mirror`, `fold`, `key`, or `private`.
  - Source-side OCR/3D labels inside the graphic are unreliable graphic-text artifacts and add no instruction unit.
  - The p78 frame still validates the lower p76 corridor through the dx=`-38` tri-contact benchmark, but the source text itself does not say what to extract.
- Conclusion:
  - Do not treat p78 pull-quote wording as standalone key material or an instruction surface under the current scan.
  - Keep it only as p76 lower-corridor registration/orientation evidence.

### Missing-Rule Frontier Refresh

- Status: refreshed; local selector search is paused unless a new clue/source changes the rule space.
- Evidence:
  - `scripts/audit_missing_rule_frontier.py`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Re-synthesized the current state after the latest physical-topology, p75/p76 same-leaf, p78 source-graphic, p79 `right/take`, opener, Typeka, O-B-B-O, 3D fold-order, and p78 contact-role closures.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Closed/deferred branch bullets now total `225`.
  - The strongest target evidence remains O5 `shitcoiner at heart`, G5 `Volcano Bonds`, and the lower El Salvador/IMF/Bukele/Mike/trust corridor.
  - `34` focused local checks are now represented in the closed-for-current-scan bucket.
  - Current scan/source chain is internally locked, but local source geometry still lacks the extraction unit/order.
- Conclusion:
  - Treat page 76 lower corridor as validation surface only.
  - Highest-value next move is source/physical/original-layout validation or external clue wording that explicitly names the selector.

### Source Reopen Requirements

- Status: checked; explicit gate created for deciding when extraction is allowed to resume.
- Evidence:
  - `scripts/audit_source_reopen_requirements.py`
  - `analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.md`
  - `analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json`
  - `analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements_sheet.jpg`
- Scope:
  - Converted the latest source/physical frontier into a concrete checklist.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Reopen requires `R1-R5`: source identity, target preservation, unit/order evidence, orientation discipline, and controlled benchmark improvement.
  - Required validation targets are O5 `shitcoiner at heart`, G5 `Volcano Bonds`, O-B-B-O (`buying the dip`, `$1 billion`, `Volcano Bonds`, `shitcoiner at heart`), and the page-76 priority crop pack.
  - Acceptable new evidence is a true physical scan/photo, original layout/export/source asset, or external clue/provenance wording that names the unit/order.
  - The same `magazine.pdf`, resaved screenshots, OCR-PDF coordinate geometry, 3D viewer state alone, broad crypto checks, and more local G5/O5 permutations are not enough.
- Conclusion:
  - Do not resume extraction from current-scan derivatives alone.
  - Score any new source against the reopen checklist before trying a selector or key path.

### Frontier Gate Refresh

- Status: refreshed; the missing-rule frontier now points directly to the source-reopen requirements.
- Evidence:
  - `scripts/audit_missing_rule_frontier.py`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Findings:
  - Closed/deferred branch bullets now total `227`.
  - Page 76 O5/G5 target evidence remains the strongest surface, but extraction is still blocked by the missing unit/order.
  - The active source/physical path must use `analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.md` and pass `R1-R5`.
- Conclusion:
  - Continue only with source/physical/original-layout validation or external clue wording that names the selector.

### Source-Reopen Candidate Intake

- Status: checked; no local file currently passes the source-reopen gate.
- Evidence:
  - `scripts/audit_source_reopen_candidate_intake.py`
  - `analysis_outputs/source_audit/source_reopen_candidate_intake/source_reopen_candidate_intake.md`
  - `analysis_outputs/source_audit/source_reopen_candidate_intake/source_reopen_candidate_intake.json`
  - Refreshed support reports:
    - `analysis_outputs/source_audit/local_source_candidate_inventory/local_source_candidate_inventory.md`
    - `analysis_outputs/source_audit/source_delta_watch/source_delta_watch.md`
- Scope:
  - Scored already-local source candidates against `R1-R5`.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Local inventory records: `45`.
  - Source delta watch candidates: `61`.
  - Actionable unknown source candidates: `0`.
  - Comparison PDFs promoted for Issue 24 geometry: `0`.
  - Screenshots promoted: `0`.
  - All local source classes are blocked, with the shared hard blocker still `R3`: no local source/clue names the extraction unit/order.
- Conclusion:
  - Already-local files should not reopen extraction.
  - Keep `magazine.pdf` as baseline geometry, `Article with Fonts.docm` as formatting witness, and comparison PDFs as style-only controls.

### Frontier Refresh After Source Intake

- Status: refreshed; top-level frontier now includes the local source-intake block.
- Evidence:
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Findings:
  - Closed/deferred branch bullets now total `228`.
  - Source/physical registration remains open only for genuinely new material; already-local files did not pass R1-R5.
- Conclusion:
  - Next dependency remains physical/original-layout/source provenance or external clue wording that names the extraction unit/order.

### External Clue Unit/Order Intake

- Status: checked; archived raw/raw-like external clues do not name the extraction unit/order.
- Evidence:
  - `scripts/audit_external_clue_unit_order_intake.py`
  - `analysis_outputs/external_clues/external_clue_unit_order_intake/external_clue_unit_order_intake.md`
  - `analysis_outputs/external_clues/external_clue_unit_order_intake/external_clue_unit_order_intake.json`
- Scope:
  - Separated raw/raw-like clue text from generated analysis prose.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Raw/raw-like records: `5`.
  - Raw/raw-like `R3` passes: `0`.
  - Announcement wording gives private-key/source/value only.
  - Schott gives mirror-writing operation family only.
  - Canva gives orientation/source-fidelity wording only; `line` is geometric (`line up`, `in line with`), not a line selector.
  - Generated report prose containing `word`, `letter`, `read`, or `select` is not source evidence.
- Conclusion:
  - Do not reopen extraction from archived external clue wording.
  - Treat archived external clues as constraints until new raw clue/provenance wording appears.

### Frontier Refresh After External Clue Intake

- Status: refreshed; top-level frontier now includes the strict archived-clue block.
- Evidence:
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Findings:
  - Closed/deferred branch bullets now total `229`.
  - External clue/provenance path remains open only for new raw material, not archived local clue text.
- Conclusion:
  - Source/physical/original-layout evidence or a new raw clue naming unit/order remains the only high-value path.

### P80 Package R3 Gate Synthesis

- Status: checked; p80 package copy is closed as a current-scan selector.
- Evidence:
  - `scripts/audit_p80_package_r3_gate_synthesis.py`
  - `analysis_outputs/source_audit/p80_package_r3_gate_synthesis/p80_package_r3_gate_synthesis.md`
  - `analysis_outputs/source_audit/p80_package_r3_gate_synthesis/p80_package_r3_gate_synthesis.json`
  - `analysis_outputs/source_audit/p80_package_r3_gate_synthesis/p80_package_r3_gate_synthesis_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Consolidated package copy, five symptoms, relief/removal, dose numbers, p79/p80 interaction, four-anchor choice, and p80->p76 geometry against `R1-R5`.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - `5 SYMPTOM RELIEF` remains real count/theme evidence for the five-unit model.
  - Explicit extraction terms on p80 package copy: `0`.
  - P80->p76 anchor geometry has `0` positive overlap rows.
  - Dose numbers and action/theme words corroborate OVERDOSE/BTC/SHITCOINS theming but do not name a word/letter/line/edge/font unit.
  - Closed/deferred branch bullets now total `230`.
- Conclusion:
  - Keep p80 as C6 count/theme/source-validation evidence only.
  - Reopen only with new physical/original-layout registration evidence or a raw clue explicitly naming package/symptom/dose/relief text as the selector.

### Typeka / Font-State R3 Gate Synthesis

- Status: checked; Typeka/font-state is closed as a current-scan selector.
- Evidence:
  - `scripts/audit_typeka_font_r3_gate_synthesis.py`
  - `analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis.md`
  - `analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis.json`
  - `analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Consolidated Typeka instruction-surface, lower-corridor font-state, manual bold disambiguation, repaired-frame contact states, transition/boundary reports, and DOCM/visual consistency against `R1-R5`.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - `Article with Fonts.docm` remains the font authority; manual Markdown bold is annotation only.
  - Typeka/font states corroborate the active page-76 corridor and the repaired `R-K-Y` trio (`should sell | Volcano Bonds | shitcoiner at heart`).
  - Strong Typeka instruction records: `0`.
  - Unit-without-action records: `0`.
  - Repaired-frame/font streams have no instruction hits.
  - Closed/deferred branch bullets now total `231`.
- Conclusion:
  - Keep Typeka as formatting/corridor/source-validation evidence only.
  - Reopen only if a raw clue explicitly names font/Typeka/Mix/bold as the selector, or if new source geometry selects exact font-run units.

### 3D Fold / Mirror Geometry R3 Gate Synthesis

- Status: checked; folded/mirrored 3D geometry is closed as a current-scan selector.
- Evidence:
  - `scripts/audit_3d_fold_mirror_r3_gate_synthesis.py`
  - `analysis_outputs/3d_article_map/fold_mirror_r3_gate_synthesis/fold_mirror_r3_gate_synthesis.md`
  - `analysis_outputs/3d_article_map/fold_mirror_r3_gate_synthesis/fold_mirror_r3_gate_synthesis.json`
  - `analysis_outputs/3d_article_map/fold_mirror_r3_gate_synthesis/fold_mirror_r3_gate_synthesis_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Consolidated reflected graph, exact high-res reflection geometry, mirror-read rule, two-hand streams, reflection boxes, anchors, fold ordering, runtime view modes, and selector-intersection evidence against `R1-R5`.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Page 76 remains strongly confirmed as the target surface: `17` medium/strong page-76 reflected edges.
  - Source-pair support is balanced: `78->76: 8`, `79->76: 9`.
  - Two-hand unit/order hits: `0` (`3` weak semantic/directional term hits).
  - Direct reflection-box active-target overlaps: `1`, only an O4 `buying the dip` graze.
  - Anchors inside/near active O4/B4/G5/O5 targets: `0/0`.
  - Fold/runtime view modes are orientation/review layers, not extraction rules.
  - Closed/deferred branch bullets now total `232`.
- Conclusion:
  - Keep 3D geometry as locator/orientation/source-validation evidence only.
  - Reopen only with new physical/original-layout registration evidence or a raw clue naming reflection id, anchor order, fold contact, word, line, or letter.

### Page-76 Highlight Cluster R3 Gate Synthesis

- Status: checked; page-76 O-B-B-O highlight cluster is closed as a current-scan selector.
- Evidence:
  - `scripts/audit_page76_highlight_cluster_r3_gate_synthesis.py`
  - `analysis_outputs/source_audit/page76_highlight_cluster_r3_gate_synthesis/page76_highlight_cluster_r3_gate_synthesis.md`
  - `analysis_outputs/source_audit/page76_highlight_cluster_r3_gate_synthesis/page76_highlight_cluster_r3_gate_synthesis.json`
  - `analysis_outputs/source_audit/page76_highlight_cluster_r3_gate_synthesis/page76_highlight_cluster_r3_gate_synthesis_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Consolidated target convergence, next-target chooser, edge contacts, fill residue, spill/tail direction, spill controls, color-swap, lower marks, and priority crops against `R1-R5`.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Active pattern is `O-B-B-O`: `buying the dip` / `$1 billion` / `Volcano Bonds` / `shitcoiner at heart`.
  - O5/L32 remains the primary future-source target; G5/L27 remains the required paired target.
  - Edge selector instruction hits: `0`.
  - Fill residue exposes no readable hidden word/symbol/order mark.
  - Spill/tail side bias is not unique against controls.
  - Color-swap points to the upper page-76 cluster, not the lower G5/O5 pair.
  - Closed/deferred branch bullets now total `233`.
- Conclusion:
  - Keep O4/B4/G5/O5 as target-location/source-validation evidence only.
  - Reopen only with a raw clue naming side/edge/fill/spill/color/word/line/letter or with new physical/original-layout contact changes.

### Comparison / OVERDOSE Layout R3 Gate Synthesis

- Status: checked; comparison/OVERDOSE layout mechanics are closed as a current-scan selector.
- Evidence:
  - `scripts/audit_comparison_overdose_layout_r3_gate_synthesis.py`
  - `analysis_outputs/comparison_articles/overdose_layout_r3_gate_synthesis/overdose_layout_r3_gate_synthesis.md`
  - `analysis_outputs/comparison_articles/overdose_layout_r3_gate_synthesis/overdose_layout_r3_gate_synthesis.json`
  - `analysis_outputs/comparison_articles/overdose_layout_r3_gate_synthesis/overdose_layout_r3_gate_synthesis_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Consolidated comparison layout, OVERDOSE style uniqueness, body highlighter grammar, comparison PDF source gate, capsule recurrence, priority-crop comparison, and `bitcoin4` witness evidence against `R1-R5`.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Comparison PDFs promoted for Issue 24 extraction geometry: `0`.
  - Independent comparison PDFs kept style-only: `3`.
  - Independent strong five-point capsule-sequence recurrences: `0`.
  - Low-res Issue 24 witness five-point recurrences in `bitcoin4`: `2`.
  - `bitcoin4` partially overlaps O5 but leaves G5 `84.098px` away, so it does not repair the G5/O5 registration benchmark.
  - Issue 24 remains visually distinctive against the comparison controls, but the comparison layer supplies no word/letter/line/font/edge/fold unit or order.
  - Closed/deferred branch bullets now total `234`.
- Conclusion:
  - Keep comparison PDFs as style controls, provenance checks, and future-source validation evidence only.
  - Reopen only if a raw clue explicitly references another issue/article/layout motif, or if materially better source/original-layout evidence passes `R1-R5` and names/supplies the extraction unit/order.

### Active Evidence Unlock Matrix

- Status: checked; the aggregate current evidence stack is not sufficient to resume extraction/key checks.
- Evidence:
  - `scripts/audit_active_evidence_unlock_matrix.py`
  - `analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix.md`
  - `analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix.json`
  - `analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Rolled up current local sources, archived/raw clues, page-76 target surface, 3D fold/mirror geometry, page-76 O-B-B-O highlights, Typeka/font state, p80 package/OVERDOSE, and comparison OVERDOSE layouts against `R1-R5`.
  - No key candidates, hashes, seed phrases, WIF checks, address checks, OCR extraction, or broad brute force were generated.
- Findings:
  - Paths checked: `8`.
  - R3 fail count: `8`; every active path still lacks a source-backed extraction unit/order.
  - R5 fail count: `7`.
  - Top targets remain O5 `shitcoiner at heart`, G5 `Volcano Bonds`, and the lower El Salvador/IMF/Bukele/Mike/trust corridor.
  - Minimum useful unlocks remain C3 extraction unit, C4 physical registration, C8 source image quality, and C2 p78 frame signature.
  - Closed/deferred branch bullets now total `235`.
- Conclusion:
  - Keep the current evidence stack as locator/provenance/source-validation evidence only.
  - Do not resume extraction or key checking unless new source/clue evidence passes `R1-R5`, especially R3 unit/order evidence.

### Post-Unlock Source Arrival Watch

- Status: checked; no new local source/clue arrival was found after the unlock matrix.
- Evidence:
  - `scripts/audit_post_unlock_source_arrival_watch.py`
  - `analysis_outputs/source_audit/post_unlock_source_arrival_watch/post_unlock_source_arrival_watch.md`
  - `analysis_outputs/source_audit/post_unlock_source_arrival_watch/post_unlock_source_arrival_watch.json`
  - `analysis_outputs/source_audit/post_unlock_source_arrival_watch/post_unlock_source_arrival_watch_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Bounded scan of Desktop, Downloads, and Documents outside the workspace for recent source/clue files.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Lookback window: `90` minutes.
  - Candidate files needing R1-R5 review: `0`.
  - Low-priority recent/named files: `0`.
  - Desktop/Downloads/Documents scan found no new material that could reopen source or unit/order evidence.
  - Closed/deferred branch bullets now total `236`.
- Conclusion:
  - No current-scan selector or key check is reopened.
  - Continue to require new physical/original-layout/source material or raw clue wording that passes `R1-R5`.

### Source Acquisition Target Packet

- Status: created; this is the current handoff checklist for the only high-value open path.
- Evidence:
  - `scripts/audit_source_acquisition_target_packet.py`
  - `analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.md`
  - `analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.json`
  - `analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Converts the current blocker into a physical/original-layout/raw-clue acquisition checklist.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - No current selector was unlocked.
  - Active target priority remains L32/O5 `shitcoiner at heart`, L27/G5 `Volcano Bonds`, and L26 `future bitcoin earnings`.
  - Packet acquisition jobs:
    - flat physical pages 75-80;
    - held-to-light/front-back leaf pairs 75/76, 77/78, 79/80 plus relevant spreads;
    - page-76 lower corridor closeups;
    - original layout/export for pages 73-80;
    - exact raw clue wording/screenshots/URLs/timestamps.
  - Required benchmark improvements remain C3 extraction unit/order, C2 p78-frame signature, C4 physical registration, and C8 source image quality.
  - Closed/deferred branch bullets remain `236`; this packet is not a dead-branch closure.
- Conclusion:
  - Use this packet before evaluating any new source/clue item.
  - Do not resume extraction or key checking until new material passes `R1-R5`, especially R3.

### Source Acquisition Packet Integrity

- Status: checked; the future-evidence handoff packet is complete and internally consistent.
- Evidence:
  - `scripts/audit_source_acquisition_packet_integrity.py`
  - `analysis_outputs/source_audit/source_acquisition_packet_integrity/source_acquisition_packet_integrity.md`
  - `analysis_outputs/source_audit/source_acquisition_packet_integrity/source_acquisition_packet_integrity.json`
  - `analysis_outputs/source_audit/source_acquisition_packet_integrity/source_acquisition_packet_integrity_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Verified source-acquisition handoff integrity before any future physical/original-layout/raw-clue comparison.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Integrity status: `PASS`.
  - Critical artifacts present: `20/20`.
  - Packet visual panels present: `8/8`; missing panels: `0`.
  - Capture jobs present: `5`.
  - R-gate coverage: `R1, R2, R3, R4, R5`.
  - Benchmark coverage: `C2, C3, C4, C8`.
  - Active targets and orientation guardrails are present.
  - Current evidence remains blocked: unlock matrix still fails R3, and post-unlock arrival watch still has `0` review candidates.
- Conclusion:
  - Use the packet as the first-stop gate when new physical/original-layout/raw clue material appears.
  - This pass does not unlock a current-scan selector and does not change the dead-branch count (`236`).

### Future Source Scoring Rubric

- Status: created; future physical/original-layout/raw-clue material now has explicit R1-R5 acceptance thresholds.
- Evidence:
  - `scripts/audit_future_source_scoring_rubric.py`
  - `analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric.md`
  - `analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric.json`
  - `analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Converted active page-76 target, p78 tri-contact, p77 near-miss, source-reopen, and packet-integrity evidence into a scoring rubric.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - `R1`: source must be materially distinct from the byte-locked current scan.
  - `R2`: source must preserve/explain O5, G5, L26-L29, and the O-B-B-O corridor.
  - `R3`: source/raw clue must name or visibly supply unit/order; this remains mandatory.
  - `R4`: orientation must be explicit; 3D/crop layer is upright, source_images/fresh PDF extraction need 180-degree rotation.
  - `R5`: source must improve a compact benchmark naturally, not by arbitrary shift.
  - Numeric benchmarks fixed for future comparison:
    - p78 current G5 gap: `38.0px`.
    - p78 repair dx: `-40.0`, tri-contact pass `true`.
    - p77 near-miss gap: `71.93px`; median line pitch: `73.73px`.
- Conclusion:
  - Use the rubric with the source-acquisition packet before any future selector/key attempt.
  - This pass does not unlock a current-scan selector and does not change the dead-branch count (`236`).

### Future Source Rubric Current-Stack Dry Run

- Status: checked; the new rubric does not reopen already-local evidence.
- Evidence:
  - `scripts/audit_future_source_rubric_current_stack_dry_run.py`
  - `analysis_outputs/source_audit/future_source_rubric_current_stack_dry_run/future_source_rubric_current_stack_dry_run.md`
  - `analysis_outputs/source_audit/future_source_rubric_current_stack_dry_run/future_source_rubric_current_stack_dry_run.json`
  - `analysis_outputs/source_audit/future_source_rubric_current_stack_dry_run/future_source_rubric_current_stack_dry_run_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Dry-ran the future-source rubric against the current eight-path evidence stack.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Paths checked: `8`.
  - Extraction-ready paths: `0`.
  - Strict R3 pass count: `0`.
  - R3 fail count: `8`.
  - Soft locator/corroboration/provenance evidence remains insufficient without R3 unit/order evidence.
- Conclusion:
  - Current stack fails the future-source rubric; no selector was unlocked.
  - This pass does not change the dead-branch count (`236`).
  - Apply the packet/rubric only to new physical/original-layout/raw clue material.

### Page-76 Target Text Authority Lock

- Status: checked; exact page-76 target text authority is locked to clean witnesses.
- Evidence:
  - `scripts/audit_page76_target_text_authority_lock.py`
  - `analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/page76_target_text_authority_lock.md`
  - `analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/page76_target_text_authority_lock.json`
  - `analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/page76_target_text_authority_lock_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked page-76 target phrases across canonical plain text, DOCM text, raw plain text, Markdown transcript, and annotated transcript.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Canonical plain, DOCM text, and Markdown transcript each preserve `10/10` target phrases.
  - Raw user plain text preserves `9/10` and omits G5 `Volcano Bonds`.
  - Annotated transcript preserves `9/10`; inline notes interrupt exact prose, so it remains a format/highlight witness.
  - The correction that restores `Volcano Bonds` affects the active corridor but adds no selector permission.
- Conclusion:
  - Use canonical plain text, DOCM text, and Markdown transcript as exact page-76 target wording authority.
  - Keep raw plain text as context only and annotated transcript as format/highlight witness.
  - No selector was unlocked; dead-branch count remains `236`.

### Page-76 Target Format Authority Lock

- Status: checked; page-76 target formatting authority is locked to DOCM/high-res witnesses.
- Evidence:
  - `scripts/audit_page76_target_format_authority_lock.py`
  - `analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.md`
  - `analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json`
  - `analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Separated real page-76 font/highlight evidence from Markdown bold markup and annotated transcript notes.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Active color pattern: `OBBO`; visual-state order: `YKKY`.
  - Active page lines: `22 25 27 32`; corridor indexes: `4 7 9 14`.
  - All four active targets are DOCM `Typeka` with bold fraction `1.0`.
  - High-res visual highlight consistency confirms exact matches for `4/4` active targets.
  - Crop-pack/manual-box evidence covers `3/4` active targets; `buying the dip` remains visual-consistency only.
  - Nearby `Typeka Mix` phrases, including `I don't really trust that guy`, are context only.
- Conclusion:
  - Use DOCM runs, high-res visual highlight consistency, and page-76 crop pack/manual boxes as format authority.
  - Keep Markdown bold as transcript markup and the annotated transcript as a format witness.
  - No selector was unlocked; dead-branch count remains `236`.

### Markdown-DOCM Mismatch Instruction Surface

- Status: checked; Markdown bold mismatches do not supply a page-76 selector.
- Evidence:
  - `scripts/audit_markdown_docm_mismatch_instruction_surface.py`
  - `analysis_outputs/docm_format_sources/markdown_docm_mismatch_instruction_surface/markdown_docm_mismatch_instruction_surface.md`
  - `analysis_outputs/docm_format_sources/markdown_docm_mismatch_instruction_surface/markdown_docm_mismatch_instruction_surface.json`
  - `analysis_outputs/docm_format_sources/markdown_docm_mismatch_instruction_surface/markdown_docm_mismatch_instruction_surface_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Sequentially aligned the user Markdown bold spans to DOCM run text and checked the page-76 corridor mismatch streams.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Markdown bold spans parsed: `230`; aligned to DOCM: `229`; unaligned: `1`.
  - Page-76 corridor Markdown bold spans: `18`.
  - Corridor Markdown-only/not-DOCM-bold spans: `13`.
  - Markdown-only stream: `lv d i e N v z I d e ll u h u`.
  - Highlighted-aligned stream: `“buying the dip.” shitcoiner at heart.`
  - DOCM-only active target stream: `$1 billion Volcano Bonds`.
  - Instruction-term hits across tested mismatch streams: `0`.
- Conclusion:
  - Keep Markdown bold as annotation/transcript markup, not source typography.
  - Keep DOCM/high-res as the active formatting authority.
  - The Markdown-vs-DOCM mismatch selector branch is closed for the current scan; dead-branch count is now `237`.

### Page-76 Active Target Crop Completion

- Status: created; the O4/B4/G5/O5 visual crop packet is complete.
- Evidence:
  - `scripts/build_page76_active_target_crop_completion.py`
  - `analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.md`
  - `analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json`
  - `analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Built a complete O4/B4/G5/O5 crop authority sheet from the high-res upright page-76 image.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Crop coverage improved from `3/4` to `4/4`.
  - Active color pattern remains `OBBO`; visual-state order remains `YKKY`.
  - Page lines remain `22 25 27 32`; corridor indexes remain `4 7 9 14`.
  - O4 `buying the dip` is now explicitly cropped from `p76_orange_4`.
  - B4 `$1 billion` uses direct full-page visual boxing because the old projected grey box is known wrong.
  - G5 `Volcano Bonds` and O5 `shitcoiner at heart` reuse the newer priority/manual boxes.
- Conclusion:
  - Use this sheet as visual source-comparison authority for future physical/original-layout/source material.
  - It completes the packet but does not unlock a selector; dead-branch count remains `237`.

### Source Packet Crop Authority Sync

- Status: checked; current handoff pair is now explicit.
- Evidence:
  - `scripts/audit_source_packet_crop_authority_sync.py`
  - `analysis_outputs/source_audit/source_packet_crop_authority_sync/source_packet_crop_authority_sync.md`
  - `analysis_outputs/source_audit/source_packet_crop_authority_sync/source_packet_crop_authority_sync.json`
  - `analysis_outputs/source_audit/source_packet_crop_authority_sync/source_packet_crop_authority_sync_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked whether the source-acquisition packet reflects the completed O4/B4/G5/O5 crop authority.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Sync status: `PASS_WITH_SUPPLEMENTAL_APPENDIX`.
  - Historical source-acquisition packet still passes integrity and remains valid as the jobs/gates checklist.
  - Historical packet still points at the older priority-crop panel and does not itself include the completed 4/4 crop sheet.
  - Completed active crop coverage is `4/4`; all target crop files are present.
  - Old projected p76 grey boxes remain blocked for B4/G5 geometry.
- Conclusion:
  - Use the source-acquisition packet for capture jobs and `R1-R5` gates.
  - Use the completed O4/B4/G5/O5 crop sheet as active page-76 visual comparison authority.
  - No selector was unlocked; dead-branch count remains `237`.

### Page-76 Active Crop Orientation Guardrail

- Status: checked; active crop boxes are locked to readable/upright orientation.
- Evidence:
  - `scripts/audit_page76_active_crop_orientation_guardrail.py`
  - `analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/page76_active_crop_orientation_guardrail.md`
  - `analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/page76_active_crop_orientation_guardrail.json`
  - `analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/page76_active_crop_orientation_guardrail_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Verified the completed O4/B4/G5/O5 crop boxes in readable/upright coordinates and documented the native source-image transform.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Upright and native page-76 images are both `2544x3264`.
  - Native rotated 180 vs upright mean absolute difference is `0.2859`; direct native vs upright mean absolute difference is `27.6479`.
  - All upright boxes and all native-transform boxes are in bounds.
  - Native `source_images` / fresh extraction need the recorded 180-degree transform before O4/B4/G5/O5 comparison.
  - Native rot180 boxes are O4 `[743, 1039, 1210, 1087]`, B4 `[1853, 819, 2116, 866]`, G5 `[1348, 672, 1749, 720]`, and O5 `[883, 282, 1504, 332]`.
- Conclusion:
  - Use upright crop boxes only in the readable/upright frame.
  - Normalize future source comparisons before applying active target boxes.
  - No selector was unlocked; dead-branch count remains `237`.

### Page-76 Active Order Orientation Trap

- Status: checked; color/visual-state order is not enough to validate orientation.
- Evidence:
  - `scripts/audit_page76_active_order_orientation_trap.py`
  - `analysis_outputs/source_audit/page76_active_order_orientation_trap/page76_active_order_orientation_trap.md`
  - `analysis_outputs/source_audit/page76_active_order_orientation_trap/page76_active_order_orientation_trap.json`
  - `analysis_outputs/source_audit/page76_active_order_orientation_trap/page76_active_order_orientation_trap_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared readable/upright O4/B4/G5/O5 order against native unnormalized top-to-bottom order.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Readable/upright order is `O4 -> B4 -> G5 -> O5`.
  - Native unnormalized order is `O5 -> G5 -> B4 -> O4`.
  - Color pattern `OBBO` and visual-state pattern `YKKY` are both palindromes, so they cannot detect a 180-degree flip.
  - Line order detects the flip: `22 25 27 32` vs `32 27 25 22`.
  - Corridor order detects the flip: `4 7 9 14` vs `14 9 7 4`.
- Conclusion:
  - Use `OBBO/YKKY` as quartet identity evidence only, not orientation proof.
  - Future source matches must preserve readable line/corridor order after orientation normalization.
  - No selector was unlocked; dead-branch count remains `237`.

### Typeka Comparison Metadata Gate

- Status: checked; local comparison PDFs cannot prove/disprove Typeka usage by metadata.
- Evidence:
  - `scripts/audit_typeka_comparison_metadata_gate.py`
  - `analysis_outputs/comparison_articles/typeka_comparison_metadata_gate/typeka_comparison_metadata_gate.md`
  - `analysis_outputs/comparison_articles/typeka_comparison_metadata_gate/typeka_comparison_metadata_gate.json`
  - `analysis_outputs/comparison_articles/typeka_comparison_metadata_gate/typeka_comparison_metadata_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Gated the Typeka comparison-article claim against local PDF and DOCM metadata.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Independent comparison PDFs checked: `3`.
  - Embedded font witnesses in those comparison PDFs: `0`.
  - Embedded Typeka resources in those comparison PDFs: `0`.
  - Image-only/raster comparison PDFs: `3`.
  - `Article with Fonts.docm` records `7451` Typeka-family characters and remains the only local Typeka font witness.
  - Issue 24 `magazine.pdf` exposes Helvetica OCR/text-layer fonts only, not visible printed Typeka typography.
- Conclusion:
  - Use comparison PDFs as visual/style controls only.
  - Use `Article with Fonts.docm` as the Typeka formatting witness, not as extraction permission.
  - Typeka remains blocked on R3 unit/order evidence; no selector was unlocked and dead-branch count remains `237`.

### Active O-B-B-O Quartet Recurrence

- Status: checked; the active lower page-76 quartet is distinctive against local independent controls.
- Evidence:
  - `scripts/audit_active_obbo_quartet_recurrence.py`
  - `analysis_outputs/comparison_articles/active_obbo_quartet_recurrence/active_obbo_quartet_recurrence.md`
  - `analysis_outputs/comparison_articles/active_obbo_quartet_recurrence/active_obbo_quartet_recurrence.json`
  - `analysis_outputs/comparison_articles/active_obbo_quartet_recurrence/active_obbo_quartet_recurrence_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Scanned existing line-shaped orange/dark highlighter detections for consecutive top-to-bottom `OBBO` windows matching O4/B4/G5/O5 placement.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, or broad brute force were generated.
- Findings:
  - Active O4/B4/G5/O5 y-ratios: `0.674326 0.741881 0.786765 0.905944`.
  - Page records scanned: `29`.
  - Independent control sources: `bitcoin3`, `issue26`, `issue27`.
  - Total `OBBO` windows: `3`; all occur in Issue 24.
  - Independent-control `OBBO` windows: `0`.
  - Active-like windows: Issue 24 `1`, independent controls `0`.
- Conclusion:
  - The lower page-76 `OBBO` placement is not a generic local OVERDOSE body-highlighter pattern.
  - Keep O4/B4/G5/O5 as distinctive target-location/source-validation evidence only.
  - No selector was unlocked; dead-branch count remains `237`.

### BOLD.docm Source Gate

- Status: checked; BOLD.docm is generated-artifact evidence, not active-corridor source authority.
- Evidence:
  - `scripts/audit_bold_docm_source_gate.py`
  - `analysis_outputs/docm_format_sources/bold_docm_source_gate/bold_docm_source_gate.md`
  - `analysis_outputs/docm_format_sources/bold_docm_source_gate/bold_docm_source_gate.json`
  - `analysis_outputs/docm_format_sources/bold_docm_source_gate/bold_docm_source_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Consolidated macro provenance, active target coverage, and Word-format authority for `BOLD.docm` vs `Article with Fonts.docm`.
  - No macros, OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - `BOLD.docm` has a VBA project and VBA data.
  - `BOLD.docm` contains `0/4` locked active targets.
  - `Article with Fonts.docm` contains `4/4` locked active targets.
  - The macro-referenced `otrobip.txt` remains unrecovered locally.
  - `BOLD.docm` has `230` words versus `1281` in `Article with Fonts.docm`.
- Conclusion:
  - Use `Article with Fonts.docm` as the Word formatting witness.
  - Use `BOLD.docm` only as generated-artifact sanity evidence unless the missing word list or original workflow files are recovered.
  - No selector was unlocked; dead-branch count remains `237`.

### BOLD.docm Highlighted Text Reconstruction

- Status: checked; reconstructed BOLD highlighted words do not unlock a selector.
- Evidence:
  - `scripts/audit_bold_highlighted_text_reconstruction.py`
  - `analysis_outputs/docm_format_sources/bold_highlighted_text_reconstruction/bold_highlighted_text_reconstruction.md`
  - `analysis_outputs/docm_format_sources/bold_highlighted_text_reconstruction/bold_highlighted_text_reconstruction.json`
  - `analysis_outputs/docm_format_sources/bold_highlighted_text_reconstruction/bold_highlighted_text_reconstruction_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Reconstructed the yellow-highlighted text in `BOLD.docm` from the Word run layer.
  - No macros, OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Yellow-highlighted runs: `43`.
  - Highlighted words: `43`.
  - Highlighted font/bold state: all `Typeka` and bold.
  - Locked active targets in BOLD full text: `0/4`.
  - Locked active targets in highlighted stream: `0/4`.
  - `IMF loan` is only a partial context overlap: `loan` is highlighted, but `IMF` is not.
  - Instruction-like highlighted terms are `right`, `one`, and `loan`, with no paired word/letter/line/font/order instruction.
- Conclusion:
  - Keep the BOLD highlighted stream classified as generated-artifact evidence only.
  - Do not promote it as source authority or selector permission unless `otrobip.txt` or original workflow files are recovered and pass R1-R5.
  - No selector was unlocked; dead-branch count remains `237`.

### 3D Active Quartet Box OCR Gate

- Status: checked; 3D target-box OCR is geometry/navigation evidence only, not exact text authority.
- Evidence:
  - `scripts/audit_3d_active_quartet_box_ocr_gate.py`
  - `analysis_outputs/3d_article_map/active_quartet_box_ocr_gate/active_quartet_box_ocr_gate.md`
  - `analysis_outputs/3d_article_map/active_quartet_box_ocr_gate/active_quartet_box_ocr_gate.json`
  - `analysis_outputs/3d_article_map/active_quartet_box_ocr_gate/active_quartet_box_ocr_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked stored 3D OCR characters and word labels inside the exact O4/B4/G5/O5 active target boxes.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Targets checked: `4`.
  - Exact OCR-box matches: `0/4`.
  - Corrupted/misread target boxes: `4`.
  - Effectively blank target boxes: `1` (`G5 Volcano Bonds`).
  - 3D target metadata preserves readable order: page lines `22 25 27 32`, corridor indexes `4 7 9 14`.
  - Box OCR examples:
    - O4 `buying the dip` -> `ByiiREeraipy"`.
    - B4 `$1 billion` -> `eis`.
    - G5 `Volcano Bonds` -> blank.
    - O5 `shitcoiner at heart` -> `siukbeodmensertslveaarty`.
- Conclusion:
  - Use the 3D map for geometry/navigation/source-registration only.
  - Use DOCM/plain text/manual crop review for exact target wording.
  - No selector was unlocked; dead-branch count remains `237`.

### P80 Numeric Active-Order Gate

- Status: checked; p80 numbers do not explain the active O4/B4/G5/O5 order.
- Evidence:
  - `scripts/audit_p80_numeric_active_order_gate.py`
  - `analysis_outputs/source_audit/p80_numeric_active_order_gate/p80_numeric_active_order_gate.md`
  - `analysis_outputs/source_audit/p80_numeric_active_order_gate/p80_numeric_active_order_gate.json`
  - `analysis_outputs/source_audit/p80_numeric_active_order_gate/p80_numeric_active_order_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared visible p80 package numbers against locked O4/B4/G5/O5 page-line/corridor order.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Raw p80 numbers: `5,100,5,16,473,6,473,80`.
  - Canonical p80 numbers excluding clipped volume duplicate: `5,100,5,16,473,80`.
  - Active page lines: `22 25 27 32`.
  - Active corridor indexes: `4 7 9 14`.
  - Active line/corridor gaps: `3 2 5`.
  - Exact sequence successes: `0`.
  - Ordered subsequence successes: `0`.
  - Repeated `5` remains the only strong direct number link, and it supports the broader five-symptom/five-highlight model rather than the four-anchor active quartet.
- Conclusion:
  - Keep p80 numeric copy as C6 count/theme/source-validation evidence only.
  - Do not promote package numbers as an active quartet selector unless a raw clue/source names page line, corridor index, dose, volume, or symptom number as the unit.
  - No selector was unlocked; dead-branch count remains `237`.

### Active Quartet Capsule-Direction Gate

- Status: checked; the p73/p79 `RRLL` capsule zigzag does not select an instruction-bearing O4/B4/G5/O5 boundary stream.
- Evidence:
  - `scripts/audit_active_quartet_capsule_direction_gate.py`
  - `analysis_outputs/source_audit/active_quartet_capsule_direction_gate/active_quartet_capsule_direction_gate.md`
  - `analysis_outputs/source_audit/active_quartet_capsule_direction_gate/active_quartet_capsule_direction_gate.json`
  - `analysis_outputs/source_audit/active_quartet_capsule_direction_gate/active_quartet_capsule_direction_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Applied the shared `RRLL` direction signature only to active target side words and above/below neighbor words.
  - Checked active order, reverse order, horizontal outgoing/incoming, and vertical outgoing/incoming modes.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Direction modes checked: `8`.
  - Instruction hit count: `0`.
  - Active page lines remain `22 25 27 32`; active corridor indexes remain `4 7 9 14`.
  - Horizontal streams include `in collateralized a`, `he's to`, `to he's`, and `a collateralized in`.
  - Vertical streams include `announced billions future trust`, `on was those`, `those was on`, and `trust future billions announced`.
- Conclusion:
  - Keep `RRLL` and the five-index pattern as locator/provenance evidence only.
  - Do not promote capsule direction as an active quartet side-word or vertical-neighbor selector unless raw clue/source wording names that unit.
  - No selector was unlocked; dead-branch count remains `237`.

### Active Punctuation / Enclosure Gate

- Status: checked; quote/dollar/period mechanics are exact-text authority, not a selector.
- Evidence:
  - `scripts/audit_active_punctuation_enclosure_gate.py`
  - `analysis_outputs/plain_text_transcript/active_punctuation_enclosure_gate/active_punctuation_enclosure_gate.md`
  - `analysis_outputs/plain_text_transcript/active_punctuation_enclosure_gate/active_punctuation_enclosure_gate.json`
  - `analysis_outputs/plain_text_transcript/active_punctuation_enclosure_gate/active_punctuation_enclosure_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected punctuation/enclosure around locked O4/B4/G5/O5 phrases in the authoritative active lines.
  - Cross-checked active-corridor correction rows for punctuation/quote changes.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Class stream: `quote+period | dollar | quote | period`.
  - Class initials: `QP D Q P`.
  - Punctuation-directed edge stream: `bp $ Vs t`.
  - Phrase edge stream: `bp $n Vs st`.
  - Active punctuation corrections: `2`.
  - Instruction hit count: `0`.
- Conclusion:
  - O4 quote+period, B4 dollar amount, G5 quotes, and O5 period preserve exact source text and should be checked in future source comparisons.
  - Do not promote punctuation/enclosure as extraction permission unless raw clue/source wording names quote, dollar, punctuation, first/last, or edge extraction.
  - No selector was unlocked; dead-branch count remains `237`.

### Active Font-Edge Transition Gate

- Status: checked; active O4/B4/G5/O5 targets are regular-Typeka insulated, not Typeka Mix-adjacent.
- Evidence:
  - `scripts/audit_active_font_edge_transition_gate.py`
  - `analysis_outputs/docm_format_sources/active_font_edge_transition_gate/active_font_edge_transition_gate.md`
  - `analysis_outputs/docm_format_sources/active_font_edge_transition_gate/active_font_edge_transition_gate.json`
  - `analysis_outputs/docm_format_sources/active_font_edge_transition_gate/active_font_edge_transition_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected immediate DOCM run-level font states before and after locked active highlighted targets.
  - Compared active target edges against the page-76 non-regular Typeka/Typeka Mix clusters.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Target state stream: `YKKY`.
  - Edge pattern stream: `R>Y>R | R>K>R | R>K>R | R>Y>R`.
  - Left-exit word stream: `he's mine collateralized a`.
  - Right-entry word stream: `I in to Meanwhile`.
  - Active Typeka Mix neighbor count: `0`.
  - Active edges all regular-insulated: `true`.
  - Instruction hit count: `0`.
- Conclusion:
  - Typeka Mix remains nearby semantic/context formatting (`El Salvador`, `Mike Novogratz`, `trust that guy`), not an immediate side selector for the active quartet.
  - Keep active font-edge transitions as source-comparison guardrails only unless a raw clue/source names Typeka Mix, font boundary, left/right run edge, or font-state extraction.
  - No selector was unlocked; dead-branch count remains `237`.

### OVERDOSE Header Registration Gate

- Status: checked; repeated `OVERDOSE` header/layout registration is not a current-scan selector.
- Evidence:
  - `scripts/audit_overdose_header_registration_gate.py`
  - `analysis_outputs/source_audit/overdose_header_registration_gate/overdose_header_registration_gate.md`
  - `analysis_outputs/source_audit/overdose_header_registration_gate/overdose_header_registration_gate.json`
  - `analysis_outputs/source_audit/overdose_header_registration_gate/overdose_header_registration_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared the p78 source graphic frame against page 76 using current horizontal mirror, same-layout/no-mirror placement, and p78->p76 `OVERDOSE` header-center translation.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Header translation is tiny: `dx=-10.68`, `dy=3.51`, so it is effectively the same-layout slot.
  - Current horizontal mirror hits active targets as `0` full + `1` partial (`O5`), with `0` strict unit hits.
  - Same-layout/no-mirror hits active targets as `2` full (`B4_text`, `G5`) + `1` partial (`O5`), with `0` strict unit hits.
  - OVERDOSE-header translation gives the same active-target result: `B4_text`, `G5`, partial `O5`, and `0` strict unit hits.
- Conclusion:
  - Same-layout/header registration is a secondary source-comparison benchmark, not extraction permission.
  - It misses O4 and supplies no source-backed unit/order term.
  - No selector was unlocked; dead-branch count remains `237`.

### OVERDOSE Same-Slot Control Gate

- Status: checked; the p78 pull-quote same-layout slot is a source-comparison control, not a selector.
- Evidence:
  - `scripts/audit_overdose_same_slot_control_gate.py`
  - `analysis_outputs/source_audit/overdose_same_slot_control_gate/overdose_same_slot_control_gate.md`
  - `analysis_outputs/source_audit/overdose_same_slot_control_gate/overdose_same_slot_control_gate.json`
  - `analysis_outputs/source_audit/overdose_same_slot_control_gate/overdose_same_slot_control_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Placed the p78 source graphic frame at the same page coordinates across pages 75-79.
  - Compared the page-76 same-layout slot against the current page-76 horizontal mirror frame.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Same-layout frame: `[294.0, 2398.0, 1310.0, 2950.0]`.
  - P76 horizontal mirror frame: `[1234.0, 2398.0, 2250.0, 2950.0]`.
  - P76 same-layout slot hits active targets: `one_billion`, `volcano_bonds`, `shitcoiner_heart`.
  - P76 same-layout hard instruction hits: `0`.
  - P76 horizontal mirror hits active targets: `shitcoiner_heart`.
  - P76 horizontal mirror hard instruction hits: `0`.
- Conclusion:
  - Same-slot geometry explains why B4/G5/O5 are useful future validation targets, but it misses O4 and does not name a unit/order.
  - Keep it as a source-comparison control only unless future original-layout/source material explicitly names repeated layout, same position, or page-slot transfer.
  - No selector was unlocked; dead-branch count remains `237`.

### Active Typeka Mix Proximity Gate

- Status: checked; nearby Typeka Mix islands do not form a one-to-one selector for O4/B4/G5/O5.
- Evidence:
  - `scripts/audit_active_mix_proximity_gate.py`
  - `analysis_outputs/docm_format_sources/active_mix_proximity_gate/active_mix_proximity_gate.md`
  - `analysis_outputs/docm_format_sources/active_mix_proximity_gate/active_mix_proximity_gate.json`
  - `analysis_outputs/docm_format_sources/active_mix_proximity_gate/active_mix_proximity_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked previous, next, and nearest Typeka Mix groups around the locked active targets.
  - Used existing page-76 DOCM signal groups and active target line/corridor metadata.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Triplet initials: `EbM E$M EVM Is-`.
  - Nearest Mix usage: `El Salvador: 2`, `Mike Novogratz: 1`, `I don't really trust that guy.: 1`.
  - O4, B4, and G5 share the same Mix bracket: previous `El Salvador`, next `Mike Novogratz`.
  - O5 has previous `I don't really trust that guy.` and no next Mix group.
  - One-to-one Mix map: `false`.
  - Instruction hit count: `0`.
- Conclusion:
  - Typeka Mix proximity is corridor/source-comparison evidence, not a selector.
  - The Mix islands are shared semantic anchors around the El Salvador/Mike/trust corridor, not four independent pointers.
  - No selector was unlocked; dead-branch count remains `237`.

### Active Quartet Pair-Symmetry Gate

- Status: checked; the palindromic `OBBO` / `YKKY` target order does not form a current-scan fold/mirror selector.
- Evidence:
  - `scripts/audit_active_quartet_pair_symmetry_gate.py`
  - `analysis_outputs/source_audit/active_quartet_pair_symmetry_gate/active_quartet_pair_symmetry_gate.md`
  - `analysis_outputs/source_audit/active_quartet_pair_symmetry_gate/active_quartet_pair_symmetry_gate.json`
  - `analysis_outputs/source_audit/active_quartet_pair_symmetry_gate/active_quartet_pair_symmetry_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Paired O4/O5 as the outer orange targets and B4/G5 as the inner black targets.
  - Tested horizontal fold, vertical fold, point reflection, and p78 same-layout/current-mirror frame midpoint relations.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active pattern remains `OBBO` / `YKKY`, line order `22 25 27 32`, corridor order `4 7 9 14`.
  - Horizontal fold max error: `436.0px`.
  - Vertical fold max error: `756.0px`.
  - Point-reflection midpoint spread: `686.69px`.
  - Best p78-frame midpoint relation is same-layout slot to B4/G5 midpoint at `180.92px`, outside the one-line `73.73px` tolerance.
  - Current p78-to-p76 mirror frame best relation is O4/O5 midpoint at `298.52px`.
- Conclusion:
  - Pair symmetry is visual validation/context only, not extraction permission.
  - B4/G5 has a near-X relation to the p78 same-layout frame, but the vertical miss keeps it from becoming a rule.
  - Reopen only if source wording names color-pair folding, pair midpoints, or an axis.
  - No selector was unlocked; dead-branch count remains `237`.

### Active Frame-Center Reflection Gate

- Status: checked; p78 same-layout/current-mirror frame centers do not turn O4/B4/G5/O5 into a reflection selector.
- Evidence:
  - `scripts/audit_active_frame_center_reflection_gate.py`
  - `analysis_outputs/source_audit/active_frame_center_reflection_gate/active_frame_center_reflection_gate.md`
  - `analysis_outputs/source_audit/active_frame_center_reflection_gate/active_frame_center_reflection_gate.json`
  - `analysis_outputs/source_audit/active_frame_center_reflection_gate/active_frame_center_reflection_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Projected locked O4/B4/G5/O5 boxes through p78 same-layout and current-mirror frame centers.
  - Tested point reflection, vertical-axis reflection, and horizontal-axis reflection.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Same-layout frame center: `[802.0, 2674.0]`.
  - Current-mirror frame center: `[1742.0, 2674.0]`.
  - Six scenarios produced `24` projections; `22` remain in bounds.
  - Hard instruction hits: `0`.
  - Active-target re-hits: `2` total, `0` strong.
  - Maximum active-target re-hit overlap: `0.198042`.
  - The only active re-hits are weak partial B4/O5 contacts under same-layout point reflection.
  - Landing previews are ordinary prose fragments such as `he's a`, `bunch to his Wall`, `collateralized`, `Maybe`, and `that he should sell`.
- Conclusion:
  - Frame-center reflection is a layout/source-comparison guardrail only.
  - Reopen only if source wording names center reflection, frame-center axis, or same-slot frame flipping.
  - No selector was unlocked; dead-branch count remains `237`.

### Active Frame Edge/Axis Gate

- Status: checked; p78 same-layout/current-mirror frame edges and centerlines do not select O4/B4/G5/O5.
- Evidence:
  - `scripts/audit_active_frame_edge_axis_gate.py`
  - `analysis_outputs/source_audit/active_frame_edge_axis_gate/active_frame_edge_axis_gate.md`
  - `analysis_outputs/source_audit/active_frame_edge_axis_gate/active_frame_edge_axis_gate.json`
  - `analysis_outputs/source_audit/active_frame_edge_axis_gate/active_frame_edge_axis_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested left, right, top, bottom, center-x, and center-y lines for the p78 same-layout frame and current p78-to-p76 mirror frame.
  - Compared those lines against locked O4/B4/G5/O5 target boxes and touched page-76 words.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Same-layout frame: `[294.0, 2398.0, 1310.0, 2950.0]`.
  - Current mirror frame: `[1234.0, 2398.0, 2250.0, 2950.0]`.
  - Lines checked: `12`.
  - Active target contacts: `6` total, `3` strong.
  - Strong contacts:
    - `same_layout_center_x` -> G5 `Volcano Bonds`.
    - `same_layout_top` -> B4 `$1 billion`.
    - `current_mirror_bottom` -> O5 `shitcoiner at heart`.
  - Line-hit stream: `same_layout_left=>- | same_layout_right=>shitcoiner_heart | same_layout_center_x=>volcano_bonds | same_layout_top=>one_billion | same_layout_bottom=>shitcoiner_heart | same_layout_center_y=>- | current_mirror_left=>shitcoiner_heart | current_mirror_right=>- | current_mirror_center_x=>- | current_mirror_top=>- | current_mirror_bottom=>shitcoiner_heart | current_mirror_center_y=>-`.
  - Hard instruction hits: `0`.
- Conclusion:
  - Frame lines are useful layout/source-comparison landmarks, not extraction permission.
  - Same-layout lines reproduce the known B4/G5/O5 same-slot contacts and still miss O4; current-mirror lines mostly clip O5.
  - Reopen only if source wording names frame edge, centerline, axis, or boundary reading.
  - No selector was unlocked; dead-branch count remains `237`.

### Active O4 Frame-Rescue Gate

- Status: checked; O4 can be recovered by a clean three-line extension of the dual p78 frame envelope, but this remains source-comparison evidence only.
- Evidence:
  - `scripts/audit_active_o4_frame_rescue_gate.py`
  - `analysis_outputs/source_audit/active_o4_frame_rescue_gate/active_o4_frame_rescue_gate.md`
  - `analysis_outputs/source_audit/active_o4_frame_rescue_gate/active_o4_frame_rescue_gate.json`
  - `analysis_outputs/source_audit/active_o4_frame_rescue_gate/active_o4_frame_rescue_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured how much the p78 same-layout frame, current mirror frame, and their combined left/right envelope must expand to recover all four active targets.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Same-layout frame: `[294.0, 2398.0, 1310.0, 2950.0]`.
  - Current mirror frame: `[1234.0, 2398.0, 2250.0, 2950.0]`.
  - Dual-frame envelope: `[294.0, 2398.0, 2250.0, 2950.0]`.
  - Line-pitch benchmark: `73.73px`.
  - The dual envelope already hits B4 `$1 billion`, G5 `Volcano Bonds`, and O5 `shitcoiner at heart`.
  - Full O4 recovery from the dual envelope needs top expansion `221.0px`, or `2.9974` line pitches.
  - Extending the dual envelope upward by exactly three line pitches hits all four active targets and fully covers O4/B4/G5 while still clipping O5.
  - Full coverage of O5 as well would require an extra `32.0px` bottom expansion.
- Conclusion:
  - This is a compact future source/original-layout validation benchmark.
  - It is not extraction permission because it uses the union of two p78-derived frames plus an extra top extension, and no current raw clue/source wording names that operation.
  - Reopen only if source wording names reading above the frame, extending the frame, or a three-line offset.
  - No selector was unlocked; dead-branch count remains `237`.

### O4 Frame-Rescue Offset Control

- Status: checked; the three-line O4 recovery is the minimum top-only line offset but not a standalone selector.
- Evidence:
  - `scripts/audit_o4_frame_rescue_offset_control.py`
  - `analysis_outputs/source_audit/o4_frame_rescue_offset_control/o4_frame_rescue_offset_control.md`
  - `analysis_outputs/source_audit/o4_frame_rescue_offset_control/o4_frame_rescue_offset_control.json`
  - `analysis_outputs/source_audit/o4_frame_rescue_offset_control/o4_frame_rescue_offset_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Control-tested the dual p78 frame envelope against top-only line offsets `0..6`.
  - Also checked a bounded top/bottom grid `0..6` by `0..3`.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Dual-frame envelope: `[294.0, 2398.0, 2250.0, 2950.0]`.
  - Line-pitch benchmark: `73.73px`.
  - Minimum integer top-only offset that touches all four active targets: `3` line pitches.
  - Top-only offsets that touch all four active targets: `[3, 4, 5, 6]`.
  - No top-only offset in the checked range fully covers all four active targets.
  - Minimum full-coverage grid offset: top `3`, bottom `1`, total `4` line pitches.
- Conclusion:
  - `3-up` is a clean minimum benchmark, but not unique once larger top extensions are allowed.
  - `3-up / 1-down` is the compact full-coverage source-validation benchmark.
  - Reopen only if source wording names line-pitch frame extension, above/below frame reading, or a three-up/one-down offset.
  - No selector was unlocked; dead-branch count remains `237`.

### O4 Frame-Rescue Content Gate

- Status: checked; the `3-up / 1-down` full-coverage frame does not isolate the active quartet.
- Evidence:
  - `scripts/audit_o4_frame_rescue_content_gate.py`
  - `analysis_outputs/source_audit/o4_frame_rescue_content_gate/o4_frame_rescue_content_gate.md`
  - `analysis_outputs/source_audit/o4_frame_rescue_content_gate/o4_frame_rescue_content_gate.json`
  - `analysis_outputs/source_audit/o4_frame_rescue_content_gate/o4_frame_rescue_content_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested whether the compact full-coverage envelope from the offset control isolates only O4/B4/G5/O5.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Full-coverage frame: `[294.0, 2176.81, 2250.0, 3023.73]`.
  - Included line range: `22-32`; corridor range: `4-14`.
  - Included words: `102`; active-target words: `10`; non-target words: `92`.
  - Active-target word density: `0.098`.
  - Non-active highlight entries: `4`.
  - Non-active bold-context lines: `5`.
  - Hard instruction hits: `0`.
- Conclusion:
  - The frame remains useful as a future source/original-layout validation benchmark.
  - It is not a current-scan selector because it captures the broad lower-corridor prose band, not only the active quartet.
  - Reopen only if source wording names a content unit/order for the frame, such as a line, word, letter, edge, or above/below-frame read.
  - No selector was unlocked; dead-branch count remains `237`.

### O4 Frame-Rescue Signal-Stream Gate

- Status: checked; the styled stream inside the `3-up / 1-down` frame is compact but still not an isolation selector.
- Evidence:
  - `scripts/audit_o4_frame_rescue_signal_stream_gate.py`
  - `analysis_outputs/source_audit/o4_frame_rescue_signal_stream_gate/o4_frame_rescue_signal_stream_gate.md`
  - `analysis_outputs/source_audit/o4_frame_rescue_signal_stream_gate/o4_frame_rescue_signal_stream_gate.json`
  - `analysis_outputs/source_audit/o4_frame_rescue_signal_stream_gate/o4_frame_rescue_signal_stream_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Filtered the full-coverage frame through the existing page-76 Typeka/font/highlight signal order.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Full-coverage frame: `[294.0, 2176.81, 2250.0, 3023.73]`.
  - Frame signal groups: `8`.
  - Frame layer-code stream: `YBKKBMMY`.
  - Active signal groups: `4`; active layer-code stream: `YKKY`.
  - Non-active signal groups: `4`; non-active layer-code stream: `BBMM`.
  - Non-active styled groups: `President Nayib Bukele`, `IMF loan`, `Mike Novogratz`, and `I don't really trust that guy.`.
  - Hard instruction hits: `0`.
- Conclusion:
  - The styled stream contains the active quartet but does not isolate it.
  - Reopen only if source wording names `Y/K/M/B`, Typeka style layers, or an exact styled-group order.
  - No selector was unlocked; dead-branch count remains `237`.

### O4 Frame-Rescue Y/K Filter Control

- Status: checked; `Y/K` inside the rescue frame isolates the active quartet, but it remains source-validation evidence only.
- Evidence:
  - `scripts/audit_o4_frame_rescue_yk_filter_control.py`
  - `analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control.md`
  - `analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control.json`
  - `analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Control-tested the `Y/K` color/style filter inside the full-coverage rescue frame against the full page-76 signal stream.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Full-page signal layer codes: `YBMMMKBMYKMYBKKBMMY`.
  - Full-page `Y/K` group count: `8`; full-page `Y/K` layer codes: `YKYKYKKY`.
  - Full-page `Y/K` non-active controls: `4`.
  - Frame signal layer codes: `YBKKBMMY`.
  - Frame `Y/K` layer codes: `YKKY`.
  - Frame `Y/K` active target coverage: `4/4`.
  - Frame `Y/K` non-active groups: `0`.
  - Hard instruction hits: `0`.
- Conclusion:
  - The `Y/K + frame` intersection cleanly recovers O4/B4/G5/O5, but it is not source-backed extraction permission.
  - Reopen only if source wording names orange/black, `Y/K`, highlighted colors, or frame-intersection filtering.
  - No selector was unlocked; dead-branch count remains `237`.

### O4 Frame Y/K Unit-Order Gate

- Status: checked; the isolated `Y/K + frame` quartet still lacks a source-backed unit/order rule.
- Evidence:
  - `scripts/audit_o4_frame_yk_unit_order_gate.py`
  - `analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/o4_frame_yk_unit_order_gate.md`
  - `analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/o4_frame_yk_unit_order_gate.json`
  - `analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/o4_frame_yk_unit_order_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked bounded unit/order streams from only the four `Y/K + frame` targets.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Isolated target count: `4`.
  - Group/vertical target order: `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart`.
  - Left-to-right target order: `one_billion -> volcano_bonds -> shitcoiner_heart -> buying_dip`.
  - Group-order layer codes: `YKKY`.
  - Page lines: `22 25 27 32`; corridor indexes: `4 7 9 14`.
  - Group index gaps: `2 1 4`; page/corridor gaps: `3 2 5`.
  - Bounded streams checked: `20`.
  - Hard instruction hits: `0`.
  - Source-backed unit/order: `false`.
- Conclusion:
  - The quartet is a strong locator but not key material.
  - Group/vertical order and left-to-right order disagree unless an external order is assumed.
  - Reopen only if source wording names a unit and order, such as group order, line order, word, letter, edge, or x-order.
  - No selector was unlocked; dead-branch count remains `237`.

### Source Packet Y/K Frame Benchmark Sync

- Status: checked; supplemental source-validation benchmark added, no selector unlocked.
- Evidence:
  - `scripts/audit_source_packet_yk_frame_benchmark_sync.py`
  - `analysis_outputs/source_audit/source_packet_yk_frame_benchmark_sync/source_packet_yk_frame_benchmark_sync.md`
  - `analysis_outputs/source_audit/source_packet_yk_frame_benchmark_sync/source_packet_yk_frame_benchmark_sync.json`
  - `analysis_outputs/source_audit/source_packet_yk_frame_benchmark_sync/source_packet_yk_frame_benchmark_sync_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked whether the historical source-acquisition packet already captured the clean `Y/K + frame` benchmark.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Historical packet already names this benchmark: `false`; supplemental benchmark needed: `true`.
  - `Y/K + frame` isolates O4/B4/G5/O5 with active coverage `4/4` and `0` non-active in-frame `Y/K` groups.
  - Full-page `Y/K` still has `4` non-active controls.
  - Upstream unit/order gate checked `20` bounded streams with `0` hard instruction hits.
  - Source-backed unit/order remains `false`; dead-branch count remains `237`.
- Conclusion:
  - Add `C9_O4_FRAME_YK_ISOLATION` as a future source-validation benchmark only.
  - The current handoff is now a trio: source-acquisition packet for jobs/gates, 4/4 crop authority for visual comparison, and this `Y/K + frame` report for benchmark validation.
  - Do not resume selector/key checks unless a new source/clue passes R1-R5 and supplies R3 unit/order or independently explains the frame-intersection rule.

### C9 Frame OVERDOSE Page Control

- Status: checked; source-validation benchmark only, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_frame_overdose_page_control.py`
  - `analysis_outputs/source_audit/c9_frame_overdose_page_control/c9_frame_overdose_page_control.md`
  - `analysis_outputs/source_audit/c9_frame_overdose_page_control/c9_frame_overdose_page_control.json`
  - `analysis_outputs/source_audit/c9_frame_overdose_page_control/c9_frame_overdose_page_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Placed the C9 `Y/K + frame` rectangle at the same coordinates on article pages 75-80 to test same-slot OVERDOSE and mirror/fold behavior.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - The C9 frame is horizontally mirror-invariant: x-mirror returns the same rectangle with `0.0 px` max coordinate delta.
  - It fully covers all four p76 active targets: O4/B4/G5/O5 overlap `1.0`.
  - Same-frame page controls contain no strict extraction/unit/order terms; strict hit count `0` across p75-p80.
  - The slot is broad across OVERDOSE pages, covering p75 `80`, p76 `89`, p77 `95`, p78 `20`, and p79 `42` words.
- Conclusion:
  - Keep C9 as future source/original-layout validation benchmark only.
  - Do not use the C9 rectangle itself as fold/mirror/order evidence because it is x-mirror invariant and broad across control pages.
  - Reopen extraction only if a new source/clue supplies R3 unit/order or independently explains why the frame-intersection rule is intended.

### C9 Frame Internal Geometry Gate

- Status: checked; source-registration detail only, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_frame_internal_geometry_gate.py`
  - `analysis_outputs/source_audit/c9_frame_internal_geometry_gate/c9_frame_internal_geometry_gate.md`
  - `analysis_outputs/source_audit/c9_frame_internal_geometry_gate/c9_frame_internal_geometry_gate.json`
  - `analysis_outputs/source_audit/c9_frame_internal_geometry_gate/c9_frame_internal_geometry_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected only O4/B4/G5/O5 positions inside the C9 frame for edge contacts, centerlines, diagonals, normalized positions, and mirror-pair relations.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - The only strict C9 edge contact is `O4:top=0.19px`.
  - Active target centers produce `0` centerline/diagonal hits at the `25 px` threshold.
  - Active target pairs produce `0` horizontal, vertical, or point-reflection mirror-pair hits at the `25 px` threshold.
  - The closest pair midpoint to the C9 frame center is `O4-O5`, still `188.21 px` away.
  - Internal geometry does not resolve the group/vertical order versus left-to-right order conflict.
- Conclusion:
  - Keep O4's top-edge contact as a future source-registration detail only.
  - Do not use C9 internal edge/axis/diagonal/pair geometry as extraction permission.
  - Reopen extraction only if a new source/clue independently names a frame edge, centerline, diagonal, or target-order operation.

### C9 Highlight Edge-Contact Control

- Status: checked; source-registration detail only, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_highlight_edge_contact_control.py`
  - `analysis_outputs/source_audit/c9_highlight_edge_contact_control/c9_highlight_edge_contact_control.md`
  - `analysis_outputs/source_audit/c9_highlight_edge_contact_control/c9_highlight_edge_contact_control.json`
  - `analysis_outputs/source_audit/c9_highlight_edge_contact_control/c9_highlight_edge_contact_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Control-tested whether O4's C9 top-edge contact is distinctive among highlight boxes overlapping the same C9 lower-page slot on pages 75-80.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - There are `8` overlapping highlight boxes across p75-p80.
  - O4 is the only strict `<=4 px` edge contact: `p76 p76_orange_4 top=0.19px`.
  - At the looser `<=25 px` threshold there are `2` contacts, including the control `p75 p75_orange_6 top=23.19px`.
  - O5 is only a wide bottom-near contact at `41.73 px`, not a strict frame-edge contact.
- Conclusion:
  - Keep O4's C9 top-edge contact as a source-registration detail only.
  - Do not use it as extraction permission because a same-slot control highlight is also near the C9 top edge at ordinary visual tolerance.
  - Reopen extraction only if a new source/clue explicitly names frame-edge or top-edge reading.

### C9 Bold/Highlight Format Density

- Status: checked; format context only, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_bold_highlight_format_density.py`
  - `analysis_outputs/source_audit/c9_bold_highlight_format_density/c9_bold_highlight_format_density.md`
  - `analysis_outputs/source_audit/c9_bold_highlight_format_density/c9_bold_highlight_format_density.json`
  - `analysis_outputs/source_audit/c9_bold_highlight_format_density/c9_bold_highlight_format_density_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked page-76 line-level bold/highlight evidence inside the C9 frame band, especially whether bold letters or general highlight density isolate O4/B4/G5/O5.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - C9 has `11` corridor lines; `8` lines carry format signals.
  - Four non-active lines carry format signals.
  - Active bold-letter stream: `buyingthedipIMFshitcoineratheart`.
  - Non-active bold-letter stream: `PresidentNayibBukeleloanieNvzIdelluhu`.
  - Exact active phrase matches in bold letters: `2/4`.
  - B4 has no line-level bold letters; G5's line-level bold letters are `IMF`, not `VolcanoBonds`.
  - Hard instruction hits in bounded format streams: `0`.
- Conclusion:
  - Do not use C9 bold-letter or general highlight density as extraction permission.
  - The only current useful C9 fact remains the `Y/K + frame` source-validation benchmark, not a bold/highlight unit/order rule.
  - Reopen extraction only if a new source/clue explicitly names bold letters, highlight colors, or a format-unit order.

### C9 Active Format Witness Reconciliation

- Status: checked; format authority reconciled, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_active_format_witness_reconciliation.py`
  - `analysis_outputs/source_audit/c9_active_format_witness_reconciliation/c9_active_format_witness_reconciliation.md`
  - `analysis_outputs/source_audit/c9_active_format_witness_reconciliation/c9_active_format_witness_reconciliation.json`
  - `analysis_outputs/source_audit/c9_active_format_witness_reconciliation/c9_active_format_witness_reconciliation_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Reconciled DOCM/high-res/crop authority with line-level bold letters, Markdown markup, annotated transcript notes, and correction markup for O4/B4/G5/O5.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - DOCM/high-res/crop format authority passes `4/4`.
  - Line-level exact bold matches are `2/4`: O4 and O5.
  - Markdown bold contains active phrases `2/4`: O4 and O5.
  - Annotated transcript bold+highlight claims are `4/4`, but remain witness/context only.
  - Witness conflicts are `2/4`: B4 has no line-level bold letters, and G5's line-level bold letters are `IMF`, not `VolcanoBonds`.
  - Correction report mentions `2/4`: O4 punctuation and G5 `Volcano Bonds` omission.
- Conclusion:
  - Keep DOCM/high-res/crop-pack as source-comparison format authority for the active quartet.
  - Do not use line-level bold letters, Markdown bold, annotated notes, or correction mentions as extraction permission.
  - Reopen extraction only if a new source/clue supplies R3 unit/order wording tied to a specific format witness.

### C9 OVERDOSE Letter-Slot Gate

- Status: checked; layout coincidence only, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_overdose_letter_slot_gate.py`
  - `analysis_outputs/source_audit/c9_overdose_letter_slot_gate/c9_overdose_letter_slot_gate.md`
  - `analysis_outputs/source_audit/c9_overdose_letter_slot_gate/c9_overdose_letter_slot_gate.json`
  - `analysis_outputs/source_audit/c9_overdose_letter_slot_gate/c9_overdose_letter_slot_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Divided the C9 frame into eight equal horizontal slots named `OVERDOSE`, then mapped O4/B4/G5/O5 boxes plus same-slot orange-highlight controls to center/span slot letters.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - C9 slot width is `244.5 px`.
  - Active center streams are `OVED` in line order and `VEDO` in x-order.
  - Active span streams are `DOSOVERRDO` in line order and `OVERRDODOS` in x-order.
  - The x-order span stream gets an `OVER` prefix only from black B4/G5 (`OV` + `ER`); orange-only active spans are `RDODOS`.
  - Same-slot orange controls produce `VOVEDO` on p75 and `OOV` on p79.
  - Strict unit/order instruction hits are `0`.
- Conclusion:
  - Do not use C9 OVERDOSE 8-letter slot mapping as extraction permission.
  - Treat `OVERRDODOS` as a layout artifact of equal slot bins unless a new source/clue explicitly names OVERDOSE letters, slots, or an 8-column reading order.
  - Keep OVERDOSE slot mechanics as source-comparison context only.

### C9 Grey/Black OVER Slot Control

- Status: checked; active `OVER` controlled, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_grey_black_over_slot_control.py`
  - `analysis_outputs/source_audit/c9_grey_black_over_slot_control/c9_grey_black_over_slot_control.md`
  - `analysis_outputs/source_audit/c9_grey_black_over_slot_control/c9_grey_black_over_slot_control.json`
  - `analysis_outputs/source_audit/c9_grey_black_over_slot_control/c9_grey_black_over_slot_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Control-tested the `OVER` span from the active black B4/G5 boxes against grey/black rows that overlap the same C9 lower-page frame.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - C9 grey/black rows in the lower frame: `3`.
  - Active corrected black pair B4/G5 produces `OVER` as `OV` + `ER`.
  - Non-active p75 `Don't fall for shitcoinery` spans `OVER` as a single grey row in the same lower-frame slot geometry.
  - Single-row OVER hits: `1`; control single-row OVER hits: `1`.
  - Pair OVER hits: `1`; active corrected pair OVER hits: `1`.
  - Strict unit/order instruction hits: `0`.
- Conclusion:
  - Do not use B4/G5's C9 grey/black `OVER` pair as extraction permission.
  - The same C9 lower-frame slot rule produces an `OVER` span in a non-active p75 grey control row.
  - Reopen only if a new source/clue explicitly names grey/black OVER slots or supplies an 8-column reading rule.

### C9 OVER Slot Tolerance Gate

- Status: checked; active `OVER` is tolerance-sensitive and controlled, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_over_slot_tolerance_gate.py`
  - `analysis_outputs/source_audit/c9_over_slot_tolerance_gate/c9_over_slot_tolerance_gate.md`
  - `analysis_outputs/source_audit/c9_over_slot_tolerance_gate/c9_over_slot_tolerance_gate.json`
  - `analysis_outputs/source_audit/c9_over_slot_tolerance_gate/c9_over_slot_tolerance_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested B4/G5 `OVER` under fixed C9 horizontal grid shifts and overlap thresholds while tracking the p75 grey control.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Canonical active black pair stream is `OVER`.
  - Canonical p75 grey control span is `OVER`.
  - Active B4/G5 `OVER` appears in `45/99` bounded combinations.
  - The p75 control `OVER` appears in `49/99` bounded combinations.
  - Both active and p75 control `OVER` appear in `37/99` bounded combinations.
  - Active `OVER` fails completely at thresholds `[150, 200]`.
- Conclusion:
  - Do not tune C9 OVER slot shifts or overlap thresholds into an extraction rule.
  - The canonical B4/G5 `OVER` is controlled by p75, and the active hit is not stable enough to act as a selector.
  - Reopen only if a new source/clue names OVERDOSE slots or an 8-column reading order.

### C9 Vertical OVERDOSE Slot Gate

- Status: checked; vertical C9 slot projection closed, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_vertical_overdose_slot_gate.py`
  - `analysis_outputs/source_audit/c9_vertical_overdose_slot_gate/c9_vertical_overdose_slot_gate.md`
  - `analysis_outputs/source_audit/c9_vertical_overdose_slot_gate/c9_vertical_overdose_slot_gate.json`
  - `analysis_outputs/source_audit/c9_vertical_overdose_slot_gate/c9_vertical_overdose_slot_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Divided the same C9 frame into eight vertical `OVERDOSE` bands in both top-to-bottom and bottom-to-top orientations.
  - Mapped active O4/B4/G5/O5 plus nearby orange and grey/black controls.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Vertical slot height is `105.87 px`.
  - Top-to-bottom active center stream in line order is `OERE`.
  - Bottom-to-top active center stream in line order is `EODO`.
  - Top-to-bottom active span stream in line order is `OERE`.
  - Bottom-to-top active span stream in line order is `EODO`.
  - Active black vertical streams are `ER` top-to-bottom and `OD` bottom-to-top.
  - Active layout-hit stream count is `0`.
  - Control layout-hit stream count is `0`.
  - Active strict instruction hit count is `0`.
- Conclusion:
  - Do not use C9 vertical OVERDOSE bands as extraction permission.
  - The active quartet yields `OERE` / `EODO`, not `OVER`, `DOSE`, `OVERDOSE`, or unit/order wording.
  - Reopen only if a new source/clue names vertical slots, OVERDOSE bands, or an 8-row reading order.

### C9 Header Glyph Slot Gate

- Status: checked; actual header-glyph projection controlled, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_header_glyph_slot_gate.py`
  - `analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.md`
  - `analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json`
  - `analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Scaled the actual page 76 and page 78 `OVERDOSE` header glyph boundaries into the C9 lower-page frame.
  - Mapped active O4/B4/G5/O5 plus the p75 grey control.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Header projections tested: `2`.
  - Max projected glyph-edge delta vs equal slots is `0.087628 px`.
  - Active B4/G5 `OVER` projections: `2`.
  - p75 control `OVER` projections: `2`.
  - Active strict instruction hit count is `0`.
  - Both p76 and p78 header-glyph projections produce active x-order span `OVERRDODOS`, active black span `OVER`, active orange span `RDODOS`, and p75 grey control span `OVER`.
- Conclusion:
  - Do not use actual OVERDOSE header glyph slots as extraction permission.
  - The glyph projections are effectively the same as equal slots and reproduce the p75 control `OVER`.
  - Reopen only if a new source/clue names OVERDOSE header letters, glyph-width slots, or an 8-column reading order.

### C9 Mirrored Header Glyph Gate

- Status: checked; mirrored header-glyph projection controlled, no selector unlocked.
- Evidence:
  - `scripts/audit_c9_mirrored_header_glyph_gate.py`
  - `analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/c9_mirrored_header_glyph_gate.md`
  - `analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/c9_mirrored_header_glyph_gate.json`
  - `analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/c9_mirrored_header_glyph_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested normal header labels, reversed header labels, x-mirrored active/control boxes across the C9 frame, and reversed-label + mirrored-geometry variants.
  - Used actual p76/p78 `OVERDOSE` header glyph boundaries from the 3D article map.
  - Mapped active O4/B4/G5/O5 plus the p75 grey control.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Variants tested: `8`.
  - Active black B4/G5 streams by variant are `OVER`, `DOSE`, `ESOD`, or `REVO`.
  - Active black `OVER` variants: `2`.
  - Active black `REVO` variants: `2`.
  - p75 control `OVER` variants: `2`.
  - p75 control `REVO` variants: `2`.
  - The p75 grey control matches the active black stream in all `8/8` variants.
  - Strict instruction hits: `0`.
- Conclusion:
  - Do not use mirrored OVERDOSE header glyph slots as extraction permission.
  - Mirroring header labels or C9 x-geometry only moves the same controlled B4/G5 signal among `OVER`, `DOSE`, `ESOD`, and `REVO`.
  - Reopen only if a new source/clue names mirrored OVERDOSE header letters, glyph slots, or an 8-column reading order.

### 3D Reflection Line-Pitch Stack Gate

- Status: checked; line-pitch walking is broad/control-heavy, no selector unlocked.
- Evidence:
  - `scripts/audit_3d_reflection_line_pitch_stack_gate.py`
  - `analysis_outputs/3d_article_map/reflection_line_pitch_stack_gate/reflection_line_pitch_stack_gate.md`
  - `analysis_outputs/3d_article_map/reflection_line_pitch_stack_gate/reflection_line_pitch_stack_gate.json`
  - `analysis_outputs/3d_article_map/reflection_line_pitch_stack_gate/reflection_line_pitch_stack_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Shifted already-registered page-76 reflected boxes by integer page-76 line pitches.
  - Compared contacts with active O4/B4/G5/O5 plus all page-76 highlighted controls.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Line pitch is `73.73 px`.
  - Reflections tested: `14`.
  - Integer shifts tested: `-14` through `14`.
  - All-four active carriers: `3`.
  - The all-four carriers are `78_76_4`, `79_76_4`, and `79_76_5`.
  - Those carriers touch O4/B4/G5/O5 only with different per-target shifts.
  - All three carriers also sweep broad page-76 highlighted controls `G3/G4/G5/O3/O4/O5`.
  - Single global shifts covering all four active targets: `0`.
  - Strict instruction hits in carrier text: `0`.
- Conclusion:
  - Do not use integer line-pitch walking of 3D reflected boxes as extraction permission.
  - The operation can touch the active quartet, but only by per-target tuning and while also hitting broad controls.
  - Reopen only if a new source/clue names a specific reflection id plus target-specific line offsets or a global line-shift rule.

### Page-76 Highlight Fold-Axis Population Gate

- Status: checked; page-76 fold axes are not a selector.
- Evidence:
  - `scripts/audit_page76_highlight_fold_axis_population_gate.py`
  - `analysis_outputs/source_audit/page76_highlight_fold_axis_population_gate/page76_highlight_fold_axis_population_gate.md`
  - `analysis_outputs/source_audit/page76_highlight_fold_axis_population_gate/page76_highlight_fold_axis_population_gate.json`
  - `analysis_outputs/source_audit/page76_highlight_fold_axis_population_gate/page76_highlight_fold_axis_population_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Enumerated horizontal, vertical, and point-reflection axes from the full page-76 highlight population.
  - Tested whether any single axis re-hits the locked O4/B4/G5/O5 quartet.
  - Used trusted active boxes from the active crop-completion authority and page-76 highlight controls from the all-source highlight mirror benchmark.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Line pitch threshold is `73.73 px`.
  - Population targets: `10`, with `4` active.
  - Axis candidates tested: `141`.
  - All-four active axes: `0`.
  - Three-plus active axes: `0`.
  - Two-active axes: `6`, all tautological point axes chosen from the same two active target centers.
  - Non-tautological two-active axes: `0`.
  - Max non-tautological active hits: `1`.
  - Strict instruction axis hits: `0`.
- Conclusion:
  - Do not use page-76 highlight-population fold axes as extraction permission.
  - No simple fold/mirror axis from the page-76 highlight population recovers the active quartet, or even three active targets.
  - Reopen only if a new source/clue names a specific axis, fold operation, or reading unit/order.

### Active Line/Corridor Mirror-Index Gate

- Status: checked; line/corridor mirror-index axis is a near miss only.
- Evidence:
  - `scripts/audit_active_line_corridor_mirror_index_gate.py`
  - `analysis_outputs/source_audit/active_line_corridor_mirror_index_gate/active_line_corridor_mirror_index_gate.md`
  - `analysis_outputs/source_audit/active_line_corridor_mirror_index_gate/active_line_corridor_mirror_index_gate.json`
  - `analysis_outputs/source_audit/active_line_corridor_mirror_index_gate/active_line_corridor_mirror_index_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mirrored locked active page-line indexes `22 25 27 32` and corridor indexes `4 7 9 14`.
  - Tested candidate half-integer axes in the page-76 lower-corridor grid.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Page-line axes tested: `27`.
  - Corridor axes tested: `27`.
  - Page-line all-four active axes: `0`.
  - Corridor all-four active axes: `0`.
  - Best page-line axis: `27.0`, with `3` active hits.
  - Best corridor axis: `9.0`, with `3` active hits.
  - Best-axis stream in active order is `MNcH`.
  - The best axis maps O4 to O5, G5 to itself, and O5 to O4, but maps B4 to the non-active `Novogratz in the tweet, figuring he could sell a` line.
  - Strict instruction axis hits: `0`.
- Conclusion:
  - Do not use active line/corridor mirror indexes as extraction permission.
  - The G5-centered line/corridor mirror is a useful near miss but fails the active quartet and supplies no unit/order instruction.
  - Reopen only if a new source/clue names a line/corridor mirror axis plus a specific unit/order rule.

### G5-Axis Bold/Highlight Rescue Gate

- Status: checked; bold/highlight filtering does not rescue the G5-centered near miss.
- Evidence:
  - `scripts/audit_g5_axis_bold_highlight_rescue_gate.py`
  - `analysis_outputs/source_audit/g5_axis_bold_highlight_rescue_gate/g5_axis_bold_highlight_rescue_gate.md`
  - `analysis_outputs/source_audit/g5_axis_bold_highlight_rescue_gate/g5_axis_bold_highlight_rescue_gate.json`
  - `analysis_outputs/source_audit/g5_axis_bold_highlight_rescue_gate/g5_axis_bold_highlight_rescue_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Rechecked the G5-centered page-line/corridor axis (`27` / `9`).
  - Required reflected rows to be bold/highlight signal-bearing.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active hits: `3`.
  - Active misses: `1`.
  - Non-active signal hits: `1`.
  - Reflected style stream: `OBGO`.
  - Reflected active-target stream: `shitcoiner_heart|-|volcano_bonds|buying_dip`.
  - Initial stream: `MNcH`.
  - Last-initial stream: `haId`.
  - Bold stream: `shitcoineratheartNvzIMFbuyingthedip`.
  - Partial-bold stream: `Nvz`.
  - Strict instruction hits: `0`.
- Conclusion:
  - Do not use the G5-centered bold/highlight rescue filter as extraction permission.
  - The B4 reflection remains the non-active `Novogratz in the tweet, figuring he could sell a` row; it is signal-bearing but not locked-active.
  - Reopen only if a new source/clue explicitly names Novogratz/sell as a replacement for B4 or names a line/corridor mirror unit/order rule.

### Page-76 Page-Center Mirror Guardrail

- Status: checked; page-center rotation/mirrors are orientation guardrails only.
- Evidence:
  - `scripts/audit_page76_page_center_mirror_guardrail.py`
  - `analysis_outputs/source_audit/page76_page_center_mirror_guardrail/page76_page_center_mirror_guardrail.md`
  - `analysis_outputs/source_audit/page76_page_center_mirror_guardrail/page76_page_center_mirror_guardrail.json`
  - `analysis_outputs/source_audit/page76_page_center_mirror_guardrail/page76_page_center_mirror_guardrail_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Transformed O4/B4/G5/O5 through page-center 180-degree rotation, vertical page-center mirror, and horizontal page-center mirror.
  - Compared projected boxes to page-76 words, highlights, active targets, and the OVERDOSE header center.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Scenario count: `3`.
  - All-four active re-hit scenarios: `0`.
  - Total highlight contacts: `1`.
  - Strict instruction hits: `0`.
  - The projection previews are ordinary article fragments, not an instruction surface.
- Conclusion:
  - Do not use page-center 180-degree rotation or page-center mirrors as extraction permission.
  - Keep them as coordinate-frame guardrails for future source comparison.
  - Reopen only if a new source/clue explicitly names page-center rotation, vertical/horizontal page-center mirroring, or a unit/order rule.

### OVERDOSE Header Ray Fan Gate

- Status: checked; OVERDOSE header rays are a visual aid only.
- Evidence:
  - `scripts/audit_overdose_header_ray_fan_gate.py`
  - `analysis_outputs/source_audit/overdose_header_ray_fan_gate/overdose_header_ray_fan_gate.md`
  - `analysis_outputs/source_audit/overdose_header_ray_fan_gate/overdose_header_ray_fan_gate.json`
  - `analysis_outputs/source_audit/overdose_header_ray_fan_gate/overdose_header_ray_fan_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Drew straight segments from the page-76 OVERDOSE header center to O4/B4/G5/O5 target centers.
  - Compared active rays with rays from the same header origin to non-active page-76 highlight centers.
  - Measured existing word/highlight intersections and strict instruction words only.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active rays: `4`.
  - Non-active highlight control rays: `3`.
  - Active strict instruction hits: `0`.
  - Control strict instruction hits: `0`.
  - Active all-quartet rays: `0`.
  - Active ray highlight-hit counts: `[2, 1, 1, 3]`.
  - Control ray highlight-hit counts: `[1, 2, 2]`.
- Conclusion:
  - Do not use OVERDOSE header rays as extraction permission.
  - Active rays do not traverse the full active quartet and do not produce instruction wording.
  - Reopen only if a new source/clue explicitly names rays, header origin, or a ray-based unit/order rule.

### C9 Glyph-Center Ray Gate

- Status: checked; C9 glyph-center rays are visual/layout context only.
- Evidence:
  - `scripts/audit_c9_glyph_center_ray_gate.py`
  - `analysis_outputs/source_audit/c9_glyph_center_ray_gate/c9_glyph_center_ray_gate.md`
  - `analysis_outputs/source_audit/c9_glyph_center_ray_gate/c9_glyph_center_ray_gate.json`
  - `analysis_outputs/source_audit/c9_glyph_center_ray_gate/c9_glyph_center_ray_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used p76 C9 OVERDOSE glyph-slot top centers as ray origins.
  - Assigned O4/B4/G5/O5 and non-active page-76 highlight controls to the slot containing each target center x.
  - Measured existing word/highlight/active-target intersections and strict instruction words only.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active rays: `4`.
  - Control rays: `3`.
  - Active assigned slot stream: `OVED`.
  - Control assigned slot stream: `DEE`.
  - Active strict instruction hits: `0`.
  - Control strict instruction hits: `0`.
  - Active all-quartet rays: `0`.
  - Active ray active-target hit counts: `[1, 1, 1, 2]`.
  - Control ray active-target hit counts: `[0, 0, 0]`.
  - Active ray highlight-hit counts: `[1, 0, 0, 2]`.
  - Control ray highlight-hit counts: `[1, 2, 1]`.
- Conclusion:
  - Do not use C9 glyph-center rays as extraction permission.
  - The active slot stream repeats the known `OVED` center-slot result and adds no source-backed unit/order instruction.
  - Rays do not traverse the full active quartet; reopen only if a new source/clue explicitly names glyph-center rays or a ray-based unit/order rule.

### C9 Target Vertical Chord Gate

- Status: checked; exact target-x C9 vertical chords are visual/layout context only.
- Evidence:
  - `scripts/audit_c9_target_vertical_chord_gate.py`
  - `analysis_outputs/source_audit/c9_target_vertical_chord_gate/c9_target_vertical_chord_gate.md`
  - `analysis_outputs/source_audit/c9_target_vertical_chord_gate/c9_target_vertical_chord_gate.json`
  - `analysis_outputs/source_audit/c9_target_vertical_chord_gate/c9_target_vertical_chord_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used exact O4/B4/G5/O5 target-center x coordinates as vertical chords through the p76 C9 OVERDOSE frame.
  - Compared active chords with non-active page-76 highlight control chords.
  - Measured existing word/highlight/active-target intersections and strict instruction words only.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active chords: `4`.
  - Control chords: `3`.
  - Active slot stream: `OVED`.
  - Control slot stream: `DEE`.
  - Active strict instruction hits: `0`.
  - Control strict instruction hits: `0`.
  - Active all-quartet chords: `0`.
  - Active chord active-target hit counts: `[2, 1, 1, 2]`.
  - Control chord active-target hit counts: `[2, 1, 1]`.
  - Active chord highlight-hit counts: `[2, 0, 0, 2]`.
  - Control chord highlight-hit counts: `[2, 0, 0]`.
- Conclusion:
  - Do not use exact target-x C9 vertical chords as extraction permission.
  - The active slot stream repeats the known `OVED` center-slot result and adds no source-backed unit/order instruction.
  - Non-active highlight controls can touch active targets with a comparable `[2, 1, 1]` pattern; reopen only if a new source/clue explicitly names vertical slot chords or a chord-based unit/order rule.

### C9 Target Horizontal Chord Gate

- Status: checked; exact target-y C9 horizontal chords are row/context evidence only.
- Evidence:
  - `scripts/audit_c9_target_horizontal_chord_gate.py`
  - `analysis_outputs/source_audit/c9_target_horizontal_chord_gate/c9_target_horizontal_chord_gate.md`
  - `analysis_outputs/source_audit/c9_target_horizontal_chord_gate/c9_target_horizontal_chord_gate.json`
  - `analysis_outputs/source_audit/c9_target_horizontal_chord_gate/c9_target_horizontal_chord_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used exact O4/B4/G5/O5 target-center y coordinates as horizontal chords through the p76 C9 OVERDOSE frame.
  - Compared active chords with non-active focus-row controls inside the same C9 frame.
  - Measured existing word/highlight/active-target intersections and strict instruction words only.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active chords: `4`.
  - Control chords: `6`.
  - Active strict instruction hits: `0`.
  - Control strict instruction hits: `0`.
  - Active all-quartet chords: `0`.
  - Active chord active-target hit counts: `[1, 1, 1, 1]`.
  - Control chord active-target hit counts: `[0, 0, 0, 0, 0, 0]`.
  - Active chord highlight-hit counts: `[1, 0, 0, 1]`.
  - Control chord highlight-hit counts: `[0, 0, 0, 0, 0, 0]`.
  - Active word hit counts: `[7, 8, 6, 5]`.
  - Control word hit counts: `[8, 10, 6, 10, 8, 11]`.
- Conclusion:
  - Do not use exact target-y C9 horizontal chords as extraction permission.
  - Active rows are ordinary article rows around the locked targets and have no strict instruction hits.
  - Non-active focus rows inside the same frame are comparable ordinary rows; reopen only if a new source/clue explicitly names horizontal rows or a row-based unit/order rule.

### 3D Reflection Shifted Carrier Content Gate

- Status: checked; shifted 3D reflection carriers are row-registration/context evidence only.
- Evidence:
  - `scripts/audit_reflection_shifted_carrier_content_gate.py`
  - `analysis_outputs/3d_article_map/reflection_shifted_carrier_content_gate/reflection_shifted_carrier_content_gate.md`
  - `analysis_outputs/3d_article_map/reflection_shifted_carrier_content_gate/reflection_shifted_carrier_content_gate.json`
  - `analysis_outputs/3d_article_map/reflection_shifted_carrier_content_gate/reflection_shifted_carrier_content_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected the three all-four 3D reflection carriers from the line-pitch stack gate.
  - Measured per-target shifted carrier boxes against trusted O4/B4/G5/O5 boxes and existing 3D-map OCR words.
  - No new OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Carrier count: `3`.
  - Active shifted slices: `12`.
  - Active page-line gaps: `[3, 2, 5]`.
  - Common carrier shift-gap pattern: `[[3, 2, 5]]`.
  - Inferred base rows: `[20, 21]`.
  - Shifted-slice word count total: `78`.
  - Non-target words inside shifted slices: `69`.
  - Target-phrase isolated slices: `0`.
  - Strict instruction hits: `0`.
- Conclusion:
  - Do not promote shifted 3D reflection carrier rows as extraction permission.
  - The tempting `3/2/5` phase is ordinary line-pitch row walking from base rows 20/21, not a source-backed unit/order rule.
  - The shifted slices remain row-context prose, and existing 3D OCR does not cleanly recover trusted target text; reopen only if a source/clue names a specific reflection carrier, base row, target-shift sequence, and extraction unit/order.

### Active Target Envelope Density Gate

- Status: checked; the O4/B4/G5/O5 bbox/hull envelope is source-validation geometry only.
- Evidence:
  - `scripts/audit_active_target_envelope_density_gate.py`
  - `analysis_outputs/source_audit/active_target_envelope_density_gate/active_target_envelope_density_gate.md`
  - `analysis_outputs/source_audit/active_target_envelope_density_gate/active_target_envelope_density_gate.json`
  - `analysis_outputs/source_audit/active_target_envelope_density_gate/active_target_envelope_density_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested the minimal O4/B4/G5/O5 page-76 envelope `[428, 2177, 1801, 2982]`.
  - Compared it with same-size page-76 controls shifted by integer line-pitch offsets.
  - Used existing 3D-map OCR word boxes as density/control witnesses only.
  - No new OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active target coverage: `4/4`.
  - Active envelope words: `89`.
  - Non-target words inside envelope: `86`.
  - Active strict instruction hits: `0`.
  - Active highlight hits: `p76_orange_4`, `p76_orange_5`.
  - Shift controls tested: `25`.
  - Shift controls with comparable density: `12`.
  - Control strict instruction hits: `0`.
- Conclusion:
  - Do not promote the active target bbox/hull envelope as a selector.
  - The envelope is a broad lower-corridor prose band, not an isolated instruction surface.
  - Keep it as validation geometry only; reopen only if a new source/clue explicitly names an envelope/bounding-box/hull operation plus a unit/order rule.

### Active Target Center Path Gate

- Status: checked; target-center connector rails are source-validation/context geometry only.
- Evidence:
  - `scripts/audit_active_target_center_path_gate.py`
  - `analysis_outputs/source_audit/active_target_center_path_gate/active_target_center_path_gate.md`
  - `analysis_outputs/source_audit/active_target_center_path_gate/active_target_center_path_gate.json`
  - `analysis_outputs/source_audit/active_target_center_path_gate/active_target_center_path_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Connected trusted active target centers in line order and obvious alternative orders.
  - Used a narrow `24.0px` rail buffer and line-pitch shifted controls.
  - Used existing 3D-map OCR word boxes as geometry/density witnesses only.
  - No new OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Primary path: `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart`.
  - Primary path words: `9`.
  - Primary non-target words: `6`.
  - Primary strict instruction hits: `0`.
  - Alternative path variants: `4`.
  - Variant strict-instruction path hits: `0`.
  - Shift controls tested: `14`.
  - Shift controls with comparable density: `10`.
  - Control strict instruction hits: `0`.
- Conclusion:
  - Do not promote target-center connector rails as a selector.
  - The rails select sparse corrupted/context OCR-map fragments, not an instruction surface.
  - Keep target-center paths as visual/source-validation context only; reopen only if a source/clue names path/rail/connector geometry plus a unit/order rule.

### Active Target Center-Path Bold Gate

- Status: checked; target-center rail bold projection is source-validation/context geometry only.
- Evidence:
  - `scripts/audit_active_target_center_path_bold_gate.py`
  - `analysis_outputs/source_audit/active_target_center_path_bold_gate/active_target_center_path_bold_gate.md`
  - `analysis_outputs/source_audit/active_target_center_path_bold_gate/active_target_center_path_bold_gate.json`
  - `analysis_outputs/source_audit/active_target_center_path_bold_gate/active_target_center_path_bold_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Projected trusted `Article with Fonts.docm` DOCM bold state onto the existing O4/B4/G5/O5 center-path rail geometry.
  - Used existing 3D-map OCR word boxes and locked active target boxes as geometry witnesses only.
  - Did not use Markdown bold as font authority.
  - No new OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Primary path: `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart`.
  - Primary rail words: `9`.
  - Primary bold rail words: `4`.
  - Active-overlap bold rail words: `3`.
  - Non-active bold rail words: `1`.
  - Non-active bold rail text: `Bukele`.
  - Direct active target bold units: `4`.
  - Direct active target bold text: `buying the dip $1 billion Volcano Bonds shitcoiner at heart`.
  - Primary strict instruction hits: `0`.
  - Primary non-active strict instruction hits: `0`.
  - Shift controls tested: `14`.
  - Shift controls matching/exceeding primary non-active bold count: `5`.
  - Control strict instruction hits: `0`.
- Conclusion:
  - Do not promote target-center rail bold projection as a selector.
  - The rail-bold layer replays known active target phrases plus one nearby bold context word, not an instruction stream.
  - Keep this as a guardrail; reopen only if a source/clue names path/rail/connector geometry plus a word/letter unit and order.

### Source Packet Native Benchmark Bridge

- Status: checked; native coordinate bridge is source-registration scaffolding only.
- Evidence:
  - `scripts/audit_source_packet_native_benchmark_bridge.py`
  - `analysis_outputs/source_audit/source_packet_native_benchmark_bridge/source_packet_native_benchmark_bridge.md`
  - `analysis_outputs/source_audit/source_packet_native_benchmark_bridge/source_packet_native_benchmark_bridge.json`
  - `analysis_outputs/source_audit/source_packet_native_benchmark_bridge/source_packet_native_benchmark_bridge_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Converted active page-76 source-comparison benchmarks into readable/upright and native source coordinates after `rotate180`.
  - Included active O4/B4/G5/O5 boxes, C9/Y-K source frames, reflected p78 frame geometry, and measured OVERDOSE header/glyph boxes.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Benchmark boxes: `15`.
  - Active target boxes: `4`.
  - Source frames: `2`.
  - OVERDOSE glyph boxes: `8`.
  - Native transform: `rotate180`.
  - Active page lines: `22 25 27 32`.
  - Active corridor indexes: `4 7 9 14`.
  - Active visual-state order: `YKKY`.
  - C9 frame x-mirror invariant: `true`.
  - Header glyph sequence: `OVERDOSE`.
  - Header glyph max edge delta vs equal slot: `0.087628px`.
  - Upright-vs-native rotated 180 mean abs diff: `0.2859`.
  - Direct native-vs-upright mean abs diff: `27.6479`.
  - All native boxes in bounds: `true`.
  - Selector unlocked: `false`.
- Conclusion:
  - Do not promote the native benchmark bridge as a selector.
  - It preserves source/physical benchmark coordinates and validates the native rotation model, but it supplies no extraction unit or order.
  - Use it only for physical scan/original export/fresh PDF extraction comparison; require an external/source-level R3 signal before extracting from these boxes.

### Source Packet Visual-State Roundtrip

- Status: checked; visual-state roundtrip is source-validation evidence only.
- Evidence:
  - `scripts/audit_source_packet_visual_state_roundtrip.py`
  - `analysis_outputs/source_audit/source_packet_visual_state_roundtrip/source_packet_visual_state_roundtrip.md`
  - `analysis_outputs/source_audit/source_packet_visual_state_roundtrip/source_packet_visual_state_roundtrip.json`
  - `analysis_outputs/source_audit/source_packet_visual_state_roundtrip/source_packet_visual_state_roundtrip_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured per-box visual-state and native `rotate180` crop stability for the current source packet.
  - Used active O4/B4/G5/O5 target boxes and OVERDOSE header/glyph boxes as controls.
  - Carried forward DOCM active target bold status from the format authority lock.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active expected visual-state order: `YKKY`.
  - Active classified visual-state order from pixels: `YKKY`.
  - Active page lines: `22 25 27 32`.
  - Active corridor indexes: `4 7 9 14`.
  - All active visual states match: `true`.
  - All active DOCM bold fractions are `1.0`: `true`.
  - Active max mean abs diff after native rotate180: `2.9794`.
  - Active max pixel diff after native rotate180: `25`.
  - Active Y orange-ratio range: `[0.7124, 0.7666]`.
  - Active K dark-ratio range: `[0.6592, 0.6994]`.
  - OVERDOSE glyph sequence: `OVERDOSE`.
  - OVERDOSE glyph max dark ratio: `0.0`.
  - OVERDOSE glyph max orange ratio: `0.277`.
  - Selector unlocked: `false`.
- Conclusion:
  - Do not promote the visual-state roundtrip as a selector.
  - It confirms the active visual-state and DOCM-bold evidence are stable under the native source rotation model, but it supplies no extraction unit or order.
  - Use it with the native benchmark bridge for future source/original-layout comparison; require source-level R3 evidence before extraction resumes.

### Source Packet Alignment Tolerance

- Status: checked; alignment tolerance is source-validation evidence only.
- Evidence:
  - `scripts/audit_source_packet_alignment_tolerance.py`
  - `analysis_outputs/source_audit/source_packet_alignment_tolerance/source_packet_alignment_tolerance.md`
  - `analysis_outputs/source_audit/source_packet_alignment_tolerance/source_packet_alignment_tolerance.json`
  - `analysis_outputs/source_audit/source_packet_alignment_tolerance/source_packet_alignment_tolerance_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured how much active O4/B4/G5/O5 boxes can be padded or shifted while preserving Y/K visual-state evidence and native `rotate180` roundtrip.
  - Kept OVERDOSE header/glyph boxes as non-active controls.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active expected visual-state order: `YKKY`.
  - Active page lines: `22 25 27 32`.
  - Active corridor indexes: `4 7 9 14`.
  - Common outward pad where all targets pass: `+4px`.
  - Common inset pad where all targets pass: `-12px`.
  - Common all-direction shift where all targets pass: `±4px`.
  - Largest any-target outward pad pass: `+16px`.
  - Smallest first outward pad failure: `+8px`.
  - Max variant mean abs diff after native rotate180: `3.021`.
  - OVERDOSE control classified-state stream: `NNNNNNNNN`.
  - OVERDOSE control max dark ratio: `0.0`.
  - OVERDOSE control max orange ratio: `0.277`.
  - Selector unlocked: `false`.
- Conclusion:
  - Do not promote alignment tolerance as a selector.
  - Future source matches should be judged with narrow tolerance: common all-target pass is only `+4px` outward padding and `±4px` full-direction shift.
  - Larger drift breaks visual-state classification, especially black-highlight boxes; loose visual matches should not count as source confirmation.
  - Use this with the native bridge and visual-state roundtrip for future source/original-layout comparison; require source-level R3 evidence before extraction resumes.

### Source Packet Geometric Fingerprint

- Status: checked; geometric fingerprint is source-registration evidence only.
- Evidence:
  - `scripts/audit_source_packet_geometric_fingerprint.py`
  - `analysis_outputs/source_audit/source_packet_geometric_fingerprint/source_packet_geometric_fingerprint.md`
  - `analysis_outputs/source_audit/source_packet_geometric_fingerprint/source_packet_geometric_fingerprint.json`
  - `analysis_outputs/source_audit/source_packet_geometric_fingerprint/source_packet_geometric_fingerprint_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Recorded active O4/B4/G5/O5 boxes, centers, page/corridor gaps, pairwise distances, center-step signs, native `rotate180` roundtrip checks, and OVERDOSE header layout context.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active visual-state order: `YKKY`.
  - Active page lines: `22 25 27 32`.
  - Active corridor indexes: `4 7 9 14`.
  - Page-line and corridor gaps: `[3, 2, 5]`.
  - Center-step signs: dx `-++`, dy `+++`.
  - Active cluster box: `[428, 2177, 1801, 2982]`.
  - Active cluster size: `[1373, 805]`.
  - Native `rotate180` center/box roundtrip max errors: `0.0px` / `0.0px`.
  - Pairwise records: `6`.
  - OVERDOSE header glyph sequence: `OVERDOSE`.
  - Frontier now records `90` focused local checks.
- Conclusion:
  - Do not promote the geometric fingerprint as a selector.
  - It stabilizes future source/physical/original-layout comparison but supplies no extraction unit, order rule, or key material.
  - It does not reopen folded/mirrored 3D geometry, bold-letter, highlight, or OVERDOSE layout mechanics.
  - Use it with the native bridge, visual-state roundtrip, and alignment tolerance; require source/provenance R3 unit-order wording before extraction resumes.

### Source Packet Frame-Normalized Geometry

- Status: checked; frame-normalized geometry is source-registration evidence only.
- Evidence:
  - `scripts/audit_source_packet_frame_normalized_geometry.py`
  - `analysis_outputs/source_audit/source_packet_frame_normalized_geometry/source_packet_frame_normalized_geometry.md`
  - `analysis_outputs/source_audit/source_packet_frame_normalized_geometry/source_packet_frame_normalized_geometry.json`
  - `analysis_outputs/source_audit/source_packet_frame_normalized_geometry/source_packet_frame_normalized_geometry_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Normalized active O4/B4/G5/O5 centers and boxes inside the C9/Y-K frame and the reflected p78 frame.
  - Tested simple C9-frame horizontal, vertical, and point mirrors against active centers.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - C9 normalized center stream: `[[0.651074, 0.028335], [0.135736, 0.288666], [0.35864, 0.461629], [0.540133, 0.920897]]`.
  - C9/Y-K full-inside active target count: `4/4`.
  - Reflected p78 full-inside active target count: `0/4`.
  - Reflected p78 partial-overlap ids: `['shitcoiner_heart']`.
  - Simple C9-frame horizontal, vertical, and point mirrors have no all-four active center re-hit at `4/25/50px`.
  - Frame-normalized fingerprint: `c9NormCenters=0.651,0.028;0.136,0.289;0.359,0.462;0.540,0.921|c9Inside=4/4|p78Inside=0/4|p78Partial=shitcoiner_heart|mirrorAllFour4px=none`.
  - Frontier now records `91` focused local checks.
- Conclusion:
  - Do not promote frame-normalized geometry as a selector.
  - It gives scale-stable source comparison coordinates, but supplies no extraction unit, order rule, or key material.
  - The reflected p78 frame alone does not explain the active quartet, and simple C9-frame mirrors do not reopen folded/mirrored geometry.
  - Use this only with future source/physical/original-layout comparison; require source/provenance R3 unit-order wording before extraction resumes.

### Source Packet Color-Profile Manifest

- Status: checked; color-profile manifest is source-validation evidence only.
- Evidence:
  - `scripts/audit_source_packet_color_profile_manifest.py`
  - `analysis_outputs/source_audit/source_packet_color_profile_manifest/source_packet_color_profile_manifest.md`
  - `analysis_outputs/source_audit/source_packet_color_profile_manifest/source_packet_color_profile_manifest.json`
  - `analysis_outputs/source_audit/source_packet_color_profile_manifest/source_packet_color_profile_manifest_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Recorded active O4/B4/G5/O5 orange/black RGB, luma, saturation, orange-ratio, dark-ratio, and native `rotate180` roundtrip profile.
  - Kept OVERDOSE header/glyphs as non-active visual controls.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active visual-state order: `YKKY`.
  - Active Y orange-ratio range: `[0.7124, 0.7666]`.
  - Active K dark-ratio range: `[0.6592, 0.6994]`.
  - Active K orange-ratio range: `[0.0, 0.0]`.
  - OVERDOSE control classified-state stream: `NNNNNNNNN`.
  - OVERDOSE control max orange ratio: `0.277`.
  - OVERDOSE control max dark ratio: `0.0`.
  - Y/control orange separation margin: `0.4354`.
  - K/control dark separation margin: `0.6592`.
  - Max native `rotate180` mean abs diff: `2.9794`.
  - Color-profile fingerprint: `states=YKKY|Yorange=0.7124-0.7666|Kdark=0.6592-0.6994|KorangeMax=0.0|ctrlOrangeMax=0.277|ctrlDarkMax=0.0|roundtripMeanMax=2.9794`.
  - Frontier now records `92` focused local checks.
- Conclusion:
  - Do not promote color profiles as a selector.
  - Active orange/black profiles are useful source-comparison benchmarks, but supply no extraction unit, order rule, or key material.
  - OVERDOSE header/glyph controls remain non-active, so this does not reopen C9/OVERDOSE layout mechanics.
  - Use this only with future source/physical/original-layout comparison; require source/provenance R3 unit-order wording before extraction resumes.

### Source Packet Repaired P78 Frame Residual

- Status: checked; repaired p78 frame residual is source-registration evidence only.
- Evidence:
  - `scripts/audit_source_packet_repaired_p78_frame_residual.py`
  - `analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual/source_packet_repaired_p78_frame_residual.md`
  - `analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual/source_packet_repaired_p78_frame_residual.json`
  - `analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual/source_packet_repaired_p78_frame_residual_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured current, `dx=-38`, and `dx=-40` reflected p78 frame variants against active O4/B4/G5/O5 source-packet boxes.
  - Used the native benchmark bridge, p78 source/native bridge, alignment tolerance, and color-profile manifest as inputs.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active visual-state order: `YKKY`.
  - Active page lines / corridor indexes: `22 25 27 32` / `4 7 9 14`.
  - Common source-packet all-direction shift tolerance: `4px`.
  - Max full-inside active count across current/dx-repaired frames: `0/4`.
  - Max partial-hit active count: `2/4`.
  - Best G5 horizontal gap: `g5_edge_touch_dx_-38` at `0.0px`.
  - Best O5 overlap: `nearest_grid_dx_-40` at `0.270725`.
  - Minimum repaired-frame B4 left expansion to touch/full-cover: `503px` / `766px`.
  - Minimum repaired-frame O4 top expansion to touch/full-cover: `173px` / `221px`.
  - Frame residual fingerprint: `frames=current,-38,-40|maxFull=0|maxPartial=2|bestG5Gap=g5_edge_touch_dx_-38:0.0|bestO5Overlap=nearest_grid_dx_-40:0.270725|minRepairedB4TouchLeft=503|minRepairedB4FullLeft=766|minRepairedO4TouchTop=173|minRepairedO4FullTop=221`.
  - Frontier now records `93` focused local checks.
- Conclusion:
  - Do not promote repaired p78 frame geometry as a selector.
  - The dx-repaired frame variants improve G5/O5 source-registration residuals but still do not fully contain the active quartet.
  - B4 and O4 require large frame expansions, so folded/mirrored p78 geometry, OVERDOSE layout, and highlight mechanics remain closed for current-scan extraction.
  - Use this only with future physical/original-layout comparison; require source/provenance R3 unit-order wording before extraction resumes.

### Source Packet Repaired Frame Expansion Leakage

- Status: checked; repaired p78-frame expansion is context leakage, not a selector.
- Evidence:
  - `scripts/audit_source_packet_repaired_frame_expansion_leakage.py`
  - `analysis_outputs/source_audit/source_packet_repaired_frame_expansion_leakage/source_packet_repaired_frame_expansion_leakage.md`
  - `analysis_outputs/source_audit/source_packet_repaired_frame_expansion_leakage/source_packet_repaired_frame_expansion_leakage.json`
  - `analysis_outputs/source_audit/source_packet_repaired_frame_expansion_leakage/source_packet_repaired_frame_expansion_leakage_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured `base`, `edge_touch_all`, and `full_cover_all` scenarios for the current, `dx=-38`, and `dx=-40` reflected p78 frames.
  - Used transcript line boxes for text authority and 3D map word centers as geometry witness.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Scenario count: `9`.
  - Base max line-context word count: `72`.
  - Edge-touch minimum line-context word count: `91`; minimum non-target word count: `89`.
  - Full-cover minimum line-context word count: `102`; minimum non-target word count: `92`.
  - Full-cover OCR-map word-center count range: `[89, 89]`.
  - Full-cover non-active highlight/format entries: `4`.
  - Full-cover hard instruction hits: `0` transcript / `0` OCR-map.
  - Expansion leakage fingerprint: `scenarios=base,touch,full|baseMaxWords=72|touchMinWords=91|fullMinWords=102|fullMinNonTarget=92|fullSignals=4|fullHard=0|fullOcrHard=0`.
  - Frontier now records `94` focused local checks.
- Conclusion:
  - Do not promote repaired frame expansion as a selector.
  - Full-cover repairs only work by taking the whole L22-L32 lower-corridor band, including 92 non-target words and four non-active format signals.
  - This closes the repaired p78-frame expansion residual for current-scan extraction; keep it as a future source-registration stress test only.

### Source Packet Handoff Integrity Matrix

- Status: checked; current source handoff is internally consistent but still extraction-locked.
- Evidence:
  - `scripts/audit_source_packet_handoff_integrity_matrix.py`
  - `analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/source_packet_handoff_integrity_matrix.md`
  - `analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/source_packet_handoff_integrity_matrix.json`
  - `analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/source_packet_handoff_integrity_matrix_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Cross-checked orientation, target order, visual state, crop completeness, text/format authority, C9/Y-K frame behavior, p78 repaired residuals, OVERDOSE controls, active box OCR, and repaired-frame leakage.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Gate count: `17`.
  - Pass/source-validation gates: `15`.
  - Reject-as-selector gates: `8`.
  - Contradictions: `0`.
  - Selector unlocks: `0`.
  - Extraction-ready gates: `0`.
  - Active visual-state order: `YKKY`.
  - Active page lines / corridor indexes: `22 25 27 32` / `4 7 9 14`.
  - Common shift tolerance: `4px`.
  - Full-cover leakage words/non-target words: `102` / `92`.
  - Integrity fingerprint: `gates=17|pass=15|reject=8|contradictions=0|selectors=0|states=YKKY|lines=22-25-27-32|corr=4-7-9-14|shift=4|leakWords=102/92`.
  - Frontier now records `95` focused local checks.
- Conclusion:
  - Use this matrix as the compact source-comparison checklist.
  - The current handoff stack has no internal contradiction, but it also has no selector unlock and no extraction-ready path.
  - Further local selector work should wait for a new source/clue that supplies source-backed R3 unit and order wording.

### Source Packet False-Positive Guardrail

- Status: checked; visual-only source matches are explicitly blocked unless source-backed R3 unit/order wording is present.
- Evidence:
  - `scripts/audit_source_packet_false_positive_guardrail.py`
  - `analysis_outputs/source_audit/source_packet_false_positive_guardrail/source_packet_false_positive_guardrail.md`
  - `analysis_outputs/source_audit/source_packet_false_positive_guardrail/source_packet_false_positive_guardrail.json`
  - `analysis_outputs/source_audit/source_packet_false_positive_guardrail/source_packet_false_positive_guardrail_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Audited known false-positive source-match modes around folded/mirrored 3D page geometry, bold/highlight witnesses, orange/black state, page-76 target clusters, C9/OVERDOSE layout, p78 repaired-frame behavior, active-box OCR, and alignment tolerance.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Guardrail count: `9`.
  - Hard rejects without R3: `9`.
  - Selector unlocks: `0`.
  - Active visual-state order: `YKKY`.
  - Active page lines / corridor indexes: `22 25 27 32` / `4 7 9 14`.
  - Guardrail classes rejected without source-backed R3: color/state only, native unrotated order, C9 frame-only containment, OVERDOSE black-OVER spelling, p78 contact/dx repair, p78 full-cover leakage, bold/annotation-only witness state, active-box OCR text, and loose alignment.
  - False-positive guardrail fingerprint: `guardrails=9|hardReject=9|states=YKKY|lines=22-25-27-32|corr=4-7-9-14|selectorUnlocks=0|requiresR3=1`.
  - Frontier now records `96` focused local checks.
- Conclusion:
  - Reject future source matches that pass only by color/frame/OVERDOSE/bold/partial-contact/OCR/alignment signals.
  - Any new source must preserve readable/upright active order and visual state, survive the existing controls, and supply source-backed R3 unit/order wording before extraction resumes.

### Source Packet R3 Bridge Audit

- Status: checked; no local authoritative R3 bridge exists for the current visual source-packet evidence.
- Evidence:
  - `scripts/audit_source_packet_r3_bridge_audit.py`
  - `analysis_outputs/source_audit/source_packet_r3_bridge_audit/source_packet_r3_bridge_audit.md`
  - `analysis_outputs/source_audit/source_packet_r3_bridge_audit/source_packet_r3_bridge_audit.json`
  - `analysis_outputs/source_audit/source_packet_r3_bridge_audit/source_packet_r3_bridge_audit_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Scanned canonical/plain article text, user annotated transcript, Markdown transcript, correction markup, external clue unit/order intake, source-reopen requirements, future source validation packet, handoff integrity matrix, and false-positive guardrail.
  - Checked for source-backed wording that would name or visibly supply words, letters, lines, edges, slots, glyphs, order, first/last, left/right, read/take/extract/count instructions, or equivalent R3 evidence tied to O4/B4/G5/O5.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Authority/correction layers scanned: `4`.
  - Active target windows: `31`.
  - Visual-only target windows: `23`.
  - Source-backed R3 bridge hits: `0`.
  - Derived correction bridge windows: `1`.
  - External raw-like R3 passes: `0`.
  - Generated report `unit/order` mentions: `37`.
  - Guardrails still blocked: `9`.
  - R3 bridge fingerprint: `authority=4|targetWindows=31|visualOnly=23|sourceR3=0|derivedR3=1|externalRawR3=0|generatedUnitOrder=37|guardrails=9|selectorUnlocks=0`.
  - Frontier now records `97` focused local checks.
- Conclusion:
  - Active target text and visual witness markup are present, but they do not name an extraction unit or order.
  - Generated report language and correction-report assessment text must not be promoted as puzzle/source evidence.
  - Keep extraction paused until a new source/provenance clue supplies R3 wording and passes R1-R5.

### Source Packet Reopen Trigger Matrix

- Status: checked; no current visual/source-packet path satisfies a reopen trigger.
- Evidence:
  - `scripts/audit_source_packet_reopen_trigger_matrix.py`
  - `analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/source_packet_reopen_trigger_matrix.md`
  - `analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/source_packet_reopen_trigger_matrix.json`
  - `analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/source_packet_reopen_trigger_matrix_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Converted the blocked visual classes into exact source/provenance triggers for future review: color/state, native orientation, C9 frame, OVERDOSE slots, p78 dx repair, p78 full-cover leakage, bold/highlight witnesses, active-box OCR, and loose alignment.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Trigger count: `9`.
  - Satisfied current triggers: `0`.
  - Source-backed R3 bridge hits: `0`.
  - Guardrails still blocked: `9`.
  - Active visual-state order: `YKKY`.
  - Active page lines / corridor indexes: `22 25 27 32` / `4 7 9 14`.
  - Reopen trigger fingerprint: `triggers=9|satisfied=0|sourceR3=0|states=YKKY|lines=22-25-27-32|corr=4-7-9-14|guardrailsBlocked=9|selectors=0`.
  - Frontier now records `98` focused local checks.
- Conclusion:
  - Every tempting visual route now has an explicit source-observation requirement.
  - None is met by the current scan, local text layers, generated reports, or local derivatives.
  - Future source/photo/export/clue review should begin by scoring the observed change against this trigger matrix before selector/key work resumes.

### Source Packet Orientation Disambiguator

- Status: checked; source-packet visual matches are orientation-validation evidence only unless they preserve the readable/upright discriminators.
- Evidence:
  - `scripts/audit_source_packet_orientation_disambiguator.py`
  - `analysis_outputs/source_audit/source_packet_orientation_disambiguator/source_packet_orientation_disambiguator.md`
  - `analysis_outputs/source_audit/source_packet_orientation_disambiguator/source_packet_orientation_disambiguator.json`
  - `analysis_outputs/source_audit/source_packet_orientation_disambiguator/source_packet_orientation_disambiguator_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared readable/upright, raw-native top-to-bottom, x-mirror, y-mirror, and point-mirror/rotate180 candidate modes for O4/B4/G5/O5.
  - No OCR, extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Orientation modes checked: `5`.
  - Accepted source-comparison modes: `1` (`readable_upright`).
  - Rejected/blocked modes: `4`.
  - Ambiguous visual signals: `4` (`YKKY`, `OBBO`, C9 x-mirror invariance, OVERDOSE control state).
  - Discriminating source/geometry signals: `6`.
  - Readable page-line / corridor order: `22 25 27 32` / `4 7 9 14`.
  - Raw native unnormalized page-line / corridor order: `32 27 25 22` / `14 9 7 4`.
  - Readable center-step signs: dx `-++`, dy `+++`.
  - Source-backed R3 bridge hits / satisfied reopen triggers / selector unlocks: `0` / `0` / `0`.
  - Orientation disambiguator fingerprint: `modes=5|accepted=1|ambiguous=4|discriminators=6|states=YKKY|color=OBBO|lines=22-25-27-32|nativeLines=32-27-25-22|dx=-++|dy=+++|sourceR3=0|selectors=0`.
  - Frontier now records `99` focused local checks.
- Conclusion:
  - Use readable/upright O4/B4/G5/O5 coordinates for future source comparison and rotate native source images 180 degrees first.
  - Do not accept `YKKY`, `OBBO`, or C9 frame containment as orientation proof.
  - Future source matches must preserve readable line/corridor order, center-step signs, C9 normalized centers, and narrow alignment tolerance before any selector work resumes.

### Source Packet Orientation Control Quartets

- Status: checked; active readable/upright geometry is selective in available controls, but still source-registration evidence only.
- Evidence:
  - `scripts/audit_source_packet_orientation_control_quartets.py`
  - `analysis_outputs/source_audit/source_packet_orientation_control_quartets/source_packet_orientation_control_quartets.md`
  - `analysis_outputs/source_audit/source_packet_orientation_control_quartets/source_packet_orientation_control_quartets.json`
  - `analysis_outputs/source_audit/source_packet_orientation_control_quartets/source_packet_orientation_control_quartets_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Controlled the active O4/B4/G5/O5 orientation fingerprint against full-page Y/K quartets, contiguous Y/K windows, and C9 format-line gap quartets.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Full-page Y/K quartets tested: `70`.
  - Full-page `YKKY` quartets: `11`.
  - Mixed/non-exact `YKKY` controls: `10`.
  - Contiguous full-page Y/K windows: `5`; `YKKY` windows: `1`, the active window.
  - C9 format-line quartets: `70`; exact `3/2/5` line-gap matches: `1`, the active `22 25 27 32` line set.
  - Non-active Y/K pixel boxes are unavailable in the current handoff, so pixel-center uniqueness against those earlier controls remains unclaimed.
  - Source-backed R3 bridge hits / satisfied reopen triggers / selector unlocks: `0` / `0` / `0`.
  - Orientation control quartet fingerprint: `ykCombos=70|YKKY=11|YKKYNonExact=10|windows=5|windowYKKY=1|lineCombos=70|lineGaps325=1|dx=-++|dy=+++|sourceR3=0|selectors=0`.
  - Frontier now records `100` focused local checks.
- Conclusion:
  - `YKKY` alone is rejected as orientation proof or selector evidence.
  - Readable/upright line/corridor order, group gaps, C9 normalized centers, and dx/dy signs remain good future source-comparison controls.
  - Extraction stays paused until a source-backed R3 unit/order instruction appears and passes the reopen matrix.

### Source Packet Source-Review Gate

- Status: checked; current source packet is not extraction-ready under the compact R1-R5 review order.
- Evidence:
  - `scripts/audit_source_packet_source_review_gate.py`
  - `analysis_outputs/source_audit/source_packet_source_review_gate/source_packet_source_review_gate.md`
  - `analysis_outputs/source_audit/source_packet_source_review_gate/source_packet_source_review_gate.json`
  - `analysis_outputs/source_audit/source_packet_source_review_gate/source_packet_source_review_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Dry-ran seven current evidence paths against R1-R5: current scan/local derivatives, active geometry, Y/K frame controls, C9/OVERDOSE mechanics, folded/reflected p78 frame repair, bold/highlight witnesses, and archived clue/provenance wording.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Current paths tested: `7`.
  - Extraction-ready paths: `0`.
  - R3 failures: `7`.
  - R1 failures: `6`.
  - R4 orientation passes: `6`.
  - Satisfied reopen triggers: `0/9`.
  - Source-backed R3 bridge hits: `0`.
  - Handoff selector unlocks: `0`.
  - Source-review gate fingerprint: `paths=7|ready=0|r3Fail=7|R1Fail=6|R4Pass=6|triggers=0/9|sourceR3=0|YKKY=11|selectors=0`.
  - Frontier now records `101` focused local checks.
- Conclusion:
  - Use the source-review gate as the compact future-evidence order: R1 distinct source, R4 readable/upright orientation, pattern controls, R2/R5 preservation and controlled improvement, then R3 source-backed unit/order.
  - Current active geometry and visual/layout controls remain validation benchmarks only.
  - Stop before selector/key work if a future item lacks R3 unit/order wording.

### Source Packet OVERDOSE Transform Control

- Status: checked; measured OVERDOSE glyph geometry does not unlock a selector.
- Evidence:
  - `scripts/audit_source_packet_overdose_transform_control.py`
  - `analysis_outputs/source_audit/source_packet_overdose_transform_control/source_packet_overdose_transform_control.md`
  - `analysis_outputs/source_audit/source_packet_overdose_transform_control/source_packet_overdose_transform_control.json`
  - `analysis_outputs/source_audit/source_packet_overdose_transform_control/source_packet_overdose_transform_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Controlled active O4/B4/G5/O5 OVERDOSE slot behavior against measured header glyph boxes, mirrored/reversed variants, p75 controls, and bounded tolerance rows.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Measured header glyph sequence: `OVERDOSE`.
  - Header glyphs differ from equal C9 slots by at most `0.087628px`.
  - Active center streams: `OVED` line-order and `VEDO` x-order.
  - Active black B4/G5 span: `OVER`; p75 control span: `OVER`.
  - Mirrored/reversed variants tested: `8`; p75 matched active black in `8/8`.
  - Tolerance rows: active black `OVER` in `45/99`; p75 `OVER` in `49/99`; both `OVER` in `37/99`.
  - Source-review extraction-ready paths / source-backed R3 hits / selector unlocks: `0` / `0` / `0`.
  - Fingerprint: `glyphDelta=0.087628|center=OVED/VEDO|black=OVER|p75=OVER|mirrors=8/8|tol=45/49|ready=0|sourceR3=0|selectors=0`.
  - Frontier now records `102` focused local checks.
- Conclusion:
  - Do not promote OVERDOSE transform/slot geometry as a selector.
  - Keep it as a future source-validation guardrail only.
  - Reopen only if a distinct source or clue names OVERDOSE/header slots and supplies a unit/order rule that p75 and mirror/tolerance controls fail.

### Source Packet Fold/Format Intersection Control

- Status: checked; folded 3D geometry plus bold/highlight state does not unlock a selector.
- Evidence:
  - `scripts/audit_source_packet_fold_format_intersection_control.py`
  - `analysis_outputs/source_audit/source_packet_fold_format_intersection_control/source_packet_fold_format_intersection_control.md`
  - `analysis_outputs/source_audit/source_packet_fold_format_intersection_control/source_packet_fold_format_intersection_control.json`
  - `analysis_outputs/source_audit/source_packet_fold_format_intersection_control/source_packet_fold_format_intersection_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Intersected folded/mirrored 3D carrier evidence with active bold/highlight authority, page-76 target-cluster controls, orientation controls, and current OVERDOSE/source-review guardrails.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Intersection gates checked: `8`; pass / partial / fail: `2` / `0` / `6`.
  - Folded/reflected carriers touching all four active targets: `3`; single global all-four shifts: `0`.
  - Shifted carrier slices: `12`; total words: `78`; non-target words: `69`; target-isolated slices: `0`.
  - Fold/highlight axes tested: `141`; all-four active axes: `0`; non-tautological two-active axes: `0`.
  - Format authority passes: `4/4`, with `2` witness conflicts.
  - Source-backed R3 hits / satisfied reopen triggers / selector unlocks: `0` / `0` / `0`.
  - Fingerprint: `gates=8|pass=2|partial=0|singleShiftAll4=0|carrierNonTarget=69|isolated=0|axesAll4=0|formatPass=4|formatConflicts=2|sourceR3=0|selectors=0`.
  - Frontier now records `103` focused local checks.
- Conclusion:
  - Do not promote folded 3D geometry plus bold/highlight state as a selector.
  - The only passing intersection pieces are validation/context gates, not extraction gates.
  - Reopen only if a distinct source names a fold/reflection/format operation and supplies a unit/order rule that passes R1-R5.

### Source Packet Terminal Coverage Matrix

- Status: checked; all requested focus areas have guardrails, but none is extraction-ready.
- Evidence:
  - `scripts/audit_source_packet_terminal_coverage_matrix.py`
  - `analysis_outputs/source_audit/source_packet_terminal_coverage_matrix/source_packet_terminal_coverage_matrix.md`
  - `analysis_outputs/source_audit/source_packet_terminal_coverage_matrix/source_packet_terminal_coverage_matrix.json`
  - `analysis_outputs/source_audit/source_packet_terminal_coverage_matrix/source_packet_terminal_coverage_matrix_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked guardrail coverage for source files/transcripts/corrections, page-76 O4/B4/G5/O5 cluster, orange/black Y/K orientation, folded/mirrored 3D plus format, OVERDOSE layout mechanics, false-positive/reopen triggers, source-backed R3 bridge, and next-move discipline.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Coverage areas checked: `8`.
  - Guardrails present: `8/8`.
  - Uncovered guardrails: `0`.
  - Extraction-ready areas: `0`.
  - Source files checked / present: `6/6`.
  - Source-backed R3 hits / satisfied reopen triggers / selector unlocks: `0` / `0` / `0`.
  - Fingerprint: `areas=8|covered=8|ready=0|sourceR3=0|triggers=0/9|selectors=0|next=source-validation`.
  - Frontier now records `104` focused local checks.
- Conclusion:
  - The current source packet is well covered by guardrails but still not extraction-ready.
  - Do not run more current-scan selector/key permutations.
  - The only useful next move is distinct source/physical/original-layout validation through R1-R5, with source-backed R3 required before selector/key work resumes.

### Source Packet Active Target Authority Crosscheck

- Status: checked; active O4/B4/G5/O5 wording and format authority are confirmed, but no selector is unlocked.
- Evidence:
  - `scripts/audit_source_packet_active_target_authority_crosscheck.py`
  - `analysis_outputs/source_audit/source_packet_active_target_authority_crosscheck/source_packet_active_target_authority_crosscheck.md`
  - `analysis_outputs/source_audit/source_packet_active_target_authority_crosscheck/source_packet_active_target_authority_crosscheck.json`
  - `analysis_outputs/source_audit/source_packet_active_target_authority_crosscheck/source_packet_active_target_authority_crosscheck_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Crosschecked active target text and format claims across canonical plain text, Markdown transcript, annotated transcript, correction markup, text/format authority locks, C9 witness reconciliation, and terminal guardrails.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active targets checked: `4`.
  - Canonical / Markdown / annotated present counts: `4/4` / `4/4` / `4/4`.
  - Format authority pass / visual exact match: `4/4` / `4/4`.
  - Raw plain missing: `volcano_bonds`.
  - Active-corridor corrections / selector-permission corrections: `3` / `0`.
  - Witness conflicts / terminal ready areas / source-backed R3 hits: `2` / `0` / `0`.
  - Fingerprint: `targets=4|canon=4|markdown=4|annotated=4|format=4|rawMissing=volcano_bonds|activeCorr=3|selectorCorr=0|witnessConflicts=2|ready=0|sourceR3=0`.
  - Frontier now records `105` focused local checks.
- Conclusion:
  - Use canonical/DOCM/Markdown for exact active target wording and DOCM/high-res/crop-pack for format authority.
  - Correction markup, Markdown bold, and annotated notes remain witnesses/context, not extraction instructions.
  - Keep source-review gating; do not reopen current-scan selector/key work without distinct source-backed unit/order evidence.

### Source Packet Active Format Stream Control

- Status: checked; active text/format/OVERDOSE streams remain controlled validation descriptors, not selectors.
- Evidence:
  - `scripts/audit_source_packet_active_format_stream_control.py`
  - `analysis_outputs/source_audit/source_packet_active_format_stream_control/source_packet_active_format_stream_control.md`
  - `analysis_outputs/source_audit/source_packet_active_format_stream_control/source_packet_active_format_stream_control.json`
  - `analysis_outputs/source_audit/source_packet_active_format_stream_control/source_packet_active_format_stream_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested named streams from active target initials/edges, readable line/corridor order, x-order, orange/black grouping, and measured OVERDOSE slot projections.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Stream modes checked: `12`.
  - Strict instruction hits: `0`.
  - OVER layout streams: `3`.
  - p75 single-row OVER controls: `1`.
  - Mirrored variants where p75 matches active black: `8/8`.
  - Full-page YKKY combinations / contiguous windows: `11` / `1`.
  - Selector-permission corrections / source-backed R3 hits / satisfied reopen triggers: `0` / `0` / `0/9`.
  - Fingerprint: `streams=12|strictHits=0|overStreams=3|p75Over=1|ykky=11|selectorCorr=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `106` focused local checks.
- Conclusion:
  - Do not promote active initials/edges, color grouped order, readable/x-order, or OVERDOSE slot labels as selector instructions.
  - The active black `OVER` remains controlled by p75 and mirror/reverse behavior.
  - Reopen selector/key work only with distinct source-backed unit/order evidence.

### Source Packet Active Index-Slot Control

- Status: checked; active line/corridor indexes do not supply an OVERDOSE slot selector.
- Evidence:
  - `scripts/audit_source_packet_active_index_slot_control.py`
  - `analysis_outputs/source_audit/source_packet_active_index_slot_control/source_packet_active_index_slot_control.md`
  - `analysis_outputs/source_audit/source_packet_active_index_slot_control/source_packet_active_index_slot_control.json`
  - `analysis_outputs/source_audit/source_packet_active_index_slot_control/source_packet_active_index_slot_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested active O4/B4/G5/O5 page lines, corridor indexes, color states, and measured OVERDOSE center-slot indexes/letters for a bounded index-to-slot rule.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active targets checked: `4`.
  - Line / corridor / line+corridor modulo-8 slot fits: `0` / `0` / `0`.
  - Line/corridor parity state: `YKKY` / `YKKY`.
  - Slot parity state: `KKYY`.
  - Line/corridor gaps vs slot gaps: `3/2/5` / `4/1/2`.
  - Slot/x order is a one-step rotation of readable line order, but no source names a rotation or start point.
  - Full-page YKKY combinations / p75 OVER controls: `11` / `1`.
  - Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
  - Fingerprint: `targets=4|lineSlotFits=0|corrSlotFits=0|lineCorrSlotFits=0|lineParity=YKKY|slotParity=KKYY|slotRot=1|slotGaps=4/1/2|ykky=11|p75Over=1|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `107` focused local checks.
- Conclusion:
  - Do not promote line/corridor parity, slot-order rotation, or active index-to-OVERDOSE-slot observations as selector instructions.
  - Keep the relation as a source-validation descriptor only.
  - Reopen selector/key work only with distinct source-backed unit/order evidence.

### Source Packet Center Rotation Word Control

- Status: checked; rotated active center-slot words are arbitrary short-word artifacts, not selectors.
- Evidence:
  - `scripts/audit_source_packet_center_rotation_word_control.py`
  - `analysis_outputs/source_audit/source_packet_center_rotation_word_control/source_packet_center_rotation_word_control.md`
  - `analysis_outputs/source_audit/source_packet_center_rotation_word_control/source_packet_center_rotation_word_control.json`
  - `analysis_outputs/source_audit/source_packet_center_rotation_word_control/source_packet_center_rotation_word_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Enumerated rotations/reversals of measured active OVERDOSE center streams from mirrored/reversed variants and checked source witnesses for strict start/rotation cue phrases.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Center stream rows checked: `16`; unique center streams: `6`.
  - Rotation/reversal rows checked: `128`.
  - Thematic short-word hit rows: `32`, with unique hits `DOVE`, `EROS`, `ROSE`, and `SORE`.
  - DOVE hit rows: `8`.
  - Source start/rotation cue hits: `0`.
  - p75 active-black mirror matches: `8/8`.
  - Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
  - Fingerprint: `streams=16|unique=6|rotRows=128|themeHits=32|layoutHits=0|DOVE=8|cueHits=0|slotRot=1|lineSlotFits=0|p75match=8/8|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `108` focused local checks.
- Conclusion:
  - Do not promote rotated center words such as `DOVE` as selector instructions.
  - Keep all rotated/reversed center short words as arbitrary artifacts until a distinct source supplies start/rotation wording.
  - Reopen selector/key work only with distinct source-backed unit/order evidence.

### Source Packet Color Split Span Control

- Status: checked; active orange/black OVERDOSE span grouping remains a controlled layout artifact, not a selector.
- Evidence:
  - `scripts/audit_source_packet_color_split_span_control.py`
  - `analysis_outputs/source_audit/source_packet_color_split_span_control/source_packet_color_split_span_control.md`
  - `analysis_outputs/source_audit/source_packet_color_split_span_control/source_packet_color_split_span_control.json`
  - `analysis_outputs/source_audit/source_packet_color_split_span_control/source_packet_color_split_span_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Enumerated active orange/black OVERDOSE slot-span streams under the 8 mirrored/reversed variants, including pure black, pure orange, and grouped color orders.
  - Checked source witnesses for color-split cue phrases.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Variant rows checked: `8`; color/slot span streams checked: `72`.
  - Layout-hit rows: `56`.
  - Black span layout-hit rows / orange span layout-hit rows / grouped color layout-hit rows: `8` / `0` / `28`.
  - Strict instruction stream hits / source color-split cue hits: `0` / `0`.
  - Unique active black streams: `DOSE`, `ESOD`, `OVER`, and `REVO`.
  - Unique pure active orange streams: `DREREV`, `RDODOS`, `SODODR`, and `VERERD`.
  - p75 active-black mirror matches / p75 single-row OVER controls: `8/8` / `1`.
  - Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
  - Fingerprint: `variants=8|streams=72|layoutHits=56|blackLayout=8|orangeLayout=0|groupedLayout=28|strictHits=0|colorCueHits=0|blackStreams=DOSE,ESOD,OVER,REVO|p75match=8/8|p75Over=1|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `109` focused local checks.
- Conclusion:
  - Do not promote orange/black OVERDOSE slot-span grouping as a selector instruction.
  - Treat black-span layout words as p75-controlled and mirror/reverse-sensitive.
  - Reopen selector/key work only with distinct source-backed color/order or unit/order evidence that also defeats the p75 control.

### Source Packet Dominant Overlap Slot Control

- Status: checked; dominant-overlap OVERDOSE slot selection duplicates center-slot behavior and is not a selector.
- Evidence:
  - `scripts/audit_source_packet_dominant_overlap_slot_control.py`
  - `analysis_outputs/source_audit/source_packet_dominant_overlap_slot_control/source_packet_dominant_overlap_slot_control.md`
  - `analysis_outputs/source_audit/source_packet_dominant_overlap_slot_control/source_packet_dominant_overlap_slot_control.json`
  - `analysis_outputs/source_audit/source_packet_dominant_overlap_slot_control/source_packet_dominant_overlap_slot_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Selected the single OVERDOSE slot with maximum horizontal overlap for each active target across the 8 mirrored/reversed variants.
  - Compared dominant-overlap streams with center-slot streams and checked source witnesses for dominant/maximum-overlap cue phrases.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Variant rows checked: `8`; dominant-overlap streams checked: `40`.
  - Active line/x dominant streams matching center streams: `16/16`.
  - Active dominant center mismatches / active dominant ambiguity count: `0` / `0`.
  - Layout-hit rows / thematic-hit rows: `0` / `4`.
  - Black dominant streams: `EV`, `OS`, `SO`, and `VE`.
  - Orange dominant streams: `DO`, `ER`, `OD`, and `RE`.
  - p75 dominant streams: `E`, `O`, `S`, and `V`.
  - Source dominant-overlap cue hits: `0`.
  - Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
  - Fingerprint: `variants=8|streams=40|activeStreams=16|centerMatch=16/16|mismatch=0|ambig=0|layoutHits=0|themeHits=4|black=EV,OS,SO,VE|orange=DO,ER,OD,RE|p75=E,O,S,V|cueHits=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `110` focused local checks.
- Conclusion:
  - Do not promote maximum-overlap slot selection as an extraction instruction.
  - Keep it as a center-slot duplicate and visual sanity check.
  - Reopen selector/key work only with distinct source-backed maximum-overlap or slot-selection evidence.

### Source Packet Span Edge Slot Control

- Status: checked; first/last touched OVERDOSE slot edges are not a selector.
- Evidence:
  - `scripts/audit_source_packet_span_edge_slot_control.py`
  - `analysis_outputs/source_audit/source_packet_span_edge_slot_control/source_packet_span_edge_slot_control.md`
  - `analysis_outputs/source_audit/source_packet_span_edge_slot_control/source_packet_span_edge_slot_control.json`
  - `analysis_outputs/source_audit/source_packet_span_edge_slot_control/source_packet_span_edge_slot_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Selected the first/last OVERDOSE slots touched by each active highlighted phrase across the 8 mirrored/reversed variants.
  - Checked active line order, active x order, black x order, orange x order, and p75 control rows.
  - Checked source witnesses for first/last, left/right, and boundary-slot cue phrases.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Variant rows checked: `8`; span-edge streams checked: `80`.
  - Active line/x edge streams checked: `32`.
  - Layout-hit rows / active layout-hit rows: `0` / `0`.
  - Thematic-hit rows / active thematic-hit rows: `0` / `0`.
  - Black edge streams: `DS`, `EO`, `OE`, `RV`, `SD`, and `VR`.
  - Orange edge streams: `DR`, `EV`, `OS`, `RD`, `SO`, and `VE`.
  - p75 edge streams: `D`, `E`, `O`, and `R`.
  - Source edge-slot cue hits: `0`.
  - Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
  - Fingerprint: `variants=8|streams=80|activeStreams=32|layoutHits=0|activeLayout=0|themeHits=0|activeTheme=0|black=DS,EO,OE,RV,SD,VR|orange=DR,EV,OS,RD,SO,VE|p75=D,E,O,R|edgeCueHits=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `111` focused local checks.
- Conclusion:
  - Do not promote first/last touched OVERDOSE slots as an extraction instruction.
  - Keep boundary-slot streams as visual controls only.
  - Reopen selector/key work only with distinct source-backed first/last, left/right, or boundary-slot evidence.

### Source Packet Overlap Width Profile Control

- Status: checked; measured OVERDOSE overlap-width profiles are source-registration diagnostics only, not a selector.
- Evidence:
  - `scripts/audit_source_packet_overlap_width_profile_control.py`
  - `analysis_outputs/source_audit/source_packet_overlap_width_profile_control/source_packet_overlap_width_profile_control.md`
  - `analysis_outputs/source_audit/source_packet_overlap_width_profile_control/source_packet_overlap_width_profile_control.json`
  - `analysis_outputs/source_audit/source_packet_overlap_width_profile_control/source_packet_overlap_width_profile_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Classified measured OVERDOSE overlap-width profiles under the 8 mirrored/reversed variants.
  - Checked active line order, active x order, black x order, orange x order, and p75 control rows.
  - Checked source witnesses for overlap-width, coverage-profile, slot-width, and ratio cue phrases.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Variant rows checked: `8`; overlap-width profile streams checked: `40`.
  - Active line/x profile streams checked: `16`.
  - Reference slot width: `244.57` px.
  - Active slot-count streams: `2-2-3-3`, `3-2-2-3`, and `3-3-2-2`.
  - Active fullish-count streams: `0-1-2-1`, `1-0-1-2`, and `1-2-1-0`.
  - Active dominant-position streams: `MLRM`, `MMRL`, `MRLM`, and `RLMM`.
  - Active edge-bias streams: `LRLL`, `RLLL`, `RLRR`, and `RRRL`.
  - Active slot counts / p75 slot counts: `[2, 3]` / `[4]`; active shares p75 slot count: `False`.
  - Source overlap-width/profile cue hits: `0`.
  - Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
  - Fingerprint: `variants=8|streams=40|activeStreams=16|slotWidth=244.57|activeSlots=2-2-3-3,3-2-2-3,3-3-2-2|fullish=0-1-2-1,1-0-1-2,1-2-1-0|dom=MLRM,MMRL,MRLM,RLMM|bias=LRLL,RLLL,RLRR,RRRL|p75Slots=4|shareP75Slots=0|widthCueHits=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `112` focused local checks.
- Conclusion:
  - Do not promote measured overlap-width profiles as an extraction instruction.
  - Keep them as phrase-width/source-registration diagnostics only.
  - Reopen selector/key work only with distinct source-backed overlap-width, coverage-ratio, or profile-order evidence.

### Source Packet Span Neighbor Slot Control

- Status: checked; immediate outside-neighbor OVERDOSE slots are not a selector.
- Evidence:
  - `scripts/audit_source_packet_span_neighbor_slot_control.py`
  - `analysis_outputs/source_audit/source_packet_span_neighbor_slot_control/source_packet_span_neighbor_slot_control.md`
  - `analysis_outputs/source_audit/source_packet_span_neighbor_slot_control/source_packet_span_neighbor_slot_control.json`
  - `analysis_outputs/source_audit/source_packet_span_neighbor_slot_control/source_packet_span_neighbor_slot_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Selected the immediate outside OVERDOSE neighbor slots before and after each active highlighted span under the 8 mirrored/reversed variants.
  - Checked active line order, active x order, black x order, orange x order, and p75 control rows.
  - Checked source witnesses for adjacent, outside, next/previous, and flanking slot/letter cue phrases.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Variant rows checked: `8`; span-neighbor streams checked: `120`.
  - Active line/x neighbor streams checked: `48`.
  - Layout-hit rows / active layout-hit rows: `0` / `0`.
  - Thematic-hit rows / active thematic-hit rows: `0` / `0`.
  - Black neighbor streams: `DE`, `DVE`, `ED`, `EVD`, `OR`, `OSR`, `RO`, `RSO`, `S`, and `V`.
  - Orange neighbor streams: `DO`, `ER`, `ERSE`, `ES`, `ESRE`, `OD`, `ODVO`, `OV`, `OVDO`, `RE`, `SE`, and `VO`.
  - p75 neighbor streams: empty, `D`, and `R`.
  - Active boundary-missing count: `48`.
  - Source neighbor-slot cue hits: `0`.
  - Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
  - Fingerprint: `variants=8|streams=120|activeStreams=48|layoutHits=0|activeLayout=0|themeHits=0|activeTheme=0|black=DE,DVE,ED,EVD,OR,OSR,RO,RSO,S,V|orange=DO,ER,ERSE,ES,ESRE,OD,ODVO,OV,OVDO,RE,SE,VO|p75=,D,R|missing=48|neighborCueHits=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `113` focused local checks.
- Conclusion:
  - Do not promote immediate outside-neighbor OVERDOSE slots as an extraction instruction.
  - Keep them as boundary-sensitive visual controls only.
  - Reopen selector/key work only with distinct source-backed adjacent, outside, next/previous, or flanking-letter evidence.

### Source Packet Span Complement Slot Control

- Status: checked; untouched/remainder OVERDOSE slots are not a selector.
- Evidence:
  - `scripts/audit_source_packet_span_complement_slot_control.py`
  - `analysis_outputs/source_audit/source_packet_span_complement_slot_control/source_packet_span_complement_slot_control.md`
  - `analysis_outputs/source_audit/source_packet_span_complement_slot_control/source_packet_span_complement_slot_control.json`
  - `analysis_outputs/source_audit/source_packet_span_complement_slot_control/source_packet_span_complement_slot_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Selected the untouched/remainder OVERDOSE slots not covered by each active highlighted span under the 8 mirrored/reversed variants.
  - Checked active line order, active x order, black x order, orange x order, and p75 control rows.
  - Checked source witnesses for untouched, remaining, remainder, complement, uncovered, unused, leftover, negative-space, and outside-span cue phrases.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Variant rows checked: `8`; span-complement streams checked: `40`.
  - Active line/x complement streams checked: `16`.
  - Layout-hit rows / active layout-hit rows / p75 layout-hit rows: `40` / `16` / `8`.
  - Thematic-hit rows / active thematic-hit rows: `0` / `0`.
  - Black complement streams: `ERDOSEOVDOSE`, `ESODVOESODRE`, `ODREVOESREVO`, and `OVERSEOVERDO`.
  - Orange complement streams: `EREVOESEVO`, `ESOVOESODO`, `ODOSEOVOSE`, and `OVESEOVERE`.
  - p75 complement streams: `DOSE`, `ESOD`, `OVER`, and `REVO`.
  - Active complement slot-count streams: `5-5-6-6`, `5-6-6-5`, and `6-6-5-5`.
  - Source complement/remainder cue hits: `0`.
  - Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
  - Fingerprint: `variants=8|streams=40|activeStreams=16|layoutHits=40|activeLayout=16|p75Layout=8|themeHits=0|activeTheme=0|black=ERDOSEOVDOSE,ESODVOESODRE,ODREVOESREVO,OVERSEOVERDO|orange=EREVOESEVO,ESOVOESODO,ODOSEOVOSE,OVESEOVERE|p75=DOSE,ESOD,OVER,REVO|counts=5-5-6-6,5-6-6-5,6-6-5-5|complementCueHits=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `114` focused local checks.
- Conclusion:
  - Do not promote untouched/remainder OVERDOSE slots as an extraction instruction.
  - Keep them as non-selective visual artifacts: complements naturally preserve most of `OVERDOSE`, and p75 controls also spell layout fragments.
  - Reopen selector/key work only with distinct source-backed untouched, remaining, unused, or remainder-letter evidence.

### Source Packet Local Asset Orientation Gate

- Status: checked; currently available local image/PDF assets do not reopen source review.
- Evidence:
  - `scripts/audit_source_packet_local_asset_orientation_gate.py`
  - `analysis_outputs/source_audit/source_packet_local_asset_orientation_gate/source_packet_local_asset_orientation_gate.md`
  - `analysis_outputs/source_audit/source_packet_local_asset_orientation_gate/source_packet_local_asset_orientation_gate.json`
  - `analysis_outputs/source_audit/source_packet_local_asset_orientation_gate/source_packet_local_asset_orientation_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared local source-like images and recorded local PDFs against the page-76 readable/upright orientation gate and native `source_images` baseline.
  - Tested candidate image orientation as-is vs 180-degree rotation, whole-page similarity, and active O4/B4/G5/O5 crop similarity.
  - Checked whether any local asset improves R1/R5 enough to reopen source review.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Image candidates checked: `40`; PDF candidates recorded: `3`.
  - Page-76 image matches / derivative matches: `2` / `4`.
  - Exact current-scan matches: `1`.
  - Higher-resolution page-76 matches: `0`.
  - R1 distinct improved local image candidates: `0`.
  - Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
  - True page-76 matches were the current native baseline `analysis_outputs/source_images/magazine_page_76.jpg` and same-resolution `magazine-4_1.jpg`.
  - The fold PNGs are lower-resolution derivatives, not improved source captures.
  - Fingerprint: `images=40|pdfs=3|page76=2|derivatives=4|exact=1|higherRes=0|r1Improved=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `115` focused local checks.
- Conclusion:
  - Do not reopen source review or extraction from currently available local image/PDF assets.
  - Keep the source-acquisition packet as the next-action checklist.
  - Reopen selector/key work only with a new physical/original-layout/raw-clue asset that improves R1/R5 and supplies R3 unit/order evidence.

### Source Packet PDF Render Quality Gate

- Status: checked; currently available local PDF renders and embedded PDF images do not reopen source review.
- Evidence:
  - `scripts/audit_source_packet_pdf_render_quality_gate.py`
  - `analysis_outputs/source_audit/source_packet_pdf_render_quality_gate/source_packet_pdf_render_quality_gate.md`
  - `analysis_outputs/source_audit/source_packet_pdf_render_quality_gate/source_packet_pdf_render_quality_gate.json`
  - `analysis_outputs/source_audit/source_packet_pdf_render_quality_gate/source_packet_pdf_render_quality_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Rendered `keyser bitcoin .pdf`, `magazine.pdf`, and `analysis_outputs/external_clues/google_drive_article_download.pdf` at 300 dpi.
  - Inspected their embedded page images against the page-76 readable/upright orientation gate and native `source_images` baseline.
  - Tested as-is vs 180-degree orientation, whole-page similarity, and active O4/B4/G5/O5 crop similarity.
  - Checked whether any PDF improves R1/R5 enough to reopen source review or satisfies source-backed R3 triggers.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDF candidates checked: `3`; PDF pages rendered: `24`; embedded page images checked: `24`.
  - Page-76 render / embedded matches: `1` / `1`.
  - Unique PDF page-76 pages: `1`.
  - Derivative render / embedded matches: `3` / `3`.
  - Higher-resolution page-76 render / embedded matches: `0` / `0`.
  - R1 distinct improved PDF candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - The only true page-76 PDF hit was `magazine.pdf` page `4`, at the already-known `2544x3264` current source resolution; its embedded image matched `magazine-4_1.jpg`.
  - `keyser bitcoin .pdf` and `analysis_outputs/external_clues/google_drive_article_download.pdf` are byte-identical and embed lower-resolution `2040x2805` page images; neither produced a page-76 match under the source-comparison threshold.
  - Fingerprint: `pdfs=3|pages=24|embedded=24|candidates=48|page76Render=1|page76Embedded=1|uniquePage76=1|higherRender=0|higherEmbedded=0|r1Improved=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `116` focused local checks.
- Conclusion:
  - Do not reopen source review or extraction from currently available local PDF renders or embedded PDF images.
  - Treat `magazine.pdf` page `4` as a duplicate/current-baseline source, not a distinct higher-resolution source.
  - Keep the source-acquisition packet as the next-action checklist.
  - Reopen selector/key work only with a new physical/original-layout/raw-clue asset that improves R1/R5 and supplies R3 unit/order evidence.

### Source Packet Fold-World OVERDOSE Order Control

- Status: checked; folded/mirrored 3D world order does not reopen OVERDOSE-slot extraction.
- Evidence:
  - `scripts/audit_source_packet_fold_world_overdose_order_control.py`
  - `analysis_outputs/source_audit/source_packet_fold_world_overdose_order_control/source_packet_fold_world_overdose_order_control.md`
  - `analysis_outputs/source_audit/source_packet_fold_world_overdose_order_control/source_packet_fold_world_overdose_order_control.json`
  - `analysis_outputs/source_audit/source_packet_fold_world_overdose_order_control/source_packet_fold_world_overdose_order_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested page order, page x order, fold-world x/y order, fold-depth z order, and fold-center distance order for active O4/B4/G5/O5.
  - Mapped each order to active OVERDOSE center-slot streams, visual-state streams, color streams, rotations/reversals, layout words, thematic words, explicit source depth/fold-order cues, R3 bridge status, and reopen triggers.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Page/fold/depth/distance order modes checked: `9`.
  - Unique active center-slot streams: `DEVO,ODEV,OEVD,OVED,VEDO`.
  - Known page/x stream order rows: `5`.
  - Fold-only new streams: `DEVO,ODEV,OEVD`.
  - Instruction-hit order rows: `0`.
  - Layout-hit / thematic-hit order rows: `0` / `8`.
  - Explicit source depth/front-back/fold-order cue hits: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `orders=9|unique=5|streams=DEVO,ODEV,OEVD,OVED,VEDO|knownOrders=5|new=DEVO,ODEV,OEVD|instructionRows=0|layoutRows=0|themeRows=8|sourceDepthCues=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `117` focused local checks.
- Conclusion:
  - Do not promote fold-world x/y/z/depth/distance order as an extraction selector.
  - The fold-only streams are permutations of the same active quartet and do not supply instruction/layout terms.
  - The `DOVE` thematic rotations remain controlled short-word artifacts, not R3 evidence.
  - Keep folded/mirrored 3D geometry as source-validation/orientation context only.
  - Reopen selector/key work only with a new physical/original-layout/raw-clue asset that improves R1/R5 and supplies R3 unit/order evidence.

### Source Packet Bold Phrase Length Slot Control

- Status: checked; active bold/highlight phrase word-count and phrase-length mechanics do not reopen OVERDOSE-slot extraction.
- Evidence:
  - `scripts/audit_source_packet_bold_phrase_length_slot_control.py`
  - `analysis_outputs/source_audit/source_packet_bold_phrase_length_slot_control/source_packet_bold_phrase_length_slot_control.md`
  - `analysis_outputs/source_audit/source_packet_bold_phrase_length_slot_control/source_packet_bold_phrase_length_slot_control.json`
  - `analysis_outputs/source_audit/source_packet_bold_phrase_length_slot_control/source_packet_bold_phrase_length_slot_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested whether active bold/highlight phrase word counts, character counts, DOCM highlight counts, or phrase lengths select OVERDOSE slot spans or center slots for O4/B4/G5/O5.
  - Compared the active quartet against non-active grey/black controls, including the p75 `OVER` control.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active rows / controls / focused controls checked: `4` / `13` / `5`.
  - Active word-count equals touched OVERDOSE slot-count in `4/4` rows.
  - Non-active grey control word-count equals touched OVERDOSE slot-count in `3/13` rows, including the p75 `OVER` control.
  - Character, highlight, and phrase-length metrics produce `0` all-active count-to-center-slot fits; best partial fit is `2/4`.
  - Source/generated count or length cue hits: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|controls=13|activeWordSpan=4/4|controlWordSpan=3/13|p75OverWordSpan=1|allCenterFitMetrics=0|partialCenterFitMax=2|sourceCountCues=0|generatedCountCues=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `118` focused local checks.
- Conclusion:
  - Do not promote active phrase word-count or phrase-length mechanics as an extraction selector.
  - The active `4/4` word-count/span-count match is a controlled coincidence because non-active grey controls, especially the p75 `OVER` row, show the same mechanic.
  - Reopen selector/key work only with a new physical/original-layout/raw-clue asset that improves R1/R5 and supplies R3 unit/order evidence.

### Source Packet Bold Phrase Edge Slot Control

- Status: checked; active bold/highlight phrase initials, finals, and edge/acrostic streams do not reopen OVERDOSE-slot extraction.
- Evidence:
  - `scripts/audit_source_packet_bold_phrase_edge_slot_control.py`
  - `analysis_outputs/source_audit/source_packet_bold_phrase_edge_slot_control/source_packet_bold_phrase_edge_slot_control.md`
  - `analysis_outputs/source_audit/source_packet_bold_phrase_edge_slot_control/source_packet_bold_phrase_edge_slot_control.json`
  - `analysis_outputs/source_audit/source_packet_bold_phrase_edge_slot_control/source_packet_bold_phrase_edge_slot_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested phrase first letters, last letters, word initials, word finals, first/last pairs, and the same edge streams under the 9 active page/fold/depth/distance orders.
  - Compared active O4/B4/G5/O5 against non-active grey/black controls and source/generated witness cue terms.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active rows / controls / fold-order rows checked: `4` / `13` / `9`.
  - Active center-edge hit rows: `0`.
  - Active touched-span edge hit rows: `0`.
  - Control center/span edge hit rows: `0` / `3`.
  - Fold-order edge-stream instruction/layout hit rows: `0` / `0`.
  - Fold-order edge streams containing their center-slot stream: `0`.
  - Source/generated initial/final/acrostic cue rows: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|controls=13|orders=9|activeCenterEdge=0|activeSpanEdge=0|controlCenterEdge=0|controlSpanEdge=3|orderInstruction=0|orderLayout=0|orderContainsCenter=0|sourceEdgeCues=0|generatedEdgeCues=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `119` focused local checks.
- Conclusion:
  - Do not promote phrase initials, finals, edge letters, or acrostic/fold-order edge streams as an extraction selector.
  - The active edge streams do not line up with active OVERDOSE center/touched spans and do not produce instruction/layout wording under folded/mirrored order variants.
  - Reopen selector/key work only with a new physical/original-layout/raw-clue asset that improves R1/R5 and supplies R3 unit/order evidence.

### Current-Scan Held-To-Light Simulator

- Status: built; current PDF/page scan can now be reviewed as an explicit held-to-light/light-table simulator, but it does not unlock extraction.
- Evidence:
  - `scripts/audit_current_scan_held_to_light_simulator.py`
  - `analysis_outputs/source_audit/current_scan_held_to_light_simulator/index.html`
  - `analysis_outputs/source_audit/current_scan_held_to_light_simulator/current_scan_held_to_light_simulator.md`
  - `analysis_outputs/source_audit/current_scan_held_to_light_simulator/current_scan_held_to_light_simulator.json`
  - `analysis_outputs/source_audit/current_scan_held_to_light_simulator/current_scan_held_to_light_simulator_sheet.jpg`
  - Pair/mode overlay images in `analysis_outputs/source_audit/current_scan_held_to_light_simulator/`.
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used current PDF-extracted page images from `analysis_outputs/source_images/magazine_page_75..80.jpg`.
  - Rotated those images 180 degrees into the readable/upright coordinate frame, then simulated bleed-through by horizontally mirroring the back page over the target page.
  - Tested true same-leaf directions 75/76, 77/78, and 79/80, plus non-physical visual-registration benchmarks 78->76, 79->76, and facing-spread 78->79.
  - No OCR extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Pair/mode rows checked: `9` / `21`.
  - Natural same-leaf 75->76 active O4/B4/G5/O5 coverage: `0.1003`.
  - Best bounded same-leaf 75->76 active coverage: `0.3242` at dx/dy `-220,200`; this is a forced translation at the search boundary, not a natural leaf alignment.
  - Best page-76 active overlay: `nonphysical_79_to_76` / `best_global_feature`, active coverage `0.3840`, dx/dy `40,80`.
  - Best global feature overlay: `same_leaf_77_to_78` / `best_global_feature`, balanced `0.5220`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pairs=9|rows=21|sameLeaf75natural=0.1003|sameLeaf75best=0.3242@-220,200|bestP76=nonphysical_79_to_76:best_global_feature:0.3840@40,80|bestGlobal=same_leaf_77_to_78:0.5220|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `120` focused local checks.
- Conclusion:
  - Use the simulator as a manual visual review and source-clue testing surface.
  - Do not treat current-scan hold-to-light as solved extraction: the physically valid 75->76 same-leaf path does not naturally select the lower O4/B4/G5/O5 corridor.
  - The strongest page-76 active overlay remains the non-physical 79->76 visual-registration benchmark, so it needs a source/layout rule before it can become a selector.
  - Next best experiment is PDF object/layout inspection for embedded image provenance, page object resources, and reusable original-layout evidence.

### Current PDF Object/Layout Inspection

- Status: checked; the current PDFs contain raster page images with OCR/text overlays, not native original-layout objects that unlock extraction.
- Evidence:
  - `scripts/audit_current_pdf_object_layout_inspection.py`
  - `analysis_outputs/source_audit/current_pdf_object_layout_inspection/current_pdf_object_layout_inspection.md`
  - `analysis_outputs/source_audit/current_pdf_object_layout_inspection/current_pdf_object_layout_inspection.json`
  - `analysis_outputs/source_audit/current_pdf_object_layout_inspection/current_pdf_object_layout_inspection_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected `magazine.pdf`, `keyser bitcoin .pdf`, and `analysis_outputs/external_clues/google_drive_article_download.pdf` as PDF objects.
  - Checked page resources, image placements, rotations, OCR/text layers, fonts, vectors, duplicate hashes, page-76 image provenance, and whether any native original-layout evidence exists.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / unique SHA groups / pages checked: `3` / `2` / `24`.
  - `keyser bitcoin .pdf` and `analysis_outputs/external_clues/google_drive_article_download.pdf` are byte-identical duplicates.
  - Page-76 candidate pages: `3`.
  - Page-76 raster-dominated pages: `3/3`.
  - Page-76 OCR/text-layer pages: `3/3`.
  - Page-76 native original-layout object evidence: `0`.
  - Page-76 text blocks / fonts / vectors / partial image placements: `94` / `3` / `0` / `2`.
  - Page-76 exact active phrase OCR hits / strict unit-order term hits: `0` / `0`.
  - Page-76 largest image dimensions: `2040x2805, 2544x3264`.
  - Higher-than-magazine page-76 image count: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|sha=2|pages=24|p76=3|p76Raster=3|p76OcrText=3|p76NativeLayout=0|p76Text=94|p76Fonts=3|p76Vectors=0|p76PartialImages=2|activePhraseHits=0|unitTermHits=0|higherP76=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `121` focused local checks.
- Conclusion:
  - Do not treat PDF object structure as the missing original-layout selector.
  - The OCR/text layer is a source witness, but it is corrupt/derivative and supplies no native layout objects, hidden placement metadata, higher-resolution page-76 asset, exact active phrase OCR hit, or strict unit/order wording.
  - Next best experiment is a crop-level light-table inspection around O4/B4/G5/O5 using the current held-to-light simulator, focused on valid 75->76 and benchmark 79->76 overlays.

### Current-Scan Crop Light-Table Targets

- Status: checked; crop-level held-to-light around O4/B4/G5/O5 does not unlock an extraction selector.
- Evidence:
  - `scripts/audit_current_scan_crop_light_table_targets.py`
  - `analysis_outputs/source_audit/current_scan_crop_light_table_targets/index.html`
  - `analysis_outputs/source_audit/current_scan_crop_light_table_targets/current_scan_crop_light_table_targets.md`
  - `analysis_outputs/source_audit/current_scan_crop_light_table_targets/current_scan_crop_light_table_targets.json`
  - `analysis_outputs/source_audit/current_scan_crop_light_table_targets/current_scan_crop_light_table_targets_sheet.jpg`
  - Target crop panels in `analysis_outputs/source_audit/current_scan_crop_light_table_targets/`.
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Zoomed the current held-to-light simulation into active page-76 O4/B4/G5/O5 boxes.
  - Compared physically valid 75->76 same-leaf alignment against the strongest non-physical 79->76 visual-registration benchmark.
  - Included natural and best-shift variants.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Scenarios / target crop rows: `4` / `16`.
  - All-four active target coverage at >=10% / >=25% / >=50%: `1` / `0` / `0`.
  - Best mean active coverage: `benchmark_79_to_76_best` at `0.3521`.
  - Best >=50% target count: `valid_75_to_76_forced_best` with `1/4` targets.
  - Valid natural 75->76 O4/B4/G5/O5 source coverage: `0.1223,0.0000,0.0526,0.1654`.
  - Valid forced 75->76 O4/B4/G5/O5 source coverage: `0.9766,0.1299,0.0540,0.0999`.
  - Benchmark 79->76 best O4/B4/G5/O5 source coverage: `0.8416,0.1138,0.1328,0.3203`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `scenarios=4|targets=16|all10=1|all25=0|all50=0|bestMean=benchmark_79_to_76_best:0.3521|best50=valid_75_to_76_forced_best:1|validNat=0.1223,0.0000,0.0526,0.1654|validForced=0.9766,0.1299,0.0540,0.0999|bench79=0.8416,0.1138,0.1328,0.3203|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `122` focused local checks.
- Conclusion:
  - Do not promote crop-level light-table ink as an extraction selector.
  - The valid 75->76 leaf does not cover all four O4/B4/G5/O5 targets, even with the forced boundary shift; the forced case mostly concentrates on O4.
  - The strongest 79->76 overlay remains non-physical and still concentrates mainly on O4/O5.
  - Next best experiment is to project actual OVERDOSE glyph rectangles into these same crop windows and compare whether glyph geometry, not generic ink overlap, supplies a source-backed unit/order rule.

### Current-Scan OVERDOSE Glyph Crop Projection

- Status: checked; actual `OVERDOSE` glyph rectangles inside current held-to-light crop windows do not unlock extraction.
- Evidence:
  - `scripts/audit_current_scan_overdose_glyph_crop_projection.py`
  - `analysis_outputs/source_audit/current_scan_overdose_glyph_crop_projection/current_scan_overdose_glyph_crop_projection.md`
  - `analysis_outputs/source_audit/current_scan_overdose_glyph_crop_projection/current_scan_overdose_glyph_crop_projection.json`
  - `analysis_outputs/source_audit/current_scan_overdose_glyph_crop_projection/current_scan_overdose_glyph_crop_projection_sheet.jpg`
  - Per-target glyph-slot crop panels in `analysis_outputs/source_audit/current_scan_overdose_glyph_crop_projection/`.
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Projected actual measured p76/p78 `OVERDOSE` header glyph slots into the current scan held-to-light crop windows for O4/B4/G5/O5.
  - Tested valid 75->76 natural and forced alignments against natural and best non-physical 79->76.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Glyph projections / scenario-projection rows / target rows: `2` / `8` / `32`.
  - All-four dominant >=10% / touched >=25% / touched >=50%: `4` / `0` / `0`.
  - Layout-hit streams / strict instruction hits: `6` / `0`.
  - Valid natural 75->76 dominant line stream: `S.RD`; black >=10% x stream: `R`.
  - Valid forced 75->76 dominant line stream: `OVRR`; black >=10% x stream: `VR`.
  - Best non-physical 79->76 dominant line stream: `DVRR`; black >=10% x stream: `OVER`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `glyphs=2|scenarioProj=8|targets=32|allDom10=4|all25=0|all50=0|layoutStreams=6|strict=0|validNat=S.RD|validForced=OVRR|bench79=DVRR|black10=R/VR/OVER|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `123` focused local checks.
- Conclusion:
  - Do not promote actual `OVERDOSE` glyph rectangles inside the current light-table crop windows as an extraction selector.
  - The glyph-aware pass does not create a physically valid all-four O4/B4/G5/O5 selector at meaningful thresholds; all >=25% and >=50% all-four counts remain `0`.
  - The only clean black `OVER` stream appears in the non-physical 79->76 benchmark and is already controlled by earlier p75/OVERDOSE slot reports.
  - Next best experiment is not another slot permutation; inspect page-76 highlight edges or crop-window boundaries for source-backed instruction terms, or require distinct source/original-layout material before extraction resumes.

### Current-Scan Highlight/Crop Boundary Instruction Probe

- Status: checked; target highlight edges and crop-window boundaries do not expose source-backed instruction wording.
- Evidence:
  - `scripts/audit_current_scan_highlight_boundary_instruction_probe.py`
  - `analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/current_scan_highlight_boundary_instruction_probe.md`
  - `analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/current_scan_highlight_boundary_instruction_probe.json`
  - `analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/current_scan_highlight_boundary_instruction_probe_sheet.jpg`
  - Per-target crop panels in `analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/`.
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used the current PDF-extracted page-76 scan, locked O4/B4/G5/O5 boxes, and 3D OCR word map.
  - Probed both active highlight edge strips and current light-table crop-window boundary strips.
  - Looked only for explicit source unit/order terms such as word, letter, line, edge, side, crop, window, fold, mirror, first, last, left, and right.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active targets / boundary regions: `4` / `32`.
  - Target-edge regions / crop-window-edge regions: `16` / `16`.
  - Regions with OCR-map word hits: `21`.
  - Strict instruction regions: `0`.
  - Target-edge strict hits / crop-window strict hits: `0` / `0`.
  - Strict instruction term hits: `-`.
  - Context/thematic regions: `2`; context terms: `bitcoin`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `targets=4|regions=32|wordRegions=21|strictRegions=0|targetStrict=0|cropStrict=0|contextRegions=2|strictTerms=-|contextTerms=bitcoin|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `124` focused local checks.
- Conclusion:
  - Do not promote target highlight edges or crop-window boundaries as selectors on the current scan.
  - The boundary regions contain ordinary article context and noisy active-box OCR, not source-backed unit/order wording.
  - Next best move is manual visual anomaly review of the boundary sheet, or distinct physical/original-layout source evidence satisfying R1/R3 before selector/key work resumes.

### Current-Scan Boundary Light-Table Anomaly Probe

- Status: checked; held-to-light boundary ink does not unlock extraction.
- Evidence:
  - `scripts/audit_current_scan_boundary_light_table_anomaly_probe.py`
  - `analysis_outputs/source_audit/current_scan_boundary_light_table_anomaly_probe/current_scan_boundary_light_table_anomaly_probe.md`
  - `analysis_outputs/source_audit/current_scan_boundary_light_table_anomaly_probe/current_scan_boundary_light_table_anomaly_probe.json`
  - `analysis_outputs/source_audit/current_scan_boundary_light_table_anomaly_probe/current_scan_boundary_light_table_anomaly_probe_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used current PDF-extracted page images and current held-to-light transforms.
  - Tested source-page ink on target outer-edge strips and crop-window boundary strips around O4/B4/G5/O5.
  - Scenarios: valid 75->76 natural, valid 75->76 forced best-shift, and best non-physical 79->76.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Scenarios / boundary rows / boundary groups: `3` / `96` / `24`.
  - All-four boundary groups at >=10% / >=25% / >=50% source coverage: `2` / `0` / `0`.
  - Physically natural all-four >=10% groups: `0`.
  - Forced/non-physical all-four >=10% groups: `2`.
  - Weak all-four >=10% groups: `valid_75_to_76_forced_best:target_outer_edge:right`; `benchmark_79_to_76_best:target_outer_edge:top`.
  - Best mean boundary group: `valid_75_to_76_forced_best:target_outer_edge:right` at `0.3757`, coverage `0.6912,0.1487,0.5278,0.1352`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `scenarios=3|rows=96|groups=24|all10=2|all25=0|all50=0|naturalAll10=0|weak=valid_75_to_76_forced_best:target_outer_edge:right;benchmark_79_to_76_best:target_outer_edge:top|best=valid_75_to_76_forced_best:target_outer_edge:right:0.3757|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `125` focused local checks.
- Conclusion:
  - Do not promote held-to-light boundary ink as an extraction selector.
  - The only all-four boundary contacts are weak 10% contacts in forced/non-physical views; the physically natural 75->76 view has no all-four boundary side, and all groups fail >=25% and >=50%.
  - Next best move is not more boundary tuning; require a source clue naming a side/edge rule or a distinct original-layout/physical asset before selector/key work resumes.

### Current-Scan Boundary Contact Source Trace

- Status: checked; weak boundary contacts trace to source prose/noise, not an instruction layer.
- Evidence:
  - `scripts/audit_current_scan_boundary_contact_source_trace.py`
  - `analysis_outputs/source_audit/current_scan_boundary_contact_source_trace/current_scan_boundary_contact_source_trace.md`
  - `analysis_outputs/source_audit/current_scan_boundary_contact_source_trace/current_scan_boundary_contact_source_trace.json`
  - `analysis_outputs/source_audit/current_scan_boundary_contact_source_trace/current_scan_boundary_contact_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used the current scan/PDF-derived page images, current held-to-light transforms, and the 3D OCR word map.
  - Traced the two weak all-four boundary contacts back to their source-page regions with inverse held-to-light mapping.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Weak all-four boundary groups traced: `2`.
  - Source-trace rows / source word-hit rows: `8` / `4`.
  - Source strict instruction rows / source context-term rows: `0` / `0`.
  - Source strict instruction terms / context terms: `-` / `-`.
  - Page-75 word rows / trace rows: `1/4`; page-79 word rows / trace rows: `3/4`.
  - Page-75 trace text: only B4 hits `epithet.`; O4/G5/O5 are blank.
  - Page-79 trace text: B4 hits `you with all`, G5 hits `peace with it replaces`, O5 hits `ore`, and O4 is blank.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `weakGroups=2|rows=8|wordRows=4|strictRows=0|contextRows=0|strictTerms=-|contextTerms=-|p75Words=1/4|p79Words=3/4|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `126` focused local checks.
- Conclusion:
  - Do not promote the weak boundary contacts as selectors.
  - They trace to ordinary prose or blank/noisy source regions and contain no source-side unit/order instruction.
  - Next best move is a source-intake/reopen-gate sanity check or new original-layout evidence, not another boundary-threshold variant.

### Current PDF OCR Target Provenance Gate

- Status: checked; current PDF OCR layers do not supply source-side exact active target text or unit/order permission.
- Evidence:
  - `scripts/audit_current_pdf_ocr_target_provenance_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ocr_target_provenance_gate/current_pdf_ocr_target_provenance_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ocr_target_provenance_gate/current_pdf_ocr_target_provenance_gate.json`
  - `analysis_outputs/source_audit/current_pdf_ocr_target_provenance_gate/current_pdf_ocr_target_provenance_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected page-76 PDF text overlays from the current PDFs.
  - Checked exact O4/B4/G5/O5 phrase presence, component-token false positives, approximate active-box OCR words, OVERDOSE header text, and strict unit/order wording.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Exact active phrase rows: `0`.
  - PDFs with all four exact active phrases: `0`.
  - Component exact/stem-like hit rows: `4` / `6`.
  - Approximate target-box word rows / exact phrase rows: `8` / `0`.
  - Strict unit/order terms: `-`.
  - OVERDOSE header PDFs: `2`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Low-res duplicate PDF component hits are ordinary prose (`buying`, `billions`, `volcanoes`, `shitcoiners`, `heart`), not exact target phrases.
  - Fingerprint: `pdfs=3|exactPhraseRows=0|allFourExactPdfs=0|componentExactRows=4|componentStemRows=6|approxBoxWordRows=8|approxBoxExactRows=0|strictTerms=-|overdosePdfs=2|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `127` focused local checks.
- Conclusion:
  - Do not reopen PDF OCR active-box text or OVERDOSE header text as an extraction source.
  - Treat PDF OCR as context only; future progress still requires a new source/original-layout clue satisfying R1/R3.

### Current PDF OCR Affine Alignment Gate

- Status: checked; OCR-layer coordinate repair does not unlock the active targets.
- Evidence:
  - `scripts/audit_current_pdf_ocr_affine_alignment_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ocr_affine_alignment_gate/current_pdf_ocr_affine_alignment_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ocr_affine_alignment_gate/current_pdf_ocr_affine_alignment_gate.json`
  - `analysis_outputs/source_audit/current_pdf_ocr_affine_alignment_gate/current_pdf_ocr_affine_alignment_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Fit page-76 PDF OCR word coordinates to the high-resolution 3D word map.
  - Tested aligned OCR words against O4/B4/G5/O5 for target components and strict unit/order words.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Fits available: `2`; `magazine.pdf` had too few usable OCR token pairs.
  - Token pairs / inliers: `268` / `268`.
  - Target word-hit rows after alignment: `6`.
  - Target exact-component rows after alignment: `0`.
  - Target strict-instruction rows after alignment: `0`.
  - Strict instruction terms after alignment: `-`.
  - Minimum component distance to its own target box: `42.205` px.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Aligned low-res target-box words were OCR noise or unrelated text: O4 `ByiiREeraipy"`, B4 `eis`, G5 blank, O5 `siukbeodmensertslveaarty`.
  - Fingerprint: `pdfs=3|fits=2|pairs=268|inliers=268|targetWordRows=6|targetComponentRows=0|targetStrictRows=0|strictAfter=-|minCompDist=42.205|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `128` focused local checks.
- Conclusion:
  - Do not reopen PDF OCR alignment as a selector.
  - The low-res OCR layer can be geometrically fit to the page map, but the corrected coordinates still do not put exact active target components or unit/order wording into O4/B4/G5/O5.
  - Future progress still depends on new physical/original-layout/source evidence or a raw clue that passes the reopen gate.

### Current PDF Render Alignment Delta Gate

- Status: checked; low-resolution duplicate PDF visible rasters do not unlock extraction.
- Evidence:
  - `scripts/audit_current_pdf_render_alignment_delta_gate.py`
  - `analysis_outputs/source_audit/current_pdf_render_alignment_delta_gate/current_pdf_render_alignment_delta_gate.md`
  - `analysis_outputs/source_audit/current_pdf_render_alignment_delta_gate/current_pdf_render_alignment_delta_gate.json`
  - `analysis_outputs/source_audit/current_pdf_render_alignment_delta_gate/current_pdf_render_alignment_delta_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared visible page-76 PDF rasters after OCR-derived alignment against the high-resolution page-76 baseline.
  - Checked O4/B4/G5/O5, orange highlights, and the OVERDOSE header for material render deltas, color-state mismatches, and source-backed reopen triggers.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Duplicate image SHA groups: `1`.
  - Non-baseline PDFs: `2`.
  - Active target material residuals: `6`.
  - Active target state mismatches: `0`.
  - Material residual regions: `12`.
  - State mismatch / expected-state mismatch regions: `0` / `2`.
  - Max mean abs diff / max large residual ratio: `97.405` / `0.4594`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Active target states are preserved in the two low-resolution duplicate PDFs after alignment: O4 `Y->Y`, B4 `K->K`, G5 `K->K`, O5 `Y->Y`.
  - Fingerprint: `pdfs=3|dupeGroups=1|nonBase=2|activeMaterial=6|activeStateMismatch=0|materialRegions=12|stateMismatch=0|expectedMismatch=2|maxMean=97.405|maxLarge=0.4594|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `129` focused local checks.
- Conclusion:
  - Do not reopen the low-resolution PDF render layer as an extraction source.
  - The residuals are render/downsample differences around text and highlight edges, not new source-side exact target authority, geometry authority, or unit/order permission.
  - Keep the high-resolution page-76 scan as visual authority unless new physical/original-layout/source evidence arrives.

### Current PDF Embedded Channel / Mask Gate

- Status: checked; PDF channels, masks, and separations do not unlock extraction.
- Evidence:
  - `scripts/audit_current_pdf_embedded_channel_mask_gate.py`
  - `analysis_outputs/source_audit/current_pdf_embedded_channel_mask_gate/current_pdf_embedded_channel_mask_gate.md`
  - `analysis_outputs/source_audit/current_pdf_embedded_channel_mask_gate/current_pdf_embedded_channel_mask_gate.json`
  - `analysis_outputs/source_audit/current_pdf_embedded_channel_mask_gate/current_pdf_embedded_channel_mask_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected page-76 embedded PDF image objects for alpha/soft masks, hard masks, non-RGB separations, ICC/CMYK channels, and RGB channel-only anomalies.
  - Checked O4/B4/G5/O5, orange highlights, and the OVERDOSE header after applying readable/upright orientation.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Page-76 image objects: `3`.
  - 8-bit DeviceRGB DCT images: `3`.
  - Duplicate image SHA groups: `1`.
  - Hidden channel candidate images: `0`.
  - SMask/Mask images: `0`.
  - Alpha pixmap images: `0`.
  - Non-RGB / ICC-CMYK-Separation images: `0` / `0`.
  - Active channel rows / state mismatches / unexpected channel states: `12` / `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - `magazine.pdf` requires `rotate180_for_readable`; the two low-resolution duplicate PDFs are readable as extracted.
  - Fingerprint: `pdfs=3|p76Images=3|rgbDct=3|dupeGroups=1|hidden=0|mask=0|alpha=0|nonRgb=0|iccSep=0|activeRows=12|activeMismatch=0|activeUnexpected=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `130` focused local checks.
- Conclusion:
  - Do not reopen PDF embedded channels, alpha, masks, or color separations as an extraction source.
  - Channel splits explain visible orange/black ink only; they add no hidden source-side exact target authority, geometry authority, or unit/order permission.
  - Keep the high-resolution page-76 scan as visual authority unless a new source exposes non-RGB separations, masks, or a distinct original-layout asset.

### Current PDF Text Overlay Render-Mode Gate

- Status: checked; PDF OCR/text overlays are invisible derivative OCR, not original-layout evidence.
- Evidence:
  - `scripts/audit_current_pdf_text_overlay_render_mode_gate.py`
  - `analysis_outputs/source_audit/current_pdf_text_overlay_render_mode_gate/current_pdf_text_overlay_render_mode_gate.md`
  - `analysis_outputs/source_audit/current_pdf_text_overlay_render_mode_gate/current_pdf_text_overlay_render_mode_gate.json`
  - `analysis_outputs/source_audit/current_pdf_text_overlay_render_mode_gate/current_pdf_text_overlay_render_mode_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected page-76 PDF OCR/text overlays for texttrace render type, visible text painting, fonts, OVERDOSE text, and active-target aligned source instructions.
  - Checked O4/B4/G5/O5 after OCR-derived alignment for exact target components and strict unit/order terms.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Texttrace spans: `755`.
  - Invisible type-3 spans / visible painted spans: `755` / `0`.
  - PDFs with all text invisible: `3`.
  - GlyphLessFont / Helvetica-only PDFs: `2` / `1`.
  - Fit-available PDFs: `2`.
  - OVERDOSE text-trace PDFs: `2`.
  - Active aligned trace rows / component hits / strict instruction hits: `6` / `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Low-resolution duplicate active-box overlay text remains OCR noise: O4 `ByiiREeraipy"`, B4 `eis`, G5 blank, O5 `siukbeodmensertslveaarty`.
  - Fingerprint: `pdfs=3|traceSpans=755|type3=755|visible=0|allInvisiblePdfs=3|glyphLess=2|helvetica=1|fits=2|overdosePdfs=2|activeTrace=6|activeComponents=0|activeStrict=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `131` focused local checks.
- Conclusion:
  - Do not reopen the PDF text overlay as an extraction source.
  - The overlay is invisible OCR context, not visible original-layout typography or source-side selector permission.
  - Future progress still depends on new physical/original-layout/source evidence or raw clue wording that passes the reopen gate.

### Current Scan Valid-Leaf Bleed-Through Control Grid

- Status: checked; physically valid page 75 -> page 76 held-to-light bleed-through does not unlock an active selector.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_bleedthrough_control_grid.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/current_scan_valid_leaf_bleedthrough_control_grid.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/current_scan_valid_leaf_bleedthrough_control_grid.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/current_scan_valid_leaf_bleedthrough_control_grid_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mirrored page 75 onto page 76 using the current scan/PDF source images.
  - Measured source-only bleed signal inside O4/B4/G5/O5, then ranked each active box against same-size lower-page controls.
  - Included natural alignment and a bounded small-jitter search only; no OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Modes / target rows: `2` / `8`.
  - Natural source-only mean/min coverage: `0.0032` / `0.0000`.
  - Natural targets >=10% / >=25% source-only coverage: `0` / `0`.
  - Natural targets at >=75th percentile vs controls: `0`.
  - Small-jitter best shift: `-80,-20`.
  - Small-jitter source-only mean/min coverage: `0.0128` / `0.0000`.
  - Small-jitter targets >=10% / >=25% source-only coverage: `0` / `0`.
  - Small-jitter targets at >=75th percentile vs controls: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `modes=2|targets=8|natMean=0.0032|natMin=0.0000|nat10=0|nat25=0|natPctl75=0|jit=-80,-20|jitMean=0.0128|jitMin=0.0000|jit10=0|jit25=0|jitPctl75=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `132` focused local checks.
- Conclusion:
  - Do not extract from the current valid same-leaf light-table view.
  - Natural page 75 -> page 76 bleed-through gives effectively no source-only active-box signal, and small-jitter alignment does not beat same-size controls.
  - Reopen light-table extraction only if a new physical/original-layout source or raw clue names the transform, unit, and order.

### Current Scan Valid-Leaf Edge-Contact Control

- Status: checked; valid same-leaf edge contacts do not unlock an active selector.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_edge_contact_control.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/current_scan_valid_leaf_edge_contact_control.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/current_scan_valid_leaf_edge_contact_control.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/current_scan_valid_leaf_edge_contact_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mirrored page 75 onto page 76 and measured source-only signal in edge collars around O4/B4/G5/O5.
  - Compared active edge rings against same-size lower-page control rings under natural alignment and the prior bounded small-jitter shift `-80,-20`.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Modes / target rows: `2` / `8`.
  - Natural edge-ring source-only mean/min coverage: `0.0418` / `0.0000`.
  - Natural targets >=10% / >=25% ring source-only coverage: `1` / `0`.
  - Natural targets at >=75th percentile vs controls: `0`.
  - Small-jitter edge-ring source-only mean/min coverage: `0.0252` / `0.0000`.
  - Small-jitter targets >=10% / >=25% ring source-only coverage: `0` / `0`.
  - Small-jitter targets at >=75th percentile vs controls: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `modes=2|targets=8|natMean=0.0418|natMin=0.0000|nat10=1|nat25=0|natPctl75=0|jit=-80,-20|jitMean=0.0252|jitMin=0.0000|jit10=0|jit25=0|jitPctl75=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `133` focused local checks.
- Conclusion:
  - Do not extract from valid same-leaf edge contacts.
  - Edge contacts are sparse, fail all-four coverage, and do not separate from same-size lower-page controls.
  - Current light-table edge panels are visual review material only unless a new source/clue names the transform, unit, and order.

### Current Scan Valid-Leaf Edge Source Trace

- Status: checked; valid same-leaf edge contacts trace to ordinary page-75 text, not source-side instruction.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_edge_source_trace.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/current_scan_valid_leaf_edge_source_trace.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/current_scan_valid_leaf_edge_source_trace.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/current_scan_valid_leaf_edge_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mapped valid page 75 -> page 76 edge-contact pixels back onto page-75 source coordinates.
  - Checked the traced source regions for strict instruction, context, unit, and order wording.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Trace rows / rows with components: `8` / `6`.
  - Rows with source words / strict instruction rows / context rows: `6` / `0` / `0`.
  - Source word hits / strict instruction hits / context hits: `42` / `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - The strongest natural O4 contact traces to ordinary page-75 prose around `riding Bitcoins coattails`, `Buterin came up with`, and `slinging proof of stake`.
  - Natural O5 and small-jitter O5 trace to `listening for the gullible and unloved`; G5 traces to ordinary `experience`/`Satoshi experience` text; B4 has no source-side words.
  - Fingerprint: `rows=8|components=6|wordRows=6|strictRows=0|contextRows=0|words=42|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `134` focused local checks.
- Conclusion:
  - Do not extract from valid-leaf edge source traces.
  - The current held-to-light edge contacts do not expose an instruction source, source-backed selector, or unit/order clue.
  - Future work should pivot back to source/provenance validation or raw clue intake rather than more current-scan light-table variants.

### Current PDF Page-Box Pair Geometry Gate

- Status: checked; current PDFs do not alter the valid page 75 -> page 76 held-to-light geometry.
- Evidence:
  - `scripts/audit_current_pdf_page_box_pair_geometry_gate.py`
  - `analysis_outputs/source_audit/current_pdf_page_box_pair_geometry_gate/current_pdf_page_box_pair_geometry_gate.md`
  - `analysis_outputs/source_audit/current_pdf_page_box_pair_geometry_gate/current_pdf_page_box_pair_geometry_gate.json`
  - `analysis_outputs/source_audit/current_pdf_page_box_pair_geometry_gate/current_pdf_page_box_pair_geometry_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked article pages 75 and 76 in all current PDFs for page boxes, crop/media boxes, rotation, image rects, scale, margins, and hidden pair-layer indicators.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / page pairs: `3` / `3`.
  - Identical pair geometry: `3/3`.
  - Same page boxes / rotations / image rects / scale: `3` / `3` / `3` / `3`.
  - Side-margin pairs / placement-offset pairs / hidden pair-layer candidates: `2` / `0` / `0`.
  - `magazine.pdf` is full-bleed on pages 75 and 76.
  - The two lower-resolution duplicate PDFs have side margins, but the page-75 and page-76 margins and image scales are identical.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|pairs=3|pairGeometryPass=3|sameBoxes=3|sameRot=3|sameImageRect=3|sameScale=3|sideMargins=2|placementOffsets=0|hiddenPairLayers=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `135` focused local checks.
- Conclusion:
  - Do not adjust or reopen the valid 75 -> 76 light-table model based on current PDF page boxes.
  - The PDFs contain no asymmetric page placement or hidden pair layer that supplies a new transform or selector.
  - Further progress needs a distinct physical/original-layout source or raw clue that names transform, unit, and order.

### Current Scan Valid-Leaf Interior Source Trace

- Status: checked; valid same-leaf interior bleed traces to ordinary page-75 text, not source-side instruction.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_interior_source_trace.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/current_scan_valid_leaf_interior_source_trace.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/current_scan_valid_leaf_interior_source_trace.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/current_scan_valid_leaf_interior_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mapped valid page 75 -> page 76 source-only interior pixels inside O4/B4/G5/O5 back onto page-75 source coordinates.
  - Checked the traced source regions for strict instruction, context, unit, and order wording.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Trace rows / rows with components: `8` / `3`.
  - Total components / component pixels: `14` / `727`.
  - Rows with source words / strict instruction rows / context rows: `3` / `0` / `0`.
  - Source word hits / strict instruction hits / context hits: `4` / `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Natural O5 traces only to `gullible`.
  - Small-jitter G5 traces to `experience.` and small-jitter O5 traces to `gullible and`.
  - O4 and B4 have no component-level source-side word hits in either mode.
  - Fingerprint: `rows=8|componentRows=3|totalComponents=14|componentPixels=727|wordRows=3|strictRows=0|contextRows=0|words=4|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `136` focused local checks.
- Conclusion:
  - Do not extract from valid-leaf interior bleed traces.
  - The current held-to-light interior components do not expose an instruction source, source-backed selector, or unit/order clue.
  - Future work should pivot back to source/provenance validation or raw clue intake rather than more current-scan light-table variants.

### Current Scan Valid-Leaf Glyph-Slot Source Trace

- Status: checked; actual OVERDOSE glyph slots do not make valid same-leaf bleed source-backed or instructional.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_glyph_slot_source_trace.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/current_scan_valid_leaf_glyph_slot_source_trace.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/current_scan_valid_leaf_glyph_slot_source_trace.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/current_scan_valid_leaf_glyph_slot_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Subdivided O4/B4/G5/O5 by actual page-76 OVERDOSE glyph slots under valid page 75 -> page 76 held-to-light alignment.
  - Mapped slot-level source-only components back onto page-75 source words.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Target rows / slot rows: `8` / `20`.
  - Component rows / word rows: `4` / `4`.
  - Total components / component pixels: `19` / `830`.
  - Source word hits / strict instruction hits / context hits: `5` / `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Natural dominant pixel/component streams: `S.RD` / `...D`.
  - Small-jitter dominant pixel/component streams: `S.RR` / `..RR`.
  - Source words are sparse ordinary page-75 prose: `gullible`, `experience.`, and `gullible and`.
  - Fingerprint: `modes=2|targets=8|slots=20|componentRows=4|wordRows=4|strictRows=0|contextRows=0|components=19|componentPixels=830|words=5|strict=0|context=0|streams=S.RD/...D;S.RR/..RR|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `137` focused local checks.
- Conclusion:
  - Do not extract from valid-leaf OVERDOSE glyph-slot traces.
  - The glyph-slot subdivision does not expose an instruction source, source-backed selector, or unit/order clue.
  - Future work should pivot back to source/provenance validation or raw clue intake rather than more current-scan light-table variants.

### Current Scan Valid-Leaf Channel Source Trace

- Status: checked; color/channel splitting does not make valid same-leaf bleed source-backed or instructional.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_channel_source_trace.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/current_scan_valid_leaf_channel_source_trace.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/current_scan_valid_leaf_channel_source_trace.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/current_scan_valid_leaf_channel_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Split valid page 75 -> page 76 source-only pixels inside O4/B4/G5/O5 into orange, dark, and grey masks.
  - Mapped each channel back onto page-75 source words.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Target rows / channel rows: `8` / `24`.
  - Component rows / orange component rows / word rows: `5` / `0` / `5`.
  - Total components / component pixels / source-only pixels: `35` / `1494` / `2481`.
  - Source word hits / strict instruction hits / context hits: `6` / `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - No orange source-only components appear in the valid leaf.
  - Dark/grey source words are sparse ordinary page-75 prose: `gullible`, `experience.`, and `gullible and`.
  - Fingerprint: `modes=2|targets=8|channels=24|componentRows=5|orangeComponentRows=0|wordRows=5|strictRows=0|contextRows=0|components=35|componentPixels=1494|sourcePixels=2481|words=6|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `138` focused local checks.
- Conclusion:
  - Do not extract from valid-leaf color/channel traces.
  - Channel separation does not expose an instruction source, source-backed selector, or unit/order clue.
  - Future work should pivot back to source/provenance validation or raw clue intake rather than more current-scan light-table variants.

### Current Scan Valid-Leaf Word-Collision Trace

- Status: checked; projected page-75 OCR words do not make valid same-leaf light-table collisions instructional.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_word_collision_trace.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/current_scan_valid_leaf_word_collision_trace.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/current_scan_valid_leaf_word_collision_trace.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/current_scan_valid_leaf_word_collision_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mirrored/projected page-75 OCR word boxes into page-76 coordinates under the valid page 75 -> page 76 held-to-light model.
  - Checked O4/B4/G5/O5 for source/target word-box collisions, strict instruction terms, context terms, and reopen-trigger evidence.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Rows / source-word rows / collision rows: `8` / `6` / `5`.
  - Source words / target words / collision pairs: `32` / `18` / `27`.
  - Strict instruction rows / context rows: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Source words are ordinary page-75 prose: `by riding Bitcoins coattails Buterin came up with the`, `Vitalik Buterin came up with`, `experience.`, `experience. blindly with your bare`, and `listening for the gullible and unloved.`
  - B4 has no page-75 source words in either valid-leaf mode.
  - Fingerprint: `modes=2|targets=8|sourceRows=6|collisionRows=5|sourceWords=32|targetWords=18|pairs=27|strictRows=0|contextRows=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `139` focused local checks.
- Conclusion:
  - Do not extract from valid-leaf OCR word collisions.
  - Word-level held-to-light overlap does not expose an instruction source, source-backed selector, or unit/order clue.
  - Future work should pivot back to source/provenance validation or raw clue intake rather than more current-scan light-table variants.

### Current Scan Valid-Leaf Line-Band Trace

- Status: checked; projected page-75 OCR line bands do not make valid same-leaf light-table alignment instructional.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_line_band_trace.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/current_scan_valid_leaf_line_band_trace.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/current_scan_valid_leaf_line_band_trace.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/current_scan_valid_leaf_line_band_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mirrored/projected page-75 OCR line bands into page-76 coordinates under the valid page 75 -> page 76 held-to-light model.
  - Checked O4/B4/G5/O5 for source/target line-band overlaps, strict instruction terms, context terms, and reopen-trigger evidence.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Rows / source-line rows / line-overlap rows: `8` / `6` / `6`.
  - Source lines / target lines / source-target overlaps: `14` / `20` / `13`.
  - Strict instruction rows / context rows: `1` / `5`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - The only strict-token hit is ordinary prose: `Nice, pleasant words from con men and shitcoiners`; it does not name an extraction rule.
  - Context hits are ordinary article terms: `Bitcoins`, `Bitcoin`, `Satoshi`, and `shitcoiners`.
  - B4 has no page-75 source-line band in either valid-leaf mode.
  - Fingerprint: `modes=2|targets=8|sourceRows=6|overlapRows=6|sourceLines=14|targetLines=20|overlaps=13|strictRows=1|contextRows=5|strict=1|context=6|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `140` focused local checks.
- Conclusion:
  - Do not extract from valid-leaf projected source line bands.
  - Line-level held-to-light overlap does not expose an instruction source, source-backed selector, or unit/order clue.
  - Future work should pivot back to source/provenance validation or raw clue intake rather than more current-scan light-table variants.

### Current PDF Leaf-Image Identity Gate

- Status: checked; current PDFs and root scan images do not contain a distinct original-layout or higher-resolution page-75/page-76 source raster.
- Evidence:
  - `scripts/audit_current_pdf_leaf_image_identity_gate.py`
  - `analysis_outputs/source_audit/current_pdf_leaf_image_identity_gate/current_pdf_leaf_image_identity_gate.md`
  - `analysis_outputs/source_audit/current_pdf_leaf_image_identity_gate/current_pdf_leaf_image_identity_gate.json`
  - `analysis_outputs/source_audit/current_pdf_leaf_image_identity_gate/current_pdf_leaf_image_identity_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared embedded PDF primary images and root scan page rasters for article pages 75/76 against the canonical current scan pages.
  - Checked for higher-resolution/original-layout rasters, soft masks, multi-image pages, and page-pair identity splits that would alter held-to-light source provenance.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Image records / leaf-pair rows: `12` / `6`.
  - Exact current-scan records / pairs: `2` / `1`.
  - Derivative-like records / pairs: `12` / `6`.
  - Higher-resolution records / pairs: `0` / `0`.
  - Distinct improved/original-layout candidates: `0`.
  - PDF soft-mask / multi-image page candidates: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - `magazine.pdf` and `magazine-*_1.jpg` preserve the current 2544x3264 scan; `keyser bitcoin .pdf`, the Google Drive article PDF, and `keyser bitcoin -*_1.jpg` are lower-resolution derivatives.
  - Fingerprint: `records=12|pairs=6|exactRecords=2|derivativeRecords=12|exactPairs=1|derivativePairs=6|higherRecords=0|higherPairs=0|distinctImproved=0|softMasks=0|multiImagePages=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `141` focused local checks.
- Conclusion:
  - Do not reopen extraction from current PDFs/root scan images as a distinct source.
  - Continue using `analysis_outputs/source_images/magazine_page_75.jpg` and `analysis_outputs/source_images/magazine_page_76.jpg` as the current-scan held-to-light source.
  - Future progress requires a truly new physical/original-layout source or raw clue that passes R1-R5 plus source-backed R3.

### Current PDF Render Leaf Simulation Gate

- Status: checked; PDF rendering does not create a valid all-four page 75 -> page 76 held-to-light selector.
- Evidence:
  - `scripts/audit_current_pdf_render_leaf_simulation_gate.py`
  - `analysis_outputs/source_audit/current_pdf_render_leaf_simulation_gate/current_pdf_render_leaf_simulation_gate.md`
  - `analysis_outputs/source_audit/current_pdf_render_leaf_simulation_gate/current_pdf_render_leaf_simulation_gate.json`
  - `analysis_outputs/source_audit/current_pdf_render_leaf_simulation_gate/current_pdf_render_leaf_simulation_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Re-measured physically valid page 75 -> page 76 held-to-light coverage using canonical scan images, PDF-rendered pages, and embedded PDF rasters.
  - Compared rendered pages against embedded rasters inside O4/B4/G5/O5 to check for visible original-layout additions.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Pair rows / target rows: `7` / `28`.
  - Render-vs-embedded PDF rows: `3`.
  - Max mean source-only coverage: `0.2119`.
  - Max targets >=10% / >=25% source-only: `2` / `2`.
  - All-four >=10% / >=25% pair counts: `0` / `0`.
  - Max render-vs-embedded page MAD / active-box MAD: `37.2097` / `26.9905`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Full-resolution `magazine.pdf` render/embedded behavior matches the canonical scan near `0.0033` mean source-only coverage.
  - Low-resolution derivative PDFs inflate only O4/B4 after resize/margins; G5/O5 still fail the threshold and no all-four selector appears.
  - Fingerprint: `pairs=7|targets=28|renderRows=3|maxMean=0.2119|max10=2|max25=2|all10=0|all25=0|maxRenderMAD=37.2097|maxActiveRenderMAD=26.9905|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `142` focused local checks.
- Conclusion:
  - Do not reopen PDF renderer toggles or low-resolution derivative held-to-light variants as extraction paths.
  - Future progress still requires a new physical/original-layout source or raw clue that passes R1-R5 plus source-backed R3.

### Current PDF Low-Res Render Source Trace

- Status: checked; the derivative-PDF O4/B4/G5 held-to-light inflation is provenance-explained and not instructional.
- Evidence:
  - `scripts/audit_current_pdf_lowres_render_source_trace.py`
  - `analysis_outputs/source_audit/current_pdf_lowres_render_source_trace/current_pdf_lowres_render_source_trace.md`
  - `analysis_outputs/source_audit/current_pdf_lowres_render_source_trace/current_pdf_lowres_render_source_trace.json`
  - `analysis_outputs/source_audit/current_pdf_lowres_render_source_trace/current_pdf_lowres_render_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mapped low-resolution derivative PDF source-only pixels from valid page 75 -> page 76 held-to-light back into page-75 OCR boxes.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Pair rows / trace rows / unique trace shapes: `4` / `12` / `6`.
  - Skipped below threshold: `4`; every skipped row is O5 at `0.0003`.
  - Source word rows / word hits: `8` / `36`.
  - Strict instruction rows / token hits: `0` / `0`.
  - Context rows / token hits: `4` / `4`.
  - All-four eligible trace-pair count: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - O4 traces to ordinary page-75 prose around `in by riding Bitcoins Buterin came up with`.
  - B4 traces to blank/grey margin material with no OCR words.
  - G5 traces only to the ordinary word `experience.`.
  - Google Drive PDF rows duplicate `keyser bitcoin .pdf` trace shapes.
  - Fingerprint: `pdfs=2|pairs=4|traceRows=12|unique=6|skipped=4|wordRows=8|words=36|strictRows=0|strict=0|contextRows=4|context=4|allFour=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `143` focused local checks.
- Conclusion:
  - Do not reopen derivative-PDF renderer/embedded light-table variants.
  - Best next direction is still new physical/original-layout source validation or raw clue wording that explicitly gives unit/order/transform for O4/B4/G5/O5.

### Current PDF OCR Reverse-Leaf Source Trace

- Status: checked; hidden PDF OCR/text layers do not add an instruction source under the valid page 75 -> page 76 mirror.
- Evidence:
  - `scripts/audit_current_pdf_ocr_reverse_leaf_source_trace.py`
  - `analysis_outputs/source_audit/current_pdf_ocr_reverse_leaf_source_trace/current_pdf_ocr_reverse_leaf_source_trace.md`
  - `analysis_outputs/source_audit/current_pdf_ocr_reverse_leaf_source_trace/current_pdf_ocr_reverse_leaf_source_trace.json`
  - `analysis_outputs/source_audit/current_pdf_ocr_reverse_leaf_source_trace/current_pdf_ocr_reverse_leaf_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Aligned page-75 PDF OCR layers to the page-75 OCR map and checked mirrored O4/B4/G5/O5 source boxes for instruction terms.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDF rows / usable OCR-fit rows: `3` / `2`.
  - Token pairs / inliers: `232` / `232`.
  - Target rows / PDF word rows / exact-box word rows: `12` / `6` / `6`.
  - Strict instruction rows / context rows: `0` / `2`.
  - All-four exact-box PDF trace pairs: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Low-resolution duplicate PDFs repeat ordinary page-75 prose: O4 `by riding Bitcoins Buterin came up with the`, G5 `experience.`, O5 `for the gullible and unloved.`.
  - B4 has no aligned PDF OCR words in the mirrored source box.
  - `magazine.pdf` OCR is rotated/garbled and does not produce a stable reverse-leaf source trace.
  - Fingerprint: `pdfs=3|fits=2|pairs=232|inliers=232|targets=12|pdfWordRows=6|exactRows=6|strictRows=0|contextRows=2|allFourExact=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `144` focused local checks.
- Conclusion:
  - Do not reopen hidden PDF OCR reverse-leaf tracing.
  - Best next direction remains new physical/original-layout source validation or raw clue wording that explicitly gives active unit/order/transform.

### Current Scan OVERDOSE Slot-Shape Phase Control

- Status: checked; active OVERDOSE slot-shape phase is a location guardrail, not an extraction instruction.
- Evidence:
  - `scripts/audit_current_scan_overdose_slot_shape_phase_control.py`
  - `analysis_outputs/source_audit/current_scan_overdose_slot_shape_phase_control/current_scan_overdose_slot_shape_phase_control.md`
  - `analysis_outputs/source_audit/current_scan_overdose_slot_shape_phase_control/current_scan_overdose_slot_shape_phase_control.json`
  - `analysis_outputs/source_audit/current_scan_overdose_slot_shape_phase_control/current_scan_overdose_slot_shape_phase_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Preserved active O4/B4/G5/O5 x positions, box sizes, OVERDOSE slot stream, and 3/2/5 line-gap shape, then shifted the same shape through lower-page line phases.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Lower line groups / scenario rows: `13` / `3`.
  - Active phases / shifted control phases: `1` / `2`.
  - Target rows / OCR word hits: `12` / `30`.
  - Strict instruction scenario rows / token hits: `0` / `0`.
  - Context scenario rows / token hits: `2` / `3`.
  - Active-phase strict/context token hits: `0` / `0`.
  - Control-phase strict/context token hits: `0` / `3`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Shifted same-shape controls hit ordinary context words, including `bitcoin` and `IMF`.
  - The active phase overlaps all four manual boxes but produces corrupted/non-instructional OCR snippets, with G5 blank.
  - Fingerprint: `lines=13|scenarios=3|active=1|controls=2|targets=12|words=30|strictRows=0|strict=0|contextRows=2|context=3|activeStrict=0|activeContext=0|controlStrict=0|controlContext=3|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `145` focused local checks.
- Conclusion:
  - Do not promote the active OVERDOSE slot-shape phase as an extraction path.
  - Keep it as source-comparison geometry only; best next direction remains a distinct physical/original-layout source or raw clue wording that explicitly names unit/order/transform.

### Current Scan OVERDOSE X-Slot Phase Control

- Status: checked; horizontal OVERDOSE phase is not selective enough to become an extraction selector.
- Evidence:
  - `scripts/audit_current_scan_overdose_xslot_phase_control.py`
  - `analysis_outputs/source_audit/current_scan_overdose_xslot_phase_control/current_scan_overdose_xslot_phase_control.md`
  - `analysis_outputs/source_audit/current_scan_overdose_xslot_phase_control/current_scan_overdose_xslot_phase_control.json`
  - `analysis_outputs/source_audit/current_scan_overdose_xslot_phase_control/current_scan_overdose_xslot_phase_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Preserved active O4/B4/G5/O5 vertical positions, box sizes, and within-slot offsets, then shifted OVERDOSE center-slot indexes through all eight horizontal phases.
  - Checked OCR words plus visual/annotated highlight overlaps.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Scenario rows / active-overlap phases / control phases: `8` / `3` / `5`.
  - Target rows / OCR word hits: `32` / `53`.
  - Strict instruction scenario rows / token hits: `0` / `0`.
  - Context scenario rows / token hits: `4` / `6`.
  - Active-overlap phase strict/context token hits: `0` / `1`.
  - Control-phase strict/context token hits: `0` / `5`.
  - Active/control visual-orange hits: `6` / `2`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Three phases still overlap all four active boxes: `OVED`, `SERO`, and `DOVR`, showing horizontal slot phase is not unique.
  - Shifted controls hit ordinary context including `bitcoin`, `IMF`, and `sell`, but no strict instruction terms.
  - Fingerprint: `phases=8|active=3|controls=5|targets=32|words=53|strictRows=0|strict=0|contextRows=4|context=6|activeStrict=0|activeContext=1|controlStrict=0|controlContext=5|activeOrange=6|controlOrange=2|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `146` focused local checks.
- Conclusion:
  - Do not promote horizontal OVERDOSE x-slot phase as extraction.
  - Keep it as source-comparison geometry only; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Container Metadata Gate

- Status: checked; current PDFs do not contain hidden container/source carriers.
- Evidence:
  - `scripts/audit_current_pdf_container_metadata_gate.py`
  - `analysis_outputs/source_audit/current_pdf_container_metadata_gate/current_pdf_container_metadata_gate.md`
  - `analysis_outputs/source_audit/current_pdf_container_metadata_gate/current_pdf_container_metadata_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected document metadata, XMP, name trees, attachments, annotations, widgets, links, optional content groups/layers, JavaScript/actions, and special catalog/page keys.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / pages checked: `3` / `24`.
  - Signal metadata fields / XML metadata streams: `4` / `0`.
  - Name trees / non-empty name trees: `2` / `0`.
  - Attachments / annotations / widgets / links: `0` / `0` / `0` / `0`.
  - Optional-content groups / layers / layer UI configs: `0` / `0` / `0`.
  - Special action object rows: `0`.
  - Strict instruction hits / context hits: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - `magazine.pdf` has no signal metadata beyond PDF format; both duplicate derivative PDFs only expose `PDF24 Tools - OCR`, a timestamp, and an empty destination name tree.
  - Fingerprint: `pdfs=3|pages=24|metadata=4|xml=0|names=2|nonEmptyNames=0|emb=0|annots=0|widgets=0|links=0|ocg=0|layers=0|actions=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `147` focused local checks.
- Conclusion:
  - Do not reopen PDF container metadata as extraction.
  - Current PDFs remain raster/OCR witnesses only; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Page Thumbnail Gate

- Status: checked; embedded PDF thumbnails are not distinct source carriers.
- Evidence:
  - `scripts/audit_current_pdf_page_thumbnail_gate.py`
  - `analysis_outputs/source_audit/current_pdf_page_thumbnail_gate/current_pdf_page_thumbnail_gate.md`
  - `analysis_outputs/source_audit/current_pdf_page_thumbnail_gate/current_pdf_page_thumbnail_gate.json`
  - `analysis_outputs/source_audit/current_pdf_page_thumbnail_gate/current_pdf_page_thumbnail_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected embedded `/Thumb` streams in the current PDFs as auxiliary rasters, especially page 76.
  - Checked whether thumbnails improve source quality, add a separate carrier, or contain instruction/context payload in object dictionaries.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / pages checked: `3` / `24`.
  - Thumbnail pages / page-76 thumbnails: `8` / `1`.
  - Unique thumbnail images / total thumbnail bytes: `8` / `87231`.
  - Thumbnail content-xref matches / higher-resolution page-76 thumbnails: `0` / `0`.
  - Distinct source carriers: `0`.
  - Strict instruction hits / context hits: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Only `magazine.pdf` has `/Thumb` streams, one `82x106` DCT preview per article page `73-80`.
  - The page-76 thumbnail is lower quality than the known `2544x3264` page raster and has no separate text, layer, annotation, or instruction payload.
  - Fingerprint: `pdfs=3|pages=24|thumbPages=8|p76Thumbs=1|uniqueThumbs=8|thumbBytes=87231|contentXrefMatches=0|higherP76=0|distinctCarrier=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `148` focused local checks.
- Conclusion:
  - Do not reopen PDF page thumbnails as extraction.
  - Treat thumbnails as provenance-only previews; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Content Stream Operator Gate

- Status: checked; PDF drawing commands are raster placement plus invisible OCR overlays only.
- Evidence:
  - `scripts/audit_current_pdf_content_stream_operator_gate.py`
  - `analysis_outputs/source_audit/current_pdf_content_stream_operator_gate/current_pdf_content_stream_operator_gate.md`
  - `analysis_outputs/source_audit/current_pdf_content_stream_operator_gate/current_pdf_content_stream_operator_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected page content streams and form XObject streams in the current PDFs, especially article page 76.
  - Separated raw PDF operator/resource evidence from invisible OCR text payload.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / pages checked: `3` / `24`.
  - Page content streams / form XObjects: `88` / `16`.
  - Image `Do` calls / form `Do` calls / unknown `Do` calls: `24` / `16` / `0`.
  - Text objects / text-show operators: `236` / `3854`.
  - Invisible text render-mode uses / visible text render-mode uses: `236` / `0`.
  - Vector paint / path / clip operators: `0` / `0` / `0`.
  - Operator strict/context hits: `0` / `0`.
  - OCR payload strict/context term rows: `8` / `14`; these are ordinary invisible OCR payload text rows, not operator/source instructions.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - `magazine.pdf` page 76 has one full-page image draw plus an invisible OCR text stream using render mode `3`.
  - The duplicate OCR PDFs page 76 have one page-image draw plus an `OL2` invisible OCR form overlay.
  - Fingerprint: `pdfs=3|pages=24|streams=88|forms=16|imageDo=24|formDo=16|unknownDo=0|textObj=236|invisTr=236|visTr=0|paint=0|path=0|clip=0|opStrict=0|opContext=0|payloadStrictRows=8|payloadContextRows=14|p76VisTr=0|p76Paint=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `149` focused local checks.
- Conclusion:
  - Do not reopen PDF content streams as original-layout/source evidence.
  - Best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Font CMap Resource Gate

- Status: checked; PDF font/CMap resources are OCR implementation details, not a distinct source carrier.
- Evidence:
  - `scripts/audit_current_pdf_font_cmap_resource_gate.py`
  - `analysis_outputs/source_audit/current_pdf_font_cmap_resource_gate/current_pdf_font_cmap_resource_gate.md`
  - `analysis_outputs/source_audit/current_pdf_font_cmap_resource_gate/current_pdf_font_cmap_resource_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected font objects, ToUnicode CMaps, CIDToGID maps, font descriptors, and embedded font files in the current PDFs, especially page 76.
  - Separated structural PDF `font` vocabulary from procedural instruction terms.
  - No OCR-to-key extraction, key candidates, hashes, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / pages checked: `3` / `24`.
  - Page font references / unique font objects: `24` / `24`.
  - Type0 GlyphLessFont objects / built-in Helvetica objects: `16` / `8`.
  - ToUnicode streams / identity CMaps: `16` / `16`.
  - CIDToGID maps / font files / unique font-file hashes: `16` / `16` / `1`.
  - Procedural resource strict/context hits: `0` / `0`.
  - Structural `font` term hits: `40`; these are normal PDF font object words, not puzzle instruction text.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - `magazine.pdf` uses built-in Helvetica only; the two OCR duplicates use repeated GlyphLessFont Type0 resources with identity CMaps and repeated small font binaries.
  - Fingerprint: `pdfs=3|pages=24|fontRefs=24|fonts=24|glyphless=16|helvetica=8|toUnicode=16|identityCMap=16|cidMaps=16|fontFiles=16|uniqueFontFiles=1|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `150` focused local checks.
- Conclusion:
  - Do not reopen PDF font/CMap resources as original-layout/source evidence.
  - Best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Embedded JPEG Marker Gate

- Status: checked; raw JPEG marker metadata is provenance-only and not a source-instruction carrier.
- Evidence:
  - `scripts/audit_current_pdf_embedded_jpeg_marker_gate.py`
  - `analysis_outputs/source_audit/current_pdf_embedded_jpeg_marker_gate/current_pdf_embedded_jpeg_marker_gate.md`
  - `analysis_outputs/source_audit/current_pdf_embedded_jpeg_marker_gate/current_pdf_embedded_jpeg_marker_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected raw JPEG marker wrappers in embedded page images and page thumbnails from the current PDFs, especially page 76.
  - Checked APP/COM marker payloads for EXIF, XMP, ICC, Photoshop, comments, and readable instruction/context text.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / JPEG records checked: `3` / `32`.
  - Page images / thumbnails / page-76 records: `24` / `8` / `4`.
  - JPEG records / parse warnings: `32` / `0`.
  - APP / COM marker segments: `40` / `0`.
  - Structural JFIF segments: `32`.
  - Non-structural APP/COM segments: `8`.
  - Provenance metadata segments: `8`.
  - Source-instruction carrier segments: `0`.
  - Strict/context marker hits: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Full embedded page images have no EXIF, XMP, ICC, Photoshop APP13, COM comments, or other non-structural APP marker carriers.
  - Only the eight tiny `magazine.pdf` thumbnails contain EXIF APP1 provenance blocks; page 76's thumbnail records `Exif Canon 2025:10:01 16:26:26 0221 0100`.
  - Fingerprint: `pdfs=3|records=32|pageImages=24|thumbs=8|p76Records=4|jpeg=32|warn=0|app=40|com=0|jfif=32|nonstruct=8|metadata=8|instrCarrier=0|strict=0|context=0|pageHashes=16|thumbHashes=8|markerSigs=3|sourceR3=0|triggers=0/9|selectors=0`.
  - Frontier now records `151` focused local checks.
- Conclusion:
  - Do not reopen embedded JPEG marker metadata as source/original-layout evidence.
  - Treat the thumbnail EXIF as provenance only; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Thumbnail EXIF Order Gate

- Status: checked; Canon thumbnail timestamps do not provide a page/fold/OVERDOSE selector.
- Evidence:
  - `scripts/audit_current_pdf_thumbnail_exif_order_gate.py`
  - `analysis_outputs/source_audit/current_pdf_thumbnail_exif_order_gate/current_pdf_thumbnail_exif_order_gate.md`
  - `analysis_outputs/source_audit/current_pdf_thumbnail_exif_order_gate/current_pdf_thumbnail_exif_order_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked whether the eight `magazine.pdf` thumbnail EXIF timestamps supply an ordering rule for page/fold/OVERDOSE mechanics.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Thumbnail EXIF rows: `8`.
  - Article/page/xref order: `73-74-75-76-77-78-79-80`.
  - Timestamp order: `73-75-74-78-79-76-77-80`.
  - Article-order monotonic: `False`; timestamp-rank inversions: `5`.
  - Candidate order matches / checks: `0` / `5`.
  - Page 76 timestamp / rank: `2025-10-01 16:26:26` / `6`.
  - Provenance metadata segments / instruction carriers: `8` / `0`.
  - Strict/context hits: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `rows=8|pages=73-80|timeOrder=73-75-74-78-79-76-77-80|articleMonotonic=0|inversions=5|metadata=8|instrCarrier=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote EXIF timestamp order as a selector.
  - Treat the Canon timestamps as scanner/PDF provenance only; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF JPEG Compression Provenance Gate

- Status: checked; JPEG compression structure is provenance-only and does not provide a page/fold/OVERDOSE selector.
- Evidence:
  - `scripts/audit_current_pdf_jpeg_compression_provenance_gate.py`
  - `analysis_outputs/source_audit/current_pdf_jpeg_compression_provenance_gate/current_pdf_jpeg_compression_provenance_gate.md`
  - `analysis_outputs/source_audit/current_pdf_jpeg_compression_provenance_gate/current_pdf_jpeg_compression_provenance_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected embedded page-image and thumbnail DCT compression structure in the current PDFs: DQT/DHT hashes, SOF sampling, compression groups, and byte-size order.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / image records: `3` / `32`.
  - Page images / thumbnails: `24` / `8`.
  - Compression groups: `3`.
  - Page-image / thumbnail compression groups: `2` / `1`.
  - Page 76 compression signatures / unique signatures: `3` / `0`.
  - Active unique compression signatures: `0`.
  - Magazine page-image byte-size order: `78-79-76-75-73-77-80-74`.
  - Magazine thumbnail byte-size order: `79-75-76-78-73-80-74-77`.
  - Candidate order matches / checks: `0` / `6`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|records=32|groups=3|pageImageGroups=2|thumbGroups=1|p76Sigs=3|p76Unique=0|activeUnique=0|byteOrder=78-79-76-75-73-77-80-74|thumbByteOrder=79-75-76-78-73-80-74-77|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote JPEG compression structure, quantization/Huffman tables, sampling, or byte-size order as a selector.
  - Treat DQT/DHT/SOF structure as image-encoding provenance only; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Image XObject Dictionary Gate

- Status: checked; image XObject dictionaries and xref numbering do not provide a source-backed selector.
- Evidence:
  - `scripts/audit_current_pdf_image_xobject_dictionary_gate.py`
  - `analysis_outputs/source_audit/current_pdf_image_xobject_dictionary_gate/current_pdf_image_xobject_dictionary_gate.md`
  - `analysis_outputs/source_audit/current_pdf_image_xobject_dictionary_gate/current_pdf_image_xobject_dictionary_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected image XObject dictionaries, thumbnail dictionaries, special image-object keys, and xref numbering in the current PDFs.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / image objects: `3` / `32`.
  - Page image / thumbnail objects: `24` / `8`.
  - Normalized dictionary groups: `3`.
  - Page 76 objects / unique dictionary groups: `4` / `0`.
  - Active unique dictionary groups: `0`.
  - Special image-key rows: `0`.
  - Strict/context dictionary hits: `0` / `0`.
  - Structural xref order matches: `4` / `4`.
  - Active-subset xref order matches: `4` / `4`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|objects=32|pageImages=24|thumbs=8|dictGroups=3|p76Objects=4|p76UniqueGroups=0|activeUniqueGroups=0|specialKeys=0|strict=0|context=0|structOrder=4/4|activeSubset=4/4|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote image XObject dictionaries or image xref order as a selector.
  - Xref numbering follows normal PDF page construction order; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Page Resource Order Gate

- Status: checked; page dictionaries, resource dictionaries, page rotation, thumbnail refs, XObject resource names, and page xref order do not provide a source-backed selector.
- Evidence:
  - `scripts/audit_current_pdf_page_resource_order_gate.py`
  - `analysis_outputs/source_audit/current_pdf_page_resource_order_gate/current_pdf_page_resource_order_gate.md`
  - `analysis_outputs/source_audit/current_pdf_page_resource_order_gate/current_pdf_page_resource_order_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected page dictionaries, resource dictionaries, XObject resource names, content/resource/thumb references, page rotation, and page xref order in the current PDFs.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / pages / page-76 rows: `3` / `24` / `3`.
  - Page/resource signature groups: `2` / `2`.
  - Page 76 unique page/resource groups: `0` / `0`.
  - Active unique page/resource groups: `0` / `0`.
  - Thumbnail-bearing pages: `8`.
  - Special page-key rows: `0`.
  - Strict/context wrapper hits: `0` / `0`.
  - Structural page-xref order matches: `3` / `3`.
  - Active-subset page-xref order matches: `3` / `3`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|pages=24|p76=3|pageGroups=2|resourceGroups=2|p76UniquePageGroups=0|p76UniqueResourceGroups=0|activeUniquePageGroups=0|activeUniqueResourceGroups=0|thumbPages=8|special=0|strict=0|context=0|pageOrder=3/3|activeSubset=3/3|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote page/resource dictionaries, resource names, page rotation, thumbnails, or page xref order as a selector.
  - `magazine.pdf` page wrappers and the duplicate-PDF OCR wrappers are ordinary PDF construction artifacts; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Content Transform Matrix Gate

- Status: checked; content-stream image/form placement matrices do not provide a source-backed selector.
- Evidence:
  - `scripts/audit_current_pdf_content_transform_matrix_gate.py`
  - `analysis_outputs/source_audit/current_pdf_content_transform_matrix_gate/current_pdf_content_transform_matrix_gate.md`
  - `analysis_outputs/source_audit/current_pdf_content_transform_matrix_gate/current_pdf_content_transform_matrix_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected numeric content-stream placement matrices around image and OCR-form `Do` calls in the current PDFs.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / pages / placements: `3` / `24` / `40`.
  - Image/form/unknown `Do` placements: `24` / `16` / `0`.
  - Placement signature groups / distinct cumulative matrices: `3` / `3`.
  - Page 76 placements / unique placement groups: `5` / `0`.
  - Active unique placement groups: `0`.
  - Strict/context wrapper hits: `0` / `0`.
  - Structural stream-order matches: `5` / `5`.
  - Active-subset stream-order matches: `5` / `5`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|pages=24|placements=40|imageDo=24|formDo=16|unknownDo=0|matrixGroups=3|distinctMatrices=3|p76Placements=5|p76UniqueGroups=0|activeUniqueGroups=0|strict=0|context=0|streamOrder=5/5|activeSubset=5/5|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote PDF content placement matrices or stream xref order as selectors.
  - The three placement matrix groups are ordinary raster/OCR placement artifacts; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Form XObject Dictionary Gate

- Status: checked; duplicate-PDF `OL2` Form XObject wrappers do not provide a source-backed selector.
- Evidence:
  - `scripts/audit_current_pdf_form_xobject_dictionary_gate.py`
  - `analysis_outputs/source_audit/current_pdf_form_xobject_dictionary_gate/current_pdf_form_xobject_dictionary_gate.md`
  - `analysis_outputs/source_audit/current_pdf_form_xobject_dictionary_gate/current_pdf_form_xobject_dictionary_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected duplicate-PDF Form XObject dictionaries, OCR form `BBox`/`Matrix`/resources, stream render mode, stream byte counts, and form xref order.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / form objects: `3` / `16`.
  - Normalized dictionary groups: `1`.
  - Page 76 forms / unique dictionary groups: `2` / `0`.
  - Active unique dictionary groups: `0`.
  - Special form-key rows: `0`.
  - Visible text render-mode rows: `0`.
  - Strict/context wrapper hits: `0` / `0`.
  - Structural form-xref order matches: `3` / `3`.
  - Active-subset form-xref order matches: `3` / `3`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|forms=16|dictGroups=1|p76Forms=2|p76UniqueGroups=0|activeUniqueGroups=0|special=0|visibleText=0|strict=0|context=0|xrefOrder=3/3|activeSubset=3/3|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote Form XObject dictionaries, `OL2` OCR wrappers, stream byte counts, or form xref order as selectors.
  - The forms are ordinary OCR containers with full-page BBox, identity Matrix, and invisible render-mode `3` text; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Trailer Xref Integrity Gate

- Status: checked; PDF file-storage/trailer/xref structure does not provide a source-backed selector.
- Evidence:
  - `scripts/audit_current_pdf_trailer_xref_integrity_gate.py`
  - `analysis_outputs/source_audit/current_pdf_trailer_xref_integrity_gate/current_pdf_trailer_xref_integrity_gate.md`
  - `analysis_outputs/source_audit/current_pdf_trailer_xref_integrity_gate/current_pdf_trailer_xref_integrity_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected PDF trailers, xref/incremental-update markers, object streams, document IDs, catalog carriers, and page object order.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / unique file hashes: `3` / `2`.
  - Xref object total: `301`.
  - `startxref` / EOF markers: `3` / `3`.
  - Incremental-update candidates: `0`.
  - Object streams / xref streams: `0` / `0`.
  - Encrypted PDFs / nonzero-generation objects: `0` / `0`.
  - Hidden trailer/storage carrier markers: `0`.
  - Trailer ID present count: `3`.
  - Strict/context storage hits: `0` / `0`.
  - Structural page-xref order matches: `3` / `3`.
  - Active-subset page-xref order matches: `3` / `3`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|uniqueSha=2|xrefObjects=301|startxref=3|eof=3|incremental=0|objStm=0|xrefStm=0|encrypted=0|nonzeroGen=0|hiddenTrailer=0|idPresent=3|strict=0|context=0|pageOrder=3/3|activeSubset=3/3|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote trailer IDs, xref chronology, page object order, file hashes, `startxref` offsets, duplicate-PDF `/Info` metadata, or file-storage structure as selectors.
  - The PDFs are simple non-incremental PDF 1.3 files at this layer, with no hidden storage carrier and no source-backed R3 unit/order/transform.
  - Frontier now records `158` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current Scan Held-To-Light Opacity Gate

- Status: checked; light-through opacity/color transfer does not provide a source-backed selector.
- Evidence:
  - `scripts/audit_current_scan_held_to_light_opacity_gate.py`
  - `analysis_outputs/source_audit/current_scan_held_to_light_opacity_gate/current_scan_held_to_light_opacity_gate.md`
  - `analysis_outputs/source_audit/current_scan_held_to_light_opacity_gate/current_scan_held_to_light_opacity_gate.json`
  - `analysis_outputs/source_audit/current_scan_held_to_light_opacity_gate/current_scan_held_to_light_opacity_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested page-76 light-through blends using current PDF/source images in readable/upright orientation.
  - Compared average, darken, and multiply blends at opacity levels `0.25`, `0.50`, and `0.75` for valid natural 75->76, valid forced 75->76, nonphysical 78->76, and nonphysical 79->76 scenarios.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Scenarios / blend rows / active-box rows: `4` / `36` / `144`.
  - Best physically valid natural 75->76 all-box darkening: `0.00` via `average@0.25`.
  - Best forced/control all-box darkening: `6.331677` via `nonphysical_79_to_76_forced_active` / `multiply@0.75`.
  - Natural all-four delta>=16 rows / forced-or-control all-four delta>=16 rows: `0` / `0`.
  - Expected Y/K state-stream matches: `20` / `36`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `scenarios=4|blendRows=36|boxRows=144|naturalBest=0.00:average@0.25|controlBest=6.33:nonphysical_79_to_76_forced_active:multiply@0.75|all16=0/0|stateMatches=20/36|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote held-to-light opacity, blend mode, alpha, visual darkening, or color-state persistence as selectors.
  - The physically valid natural 75->76 view does not produce an active-quartet opacity signal; the best row is a weak nonphysical forced-control blend and still below the all-four delta>=16 threshold.
  - Frontier now records `159` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Render Resolution Invariance Gate

- Status: checked; high-DPI PDF rendering does not expose a distinct original-layout or active-quartet selector.
- Evidence:
  - `scripts/audit_current_pdf_render_resolution_invariance_gate.py`
  - `analysis_outputs/source_audit/current_pdf_render_resolution_invariance_gate/current_pdf_render_resolution_invariance_gate.md`
  - `analysis_outputs/source_audit/current_pdf_render_resolution_invariance_gate/current_pdf_render_resolution_invariance_gate.json`
  - `analysis_outputs/source_audit/current_pdf_render_resolution_invariance_gate/current_pdf_render_resolution_invariance_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Rendered page 76 of the current PDFs at zoom levels `1`, `2`, and `4`.
  - Normalized each render to the readable/upright `2544x3264` frame, then compared low-vs-high render deltas in active target boxes, shifted controls, and projected C9/OVERDOSE slots.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / zooms / render rows: `3` / `3` / `9`.
  - Comparison rows: `6`.
  - Active region rows / OVERDOSE slot rows: `24` / `48`.
  - Active outliers above shifted-control p95: `4`.
  - All-four active outlier comparisons: `0`.
  - Max active/control/OVERDOSE-slot mean absolute delta: `33.652132` / `31.54227` / `17.370846`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|zooms=3|renders=9|comparisons=6|activeOutliers=4|allFourOutliers=0|maxActive=33.652|maxControl=31.542|maxSlot=17.371|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote PDF render DPI, anti-aliasing/resampling deltas, active-box high-DPI residuals, or projected OVERDOSE slot render deltas as selectors.
  - Individual B4/G5 residuals in `magazine.pdf` do not generalize to all four active targets; duplicate PDFs are controlled, and OVERDOSE slot deltas stay below active/control maxima.
  - Frontier now records `160` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current Scan JPEG Block Grid Gate

- Status: checked; current-scan JPEG `8x8` block phase/energy does not provide a selector.
- Evidence:
  - `scripts/audit_current_scan_jpeg_block_grid_gate.py`
  - `analysis_outputs/source_audit/current_scan_jpeg_block_grid_gate/current_scan_jpeg_block_grid_gate.md`
  - `analysis_outputs/source_audit/current_scan_jpeg_block_grid_gate/current_scan_jpeg_block_grid_gate.json`
  - `analysis_outputs/source_audit/current_scan_jpeg_block_grid_gate/current_scan_jpeg_block_grid_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared active O4/B4/G5/O5 boxes, 16 shifted controls, and 8 projected C9/OVERDOSE slots against JPEG block-grid edge phase and block-boundary energy.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`.
  - Active/control/OVERDOSE strict edge hits: `6` / `18` / `22`.
  - Active boundary-ratio outliers above shifted-control p95: `0`.
  - All-four active boundary-ratio outlier: `0`.
  - Max active/control/OVERDOSE-slot boundary ratio: `1.551` / `4.014` / `1.296`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|controls=16|slots=8|edgeHits=6/18/22|activeOutliers=0|allFourOutliers=0|ratioMax=1.551/4.014/1.296|controlP95=3.361|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote JPEG block phase, `8x8` grid alignment, block-boundary energy, active-box edge hits, or projected OVERDOSE slot block contacts as selectors.
  - Controls exceed active boundary-ratio behavior and the active quartet has no all-four block-grid outlier.
  - Frontier now records `161` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current Scan Halftone Screen Gate

- Status: checked; current-scan halftone/screen texture does not provide a selector.
- Evidence:
  - `scripts/audit_current_scan_halftone_screen_gate.py`
  - `analysis_outputs/source_audit/current_scan_halftone_screen_gate/current_scan_halftone_screen_gate.md`
  - `analysis_outputs/source_audit/current_scan_halftone_screen_gate/current_scan_halftone_screen_gate.json`
  - `analysis_outputs/source_audit/current_scan_halftone_screen_gate/current_scan_halftone_screen_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured high-frequency/halftone texture and dominant screen-angle behavior in active O4/B4/G5/O5 boxes, 16 shifted controls, and 8 projected C9/OVERDOSE slots.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`.
  - Active dominant-share outliers above shifted-control p95: `0`.
  - Active highpass-RMS outliers above shifted-control p95: `1`.
  - All-four active dominant-share/highpass outliers: `0` / `0`.
  - Active dominant angle bin: `90.0-112.5` for all four active boxes.
  - Matching controls / matching OVERDOSE slots for that bin: `12` / `7`.
  - Max active/control/OVERDOSE dominant share: `0.241` / `0.373` / `0.240`.
  - Max active/control/OVERDOSE highpass RMS: `50.752` / `50.636` / `38.139`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|controls=16|slots=8|shareOutliers=0|highpassOutliers=1|allFourShare=0|allFourHighpass=0|activeBins=90.0-112.5,90.0-112.5,90.0-112.5,90.0-112.5|commonBin=90.0-112.5|controlCommon=12|slotCommon=7|shareMax=0.241/0.373/0.240|highpassMax=50.752/50.636/38.139|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote halftone/screen angle, high-frequency texture, high-pass residue, dominant gradient bin, or print/scan texture anisotropy as selectors.
  - The active boxes share a dominant angle bin, but that same bin is common in shifted controls and projected OVERDOSE slots; active texture strength is not an all-four outlier.
  - Frontier now records `162` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current PDF Logical Structure Gate

- Status: checked; tagged-PDF/logical structure does not provide a selector.
- Evidence:
  - `scripts/audit_current_pdf_logical_structure_gate.py`
  - `analysis_outputs/source_audit/current_pdf_logical_structure_gate/current_pdf_logical_structure_gate.md`
  - `analysis_outputs/source_audit/current_pdf_logical_structure_gate/current_pdf_logical_structure_gate.json`
  - `analysis_outputs/source_audit/current_pdf_logical_structure_gate/current_pdf_logical_structure_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected current PDFs for `StructTreeRoot`, `MarkInfo`, `ActualText`, `Alt`, `MCID`, `Artifact`, `BDC/BMC/EMC`, and related logical/marked-content markers.
  - Separated decoded content-stream markers from raw byte occurrences.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs: `3`.
  - Tagged catalog count: `0`.
  - Logical object marker count: `0`.
  - Decoded content marker count / page-76 decoded marker count: `0` / `0`.
  - Raw-only `BDC` candidates: `1`.
  - Strict context hits: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|taggedCatalogs=0|logicalObjects=0|contentMarkers=0|p76ContentMarkers=0|rawOnlyBDC=1|strict=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote tagged-PDF/logical structure, `ActualText`, `Alt`, `MCID`, marked-content operators, or PDF logical reading order as selectors for the current PDFs.
  - The lone raw `BDC` occurrence is not present in decoded content streams and does not attach to page 76 or active targets.
  - Frontier now records `163` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.

### Current Scan Valid-Leaf Local Warp Gate

- Status: checked; local page-warp/curl compensation does not provide a selector.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_local_warp_gate.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_gate/current_scan_valid_leaf_local_warp_gate.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_gate/current_scan_valid_leaf_local_warp_gate.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_gate/current_scan_valid_leaf_local_warp_gate_sheet.jpg`
  - Four per-target panels under `analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_gate/`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Kept the physically valid page 75 -> page 76 light-table topology and mirrored page 75 into page 76.
  - Allowed each O4/B4/G5/O5 box, same-size controls, and projected C9/OVERDOSE slot box an independent local `[-120,120]` px translation at 20 px steps.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active boxes / OVERDOSE slots / local shifts per box: `4` / `8` / `169`.
  - Active best source-only coverage max/min/mean: `0.0693` / `0.0038` / `0.0248`.
  - Active boxes above same-size control p95: `0/4`.
  - Active boxes at least 10% / 25% source-only coverage: `0` / `0`.
  - Max active control percentile: `0.210`.
  - Max control best source-only coverage: `0.9982`.
  - Active best-shift dx/dy range: `120` / `240`.
  - Max OVERDOSE-slot best source-only coverage / slots at least 25%: `0.2575` / `1`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|slots=8|shifts=169|activeMax=0.0693|activeMin=0.0038|activeMean=0.0248|activeP95=0|active10=0|active25=0|pctMax=0.210|controlMax=0.9982|warpRange=120/240|slotMax=0.2575|slot25=1|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote local page curl, local warp compensation, per-box registration, source-only active coverage, or projected OVERDOSE slot local alignment as selectors.
  - The active quartet stays weak even under an independent-shift upper bound, while lower-page controls can be made far stronger under the same rule.
  - Frontier now records `164` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Valid-Leaf Local-Warp Source Trace

- Status: checked; local-warp source provenance does not provide a selector.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_local_warp_source_trace.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_source_trace/current_scan_valid_leaf_local_warp_source_trace.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_source_trace/current_scan_valid_leaf_local_warp_source_trace.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_source_trace/current_scan_valid_leaf_local_warp_source_trace_sheet.jpg`
  - Twelve per-row trace panels under `analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_source_trace/`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Traced source-only pixels selected by the valid page 75 -> page 76 local-warp upper-bound gate back to page-75 source words.
  - Covered active O4/B4/G5/O5 and all eight projected C9/OVERDOSE slots.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Trace rows / active / OVERDOSE slots: `12` / `4` / `8`.
  - Component rows / total components / component pixels: `12` / `115` / `136876`.
  - Source-only pixels traced: `236995`.
  - Source-word rows / strict instruction rows / context rows: `12` / `0` / `3`.
  - Active strict rows / OVERDOSE-slot strict rows: `0` / `0`.
  - Source word hits / strict instruction hits / context hits: `143` / `0` / `3`.
  - Active previews: O4 `or shitcoinery.`, B4 `lab.`, G5 `with your bare rabbit hole if this`, O5 `Anything worth hearing is`.
  - OVERDOSE context hits are ordinary `bitcoin` only in slots 5/6/7.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `rows=12|active=4|slots=8|componentRows=12|components=115|pixels=136876|sourceOnly=236995|wordRows=12|strictRows=0|contextRows=3|activeStrict=0|slotStrict=0|words=143|strict=0|context=3|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote local-warp source traces, source-only component provenance, or projected OVERDOSE slot source words as selectors.
  - Local-warp pixels trace to sparse ordinary page-75 prose/graphic areas; no source-side unit/order instruction appears.
  - Frontier now records `165` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Native Image Registration Gate

- Status: checked; exact embedded-PDF page image registration does not provide a selector.
- Evidence:
  - `scripts/audit_current_pdf_native_image_registration_gate.py`
  - `analysis_outputs/source_audit/current_pdf_native_image_registration_gate/current_pdf_native_image_registration_gate.md`
  - `analysis_outputs/source_audit/current_pdf_native_image_registration_gate/current_pdf_native_image_registration_gate.json`
  - `analysis_outputs/source_audit/current_pdf_native_image_registration_gate/current_pdf_native_image_registration_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used each PDF's embedded page images and exact image placement boxes for article page 75 -> page 76.
  - Mirrored page 75 into page 76 with no registration search or local shifts, then measured active O4/B4/G5/O5 boxes and all projected C9/OVERDOSE slots.
  - Covered `magazine.pdf`, `keyser bitcoin .pdf`, and `analysis_outputs/external_clues/google_drive_article_download.pdf`.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / pairs / active rows / projected OVERDOSE slot rows: `3` / `3` / `12` / `24`.
  - Same image-rect pairs / placement-offset pairs / side-margin pairs: `3` / `0` / `2`.
  - Active rows above same-size control p95 / at least 10% / at least 25%: `2` / `2` / `2`.
  - PDFs with all four active above control p95 / all four active at least 10%: `0` / `0`.
  - Max active / mean active / max control source-only coverage: `0.5800` / `0.1187` / `0.8795`.
  - Max projected OVERDOSE-slot source-only coverage / slots at least 25%: `0.6341` / `2`.
  - `magazine.pdf` exact native registration is weak at active boxes: max active coverage `0.0058`, with `0/4` above p95 and `0/4` at least 10%.
  - The two low-resolution duplicate PDFs produce a single O4 spike (`0.5800`) but B4/G5/O5 remain weak (`0.0559`, `0.0694`, `0.0004`), so the artifact does not form an all-four rule.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|pairs=3|activeRows=12|slots=24|sameRects=3|offsetPairs=0|sideMargins=2|activeMax=0.5800|activeMean=0.1187|activeP95=2|active10=2|active25=2|allFourP95=0|allFour10=0|controlMax=0.8795|slotMax=0.6341|slot25=2|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote PDF-native image placement, page-image rect parity, side margins, or exact embedded-image registration as selectors.
  - The current PDFs preserve identical page-75/page-76 image rectangles within each pair and expose no original-layout offset or hidden registration cue; exact native registration does not rescue the active quartet.
  - Frontier now records `166` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Native Registration Candidate Source Trace

- Status: checked; the exact-registration low-resolution O4/slot0 anomaly traces to ordinary source material, not instructions.
- Evidence:
  - `scripts/audit_current_pdf_native_registration_candidate_source_trace.py`
  - `analysis_outputs/source_audit/current_pdf_native_registration_candidate_source_trace/current_pdf_native_registration_candidate_source_trace.md`
  - `analysis_outputs/source_audit/current_pdf_native_registration_candidate_source_trace/current_pdf_native_registration_candidate_source_trace.json`
  - `analysis_outputs/source_audit/current_pdf_native_registration_candidate_source_trace/current_pdf_native_registration_candidate_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Traced only exact PDF-native registration rows that crossed thresholds in the previous gate: O4 and projected OVERDOSE slot0 in the two low-resolution duplicate PDFs.
  - Mapped source-only pixels back through the valid page 75 -> page 76 mirror to page-75 source words.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Candidate trace rows / active / OVERDOSE slots: `4` / `2` / `2`.
  - Components / component pixels / source-only pixels: `34` / `196264` / `198756`.
  - Source-word rows / source-word hits: `2` / `16`.
  - Strict instruction rows / hits: `0` / `0`.
  - Context rows / hits: `2` / `2`.
  - The active O4 duplicate rows map to ordinary page-75 prose around `in by riding Bitcoins Buterin came up with`.
  - The projected OVERDOSE slot0 duplicate rows map to a no-word/blank source region.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `rows=4|active=2|slots=2|components=34|pixels=196264|sourceOnly=198756|wordRows=2|words=16|strictRows=0|strict=0|contextRows=2|context=2|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote the low-resolution duplicate PDF O4/slot0 native-registration spike as a selector.
  - The threshold-crossing pixels trace to ordinary page-75 prose/context or blank regions, not to source-side unit/order wording; the effect is duplicate-only and non-quartet.
  - Frontier now records `167` focused local checks; best next direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Held-to-Light Composite Polarity Gate

- Status: checked; exact PDF-native held-to-light simulator/orientation variants do not provide a selector.
- Evidence:
  - `scripts/audit_current_pdf_held_to_light_composite_polarity_gate.py`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/current_pdf_held_to_light_composite_polarity_gate.md`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/current_pdf_held_to_light_composite_polarity_gate.json`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/current_pdf_held_to_light_composite_polarity_gate_sheet.jpg`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/magazine_physical_back_mirror_held_to_light_full.jpg`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/magazine_physical_back_mirror_held_to_light_active_crop.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Built a held-to-light composite simulator from each current PDF's embedded page-75 and page-76 article images.
  - Tested four fixed physical orientation hypotheses: physical back mirror, same-side no mirror, back mirror plus 180-degree turn, and front 180-degree turn.
  - Measured active O4/B4/G5/O5 boxes and projected C9/OVERDOSE slots against same-size lower-page controls.
  - No registration search, OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / transforms / variants: `3` / `4` / `12`.
  - Active rows / projected OVERDOSE slot rows: `48` / `96`.
  - Best active boxes >=10% source-only / above control p95 / clean-through >=10%: `3` / `0` / `3`.
  - All-four >=10% / all-four above p95 / all-four clean-through variants: `0` / `0` / `0`.
  - Original-resolution `magazine.pdf` physical-back mirror active boxes >=10% / mean source-only coverage: `0` / `0.0033`.
  - Max active / max control / max OVERDOSE-slot source-only coverage: `0.5800` / `0.9998` / `0.6341`.
  - The derivative PDFs can still inflate isolated O4/slot coverage, but no transform produces an all-four O4/B4/G5/O5 rule and same-size controls remain stronger.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|transforms=4|variants=12|activeRows=48|slots=96|best10=3|bestP95=0|all10=0|allP95=0|magPhys10=0|magPhysMean=0.0033|activeMax=0.5800|controlMax=0.9998|slotMax=0.6341|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote exact PDF-native held-to-light orientation/polarity variants as selectors.
  - The true original-resolution `magazine.pdf` physical-back mirror view is essentially blank at the active quartet, and low-resolution derivative spikes remain non-quartet/control-dominated.
  - Frontier now records `168` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Held-to-Light Candidate Source Trace

- Status: checked; derivative held-to-light composite hits trace to ordinary source text/blank regions, not instructions.
- Evidence:
  - `scripts/audit_current_pdf_held_to_light_candidate_source_trace.py`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_candidate_source_trace/current_pdf_held_to_light_candidate_source_trace.md`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_candidate_source_trace/current_pdf_held_to_light_candidate_source_trace.json`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_candidate_source_trace/current_pdf_held_to_light_candidate_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Traced only threshold-crossing rows from the exact PDF-native held-to-light composite polarity gate.
  - Mapped source-only pixels back through each fixed orientation transform to page-75 source words.
  - Covered derivative active hits and projected OVERDOSE slots that crossed the prior pass threshold.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Candidate trace rows / active / OVERDOSE slots: `23` / `15` / `8`.
  - Unique trace shapes: `12`.
  - Component rows / components / source-only pixels: `23` / `203` / `581806`.
  - Source-word rows / source-word hits: `19` / `110`.
  - Strict instruction rows / hits: `0` / `0`.
  - Context rows / hits: `5` / `5`.
  - Representative source previews are ordinary page-75 prose or title/graphic text, including `in by riding Bitcoins Buterin came up with`, `Don't fa Keep your Go Bitcoin`, `The markets sensed Markets are like`, `TOXIC AF`, and blank/no-word slot regions.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `rows=23|active=15|slots=8|unique=12|componentRows=23|components=203|sourceOnly=581806|wordRows=19|words=110|strictRows=0|strict=0|contextRows=5|context=5|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote derivative PDF held-to-light composite hits as selectors.
  - The threshold-crossing rows trace to ordinary source prose, blank/no-word regions, or broad rotated/mirrored slices, not source-backed unit/order instructions.
  - Frontier now records `169` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Page 76 Highlight Edge Slot-Ruler Gate

- Status: checked; page-76 highlight edges/centers do not provide an OVERDOSE slot-ruler selector.
- Evidence:
  - `scripts/audit_page76_highlight_edge_slot_ruler_gate.py`
  - `analysis_outputs/source_audit/page76_highlight_edge_slot_ruler_gate/page76_highlight_edge_slot_ruler_gate.md`
  - `analysis_outputs/source_audit/page76_highlight_edge_slot_ruler_gate/page76_highlight_edge_slot_ruler_gate.json`
  - `analysis_outputs/source_audit/page76_highlight_edge_slot_ruler_gate/page76_highlight_edge_slot_ruler_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Treated page-76 highlight left/center/right edges as vertical fold/mirror rulers and top/center/bottom edges as horizontal fold rulers.
  - Mirrored active O4/B4/G5/O5 centers across those rulers and classified resulting x positions against the actual C9 OVERDOSE header glyph slots.
  - Checked axis-near page-76 text for strict instruction terms.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Page-76 highlights / vertical axes / horizontal axes: `5` / `15` / `15`.
  - Direct active center stream remains the known `OVED`.
  - All-four mirrored-inside-slot vertical axes: `5`; max mirrored active centers inside slots: `4`.
  - Those all-four-in-slot axes produce streams such as `ODRV`, `REOR`, `REOD`, and `OORV`, not `OVER` or `DOSE`.
  - Vertical axes with `OVER`/`DOSE` layout-term stream hits: `0`.
  - Strict / loose slot-boundary contacts: `0` / `4`.
  - Horizontal axes with all four mirrored centers inside the C9 frame Y-band: `0`.
  - Strict instruction axis hits: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `highlights=5|vAxes=15|hAxes=15|direct=OVED|allSlot=5|maxSlot=4|layoutAxes=0|strictSlot=0|looseSlot=4|hAllY=0|strictAxis=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote page-76 highlight edges/centers as OVERDOSE slot rulers or fold axes.
  - The axis mirror can keep all four active centers inside slots for several broad rulers, but it does not create a meaningful OVERDOSE-derived stream or source-backed unit/order wording.
  - Frontier now records `170` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### OVERDOSE Glyph Axis Ruler Gate

- Status: checked; actual OVERDOSE glyph edges/centers do not provide a fold-axis or slot-ruler selector.
- Evidence:
  - `scripts/audit_overdose_glyph_axis_ruler_gate.py`
  - `analysis_outputs/source_audit/overdose_glyph_axis_ruler_gate/overdose_glyph_axis_ruler_gate.md`
  - `analysis_outputs/source_audit/overdose_glyph_axis_ruler_gate/overdose_glyph_axis_ruler_gate.json`
  - `analysis_outputs/source_audit/overdose_glyph_axis_ruler_gate/overdose_glyph_axis_ruler_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Treated actual page-76 `OVERDOSE` header glyph edges/centers and their C9-projected equivalents as possible fold/mirror rulers.
  - Mirrored active O4/B4/G5/O5 centers across those axes and classified resulting x positions against the actual C9 OVERDOSE glyph slots.
  - Checked axis-near page-76 text for strict instruction terms.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Native header axes / C9-projected axes: `17` / `17`.
  - Native all-four mirrored-inside-slot axes / native max inside: `0` / `0`.
  - C9-projected all-four mirrored-inside-slot axes / projected max inside: `4` / `4`.
  - All-four projected streams: `ESOR`, `ODRV`, `RESD`, `VODE`.
  - Layout-term axis hits / strict instruction axis hits: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `nativeAxes=17|projectedAxes=17|nativeAllSlot=0|projectedAllSlot=4|nativeMax=0|projectedMax=4|layoutAxes=0|strictAxis=0|streams=ESOR,ODRV,RESD,VODE|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote OVERDOSE glyph edges/centers as fold axes or slot-ruler selectors.
  - Native header axes miss the lower C9 frame entirely; C9-projected axes can keep all four centers inside slots only as non-word fragments with no source-backed unit/order wording.
  - Frontier now records `171` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### OVERDOSE Glyph-Axis Word-Center Control Gate

- Status: checked; the C9-projected OVERDOSE axes that looked geometrically promising are broad controls, not selectors.
- Evidence:
  - `scripts/audit_overdose_glyph_axis_word_center_control_gate.py`
  - `analysis_outputs/source_audit/overdose_glyph_axis_word_center_control_gate/overdose_glyph_axis_word_center_control_gate.md`
  - `analysis_outputs/source_audit/overdose_glyph_axis_word_center_control_gate/overdose_glyph_axis_word_center_control_gate.json`
  - `analysis_outputs/source_audit/overdose_glyph_axis_word_center_control_gate/overdose_glyph_axis_word_center_control_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Kept only the four C9-projected OVERDOSE axes that mirrored all four active O4/B4/G5/O5 centers into glyph slots.
  - Applied them to ordinary non-target page-76 C9-frame word centers and four-word sliding windows.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Selected axes / active all-four axes: `4` / `4`.
  - Active streams: `ESOR`, `ODRV`, `RESD`, `VODE`; active meaningful layout axes: `0`.
  - C9 words / non-target controls: `88` / `85`.
  - Control word centers mirrored inside slots: `336/340`.
  - Control four-word windows / all-four-in-slot windows: `328` / `315`.
  - Control meaningful layout windows / strict instruction windows: `1` / `0`.
  - The one control layout hit is `ESOD` from ordinary prose `mine in bitcoin that`, which confirms the axis behavior is not active-specific.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `axes=4|activeAll=4|activeLayout=0|streams=ESOR,ODRV,RESD,VODE|c9Words=88|controls=85|ctrlInside=336/340|ctrlAll4=315/328|ctrlLayout=1|ctrlStrict=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote C9-projected OVERDOSE glyph axes as selectors.
  - They are broad C9 frame geometry and should remain source-validation context only.
  - Frontier now records `172` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Valid Leaf Strict-Term Disambiguation Gate

- Status: checked; the lone strict-looking term in the valid 75->76 line-band trace is ordinary prose, not an extraction instruction.
- Evidence:
  - `scripts/audit_valid_leaf_strict_term_disambiguation_gate.py`
  - `analysis_outputs/source_audit/valid_leaf_strict_term_disambiguation_gate/valid_leaf_strict_term_disambiguation_gate.md`
  - `analysis_outputs/source_audit/valid_leaf_strict_term_disambiguation_gate/valid_leaf_strict_term_disambiguation_gate.json`
  - `analysis_outputs/source_audit/valid_leaf_strict_term_disambiguation_gate/valid_leaf_strict_term_disambiguation_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Isolated the only strict-term hit from the physically valid page 75 -> page 76 held-to-light line-band trace.
  - Checked whether it is instruction grammar or ordinary prose.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Strict carrier rows / terms / targets: `1` / `words` / `O5`.
  - Action-term carriers / unit-only carriers / order-term carriers: `0` / `1` / `0`.
  - Instruction candidate carriers: `0`.
  - All-four active coverage by strict carriers: `false`.
  - Page-75 global strict-like line count: `1`.
  - The source text is ordinary prose: `to. Nice, pleasant words from con men and shitcoiners`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `strictRows=1|terms=words|targets=O5|action=0|unitOnly=1|order=0|instr=0|all4=0|p75StrictLines=1|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote valid-leaf line-band `words` as an instruction source.
  - Valid 75->76 line-band extraction remains closed for the current scan.
  - Frontier now records `173` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Valid Leaf Target-Context Instruction Gate

- Status: checked; target-side valid 75->76 line-band context is article prose, not selector grammar.
- Evidence:
  - `scripts/audit_valid_leaf_target_context_instruction_gate.py`
  - `analysis_outputs/source_audit/valid_leaf_target_context_instruction_gate/valid_leaf_target_context_instruction_gate.md`
  - `analysis_outputs/source_audit/valid_leaf_target_context_instruction_gate/valid_leaf_target_context_instruction_gate.json`
  - `analysis_outputs/source_audit/valid_leaf_target_context_instruction_gate/valid_leaf_target_context_instruction_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Classified target-side page-76 context words in the physically valid page 75 -> page 76 held-to-light line-band trace.
  - Checked tempting terms including `sell`, `mine`, and O5 phrase-context `heart`.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Trace rows / target context carrier rows: `8` / `6`.
  - Target line context terms: `bitcoin,bukele,imf,mine,sell,volcano`.
  - Phrase context terms: `billion,bond,dip,heart,shitcoiner,volcano`.
  - Target-only context carrier rows / source-backed context carrier rows: `6` / `1`.
  - Action / unit / order carrier rows: `0` / `0` / `0`.
  - Instruction candidates / source-backed instruction candidates: `0` / `0`.
  - The only exact source-backed context term is `bitcoin`, still with no instruction grammar.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `rows=8|ctxRows=6|lineTerms=bitcoin,bukele,imf,mine,sell,volcano|phraseTerms=billion,bond,dip,heart,shitcoiner,volcano|targetOnly=6|sourceCtx=1|sourceCtxTerms=bitcoin|action=0|unit=0|order=0|instr=0|sourceInstr=0|all4ctx=0|all4instr=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote target-side held-to-light context words as selectors.
  - `sell` and `mine` are page-76 article verbs, not extraction instructions.
  - `heart` appears in the known O5 phrase label but not as a readable target-side line-band context term in the current trace row.
  - Frontier now records `174` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Held-to-Light Active-Box Balance Gate

- Status: checked; current-scan light-table views do not physically isolate O4/B4/G5/O5 as a balanced quartet.
- Evidence:
  - `scripts/audit_current_scan_held_to_light_active_box_balance_gate.py`
  - `analysis_outputs/source_audit/current_scan_held_to_light_active_box_balance_gate/current_scan_held_to_light_active_box_balance_gate.md`
  - `analysis_outputs/source_audit/current_scan_held_to_light_active_box_balance_gate/current_scan_held_to_light_active_box_balance_gate.json`
  - `analysis_outputs/source_audit/current_scan_held_to_light_active_box_balance_gate/current_scan_held_to_light_active_box_balance_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Reused the current scan held-to-light simulator rows and current active target boxes.
  - Checked whether any physically valid page 75 -> page 76 view lights up O4/B4/G5/O5 together.
  - Compared physical natural 75->76, forced same-leaf shifts, and nonphysical page-78/page-79 controls.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active simulator rows: `9`.
  - Physical natural selector candidates: `0`.
  - Same-leaf 75->76 all-four >=10% rows / >=25% rows: `0` / `0`.
  - Nonphysical all-four >=10% rows / >=25% rows: `2` / `0`.
  - Physical natural 75->76 min active-box coverage: `0.0000`.
  - Best same-leaf 75->76 min coverage: `0.0540` at forced shift `-220,+200`.
  - Best nonphysical min coverage: `0.1138` at page `79->76` forced shift `+40,+80`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `activeRows=9|physicalCandidates=0|sameLeafAll4_10=0|sameLeafAll4_25=0|nonphysicalAll4_10=2|nonphysicalAll4_25=0|naturalMin=0.0000|sameLeafBestMin=0.0540@-220,200|nonphysicalBestMin=0.1138@nonphysical_79_to_76:40,80|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote current-scan held-to-light geometry as a selector.
  - Physical 75->76 does not illuminate the active quartet, and apparent all-four low-threshold hits require nonphysical page pairs and forced translations.
  - Frontier now records `175` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Partial Image Placement Gate

- Status: checked; the page-76 partial PDF image placements are duplicate inset full-page rasters, not local overlays.
- Evidence:
  - `scripts/audit_current_pdf_partial_image_placement_gate.py`
  - `analysis_outputs/source_audit/current_pdf_partial_image_placement_gate/current_pdf_partial_image_placement_gate.md`
  - `analysis_outputs/source_audit/current_pdf_partial_image_placement_gate/current_pdf_partial_image_placement_gate.json`
  - `analysis_outputs/source_audit/current_pdf_partial_image_placement_gate/current_pdf_partial_image_placement_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Resolved the two page-76 `partialImagePlacement` rows from the current PDF object/layout report.
  - Checked whether they are local overlays/original-layout carriers or just inset full-page raster pages.
  - Projected O4/B4/G5/O5 into the partial placement geometry.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Page-76 partial placements: `2`.
  - Partial signature groups / unique page-76 partial groups: `1` / `0`.
  - Near-full content partial rows / local overlay partial rows: `2` / `0`.
  - All-page repeating partial groups: `1`.
  - Partial rows containing all four active boxes: `2`.
  - Active projection rows inside placement: `8/8`.
  - Partial coverage range: `0.941176` - `0.941176`.
  - Strict hits / special keys / visible painted spans: `0` / `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `p76Partial=2|partialGroups=1|uniqueP76Partial=0|nearFull=2|localPartial=0|allPageGroups=1|allFourInside=2|activeInside=8/8|strict=0|special=0|visible=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote current-PDF partial placements as source/original-layout selectors.
  - They contain all four active boxes only because the lower-resolution duplicate PDF image is the whole article page inset inside side margins.
  - Frontier now records `176` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Form Overlay Placement Gate

- Status: checked; the duplicate-PDF `OL2` OCR form offset is a repeated near-full-page invisible text overlay, not a page-76 selector.
- Evidence:
  - `scripts/audit_current_pdf_form_overlay_placement_gate.py`
  - `analysis_outputs/source_audit/current_pdf_form_overlay_placement_gate/current_pdf_form_overlay_placement_gate.md`
  - `analysis_outputs/source_audit/current_pdf_form_overlay_placement_gate/current_pdf_form_overlay_placement_gate.json`
  - `analysis_outputs/source_audit/current_pdf_form_overlay_placement_gate/current_pdf_form_overlay_placement_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Applied the duplicate-PDF `OL2` form placement matrix to its actual form BBox.
  - Checked whether the `0.119995pt` offset is a hidden/local layout signal or a whole-page OCR wrapper.
  - Projected O4/B4/G5/O5 into the overlay geometry.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Form placements / page-76 form placements: `16` / `2`.
  - Overlay signature groups / page-76 unique overlay groups: `1` / `0`.
  - Active unique overlay groups: `0`.
  - Near-full overlays / page-76 near-full overlays: `16` / `2`.
  - All-page repeating overlay groups: `1`.
  - Visible/invisible text placements: `0` / `16`.
  - Strict/context hits: `0` / `0`.
  - Top offset point values: `0.119995`.
  - Active projection rows inside overlay: `8/8`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `forms=16|p76Forms=2|groups=1|p76Unique=0|activeUnique=0|nearFull=16|p76NearFull=2|allPageGroups=1|visiblePlacements=0|invisiblePlacements=16|strict=0|offsets=0.119995|activeInside=8/8|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote `OL2` form placement or the `0.119995pt` offset as a selector.
  - The overlay contains all active boxes only because it covers almost the whole page, and the text is invisible OCR with no strict unit/order wording.
  - Frontier now records `177` focused local checks; best next direction remains external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Light-Table Blend-Mode Gate

- Status: checked; alternate held-to-light blend modes do not unlock a source-backed selector.
- Evidence:
  - `scripts/audit_current_scan_light_table_blend_mode_gate.py`
  - `analysis_outputs/source_audit/current_scan_light_table_blend_mode_gate/current_scan_light_table_blend_mode_gate.md`
  - `analysis_outputs/source_audit/current_scan_light_table_blend_mode_gate/current_scan_light_table_blend_mode_gate.json`
  - `analysis_outputs/source_audit/current_scan_light_table_blend_mode_gate/current_scan_light_table_blend_mode_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Reused the current scan/PDF page images and existing held-to-light registrations.
  - Tested five blend modes at three alpha levels against O4/B4/G5/O5, compared with 24 nearby line-shifted controls.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Scenarios / blend rows / controls: `4` / `60` / `24`.
  - Natural 75->76 all-four active-outlier rows: `3`.
  - Natural 75->76 all-four source-supported rows: `0`.
  - Best natural blend: `average@0.70`, active outliers `4/4`, source-supported outliers `3/4`, min active source-ink ratio `0.0000`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `scenarios=4|modes=5|alphas=3|blendRows=60|controls=24|naturalAll4Outlier=3|controlAll4Outlier=0|naturalAll4Source=0|controlAll4Source=0|bestNatural=4/4:3/4src:average@0.70:29.55|bestControl=3/4:3/4src:nonphysical_79_to_76_forced_active:average@0.35:-10.50|preR3=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote the average-blend all-four visual pop as a selector.
  - The effect is not source-ink-supported across O4/B4/G5/O5 and is best treated as target-highlight washout under arbitrary blend/alpha.
  - Frontier now records `178` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Valid-Leaf Source-Ink Landing Gate

- Status: checked; the valid physical 75->76 held-to-light leaf does not land source ink on all four active targets.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_source_ink_landing_gate.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/current_scan_valid_leaf_source_ink_landing_gate.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/current_scan_valid_leaf_source_ink_landing_gate.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/current_scan_valid_leaf_source_ink_landing_gate_sheet.jpg`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/valid_75_to_76_source_ink_overlay.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured actual mirrored page-75 source ink landing inside O4/B4/G5/O5 under the natural same-leaf 75->76 registration.
  - Compared the active boxes with 24 same-size line-shifted controls.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active source-supported targets at >=0.05: `O4,G5,O5` (`3/4`).
  - Zero-source-ink targets: `B4`.
  - Source-ink ratios: `O4:0.1402`, `B4:0.0000`, `G5:0.0596`, `O5:0.1940`.
  - All-four source-supported / weak-source-supported: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `scenario=valid_75_to_76_natural|targets=4|controls=24|activeGe05=3|activeGe01=3|all4Ge05=0|all4Ge01=0|zeroTargets=B4|ratios=O4:0.1402,B4:0.0000,G5:0.0596,O5:0.1940|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not treat the valid 75->76 physical leaf as extraction-ready.
  - B4 has zero landing source ink, so the average-blend all-four visual pop is not a physical back-page ink carrier.
  - Frontier now records `179` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Valid-Leaf Jitter Source-Ink Rescue Gate

- Status: checked; small physical-registration jitter does not rescue B4 source ink.
- Evidence:
  - `scripts/audit_current_scan_valid_leaf_jitter_source_ink_rescue_gate.py`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate/current_scan_valid_leaf_jitter_source_ink_rescue_gate.md`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate/current_scan_valid_leaf_jitter_source_ink_rescue_gate.json`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate/current_scan_valid_leaf_jitter_source_ink_rescue_gate_sheet.jpg`
  - `analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate/best_b4_jitter_source_ink_overlay.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested the documented `+-4px` common visual tolerance window and an extended `+-8px` guardrail window around natural page-75-to-76 held-to-light registration.
  - Scanned 81 credible shifts and 289 guardrail shifts.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Credible all-four source-supported rows / B4-positive rows: `0` / `0`.
  - Extended all-four source-supported rows / B4-positive rows: `0` / `0`.
  - Best credible shift: `0,0`, active support `3/4`, B4 source ink `0.0000`, min active source ink `0.0000`.
  - Best credible ratios: `O4:0.1402`, `B4:0.0000`, `G5:0.0596`, `O5:0.1940`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `credible=+-4|extended=+-8|credibleRows=81|extendedRows=289|credAll4=0|extAll4=0|credB4Pos=0|extB4Pos=0|bestCred=0,0:3/4:B4=0.0000:min=0.0000|bestExt=0,0:3/4:B4=0.0000:min=0.0000|bestCredRatios=O4:0.1402,B4:0.0000,G5:0.0596,O5:0.1940|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue current-scan valid-leaf source-ink rescue.
  - The B4 zero-source-ink blocker is stable against small physical registration jitter.
  - Frontier now records `180` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current Scan B4 Self-Signal Guardrail

- Status: checked; B4's average-blend visual pop is target-only, not source-backed.
- Evidence:
  - `scripts/audit_current_scan_b4_self_signal_guardrail.py`
  - `analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail/current_scan_b4_self_signal_guardrail.md`
  - `analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail/current_scan_b4_self_signal_guardrail.json`
  - `analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail/current_scan_b4_self_signal_guardrail_sheet.jpg`
  - `analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail/b4_self_signal_delta_overlay.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Decomposed valid natural page-75-to-76 `average@0.70` blend deltas into source-supported versus page-76 target-only pixels.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Source-supported outlier targets: `O4,G5,O5` (`3/4`).
  - Zero-source self-signal targets: `B4`.
  - All-four source-supported outlier: `False`.
  - B4 source-ink ratio: `0.000000`.
  - B4 target-only delta share: `0.995667`.
  - B4 source-supported delta share: `0.000000`.
  - B4 average-delta outlier over matched controls: `+85.055301`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `scenario=valid_75_to_76_natural|alpha=0.70|targets=4|controls=24|B4src=0.0000|B4targetOnly=0.9957|B4srcDelta=0.0000|B4dCtl=85.06|srcOutliers=3/4|selfZero=B4|all4Src=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote B4 average-blend contrast or the all-four average-blend visual pop as a selector.
  - The B4 effect is explained by page-76 black target ink being washed by a blank/white source area, not by physical source ink.
  - Frontier now records `181` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Active-Region Render/Embedded Identity Gate

- Status: checked; current PDF visible renders add no active/OVERDOSE layer beyond embedded page-image carriers.
- Evidence:
  - `scripts/audit_current_pdf_active_region_render_embedded_identity_gate.py`
  - `analysis_outputs/source_audit/current_pdf_active_region_render_embedded_identity_gate/current_pdf_active_region_render_embedded_identity_gate.md`
  - `analysis_outputs/source_audit/current_pdf_active_region_render_embedded_identity_gate/current_pdf_active_region_render_embedded_identity_gate.json`
  - `analysis_outputs/source_audit/current_pdf_active_region_render_embedded_identity_gate/current_pdf_active_region_render_embedded_identity_gate_sheet.jpg`
  - Render/embedded preview images for `magazine.pdf`, `keyser bitcoin .pdf`, and `analysis_outputs/external_clues/google_drive_article_download.pdf`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared normalized visible page-76 PDF renders to the normalized embedded page-image carrier over active boxes, OVERDOSE slots, and matched controls.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked / measured regions: `3` / `60`.
  - Active render-vs-embedded mismatches: `0`.
  - All-four active mismatch PDF count: `0`.
  - OVERDOSE-slot render-vs-embedded mismatches: `0`.
  - Matched-control render-vs-embedded mismatches: `0`.
  - Max active / OVERDOSE-slot render-vs-embedded mean absolute difference: `7.198912` / `3.121697`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|regions=60|activeMismatch=0|all4Pdf=0|slotMismatch=0|controlMismatch=0|maxActive=7.199|maxSlot=3.122|activeP95=6.708|controlP95=5.031|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue current-PDF hidden visible render overlays for active boxes or OVERDOSE mechanics.
  - The PDFs render the same raster page-image carrier in the measured regions; they do not restore original-layout authority.
  - Frontier now records `182` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current Scan RGB Registration Gate

- Status: checked; RGB channel registration does not create a hidden active/OVERDOSE signal.
- Evidence:
  - `scripts/audit_current_scan_rgb_registration_gate.py`
  - `analysis_outputs/source_audit/current_scan_rgb_registration_gate/current_scan_rgb_registration_gate.md`
  - `analysis_outputs/source_audit/current_scan_rgb_registration_gate/current_scan_rgb_registration_gate.json`
  - `analysis_outputs/source_audit/current_scan_rgb_registration_gate/current_scan_rgb_registration_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured local RGB channel displacement in page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots.
  - Search radius was `+-3px` for red-against-green and blue-against-green edge alignment.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`.
  - Reliable active boxes: `4/4`.
  - Active nonzero RGB registration rows: `0`.
  - Active confidence-gain outliers above shifted-control p95: `0`.
  - All-four active nonzero / confidence outlier: `0` / `0`.
  - Shared active shift signature / matching controls / matching OVERDOSE slots: `RG+0,+0|BG+0,+0` / `16` / `8`.
  - Max active/control/OVERDOSE shift magnitude: `0.0` / `0.0` / `0.0` px.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|controls=16|slots=8|radius=3|reliableActive=4|activeNonzero=0|activeGainOutliers=0|allFourNonzero=0|allFourGain=0|commonSig=RG+0,+0|BG+0,+0|controlCommon=16|slotCommon=8|shiftMax=0.0/0.0/0.0|gainMax=0.000/0.000/0.000|controlP95=0.0/0.000|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue RGB channel registration, chromatic displacement, or scan color-fringe behavior as selectors.
  - The current scan shows no channel-offset carrier in active boxes or projected OVERDOSE slots.
  - Frontier now records `183` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Color Management / ExtGState Gate

- Status: checked; current PDF graphics-state/color-management resources do not create a hidden active/OVERDOSE selector.
- Evidence:
  - `scripts/audit_current_pdf_color_management_extgstate_gate.py`
  - `analysis_outputs/source_audit/current_pdf_color_management_extgstate_gate/current_pdf_color_management_extgstate_gate.md`
  - `analysis_outputs/source_audit/current_pdf_color_management_extgstate_gate/current_pdf_color_management_extgstate_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected current PDF catalog OutputIntents, page ColorSpace/ExtGState resources, blend/opacity/transfer/overprint keys, image Decode/Intent/Interpolate keys, and color operators.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs/page rows: `3` / `24`.
  - OutputIntent objects: `0`.
  - Page-76 unique resource signatures: `0`.
  - ExtGState objects / page-76 ExtGState objects: `0` / `0`.
  - Blend/opacity/transfer/overprint ExtGState objects: `0` / `0` / `0` / `0`.
  - ColorSpace objects / page-76 ColorSpace objects: `0` / `0`.
  - ICCBased / Separation-or-DeviceN ColorSpace objects: `0` / `0`.
  - Image objects / page-76 image objects: `24` / `3`.
  - Image Decode-array rows / special image color-key rows: `0` / `0`.
  - Strict/context hits: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|pages=24|outputIntents=0|page76UniqueRes=0|ext=0|p76ext=0|bm=0|opacity=0|transfer=0|overprint=0|colorspaces=0|p76colorspaces=0|icc=0|sep=0|images=24|decode=0|specialImages=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue current-PDF color-management, OutputIntent, ExtGState, blend/opacity/transfer/overprint, or image Decode/Intent paths as selectors.
  - The current PDFs remain raster/OCR witnesses only; they do not expose a hidden graphics-state or page-76 resource carrier.
  - Frontier now records `184` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Luminance Bitplane Gate

- Status: checked; low-order bit-plane and threshold-plane contrast does not create a hidden active/OVERDOSE selector.
- Evidence:
  - `scripts/audit_current_scan_luminance_bitplane_gate.py`
  - `analysis_outputs/source_audit/current_scan_luminance_bitplane_gate/current_scan_luminance_bitplane_gate.md`
  - `analysis_outputs/source_audit/current_scan_luminance_bitplane_gate/current_scan_luminance_bitplane_gate.json`
  - `analysis_outputs/source_audit/current_scan_luminance_bitplane_gate/current_scan_luminance_bitplane_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured low-order luminance bit planes `[0,1,2,3]` and threshold masks `[64,96,128,160,192]` in page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`.
  - Active low-bit outlier rows: `4` (`O4,B4,G5,O5`).
  - Active threshold-plane outlier rows: `4` (`O4,B4,G5,O5`).
  - All-four active low-bit / threshold-plane outlier: `1` / `1`.
  - Active common low-bit signature: `mixed`.
  - Shared active low-bit carrier / hidden bitplane candidate: `0` / `0`.
  - Max active/control/OVERDOSE low-bit abs-z: `4.62` / `1.81` / `1.50`.
  - Max active/control/OVERDOSE threshold abs-z: `10.15` / `2.17` / `1.29`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|controls=16|slots=8|bits=0,1,2,3|thresholds=64,96,128,160,192|activeLowBitOutliers=4|activeThresholdOutliers=4|allFourLowBit=1|allFourThreshold=1|sharedCarrier=0|hiddenCandidate=0|commonLowBit=mixed|controlCommon=0|slotCommon=0|maxLowBitZ=4.62/1.81/1.50|maxThresholdZ=10.15/2.17/1.29|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue current-scan luminance bit-plane or threshold-plane tuning as a selector.
  - The active boxes stand out because visible orange/black target ink has distinct plane statistics, but there is no shared low-bit carrier and no source-backed unit/order/transform cue.
  - Frontier now records `185` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Threshold Morphology Gate

- Status: checked; thresholded ink/component shape does not create a hidden active/OVERDOSE selector.
- Evidence:
  - `scripts/audit_current_scan_threshold_morphology_gate.py`
  - `analysis_outputs/source_audit/current_scan_threshold_morphology_gate/current_scan_threshold_morphology_gate.md`
  - `analysis_outputs/source_audit/current_scan_threshold_morphology_gate/current_scan_threshold_morphology_gate.json`
  - `analysis_outputs/source_audit/current_scan_threshold_morphology_gate/current_scan_threshold_morphology_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured thresholded ink/component morphology at thresholds `[64,96,128,160,192]` in page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots.
  - Metrics included component counts, largest component ratios, ink bbox area, row/column occupancy, and projection-run counts.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`.
  - Active morphology outlier rows: `4` (`O4,B4,G5,O5`).
  - All-four active morphology outlier: `1`.
  - Active common morphology signature: `mixed`.
  - Shared active morphology carrier / hidden morphology candidate: `0` / `0`.
  - Max active/control/OVERDOSE morphology abs-z: `78.91` / `2.48` / `30.19`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|controls=16|slots=8|thresholds=64,96,128,160,192|activeMorphOutliers=4|allFourMorph=1|sharedCarrier=0|hiddenCandidate=0|commonMorph=mixed|controlCommon=0|slotCommon=0|maxMorphZ=78.91/2.48/30.19|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue current-scan threshold morphology or component-shape tuning as a selector.
  - The active boxes stand out because visible orange/black target ink has distinct component morphology, but the active signatures are mixed and do not form a shared all-four carrier.
  - Frontier now records `186` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Highlight Edge-Halo Gate

- Status: checked; outside-ring orange/black highlight halo does not create a hidden active/OVERDOSE selector.
- Evidence:
  - `scripts/audit_current_scan_highlight_edge_halo_gate.py`
  - `analysis_outputs/source_audit/current_scan_highlight_edge_halo_gate/current_scan_highlight_edge_halo_gate.md`
  - `analysis_outputs/source_audit/current_scan_highlight_edge_halo_gate/current_scan_highlight_edge_halo_gate.json`
  - `analysis_outputs/source_audit/current_scan_highlight_edge_halo_gate/current_scan_highlight_edge_halo_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured outside orange/black/combined-ink edge rings at pads `[4,8,16,32]` around page-76 active boxes, shifted controls, and projected C9/OVERDOSE slots.
  - Inside edge strips were kept as diagnostics only; the decision score uses outside-ring halo measurements.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active/control/OVERDOSE-slot boxes: `4` / `16` / `8`.
  - Active outside-ring halo outlier rows: `3` (`O4,B4,O5`); `G5` does not pass as an outside-halo outlier.
  - All-four active outside-ring halo outlier: `0`.
  - Active common halo signature: `mixed`.
  - Active common ink edge-bias signature: `mixed`.
  - Shared active halo carrier / hidden halo candidate: `0` / `0`.
  - Max active/control/OVERDOSE halo abs-z: `19.49` / `3.72` / `11.78`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|controls=16|slots=8|outerPads=4,8,16,32|innerStrips=4,8,16|activeHaloOutliers=3|allFourHalo=0|sharedCarrier=0|hiddenCandidate=0|commonHalo=mixed|commonEdge=mixed|controlHaloCommon=0|slotHaloCommon=0|controlEdgeCommon=0|slotEdgeCommon=0|maxHaloZ=19.49/3.72/11.78|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue current-scan highlight edge-halo tuning as a selector.
  - The outside rings show highlight-adjacent behavior for O4/B4/O5, but G5 does not join it and the active edge directions do not form a shared carrier.
  - Frontier now records `187` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Slot-Boundary Residual Gate

- Status: checked; target starts, centers, and ends do not create a C9/OVERDOSE slot-ruler selector.
- Evidence:
  - `scripts/audit_current_scan_slot_boundary_residual_gate.py`
  - `analysis_outputs/source_audit/current_scan_slot_boundary_residual_gate/current_scan_slot_boundary_residual_gate.md`
  - `analysis_outputs/source_audit/current_scan_slot_boundary_residual_gate/current_scan_slot_boundary_residual_gate.json`
  - `analysis_outputs/source_audit/current_scan_slot_boundary_residual_gate/current_scan_slot_boundary_residual_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured O4/B4/G5/O5 box starts, centers, and ends against actual C9/OVERDOSE glyph-slot boundaries and centers.
  - Compared active boxes with page-76 non-active highlight controls and vertical-shift controls.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active/highlight-control/vertical-control boxes: `4` / `7` / `16`.
  - All-four active any-anchor close <=16 px: `0`.
  - All-four active left-boundary / center / right-boundary close <=16 px: `0` / `0` / `0`.
  - Active common slot-boundary signature: `mixed`.
  - Active nearest-center streams L/C/R: `DOER` / `OVED` / `SVRO`.
  - Active nearest-boundary streams L/C/R: `4123` / `5134` / `6246`.
  - Mean active/highlight-control anchor residual: `31.90` / `26.00` px.
  - Shared active slot-boundary carrier / hidden slot-boundary candidate: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|highlightControls=7|verticalControls=16|thresholds=4,8,16,32|allFourAny16=0|allFourLeftB16=0|allFourCenter16=0|allFourRightB16=0|commonSig=mixed|streamsC=DOER/OVED/SVRO|streamsB=4123/5134/6246|meanResidual=31.90/26.00|sharedCarrier=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue C9/OVERDOSE slot-boundary residual tuning as a selector.
  - The known center stream `OVED` is still visible, but no all-four boundary/center/right-edge landing pattern appears and non-active controls are at least as close to the ruler.
  - Frontier now records `188` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current Scan Active Envelope Transform Gate

- Status: checked; the active quartet does not fold/mirror back onto itself around its own envelope.
- Evidence:
  - `scripts/audit_current_scan_active_envelope_transform_gate.py`
  - `analysis_outputs/source_audit/current_scan_active_envelope_transform_gate/current_scan_active_envelope_transform_gate.md`
  - `analysis_outputs/source_audit/current_scan_active_envelope_transform_gate/current_scan_active_envelope_transform_gate.json`
  - `analysis_outputs/source_audit/current_scan_active_envelope_transform_gate/current_scan_active_envelope_transform_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Transformed O4/B4/G5/O5 around their own active envelope `[428.0,2177.0,1801.0,2982.0]`, center `[1114.5,2579.5]`.
  - Tested `hmirror`, `vmirror`, `rot180`, `diag_main`, and `diag_anti`.
  - Compared transformed centers/boxes against active targets, page-76 non-active highlight controls, and actual C9/OVERDOSE slots.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active/highlight-control boxes: `4` / `7`.
  - Best active-other hit count <=32 / <=64 px: `0` / `1`.
  - Any transform all-four active-other re-hit <=32 / <=64 px: `0` / `0`.
  - Any transform all-four active-any re-hit <=32 / <=64 px: `0` / `0`.
  - Best transform by active-other <=64 px: `diag_anti`.
  - Slot streams: `hmirror:VORE`, `vmirror:OVED`, `rot180:VORE`, `diag_main:OERO`, `diag_anti:ODRO`.
  - Hidden active-envelope transform candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|highlightControls=7|transforms=hmirror,vmirror,rot180,diag_main,diag_anti|allFourAny32=0|allFourAny64=0|allFourOther32=0|allFourOther64=0|bestOther32=0|bestOther64=1|bestTransform=diag_anti|streams=hmirror:VORE/0/0,vmirror:OVED/0/0,rot180:VORE/0/0,diag_main:OERO/0/0,diag_anti:ODRO/0/1|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue active-envelope centered mirror/rotation/diagonal-fold geometry as a selector.
  - The best result is only one weak active-other near-hit within 64 px, not an all-four fold carrier.
  - Frontier now records `189` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Active Box Coordinate Grid Gate

- Status: checked; current-PDF page-point coordinates do not create a hidden active-box selector.
- Evidence:
  - `scripts/audit_current_pdf_active_box_coordinate_grid_gate.py`
  - `analysis_outputs/source_audit/current_pdf_active_box_coordinate_grid_gate/current_pdf_active_box_coordinate_grid_gate.md`
  - `analysis_outputs/source_audit/current_pdf_active_box_coordinate_grid_gate/current_pdf_active_box_coordinate_grid_gate.json`
  - `analysis_outputs/source_audit/current_pdf_active_box_coordinate_grid_gate/current_pdf_active_box_coordinate_grid_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mapped O4/B4/G5/O5, page-76 non-active highlight controls, and C9/OVERDOSE slots into the current PDFs' point-coordinate systems.
  - Checked `3` PDFs, `visualTopOrigin` and `pdfBottomOrigin` coordinate modes, grids `1pt,0.5pt,0.25pt,6pt,12pt,72pt`, and tolerances `[0.05,0.12]` pt.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / active / highlight-control / OVERDOSE-slot regions: `3` / `4` / `7` / `8`.
  - Any all-four active center close <=0.05 / <=0.12 pt: `0` / `1`.
  - Any all-four active edge close <=0.05 / <=0.12 pt: `0` / `1`.
  - Best active center close count <=0.05 / <=0.12 pt: `1` / `4`.
  - Best control center close count <=0.05 / <=0.12 pt: `2` / `7`.
  - Best grid row: `analysis_outputs/external_clues/google_drive_article_download.pdf` / `pdfBottomOrigin` / `0.25pt`.
  - Grid alignment candidate / hidden PDF coordinate candidate: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|regions=4/7/8|modes=visualTop,pdfBottom|grids=1pt,0.5pt,0.25pt,6pt,12pt,72pt|allFourCenter05=0|allFourCenter12=1|allFourEdges05=0|allFourEdges12=1|bestCenter05=1|bestCenter12=4|controlBest05=2|controlBest12=7|best=analysis_outputs/external_clues/google_drive_article_download.pdf:pdfBottomOrigin:0.25pt|gridCandidate=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue current-PDF point/grid coordinates as a selector.
  - The loose 0.12pt all-four active landing on a 0.25pt grid is controlled by non-active page-76 highlights, which match that grid more strongly.
  - Frontier now records `190` focused local checks; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Current PDF Image Rect Margin Phase Gate

- Status: checked; current-PDF embedded image rectangles, trim margins, side margins, and 18pt margin units do not create a hidden active-box selector.
- Evidence:
  - `scripts/audit_current_pdf_image_rect_margin_phase_gate.py`
  - `analysis_outputs/source_audit/current_pdf_image_rect_margin_phase_gate/current_pdf_image_rect_margin_phase_gate.md`
  - `analysis_outputs/source_audit/current_pdf_image_rect_margin_phase_gate/current_pdf_image_rect_margin_phase_gate.json`
  - `analysis_outputs/source_audit/current_pdf_image_rect_margin_phase_gate/current_pdf_image_rect_margin_phase_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mapped O4/B4/G5/O5, page-76 non-active highlight controls, and C9/OVERDOSE slots into the current PDFs' embedded image rectangles.
  - Checked image-rect fractions `halves,thirds,quarters,eighths,sixteenths` and the observed 18pt side-margin units in the low-resolution duplicate PDFs.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / active / highlight-control / OVERDOSE-slot regions: `3` / `4` / `7` / `8`.
  - Any all-four active fraction close <=0.001 / <=0.0025 / <=0.005: `0` / `0` / `0`.
  - Any all-four active margin-unit close <=0.25 / <=0.5 / <=1.0 pt: `0` / `0` / `0`.
  - Best fraction active/control close <=0.005: `0` / `0`.
  - Best margin-unit active/control close <=1.0 pt: `0` / `0`.
  - Best summary row: `analysis_outputs/external_clues/google_drive_article_download.pdf` / `pdfBottomOrigin` / `sixteenths`.
  - Margin phase candidate / hidden candidate: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|regions=4/7/8|fractionRulers=halves,thirds,quarters,eighths,sixteenths|marginUnits=18.0,18.0|allFourFrac001=0|allFourFrac0025=0|allFourFrac005=0|allFourMargin025=0|allFourMargin050=0|allFourMargin100=0|bestFracActive005=0|bestFracControl005=0|bestMarginActive100=0|bestMarginControl100=0|best=analysis_outputs/external_clues/google_drive_article_download.pdf:pdfBottomOrigin:sixteenths|marginCandidate=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not pursue current-PDF image-rect or 18pt side-margin phase as a selector.
  - This pass produced 0 all-four active fraction or margin-unit landings, so it is a stronger negative than the previous loose PDF point-grid result.
  - Frontier now records `191` focused local checks and `237` closed/deferred branch bullets; best next direction remains original-layout/physical source acquisition or raw clue wording that explicitly names transform, unit, and order.

### Local PDF Filesystem Provenance Gate

- Status: checked; local filesystem provenance does not reveal a distinct original-layout source or selector.
- Evidence:
  - `scripts/audit_local_pdf_filesystem_provenance_gate.py`
  - `analysis_outputs/source_audit/local_pdf_filesystem_provenance_gate/local_pdf_filesystem_provenance_gate.md`
  - `analysis_outputs/source_audit/local_pdf_filesystem_provenance_gate/local_pdf_filesystem_provenance_gate.json`
  - `analysis_outputs/source_audit/local_pdf_filesystem_provenance_gate/local_pdf_filesystem_provenance_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected the current PDF files' local SHA-256 hashes, file timestamps, Spotlight/Finder `where-from` provenance, extended attributes, quarantine agent, and PDF document metadata.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / unique SHA-256 hashes / duplicate groups: `3` / `2` / `1`.
  - `keyser bitcoin .pdf` and `analysis_outputs/external_clues/google_drive_article_download.pdf` are byte-identical with SHA-256 prefix `0078fe23401fab48`.
  - `keyser bitcoin .pdf`: where-from `https://drive.google.com/`, quarantine agent `Brave`, PDF creator `PDF24 Tools - OCR`.
  - `analysis_outputs/external_clues/google_drive_article_download.pdf`: same PDF24 OCR content/hash, no preserved where-from metadata.
  - `magazine.pdf`: distinct SHA-256 prefix `a0714dcbe503ecdf`, where-from `PRIVATE_SOURCE_OMITTED`, quarantine agent `Brave`, no original-layout PDF creator metadata.
  - Strict instruction hits / original-layout candidate count: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|uniqueSha=2|dupGroups=1|whereFroms=magazine.pdf:PRIVATE_SOURCE_OMITTED bitcoin .pdf:https://drive.google.com/:Brave,google_drive_article_download.pdf:-:-|origCandidates=0|strict=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not treat current PDF filesystem provenance as an original-layout source or selector.
  - The local files confirm derivative provenance: two duplicate Google Drive/PDF24 OCR witnesses plus one distinct ChatGPT-sourced PDF witness.
  - Frontier now records `192` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names unit, order, or transform.

### Current Scan Page Frame / Trim Registration Gate

- Status: checked; current scan rasters do not expose a physical page-frame/trim cue that reopens held-to-light registration.
- Evidence:
  - `scripts/audit_current_scan_page_frame_trim_registration_gate.py`
  - `analysis_outputs/source_audit/current_scan_page_frame_trim_registration_gate/current_scan_page_frame_trim_registration_gate.md`
  - `analysis_outputs/source_audit/current_scan_page_frame_trim_registration_gate/current_scan_page_frame_trim_registration_gate.json`
  - `analysis_outputs/source_audit/current_scan_page_frame_trim_registration_gate/current_scan_page_frame_trim_registration_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected current source/upright page rasters for pages `75`, `76`, `78`, and `79`.
  - Measured edge profiles and edge-band non-white shares to test for a stable physical page-frame/trim line or crop/skew cue that could justify changing valid page-75 -> page-76 held-to-light registration.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Valid pair / same canvas: `75->76` / `1` (`2544x3264`).
  - Pages with all four frame-like edges: `0`.
  - Valid pair both pages all-edge frame-like: `0`.
  - Trim correction candidate / hidden trim-skew candidate: `0` / `0`.
  - Active distance rows: `4`, measured only against canvas because no reliable physical page-frame line was detected.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pages=4|pair=75->76|sameCanvas=1|allEdgesPages=0|pairAllEdges=0|trimCandidate=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not reopen held-to-light with ad hoc current-scan trim, skew, or crop correction.
  - The valid pages share the same canvas, and detected edge hits are content/margin profiles rather than a stable physical registration frame.
  - Frontier now records `193` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names unit, order, transform, or page-frame registration.

### Current Scan Content Box Registration Gate

- Status: checked; visible content-box normalization does not reopen held-to-light registration.
- Evidence:
  - `scripts/audit_current_scan_content_box_registration_gate.py`
  - `analysis_outputs/source_audit/current_scan_content_box_registration_gate/current_scan_content_box_registration_gate.md`
  - `analysis_outputs/source_audit/current_scan_content_box_registration_gate/current_scan_content_box_registration_gate.json`
  - `analysis_outputs/source_audit/current_scan_content_box_registration_gate/current_scan_content_box_registration_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured all-page and lower-half visible content envelopes on current page rasters `75`, `76`, `78`, and `79`.
  - Tested whether those envelopes create a justified mirrored page-75 -> page-76 held-to-light registration correction.
  - Applied the content-box translations to mirrored page-75 source ink and measured O4/B4/G5/O5 landing support.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Valid pair / same canvas: `75->76` / `1`.
  - All-page content shift dx,dy: `31.5,-61.0`; stable: `0`.
  - Lower-half content shift dx,dy: `32.5,-0.5`; stable: `1`, but clipped to canvas/band edges.
  - Natural / all-content / lower-half landing support: `3/4` / `2/4` / `2/4`.
  - B4 source-ink ratio remains `0.0000` under all tested modes.
  - Content-box registration candidate / hidden content-box candidate: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pages=4|pair=75->76|sameCanvas=1|allShift=31.5,-61.0|lowerShift=32.5,-0.5|allStable=0|lowerStable=1|natural=3/4:B4=0.0000|allContent=2/4:B4=0.0000|lowerContent=2/4:B4=0.0000|candidate=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not use current-scan content-box normalization as a held-to-light selector.
  - The lower-page content envelope shows a repeatable horizontal bias, but it is an edge/band-clipped raster property and does not rescue the missing B4 source-ink landing.
  - Frontier now records `194` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.

### Current Scan Source Layer Landing Gate

- Status: checked; source-layer color/ink split does not rescue valid held-to-light.
- Evidence:
  - `scripts/audit_current_scan_source_layer_landing_gate.py`
  - `analysis_outputs/source_audit/current_scan_source_layer_landing_gate/current_scan_source_layer_landing_gate.md`
  - `analysis_outputs/source_audit/current_scan_source_layer_landing_gate/current_scan_source_layer_landing_gate.json`
  - `analysis_outputs/source_audit/current_scan_source_layer_landing_gate/current_scan_source_layer_landing_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Split mirrored page-75 source material into black, orange, grey, combined feature, and broad non-white source masks.
  - Measured O4/B4/G5/O5 landing under natural, all-content-box, and lower-half content-box registration modes.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Modes / layers / active target layer rows: `3` / `5` / `60`.
  - B4 positive source-layer/mode count: `0/15`.
  - All-four supported layer/mode count: `0`; all-four weak-supported layer/mode count: `0`.
  - Best layer/mode: `natural_hflip:feature`, still only `3/4` supported.
  - Orange source material does not land on any active target in the valid leaf/content-box registrations.
  - Hidden source-layer candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `modes=3|layers=black,orange,grey,feature,broad|rows=60|b4PositiveLayerModes=0|allFour=0|allFourWeak=0|best=natural_hflip:feature:3/4|b4Ratios=natural_hflip:black:0.0000,natural_hflip:orange:0.0000,natural_hflip:grey:0.0000,natural_hflip:feature:0.0000,natural_hflip:broad:0.0000,all_content_box_translation:black:0.0000,all_content_box_translation:orange:0.0000,all_content_box_translation:grey:0.0000,all_content_box_translation:feature:0.0000,all_content_box_translation:broad:0.0000,lower_half_content_box_translation:black:0.0000,lower_half_content_box_translation:orange:0.0000,lower_half_content_box_translation:grey:0.0000,lower_half_content_box_translation:feature:0.0000,lower_half_content_box_translation:broad:0.0000|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not reopen held-to-light by swapping the source mask or color layer.
  - B4 is absent across black, orange, grey, combined feature, and broad non-white source layers, so the failure is not a dark-ink threshold artifact.
  - Frontier now records `195` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.

### Current Scan Source Layer Miss-Distance Gate

- Status: checked; B4 is not a tiny crop/threshold miss in the current held-to-light registrations.
- Evidence:
  - `scripts/audit_current_scan_source_layer_miss_distance_gate.py`
  - `analysis_outputs/source_audit/current_scan_source_layer_miss_distance_gate/current_scan_source_layer_miss_distance_gate.md`
  - `analysis_outputs/source_audit/current_scan_source_layer_miss_distance_gate/current_scan_source_layer_miss_distance_gate.json`
  - `analysis_outputs/source_audit/current_scan_source_layer_miss_distance_gate/current_scan_source_layer_miss_distance_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured nearest source-layer pixels outside O4/B4/G5/O5 under natural, all-content-box, and lower-half content-box registrations.
  - Used black, orange, grey, combined feature, and broad non-white masks plus line-shift controls.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Modes / layers / active distance rows / control distance rows: `3` / `5` / `60` / `360`.
  - B4 minimum expansion any / feature / broad: `22px` / `136px` / `22px`.
  - B4 tiny-miss candidate at `<=16px`: `0`.
  - All-four within-expansion layer/mode counts: `<=4px:0`, `<=8px:0`, `<=16px:0`, `<=32px:1`, `<=64px:1`, `<=128px:3`.
  - Best all-four expansion is `all_content_box_translation:broad:22px`; this is broad/non-white contact, not feature/ink support.
  - Feature-mask B4 distances are still large: natural `136px`, all-content `202px`, lower-half `160px`.
  - Hidden miss-distance candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `modes=3|layers=black,orange,grey,feature,broad|rows=60|controls=360|b4MinAny=22|b4MinFeature=136|b4MinBroad=22|b4Tiny=0|allFourWithin16=0|bestAllFour=all_content_box_translation:broad:22px|b4=natural_hflip:black:136,natural_hflip:orange:288,natural_hflip:grey:136,natural_hflip:feature:136,natural_hflip:broad:67,all_content_box_translation:black:203,all_content_box_translation:orange:>260,all_content_box_translation:grey:202,all_content_box_translation:feature:202,all_content_box_translation:broad:22,lower_half_content_box_translation:black:161,lower_half_content_box_translation:orange:>260,lower_half_content_box_translation:grey:160,lower_half_content_box_translation:feature:160,lower_half_content_box_translation:broad:71|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not reopen held-to-light by treating B4 as a small crop/threshold miss.
  - The nearest B4 rescue is broad/non-white all-content contact at `22px`, outside the tiny-miss band and unsupported by source-backed R3.
  - Frontier now records `196` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.
  - If continuing with the current scan only, next trace the `all_content_box_translation:broad:22px` B4 contact back to source components/words as a provenance check, not a key-candidate path.

### Current Scan B4 Broad-Contact Provenance Gate

- Status: checked; the only near B4 broad-mask rescue is scan/halo/margin noise, not source text.
- Evidence:
  - `scripts/audit_current_scan_b4_broad_contact_provenance_gate.py`
  - `analysis_outputs/source_audit/current_scan_b4_broad_contact_provenance_gate/current_scan_b4_broad_contact_provenance_gate.md`
  - `analysis_outputs/source_audit/current_scan_b4_broad_contact_provenance_gate/current_scan_b4_broad_contact_provenance_gate.json`
  - `analysis_outputs/source_audit/current_scan_b4_broad_contact_provenance_gate/current_scan_b4_broad_contact_provenance_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Traced the nearest `all_content_box_translation:broad` B4 contact back through the page-75 mirror transform.
  - Checked pixel class/RGB, mapped page-75 source location, OCR word proximity, and source-side strict/context terms.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - B4 broad nearest distance / minimal expansion / first pixel expansion: `21.84px` / `22px` / `32px`.
  - Radius `32px` contact: `1` broad pixel, `0` feature pixels, `1` broad-only pixel, `1` component.
  - Nearest target point -> mapped source point: `[711, 2450]` -> `[1864, 2511]`.
  - Target/source point RGB: `[242,242,242]` / `[242,242,242]`; this is broad only, not black/orange/grey/feature.
  - Source words within `64/128/256px`: `0/0/4`.
  - Nearest page-75 OCR word: `lab.` at `249.047px`; nearest strict instruction word: `words` at `913.859px`.
  - Strict/context hits in traced contact contexts: `0` / `0`.
  - Hidden broad-contact candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `mode=all_content_box_translation|target=B4|layer=broad|b4BroadMin=22|firstExpansion=32|r32BroadPx=1|r32FeaturePx=0|r32BroadOnlyPx=1|r32Components=1|pointLayers=broad|sourceWords64=0|sourceWords128=0|nearestWord=249.047:lab|nearestStrict=913.859:words|strict=0|context=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not reopen held-to-light from the all-content broad B4 contact.
  - The contact is a single off-white broad-mask pixel with no nearby source text or instruction wording.
  - Frontier now records `197` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.

### Current PDF B4 Contact Pixel Provenance Gate

- Status: checked; the exact B4 broad-contact pixel is a PDF carrier/provenance warning, not a selector.
- Evidence:
  - `scripts/audit_current_pdf_b4_contact_pixel_provenance_gate.py`
  - `analysis_outputs/source_audit/current_pdf_b4_contact_pixel_provenance_gate/current_pdf_b4_contact_pixel_provenance_gate.md`
  - `analysis_outputs/source_audit/current_pdf_b4_contact_pixel_provenance_gate/current_pdf_b4_contact_pixel_provenance_gate.json`
  - `analysis_outputs/source_audit/current_pdf_b4_contact_pixel_provenance_gate/current_pdf_b4_contact_pixel_provenance_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Sampled source point `[1864,2511]` and target point `[711,2450]` across embedded page images and 300dpi renders from the current PDF carriers.
  - Rebuilt the all-content page-75 -> page-76 B4 landing for the same broad-contact point.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / candidate rows: `3` / `6`.
  - Source point broad / feature candidates: `6` / `4`; landing point broad / feature candidates: `6` / `4`.
  - Radius-32 feature-contact candidates: `4`; render-only feature/contact candidates: `2`.
  - The byte-locked `magazine.pdf` embedded/render carrier keeps the point broad/background only with source/landing RGB `[243,243,243]`, radius-32 broad `1`, and feature `0`.
  - The feature-colored rows come from duplicate/lower-resolution carriers (`keyser bitcoin .pdf` and the Google Drive article download), not from the byte-locked current scan carrier.
  - Hidden PDF render contact candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|candidates=6|srcBroad=6|srcFeature=4|landBroad=6|landFeature=4|r32Feature=4|magEmbRgb=[243, 243, 243]|baseRgb=[242, 242, 242]|renderOnlyFeature=2|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not reopen current-PDF rendering for the B4 broad rescue.
  - Treat duplicate/lower-resolution feature-colored contacts as provenance warnings, not extraction evidence.
  - Frontier now records `198` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.

### Current PDF Duplicate-Background Feature Artifact Gate

- Status: checked; duplicate-PDF feature-looking B4 contact is controlled as a resampling artifact.
- Evidence:
  - `scripts/audit_current_pdf_duplicate_background_feature_artifact_gate.py`
  - `analysis_outputs/source_audit/current_pdf_duplicate_background_feature_artifact_gate/current_pdf_duplicate_background_feature_artifact_gate.md`
  - `analysis_outputs/source_audit/current_pdf_duplicate_background_feature_artifact_gate/current_pdf_duplicate_background_feature_artifact_gate.json`
  - `analysis_outputs/source_audit/current_pdf_duplicate_background_feature_artifact_gate/current_pdf_duplicate_background_feature_artifact_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested whether lower-resolution duplicate PDF carriers uniquely create the B4 feature-looking contact, or whether matched off-white broad-only background controls convert the same way.
  - Sampled the B4 source point `[1864,2511]`, local controls, and page-grid controls on page 75.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - B4 duplicate feature rows / magazine feature rows: `4/4` / `0/2`.
  - Local matched background controls any/all duplicate feature: `44/54` / `40/54`.
  - Page-grid matched background controls any/all duplicate feature: `48/57` / `39/57`.
  - Controls matching or exceeding B4's duplicate feature-row count, local/page-grid: `40` / `39`.
  - Hidden duplicate-PDF feature candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `local=54|localAny=44|localAll=40|page=57|pageAny=48|pageAll=39|b4DupFeature=4/4|b4MagFeature=0/2|localAtLeastB4=40|pageAtLeastB4=39|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not treat duplicate-PDF feature-colored B4 contact as source ink.
  - The duplicate carriers convert many ordinary off-white background pixels to feature, so B4 is not unique there.
  - Frontier now records `199` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.

### Current PDF Page-76 Carrier-State Stability Gate

- Status: checked; page-76 duplicate-PDF carrier changes are controlled provenance artifacts, not selectors.
- Evidence:
  - `scripts/audit_current_pdf_page76_carrier_state_stability_gate.py`
  - `analysis_outputs/source_audit/current_pdf_page76_carrier_state_stability_gate/current_pdf_page76_carrier_state_stability_gate.md`
  - `analysis_outputs/source_audit/current_pdf_page76_carrier_state_stability_gate/current_pdf_page76_carrier_state_stability_gate.json`
  - `analysis_outputs/source_audit/current_pdf_page76_carrier_state_stability_gate/current_pdf_page76_carrier_state_stability_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared byte-locked `magazine.pdf` embedded/render carriers against duplicate/lower-resolution PDF carriers across O4/B4/G5/O5, eight OVERDOSE slot boxes, and sixteen matched line-shift controls.
  - Checked source/render provenance and carrier-state stability only.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Carriers total / byte-locked magazine / duplicate: `6` / `2` / `4`.
  - Active target / OVERDOSE slot / control regions: `4` / `8` / `16`.
  - Active duplicate presence-mismatch rows: `10`; OVERDOSE slot duplicate presence-mismatch rows: `32`.
  - Active / slot outliers above matched line-shift control p95: `0` / `0`.
  - All-four active outlier: `0`.
  - Control p95 max-layer delta: `0.999855`.
  - Max active / slot duplicate layer delta: `0.989695` / `0.984838`.
  - Active states: O4 `orange->grey`, B4 `black->black`, G5 `black->grey`, O5 `orange->grey`.
  - Every OVERDOSE slot has four duplicate mismatch rows, but none are outliers above the line-shift control p95.
  - Hidden page-76 duplicate carrier candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `carriers=6|active=4|slots=8|controls=16|activeMismatchRows=10|slotMismatchRows=32|activeOutliers=0|slotOutliers=0|controlP95=0.999855|all4ActiveOutlier=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not use duplicate/current-PDF carrier differences as a page-76 selector.
  - The duplicate PDFs shift visible states, but those shifts are not unique against matched controls and do not supply a source-backed unit/order rule.
  - Frontier now records `200` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.

### Current PDF All-Leaf Imposition Consistency Gate

- Status: checked; current PDFs do not expose an original-layout/imposition cue across article leaf pairs.
- Evidence:
  - `scripts/audit_current_pdf_all_leaf_imposition_consistency_gate.py`
  - `analysis_outputs/source_audit/current_pdf_all_leaf_imposition_consistency_gate/current_pdf_all_leaf_imposition_consistency_gate.md`
  - `analysis_outputs/source_audit/current_pdf_all_leaf_imposition_consistency_gate/current_pdf_all_leaf_imposition_consistency_gate.json`
  - `analysis_outputs/source_audit/current_pdf_all_leaf_imposition_consistency_gate/current_pdf_all_leaf_imposition_consistency_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected page boxes, rotation, embedded image placement, scale, and hidden-layer indicators across article leaf pairs `75/76`, `77/78`, and `79/80` in the current PDFs.
  - Checked original-layout/imposition provenance only.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs / inspected page records / leaf pairs: `3` / `18` / `9`.
  - Identical front/back pair geometry: `9/9`.
  - PDFs with uniform page geometry across pages 75-80: `3/3`.
  - Unique geometry families: `2`: full-bleed `magazine.pdf` and the two inset duplicate PDF24 derivatives.
  - Side-margin pairs: `6`, all from the duplicate PDFs and all global across the inspected leaves.
  - Placement-offset pairs / hidden pair-layer candidates: `0` / `0`.
  - All-leaf imposition candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|pages=18|leafPairs=9|pairPass=9|withinPdfUniform=3|geometryFamilies=2|sideMarginPairs=6|placementOffsetPairs=0|hiddenPairLayers=0|impositionCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not use current-PDF all-leaf page-pair/imposition differences as a held-to-light selector.
  - The PDF layout is uniform within each carrier; duplicate side margins are derivative-layout artifacts.
  - Frontier now records `201` focused local checks; best next direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.

### Current Scan All-Leaf Light-Table Parity Gate

- Status: checked; natural all-leaf held-to-light parity in the current scan does not make page 76 or OVERDOSE a selector.
- Evidence:
  - `scripts/audit_current_scan_all_leaf_light_table_parity_gate.py`
  - `analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/current_scan_all_leaf_light_table_parity_gate.md`
  - `analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/current_scan_all_leaf_light_table_parity_gate.json`
  - `analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/current_scan_all_leaf_light_table_parity_gate_sheet.jpg`
  - Natural overlay panels:
    - `analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/valid_75_to_76_natural_light_table_overlay.jpg`
    - `analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/valid_77_to_78_natural_light_table_overlay.jpg`
    - `analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/valid_79_to_80_natural_light_table_overlay.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Normalized current-scan/source pages 75-80 to readable/upright coordinates and tested only the natural odd-page mirror over even-page leaf pairs `75->76`, `77->78`, and `79->80`.
  - Measured O4/B4/G5/O5 same-coordinate boxes, matched line-shift controls, and C9/OVERDOSE slot columns.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Valid leaf pairs / active rows / line-shift controls / OVERDOSE slot rows: `3` / `12` / `72` / `24`.
  - Page-76 active ink / feature outliers: `0` / `0`.
  - All-four page-76 active ink / feature outlier: `0` / `0`.
  - Page-76 OVERDOSE slot ink / feature outliers: `0` / `0`.
  - Hidden all-leaf light-table candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Page-76 active source-ink ratios: O4 `0.140212`, B4 `0.000000`, G5 `0.059643`, O5 `0.194042`; all are below neighboring same-coordinate and line-shift control ceilings.
  - Fingerprint: `pairs=3|activeRows=12|slots=24|controls=72|p76ActiveInkOutliers=0|p76ActiveFeatureOutliers=0|all4Ink=0|all4Feature=0|slotInkOutliers=0|slotFeatureOutliers=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not treat the current scan's held-to-light construction as extraction-ready.
  - The best direction remains physical/original-layout source validation or raw clue wording that names the missing unit/order/transform.
  - Frontier now records `202` focused local checks.

### Current Scan Light-Table Density Calibration Gate

- Status: checked; density-normalizing the natural leaf overlays still does not promote page 76 or OVERDOSE into a selector.
- Evidence:
  - `scripts/audit_current_scan_light_table_density_calibration_gate.py`
  - `analysis_outputs/source_audit/current_scan_light_table_density_calibration_gate/current_scan_light_table_density_calibration_gate.md`
  - `analysis_outputs/source_audit/current_scan_light_table_density_calibration_gate/current_scan_light_table_density_calibration_gate.json`
  - `analysis_outputs/source_audit/current_scan_light_table_density_calibration_gate/current_scan_light_table_density_calibration_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Normalized natural valid leaf pairs `75->76`, `77->78`, and `79->80` against full-page, active-band, C9-frame, and matched line-control source density.
  - Measured O4/B4/G5/O5 active boxes, matched line-shift controls, and C9/OVERDOSE slot rows.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Valid leaf pairs / active rows / line-shift controls / OVERDOSE slot rows: `3` / `12` / `72` / `24`.
  - Page-76 normalized active ink / feature outliers: `0` / `0`.
  - All-four page-76 normalized active ink / feature outlier: `0` / `0`.
  - Page-76 normalized OVERDOSE slot ink outliers: `3`.
  - Hidden density-calibrated candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - The strongest page-76 active normalized ink ratios are O4 `1.491261` and O5 `2.063778`, but matched line-control p95 thresholds still absorb them; B4 remains `0.000000`.
  - Fingerprint: `pairs=3|active=12|controls=72|slots=24|p76NormInkOutliers=0|p76NormFeatureOutliers=0|all4NormInk=0|all4NormFeature=0|slotNormInkOutliers=3|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Treat the 3 normalized OVERDOSE slot ink outliers as slot-density artifacts, not extraction permission.
  - The active quartet is still not all-four supported after density calibration, and no source-backed unit/order rule appears.
  - Frontier now records `203` focused local checks.

### Current Scan OVERDOSE Density-Outlier Provenance Gate

- Status: checked; the three density-normalized OVERDOSE slot outliers trace to partial highlight/source-density bleed-through, not a selector.
- Evidence:
  - `scripts/audit_current_scan_overdose_density_outlier_provenance_gate.py`
  - `analysis_outputs/source_audit/current_scan_overdose_density_outlier_provenance_gate/current_scan_overdose_density_outlier_provenance_gate.md`
  - `analysis_outputs/source_audit/current_scan_overdose_density_outlier_provenance_gate/current_scan_overdose_density_outlier_provenance_gate.json`
  - `analysis_outputs/source_audit/current_scan_overdose_density_outlier_provenance_gate/current_scan_overdose_density_outlier_provenance_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Traced page-76 density outlier slot columns against active target contact, mirrored page-75 source words/highlights, page-76 target words/highlights, and strict instruction terms.
  - Used the current scan/PDF source images and existing 3D article-map OCR/highlight geometry only.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Slot columns checked / page-76 density outlier slots: `8` / `3`.
  - Outlier slots / letters in x-order: `slot_3_R`, `slot_5_O`, `slot_6_S` / `ROS`.
  - Outlier letters by ink strength: `SOR`.
  - Longest contiguous outlier run: `2`.
  - Outlier active contacts: `G5,O4,O5` (`3/4`); B4 contact is `0`.
  - Outlier strict instruction hits: `0`.
  - Outlier target/source highlight ids: `p76_orange_4,p76_orange_5` / `p75_orange_6,p75_orange_7,p75_orange_8`.
  - Hidden outlier provenance candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `slots=8|outliers=3|letters=ROS|byInk=SOR|contiguousRun=2|activeContacts=3/4|B4=0|instr=0|targetHighlights=2|sourceHighlights=3|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not tune the density threshold to promote `ROS` or `SOR`.
  - The outlier slots miss B4, do not form a complete OVERDOSE run, and contain no source-backed unit/order instruction.
  - Frontier now records `204` focused local checks.

### Current Scan OVERDOSE Density Highlight-Ablation Gate

- Status: checked; source-highlight ablation weakens the OVERDOSE slot-density signal but does not produce a stable selector.
- Evidence:
  - `scripts/audit_current_scan_overdose_density_highlight_ablation_gate.py`
  - `analysis_outputs/source_audit/current_scan_overdose_density_highlight_ablation_gate/current_scan_overdose_density_highlight_ablation_gate.md`
  - `analysis_outputs/source_audit/current_scan_overdose_density_highlight_ablation_gate/current_scan_overdose_density_highlight_ablation_gate.json`
  - `analysis_outputs/source_audit/current_scan_overdose_density_highlight_ablation_gate/current_scan_overdose_density_highlight_ablation_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Removed mirrored page-75 source-highlight rectangles `p75_orange_6`, `p75_orange_7`, and `p75_orange_8` from the natural `75->76` source mask, then remeasured the eight C9/OVERDOSE slot columns.
  - Compared baseline slot density, outlier-highlight ablation, all-highlight ablation, and non-outlier-highlight control ablation.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Slot columns checked: `8`.
  - Baseline outlier slots / letters: `slot_3_R`, `slot_5_O`, `slot_6_S` / `ROS`.
  - Ablated mirrored source highlight ids: `p75_orange_6,p75_orange_7,p75_orange_8`.
  - Outlier survivors after outlier-highlight ablation: `2/3`; surviving letters: `OS`.
  - Outlier survivors after all-highlight ablation: `2/3`.
  - Mean outlier drop after outlier-highlight ablation: `30.373%`.
  - Non-outlier highlight-control status flips: `0`.
  - `slot_3_R` drops below the other-leaf max, but `slot_5_O` and `slot_6_S` remain above it.
  - Hidden highlight-ablation candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `slots=8|baselineOutliers=3|letters=ROS|outlierHighlightIds=p75_orange_6,p75_orange_7,p75_orange_8|surviveOutlierAblation=2|surviveLetters=OS|surviveAllAblation=2|meanDropPct=30.4|nonOutlierControlFlips=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not promote `ROS`, `SOR`, or post-ablation `OS`.
  - The signal is partly highlight-dependent, still partial, still misses B4/all-four support, and still lacks source-backed unit/order wording.
  - Frontier now records `205` focused local checks.

### Current Scan Active Source-Highlight Ablation Gate

- Status: checked; removing mirrored page-75 source highlights does not change active target support and does not rescue B4/all-four support.
- Evidence:
  - `scripts/audit_current_scan_active_source_highlight_ablation_gate.py`
  - `analysis_outputs/source_audit/current_scan_active_source_highlight_ablation_gate/current_scan_active_source_highlight_ablation_gate.md`
  - `analysis_outputs/source_audit/current_scan_active_source_highlight_ablation_gate/current_scan_active_source_highlight_ablation_gate.json`
  - `analysis_outputs/source_audit/current_scan_active_source_highlight_ablation_gate/current_scan_active_source_highlight_ablation_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Removed all mirrored page-75 source-highlight rectangles from the natural `75->76` held-to-light source mask.
  - Remeasured active targets O4/B4/G5/O5 and 24 matched line-shift controls using the current scan/PDF-derived images.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active targets checked: `4`.
  - Baseline positive targets: `O4,G5,O5`.
  - Positive targets after all source-highlight ablation: `O4,G5,O5`.
  - All-four active positive before/after ablation: `0` / `0`.
  - B4 source ink before/after ablation: `0.000000` / `0.000000`.
  - Mean/max active source-ink drop after ablation: `0.000%` / `0.000%`.
  - Control positives before/after ablation: `13` / `12` of `24`.
  - No active target had an overlapping mirrored page-75 source highlight.
  - Hidden active highlight-ablation candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `targets=4|baselinePositive=O4,G5,O5|afterAllPositive=O4,G5,O5|B4Base=0.000000|B4After=0.000000|meanDropPct=0.0|maxDropPct=0.0|controlsPositive=13->12|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not use source-highlight removal as an active selector.
  - O4/G5/O5 remain positive, B4 remains zero, all-four support remains false, and source-backed R3 remains absent.
  - Frontier now records `206` focused local checks.

### Current Scan Physical Bleed-Through Correlation Gate

- Status: checked; the current scan/PDF-derived page images do not contain a selective real physical bleed-through signal.
- Evidence:
  - `scripts/audit_current_scan_physical_bleedthrough_correlation_gate.py`
  - `analysis_outputs/source_audit/current_scan_physical_bleedthrough_correlation_gate/current_scan_physical_bleedthrough_correlation_gate.md`
  - `analysis_outputs/source_audit/current_scan_physical_bleedthrough_correlation_gate/current_scan_physical_bleedthrough_correlation_gate.json`
  - `analysis_outputs/source_audit/current_scan_physical_bleedthrough_correlation_gate/current_scan_physical_bleedthrough_correlation_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested fixed valid leaf pairs `75->76`, `77->78`, and `79->80` against 27 invalid source-page controls.
  - Compared mirrored source-page darkness with target-page darkness in low-ink/background regions.
  - Remeasured the page-76 O4/B4/G5/O5 active boxes and a padded active envelope as scan-translucency witnesses.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Valid leaf pairs / invalid control pairs: `3` / `27`.
  - Valid pairs above same-target invalid-control p95: `0/3`.
  - Page `75->76` darkness delta / invalid-control p95: `0.707301` / `0.961401`.
  - Page-76 active boxes above invalid-source p95: `0/4`.
  - Page-76 active boxes with enough source-signal pixels: `0/4`.
  - Active source-signal pixels: O4 `113`, B4 `0`, G5 `108`, O5 `107`.
  - Padded active-envelope darkness delta: `-0.454619`.
  - Hidden physical bleed-through candidate: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pairs=30|valid=3|controls=27|validAboveP95=0|page76Delta=0.707301|page76P95=0.961401|activeAbove=0/4|activeEnoughSignal=0/4|validMedian=0.7073|controlMedian=0.3803|validMax=0.9485|controlMax=3.3639|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not treat the current page images as an already-translucent physical source.
  - The valid leaf pairs do not separate from invalid controls, page 76 does not show selective active-box bleed-through, and B4 remains unsupported.
  - Frontier now records `207` focused local checks.

### Current Scan Active Quartet Fingerprint Specificity Gate

- Status: checked; the full active row-box fingerprint is specific to O4/B4/G5/O5 among available current-scan page-76 highlight/annotation controls, but it remains registration evidence only.
- Evidence:
  - `scripts/audit_current_scan_active_quartet_fingerprint_specificity_gate.py`
  - `analysis_outputs/source_audit/current_scan_active_quartet_fingerprint_specificity_gate/current_scan_active_quartet_fingerprint_specificity_gate.md`
  - `analysis_outputs/source_audit/current_scan_active_quartet_fingerprint_specificity_gate/current_scan_active_quartet_fingerprint_specificity_gate.json`
  - `analysis_outputs/source_audit/current_scan_active_quartet_fingerprint_specificity_gate/current_scan_active_quartet_fingerprint_specificity_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Combined active-index boxes with page-76 annotated color rows and visual-orange rows from the current scan/PDF highlight audit.
  - Checked all top-to-bottom quartets for `YKKY`, `OBBO`, fitted line gaps `3/2/5`, and C9 center-slot stream `OVED`.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Candidate rows after duplicate collapse: `13`.
  - Quartets checked: `715`.
  - YKKY/OBBO hits: `54`.
  - YKKY/OBBO/line-gap `3/2/5` hits: `2`.
  - Slot-stream `OVED` hits: `4`.
  - Combined fingerprint hits: `1`.
  - Non-active combined hits: `0`.
  - The exact combined hit is `O4 | B4 | G5 | O5`.
  - The closest non-exact row set keeps state/color/line gaps but fails slot stream: `O4 | annotated_14_grey | G5 | O5` -> `OEED`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `candidates=13|quartets=715|YKKYOBBO=54|gap325=2|slotOVED=4|combined=1|nonActiveCombined=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Keep `YKKY/OBBO/3-2-5/OVED` as a source-validation/registration fingerprint.
  - Do not use it as extraction permission without raw clue/source wording that supplies the missing unit, order, transform, or read direction.
  - Frontier now records `208` focused local checks.

### Current Scan Target Witness-Box Substitution Gate

- Status: checked; the active geometry fingerprint depends on the exact active-index/visual-duplicate boxes, not broad annotation boxes.
- Evidence:
  - `scripts/audit_current_scan_target_witness_box_substitution_gate.py`
  - `analysis_outputs/source_audit/current_scan_target_witness_box_substitution_gate/current_scan_target_witness_box_substitution_gate.md`
  - `analysis_outputs/source_audit/current_scan_target_witness_box_substitution_gate/current_scan_target_witness_box_substitution_gate.json`
  - `analysis_outputs/source_audit/current_scan_target_witness_box_substitution_gate/current_scan_target_witness_box_substitution_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Swapped all available current-scan/PDF witness boxes for O4/B4/G5/O5 target phrases.
  - Compared active-index boxes, visual-orange duplicates, and annotated color boxes for the same target phrases.
  - Checked each same-target geometry variant for `YKKY`, `OBBO`, fitted line gaps `3/2/5`, and C9 center-slot stream `OVED`.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Per-target geometry options: `O4:2, B4:2, G5:2, O5:1`.
  - Same-target geometry variants checked: `8`.
  - Line-gap `3/2/5` hits: `2`.
  - Slot-stream `OVED` hits: `1`.
  - Combined fingerprint hits: `1`.
  - Combined hits using substituted/non-exact boxes: `0`.
  - The only combined hit uses exact active-index boxes, with O4/O5 also duplicated by visual-orange rows.
  - B4's broad annotation substitution preserves the line-gap pattern in one variant but changes `OVED` to `OEED`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `options=O4:2,B4:2,G5:2,O5:1|variants=8|line325=2|slotOVED=1|lineAndSlot=1|combined=1|subCombined=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Use exact active-index boxes plus exact visual-orange duplicates as future source-validation geometry.
  - Treat broad annotation boxes as text/context witnesses only.
  - No alternate read path or extraction selector is created by witness-box substitution.
  - Frontier now records `209` focused local checks.

### Current Scan Page-76 Image Witness State-Stability Gate

- Status: checked; the exact local page-76 image witnesses are stable raster duplicates and do not add a new source layer.
- Evidence:
  - `scripts/audit_current_scan_page76_image_witness_state_stability_gate.py`
  - `analysis_outputs/source_audit/current_scan_page76_image_witness_state_stability_gate/current_scan_page76_image_witness_state_stability_gate.md`
  - `analysis_outputs/source_audit/current_scan_page76_image_witness_state_stability_gate/current_scan_page76_image_witness_state_stability_gate.json`
  - `analysis_outputs/source_audit/current_scan_page76_image_witness_state_stability_gate/current_scan_page76_image_witness_state_stability_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Scanned root full-page images plus `analysis_outputs/source_images` and `analysis_outputs/3d_article_map` upright page images.
  - Identified page-76 witnesses by sample image similarity against the upright page-76 reference, testing normal and 180-degree-rotated orientation.
  - Remeasured exact O4/B4/G5/O5 active boxes for visual state, color stream, and C9 slot stream.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Full-page image candidates checked: `26`.
  - Exact page-76 witnesses: `3`.
  - Exact witnesses: `analysis_outputs/3d_article_map/page_76_upright.jpg`, `analysis_outputs/source_images/magazine_page_76.jpg`, `magazine-4_1.jpg`.
  - Stable exact witnesses: `3/3`.
  - Near page-76 controls: `9`.
  - Hidden changed-state witness candidates: `0`.
  - Exact witness max active-crop mean absolute difference: `6.455416`.
  - Exact witnesses preserve `YKKY` / `OBBO` / `OVED`.
  - Near controls do not preserve the active state/color stream.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `images=26|exact=3|stableExact=3|near=9|hiddenChanged=0|exactMaxDiff=6.455|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Treat local page-76 image witnesses as duplicate raster validation only.
  - No local image witness changes active-box state, creates alternate geometry, or unlocks extraction.
  - Frontier now records `210` focused local checks.

### Current Scan Page-76 Image Witness Micro-Registration Gate

- Status: checked; exact page-76 image witnesses have no active-box local registration drift.
- Evidence:
  - `scripts/audit_current_scan_page76_image_witness_microregistration_gate.py`
  - `analysis_outputs/source_audit/current_scan_page76_image_witness_microregistration_gate/current_scan_page76_image_witness_microregistration_gate.md`
  - `analysis_outputs/source_audit/current_scan_page76_image_witness_microregistration_gate/current_scan_page76_image_witness_microregistration_gate.json`
  - `analysis_outputs/source_audit/current_scan_page76_image_witness_microregistration_gate/current_scan_page76_image_witness_microregistration_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used the three exact page-76 witnesses from the prior image witness stability report.
  - Searched `+/-8px` around each exact O4/B4/G5/O5 box.
  - Compared zero-shift crops to best local shifted crops using mean absolute RGB difference.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Exact page-76 witnesses checked: `3`.
  - Active target shift rows checked: `12`.
  - Search radius: `+/-8px`.
  - Nonzero best shifts: `0`.
  - Max absolute best shift: `0px`.
  - Max zero-shift mean absolute difference: `6.455416`.
  - Max zero-to-best improvement: `0.0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `witnesses=3|targets=12|radius=8|nonZeroShift=0|maxAbsShift=0|maxZeroDiff=6.455|maxImprove=0.000|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Treat the exact page-76 witnesses as aligned duplicate rasters.
  - Remaining crop differences are raster/JPEG differences, not active-box geometry drift.
  - No hidden registration layer, alternate selector, or extraction path is created.
  - Frontier now records `211` focused local checks.

### Current Scan Active-Box OVERDOSE Edge-Residue Gate

- Status: checked; active-box edge/center residue against the C9/OVERDOSE slot ruler is not an extraction selector.
- Evidence:
  - `scripts/audit_current_scan_active_box_overdose_edge_residue_gate.py`
  - `analysis_outputs/source_audit/current_scan_active_box_overdose_edge_residue_gate/current_scan_active_box_overdose_edge_residue_gate.md`
  - `analysis_outputs/source_audit/current_scan_active_box_overdose_edge_residue_gate/current_scan_active_box_overdose_edge_residue_gate.json`
  - `analysis_outputs/source_audit/current_scan_active_box_overdose_edge_residue_gate/current_scan_active_box_overdose_edge_residue_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Reused the locked O4/B4/G5/O5 active boxes and the same eight current-scan/PDF witness-box variants from the target witness substitution gate.
  - Compared each box left edge, center, and right edge against C9/OVERDOSE slot centers and boundaries.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Witness variants checked: `8`.
  - Exact active nearest-center streams left/center/right: `DOER` / `OVED` / `SVRO`.
  - Exact active close rows any-anchor / left-boundary / center-slot / right-boundary at `<=16px`: `3/2/0/0`.
  - Variants with all-four any-anchor closeness: `1`.
  - All-four any-anchor close variants using substituted boxes: `1`.
  - Best mean nearest-residue variant is ordinal `5` at `27.08px`, and it uses substituted annotated O4.
  - Exact active mean nearest residue is `31.916667px`; exact active mean center residue is `76.625px`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `variants=8|exactCenter=OVED|exactEdges=DOER/SVRO|exactClose=3/2/0/0|allFourAny=1|subAllFourAny=1|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The exact active centers still repeat the known `OVED` signal, but the exact box edges do not add a repeatable all-four residue rule.
  - Edge closeness is not exact-active-specific because a substituted annotation variant is better on the residue metric.
  - Do not tune C9 edge/center residue further without a new source or raw clue that names the missing unit/order/transform.
  - Frontier now records `212` focused local checks.

### Current Scan Held-To-Light Component Readability Gate

- Status: checked; current-scan held-to-light source residue does not produce readable hidden target text.
- Evidence:
  - `scripts/audit_current_scan_held_to_light_component_readability_gate.py`
  - `analysis_outputs/source_audit/current_scan_held_to_light_component_readability_gate/current_scan_held_to_light_component_readability_gate.md`
  - `analysis_outputs/source_audit/current_scan_held_to_light_component_readability_gate/current_scan_held_to_light_component_readability_gate.json`
  - `analysis_outputs/source_audit/current_scan_held_to_light_component_readability_gate/current_scan_held_to_light_component_readability_gate_sheet.jpg`
  - Per-target component panels in `analysis_outputs/source_audit/current_scan_held_to_light_component_readability_gate/`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Simulated page 75 held behind page 76 under three same-leaf registrations: natural valid leaf, small-jitter best control, and forced crop-light-table guardrail.
  - Limited inspection to the active `O4`, `B4`, `G5`, and `O5` boxes.
  - Counted source-only components, letterlike components, mapped source words, strict instruction terms, and context terms.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Modes checked: `3`.
  - Target rows checked: `12`.
  - Natural valid-leaf readable rows: `0`.
  - Forced/control readable rows: `2`.
  - All-four readable modes: `0`.
  - Strict instruction rows / source-word rows / context-term rows: `0/0/0`.
  - Hidden readability candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `modes=3|rows=12|naturalReadable=0|forcedReadable=2|allFourReadable=0|strictRows=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The physically natural held-to-light view has no readable target rows.
  - Partial readability appears only in forced/control placements, not across all four active boxes, and has no source words or instruction terms.
  - Do not continue tuning held-to-light readability on the current scan unless a new physical/original-layout source or raw clue changes the alignment model.
  - Frontier now records `213` focused local checks.

### Current Source Arrival Refresh Gate

- Status: checked; no new local source/clue arrival currently reopens R1-R5 review.
- Evidence:
  - `scripts/audit_current_source_arrival_refresh_gate.py`
  - `analysis_outputs/source_audit/current_source_arrival_refresh_gate/current_source_arrival_refresh_gate.md`
  - `analysis_outputs/source_audit/current_source_arrival_refresh_gate/current_source_arrival_refresh_gate.json`
  - `analysis_outputs/source_audit/current_source_arrival_refresh_gate/current_source_arrival_refresh_gate_sheet.jpg`
- Scope:
  - Scanned Desktop, Downloads, and Documents for recent source-like files across a `72` hour window.
  - Compared results against known/prior source paths from the local source delta and post-unlock arrival watches.
  - Used only metadata/path/name checks; no OCR, extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Records considered: `12`.
  - Candidate review needed: `0`.
  - Low-priority recent/named files: `2`.
  - Known recent/named files: `10`.
  - Low-priority matches were generic/non-puzzle-specific path/name hits: `private_inputs/Documents/oftalmosalud/data/sources.md` and `private_inputs/Downloads/Adobe Scan Sep 6, 2023 (1).pdf`.
  - Source-backed R3 hits / selector unlocks: `0` / `0`.
  - Fingerprint: `lookbackH=72|records=12|review=0|low=2|known=10|sourceR3=0|selectors=0`.
- Conclusion:
  - No new physical/original-layout/source/raw-clue item is available locally to reopen extraction.
  - Current-scan/PDF evidence remains blocked until a promoted source or raw clue supplies R3 unit/order evidence.

### Current PDF OCR Document-Order Gate

- Status: checked; invisible PDF OCR document order does not supply an active target selector.
- Evidence:
  - `scripts/audit_current_pdf_ocr_document_order_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ocr_document_order_gate/current_pdf_ocr_document_order_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ocr_document_order_gate/current_pdf_ocr_document_order_gate.json`
  - `analysis_outputs/source_audit/current_pdf_ocr_document_order_gate/current_pdf_ocr_document_order_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected the current PDFs' invisible OCR word order on page 76.
  - Mapped O4/B4/G5/O5 into PDF image rectangles and recorded OCR words inside each active box.
  - Compared first target-component occurrence order against active order and checked for strict unit/order terms near the active boxes.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - PDFs with all four active boxes populated by OCR words: `0`.
  - PDFs with all four active component targets present somewhere in OCR order: `2`.
  - PDFs whose first component occurrences match active order: `0`.
  - Duplicate OCR PDFs' first component order: `O5-O4-G5-B4`.
  - Strict unit/order hits near active boxes: `0`.
  - Hidden OCR document-order candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|allFourBoxes=0|allFourComponents=2|activeOrder=0|strictNear=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The current PDFs' invisible OCR layer is derivative article context, not original-layout authority.
  - Keep PDF OCR document order closed unless a distinct source or raw clue supplies R3 unit/order evidence.
  - Frontier now records `214` focused local checks.

### Current PDF OCR OVERDOSE Index-Offset Gate

- Status: checked; hidden OCR `OVERDOSE` document index does not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_ocr_overdose_index_offset_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ocr_overdose_index_offset_gate/current_pdf_ocr_overdose_index_offset_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ocr_overdose_index_offset_gate/current_pdf_ocr_overdose_index_offset_gate.json`
  - `analysis_outputs/source_audit/current_pdf_ocr_overdose_index_offset_gate/current_pdf_ocr_overdose_index_offset_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Located OCR `OVERDOSE` positions in the current PDFs and tested plus/minus active line/corridor/slot units for `O4`, `B4`, `G5`, and `O5`.
  - Checked whether bounded offset landings hit active target-component words or strict instruction terms.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - PDFs with OCR `OVERDOSE`: `2`.
  - Offset landing rows checked: `46`.
  - Target-component offset hits: `2`.
  - Strict instruction offset hits: `0`.
  - Both target hits duplicate the same relation in the byte-identical OCR PDFs: `G5 + corridorIndex=9 -> heart`.
  - PDFs with all-four known-unit deltas: `0`.
  - Hidden OVERDOSE index candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|overdosePdfs=2|offsetRows=46|targetHits=2|strictHits=0|allFourKnownDelta=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The hidden OCR `OVERDOSE` index produces only a duplicated context-word landing, not an all-four or instruction-bearing rule.
  - Keep current PDF OCR/OVERDOSE offsets closed unless a distinct source/raw clue supplies R3 unit/order evidence.
  - Frontier now records `215` focused local checks.

### Current PDF OCR OVERDOSE Neighborhood Gate

- Status: checked; hidden OCR `OVERDOSE` local word windows do not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_ocr_overdose_neighborhood_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ocr_overdose_neighborhood_gate/current_pdf_ocr_overdose_neighborhood_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ocr_overdose_neighborhood_gate/current_pdf_ocr_overdose_neighborhood_gate.json`
  - `analysis_outputs/source_audit/current_pdf_ocr_overdose_neighborhood_gate/current_pdf_ocr_overdose_neighborhood_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Located OCR `OVERDOSE` positions in the current PDFs and inspected fixed word windows at radii `4`, `8`, `16`, and `32`.
  - Counted strict unit/order terms, O4/B4/G5/O5 component target terms, all-four neighborhoods, and active-order neighborhoods.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - PDFs with OCR `OVERDOSE`: `2`.
  - OCR `OVERDOSE` word count: `2`.
  - Neighborhood rows checked: `8`.
  - Strict unit/order neighborhood rows: `0`.
  - Target-component neighborhood rows: `4`.
  - All-four target neighborhoods: `0`.
  - Active-order neighborhoods: `0`.
  - Hidden OVERDOSE neighborhood candidates: `0`.
  - The only target context in these windows is duplicated O5/`heart` text from the byte-identical OCR PDFs.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|overdosePdfs=2|overdoseWords=2|rows=8|strictRows=0|targetRows=4|allFourRows=0|activeOrderRows=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The hidden OCR `OVERDOSE` neighborhood has ordinary opening context only, not instruction wording, all-four target coverage, or active-order structure.
  - Keep current PDF OCR/OVERDOSE local windows closed unless a distinct source/raw clue supplies R3 unit/order evidence.
  - Frontier now records `216` focused local checks.

### Current PDF OCR Page-Header Sequence Gate

- Status: checked; current PDF OCR page starts do not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_ocr_page_header_sequence_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ocr_page_header_sequence_gate/current_pdf_ocr_page_header_sequence_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ocr_page_header_sequence_gate/current_pdf_ocr_page_header_sequence_gate.json`
  - `analysis_outputs/source_audit/current_pdf_ocr_page_header_sequence_gate/current_pdf_ocr_page_header_sequence_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected page-start OCR text across current PDF article pages `73-80`.
  - Tested whether page 76 starting with OCR `OVERDOSE` in duplicate OCR PDFs creates a page-order, unit/order, or all-four target selector.
  - Counted strict unit/order terms, target component terms, all-four target page-start rows, active-order page-start rows, and selector candidates.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Article page-start rows checked: `24`.
  - Page-76 OCR `OVERDOSE` header PDFs: `2`.
  - Strict page-start rows: `0`.
  - Target page-start rows: `2`.
  - All-four target page-start rows: `0`.
  - Active-order page-start rows: `0`.
  - Page-header sequence candidates: `0`.
  - The duplicate OCR PDFs share first-token sequence `73:jopeajes 74:overdose 75:jopeajes 76:overdose 77:o 78:overdose 79:of 80:fake`, which is OCR/article/header noise rather than a source-backed instruction sequence.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|pageRows=24|p76Overdose=2|strictRows=0|targetRows=2|allFourRows=0|activeOrderRows=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Page 76 begins with `OVERDOSE` only in byte-identical OCR derivatives, and page-start OCR rows do not combine instruction terms with all-four active target terms or active-order structure.
  - Keep current PDF OCR page starts closed unless a distinct source/raw clue supplies R3 unit/order evidence.
  - Frontier now records `217` focused local checks.

### Current PDF Visual Header/Footer Band Sequence Gate

- Status: checked; visible PDF top/bottom band layout does not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_visual_header_footer_band_sequence_gate.py`
  - `analysis_outputs/source_audit/current_pdf_visual_header_footer_band_sequence_gate/current_pdf_visual_header_footer_band_sequence_gate.md`
  - `analysis_outputs/source_audit/current_pdf_visual_header_footer_band_sequence_gate/current_pdf_visual_header_footer_band_sequence_gate.json`
  - `analysis_outputs/source_audit/current_pdf_visual_header_footer_band_sequence_gate/current_pdf_visual_header_footer_band_sequence_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Rendered the three current PDFs as displayed for article pages `73-80`.
  - Cropped top and bottom bands, measured visual signatures, and compared page 76 against same-band neighbors inside each PDF.
  - Used the prior OCR page-header report only to label repeated `OVERDOSE` page-start context.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Article page rows checked: `24`.
  - Visual bands checked: `48`.
  - OCR `OVERDOSE` page-start rows imported from previous gate: `6`.
  - Page-76 top-band near matches: `15`.
  - Page-76 bottom-band near matches: `5`.
  - Duplicate OCR PDFs show page-76 top closest to pages `74`, `78`, and `75`, and those same PDFs have OCR `OVERDOSE` starts on pages `74`, `76`, and `78`.
  - Visual header/footer sequence candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|pages=24|bands=48|p76TopNear=15|p76BottomNear=5|ocrOverdoseStarts=6|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The visible page-76 header/footer band state is layout/context evidence only; it does not name a unit/order or distinguish a source-backed extraction path.
  - Keep current PDF visual header/footer bands closed unless a true source asset or raw clue supplies R3 unit/order evidence.
  - Frontier now records `218` focused local checks.

### Current PDF Repeated OVERDOSE Header Lane Gate

- Status: checked; repeated `OVERDOSE` page-start lane projections do not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_repeated_overdose_header_lane_gate.py`
  - `analysis_outputs/source_audit/current_pdf_repeated_overdose_header_lane_gate/current_pdf_repeated_overdose_header_lane_gate.md`
  - `analysis_outputs/source_audit/current_pdf_repeated_overdose_header_lane_gate/current_pdf_repeated_overdose_header_lane_gate.json`
  - `analysis_outputs/source_audit/current_pdf_repeated_overdose_header_lane_gate/current_pdf_repeated_overdose_header_lane_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used the repeated OCR `OVERDOSE` page-start rows in the current PDFs as controls.
  - Split each header into normal, reversed-label, x-mirrored, and x-mirrored/reversed vertical lanes.
  - Counted lane-carried target terms, strict unit/order words, all-four target rows, active-order rows, and selector candidates.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Repeated OCR `OVERDOSE` header rows: `6` from pages `74`, `76`, and `78` in the two duplicate OCR PDFs.
  - Lane rows checked: `24`.
  - Target lane rows: `0`.
  - Strict unit/order lane rows: `0`.
  - All-four lane rows: `0`.
  - Active-order lane rows: `0`.
  - Page-76 target lane rows: `0`.
  - Header-lane candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|overdoseHeaders=6|laneRows=24|targetRows=0|strictRows=0|allFourRows=0|activeOrderRows=0|page76TargetRows=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Repeated `OVERDOSE` page-start lanes do not touch target terms or instruction terms, even before applying the source-backed R3 requirement.
  - Keep repeated `OVERDOSE` header lane mechanics closed unless a true source asset or raw clue supplies R3 unit/order evidence.
  - Frontier now records `219` focused local checks.

### Current PDF OVERDOSE Header Delta Transfer Gate

- Status: checked; repeated `OVERDOSE` header offsets do not transfer page-76 targets to a selector.
- Evidence:
  - `scripts/audit_current_pdf_overdose_header_delta_transfer_gate.py`
  - `analysis_outputs/source_audit/current_pdf_overdose_header_delta_transfer_gate/current_pdf_overdose_header_delta_transfer_gate.md`
  - `analysis_outputs/source_audit/current_pdf_overdose_header_delta_transfer_gate/current_pdf_overdose_header_delta_transfer_gate.json`
  - `analysis_outputs/source_audit/current_pdf_overdose_header_delta_transfer_gate/current_pdf_overdose_header_delta_transfer_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Measured OCR `OVERDOSE` header-center deltas from article page `76` to repeated-header pages `74` and `78`.
  - Applied direct and mirrored header-delta transfers to the locked page-76 O4/B4/G5/O5 target boxes.
  - Checked transferred boxes for OCR text, target terms, strict unit/order words, all-four target coverage, active-order target coverage, and selector candidates.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Repeated OCR `OVERDOSE` header rows: `6`.
  - Transfer variants: `12`.
  - Transferred target boxes checked: `48`.
  - Text-hit boxes: `0`.
  - Target-term boxes: `0`.
  - Strict unit/order boxes: `0`.
  - All-four transfer variants: `0`.
  - Active-order transfer variants: `0`.
  - Header-delta transfer candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|headers=6|variants=12|boxRows=48|textRows=0|targetRows=0|strictRows=0|allFourVariants=0|activeOrderVariants=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Measured page-76-to-74/78 `OVERDOSE` header offsets do not land the active boxes on OCR words at all.
  - Keep repeated `OVERDOSE` header-offset mechanics closed unless a true source asset or raw clue supplies R3 unit/order evidence.
  - Frontier now records `220` focused local checks.

### Current PDF OVERDOSE Body-Start Vector Gate

- Status: checked; repeated `OVERDOSE` header-to-body-start rays do not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_overdose_body_start_vector_gate.py`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_start_vector_gate/current_pdf_overdose_body_start_vector_gate.md`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_start_vector_gate/current_pdf_overdose_body_start_vector_gate.json`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_start_vector_gate/current_pdf_overdose_body_start_vector_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used repeated OCR `OVERDOSE` page-start rows in the current PDFs.
  - Measured the vector from each header to the first readable body line and checked 10 pt / 20 pt ray tubes through OCR words.
  - Counted target terms, strict unit/order words, all-four target rows, active-order rows, selector candidates, and source-backed R3.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Repeated OCR `OVERDOSE` header rows: `6`.
  - Body-start rows: `4`; page `74` has no body line in the duplicate OCR PDFs.
  - Body vector rows: `8`.
  - Target vector rows: `0`.
  - Strict unit/order vector rows: `0`.
  - All-four vector rows: `0`.
  - Active-order vector rows: `0`.
  - Body-start vector candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|headers=6|bodyRows=4|vectorRows=8|targetRows=0|strictRows=0|allFourRows=0|activeOrderRows=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Repeated `OVERDOSE` header-to-first-body-line vectors hit ordinary opening prose, not target or instruction structure.
  - Keep repeated `OVERDOSE` body-start vector mechanics closed unless a true source asset or raw clue supplies R3 unit/order evidence.
  - Frontier now records `221` focused local checks.

### Current PDF OVERDOSE Body-Basis Reflection Gate

- Status: checked; `OVERDOSE` body-axis and body-start perpendicular reflections do not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_overdose_body_basis_reflection_gate.py`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_basis_reflection_gate/current_pdf_overdose_body_basis_reflection_gate.md`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_basis_reflection_gate/current_pdf_overdose_body_basis_reflection_gate.json`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_basis_reflection_gate/current_pdf_overdose_body_basis_reflection_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used repeated OCR `OVERDOSE` pages with a readable first body line: pages `76` and `78` in the two duplicate OCR PDFs.
  - Reflected locked O4/B4/G5/O5 boxes across the header-to-body axis and the perpendicular body-start axis.
  - Counted reflected-box OCR words, target terms, strict unit/order words, all-four target rows, active-order rows, selector candidates, and source-backed R3.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Body-basis rows: `4`.
  - Transform variants: `8`.
  - Reflected active boxes: `32`.
  - In-page reflected boxes: `10`.
  - Text-hit reflected boxes: `2`.
  - Target-term reflected boxes: `0`.
  - Strict unit/order reflected boxes: `0`.
  - All-four transform variants: `0`.
  - Active-order transform variants: `0`.
  - Body-basis reflection candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|basisRows=4|variants=8|boxRows=32|inPage=10|textRows=2|targetRows=0|strictRows=0|allFourVariants=0|activeOrderVariants=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Most reflected active boxes leave the page; the only text contacts are page-78 control prose and contain no target or instruction terms.
  - Keep `OVERDOSE` body-basis reflection mechanics closed unless a true source asset or raw clue supplies R3 body-axis/fold/unit-order evidence.
  - Frontier now records `222` focused local checks.

### Current PDF OVERDOSE Body-Line Lattice Gate

- Status: checked; `OVERDOSE` body-line row/column mapping does not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_overdose_body_lattice_gate.py`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_lattice_gate/current_pdf_overdose_body_lattice_gate.md`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_lattice_gate/current_pdf_overdose_body_lattice_gate.json`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_lattice_gate/current_pdf_overdose_body_lattice_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used repeated OCR `OVERDOSE` pages with readable body text: pages `76` and `78` in the two duplicate OCR PDFs.
  - Mapped locked O4/B4/G5/O5 boxes to nearest OCR body lines.
  - Counted row order, column placement, nearest-line target terms, strict unit/order words, all-four target rows, active-order rows, selector candidates, and source-backed R3.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Body-lattice pages: `4`.
  - Mapped active rows: `16`.
  - Own-target line hits: `0`.
  - Strict mapped rows: `0`.
  - All-four own-target variants: `0`.
  - Active-row-order variants: `4`, but this comes from fixed target-box height order and also appears in page-78 controls.
  - Body-lattice candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|latticePages=4|mappedRows=16|ownTargetRows=0|strictRows=0|allFourVariants=0|activeOrderVariants=4|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Body-line lattice mapping preserves geometric target order but does not recover target text or instruction wording.
  - Keep `OVERDOSE` body-line lattice mechanics closed unless a true source asset or raw clue supplies R3 row/column/unit-order evidence.
  - Frontier now records `223` focused local checks.

### Current PDF OVERDOSE Body-Offset Transfer Gate

- Status: checked; repeated `OVERDOSE` body-row offsets do not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_overdose_body_offset_transfer_gate.py`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_offset_transfer_gate/current_pdf_overdose_body_offset_transfer_gate.md`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_offset_transfer_gate/current_pdf_overdose_body_offset_transfer_gate.json`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_offset_transfer_gate/current_pdf_overdose_body_offset_transfer_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Derived the page-76 active O4/B4/G5/O5 body-row offsets from repeated OCR `OVERDOSE` body starts.
  - Transferred only those offsets to repeated `OVERDOSE` pages `74`, `76`, and `78` in the current PDFs.
  - Counted own-target hits, strict unit/order words, all-four target pages, active-order pages, selector candidates, and source-backed R3.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Repeated OCR `OVERDOSE` header rows: `6`.
  - Body-offset pages: `4`.
  - Source offset rows: `8`.
  - Transferred offset rows: `16`.
  - Offset signature in both duplicate OCR PDFs: `O4=35`, `B4=40`, `G5=42`, `O5=44`.
  - Own-target offset hits: `0`.
  - Strict offset rows: `0`.
  - All-four own-target pages: `0`.
  - Active-target-order pages: `0`.
  - Body-offset candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|headers=6|sourceOffsets=8|offsetPages=4|offsetRows=16|ownTargetRows=0|strictRows=0|allFourPages=0|activeOrderPages=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The body-row offset signature is reproducible in duplicate OCR PDFs but lands on ordinary OCR rows and does not recover target text, instruction wording, active order, candidates, or source-backed R3.
  - Keep `OVERDOSE` body-offset transfer mechanics closed unless a true source asset or raw clue supplies R3 body-row offset/unit-order evidence.
  - Frontier now records `224` focused local checks.

### Current PDF OVERDOSE Body-Offset Column Gate

- Status: checked; repeated `OVERDOSE` body-row plus x-column word landings do not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_overdose_body_offset_column_gate.py`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_offset_column_gate/current_pdf_overdose_body_offset_column_gate.md`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_offset_column_gate/current_pdf_overdose_body_offset_column_gate.json`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_offset_column_gate/current_pdf_overdose_body_offset_column_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Derived page-76 active O4/B4/G5/O5 body-row offsets plus x positions from repeated OCR `OVERDOSE` body grids.
  - Transferred those row-plus-column points to repeated `OVERDOSE` pages `74`, `76`, and `78` in the current PDFs.
  - Kept only the nearest OCR word on each landed row.
  - Counted target words, own-target words, strict unit/order words, all-four target pages, active-order pages, selector candidates, and source-backed R3.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Repeated OCR `OVERDOSE` header rows: `6`.
  - Source row-plus-column points: `8`.
  - Column landing pages: `4`.
  - Landed word rows: `16`.
  - Nearest-word streams:
    - Page `76`: `eis and Street siukbeodmensertslveaarty`.
    - Page `78`: `@ economy aa efficie:`.
  - Target-word hits: `0`.
  - Own-target word hits: `0`.
  - Strict-word hits: `0`.
  - All-four own-target pages: `0`.
  - Active-word-target-order pages: `0`.
  - Body-offset column candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|headers=6|sourcePoints=8|columnPages=4|wordRows=16|targetWordRows=0|ownWordRows=0|strictWordRows=0|allFourPages=0|activeOrderPages=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The row-plus-column version lands on concrete OCR words, but those words are OCR noise/ordinary prose rather than target or instruction words.
  - Keep `OVERDOSE` body-offset column mechanics closed unless a true source asset or raw clue supplies R3 row-plus-column word/unit-order evidence.
  - Frontier now records `225` focused local checks.

### Current PDF OVERDOSE Body-Fraction Column Gate

- Status: checked; normalized repeated `OVERDOSE` body-row fraction plus x-column word landings do not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_overdose_body_fraction_column_gate.py`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_fraction_column_gate/current_pdf_overdose_body_fraction_column_gate.md`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_fraction_column_gate/current_pdf_overdose_body_fraction_column_gate.json`
  - `analysis_outputs/source_audit/current_pdf_overdose_body_fraction_column_gate/current_pdf_overdose_body_fraction_column_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Derived page-76 active O4/B4/G5/O5 normalized body-row fractions plus x positions from repeated OCR `OVERDOSE` body grids.
  - Transferred those fraction-plus-column points to repeated `OVERDOSE` pages `74`, `76`, and `78` in the current PDFs.
  - Kept only the nearest OCR word on each landed row.
  - Counted target words, own-target words, strict unit/order words, all-four target pages, active-order pages, selector candidates, and source-backed R3.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Repeated OCR `OVERDOSE` header rows: `6`.
  - Source normalized row-plus-column fractions: `8`.
  - Fraction landing pages: `4`.
  - Landed word rows: `16`.
  - Source fractions: `O4=0.795455`, `B4=0.909091`, `G5=0.954545`, `O5=1.0`.
  - Nearest-word streams:
    - Page `76`: `eis and Street siukbeodmensertslveaarty`.
    - Page `78`: `nrot peste 4 ware`.
  - Page `78` landed rows: `36,41,43,45`.
  - Target-word hits: `0`.
  - Own-target word hits: `0`.
  - Strict-word hits: `0`.
  - All-four own-target pages: `0`.
  - Active-word-target-order pages: `0`.
  - Body-fraction column candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|headers=6|sourceFractions=8|fractionPages=4|wordRows=16|targetWordRows=0|ownWordRows=0|strictWordRows=0|allFourPages=0|activeOrderPages=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Normalized body-row fractions change the page-78 landing rows but still land on OCR noise/ordinary prose rather than target or instruction words.
  - Keep `OVERDOSE` body-fraction column mechanics closed unless a true source asset or raw clue supplies R3 normalized row-plus-column word/unit-order evidence.
  - Frontier now records `226` focused local checks.

### Current PDF Leaf-Pair Texture Correlation Gate

- Status: checked; embedded PDF leaf-pair texture does not support physical back-side mirror as a selector.
- Evidence:
  - `scripts/audit_current_pdf_leaf_pair_texture_correlation_gate.py`
  - `analysis_outputs/source_audit/current_pdf_leaf_pair_texture_correlation_gate/current_pdf_leaf_pair_texture_correlation_gate.md`
  - `analysis_outputs/source_audit/current_pdf_leaf_pair_texture_correlation_gate/current_pdf_leaf_pair_texture_correlation_gate.json`
  - `analysis_outputs/source_audit/current_pdf_leaf_pair_texture_correlation_gate/current_pdf_leaf_pair_texture_correlation_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Compared embedded PDF page-image texture for leaf pairs `75/76`, `77/78`, and `79/80` across the three current PDFs.
  - Tested physical back-side mirror against same-side/no-mirror, mirrored+180, and unmirrored+180 controls.
  - Measured active-region correlation, feature IoU, same-slot O4/B4/G5/O5 controls, all-four active-box outliers, and source-backed R3.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDFs checked: `3`.
  - Leaf pairs checked: `9`.
  - Transform rows: `36`.
  - Active-box rows: `144`.
  - Active boxes above same-size control p95: `17`.
  - All-four above-control-p95 variants: `1`.
  - Physical back-side mirror best pair rows: `0/9`.
  - Page `75/76` physical back-side mirror best rows: `0/3`.
  - Page `75/76` physical active-region max correlation / feature IoU: `-0.0158` / `0.0500`.
  - The only all-four above-control-p95 row is `magazine.pdf` `75/76` `same_side_no_mirror`, not the physical mirror transform.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pdfs=3|pairs=9|transforms=4|rows=36|activeRows=144|activeP95=17|allFourP95=1|physBest=0|p7576PhysBest=0/3|p7576PhysCorrMax=-0.0158|p7576PhysIouMax=0.0500|activeIouMax=0.9550|activeCorrMax=0.2029|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Physical mirror is not the winning texture registration for any tested current-PDF leaf pair.
  - Keep PDF leaf-pair texture/correlation mechanics closed unless a distinct physical/original-layout source or raw clue supplies the missing transform/unit/order evidence.
  - Frontier now records `227` focused local checks.

### Local Page Raster Lineage Gate

- Status: checked; loose/local page images do not provide a distinct source.
- Evidence:
  - `scripts/audit_local_page_raster_lineage_gate.py`
  - `analysis_outputs/source_audit/local_page_raster_lineage_gate/local_page_raster_lineage_gate.md`
  - `analysis_outputs/source_audit/local_page_raster_lineage_gate/local_page_raster_lineage_gate.json`
  - `analysis_outputs/source_audit/local_page_raster_lineage_gate/local_page_raster_lineage_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mapped loose root JPEGs, source-image cache files, and 3D upright page images against embedded PDF page rasters for article pages `73-80`.
  - Used orientation-aware sample matching to classify near-duplicates, derivative-like rows, distinct local raster candidates, and promoted source candidates.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - PDF embedded reference rows: `24`.
  - Local page-raster candidates: `24`.
  - Near-duplicate rows: `24`.
  - Derivative-like rows: `24`.
  - Distinct local raster candidates: `0`.
  - Promoted source candidates: `0`.
  - Higher-resolution-than-best-reference rows: `0`.
  - Sharper-than-best-reference rows: `0`.
  - Root `keyser bitcoin -1_1.jpg` through `keyser bitcoin -8_1.jpg` map exactly to article pages `73-80`.
  - Root `magazine-1_1.jpg` through `magazine-4_1.jpg` map exactly to article pages `73-76`.
  - 3D upright cache pages `75-80` map back to the same embedded image family after the documented rotation.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `refs=24|candidates=24|nearDup=24|derivative=24|distinct=0|promoted=0|higher=0|sharper=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The loose/local raster files are duplicate witnesses, not new source material.
  - Keep local page raster lineage closed unless a new physical/original-layout asset or raw clue wording passes source-reopen requirements.
  - Frontier now records `228` focused local checks.

### Current Scan Background Seam Residual Gate

- Status: checked; background seam/gutter/crop residuals do not provide a selector.
- Evidence:
  - `scripts/audit_current_scan_background_seam_residual_gate.py`
  - `analysis_outputs/source_audit/current_scan_background_seam_residual_gate/current_scan_background_seam_residual_gate.md`
  - `analysis_outputs/source_audit/current_scan_background_seam_residual_gate/current_scan_background_seam_residual_gate.json`
  - `analysis_outputs/source_audit/current_scan_background_seam_residual_gate/current_scan_background_seam_residual_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Masked foreground text/highlight ink and inspected only broad page-background luminance transitions on upright page rasters `75`, `76`, `78`, and `79`.
  - Compared page-76-unique vertical/horizontal background seam candidates against active O4/B4/G5/O5 boxes, non-active highlight controls, and projected OVERDOSE slots.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Pages checked: `4`.
  - Page-76 structural vertical/horizontal seam lines: `0` / `24`.
  - Page-76 unique structural vertical/horizontal seam lines: `0` / `14`.
  - Active boxes close to unique structural x/y lines at `<=16px`: `0` / `1`.
  - All-four active close to unique structural x/y lines at `<=16px`: `0` / `0`.
  - Shared active vertical/horizontal line hits at `<=16px`: `0` / `1`.
  - Controls close to unique structural x/y lines at `<=16px`: `0` / `2`.
  - OVERDOSE slots close to unique structural x/y lines at `<=16px`: `0` / `0`.
  - The one active hit is G5 near a horizontal background transition; it is not shared by O4/B4/O5 and controls also hit horizontal transitions.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pages=4|p76V=0|p76H=24|uniqV=0|uniqH=14|activeX16=0|activeY16=1|allX16=0|allY16=0|sharedX16=0|sharedY16=1|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The current scan background has no vertical structural carrier and no all-four active horizontal seam carrier.
  - Keep background seam/gutter residuals closed unless a new physical/original-layout source changes the background seams or raw clue wording explicitly names seam, gutter, trim, fold, crop line, unit, and read order.
  - Frontier now records `229` focused local checks.

### Current Scan Paper Texture Duplex Gate

- Status: checked; paper/background texture does not support physical mirror as a selector.
- Evidence:
  - `scripts/audit_current_scan_paper_texture_duplex_gate.py`
  - `analysis_outputs/source_audit/current_scan_paper_texture_duplex_gate/current_scan_paper_texture_duplex_gate.md`
  - `analysis_outputs/source_audit/current_scan_paper_texture_duplex_gate/current_scan_paper_texture_duplex_gate.json`
  - `analysis_outputs/source_audit/current_scan_paper_texture_duplex_gate/current_scan_paper_texture_duplex_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Masked foreground text/highlight ink and kept only paper/background texture on current upright page rasters `75-80`.
  - Compared physical leaf pairs `75/76`, `77/78`, and `79/80` with six control page pairs across identity, horizontal mirror, vertical mirror, and 180-degree rotation transforms.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Physical leaf pairs / control pairs: `3` / `6`.
  - Transform rows: `36`.
  - Physical mirror best pair rows: `1/3`.
  - Physical mirror above control p95 rows: `0/3`.
  - Physical mirror max correlation: `0.308967`.
  - Control max / p95 correlation: `0.349464` / `0.322037`.
  - Physical pair best transforms: `75/76=identity`, `77/78=hmirror`, `79/80=rot180`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pairs=9|rows=36|physMirrorBest=1/3|physAboveControlP95=0/3|physMax=0.3090|controlMax=0.3495|controlP95=0.3220|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Paper/fiber texture does not make the physical back-side mirror a stable registration rule in the current scan.
  - Keep paper-texture duplex registration closed unless a new physical/original-layout source changes the registration or raw clue wording explicitly names side, mirror, paper texture, unit, and read order.
  - Frontier now records `230` focused local checks.

### Current Scan Paper Texture Shift Gate

- Status: checked; small global mirror-shift does not rescue paper/fiber duplex registration.
- Evidence:
  - `scripts/audit_current_scan_paper_texture_shift_gate.py`
  - `analysis_outputs/source_audit/current_scan_paper_texture_shift_gate/current_scan_paper_texture_shift_gate.md`
  - `analysis_outputs/source_audit/current_scan_paper_texture_shift_gate/current_scan_paper_texture_shift_gate.json`
  - `analysis_outputs/source_audit/current_scan_paper_texture_shift_gate/current_scan_paper_texture_shift_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Masked foreground text/highlight ink and kept only paper/background texture on current upright page rasters `75-80`.
  - Applied the physical horizontal mirror and allowed global shifts from `-32` to `32` px in `8` px steps.
  - Compared physical leaf pairs `75/76`, `77/78`, and `79/80` against six control page pairs.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Physical leaf pairs / control pairs: `3` / `6`.
  - Shift rows: `729`.
  - Physical best above control-best p95 rows: `1/3`.
  - Physical best at `<=16px` shift rows: `1/3`.
  - Physical zero-shift above control-best p95 rows: `0/3`.
  - Physical best max correlation: `0.426065`.
  - Control best max / p95 correlation: `0.369263` / `0.355692`.
  - Physical best shifts: `75/76=(-32,-24)`, `77/78=(0,-8)`, `79/80=(32,-32)`.
  - The lone above-threshold physical result is `79/80`; it needs the maximum tested shift and has low background overlap, so it is not a stable leaf-pair registration rule.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `pairs=9|shifts=81|rows=729|physAboveControlP95=1/3|physSmallShiftBest=1/3|zeroShiftAboveControlP95=0/3|physBestMax=0.4261|controlBestMax=0.3693|controlBestP95=0.3557|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Paper/fiber texture does not produce a usable held-to-light/duplex registration selector, even when small scan slip is allowed after mirroring.
  - Keep paper-texture shift rescue closed unless a new physical/original-layout source changes the registration or raw clue wording explicitly names side, mirror, paper texture, shift/registration, unit, and read order.
  - Frontier now records `231` focused local checks.

### Current Scan Light Table Self Signal Partition Gate

- Status: checked; the valid held-to-light average-blend pop is front-page self-signal, not all-four source evidence.
- Evidence:
  - `scripts/audit_current_scan_light_table_self_signal_partition_gate.py`
  - `analysis_outputs/source_audit/current_scan_light_table_self_signal_partition_gate/current_scan_light_table_self_signal_partition_gate.md`
  - `analysis_outputs/source_audit/current_scan_light_table_self_signal_partition_gate/current_scan_light_table_self_signal_partition_gate.json`
  - `analysis_outputs/source_audit/current_scan_light_table_self_signal_partition_gate/current_scan_light_table_self_signal_partition_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used the physically valid current-scan `75 -> 76` average blend at alpha `0.70`.
  - Partitioned blend delta into page-76 target-only ink versus mirrored page-75 source-supported signal.
  - Compared O4/B4/G5/O5 with `24` line-shift controls and `8` projected OVERDOSE slots.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - Active / line-shift controls / OVERDOSE slots: `4` / `24` / `8`.
  - Active target-only dominant rows: `4/4`.
  - Active source-supported dominant rows: `0/4`.
  - Active source-supported mean/share above control p95 rows: `0/4` / `0/4`.
  - Active min target-only delta share: `0.847292`.
  - Active max source-supported delta share: `0.151722`.
  - Active target-only/source-supported shares:
    - `O4`: `0.886249` / `0.113351`.
    - `B4`: `0.995653` / `0.0`.
    - `G5`: `0.963745` / `0.032698`.
    - `O5`: `0.847292` / `0.151722`.
  - OVERDOSE slot controls include stronger source-supported shares than the active boxes, so the active visual pop is not a unique back-page source signal.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `active=4|controls=24|slots=8|alpha=0.70|activeTargetOnlyDominant=4/4|activeSourceDominant=0/4|activeSrcMeanAboveCtlP95=0/4|activeSrcShareAboveCtlP95=0/4|activeMinTargetOnly=0.8473|activeMaxSourceShare=0.1517|slotSrcMeanP95=28.9530|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The valid held-to-light average blend is visually tempting because page-76 target ink is being faded against a pale mirrored source layer.
  - Do not treat the valid `75 -> 76` blend as source evidence, and stop varying blend/opacity/order for this pair unless new source/clue material supplies unit, transform, and read order.
  - Frontier now records `232` focused local checks.

### Current Scan OVERDOSE Slot Source Support Trace

- Status: checked; source-supported OVERDOSE slot signal is ordinary page-75 text-band bleed, not an extraction selector.
- Evidence:
  - `scripts/audit_current_scan_overdose_slot_source_support_trace.py`
  - `analysis_outputs/source_audit/current_scan_overdose_slot_source_support_trace/current_scan_overdose_slot_source_support_trace.md`
  - `analysis_outputs/source_audit/current_scan_overdose_slot_source_support_trace/current_scan_overdose_slot_source_support_trace.json`
  - `analysis_outputs/source_audit/current_scan_overdose_slot_source_support_trace/current_scan_overdose_slot_source_support_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used the physically valid current-scan `75 -> 76` horizontal mirror.
  - Mapped all `8` projected OVERDOSE slot boxes back to page-75 source bands.
  - Checked source OCR words, instruction-like terms, action/order terms, and context terms.
  - No OCR-to-key extraction, key candidates, hashes-to-key, seed phrases, WIF checks, address checks, BIP39, or broad brute force were run.
- Findings:
  - High source-supported slots: `3` (`O5,S6,E7`).
  - High source-supported run: `OSE@5-7`.
  - Source word hits / OCR rows: `111` / `58`.
  - Instruction-like hits / action-order hits / high-slot action-order hits: `1` / `0` / `0`.
  - Unit-only prose term: `words`.
  - Context hits: `bitcoin`, `bitcoins`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `slots=8|highSrc=3|highRun=OSE@5-7|highSlots=O5,S6,E7|words=111|wordRows=58|instructionLike=1|actionOrder=0|highActionOrder=0|unitOnly=words|context=2|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The `OSE` source-support run is real geometry under the valid mirror, but it maps to broad lower-page source prose.
  - It does not supply source-backed unit/order/read permission and does not rescue the active quartet.
  - Frontier now records `233` focused local checks.

### Current PDF OVERDOSE Slot Source Support Trace

- Status: checked; the original PDF render preserves the `OSE` source-support run, but it still does not produce an action/order selector.
- Evidence:
  - `scripts/audit_current_pdf_overdose_slot_source_support_trace.py`
  - `analysis_outputs/source_audit/current_pdf_overdose_slot_source_support_trace/current_pdf_overdose_slot_source_support_trace.md`
  - `analysis_outputs/source_audit/current_pdf_overdose_slot_source_support_trace/current_pdf_overdose_slot_source_support_trace.json`
  - `analysis_outputs/source_audit/current_pdf_overdose_slot_source_support_trace/current_pdf_overdose_slot_source_support_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Re-ran the OVERDOSE slot source-support trace on PDF-native carriers: visible page renders and embedded page-image canvases.
  - Covered `magazine.pdf`, `keyser bitcoin .pdf`, and the Google Drive duplicate PDF.
  - Used the valid `75 -> 76` horizontal mirror and the same `8` projected OVERDOSE slots.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - PDF carrier rows checked: `6`.
  - Current-scan high run: `OSE@5-7`.
  - PDF carrier rows matching current scan: `2/6`.
  - `magazine.pdf` visible render / embedded canvas high runs: `OSE@5-7` / `OSE@5-7`.
  - Duplicate/Google carriers over-support all slots as `OVERDOSE@0-7`, consistent with carrier saturation rather than puzzle instruction.
  - Action/order hits / high-slot action-order hits: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `carriers=6|scanRun=OSE@5-7|match=2/6|magRender=OSE@5-7|magEmbedded=OSE@5-7|actionOrder=0|highActionOrder=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The `OSE` slot pattern is not merely a scan artifact; it is stable in the byte-locked `magazine.pdf` render and embedded canvas.
  - It remains a page-75 text-band provenance/control result, not an extraction path, because it has no source-backed unit, transform, action/order wording, or read order.
  - Frontier now records `234` focused local checks.

### Current PDF OSE Source Highlight Phrase Gate

- Status: checked; `OSE@5-7` has partial orange-highlight contact, but no complete highlight bridge and no action/order selector.
- Evidence:
  - `scripts/audit_current_pdf_ose_source_highlight_phrase_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ose_source_highlight_phrase_gate/current_pdf_ose_source_highlight_phrase_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ose_source_highlight_phrase_gate/current_pdf_ose_source_highlight_phrase_gate.json`
  - `analysis_outputs/source_audit/current_pdf_ose_source_highlight_phrase_gate/current_pdf_ose_source_highlight_phrase_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested the stable byte-locked `magazine.pdf` `OSE@5-7` source run against page-75/page-76 orange-highlight boxes and nearby source/target phrase text.
  - Checked source-highlight words, target-highlight words, source edge words, strict unit terms, action/order terms, context terms, and selector-candidate rows.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Carriers / slot rows: `2` / `16`.
  - Render high slots: `O5,S6,E7`.
  - Source-highlight contact in render high slots: `3/3`.
  - Target-highlight contact in render high slots: `2/3`.
  - Two-sided highlight bridge in render high slots: `2/3`.
  - High-slot action/order rows / selector candidates: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Render high source-highlight text: `O5=dignity.`, `S6=Keep your dignity. the BSR`, `E7=Keep`.
  - Fingerprint: `carriers=2|rows=16|high=6|renderHigh=O5,S6,E7|highSrcHi=3/3|highTgtHi=2/3|highBridge=2/3|highAction=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Orange highlight contact makes `OSE` worth documenting, but it is incomplete and still reads as ordinary article prose.
  - It does not supply unit, transform, action/order wording, or read order.
  - Frontier now records `235` focused local checks.

### Current PDF OSE Highlight Mirror Geometry Gate

- Status: checked; the `OSE` source highlights mirror into OVERDOSE slot bands, not into page-76 active targets.
- Evidence:
  - `scripts/audit_current_pdf_ose_highlight_mirror_geometry_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ose_highlight_mirror_geometry_gate/current_pdf_ose_highlight_mirror_geometry_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ose_highlight_mirror_geometry_gate/current_pdf_ose_highlight_mirror_geometry_gate.json`
  - `analysis_outputs/source_audit/current_pdf_ose_highlight_mirror_geometry_gate/current_pdf_ose_highlight_mirror_geometry_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Mirrored all page-75 orange highlights onto page 76 using the valid `75 -> 76` horizontal mirror.
  - Focused on `p75_orange_7` and `p75_orange_8`, the page-75 source highlights behind the stable `OSE@5-7` source-support run.
  - Checked contacts with page-76 orange highlights, locked O4/B4/G5/O5 active target boxes, and measured OVERDOSE slot boxes.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Page-75 orange highlights / OSE source highlights: `8` / `2`.
  - OSE rows with page-76 highlight contact: `0/2`.
  - OSE rows with active target contact: `0/2`.
  - OSE rows with OVERDOSE slot contact: `2/2`.
  - Non-OSE rows with active target contact: `0/6`.
  - Selector candidates: `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - `p75_orange_7` mirrors into `S6,O5,E7`; `p75_orange_8` mirrors into `S6`.
  - Fingerprint: `p75Hi=8|oseHi=2|oseP76Hi=0/2|oseActive=0/2|oseSlots=2/2|nonOseActive=0/6|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The stable `OSE` signal is explained by lower OVERDOSE slot-band geometry.
  - It does not land on locked page-76 targets and does not create a highlight/read selector.
  - Frontier now records `236` focused local checks.

### Current PDF OSE Highlight Translation Rescue Gate

- Status: checked; no small single translation rescues the OSE source highlights onto active page-76 targets.
- Evidence:
  - `scripts/audit_current_pdf_ose_highlight_translation_rescue_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ose_highlight_translation_rescue_gate/current_pdf_ose_highlight_translation_rescue_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ose_highlight_translation_rescue_gate/current_pdf_ose_highlight_translation_rescue_gate.json`
  - `analysis_outputs/source_audit/current_pdf_ose_highlight_translation_rescue_gate/current_pdf_ose_highlight_translation_rescue_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Tested whether the two mirrored OSE page-75 source-highlight boxes can be globally translated onto the locked O4/B4/G5/O5 page-76 active targets.
  - This is a bounded scan-slip/registration check only; no key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Source highlights / active targets: `2` / `4`.
  - Natural active coverage: `0/4`.
  - Best active coverage within `160px`: `0/4`.
  - Best active coverage within `320px`: `1/4`.
  - The first possible active hit needs `dx=0`, `dy=-190`, `Linf=190` onto `O4`.
  - Two-target coverage needs `dx=-928`, `dy=0`, `Linf=928` onto `B4,G5`.
  - Three-target and four-target translation coverage are impossible with the two OSE boxes.
  - Selector candidates / source-backed R3 hits / satisfied triggers: `0` / `0` / `0/9`.
  - Fingerprint: `sources=2|targets=4|natural=0|small160=0|moderate320=1|oneLinf=190.0|twoLinf=928.0|threePossible=0|fourPossible=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The OSE source-highlight geometry cannot be rescued as an active-target selector by a plausible single scan offset.
  - Keep OSE as slot-band provenance only unless a new clue names a non-arbitrary transform/read order.
  - Frontier now records `237` focused local checks.

### Current PDF Held-to-Light All-Target Phrase Gate

- Status: checked; all-target held-to-light source phrasing does not supply a selector.
- Evidence:
  - `scripts/audit_current_pdf_held_to_light_all_target_phrase_gate.py`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_all_target_phrase_gate/current_pdf_held_to_light_all_target_phrase_gate.md`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_all_target_phrase_gate/current_pdf_held_to_light_all_target_phrase_gate.json`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_all_target_phrase_gate/current_pdf_held_to_light_all_target_phrase_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Traced all O4/B4/G5/O5 active boxes through the four fixed PDF held-to-light orientations, then assembled page-75 source words in active order.
  - This closes the full-quartet source-phrase gap left by the earlier threshold-crossing held-to-light source trace.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - PDFs / transforms / variants: `3` / `4` / `12`.
  - All-four source-word variants: `6`.
  - Target rows with source words / source-word hits: `39` / `102`.
  - Strict instruction rows / action-order rows: `0` / `0`.
  - Context rows / hits: `6` / `6`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - `magazine.pdf` physical-back mirror is incomplete: `O4=Buterin came up with`, `B4=` blank, `G5=experience.`, `O5=for the gullible and unloved.`
  - All-four phrase rows occur only in orientation controls and read as ordinary page-75 prose fragments, not instructions.
  - Fingerprint: `pdfs=3|transforms=4|variants=12|targetRows=48|allFourWords=6|wordRows=39|words=102|strictRows=0|strict=0|actionRows=0|action=0|contextRows=6|context=6|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not use all-target held-to-light page-75 phrasing as a selector.
  - The next useful move is still a distinct original-layout/source asset or raw clue wording that names transform, unit, and read order.
  - Frontier now records `238` focused local checks.

### Current PDF Held-to-Light Color Phrase Gate

- Status: checked; active color order does not supply a held-to-light source selector.
- Evidence:
  - `scripts/audit_current_pdf_held_to_light_color_phrase_gate.py`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_color_phrase_gate/current_pdf_held_to_light_color_phrase_gate.md`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_color_phrase_gate/current_pdf_held_to_light_color_phrase_gate.json`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_color_phrase_gate/current_pdf_held_to_light_color_phrase_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Reused the fixed all-target PDF held-to-light source-word trace and grouped active target words by `Y/orange` and `K/black` orderings.
  - Tested active order, `Y` then `K`, `K` then `Y`, orange then black, and black then orange stream mechanics.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Variants / stream rows: `12` / `60`.
  - All-four source-word variants imported: `6`.
  - Populated stream rows / all-four populated stream rows: `60` / `30`.
  - Source-word hits: `510`.
  - Strict instruction hits / action-order hits: `0` / `0`.
  - Context-term hits: `30`.
  - Color selector candidates / source-backed R3 hits / satisfied triggers: `0` / `0` / `0/9`.
  - Fingerprint: `variants=12|streams=60|allFourWords=6|populatedStreams=60|allFourStreams=30|words=510|strict=0|action=0|context=30|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Color grouping changes ordinary page-75 prose order but adds no unit, order, or action wording.
  - Keep `YKKY` / `OBBO` as a source-validation fingerprint, not as an extraction rule.
  - Frontier now records `239` focused local checks.

### Current PDF Held-to-Light Component Readability Gate

- Status: checked; exact PDF held-to-light residue does not form a usable readable extraction layer.
- Evidence:
  - `scripts/audit_current_pdf_held_to_light_component_readability_gate.py`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_component_readability_gate/current_pdf_held_to_light_component_readability_gate.md`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_component_readability_gate/current_pdf_held_to_light_component_readability_gate.json`
  - `analysis_outputs/source_audit/current_pdf_held_to_light_component_readability_gate/current_pdf_held_to_light_component_readability_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Checked only threshold-crossing exact PDF-native held-to-light rows, then classified source-only residue by connected components, clean letter-like shapes, edge dominance, and source-word/instruction trace.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Candidate rows / active rows / OVERDOSE-slot rows: `23` / `15` / `8`.
  - Source-only component rows / components: `23` / `203`.
  - Letter-like / clean letter-like components: `168` / `122`.
  - Visual-readable-like rows: `5`.
  - Merged or edge-dominated rows: `18`.
  - Source-word rows / hits: `19` / `110`.
  - Strict instruction hits / selector candidates: `0` / `0`.
  - Source-backed R3 hits / satisfied triggers: `0` / `0/9`.
  - Fingerprint: `rows=23|active=15|slots=8|componentRows=23|components=203|letterlike=168|clean=122|visualRows=5|mergedRows=18|wordRows=19|words=110|strict=0|context=5|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Some residue rows are visually readable-like, but they trace to ordinary page-75 prose and provide no unit/order/action wording.
  - Rows with the most residue are merged or edge-dominated, so this does not supply a robust held-to-light extraction layer.
  - Frontier now records `240` focused local checks.

### Current PDF JPEG Entropy Tail Gate

- Status: checked; embedded JPEG entropy/tail structure is provenance only, not a selector.
- Evidence:
  - `scripts/audit_current_pdf_jpeg_entropy_tail_gate.py`
  - `analysis_outputs/source_audit/current_pdf_jpeg_entropy_tail_gate/current_pdf_jpeg_entropy_tail_gate.md`
  - `analysis_outputs/source_audit/current_pdf_jpeg_entropy_tail_gate/current_pdf_jpeg_entropy_tail_gate.json`
  - `analysis_outputs/source_audit/current_pdf_jpeg_entropy_tail_gate/current_pdf_jpeg_entropy_tail_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Inspected the current PDFs' embedded page images and thumbnails for entropy-coded byte signatures, SOS/EOI structure, post-EOI tails, restart markers, stuffed bytes, and bounded page-order signatures.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Image rows / page-image rows: `32` / `24`.
  - Entropy signature groups: `24`.
  - Page-76 unique entropy signatures: `1`, limited to the high-resolution `magazine.pdf` page-image lineage.
  - Active-page unique entropy signatures: `4`, a lineage-wide property rather than a page-76 selector.
  - Rows with bytes after EOI: `5`.
  - Tail strict/context rows: `0` / `0`.
  - Unexpected scan-marker rows / restart-marker rows: `0` / `0`.
  - Exact bounded entropy-order matches: `0`.
  - Structural-only signal rows: `10`.
  - Selector candidates / source-backed R3 hits / satisfied triggers: `0` / `0` / `0/9`.
  - Fingerprint: `pdfs=3|images=32|pageImages=24|groups=24|p76Unique=1|activeUnique=4|tails=5|strictTails=0|contextTails=0|unexpected=0|restart=0|orders=0|structural=10|candidates=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The page-76 uniqueness is only a high-resolution lineage artifact, and the short post-EOI tails are non-printable bytes confined to `magazine.pdf`.
  - Do not extend current-PDF binary-wrapper checks unless a materially different source file appears.
  - Frontier now records `241` focused local checks.

### OVERDOSE Style Uniqueness Control Refresh

- Status: checked; generic OVERDOSE house style is downgraded, while Issue 24 body highlights remain validation-only.
- Evidence:
  - `scripts/audit_overdose_style_uniqueness.py`
  - `analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness.md`
  - `analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness.json`
  - `analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness_contact_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Compared Issue 24 with the local Max/OVERDOSE comparison PDFs for recurring branding, dark/color layout, capsule-like marks, and body-highlight behavior.
  - A paper-texture microshift candidate only reproduced the already-closed texture-shift stop-check and was not promoted.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Issue 24 has sustained highlighter-like pages `[3,4,5,6,7,8]` and orange-band pages `[3,4,5,6,7,8]`.
  - Independent comparison PDFs show only partial/isolated highlighter-like pages: `issue26=[4,5]`, `issue27=[1]`, `bitcoin3=[7,8]`.
  - `bitcoin4.pdf` is a lower-quality Issue 24 witness, not an independent article.
  - All comparison PDFs are image-only, so they cannot settle Typeka/font-state extraction.
- Conclusion:
  - Generic `OVERDOSE` styling, dark pages, broad colored art, and capsule-like graphics are house style/provenance, not a selector.
  - Exact Issue 24 orange/grey highlights stay useful for source validation only; no page-76 geometry or extraction unit is supplied.
  - Frontier now records `242` focused local checks and `238` closed/deferred branch bullets.

### Current PDF Thumbnail Active Signal Gate

- Status: checked; the embedded page-76 thumbnail is a blurred preview, not active visual evidence.
- Evidence:
  - `scripts/audit_current_pdf_thumbnail_active_signal_gate.py`
  - `analysis_outputs/source_audit/current_pdf_thumbnail_active_signal_gate/current_pdf_thumbnail_active_signal_gate.md`
  - `analysis_outputs/source_audit/current_pdf_thumbnail_active_signal_gate/current_pdf_thumbnail_active_signal_gate.json`
  - `analysis_outputs/source_audit/current_pdf_thumbnail_active_signal_gate/current_pdf_thumbnail_active_signal_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Compared the `82x106` embedded `magazine.pdf` page-76 thumbnail with a same-size trusted page-image downsample across O4/B4/G5/O5, page-76 highlight controls, and C9/OVERDOSE slots.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Best orientation is `rot180`, with full-thumbnail MAD `15.2525`.
  - Active state matches expected in only `3/4` boxes; O4 shifts from orange in the downsample to black/grey in the thumbnail due to blur.
  - Active/control/slot state changes vs same-size downsample are `1/1/2`.
  - Hidden thumbnail signal candidates / source-backed R3 / selectors: `0` / `0` / `0`.
  - Fingerprint: `thumb=82x106|transform=rot180|mad=15.2525|activeMatch=3/4|activeChanged=1|controlChanged=1|slotChanged=2|activeMinPx=60|maxActiveMad=52.2833|maxSlotMad=36.8774|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Do not use the embedded page-76 thumbnail as a source layer, active target witness, or OVERDOSE-slot selector.
  - Frontier now records `243` focused local checks and `239` closed/deferred branch bullets.

### Current Scan OVERDOSE Glyph Stroke-Centroid Gate

- Status: checked; actual header ink centers do not unlock a selector.
- Evidence:
  - `scripts/audit_current_scan_overdose_glyph_stroke_centroid_gate.py`
  - `analysis_outputs/source_audit/current_scan_overdose_glyph_stroke_centroid_gate/current_scan_overdose_glyph_stroke_centroid_gate.md`
  - `analysis_outputs/source_audit/current_scan_overdose_glyph_stroke_centroid_gate/current_scan_overdose_glyph_stroke_centroid_gate.json`
  - `analysis_outputs/source_audit/current_scan_overdose_glyph_stroke_centroid_gate/current_scan_overdose_glyph_stroke_centroid_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Used the current scan/PDF source material to detect visible orange p76/p78 `OVERDOSE` header ink, split it into stroke components, and project stroke centroids back into the C9 frame.
  - Compared O4/B4/G5/O5 with existing page-76 control rows; no key extraction, hashes, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - p76/p78 headers each produced `8` orange stroke components.
  - Active center stream stayed `OVED`; left/right streams stayed `DOER` / `SVRO`.
  - All-four active any-anchor / center close projections: `0` / `0`.
  - Active close<=16px rows were only `2/4`; controls reached `10` close<=16px rows.
  - Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`.
  - Fingerprint: `headers=2|components=8,8|rows=27|activeClose16=2|controlClose16=10|allFourAny=0|allFourCenter=0|activeP05=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Actual visible `OVERDOSE` stroke centroids are not a better ruler than the already-closed slot/boundary tests.
  - Frontier now records `244` focused local checks and `240` closed/deferred branch bullets.

### Current Scan Header/Footer Lane Registration Gate

- Status: checked; visible article-lane registration does not rescue current-scan held-to-light.
- Evidence:
  - `scripts/audit_current_scan_header_footer_lane_registration_gate.py`
  - `analysis_outputs/source_audit/current_scan_header_footer_lane_registration_gate/current_scan_header_footer_lane_registration_gate.md`
  - `analysis_outputs/source_audit/current_scan_header_footer_lane_registration_gate/current_scan_header_footer_lane_registration_gate.json`
  - `analysis_outputs/source_audit/current_scan_header_footer_lane_registration_gate/current_scan_header_footer_lane_registration_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Registered mirrored source pages to page 76 by top-header, footer, lower-body, header/footer-mean, and natural hflip lanes.
  - Compared valid page 75->76 against invalid source controls `[77,78,79,80]` on O4/B4/G5/O5 only.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Valid lane rows / control rows: `5` / `20`.
  - Best valid mode: `lower_body_lane`.
  - Best valid supported / above-control-p95 count: `3/4` / `0/4`.
  - Max control supported count: `4`.
  - All-four supported lane modes: `[]`.
  - Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`.
  - Fingerprint: `valid=5|controls=20|modes=5|best=lower_body_lane|bestSupport=3/4|bestAboveP95=0/4|bestMean=0.263549|controlMax=4|allFour=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Header/footer/body-lane registration is not a source-backed selector and does not justify reopening current-scan held-to-light extraction.
  - Frontier now records `245` focused local checks and `241` closed/deferred branch bullets.

### Current Scan Lane Affine Registration Gate

- Status: checked; two-lane affine/stretch registration does not rescue current-scan held-to-light.
- Evidence:
  - `scripts/audit_current_scan_lane_affine_registration_gate.py`
  - `analysis_outputs/source_audit/current_scan_lane_affine_registration_gate/current_scan_lane_affine_registration_gate.md`
  - `analysis_outputs/source_audit/current_scan_lane_affine_registration_gate/current_scan_lane_affine_registration_gate.json`
  - `analysis_outputs/source_audit/current_scan_lane_affine_registration_gate/current_scan_lane_affine_registration_gate_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Tested top-header/footer and top-header/lower-body two-anchor affine registration, allowing translation plus x/y scale.
  - Compared valid mirrored page 75->76 against invalid source controls `[77,78,79,80]` on O4/B4/G5/O5 only.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Valid affine rows / control rows: `3` / `13`.
  - Best valid mode: `top_header_lane+lower_body_lane_affine`.
  - Best valid transform: `sx=1.013988`, `sy=1.150444`, `tx=-280.62`, `ty=-39.654`.
  - Best valid supported / above-control-p95 count: `3/4` / `0/4`.
  - Max control supported / above-control-p95 count: `4/4` / `4/4`.
  - All-four valid affine modes: `[]`.
  - Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`.
  - Fingerprint: `valid=3|controls=13|modes=4|best=top_header_lane+lower_body_lane_affine|bestSupport=3/4|bestAboveP95=0/4|bestMean=0.201997|controlMax=4|controlAboveMax=4|allFour=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Simple lane stretch/scale is not a source-backed selector and does not justify reopening current-scan held-to-light extraction.
  - Frontier now records `246` focused local checks and `242` closed/deferred branch bullets.

### Current Scan Lane Affine Source Trace

- Status: checked; page-75 source words behind the affine near miss are ordinary prose, not instruction.
- Evidence:
  - `scripts/audit_current_scan_lane_affine_source_trace.py`
  - `analysis_outputs/source_audit/current_scan_lane_affine_source_trace/current_scan_lane_affine_source_trace.md`
  - `analysis_outputs/source_audit/current_scan_lane_affine_source_trace/current_scan_lane_affine_source_trace.json`
  - `analysis_outputs/source_audit/current_scan_lane_affine_source_trace/current_scan_lane_affine_source_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Traced only the valid page-75 -> page-76 lane-affine rows through O4/B4/G5/O5 using page-75 source words from the 3D article map.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Valid affine modes traced: `3`.
  - Trace rows / source-word rows / source-word hits: `12` / `9` / `51`.
  - Supported rows / above-control-p95 rows: `6` / `0`.
  - Strict instruction rows / hits: `1` / `1`; the lone strict token is unit-only `words` in ordinary prose.
  - Context rows / hits: `0` / `0`.
  - All-four supported modes: `[]`.
  - Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`.
  - Fingerprint: `modes=3|rows=12|wordRows=9|words=51|supported=6|aboveP95=0|strictRows=1|strictHits=1|contextRows=0|contextHits=0|allFour=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The lane-affine 3/4 near miss does not supply unit/order/action evidence.
  - Frontier now records `247` focused local checks and `243` closed/deferred branch bullets.

### Current Scan Active-Envelope Transform Text Trace

- Status: checked; folded/mirrored active-envelope projections land on ordinary page-76 text, not instruction.
- Evidence:
  - `scripts/audit_current_scan_active_envelope_transform_text_trace.py`
  - `analysis_outputs/source_audit/current_scan_active_envelope_transform_text_trace/current_scan_active_envelope_transform_text_trace.md`
  - `analysis_outputs/source_audit/current_scan_active_envelope_transform_text_trace/current_scan_active_envelope_transform_text_trace.json`
  - `analysis_outputs/source_audit/current_scan_active_envelope_transform_text_trace/current_scan_active_envelope_transform_text_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Traced hmirror, vmirror, rot180, and normalized diagonal active-envelope fold/mirror projections onto page-76 OCR words from the current scan/article map.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Transform rows / projected rows: `5` / `20`.
  - Rows with page-76 words / total word hits: `18` / `61`.
  - Strict instruction rows / hits: `0` / `0`.
  - Context rows / hits: `1` / `1`.
  - Target-term rows / hits: `1` / `1`.
  - All-four word-hit modes: `vmirror,rot180,diag_anti`.
  - All-four strict modes: `[]`.
  - Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`.
  - Fingerprint: `transforms=5|rows=20|wordRows=18|words=61|strictRows=0|strictHits=0|contextRows=1|targetRows=1|allFourWords=3|allFourStrict=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The active-envelope fold/mirror projection is not an instruction selector in the current scan.
  - Frontier now records `248` focused local checks and `244` closed/deferred branch bullets.

### Current Scan Active-Envelope Transform Format Trace

- Status: checked; anti-diagonal active-envelope overlap is a weak self-overlap, not a selector.
- Evidence:
  - `scripts/audit_current_scan_active_envelope_transform_format_trace.py`
  - `analysis_outputs/source_audit/current_scan_active_envelope_transform_format_trace/current_scan_active_envelope_transform_format_trace.md`
  - `analysis_outputs/source_audit/current_scan_active_envelope_transform_format_trace/current_scan_active_envelope_transform_format_trace.json`
  - `analysis_outputs/source_audit/current_scan_active_envelope_transform_format_trace/current_scan_active_envelope_transform_format_trace_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Measured full projected-box overlap between active-envelope fold/mirror projections and page-76 active/highlight-control format boxes.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Transform rows / projected rows: `5` / `20`.
  - Active-overlap rows / control-overlap rows: `11` / `1`.
  - All-four active-overlap modes: `diag_anti`.
  - All-four control-overlap modes: `[]`.
  - Diag-anti format stream: `O4-O5-G5-B4` / `orange-orange-black-black`.
  - Diag-anti overlap-vs-projected min/max: `0.129087` / `0.324257`.
  - Strict instruction rows / context rows / target rows from paired text trace: `0` / `1` / `1`.
  - Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`.
  - Fingerprint: `transforms=5|rows=20|activeRows=11|controlRows=1|allFourActive=1|diagAntiMinMax=0.129087/0.324257|strictRows=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The all-four anti-diagonal overlap is a partial active-envelope self-contact, not extraction permission.
  - Frontier now records `249` focused local checks and `245` closed/deferred branch bullets.

### Current Scan Active-Envelope Anti-Diagonal Overlap Control

- Status: checked; the active anti-diagonal near miss is selective but still not extraction permission.
- Evidence:
  - `scripts/audit_current_scan_active_envelope_antidiag_overlap_control.py`
  - `analysis_outputs/source_audit/current_scan_active_envelope_antidiag_overlap_control/current_scan_active_envelope_antidiag_overlap_control.md`
  - `analysis_outputs/source_audit/current_scan_active_envelope_antidiag_overlap_control/current_scan_active_envelope_antidiag_overlap_control.json`
  - `analysis_outputs/source_audit/current_scan_active_envelope_antidiag_overlap_control/current_scan_active_envelope_antidiag_overlap_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Evaluated normalized anti-diagonal self-overlap for every four-box page-76 active/highlight quartet from the current scan/PDF-derived source material.
  - No key extraction, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Page-76 active/highlight boxes / quartets: `11` / `330`.
  - All-four overlap quartets / distinct all-four streams: `42` / `17`.
  - Active quartet rank among all-four / distinct all-four: `1` / `1`.
  - Active quartet stream / kind stream: `O4-O5-G5-B4` / `orange-orange-black-black`.
  - Active quartet min/mean/max overlap-vs-projected: `0.129086526` / `0.208202625` / `0.324256666`.
  - Paired text/format strict rows: `0` / `0`.
  - Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`.
  - Fingerprint: `boxes=11|quartets=330|allFour=42|distinct=17|activeRank=1/1|activeMinMeanMax=0.129086526/0.208202625/0.324256666|strict=0/0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The active quartet is the strongest current page-76 highlighted quartet under anti-diagonal self-overlap.
  - It remains a geometry/provenance near miss only because the overlap is weak, paired text/format strict rows are 0/0, and no source-backed unit/order or reopen trigger exists.
  - Frontier now records `250` focused local checks and `246` closed/deferred branch bullets.

### Current PDF OCR Instruction-Scope Gate

- Status: checked; current PDF OCR/layout text does not supply the missing unit/order rule.
- Evidence:
  - `scripts/audit_current_pdf_ocr_instruction_scope_gate.py`
  - `analysis_outputs/source_audit/current_pdf_ocr_instruction_scope_gate/current_pdf_ocr_instruction_scope_gate.md`
  - `analysis_outputs/source_audit/current_pdf_ocr_instruction_scope_gate/current_pdf_ocr_instruction_scope_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Scanned the three current PDFs' OCR/text overlay tokens across article pages 73-80 for bounded action-plus-unit instruction windows.
  - No OCR-to-key extraction, candidate generation, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - PDFs / pages / OCR tokens: `3` / `24` / `4160`.
  - Action / unit / transform / target term hits: `10` / `10` / `0` / `98`.
  - Action-plus-unit windows / candidate windows: `0` / `0`.
  - Hard phrase hits: `0`.
  - Visible painted text spans / invisible Type3 spans: `0` / `755`.
  - Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`.
  - `magazine.pdf` contributes no strict action/unit/transform terms in this token pass.
  - The duplicate OCR PDFs contain only isolated ordinary terms: `first:3, get:3, look:1, open:1, right:1, words:1`.
  - Fingerprint: `pdfs=3|pages=24|tokens=4160|action=10|unit=10|transform=0|target=98|actionUnitWindows=0|candidates=0|hardPhrases=0|visible=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The current PDF text layer is derivative OCR context, not original-layout instruction evidence.
  - Reopen OCR/layout text only for a distinct source PDF/export or raw clue wording that supplies action plus unit/order.
  - Frontier now records `251` focused local checks and `247` closed/deferred branch bullets.

### Source Packet Highlight Count Slot Permutation Control

- Status: checked; active phrase counts can make tempting fold-world streams only with arbitrary ordering.
- Evidence:
  - `scripts/audit_source_packet_highlight_count_slot_permutation_control.py`
  - `analysis_outputs/source_audit/source_packet_highlight_count_slot_permutation_control/source_packet_highlight_count_slot_permutation_control.md`
  - `analysis_outputs/source_audit/source_packet_highlight_count_slot_permutation_control/source_packet_highlight_count_slot_permutation_control.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Mapped existing active phrase count metrics to the eight `OVERDOSE` slots using zero-based and one-based modulo.
  - Checked canonical active order plus bounded active target permutations against layout streams, hard instruction streams, and known fold-world streams.
  - No OCR-to-key extraction, key candidates, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Metrics / index modes / canonical streams: `10` / `2` / `20`.
  - Canonical layout / instruction / fold-world hits: `0` / `0` / `0`.
  - Interesting permutation rows / fold-world hits / layout hits: `5` / `5` / `0`.
  - All-active center-fit metrics / max active center fit: `0` / `2/4`.
  - Source count-cue hits / source-backed R3 / satisfied triggers / selectors: `0` / `0` / `0/9` / `0`.
  - Canonical one-based `docmHighlightCount` stream is `OVDE`.
  - The five fold-world hits (`OVED,VEDO,DEVO,ODEV,OEVD`) appear only by using one-based `docmHighlightCount` with arbitrary active target permutations.
  - Fingerprint: `metrics=10|indexModes=2|canonical=20|permRows=5|canonLayout=0|canonInstr=0|canonFold=0|permFold=5|permLayout=0|allCenterFit=0|maxCenterFit=2/4|sourceCountCues=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - Phrase counts, character counts, and DOCM highlight counts remain validation descriptors only.
  - Do not use them as an extraction rule unless a source clue names count/length/highlight-count and the target order.
  - Frontier now records `252` focused local checks and `248` closed/deferred branch bullets.

### Source Packet Active Span Bridge Control

- Status: checked; adjacent active spans reproduce only a controlled `OVER` echo.
- Evidence:
  - `scripts/audit_source_packet_active_span_bridge_control.py`
  - `analysis_outputs/source_audit/source_packet_active_span_bridge_control/source_packet_active_span_bridge_control.md`
  - `analysis_outputs/source_audit/source_packet_active_span_bridge_control/source_packet_active_span_bridge_control.json`
  - `analysis_outputs/source_audit/source_packet_active_span_bridge_control/source_packet_active_span_bridge_control_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Joined adjacent active O4/B4/G5/O5 `OVERDOSE` span letters in readable line order and x order, then compared the result against non-active grey single spans and page-adjacent grey control pairs.
  - No OCR-to-key extraction, key candidates, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - Active line pairs / x pairs: `3` / `3`.
  - Active readable-line adjacent streams: `O4+B4=DOSOV`, `B4+G5=OVER`, `G5+O5=ERRDO`.
  - Line exact `OVER` / x exact `OVER` / unique active exact `OVER` pairs: `1` / `1` / `1`.
  - Non-active single-span layout rows / exact `OVER` / exact `OVERDOSE`: `5` / `1` / `1`.
  - Non-active page-adjacent control layout pairs: `6/8`.
  - Source bridge-cue hits / source-backed R3 / satisfied triggers / selectors: `0` / `0` / `0/9` / `0`.
  - Fingerprint: `activeRows=4|nonactiveRows=13|linePairs=3|xPairs=3|lineExactOVER=1|xExactOVER=1|uniqueActiveExactOVER=1|activeLayoutPairs=2|controlPairs=8|controlLayoutPairs=6|controlExactOVER=0|nonactiveSingleLayout=5|nonactiveExactOVER=1|nonactiveExactOVERDOSE=1|bridgeCues=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - B4+G5 is a real exact `OVER` bridge, but it is not selective enough to act as a rule.
  - Treat adjacent span bridging as closed unless new source wording names joining, adjacency, span-bridge order, or another explicit unit/order.
  - Frontier now records `253` focused local checks and `249` closed/deferred branch bullets.

### Current PDF Navigation / Article Thread Gate

- Status: checked; current PDFs do not contain a hidden navigation/read-order carrier.
- Evidence:
  - `scripts/audit_current_pdf_navigation_thread_gate.py`
  - `analysis_outputs/source_audit/current_pdf_navigation_thread_gate/current_pdf_navigation_thread_gate.md`
  - `analysis_outputs/source_audit/current_pdf_navigation_thread_gate/current_pdf_navigation_thread_gate.json`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
    - `analysis_outputs/dead_branch_blacklist.md`
- Scope:
  - Inspected the three current PDFs for outlines/bookmarks, page labels, named destinations, open actions, page modes, article threads, page beads, and page-level navigation keys.
  - No OCR-to-key extraction, key candidates, hash search, seed phrase, WIF, address, BIP39, or broad brute force was run.
- Findings:
  - PDFs / pages: `3` / `24`.
  - TOC entries / outline xrefs / page labels / named destinations: `0` / `0` / `0` / `0`.
  - Catalog navigation signal PDFs / page signal rows / page bead rows: `2` / `0` / `0`.
  - Links / embedded-file names: `0` / `0`.
  - Raw structural token mentions: `6`, all from the duplicate OCR PDFs' empty `/Names`/`/Dests` structure.
  - Strict navigation hits / context hits: `0` / `0`.
  - Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`.
  - Fingerprint: `pdfs=3|pages=24|toc=0|outlines=0|labels=0|dests=0|catalogSignalPdfs=2|pageSignals=0|beads=0|links=0|rawTokens=6|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`.
- Conclusion:
  - The current PDF wrappers do not supply original-layout unit/order metadata.
  - Treat PDF navigation/article-thread metadata as closed unless a distinct original-layout/source PDF appears.
  - Frontier now records `254` focused local checks and `250` closed/deferred branch bullets.

### Scan-Only Source Constraint Refresh

- Status: updated; native/original PDF layer acquisition is no longer a live assumption for the current source set.
- Evidence:
  - User clarification on 2026-05-24: there is no original PDF; all available PDFs are scanned.
  - `scripts/audit_source_reopen_requirements.py`
  - `analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.md`
  - `analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json`
  - `scripts/audit_missing_rule_frontier.py`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
  - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Findings:
  - `magazine.pdf` remains the best current scanned baseline and source-registration witness.
  - Reopen evidence is now framed as physical scan/photo, higher-resolution scanned-source export, or raw clue/provenance wording.
  - Requests for native/original PDF layout layers from the current source set are explicitly listed as not enough to reopen extraction.
  - Frontier highest-value next move is now `new scan/physical/raw-clue asset validation against the source-acquisition packet and readable/upright 3D crop geometry`.
- Conclusion:
  - Stop chasing hidden native PDF layout layers for the known PDFs.
  - Continue only with scan-derived physical/held-to-light evidence or raw clue wording that supplies the missing unit/order/transform.

### Scan-Only Held-To-Light Adjudication

- Status: checked; fixed natural page-75->page-76 held-to-light is not a selector under the current scan.
- Evidence:
  - `scripts/audit_scan_only_held_to_light_adjudication.py`
  - `analysis_outputs/source_audit/scan_only_held_to_light_adjudication/scan_only_held_to_light_adjudication.md`
  - `analysis_outputs/source_audit/scan_only_held_to_light_adjudication/scan_only_held_to_light_adjudication.json`
  - `analysis_outputs/source_audit/scan_only_held_to_light_adjudication/scan_only_held_to_light_adjudication_sheet.jpg`
  - Refreshed frontier:
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.md`
    - `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json`
- Scope:
  - Used only `magazine.pdf` embedded scanned images.
  - Tested the physically valid page 75 back -> page 76 front relation with readable/upright `rot180`, horizontal mirror, and fixed no-shift registration.
  - Included blind overlay, fixed opacities `0.35/0.50/0.65`, source-only ink, sampled controls, and the full 256-control population.
- Findings:
  - Active boxes at or above 10% source-only ink: `0/4`.
  - Active boxes above same-size nearby-control p95: `0/4`.
  - Source-backed R3 unit/order bridge: `0`.
  - Selector unlocked: `False`.
  - Fingerprint: `pair=75->76|opacities=0.35,0.50,0.65|controls=256|activeGe10=0/4|activeGtP95=0/4|sourceR3=0|selectors=0`.
- Adversarial review:
  - Initial reviewer required narrower wording, fuller control visibility, and an unlabeled readability panel.
  - Those fixes were applied; follow-up review found no remaining blocking findings.
- Conclusion:
  - Result: `fail_no_r3_fixed_natural_registration_not_selector`.
  - Keep fixed current-scan light-table output as visual/source-registration evidence only, not extraction permission.
  - Reopen only with a physically new or higher-resolution scan, or raw clue wording that names unit/order/transform.

### Scan-Only Held-To-Light Tolerance Sweep

- Status: checked; bounded page-75->page-76 registration wobble does not rescue held-to-light under the current scan.
- Evidence:
  - `scripts/audit_scan_only_held_to_light_tolerance_sweep.py`
  - `analysis_outputs/source_audit/scan_only_held_to_light_tolerance_sweep/scan_only_held_to_light_tolerance_sweep.md`
  - `analysis_outputs/source_audit/scan_only_held_to_light_tolerance_sweep/scan_only_held_to_light_tolerance_sweep.json`
  - `analysis_outputs/source_audit/scan_only_held_to_light_tolerance_sweep/scan_only_held_to_light_tolerance_sweep_sheet.jpg`
- Scope:
  - Used only `magazine.pdf` embedded scanned images.
  - Kept the physically valid page 75 back -> page 76 front relation, readable `rot180`, horizontal mirror, and a bounded registration grid: dx/dy +/-80 px in 20 px steps plus rotations -1/0/+1 degrees.
  - Scored 243 modes against the locked O4/B4/G5/O5 boxes and all 256 same-size nearby lower-corridor controls.
- Findings:
  - Best mode: `rot=-1.0, dx=-80, dy=-20`.
  - Best active >=10% source-only: `0/4`.
  - Best active above control p95: `0/4`.
  - All-four signal candidate modes / all-four >=10% modes / all-four above-control-p95 modes: `0` / `0` / `0`.
  - Source-backed R3 unit/order bridge: `0`.
  - Selector unlocked: `False`.
  - Fingerprint: `pair=75->76|grid=dxdy+-80x20,rot=-1/0/+1|modes=243|controls=256|all4Signal=0|all4Ge10=0|all4GtP95=0|bestGe10=0/4|bestGtP95=0/4|sourceR3=0|selectors=0`.
- Adversarial review:
  - Blocking findings: `0`.
  - Reviewer accepted the grid, controls, lack of readable instruction, R3 absence, and bounded-scope wording.
  - Visual source-only panel was aligned to the same transformed binary mask used for scoring after review.
- Conclusion:
  - Result: `fail_no_r3_bounded_registration_tolerance_not_selector`.
  - Treat current-scan held-to-light as exhausted for fixed natural registration plus this bounded tolerance window.
  - Do not reopen held-to-light with the same scan unless a new source clue names a unit/order/transform or a materially better physical scan appears.

### Current Gathered Local Source-Reopen Gate

- Status: checked; no already-gathered local source candidate reopens extraction.
- Evidence:
  - `scripts/audit_current_local_source_reopen_gate.py`
  - `analysis_outputs/source_audit/current_local_source_reopen_gate/current_local_source_reopen_gate.md`
  - `analysis_outputs/source_audit/current_local_source_reopen_gate/current_local_source_reopen_gate.json`
  - `analysis_outputs/source_audit/current_local_source_reopen_gate/current_local_source_reopen_gate_sheet.jpg`
- Scope:
  - Checked the known local source inventory, clue/source folders, source images, thread media, and shallow Desktop/Downloads source-like files.
  - This was source triage only, not extraction, hashing, WIF/seed/address testing, or brute force.
  - Generated analysis reports were blocked from R3 authority.
- Findings:
  - Candidates / authority classes: `364` / `16`.
  - Promoted / manual R3 / R3 partial review candidates: `0` / `0` / `0`.
  - Current scan family and derived-current-scan records: `14`.
  - Fingerprint: `candidates=364|promoted=0|manualR3=0|r3Partial=0|classes=16`.
- Adversarial review:
  - Blocking findings: `0`.
  - Reviewer agreed the decision holds for the gathered candidate set.
  - Caveat: this is not a full recursive disk crawl and image OCR was not attempted.
- Conclusion:
  - Result: `no_current_local_source_passes_r1_r5`.
  - Keep already-local files as baseline/provenance/context only.
  - Reopen extraction only if a better physical/source image or raw clue wording supplies R3 unit/order/transform and passes R1-R5.

### Corrected-Topology 77 -> 76 Light-Table Audit

- Status: checked; the proposed page-77-back-of-page-76 branch does not unlock extraction from current scan pixels.
- Evidence:
  - External proposal: `missing_rule_next_experiments.md`
  - `scripts/audit_corrected_topology_77_76_light_table.py`
  - `analysis_outputs/source_audit/corrected_topology_77_76_light_table/corrected_topology_77_76_light_table.md`
  - `analysis_outputs/source_audit/corrected_topology_77_76_light_table/corrected_topology_77_76_light_table.json`
  - `analysis_outputs/source_audit/corrected_topology_77_76_light_table/corrected_topology_77_76_light_table_sheet.jpg`
- Scope:
  - Compared old assumed leaves `(75,76), (77,78), (79,80)` with proposed corrected leaves `(74,75), (76,77), (78,79)` using paper-texture duplex scoring.
  - Tested page 77 white-knockout mask horizontally mirrored onto page 76 across a bounded dx/dy +/-80 px, rotation -1/0/+1 degree grid.
  - Scored locked O4/B4/G5/O5 against 64 same-size nearby controls per target.
- Findings:
  - Paper texture confirmation: `False`; use this as weak/non-confirmation only, not a hard disproof of the topology.
  - Best mode: `hmirror p77 white, rot=-1.0, dx=-40, dy=+0`.
  - All-four signal modes: `0`.
  - Best active >=10% source coverage: `3/4`.
  - Best active above nearby-control p95: `1/4`.
  - Source-backed R3 / selector unlocked: `0` / `False`.
  - Fingerprint: `pair=77->76|whiteMask=0.0798|grid=dxdy+-80x20,rot=-1/0/+1|modes=243|all4Signal=0|bestGe10=3/4|bestGtP95=1/4|paperConfirmed=0|sourceR3=0|selectors=0`.
- Adversarial review:
  - Blocking findings: `0`.
  - Reviewer agreed this closes only the current-pixel extraction branch and leaves physical-copy validation as the fair remaining test.
- Conclusion:
  - Result: `fail_no_target_specific_white_mask_signal`.
  - Do not use current-scan `77 -> 76` white-mask overlay as a selector.
  - Keep the topology proposal open only for a physical copy or materially better source image.

### Open-Heart Capsule Rule Audit

- Status: checked; useful partial selector, not a complete R3/extraction rule.
- Evidence:
  - External proposal: `r3_candidate_rules.md`
  - `scripts/audit_open_heart_capsule_rule.py`
  - `analysis_outputs/source_audit/open_heart_capsule_rule/open_heart_capsule_rule.md`
  - `analysis_outputs/source_audit/open_heart_capsule_rule/open_heart_capsule_rule.json`
  - `analysis_outputs/source_audit/open_heart_capsule_rule/open_heart_capsule_rule_sheet.jpg`
- Scope:
  - Tested the O-K-K-O capsule idea: orange span as cap, black span as body, and the canonical bridge between the two black spans as payload.
  - Compared against visual/body-highlighter quartet windows, adjacent K-K bridge controls, existing Y/K quartet controls, and source-packet reopen triggers.
  - No extraction, hashing, WIF/seed/address testing, BIP39 checks, or brute force was run.
- Findings:
  - Visual quartet windows / OBBO windows / independent-control OBBO windows: `34` / `3` / `0`.
  - Existing broader Y/K controls: `70` full-page combinations, `11` YKKY combinations, `1` contiguous sliding YKKY window.
  - Active bridge text: `in bitcoin — that he should sell billions worth of future bitcoin earnings collateralized`.
  - Active bridge words: `13`.
  - Max non-active OBBO bridge words / adjacent K-K bridge words: `0` / `2`.
  - Source-backed R3 / reopen triggers / selector unlocked: `0` / `0/9` / `False`.
  - Fingerprint: `visualQuartets=34|obbo=3|issue24Obbo=3|indObbo=0|activeBridgeWords=13|maxNonactiveObboBridgeWords=0|maxAdjacentKkBridgeWords=2|uniqueBridge=1|sourceR3=0|triggers=0/9|selector=0`.
- Adversarial review:
  - Agreed the active bridge is a bounded real outlier in current visual/highlighter controls.
  - Agreed it remains article-context convergence only: `should sell`, `bitcoin`, and `collateralized`, with no source-backed word/letter/line/order instruction.
  - Caveats: the proposal's referenced `715-quartet` falsifier was not located/run here, and the MAX-heart-KEISER marker claim was not independently adjudicated in this pass.
- Conclusion:
  - Result: `partial_unique_selector_no_downstream_r3`.
  - Keep the rule as a target/source-validation clue for page 76 O4/B4/G5/O5.
  - Do not use it to resume key/seed/address extraction unless a new source explicitly names how to read, take, count, or order the selected bridge.

# Source word geometry · 10 November 2026

This is a source-reading repair, before cipher selection. The frozen model covers all 142 canonical printed rows and 1,243 lexical words on pages 75–79. Fifteen standalone punctuation tokens remain separate. It contains the raw OCR, exact canonical tokens, alignment alternatives, approximate word boxes, confidence and seven explicit visual adjudications. It performs no target extraction or key checks.

The source authority is `printed-lines.json`, not OCR. Machine matches require a unique normalized token match across every optimal monotonic edit alignment. Case and punctuation differences are retained. Seven remaining character confusions were reviewed against source pixels; their original OCR and decisions are preserved. `verified` describes that source mapping. It does not mean human verification, original font metadata, or calibrated physical certainty.

| Artifact | SHA-256 |
| --- | --- |
| `word-geometry-20261110.json` | `e3348d0d60d3097b05d0afdb0a1fccf66409274408af9ae7a9369c37fe596e9f` |
| `word-geometry-adjudications-20261110.json` | `0c06a877c46f98fe3b962dedf278d9993b95b35123cf88688b66b0c36cc7b1cc` |
| `word-geometry-review-20261110.png` | `2704a672e1b07d9ec3fd262d7229dd81202cfd17503bdb2fd373fb1ab9550882` |

Every box uses top-left pixel coordinates in a 2544 × 3264 row-specific frame. Extract the exact embedded JPEG, rotate it 180° upright, then use the canonical locator's fixed-center rotation. Page 79's first paragraph uses 2.5° counterclockwise, nearest-neighbor sampling, white fill and no canvas expansion. Other rows use 0°. `originalUprightPolygon` maps back to the upright page. A word center must be inverse-rotated before comparing it with an original-page mask.

## Reproduce the source preflight

Run from the public research directory on macOS with Python, Pillow, PyMuPDF, Swift and Apple Vision. Use a fresh local output directory. The commands below read only the public source files and create local source artifacts; they do not run the puzzle tests.

```sh
python3 -m venv /tmp/key404-word-source-venv
/tmp/key404-word-source-venv/bin/pip install Pillow PyMuPDF
work=/tmp/key404-word-source-replay
mkdir "$work"
swiftc -O scripts/batch20_vision.swift -o "$work/vision-reader"
py=/tmp/key404-word-source-venv/bin/python
"$py" scripts/prepare_word_geometry_20261110.py --corpus . --out "$work/pass1"
"$work/vision-reader" --manifest "$work/pass1/jobs.json" --out "$work/pass1/vision.json"
"$py" scripts/align_word_geometry_20261110.py --input "$work/pass1" --out "$work/pass1/word-geometry-dedup.json"
"$py" scripts/assemble_word_geometry_20261110.py --prepare-second-pass --first "$work/pass1" --out "$work/pass2"
"$work/vision-reader" --manifest "$work/pass2/jobs.json" --out "$work/pass2/vision.json"
"$py" scripts/align_word_geometry_20261110.py --input "$work/pass2" --out "$work/pass2/word-geometry-dedup.json"
"$py" scripts/assemble_word_geometry_20261110.py --first "$work/pass1" --second "$work/pass2" --corpus . --out "$work/word-geometry.json"
shasum -a 256 "$work/word-geometry.json"
```

The first pass has 142 native-resolution full-width row crops with 12 pixels of vertical padding. The second pass has three fixed representations of 18 fixed rows: gray autocontrast, black ink below luminance 110, and white ink above luminance 175, each at 2× scale. These rows were chosen by source-recognition ambiguity before duplicate OCR observations were merged. The helper fixes that list; it does not choose rows by cipher output. A whole-row choice maximizes exact lexical matches, then minimizes edit distance, then maximizes all-token matches. Equal scores prefer the original view, then gray, black, white.

The assembler applies the seven frozen visual decisions only when each canonical token, unique OCR substitution, OCR identifier and box exactly matches its recorded decision. A mismatch stops assembly for a new source review. It never guesses a replacement box. The frozen artifact is the registered experiment input: Apple Vision and image-library versions can change regenerated observations, so a fresh run is not automatically equivalent. The original engine metadata is inside the frozen file. Replaying the recorded OCR through these helpers reproduced the exact frozen SHA-256; both preparation stages reproduced their original source crops byte-for-byte.

Vision's range boxes are approximate. The per-word center guard is a review aid, not a calibrated error bound; some guards exceed 12 pixels. Pixel spacing and baseline experiments must measure actual ink and handle clipped or ambiguous regions explicitly. Keep any regenerated local outputs separate until their source coverage and differences have been reviewed.

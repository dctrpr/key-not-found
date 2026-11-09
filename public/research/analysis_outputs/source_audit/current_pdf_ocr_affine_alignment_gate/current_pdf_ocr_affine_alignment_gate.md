# Current PDF OCR Affine Alignment Gate

Scope: fit page-76 PDF OCR word coordinates to the high-resolution 3D word map and test aligned OCR words against O4/B4/G5/O5. This checks OCR-layer misregistration only; no key derivation, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.

- Created: `2026-05-21T15:33:03`
- PDFs checked: `3`
- Fits available: `2`
- Token pairs / inliers: `268` / `268`
- Target word-hit rows after alignment: `6`
- Target exact-component rows after alignment: `0`
- Target strict-instruction rows after alignment: `0`
- Strict instruction terms after alignment: `-`
- Minimum component distance to its own target box: `42.205` px
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_ocr_affine_alignment_gate/current_pdf_ocr_affine_alignment_gate_sheet.jpg`
- Fingerprint: `pdfs=3|fits=2|pairs=268|inliers=268|targetWordRows=6|targetComponentRows=0|targetStrictRows=0|strictAfter=-|minCompDist=42.205|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | words | pairs | inliers | median residual | target word rows | component rows | strict rows | nearest component distance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `magazine.pdf` | `239` | `0` | `0` | `None` | `0/4` | `0/4` | `0/4` | `-` |
| `keyser bitcoin .pdf` | `263` | `134` | `134` | `0.002` | `3/4` | `0/4` | `0/4` | `42.205` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `263` | `134` | `134` | `0.002` | `3/4` | `0/4` | `0/4` | `42.205` |

## Target Rows

### `magazine.pdf`

- Fit unavailable: `too_few_token_pairs` with `0` token pairs.

### `keyser bitcoin .pdf`

- O4 `buying the dip` aligned words: `ByiiREeraipy"`; components: `-`; strict: `-`
- B4 `$1 billion` aligned words: `eis`; components: `-`; strict: `-`
- G5 `Volcano Bonds` aligned words: `-`; components: `-`; strict: `-`
- O5 `shitcoiner at heart` aligned words: `siukbeodmensertslveaarty`; components: `-`; strict: `-`
- O4 nearest `buying` component after alignment: `buying` at `1259.195` px; inside target: `False`
- B4 nearest `billion` component after alignment: `billions` at `42.205` px; inside target: `False`
- G5 nearest `volcano` component after alignment: `volcanoes` at `230.502` px; inside target: `False`
- O5 nearest `shitcoiner` component after alignment: `shitcoiners'` at `1860.785` px; inside target: `False`
- O5 nearest `heart` component after alignment: `heart` at `2559.157` px; inside target: `False`

### `analysis_outputs/external_clues/google_drive_article_download.pdf`

- O4 `buying the dip` aligned words: `ByiiREeraipy"`; components: `-`; strict: `-`
- B4 `$1 billion` aligned words: `eis`; components: `-`; strict: `-`
- G5 `Volcano Bonds` aligned words: `-`; components: `-`; strict: `-`
- O5 `shitcoiner at heart` aligned words: `siukbeodmensertslveaarty`; components: `-`; strict: `-`
- O4 nearest `buying` component after alignment: `buying` at `1259.195` px; inside target: `False`
- B4 nearest `billion` component after alignment: `billions` at `42.205` px; inside target: `False`
- G5 nearest `volcano` component after alignment: `volcanoes` at `230.502` px; inside target: `False`
- O5 nearest `shitcoiner` component after alignment: `shitcoiners'` at `1860.785` px; inside target: `False`
- O5 nearest `heart` component after alignment: `heart` at `2559.157` px; inside target: `False`

## Decision

- Do not reopen PDF OCR alignment as a selector.
- The low-resolution duplicate PDFs can be geometrically fit back onto the high-resolution word map, but the aligned OCR layer still does not put exact active target components or strict unit/order terms into the O4/B4/G5/O5 boxes.
- The high-resolution `magazine.pdf` OCR text is too corrupt/rotated to provide enough unique word correspondences for a useful fit.

## Next Move

- Treat OCR-layer coordinate repair as closed. Future useful work remains source-intake/reopen-gate validation unless new physical/original-layout/source evidence arrives.

# Current PDF B4 Contact Pixel Provenance Gate

Scope: sampled the exact B4 broad-contact source point across current PDF embedded page images and 300dpi renders, then rebuilt the all-content page-75 -> page-76 landing. This checks PDF/render provenance only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T11:43:43+02:00`
- PDFs / candidates: `3` / `6`
- Source point / target landing point: `[1864, 2511]` / `[711, 2450]`
- Source point broad / feature candidates: `6` / `4`
- Landing point broad / feature candidates: `6` / `4`
- Radius-32 feature contact candidates: `4`
- Render-only feature/contact candidates: `2`
- Baseline / magazine embedded source RGB: `[242, 242, 242]` / `[243, 243, 243]`
- Hidden PDF render contact candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_b4_contact_pixel_provenance_gate/current_pdf_b4_contact_pixel_provenance_gate_sheet.jpg`
- Fingerprint: `pdfs=3|candidates=6|srcBroad=6|srcFeature=4|landBroad=6|landFeature=4|r32Feature=4|magEmbRgb=[243, 243, 243]|baseRgb=[242, 242, 242]|renderOnlyFeature=2|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Candidate Rows

| PDF | kind | orientation | source RGB | source layers | landing RGB | landing layers | r32 broad | r32 feature | source delta | embedded delta | verdict |
|---|---|---|---|---|---|---|---:|---:|---:|---:|---|
| `magazine.pdf` | `embedded` | `rotate180` | `[243, 243, 243]` | `broad` | `[243, 243, 243]` | `broad` | `1` | `0` | `1` | `1` | `broad_background_only` |
| `magazine.pdf` | `render_300dpi` | `as_is` | `[243, 243, 243]` | `broad` | `[243, 243, 243]` | `broad` | `1` | `0` | `1` | `0` | `broad_background_only` |
| `keyser bitcoin .pdf` | `embedded` | `as_is` | `[217, 223, 223]` | `grey,feature,broad` | `[217, 223, 223]` | `grey,feature,broad` | `23936` | `22445` | `25` | `25` | `feature_contact_created` |
| `keyser bitcoin .pdf` | `render_300dpi` | `as_is` | `[222, 228, 228]` | `grey,feature,broad` | `[222, 228, 228]` | `grey,feature,broad` | `23936` | `23362` | `20` | `5` | `feature_contact_created` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `embedded` | `as_is` | `[217, 223, 223]` | `grey,feature,broad` | `[217, 223, 223]` | `grey,feature,broad` | `23936` | `22445` | `25` | `25` | `feature_contact_created` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `render_300dpi` | `as_is` | `[222, 228, 228]` | `grey,feature,broad` | `[222, 228, 228]` | `grey,feature,broad` | `23936` | `23362` | `20` | `5` | `feature_contact_created` |

## Decision

- `current_pdf_b4_contact_pixel_background_carrier`
- The byte-locked `magazine.pdf` embedded/render carrier keeps the sampled B4 point broad/background only, not feature ink.
- The feature-colored rows come from duplicate/lower-resolution PDF carriers; they are provenance warnings, not selectors.
- No render-only candidate creates a source-backed R3 bridge.
- This keeps current-PDF rendering closed for the B4 broad rescue.

## Next Move

- Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.

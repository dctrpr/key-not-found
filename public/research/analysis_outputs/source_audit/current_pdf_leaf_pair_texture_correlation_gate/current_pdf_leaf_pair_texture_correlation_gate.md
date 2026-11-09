# Current PDF Leaf-Pair Texture Correlation Gate

Scope: compared embedded PDF page-image texture for article leaf pairs 75/76, 77/78, and 79/80 under four fixed orientation hypotheses, including the natural physical back-side mirror. This is source/provenance validation only; no OCR-to-key extraction, key candidates, hashes, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T16:06:23`
- Decision: `current_pdf_leaf_pair_texture_correlation_no_selector`
- PDFs / leaf pairs / transforms / variant rows: `3` / `9` / `4` / `36`
- Active-box rows / above control p95 / all-four above p95 variants: `144` / `17` / `1`
- Physical-back mirror best pair rows: `0` / `9`
- Page 75/76 physical-back mirror best rows: `0` / `3`
- Max page 75/76 physical active-region correlation / feature IoU: `-0.0158` / `0.0500`
- Max active-box feature IoU / active-box correlation: `0.9550` / `0.2029`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_leaf_pair_texture_correlation_gate/current_pdf_leaf_pair_texture_correlation_gate_sheet.jpg`
- Fingerprint: `pdfs=3|pairs=9|transforms=4|rows=36|activeRows=144|activeP95=17|allFourP95=1|physBest=0|p7576PhysBest=0/3|p7576PhysCorrMax=-0.0158|p7576PhysIouMax=0.0500|activeIouMax=0.9550|activeCorrMax=0.2029|sourceR3=0|triggers=0/9|selectors=0`

## Pair Rows

| PDF | pair | transform | active-region corr | active-region IoU | full corr | active boxes >p95 | all-four >p95 | IoU>=10 | best for pair |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `75/76` | `same_side_no_mirror` | -0.0073 | 0.0550 | -0.1041 | 0 | 0 | 0 | 1 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `75/76` | `back_mirror_rotate180` | -0.0443 | 0.0572 | -0.1364 | 0 | 0 | 1 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `75/76` | `front_rotate180` | -0.0686 | 0.0543 | 0.0857 | 0 | 0 | 0 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `75/76` | `physical_back_mirror` | -0.1466 | 0.0354 | 0.1210 | 0 | 0 | 0 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `77/78` | `front_rotate180` | 0.1026 | 0.1843 | -0.1620 | 1 | 0 | 2 | 1 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `77/78` | `back_mirror_rotate180` | -0.1166 | 0.1768 | -0.4080 | 1 | 0 | 2 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `77/78` | `physical_back_mirror` | -0.0918 | 0.1650 | -0.0462 | 1 | 0 | 2 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `77/78` | `same_side_no_mirror` | -0.0158 | 0.1772 | -0.3035 | 1 | 0 | 2 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `79/80` | `back_mirror_rotate180` | 0.1348 | 0.0797 | 0.2177 | 0 | 0 | 1 | 1 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `79/80` | `front_rotate180` | 0.0822 | 0.0820 | 0.0640 | 1 | 0 | 3 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `79/80` | `physical_back_mirror` | 0.0868 | 0.2253 | -0.0526 | 0 | 0 | 3 | 0 |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `79/80` | `same_side_no_mirror` | 0.0193 | 0.2039 | 0.2299 | 0 | 0 | 2 | 0 |
| `keyser bitcoin .pdf` | `75/76` | `same_side_no_mirror` | -0.0073 | 0.0550 | -0.1041 | 0 | 0 | 0 | 1 |
| `keyser bitcoin .pdf` | `75/76` | `back_mirror_rotate180` | -0.0443 | 0.0572 | -0.1364 | 0 | 0 | 1 | 0 |
| `keyser bitcoin .pdf` | `75/76` | `front_rotate180` | -0.0686 | 0.0543 | 0.0857 | 0 | 0 | 0 | 0 |
| `keyser bitcoin .pdf` | `75/76` | `physical_back_mirror` | -0.1466 | 0.0354 | 0.1210 | 0 | 0 | 0 | 0 |
| `keyser bitcoin .pdf` | `77/78` | `front_rotate180` | 0.1026 | 0.1843 | -0.1620 | 1 | 0 | 2 | 1 |
| `keyser bitcoin .pdf` | `77/78` | `back_mirror_rotate180` | -0.1166 | 0.1768 | -0.4080 | 1 | 0 | 2 | 0 |
| `keyser bitcoin .pdf` | `77/78` | `physical_back_mirror` | -0.0918 | 0.1650 | -0.0462 | 1 | 0 | 2 | 0 |
| `keyser bitcoin .pdf` | `77/78` | `same_side_no_mirror` | -0.0158 | 0.1772 | -0.3035 | 1 | 0 | 2 | 0 |
| `keyser bitcoin .pdf` | `79/80` | `back_mirror_rotate180` | 0.1348 | 0.0797 | 0.2177 | 0 | 0 | 1 | 1 |
| `keyser bitcoin .pdf` | `79/80` | `front_rotate180` | 0.0822 | 0.0820 | 0.0640 | 1 | 0 | 3 | 0 |
| `keyser bitcoin .pdf` | `79/80` | `physical_back_mirror` | 0.0868 | 0.2253 | -0.0526 | 0 | 0 | 3 | 0 |
| `keyser bitcoin .pdf` | `79/80` | `same_side_no_mirror` | 0.0193 | 0.2039 | 0.2299 | 0 | 0 | 2 | 0 |
| `magazine.pdf` | `75/76` | `same_side_no_mirror` | 0.0764 | 0.1154 | 0.0731 | 4 | 1 | 4 | 1 |
| `magazine.pdf` | `75/76` | `back_mirror_rotate180` | 0.0410 | 0.0795 | 0.0261 | 0 | 0 | 2 | 0 |
| `magazine.pdf` | `75/76` | `front_rotate180` | 0.0276 | 0.0704 | 0.0252 | 1 | 0 | 1 | 0 |
| `magazine.pdf` | `75/76` | `physical_back_mirror` | -0.0158 | 0.0500 | 0.0595 | 2 | 0 | 2 | 0 |
| `magazine.pdf` | `77/78` | `same_side_no_mirror` | 0.1017 | 0.1745 | -0.0136 | 0 | 0 | 1 | 1 |
| `magazine.pdf` | `77/78` | `back_mirror_rotate180` | -0.0841 | 0.1578 | -0.0729 | 0 | 0 | 1 | 0 |
| `magazine.pdf` | `77/78` | `front_rotate180` | -0.0309 | 0.1645 | -0.0486 | 0 | 0 | 1 | 0 |
| `magazine.pdf` | `77/78` | `physical_back_mirror` | -0.1083 | 0.1555 | -0.0399 | 0 | 0 | 1 | 0 |
| `magazine.pdf` | `79/80` | `front_rotate180` | 0.1317 | 0.1631 | 0.0092 | 0 | 0 | 2 | 1 |
| `magazine.pdf` | `79/80` | `back_mirror_rotate180` | 0.1232 | 0.1735 | 0.0167 | 0 | 0 | 2 | 0 |
| `magazine.pdf` | `79/80` | `physical_back_mirror` | 0.0486 | 0.0857 | 0.0016 | 0 | 0 | 1 | 0 |
| `magazine.pdf` | `79/80` | `same_side_no_mirror` | 0.0240 | 0.0965 | -0.0037 | 0 | 0 | 1 | 0 |

## Decision

- `current_pdf_leaf_pair_texture_correlation_no_selector`.
- Physical back-side mirror is not a distinctive all-pair or all-target registration signal in the current PDFs.
- Page 75/76 can show ordinary page-text texture correlation in derivative PDFs, but it does not create an all-four active-box outlier above same-size controls and does not supply unit/order wording.
- Treat this as another source/provenance stop-check, not a selector.

## Next Move

- Keep local PDF leaf-pair texture/correlation mechanics closed unless a distinct physical/original-layout source appears or raw clue wording names the transform, unit, and read order.

# Current PDF OVERDOSE Slot Source-Support Trace

Scope: current PDF carriers only. For each PDF, the visible render and embedded page-image canvas for pages `75` and `76` were normalized to the same upright 2544x3264 page geometry, then the valid `75 -> 76` mirror was measured across projected OVERDOSE slots. No OCR-to-key extraction, candidates, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-24T17:03:10`
- Carrier rows: `6`
- Rows matching current-scan high run: `2/6`
- Magazine render/embedded high run: `OSE@5-7` / `OSE@5-7`
- Total action/order instruction hits: `0`
- High-slot action/order instruction hits: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `carriers=6|scanRun=OSE@5-7|match=2/6|magRender=OSE@5-7|magEmbedded=OSE@5-7|actionOrder=0|highActionOrder=0|sourceR3=0|triggers=0/9|selectors=0`

## Carrier Rows

| pdf | carrier | p75 orientation | p76 orientation | high slots | high run | action/order | unit-only | context |
|---|---|---|---|---|---|---:|---|---|
| `magazine.pdf` | `render` | `as_is` | `as_is` | `O5,S6,E7` | `OSE@5-7` | 0 | `words` | `bitcoin, bitcoins` |
| `magazine.pdf` | `embedded_canvas` | `rotate180` | `rotate180` | `O5,S6,E7` | `OSE@5-7` | 0 | `words` | `bitcoin, bitcoins` |
| `keyser bitcoin .pdf` | `render` | `as_is` | `as_is` | `O0,V1,E2,R3,D4,O5,S6,E7` | `OVERDOSE@0-7` | 0 | `words` | `bitcoin, bitcoins` |
| `keyser bitcoin .pdf` | `embedded_canvas` | `as_is` | `as_is` | `O0,V1,E2,R3,D4,O5,S6,E7` | `OVERDOSE@0-7` | 0 | `words` | `bitcoin, bitcoins` |
| `google_drive_article_download.pdf` | `render` | `as_is` | `as_is` | `O0,V1,E2,R3,D4,O5,S6,E7` | `OVERDOSE@0-7` | 0 | `words` | `bitcoin, bitcoins` |
| `google_drive_article_download.pdf` | `embedded_canvas` | `as_is` | `as_is` | `O0,V1,E2,R3,D4,O5,S6,E7` | `OVERDOSE@0-7` | 0 | `words` | `bitcoin, bitcoins` |

## Slot Source Shares

| pdf/carrier | O0 | V1 | E2 | R3 | D4 | O5 | S6 | E7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `magazine.pdf / render` | `4.3e-05` | `0.020231` | `0.328525` | `0.418767` | `0.475779` | `0.668075` | `0.94643` | `0.789242` |
| `magazine.pdf / embedded_canvas` | `5.8e-05` | `0.020368` | `0.330454` | `0.417839` | `0.475935` | `0.667914` | `0.950425` | `0.79334` |
| `keyser bitcoin .pdf / render` | `1.0` | `0.999964` | `0.999849` | `0.999511` | `0.999607` | `0.999915` | `0.999966` | `0.996562` |
| `keyser bitcoin .pdf / embedded_canvas` | `1.0` | `0.99949` | `0.998702` | `0.997419` | `0.997631` | `0.999062` | `0.998385` | `0.992373` |
| `google_drive_article_download.pdf / render` | `1.0` | `0.999964` | `0.999849` | `0.999511` | `0.999607` | `0.999915` | `0.999966` | `0.996562` |
| `google_drive_article_download.pdf / embedded_canvas` | `1.0` | `0.99949` | `0.998702` | `0.997419` | `0.997631` | `0.999062` | `0.998385` | `0.992373` |

## Decision

- `pdf_overdose_slot_source_support_matches_scan_but_no_selector`.
- Reason: The byte-locked PDF render and embedded page-image canvas reproduce the same high OSE source-support run as the current scan, but action/order instruction hits remain 0 and source-backed R3 remains absent.
- Next move: Treat PDF-native OVERDOSE slot source support as a stable page-75 text-band control, not an extraction path; the next useful move needs new source/clue material with unit, transform, and read order.

Sheet: `analysis_outputs/source_audit/current_pdf_overdose_slot_source_support_trace/current_pdf_overdose_slot_source_support_trace_sheet.jpg`

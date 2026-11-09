# Current PDF OCR OVERDOSE Index Offset Gate

Scope: inspected hidden PDF OCR `OVERDOSE` word index plus/minus existing active line, corridor, and slot units. No OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T14:06:24`
- PDFs checked: `3`
- PDFs with OCR `OVERDOSE`: `2`
- Offset landing rows checked: `46`
- Target-component offset hits: `2`
- Strict instruction offset hits: `0`
- PDFs where all four component deltas match their own known units: `0`
- Hidden OVERDOSE index candidates: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_ocr_overdose_index_offset_gate/current_pdf_ocr_overdose_index_offset_gate_sheet.jpg`
- Fingerprint: `pdfs=3|overdosePdfs=2|offsetRows=46|targetHits=2|strictHits=0|allFourKnownDelta=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | words | OVERDOSE indexes | component order | component deltas | target hits | strict hits | candidate |
|---|---:|---|---|---|---:|---:|---:|
| `magazine.pdf` | `245` | `-` | `-` | `-` | `0` | `0` | `0` |
| `keyser bitcoin .pdf` | `265` | `[0]` | `O5-O4-G5-B4` | `O4:81 own=0; B4:209 own=0; G5:198 own=0; O5:9 own=0` | `1` | `0` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `265` | `[0]` | `O5-O4-G5-B4` | `O4:81 own=0; B4:209 own=0; G5:198 own=0; O5:9 own=0` | `1` | `0` | `0` |

## Offset Hits

### `keyser bitcoin .pdf`

| source target | offset | landed index | landed text | hit target | strict | context |
|---|---|---:|---|---|---:|---|
| `G5` | `+corridorIndex=9` | `9` | `heart` | `O5` | `0` | `Get some bitcoin. Open your heart to Biteoiny It's the freaking` |

### `analysis_outputs/external_clues/google_drive_article_download.pdf`

| source target | offset | landed index | landed text | hit target | strict | context |
|---|---|---:|---|---|---:|---|
| `G5` | `+corridorIndex=9` | `9` | `heart` | `O5` | `0` | `Get some bitcoin. Open your heart to Biteoiny It's the freaking` |


## Decision

- `current_pdf_ocr_overdose_index_offset_no_selector`.
- The hidden OCR `OVERDOSE` word is present only in the duplicate OCR PDFs and does not supply a selective index-offset rule.
- Existing active line/corridor/slot units do not land on active component words or strict unit/order terms in a way that covers all four active targets.

## Next Move

- Keep hidden PDF OCR OVERDOSE index offsets closed. Continue toward physical/original-layout/source evidence or raw clue wording that supplies R3 unit/order.

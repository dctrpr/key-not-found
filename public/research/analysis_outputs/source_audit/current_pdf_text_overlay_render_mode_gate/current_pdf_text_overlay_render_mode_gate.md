# Current PDF Text Overlay Render-Mode Gate

Scope: inspect page-76 PDF OCR/text overlays for visible render modes, font/layout evidence, OVERDOSE text, and active-target aligned source instructions. No OCR-to-key extraction, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.

- Created: `2026-05-24T02:29:23`
- PDFs checked: `3`
- Texttrace spans: `755`
- Invisible type-3 spans / visible painted spans: `755` / `0`
- PDFs with all text invisible: `3`
- GlyphLessFont / Helvetica-only PDFs: `2` / `1`
- Fit-available PDFs: `2`
- OVERDOSE text-trace PDFs: `2`
- Active aligned trace rows / component hits / strict instruction hits: `6` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_text_overlay_render_mode_gate/current_pdf_text_overlay_render_mode_gate_sheet.jpg`
- Fingerprint: `pdfs=3|traceSpans=755|type3=755|visible=0|allInvisiblePdfs=3|glyphLess=2|helvetica=1|fits=2|overdosePdfs=2|activeTrace=6|activeComponents=0|activeStrict=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Rows

| PDF | trace spans | type counts | visible spans | fonts | fit | OVERDOSE hits | active trace/component/strict |
|---|---:|---|---:|---|---:|---:|---:|
| `magazine.pdf` | `221` | `{'3': 221}` | `0` | `Helvetica` | `False` | `0` | `0/0/0` |
| `keyser bitcoin .pdf` | `267` | `{'3': 267}` | `0` | `GlyphLessFont` | `True` | `1` | `3/0/0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `267` | `{'3': 267}` | `0` | `GlyphLessFont` | `True` | `1` | `3/0/0` |

## Active Target Overlay Detail

| PDF | target | aligned trace count | trace types | aligned text | component hits | strict hits |
|---|---|---:|---|---|---|---|
| `keyser bitcoin .pdf` | `O4 buying the dip` | `1` | `[3]` | `ByiiREeraipy"` | `[]` | `[]` |
| `keyser bitcoin .pdf` | `B4 $1 billion` | `1` | `[3]` | `eis` | `[]` | `[]` |
| `keyser bitcoin .pdf` | `G5 Volcano Bonds` | `0` | `[]` | `` | `[]` | `[]` |
| `keyser bitcoin .pdf` | `O5 shitcoiner at heart` | `1` | `[3]` | `siukbeodmensertslveaarty` | `[]` | `[]` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `O4 buying the dip` | `1` | `[3]` | `ByiiREeraipy"` | `[]` | `[]` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `B4 $1 billion` | `1` | `[3]` | `eis` | `[]` | `[]` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `G5 Volcano Bonds` | `0` | `[]` | `` | `[]` | `[]` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `O5 shitcoiner at heart` | `1` | `[3]` | `siukbeodmensertslveaarty` | `[]` | `[]` |

## Decision

- Do not reopen the PDF text overlay as an extraction source.
- All page-76 text overlay spans are invisible/type-3 OCR traces, not visible original-layout typography.
- The fit-available OCR overlays still contain no active exact components or strict unit/order terms inside O4/B4/G5/O5.

## Next Move

- Treat PDF text overlays as derivative OCR context only. Future progress still depends on new physical/original-layout/source evidence or a raw clue that passes the reopen gate.

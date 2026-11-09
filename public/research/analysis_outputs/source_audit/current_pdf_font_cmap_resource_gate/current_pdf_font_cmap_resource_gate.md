# Current PDF Font CMap Resource Gate

Scope: inspected PDF font resources, ToUnicode CMaps, CIDToGID maps, font descriptors, and embedded font files in the current PDFs, with page 76 treated as the target page. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.

- Created: `2026-05-24T05:02:44`
- PDFs / pages checked: `3` / `24`
- Page font references / unique font objects: `24` / `24`
- Type0 GlyphLessFont objects / built-in Helvetica objects: `16` / `8`
- ToUnicode streams / full-range identity CMaps: `16` / `16`
- CIDToGID maps / font files / unique font-file hashes: `16` / `16` / `1`
- Procedural resource strict/context hits: `0` / `0`
- Structural `font` term hits: `40`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|pages=24|fontRefs=24|fonts=24|glyphless=16|helvetica=8|toUnicode=16|identityCMap=16|cidMaps=16|fontFiles=16|uniqueFontFiles=1|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## Page 76 Font Rows

| PDF | font xref | type | base font | resource | encoding | ToUnicode | identity CMap | font files | resource hits |
|---|---:|---|---|---|---|---:|---:|---:|---|
| `magazine.pdf` | 35 | Type1 | Helvetica | F3 | WinAnsiEncoding | 0 | 0 | 0 | - |
| `keyser bitcoin .pdf` | 72 | Type0 | GlyphLessFont | f-0-0 | Identity-H | 1 | 1 | 1 | - |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 72 | Type0 | GlyphLessFont | f-0-0 | Identity-H | 1 | 1 | 1 | - |

## PDF Summary Rows

| PDF | unique fonts | ToUnicode | identity CMaps | font files | resource hits |
|---|---:|---:|---:|---:|---|
| `magazine.pdf` | 8 | 0 | 0 | 0 | - |
| `keyser bitcoin .pdf` | 8 | 8 | 8 | 8 | - |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | 8 | 8 | 8 | 8 | - |

## Resource Notes

- `magazine.pdf` uses built-in `/Helvetica` with `/WinAnsiEncoding`; it has no embedded font file and no ToUnicode CMap.
- The two duplicate OCR PDFs use per-page `/GlyphLessFont` Type0 resources with `/Identity-H` encoding.
- Their ToUnicode streams are full-range identity CMaps (`<0000> <FFFF> <0000>`), not instruction text.
- Their embedded font files are small repeated GlyphLessFont binaries; printable strings are font/table names only and contain no puzzle instruction/context terms.

## Decision

- `current_pdf_font_cmap_resource_no_source_carrier`
- Do not reopen current PDF font/CMap resources as original-layout/source evidence.
- Treat the font stack as OCR implementation detail only.

## Next Move

- Continue source/original-layout validation only if a distinct source asset or raw clue wording changes the rule space.

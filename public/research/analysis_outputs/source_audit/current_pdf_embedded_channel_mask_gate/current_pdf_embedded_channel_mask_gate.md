# Current PDF Embedded Channel / Mask Gate

Scope: inspect page-76 embedded PDF image objects for alpha/soft masks, hard masks, non-RGB separations, ICC/CMYK channels, and channel-only anomalies around O4/B4/G5/O5, orange highlights, and the OVERDOSE header. No OCR-to-key extraction, hashes, seed/WIF/address checks, BIP39 checks, or candidate generation were run.

- Created: `2026-05-21T15:52:05`
- PDFs checked: `3`
- Page-76 image objects: `3`
- 8-bit DeviceRGB DCT images: `3`
- Duplicate image SHA groups: `1`
- Hidden channel candidate images: `0`
- SMask/Mask images: `0`
- Alpha pixmap images: `0`
- Non-RGB / ICC-CMYK-Separation images: `0` / `0`
- Active channel rows / state mismatches / unexpected channel states: `12` / `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_embedded_channel_mask_gate/current_pdf_embedded_channel_mask_gate_sheet.jpg`
- Fingerprint: `pdfs=3|p76Images=3|rgbDct=3|dupeGroups=1|hidden=0|mask=0|alpha=0|nonRgb=0|iccSep=0|activeRows=12|activeMismatch=0|activeUnexpected=0|sourceR3=0|triggers=0/9|selectors=0`

## Page-76 Image Objects

| PDF | xref | image px | rotation/orientation | bpc | colorspace | filter | smask | alpha | hidden candidate | sha prefix |
|---|---:|---:|---|---:|---|---|---:|---:|---:|---|
| `magazine.pdf` | `37` | `2544x3264` | `180/rotate180_for_readable` | `8` | `DeviceRGB` | `DCTDecode` | `0` | `False` | `False` | `d9f4a15c43f39b3a` |
| `keyser bitcoin .pdf` | `59` | `2040x2805` | `0/as_extracted_readable` | `8` | `DeviceRGB` | `DCTDecode` | `0` | `False` | `False` | `26d6e8002fe1d86b` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `59` | `2040x2805` | `0/as_extracted_readable` | `8` | `DeviceRGB` | `DCTDecode` | `0` | `False` | `False` | `26d6e8002fe1d86b` |

## Active Target Channel Detail

| PDF | target | expected | visible | channel explanation | orange | dark | RGB means | spread |
|---|---|---|---|---|---:|---:|---|---:|
| `magazine.pdf` | `O4 buying the dip` | `Y` | `Y` | `expected_orange_rgb` | `0.5467` | `0.6933` | `214.309/152.101/97.025` | `117.284` |
| `magazine.pdf` | `B4 $1 billion` | `K` | `K` | `expected_dark_ink` | `0.0` | `0.5106` | `131.843/131.84/131.863` | `0.022` |
| `magazine.pdf` | `G5 Volcano Bonds` | `K` | `K` | `expected_dark_ink` | `0.0` | `0.5323` | `126.471/126.453/126.481` | `0.028` |
| `magazine.pdf` | `O5 shitcoiner at heart` | `Y` | `Y` | `expected_orange_rgb` | `0.503` | `0.6936` | `203.953/147.3/95.69` | `108.263` |
| `keyser bitcoin .pdf` | `O4 buying the dip` | `Y` | `Y` | `expected_orange_rgb` | `0.5569` | `0.6297` | `205.097/156.825/118.842` | `86.255` |
| `keyser bitcoin .pdf` | `B4 $1 billion` | `K` | `K` | `expected_dark_ink` | `0.0039` | `0.4362` | `170.273/169.694/167.458` | `2.815` |
| `keyser bitcoin .pdf` | `G5 Volcano Bonds` | `K` | `K` | `expected_dark_ink` | `0.0016` | `0.5186` | `154.11/152.482/150.608` | `3.501` |
| `keyser bitcoin .pdf` | `O5 shitcoiner at heart` | `Y` | `Y` | `expected_orange_rgb` | `0.5083` | `0.644` | `197.53/151.559/114.747` | `82.783` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `O4 buying the dip` | `Y` | `Y` | `expected_orange_rgb` | `0.5569` | `0.6297` | `205.097/156.825/118.842` | `86.255` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `B4 $1 billion` | `K` | `K` | `expected_dark_ink` | `0.0039` | `0.4362` | `170.273/169.694/167.458` | `2.815` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `G5 Volcano Bonds` | `K` | `K` | `expected_dark_ink` | `0.0016` | `0.5186` | `154.11/152.482/150.608` | `3.501` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `O5 shitcoiner at heart` | `Y` | `Y` | `expected_orange_rgb` | `0.5083` | `0.644` | `197.53/151.559/114.747` | `82.783` |

## Decision

- Do not reopen PDF embedded channels, alpha, masks, or color separations as an extraction source.
- Page 76 is stored as ordinary 8-bit DeviceRGB JPEG page images in all three PDFs; the two low-resolution PDFs are duplicates of each other.
- Channel splits explain visible orange/black ink only and add no hidden source-side unit/order evidence.

## Next Move

- Keep the high-resolution page-76 scan as visual authority. Reopen this branch only if a new source file exposes non-RGB separations, masks, or a distinct original-layout asset.

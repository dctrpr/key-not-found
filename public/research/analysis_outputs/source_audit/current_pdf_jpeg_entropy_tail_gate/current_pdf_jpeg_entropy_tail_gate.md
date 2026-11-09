# Current PDF JPEG Entropy Tail Gate

- Created: `2026-05-24T18:04:08`
- Decision: `current_pdf_jpeg_entropy_tail_no_selector`
- Fingerprint: `pdfs=3|images=32|pageImages=24|groups=24|p76Unique=1|activeUnique=4|tails=5|strictTails=0|contextTails=0|unexpected=0|restart=0|orders=0|structural=10|candidates=0|sourceR3=0|triggers=0/9|selectors=0`
- Sheet: `analysis_outputs/source_audit/current_pdf_jpeg_entropy_tail_gate/current_pdf_jpeg_entropy_tail_gate_sheet.jpg`

## Summary

- Image rows / page-image rows: `32` / `24`
- Entropy signature groups: `24`
- Page-76 unique entropy signatures: `1`
- Active-page unique entropy signatures: `4`
- Rows with bytes after EOI: `5`
- Tail strict/context rows: `0` / `0`
- Unexpected scan/marker rows: `0`
- Restart-marker rows: `0`
- Matched bounded entropy orders: `0`
- Structural-only signal rows: `10`
- Selector candidates / source-backed R3 / triggers: `0` / `0` / `0/9`

## Page-Image Entropy Orders

- `magazine.pdf`: `74-80-77-73-75-76-79-78`
- `keyser bitcoin .pdf`: `74-77-80-78-76-75-79-73`
- `analysis_outputs/external_clues/google_drive_article_download.pdf`: `74-77-80-78-76-75-79-73`

## Signature Groups

- `DCTDecode|2040x2805|sof=SOF0|scans=1|dri=None|entropy=697563|stuffed=2778|rst=0|trail=0`: `2` rows
- `DCTDecode|2040x2805|sof=SOF0|scans=1|dri=None|entropy=749737|stuffed=2183|rst=0|trail=0`: `2` rows
- `DCTDecode|2040x2805|sof=SOF0|scans=1|dri=None|entropy=752773|stuffed=2227|rst=0|trail=0`: `2` rows
- `DCTDecode|2040x2805|sof=SOF0|scans=1|dri=None|entropy=762783|stuffed=2372|rst=0|trail=0`: `2` rows
- `DCTDecode|2040x2805|sof=SOF0|scans=1|dri=None|entropy=766658|stuffed=2534|rst=0|trail=0`: `2` rows
- `DCTDecode|2040x2805|sof=SOF0|scans=1|dri=None|entropy=827693|stuffed=5522|rst=0|trail=0`: `2` rows
- `DCTDecode|2040x2805|sof=SOF0|scans=1|dri=None|entropy=886253|stuffed=2456|rst=0|trail=0`: `2` rows
- `DCTDecode|2040x2805|sof=SOF0|scans=1|dri=None|entropy=994381|stuffed=4746|rst=0|trail=0`: `2` rows

## Decision

- Do not promote embedded JPEG entropy/tail structure as a source or selector.
- Page 76 is unique only in the high-resolution `magazine.pdf` lineage where page-image entropy lengths are generally unique; the duplicate low-resolution PDF lineage shares its page signatures.
- The short post-EOI tails are non-printable padding/trailing bytes confined to `magazine.pdf`, with no strict/context strings and no instruction terms.
- There are no restart-marker structures, unexpected scan markers, or exact bounded article/fold/active entropy orders.

## Next Move

- Stop extending PDF binary-wrapper checks unless a new source file differs materially from the current two PDF lineages.

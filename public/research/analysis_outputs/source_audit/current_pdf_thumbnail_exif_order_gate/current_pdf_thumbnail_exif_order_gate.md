# Current PDF Thumbnail EXIF Order Gate

Scope: checked whether the Canon EXIF timestamps in the tiny `magazine.pdf` thumbnails form a page/fold/OVERDOSE ordering selector. The EXIF rows come from the current PDF embedded JPEG marker gate, which was built from raw DCT streams in the current PDFs. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.

- Created: `2026-05-24T05:16:19`
- Thumbnail EXIF rows: `8`
- Article/page/xref order: `73-74-75-76-77-78-79-80`
- Timestamp order: `73-75-74-78-79-76-77-80`
- Article-order monotonic: `False`
- Article-order inversions in timestamp rank stream: `5`
- Candidate order matches / checks: `0` / `5`
- Page 76 timestamp / rank: `2025-10-01 16:26:26` / `6`
- Provenance metadata / instruction carriers: `8` / `0`
- Strict/context hits: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `rows=8|pages=73-80|timeOrder=73-75-74-78-79-76-77-80|articleMonotonic=0|inversions=5|metadata=8|instrCarrier=0|strict=0|context=0|sourceR3=0|triggers=0/9|selectors=0`

## Thumbnail Timestamp Rows

| article page | xref | timestamp | rank | seconds from first | previous article delta | sample |
|---:|---:|---|---:|---:|---:|---|
| 73 | 17 | `2025-10-01 16:19:01` | 1 | 0 |  | `Exif Canon 2025:10:01 16:19:01 0221 0100` |
| 74 | 24 | `2025-10-01 16:22:52` | 3 | 231 | 231 | `Exif Canon 2025:10:01 16:22:52 0221 0100` |
| 75 | 31 | `2025-10-01 16:21:45` | 2 | 164 | -67 | `Exif Canon 2025:10:01 16:21:45 0221 0100` |
| 76 | 38 | `2025-10-01 16:26:26` | 6 | 445 | 281 | `Exif Canon 2025:10:01 16:26:26 0221 0100` |
| 77 | 45 | `2025-10-01 16:27:50` | 7 | 529 | 84 | `Exif Canon 2025:10:01 16:27:50 0221 0100` |
| 78 | 52 | `2025-10-01 16:23:58` | 4 | 297 | -232 | `Exif Canon 2025:10:01 16:23:58 0221 0100` |
| 79 | 59 | `2025-10-01 16:25:19` | 5 | 378 | 81 | `Exif Canon 2025:10:01 16:25:19 0221 0100` |
| 80 | 66 | `2025-10-01 16:28:58` | 8 | 597 | 219 | `Exif Canon 2025:10:01 16:28:58 0221 0100` |

## Timestamp-Order Gaps

| from page | to page | seconds |
|---:|---:|---:|
| 73 | 75 | 164 |
| 75 | 74 | 67 |
| 74 | 78 | 66 |
| 78 | 79 | 81 |
| 79 | 76 | 67 |
| 76 | 77 | 84 |
| 77 | 80 | 68 |

## Candidate Order Checks

| candidate | expected | observed | match | interpretation |
|---|---|---|---:|---|
| article/page/xref order | `73-74-75-76-77-78-79-80` | `73-75-74-78-79-76-77-80` | `0` | Would support using thumbnail timestamps as current PDF page order. |
| reverse article order | `80-79-78-77-76-75-74-73` | `73-75-74-78-79-76-77-80` | `0` | Would support a simple mirror/reverse page-order selector. |
| known valid leaf 75->76 adjacency | `ranks adjacent` | `rank75=2 rank76=6` | `0` | Would support timestamp order as a physical leaf traversal clue. |
| active lower-page quartet 76-78-79-80 | `76-78-79-80` | `78-79-76-80` | `0` | Would support timestamp order as a page-76/OVERDOSE traversal selector. |
| page 76 boundary role | `rank 1 or 8` | `rank76=6` | `0` | Would make the page-76 target a timestamp boundary. |

## Decision

- `current_pdf_thumbnail_exif_order_no_selector`
- The timestamp order is `73-75-74-78-79-76-77-80`, not article/page/xref order or a simple reverse order.
- Page 76 is timestamp rank 6, not a first/last boundary, and the known valid 75->76 leaf is not adjacent in timestamp order.
- The EXIF rows contain no strict instruction terms, no puzzle context terms, no source-instruction carrier segment, and no source-backed R3 bridge.
- Treat the Canon timestamps as scanner/PDF provenance, not as a page/fold/OVERDOSE selector.

## Next Move

- Continue source/original-layout validation only if a distinct physical scan, source export, or raw clue wording supplies a unit/order/transform.

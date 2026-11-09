# Current PDF JPEG Compression Provenance Gate

Scope: checked whether embedded JPEG/DCT compression structure in the current PDFs supplies a page/fold/OVERDOSE selector. The pass inspects quantization and Huffman table signatures, SOF sampling, compression groups, and raw byte-size order. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.

- Created: `2026-05-24T05:23:10`
- PDFs / image records: `3` / `32`
- Page images / thumbnails: `24` / `8`
- Compression groups: `3`
- Page-image / thumbnail compression groups: `2` / `1`
- Page 76 compression signatures / unique signatures: `3` / `0`
- Active unique compression signatures: `0`
- Magazine page-image byte-size order: `78-79-76-75-73-77-80-74`
- Magazine thumbnail byte-size order: `79-75-76-78-73-80-74-77`
- Candidate order matches / checks: `0` / `6`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `pdfs=3|records=32|groups=3|pageImageGroups=2|thumbGroups=1|p76Sigs=3|p76Unique=0|activeUnique=0|byteOrder=78-79-76-75-73-77-80-74|thumbByteOrder=79-75-76-78-73-80-74-77|sourceR3=0|triggers=0/9|selectors=0`

## Compression Groups

| group | records | roles | PDFs | article pages | p76 records | byte range | signature |
|---|---:|---|---|---|---:|---|---|
| J1 | 16 | `page_image` | `analysis_outputs/external_clues/google_drive_article_download.pdf,keyser bitcoin .pdf` | `73-74-75-76-77-78-79-80` | 2 | `700966-999752` | `DCTDecode|2040x2805|sof=SOF0|sampling=1:2x2:q0;2:1x1:q1;3:1x1:q1|dqt=923fad45b89409f0|dht=3332adea16c3317e` |
| J2 | 8 | `page_image` | `magazine.pdf` | `73-74-75-76-77-78-79-80` | 1 | `561468-1347648` | `DCTDecode|2544x3264|sof=SOF0|sampling=1:2x1:q0;2:1x1:q1;3:1x1:q1|dqt=1249c9d146fa7b71|dht=bd22c11fd034b824` |
| J3 | 8 | `page_thumbnail` | `magazine.pdf` | `73-74-75-76-77-78-79-80` | 1 | `9027-12751` | `DCTDecode|82x106|sof=SOF0|sampling=1:2x2:q0;2:1x1:q1;3:1x1:q1|dqt=812fc98121e5ef68|dht=3332adea16c3317e` |

## Candidate Order Checks

| candidate | expected | observed | match |
|---|---|---|---:|
| magazine page-image byte-size order vs page order | `73-74-75-76-77-78-79-80` | `78-79-76-75-73-77-80-74` | `0` |
| magazine page-image byte-size order vs reverse page order | `80-79-78-77-76-75-74-73` | `78-79-76-75-73-77-80-74` | `0` |
| magazine thumbnail byte-size order vs page order | `73-74-75-76-77-78-79-80` | `79-75-76-78-73-80-74-77` | `0` |
| magazine thumbnail byte-size order vs reverse page order | `80-79-78-77-76-75-74-73` | `79-75-76-78-73-80-74-77` | `0` |
| active page-image byte-size order vs 76-78-79-80 | `76-78-79-80` | `78-79-76-80` | `0` |
| active thumbnail byte-size order vs 76-78-79-80 | `76-78-79-80` | `79-76-78-80` | `0` |

## Decision

- `current_pdf_jpeg_compression_provenance_no_selector`
- JPEG compression structure forms broad provenance groups, not a page-76 or active-quartet carrier.
- Page 76 has no unique compression signature; its signatures are shared with non-active pages and/or duplicate PDFs.
- Byte-size ordering does not match page order, reverse page order, or active 76-78-79-80 order.
- Treat DQT/DHT/SOF compression structure as image-encoding provenance only.

## Next Move

- Continue source/original-layout validation only if a distinct physical scan, source export, or raw clue wording supplies a unit/order/transform.

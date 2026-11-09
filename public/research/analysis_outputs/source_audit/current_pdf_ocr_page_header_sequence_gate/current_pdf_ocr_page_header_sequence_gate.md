# Current PDF OCR Page-Header Sequence Gate

Scope: inspected page-start OCR text across current PDF article pages 73-80, with special attention to page 76 starting at `OVERDOSE` in the duplicate OCR PDFs. This is a page-header/order inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T14:18:40`
- Decision: `current_pdf_ocr_page_header_sequence_no_selector`
- PDFs checked / page rows checked: `3` / `24`
- Page-76 `OVERDOSE` header PDFs: `2`
- Strict page-start rows / target page-start rows: `0` / `2`
- All-four target page-start rows / active-order page-start rows: `0` / `0`
- Page-header sequence candidates: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_ocr_page_header_sequence_gate/current_pdf_ocr_page_header_sequence_gate_sheet.jpg`
- Fingerprint: `pdfs=3|pageRows=24|p76Overdose=2|strictRows=0|targetRows=2|allFourRows=0|activeOrderRows=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Summary

| PDF | pages | p76 starts OVERDOSE | strict page starts | target page starts | all-four page starts | candidates | first-token sequence |
|---|---:|---:|---:|---:|---:|---:|---|
| `magazine.pdf` | `8` | `0` | `0` | `0` | `0` | `0` | `73:tl 74:l 75:r 76:9l 77:euoiu 78:bl 79:6l 80:ob` |
| `keyser bitcoin .pdf` | `8` | `1` | `0` | `1` | `0` | `0` | `73:jopeajes 74:overdose 75:jopeajes 76:overdose 77:o 78:overdose 79:of 80:fake` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `8` | `1` | `0` | `1` | `0` | `0` | `73:jopeajes 74:overdose 75:jopeajes 76:overdose 77:o 78:overdose 79:of 80:fake` |

## Page Rows

| PDF | article page | first token | strict hits | target ids | target order | candidate | first words |
|---|---:|---|---|---|---|---:|---|
| `magazine.pdf` | `73` | `tl` | `-` | `-` | `-` | `0` | `T,L o (! (§ U) tr o .F G E')(! =tr ooH6 ffi= resTex xtsw ttlT/t'\ trE/\O SSOOUgAO J ü t aL\ I b-` |
| `magazine.pdf` | `74` | `l` | `-` | `-` | `-` | `0` | `,L 3SOOUSAO` |
| `magazine.pdf` | `75` | `r` | `-` | `-` | `-` | `0` | `r- 9L .pa^orun pue sTqJITnE aql JoJ SrrrualsrT ,,{sEa aJE sJarrroc+rr{s pur? rrour rroc uroJJ spJon +treseald .act1i .o1 ualsrT o1 pJ€r{ st Brrr.reeq` |
| `magazine.pdf` | `76` | `9l` | `-` | `-` | `-` | `0` | `9L q o 9. §) Gt ß) §. o m a 0i? 0) o ts SrAq aSnBCAq aO",{tsInI ,r(n8 1eq1+snJ+ ,(11ee.r truop f '+T` |
| `magazine.pdf` | `77` | `euoiu` | `-` | `-` | `-` | `0` | `euoIu a u s seo s.Ieu o s ecu e xe nolc .u Ieao ueus l[.r.ro tss us I n' '(+q8ft se/',r oTlalso3 srirlg)` |
| `magazine.pdf` | `78` | `bl` | `-` | `-` | `-` | `0` | `BL I x g o 9. 0) GI 0) N. o m a A)? o) .{coTg sTseuac eq+ uT eJar{l 1r{8Tr .+T eas ol` |
| `magazine.pdf` | `79` | `6l` | `-` | `-` | `-` | `0` | `6L )$ I § s f .e^oT puts ectsed q+Tat 11 secalder puts e+tsq puts rtseJ slenbuoc uToclTg se -.dse1sco pue ,.tuo3e aq+ -` |
| `magazine.pdf` | `80` | `ob` | `-` | `-` | `-` | `0` | `OB 8r8 CTXOI % @ o o E J 5 * r j t" J ov 3)lvJ'` |
| `keyser bitcoin .pdf` | `73` | `jopeajes` | `-` | `-` | `-` | `0` | `Jopeajes |q | ouszeBew ujoora 73 OVERDOSE` |
| `keyser bitcoin .pdf` | `74` | `overdose` | `-` | `-` | `-` | `0` | `OVERDOSE` |
| `keyser bitcoin .pdf` | `75` | `jopeajes` | `-` | `-` | `-` | `0` | `Jopeajes |3 | ouszeBe; ujooyg BITCOIN IS TOXIC AF Here's the bitter truth. Bitcoin was not a reaction to the Global Financial Crisis of` |
| `keyser bitcoin .pdf` | `76` | `overdose` | `-` | `O5` | `O5` | `0` | `OVERDOSE Get some toxicity. Get some bitcoin. Open your heart to Biteoiny It's the freaking UTXO ghetto up in here, y'all. It's funkier than` |
| `keyser bitcoin .pdf` | `77` | `o` | `-` | `-` | `-` | `0` | `o = ce] 2 = c S =} > -= = rc) a wo = — 2 A 4 Meanwhile, back in Tl Salvador,` |
| `keyser bitcoin .pdf` | `78` | `overdose` | `-` | `-` | `-` | `0` | `OVERDOSE We've never had an economy and a money that incentivizes love before until bitcoin. Love opens up the collective unconscious and our joint` |
| `keyser bitcoin .pdf` | `79` | `of` | `-` | `-` | `-` | `0` | `of love — because bitcoin is infinitely more efficient: To wrap this up, as we move from a REEENT violence cate sieehy tO a` |
| `keyser bitcoin .pdf` | `80` | `fake` | `-` | `-` | `-` | `0` | `FAKE AD` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `73` | `jopeajes` | `-` | `-` | `-` | `0` | `Jopeajes |q | ouszeBew ujoora 73 OVERDOSE` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `overdose` | `-` | `-` | `-` | `0` | `OVERDOSE` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `75` | `jopeajes` | `-` | `-` | `-` | `0` | `Jopeajes |3 | ouszeBe; ujooyg BITCOIN IS TOXIC AF Here's the bitter truth. Bitcoin was not a reaction to the Global Financial Crisis of` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `overdose` | `-` | `O5` | `O5` | `0` | `OVERDOSE Get some toxicity. Get some bitcoin. Open your heart to Biteoiny It's the freaking UTXO ghetto up in here, y'all. It's funkier than` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `77` | `o` | `-` | `-` | `-` | `0` | `o = ce] 2 = c S =} > -= = rc) a wo = — 2 A 4 Meanwhile, back in Tl Salvador,` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `overdose` | `-` | `-` | `-` | `0` | `OVERDOSE We've never had an economy and a money that incentivizes love before until bitcoin. Love opens up the collective unconscious and our joint` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `79` | `of` | `-` | `-` | `-` | `0` | `of love — because bitcoin is infinitely more efficient: To wrap this up, as we move from a REEENT violence cate sieehy tO a` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `80` | `fake` | `-` | `-` | `-` | `0` | `FAKE AD` |

## Decision

- `current_pdf_ocr_page_header_sequence_no_selector`.
- Page 76 begins with OCR `OVERDOSE` only in the byte-identical duplicate OCR PDFs, and the page-start text is ordinary article/header prose.
- Page-start OCR rows do not combine strict extraction wording with all-four active target terms or active-order structure.

## Next Move

- Treat current PDF OCR page headers as derivative context only. Continue toward distinct physical/original-layout/source material or raw clue wording that supplies R3 unit/order.

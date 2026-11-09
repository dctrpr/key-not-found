# Current PDF Visual Header/Footer Band Sequence Gate

Scope: rendered the current PDF article pages 73-80 as displayed, cropped top and bottom page bands, and compared page 76 against neighboring page bands. This is a visible layout inspection only; no OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T14:24:25`
- Decision: `current_pdf_visual_header_footer_band_sequence_no_selector`
- PDFs checked / page rows checked / band rows checked: `3` / `24` / `48`
- OCR OVERDOSE page-start rows imported from previous gate: `6`
- Page-76 top-band near matches / bottom-band near matches: `15` / `5`
- Visual header/footer sequence candidates: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_pdf_visual_header_footer_band_sequence_gate/current_pdf_visual_header_footer_band_sequence_gate_sheet.jpg`
- Fingerprint: `pdfs=3|pages=24|bands=48|p76TopNear=15|p76BottomNear=5|ocrOverdoseStarts=6|candidates=0|sourceR3=0|triggers=0/9|selectors=0`

## PDF Summary

| PDF | pages | OCR OVERDOSE starts | p76 top near others | p76 bottom near others | p76 top signature | p76 bottom signature | candidates |
|---|---:|---|---:|---:|---|---|---:|
| `magazine.pdf` | `8` | `-` | `5` | `3` | `D058-K012-O048-E031-L246` | `D068-K035-O018-E048-L241` | `0` |
| `keyser bitcoin .pdf` | `8` | `74,76,78` | `5` | `1` | `D163-K002-O050-E034-L210` | `D381-K001-O000-E012-L182` | `0` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `8` | `74,76,78` | `5` | `1` | `D163-K002-O050-E034-L210` | `D381-K001-O000-E012-L182` | `0` |

## Closest Page-76 Band Matches

| PDF | band | closest non-self pages by MAD |
|---|---|---|
| `magazine.pdf` | `top` | `78=9.3, 75=15.7, 79=15.8` |
| `magazine.pdf` | `bottom` | `75=15.7, 79=18.8, 78=22.7` |
| `keyser bitcoin .pdf` | `top` | `74=19.8, 78=22.0, 75=29.1` |
| `keyser bitcoin .pdf` | `bottom` | `79=34.0, 74=35.3, 78=35.3` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `top` | `74=19.8, 78=22.0, 75=29.1` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `bottom` | `79=34.0, 74=35.3, 78=35.3` |

## Band Rows

| PDF | article page | band | mean lum | dark | black | orange | edge | signature |
|---|---:|---|---:|---:|---:|---:|---:|---|
| `magazine.pdf` | `73` | `top` | `233.6487` | `0.082878` | `0.067956` | `0.001732` | `0.026541` | `D082-K067-O001-E026-L233` |
| `magazine.pdf` | `73` | `bottom` | `224.3594` | `0.193763` | `0.003984` | `0.0` | `0.06017` | `D193-K003-O000-E060-L224` |
| `magazine.pdf` | `74` | `top` | `245.2749` | `0.00082` | `0.0` | `0.001719` | `0.002206` | `D000-K000-O001-E002-L245` |
| `magazine.pdf` | `74` | `bottom` | `196.9481` | `0.375352` | `0.008503` | `0.0` | `0.142798` | `D375-K008-O000-E142-L196` |
| `magazine.pdf` | `75` | `top` | `246.4848` | `0.037422` | `0.028151` | `0.002018` | `0.028346` | `D037-K028-O002-E028-L246` |
| `magazine.pdf` | `75` | `bottom` | `250.0187` | `0.025729` | `0.004883` | `0.0` | `0.04549` | `D025-K004-O000-E045-L250` |
| `magazine.pdf` | `76` | `top` | `246.0359` | `0.058268` | `0.012656` | `0.048333` | `0.03118` | `D058-K012-O048-E031-L246` |
| `magazine.pdf` | `76` | `bottom` | `241.4739` | `0.068737` | `0.035365` | `0.018789` | `0.04831` | `D068-K035-O018-E048-L241` |
| `magazine.pdf` | `77` | `top` | `18.7577` | `0.981159` | `0.96875` | `0.001497` | `0.025856` | `D981-K968-O001-E025-L018` |
| `magazine.pdf` | `77` | `bottom` | `21.7702` | `0.972487` | `0.951576` | `0.0` | `0.039488` | `D972-K951-O000-E039-L021` |
| `magazine.pdf` | `78` | `top` | `252.3724` | `0.012161` | `0.005664` | `0.002031` | `0.018683` | `D012-K005-O002-E018-L252` |
| `magazine.pdf` | `78` | `bottom` | `244.2978` | `0.045104` | `0.039883` | `0.0` | `0.014189` | `D045-K039-O000-E014-L244` |
| `magazine.pdf` | `79` | `top` | `247.0869` | `0.037708` | `0.020898` | `0.002031` | `0.045018` | `D037-K020-O002-E045-L247` |
| `magazine.pdf` | `79` | `bottom` | `247.2721` | `0.033594` | `0.022448` | `0.001901` | `0.026755` | `D033-K022-O001-E026-L247` |
| `magazine.pdf` | `80` | `top` | `158.3421` | `0.950625` | `0.0` | `0.614857` | `0.001634` | `D950-K000-O614-E001-L158` |
| `magazine.pdf` | `80` | `bottom` | `164.9346` | `0.923893` | `0.0` | `0.937096` | `0.002091` | `D923-K000-O937-E002-L164` |
| `keyser bitcoin .pdf` | `73` | `top` | `205.5747` | `0.165951` | `0.070898` | `0.001328` | `0.035406` | `D165-K070-O001-E035-L205` |
| `keyser bitcoin .pdf` | `73` | `bottom` | `219.9228` | `0.046745` | `0.0` | `0.0` | `0.002771` | `D046-K000-O000-E002-L219` |
| `keyser bitcoin .pdf` | `74` | `top` | `215.5037` | `0.096432` | `0.003372` | `0.003424` | `0.0122` | `D096-K003-O003-E012-L215` |
| `keyser bitcoin .pdf` | `74` | `bottom` | `193.5705` | `0.309063` | `0.003919` | `0.031745` | `0.01947` | `D309-K003-O031-E019-L193` |
| `keyser bitcoin .pdf` | `75` | `top` | `221.9205` | `0.074896` | `0.010951` | `0.000846` | `0.029504` | `D074-K010-O000-E029-L221` |
| `keyser bitcoin .pdf` | `75` | `bottom` | `222.3924` | `0.033503` | `0.0` | `0.0` | `0.002099` | `D033-K000-O000-E002-L222` |
| `keyser bitcoin .pdf` | `76` | `top` | `210.6336` | `0.163203` | `0.002305` | `0.050599` | `0.034739` | `D163-K002-O050-E034-L210` |
| `keyser bitcoin .pdf` | `76` | `bottom` | `182.5657` | `0.381237` | `0.001302` | `0.0` | `0.012672` | `D381-K001-O000-E012-L182` |
| `keyser bitcoin .pdf` | `77` | `top` | `102.9694` | `0.869245` | `0.092734` | `0.002344` | `0.025805` | `D869-K092-O002-E025-L102` |
| `keyser bitcoin .pdf` | `77` | `bottom` | `131.2006` | `0.684844` | `0.054609` | `0.00862` | `0.017637` | `D684-K054-O008-E017-L131` |
| `keyser bitcoin .pdf` | `78` | `top` | `216.6998` | `0.096953` | `0.044531` | `0.002188` | `0.027983` | `D096-K044-O002-E027-L216` |
| `keyser bitcoin .pdf` | `78` | `bottom` | `193.7843` | `0.252526` | `0.052943` | `0.016654` | `0.017783` | `D252-K052-O016-E017-L193` |
| `keyser bitcoin .pdf` | `79` | `top` | `213.1051` | `0.146315` | `0.00082` | `0.065143` | `0.044066` | `D146-K000-O065-E044-L213` |
| `keyser bitcoin .pdf` | `79` | `bottom` | `205.224` | `0.208437` | `0.0` | `0.17181` | `0.010636` | `D208-K000-O171-E010-L205` |
| `keyser bitcoin .pdf` | `80` | `top` | `164.8768` | `0.75668` | `0.004232` | `0.668112` | `0.007136` | `D756-K004-O668-E007-L164` |
| `keyser bitcoin .pdf` | `80` | `bottom` | `163.7346` | `0.648958` | `0.003984` | `0.42388` | `0.00864` | `D648-K003-O423-E008-L163` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `73` | `top` | `205.5747` | `0.165951` | `0.070898` | `0.001328` | `0.035406` | `D165-K070-O001-E035-L205` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `73` | `bottom` | `219.9228` | `0.046745` | `0.0` | `0.0` | `0.002771` | `D046-K000-O000-E002-L219` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `top` | `215.5037` | `0.096432` | `0.003372` | `0.003424` | `0.0122` | `D096-K003-O003-E012-L215` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `74` | `bottom` | `193.5705` | `0.309063` | `0.003919` | `0.031745` | `0.01947` | `D309-K003-O031-E019-L193` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `75` | `top` | `221.9205` | `0.074896` | `0.010951` | `0.000846` | `0.029504` | `D074-K010-O000-E029-L221` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `75` | `bottom` | `222.3924` | `0.033503` | `0.0` | `0.0` | `0.002099` | `D033-K000-O000-E002-L222` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `top` | `210.6336` | `0.163203` | `0.002305` | `0.050599` | `0.034739` | `D163-K002-O050-E034-L210` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `76` | `bottom` | `182.5657` | `0.381237` | `0.001302` | `0.0` | `0.012672` | `D381-K001-O000-E012-L182` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `77` | `top` | `102.9694` | `0.869245` | `0.092734` | `0.002344` | `0.025805` | `D869-K092-O002-E025-L102` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `77` | `bottom` | `131.2006` | `0.684844` | `0.054609` | `0.00862` | `0.017637` | `D684-K054-O008-E017-L131` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `top` | `216.6998` | `0.096953` | `0.044531` | `0.002188` | `0.027983` | `D096-K044-O002-E027-L216` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `78` | `bottom` | `193.7843` | `0.252526` | `0.052943` | `0.016654` | `0.017783` | `D252-K052-O016-E017-L193` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `79` | `top` | `213.1051` | `0.146315` | `0.00082` | `0.065143` | `0.044066` | `D146-K000-O065-E044-L213` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `79` | `bottom` | `205.224` | `0.208437` | `0.0` | `0.17181` | `0.010636` | `D208-K000-O171-E010-L205` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `80` | `top` | `164.8768` | `0.75668` | `0.004232` | `0.668112` | `0.007136` | `D756-K004-O668-E007-L164` |
| `analysis_outputs/external_clues/google_drive_article_download.pdf` | `80` | `bottom` | `163.7346` | `0.648958` | `0.003984` | `0.42388` | `0.00864` | `D648-K003-O423-E008-L163` |

## Decision

- `current_pdf_visual_header_footer_band_sequence_no_selector`.
- The visible header/footer bands do not add a source-backed extraction rule. Page 76 remains a useful target/validation area, but its top/bottom band state does not supply a unit, order, or selector.
- The repeated OCR `OVERDOSE` page-start rows belong to the duplicate OCR PDFs and remain context unless a separate source/provenance trigger supplies R3 wording.

## Next Move

- Use visual PDF band state only as registration evidence. The next best move is a direct held-to-light/source-layout comparison against any true physical scan, original layout export, or raw clue wording that names a unit/order.

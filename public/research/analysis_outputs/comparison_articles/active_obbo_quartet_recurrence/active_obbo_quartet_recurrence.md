# Active O-B-B-O Quartet Recurrence

Scope: scan existing line-shaped orange/dark highlighter detections across Issue 24 and independent Max/OVERDOSE comparison articles for the active page-76 `OBBO` quartet. No extraction, key derivation, hashing, OCR extraction, WIF/Base58 scanning, seed generation, or address checks were run.

- Created: `2026-05-21T00:06:45`
- Sheet: `analysis_outputs/comparison_articles/active_obbo_quartet_recurrence/active_obbo_quartet_recurrence_sheet.jpg`
- Decision: `active_obbo_quartet_distinctive_but_no_r3_selector`

## Summary

- Active y ratios: `0.674326 0.741881 0.786765 0.905944`.
- Active readable line order guardrail: `22 25 27 32`.
- Active readable corridor guardrail: `4 7 9 14`.
- Total consecutive `OBBO` windows: `3`.
- Issue 24 `OBBO` windows: `3`.
- Independent-control `OBBO` windows: `0`.
- Issue 24 active-like windows: `1`.
- Independent-control active-like windows: `0`.

## Source Summary

| source | pages | OBBO windows | active-like windows | note |
|---|---:|---:|---:|---|
| `bitcoin3` | `8` | `0` | `0` | independent control |
| `issue24_toxic_af` | `8` | `3` | `1` | Issue 24 target article |
| `issue26` | `5` | `0` | `0` | independent control |
| `issue27` | `8` | `0` | `0` | independent control |

## OBBO Windows

| rank | source/page | index | y ratios | active L1 delta | active-like |
|---:|---|---:|---|---:|---|
| `1` | `issue24_toxic_af p4` | `7` | `[0.674479, 0.742341, 0.786458, 0.906097]` | `0.001072` | `True` |
| `2` | `issue24_toxic_af p3` | `2` | `[0.328891, 0.375306, 0.397059, 0.568781]` | `1.438879` | `False` |
| `3` | `issue24_toxic_af p4` | `2` | `[0.145374, 0.26394, 0.287071, 0.421722]` | `1.990809` | `False` |

## Assessment

- The exact lower page-76 `OBBO` placement appears as an active-like window only in Issue 24 page 4, matching O4/B4/G5/O5.
- The independent comparison articles in the body-highlighter grammar set produce `0` consecutive `OBBO` windows, so the active quartet is not a generic OVERDOSE body-highlighter pattern in the local controls.
- This strengthens the page-76 lower corridor as target-location/source-validation evidence, but it still does not name a word/letter/line/font unit or an extraction order.

## Next Move

- Keep the lower page-76 O4/B4/G5/O5 OBBO quartet as distinctive target-location/source-validation evidence only; do not treat it as extraction permission without R3 unit/order wording.

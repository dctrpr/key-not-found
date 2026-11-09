# 3D Active Target Label Gate

Scope: check whether the 3D map word-label layer can be trusted for the active page-76 target/corridor phrases. No key derivation, hashing, seed, WIF, or address checks were run.

- Created: `2026-05-20T13:50:36`
- Active target phrases missing from 3D word labels: `4`
- Suspect OCR/alternate phrases present: `p77_nas_gone, p78_fills_gap`
- Trusted navigation phrases present: `p76_should_sell, p76_future_earnings, p77_100000`

## Phrase Checks

| id | page | role | canonical | 3D label | context |
|---|---:|---|---:|---:|---|
| `p76_open_heart` | 76 | orange target | `True` | `False` | `-` |
| `p76_buying_dip` | 76 | orange target | `True` | `False` | `-` |
| `p76_bukele` | 76 | corridor target | `True` | `True` | ` monetary fund imf on twitter he s taunting them telling them he s byiireeraipy i tweeted president nayib bukele when he announced he was going to tap his nation s volcanoes to ...` |
| `p76_one_billion` | 76 | grey target | `True` | `False` | `-` |
| `p76_should_sell` | 76 | p78 frame edge phrase | `True` | `True` | `en he announced he was going to tap his nation s volcanoes to mine eis in bitcoin that he should sell billions worth of future bitcoin earnings collateralized to pay off the imf...` |
| `p76_future_earnings` | 76 | p78 frame band | `True` | `True` | `o tap his nation s volcanoes to mine eis in bitcoin that he should sell billions worth of future bitcoin earnings collateralized to pay off the imf loan and get rid of those lee...` |
| `p76_volcano_bonds` | 76 | G5 / grey target | `True` | `False` | `-` |
| `p76_imf_loan` | 76 | corridor target | `True` | `True` | `at he should sell billions worth of future bitcoin earnings collateralized to pay off the imf loan and get rid of those leeches i tagged mike novogratz in the tweet figuring he ...` |
| `p76_mike_novogratz` | 76 | Typeka Mix anchor | `True` | `True` | `oin earnings collateralized to pay off the imf loan and get rid of those leeches i tagged mike novogratz in the tweet figuring he could sella bunch to his wall street crony pals...` |
| `p76_trust_that_guy` | 76 | Typeka Mix anchor | `True` | `True` | `sella bunch to his wall street crony pals but so far he hasn t moved on it i don t really trust that guy maybe because he s a siukbeodmensertslveaarty` |
| `p76_shitcoiner_heart` | 76 | O5 / orange target | `True` | `False` | `-` |
| `p77_100000` | 77 | zero/#0 benchmark | `True` | `True` | `f writing jack mallers strike app nas gone from 20 000 new sign ups aday toa mind bending 100 000 and se se bb aye g a reb we a ha me dele a sten r aa este stat rat et ready to ...` |
| `p77_has_gone` | 77 | known correction | `True` | `False` | `-` |
| `p77_nas_gone` | 77 | known OCR error | `False` | `True` | `42% of the country is now hyperbitcoinized at the time of writing jack mallers strike app nas gone from 20 000 new sign ups aday toa mind bending 100 000 and se se bb aye g a re...` |
| `p77_monetizing` | 77 | p77 near-miss source | `True` | `False` | `-` |
| `p78_fills_in_gap` | 78 | known correction | `True` | `False` | `-` |
| `p78_fills_gap` | 78 | known OCR/alternate wording | `False` | `True` | `iat money with perfect bitcoin remove the war incentive and you remove the hate incentive bitcoin fills the gap with love our most natural tendency if given a chance the warmong...` |

## Assessment

- The 3D word-label layer is not exact enough for active target extraction.
- It preserves some navigation anchors such as `should sell`, `future bitcoin earnings`, and p77 `100,000`.
- It misses or distorts critical active phrases, including G5/O5-style target text; the canonical DOCM/plain text remains the wording truth.
- The 3D viewer should stay a visual/geometry map only. Any future selected region must be translated to exact text using the corrected transcript or source crop review.

## Decision

- Do not use article_3d_map_data word labels as extraction text for the page-76 lower corridor.

## Next Move

- If the viewer is edited later, add a visible 'OCR label only / exact text in transcript' cue for target phrases; otherwise continue source-gated investigation.

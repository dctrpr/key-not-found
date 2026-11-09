# Spread Model Reconciliation

Scope: reconcile the photographed opener spread with earlier high-res spread and front/back tests. This uses raw horizontal reflection of source orange boxes onto target orange/grey boxes. No key candidates are generated.

## Models Tested

- PDF-adjacent / photographed spread candidates: `[(73, 74), (75, 76), (77, 78), (79, 80)]`
- Standard even-left / odd-right spread candidates: `[(76, 77), (78, 79)]`

## Direction Results

### pdf_adjacent_or_photographed_spread 73 -> 74
- source orange boxes: `13`
- target highlight boxes: `8`
- meaningful raw intersections: `6`
- target pattern: `O2O8O6O3O4O7`
- p73 `small OVERDOSE section label` -> p74 orange 2 `small OVERDOSE section label component` (src=0.952, tgt=0.825, dist=1.0)
- p73 `small OVERDOSE section label` -> p74 orange 8 `small OVERDOSE section label component` (src=0.867, tgt=0.952, dist=1.1)
- p73 `small OVERDOSE section label` -> p74 orange 6 `small OVERDOSE section label component` (src=0.947, tgt=0.947, dist=1.0)
- p73 `small OVERDOSE section label` -> p74 orange 3 `small OVERDOSE section label component` (src=0.941, tgt=0.896, dist=1.1)
- p73 `small OVERDOSE section label` -> p74 orange 4 `small OVERDOSE section label component` (src=0.899, tgt=0.852, dist=1.8)
- p73 `small OVERDOSE section label` -> p74 orange 7 `small OVERDOSE section label component` (src=0.840, tgt=0.882, dist=2.1)

### pdf_adjacent_or_photographed_spread 74 -> 73
- source orange boxes: `8`
- target highlight boxes: `13`
- meaningful raw intersections: `6`
- target pattern: `O8O9O11O7O6O10`
- p74 `small OVERDOSE section label component` -> p73 orange 8 `small OVERDOSE section label` (src=0.825, tgt=0.952, dist=1.0)
- p74 `small OVERDOSE section label component` -> p73 orange 9 `small OVERDOSE section label` (src=0.952, tgt=0.867, dist=1.1)
- p74 `small OVERDOSE section label component` -> p73 orange 11 `small OVERDOSE section label` (src=0.947, tgt=0.947, dist=1.0)
- p74 `small OVERDOSE section label component` -> p73 orange 7 `small OVERDOSE section label` (src=0.896, tgt=0.941, dist=1.1)
- p74 `small OVERDOSE section label component` -> p73 orange 6 `small OVERDOSE section label` (src=0.852, tgt=0.899, dist=1.8)
- p74 `small OVERDOSE section label component` -> p73 orange 10 `small OVERDOSE section label` (src=0.882, tgt=0.840, dist=2.1)

### pdf_adjacent_or_photographed_spread 75 -> 76
- source orange boxes: `8`
- target highlight boxes: `10`
- meaningful raw intersections: `0`
- target pattern: ``

### pdf_adjacent_or_photographed_spread 76 -> 75
- source orange boxes: `5`
- target highlight boxes: `11`
- meaningful raw intersections: `0`
- target pattern: ``

### pdf_adjacent_or_photographed_spread 77 -> 78
- source orange boxes: `2`
- target highlight boxes: `7`
- meaningful raw intersections: `0`
- target pattern: ``

### pdf_adjacent_or_photographed_spread 78 -> 77
- source orange boxes: `4`
- target highlight boxes: `5`
- meaningful raw intersections: `1`
- target pattern: `G2`
- p78 `BILLION worth of hate toys in Afghanistan, / $2 trillion fiat cuck-bucks.` -> p77 grey 2 `shitcoiners, useless Royals` (src=0.497, tgt=1.000, dist=102.1)

### pdf_adjacent_or_photographed_spread 79 -> 80
- source orange boxes: `10`
- target highlight boxes: `2`
- meaningful raw intersections: `2`
- target pattern: `O2O1`
- p79 `Everyone will live their own experience in the rabbit hole.` -> p80 orange 2 `6 FL OZ (473 mL)` (src=0.201, tgt=0.306, dist=153.2)
- p79 `Everyone will live their own experience in the rabbit hole.` -> p80 orange 1 `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` (src=0.233, tgt=0.127, dist=321.2)

### pdf_adjacent_or_photographed_spread 80 -> 79
- source orange boxes: `2`
- target highlight boxes: `11`
- meaningful raw intersections: `2`
- target pattern: `O4O4`
- p80 `6 FL OZ (473 mL)` -> p79 orange 4 `Everyone will live their own experience in the rabbit hole.` (src=0.306, tgt=0.201, dist=153.2)
- p80 `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` -> p79 orange 4 `Everyone will live their own experience in the rabbit hole.` (src=0.127, tgt=0.233, dist=321.2)

### standard_even_left_odd_right 76 -> 77
- source orange boxes: `5`
- target highlight boxes: `5`
- meaningful raw intersections: `1`
- target pattern: `G2`
- p76 `by the rancid catnip of fiat money.` -> p77 grey 2 `shitcoiners, useless Royals` (src=0.854, tgt=0.432, dist=151.8)

### standard_even_left_odd_right 77 -> 76
- source orange boxes: `2`
- target highlight boxes: `10`
- meaningful raw intersections: `0`
- target pattern: ``

### standard_even_left_odd_right 78 -> 79
- source orange boxes: `4`
- target highlight boxes: `11`
- meaningful raw intersections: `1`
- target pattern: `O4`
- p78 `the game-theorized Bitcoin protocol,` -> p79 orange 4 `Everyone will live their own experience in the rabbit hole.` (src=0.303, tgt=0.291, dist=394.6)

### standard_even_left_odd_right 79 -> 78
- source orange boxes: `10`
- target highlight boxes: `7`
- meaningful raw intersections: `1`
- target pattern: `O4`
- p79 `Everyone will live their own experience in the rabbit hole.` -> p78 orange 4 `the game-theorized Bitcoin protocol,` (src=0.291, tgt=0.303, dist=394.6)

## Assessment

- The opener photo requires us to keep a PDF-adjacent spread layer in the source model, at least for pages 73-74.
- That does not rescue page 76: raw `75 -> 76` in the PDF-adjacent model has no meaningful hit.
- The `79 <-> 80` adjacent interaction is the only repeated nearby source/theme signal, tying page 79 end-text to the page-80 medicine/package artwork.
- This reinforces the medicine/five-capsule provenance layer, but it still does not define page-76 target text, ordering, or letter extraction.
- The next useful move remains a source/physical registration improvement or a specific mirror-writing rule, not more unconstrained spread folding.

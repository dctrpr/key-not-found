# Front/Back Leaf Box Registration Audit

Scope: refine the physical hold-to-light idea by using the high-res scan as geometry truth, mirroring orange highlight boxes through the actual front/back leaves, and allowing only a bounded crop-correction translation (`-180..180` px, step `20`). OCR is not used as geometry and no key candidates are generated.

- Contact sheet: `analysis_outputs/source_audit/front_back_leaf_box_registration_sheet.jpg`

## Direction Results

### 75 -> 76
- Source orange boxes: 8
- Target orange/grey boxes: 10
- Raw hflip: edges=0 score=0.00000
- Best small translation: dx=0 dy=-180 edges=2 score=1.10606
- p75 O1 `They are the sum of` -> p76 G1 `Gotta be this way... post-1971 fiat money` (src=0.527, tgt=0.114, dist=622.1)
- p75 O2 `all our neuroses.` -> p76 G1 `Gotta be this way... post-1971 fiat money` (src=0.399, tgt=0.077, dist=613.8)

### 76 -> 75
- Source orange boxes: 5
- Target orange/grey boxes: 11
- Raw hflip: edges=0 score=0.00000
- Best small translation: dx=-20 dy=-180 edges=2 score=1.28115
- p76 O4 `“buying the dip.”` -> p75 O5 `that’s ever been invented or discovered.` (src=0.667, tgt=0.228, dist=129.8)
- p76 O3 `by the rancid catnip of fiat money.` -> p75 G1 `money printers, banking` (src=0.441, tgt=0.448, dist=109.0)

### 77 -> 78
- Source orange boxes: 2
- Target orange/grey boxes: 7
- Raw hflip: edges=0 score=0.00000
- Best small translation: dx=120 dy=100 edges=1 score=1.00333
- p77 O2 `harass old women and children` -> p78 O3 `BILLION worth of hate toys in Afghanistan, / $2 trillion fiat cuck-bucks.` (src=1.000, tgt=0.223, dist=293.5)

### 78 -> 77
- Source orange boxes: 4
- Target orange/grey boxes: 5
- Raw hflip: edges=1 score=1.15000
- Best small translation: dx=120 dy=-160 edges=2 score=2.10053
- p78 O3 `BILLION worth of hate toys in Afghanistan, / $2 trillion fiat cuck-bucks.` -> p77 O2 `harass old women and children` (src=0.223, tgt=1.000, dist=292.7)
- p78 O1 `The numbers don’t lie.` -> p77 G1 `Sorry Bhutan... shitcoin hell` (src=0.987, tgt=0.132, dist=171.8)

### 79 -> 80
- Source orange boxes: 10
- Target orange/grey boxes: 2
- Raw hflip: edges=2 score=0.83904
- Best small translation: dx=0 dy=-60 edges=4 score=1.71811
- p79 O5 `We are getting our souls back and our minds.` -> p80 O1 `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` (src=0.319, tgt=0.125, dist=187.7)
- p79 O4 `Everyone will live their own experience in the rabbit hole.` -> p80 O2 `6 FL OZ (473 mL)` (src=0.201, tgt=0.306, dist=151.0)
- p79 O5 `We are getting our souls back and our minds.` -> p80 O2 `6 FL OZ (473 mL)` (src=0.275, tgt=0.300, dist=343.0)
- p79 O4 `Everyone will live their own experience in the rabbit hole.` -> p80 O1 `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` (src=0.233, tgt=0.127, dist=298.1)

### 80 -> 79
- Source orange boxes: 2
- Target orange/grey boxes: 11
- Raw hflip: edges=2 score=0.83904
- Best small translation: dx=0 dy=60 edges=4 score=1.71811
- p80 O1 `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` -> p79 O5 `We are getting our souls back and our minds.` (src=0.125, tgt=0.319, dist=187.7)
- p80 O2 `6 FL OZ (473 mL)` -> p79 O4 `Everyone will live their own experience in the rabbit hole.` (src=0.306, tgt=0.201, dist=151.0)
- p80 O2 `6 FL OZ (473 mL)` -> p79 O5 `We are getting our souls back and our minds.` (src=0.300, tgt=0.275, dist=343.0)
- p80 O1 `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` -> p79 O4 `Everyone will live their own experience in the rabbit hole.` (src=0.127, tgt=0.233, dist=298.1)

## Page-76 Check

- The only true leaf direction targeting page 76 is `75 -> 76`; its best bounded translation is dx=0 dy=-180 with 2 meaningful edge(s).
- p75 O1 `They are the sum of` -> p76 G1 `Gotta be this way... post-1971 fiat money` (src=0.527, tgt=0.114, dist=622.1)
- p75 O2 `all our neuroses.` -> p76 G1 `Gotta be this way... post-1971 fiat money` (src=0.399, tgt=0.077, dist=613.8)

## Assessment

- This refined front/back leaf pass does not reproduce the strong page-76 corridor behavior seen in the 78/79 -> 76 mirrored-highlight graph.
- Any best translations are isolated box coincidences; they do not give a repeated page-76 selector or a human-readable ordering rule.
- Treat true front/back leaf overlay as downgraded unless a physical scan/photo reveals bleed-through marks that are not present in the digital source.
- Next best move: stop spending cycles on generic leaf overlays and inspect the original Canva thumbnail/export or page-76 corridor typography for an explicit ordering/instruction cue.

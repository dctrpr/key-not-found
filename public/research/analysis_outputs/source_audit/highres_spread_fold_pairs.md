# High-Res Spread Fold Pairs

Scope: true facing-spread geometry on high-res magazine pages. Tests 76/77 and 78/79 by reflecting orange highlights across the spine onto the opposite page's orange and grey/black highlights.

- Contact sheet: `analysis_outputs/source_audit/highres_spread_fold_pairs_contact_sheet.jpg`

## Results

### 77 -> 76
- source orange boxes: 2
- target highlight boxes: 10
- meaningful intersections: 0
- target pattern: ``

### 76 -> 77
- source orange boxes: 5
- target highlight boxes: 5
- meaningful intersections: 1
- target pattern: `G2`
- p76 box 3 `by the rancid catnip of fiat money.` -> p77 grey 2 `shitcoiners, useless Royals` (source=0.854, target=0.433, dist=151.6)

### 79 -> 78
- source orange boxes: 10
- target highlight boxes: 7
- meaningful intersections: 1
- target pattern: `O4`
- p79 box 4 `Everyone will live their own experience in the rabbit hole.` -> p78 orange 4 `the game-theorized Bitcoin protocol,` (source=0.291, target=0.303, dist=394.6)

### 78 -> 79
- source orange boxes: 4
- target highlight boxes: 11
- meaningful intersections: 1
- target pattern: `O4`
- p78 box 4 `the game-theorized Bitcoin protocol,` -> p79 orange 4 `Everyone will live their own experience in the rabbit hole.` (source=0.303, target=0.291, dist=394.6)

## Assessment

- True high-res facing-spread folds do not produce a clean one-to-one selector across the available article spreads.
- Any hits should be treated as regional/semantic evidence only unless a separate instruction tells us why that spread and direction should be chosen.
- The page-76 corridor remains stronger than the spread-pair output, so the next move is not more generic spread folding. It is either a physical scan/alignment or one explicit mirror-writing read rule on the page-76 corridor.

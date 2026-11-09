# Selector Gap Map

Scope: synthesize the current local evidence and identify what is still missing before more key-format or geometry work is justified. No key derivation was run.

- Created: `2026-05-20T03:57:53`
- Closed branch count: `31`
- Active branch count: `11`

## What Is Strong Now

- **Page 76 is the current target surface.** Status: `strong`. 17 of 17 medium/strong reflected edges land on page 76.
- **The strongest local registration is a row/region anchor, not a letter selector.** Status: `strong`. p79 box 1 maps to p76 black 1 with target coverage 0.76962 and center distance 9.96 px, but registered pattern is only B1B2.
- **The current high-res scan is geometry truth; OCR/source variants are too distorted for final selection.** Status: `strong`. Source-registration audit shows mean content-vs-highlight delta 116.91 px on pages 75-79, with max 4378.13 px including p80 package-art mismatch.
- **Typeka is a formatting witness, but not yet a selector.** Status: `medium`. Article with Fonts.docm records {'Typeka': 6568, 'Typeka Mix': 883}; p76 target sequence YKYKYKKY and Typeka streams have no instruction hits.
- **The local comparison PDFs cannot prove Typeka uniqueness.** Status: `strong`. Issue_26.pdf and bitcoin3.pdf have no embedded font rows and no usable extractable text; image counts [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1]].
- **Lower p76 brush/X marks reinforce the corridor, but do not add order.** Status: `medium`. 2 true standalone marks; pointer reads return adjacent Novogratz/distrust/shitcoiner prose only.

## Missing Selector Rule

A human-solvable selector must still supply four things: source layer, target region, ordering, and extraction unit.

- `source layer`: current best `high-res page 76 corridor plus reflected 78/79 evidence`; gap: No independent instruction says whether the source layer is highlight color, Typeka state, physical bleed-through, or Canva-marked registration.
- `target region`: current best `page-76 El Salvador/Bukele/IMF/$1 billion/Volcano corridor`; gap: Region is strong, but it is too broad for key extraction.
- `ordering`: current best `78/79 page-pair balance and the p79-yellow -> p76-black calibration anchor`; gap: No tested ordering stream creates readable instruction or checksum-like material.
- `extraction unit`: current best `line/phrase units, not letters`; gap: No rule decides first/last/bold/Mix/highlight/below/above words.

## Ranked Next Moves

1. **Recover source-level instruction/provenance**: Most local mechanics now identify a corridor but not the selector. The next useful evidence is Max's original clue wording/thread, higher-resolution Canva assets, or layout-source provenance. Local action: Search only for source artifacts not already ingested; avoid generating more key candidates.
2. **Physical magazine/photo branch**: If a real page curl, bleed-through, or print registration changes alignment, it can reopen geometry. The current digital scan does not. Local action: Wait for new scan/photo before repeating fold/hold-to-light overlays.
3. **One-rule manual solve reconstruction**: The public clue likely points to one human action. The remaining task is to write and test one explicit rule at a time against page 76, not broad transformations. Local action: For each proposed rule, require source page, target box, ordering, extraction unit, and expected readable output before running anything.

## Decision

- Do not run more broad hashing, key promotion, local fold geometry, Typeka-only streams, or mark-pointer tests without a new independent clue.
- The live problem is not key format. It is the missing human-readable selector/provenance rule that chooses which page-76 corridor material matters and in what order.

# DOCM / Visual Highlight Consistency

Scope: compare `Article with Fonts.docm` highlighted runs with the manual high-res visual orange/grey highlight readings. No key derivation was run.

- Created: `2026-05-20T09:21:36`
- DOCM printed highlight spans: `34`
- DOCM cyan spans: `3`
- Visual spans: `34`
- Unmatched visual spans: `1`
- Unmatched DOCM printed spans: `0`
- Cyan bridge spans: `0`

## DOCM Cyan Spans

- p75 `M` runs `[2]`
- p75 `N` runs `[42]`
- p78 `BILLION` runs `[263]`

## Unmatched Visual Spans

- `visual_orange_20` p80 orange: `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS; 6 FL OZ (473 mL)` (not present in DOCM printed article highlights)

## Unmatched DOCM Printed Spans

- none

## Cyan Bridges

- none

## Assessment

- DOCM yellow/black mostly mirrors the manual high-res orange/grey highlight system.
- The main material mismatch is p78 `$85 BILLION`: DOCM splits `BILLION` into cyan, so same-color yellow alone omits part of the visible orange phrase.
- The other unmatched visual item is p80 package art, which is graphic/package copy outside the article-body DOCM text.
- Cyan remains a DOCM-only formatting anomaly, not a scan-visible highlight layer.

## Next Move

- Treat DOCM yellow/black as wording support for visible highlights, not a separate selector. Do not use cyan unless a future source proves the Word formatting is original puzzle material.

# Typeka / Highlight Boundary Alignment

Scope: test whether Typeka/Typeka Mix font-family transitions align with highlight on/off boundaries as a selector. No key derivation was run.

- Created: `2026-05-20T09:17:08`
- DOCM source: `private_inputs/Desktop/Article with Fonts.docm`
- Runs inspected: `344`
- Font-change boundaries: `58`
- Typeka Mix font boundaries: `56`
- Highlight-change boundaries: `71`
- Coincident font+highlight boundaries: `3`
- Highlighted Typeka Mix chars: `0`
- Instruction-hit streams: `1`

## Character Counts

### Fonts
- `Typeka`: 6574
- `Typeka Mix`: 883
- `Stencil`: 19
- `LonestarW00-Regular`: 8

### Highlights
- `(none)`: 6251
- `yellow`: 748
- `black`: 476
- `cyan`: 9

## Boundary Streams

- `typeka_mix_text` len `882` hits `['first']`: `ax KeiserThey discount stuff in advance.collective panicthe black hole of the Cosmic Nowocoiners and shitcoiners,and even some Bitcoiners, consider this view toxic.Toxic Bitcoin MaximalistsVitalik ButerinGo Bitcoin Toxic Maximalist,George Clintonbeing ripped ...`
- `highlighted_typeka_mix_text` len `0` hits `[]`: ``
- `typeka_mix_boundary_edges` len `104` hits `[]`: `MarBtTeMaccgtwaNocEtTsteVncyGtttGnanbdoecstdnsmfErdMzitIygJsSmRrleBrodPkfeFpEa51aySyAsssfeTeIkTrTIeSsWHu`
- `font_change_boundary_edges` len `108` hits `[]`: `EwMarBFHtTeMaccgtwaNocEtTsteVncyGtttGnanbdoecstdnsmfErdMzitIygJsSmRrleBrodPkfeFpEa51aySyAsssfeTeIkTrTIeSsWHu`
- `highlight_change_boundary_edges` len `116` hits `[]`: `hMMayTsTfmsrNNosL1oFdIeMtebDyKyGeL1odGnIeGedbyyIssbIe1nVsastMeTslHrFiaswndssfIgoTesgamadwgA5BNwnftsBtlawytsidteTynEs`
- `font_and_highlight_change_boundary_edges` len `6` hits `[]`: `MaNoyG`

## Coincident Font+Highlight Boundary Samples

- runs `2->3` `Typeka/cyan` -> `Typeka Mix/`, edge `Ma`: `M` / `ax Keiser`
- runs `42->43` `Typeka/cyan` -> `Typeka Mix/`, edge `No`: `N` / `ocoiners and shitcoiners,`
- runs `67->68` `Typeka/yellow` -> `Typeka Mix/`, edge `yG`: `Keep your dignity.` / `Go Bitcoin Toxic Maximalist,`

## Assessment

- Typeka Mix does not appear inside highlighted runs in the Article-with-Fonts witness.
- Font-family changes and highlight on/off boundaries are mostly separate events, not a locked overlay-selector system.
- The only instruction-term hit is `first` inside ordinary prose (`first time in our existence`), not a boundary instruction.
- The coincident font+highlight boundary edge stream is too small/noisy to name a rule.
- Typeka Mix text is semantic article emphasis and name/phrase styling; it does not produce an instruction-like boundary stream.

## Next Move

- Keep Article with Fonts.docm as a formatting witness. Reopen Typeka/font-state extraction only if a source clue explicitly names a font state or a better source chooses exact words/lines first.

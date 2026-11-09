# Active Font-Edge Transition Gate

Scope: inspect the immediate DOCM run-level font states before and after locked O4/B4/G5/O5 targets. No extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.

- Created: `2026-05-21T00:58:56`
- Sheet: `analysis_outputs/docm_format_sources/active_font_edge_transition_gate/active_font_edge_transition_gate_sheet.jpg`
- Decision: `active_font_edges_are_regular_insulated_no_typeka_mix_selector`

## Summary

- Target state stream: `YKKY`.
- Edge pattern stream: `R>Y>R | R>K>R | R>K>R | R>Y>R`.
- Left-exit word stream: `he's mine collateralized a`.
- Right-entry word stream: `I in to Meanwhile`.
- Mix-neighbor count: `0`.
- Active edges all regular-insulated: `True`.
- Instruction hit count: `0`.

## Active Edges

| id | target | runs | edge | left state | left last word | target text | right first word | right state | Typeka Mix neighbor |
|---|---|---|---|---|---|---|---|---|---:|
| `O4` | `buying the dip` | `124-126` | `R>Y>R` | `Typeka regular` | `he's` | `"buying the dip."` | `I` | `Typeka regular` | `False` |
| `B4_text` | `$1 billion` | `131-131` | `R>K>R` | `Typeka regular` | `mine` | `$1 billion` | `in` | `Typeka regular` | `False` |
| `G5` | `Volcano Bonds` | `137-137` | `R>K>R` | `Typeka regular` | `collateralized` | `“Volcano Bonds”` | `to` | `Typeka regular` | `False` |
| `O5` | `shitcoiner at heart` | `151-151` | `R>Y>R` | `Typeka regular` | `a` | `shitcoiner at heart.` | `Meanwhile` | `Typeka regular` | `False` |

## Page-76 Non-Regular Clusters

| state | edge | runs | text |
|---|---|---|---|
| `M` | `R>M>R` | `120-120` | `El Salvador` |
| `Y` | `R>Y>R` | `124-126` | `"buying the dip."` |
| `B` | `R>B>R` | `128-128` | `President Nayib Bukele` |
| `K` | `R>K>R` | `131-131` | `$1 billion` |
| `K` | `R>K>R` | `137-137` | `“Volcano Bonds”` |
| `B` | `R>B>B` | `140-140` | `IMF` |
| `B` | `B>B>R` | `141-141` | `loan` |
| `M` | `R>M>M` | `143-143` | `Mike` |
| `M` | `M>M>R` | `144-144` | `Novogratz` |
| `M` | `R>M>R` | `148-148` | `I don't really trust that guy.` |
| `Y` | `R>Y>R` | `151-151` | `shitcoiner at heart.` |

## Assessment

- The active highlighted quartet is font-edge regular-insulated: every active target is entered from Typeka regular and exits to Typeka regular.
- No active O4/B4/G5/O5 target has Typeka Mix as its immediate run-level neighbor, so Typeka Mix is not a direct side selector for the active quartet.
- The target state stream remains the already-known `YKKY`; the edge pattern stream is just `R>Y>R | R>K>R | R>K>R | R>Y>R`.
- Left-exit and right-entry word streams from DOCM run boundaries are ordinary corridor prose and contain no instruction hits.
- This supports the active highlights as target/source-validation evidence, but does not supply R3 unit/order evidence.

## Next Move

- Keep font-edge transitions as a source-comparison guardrail; reopen only if raw clue/source wording names Typeka Mix, font boundary, left/right run edge, or font-state extraction.

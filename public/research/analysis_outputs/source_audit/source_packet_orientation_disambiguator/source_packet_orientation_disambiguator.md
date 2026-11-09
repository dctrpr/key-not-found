# Source Packet Orientation Disambiguator

Scope: record which source-packet visual/geometry signals can and cannot disambiguate page orientation for future source review. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.

- Created: `2026-05-21T07:22:01`
- Orientation modes checked: `5`
- Accepted source-comparison modes: `1`
- Rejected/blocked modes: `4`
- Ambiguous visual signals: `4`
- Discriminating source/geometry signals: `6`
- Visual/color patterns: `YKKY` / `OBBO`
- Readable page-line order: `22 25 27 32`
- Raw native unnormalized page-line order: `32 27 25 22`
- Readable corridor order: `4 7 9 14`
- Raw native unnormalized corridor order: `14 9 7 4`
- Readable center-step signs: dx `-++`, dy `+++`
- Common shift tolerance: `±4px`
- Source-backed R3 bridge hits: `0`
- Satisfied reopen triggers: `0`
- Selector unlocks / extraction-ready gates: `0` / `0`
- Orientation disambiguator fingerprint: `modes=5|accepted=1|ambiguous=4|discriminators=6|states=YKKY|color=OBBO|lines=22-25-27-32|nativeLines=32-27-25-22|dx=-++|dy=+++|sourceR3=0|selectors=0`
- Sheet: `analysis_outputs/source_audit/source_packet_orientation_disambiguator/source_packet_orientation_disambiguator_sheet.jpg`

## Orientation Modes

| mode | target order | visual state | page lines | corridor indexes | dx/dy signs | C9 normalized centers | decision |
|---|---|---|---|---|---|---|---|
| `readable_upright` | `buying_dip,one_billion,volcano_bonds,shitcoiner_heart` | `YKKY` | `22 25 27 32` | `4 7 9 14` | `-++` / `+++` | `0.651,0.028;0.136,0.289;0.359,0.462;0.540,0.921` | `accept_for_source_comparison` |
| `raw_native_unrotated_top_to_bottom` | `shitcoiner_heart,volcano_bonds,one_billion,buying_dip` | `YKKY` | `32 27 25 22` | `14 9 7 4` | `--+` / `---` | `0.540,0.921;0.359,0.462;0.136,0.289;0.651,0.028` | `reject_until_rot180_normalized` |
| `x_mirror_about_page` | `buying_dip,one_billion,volcano_bonds,shitcoiner_heart` | `YKKY` | `22 25 27 32` | `4 7 9 14` | `+--` / `+++` | `0.349,0.028;0.864,0.289;0.641,0.462;0.460,0.921` | `reject_as_loose_mirror` |
| `y_mirror_about_page` | `buying_dip,one_billion,volcano_bonds,shitcoiner_heart` | `YKKY` | `22 25 27 32` | `4 7 9 14` | `-++` / `---` | `0.651,-1.315;0.136,-1.576;0.359,-1.749;0.540,-2.208` | `reject_as_loose_mirror` |
| `point_mirror_or_page_rotate180` | `buying_dip,one_billion,volcano_bonds,shitcoiner_heart` | `YKKY` | `22 25 27 32` | `4 7 9 14` | `+--` / `---` | `0.349,-1.315;0.864,-1.576;0.641,-1.749;0.460,-2.208` | `reject_without_native_rot180_context` |

## Signal Roles

| signal | observed | role | future-source use |
|---|---|---|---|
| `visual state stream` | `YKKY` | `ambiguous` | Do not validate orientation from YKKY alone; it survives reversal. |
| `orange/black color stream` | `OBBO` | `ambiguous` | Do not validate orientation from OBBO alone; it is palindromic. |
| `C9 frame horizontal mirror` | `xMirrorInvariant=True` | `ambiguous` | Treat frame-only matches as source-registration evidence, not selector permission. |
| `OVERDOSE control state` | `NNNNNNNNN` | `ambiguous` | Header glyphs stay non-active; require external slot wording before use. |
| `page-line order` | `22 25 27 32 vs 32 27 25 22` | `discriminator` | Require readable order 22/25/27/32 after orientation normalization. |
| `corridor-index order` | `4 7 9 14 vs 14 9 7 4` | `discriminator` | Require corridor order 4/7/9/14 after orientation normalization. |
| `center-step signs` | `dx -++; dy +++` | `discriminator` | Reject loose mirror matches that invert dx or dy signs without provenance. |
| `C9 normalized centers` | `[[0.651074, 0.028335], [0.135736, 0.288666], [0.35864, 0.461629], [0.540133, 0.920897]]` | `discriminator` | Compare normalized positions, not just frame containment or color state. |
| `native rotate180 roundtrip` | `mean 0.2859 vs direct 27.6479` | `discriminator` | Normalize native source assets with the documented 180-degree transform first. |
| `alignment tolerance` | `shift +/-4px; pad +4px` | `discriminator` | Reject geometry matches outside the narrow tolerance unless source provenance explains them. |

## Decision

- Keep the source packet in readable/upright coordinates for comparison; normalize native source images with the documented 180-degree transform first.
- Do not accept `YKKY`, `OBBO`, or C9 frame containment as orientation proof because all are ambiguous under reversal or mirror controls.
- Accept only source matches that preserve readable page-line order `22 25 27 32`, corridor order `4 7 9 14`, center-step signs `-++/+++`, C9 normalized centers, and the narrow `±4px` tolerance unless new source provenance explains a transform.
- This pass is validation-only and does not reopen extraction because source-backed R3 unit/order evidence remains absent.

## Next Move

Use this disambiguator with the reopen-trigger matrix when inspecting a new source asset: normalize orientation first, then require readable order 22/25/27/32 and corridor order 4/7/9/14 before treating visual matches as evidence.

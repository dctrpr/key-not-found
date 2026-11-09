# O-B-B-O High-Res Boundary Coincidences

Scope: check whether the four active page-76 O-B-B-O anchors share exact visual boundaries with each other, the repaired p78 frame, or M3/M4. No text extraction, key candidates, hashes, seed phrases, WIF checks, or address checks were generated.

- Created: `2026-05-20T19:52:11`
- Overlay: `analysis_outputs/source_audit/obbo_highres_boundary_coincidences/obbo_highres_boundary_coincidences_overlay.jpg`
- Exact threshold: `6.0` px; near threshold: `20.0` px

## Anchors

| id | color | label | box |
|---|---|---|---|
| `buying_dip` | `orange` | `buying the dip` | `[1328.0, 2160.0, 1760.0, 2226.0]` |
| `one_billion` | `black` | `$1 billion` | `[430.0, 2400.0, 690.0, 2447.0]` |
| `volcano_bonds` | `black` | `Volcano Bonds` | `[795.0, 2544.0, 1196.0, 2592.0]` |
| `shitcoiner_heart` | `orange` | `shitcoiner at heart` | `[1040.0, 2932.0, 1661.0, 2982.0]` |

## Exact Boundary Hits

| a | boundary | b | boundary | axis | delta |
|---|---|---|---|---|---:|
| `one_billion` | `top` | `frame_dx_minus_38` | `top` | `y` | `2.0` |
| `volcano_bonds` | `right` | `frame_dx_minus_38` | `left` | `x` | `0.0` |

## Near Boundary Hits

| a | boundary | b | boundary | axis | delta | class |
|---|---|---|---|---|---:|---|
| `shitcoiner_heart` | `top` | `frame_dx_minus_38` | `bottom` | `y` | `18.0` | `near` |
| `shitcoiner_heart` | `centerY` | `frame_dx_minus_38` | `bottom` | `y` | `7.0` | `near` |

## Frame Contacts

| anchor | label | exact contact | near contact | right->frame left | top->frame bottom |
|---|---|---|---|---:|---:|
| `buying_dip` | `buying the dip` | `False` | `False` | `564.0` | `790.0` |
| `one_billion` | `$1 billion` | `False` | `False` | `506.0` | `550.0` |
| `volcano_bonds` | `Volcano Bonds` | `True` | `True` | `0.0` | `406.0` |
| `shitcoiner_heart` | `shitcoiner at heart` | `False` | `True` | `465.0` | `18.0` |

## Assessment

- Two exact boundary coincidences appear in the active O-B-B-O field: B4/$1 billion top aligns with the repaired frame top within 2 px, and G5/Volcano Bonds right edge equals the repaired frame left edge.
- The B4/frame-top hit is only a row/guide alignment because B4 is horizontally outside the repaired frame; it is not a frame contact.
- The G5/frame-left hit is the only exact contact-style boundary coincidence.
- O5 is a near frame contact because the frame bottom crosses the O5 band, but it is not an exact top/bottom boundary coincidence.
- The other O-B-B-O anchors do not provide exact shared contact boundaries with each other, the repaired frame, or M3/M4 mark boxes under the current high-res coordinates.
- This means the four-anchor O-B-B-O structure is a corridor/signature, not a complete geometric boundary selector.
- Do not extract text from O-B-B-O boundary sides unless a new source clue supplies a boundary side/order.

## Decision

- Close O-B-B-O boundary coincidence as a standalone selector under the current scan.
- Next move: Use the four-anchor O-B-B-O only as a corridor signature; next bounded pass should inspect whether the 3D folded view reveals a non-boundary visual ordering cue, not another text/key stream.

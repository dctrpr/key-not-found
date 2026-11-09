# P80 to Page-76 Anchor Geometry Audit

Scope: simple p80 package-label to p76 four-anchor geometry audit using identity, hflip, vflip, and 180-degree rotation. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.

- Created: `2026-05-20T19:30:18`
- Sheet: `analysis_outputs/source_audit/p80_to_p76_anchor_geometry/p80_to_p76_anchor_geometry_sheet.jpg`

## Nearest Cases

| p80 label | transform | nearest anchor | center distance | overlap/anchor | overlap/mapped |
|---|---|---|---:|---:|---:|
| `O2: 6 FL OZ (473 mL)` | `hflip` | `buying the dip` | `183.57` | `0.0` | `0.0` |
| `O1: 5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` | `identity` | `buying the dip` | `292.16` | `0.0` | `0.0` |
| `O2: 6 FL OZ (473 mL)` | `identity` | `buying the dip` | `515.74` | `0.0` | `0.0` |
| `O1: 5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS` | `hflip` | `buying the dip` | `569.84` | `0.0` | `0.0` |

## Positive Overlap Rows

- None at the 10% overlap threshold.

## Assessment

- No page-80 package label maps directly onto the four page-76 anchors under identity, hflip, vflip, or 180-degree rotation.
- The closest center-distance cases are still broad package-box placements, not narrow anchor overlaps.
- This supports keeping p80 as theme/count corroboration only; it does not physically choose the OBBO anchors in the current scan.
- Reopen p80 geometry only if a new physical/source image changes page registration or gives an explicit fold axis.

## Decision

- Keep p80 package geometry closed for the current scan; no tested mirror/fold transform selects the four page-76 anchors.

## Next Move

- Move back to the page-76/p78-p79 corridor itself: test whether M3/M4 standalone marks choose anchor order within OBBO.

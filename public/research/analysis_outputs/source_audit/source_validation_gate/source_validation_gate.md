# Source Validation Gate

Scope: consolidate the current source-fidelity benchmarks into a gate for future physical/original-layout/source material. No key derivation, hashing, WIF, seed, or address checks were run.

- Created: `2026-05-20T10:23:55`
- Sheet: `analysis_outputs/source_audit/source_validation_gate/source_validation_gate_sheet.jpg`

## Gates

| gate | accept | reject / block |
|---|---|---|
| `source_quality` | Native/original-layout export, source image, or physical scan/photo with enough resolution to inspect the benchmark crops. | Connector thumbnail, OCR PDF coordinates, low-res screenshot, or derived analysis image only. |
| `page76_priority_crops` | O5, G5, and L25-L32 crop regions are visible and can be compared against the baseline sheet. | - |
| `zero_hash0_hotspots` | New source visibly confirms or changes one of the zero/#0 hotspots. | - |
| `p79_pill_geometry` | New source changes or confirms the five-fragment count/order/placement. | - |
| `p78_frame_exact_edge` | New source supports or changes the repaired exact-edge signature and M3/O5/G5 tri-contact. | - |
| `extraction_permission` | Only proceed to key checks if the new source/clue names the extraction unit/order. | word, letter, line, edge, font state, first/last, explicit ordering |

## Baseline Priority

- O5 primary: `Maybe because he's a shitcoiner at heart.`.
- G5 pair: `collateralized “Volcano Bonds” to pay off the IMF`.
- Source band: `billions worth of future bitcoin earnings`.
- Zero/#0 baseline sheet: `analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops_sheet.jpg`.
- P79 pill baseline: `5` lower-left fragments.
- Repaired exact-edge signature: `should sell | Volcano Bonds | shitcoiner at heart` / `RKY`.

## Decision

- A new source is promoted only if it changes/validates source geometry in a benchmark region or reveals instruction/layer text.
- If benchmark regions are unchanged and no unit is named, treat the source as a witness only.
- Do not run key candidates until the extraction unit/order is named.

## Next Move

- When a new source arrives, run this gate first: source quality, page-76 priority crops, zero/#0 hotspots, p79 pill geometry, repaired p78 frame, then extraction permission.

# 3D Active Quartet Box OCR Gate

Scope: check the 3D map's stored OCR characters and word labels inside the exact O4/B4/G5/O5 active target boxes. No OCR was run, and no extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.

- Created: `2026-05-21T00:23:42`
- Sheet: `analysis_outputs/3d_article_map/active_quartet_box_ocr_gate/active_quartet_box_ocr_gate_sheet.jpg`
- Decision: `3d_target_box_ocr_not_text_authority`

## Summary

- Targets checked: `4`.
- Exact OCR-box matches: `0`.
- Corrupted/misread target boxes: `4`.
- Blank target boxes: `1`.
- Readable order preserved by target metadata: `22 25 27 32` lines / `4 7 9 14` corridor indexes.

## Target Box Checks

| target | exact wording | box chars | box words | char similarity | exact match |
|---|---|---|---|---:|---:|
| `O4 buying the dip` | `buying the dip` | `ByiiREeraipy"` | `ByiiREeraipy"` | `0.5` | `False` |
| `B4 $1 billion` | `$1 billion` | `eis` | `eis` | `0.1667` | `False` |
| `G5 Volcano Bonds` | `Volcano Bonds` | `-` | `-` | `0.0` | `False` |
| `O5 shitcoiner at heart` | `shitcoiner at heart` | `siukbeodmensertslveaarty` | `siukbeodmensertslveaarty` | `0.4878` | `False` |

## Assessment

- The 3D/canvas box geometry still identifies the same O4/B4/G5/O5 physical targets and preserves the readable line/corridor order.
- The text labels inside those boxes are not extraction-grade: O4, B4, G5, and O5 all fail exact OCR-box matching.
- This reinforces the current authority split: 3D map for geometry/navigation, DOCM/plain text/crop review for exact wording.

## Next Move

- Keep 3D target boxes as geometry/source-registration aids only; exact wording must be resolved through DOCM/plain text/crop review before any future selector is evaluated.

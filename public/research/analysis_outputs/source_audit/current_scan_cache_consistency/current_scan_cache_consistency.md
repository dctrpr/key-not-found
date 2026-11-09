# Current Scan Cache Consistency Audit

Scope: verify that the current cached page images and 3D viewer images came from the supplied best `magazine.pdf`. No OCR extraction, key derivation, seed, WIF, or address checks were run.

- Created: `2026-05-20T11:41:04`
- Project PDF md5: `2c454d800cf2971c1f86fd016f64b7a0`
- Desktop PDF md5: `2c454d800cf2971c1f86fd016f64b7a0`
- Project/Desktop byte-identical: `True`
- Visual RMS tolerance: `2.0`
- Source caches pixel-match extracted PDF images: `False`
- Source caches visually match extracted PDF images: `True`
- Source-to-3D transform: `rotate180`
- 3D upright images visually match after rotate180: `True`
- Page-76 comparison sheet: `analysis_outputs/source_audit/current_scan_cache_consistency/page76_source_vs_3d_sheet.jpg`

## Page Checks

| article page | pdf page | extracted size | source visual match | source diff rms/max | 3D after rotate180 visual match | 3D diff rms/max |
|---:|---:|---|---|---|---|---|
| 75 | 3 | `2544x3264` | `True` | `1.278111/69` | `True` | `1.110935/31` |
| 76 | 4 | `2544x3264` | `True` | `1.163935/58` | `True` | `1.048976/31` |
| 77 | 5 | `2544x3264` | `True` | `1.161545/43` | `True` | `1.195802/27` |
| 78 | 6 | `2544x3264` | `True` | `1.198546/62` | `True` | `1.025751/30` |
| 79 | 7 | `2544x3264` | `True` | `1.362447/59` | `True` | `1.122697/29` |
| 80 | 8 | `2544x3264` | `True` | `1.238367/48` | `True` | `1.273871/27` |

## Assessment

- The Desktop and project magazine.pdf files are byte-identical.
- Cached source images for pages 75-80 visually match the embedded images extracted from the current Desktop magazine.pdf; pixel hashes differ only because the caches are JPEG-resaved.
- 3D viewer upright images for pages 75-80 visually match the current source images after a 180-degree rotation.

## Decision

- The 3D upright image layer is source-faithful after accounting for the native PDF image orientation. The previous native-orientation mismatch was an orientation check error, not a stale-source finding.

## Next Move

- Use the 3D upright layer for readable-orientation geometry, or use source_images/fresh PDF extraction with a 180-degree rotation before comparing upright crop coordinates.

# Same-face trim transfer feasibility for pages 78 and 79

**All six fixed foot windows lack a matching print landmark.** Five other windows show a plausible counterpart in the high-resolution image of the same printed face. The available landmarks leave the foot spans outside the planned validation coverage. Physical registration remains unresolved. [Machine result](RESULT.json) · [Prior trim observations](../g02_edge_screen/MERGED.json)

One AI reviewer inspected all 13 low-resolution windows and the matching high-resolution pages, completing the review at 2026-11-10T23:52:39.574Z. The reviewer prepared the privately frozen window plan and had previously examined the scan lineage. This exploratory pass had no public preregistration or independent second reader. The earlier registered perimeter screen supplied the fixed trim intervals and corner boxes. [Perimeter protocol](../g02_edge_screen/PROTOCOL.md) · [Packet manifest](../g02_edge_screen/PACKET_MANIFEST.json)

| Window | Low-resolution box [x0, y0, x1, y1), px | Provisional observation |
| --- | --- | --- |
| p78-right-701 | [1819,573,1979,829] | Blank paper |
| p78-right-1402 | [1818,1274,1978,1530] | Matching vertical side imprint, with a distinct stroke endpoint on its first capital |
| p78-right-2103 | [1817,1975,1977,2231] | Blank paper and faint texture |
| p78-bottom-510 | [382,2441,638,2601] | Blank margin below the printed graphic |
| p78-bottom-1020 | [892,2445,1148,2605] | Blank margin |
| p78-bottom-1530 | [1402,2448,1658,2608] | Blank margin |
| p78-SE | [1814,2447,1974,2607] | Matching printed folio 78 |
| p79-bottom-510 | [382,2460,638,2620] | Blank margin with faint speckling |
| p79-bottom-1020 | [892,2448,1148,2608] | Blank margin with thin perimeter trace |
| p79-bottom-1530 | [1402,2434,1658,2594] | Blank margin with colored perimeter trace |
| p79-left-1402 | [44,1274,204,1530] | Matching side-imprint separator. Adjacent lettering bends in the photograph. |
| p79-left-2103 | [50,1975,210,2231] | Matching stroke tip of a distinct drawing. The crop cuts off the rest of the drawing. |
| p79-SW | [65,2469,225,2629] | Matching printed folio 79 |

The folios offer corner landmarks, and the imprint and drawing offer limited fore-edge support. Those candidate features require independent coordinate confirmation. The result covers only the fixed windows. It includes no fitted transform, uncertainty interval, displacement estimate or stencil reading.

## Reproduce the windows

Use the [2040×2805 source photograph PDF](../../../keyser%20bitcoin%20.pdf) and the [2544×3264 source scan PDF](../../../magazine.pdf), with PyMuPDF 1.26.5 and Pillow 11.3.0. Verify the PDF and embedded image hashes against the machine result. Use zero-based PDF pages 5 and 6. Decode the single embedded JPEG for each page to RGB. Keep the lower-resolution raster in native orientation and transpose the higher-resolution raster by 180° to upright.

For each foot interval, take the 256-pixel span centered at its fixed x transect and the 160 pixels above its lower y bound. For right and left fore-edge marks use the 256-pixel span centered at the fixed y transect and 160 pixels inward from the marked x interval. For each corner use a 160×160 px rectangle inward from both coordinate ranges. The table and JSON give the resulting half-open bounds. Crop these rectangles in native lower-resolution pixels and identify the corresponding printed feature by appearance in the upright high-resolution face. Keep paper texture, shadows and the raster boundary outside the landmark set.

A second focused inspection regenerated the six foot crops after reading the first assessment. It also found blank margins or perimeter texture in each crop. This check covered only the six foot windows. [Original foot-window pixels](FOOT_WINDOWS.png)

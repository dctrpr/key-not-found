# What the scans establish about alignment

The two raster families give us digital image positions. Neither gives a measured physical displacement range for pages 76/77 or 78/79. The lower-resolution photographs show partial paper edges, material outside the page and gutter curvature. They supply a source for checking edge visibility before fitting an alignment. [Higher-resolution scan](../../../magazine.pdf) · [Lower-resolution photographs](../../../keyser%20bitcoin%20.pdf) · [Source register](../../../sources/provenance.json)

## Raster lineage

- The higher-resolution PDF embeds one 2544 × 3264 JPEG per checked face, covering the full 610.56 × 783.36 pt frame with PDF rotation 180°. All four embedded images match the frozen word geometry. The original and sanitized wrappers have the same embedded bytes and placement. The original explicit TrimBox equals its MediaBox. The public wrapper preserves the media frame and image placement.
- The native JPEG cache regenerates from those embedded images at quality 95. Rotating each cached image 180° and re-encoding at quality 92 reproduces the retained upright cache byte for byte. These operations account for the orientation of the scans. The observed offset between the digital frame origins is exactly zero.
- The two retained lower-resolution PDF paths are byte-identical in the public corpus. Each page places one 2040 × 2805 JPEG on a 612 × 792 pt frame at `[18,0,594,792]` pt. The 18 pt inset is wrapper placement. The archive supplies no documented camera geometry, matching physical points or proof of independent acquisition. [Duplicate lower-resolution PDF](../../external_clues/google_drive_article_download.pdf)

The corrected gutter and page-order evidence supports testing 76/77 and 78/79 as the pair blocks. The earlier horizontal-mirror texture check exceeded its control threshold on zero of the three corrected pairs. Its white-mask fit optimized landing on selected content. It gives no independently measured registration range. [Page order audit](../../continuation_20261109/state_audit.md) · [Texture comparison](../../source_audit/corrected_topology_77_76_light_table/corrected_topology_77_76_light_table.md)

## Reproduce the public metadata checks

[Public raster replay receipt](RASTER_VERIFICATION.json)

Use PyMuPDF 1.26.5 and Pillow 11.3.0. PDF indices for printed pages 76–79 are 3–6. Inspect `xref_get_key(page.xref, "MediaBox")`, `"TrimBox"` and `"Rotate"`. Use `page.get_image_rects(xref, transform=True)` to check placement and `document.extract_image(xref)["image"]` to hash the exact embedded bytes. Decode each higher-resolution JPEG to RGB and encode at quality 95. Reopen the result, transpose `ROTATE_180`, and encode at quality 92. Compare to the two retained caches. For the perimeter review, inspect the lower-resolution embedded images in their native orientation with the content center covered. [Native cache](../../source_images/) · [Upright cache](../../3d_article_map/) · [Frozen geometry](../../../sources/word-geometry-20261110.json)

| Printed page | Higher-resolution embedded image SHA-256 |
| --- | --- |
| 76 | `d9f4a15c43f39b3af4840e9e92833117938c6c79a690c10a3623160c66778d3c` |
| 77 | `e7aa5974278bc65142ecf11cf11bcef9c21ee85ca717585d553ce7de6e37347b` |
| 78 | `81066fc47ebee1654826f1957391bed19271189d817d45ec672c9f11a92ce29a` |
| 79 | `984a7baaf2bebef86c7ad83fdb758e66fa7ab201c5e0e4f797e27927708c784b` |

A physical range would require repeatably identifiable trim edges or fiducials on both faces, a coordinate link to the pinned raster, and measured residuals. First document which edges are visible and how much gutter curvature they contain. A border that cannot be traced reproducibly leaves that degree of alignment unresolved.

# Current Scan Background Seam Residual Gate

Scope: background-only seam/gutter scan of current page rasters. Foreground text/highlight ink is masked out before looking for broad luminance transitions. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-24T16:21:27`
- Pages checked: `4`
- Page-76 structural vertical/horizontal seam lines: `0` / `24`
- Page-76 unique structural vertical/horizontal lines: `0` / `14`
- Active boxes close to unique structural x/y lines at <=16px: `0` / `1`
- All-four active close to unique structural x/y lines at <=16px: `0` / `0`
- Shared active vertical/horizontal line hits at <=16px: `0` / `1`
- Controls close to unique structural x/y lines at <=16px: `0` / `2`
- OVERDOSE slots close to unique structural x/y lines at <=16px: `0` / `0`
- Source-backed R3 hits / satisfied triggers: `0` / `0/9`
- Fingerprint: `pages=4|p76V=0|p76H=24|uniqV=0|uniqH=14|activeX16=0|activeY16=1|allX16=0|allY16=0|sharedX16=0|sharedY16=1|sourceR3=0|triggers=0/9|selectors=0`

## Page-76 Background Profile

- Background share: `0.925779`
- Vertical profile threshold / max z / max support: `16.0` / `0.0` / `0.0`
- Horizontal profile threshold / max z / max support: `16.0` / `19.640568` / `0.092374`
- Unique vertical coords: `none`
- Unique horizontal coords: `619,681,751,769,1162,1452,1506,1524,2116,2137,2355,2572,2643,2795`

## Active Rows

| id | phrase | close x16 | close y16 | nearest x anchors | nearest y anchors |
|---|---|---:|---:|---|---|
| `O4` | `buying the dip` | `0` | `0` | `left:None:None; center:None:None; right:None:None` | `top:2137:40.0; center:2137:64.0; bottom:2137:88.0` |
| `B4` | `$1 billion` | `0` | `0` | `left:None:None; center:None:None; right:None:None` | `top:2355:43.0; center:2355:66.5; bottom:2355:90.0` |
| `G5` | `Volcano Bonds` | `0` | `1` | `left:None:None; center:None:None; right:None:None` | `top:2572:28.0; center:2572:4.0; bottom:2572:20.0` |
| `O5` | `shitcoiner at heart` | `0` | `0` | `left:None:None; center:None:None; right:None:None` | `top:2795:137.0; center:2795:162.0; bottom:2795:187.0` |

## Decision

- `background_seam_residual_not_a_selector`.
- Reason: Background-only structural seam lines do not produce an all-four active alignment, do not supply a shared vertical/horizontal line carrier, and still have no source-backed R3 trigger.
- Next move: Keep page-76 background seam/gutter residuals closed. Reopen only if a new physical/original-layout source changes page-background seams or raw clue wording explicitly names a seam, gutter, trim, fold, or crop-line read.

Sheet: `analysis_outputs/source_audit/current_scan_background_seam_residual_gate/current_scan_background_seam_residual_gate_sheet.jpg`

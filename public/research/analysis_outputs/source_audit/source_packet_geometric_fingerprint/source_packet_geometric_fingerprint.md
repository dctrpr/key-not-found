# Source Packet Geometric Fingerprint

Scope: record O4/B4/G5/O5 active-quartet geometry for future source/original-layout comparison. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.

- Created: `2026-05-21T06:06:41`
- Active order: `buying_dip -> one_billion -> volcano_bonds -> shitcoiner_heart`
- Visual-state order: `YKKY`
- Page lines: `22 25 27 32`
- Corridor indexes: `4 7 9 14`
- Page-line gaps: `[3, 2, 5]`
- Corridor gaps: `[3, 2, 5]`
- Center-step signs: dx `-++`, dy `+++`
- Cluster box: `[428, 2177, 1801, 2982]`
- Cluster size: `[1373, 805]`
- Cluster centroid: `[1118.25, 2536.875]`
- Native rotate180 max center roundtrip error: `0.0px`
- Native rotate180 max box roundtrip error: `0.0px`
- OVERDOSE header glyph sequence: `OVERDOSE`
- OVERDOSE header-to-cluster centroid vector: `{'dx': -1102.87, 'dy': 2368.23, 'distancePx': 2612.439, 'angleDegreesImageYDown': 114.971}`
- Registration fingerprint: `order=buying_dip/one_billion/volcano_bonds/shitcoiner_heart|states=YKKY|lines=22-25-27-32|corr=4-7-9-14|lineGaps=3-2-5|corrGaps=3-2-5|dxSigns=-++|dySigns=+++|cluster=1373x805|nativeRoundtripCenter=0.0`
- Sheet: `analysis_outputs/source_audit/source_packet_geometric_fingerprint/source_packet_geometric_fingerprint_sheet.jpg`

## Pairwise Geometry

| from | to | visual | line gap | corridor gap | dx | dy | distance px | angle image-y-down |
|---|---|---|---:|---:|---:|---:|---:|---:|
| `buying_dip` | `one_billion` | `YK` | `3` | `3` | `-1008.0` | `220.5` | `1031.835` | `167.661` |
| `buying_dip` | `volcano_bonds` | `YK` | `5` | `5` | `-572.0` | `367.0` | `679.612` | `147.315` |
| `buying_dip` | `shitcoiner_heart` | `YY` | `10` | `10` | `-217.0` | `756.0` | `786.527` | `106.015` |
| `one_billion` | `volcano_bonds` | `KK` | `2` | `2` | `436.0` | `146.5` | `459.955` | `18.573` |
| `one_billion` | `shitcoiner_heart` | `KY` | `7` | `7` | `791.0` | `535.5` | `955.218` | `34.098` |
| `volcano_bonds` | `shitcoiner_heart` | `KY` | `5` | `5` | `355.0` | `389.0` | `526.636` | `47.617` |

## Decision

- Keep this as a source-validation fingerprint only.
- It does not reopen folded/mirrored 3D geometry, bold-letter, highlight, or OVERDOSE layout selectors.
- It gives future source comparison a stable geometry target: order, gaps, center-step signs, cluster size, and native rotate180 roundtrip.
- Extraction remains blocked until source/provenance wording supplies R3 unit/order evidence.

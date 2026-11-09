# Current Scan Page Frame / Trim Registration Gate

Scope: inspected current upright/source page rasters for a measurable page-frame, trim-line, skew, or crop-offset cue that could justify changing valid page-75 -> page-76 held-to-light registration. This is geometry/source validation only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T10:57:17+02:00`
- Pages checked: `[75, 76, 78, 79]`
- Valid pair / same canvas: `75->76` / `1`
- Pages with all four frame-like edges: `0`
- Valid pair both pages all-edge frame-like: `0`
- Trim correction candidate / hidden trim-skew candidate: `0` / `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_page_frame_trim_registration_gate/current_scan_page_frame_trim_registration_gate_sheet.jpg`
- Fingerprint: `pages=4|pair=75->76|sameCanvas=1|allEdgesPages=0|pairAllEdges=0|trimCandidate=0|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Page Edge Rows

| page | mode | top med/cov/iqr | bottom med/cov/iqr | left med/cov/iqr | right med/cov/iqr | frame-like edges |
|---:|---|---|---|---|---|---:|
| `75` | `source_rot180_to_readable` | `337.0/0.383648/24.5` | `300.0/0.490566/8.0` | `32.0/0.480392/3.0` | `0.0/0.830882/0.0` | `0` |
| `76` | `source_rot180_to_readable` | `138.0/0.179245/164.0` | `281.0/0.669811/160.0` | `40.0/0.867647/3.0` | `97.0/0.536765/219.0` | `0` |
| `78` | `source_rot180_to_readable` | `134.0/0.091195/3.0` | `126.5/0.220126/325.75` | `41.0/0.982843/10.0` | `76.0/0.247549/174.0` | `1` |
| `79` | `source_rot180_to_readable` | `144.5/0.352201/153.25` | `263.0/0.308176/105.5` | `90.0/0.590686/99.0` | `0.0/0.941176/1.0` | `1` |

## Valid 75 -> 76 Edge Deltas

| side | median first-content delta px | coverage delta | edge-band share delta | both frame-like |
|---|---:|---:|---:|---:|
| `top` | `-199.0` | `-0.204403` | `0.002031` | `0` |
| `bottom` | `-19.0` | `0.179245` | `0.001294` | `0` |
| `left` | `8.0` | `0.387255` | `0.0` | `0` |
| `right` | `97.0` | `-0.294117` | `-0.157744` | `0` |

## Active Target Frame Use

- Page-76 active boxes were only measured against the canvas because no reliable physical page-frame line was detected.
- Active box distance rows: `4`

## Decision

- `current_scan_page_frame_trim_registration_no_selector`
- The valid 75->76 pages share the same `2544x3264` canvas, but the edge profiles do not expose a stable all-edge physical trim/frame line.
- Edge hits are content/margin profiles rather than a registration frame, so they do not justify a hidden trim, skew, or crop correction.

## Next Move

- Keep current-scan held-to-light registration closed unless a distinct physical/original-layout source supplies a measurable page-frame or registration cue. The best direction remains source validation or raw clue wording that names unit/order/transform.

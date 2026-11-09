# Current Scan OVERDOSE Glyph Stroke-Centroid Gate

Scope: detected the actual orange ink components of the p76/p78 `OVERDOSE` headers, projected their stroke centroids into the C9 frame, and compared O4/B4/G5/O5 plus existing controls. No OCR-to-key extraction, candidate generation, hashing, seed/WIF/address checks, BIP39, or broad brute force was run.

- Created: `2026-05-24T19:18:33`
- Header projections / component counts: `2` / `[8, 8]`
- Region rows / active / controls: `27` / `4` / `23`
- Best active any-anchor close<=16px rows: `2/4`
- Best control any-anchor close<=16px rows: `10`
- All-four active any-anchor / center close projections: `0` / `0`
- Active-better-than-control-p05 projection count: `0`
- Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`
- Sheet: `analysis_outputs/source_audit/current_scan_overdose_glyph_stroke_centroid_gate/current_scan_overdose_glyph_stroke_centroid_gate_sheet.jpg`
- Fingerprint: `headers=2|components=8,8|rows=27|activeClose16=2|controlClose16=10|allFourAny=0|allFourCenter=0|activeP05=0|sourceR3=0|triggers=0/9|selectors=0`

## Projection Rows

| projection | center stream | left/right streams | active close<=16 | control close<=16 | control p05 | best active/control distance |
|---|---|---|---:|---:|---:|---:|
| `p76_orange_stroke_centroids` | `OVED` | `DOER/SVRO` | 2 | 10 | 4.179 | 4.179 / 0.303 |
| `p78_orange_stroke_centroids` | `OVED` | `DOER/SVRO` | 1 | 5 | 0.082 | 0.082 / 0.082 |

## Decision

- `current_scan_overdose_glyph_stroke_centroid_no_selector`.
- Actual orange stroke centroids do not make the active quartet an all-four close alignment.
- Controls still produce comparable close centroid contacts, and no source-backed R3 unit/order trigger is satisfied.
- Keep OVERDOSE stroke geometry as source-validation context only.

## Next Move

- Stop tuning current-scan OVERDOSE stroke/slot geometry.
- Highest-value direction remains a distinct physical/original-layout/source asset or raw clue wording that supplies the missing unit, order, or transform.

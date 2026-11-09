# Current-Scan Valid-Leaf Local-Warp Gate

Scope: tested the current scan/PDF page images under the physically valid page 75 -> page 76 held-to-light topology, but allowed each target box an independent local translation in `[-120,120]` px at 20 px steps. This is a generous upper bound for page curl/warp, not an extraction path. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39, or broad brute force were run.

- Created: `2026-05-24T06:46:28`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_gate/current_scan_valid_leaf_local_warp_gate_sheet.jpg`
- Active boxes / projected OVERDOSE slots: `4` / `8`
- Local shifts per box: `169`
- Active best source-only coverage max/min/mean: `0.0693` / `0.0038` / `0.0248`
- Active boxes above same-size control p95: `0/4`
- Active boxes at least 10% / 25% source-only coverage: `0` / `0`
- Max active control percentile: `0.210`
- Max control best source-only coverage: `0.9982`
- Active local-shift dx/dy range: `120` / `240`
- Max OVERDOSE-slot best source-only coverage / slots at least 25%: `0.2575` / `1`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `active=4|slots=8|shifts=169|activeMax=0.0693|activeMin=0.0038|activeMean=0.0248|activeP95=0|active10=0|active25=0|pctMax=0.210|controlMax=0.9982|warpRange=120/240|slotMax=0.2575|slot25=1|sourceR3=0|triggers=0/9|selectors=0`

## Active Rows

| target | phrase | best dx | best dy | best source-only | control percentile | control p95 | control max | above p95 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| O4 | buying the dip | 0 | -120 | 0.0118 | 0.096 | 0.8843 | 0.9582 | no |
| B4 | $1 billion | -120 | 120 | 0.0038 | 0.118 | 0.9515 | 0.9982 | no |
| G5 | Volcano Bonds | -80 | -100 | 0.0693 | 0.210 | 0.8974 | 0.9581 | no |
| O5 | shitcoiner at heart | -120 | 120 | 0.0144 | 0.047 | 0.7385 | 0.9141 | no |

## OVERDOSE Slots

| slot | letter | best dx | best dy | best source-only |
|---:|---|---:|---:|---:|
| 0 | O | -120 | 100 | 0.0027 |
| 1 | V | -120 | 100 | 0.0442 |
| 2 | E | -120 | 100 | 0.1231 |
| 3 | R | 0 | 100 | 0.1306 |
| 4 | D | -120 | 20 | 0.1444 |
| 5 | O | -120 | 20 | 0.2214 |
| 6 | S | 0 | 60 | 0.2575 |
| 7 | E | 120 | 60 | 0.2105 |

## Decision

- `valid_leaf_local_warp_no_selector`
- Even with per-box local translation as a generous upper bound for page curl/warp, all four active boxes stay below their same-size control p95 and below 10% source-only coverage. Control boxes can be made much stronger under the same rule.
- Treat local held-to-light warp/curl compensation as closed for the current scan. Further progress needs distinct source/original-layout material or raw clue wording that names the transform, unit, and order.

# Current Scan Physical Bleed-Through Correlation Gate

Scope: tested whether the current scan/PDF-derived page images already contain real physical backside bleed-through. Mirrored source-page darkness was compared with target-page darkness in low-ink/background regions for fixed valid leaf pairs and invalid source-page controls. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.

- Created: `2026-05-24T12:55:04`
- Valid leaf pairs / invalid control pairs: `3` / `27`
- Valid pairs above same-target invalid-control p95: `0` / `3`
- Page 75->76 darkness delta / invalid-control p95: `0.707301` / `0.961401`
- Page 76 active boxes above invalid-source p95: `0` / `4`
- Page 76 active boxes with enough source-signal pixels: `0` / `4`
- All-four active above invalid-source p95: `0`
- Median valid/control darkness delta: `0.707301` / `0.380306`
- Max valid/control darkness delta: `0.948513` / `3.363945`
- Hidden physical bleed-through candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_physical_bleedthrough_correlation_gate/current_scan_physical_bleedthrough_correlation_gate_sheet.jpg`
- Fingerprint: `pairs=30|valid=3|controls=27|validAboveP95=0|page76Delta=0.707301|page76P95=0.961401|activeAbove=0/4|activeEnoughSignal=0/4|validMedian=0.7073|controlMedian=0.3803|validMax=0.9485|controlMax=3.3639|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Valid Pair Rows

| pair | delta | invalid p95 | above p95 | source signal pixels | corr |
|---|---:|---:|---:|---:|---:|
| `75->76` | `0.707301` | `0.961401` | `0` | `584046` | `0.03765216` |
| `77->78` | `-0.253771` | `0.437206` | `0` | `6957721` | `-0.01385778` |
| `79->80` | `0.948513` | `2.273337` | `0` | `152167` | `0.01840951` |

## Page 76 Active Rows

| target | phrase | delta | invalid-source p95 | above p95 | source signal pixels | source signal fraction |
|---|---|---:|---:|---:|---:|---:|
| `O4` | `buying the dip` | `None` | `0.0` | `0` | `113` | `0.17199391` |
| `B4` | `$1 billion` | `None` | `0.039135` | `0` | `0` | `0.0` |
| `G5` | `Volcano Bonds` | `None` | `-2.496163` | `0` | `108` | `0.02329594` |
| `O5` | `shitcoiner at heart` | `None` | `-1.962763` | `0` | `107` | `0.05898567` |

## Region Rows

| region | delta | signal pixels | corr |
|---|---:|---:|---:|
| `page76_active_envelope_padded48` | `-0.454619` | `115190` | `-0.01959538` |
| `page76_full_page` | `0.707301` | `584046` | `0.03765216` |

## Decision

- `current_scan_physical_bleedthrough_correlation_no_selector`
- The current page images do not behave like a physically translucent scan that makes page 75 visibly bleed into page 76 in a selective way.
- Valid leaf-pair darkness deltas do not beat invalid source-page controls, and the page-76 active quartet does not have all-four active-box support.
- This keeps current scan/PDF images in the witness/provenance bucket, not the extraction-source bucket.

## Next Move

- Continue only with true physical/original-layout source validation or raw clue wording that names the missing registration unit, reading order, or transform.

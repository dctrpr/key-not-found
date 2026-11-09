# Current PDF OSE Highlight Translation Rescue Gate

Scope: computed exact global-translation intervals needed for the two mirrored OSE page-75 source-highlight boxes to overlap locked page-76 O4/B4/G5/O5 targets. This is a bounded geometry feasibility check only; no OCR-to-key extraction, key candidates, hashes-to-key, WIF, seed, address, BIP39, or broad brute-force checks were run.

- Created: `2026-05-24T17:26:46`
- Decision: `pdf_ose_highlight_translation_rescue_no_selector`
- OSE source highlights / active targets: `2` / `4`
- Natural active coverage: `0/4`
- Best coverage within `160` px: `0/4`
- Best coverage within `320` px: `1/4`
- Minimum one-target shift: `dx=0.0, dy=-190.0, Linf=190.0`
- Minimum two-target shift: `dx=-928.0, dy=0.0, Linf=928.0`
- Three-target translation possible: `0`
- Four-target translation possible: `0`
- Selector candidates: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Fingerprint: `sources=2|targets=4|natural=0|small160=0|moderate320=1|oneLinf=190.0|twoLinf=928.0|threePossible=0|fourPossible=0|candidates=0|sourceR3=0|triggers=0/9|selectors=0`
- Sheet: `analysis_outputs/source_audit/current_pdf_ose_highlight_translation_rescue_gate/current_pdf_ose_highlight_translation_rescue_gate_sheet.jpg`

## Best Translation Solutions

| requested coverage | dx | dy | L-inf | actual coverage at closest shift | assignment |
|---:|---:|---:|---:|---|---|
| `1` | `0.0` | `-190.0` | `190.0` | `O4` | `p75_orange_7->O4` |
| `2` | `-928.0` | `0.0` | `928.0` | `B4,G5` | `p75_orange_7->B4; p75_orange_8->G5` |
| `3` | `-` | `-` | `-` | `-` | `impossible` |
| `4` | `-` | `-` | `-` | `-` | `impossible` |

## Closest Pairwise Hits

| source | target | closest dx | closest dy | L-inf | interval dx | interval dy |
|---|---|---:|---:|---:|---|---|
| `p75_orange_7` | `O4` | `0.0` | `-190.0` | `190.0` | `[-758.0, 182.0]` | `[-287.0, -190.0]` |
| `p75_orange_8` | `O4` | `-8.0` | `-328.0` | `328.0` | `[-666.0, -8.0]` | `[-423.0, -328.0]` |
| `p75_orange_8` | `O5` | `-148.0` | `332.0` | `332.0` | `[-960.0, -148.0]` | `[332.0, 429.0]` |
| `p75_orange_7` | `G5` | `-423.0` | `80.0` | `423.0` | `[-1297.0, -423.0]` | `[80.0, 177.0]` |
| `p75_orange_7` | `O5` | `0.0` | `468.0` | `468.0` | `[-1052.0, 42.0]` | `[468.0, 567.0]` |
| `p75_orange_8` | `G5` | `-613.0` | `0.0` | `613.0` | `[-1205.0, -613.0]` | `[-56.0, 39.0]` |
| `p75_orange_7` | `B4` | `-928.0` | `0.0` | `928.0` | `[-1664.0, -928.0]` | `[-66.0, 30.0]` |
| `p75_orange_8` | `B4` | `-1118.0` | `-108.0` | `1118.0` | `[-1572.0, -1118.0]` | `[-202.0, -108.0]` |

## Decision

- `pdf_ose_highlight_translation_rescue_no_selector`.
- A small physical-style registration correction does not rescue OSE onto any active target.
- The first active contact needs a `190px` vertical shift, which is already outside the small tolerance used for scan-slip checks.
- Two-target coverage needs a roughly half-page horizontal relocation (`928px`), and three/four-target coverage is impossible for these two OSE highlight boxes under one global shift.

## Next Move

- Keep OSE as slot-band provenance only. Reopen only with source/clue wording that names a non-arbitrary transform and read order.

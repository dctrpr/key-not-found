# Current Scan Active Source-Highlight Ablation Gate

Scope: removes mirrored page-75 source-highlight rectangles from the natural `75->76` held-to-light source mask, then remeasures O4/B4/G5/O5 and matched line-shift controls. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T12:43:49`
- Active targets checked: `4`
- Baseline positive targets: `O4,G5,O5`
- Positive targets after all source-highlight ablation: `O4,G5,O5`
- All-four active positive before/after ablation: `0` / `0`
- B4 source ink before/after ablation: `0.000000` / `0.000000`
- Mean/max active source-ink drop after ablation: `0.000%` / `0.000%`
- Control positives before/after ablation: `13` / `12` of `24`
- Hidden active highlight-ablation candidate: `0`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Sheet: `analysis_outputs/source_audit/current_scan_active_source_highlight_ablation_gate/current_scan_active_source_highlight_ablation_gate_sheet.jpg`
- Fingerprint: `targets=4|baselinePositive=O4,G5,O5|afterAllPositive=O4,G5,O5|B4Base=0.000000|B4After=0.000000|meanDropPct=0.0|maxDropPct=0.0|controlsPositive=13->12|hiddenCandidate=0|sourceR3=0|triggers=0/9|selectors=0`

## Active Target Trace

| target | baseline ink | after all highlights | drop | after overlapping highlights | overlapping source highlights | positive after all |
|---|---:|---:|---:|---:|---|---:|
| `O4` | 0.140212 | 0.140212 | 0.000% | 0.140212 | - | 1 |
| `B4` | 0.000000 | 0.000000 | 0.000% | 0.000000 | - | 0 |
| `G5` | 0.059643 | 0.059643 | 0.000% | 0.059643 | - | 1 |
| `O5` | 0.194042 | 0.194042 | 0.000% | 0.194042 | - | 1 |

## Decision

- `current_scan_active_source_highlight_ablation_no_selector`
- B4 remains zero before and after source-highlight ablation.
- The active target source-ink pattern is partial, not all-four, and still has no source-backed unit/order wording.

## Next Move

- Continue with physical/original-layout source validation or raw clue wording that names unit/order/transform.
- If staying local-only, move away from held-to-light density and inspect constrained folded geometry or original PDF/source acquisition evidence.

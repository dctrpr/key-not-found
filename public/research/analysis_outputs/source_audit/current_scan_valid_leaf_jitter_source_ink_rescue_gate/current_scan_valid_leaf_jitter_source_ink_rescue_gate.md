# Current Scan Valid Leaf Jitter Source-Ink Rescue Gate

Scope: tested whether small jitter around the natural same-leaf 75->76 held-to-light registration can rescue B4 source ink or create a source-supported O4/B4/G5/O5 quartet. The credible window is the documented common visual tolerance from the source-packet alignment gate. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.

- Created: `2026-05-24T09:02:56`
- Credible shift window: `+-4px`
- Extended guardrail window: `+-8px`
- Credible shift rows / extended rows: `81` / `289`
- Credible all-four source-supported rows / B4-positive rows: `0` / `0`
- Extended all-four source-supported rows / B4-positive rows: `0` / `0`
- Best credible shift: `0,0` with active support `3/4`, B4 `0.0000`, min `0.0000`
- Best extended shift: `0,0` with active support `3/4`, B4 `0.0000`, min `0.0000`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Overlay: `analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate/best_b4_jitter_source_ink_overlay.jpg`
- Sheet: `analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate/current_scan_valid_leaf_jitter_source_ink_rescue_gate_sheet.jpg`
- Fingerprint: `credible=+-4|extended=+-8|credibleRows=81|extendedRows=289|credAll4=0|extAll4=0|credB4Pos=0|extB4Pos=0|bestCred=0,0:3/4:B4=0.0000:min=0.0000|bestExt=0,0:3/4:B4=0.0000:min=0.0000|bestCredRatios=O4:0.1402,B4:0.0000,G5:0.0596,O5:0.1940|sourceR3=0|triggers=0/9|selectors=0`

## Best Credible Target Rows

| target | phrase | source ink ratio | control p95 | supported | weak supported |
|---|---|---:|---:|---:|---:|
| `O4` | `buying the dip` | 0.140212 | 0.473969 | 1 | 1 |
| `B4` | `$1 billion` | 0.000000 | 0.000000 | 0 | 0 |
| `G5` | `Volcano Bonds` | 0.059643 | 0.210645 | 1 | 1 |
| `O5` | `shitcoiner at heart` | 0.194042 | 0.258535 | 1 | 1 |

## Decision

- `current_scan_valid_leaf_jitter_source_ink_rescue_no_selector`
- The documented `+-4px` tolerance window does not rescue B4 source ink.
- The `+-8px` guardrail window also has no B4-positive row and no all-four source-supported row.
- This stabilizes the previous B4 zero-source-ink closure against small physical registration jitter.

## Next Move

- Stop pursuing current-scan valid-leaf source-ink rescue without a new source/clue that supplies transform, unit, and order.
- Continue with original-layout/physical source acquisition or raw clue wording scored against the source-acquisition packet and R1-R5 reopen requirements.

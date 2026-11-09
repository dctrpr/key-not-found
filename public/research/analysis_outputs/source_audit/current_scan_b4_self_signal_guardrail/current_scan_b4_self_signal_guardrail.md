# Current Scan B4 Self-Signal Guardrail

Scope: decomposed the valid page-75-to-76 held-to-light average blend into source-supported pixels versus page-76 target-only pixels. This checks whether B4's visual pop is a real back-page source carrier. No key derivation, OCR-to-key extraction, seed/WIF/address checks, hashes, or brute force were run.

- Created: `2026-05-24T09:11:52`
- Scenario: `valid_75_to_76_natural`, mirrored page `75` over page `76`, `dx=0`, `dy=0`
- Blend checked: `average@0.70`
- Active targets / controls: `4` / `24`
- Source-supported outlier targets: `O4,G5,O5`
- Zero-source self-signal targets: `B4`
- All-four source-supported outlier: `False`
- B4 source-ink ratio: `0.000000`
- B4 target-ink ratio: `0.763045`
- B4 average-blend delta: `115.832322`
- B4 matched-control p95 delta: `30.777021`
- B4 delta above matched control p95: `85.055301`
- B4 target-only delta share: `0.995667`
- B4 source-supported delta share: `0.000000`
- Source-backed R3 / satisfied triggers: `0` / `0/9`
- Overlay: `analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail/b4_self_signal_delta_overlay.jpg`
- Sheet: `analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail/current_scan_b4_self_signal_guardrail_sheet.jpg`
- Fingerprint: `scenario=valid_75_to_76_natural|alpha=0.70|targets=4|controls=24|B4src=0.0000|B4targetOnly=0.9957|B4srcDelta=0.0000|B4dCtl=85.06|srcOutliers=3/4|selfZero=B4|all4Src=0|sourceR3=0|triggers=0/9|selectors=0`

## Active Rows

| target | phrase | source ink | target ink | avg delta | control p95 | delta over p95 | target-only delta share | source-supported delta share | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `O4` | buying the dip | `0.140212` | `0.994647` | `93.322166` | `63.773729` | `29.548437` | `0.884764` | `0.114705` | source-supported outlier |
| `B4` | $1 billion | `0.000000` | `0.763045` | `115.832322` | `30.777021` | `85.055301` | `0.995667` | `0.000000` | zero-source self-signal |
| `G5` | Volcano Bonds | `0.059643` | `0.817643` | `118.949778` | `50.123852` | `68.825926` | `0.963742` | `0.032702` | source-supported outlier |
| `O5` | shitcoiner at heart | `0.194042` | `0.978422` | `87.761922` | `42.721548` | `45.040374` | `0.849008` | `0.149590` | source-supported outlier |

## Decision

- `current_scan_b4_self_signal_no_selector`
- B4 has zero valid page-75 source ink but still produces a strong average-blend delta because the page-76 black target phrase is blended against a blank/white source area.
- This explains why the all-four average-blend view can look tempting while still failing as physical back-page evidence.
- Do not use B4 average-blend contrast, or the all-four average-blend visual pop, as a selector without a new source/clue that supplies transform, unit, and order.

## Next Move

- Stop varying current-scan light-table blend, opacity, and small registration jitter for B4.
- Best next direction remains original-layout/physical source acquisition or raw clue wording scored against R1-R5 and the source-acquisition packet.

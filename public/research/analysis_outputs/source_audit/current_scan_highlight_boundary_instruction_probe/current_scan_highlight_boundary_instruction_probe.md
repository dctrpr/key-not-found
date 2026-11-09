# Current-Scan Highlight Boundary Instruction Probe

Created: `2026-05-21T15:00:51`

## Scope

Current-scan page-76 target highlight-edge and crop-window boundary probe for O4/B4/G5/O5; no key derivation, hashing, WIF, seed, address checks, OCR-to-key extraction, or broad candidate generation.

## Inputs

- `activeIndexSlot`: `analysis_outputs/source_audit/source_packet_active_index_slot_control/source_packet_active_index_slot_control.json`
- `articleMap`: `analysis_outputs/3d_article_map/article_3d_map_data.json`
- `sourcePage`: `analysis_outputs/source_images/magazine_page_76.jpg`
- `uprightPage`: `analysis_outputs/3d_article_map/page_76_upright.jpg`
- `sourceReviewGate`: `analysis_outputs/source_audit/source_packet_source_review_gate/source_packet_source_review_gate.json`
- `reopenTriggerMatrix`: `analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/source_packet_reopen_trigger_matrix.json`

## Summary

- Active targets / boundary regions: `4` / `32`.
- Regions with OCR-map word hits: `21`.
- Strict instruction regions: `0` (`target_edge=0`, `crop_window_edge=0`).
- Strict instruction term hits: `-`.
- Context/thematic regions: `2`; context terms: `bitcoin`.
- Source-backed R3 hits / satisfied reopen triggers: `0` / `0/9`.
- Fingerprint: `targets=4|regions=32|wordRegions=21|strictRegions=0|targetStrict=0|cropStrict=0|contextRegions=2|strictTerms=-|contextTerms=bitcoin|sourceR3=0|triggers=0/9|selectors=0`.

## Boundary Rows With Words

| target | kind | side | words | strict | context | text |
|---|---:|---:|---:|---|---|---|
| `O4` | `target_edge` | `top` | 1 | `-` | `-` | ByiiREeraipy" |
| `O4` | `target_edge` | `bottom` | 4 | `-` | `-` | ByiiREeraipy" when he announced |
| `O4` | `crop_window_edge` | `left` | 3 | `-` | `-` | Monetary them Bukele |
| `O4` | `crop_window_edge` | `top` | 2 | `-` | `-` | El Salvador |
| `O4` | `crop_window_edge` | `bottom` | 3 | `-` | `-` | volcanoes to mine |
| `B4` | `target_edge` | `top` | 1 | `-` | `-` | eis |
| `B4` | `target_edge` | `bottom` | 2 | `-` | `-` | eis billions |
| `B4` | `crop_window_edge` | `right` | 3 | `-` | `bitcoin` | tap bitcoin of |
| `B4` | `crop_window_edge` | `top` | 3 | `-` | `-` | I tweeted President |
| `B4` | `crop_window_edge` | `bottom` | 1 | `-` | `-` | collateralized |
| `G5` | `target_edge` | `right` | 1 | `-` | `-` | to |
| `G5` | `target_edge` | `bottom` | 4 | `-` | `-` | rid of those leeches. |
| `G5` | `crop_window_edge` | `left` | 3 | `-` | `-` | billions collateralized and |
| `G5` | `crop_window_edge` | `right` | 4 | `-` | `-` | earnings off tagged could |
| `G5` | `crop_window_edge` | `top` | 6 | `-` | `bitcoin` | in bitcoin — that he should |
| `G5` | `crop_window_edge` | `bottom` | 7 | `-` | `-` | Novogratz in the tweet, figuring he could |
| `O5` | `target_edge` | `left` | 1 | `-` | `-` | a |
| `O5` | `target_edge` | `top` | 1 | `-` | `-` | siukbeodmensertslveaarty |
| `O5` | `target_edge` | `bottom` | 1 | `-` | `-` | siukbeodmensertslveaarty |
| `O5` | `crop_window_edge` | `left` | 1 | `-` | `-` | it. |
| `O5` | `crop_window_edge` | `top` | 7 | `-` | `-` | it. I don't really trust that guy |

## Decision

- `boundary_edges_no_source_instruction_selector`.
- Neither active highlight edges nor the current light-table crop-window boundaries expose source-backed unit/order wording. Nearby OCR words are ordinary article context or noisy active-box text.
- Next move: Stop tuning boundary strips on the current scan. The next useful move is either a manual review of the generated boundary sheet for visual anomalies or a distinct physical/original-layout source that can satisfy R1/R3.

## Artifacts

- Sheet: `analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/current_scan_highlight_boundary_instruction_probe_sheet.jpg`
- Crop panel: `analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/O4_boundary_probe.jpg`
- Crop panel: `analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/B4_boundary_probe.jpg`
- Crop panel: `analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/G5_boundary_probe.jpg`
- Crop panel: `analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/O5_boundary_probe.jpg`

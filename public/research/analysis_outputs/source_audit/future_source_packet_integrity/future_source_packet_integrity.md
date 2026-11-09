# Future Source Packet Integrity

Scope: verify the future-source validation packet and visual review sheet against current benchmark files. No key derivation, hashing, WIF, seed, address, or broad extraction checks were run.

- Created: `2026-05-20T14:14:50`
- Status: `PASS`
- Missing artifacts: `0`
- Stale benchmark inputs: `0`
- Failed benchmark checks: `0`

## Benchmark Checks

| check | pass | value | expected |
|---|---:|---|---|
| `review_sheet_registered` | `True` | `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.jpg` | `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.jpg` |
| `review_panel_count` | `True` | `9` | `9` |
| `tri_contact_repair` | `True` | `{'edgeTouchDx': -38.0, 'edgeTouchTriContactPass': True, 'currentFrame': [1234.0, 2398.0, 2250.0, 2950.0], 'repairFrame': [1196.0, 2398.0, 2212.0, 2950.0]}` | `dx around -38/-40 or tri-contact pass` |
| `exact_edge_signature` | `True` | `[{'name': 'g5_edge_touch_dx_minus_38', 'exactPhraseStream': 'should sell | Volcano Bonds | shitcoiner at heart', 'exactStyleStream': 'RKY', 'instructionHits': {}}, {'name': 'nearest_grid_dx_minus_40', 'exactPhraseStream': 'should sell | Volcano Bonds | shitcoiner at heart', 'exactStyleStream': 'RKY', 'instructionHits': {}}, {'name': 'best_overlap_dx_minus_160_dy_35', 'exactPhraseStream': 'should sell | Volcano Bonds | shitcoiner at heart', 'exactStyleStream': 'RKY', 'instructionHits': {}}]` | `should sell | Volcano Bonds | shitcoiner at heart / RKY` |
| `typeka_authority_registered` | `True` | `{'packetSheet': 'analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg', 'reviewHasPanel': True, 'sourceSheet': 'analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg'}` | `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg` |
| `p77_near_miss_present` | `True` | `71.93` | `recorded p77 near-miss gap` |
| `frontier_dead_branch_count` | `True` | `209` | `>= 208` |

## Required Artifacts

| artifact | exists | size | path |
|---|---:|---:|---|
| `packet_json` | `True` | `11487` | `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json` |
| `packet_md` | `True` | `4264` | `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.md` |
| `review_json` | `True` | `3842` | `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.json` |
| `review_md` | `True` | `1710` | `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.md` |
| `review_sheet` | `True` | `777602` | `analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.jpg` |
| `page76_priority_crop_sheet` | `True` | `541734` | `analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg` |
| `p78_frame_tricontact_json` | `True` | `5537` | `analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json` |
| `p78_frame_tricontact_overlay` | `True` | `273199` | `analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg` |
| `repaired_frame_font_states_json` | `True` | `20590` | `analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states.json` |
| `typeka_authority_sheet` | `True` | `491496` | `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg` |
| `typeka_authority_json` | `True` | `6731` | `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.json` |
| `zero_visual_crop_sheet` | `True` | `928042` | `analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops_sheet.jpg` |
| `p79_pill_baseline_sheet` | `True` | `206613` | `analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry_sheet.jpg` |
| `p77_one_line_near_miss_json` | `True` | `6410` | `analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json` |
| `missing_rule_frontier_json` | `True` | `6820` | `analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json` |

## Assessment

- The future-source packet and review sheet are present and non-empty.
- The packet still points at the live review sheet and the current p78 exact-edge signature remains the same compact benchmark.
- No extraction branch is reopened by this pass; it only verifies that future source comparisons are using current benchmarks.

## Decision

- Use the current packet/review sheet as the source-comparison gate.

## Next Move

- Continue waiting for a true new source/clue; compare it first against the packet and review sheet before any extraction/key work.

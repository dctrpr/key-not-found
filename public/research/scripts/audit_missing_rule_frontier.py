#!/usr/bin/env python3
"""Synthesize the current missing-rule frontier.

This is a bounded investigation pass, not a candidate generator. It reviews the
latest local evidence and closed branches to decide whether another local
selector experiment is justified or whether the next real dependency is source
material / an external rule.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/missing_rule_frontier"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "missing_rule_frontier.json"
OUT_MD = OUT / "missing_rule_frontier.md"

REPORTS = {
    "target_convergence": ROOT / "analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json",
    "next_target_chooser": ROOT / "analysis_outputs/source_audit/page76_next_target_chooser/page76_next_target_chooser.json",
    "g5_o5_units": ROOT / "analysis_outputs/source_audit/g5_o5_local_unit_rules/g5_o5_local_unit_rules.md",
    "exact_edge_word_ops": ROOT / "analysis_outputs/source_audit/exact_edge_literal_word_ops/exact_edge_literal_word_ops.md",
    "symmetric_line_fold": ROOT / "analysis_outputs/source_audit/g5_o5_symmetric_line_fold/g5_o5_symmetric_line_fold.md",
    "axis_spine": ROOT / "analysis_outputs/source_audit/page76_axis_spine_selector/page76_axis_spine_selector.md",
    "mark_pointers": ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.md",
    "rky_rarity": ROOT / "analysis_outputs/docm_format_sources/repaired_rky_signature_rarity/repaired_rky_signature_rarity.json",
    "rky_control": ROOT / "analysis_outputs/docm_format_sources/rky_control_window_contrast/rky_control_window_contrast.json",
    "color_swap": ROOT / "analysis_outputs/source_audit/page76_color_swap_mirror_filter/page76_color_swap_mirror_filter.json",
    "color_swap_take_right": ROOT / "analysis_outputs/source_audit/color_swap_take_right_rule/color_swap_take_right_rule.json",
    "monetizing_near_miss_unit": ROOT / "analysis_outputs/source_audit/monetizing_near_miss_unit/monetizing_near_miss_unit.md",
    "content_box_physical_normalization": ROOT / "analysis_outputs/source_audit/content_box_physical_normalization/content_box_physical_normalization.json",
    "p80_symptom_relief_rule": ROOT / "analysis_outputs/source_audit/p80_symptom_relief_rule/p80_symptom_relief_rule.md",
    "p77_one_line_near_miss": ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json",
    "canva_lineup_shift_scope": ROOT / "analysis_outputs/source_audit/canva_lineup_shift_scope/canva_lineup_shift_scope.json",
    "zero_index_rule_scope": ROOT / "analysis_outputs/source_audit/zero_index_rule_scope/zero_index_rule_scope.json",
    "source_delta_watch": ROOT / "analysis_outputs/source_audit/source_delta_watch/source_delta_watch.json",
    "future_source_validation_packet": ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json",
    "local_source_inventory": ROOT / "analysis_outputs/source_audit/local_source_candidate_inventory/local_source_candidate_inventory.md",
    "priority_crop_pack": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json",
    "active_path_readiness_gate": ROOT / "analysis_outputs/source_audit/active_path_readiness_gate/active_path_readiness_gate.json",
    "active_line_unit_reconciliation": ROOT / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json",
    "plain_correction_selector_impact": ROOT / "analysis_outputs/plain_text_transcript/correction_selector_impact/correction_selector_impact.json",
    "bold_vs_article_active_corridor": ROOT / "analysis_outputs/docm_format_sources/bold_vs_article_active_corridor/bold_vs_article_active_corridor.json",
    "page76_highlight_edge_selector": ROOT / "analysis_outputs/source_audit/page76_highlight_edge_selector/page76_highlight_edge_selector.json",
    "page76_active_highlight_fill": ROOT / "analysis_outputs/source_audit/page76_active_highlight_fill/page76_active_highlight_fill.json",
    "page76_highlight_spill_direction": ROOT / "analysis_outputs/source_audit/page76_highlight_spill_direction/page76_highlight_spill_direction.json",
    "page76_spill_control_comparison": ROOT / "analysis_outputs/source_audit/page76_spill_control_comparison/page76_spill_control_comparison.json",
    "reflection_box_target_overlap": ROOT / "analysis_outputs/3d_article_map/reflection_box_target_overlap/reflection_box_target_overlap.json",
    "reflection_line_pitch_stack_gate": ROOT
    / "analysis_outputs/3d_article_map/reflection_line_pitch_stack_gate/reflection_line_pitch_stack_gate.json",
    "reflection_shifted_carrier_content_gate": ROOT
    / "analysis_outputs/3d_article_map/reflection_shifted_carrier_content_gate/"
    "reflection_shifted_carrier_content_gate.json",
    "page76_highlight_fold_axis_population_gate": ROOT
    / "analysis_outputs/source_audit/page76_highlight_fold_axis_population_gate/page76_highlight_fold_axis_population_gate.json",
    "anchor_point_target_proximity": ROOT / "analysis_outputs/3d_article_map/anchor_point_target_proximity/anchor_point_target_proximity.json",
    "docm_visual_highlight_consistency": ROOT / "analysis_outputs/docm_format_sources/docm_visual_highlight_consistency/docm_visual_highlight_consistency.json",
    "desktop_best_scan_pixel_lock": ROOT / "analysis_outputs/source_audit/desktop_best_scan_pixel_lock/desktop_best_scan_pixel_lock.json",
    "opening_spread_instruction_surface": ROOT / "analysis_outputs/source_audit/opening_spread_instruction_surface/opening_spread_instruction_surface.json",
    "typeka_instruction_surface": ROOT / "analysis_outputs/docm_format_sources/typeka_instruction_surface/typeka_instruction_surface.json",
    "p79_take_all_energy_selector": ROOT / "analysis_outputs/source_audit/p79_take_all_energy_selector/p79_take_all_energy_selector.json",
    "issue24_physical_page_topology": ROOT / "analysis_outputs/source_audit/issue24_physical_page_topology/issue24_physical_page_topology.json",
    "p75_p76_valid_leaf_recheck": ROOT / "analysis_outputs/source_audit/p75_p76_valid_leaf_recheck/p75_p76_valid_leaf_recheck.json",
    "p78_source_graphic_instruction_surface": ROOT / "analysis_outputs/source_audit/p78_source_graphic_instruction_surface/p78_source_graphic_instruction_surface.json",
    "fold_nonboundary_ordering": ROOT / "analysis_outputs/3d_article_map/fold_nonboundary_ordering/fold_nonboundary_ordering.json",
    "obbo_anchor_signature": ROOT / "analysis_outputs/comparison_articles/obbo_anchor_signature/obbo_anchor_signature.json",
    "obbo_boundary_coincidences": ROOT / "analysis_outputs/source_audit/obbo_highres_boundary_coincidences/obbo_highres_boundary_coincidences.json",
    "p78_contact_role_grammar": ROOT / "analysis_outputs/source_audit/p78_contact_role_grammar/p78_contact_role_grammar.json",
    "source_reopen_requirements": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
    "source_reopen_candidate_intake": ROOT / "analysis_outputs/source_audit/source_reopen_candidate_intake/source_reopen_candidate_intake.json",
    "current_local_source_reopen_gate": ROOT
    / "analysis_outputs/source_audit/current_local_source_reopen_gate/current_local_source_reopen_gate.json",
    "external_clue_unit_order_intake": ROOT / "analysis_outputs/external_clues/external_clue_unit_order_intake/external_clue_unit_order_intake.json",
    "p80_package_r3_gate_synthesis": ROOT / "analysis_outputs/source_audit/p80_package_r3_gate_synthesis/p80_package_r3_gate_synthesis.json",
    "p80_numeric_active_order_gate": ROOT / "analysis_outputs/source_audit/p80_numeric_active_order_gate/p80_numeric_active_order_gate.json",
    "active_quartet_capsule_direction_gate": ROOT / "analysis_outputs/source_audit/active_quartet_capsule_direction_gate/active_quartet_capsule_direction_gate.json",
    "active_punctuation_enclosure_gate": ROOT / "analysis_outputs/plain_text_transcript/active_punctuation_enclosure_gate/active_punctuation_enclosure_gate.json",
    "active_font_edge_transition_gate": ROOT / "analysis_outputs/docm_format_sources/active_font_edge_transition_gate/active_font_edge_transition_gate.json",
    "active_mix_proximity_gate": ROOT / "analysis_outputs/docm_format_sources/active_mix_proximity_gate/active_mix_proximity_gate.json",
    "active_quartet_pair_symmetry_gate": ROOT / "analysis_outputs/source_audit/active_quartet_pair_symmetry_gate/active_quartet_pair_symmetry_gate.json",
    "active_target_envelope_density_gate": ROOT
    / "analysis_outputs/source_audit/active_target_envelope_density_gate/active_target_envelope_density_gate.json",
    "active_target_center_path_gate": ROOT
    / "analysis_outputs/source_audit/active_target_center_path_gate/active_target_center_path_gate.json",
    "active_target_center_path_bold_gate": ROOT
    / "analysis_outputs/source_audit/active_target_center_path_bold_gate/active_target_center_path_bold_gate.json",
    "active_line_corridor_mirror_index_gate": ROOT
    / "analysis_outputs/source_audit/active_line_corridor_mirror_index_gate/active_line_corridor_mirror_index_gate.json",
    "g5_axis_bold_highlight_rescue_gate": ROOT
    / "analysis_outputs/source_audit/g5_axis_bold_highlight_rescue_gate/g5_axis_bold_highlight_rescue_gate.json",
    "page76_page_center_mirror_guardrail": ROOT
    / "analysis_outputs/source_audit/page76_page_center_mirror_guardrail/page76_page_center_mirror_guardrail.json",
    "overdose_header_ray_fan_gate": ROOT
    / "analysis_outputs/source_audit/overdose_header_ray_fan_gate/overdose_header_ray_fan_gate.json",
    "c9_glyph_center_ray_gate": ROOT
    / "analysis_outputs/source_audit/c9_glyph_center_ray_gate/c9_glyph_center_ray_gate.json",
    "c9_target_vertical_chord_gate": ROOT
    / "analysis_outputs/source_audit/c9_target_vertical_chord_gate/c9_target_vertical_chord_gate.json",
    "c9_target_horizontal_chord_gate": ROOT
    / "analysis_outputs/source_audit/c9_target_horizontal_chord_gate/c9_target_horizontal_chord_gate.json",
    "active_frame_center_reflection_gate": ROOT / "analysis_outputs/source_audit/active_frame_center_reflection_gate/active_frame_center_reflection_gate.json",
    "active_frame_edge_axis_gate": ROOT / "analysis_outputs/source_audit/active_frame_edge_axis_gate/active_frame_edge_axis_gate.json",
    "active_o4_frame_rescue_gate": ROOT / "analysis_outputs/source_audit/active_o4_frame_rescue_gate/active_o4_frame_rescue_gate.json",
    "o4_frame_rescue_offset_control": ROOT / "analysis_outputs/source_audit/o4_frame_rescue_offset_control/o4_frame_rescue_offset_control.json",
    "o4_frame_rescue_content_gate": ROOT / "analysis_outputs/source_audit/o4_frame_rescue_content_gate/o4_frame_rescue_content_gate.json",
    "o4_frame_rescue_signal_stream_gate": ROOT / "analysis_outputs/source_audit/o4_frame_rescue_signal_stream_gate/o4_frame_rescue_signal_stream_gate.json",
    "o4_frame_rescue_yk_filter_control": ROOT / "analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control.json",
    "o4_frame_yk_unit_order_gate": ROOT / "analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/o4_frame_yk_unit_order_gate.json",
    "overdose_header_registration_gate": ROOT / "analysis_outputs/source_audit/overdose_header_registration_gate/overdose_header_registration_gate.json",
    "overdose_same_slot_control_gate": ROOT / "analysis_outputs/source_audit/overdose_same_slot_control_gate/overdose_same_slot_control_gate.json",
    "typeka_font_r3_gate_synthesis": ROOT / "analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis.json",
    "fold_mirror_r3_gate_synthesis": ROOT / "analysis_outputs/3d_article_map/fold_mirror_r3_gate_synthesis/fold_mirror_r3_gate_synthesis.json",
    "page76_highlight_cluster_r3_gate_synthesis": ROOT / "analysis_outputs/source_audit/page76_highlight_cluster_r3_gate_synthesis/page76_highlight_cluster_r3_gate_synthesis.json",
    "comparison_overdose_layout_r3_gate_synthesis": ROOT / "analysis_outputs/comparison_articles/overdose_layout_r3_gate_synthesis/overdose_layout_r3_gate_synthesis.json",
    "overdose_style_uniqueness": ROOT / "analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness.json",
    "active_evidence_unlock_matrix": ROOT / "analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix.json",
    "post_unlock_source_arrival_watch": ROOT / "analysis_outputs/source_audit/post_unlock_source_arrival_watch/post_unlock_source_arrival_watch.json",
    "source_acquisition_target_packet": ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.json",
    "source_acquisition_packet_integrity": ROOT / "analysis_outputs/source_audit/source_acquisition_packet_integrity/source_acquisition_packet_integrity.json",
    "future_source_scoring_rubric": ROOT / "analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric.json",
    "future_source_rubric_current_stack_dry_run": ROOT / "analysis_outputs/source_audit/future_source_rubric_current_stack_dry_run/future_source_rubric_current_stack_dry_run.json",
    "page76_target_text_authority_lock": ROOT / "analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/page76_target_text_authority_lock.json",
    "page76_target_format_authority_lock": ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json",
    "markdown_docm_mismatch_instruction_surface": ROOT / "analysis_outputs/docm_format_sources/markdown_docm_mismatch_instruction_surface/markdown_docm_mismatch_instruction_surface.json",
    "page76_active_target_crop_completion": ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json",
    "source_packet_crop_authority_sync": ROOT / "analysis_outputs/source_audit/source_packet_crop_authority_sync/source_packet_crop_authority_sync.json",
    "source_packet_yk_frame_benchmark_sync": ROOT
    / "analysis_outputs/source_audit/source_packet_yk_frame_benchmark_sync/source_packet_yk_frame_benchmark_sync.json",
    "source_packet_native_benchmark_bridge": ROOT
    / "analysis_outputs/source_audit/source_packet_native_benchmark_bridge/source_packet_native_benchmark_bridge.json",
    "source_packet_visual_state_roundtrip": ROOT
    / "analysis_outputs/source_audit/source_packet_visual_state_roundtrip/source_packet_visual_state_roundtrip.json",
    "source_packet_alignment_tolerance": ROOT
    / "analysis_outputs/source_audit/source_packet_alignment_tolerance/source_packet_alignment_tolerance.json",
    "source_packet_geometric_fingerprint": ROOT
    / "analysis_outputs/source_audit/source_packet_geometric_fingerprint/source_packet_geometric_fingerprint.json",
    "source_packet_frame_normalized_geometry": ROOT
    / "analysis_outputs/source_audit/source_packet_frame_normalized_geometry/source_packet_frame_normalized_geometry.json",
    "source_packet_color_profile_manifest": ROOT
    / "analysis_outputs/source_audit/source_packet_color_profile_manifest/source_packet_color_profile_manifest.json",
    "source_packet_repaired_p78_frame_residual": ROOT
    / "analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual/"
    "source_packet_repaired_p78_frame_residual.json",
    "source_packet_repaired_frame_expansion_leakage": ROOT
    / "analysis_outputs/source_audit/source_packet_repaired_frame_expansion_leakage/"
    "source_packet_repaired_frame_expansion_leakage.json",
    "source_packet_handoff_integrity_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/"
    "source_packet_handoff_integrity_matrix.json",
    "source_packet_false_positive_guardrail": ROOT
    / "analysis_outputs/source_audit/source_packet_false_positive_guardrail/"
    "source_packet_false_positive_guardrail.json",
    "source_packet_r3_bridge_audit": ROOT
    / "analysis_outputs/source_audit/source_packet_r3_bridge_audit/"
    "source_packet_r3_bridge_audit.json",
    "source_packet_reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
    "source_packet_orientation_disambiguator": ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_disambiguator/"
    "source_packet_orientation_disambiguator.json",
    "source_packet_orientation_control_quartets": ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_control_quartets/"
    "source_packet_orientation_control_quartets.json",
    "source_packet_source_review_gate": ROOT
    / "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json",
    "source_packet_overdose_transform_control": ROOT
    / "analysis_outputs/source_audit/source_packet_overdose_transform_control/"
    "source_packet_overdose_transform_control.json",
    "source_packet_fold_format_intersection_control": ROOT
    / "analysis_outputs/source_audit/source_packet_fold_format_intersection_control/"
    "source_packet_fold_format_intersection_control.json",
    "source_packet_terminal_coverage_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_terminal_coverage_matrix/"
    "source_packet_terminal_coverage_matrix.json",
    "source_packet_active_target_authority_crosscheck": ROOT
    / "analysis_outputs/source_audit/source_packet_active_target_authority_crosscheck/"
    "source_packet_active_target_authority_crosscheck.json",
    "source_packet_active_format_stream_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_format_stream_control/"
    "source_packet_active_format_stream_control.json",
    "source_packet_active_index_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json",
    "source_packet_center_rotation_word_control": ROOT
    / "analysis_outputs/source_audit/source_packet_center_rotation_word_control/"
    "source_packet_center_rotation_word_control.json",
    "source_packet_color_split_span_control": ROOT
    / "analysis_outputs/source_audit/source_packet_color_split_span_control/"
    "source_packet_color_split_span_control.json",
    "source_packet_dominant_overlap_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_dominant_overlap_slot_control/"
    "source_packet_dominant_overlap_slot_control.json",
    "source_packet_span_edge_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_span_edge_slot_control/"
    "source_packet_span_edge_slot_control.json",
    "source_packet_overlap_width_profile_control": ROOT
    / "analysis_outputs/source_audit/source_packet_overlap_width_profile_control/"
    "source_packet_overlap_width_profile_control.json",
    "source_packet_span_neighbor_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_span_neighbor_slot_control/"
    "source_packet_span_neighbor_slot_control.json",
    "source_packet_span_complement_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_span_complement_slot_control/"
    "source_packet_span_complement_slot_control.json",
    "source_packet_local_asset_orientation_gate": ROOT
    / "analysis_outputs/source_audit/source_packet_local_asset_orientation_gate/"
    "source_packet_local_asset_orientation_gate.json",
    "source_packet_pdf_render_quality_gate": ROOT
    / "analysis_outputs/source_audit/source_packet_pdf_render_quality_gate/"
    "source_packet_pdf_render_quality_gate.json",
    "current_scan_held_to_light_simulator": ROOT
    / "analysis_outputs/source_audit/current_scan_held_to_light_simulator/"
    "current_scan_held_to_light_simulator.json",
    "scan_only_held_to_light_adjudication": ROOT
    / "analysis_outputs/source_audit/scan_only_held_to_light_adjudication/"
    "scan_only_held_to_light_adjudication.json",
    "scan_only_held_to_light_tolerance_sweep": ROOT
    / "analysis_outputs/source_audit/scan_only_held_to_light_tolerance_sweep/"
    "scan_only_held_to_light_tolerance_sweep.json",
    "corrected_topology_77_76_light_table": ROOT
    / "analysis_outputs/source_audit/corrected_topology_77_76_light_table/"
    "corrected_topology_77_76_light_table.json",
    "open_heart_capsule_rule": ROOT
    / "analysis_outputs/source_audit/open_heart_capsule_rule/"
    "open_heart_capsule_rule.json",
    "current_scan_held_to_light_active_box_balance_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_held_to_light_active_box_balance_gate/"
    "current_scan_held_to_light_active_box_balance_gate.json",
    "current_scan_held_to_light_component_readability_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_held_to_light_component_readability_gate/"
    "current_scan_held_to_light_component_readability_gate.json",
    "current_scan_held_to_light_opacity_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_held_to_light_opacity_gate/"
    "current_scan_held_to_light_opacity_gate.json",
    "current_scan_light_table_blend_mode_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_light_table_blend_mode_gate/"
    "current_scan_light_table_blend_mode_gate.json",
    "current_scan_valid_leaf_source_ink_landing_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/"
    "current_scan_valid_leaf_source_ink_landing_gate.json",
    "current_scan_all_leaf_light_table_parity_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/"
    "current_scan_all_leaf_light_table_parity_gate.json",
    "current_scan_light_table_density_calibration_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_light_table_density_calibration_gate/"
    "current_scan_light_table_density_calibration_gate.json",
    "current_scan_overdose_density_outlier_provenance_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_overdose_density_outlier_provenance_gate/"
    "current_scan_overdose_density_outlier_provenance_gate.json",
    "current_scan_overdose_density_highlight_ablation_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_overdose_density_highlight_ablation_gate/"
    "current_scan_overdose_density_highlight_ablation_gate.json",
    "current_scan_active_source_highlight_ablation_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_active_source_highlight_ablation_gate/"
    "current_scan_active_source_highlight_ablation_gate.json",
    "current_scan_physical_bleedthrough_correlation_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_physical_bleedthrough_correlation_gate/"
    "current_scan_physical_bleedthrough_correlation_gate.json",
    "current_scan_active_quartet_fingerprint_specificity_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_active_quartet_fingerprint_specificity_gate/"
    "current_scan_active_quartet_fingerprint_specificity_gate.json",
    "current_scan_target_witness_box_substitution_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_target_witness_box_substitution_gate/"
    "current_scan_target_witness_box_substitution_gate.json",
    "current_scan_page76_image_witness_state_stability_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_page76_image_witness_state_stability_gate/"
    "current_scan_page76_image_witness_state_stability_gate.json",
    "current_scan_page76_image_witness_microregistration_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_page76_image_witness_microregistration_gate/"
    "current_scan_page76_image_witness_microregistration_gate.json",
    "current_scan_active_box_overdose_edge_residue_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_active_box_overdose_edge_residue_gate/"
    "current_scan_active_box_overdose_edge_residue_gate.json",
    "current_scan_valid_leaf_jitter_source_ink_rescue_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate/"
    "current_scan_valid_leaf_jitter_source_ink_rescue_gate.json",
    "current_scan_page_frame_trim_registration_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_page_frame_trim_registration_gate/"
    "current_scan_page_frame_trim_registration_gate.json",
    "current_scan_content_box_registration_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_content_box_registration_gate/"
    "current_scan_content_box_registration_gate.json",
    "current_scan_header_footer_lane_registration_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_header_footer_lane_registration_gate/"
    "current_scan_header_footer_lane_registration_gate.json",
    "current_scan_lane_affine_registration_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_lane_affine_registration_gate/"
    "current_scan_lane_affine_registration_gate.json",
    "current_scan_lane_affine_source_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_lane_affine_source_trace/"
    "current_scan_lane_affine_source_trace.json",
    "current_scan_source_layer_landing_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_source_layer_landing_gate/"
    "current_scan_source_layer_landing_gate.json",
    "current_scan_source_layer_miss_distance_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_source_layer_miss_distance_gate/"
    "current_scan_source_layer_miss_distance_gate.json",
    "current_scan_b4_broad_contact_provenance_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_b4_broad_contact_provenance_gate/"
    "current_scan_b4_broad_contact_provenance_gate.json",
    "current_pdf_b4_contact_pixel_provenance_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_b4_contact_pixel_provenance_gate/"
    "current_pdf_b4_contact_pixel_provenance_gate.json",
    "current_pdf_duplicate_background_feature_artifact_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_duplicate_background_feature_artifact_gate/"
    "current_pdf_duplicate_background_feature_artifact_gate.json",
    "current_pdf_page76_carrier_state_stability_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_page76_carrier_state_stability_gate/"
    "current_pdf_page76_carrier_state_stability_gate.json",
    "current_scan_b4_self_signal_guardrail": ROOT
    / "analysis_outputs/source_audit/current_scan_b4_self_signal_guardrail/"
    "current_scan_b4_self_signal_guardrail.json",
    "current_scan_light_table_self_signal_partition_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_light_table_self_signal_partition_gate/"
    "current_scan_light_table_self_signal_partition_gate.json",
    "current_scan_overdose_slot_source_support_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_overdose_slot_source_support_trace/"
    "current_scan_overdose_slot_source_support_trace.json",
    "current_pdf_overdose_slot_source_support_trace": ROOT
    / "analysis_outputs/source_audit/current_pdf_overdose_slot_source_support_trace/"
    "current_pdf_overdose_slot_source_support_trace.json",
    "current_pdf_ose_source_highlight_phrase_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ose_source_highlight_phrase_gate/"
    "current_pdf_ose_source_highlight_phrase_gate.json",
    "current_pdf_ose_highlight_mirror_geometry_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ose_highlight_mirror_geometry_gate/"
    "current_pdf_ose_highlight_mirror_geometry_gate.json",
    "current_pdf_ose_highlight_translation_rescue_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ose_highlight_translation_rescue_gate/"
    "current_pdf_ose_highlight_translation_rescue_gate.json",
    "current_scan_valid_leaf_bleedthrough_control_grid": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_bleedthrough_control_grid/"
    "current_scan_valid_leaf_bleedthrough_control_grid.json",
    "current_scan_valid_leaf_local_warp_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_gate/"
    "current_scan_valid_leaf_local_warp_gate.json",
    "current_scan_valid_leaf_local_warp_source_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_local_warp_source_trace/"
    "current_scan_valid_leaf_local_warp_source_trace.json",
    "current_scan_valid_leaf_edge_contact_control": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_edge_contact_control/"
    "current_scan_valid_leaf_edge_contact_control.json",
    "current_scan_valid_leaf_edge_source_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_edge_source_trace/"
    "current_scan_valid_leaf_edge_source_trace.json",
    "current_scan_valid_leaf_interior_source_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_interior_source_trace/"
    "current_scan_valid_leaf_interior_source_trace.json",
    "current_scan_valid_leaf_glyph_slot_source_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_glyph_slot_source_trace/"
    "current_scan_valid_leaf_glyph_slot_source_trace.json",
    "current_scan_valid_leaf_channel_source_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_channel_source_trace/"
    "current_scan_valid_leaf_channel_source_trace.json",
    "current_scan_valid_leaf_word_collision_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace/"
    "current_scan_valid_leaf_word_collision_trace.json",
    "current_scan_valid_leaf_line_band_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/"
    "current_scan_valid_leaf_line_band_trace.json",
    "valid_leaf_strict_term_disambiguation_gate": ROOT
    / "analysis_outputs/source_audit/valid_leaf_strict_term_disambiguation_gate/"
    "valid_leaf_strict_term_disambiguation_gate.json",
    "valid_leaf_target_context_instruction_gate": ROOT
    / "analysis_outputs/source_audit/valid_leaf_target_context_instruction_gate/"
    "valid_leaf_target_context_instruction_gate.json",
    "current_pdf_page_box_pair_geometry_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_page_box_pair_geometry_gate/"
    "current_pdf_page_box_pair_geometry_gate.json",
    "current_pdf_all_leaf_imposition_consistency_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_all_leaf_imposition_consistency_gate/"
    "current_pdf_all_leaf_imposition_consistency_gate.json",
    "current_pdf_leaf_pair_texture_correlation_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_leaf_pair_texture_correlation_gate/"
    "current_pdf_leaf_pair_texture_correlation_gate.json",
    "current_pdf_native_image_registration_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_native_image_registration_gate/"
    "current_pdf_native_image_registration_gate.json",
    "current_pdf_native_registration_candidate_source_trace": ROOT
    / "analysis_outputs/source_audit/current_pdf_native_registration_candidate_source_trace/"
    "current_pdf_native_registration_candidate_source_trace.json",
    "current_pdf_held_to_light_composite_polarity_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate/"
    "current_pdf_held_to_light_composite_polarity_gate.json",
    "current_pdf_held_to_light_candidate_source_trace": ROOT
    / "analysis_outputs/source_audit/current_pdf_held_to_light_candidate_source_trace/"
    "current_pdf_held_to_light_candidate_source_trace.json",
    "current_pdf_held_to_light_all_target_phrase_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_held_to_light_all_target_phrase_gate/"
    "current_pdf_held_to_light_all_target_phrase_gate.json",
    "current_pdf_held_to_light_color_phrase_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_held_to_light_color_phrase_gate/"
    "current_pdf_held_to_light_color_phrase_gate.json",
    "current_pdf_held_to_light_component_readability_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_held_to_light_component_readability_gate/"
    "current_pdf_held_to_light_component_readability_gate.json",
    "page76_highlight_edge_slot_ruler_gate": ROOT
    / "analysis_outputs/source_audit/page76_highlight_edge_slot_ruler_gate/"
    "page76_highlight_edge_slot_ruler_gate.json",
    "overdose_glyph_axis_ruler_gate": ROOT
    / "analysis_outputs/source_audit/overdose_glyph_axis_ruler_gate/"
    "overdose_glyph_axis_ruler_gate.json",
    "overdose_glyph_axis_word_center_control_gate": ROOT
    / "analysis_outputs/source_audit/overdose_glyph_axis_word_center_control_gate/"
    "overdose_glyph_axis_word_center_control_gate.json",
    "current_pdf_leaf_image_identity_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_leaf_image_identity_gate/"
    "current_pdf_leaf_image_identity_gate.json",
    "current_pdf_render_leaf_simulation_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_render_leaf_simulation_gate/"
    "current_pdf_render_leaf_simulation_gate.json",
    "current_pdf_lowres_render_source_trace": ROOT
    / "analysis_outputs/source_audit/current_pdf_lowres_render_source_trace/"
    "current_pdf_lowres_render_source_trace.json",
    "current_pdf_ocr_reverse_leaf_source_trace": ROOT
    / "analysis_outputs/source_audit/current_pdf_ocr_reverse_leaf_source_trace/"
    "current_pdf_ocr_reverse_leaf_source_trace.json",
    "current_scan_overdose_slot_shape_phase_control": ROOT
    / "analysis_outputs/source_audit/current_scan_overdose_slot_shape_phase_control/"
    "current_scan_overdose_slot_shape_phase_control.json",
    "current_scan_overdose_xslot_phase_control": ROOT
    / "analysis_outputs/source_audit/current_scan_overdose_xslot_phase_control/"
    "current_scan_overdose_xslot_phase_control.json",
    "current_pdf_container_metadata_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_container_metadata_gate/"
    "current_pdf_container_metadata_gate.json",
    "current_pdf_logical_structure_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_logical_structure_gate/"
    "current_pdf_logical_structure_gate.json",
    "current_pdf_navigation_thread_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_navigation_thread_gate/"
    "current_pdf_navigation_thread_gate.json",
    "current_pdf_page_thumbnail_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_page_thumbnail_gate/"
    "current_pdf_page_thumbnail_gate.json",
    "current_pdf_thumbnail_active_signal_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_thumbnail_active_signal_gate/"
    "current_pdf_thumbnail_active_signal_gate.json",
    "current_pdf_content_stream_operator_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_content_stream_operator_gate/"
    "current_pdf_content_stream_operator_gate.json",
    "current_pdf_content_transform_matrix_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_content_transform_matrix_gate/"
    "current_pdf_content_transform_matrix_gate.json",
    "current_pdf_form_xobject_dictionary_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_form_xobject_dictionary_gate/"
    "current_pdf_form_xobject_dictionary_gate.json",
    "current_pdf_form_overlay_placement_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_form_overlay_placement_gate/"
    "current_pdf_form_overlay_placement_gate.json",
    "current_pdf_trailer_xref_integrity_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_trailer_xref_integrity_gate/"
    "current_pdf_trailer_xref_integrity_gate.json",
    "current_pdf_font_cmap_resource_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_font_cmap_resource_gate/"
    "current_pdf_font_cmap_resource_gate.json",
    "current_pdf_embedded_jpeg_marker_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_embedded_jpeg_marker_gate/"
    "current_pdf_embedded_jpeg_marker_gate.json",
    "current_pdf_thumbnail_exif_order_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_thumbnail_exif_order_gate/"
    "current_pdf_thumbnail_exif_order_gate.json",
    "current_pdf_jpeg_compression_provenance_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_jpeg_compression_provenance_gate/"
    "current_pdf_jpeg_compression_provenance_gate.json",
    "current_pdf_jpeg_entropy_tail_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_jpeg_entropy_tail_gate/"
    "current_pdf_jpeg_entropy_tail_gate.json",
    "current_pdf_image_xobject_dictionary_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_image_xobject_dictionary_gate/"
    "current_pdf_image_xobject_dictionary_gate.json",
    "current_pdf_page_resource_order_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_page_resource_order_gate/"
    "current_pdf_page_resource_order_gate.json",
    "current_pdf_object_layout_inspection": ROOT
    / "analysis_outputs/source_audit/current_pdf_object_layout_inspection/"
    "current_pdf_object_layout_inspection.json",
    "current_pdf_partial_image_placement_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_partial_image_placement_gate/"
    "current_pdf_partial_image_placement_gate.json",
    "current_scan_crop_light_table_targets": ROOT
    / "analysis_outputs/source_audit/current_scan_crop_light_table_targets/"
    "current_scan_crop_light_table_targets.json",
    "current_scan_overdose_glyph_crop_projection": ROOT
    / "analysis_outputs/source_audit/current_scan_overdose_glyph_crop_projection/"
    "current_scan_overdose_glyph_crop_projection.json",
    "current_scan_highlight_boundary_instruction_probe": ROOT
    / "analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe/"
    "current_scan_highlight_boundary_instruction_probe.json",
    "current_scan_boundary_light_table_anomaly_probe": ROOT
    / "analysis_outputs/source_audit/current_scan_boundary_light_table_anomaly_probe/"
    "current_scan_boundary_light_table_anomaly_probe.json",
    "current_scan_boundary_contact_source_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_boundary_contact_source_trace/"
    "current_scan_boundary_contact_source_trace.json",
    "current_pdf_ocr_target_provenance_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ocr_target_provenance_gate/"
    "current_pdf_ocr_target_provenance_gate.json",
    "current_pdf_ocr_instruction_scope_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ocr_instruction_scope_gate/"
    "current_pdf_ocr_instruction_scope_gate.json",
    "current_pdf_ocr_document_order_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ocr_document_order_gate/"
    "current_pdf_ocr_document_order_gate.json",
    "current_pdf_ocr_overdose_index_offset_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ocr_overdose_index_offset_gate/"
    "current_pdf_ocr_overdose_index_offset_gate.json",
    "current_pdf_ocr_overdose_neighborhood_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ocr_overdose_neighborhood_gate/"
    "current_pdf_ocr_overdose_neighborhood_gate.json",
    "current_pdf_ocr_page_header_sequence_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ocr_page_header_sequence_gate/"
    "current_pdf_ocr_page_header_sequence_gate.json",
    "current_pdf_visual_header_footer_band_sequence_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_visual_header_footer_band_sequence_gate/"
    "current_pdf_visual_header_footer_band_sequence_gate.json",
    "current_pdf_repeated_overdose_header_lane_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_repeated_overdose_header_lane_gate/"
    "current_pdf_repeated_overdose_header_lane_gate.json",
    "current_pdf_overdose_header_delta_transfer_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_overdose_header_delta_transfer_gate/"
    "current_pdf_overdose_header_delta_transfer_gate.json",
    "current_pdf_overdose_body_start_vector_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_overdose_body_start_vector_gate/"
    "current_pdf_overdose_body_start_vector_gate.json",
    "current_pdf_overdose_body_basis_reflection_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_overdose_body_basis_reflection_gate/"
    "current_pdf_overdose_body_basis_reflection_gate.json",
    "current_pdf_overdose_body_lattice_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_overdose_body_lattice_gate/"
    "current_pdf_overdose_body_lattice_gate.json",
    "current_pdf_overdose_body_offset_transfer_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_overdose_body_offset_transfer_gate/"
    "current_pdf_overdose_body_offset_transfer_gate.json",
    "current_pdf_overdose_body_offset_column_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_overdose_body_offset_column_gate/"
    "current_pdf_overdose_body_offset_column_gate.json",
    "current_pdf_overdose_body_fraction_column_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_overdose_body_fraction_column_gate/"
    "current_pdf_overdose_body_fraction_column_gate.json",
    "current_pdf_ocr_affine_alignment_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_ocr_affine_alignment_gate/"
    "current_pdf_ocr_affine_alignment_gate.json",
    "current_pdf_render_alignment_delta_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_render_alignment_delta_gate/"
    "current_pdf_render_alignment_delta_gate.json",
    "current_pdf_render_resolution_invariance_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_render_resolution_invariance_gate/"
    "current_pdf_render_resolution_invariance_gate.json",
    "current_pdf_active_region_render_embedded_identity_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_active_region_render_embedded_identity_gate/"
    "current_pdf_active_region_render_embedded_identity_gate.json",
    "current_scan_jpeg_block_grid_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_jpeg_block_grid_gate/"
    "current_scan_jpeg_block_grid_gate.json",
    "current_scan_halftone_screen_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_halftone_screen_gate/"
    "current_scan_halftone_screen_gate.json",
    "current_scan_rgb_registration_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_rgb_registration_gate/"
    "current_scan_rgb_registration_gate.json",
    "current_scan_luminance_bitplane_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_luminance_bitplane_gate/"
    "current_scan_luminance_bitplane_gate.json",
    "current_scan_threshold_morphology_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_threshold_morphology_gate/"
    "current_scan_threshold_morphology_gate.json",
    "current_scan_highlight_edge_halo_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_highlight_edge_halo_gate/"
    "current_scan_highlight_edge_halo_gate.json",
    "current_scan_slot_boundary_residual_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_slot_boundary_residual_gate/"
    "current_scan_slot_boundary_residual_gate.json",
    "current_scan_overdose_glyph_stroke_centroid_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_overdose_glyph_stroke_centroid_gate/"
    "current_scan_overdose_glyph_stroke_centroid_gate.json",
    "current_scan_active_envelope_transform_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_active_envelope_transform_gate/"
    "current_scan_active_envelope_transform_gate.json",
    "current_scan_active_envelope_transform_text_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_active_envelope_transform_text_trace/"
    "current_scan_active_envelope_transform_text_trace.json",
    "current_scan_active_envelope_transform_format_trace": ROOT
    / "analysis_outputs/source_audit/current_scan_active_envelope_transform_format_trace/"
    "current_scan_active_envelope_transform_format_trace.json",
    "current_scan_active_envelope_antidiag_overlap_control": ROOT
    / "analysis_outputs/source_audit/current_scan_active_envelope_antidiag_overlap_control/"
    "current_scan_active_envelope_antidiag_overlap_control.json",
    "current_scan_background_seam_residual_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_background_seam_residual_gate/"
    "current_scan_background_seam_residual_gate.json",
    "current_scan_paper_texture_duplex_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_paper_texture_duplex_gate/"
    "current_scan_paper_texture_duplex_gate.json",
    "current_scan_paper_texture_shift_gate": ROOT
    / "analysis_outputs/source_audit/current_scan_paper_texture_shift_gate/"
    "current_scan_paper_texture_shift_gate.json",
    "current_pdf_active_box_coordinate_grid_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_active_box_coordinate_grid_gate/"
    "current_pdf_active_box_coordinate_grid_gate.json",
    "current_pdf_image_rect_margin_phase_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_image_rect_margin_phase_gate/"
    "current_pdf_image_rect_margin_phase_gate.json",
    "local_pdf_filesystem_provenance_gate": ROOT
    / "analysis_outputs/source_audit/local_pdf_filesystem_provenance_gate/"
    "local_pdf_filesystem_provenance_gate.json",
    "local_page_raster_lineage_gate": ROOT
    / "analysis_outputs/source_audit/local_page_raster_lineage_gate/"
    "local_page_raster_lineage_gate.json",
    "current_pdf_color_management_extgstate_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_color_management_extgstate_gate/"
    "current_pdf_color_management_extgstate_gate.json",
    "current_pdf_embedded_channel_mask_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_embedded_channel_mask_gate/"
    "current_pdf_embedded_channel_mask_gate.json",
    "current_pdf_text_overlay_render_mode_gate": ROOT
    / "analysis_outputs/source_audit/current_pdf_text_overlay_render_mode_gate/"
    "current_pdf_text_overlay_render_mode_gate.json",
    "source_packet_fold_world_overdose_order_control": ROOT
    / "analysis_outputs/source_audit/source_packet_fold_world_overdose_order_control/"
    "source_packet_fold_world_overdose_order_control.json",
    "source_packet_bold_phrase_length_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_bold_phrase_length_slot_control/"
    "source_packet_bold_phrase_length_slot_control.json",
    "source_packet_highlight_count_slot_permutation_control": ROOT
    / "analysis_outputs/source_audit/source_packet_highlight_count_slot_permutation_control/"
    "source_packet_highlight_count_slot_permutation_control.json",
    "source_packet_active_span_bridge_control": ROOT
    / "analysis_outputs/source_audit/source_packet_active_span_bridge_control/"
    "source_packet_active_span_bridge_control.json",
    "source_packet_bold_phrase_edge_slot_control": ROOT
    / "analysis_outputs/source_audit/source_packet_bold_phrase_edge_slot_control/"
    "source_packet_bold_phrase_edge_slot_control.json",
    "c9_frame_overdose_page_control": ROOT
    / "analysis_outputs/source_audit/c9_frame_overdose_page_control/c9_frame_overdose_page_control.json",
    "c9_frame_internal_geometry_gate": ROOT
    / "analysis_outputs/source_audit/c9_frame_internal_geometry_gate/c9_frame_internal_geometry_gate.json",
    "c9_highlight_edge_contact_control": ROOT
    / "analysis_outputs/source_audit/c9_highlight_edge_contact_control/c9_highlight_edge_contact_control.json",
    "c9_bold_highlight_format_density": ROOT
    / "analysis_outputs/source_audit/c9_bold_highlight_format_density/c9_bold_highlight_format_density.json",
    "c9_active_format_witness_reconciliation": ROOT
    / "analysis_outputs/source_audit/c9_active_format_witness_reconciliation/c9_active_format_witness_reconciliation.json",
    "c9_overdose_letter_slot_gate": ROOT
    / "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/c9_overdose_letter_slot_gate.json",
    "c9_grey_black_over_slot_control": ROOT
    / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/c9_grey_black_over_slot_control.json",
    "c9_over_slot_tolerance_gate": ROOT
    / "analysis_outputs/source_audit/c9_over_slot_tolerance_gate/c9_over_slot_tolerance_gate.json",
    "c9_vertical_overdose_slot_gate": ROOT
    / "analysis_outputs/source_audit/c9_vertical_overdose_slot_gate/c9_vertical_overdose_slot_gate.json",
    "c9_header_glyph_slot_gate": ROOT
    / "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json",
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/c9_mirrored_header_glyph_gate.json",
    "page76_active_crop_orientation_guardrail": ROOT / "analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/page76_active_crop_orientation_guardrail.json",
    "page76_active_order_orientation_trap": ROOT / "analysis_outputs/source_audit/page76_active_order_orientation_trap/page76_active_order_orientation_trap.json",
    "active_quartet_box_ocr_gate": ROOT / "analysis_outputs/3d_article_map/active_quartet_box_ocr_gate/active_quartet_box_ocr_gate.json",
    "typeka_comparison_metadata_gate": ROOT / "analysis_outputs/comparison_articles/typeka_comparison_metadata_gate/typeka_comparison_metadata_gate.json",
    "active_obbo_quartet_recurrence": ROOT / "analysis_outputs/comparison_articles/active_obbo_quartet_recurrence/active_obbo_quartet_recurrence.json",
    "bold_docm_source_gate": ROOT / "analysis_outputs/docm_format_sources/bold_docm_source_gate/bold_docm_source_gate.json",
    "bold_highlighted_text_reconstruction": ROOT / "analysis_outputs/docm_format_sources/bold_highlighted_text_reconstruction/bold_highlighted_text_reconstruction.json",
}

DEAD_BRANCH = ROOT / "analysis_outputs/dead_branch_blacklist.md"


def exists(rel: Path) -> str:
    return "present" if rel.exists() else "missing"


def md_contains(path: Path, patterns: list[str]) -> dict[str, bool]:
    if not path.exists():
        return {p: False for p in patterns}
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    return {p: p.lower() in text for p in patterns}


def count_dead_branches() -> int:
    if not DEAD_BRANCH.exists():
        return 0
    return sum(1 for line in DEAD_BRANCH.read_text(encoding="utf-8").splitlines() if line.strip().startswith("- "))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def evidence_summary() -> dict:
    target = load_json(REPORTS["target_convergence"])
    chooser = load_json(REPORTS["next_target_chooser"])
    rky = load_json(REPORTS["rky_rarity"])
    rky_control = load_json(REPORTS["rky_control"])
    content_norm = load_json(REPORTS["content_box_physical_normalization"])
    one_line = load_json(REPORTS["p77_one_line_near_miss"])
    canva_lineup = load_json(REPORTS["canva_lineup_shift_scope"])
    zero_index = load_json(REPORTS["zero_index_rule_scope"])
    source_delta = load_json(REPORTS["source_delta_watch"])
    source_packet = load_json(REPORTS["future_source_validation_packet"])
    scan_lock = load_json(REPORTS["desktop_best_scan_pixel_lock"])
    topology = load_json(REPORTS["issue24_physical_page_topology"])
    p75p76 = load_json(REPORTS["p75_p76_valid_leaf_recheck"])
    p78_source = load_json(REPORTS["p78_source_graphic_instruction_surface"])
    source_reopen = load_json(REPORTS["source_reopen_requirements"])
    source_intake = load_json(REPORTS["source_reopen_candidate_intake"])
    external_unit = load_json(REPORTS["external_clue_unit_order_intake"])
    p80_package_gate = load_json(REPORTS["p80_package_r3_gate_synthesis"])
    p80_numeric_gate = load_json(REPORTS["p80_numeric_active_order_gate"])
    active_capsule_direction_gate = load_json(REPORTS["active_quartet_capsule_direction_gate"])
    active_punctuation_gate = load_json(REPORTS["active_punctuation_enclosure_gate"])
    active_font_edge_gate = load_json(REPORTS["active_font_edge_transition_gate"])
    active_mix_proximity_gate = load_json(REPORTS["active_mix_proximity_gate"])
    active_quartet_pair_symmetry_gate = load_json(REPORTS["active_quartet_pair_symmetry_gate"])
    active_target_envelope_density_gate = load_json(REPORTS["active_target_envelope_density_gate"])
    active_target_center_path_gate = load_json(REPORTS["active_target_center_path_gate"])
    active_target_center_path_bold_gate = load_json(REPORTS["active_target_center_path_bold_gate"])
    active_line_corridor_mirror_index_gate = load_json(REPORTS["active_line_corridor_mirror_index_gate"])
    g5_axis_bold_highlight_rescue_gate = load_json(REPORTS["g5_axis_bold_highlight_rescue_gate"])
    page76_page_center_mirror_guardrail = load_json(REPORTS["page76_page_center_mirror_guardrail"])
    overdose_header_ray_fan_gate = load_json(REPORTS["overdose_header_ray_fan_gate"])
    c9_glyph_center_ray_gate = load_json(REPORTS["c9_glyph_center_ray_gate"])
    c9_target_vertical_chord_gate = load_json(REPORTS["c9_target_vertical_chord_gate"])
    c9_target_horizontal_chord_gate = load_json(REPORTS["c9_target_horizontal_chord_gate"])
    active_frame_center_reflection_gate = load_json(REPORTS["active_frame_center_reflection_gate"])
    active_frame_edge_axis_gate = load_json(REPORTS["active_frame_edge_axis_gate"])
    active_o4_frame_rescue_gate = load_json(REPORTS["active_o4_frame_rescue_gate"])
    o4_frame_rescue_offset_control = load_json(REPORTS["o4_frame_rescue_offset_control"])
    o4_frame_rescue_content_gate = load_json(REPORTS["o4_frame_rescue_content_gate"])
    o4_frame_rescue_signal_stream_gate = load_json(REPORTS["o4_frame_rescue_signal_stream_gate"])
    o4_frame_rescue_yk_filter_control = load_json(REPORTS["o4_frame_rescue_yk_filter_control"])
    o4_frame_yk_unit_order_gate = load_json(REPORTS["o4_frame_yk_unit_order_gate"])
    overdose_header_gate = load_json(REPORTS["overdose_header_registration_gate"])
    overdose_same_slot_gate = load_json(REPORTS["overdose_same_slot_control_gate"])
    typeka_font_gate = load_json(REPORTS["typeka_font_r3_gate_synthesis"])
    fold_mirror_gate = load_json(REPORTS["fold_mirror_r3_gate_synthesis"])
    reflection_line_pitch_stack = load_json(REPORTS["reflection_line_pitch_stack_gate"])
    reflection_shifted_carrier_content = load_json(REPORTS["reflection_shifted_carrier_content_gate"])
    highlight_fold_axis_population = load_json(REPORTS["page76_highlight_fold_axis_population_gate"])
    highlight_cluster_gate = load_json(REPORTS["page76_highlight_cluster_r3_gate_synthesis"])
    comparison_layout_gate = load_json(REPORTS["comparison_overdose_layout_r3_gate_synthesis"])
    overdose_style_uniqueness = load_json(REPORTS["overdose_style_uniqueness"])
    overdose_style_summaries = {
        summary.get("slug"): summary
        for summary in overdose_style_uniqueness.get("summaries", [])
    }
    overdose_style_roles = {
        result.get("slug"): result.get("role")
        for result in overdose_style_uniqueness.get("results", [])
    }
    unlock_matrix = load_json(REPORTS["active_evidence_unlock_matrix"])
    source_arrival = load_json(REPORTS["post_unlock_source_arrival_watch"])
    acquisition_packet = load_json(REPORTS["source_acquisition_target_packet"])
    acquisition_integrity = load_json(REPORTS["source_acquisition_packet_integrity"])
    scoring_rubric = load_json(REPORTS["future_source_scoring_rubric"])
    rubric_dry_run = load_json(REPORTS["future_source_rubric_current_stack_dry_run"])
    target_text_lock = load_json(REPORTS["page76_target_text_authority_lock"])
    target_format_lock = load_json(REPORTS["page76_target_format_authority_lock"])
    markdown_docm_mismatch = load_json(REPORTS["markdown_docm_mismatch_instruction_surface"])
    active_crop_completion = load_json(REPORTS["page76_active_target_crop_completion"])
    packet_crop_sync = load_json(REPORTS["source_packet_crop_authority_sync"])
    packet_yk_sync = load_json(REPORTS["source_packet_yk_frame_benchmark_sync"])
    packet_native_bridge = load_json(REPORTS["source_packet_native_benchmark_bridge"])
    packet_visual_roundtrip = load_json(REPORTS["source_packet_visual_state_roundtrip"])
    packet_alignment_tolerance = load_json(REPORTS["source_packet_alignment_tolerance"])
    packet_geometric_fingerprint = load_json(REPORTS["source_packet_geometric_fingerprint"])
    packet_frame_normalized = load_json(REPORTS["source_packet_frame_normalized_geometry"])
    packet_color_profile = load_json(REPORTS["source_packet_color_profile_manifest"])
    packet_repaired_p78_frame = load_json(REPORTS["source_packet_repaired_p78_frame_residual"])
    packet_repaired_frame_leakage = load_json(REPORTS["source_packet_repaired_frame_expansion_leakage"])
    packet_handoff_integrity = load_json(REPORTS["source_packet_handoff_integrity_matrix"])
    packet_false_positive_guardrail = load_json(REPORTS["source_packet_false_positive_guardrail"])
    packet_r3_bridge = load_json(REPORTS["source_packet_r3_bridge_audit"])
    packet_reopen_trigger = load_json(REPORTS["source_packet_reopen_trigger_matrix"])
    packet_orientation_disambiguator = load_json(REPORTS["source_packet_orientation_disambiguator"])
    packet_orientation_control_quartets = load_json(REPORTS["source_packet_orientation_control_quartets"])
    packet_source_review_gate = load_json(REPORTS["source_packet_source_review_gate"])
    packet_overdose_transform_control = load_json(REPORTS["source_packet_overdose_transform_control"])
    packet_fold_format_intersection = load_json(REPORTS["source_packet_fold_format_intersection_control"])
    packet_terminal_coverage = load_json(REPORTS["source_packet_terminal_coverage_matrix"])
    packet_active_target_authority = load_json(REPORTS["source_packet_active_target_authority_crosscheck"])
    packet_active_format_stream = load_json(REPORTS["source_packet_active_format_stream_control"])
    packet_active_index_slot = load_json(REPORTS["source_packet_active_index_slot_control"])
    packet_center_rotation_word = load_json(REPORTS["source_packet_center_rotation_word_control"])
    packet_color_split_span = load_json(REPORTS["source_packet_color_split_span_control"])
    packet_dominant_overlap = load_json(REPORTS["source_packet_dominant_overlap_slot_control"])
    packet_span_edge_slot = load_json(REPORTS["source_packet_span_edge_slot_control"])
    packet_overlap_width_profile = load_json(REPORTS["source_packet_overlap_width_profile_control"])
    packet_span_neighbor_slot = load_json(REPORTS["source_packet_span_neighbor_slot_control"])
    packet_span_complement_slot = load_json(REPORTS["source_packet_span_complement_slot_control"])
    packet_local_asset_orientation = load_json(REPORTS["source_packet_local_asset_orientation_gate"])
    packet_pdf_render_quality = load_json(REPORTS["source_packet_pdf_render_quality_gate"])
    current_scan_held_to_light = load_json(REPORTS["current_scan_held_to_light_simulator"])
    current_scan_held_to_light_active_balance = load_json(
        REPORTS["current_scan_held_to_light_active_box_balance_gate"]
    )
    current_scan_held_to_light_component_readability = load_json(
        REPORTS["current_scan_held_to_light_component_readability_gate"]
    )
    current_scan_held_to_light_opacity = load_json(
        REPORTS["current_scan_held_to_light_opacity_gate"]
    )
    current_scan_light_table_blend_mode = load_json(
        REPORTS["current_scan_light_table_blend_mode_gate"]
    )
    current_scan_valid_leaf_source_ink_landing = load_json(
        REPORTS["current_scan_valid_leaf_source_ink_landing_gate"]
    )
    current_scan_all_leaf_light_table_parity = load_json(
        REPORTS["current_scan_all_leaf_light_table_parity_gate"]
    )
    current_scan_light_table_density_calibration = load_json(
        REPORTS["current_scan_light_table_density_calibration_gate"]
    )
    current_scan_overdose_density_outlier_provenance = load_json(
        REPORTS["current_scan_overdose_density_outlier_provenance_gate"]
    )
    current_scan_overdose_density_highlight_ablation = load_json(
        REPORTS["current_scan_overdose_density_highlight_ablation_gate"]
    )
    current_scan_active_source_highlight_ablation = load_json(
        REPORTS["current_scan_active_source_highlight_ablation_gate"]
    )
    current_scan_physical_bleedthrough_correlation = load_json(
        REPORTS["current_scan_physical_bleedthrough_correlation_gate"]
    )
    current_scan_active_quartet_fingerprint_specificity = load_json(
        REPORTS["current_scan_active_quartet_fingerprint_specificity_gate"]
    )
    current_scan_target_witness_box_substitution = load_json(
        REPORTS["current_scan_target_witness_box_substitution_gate"]
    )
    current_scan_page76_image_witness_state_stability = load_json(
        REPORTS["current_scan_page76_image_witness_state_stability_gate"]
    )
    current_scan_page76_image_witness_microregistration = load_json(
        REPORTS["current_scan_page76_image_witness_microregistration_gate"]
    )
    current_scan_active_box_overdose_edge_residue = load_json(
        REPORTS["current_scan_active_box_overdose_edge_residue_gate"]
    )
    current_scan_valid_leaf_jitter_source_ink_rescue = load_json(
        REPORTS["current_scan_valid_leaf_jitter_source_ink_rescue_gate"]
    )
    current_scan_page_frame_trim_registration = load_json(
        REPORTS["current_scan_page_frame_trim_registration_gate"]
    )
    current_scan_content_box_registration = load_json(
        REPORTS["current_scan_content_box_registration_gate"]
    )
    current_scan_source_layer_landing = load_json(
        REPORTS["current_scan_source_layer_landing_gate"]
    )
    current_scan_source_layer_miss_distance = load_json(
        REPORTS["current_scan_source_layer_miss_distance_gate"]
    )
    current_scan_b4_broad_contact_provenance = load_json(
        REPORTS["current_scan_b4_broad_contact_provenance_gate"]
    )
    current_pdf_b4_contact_pixel_provenance = load_json(
        REPORTS["current_pdf_b4_contact_pixel_provenance_gate"]
    )
    current_pdf_duplicate_background_feature_artifact = load_json(
        REPORTS["current_pdf_duplicate_background_feature_artifact_gate"]
    )
    current_pdf_page76_carrier_state_stability = load_json(
        REPORTS["current_pdf_page76_carrier_state_stability_gate"]
    )
    current_scan_b4_self_signal = load_json(
        REPORTS["current_scan_b4_self_signal_guardrail"]
    )
    current_scan_light_table_self_signal_partition = load_json(
        REPORTS["current_scan_light_table_self_signal_partition_gate"]
    )
    current_scan_overdose_slot_source_support_trace = load_json(
        REPORTS["current_scan_overdose_slot_source_support_trace"]
    )
    current_pdf_overdose_slot_source_support_trace = load_json(
        REPORTS["current_pdf_overdose_slot_source_support_trace"]
    )
    current_pdf_ose_source_highlight_phrase = load_json(
        REPORTS["current_pdf_ose_source_highlight_phrase_gate"]
    )
    current_pdf_ose_highlight_mirror_geometry = load_json(
        REPORTS["current_pdf_ose_highlight_mirror_geometry_gate"]
    )
    current_pdf_ose_highlight_translation_rescue = load_json(
        REPORTS["current_pdf_ose_highlight_translation_rescue_gate"]
    )
    current_scan_valid_leaf_bleedthrough = load_json(
        REPORTS["current_scan_valid_leaf_bleedthrough_control_grid"]
    )
    current_scan_valid_leaf_local_warp = load_json(
        REPORTS["current_scan_valid_leaf_local_warp_gate"]
    )
    current_scan_valid_leaf_local_warp_source_trace = load_json(
        REPORTS["current_scan_valid_leaf_local_warp_source_trace"]
    )
    current_scan_valid_leaf_edge_contact = load_json(
        REPORTS["current_scan_valid_leaf_edge_contact_control"]
    )
    current_scan_valid_leaf_edge_source_trace = load_json(
        REPORTS["current_scan_valid_leaf_edge_source_trace"]
    )
    current_scan_valid_leaf_interior_source_trace = load_json(
        REPORTS["current_scan_valid_leaf_interior_source_trace"]
    )
    current_scan_valid_leaf_glyph_slot_source_trace = load_json(
        REPORTS["current_scan_valid_leaf_glyph_slot_source_trace"]
    )
    current_scan_valid_leaf_channel_source_trace = load_json(
        REPORTS["current_scan_valid_leaf_channel_source_trace"]
    )
    current_scan_valid_leaf_word_collision_trace = load_json(
        REPORTS["current_scan_valid_leaf_word_collision_trace"]
    )
    current_scan_valid_leaf_line_band_trace = load_json(
        REPORTS["current_scan_valid_leaf_line_band_trace"]
    )
    valid_leaf_strict_term_disambiguation = load_json(
        REPORTS["valid_leaf_strict_term_disambiguation_gate"]
    )
    valid_leaf_target_context_instruction = load_json(
        REPORTS["valid_leaf_target_context_instruction_gate"]
    )
    current_pdf_page_box_pair_geometry = load_json(
        REPORTS["current_pdf_page_box_pair_geometry_gate"]
    )
    current_pdf_leaf_pair_texture_correlation = load_json(
        REPORTS["current_pdf_leaf_pair_texture_correlation_gate"]
    )
    current_pdf_native_image_registration = load_json(
        REPORTS["current_pdf_native_image_registration_gate"]
    )
    current_pdf_native_registration_candidate_trace = load_json(
        REPORTS["current_pdf_native_registration_candidate_source_trace"]
    )
    current_pdf_held_to_light_composite_polarity = load_json(
        REPORTS["current_pdf_held_to_light_composite_polarity_gate"]
    )
    current_pdf_held_to_light_candidate_trace = load_json(
        REPORTS["current_pdf_held_to_light_candidate_source_trace"]
    )
    current_pdf_held_to_light_all_target_phrase = load_json(
        REPORTS["current_pdf_held_to_light_all_target_phrase_gate"]
    )
    current_pdf_held_to_light_color_phrase = load_json(
        REPORTS["current_pdf_held_to_light_color_phrase_gate"]
    )
    current_pdf_held_to_light_component_readability = load_json(
        REPORTS["current_pdf_held_to_light_component_readability_gate"]
    )
    page76_highlight_edge_slot_ruler = load_json(
        REPORTS["page76_highlight_edge_slot_ruler_gate"]
    )
    overdose_glyph_axis_ruler = load_json(
        REPORTS["overdose_glyph_axis_ruler_gate"]
    )
    overdose_glyph_axis_word_center_control = load_json(
        REPORTS["overdose_glyph_axis_word_center_control_gate"]
    )
    current_pdf_leaf_image_identity = load_json(
        REPORTS["current_pdf_leaf_image_identity_gate"]
    )
    current_pdf_render_leaf_simulation = load_json(
        REPORTS["current_pdf_render_leaf_simulation_gate"]
    )
    current_pdf_lowres_render_source_trace = load_json(
        REPORTS["current_pdf_lowres_render_source_trace"]
    )
    current_pdf_ocr_reverse_leaf_source_trace = load_json(
        REPORTS["current_pdf_ocr_reverse_leaf_source_trace"]
    )
    current_scan_overdose_slot_shape_phase_control = load_json(
        REPORTS["current_scan_overdose_slot_shape_phase_control"]
    )
    current_scan_overdose_xslot_phase_control = load_json(
        REPORTS["current_scan_overdose_xslot_phase_control"]
    )
    current_pdf_container_metadata_gate = load_json(
        REPORTS["current_pdf_container_metadata_gate"]
    )
    current_pdf_logical_structure_gate = load_json(
        REPORTS["current_pdf_logical_structure_gate"]
    )
    current_pdf_page_thumbnail_gate = load_json(
        REPORTS["current_pdf_page_thumbnail_gate"]
    )
    current_pdf_thumbnail_active_signal_gate = load_json(
        REPORTS["current_pdf_thumbnail_active_signal_gate"]
    )
    current_pdf_content_stream_operator_gate = load_json(
        REPORTS["current_pdf_content_stream_operator_gate"]
    )
    current_pdf_content_transform_matrix_gate = load_json(
        REPORTS["current_pdf_content_transform_matrix_gate"]
    )
    current_pdf_form_xobject_dictionary_gate = load_json(
        REPORTS["current_pdf_form_xobject_dictionary_gate"]
    )
    current_pdf_form_overlay_placement_gate = load_json(
        REPORTS["current_pdf_form_overlay_placement_gate"]
    )
    current_pdf_trailer_xref_integrity_gate = load_json(
        REPORTS["current_pdf_trailer_xref_integrity_gate"]
    )
    current_pdf_font_cmap_resource_gate = load_json(
        REPORTS["current_pdf_font_cmap_resource_gate"]
    )
    current_pdf_embedded_jpeg_marker_gate = load_json(
        REPORTS["current_pdf_embedded_jpeg_marker_gate"]
    )
    current_pdf_thumbnail_exif_order_gate = load_json(
        REPORTS["current_pdf_thumbnail_exif_order_gate"]
    )
    current_pdf_jpeg_compression_provenance_gate = load_json(
        REPORTS["current_pdf_jpeg_compression_provenance_gate"]
    )
    current_pdf_jpeg_entropy_tail_gate = load_json(
        REPORTS["current_pdf_jpeg_entropy_tail_gate"]
    )
    current_pdf_image_xobject_dictionary_gate = load_json(
        REPORTS["current_pdf_image_xobject_dictionary_gate"]
    )
    current_pdf_page_resource_order_gate = load_json(
        REPORTS["current_pdf_page_resource_order_gate"]
    )
    current_pdf_object_layout = load_json(REPORTS["current_pdf_object_layout_inspection"])
    current_pdf_partial_image_placement = load_json(
        REPORTS["current_pdf_partial_image_placement_gate"]
    )
    current_scan_crop_light_table = load_json(REPORTS["current_scan_crop_light_table_targets"])
    current_scan_overdose_glyph_crop = load_json(
        REPORTS["current_scan_overdose_glyph_crop_projection"]
    )
    current_scan_highlight_boundary_instruction = load_json(
        REPORTS["current_scan_highlight_boundary_instruction_probe"]
    )
    current_scan_boundary_light_table_anomaly = load_json(
        REPORTS["current_scan_boundary_light_table_anomaly_probe"]
    )
    current_scan_boundary_contact_source_trace = load_json(
        REPORTS["current_scan_boundary_contact_source_trace"]
    )
    current_pdf_ocr_target_provenance = load_json(
        REPORTS["current_pdf_ocr_target_provenance_gate"]
    )
    current_pdf_ocr_document_order = load_json(
        REPORTS["current_pdf_ocr_document_order_gate"]
    )
    current_pdf_ocr_overdose_index_offset = load_json(
        REPORTS["current_pdf_ocr_overdose_index_offset_gate"]
    )
    current_pdf_ocr_overdose_neighborhood = load_json(
        REPORTS["current_pdf_ocr_overdose_neighborhood_gate"]
    )
    current_pdf_ocr_page_header_sequence = load_json(
        REPORTS["current_pdf_ocr_page_header_sequence_gate"]
    )
    current_pdf_visual_header_footer_band_sequence = load_json(
        REPORTS["current_pdf_visual_header_footer_band_sequence_gate"]
    )
    current_pdf_repeated_overdose_header_lane = load_json(
        REPORTS["current_pdf_repeated_overdose_header_lane_gate"]
    )
    current_pdf_overdose_header_delta_transfer = load_json(
        REPORTS["current_pdf_overdose_header_delta_transfer_gate"]
    )
    current_pdf_overdose_body_start_vector = load_json(
        REPORTS["current_pdf_overdose_body_start_vector_gate"]
    )
    current_pdf_overdose_body_basis_reflection = load_json(
        REPORTS["current_pdf_overdose_body_basis_reflection_gate"]
    )
    current_pdf_overdose_body_lattice = load_json(
        REPORTS["current_pdf_overdose_body_lattice_gate"]
    )
    current_pdf_overdose_body_offset_transfer = load_json(
        REPORTS["current_pdf_overdose_body_offset_transfer_gate"]
    )
    current_pdf_overdose_body_offset_column = load_json(
        REPORTS["current_pdf_overdose_body_offset_column_gate"]
    )
    current_pdf_overdose_body_fraction_column = load_json(
        REPORTS["current_pdf_overdose_body_fraction_column_gate"]
    )
    current_pdf_ocr_affine_alignment = load_json(
        REPORTS["current_pdf_ocr_affine_alignment_gate"]
    )
    current_pdf_render_alignment_delta = load_json(
        REPORTS["current_pdf_render_alignment_delta_gate"]
    )
    current_pdf_render_resolution_invariance = load_json(
        REPORTS["current_pdf_render_resolution_invariance_gate"]
    )
    current_pdf_render_embedded_identity = load_json(
        REPORTS["current_pdf_active_region_render_embedded_identity_gate"]
    )
    current_scan_jpeg_block_grid = load_json(
        REPORTS["current_scan_jpeg_block_grid_gate"]
    )
    current_scan_halftone_screen = load_json(
        REPORTS["current_scan_halftone_screen_gate"]
    )
    current_scan_rgb_registration = load_json(
        REPORTS["current_scan_rgb_registration_gate"]
    )
    current_scan_luminance_bitplane = load_json(
        REPORTS["current_scan_luminance_bitplane_gate"]
    )
    current_scan_threshold_morphology = load_json(
        REPORTS["current_scan_threshold_morphology_gate"]
    )
    current_scan_highlight_edge_halo = load_json(
        REPORTS["current_scan_highlight_edge_halo_gate"]
    )
    current_scan_slot_boundary_residual = load_json(
        REPORTS["current_scan_slot_boundary_residual_gate"]
    )
    current_scan_active_envelope_transform = load_json(
        REPORTS["current_scan_active_envelope_transform_gate"]
    )
    current_scan_background_seam_residual = load_json(
        REPORTS["current_scan_background_seam_residual_gate"]
    )
    current_scan_paper_texture_duplex = load_json(
        REPORTS["current_scan_paper_texture_duplex_gate"]
    )
    current_scan_paper_texture_shift = load_json(
        REPORTS["current_scan_paper_texture_shift_gate"]
    )
    current_pdf_active_box_coordinate_grid = load_json(
        REPORTS["current_pdf_active_box_coordinate_grid_gate"]
    )
    current_pdf_image_rect_margin_phase = load_json(
        REPORTS["current_pdf_image_rect_margin_phase_gate"]
    )
    local_pdf_filesystem_provenance = load_json(
        REPORTS["local_pdf_filesystem_provenance_gate"]
    )
    local_page_raster_lineage = load_json(
        REPORTS["local_page_raster_lineage_gate"]
    )
    current_pdf_color_management_extgstate = load_json(
        REPORTS["current_pdf_color_management_extgstate_gate"]
    )
    current_pdf_embedded_channel_mask = load_json(
        REPORTS["current_pdf_embedded_channel_mask_gate"]
    )
    current_pdf_text_overlay_render_mode = load_json(
        REPORTS["current_pdf_text_overlay_render_mode_gate"]
    )
    packet_fold_world_overdose_order = load_json(
        REPORTS["source_packet_fold_world_overdose_order_control"]
    )
    packet_bold_phrase_length_slot = load_json(
        REPORTS["source_packet_bold_phrase_length_slot_control"]
    )
    packet_bold_phrase_edge_slot = load_json(
        REPORTS["source_packet_bold_phrase_edge_slot_control"]
    )
    c9_page_control = load_json(REPORTS["c9_frame_overdose_page_control"])
    c9_internal_gate = load_json(REPORTS["c9_frame_internal_geometry_gate"])
    c9_highlight_edge_control = load_json(REPORTS["c9_highlight_edge_contact_control"])
    c9_bold_density = load_json(REPORTS["c9_bold_highlight_format_density"])
    c9_witness = load_json(REPORTS["c9_active_format_witness_reconciliation"])
    c9_overdose_slots = load_json(REPORTS["c9_overdose_letter_slot_gate"])
    c9_grey_black_over_control = load_json(REPORTS["c9_grey_black_over_slot_control"])
    c9_over_tolerance_gate = load_json(REPORTS["c9_over_slot_tolerance_gate"])
    c9_vertical_slots = load_json(REPORTS["c9_vertical_overdose_slot_gate"])
    c9_header_glyph_slots = load_json(REPORTS["c9_header_glyph_slot_gate"])
    c9_mirrored_header_glyph = load_json(REPORTS["c9_mirrored_header_glyph_gate"])
    orientation_guardrail = load_json(REPORTS["page76_active_crop_orientation_guardrail"])
    order_trap = load_json(REPORTS["page76_active_order_orientation_trap"])
    active_box_ocr_gate = load_json(REPORTS["active_quartet_box_ocr_gate"])
    typeka_comparison_metadata = load_json(REPORTS["typeka_comparison_metadata_gate"])
    active_obbo_recurrence = load_json(REPORTS["active_obbo_quartet_recurrence"])
    bold_source_gate = load_json(REPORTS["bold_docm_source_gate"])
    bold_highlighted_text = load_json(REPORTS["bold_highlighted_text_reconstruction"])

    top_targets = []
    for item in target.get("ranking", [])[:3]:
        top_targets.append(
            {
                "target": item.get("target"),
                "label": item.get("label"),
                "score": item.get("score"),
                "layers": item.get("independentLayerCount"),
            }
        )

    return {
        "topTargets": top_targets,
        "nextTargetDecision": {
            "primary": chooser.get("decision", {}).get("primaryManualTarget")
            if isinstance(chooser.get("decision"), dict)
            else None,
            "rawKeys": list(chooser.keys()) if chooser else [],
        },
        "rkyTotals": rky.get("totals", {}),
        "rkyControlRecords": [
            {
                "name": r.get("name"),
                "proceduralHits": r.get("proceduralHits"),
                "page76TargetHits": r.get("page76TargetHits"),
            }
            for r in rky_control.get("records", [])
        ],
        "contentBoxPhysicalNormalization": {
            "p77ToO5BaselineShift": content_norm.get("comparison", {}).get("p77ToO5Baseline", {}).get("touchShiftMagnitude"),
            "p77ToO5NormalizedShift": content_norm.get("comparison", {}).get("p77ToO5Normalized", {}).get("touchShiftMagnitude"),
            "p77DirectHitCountNormalized": content_norm.get("comparison", {}).get("p77DirectHitCountNormalized"),
        },
        "p77OneLineNearMiss": {
            "baselineVerticalGapPx": one_line.get("gapVsLinePitch", {}).get("baselineVerticalGapPx"),
            "medianLinePitchPx": one_line.get("gapVsLinePitch", {}).get("medianLinePitchPx"),
            "p77OneLineUpO5HitCount": one_line.get("hitSummary", {}).get("p77OneLineUpO5HitCount"),
        },
        "canvaLineupShiftScope": {
            "oneLineUpHitCount": canva_lineup.get("oneLineUpHitCount"),
            "p79PillOneLineUpHitCount": canva_lineup.get("p79PillOneLineUpHitCount"),
            "totalHits": canva_lineup.get("totalHits"),
        },
        "zeroIndexRuleScope": {
            "trusted100000Effect": zero_index.get("trusted100000Effect"),
            "unsupported1000000VariantEffect": zero_index.get("unsupported1000000VariantEffect"),
            "streamInstructionHits": zero_index.get("streamInstructionHits"),
        },
        "sourceDeltaWatch": {
            "candidateCount": source_delta.get("candidateCount"),
            "actionableUnknownCount": source_delta.get("actionableUnknownCount"),
            "decision": source_delta.get("decision"),
        },
        "futureSourceValidationPacket": {
            "decision": source_packet.get("decision"),
            "minimumReopenConditions": [
                item.get("condition") for item in source_packet.get("minimumReopenConditions", [])
            ],
        },
        "latestSourceClosures": {
            "desktopBestScanPixelLock": scan_lock.get("decision"),
            "issue24Topology": topology.get("decision"),
            "p75p76ValidLeaf": p75p76.get("decision"),
            "p78SourceGraphicInstructionSurface": p78_source.get("decision"),
        },
        "sourceReopenRequirements": {
            "decision": source_reopen.get("decision"),
            "reopenGates": [row.get("id") for row in source_reopen.get("reopenGates", [])],
            "sheet": source_reopen.get("sheet"),
        },
        "sourceReopenCandidateIntake": {
            "decision": source_intake.get("decision"),
            "sourceDeltaActionableUnknownCount": source_intake.get("sourceDeltaActionableUnknownCount"),
            "verdictCounts": source_intake.get("verdictCounts"),
        },
        "externalClueUnitOrderIntake": {
            "decision": external_unit.get("decision"),
            "rawLikeRecordCount": external_unit.get("rawLikeRecordCount"),
            "rawLikeR3PassCount": external_unit.get("rawLikeR3PassCount"),
            "derivedR3PassCount": external_unit.get("derivedR3PassCount"),
        },
        "p80PackageR3GateSynthesis": {
            "decision": p80_package_gate.get("decision"),
            "explicitExtractionTerms": p80_package_gate.get("explicitExtractionTerms"),
            "gateRows": [
                {
                    "gate": row.get("gate"),
                    "status": row.get("status"),
                }
                for row in p80_package_gate.get("gateRows", [])
            ],
        },
        "p80NumericActiveOrderGate": {
            "decision": p80_numeric_gate.get("decision"),
            "rawNumbersCsv": p80_numeric_gate.get("summary", {}).get("rawNumbersCsv"),
            "canonicalNumbersCsv": p80_numeric_gate.get("summary", {}).get("canonicalNumbersCsv"),
            "activePageLines": p80_numeric_gate.get("summary", {}).get("activePageLines"),
            "activeCorridorIndexes": p80_numeric_gate.get("summary", {}).get("activeCorridorIndexes"),
            "activeLineGaps": p80_numeric_gate.get("summary", {}).get("activeLineGaps"),
            "exactSequenceSuccessCount": p80_numeric_gate.get("summary", {}).get("exactSequenceSuccessCount"),
            "orderedSubsequenceSuccessCount": p80_numeric_gate.get("summary", {}).get("orderedSubsequenceSuccessCount"),
            "onlyStrongDirectNumberLink": p80_numeric_gate.get("summary", {}).get("onlyStrongDirectNumberLink"),
            "selectorUnlocked": p80_numeric_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": p80_numeric_gate.get("sheet"),
        },
        "activeQuartetCapsuleDirectionGate": {
            "decision": active_capsule_direction_gate.get("decision"),
            "stepSigns": active_capsule_direction_gate.get("summary", {}).get("stepSigns"),
            "sameStepSignature": active_capsule_direction_gate.get("summary", {}).get("sameStepSignature"),
            "modeCount": active_capsule_direction_gate.get("summary", {}).get("modeCount"),
            "nonblankStreamCount": active_capsule_direction_gate.get("summary", {}).get("nonblankStreamCount"),
            "instructionHitCount": active_capsule_direction_gate.get("summary", {}).get("instructionHitCount"),
            "instructionHitModeCount": active_capsule_direction_gate.get("summary", {}).get("instructionHitModeCount"),
            "activePageLines": active_capsule_direction_gate.get("summary", {}).get("activePageLines"),
            "activeCorridorIndexes": active_capsule_direction_gate.get("summary", {}).get("activeCorridorIndexes"),
            "selectorUnlocked": active_capsule_direction_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_capsule_direction_gate.get("sheet"),
        },
        "activePunctuationEnclosureGate": {
            "decision": active_punctuation_gate.get("decision"),
            "classStream": active_punctuation_gate.get("summary", {}).get("classStream"),
            "classInitialStream": active_punctuation_gate.get("summary", {}).get("classInitialStream"),
            "selectorPickStream": active_punctuation_gate.get("summary", {}).get("selectorPickStream"),
            "phraseEdgeStream": active_punctuation_gate.get("summary", {}).get("phraseEdgeStream"),
            "activePunctuationCorrectionCount": active_punctuation_gate.get("summary", {}).get("activePunctuationCorrectionCount"),
            "instructionHitCount": active_punctuation_gate.get("summary", {}).get("instructionHitCount"),
            "selectorUnlocked": active_punctuation_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_punctuation_gate.get("sheet"),
        },
        "activeFontEdgeTransitionGate": {
            "decision": active_font_edge_gate.get("decision"),
            "targetStateStream": active_font_edge_gate.get("summary", {}).get("targetStateStream"),
            "edgePatternStream": active_font_edge_gate.get("summary", {}).get("edgePatternStream"),
            "leftExitWordStream": active_font_edge_gate.get("summary", {}).get("leftExitWordStream"),
            "rightEntryWordStream": active_font_edge_gate.get("summary", {}).get("rightEntryWordStream"),
            "mixNeighborCount": active_font_edge_gate.get("summary", {}).get("mixNeighborCount"),
            "activeEdgeAllRegularInsulated": active_font_edge_gate.get("summary", {}).get("activeEdgeAllRegularInsulated"),
            "instructionHitCount": active_font_edge_gate.get("summary", {}).get("instructionHitCount"),
            "selectorUnlocked": active_font_edge_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_font_edge_gate.get("sheet"),
        },
        "activeMixProximityGate": {
            "decision": active_mix_proximity_gate.get("decision"),
            "tripletInitials": active_mix_proximity_gate.get("streams", {}).get("tripletInitials"),
            "nearestMixText": active_mix_proximity_gate.get("streams", {}).get("nearestMixText"),
            "uniqueNearestMixGroupCount": active_mix_proximity_gate.get("summary", {}).get("uniqueNearestMixGroupCount"),
            "oneToOneMixMap": active_mix_proximity_gate.get("summary", {}).get("oneToOneMixMap"),
            "sharedElMikeBandTargets": active_mix_proximity_gate.get("summary", {}).get("sharedElMikeBandTargets"),
            "instructionHitCount": active_mix_proximity_gate.get("summary", {}).get("instructionHitCount"),
            "selectorUnlocked": active_mix_proximity_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_mix_proximity_gate.get("sheet"),
        },
        "activeQuartetPairSymmetryGate": {
            "decision": active_quartet_pair_symmetry_gate.get("decision"),
            "colorPattern": active_quartet_pair_symmetry_gate.get("summary", {}).get("colorPattern"),
            "visualStatePattern": active_quartet_pair_symmetry_gate.get("summary", {}).get("visualStatePattern"),
            "pageLines": active_quartet_pair_symmetry_gate.get("summary", {}).get("pageLines"),
            "corridorIndexes": active_quartet_pair_symmetry_gate.get("summary", {}).get("corridorIndexes"),
            "primaryHorizontalMaxErrorPx": active_quartet_pair_symmetry_gate.get("summary", {}).get("primaryHorizontalMaxErrorPx"),
            "primaryVerticalMaxErrorPx": active_quartet_pair_symmetry_gate.get("summary", {}).get("primaryVerticalMaxErrorPx"),
            "primaryPointMidpointSpreadPx": active_quartet_pair_symmetry_gate.get("summary", {}).get("primaryPointMidpointSpreadPx"),
            "bestFrameRelationName": active_quartet_pair_symmetry_gate.get("summary", {}).get("bestFrameRelationName"),
            "bestFrameRelationDistancePx": active_quartet_pair_symmetry_gate.get("summary", {}).get("bestFrameRelationDistancePx"),
            "selectorUnlocked": active_quartet_pair_symmetry_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_quartet_pair_symmetry_gate.get("sheet"),
        },
        "activeTargetEnvelopeDensityGate": {
            "decision": active_target_envelope_density_gate.get("decision", {}).get(
                "activeTargetEnvelopeDensityGate"
            ),
            "activeEnvelopeBox": active_target_envelope_density_gate.get("geometry", {}).get(
                "activeEnvelopeBox"
            ),
            "activeEnvelopeWordCount": active_target_envelope_density_gate.get("summary", {}).get(
                "activeEnvelopeWordCount"
            ),
            "activeEnvelopeNonTargetWordCount": active_target_envelope_density_gate.get(
                "summary", {}
            ).get("activeEnvelopeNonTargetWordCount"),
            "activeTargetCoverage": active_target_envelope_density_gate.get("summary", {}).get(
                "activeTargetCoverage"
            ),
            "activeStrictInstructionHitCount": active_target_envelope_density_gate.get(
                "summary", {}
            ).get("activeStrictInstructionHitCount"),
            "controlComparableWordCount": active_target_envelope_density_gate.get(
                "summary", {}
            ).get("controlComparableWordCount"),
            "controlStrictInstructionHitCount": active_target_envelope_density_gate.get(
                "summary", {}
            ).get("controlStrictInstructionHitCount"),
            "selectorUnlocked": active_target_envelope_density_gate.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": active_target_envelope_density_gate.get("sheet"),
        },
        "activeTargetCenterPathGate": {
            "decision": active_target_center_path_gate.get("decision", {}).get(
                "activeTargetCenterPathGate"
            ),
            "primaryOrder": active_target_center_path_gate.get("summary", {}).get(
                "primaryOrder"
            ),
            "primaryVisualStateOrder": active_target_center_path_gate.get("summary", {}).get(
                "primaryVisualStateOrder"
            ),
            "primaryWordCount": active_target_center_path_gate.get("summary", {}).get(
                "primaryWordCount"
            ),
            "primaryNonTargetWordCount": active_target_center_path_gate.get("summary", {}).get(
                "primaryNonTargetWordCount"
            ),
            "primaryStrictInstructionHitCount": active_target_center_path_gate.get(
                "summary", {}
            ).get("primaryStrictInstructionHitCount"),
            "variantStrictInstructionHitCount": active_target_center_path_gate.get(
                "summary", {}
            ).get("variantStrictInstructionHitCount"),
            "controlComparableWordCount": active_target_center_path_gate.get("summary", {}).get(
                "controlComparableWordCount"
            ),
            "controlStrictInstructionHitCount": active_target_center_path_gate.get(
                "summary", {}
            ).get("controlStrictInstructionHitCount"),
            "selectorUnlocked": active_target_center_path_gate.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": active_target_center_path_gate.get("sheet"),
        },
        "activeTargetCenterPathBoldGate": {
            "decision": active_target_center_path_bold_gate.get("decision", {}).get(
                "activeTargetCenterPathBoldGate"
            ),
            "primaryOrder": active_target_center_path_bold_gate.get("summary", {}).get(
                "primaryOrder"
            ),
            "primaryRailWordCount": active_target_center_path_bold_gate.get("summary", {}).get(
                "primaryRailWordCount"
            ),
            "primaryBoldRailWordCount": active_target_center_path_bold_gate.get(
                "summary", {}
            ).get("primaryBoldRailWordCount"),
            "primaryActiveOverlapBoldRailWordCount": active_target_center_path_bold_gate.get(
                "summary", {}
            ).get("primaryActiveOverlapBoldRailWordCount"),
            "primaryNonActiveBoldRailWordCount": active_target_center_path_bold_gate.get(
                "summary", {}
            ).get("primaryNonActiveBoldRailWordCount"),
            "primaryDirectTargetBoldUnitCount": active_target_center_path_bold_gate.get(
                "summary", {}
            ).get("primaryDirectTargetBoldUnitCount"),
            "primaryNonActiveRailBoldText": active_target_center_path_bold_gate.get(
                "summary", {}
            ).get("primaryNonActiveRailBoldText"),
            "primaryStrictInstructionHitCount": active_target_center_path_bold_gate.get(
                "summary", {}
            ).get("primaryStrictInstructionHitCount"),
            "primaryNonActiveStrictInstructionHitCount": active_target_center_path_bold_gate.get(
                "summary", {}
            ).get("primaryNonActiveStrictInstructionHitCount"),
            "controlComparableNonActiveBoldCount": active_target_center_path_bold_gate.get(
                "summary", {}
            ).get("controlComparableNonActiveBoldCount"),
            "controlStrictInstructionHitCount": active_target_center_path_bold_gate.get(
                "summary", {}
            ).get("controlStrictInstructionHitCount"),
            "selectorUnlocked": active_target_center_path_bold_gate.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": active_target_center_path_bold_gate.get("sheet"),
        },
        "activeLineCorridorMirrorIndexGate": {
            "decision": active_line_corridor_mirror_index_gate.get("decision", {}).get(
                "activeLineCorridorMirrorIndexGate"
            ),
            "pageLineAxisCount": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "pageLineAxisCount"
            ),
            "corridorAxisCount": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "corridorAxisCount"
            ),
            "pageLineAllFourAxisCount": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "pageLineAllFourAxisCount"
            ),
            "corridorAllFourAxisCount": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "corridorAllFourAxisCount"
            ),
            "bestPageLineAxis": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "bestPageLineAxis"
            ),
            "bestPageLineActiveHitCount": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "bestPageLineActiveHitCount"
            ),
            "bestCorridorAxis": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "bestCorridorAxis"
            ),
            "bestCorridorActiveHitCount": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "bestCorridorActiveHitCount"
            ),
            "strictInstructionAxisHits": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "strictInstructionAxisHits"
            ),
            "selectorUnlocked": active_line_corridor_mirror_index_gate.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": active_line_corridor_mirror_index_gate.get("sheet"),
        },
        "g5AxisBoldHighlightRescueGate": {
            "decision": g5_axis_bold_highlight_rescue_gate.get("decision", {}).get(
                "g5AxisBoldHighlightRescueGate"
            ),
            "axisPageLine": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get("axisPageLine"),
            "axisCorridorIndex": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "axisCorridorIndex"
            ),
            "activeHitCount": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "activeHitCount"
            ),
            "activeMissCount": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "activeMissCount"
            ),
            "nonActiveSignalHitCount": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "nonActiveSignalHitCount"
            ),
            "reflectedStyleStream": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "reflectedStyleStream"
            ),
            "reflectedActiveTargetStream": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "reflectedActiveTargetStream"
            ),
            "boldStreamLength": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "boldStreamLength"
            ),
            "partialBoldStream": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "partialBoldStream"
            ),
            "strictInstructionHitCount": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "strictInstructionHitCount"
            ),
            "selectorUnlocked": g5_axis_bold_highlight_rescue_gate.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": g5_axis_bold_highlight_rescue_gate.get("sheet"),
        },
        "page76PageCenterMirrorGuardrail": {
            "decision": page76_page_center_mirror_guardrail.get("decision", {}).get(
                "pageCenterMirrorAsSelector"
            ),
            "scenarioCount": page76_page_center_mirror_guardrail.get("summary", {}).get(
                "scenarioCount"
            ),
            "testedModes": page76_page_center_mirror_guardrail.get("summary", {}).get(
                "testedModes"
            ),
            "allFourActiveRehitScenarioCount": page76_page_center_mirror_guardrail.get(
                "summary", {}
            ).get("allFourActiveRehitScenarioCount"),
            "totalHighlightHitCount": page76_page_center_mirror_guardrail.get(
                "summary", {}
            ).get("totalHighlightHitCount"),
            "strictInstructionHitCount": page76_page_center_mirror_guardrail.get(
                "summary", {}
            ).get("strictInstructionHitCount"),
            "selectorUnlocked": page76_page_center_mirror_guardrail.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": page76_page_center_mirror_guardrail.get("sheet"),
        },
        "overdoseHeaderRayFanGate": {
            "decision": overdose_header_ray_fan_gate.get("decision", {}).get(
                "overdoseHeaderRayFanAsSelector"
            ),
            "activeRayCount": overdose_header_ray_fan_gate.get("summary", {}).get("activeRayCount"),
            "controlRayCount": overdose_header_ray_fan_gate.get("summary", {}).get("controlRayCount"),
            "activeStrictInstructionHitCount": overdose_header_ray_fan_gate.get(
                "summary", {}
            ).get("activeStrictInstructionHitCount"),
            "controlStrictInstructionHitCount": overdose_header_ray_fan_gate.get(
                "summary", {}
            ).get("controlStrictInstructionHitCount"),
            "activeAllQuartetRayCount": overdose_header_ray_fan_gate.get("summary", {}).get(
                "activeAllQuartetRayCount"
            ),
            "activeRayHighlightHitCounts": overdose_header_ray_fan_gate.get("summary", {}).get(
                "activeRayHighlightHitCounts"
            ),
            "controlRayHighlightHitCounts": overdose_header_ray_fan_gate.get("summary", {}).get(
                "controlRayHighlightHitCounts"
            ),
            "selectorUnlocked": overdose_header_ray_fan_gate.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": overdose_header_ray_fan_gate.get("sheet"),
        },
        "c9GlyphCenterRayGate": {
            "decision": c9_glyph_center_ray_gate.get("decision", {}).get(
                "c9GlyphCenterRayAsSelector"
            ),
            "activeRayCount": c9_glyph_center_ray_gate.get("summary", {}).get(
                "activeRayCount"
            ),
            "controlRayCount": c9_glyph_center_ray_gate.get("summary", {}).get(
                "controlRayCount"
            ),
            "activeAssignedSlotStream": c9_glyph_center_ray_gate.get("summary", {}).get(
                "activeAssignedSlotStream"
            ),
            "controlAssignedSlotStream": c9_glyph_center_ray_gate.get("summary", {}).get(
                "controlAssignedSlotStream"
            ),
            "activeStrictInstructionHitCount": c9_glyph_center_ray_gate.get(
                "summary", {}
            ).get("activeStrictInstructionHitCount"),
            "controlStrictInstructionHitCount": c9_glyph_center_ray_gate.get(
                "summary", {}
            ).get("controlStrictInstructionHitCount"),
            "activeAllQuartetRayCount": c9_glyph_center_ray_gate.get("summary", {}).get(
                "activeAllQuartetRayCount"
            ),
            "activeRayActiveTargetHitCounts": c9_glyph_center_ray_gate.get(
                "summary", {}
            ).get("activeRayActiveTargetHitCounts"),
            "controlRayActiveTargetHitCounts": c9_glyph_center_ray_gate.get(
                "summary", {}
            ).get("controlRayActiveTargetHitCounts"),
            "activeRayHighlightHitCounts": c9_glyph_center_ray_gate.get("summary", {}).get(
                "activeRayHighlightHitCounts"
            ),
            "controlRayHighlightHitCounts": c9_glyph_center_ray_gate.get("summary", {}).get(
                "controlRayHighlightHitCounts"
            ),
            "selectorUnlocked": c9_glyph_center_ray_gate.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": c9_glyph_center_ray_gate.get("sheet"),
        },
        "c9TargetVerticalChordGate": {
            "decision": c9_target_vertical_chord_gate.get("decision", {}).get(
                "c9TargetVerticalChordAsSelector"
            ),
            "activeChordCount": c9_target_vertical_chord_gate.get("summary", {}).get(
                "activeChordCount"
            ),
            "controlChordCount": c9_target_vertical_chord_gate.get("summary", {}).get(
                "controlChordCount"
            ),
            "activeSlotStream": c9_target_vertical_chord_gate.get("summary", {}).get(
                "activeSlotStream"
            ),
            "controlSlotStream": c9_target_vertical_chord_gate.get("summary", {}).get(
                "controlSlotStream"
            ),
            "activeStrictInstructionHitCount": c9_target_vertical_chord_gate.get(
                "summary", {}
            ).get("activeStrictInstructionHitCount"),
            "controlStrictInstructionHitCount": c9_target_vertical_chord_gate.get(
                "summary", {}
            ).get("controlStrictInstructionHitCount"),
            "activeAllQuartetChordCount": c9_target_vertical_chord_gate.get(
                "summary", {}
            ).get("activeAllQuartetChordCount"),
            "activeChordActiveTargetHitCounts": c9_target_vertical_chord_gate.get(
                "summary", {}
            ).get("activeChordActiveTargetHitCounts"),
            "controlChordActiveTargetHitCounts": c9_target_vertical_chord_gate.get(
                "summary", {}
            ).get("controlChordActiveTargetHitCounts"),
            "activeChordHighlightHitCounts": c9_target_vertical_chord_gate.get(
                "summary", {}
            ).get("activeChordHighlightHitCounts"),
            "controlChordHighlightHitCounts": c9_target_vertical_chord_gate.get(
                "summary", {}
            ).get("controlChordHighlightHitCounts"),
            "selectorUnlocked": c9_target_vertical_chord_gate.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": c9_target_vertical_chord_gate.get("sheet"),
        },
        "c9TargetHorizontalChordGate": {
            "decision": c9_target_horizontal_chord_gate.get("decision", {}).get(
                "c9TargetHorizontalChordAsSelector"
            ),
            "activeChordCount": c9_target_horizontal_chord_gate.get("summary", {}).get(
                "activeChordCount"
            ),
            "controlChordCount": c9_target_horizontal_chord_gate.get("summary", {}).get(
                "controlChordCount"
            ),
            "activeStrictInstructionHitCount": c9_target_horizontal_chord_gate.get(
                "summary", {}
            ).get("activeStrictInstructionHitCount"),
            "controlStrictInstructionHitCount": c9_target_horizontal_chord_gate.get(
                "summary", {}
            ).get("controlStrictInstructionHitCount"),
            "activeAllQuartetChordCount": c9_target_horizontal_chord_gate.get(
                "summary", {}
            ).get("activeAllQuartetChordCount"),
            "activeChordActiveTargetHitCounts": c9_target_horizontal_chord_gate.get(
                "summary", {}
            ).get("activeChordActiveTargetHitCounts"),
            "controlChordActiveTargetHitCounts": c9_target_horizontal_chord_gate.get(
                "summary", {}
            ).get("controlChordActiveTargetHitCounts"),
            "activeChordHighlightHitCounts": c9_target_horizontal_chord_gate.get(
                "summary", {}
            ).get("activeChordHighlightHitCounts"),
            "controlChordHighlightHitCounts": c9_target_horizontal_chord_gate.get(
                "summary", {}
            ).get("controlChordHighlightHitCounts"),
            "activeWordHitCounts": c9_target_horizontal_chord_gate.get("summary", {}).get(
                "activeWordHitCounts"
            ),
            "controlWordHitCounts": c9_target_horizontal_chord_gate.get("summary", {}).get(
                "controlWordHitCounts"
            ),
            "selectorUnlocked": c9_target_horizontal_chord_gate.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": c9_target_horizontal_chord_gate.get("sheet"),
        },
        "activeFrameCenterReflectionGate": {
            "decision": active_frame_center_reflection_gate.get("decision"),
            "sameLayoutFrameCenter": active_frame_center_reflection_gate.get("frames", {}).get("frameCenters", {}).get("sameLayout"),
            "currentMirrorFrameCenter": active_frame_center_reflection_gate.get("frames", {}).get("frameCenters", {}).get("currentMirror"),
            "scenarioCount": active_frame_center_reflection_gate.get("summary", {}).get("scenarioCount"),
            "projectionCount": active_frame_center_reflection_gate.get("summary", {}).get("projectionCount"),
            "inBoundsProjectionCount": active_frame_center_reflection_gate.get("summary", {}).get("inBoundsProjectionCount"),
            "totalHardInstructionHitCount": active_frame_center_reflection_gate.get("summary", {}).get("totalHardInstructionHitCount"),
            "totalActiveTargetRehitCount": active_frame_center_reflection_gate.get("summary", {}).get("totalActiveTargetRehitCount"),
            "totalStrongActiveTargetRehitCount": active_frame_center_reflection_gate.get("summary", {}).get("totalStrongActiveTargetRehitCount"),
            "maxActiveTargetRehitOverlap": active_frame_center_reflection_gate.get("summary", {}).get("maxActiveTargetRehitOverlap"),
            "selectorUnlocked": active_frame_center_reflection_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_frame_center_reflection_gate.get("sheet"),
        },
        "activeFrameEdgeAxisGate": {
            "decision": active_frame_edge_axis_gate.get("decision"),
            "sameLayoutFrame": active_frame_edge_axis_gate.get("frames", {}).get("sameLayoutFrame"),
            "currentMirrorFrame": active_frame_edge_axis_gate.get("frames", {}).get("currentMirrorFrame"),
            "lineCount": active_frame_edge_axis_gate.get("summary", {}).get("lineCount"),
            "totalActiveTargetHitCount": active_frame_edge_axis_gate.get("summary", {}).get("totalActiveTargetHitCount"),
            "totalStrongActiveTargetHitCount": active_frame_edge_axis_gate.get("summary", {}).get("totalStrongActiveTargetHitCount"),
            "strongActiveTargetLines": active_frame_edge_axis_gate.get("summary", {}).get("strongActiveTargetLines"),
            "lineHitStream": active_frame_edge_axis_gate.get("summary", {}).get("lineHitStream"),
            "totalHardInstructionHitCount": active_frame_edge_axis_gate.get("summary", {}).get("totalHardInstructionHitCount"),
            "selectorUnlocked": active_frame_edge_axis_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_frame_edge_axis_gate.get("sheet"),
        },
        "activeO4FrameRescueGate": {
            "decision": active_o4_frame_rescue_gate.get("decision"),
            "linePitchPx": active_o4_frame_rescue_gate.get("linePitchPx"),
            "sameLayoutFrame": active_o4_frame_rescue_gate.get("frames", {}).get("sameLayout"),
            "currentMirrorFrame": active_o4_frame_rescue_gate.get("frames", {}).get("currentMirror"),
            "dualEnvelope": active_o4_frame_rescue_gate.get("frames", {}).get("dualEnvelope"),
            "dualEnvelopeFullTopExpansionPx": active_o4_frame_rescue_gate.get("summary", {}).get("dualEnvelopeFullTopExpansionPx"),
            "dualEnvelopeFullTopInLinePitches": active_o4_frame_rescue_gate.get("summary", {}).get("dualEnvelopeFullTopInLinePitches"),
            "dualEnvelopeTouchTopExpansionPx": active_o4_frame_rescue_gate.get("summary", {}).get("dualEnvelopeTouchTopExpansionPx"),
            "topMinus3LinePitchHitIds": active_o4_frame_rescue_gate.get("summary", {}).get("topMinus3LinePitchHitIds"),
            "topMinus3LinePitchFullHitIds": active_o4_frame_rescue_gate.get("summary", {}).get("topMinus3LinePitchFullHitIds"),
            "selectorUnlocked": active_o4_frame_rescue_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_o4_frame_rescue_gate.get("sheet"),
        },
        "o4FrameRescueOffsetControl": {
            "decision": o4_frame_rescue_offset_control.get("decision"),
            "linePitchPx": o4_frame_rescue_offset_control.get("linePitchPx"),
            "dualEnvelope": o4_frame_rescue_offset_control.get("dualEnvelope"),
            "topOnlyOffsetCount": o4_frame_rescue_offset_control.get("summary", {}).get("topOnlyOffsetCount"),
            "gridOffsetCount": o4_frame_rescue_offset_control.get("summary", {}).get("gridOffsetCount"),
            "minimumTopOnlyAllFourPartial": o4_frame_rescue_offset_control.get("summary", {}).get("minimumTopOnlyAllFourPartial"),
            "topOnlyAllFourPartialOffsets": o4_frame_rescue_offset_control.get("summary", {}).get("topOnlyAllFourPartialOffsets"),
            "topOnlyAllFourFullOffsets": o4_frame_rescue_offset_control.get("summary", {}).get("topOnlyAllFourFullOffsets"),
            "minimumFullCoverageTopLines": o4_frame_rescue_offset_control.get("summary", {}).get("minimumFullCoverageTopLines"),
            "minimumFullCoverageBottomLines": o4_frame_rescue_offset_control.get("summary", {}).get("minimumFullCoverageBottomLines"),
            "minimumFullCoverageTotalLineExpansion": o4_frame_rescue_offset_control.get("summary", {}).get("minimumFullCoverageTotalLineExpansion"),
            "selectorUnlocked": o4_frame_rescue_offset_control.get("summary", {}).get("selectorUnlocked"),
            "sheet": o4_frame_rescue_offset_control.get("sheet"),
        },
        "o4FrameRescueContentGate": {
            "decision": o4_frame_rescue_content_gate.get("decision"),
            "fullCoverageFrame": o4_frame_rescue_content_gate.get("fullCoverageFrame"),
            "includedLineCount": o4_frame_rescue_content_gate.get("summary", {}).get("includedLineCount"),
            "includedLineRange": o4_frame_rescue_content_gate.get("summary", {}).get("includedLineRange"),
            "includedCorridorRange": o4_frame_rescue_content_gate.get("summary", {}).get("includedCorridorRange"),
            "includedWordCount": o4_frame_rescue_content_gate.get("summary", {}).get("includedWordCount"),
            "activeTargetWordCount": o4_frame_rescue_content_gate.get("summary", {}).get("activeTargetWordCount"),
            "nonTargetWordCount": o4_frame_rescue_content_gate.get("summary", {}).get("nonTargetWordCount"),
            "nonActiveHighlightEntryCount": o4_frame_rescue_content_gate.get("summary", {}).get("nonActiveHighlightEntryCount"),
            "nonActiveBoldContextLineCount": o4_frame_rescue_content_gate.get("summary", {}).get("nonActiveBoldContextLineCount"),
            "hardInstructionHitCount": o4_frame_rescue_content_gate.get("summary", {}).get("hardInstructionHitCount"),
            "selectorUnlocked": o4_frame_rescue_content_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": o4_frame_rescue_content_gate.get("sheet"),
        },
        "o4FrameRescueSignalStreamGate": {
            "decision": o4_frame_rescue_signal_stream_gate.get("decision"),
            "fullCoverageFrame": o4_frame_rescue_signal_stream_gate.get("fullCoverageFrame"),
            "frameSignalGroupCount": o4_frame_rescue_signal_stream_gate.get("summary", {}).get("frameSignalGroupCount"),
            "activeSignalGroupCount": o4_frame_rescue_signal_stream_gate.get("summary", {}).get("activeSignalGroupCount"),
            "nonActiveSignalGroupCount": o4_frame_rescue_signal_stream_gate.get("summary", {}).get("nonActiveSignalGroupCount"),
            "frameLayerCodes": o4_frame_rescue_signal_stream_gate.get("summary", {}).get("frameLayerCodes"),
            "activeLayerCodes": o4_frame_rescue_signal_stream_gate.get("summary", {}).get("activeLayerCodes"),
            "nonActiveLayerCodes": o4_frame_rescue_signal_stream_gate.get("summary", {}).get("nonActiveLayerCodes"),
            "nonActiveSignalTexts": o4_frame_rescue_signal_stream_gate.get("summary", {}).get("nonActiveSignalTexts"),
            "hardInstructionHitCount": o4_frame_rescue_signal_stream_gate.get("summary", {}).get("hardInstructionHitCount"),
            "selectorUnlocked": o4_frame_rescue_signal_stream_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": o4_frame_rescue_signal_stream_gate.get("sheet"),
        },
        "o4FrameRescueYkFilterControl": {
            "decision": o4_frame_rescue_yk_filter_control.get("decision"),
            "fullPageSignalLayerCodes": o4_frame_rescue_yk_filter_control.get("summary", {}).get("fullPageSignalLayerCodes"),
            "fullPageYkGroupCount": o4_frame_rescue_yk_filter_control.get("summary", {}).get("fullPageYkGroupCount"),
            "fullPageYkLayerCodes": o4_frame_rescue_yk_filter_control.get("summary", {}).get("fullPageYkLayerCodes"),
            "fullPageYkNonActiveGroupCount": o4_frame_rescue_yk_filter_control.get("summary", {}).get("fullPageYkNonActiveGroupCount"),
            "frameSignalLayerCodes": o4_frame_rescue_yk_filter_control.get("summary", {}).get("frameSignalLayerCodes"),
            "frameYkLayerCodes": o4_frame_rescue_yk_filter_control.get("summary", {}).get("frameYkLayerCodes"),
            "frameYkActiveGroupCount": o4_frame_rescue_yk_filter_control.get("summary", {}).get("frameYkActiveGroupCount"),
            "frameYkNonActiveGroupCount": o4_frame_rescue_yk_filter_control.get("summary", {}).get("frameYkNonActiveGroupCount"),
            "frameYkAllActiveTargetsCovered": o4_frame_rescue_yk_filter_control.get("summary", {}).get("frameYkAllActiveTargetsCovered"),
            "hardInstructionHitCount": o4_frame_rescue_yk_filter_control.get("summary", {}).get("hardInstructionHitCount"),
            "selectorUnlocked": o4_frame_rescue_yk_filter_control.get("summary", {}).get("selectorUnlocked"),
            "sheet": o4_frame_rescue_yk_filter_control.get("sheet"),
        },
        "o4FrameYkUnitOrderGate": {
            "decision": o4_frame_yk_unit_order_gate.get("decision"),
            "isolatedTargetCount": o4_frame_yk_unit_order_gate.get("summary", {}).get("isolatedTargetCount"),
            "groupOrderTargetIds": o4_frame_yk_unit_order_gate.get("summary", {}).get("groupOrderTargetIds"),
            "leftToRightTargetIds": o4_frame_yk_unit_order_gate.get("summary", {}).get("leftToRightTargetIds"),
            "groupOrderLayerCodes": o4_frame_yk_unit_order_gate.get("summary", {}).get("groupOrderLayerCodes"),
            "pageLines": o4_frame_yk_unit_order_gate.get("summary", {}).get("pageLines"),
            "corridorIndexes": o4_frame_yk_unit_order_gate.get("summary", {}).get("corridorIndexes"),
            "groupIndexGaps": o4_frame_yk_unit_order_gate.get("summary", {}).get("groupIndexGaps"),
            "pageLineGaps": o4_frame_yk_unit_order_gate.get("summary", {}).get("pageLineGaps"),
            "corridorGaps": o4_frame_yk_unit_order_gate.get("summary", {}).get("corridorGaps"),
            "boundedStreamCount": o4_frame_yk_unit_order_gate.get("summary", {}).get("boundedStreamCount"),
            "totalHardInstructionHitCount": o4_frame_yk_unit_order_gate.get("summary", {}).get("totalHardInstructionHitCount"),
            "sourceBackedUnitOrder": o4_frame_yk_unit_order_gate.get("summary", {}).get("sourceBackedUnitOrder"),
            "selectorUnlocked": o4_frame_yk_unit_order_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": o4_frame_yk_unit_order_gate.get("sheet"),
        },
        "overdoseHeaderRegistrationGate": {
            "decision": overdose_header_gate.get("decision"),
            "headerRegistration": overdose_header_gate.get("headerRegistration"),
            "scenarioSummaries": [
                {
                    "id": row.get("id"),
                    "activeFullHitCount": row.get("summary", {}).get("activeFullHitCount"),
                    "activePartialHitCount": row.get("summary", {}).get("activePartialHitCount"),
                    "activeHitIds": row.get("summary", {}).get("activeHitIds"),
                    "strictUnitTermHitCount": row.get("summary", {}).get("strictUnitTermHitCount"),
                }
                for row in overdose_header_gate.get("scenarios", [])
            ],
            "selectorUnlocked": overdose_header_gate.get("decision", {}).get("selectorUnlocked"),
            "sheet": overdose_header_gate.get("sheet"),
        },
        "overdoseSameSlotControlGate": {
            "decision": overdose_same_slot_gate.get("decision"),
            "sameSlotFrame": overdose_same_slot_gate.get("sameSlotFrame"),
            "p76HorizontalMirrorFrame": overdose_same_slot_gate.get("p76HorizontalMirrorFrame"),
            "p76SameSlotActiveTargetHitCount": overdose_same_slot_gate.get("summary", {}).get("p76SameSlotActiveTargetHitCount"),
            "p76SameSlotActiveTargets": overdose_same_slot_gate.get("summary", {}).get("p76SameSlotActiveTargets"),
            "p76SameSlotHardInstructionHitCount": overdose_same_slot_gate.get("summary", {}).get("p76SameSlotHardInstructionHitCount"),
            "p76MirrorActiveTargetHitCount": overdose_same_slot_gate.get("summary", {}).get("p76MirrorActiveTargetHitCount"),
            "p76MirrorActiveTargets": overdose_same_slot_gate.get("summary", {}).get("p76MirrorActiveTargets"),
            "p76MirrorHardInstructionHitCount": overdose_same_slot_gate.get("summary", {}).get("p76MirrorHardInstructionHitCount"),
            "selectorUnlocked": overdose_same_slot_gate.get("decision", {}).get("selectorUnlocked"),
            "sheet": overdose_same_slot_gate.get("sheet"),
        },
        "typekaFontR3GateSynthesis": {
            "decision": typeka_font_gate.get("decision"),
            "strongInstructionRecordCount": typeka_font_gate.get("strongInstructionRecordCount"),
            "proceduralNoUnitRecordCount": typeka_font_gate.get("proceduralNoUnitRecordCount"),
            "unitNoActionRecordCount": typeka_font_gate.get("unitNoActionRecordCount"),
            "gateRows": [
                {
                    "gate": row.get("gate"),
                    "status": row.get("status"),
                }
                for row in typeka_font_gate.get("gateRows", [])
            ],
        },
        "foldMirrorR3GateSynthesis": {
            "decision": fold_mirror_gate.get("decision"),
            "page76MediumStrongEdges": fold_mirror_gate.get("reflectedGraphSummary", {}).get("page76MediumPlusEdges"),
            "twoHandWeakTermHitCount": fold_mirror_gate.get("twoHandWeakTermHitCount"),
            "twoHandUnitOrderHitCount": fold_mirror_gate.get("twoHandUnitOrderHitCount"),
            "reflectionBoxActiveTargetOverlapCount": fold_mirror_gate.get("reflectionBox", {}).get("activeTargetOverlapCount"),
            "anchorInsideTargetCount": fold_mirror_gate.get("anchorPoint", {}).get("insideTargetCount"),
            "anchorNearTargetWithin50Count": fold_mirror_gate.get("anchorPoint", {}).get("nearTargetWithin50Count"),
            "gateRows": [
                {
                    "gate": row.get("gate"),
                    "status": row.get("status"),
                }
                for row in fold_mirror_gate.get("gateRows", [])
            ],
        },
        "reflectionLinePitchStackGate": {
            "decision": reflection_line_pitch_stack.get("decision", {}).get("reflectionLinePitchStackGate"),
            "linePitchPx": reflection_line_pitch_stack.get("summary", {}).get("linePitchPx"),
            "reflectionCount": reflection_line_pitch_stack.get("summary", {}).get("reflectionCount"),
            "allFourActiveCarrierCount": reflection_line_pitch_stack.get("summary", {}).get("allFourActiveCarrierCount"),
            "allFourActiveCarrierIds": reflection_line_pitch_stack.get("summary", {}).get("allFourActiveCarrierIds"),
            "singleShiftAllFourCount": reflection_line_pitch_stack.get("summary", {}).get("singleShiftAllFourCount"),
            "strictInstructionHitCount": reflection_line_pitch_stack.get("summary", {}).get("strictInstructionHitCount"),
            "selectorUnlocked": reflection_line_pitch_stack.get("summary", {}).get("selectorUnlocked"),
            "sheet": reflection_line_pitch_stack.get("sheet"),
        },
        "reflectionShiftedCarrierContentGate": {
            "decision": reflection_shifted_carrier_content.get("decision", {}).get(
                "reflectionShiftedCarrierContentGate"
            ),
            "carrierCount": reflection_shifted_carrier_content.get("summary", {}).get("carrierCount"),
            "activeSliceCount": reflection_shifted_carrier_content.get("summary", {}).get(
                "activeSliceCount"
            ),
            "activeLineGapPattern": reflection_shifted_carrier_content.get("summary", {}).get(
                "activeLineGapPattern"
            ),
            "commonShiftGapPatterns": reflection_shifted_carrier_content.get("summary", {}).get(
                "commonShiftGapPatterns"
            ),
            "uniqueInferredBaseLines": reflection_shifted_carrier_content.get("summary", {}).get(
                "uniqueInferredBaseLines"
            ),
            "targetPhraseIsolatedSliceCount": reflection_shifted_carrier_content.get(
                "summary", {}
            ).get("targetPhraseIsolatedSliceCount"),
            "sliceWordCountTotal": reflection_shifted_carrier_content.get("summary", {}).get(
                "sliceWordCountTotal"
            ),
            "sliceNonTargetWordCountTotal": reflection_shifted_carrier_content.get(
                "summary", {}
            ).get("sliceNonTargetWordCountTotal"),
            "strictInstructionHitCount": reflection_shifted_carrier_content.get("summary", {}).get(
                "strictInstructionHitCount"
            ),
            "selectorUnlocked": reflection_shifted_carrier_content.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": reflection_shifted_carrier_content.get("sheet"),
        },
        "page76HighlightFoldAxisPopulationGate": {
            "decision": highlight_fold_axis_population.get("decision", {}).get(
                "page76HighlightFoldAxisPopulationGate"
            ),
            "populationCount": highlight_fold_axis_population.get("summary", {}).get("populationCount"),
            "axisCandidateCount": highlight_fold_axis_population.get("summary", {}).get("axisCandidateCount"),
            "allFourActiveAxisCount": highlight_fold_axis_population.get("summary", {}).get(
                "allFourActiveAxisCount"
            ),
            "threePlusActiveAxisCount": highlight_fold_axis_population.get("summary", {}).get(
                "threePlusActiveAxisCount"
            ),
            "twoActiveAxisCount": highlight_fold_axis_population.get("summary", {}).get("twoActiveAxisCount"),
            "tautologicalTwoActivePointAxisCount": highlight_fold_axis_population.get("summary", {}).get(
                "tautologicalTwoActivePointAxisCount"
            ),
            "nonTautologicalTwoActiveAxisCount": highlight_fold_axis_population.get("summary", {}).get(
                "nonTautologicalTwoActiveAxisCount"
            ),
            "maxNonTautologicalActiveHits": highlight_fold_axis_population.get("summary", {}).get(
                "maxNonTautologicalActiveHits"
            ),
            "strictInstructionAxisHits": highlight_fold_axis_population.get("summary", {}).get(
                "strictInstructionAxisHits"
            ),
            "selectorUnlocked": highlight_fold_axis_population.get("summary", {}).get("selectorUnlocked"),
            "sheet": highlight_fold_axis_population.get("sheet"),
        },
        "page76HighlightClusterR3GateSynthesis": {
            "decision": highlight_cluster_gate.get("decision"),
            "activeColorPattern": highlight_cluster_gate.get("activeCluster", {}).get("colorPattern"),
            "edgeInstructionHitCount": highlight_cluster_gate.get("edgeSelector", {}).get("instructionHitCount"),
            "fillLargeResidualComponentTotal": highlight_cluster_gate.get("fillResidue", {}).get("largeResidualComponentTotal"),
            "spillDominantSideStream": highlight_cluster_gate.get("spillDirection", {}).get("dominantSideStream"),
            "activeSpillOrdersAlsoSeenInControls": highlight_cluster_gate.get("spillControl", {}).get("activeOrdersAlsoSeenInControls"),
            "gateRows": [
                {
                    "gate": row.get("gate"),
                    "status": row.get("status"),
                }
                for row in highlight_cluster_gate.get("gateRows", [])
            ],
        },
        "comparisonOverdoseLayoutR3GateSynthesis": {
            "decision": comparison_layout_gate.get("decision"),
            "sourceGatePromotedForExtractionGeometry": comparison_layout_gate.get("sourceGate", {}).get("promotedForExtractionGeometry"),
            "sourceGateStyleOnlyComparisonCount": comparison_layout_gate.get("sourceGate", {}).get("styleOnlyComparisonCount"),
            "independentStrongFivePointCapsuleSequences": comparison_layout_gate.get("capsuleRecurrence", {}).get("comparisonStrongFivePointSequenceMatches"),
            "lowResWitnessStrongFivePointCapsuleSequences": comparison_layout_gate.get("capsuleRecurrence", {}).get("lowResWitnessStrongFivePointSequenceMatches"),
            "bitcoin4G5HorizontalGapPx": comparison_layout_gate.get("bitcoin4Witness", {}).get("g5HorizontalGapPx"),
            "bitcoin4O5OverlapVsTarget": comparison_layout_gate.get("bitcoin4Witness", {}).get("o5OverlapVsTarget"),
            "gateRows": [
                {
                    "gate": row.get("gate"),
                    "status": row.get("status"),
                }
                for row in comparison_layout_gate.get("gateRows", [])
            ],
        },
        "overdoseStyleUniqueness": {
            "decision": overdose_style_uniqueness.get("decision"),
            "issue24HighlighterLikePages": overdose_style_summaries.get("issue24", {}).get("highlighterLikePages"),
            "issue24OrangeBandPages": overdose_style_summaries.get("issue24", {}).get("orangeBandPages"),
            "issue24MaxHighlightScore": overdose_style_summaries.get("issue24", {}).get("maxHighlightScore"),
            "independentComparisonHighlighterLikePages": {
                slug: overdose_style_summaries.get(slug, {}).get("highlighterLikePages")
                for slug in ["issue26", "issue27", "bitcoin3"]
            },
            "bitcoin4Role": overdose_style_roles.get("bitcoin4"),
            "bitcoin4HighlighterLikePages": overdose_style_summaries.get("bitcoin4", {}).get("highlighterLikePages"),
            "allComparisonPdfsImageOnly": all(
                overdose_style_summaries.get(slug, {})
                .get("textLayer", {})
                .get("isImageOnly")
                for slug in ["issue26", "issue27", "bitcoin3", "bitcoin4"]
            ),
            "contactSheet": overdose_style_uniqueness.get("contactSheet"),
        },
        "activeEvidenceUnlockMatrix": {
            "decision": unlock_matrix.get("decision"),
            "pathsChecked": unlock_matrix.get("summary", {}).get("pathsChecked"),
            "r3FailCount": unlock_matrix.get("summary", {}).get("r3FailCount"),
            "r5FailCount": unlock_matrix.get("summary", {}).get("r5FailCount"),
            "allPathsBlockedOnR3": unlock_matrix.get("summary", {}).get("allPathsBlockedOnR3"),
            "minimumReopenConditions": unlock_matrix.get("summary", {}).get("minimumReopenConditions"),
        },
        "postUnlockSourceArrivalWatch": {
            "decision": source_arrival.get("decision"),
            "lookbackMinutes": source_arrival.get("lookbackMinutes"),
            "candidateReviewNeededCount": source_arrival.get("candidateReviewNeededCount"),
            "lowPriorityCount": source_arrival.get("lowPriorityCount"),
            "stats": source_arrival.get("stats"),
        },
        "sourceAcquisitionTargetPacket": {
            "decision": acquisition_packet.get("decision"),
            "captureJobCount": len(acquisition_packet.get("captureJobs", [])),
            "captureJobs": [
                {
                    "id": row.get("id"),
                    "priority": row.get("priority"),
                    "kind": row.get("kind"),
                    "rGates": row.get("rGates"),
                }
                for row in acquisition_packet.get("captureJobs", [])
            ],
            "benchmarkChecks": [
                {
                    "id": row.get("id"),
                    "current": row.get("current"),
                }
                for row in acquisition_packet.get("benchmarkChecks", [])
            ],
        },
        "sourceAcquisitionPacketIntegrity": {
            "decision": acquisition_integrity.get("decision"),
            "status": acquisition_integrity.get("status"),
            "failedCheckCount": len(acquisition_integrity.get("failedChecks", [])),
            "missingCriticalFileCount": len(acquisition_integrity.get("missingCriticalFiles", [])),
            "missingPacketPanelCount": len(acquisition_integrity.get("missingPacketPanels", [])),
            "captureJobCount": acquisition_integrity.get("captureJobCount"),
            "rGateCoverage": acquisition_integrity.get("rGateCoverage"),
            "benchmarkCoverage": acquisition_integrity.get("benchmarkCoverage"),
        },
        "futureSourceScoringRubric": {
            "decision": scoring_rubric.get("decision"),
            "rubricGateCount": len(scoring_rubric.get("rubricRows", [])),
            "sheet": scoring_rubric.get("sheet"),
            "allowExtractionOnlyIf": scoring_rubric.get("extractionGate", {}).get("allowExtractionOnlyIf"),
            "p78CurrentG5GapPx": scoring_rubric.get("numericBenchmarks", {}).get("p78Frame", {}).get("currentG5GapPx"),
            "p78RepairDx": scoring_rubric.get("numericBenchmarks", {}).get("p78Frame", {}).get("repairDx"),
            "p77BaselineGapPx": scoring_rubric.get("numericBenchmarks", {}).get("p77NearMiss", {}).get("baselineVerticalGapPx"),
        },
        "futureSourceRubricCurrentStackDryRun": {
            "decision": rubric_dry_run.get("decision"),
            "pathCount": rubric_dry_run.get("summary", {}).get("pathCount"),
            "extractionReadyCount": rubric_dry_run.get("summary", {}).get("extractionReadyCount"),
            "r3FailCount": rubric_dry_run.get("summary", {}).get("r3FailCount"),
            "allCurrentPathsBlocked": rubric_dry_run.get("summary", {}).get("allCurrentPathsBlocked"),
            "allCurrentPathsFailR3": rubric_dry_run.get("summary", {}).get("allCurrentPathsFailR3"),
            "sheet": rubric_dry_run.get("sheet"),
        },
        "page76TargetTextAuthorityLock": {
            "decision": target_text_lock.get("decision"),
            "targetTextAuthority": target_text_lock.get("authorityLock", {}).get("targetTextAuthority"),
            "rawPlainUse": target_text_lock.get("authorityLock", {}).get("rawPlainUse"),
            "annotatedTranscriptUse": target_text_lock.get("authorityLock", {}).get("annotatedTranscriptUse"),
            "rawPlainMissing": target_text_lock.get("authorityLock", {}).get("rawPlainMissing"),
            "authoritativeMissing": target_text_lock.get("authorityLock", {}).get("authoritativeMissing"),
            "selectorPermissionCorrectionCount": target_text_lock.get("correctionSummary", {}).get("selectorPermissionCorrectionCount"),
        },
        "page76TargetFormatAuthorityLock": {
            "decision": target_format_lock.get("decision"),
            "formatAuthority": target_format_lock.get("authorityLock", {}).get("formatAuthority"),
            "markdownUse": target_format_lock.get("authorityLock", {}).get("markdownUse"),
            "annotatedUse": target_format_lock.get("authorityLock", {}).get("annotatedUse"),
            "selectorUnlocked": target_format_lock.get("authorityLock", {}).get("selectorUnlocked"),
            "activeColorPattern": target_format_lock.get("summary", {}).get("activeColorPattern"),
            "activeVisualStateOrder": target_format_lock.get("summary", {}).get("activeVisualStateOrder"),
            "allActiveTargetsDocmTypekaBold": target_format_lock.get("summary", {}).get("allActiveTargetsDocmTypekaBold"),
            "activeVisualExactMatchCount": target_format_lock.get("summary", {}).get("activeVisualExactMatchCount"),
            "cropPackActiveCoverageCount": target_format_lock.get("summary", {}).get("cropPackActiveCoverageCount"),
        },
        "markdownDocmMismatchInstructionSurface": {
            "decision": markdown_docm_mismatch.get("decision"),
            "markdownBoldSpanCount": markdown_docm_mismatch.get("summary", {}).get("markdownBoldSpanCount"),
            "alignedCount": markdown_docm_mismatch.get("summary", {}).get("alignedCount"),
            "corridorMarkdownBoldSpanCount": markdown_docm_mismatch.get("summary", {}).get("corridorMarkdownBoldSpanCount"),
            "corridorMarkdownOnlySpanCount": markdown_docm_mismatch.get("summary", {}).get("corridorMarkdownOnlySpanCount"),
            "corridorDocmOnlyActiveTargetCount": markdown_docm_mismatch.get("summary", {}).get("corridorDocmOnlyActiveTargetCount"),
            "totalInstructionHitCount": markdown_docm_mismatch.get("summary", {}).get("totalInstructionHitCount"),
            "corridorMarkdownOnlyStream": markdown_docm_mismatch.get("streams", {}).get("corridorMarkdownOnlyStream"),
            "corridorDocmOnlyActiveTargetStream": markdown_docm_mismatch.get("streams", {}).get("corridorDocmOnlyActiveTargetStream"),
        },
        "page76ActiveTargetCropCompletion": {
            "decision": active_crop_completion.get("decision"),
            "cropCoverage": active_crop_completion.get("summary", {}).get("cropCoverage"),
            "activeColorPattern": active_crop_completion.get("summary", {}).get("activeColorPattern"),
            "activeVisualStateOrder": active_crop_completion.get("summary", {}).get("activeVisualStateOrder"),
            "pageLines": active_crop_completion.get("summary", {}).get("pageLines"),
            "corridorIndexes": active_crop_completion.get("summary", {}).get("corridorIndexes"),
            "selectorUnlocked": active_crop_completion.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_crop_completion.get("sheet"),
        },
        "sourcePacketCropAuthoritySync": {
            "decision": packet_crop_sync.get("decision"),
            "syncStatus": packet_crop_sync.get("summary", {}).get("syncStatus"),
            "historicalPacketStillValid": packet_crop_sync.get("summary", {}).get("historicalPacketStillValid"),
            "historicalPacketUsesOldPriorityCropPanel": packet_crop_sync.get("summary", {}).get("historicalPacketUsesOldPriorityCropPanel"),
            "completedCropPanelAlreadyInHistoricalPacket": packet_crop_sync.get("summary", {}).get("completedCropPanelAlreadyInHistoricalPacket"),
            "cropCoverage": packet_crop_sync.get("summary", {}).get("cropCoverage"),
            "allTargetCropsPresent": packet_crop_sync.get("summary", {}).get("allTargetCropsPresent"),
            "selectorUnlocked": packet_crop_sync.get("summary", {}).get("selectorUnlocked"),
            "sheet": packet_crop_sync.get("sheet"),
        },
        "sourcePacketYkFrameBenchmarkSync": {
            "decision": packet_yk_sync.get("decision"),
            "historicalPacketHasYkFrameBenchmark": packet_yk_sync.get("summary", {}).get("historicalPacketHasYkFrameBenchmark"),
            "supplementNeeded": packet_yk_sync.get("summary", {}).get("supplementNeeded"),
            "frameYkActiveTargetCoverage": packet_yk_sync.get("summary", {}).get("frameYkActiveTargetCoverage"),
            "frameYkNonActiveGroupCount": packet_yk_sync.get("summary", {}).get("frameYkNonActiveGroupCount"),
            "fullPageYkNonActiveGroupCount": packet_yk_sync.get("summary", {}).get("fullPageYkNonActiveGroupCount"),
            "boundedStreamCount": packet_yk_sync.get("summary", {}).get("boundedStreamCount"),
            "hardInstructionHitCount": packet_yk_sync.get("summary", {}).get("hardInstructionHitCount"),
            "sourceBackedUnitOrder": packet_yk_sync.get("summary", {}).get("sourceBackedUnitOrder"),
            "selectorUnlocked": packet_yk_sync.get("summary", {}).get("selectorUnlocked"),
            "sheet": packet_yk_sync.get("sheet"),
        },
        "sourcePacketNativeBenchmarkBridge": {
            "decision": packet_native_bridge.get("decision", {}).get(
                "sourcePacketNativeBenchmarkBridge"
            ),
            "transform": packet_native_bridge.get("transform"),
            "benchmarkBoxCount": packet_native_bridge.get("summary", {}).get(
                "benchmarkBoxCount"
            ),
            "activePageLines": packet_native_bridge.get("summary", {}).get("activePageLines"),
            "activeCorridorIndexes": packet_native_bridge.get("summary", {}).get(
                "activeCorridorIndexes"
            ),
            "activeVisualStateOrder": packet_native_bridge.get("summary", {}).get(
                "activeVisualStateOrder"
            ),
            "c9FrameXMirrorInvariant": packet_native_bridge.get("summary", {}).get(
                "c9FrameXMirrorInvariant"
            ),
            "headerGlyphSequence": packet_native_bridge.get("summary", {}).get(
                "headerGlyphSequence"
            ),
            "headerGlyphMaxEdgeDeltaVsEqualSlotPx": packet_native_bridge.get("summary", {}).get(
                "headerGlyphMaxEdgeDeltaVsEqualSlotPx"
            ),
            "rot180MeanAbsDiff": packet_native_bridge.get("imageDiff", {}).get(
                "rot180MeanAbsDiff"
            ),
            "directMeanAbsDiff": packet_native_bridge.get("imageDiff", {}).get(
                "directMeanAbsDiff"
            ),
            "allNativeBoxesInBounds": packet_native_bridge.get("summary", {}).get(
                "allNativeBoxesInBounds"
            ),
            "selectorUnlocked": packet_native_bridge.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_native_bridge.get("sheet"),
        },
        "sourcePacketVisualStateRoundtrip": {
            "decision": packet_visual_roundtrip.get("decision", {}).get(
                "sourcePacketVisualStateRoundtrip"
            ),
            "activeExpectedVisualStateOrder": packet_visual_roundtrip.get("summary", {}).get(
                "activeExpectedVisualStateOrder"
            ),
            "activeClassifiedVisualStateOrder": packet_visual_roundtrip.get("summary", {}).get(
                "activeClassifiedVisualStateOrder"
            ),
            "activePageLines": packet_visual_roundtrip.get("summary", {}).get("activePageLines"),
            "activeCorridorIndexes": packet_visual_roundtrip.get("summary", {}).get(
                "activeCorridorIndexes"
            ),
            "allActiveVisualStatesMatch": packet_visual_roundtrip.get("summary", {}).get(
                "allActiveVisualStatesMatch"
            ),
            "allActiveDocmBoldFractionOne": packet_visual_roundtrip.get("summary", {}).get(
                "allActiveDocmBoldFractionOne"
            ),
            "activeMaxMeanAbsDiff": packet_visual_roundtrip.get("summary", {}).get(
                "activeMaxMeanAbsDiff"
            ),
            "activeYOrangeRatioRange": packet_visual_roundtrip.get("summary", {}).get(
                "activeYOrangeRatioRange"
            ),
            "activeKDarkRatioRange": packet_visual_roundtrip.get("summary", {}).get(
                "activeKDarkRatioRange"
            ),
            "overdoseGlyphSequence": packet_visual_roundtrip.get("summary", {}).get(
                "overdoseGlyphSequence"
            ),
            "overdoseGlyphMaxDarkRatio": packet_visual_roundtrip.get("summary", {}).get(
                "overdoseGlyphMaxDarkRatio"
            ),
            "overdoseGlyphMaxOrangeRatio": packet_visual_roundtrip.get("summary", {}).get(
                "overdoseGlyphMaxOrangeRatio"
            ),
            "selectorUnlocked": packet_visual_roundtrip.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_visual_roundtrip.get("sheet"),
        },
        "sourcePacketAlignmentTolerance": {
            "decision": packet_alignment_tolerance.get("decision", {}).get(
                "sourcePacketAlignmentTolerance"
            ),
            "activeExpectedVisualStateOrder": packet_alignment_tolerance.get("summary", {}).get(
                "activeExpectedVisualStateOrder"
            ),
            "activePageLines": packet_alignment_tolerance.get("summary", {}).get(
                "activePageLines"
            ),
            "activeCorridorIndexes": packet_alignment_tolerance.get("summary", {}).get(
                "activeCorridorIndexes"
            ),
            "commonOutwardPadAllTargetsPassPx": packet_alignment_tolerance.get("summary", {}).get(
                "commonOutwardPadAllTargetsPassPx"
            ),
            "commonInsetPadAllTargetsPassPx": packet_alignment_tolerance.get("summary", {}).get(
                "commonInsetPadAllTargetsPassPx"
            ),
            "commonFullEightDirectionShiftAllTargetsPassPx": packet_alignment_tolerance.get(
                "summary", {}
            ).get("commonFullEightDirectionShiftAllTargetsPassPx"),
            "largestAnyTargetOutwardPadPassPx": packet_alignment_tolerance.get("summary", {}).get(
                "largestAnyTargetOutwardPadPassPx"
            ),
            "smallestFirstPadFailurePx": packet_alignment_tolerance.get("summary", {}).get(
                "smallestFirstPadFailurePx"
            ),
            "overdoseControlClassifiedStates": packet_alignment_tolerance.get("summary", {}).get(
                "overdoseControlClassifiedStates"
            ),
            "overdoseControlMaxDarkRatio": packet_alignment_tolerance.get("summary", {}).get(
                "overdoseControlMaxDarkRatio"
            ),
            "overdoseControlMaxOrangeRatio": packet_alignment_tolerance.get("summary", {}).get(
                "overdoseControlMaxOrangeRatio"
            ),
            "maxVariantMeanAbsDiff": packet_alignment_tolerance.get("summary", {}).get(
                "maxVariantMeanAbsDiff"
            ),
            "selectorUnlocked": packet_alignment_tolerance.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_alignment_tolerance.get("sheet"),
        },
        "sourcePacketGeometricFingerprint": {
            "decision": packet_geometric_fingerprint.get("decision", {}).get(
                "sourcePacketGeometricFingerprint"
            ),
            "activeOrder": packet_geometric_fingerprint.get("summary", {}).get(
                "activeOrder"
            ),
            "visualStateOrder": packet_geometric_fingerprint.get("summary", {}).get(
                "visualStateOrder"
            ),
            "activePageLines": packet_geometric_fingerprint.get("summary", {}).get(
                "activePageLines"
            ),
            "activeCorridorIndexes": packet_geometric_fingerprint.get("summary", {}).get(
                "activeCorridorIndexes"
            ),
            "pageLineGaps": packet_geometric_fingerprint.get("summary", {}).get(
                "pageLineGaps"
            ),
            "corridorGaps": packet_geometric_fingerprint.get("summary", {}).get(
                "corridorGaps"
            ),
            "dxSignStream": packet_geometric_fingerprint.get("summary", {}).get(
                "dxSignStream"
            ),
            "dySignStream": packet_geometric_fingerprint.get("summary", {}).get(
                "dySignStream"
            ),
            "clusterBox": packet_geometric_fingerprint.get("summary", {}).get(
                "clusterBox"
            ),
            "clusterSize": packet_geometric_fingerprint.get("summary", {}).get(
                "clusterSize"
            ),
            "maxNativeRoundtripCenterErrorPx": packet_geometric_fingerprint.get(
                "summary", {}
            ).get("maxNativeRoundtripCenterErrorPx"),
            "pairwiseRecordCount": packet_geometric_fingerprint.get("summary", {}).get(
                "pairwiseRecordCount"
            ),
            "overdoseHeaderGlyphSequence": packet_geometric_fingerprint.get("summary", {}).get(
                "overdoseHeaderGlyphSequence"
            ),
            "sourceRegistrationFingerprint": packet_geometric_fingerprint.get("summary", {}).get(
                "sourceRegistrationFingerprint"
            ),
            "selectorUnlocked": packet_geometric_fingerprint.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_geometric_fingerprint.get("sheet"),
        },
        "sourcePacketFrameNormalizedGeometry": {
            "decision": packet_frame_normalized.get("decision", {}).get(
                "sourcePacketFrameNormalizedGeometry"
            ),
            "activeOrder": packet_frame_normalized.get("summary", {}).get(
                "activeOrder"
            ),
            "visualStateOrder": packet_frame_normalized.get("summary", {}).get(
                "visualStateOrder"
            ),
            "activePageLines": packet_frame_normalized.get("summary", {}).get(
                "activePageLines"
            ),
            "activeCorridorIndexes": packet_frame_normalized.get("summary", {}).get(
                "activeCorridorIndexes"
            ),
            "c9FrameBox": packet_frame_normalized.get("summary", {}).get("c9FrameBox"),
            "c9NormalizedCenterStream": packet_frame_normalized.get("summary", {}).get(
                "c9NormalizedCenterStream"
            ),
            "c9ActiveFullInsideCount": packet_frame_normalized.get("summary", {}).get(
                "c9ActiveFullInsideCount"
            ),
            "reflectedP78FrameBox": packet_frame_normalized.get("summary", {}).get(
                "reflectedP78FrameBox"
            ),
            "reflectedP78FullInsideCount": packet_frame_normalized.get("summary", {}).get(
                "reflectedP78FullInsideCount"
            ),
            "reflectedP78PartialOverlapIds": packet_frame_normalized.get("summary", {}).get(
                "reflectedP78PartialOverlapIds"
            ),
            "mirrorHitCountsByThreshold": packet_frame_normalized.get("summary", {}).get(
                "mirrorHitCountsByThreshold"
            ),
            "mirrorAllFourRehitByThreshold": packet_frame_normalized.get("summary", {}).get(
                "mirrorAllFourRehitByThreshold"
            ),
            "frameNormalizedFingerprint": packet_frame_normalized.get("summary", {}).get(
                "frameNormalizedFingerprint"
            ),
            "selectorUnlocked": packet_frame_normalized.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_frame_normalized.get("sheet"),
        },
        "sourcePacketColorProfileManifest": {
            "decision": packet_color_profile.get("decision", {}).get(
                "sourcePacketColorProfileManifest"
            ),
            "activeOrder": packet_color_profile.get("summary", {}).get("activeOrder"),
            "activeVisualStateOrder": packet_color_profile.get("summary", {}).get(
                "activeVisualStateOrder"
            ),
            "activeAllStatesMatchExpected": packet_color_profile.get("summary", {}).get(
                "activeAllStatesMatchExpected"
            ),
            "activePageLines": packet_color_profile.get("summary", {}).get(
                "activePageLines"
            ),
            "activeCorridorIndexes": packet_color_profile.get("summary", {}).get(
                "activeCorridorIndexes"
            ),
            "activeYOrangeRatioRange": packet_color_profile.get("summary", {}).get(
                "activeYOrangeRatioRange"
            ),
            "activeKDarkRatioRange": packet_color_profile.get("summary", {}).get(
                "activeKDarkRatioRange"
            ),
            "activeKOrangeRatioRange": packet_color_profile.get("summary", {}).get(
                "activeKOrangeRatioRange"
            ),
            "overdoseControlClassifiedStateStream": packet_color_profile.get(
                "summary", {}
            ).get("overdoseControlClassifiedStateStream"),
            "overdoseControlMaxOrangeRatio": packet_color_profile.get("summary", {}).get(
                "overdoseControlMaxOrangeRatio"
            ),
            "overdoseControlMaxDarkRatio": packet_color_profile.get("summary", {}).get(
                "overdoseControlMaxDarkRatio"
            ),
            "minActiveYOrangeMinusMaxControlOrange": packet_color_profile.get(
                "summary", {}
            ).get("minActiveYOrangeMinusMaxControlOrange"),
            "minActiveKDarkMinusMaxControlDark": packet_color_profile.get("summary", {}).get(
                "minActiveKDarkMinusMaxControlDark"
            ),
            "maxNativeRoundtripMeanAbsDiff": packet_color_profile.get("summary", {}).get(
                "maxNativeRoundtripMeanAbsDiff"
            ),
            "colorProfileFingerprint": packet_color_profile.get("summary", {}).get(
                "colorProfileFingerprint"
            ),
            "selectorUnlocked": packet_color_profile.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_color_profile.get("sheet"),
        },
        "sourcePacketRepairedP78FrameResidual": {
            "decision": packet_repaired_p78_frame.get("decision", {}).get(
                "sourcePacketRepairedP78FrameResidual"
            ),
            "activeOrder": packet_repaired_p78_frame.get("activeOrder"),
            "activeVisualStateOrder": packet_repaired_p78_frame.get(
                "activeVisualStateOrder"
            ),
            "activePageLines": packet_repaired_p78_frame.get("activePageLines"),
            "activeCorridorIndexes": packet_repaired_p78_frame.get(
                "activeCorridorIndexes"
            ),
            "maxFullInsideCount": packet_repaired_p78_frame.get("summary", {}).get(
                "maxFullInsideCount"
            ),
            "maxPartialHitCount": packet_repaired_p78_frame.get("summary", {}).get(
                "maxPartialHitCount"
            ),
            "bestG5GapFrame": packet_repaired_p78_frame.get("summary", {}).get(
                "bestG5GapFrame"
            ),
            "bestG5HorizontalGapPx": packet_repaired_p78_frame.get("summary", {}).get(
                "bestG5HorizontalGapPx"
            ),
            "bestO5OverlapFrame": packet_repaired_p78_frame.get("summary", {}).get(
                "bestO5OverlapFrame"
            ),
            "bestO5OverlapFraction": packet_repaired_p78_frame.get("summary", {}).get(
                "bestO5OverlapFraction"
            ),
            "minimumRepairedB4TouchLeftExpansionPx": packet_repaired_p78_frame.get(
                "summary", {}
            ).get("minimumRepairedB4TouchLeftExpansionPx"),
            "minimumRepairedB4FullLeftExpansionPx": packet_repaired_p78_frame.get(
                "summary", {}
            ).get("minimumRepairedB4FullLeftExpansionPx"),
            "minimumRepairedO4TouchTopExpansionPx": packet_repaired_p78_frame.get(
                "summary", {}
            ).get("minimumRepairedO4TouchTopExpansionPx"),
            "minimumRepairedO4FullTopExpansionPx": packet_repaired_p78_frame.get(
                "summary", {}
            ).get("minimumRepairedO4FullTopExpansionPx"),
            "frameResidualFingerprint": packet_repaired_p78_frame.get("summary", {}).get(
                "frameResidualFingerprint"
            ),
            "selectorUnlocked": packet_repaired_p78_frame.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_repaired_p78_frame.get("sheet"),
        },
        "sourcePacketRepairedFrameExpansionLeakage": {
            "decision": packet_repaired_frame_leakage.get("decision", {}).get(
                "sourcePacketRepairedFrameExpansionLeakage"
            ),
            "frameVariantCount": packet_repaired_frame_leakage.get("summary", {}).get(
                "frameVariantCount"
            ),
            "scenarioCount": packet_repaired_frame_leakage.get("summary", {}).get(
                "scenarioCount"
            ),
            "baseMaxLineContextWordCount": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("baseMaxLineContextWordCount"),
            "touchMinLineContextWordCount": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("touchMinLineContextWordCount"),
            "touchMinLineContextNonTargetWordCount": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("touchMinLineContextNonTargetWordCount"),
            "fullCoverMinLineContextWordCount": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("fullCoverMinLineContextWordCount"),
            "fullCoverMinLineContextNonTargetWordCount": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("fullCoverMinLineContextNonTargetWordCount"),
            "fullCoverOcrMapWordCenterCountRange": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("fullCoverOcrMapWordCenterCountRange"),
            "fullCoverMaxNonActiveHighlightEntryCount": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("fullCoverMaxNonActiveHighlightEntryCount"),
            "fullCoverHardInstructionHitCount": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("fullCoverHardInstructionHitCount"),
            "fullCoverOcrMapHardInstructionHitCount": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("fullCoverOcrMapHardInstructionHitCount"),
            "fullCoverLineRanges": packet_repaired_frame_leakage.get("summary", {}).get(
                "fullCoverLineRanges"
            ),
            "expansionLeakageFingerprint": packet_repaired_frame_leakage.get(
                "summary", {}
            ).get("expansionLeakageFingerprint"),
            "selectorUnlocked": packet_repaired_frame_leakage.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_repaired_frame_leakage.get("sheet"),
        },
        "sourcePacketHandoffIntegrityMatrix": {
            "decision": packet_handoff_integrity.get("decision", {}).get(
                "sourcePacketHandoffIntegrityMatrix"
            ),
            "gateCount": packet_handoff_integrity.get("summary", {}).get("gateCount"),
            "passGateCount": packet_handoff_integrity.get("summary", {}).get(
                "passGateCount"
            ),
            "rejectGateCount": packet_handoff_integrity.get("summary", {}).get(
                "rejectGateCount"
            ),
            "contradictionCount": packet_handoff_integrity.get("summary", {}).get(
                "contradictionCount"
            ),
            "selectorUnlockedCount": packet_handoff_integrity.get("summary", {}).get(
                "selectorUnlockedCount"
            ),
            "extractionReadyGateCount": packet_handoff_integrity.get("summary", {}).get(
                "extractionReadyGateCount"
            ),
            "activeVisualStateOrder": packet_handoff_integrity.get("summary", {}).get(
                "activeVisualStateOrder"
            ),
            "activePageLines": packet_handoff_integrity.get("summary", {}).get(
                "activePageLines"
            ),
            "activeCorridorIndexes": packet_handoff_integrity.get("summary", {}).get(
                "activeCorridorIndexes"
            ),
            "commonShiftTolerancePx": packet_handoff_integrity.get("summary", {}).get(
                "commonShiftTolerancePx"
            ),
            "fullCoverLeakageWords": packet_handoff_integrity.get("summary", {}).get(
                "fullCoverLeakageWords"
            ),
            "fullCoverLeakageNonTargetWords": packet_handoff_integrity.get(
                "summary", {}
            ).get("fullCoverLeakageNonTargetWords"),
            "integrityFingerprint": packet_handoff_integrity.get("summary", {}).get(
                "integrityFingerprint"
            ),
            "selectorUnlocked": packet_handoff_integrity.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_handoff_integrity.get("sheet"),
        },
        "sourcePacketFalsePositiveGuardrail": {
            "decision": packet_false_positive_guardrail.get("decision", {}).get(
                "sourcePacketFalsePositiveGuardrail"
            ),
            "guardrailCount": packet_false_positive_guardrail.get("summary", {}).get(
                "guardrailCount"
            ),
            "hardRejectWithoutR3Count": packet_false_positive_guardrail.get(
                "summary", {}
            ).get("hardRejectWithoutR3Count"),
            "selectorUnlockedCount": packet_false_positive_guardrail.get(
                "summary", {}
            ).get("selectorUnlockedCount"),
            "activeVisualStateOrder": packet_false_positive_guardrail.get(
                "summary", {}
            ).get("activeVisualStateOrder"),
            "activePageLines": packet_false_positive_guardrail.get("summary", {}).get(
                "activePageLines"
            ),
            "activeCorridorIndexes": packet_false_positive_guardrail.get(
                "summary", {}
            ).get("activeCorridorIndexes"),
            "requiredToReopenUniqueCount": packet_false_positive_guardrail.get(
                "summary", {}
            ).get("requiredToReopenUniqueCount"),
            "falsePositiveGuardrailFingerprint": packet_false_positive_guardrail.get(
                "summary", {}
            ).get("falsePositiveGuardrailFingerprint"),
            "selectorUnlocked": packet_false_positive_guardrail.get("summary", {}).get(
                "selectorUnlocked"
            ),
            "sheet": packet_false_positive_guardrail.get("sheet"),
        },
        "sourcePacketR3BridgeAudit": {
            "decision": packet_r3_bridge.get("decision", {}).get(
                "sourcePacketR3BridgeAudit"
            ),
            "authoritySourceCount": packet_r3_bridge.get("summary", {}).get(
                "authoritySourceCount"
            ),
            "authorityActiveTargetMentionCount": packet_r3_bridge.get(
                "summary", {}
            ).get("authorityActiveTargetMentionCount"),
            "authorityVisualOnlyTargetWindowCount": packet_r3_bridge.get(
                "summary", {}
            ).get("authorityVisualOnlyTargetWindowCount"),
            "sourceBackedR3BridgeHitCount": packet_r3_bridge.get("summary", {}).get(
                "sourceBackedR3BridgeHitCount"
            ),
            "derivedCorrectionBridgeWindowCount": packet_r3_bridge.get(
                "summary", {}
            ).get("derivedCorrectionBridgeWindowCount"),
            "externalRawLikeR3PassCount": packet_r3_bridge.get("summary", {}).get(
                "externalRawLikeR3PassCount"
            ),
            "generatedUnitOrderPhraseCount": packet_r3_bridge.get("summary", {}).get(
                "generatedUnitOrderPhraseCount"
            ),
            "guardrailStillBlockedCount": packet_r3_bridge.get("summary", {}).get(
                "guardrailStillBlockedCount"
            ),
            "r3BridgeFingerprint": packet_r3_bridge.get("summary", {}).get(
                "r3BridgeFingerprint"
            ),
            "sourceBackedR3BridgeUnlocked": packet_r3_bridge.get("summary", {}).get(
                "sourceBackedR3BridgeUnlocked"
            ),
            "sheet": packet_r3_bridge.get("sheet"),
        },
        "sourcePacketReopenTriggerMatrix": {
            "decision": packet_reopen_trigger.get("decision", {}).get(
                "sourcePacketReopenTriggerMatrix"
            ),
            "triggerCount": packet_reopen_trigger.get("summary", {}).get("triggerCount"),
            "satisfiedTriggerCount": packet_reopen_trigger.get("summary", {}).get(
                "satisfiedTriggerCount"
            ),
            "blockedTriggerCount": packet_reopen_trigger.get("summary", {}).get(
                "blockedTriggerCount"
            ),
            "r1r5GateCount": packet_reopen_trigger.get("summary", {}).get(
                "r1r5GateCount"
            ),
            "sourceBackedR3BridgeHitCount": packet_reopen_trigger.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "guardrailStillBlockedCount": packet_reopen_trigger.get("summary", {}).get(
                "guardrailStillBlockedCount"
            ),
            "activeVisualStateOrder": packet_reopen_trigger.get("summary", {}).get(
                "activeVisualStateOrder"
            ),
            "activePageLines": packet_reopen_trigger.get("summary", {}).get(
                "activePageLines"
            ),
            "activeCorridorIndexes": packet_reopen_trigger.get("summary", {}).get(
                "activeCorridorIndexes"
            ),
            "reopenTriggerFingerprint": packet_reopen_trigger.get("summary", {}).get(
                "reopenTriggerFingerprint"
            ),
            "sheet": packet_reopen_trigger.get("sheet"),
        },
        "sourcePacketOrientationDisambiguator": {
            "decision": packet_orientation_disambiguator.get("decision", {}).get(
                "sourcePacketOrientationDisambiguator"
            ),
            "orientationModeCount": packet_orientation_disambiguator.get("summary", {}).get(
                "orientationModeCount"
            ),
            "acceptedOrientationModeCount": packet_orientation_disambiguator.get(
                "summary", {}
            ).get("acceptedOrientationModeCount"),
            "rejectedOrientationModeCount": packet_orientation_disambiguator.get(
                "summary", {}
            ).get("rejectedOrientationModeCount"),
            "ambiguousSignalCount": packet_orientation_disambiguator.get("summary", {}).get(
                "ambiguousSignalCount"
            ),
            "discriminatingSignalCount": packet_orientation_disambiguator.get(
                "summary", {}
            ).get("discriminatingSignalCount"),
            "currentVisualStatePattern": packet_orientation_disambiguator.get(
                "summary", {}
            ).get("currentVisualStatePattern"),
            "currentColorPattern": packet_orientation_disambiguator.get("summary", {}).get(
                "currentColorPattern"
            ),
            "readablePageLineOrder": packet_orientation_disambiguator.get("summary", {}).get(
                "readablePageLineOrder"
            ),
            "nativeUnnormalizedPageLineOrder": packet_orientation_disambiguator.get(
                "summary", {}
            ).get("nativeUnnormalizedPageLineOrder"),
            "readableCorridorOrder": packet_orientation_disambiguator.get("summary", {}).get(
                "readableCorridorOrder"
            ),
            "nativeUnnormalizedCorridorOrder": packet_orientation_disambiguator.get(
                "summary", {}
            ).get("nativeUnnormalizedCorridorOrder"),
            "readableDxSignStream": packet_orientation_disambiguator.get("summary", {}).get(
                "readableDxSignStream"
            ),
            "readableDySignStream": packet_orientation_disambiguator.get("summary", {}).get(
                "readableDySignStream"
            ),
            "commonShiftTolerancePx": packet_orientation_disambiguator.get("summary", {}).get(
                "commonShiftTolerancePx"
            ),
            "sourceBackedR3BridgeHitCount": packet_orientation_disambiguator.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_orientation_disambiguator.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "orientationDisambiguatorFingerprint": packet_orientation_disambiguator.get(
                "summary", {}
            ).get("orientationDisambiguatorFingerprint"),
            "sheet": packet_orientation_disambiguator.get("sheet"),
        },
        "sourcePacketOrientationControlQuartets": {
            "decision": packet_orientation_control_quartets.get("decision", {}).get(
                "sourcePacketOrientationControlQuartets"
            ),
            "fullPageYkCombinationCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("fullPageYkCombinationCount"),
            "fullPageYkYkkyCombinationCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("fullPageYkYkkyCombinationCount"),
            "fullPageYkYkkyNonExactCombinationCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("fullPageYkYkkyNonExactCombinationCount"),
            "fullPageYkSlidingWindowCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("fullPageYkSlidingWindowCount"),
            "fullPageYkSlidingYkkyCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("fullPageYkSlidingYkkyCount"),
            "formatLineCombinationCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("formatLineCombinationCount"),
            "formatLineGapExactMatchCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("formatLineGapExactMatchCount"),
            "formatLineGapExactNonActiveMatchCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("formatLineGapExactNonActiveMatchCount"),
            "nonActiveYkGroupsMissingPixelGeometryCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("nonActiveYkGroupsMissingPixelGeometryCount"),
            "sourceBackedR3BridgeHitCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "orientationControlQuartetFingerprint": packet_orientation_control_quartets.get(
                "summary", {}
            ).get("orientationControlQuartetFingerprint"),
            "sheet": packet_orientation_control_quartets.get("sheet"),
        },
        "sourcePacketSourceReviewGate": {
            "decision": packet_source_review_gate.get("decision", {}).get(
                "sourcePacketSourceReviewGate"
            ),
            "pathCount": packet_source_review_gate.get("summary", {}).get("pathCount"),
            "extractionReadyCount": packet_source_review_gate.get("summary", {}).get(
                "extractionReadyCount"
            ),
            "r3FailCount": packet_source_review_gate.get("summary", {}).get("r3FailCount"),
            "r1FailCount": packet_source_review_gate.get("summary", {}).get("r1FailCount"),
            "r4PassCount": packet_source_review_gate.get("summary", {}).get("r4PassCount"),
            "satisfiedReopenTriggerCount": packet_source_review_gate.get("summary", {}).get(
                "satisfiedReopenTriggerCount"
            ),
            "sourceBackedR3BridgeHitCount": packet_source_review_gate.get("summary", {}).get(
                "sourceBackedR3BridgeHitCount"
            ),
            "orientationControlYkkyCombinationCount": packet_source_review_gate.get(
                "summary", {}
            ).get("orientationControlYkkyCombinationCount"),
            "sourceReviewGateFingerprint": packet_source_review_gate.get("summary", {}).get(
                "sourceReviewGateFingerprint"
            ),
            "sheet": packet_source_review_gate.get("sheet"),
        },
        "sourcePacketOverdoseTransformControl": {
            "decision": packet_overdose_transform_control.get("decision", {}).get(
                "sourcePacketOverdoseTransformControl"
            ),
            "glyphSequence": packet_overdose_transform_control.get("summary", {}).get(
                "glyphSequence"
            ),
            "headerGlyphMaxEdgeDeltaVsEqualSlotPx": packet_overdose_transform_control.get(
                "summary", {}
            ).get("headerGlyphMaxEdgeDeltaVsEqualSlotPx"),
            "activeCenterLineOrderStream": packet_overdose_transform_control.get(
                "summary", {}
            ).get("activeCenterLineOrderStream"),
            "activeCenterXOrderStream": packet_overdose_transform_control.get(
                "summary", {}
            ).get("activeCenterXOrderStream"),
            "activeBlackSpanXOrderStream": packet_overdose_transform_control.get(
                "summary", {}
            ).get("activeBlackSpanXOrderStream"),
            "p75ControlSpan": packet_overdose_transform_control.get("summary", {}).get(
                "p75ControlSpan"
            ),
            "p75MirrorVariantMatchCount": packet_overdose_transform_control.get(
                "summary", {}
            ).get("p75MirrorVariantMatchCount"),
            "mirrorVariantCount": packet_overdose_transform_control.get("summary", {}).get(
                "mirrorVariantCount"
            ),
            "toleranceActiveOverCount": packet_overdose_transform_control.get(
                "summary", {}
            ).get("toleranceActiveOverCount"),
            "toleranceP75OverCount": packet_overdose_transform_control.get(
                "summary", {}
            ).get("toleranceP75OverCount"),
            "sourceReviewExtractionReadyCount": packet_overdose_transform_control.get(
                "summary", {}
            ).get("sourceReviewExtractionReadyCount"),
            "sourceBackedR3BridgeHitCount": packet_overdose_transform_control.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "overdoseTransformControlFingerprint": packet_overdose_transform_control.get(
                "summary", {}
            ).get("overdoseTransformControlFingerprint"),
            "sheet": packet_overdose_transform_control.get("sheet"),
        },
        "sourcePacketFoldFormatIntersectionControl": {
            "decision": packet_fold_format_intersection.get("decision", {}).get(
                "sourcePacketFoldFormatIntersectionControl"
            ),
            "intersectionGateCount": packet_fold_format_intersection.get("summary", {}).get(
                "intersectionGateCount"
            ),
            "passGateCount": packet_fold_format_intersection.get("summary", {}).get(
                "passGateCount"
            ),
            "partialGateCount": packet_fold_format_intersection.get("summary", {}).get(
                "partialGateCount"
            ),
            "failGateCount": packet_fold_format_intersection.get("summary", {}).get(
                "failGateCount"
            ),
            "extractionReadyIntersectionCount": packet_fold_format_intersection.get(
                "summary", {}
            ).get("extractionReadyIntersectionCount"),
            "allFourActiveCarrierCount": packet_fold_format_intersection.get(
                "summary", {}
            ).get("allFourActiveCarrierCount"),
            "singleShiftAllFourCount": packet_fold_format_intersection.get("summary", {}).get(
                "singleShiftAllFourCount"
            ),
            "sliceNonTargetWordCountTotal": packet_fold_format_intersection.get(
                "summary", {}
            ).get("sliceNonTargetWordCountTotal"),
            "targetPhraseIsolatedSliceCount": packet_fold_format_intersection.get(
                "summary", {}
            ).get("targetPhraseIsolatedSliceCount"),
            "allFourActiveAxisCount": packet_fold_format_intersection.get("summary", {}).get(
                "allFourActiveAxisCount"
            ),
            "formatAuthorityPassCount": packet_fold_format_intersection.get(
                "summary", {}
            ).get("formatAuthorityPassCount"),
            "witnessConflictCount": packet_fold_format_intersection.get("summary", {}).get(
                "witnessConflictCount"
            ),
            "sourceBackedR3BridgeHitCount": packet_fold_format_intersection.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "selectorUnlockedCount": packet_fold_format_intersection.get("summary", {}).get(
                "selectorUnlockedCount"
            ),
            "foldFormatIntersectionFingerprint": packet_fold_format_intersection.get(
                "summary", {}
            ).get("foldFormatIntersectionFingerprint"),
            "sheet": packet_fold_format_intersection.get("sheet"),
        },
        "sourcePacketTerminalCoverageMatrix": {
            "decision": packet_terminal_coverage.get("decision", {}).get(
                "sourcePacketTerminalCoverageMatrix"
            ),
            "coverageAreaCount": packet_terminal_coverage.get("summary", {}).get(
                "coverageAreaCount"
            ),
            "coveredGuardrailCount": packet_terminal_coverage.get("summary", {}).get(
                "coveredGuardrailCount"
            ),
            "uncoveredGuardrailCount": packet_terminal_coverage.get("summary", {}).get(
                "uncoveredGuardrailCount"
            ),
            "extractionReadyAreaCount": packet_terminal_coverage.get("summary", {}).get(
                "extractionReadyAreaCount"
            ),
            "sourceBackedR3BridgeHitCount": packet_terminal_coverage.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_terminal_coverage.get("summary", {}).get(
                "satisfiedReopenTriggerCount"
            ),
            "selectorUnlockedCount": packet_terminal_coverage.get("summary", {}).get(
                "selectorUnlockedCount"
            ),
            "sourceFilesPresentCount": packet_terminal_coverage.get("summary", {}).get(
                "sourceFilesPresentCount"
            ),
            "sourceFilesCheckedCount": packet_terminal_coverage.get("summary", {}).get(
                "sourceFilesCheckedCount"
            ),
            "terminalCoverageFingerprint": packet_terminal_coverage.get("summary", {}).get(
                "terminalCoverageFingerprint"
            ),
            "sheet": packet_terminal_coverage.get("sheet"),
        },
        "sourcePacketActiveTargetAuthorityCrosscheck": {
            "decision": packet_active_target_authority.get("decision", {}).get(
                "sourcePacketActiveTargetAuthorityCrosscheck"
            ),
            "activeTargetCount": packet_active_target_authority.get("summary", {}).get(
                "activeTargetCount"
            ),
            "canonicalPresentCount": packet_active_target_authority.get("summary", {}).get(
                "canonicalPresentCount"
            ),
            "markdownPresentCount": packet_active_target_authority.get("summary", {}).get(
                "markdownPresentCount"
            ),
            "annotatedPresentCount": packet_active_target_authority.get("summary", {}).get(
                "annotatedPresentCount"
            ),
            "formatAuthorityPassCount": packet_active_target_authority.get("summary", {}).get(
                "formatAuthorityPassCount"
            ),
            "terminalCoverageReadyAreas": packet_active_target_authority.get(
                "summary", {}
            ).get("terminalCoverageReadyAreas"),
            "rawPlainMissing": packet_active_target_authority.get("summary", {}).get(
                "rawPlainMissing"
            ),
            "activeCorridorCorrectionCount": packet_active_target_authority.get(
                "summary", {}
            ).get("activeCorridorCorrectionCount"),
            "selectorPermissionCorrectionCount": packet_active_target_authority.get(
                "summary", {}
            ).get("selectorPermissionCorrectionCount"),
            "witnessConflictCount": packet_active_target_authority.get("summary", {}).get(
                "witnessConflictCount"
            ),
            "sourceBackedR3BridgeHitCount": packet_active_target_authority.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "authorityCrosscheckFingerprint": packet_active_target_authority.get(
                "summary", {}
            ).get("authorityCrosscheckFingerprint"),
            "sheet": packet_active_target_authority.get("sheet"),
        },
        "sourcePacketActiveFormatStreamControl": {
            "decision": packet_active_format_stream.get("decision", {}).get(
                "sourcePacketActiveFormatStreamControl"
            ),
            "streamModeCount": packet_active_format_stream.get("summary", {}).get(
                "streamModeCount"
            ),
            "sourceAuthorityOrderModeCount": packet_active_format_stream.get(
                "summary", {}
            ).get("sourceAuthorityOrderModeCount"),
            "overdoseProjectionStreamCount": packet_active_format_stream.get(
                "summary", {}
            ).get("overdoseProjectionStreamCount"),
            "strictInstructionHitCount": packet_active_format_stream.get(
                "summary", {}
            ).get("strictInstructionHitCount"),
            "layoutOverStreamCount": packet_active_format_stream.get("summary", {}).get(
                "layoutOverStreamCount"
            ),
            "controlSingleRowOverCount": packet_active_format_stream.get(
                "summary", {}
            ).get("controlSingleRowOverCount"),
            "fullPageYkYkkyCombinationCount": packet_active_format_stream.get(
                "summary", {}
            ).get("fullPageYkYkkyCombinationCount"),
            "selectorPermissionCorrectionCount": packet_active_format_stream.get(
                "summary", {}
            ).get("selectorPermissionCorrectionCount"),
            "sourceBackedR3BridgeHitCount": packet_active_format_stream.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_active_format_stream.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_active_format_stream.get("summary", {}).get(
                "triggerCount"
            ),
            "formatStreamFingerprint": packet_active_format_stream.get("summary", {}).get(
                "formatStreamFingerprint"
            ),
            "sheet": packet_active_format_stream.get("sheet"),
        },
        "sourcePacketActiveIndexSlotControl": {
            "decision": packet_active_index_slot.get("decision", {}).get(
                "sourcePacketActiveIndexSlotControl"
            ),
            "activeTargetCount": packet_active_index_slot.get("summary", {}).get(
                "activeTargetCount"
            ),
            "lineToSlotAffineFitCount": packet_active_index_slot.get("summary", {}).get(
                "lineToSlotAffineFitCount"
            ),
            "corridorToSlotAffineFitCount": packet_active_index_slot.get(
                "summary", {}
            ).get("corridorToSlotAffineFitCount"),
            "lineCorridorToSlotAffineFitCount": packet_active_index_slot.get(
                "summary", {}
            ).get("lineCorridorToSlotAffineFitCount"),
            "lineParityStateStream": packet_active_index_slot.get("summary", {}).get(
                "lineParityStateStream"
            ),
            "slotParityStateStream": packet_active_index_slot.get("summary", {}).get(
                "slotParityStateStream"
            ),
            "slotOrderRotationIndex": packet_active_index_slot.get("summary", {}).get(
                "slotOrderRotationIndex"
            ),
            "slotGapsMod8": packet_active_index_slot.get("summary", {}).get(
                "slotGapsMod8"
            ),
            "fullPageYkYkkyCombinationCount": packet_active_index_slot.get(
                "summary", {}
            ).get("fullPageYkYkkyCombinationCount"),
            "controlSingleRowOverCount": packet_active_index_slot.get("summary", {}).get(
                "controlSingleRowOverCount"
            ),
            "sourceBackedR3BridgeHitCount": packet_active_index_slot.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_active_index_slot.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_active_index_slot.get("summary", {}).get(
                "triggerCount"
            ),
            "indexSlotFingerprint": packet_active_index_slot.get("summary", {}).get(
                "indexSlotFingerprint"
            ),
            "sheet": packet_active_index_slot.get("sheet"),
        },
        "sourcePacketCenterRotationWordControl": {
            "decision": packet_center_rotation_word.get("decision", {}).get(
                "sourcePacketCenterRotationWordControl"
            ),
            "centerStreamRowCount": packet_center_rotation_word.get("summary", {}).get(
                "centerStreamRowCount"
            ),
            "uniqueCenterStreamCount": packet_center_rotation_word.get("summary", {}).get(
                "uniqueCenterStreamCount"
            ),
            "rotationRowCount": packet_center_rotation_word.get("summary", {}).get(
                "rotationRowCount"
            ),
            "thematicHitRowCount": packet_center_rotation_word.get("summary", {}).get(
                "thematicHitRowCount"
            ),
            "uniqueThematicHits": packet_center_rotation_word.get("summary", {}).get(
                "uniqueThematicHits"
            ),
            "doveHitCount": packet_center_rotation_word.get("summary", {}).get(
                "doveHitCount"
            ),
            "sourceStartCueHitCount": packet_center_rotation_word.get("summary", {}).get(
                "sourceStartCueHitCount"
            ),
            "slotOrderRotationIndex": packet_center_rotation_word.get("summary", {}).get(
                "slotOrderRotationIndex"
            ),
            "lineToSlotAffineFitCount": packet_center_rotation_word.get(
                "summary", {}
            ).get("lineToSlotAffineFitCount"),
            "p75ControlMatchesActiveBlackCount": packet_center_rotation_word.get(
                "summary", {}
            ).get("p75ControlMatchesActiveBlackCount"),
            "mirrorVariantCount": packet_center_rotation_word.get("summary", {}).get(
                "mirrorVariantCount"
            ),
            "sourceBackedR3BridgeHitCount": packet_center_rotation_word.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_center_rotation_word.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_center_rotation_word.get("summary", {}).get(
                "triggerCount"
            ),
            "centerRotationFingerprint": packet_center_rotation_word.get(
                "summary", {}
            ).get("centerRotationFingerprint"),
            "sheet": packet_center_rotation_word.get("sheet"),
        },
        "sourcePacketColorSplitSpanControl": {
            "decision": packet_color_split_span.get("decision", {}).get(
                "sourcePacketColorSplitSpanControl"
            ),
            "variantCount": packet_color_split_span.get("summary", {}).get(
                "variantCount"
            ),
            "streamRowCount": packet_color_split_span.get("summary", {}).get(
                "streamRowCount"
            ),
            "layoutHitRowCount": packet_color_split_span.get("summary", {}).get(
                "layoutHitRowCount"
            ),
            "blackLayoutHitRowCount": packet_color_split_span.get("summary", {}).get(
                "blackLayoutHitRowCount"
            ),
            "orangeLayoutHitRowCount": packet_color_split_span.get("summary", {}).get(
                "orangeLayoutHitRowCount"
            ),
            "groupedLayoutHitRowCount": packet_color_split_span.get("summary", {}).get(
                "groupedLayoutHitRowCount"
            ),
            "strictInstructionHitCount": packet_color_split_span.get("summary", {}).get(
                "strictInstructionHitCount"
            ),
            "sourceColorSplitCueHitCount": packet_color_split_span.get(
                "summary", {}
            ).get("sourceColorSplitCueHitCount"),
            "uniqueBlackStreams": packet_color_split_span.get("summary", {}).get(
                "uniqueBlackStreams"
            ),
            "uniqueOrangeStreams": packet_color_split_span.get("summary", {}).get(
                "uniqueOrangeStreams"
            ),
            "p75ControlMatchesActiveBlackCount": packet_color_split_span.get(
                "summary", {}
            ).get("p75ControlMatchesActiveBlackCount"),
            "p75SingleRowOverCount": packet_color_split_span.get("summary", {}).get(
                "p75SingleRowOverCount"
            ),
            "sourceBackedR3BridgeHitCount": packet_color_split_span.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_color_split_span.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_color_split_span.get("summary", {}).get(
                "triggerCount"
            ),
            "colorSplitSpanFingerprint": packet_color_split_span.get(
                "summary", {}
            ).get("colorSplitSpanFingerprint"),
            "sheet": packet_color_split_span.get("sheet"),
        },
        "sourcePacketDominantOverlapSlotControl": {
            "decision": packet_dominant_overlap.get("decision", {}).get(
                "sourcePacketDominantOverlapSlotControl"
            ),
            "variantCount": packet_dominant_overlap.get("summary", {}).get(
                "variantCount"
            ),
            "streamRowCount": packet_dominant_overlap.get("summary", {}).get(
                "streamRowCount"
            ),
            "activeDominantStreamCount": packet_dominant_overlap.get(
                "summary", {}
            ).get("activeDominantStreamCount"),
            "dominantMatchesCenterStreamCount": packet_dominant_overlap.get(
                "summary", {}
            ).get("dominantMatchesCenterStreamCount"),
            "activeDominantCenterMismatchCount": packet_dominant_overlap.get(
                "summary", {}
            ).get("activeDominantCenterMismatchCount"),
            "activeDominantAmbiguousCount": packet_dominant_overlap.get(
                "summary", {}
            ).get("activeDominantAmbiguousCount"),
            "layoutHitRowCount": packet_dominant_overlap.get("summary", {}).get(
                "layoutHitRowCount"
            ),
            "thematicHitRowCount": packet_dominant_overlap.get("summary", {}).get(
                "thematicHitRowCount"
            ),
            "blackDominantStreams": packet_dominant_overlap.get("summary", {}).get(
                "blackDominantStreams"
            ),
            "orangeDominantStreams": packet_dominant_overlap.get("summary", {}).get(
                "orangeDominantStreams"
            ),
            "p75DominantStreams": packet_dominant_overlap.get("summary", {}).get(
                "p75DominantStreams"
            ),
            "sourceDominantCueHitCount": packet_dominant_overlap.get(
                "summary", {}
            ).get("sourceDominantCueHitCount"),
            "sourceBackedR3BridgeHitCount": packet_dominant_overlap.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_dominant_overlap.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_dominant_overlap.get("summary", {}).get(
                "triggerCount"
            ),
            "dominantOverlapFingerprint": packet_dominant_overlap.get(
                "summary", {}
            ).get("dominantOverlapFingerprint"),
            "sheet": packet_dominant_overlap.get("sheet"),
        },
        "sourcePacketSpanEdgeSlotControl": {
            "decision": packet_span_edge_slot.get("decision", {}).get(
                "sourcePacketSpanEdgeSlotControl"
            ),
            "variantCount": packet_span_edge_slot.get("summary", {}).get(
                "variantCount"
            ),
            "streamRowCount": packet_span_edge_slot.get("summary", {}).get(
                "streamRowCount"
            ),
            "activeEdgeStreamCount": packet_span_edge_slot.get("summary", {}).get(
                "activeEdgeStreamCount"
            ),
            "layoutHitRowCount": packet_span_edge_slot.get("summary", {}).get(
                "layoutHitRowCount"
            ),
            "activeLayoutHitRowCount": packet_span_edge_slot.get("summary", {}).get(
                "activeLayoutHitRowCount"
            ),
            "thematicHitRowCount": packet_span_edge_slot.get("summary", {}).get(
                "thematicHitRowCount"
            ),
            "activeThematicHitRowCount": packet_span_edge_slot.get("summary", {}).get(
                "activeThematicHitRowCount"
            ),
            "blackEdgeStreams": packet_span_edge_slot.get("summary", {}).get(
                "blackEdgeStreams"
            ),
            "orangeEdgeStreams": packet_span_edge_slot.get("summary", {}).get(
                "orangeEdgeStreams"
            ),
            "p75EdgeStreams": packet_span_edge_slot.get("summary", {}).get(
                "p75EdgeStreams"
            ),
            "sourceEdgeCueHitCount": packet_span_edge_slot.get("summary", {}).get(
                "sourceEdgeCueHitCount"
            ),
            "sourceBackedR3BridgeHitCount": packet_span_edge_slot.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_span_edge_slot.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_span_edge_slot.get("summary", {}).get(
                "triggerCount"
            ),
            "spanEdgeFingerprint": packet_span_edge_slot.get("summary", {}).get(
                "spanEdgeFingerprint"
            ),
            "sheet": packet_span_edge_slot.get("sheet"),
        },
        "sourcePacketOverlapWidthProfileControl": {
            "decision": packet_overlap_width_profile.get("decision", {}).get(
                "sourcePacketOverlapWidthProfileControl"
            ),
            "variantCount": packet_overlap_width_profile.get("summary", {}).get(
                "variantCount"
            ),
            "streamRowCount": packet_overlap_width_profile.get("summary", {}).get(
                "streamRowCount"
            ),
            "activeProfileStreamCount": packet_overlap_width_profile.get(
                "summary", {}
            ).get("activeProfileStreamCount"),
            "slotWidthReferencePx": packet_overlap_width_profile.get(
                "summary", {}
            ).get("slotWidthReferencePx"),
            "activeSlotCountStreams": packet_overlap_width_profile.get(
                "summary", {}
            ).get("activeSlotCountStreams"),
            "activeFullishCountStreams": packet_overlap_width_profile.get(
                "summary", {}
            ).get("activeFullishCountStreams"),
            "activeDominantPositionStreams": packet_overlap_width_profile.get(
                "summary", {}
            ).get("activeDominantPositionStreams"),
            "activeEdgeBiasStreams": packet_overlap_width_profile.get(
                "summary", {}
            ).get("activeEdgeBiasStreams"),
            "activeSlotCounts": packet_overlap_width_profile.get("summary", {}).get(
                "activeSlotCounts"
            ),
            "p75SlotCounts": packet_overlap_width_profile.get("summary", {}).get(
                "p75SlotCounts"
            ),
            "activeSharesP75SlotCount": packet_overlap_width_profile.get(
                "summary", {}
            ).get("activeSharesP75SlotCount"),
            "sourceWidthProfileCueHitCount": packet_overlap_width_profile.get(
                "summary", {}
            ).get("sourceWidthProfileCueHitCount"),
            "sourceBackedR3BridgeHitCount": packet_overlap_width_profile.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_overlap_width_profile.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_overlap_width_profile.get("summary", {}).get(
                "triggerCount"
            ),
            "overlapWidthFingerprint": packet_overlap_width_profile.get(
                "summary", {}
            ).get("overlapWidthFingerprint"),
            "sheet": packet_overlap_width_profile.get("sheet"),
        },
        "sourcePacketSpanNeighborSlotControl": {
            "decision": packet_span_neighbor_slot.get("decision", {}).get(
                "sourcePacketSpanNeighborSlotControl"
            ),
            "variantCount": packet_span_neighbor_slot.get("summary", {}).get(
                "variantCount"
            ),
            "streamRowCount": packet_span_neighbor_slot.get("summary", {}).get(
                "streamRowCount"
            ),
            "activeNeighborStreamCount": packet_span_neighbor_slot.get(
                "summary", {}
            ).get("activeNeighborStreamCount"),
            "layoutHitRowCount": packet_span_neighbor_slot.get("summary", {}).get(
                "layoutHitRowCount"
            ),
            "activeLayoutHitRowCount": packet_span_neighbor_slot.get(
                "summary", {}
            ).get("activeLayoutHitRowCount"),
            "thematicHitRowCount": packet_span_neighbor_slot.get("summary", {}).get(
                "thematicHitRowCount"
            ),
            "activeThematicHitRowCount": packet_span_neighbor_slot.get(
                "summary", {}
            ).get("activeThematicHitRowCount"),
            "blackNeighborStreams": packet_span_neighbor_slot.get("summary", {}).get(
                "blackNeighborStreams"
            ),
            "orangeNeighborStreams": packet_span_neighbor_slot.get("summary", {}).get(
                "orangeNeighborStreams"
            ),
            "p75NeighborStreams": packet_span_neighbor_slot.get("summary", {}).get(
                "p75NeighborStreams"
            ),
            "activeBoundaryMissingCount": packet_span_neighbor_slot.get(
                "summary", {}
            ).get("activeBoundaryMissingCount"),
            "sourceNeighborCueHitCount": packet_span_neighbor_slot.get(
                "summary", {}
            ).get("sourceNeighborCueHitCount"),
            "sourceBackedR3BridgeHitCount": packet_span_neighbor_slot.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_span_neighbor_slot.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_span_neighbor_slot.get("summary", {}).get(
                "triggerCount"
            ),
            "spanNeighborFingerprint": packet_span_neighbor_slot.get(
                "summary", {}
            ).get("spanNeighborFingerprint"),
            "sheet": packet_span_neighbor_slot.get("sheet"),
        },
        "sourcePacketSpanComplementSlotControl": {
            "decision": packet_span_complement_slot.get("decision", {}).get(
                "sourcePacketSpanComplementSlotControl"
            ),
            "variantCount": packet_span_complement_slot.get("summary", {}).get(
                "variantCount"
            ),
            "streamRowCount": packet_span_complement_slot.get("summary", {}).get(
                "streamRowCount"
            ),
            "activeComplementStreamCount": packet_span_complement_slot.get(
                "summary", {}
            ).get("activeComplementStreamCount"),
            "layoutHitRowCount": packet_span_complement_slot.get("summary", {}).get(
                "layoutHitRowCount"
            ),
            "activeLayoutHitRowCount": packet_span_complement_slot.get(
                "summary", {}
            ).get("activeLayoutHitRowCount"),
            "p75LayoutHitRowCount": packet_span_complement_slot.get(
                "summary", {}
            ).get("p75LayoutHitRowCount"),
            "thematicHitRowCount": packet_span_complement_slot.get("summary", {}).get(
                "thematicHitRowCount"
            ),
            "activeThematicHitRowCount": packet_span_complement_slot.get(
                "summary", {}
            ).get("activeThematicHitRowCount"),
            "blackComplementStreams": packet_span_complement_slot.get(
                "summary", {}
            ).get("blackComplementStreams"),
            "orangeComplementStreams": packet_span_complement_slot.get(
                "summary", {}
            ).get("orangeComplementStreams"),
            "p75ComplementStreams": packet_span_complement_slot.get("summary", {}).get(
                "p75ComplementStreams"
            ),
            "activeComplementSlotCountStreams": packet_span_complement_slot.get(
                "summary", {}
            ).get("activeComplementSlotCountStreams"),
            "sourceComplementCueHitCount": packet_span_complement_slot.get(
                "summary", {}
            ).get("sourceComplementCueHitCount"),
            "sourceBackedR3BridgeHitCount": packet_span_complement_slot.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_span_complement_slot.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_span_complement_slot.get("summary", {}).get(
                "triggerCount"
            ),
            "spanComplementFingerprint": packet_span_complement_slot.get(
                "summary", {}
            ).get("spanComplementFingerprint"),
            "sheet": packet_span_complement_slot.get("sheet"),
        },
        "sourcePacketLocalAssetOrientationGate": {
            "decision": packet_local_asset_orientation.get("decision", {}).get(
                "sourcePacketLocalAssetOrientationGate"
            ),
            "imageCandidateCount": packet_local_asset_orientation.get(
                "summary", {}
            ).get("imageCandidateCount"),
            "pdfCandidateCount": packet_local_asset_orientation.get(
                "summary", {}
            ).get("pdfCandidateCount"),
            "page76MatchCount": packet_local_asset_orientation.get("summary", {}).get(
                "page76MatchCount"
            ),
            "derivativePage76MatchCount": packet_local_asset_orientation.get(
                "summary", {}
            ).get("derivativePage76MatchCount"),
            "exactCurrentScanMatchCount": packet_local_asset_orientation.get(
                "summary", {}
            ).get("exactCurrentScanMatchCount"),
            "higherResolutionPage76Count": packet_local_asset_orientation.get(
                "summary", {}
            ).get("higherResolutionPage76Count"),
            "r1DistinctImprovedCount": packet_local_asset_orientation.get(
                "summary", {}
            ).get("r1DistinctImprovedCount"),
            "sourceBackedR3BridgeHitCount": packet_local_asset_orientation.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_local_asset_orientation.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_local_asset_orientation.get("summary", {}).get(
                "triggerCount"
            ),
            "localAssetOrientationFingerprint": packet_local_asset_orientation.get(
                "summary", {}
            ).get("localAssetOrientationFingerprint"),
            "sheet": packet_local_asset_orientation.get("sheet"),
        },
        "sourcePacketPdfRenderQualityGate": {
            "decision": packet_pdf_render_quality.get("decision", {}).get(
                "sourcePacketPdfRenderQualityGate"
            ),
            "pdfCandidateCount": packet_pdf_render_quality.get("summary", {}).get(
                "pdfCandidateCount"
            ),
            "renderedPageCount": packet_pdf_render_quality.get("summary", {}).get(
                "renderedPageCount"
            ),
            "embeddedImageCount": packet_pdf_render_quality.get("summary", {}).get(
                "embeddedImageCount"
            ),
            "page76RenderMatchCount": packet_pdf_render_quality.get("summary", {}).get(
                "page76RenderMatchCount"
            ),
            "page76EmbeddedMatchCount": packet_pdf_render_quality.get("summary", {}).get(
                "page76EmbeddedMatchCount"
            ),
            "uniquePage76PdfPageCount": packet_pdf_render_quality.get("summary", {}).get(
                "uniquePage76PdfPageCount"
            ),
            "higherResolutionPage76RenderCount": packet_pdf_render_quality.get(
                "summary", {}
            ).get("higherResolutionPage76RenderCount"),
            "higherResolutionPage76EmbeddedCount": packet_pdf_render_quality.get(
                "summary", {}
            ).get("higherResolutionPage76EmbeddedCount"),
            "r1DistinctImprovedPdfCandidateCount": packet_pdf_render_quality.get(
                "summary", {}
            ).get("r1DistinctImprovedPdfCandidateCount"),
            "sourceBackedR3BridgeHitCount": packet_pdf_render_quality.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_pdf_render_quality.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_pdf_render_quality.get("summary", {}).get(
                "triggerCount"
            ),
            "pdfRenderQualityFingerprint": packet_pdf_render_quality.get(
                "summary", {}
            ).get("pdfRenderQualityFingerprint"),
            "sheet": packet_pdf_render_quality.get("sheet"),
        },
        "currentScanHeldToLightSimulator": {
            "decision": current_scan_held_to_light.get("decision", {}).get(
                "currentScanHeldToLightSimulator"
            ),
            "pairCount": current_scan_held_to_light.get("summary", {}).get(
                "pairCount"
            ),
            "modeRowCount": current_scan_held_to_light.get("summary", {}).get(
                "modeRowCount"
            ),
            "naturalSameLeaf75To76ActiveOverTarget": current_scan_held_to_light.get(
                "summary", {}
            ).get("naturalSameLeaf75To76ActiveOverTarget"),
            "bestSameLeaf75To76ActiveOverTarget": current_scan_held_to_light.get(
                "summary", {}
            ).get("bestSameLeaf75To76ActiveOverTarget"),
            "bestSameLeaf75To76Shift": current_scan_held_to_light.get(
                "summary", {}
            ).get("bestSameLeaf75To76Shift"),
            "bestPage76ActivePair": current_scan_held_to_light.get(
                "summary", {}
            ).get("bestPage76ActivePair"),
            "bestPage76ActiveMode": current_scan_held_to_light.get(
                "summary", {}
            ).get("bestPage76ActiveMode"),
            "bestPage76ActiveOverTarget": current_scan_held_to_light.get(
                "summary", {}
            ).get("bestPage76ActiveOverTarget"),
            "bestPage76ActiveShift": current_scan_held_to_light.get(
                "summary", {}
            ).get("bestPage76ActiveShift"),
            "bestGlobalPair": current_scan_held_to_light.get("summary", {}).get(
                "bestGlobalPair"
            ),
            "bestGlobalBalanced": current_scan_held_to_light.get("summary", {}).get(
                "bestGlobalBalanced"
            ),
            "sourceBackedR3BridgeHitCount": current_scan_held_to_light.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_held_to_light.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_held_to_light.get("summary", {}).get(
                "triggerCount"
            ),
            "heldToLightSimulatorFingerprint": current_scan_held_to_light.get(
                "summary", {}
            ).get("heldToLightSimulatorFingerprint"),
            "sheet": current_scan_held_to_light.get("sheet"),
            "htmlSimulator": current_scan_held_to_light.get("htmlSimulator"),
        },
        "currentScanHeldToLightActiveBoxBalanceGate": {
            "decision": current_scan_held_to_light_active_balance.get("decision"),
            "activeRowCount": current_scan_held_to_light_active_balance.get("summary", {}).get("activeRowCount"),
            "physicalNaturalSelectorCandidateCount": current_scan_held_to_light_active_balance.get("summary", {}).get("physicalNaturalSelectorCandidateCount"),
            "sameLeaf75To76All4Ge10Count": current_scan_held_to_light_active_balance.get("summary", {}).get("sameLeaf75To76All4Ge10Count"),
            "sameLeaf75To76All4Ge25Count": current_scan_held_to_light_active_balance.get("summary", {}).get("sameLeaf75To76All4Ge25Count"),
            "nonphysicalAll4Ge10Count": current_scan_held_to_light_active_balance.get("summary", {}).get("nonphysicalAll4Ge10Count"),
            "nonphysicalAll4Ge25Count": current_scan_held_to_light_active_balance.get("summary", {}).get("nonphysicalAll4Ge25Count"),
            "bestPhysicalNaturalMinCoverage": current_scan_held_to_light_active_balance.get("summary", {}).get("bestPhysicalNaturalMinCoverage"),
            "bestSameLeaf75To76MinCoverage": current_scan_held_to_light_active_balance.get("summary", {}).get("bestSameLeaf75To76MinCoverage"),
            "bestSameLeaf75To76Row": current_scan_held_to_light_active_balance.get("summary", {}).get("bestSameLeaf75To76Row"),
            "bestNonphysicalMinCoverage": current_scan_held_to_light_active_balance.get("summary", {}).get("bestNonphysicalMinCoverage"),
            "bestNonphysicalRow": current_scan_held_to_light_active_balance.get("summary", {}).get("bestNonphysicalRow"),
            "sourceBackedR3BridgeHitCount": current_scan_held_to_light_active_balance.get("summary", {}).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_held_to_light_active_balance.get("summary", {}).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_held_to_light_active_balance.get("summary", {}).get("triggerCount"),
            "fingerprint": current_scan_held_to_light_active_balance.get("fingerprint"),
            "sheet": current_scan_held_to_light_active_balance.get("sheet"),
        },
        "currentScanHeldToLightComponentReadabilityGate": {
            "decision": current_scan_held_to_light_component_readability.get(
                "decision", {}
            ).get("currentScanHeldToLightComponentReadabilityGate"),
            "modeCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("modeCount"),
            "targetRowCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("targetRowCount"),
            "naturalReadableRowCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("naturalReadableRowCount"),
            "forcedReadableRowCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("forcedReadableRowCount"),
            "allFourReadableModeCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("allFourReadableModeCount"),
            "strictInstructionRowCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("strictInstructionRowCount"),
            "sourceWordRowCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("sourceWordRowCount"),
            "hiddenReadabilityCandidateCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("hiddenReadabilityCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("triggerCount"),
            "componentReadabilityFingerprint": current_scan_held_to_light_component_readability.get(
                "summary", {}
            ).get("componentReadabilityFingerprint"),
            "sheet": current_scan_held_to_light_component_readability.get("sheet"),
        },
        "currentScanHeldToLightOpacityGate": {
            "decision": current_scan_held_to_light_opacity.get("decision", {}).get(
                "currentScanHeldToLightOpacityGate"
            ),
            "scenarioCount": current_scan_held_to_light_opacity.get("summary", {}).get(
                "scenarioCount"
            ),
            "blendRowCount": current_scan_held_to_light_opacity.get("summary", {}).get(
                "blendRowCount"
            ),
            "activeBoxBlendRowCount": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("activeBoxBlendRowCount"),
            "bestNaturalMinActiveDarkeningDelta": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("bestNaturalMinActiveDarkeningDelta"),
            "bestNaturalBlend": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("bestNaturalBlend"),
            "bestForcedOrControlMinActiveDarkeningDelta": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("bestForcedOrControlMinActiveDarkeningDelta"),
            "bestForcedOrControlScenario": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("bestForcedOrControlScenario"),
            "bestForcedOrControlBlend": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("bestForcedOrControlBlend"),
            "naturalAllFourDelta16Count": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("naturalAllFourDelta16Count"),
            "forcedOrControlAllFourDelta16Count": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("forcedOrControlAllFourDelta16Count"),
            "expectedStateStreamMatchCount": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("expectedStateStreamMatchCount"),
            "sourceBackedR3BridgeHitCount": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_held_to_light_opacity.get("summary", {}).get(
                "triggerCount"
            ),
            "heldToLightOpacityFingerprint": current_scan_held_to_light_opacity.get(
                "summary", {}
            ).get("heldToLightOpacityFingerprint"),
            "sheet": current_scan_held_to_light_opacity.get("sheet"),
        },
        "currentScanLightTableBlendModeGate": {
            "decision": current_scan_light_table_blend_mode.get("decision", {}).get(
                "currentScanLightTableBlendModeGate"
            ),
            "scenarioCount": current_scan_light_table_blend_mode.get("summary", {}).get(
                "scenarioCount"
            ),
            "blendModeCount": current_scan_light_table_blend_mode.get("summary", {}).get(
                "blendModeCount"
            ),
            "alphaCount": current_scan_light_table_blend_mode.get("summary", {}).get(
                "alphaCount"
            ),
            "blendRowCount": current_scan_light_table_blend_mode.get("summary", {}).get(
                "blendRowCount"
            ),
            "controlBoxCount": current_scan_light_table_blend_mode.get("summary", {}).get(
                "controlBoxCount"
            ),
            "bestNaturalActiveOutlierCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("bestNaturalActiveOutlierCount"),
            "bestNaturalSourceSupportedOutlierCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("bestNaturalSourceSupportedOutlierCount"),
            "bestNaturalBlend": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("bestNaturalBlend"),
            "bestNaturalMinActiveMinusMatchedControlP95": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("bestNaturalMinActiveMinusMatchedControlP95"),
            "bestForcedOrControlActiveOutlierCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("bestForcedOrControlActiveOutlierCount"),
            "bestForcedOrControlSourceSupportedOutlierCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("bestForcedOrControlSourceSupportedOutlierCount"),
            "bestForcedOrControlScenario": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("bestForcedOrControlScenario"),
            "bestForcedOrControlBlend": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("bestForcedOrControlBlend"),
            "naturalAllFourActiveOutlierCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("naturalAllFourActiveOutlierCount"),
            "forcedOrControlAllFourActiveOutlierCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("forcedOrControlAllFourActiveOutlierCount"),
            "naturalAllFourSourceSupportedOutlierCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("naturalAllFourSourceSupportedOutlierCount"),
            "forcedOrControlAllFourSourceSupportedOutlierCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("forcedOrControlAllFourSourceSupportedOutlierCount"),
            "selectorCandidateBeforeR3Count": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("selectorCandidateBeforeR3Count"),
            "sourceBackedR3BridgeHitCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_light_table_blend_mode.get("summary", {}).get(
                "triggerCount"
            ),
            "lightTableBlendModeFingerprint": current_scan_light_table_blend_mode.get(
                "summary", {}
            ).get("lightTableBlendModeFingerprint"),
            "sheet": current_scan_light_table_blend_mode.get("sheet"),
        },
        "currentScanValidLeafSourceInkLandingGate": {
            "decision": current_scan_valid_leaf_source_ink_landing.get("decision", {}).get(
                "currentScanValidLeafSourceInkLandingGate"
            ),
            "scenarioId": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("scenarioId"),
            "targetCount": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("targetCount"),
            "controlBoxCount": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("controlBoxCount"),
            "activeSourceSupportedTargets": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("activeSourceSupportedTargets"),
            "weakSourceSupportedTargets": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("weakSourceSupportedTargets"),
            "zeroSourceInkTargets": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("zeroSourceInkTargets"),
            "activeSourceSupportedCount": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("activeSourceSupportedCount"),
            "weakActiveSourceSupportedCount": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("weakActiveSourceSupportedCount"),
            "allFourSourceSupported": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("allFourSourceSupported"),
            "allFourWeakSourceSupported": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("allFourWeakSourceSupported"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("triggerCount"),
            "sourceInkLandingFingerprint": current_scan_valid_leaf_source_ink_landing.get(
                "summary", {}
            ).get("sourceInkLandingFingerprint"),
            "overlay": current_scan_valid_leaf_source_ink_landing.get("overlay"),
            "sheet": current_scan_valid_leaf_source_ink_landing.get("sheet"),
        },
        "currentScanAllLeafLightTableParityGate": {
            "decision": current_scan_all_leaf_light_table_parity.get(
                "decision", {}
            ).get("currentScanAllLeafLightTableParityGate"),
            "validLeafPairCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("validLeafPairCount"),
            "activeRegionCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("activeRegionCount"),
            "lineShiftControlRegionCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("lineShiftControlRegionCount"),
            "slotRegionCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("slotRegionCount"),
            "page76ActiveInkOutlierCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("page76ActiveInkOutlierCount"),
            "page76ActiveFeatureOutlierCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("page76ActiveFeatureOutlierCount"),
            "allFourPage76InkOutlier": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("allFourPage76InkOutlier"),
            "allFourPage76FeatureOutlier": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("allFourPage76FeatureOutlier"),
            "page76SlotInkOutlierCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("page76SlotInkOutlierCount"),
            "page76SlotFeatureOutlierCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("page76SlotFeatureOutlierCount"),
            "hiddenAllLeafLightTableCandidate": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("hiddenAllLeafLightTableCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("triggerCount"),
            "allLeafLightTableParityFingerprint": current_scan_all_leaf_light_table_parity.get(
                "summary", {}
            ).get("allLeafLightTableParityFingerprint"),
            "sheet": current_scan_all_leaf_light_table_parity.get("sheet"),
        },
        "currentScanLightTableDensityCalibrationGate": {
            "decision": current_scan_light_table_density_calibration.get(
                "decision", {}
            ).get("currentScanLightTableDensityCalibrationGate"),
            "validLeafPairCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("validLeafPairCount"),
            "activeRegionCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("activeRegionCount"),
            "lineShiftControlRegionCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("lineShiftControlRegionCount"),
            "slotRegionCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("slotRegionCount"),
            "page76NormalizedInkOutlierCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("page76NormalizedInkOutlierCount"),
            "page76NormalizedFeatureOutlierCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("page76NormalizedFeatureOutlierCount"),
            "allFourPage76NormalizedInkOutlier": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("allFourPage76NormalizedInkOutlier"),
            "allFourPage76NormalizedFeatureOutlier": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("allFourPage76NormalizedFeatureOutlier"),
            "page76SlotNormalizedInkOutlierCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("page76SlotNormalizedInkOutlierCount"),
            "hiddenDensityCalibratedCandidate": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("hiddenDensityCalibratedCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("triggerCount"),
            "densityCalibrationFingerprint": current_scan_light_table_density_calibration.get(
                "summary", {}
            ).get("densityCalibrationFingerprint"),
            "sheet": current_scan_light_table_density_calibration.get("sheet"),
        },
        "currentScanOverdoseDensityOutlierProvenanceGate": {
            "decision": current_scan_overdose_density_outlier_provenance.get(
                "decision", {}
            ).get("currentScanOverdoseDensityOutlierProvenanceGate"),
            "slotCount": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("slotCount"),
            "page76DensityOutlierSlotCount": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("page76DensityOutlierSlotCount"),
            "outlierSlotIds": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("outlierSlotIds"),
            "outlierLettersXOrder": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("outlierLettersXOrder"),
            "outlierLettersByInkStrength": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("outlierLettersByInkStrength"),
            "outlierLongestContiguousRun": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("outlierLongestContiguousRun"),
            "outlierActiveContactLabels": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("outlierActiveContactLabels"),
            "outlierAllFourActiveContacts": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("outlierAllFourActiveContacts"),
            "outlierB4Contact": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("outlierB4Contact"),
            "outlierInstructionHitCount": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("outlierInstructionHitCount"),
            "hiddenOutlierProvenanceCandidate": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("hiddenOutlierProvenanceCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("triggerCount"),
            "outlierProvenanceFingerprint": current_scan_overdose_density_outlier_provenance.get(
                "summary", {}
            ).get("outlierProvenanceFingerprint"),
            "sheet": current_scan_overdose_density_outlier_provenance.get("sheet"),
        },
        "currentScanOverdoseDensityHighlightAblationGate": {
            "decision": current_scan_overdose_density_highlight_ablation.get(
                "decision", {}
            ).get("currentScanOverdoseDensityHighlightAblationGate"),
            "slotCount": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("slotCount"),
            "baselineOutlierSlotCount": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("baselineOutlierSlotCount"),
            "baselineOutlierLetters": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("baselineOutlierLetters"),
            "outlierSourceHighlightIds": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("outlierSourceHighlightIds"),
            "outlierSurvivorCountAfterOutlierHighlightAblation": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("outlierSurvivorCountAfterOutlierHighlightAblation"),
            "outlierSurvivorLettersAfterOutlierHighlightAblation": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("outlierSurvivorLettersAfterOutlierHighlightAblation"),
            "outlierSurvivorCountAfterAllHighlightAblation": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("outlierSurvivorCountAfterAllHighlightAblation"),
            "meanOutlierHighlightAblationDropPct": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("meanOutlierHighlightAblationDropPct"),
            "nonOutlierHighlightControlFlipCount": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("nonOutlierHighlightControlFlipCount"),
            "hiddenHighlightAblationCandidate": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("hiddenHighlightAblationCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("triggerCount"),
            "highlightAblationFingerprint": current_scan_overdose_density_highlight_ablation.get(
                "summary", {}
            ).get("highlightAblationFingerprint"),
            "sheet": current_scan_overdose_density_highlight_ablation.get("sheet"),
        },
        "currentScanActiveSourceHighlightAblationGate": {
            "decision": current_scan_active_source_highlight_ablation.get(
                "decision", {}
            ).get("currentScanActiveSourceHighlightAblationGate"),
            "activeTargetCount": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("activeTargetCount"),
            "baselinePositiveTargets": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("baselinePositiveTargets"),
            "allHighlightAblationPositiveTargets": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("allHighlightAblationPositiveTargets"),
            "baselineAllFourPositive": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("baselineAllFourPositive"),
            "allHighlightAblationAllFourPositive": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("allHighlightAblationAllFourPositive"),
            "b4InkBaseline": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("b4InkBaseline"),
            "b4InkAfterAllHighlightAblation": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("b4InkAfterAllHighlightAblation"),
            "meanActiveAllHighlightDropPct": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("meanActiveAllHighlightDropPct"),
            "controlPositiveBeforeAllHighlightAblation": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("controlPositiveBeforeAllHighlightAblation"),
            "controlPositiveAfterAllHighlightAblation": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("controlPositiveAfterAllHighlightAblation"),
            "hiddenActiveHighlightAblationCandidate": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("hiddenActiveHighlightAblationCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("triggerCount"),
            "activeSourceHighlightAblationFingerprint": current_scan_active_source_highlight_ablation.get(
                "summary", {}
            ).get("activeSourceHighlightAblationFingerprint"),
            "sheet": current_scan_active_source_highlight_ablation.get("sheet"),
        },
        "currentScanPhysicalBleedthroughCorrelationGate": {
            "decision": current_scan_physical_bleedthrough_correlation.get(
                "decision", {}
            ).get("currentScanPhysicalBleedthroughCorrelationGate"),
            "validLeafPairCount": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("validLeafPairCount"),
            "invalidControlPairCount": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("invalidControlPairCount"),
            "validPairsAboveTargetInvalidP95Count": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("validPairsAboveTargetInvalidP95Count"),
            "page76ValidDarknessDelta": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("page76ValidDarknessDelta"),
            "page76InvalidControlP95Delta": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("page76InvalidControlP95Delta"),
            "page76ActiveBoxesAboveInvalidP95Count": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("page76ActiveBoxesAboveInvalidP95Count"),
            "page76ActiveBoxesWithEnoughSourceSignalCount": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("page76ActiveBoxesWithEnoughSourceSignalCount"),
            "page76AllFourActiveBoxesAboveInvalidP95": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("page76AllFourActiveBoxesAboveInvalidP95"),
            "medianValidDarknessDelta": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("medianValidDarknessDelta"),
            "medianInvalidControlDarknessDelta": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("medianInvalidControlDarknessDelta"),
            "maxValidDarknessDelta": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("maxValidDarknessDelta"),
            "maxInvalidControlDarknessDelta": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("maxInvalidControlDarknessDelta"),
            "hiddenPhysicalBleedthroughCandidate": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("hiddenPhysicalBleedthroughCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("triggerCount"),
            "physicalBleedthroughCorrelationFingerprint": current_scan_physical_bleedthrough_correlation.get(
                "summary", {}
            ).get("physicalBleedthroughCorrelationFingerprint"),
            "sheet": current_scan_physical_bleedthrough_correlation.get("sheet"),
        },
        "currentScanActiveQuartetFingerprintSpecificityGate": {
            "decision": current_scan_active_quartet_fingerprint_specificity.get(
                "decision", {}
            ).get("currentScanActiveQuartetFingerprintSpecificityGate"),
            "candidateRowCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("candidateRowCount"),
            "quartetCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("quartetCount"),
            "stateColorHitCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("stateColorHitCount"),
            "stateColorLineGapHitCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("stateColorLineGapHitCount"),
            "slotStreamHitCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("slotStreamHitCount"),
            "combinedFingerprintHitCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("combinedFingerprintHitCount"),
            "combinedNonActiveHitCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("combinedNonActiveHitCount"),
            "hiddenCurrentScanFingerprintCandidate": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("hiddenCurrentScanFingerprintCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("triggerCount"),
            "specificityFingerprint": current_scan_active_quartet_fingerprint_specificity.get(
                "summary", {}
            ).get("specificityFingerprint"),
            "sheet": current_scan_active_quartet_fingerprint_specificity.get("sheet"),
        },
        "currentScanTargetWitnessBoxSubstitutionGate": {
            "decision": current_scan_target_witness_box_substitution.get(
                "decision", {}
            ).get("currentScanTargetWitnessBoxSubstitutionGate"),
            "geometryVariantCount": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("geometryVariantCount"),
            "perTargetOptionCounts": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("perTargetOptionCounts"),
            "lineGapHitCount": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("lineGapHitCount"),
            "slotStreamHitCount": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("slotStreamHitCount"),
            "lineGapAndSlotHitCount": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("lineGapAndSlotHitCount"),
            "combinedFingerprintHitCount": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("combinedFingerprintHitCount"),
            "combinedSubstitutedHitCount": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("combinedSubstitutedHitCount"),
            "sourceBackedR3BridgeHitCount": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("triggerCount"),
            "witnessBoxSubstitutionFingerprint": current_scan_target_witness_box_substitution.get(
                "summary", {}
            ).get("witnessBoxSubstitutionFingerprint"),
            "sheet": current_scan_target_witness_box_substitution.get("sheet"),
        },
        "currentScanPage76ImageWitnessStateStabilityGate": {
            "decision": current_scan_page76_image_witness_state_stability.get(
                "decision", {}
            ).get("currentScanPage76ImageWitnessStateStabilityGate"),
            "candidateImageCount": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("candidateImageCount"),
            "exactPage76WitnessCount": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("exactPage76WitnessCount"),
            "stableExactWitnessCount": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("stableExactWitnessCount"),
            "nearPage76ControlCount": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("nearPage76ControlCount"),
            "hiddenChangedStateWitnessCandidateCount": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("hiddenChangedStateWitnessCandidateCount"),
            "exactPage76WitnessPaths": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("exactPage76WitnessPaths"),
            "exactWitnessMaxActiveCropMeanAbsDiff": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("exactWitnessMaxActiveCropMeanAbsDiff"),
            "sourceBackedR3BridgeHitCount": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("triggerCount"),
            "page76ImageWitnessStateFingerprint": current_scan_page76_image_witness_state_stability.get(
                "summary", {}
            ).get("page76ImageWitnessStateFingerprint"),
            "sheet": current_scan_page76_image_witness_state_stability.get("sheet"),
        },
        "currentScanPage76ImageWitnessMicroregistrationGate": {
            "decision": current_scan_page76_image_witness_microregistration.get(
                "decision", {}
            ).get("currentScanPage76ImageWitnessMicroregistrationGate"),
            "exactPage76WitnessCount": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("exactPage76WitnessCount"),
            "targetShiftRowCount": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("targetShiftRowCount"),
            "searchRadiusPx": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("searchRadiusPx"),
            "nonZeroBestShiftCount": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("nonZeroBestShiftCount"),
            "maxAbsBestShiftPx": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("maxAbsBestShiftPx"),
            "maxZeroShiftMeanAbsDiff": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("maxZeroShiftMeanAbsDiff"),
            "maxZeroToBestImprovement": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("maxZeroToBestImprovement"),
            "sourceBackedR3BridgeHitCount": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("triggerCount"),
            "microregistrationFingerprint": current_scan_page76_image_witness_microregistration.get(
                "summary", {}
            ).get("microregistrationFingerprint"),
            "sheet": current_scan_page76_image_witness_microregistration.get("sheet"),
        },
        "currentScanActiveBoxOverdoseEdgeResidueGate": {
            "decision": current_scan_active_box_overdose_edge_residue.get(
                "decision", {}
            ).get("currentScanActiveBoxOverdoseEdgeResidueGate"),
            "variantCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("variantCount"),
            "exactActiveCenterStream": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("exactActiveCenterStream"),
            "exactActiveLeftCenterStream": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("exactActiveLeftCenterStream"),
            "exactActiveRightCenterStream": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("exactActiveRightCenterStream"),
            "exactActiveAnyAnchorClose16RowCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("exactActiveAnyAnchorClose16RowCount"),
            "exactActiveLeftBoundaryClose16RowCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("exactActiveLeftBoundaryClose16RowCount"),
            "exactActiveCenterSlotClose16RowCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("exactActiveCenterSlotClose16RowCount"),
            "exactActiveRightBoundaryClose16RowCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("exactActiveRightBoundaryClose16RowCount"),
            "allFourAnyAnchorClose16VariantCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("allFourAnyAnchorClose16VariantCount"),
            "substitutedAllFourAnyAnchorClose16VariantCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("substitutedAllFourAnyAnchorClose16VariantCount"),
            "bestMeanNearestResidueVariantOrdinal": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("bestMeanNearestResidueVariantOrdinal"),
            "bestMeanNearestResiduePx": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("bestMeanNearestResiduePx"),
            "sourceBackedR3BridgeHitCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("triggerCount"),
            "edgeResidueFingerprint": current_scan_active_box_overdose_edge_residue.get(
                "summary", {}
            ).get("edgeResidueFingerprint"),
            "sheet": current_scan_active_box_overdose_edge_residue.get("sheet"),
        },
        "currentScanValidLeafJitterSourceInkRescueGate": {
            "decision": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "decision", {}
            ).get("currentScanValidLeafJitterSourceInkRescueGate"),
            "credibleShiftLimitPx": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("credibleShiftLimitPx"),
            "extendedGuardrailShiftLimitPx": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("extendedGuardrailShiftLimitPx"),
            "credibleShiftRowCount": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("credibleShiftRowCount"),
            "extendedShiftRowCount": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("extendedShiftRowCount"),
            "credibleAllFourSourceSupportedCount": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("credibleAllFourSourceSupportedCount"),
            "extendedAllFourSourceSupportedCount": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("extendedAllFourSourceSupportedCount"),
            "credibleB4PositiveShiftCount": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("credibleB4PositiveShiftCount"),
            "extendedB4PositiveShiftCount": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("extendedB4PositiveShiftCount"),
            "bestCredibleShift": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("bestCredibleShift"),
            "bestExtendedShift": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("bestExtendedShift"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("triggerCount"),
            "jitterSourceInkRescueFingerprint": current_scan_valid_leaf_jitter_source_ink_rescue.get(
                "summary", {}
            ).get("jitterSourceInkRescueFingerprint"),
            "overlay": current_scan_valid_leaf_jitter_source_ink_rescue.get("overlay"),
            "sheet": current_scan_valid_leaf_jitter_source_ink_rescue.get("sheet"),
        },
        "currentScanPageFrameTrimRegistrationGate": {
            "decision": current_scan_page_frame_trim_registration.get(
                "decision", {}
            ).get("currentScanPageFrameTrimRegistrationGate"),
            "pageCount": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("pageCount"),
            "pagesChecked": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("pagesChecked"),
            "validPair": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("validPair"),
            "sameCanvasValidPair": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("sameCanvasValidPair"),
            "allEdgesFrameLikePageCount": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("allEdgesFrameLikePageCount"),
            "validPairBothPagesAllEdgesFrameLike": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("validPairBothPagesAllEdgesFrameLike"),
            "trimCorrectionCandidate": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("trimCorrectionCandidate"),
            "hiddenTrimSkewCandidate": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("hiddenTrimSkewCandidate"),
            "activeDistanceRowCount": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("activeDistanceRowCount"),
            "sourceBackedR3BridgeHitCount": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("triggerCount"),
            "pageFrameTrimFingerprint": current_scan_page_frame_trim_registration.get(
                "summary", {}
            ).get("pageFrameTrimFingerprint"),
            "sheet": current_scan_page_frame_trim_registration.get("sheet"),
        },
        "currentScanContentBoxRegistrationGate": {
            "decision": current_scan_content_box_registration.get(
                "decision", {}
            ).get("currentScanContentBoxRegistrationGate"),
            "pageCount": current_scan_content_box_registration.get(
                "summary", {}
            ).get("pageCount"),
            "pagesChecked": current_scan_content_box_registration.get(
                "summary", {}
            ).get("pagesChecked"),
            "validPair": current_scan_content_box_registration.get(
                "summary", {}
            ).get("validPair"),
            "sameCanvasValidPair": current_scan_content_box_registration.get(
                "summary", {}
            ).get("sameCanvasValidPair"),
            "validPairAllContentShift": current_scan_content_box_registration.get(
                "summary", {}
            ).get("validPairAllContentShift"),
            "validPairLowerHalfShift": current_scan_content_box_registration.get(
                "summary", {}
            ).get("validPairLowerHalfShift"),
            "allContentShiftStable": current_scan_content_box_registration.get(
                "summary", {}
            ).get("allContentShiftStable"),
            "lowerHalfContentShiftStable": current_scan_content_box_registration.get(
                "summary", {}
            ).get("lowerHalfContentShiftStable"),
            "lowerHalfBoxesClippedToCanvasOrBand": current_scan_content_box_registration.get(
                "summary", {}
            ).get("lowerHalfBoxesClippedToCanvasOrBand"),
            "contentBoxRegistrationCandidate": current_scan_content_box_registration.get(
                "summary", {}
            ).get("contentBoxRegistrationCandidate"),
            "hiddenContentBoxCandidate": current_scan_content_box_registration.get(
                "summary", {}
            ).get("hiddenContentBoxCandidate"),
            "bestLandingModeId": current_scan_content_box_registration.get(
                "summary", {}
            ).get("bestLandingModeId"),
            "bestLandingSupportedCount": current_scan_content_box_registration.get(
                "summary", {}
            ).get("bestLandingSupportedCount"),
            "b4BestSourceInkRatio": current_scan_content_box_registration.get(
                "summary", {}
            ).get("b4BestSourceInkRatio"),
            "sourceBackedR3BridgeHitCount": current_scan_content_box_registration.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_content_box_registration.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_content_box_registration.get(
                "summary", {}
            ).get("triggerCount"),
            "contentBoxRegistrationFingerprint": current_scan_content_box_registration.get(
                "summary", {}
            ).get("contentBoxRegistrationFingerprint"),
            "sheet": current_scan_content_box_registration.get("sheet"),
        },
        "currentScanSourceLayerLandingGate": {
            "decision": current_scan_source_layer_landing.get("decision", {}).get(
                "currentScanSourceLayerLandingGate"
            ),
            "modeCount": current_scan_source_layer_landing.get("summary", {}).get(
                "modeCount"
            ),
            "layersChecked": current_scan_source_layer_landing.get("summary", {}).get(
                "layersChecked"
            ),
            "activeLayerRowCount": current_scan_source_layer_landing.get(
                "summary", {}
            ).get("activeLayerRowCount"),
            "b4PositiveLayerModeCount": current_scan_source_layer_landing.get(
                "summary", {}
            ).get("b4PositiveLayerModeCount"),
            "allFourSupportedLayerModeCount": current_scan_source_layer_landing.get(
                "summary", {}
            ).get("allFourSupportedLayerModeCount"),
            "allFourWeakSupportedLayerModeCount": current_scan_source_layer_landing.get(
                "summary", {}
            ).get("allFourWeakSupportedLayerModeCount"),
            "bestLayerMode": current_scan_source_layer_landing.get("summary", {}).get(
                "bestLayerMode"
            ),
            "bestSupportedCount": current_scan_source_layer_landing.get(
                "summary", {}
            ).get("bestSupportedCount"),
            "hiddenSourceLayerCandidate": current_scan_source_layer_landing.get(
                "summary", {}
            ).get("hiddenSourceLayerCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_source_layer_landing.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_source_layer_landing.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_source_layer_landing.get("summary", {}).get(
                "triggerCount"
            ),
            "sourceLayerLandingFingerprint": current_scan_source_layer_landing.get(
                "summary", {}
            ).get("sourceLayerLandingFingerprint"),
            "sheet": current_scan_source_layer_landing.get("sheet"),
        },
        "currentScanSourceLayerMissDistanceGate": {
            "decision": current_scan_source_layer_miss_distance.get("decision", {}).get(
                "currentScanSourceLayerMissDistanceGate"
            ),
            "modeCount": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("modeCount"),
            "layersChecked": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("layersChecked"),
            "activeDistanceRowCount": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("activeDistanceRowCount"),
            "controlDistanceRowCount": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("controlDistanceRowCount"),
            "b4MinExpansionAnyPx": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("b4MinExpansionAnyPx"),
            "b4MinExpansionFeaturePx": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("b4MinExpansionFeaturePx"),
            "b4MinExpansionBroadPx": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("b4MinExpansionBroadPx"),
            "b4TinyMissCandidate": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("b4TinyMissCandidate"),
            "allFourWithinExpansionLayerModeCounts": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("allFourWithinExpansionLayerModeCounts"),
            "bestAllFourExpansionLayerMode": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("bestAllFourExpansionLayerMode"),
            "hiddenMissDistanceCandidate": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("hiddenMissDistanceCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("triggerCount"),
            "sourceLayerMissDistanceFingerprint": current_scan_source_layer_miss_distance.get(
                "summary", {}
            ).get("sourceLayerMissDistanceFingerprint"),
            "sheet": current_scan_source_layer_miss_distance.get("sheet"),
        },
        "currentScanB4BroadContactProvenanceGate": {
            "decision": current_scan_b4_broad_contact_provenance.get(
                "decision", {}
            ).get("currentScanB4BroadContactProvenanceGate"),
            "modeId": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("modeId"),
            "target": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("target"),
            "layer": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("layer"),
            "b4BroadNearestDistancePx": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("b4BroadNearestDistancePx"),
            "b4BroadMinimalExpansionPx": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("b4BroadMinimalExpansionPx"),
            "firstExpansionWithPixelsPx": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("firstExpansionWithPixelsPx"),
            "radius32BroadPixelCount": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("radius32BroadPixelCount"),
            "radius32FeaturePixelCount": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("radius32FeaturePixelCount"),
            "radius32BroadOnlyPixelCount": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("radius32BroadOnlyPixelCount"),
            "nearestPointTargetRgb": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("nearestPointTargetRgb"),
            "sourceWordsWithinContextPads": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("sourceWordsWithinContextPads"),
            "nearestWordDistancePx": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("nearestWordDistancePx"),
            "nearestWordText": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("nearestWordText"),
            "nearestStrictInstructionDistancePx": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("nearestStrictInstructionDistancePx"),
            "strictInstructionHitCount": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("strictInstructionHitCount"),
            "contextTermHitCount": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("contextTermHitCount"),
            "hiddenBroadContactCandidate": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("hiddenBroadContactCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("triggerCount"),
            "b4BroadContactProvenanceFingerprint": current_scan_b4_broad_contact_provenance.get(
                "summary", {}
            ).get("b4BroadContactProvenanceFingerprint"),
            "sheet": current_scan_b4_broad_contact_provenance.get("sheet"),
        },
        "currentPdfB4ContactPixelProvenanceGate": {
            "decision": current_pdf_b4_contact_pixel_provenance.get(
                "decision", {}
            ).get("currentPdfB4ContactPixelProvenanceGate"),
            "candidateCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("candidateCount"),
            "pdfCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("pdfCount"),
            "sourcePointBroadCandidateCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("sourcePointBroadCandidateCount"),
            "sourcePointFeatureCandidateCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("sourcePointFeatureCandidateCount"),
            "landingPointBroadCandidateCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("landingPointBroadCandidateCount"),
            "landingPointFeatureCandidateCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("landingPointFeatureCandidateCount"),
            "radius32FeatureContactCandidateCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("radius32FeatureContactCandidateCount"),
            "renderOnlyContactCandidateCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("renderOnlyContactCandidateCount"),
            "baselineSourcePointRgb": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("baselineSourcePointRgb"),
            "magazineEmbeddedSourcePointRgb": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("magazineEmbeddedSourcePointRgb"),
            "hiddenPdfRenderContactCandidate": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("hiddenPdfRenderContactCandidate"),
            "sourceBackedR3BridgeHitCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("triggerCount"),
            "currentPdfB4ContactPixelProvenanceFingerprint": current_pdf_b4_contact_pixel_provenance.get(
                "summary", {}
            ).get("currentPdfB4ContactPixelProvenanceFingerprint"),
            "sheet": current_pdf_b4_contact_pixel_provenance.get("sheet"),
        },
        "currentPdfDuplicateBackgroundFeatureArtifactGate": {
            "decision": current_pdf_duplicate_background_feature_artifact.get(
                "decision", {}
            ).get("currentPdfDuplicateBackgroundFeatureArtifactGate"),
            "pageNo": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("pageNo"),
            "sourcePoint": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("sourcePoint"),
            "baselineB4Rgb": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("baselineB4Rgb"),
            "carrierCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("carrierCount"),
            "magazineCarrierCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("magazineCarrierCount"),
            "duplicateCarrierCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("duplicateCarrierCount"),
            "b4DuplicateFeatureRows": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("b4DuplicateFeatureRows"),
            "b4MagazineFeatureRows": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("b4MagazineFeatureRows"),
            "localPointCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            )
            .get("local", {})
            .get("pointCount"),
            "localAnyDuplicateFeatureCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            )
            .get("local", {})
            .get("anyDuplicateFeatureCount"),
            "localAllDuplicateFeatureCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            )
            .get("local", {})
            .get("allDuplicateFeatureCount"),
            "pageGridPointCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            )
            .get("pageGrid", {})
            .get("pointCount"),
            "pageGridAnyDuplicateFeatureCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            )
            .get("pageGrid", {})
            .get("anyDuplicateFeatureCount"),
            "pageGridAllDuplicateFeatureCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            )
            .get("pageGrid", {})
            .get("allDuplicateFeatureCount"),
            "localControlsAtLeastB4DuplicateFeatureRows": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("localControlsAtLeastB4DuplicateFeatureRows"),
            "pageControlsAtLeastB4DuplicateFeatureRows": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("pageControlsAtLeastB4DuplicateFeatureRows"),
            "hiddenDuplicatePdfFeatureCandidate": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("hiddenDuplicatePdfFeatureCandidate"),
            "sourceBackedR3BridgeHitCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("triggerCount"),
            "duplicateBackgroundFeatureArtifactFingerprint": current_pdf_duplicate_background_feature_artifact.get(
                "summary", {}
            ).get("duplicateBackgroundFeatureArtifactFingerprint"),
            "sheet": current_pdf_duplicate_background_feature_artifact.get("sheet"),
        },
        "currentPdfPage76CarrierStateStabilityGate": {
            "decision": current_pdf_page76_carrier_state_stability.get(
                "decision", {}
            ).get("currentPdfPage76CarrierStateStabilityGate"),
            "pageNo": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("pageNo"),
            "carrierCount": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("carrierCount"),
            "magazineCarrierCount": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("magazineCarrierCount"),
            "duplicateCarrierCount": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("duplicateCarrierCount"),
            "activeRegionCount": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("activeRegionCount"),
            "overdoseSlotRegionCount": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("overdoseSlotRegionCount"),
            "lineShiftControlRegionCount": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("lineShiftControlRegionCount"),
            "activeDuplicatePresenceMismatchRows": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("activeDuplicatePresenceMismatchRows"),
            "slotDuplicatePresenceMismatchRows": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("slotDuplicatePresenceMismatchRows"),
            "activeDuplicateOutlierRows": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("activeDuplicateOutlierRows"),
            "slotDuplicateOutlierRows": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("slotDuplicateOutlierRows"),
            "lineShiftControlOutlierRows": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("lineShiftControlOutlierRows"),
            "allFourActiveOutlier": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("allFourActiveOutlier"),
            "controlP95MaxLayerDelta": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("controlP95MaxLayerDelta"),
            "maxActiveDuplicateLayerDelta": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("maxActiveDuplicateLayerDelta"),
            "maxSlotDuplicateLayerDelta": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("maxSlotDuplicateLayerDelta"),
            "hiddenPage76DuplicateCarrierCandidate": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("hiddenPage76DuplicateCarrierCandidate"),
            "sourceBackedR3BridgeHitCount": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("triggerCount"),
            "page76CarrierStateStabilityFingerprint": current_pdf_page76_carrier_state_stability.get(
                "summary", {}
            ).get("page76CarrierStateStabilityFingerprint"),
            "sheet": current_pdf_page76_carrier_state_stability.get("sheet"),
        },
        "currentScanB4SelfSignalGuardrail": {
            "decision": current_scan_b4_self_signal.get("decision", {}).get(
                "currentScanB4SelfSignalGuardrail"
            ),
            "scenarioId": current_scan_b4_self_signal.get("summary", {}).get(
                "scenarioId"
            ),
            "blendMode": current_scan_b4_self_signal.get("summary", {}).get(
                "blendMode"
            ),
            "alpha": current_scan_b4_self_signal.get("summary", {}).get("alpha"),
            "targetCount": current_scan_b4_self_signal.get("summary", {}).get(
                "targetCount"
            ),
            "controlBoxCount": current_scan_b4_self_signal.get("summary", {}).get(
                "controlBoxCount"
            ),
            "sourceSupportedOutlierTargets": current_scan_b4_self_signal.get(
                "summary", {}
            ).get("sourceSupportedOutlierTargets"),
            "zeroSourceSelfSignalTargets": current_scan_b4_self_signal.get(
                "summary", {}
            ).get("zeroSourceSelfSignalTargets"),
            "allFourSourceSupportedOutlier": current_scan_b4_self_signal.get(
                "summary", {}
            ).get("allFourSourceSupportedOutlier"),
            "b4SourceInkRatio": current_scan_b4_self_signal.get("summary", {}).get(
                "b4SourceInkRatio"
            ),
            "b4TargetOnlyDeltaShare": current_scan_b4_self_signal.get(
                "summary", {}
            ).get("b4TargetOnlyDeltaShare"),
            "b4SourceSupportedDeltaShare": current_scan_b4_self_signal.get(
                "summary", {}
            ).get("b4SourceSupportedDeltaShare"),
            "b4DeltaAboveMatchedControlP95": current_scan_b4_self_signal.get(
                "summary", {}
            ).get("b4DeltaAboveMatchedControlP95"),
            "sourceBackedR3BridgeHitCount": current_scan_b4_self_signal.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_b4_self_signal.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_b4_self_signal.get("summary", {}).get(
                "triggerCount"
            ),
            "b4SelfSignalFingerprint": current_scan_b4_self_signal.get(
                "summary", {}
            ).get("b4SelfSignalFingerprint"),
            "overlay": current_scan_b4_self_signal.get("overlay"),
            "sheet": current_scan_b4_self_signal.get("sheet"),
        },
        "currentScanLightTableSelfSignalPartitionGate": {
            "decision": current_scan_light_table_self_signal_partition.get("decision"),
            "scenarioId": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("scenarioId"),
            "alpha": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("alpha"),
            "activeCount": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("activeCount"),
            "controlCount": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("controlCount"),
            "overdoseSlotCount": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("overdoseSlotCount"),
            "activeTargetOnlyDominantCount": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("activeTargetOnlyDominantCount"),
            "activeSourceSupportedDominantCount": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("activeSourceSupportedDominantCount"),
            "activeSourceSupportedMeanAboveControlP95Count": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("activeSourceSupportedMeanAboveControlP95Count"),
            "activeSourceSupportedShareAboveControlP95Count": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("activeSourceSupportedShareAboveControlP95Count"),
            "activeMinTargetOnlyDeltaShare": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("activeMinTargetOnlyDeltaShare"),
            "activeMaxSourceSupportedDeltaShare": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("activeMaxSourceSupportedDeltaShare"),
            "selfSignalSelectorCandidate": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("selfSignalSelectorCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("triggerCount"),
            "lightTableSelfSignalPartitionFingerprint": current_scan_light_table_self_signal_partition.get(
                "summary", {}
            ).get("lightTableSelfSignalPartitionFingerprint"),
            "sheet": current_scan_light_table_self_signal_partition.get("sheet"),
        },
        "currentScanOverdoseSlotSourceSupportTrace": {
            "decision": current_scan_overdose_slot_source_support_trace.get("decision"),
            "slotCount": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("slotCount"),
            "highSourceSupportedSlotCount": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("highSourceSupportedSlotCount"),
            "highSourceSupportedSlotIdsCsv": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("highSourceSupportedSlotIdsCsv"),
            "highSourceSupportedRunsCsv": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("highSourceSupportedRunsCsv"),
            "totalSourceWordHits": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "totalSourceWordRows": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("totalSourceWordRows"),
            "totalStrictInstructionHits": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "totalActionOrderInstructionHits": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("totalActionOrderInstructionHits"),
            "highSlotActionOrderInstructionHitCount": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("highSlotActionOrderInstructionHitCount"),
            "unitOnlyInstructionHits": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("unitOnlyInstructionHits"),
            "totalContextTermHits": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("totalContextTermHits"),
            "contextTermHits": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("contextTermHits"),
            "sourceBackedR3BridgeHitCount": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_scan_overdose_slot_source_support_trace.get("sheet"),
        },
        "currentPdfOverdoseSlotSourceSupportTrace": {
            "decision": current_pdf_overdose_slot_source_support_trace.get("decision"),
            "carrierRowCount": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("carrierRowCount"),
            "currentScanHighRun": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("currentScanHighRun"),
            "carrierRowsMatchingScanRun": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("carrierRowsMatchingScanRun"),
            "magazineRenderHighRun": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("magazineRenderHighRun"),
            "magazineEmbeddedHighRun": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("magazineEmbeddedHighRun"),
            "totalActionOrderInstructionHits": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("totalActionOrderInstructionHits"),
            "highSlotActionOrderInstructionHitCount": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("highSlotActionOrderInstructionHitCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_overdose_slot_source_support_trace.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_overdose_slot_source_support_trace.get("sheet"),
        },
        "currentPdfOseSourceHighlightPhraseGate": {
            "decision": current_pdf_ose_source_highlight_phrase.get("decision"),
            "carrierCount": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("carrierCount"),
            "slotRowCount": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("slotRowCount"),
            "renderHighSlotIds": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("renderHighSlotIds"),
            "renderHighSlotsWithSourceHighlight": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("renderHighSlotsWithSourceHighlight"),
            "renderHighSlotsWithTargetHighlight": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("renderHighSlotsWithTargetHighlight"),
            "renderHighSlotsWithHighlightBridge": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("renderHighSlotsWithHighlightBridge"),
            "allRenderHighSlotsHaveHighlightBridge": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("allRenderHighSlotsHaveHighlightBridge"),
            "highSlotActionOrderRows": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("highSlotActionOrderRows"),
            "selectorCandidateCount": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("selectorCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_ose_source_highlight_phrase.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_ose_source_highlight_phrase.get("sheet"),
        },
        "currentPdfOseHighlightMirrorGeometryGate": {
            "decision": current_pdf_ose_highlight_mirror_geometry.get("decision"),
            "p75HighlightCount": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("p75HighlightCount"),
            "oseSourceHighlightIds": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("oseSourceHighlightIds"),
            "oseSourceHighlightCount": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("oseSourceHighlightCount"),
            "oseRowsWithP76HighlightContact": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("oseRowsWithP76HighlightContact"),
            "oseRowsWithActiveTargetContact": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("oseRowsWithActiveTargetContact"),
            "oseRowsWithOverdoseSlotContact": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("oseRowsWithOverdoseSlotContact"),
            "nonOseRowsWithActiveTargetContact": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("nonOseRowsWithActiveTargetContact"),
            "selectorCandidateCount": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("selectorCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_ose_highlight_mirror_geometry.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_ose_highlight_mirror_geometry.get("sheet"),
        },
        "currentPdfOseHighlightTranslationRescueGate": {
            "decision": current_pdf_ose_highlight_translation_rescue.get("decision"),
            "sourceHighlightCount": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("sourceHighlightCount"),
            "activeTargetCount": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("activeTargetCount"),
            "naturalActiveCoverageCount": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("naturalActiveCoverageCount"),
            "smallShiftLimitPx": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("smallShiftLimitPx"),
            "smallShiftBestCoverageCount": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("smallShiftBestCoverageCount"),
            "moderateShiftLimitPx": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("moderateShiftLimitPx"),
            "moderateShiftBestCoverageCount": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("moderateShiftBestCoverageCount"),
            "minimumOneTargetShift": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("minimumOneTargetShift"),
            "minimumTwoTargetShift": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("minimumTwoTargetShift"),
            "threeTargetTranslationPossible": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("threeTargetTranslationPossible"),
            "fourTargetTranslationPossible": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("fourTargetTranslationPossible"),
            "selectorCandidateCount": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("selectorCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_ose_highlight_translation_rescue.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_ose_highlight_translation_rescue.get("sheet"),
        },
        "currentScanValidLeafBleedthroughControlGrid": {
            "decision": current_scan_valid_leaf_bleedthrough.get("decision"),
            "modeCount": current_scan_valid_leaf_bleedthrough.get("summary", {}).get(
                "modeCount"
            ),
            "targetRowCount": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("targetRowCount"),
            "naturalMeanSourceOnlyCoverage": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("naturalMeanSourceOnlyCoverage"),
            "naturalMinSourceOnlyCoverage": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("naturalMinSourceOnlyCoverage"),
            "naturalTargetCountAtLeast10": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("naturalTargetCountAtLeast10"),
            "naturalTargetCountAtLeast25": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("naturalTargetCountAtLeast25"),
            "naturalHighPercentileCount": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("naturalHighPercentileCount"),
            "jitterBestShift": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("jitterBestShift"),
            "jitterMeanSourceOnlyCoverage": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("jitterMeanSourceOnlyCoverage"),
            "jitterMinSourceOnlyCoverage": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("jitterMinSourceOnlyCoverage"),
            "jitterTargetCountAtLeast10": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("jitterTargetCountAtLeast10"),
            "jitterTargetCountAtLeast25": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("jitterTargetCountAtLeast25"),
            "jitterHighPercentileCount": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("jitterHighPercentileCount"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_bleedthrough.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_valid_leaf_bleedthrough.get("fingerprint"),
            "sheet": current_scan_valid_leaf_bleedthrough.get("sheet"),
        },
        "currentScanValidLeafLocalWarpGate": {
            "decision": current_scan_valid_leaf_local_warp.get("decision", {}).get(
                "currentScanValidLeafLocalWarpGate"
            ),
            "activeBoxCount": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("activeBoxCount"),
            "overdoseSlotBoxCount": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("overdoseSlotBoxCount"),
            "shiftCount": current_scan_valid_leaf_local_warp.get("summary", {}).get(
                "shiftCount"
            ),
            "maxActiveBestSourceOnlyCoverage": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("maxActiveBestSourceOnlyCoverage"),
            "minActiveBestSourceOnlyCoverage": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("minActiveBestSourceOnlyCoverage"),
            "meanActiveBestSourceOnlyCoverage": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("meanActiveBestSourceOnlyCoverage"),
            "activeAboveControlP95Count": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("activeAboveControlP95Count"),
            "activeAtLeast10Count": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("activeAtLeast10Count"),
            "activeAtLeast25Count": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("activeAtLeast25Count"),
            "maxActiveControlPercentile": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("maxActiveControlPercentile"),
            "maxControlBestSourceOnlyCoverage": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("maxControlBestSourceOnlyCoverage"),
            "activeDxRange": current_scan_valid_leaf_local_warp.get("summary", {}).get(
                "activeDxRange"
            ),
            "activeDyRange": current_scan_valid_leaf_local_warp.get("summary", {}).get(
                "activeDyRange"
            ),
            "maxOverdoseSlotBestSourceOnlyCoverage": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("maxOverdoseSlotBestSourceOnlyCoverage"),
            "overdoseSlotAtLeast25Count": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("overdoseSlotAtLeast25Count"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_local_warp.get("summary", {}).get(
                "triggerCount"
            ),
            "localWarpFingerprint": current_scan_valid_leaf_local_warp.get(
                "summary", {}
            ).get("localWarpFingerprint"),
            "sheet": current_scan_valid_leaf_local_warp.get("sheet"),
        },
        "currentScanValidLeafLocalWarpSourceTrace": {
            "decision": current_scan_valid_leaf_local_warp_source_trace.get(
                "decision"
            ),
            "traceRowCount": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("traceRowCount"),
            "activeTraceRowCount": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("activeTraceRowCount"),
            "overdoseSlotTraceRowCount": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("overdoseSlotTraceRowCount"),
            "componentRows": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("componentRows"),
            "totalComponentCount": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("totalComponentCount"),
            "totalComponentPixelCount": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("totalComponentPixelCount"),
            "totalSourceOnlyPixelCount": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("totalSourceOnlyPixelCount"),
            "wordHitRows": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("wordHitRows"),
            "strictInstructionRows": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("strictInstructionRows"),
            "contextTermRows": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("contextTermRows"),
            "activeStrictInstructionRows": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("activeStrictInstructionRows"),
            "overdoseSlotStrictInstructionRows": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("overdoseSlotStrictInstructionRows"),
            "totalSourceWordHits": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "totalStrictInstructionHits": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "totalContextTermHits": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("totalContextTermHits"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_local_warp_source_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_valid_leaf_local_warp_source_trace.get(
                "fingerprint"
            ),
            "sheet": current_scan_valid_leaf_local_warp_source_trace.get("sheet"),
        },
        "currentScanValidLeafEdgeContactControl": {
            "decision": current_scan_valid_leaf_edge_contact.get("decision"),
            "modeCount": current_scan_valid_leaf_edge_contact.get("summary", {}).get(
                "modeCount"
            ),
            "targetRowCount": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("targetRowCount"),
            "naturalMeanRingSourceOnlyCoverage": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("naturalMeanRingSourceOnlyCoverage"),
            "naturalMinRingSourceOnlyCoverage": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("naturalMinRingSourceOnlyCoverage"),
            "naturalTargetCountAtLeast10": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("naturalTargetCountAtLeast10"),
            "naturalTargetCountAtLeast25": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("naturalTargetCountAtLeast25"),
            "naturalHighPercentileCount": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("naturalHighPercentileCount"),
            "jitterShift": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("jitterShift"),
            "jitterMeanRingSourceOnlyCoverage": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("jitterMeanRingSourceOnlyCoverage"),
            "jitterMinRingSourceOnlyCoverage": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("jitterMinRingSourceOnlyCoverage"),
            "jitterTargetCountAtLeast10": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("jitterTargetCountAtLeast10"),
            "jitterTargetCountAtLeast25": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("jitterTargetCountAtLeast25"),
            "jitterHighPercentileCount": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("jitterHighPercentileCount"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_edge_contact.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_valid_leaf_edge_contact.get("fingerprint"),
            "sheet": current_scan_valid_leaf_edge_contact.get("sheet"),
        },
        "currentScanValidLeafEdgeSourceTrace": {
            "decision": current_scan_valid_leaf_edge_source_trace.get("decision"),
            "traceRowCount": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("traceRowCount"),
            "componentRows": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("componentRows"),
            "wordHitRows": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("wordHitRows"),
            "strictInstructionRows": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("strictInstructionRows"),
            "contextTermRows": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("contextTermRows"),
            "totalSourceWordHits": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "totalStrictInstructionHits": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_edge_source_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_valid_leaf_edge_source_trace.get("fingerprint"),
            "sheet": current_scan_valid_leaf_edge_source_trace.get("sheet"),
        },
        "currentScanValidLeafInteriorSourceTrace": {
            "decision": current_scan_valid_leaf_interior_source_trace.get("decision"),
            "traceRowCount": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("traceRowCount"),
            "componentRows": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("componentRows"),
            "totalComponentCount": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("totalComponentCount"),
            "totalComponentPixelCount": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("totalComponentPixelCount"),
            "wordHitRows": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("wordHitRows"),
            "strictInstructionRows": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("strictInstructionRows"),
            "contextTermRows": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("contextTermRows"),
            "totalSourceWordHits": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "totalStrictInstructionHits": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_interior_source_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_valid_leaf_interior_source_trace.get("fingerprint"),
            "sheet": current_scan_valid_leaf_interior_source_trace.get("sheet"),
        },
        "currentScanValidLeafGlyphSlotSourceTrace": {
            "decision": current_scan_valid_leaf_glyph_slot_source_trace.get("decision"),
            "targetRowCount": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("targetRowCount"),
            "slotTraceRowCount": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("slotTraceRowCount"),
            "componentRows": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("componentRows"),
            "wordHitRows": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("wordHitRows"),
            "strictInstructionRows": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("strictInstructionRows"),
            "contextTermRows": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("contextTermRows"),
            "totalComponentCount": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("totalComponentCount"),
            "totalComponentPixelCount": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("totalComponentPixelCount"),
            "totalSourceWordHits": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "totalStrictInstructionHits": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "modeStreams": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("modeStreams"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_glyph_slot_source_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_valid_leaf_glyph_slot_source_trace.get("fingerprint"),
            "sheet": current_scan_valid_leaf_glyph_slot_source_trace.get("sheet"),
        },
        "currentScanValidLeafChannelSourceTrace": {
            "decision": current_scan_valid_leaf_channel_source_trace.get("decision"),
            "targetRowCount": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("targetRowCount"),
            "channelRowCount": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("channelRowCount"),
            "componentRows": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("componentRows"),
            "orangeComponentRows": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("orangeComponentRows"),
            "wordHitRows": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("wordHitRows"),
            "strictInstructionRows": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("strictInstructionRows"),
            "contextTermRows": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("contextTermRows"),
            "totalComponentCount": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("totalComponentCount"),
            "totalComponentPixelCount": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("totalComponentPixelCount"),
            "totalSourceOnlyPixelCount": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("totalSourceOnlyPixelCount"),
            "totalSourceWordHits": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "totalStrictInstructionHits": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_channel_source_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_valid_leaf_channel_source_trace.get("fingerprint"),
            "sheet": current_scan_valid_leaf_channel_source_trace.get("sheet"),
        },
        "currentScanValidLeafWordCollisionTrace": {
            "decision": current_scan_valid_leaf_word_collision_trace.get("decision"),
            "traceRowCount": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("traceRowCount"),
            "sourceWordRows": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("sourceWordRows"),
            "targetWordRows": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("targetWordRows"),
            "collisionRows": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("collisionRows"),
            "totalSourceWordHits": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "totalTargetWordHits": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("totalTargetWordHits"),
            "totalCollisionPairs": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("totalCollisionPairs"),
            "strictInstructionRows": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("strictInstructionRows"),
            "contextTermRows": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("contextTermRows"),
            "totalStrictInstructionHits": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_word_collision_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_valid_leaf_word_collision_trace.get("fingerprint"),
            "sheet": current_scan_valid_leaf_word_collision_trace.get("sheet"),
        },
        "currentScanValidLeafLineBandTrace": {
            "decision": current_scan_valid_leaf_line_band_trace.get("decision"),
            "traceRowCount": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("traceRowCount"),
            "sourceLineRows": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("sourceLineRows"),
            "targetLineRows": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("targetLineRows"),
            "lineOverlapRows": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("lineOverlapRows"),
            "totalSourceLineHits": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("totalSourceLineHits"),
            "totalTargetLineHits": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("totalTargetLineHits"),
            "totalSourceTargetLineOverlaps": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("totalSourceTargetLineOverlaps"),
            "strictInstructionRows": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("strictInstructionRows"),
            "contextTermRows": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("contextTermRows"),
            "totalStrictInstructionHits": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "totalContextTermHits": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("totalContextTermHits"),
            "sourceBackedR3BridgeHitCount": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_valid_leaf_line_band_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_valid_leaf_line_band_trace.get("fingerprint"),
            "sheet": current_scan_valid_leaf_line_band_trace.get("sheet"),
        },
        "validLeafStrictTermDisambiguationGate": {
            "decision": valid_leaf_strict_term_disambiguation.get("decision"),
            "strictCarrierRowCount": valid_leaf_strict_term_disambiguation.get("summary", {}).get("strictCarrierRowCount"),
            "strictTerms": valid_leaf_strict_term_disambiguation.get("summary", {}).get("strictTerms"),
            "strictCarrierTargets": valid_leaf_strict_term_disambiguation.get("summary", {}).get("strictCarrierTargets"),
            "actionCarrierCount": valid_leaf_strict_term_disambiguation.get("summary", {}).get("actionCarrierCount"),
            "unitOnlyCarrierCount": valid_leaf_strict_term_disambiguation.get("summary", {}).get("unitOnlyCarrierCount"),
            "orderCarrierCount": valid_leaf_strict_term_disambiguation.get("summary", {}).get("orderCarrierCount"),
            "instructionCandidateCount": valid_leaf_strict_term_disambiguation.get("summary", {}).get("instructionCandidateCount"),
            "allFourActiveTargetsCoveredByStrictCarriers": valid_leaf_strict_term_disambiguation.get("summary", {}).get("allFourActiveTargetsCoveredByStrictCarriers"),
            "page75StrictLikeLineCount": valid_leaf_strict_term_disambiguation.get("summary", {}).get("page75StrictLikeLineCount"),
            "sourceBackedR3BridgeHitCount": valid_leaf_strict_term_disambiguation.get("summary", {}).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": valid_leaf_strict_term_disambiguation.get("summary", {}).get("satisfiedReopenTriggerCount"),
            "triggerCount": valid_leaf_strict_term_disambiguation.get("summary", {}).get("triggerCount"),
            "fingerprint": valid_leaf_strict_term_disambiguation.get("fingerprint"),
            "sheet": valid_leaf_strict_term_disambiguation.get("sheet"),
        },
        "validLeafTargetContextInstructionGate": {
            "decision": valid_leaf_target_context_instruction.get("decision"),
            "traceRowCount": valid_leaf_target_context_instruction.get("summary", {}).get("traceRowCount"),
            "targetContextCarrierRowCount": valid_leaf_target_context_instruction.get("summary", {}).get("targetContextCarrierRowCount"),
            "targetContextTerms": valid_leaf_target_context_instruction.get("summary", {}).get("targetContextTerms"),
            "phraseContextTerms": valid_leaf_target_context_instruction.get("summary", {}).get("phraseContextTerms"),
            "targetOnlyContextCarrierRowCount": valid_leaf_target_context_instruction.get("summary", {}).get("targetOnlyContextCarrierRowCount"),
            "sourceBackedContextCarrierRowCount": valid_leaf_target_context_instruction.get("summary", {}).get("sourceBackedContextCarrierRowCount"),
            "sourceBackedContextTerms": valid_leaf_target_context_instruction.get("summary", {}).get("sourceBackedContextTerms"),
            "actionCarrierCount": valid_leaf_target_context_instruction.get("summary", {}).get("actionCarrierCount"),
            "unitCarrierCount": valid_leaf_target_context_instruction.get("summary", {}).get("unitCarrierCount"),
            "orderCarrierCount": valid_leaf_target_context_instruction.get("summary", {}).get("orderCarrierCount"),
            "instructionCandidateCount": valid_leaf_target_context_instruction.get("summary", {}).get("instructionCandidateCount"),
            "sourceBackedInstructionCandidateCount": valid_leaf_target_context_instruction.get("summary", {}).get("sourceBackedInstructionCandidateCount"),
            "allFourActiveTargetsCoveredByTargetContext": valid_leaf_target_context_instruction.get("summary", {}).get("allFourActiveTargetsCoveredByTargetContext"),
            "allFourActiveTargetsCoveredByInstructionCandidates": valid_leaf_target_context_instruction.get("summary", {}).get("allFourActiveTargetsCoveredByInstructionCandidates"),
            "sourceBackedR3BridgeHitCount": valid_leaf_target_context_instruction.get("summary", {}).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": valid_leaf_target_context_instruction.get("summary", {}).get("satisfiedReopenTriggerCount"),
            "triggerCount": valid_leaf_target_context_instruction.get("summary", {}).get("triggerCount"),
            "fingerprint": valid_leaf_target_context_instruction.get("fingerprint"),
            "sheet": valid_leaf_target_context_instruction.get("sheet"),
        },
        "currentPdfPageBoxPairGeometryGate": {
            "decision": current_pdf_page_box_pair_geometry.get("decision"),
            "pdfCount": current_pdf_page_box_pair_geometry.get("summary", {}).get(
                "pdfCount"
            ),
            "pairCount": current_pdf_page_box_pair_geometry.get("summary", {}).get(
                "pairCount"
            ),
            "identicalPairGeometryCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("identicalPairGeometryCount"),
            "sameBoxPairCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("sameBoxPairCount"),
            "sameRotationPairCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("sameRotationPairCount"),
            "sameImageRectPairCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("sameImageRectPairCount"),
            "sameScalePairCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("sameScalePairCount"),
            "sideMarginPairCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("sideMarginPairCount"),
            "placementOffsetPairCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("placementOffsetPairCount"),
            "hiddenPairLayerCandidateCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("hiddenPairLayerCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_page_box_pair_geometry.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_page_box_pair_geometry.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": current_pdf_page_box_pair_geometry.get("fingerprint"),
            "sheet": current_pdf_page_box_pair_geometry.get("sheet"),
        },
        "currentPdfLeafPairTextureCorrelationGate": {
            "decision": current_pdf_leaf_pair_texture_correlation.get("decision"),
            "pdfCount": current_pdf_leaf_pair_texture_correlation.get("summary", {}).get(
                "pdfCount"
            ),
            "pairCount": current_pdf_leaf_pair_texture_correlation.get("summary", {}).get(
                "pairCount"
            ),
            "transformCount": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("transformCount"),
            "variantRowCount": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("variantRowCount"),
            "activeBoxRowCount": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("activeBoxRowCount"),
            "activeBoxAboveControlP95Count": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("activeBoxAboveControlP95Count"),
            "allFourAboveControlP95VariantCount": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("allFourAboveControlP95VariantCount"),
            "physicalBestVariantCount": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("physicalBestVariantCount"),
            "page75_76PhysicalBestCount": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("page75_76PhysicalBestCount"),
            "page75_76PairCount": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("page75_76PairCount"),
            "page75_76PhysicalMaxActiveRegionCorrelation": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("page75_76PhysicalMaxActiveRegionCorrelation"),
            "page75_76PhysicalMaxActiveRegionFeatureIou": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("page75_76PhysicalMaxActiveRegionFeatureIou"),
            "sourceBackedR3BridgeHitCount": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_leaf_pair_texture_correlation.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_leaf_pair_texture_correlation.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": current_pdf_leaf_pair_texture_correlation.get("fingerprint"),
            "sheet": current_pdf_leaf_pair_texture_correlation.get("sheet"),
        },
        "currentPdfNativeImageRegistrationGate": {
            "decision": current_pdf_native_image_registration.get("decision"),
            "pdfCount": current_pdf_native_image_registration.get("summary", {}).get(
                "pdfCount"
            ),
            "pairCount": current_pdf_native_image_registration.get("summary", {}).get(
                "pairCount"
            ),
            "activeRowCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("activeRowCount"),
            "overdoseSlotRowCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("overdoseSlotRowCount"),
            "sameImageRectPairCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("sameImageRectPairCount"),
            "placementOffsetPairCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("placementOffsetPairCount"),
            "sideMarginPairCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("sideMarginPairCount"),
            "totalActiveAboveControlP95Count": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("totalActiveAboveControlP95Count"),
            "totalActiveAtLeast10Count": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("totalActiveAtLeast10Count"),
            "totalActiveAtLeast25Count": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("totalActiveAtLeast25Count"),
            "allFourAboveControlP95PdfCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("allFourAboveControlP95PdfCount"),
            "allFourAtLeast10PdfCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("allFourAtLeast10PdfCount"),
            "maxActiveSourceOnlyCoverage": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("maxActiveSourceOnlyCoverage"),
            "meanActiveSourceOnlyCoverage": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("meanActiveSourceOnlyCoverage"),
            "maxControlSourceOnlyCoverage": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("maxControlSourceOnlyCoverage"),
            "maxOverdoseSlotSourceOnlyCoverage": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("maxOverdoseSlotSourceOnlyCoverage"),
            "overdoseSlotAtLeast25Count": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("overdoseSlotAtLeast25Count"),
            "sourceBackedR3BridgeHitCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_native_image_registration.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_native_image_registration.get("fingerprint"),
            "sheet": current_pdf_native_image_registration.get("sheet"),
        },
        "currentPdfNativeRegistrationCandidateSourceTrace": {
            "decision": current_pdf_native_registration_candidate_trace.get(
                "decision"
            ),
            "candidateTraceRowCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("candidateTraceRowCount"),
            "activeTraceRowCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("activeTraceRowCount"),
            "overdoseSlotTraceRowCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("overdoseSlotTraceRowCount"),
            "totalComponentCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("totalComponentCount"),
            "totalComponentPixelCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("totalComponentPixelCount"),
            "totalSourceOnlyPixelCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("totalSourceOnlyPixelCount"),
            "sourceWordRowCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("sourceWordRowCount"),
            "totalSourceWordHits": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "strictInstructionRowCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("strictInstructionRowCount"),
            "totalStrictInstructionHits": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "contextTermRowCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("contextTermRowCount"),
            "totalContextTermHits": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("totalContextTermHits"),
            "sourceBackedR3BridgeHitCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_native_registration_candidate_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_native_registration_candidate_trace.get(
                "fingerprint"
            ),
            "sheet": current_pdf_native_registration_candidate_trace.get("sheet"),
        },
        "currentPdfHeldToLightCompositePolarityGate": {
            "decision": current_pdf_held_to_light_composite_polarity.get("decision"),
            "variantCount": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("variantCount"),
            "activeRowCount": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("activeRowCount"),
            "overdoseSlotRowCount": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("overdoseSlotRowCount"),
            "bestActiveAtLeast10Count": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("bestActiveAtLeast10Count"),
            "bestActiveAboveControlP95Count": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("bestActiveAboveControlP95Count"),
            "allFourAtLeast10VariantCount": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("allFourAtLeast10VariantCount"),
            "allFourAboveControlP95VariantCount": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("allFourAboveControlP95VariantCount"),
            "magazinePhysicalActiveAtLeast10Count": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("magazinePhysicalActiveAtLeast10Count"),
            "magazinePhysicalMeanActiveSourceOnlyCoverage": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("magazinePhysicalMeanActiveSourceOnlyCoverage"),
            "maxActiveSourceOnlyCoverage": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("maxActiveSourceOnlyCoverage"),
            "maxControlSourceOnlyCoverage": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("maxControlSourceOnlyCoverage"),
            "maxOverdoseSlotSourceOnlyCoverage": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("maxOverdoseSlotSourceOnlyCoverage"),
            "sourceBackedR3BridgeHitCount": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_held_to_light_composite_polarity.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_held_to_light_composite_polarity.get(
                "fingerprint"
            ),
            "sheet": current_pdf_held_to_light_composite_polarity.get("sheet"),
            "simulatorImages": current_pdf_held_to_light_composite_polarity.get(
                "simulatorImages"
            ),
        },
        "currentPdfHeldToLightCandidateSourceTrace": {
            "decision": current_pdf_held_to_light_candidate_trace.get("decision"),
            "candidateTraceRowCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("candidateTraceRowCount"),
            "activeTraceRowCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("activeTraceRowCount"),
            "overdoseSlotTraceRowCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("overdoseSlotTraceRowCount"),
            "uniqueTraceShapeCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("uniqueTraceShapeCount"),
            "componentRowCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("componentRowCount"),
            "totalComponentCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("totalComponentCount"),
            "totalSourceOnlyPixelCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("totalSourceOnlyPixelCount"),
            "sourceWordRowCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("sourceWordRowCount"),
            "totalSourceWordHits": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "strictInstructionRowCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("strictInstructionRowCount"),
            "totalStrictInstructionHits": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "contextTermRowCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("contextTermRowCount"),
            "totalContextTermHits": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("totalContextTermHits"),
            "sourceBackedR3BridgeHitCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_held_to_light_candidate_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_held_to_light_candidate_trace.get("fingerprint"),
            "sheet": current_pdf_held_to_light_candidate_trace.get("sheet"),
        },
        "currentPdfHeldToLightAllTargetPhraseGate": {
            "decision": current_pdf_held_to_light_all_target_phrase.get("decision"),
            "pdfCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("pdfCount"),
            "transformCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("transformCount"),
            "variantCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("variantCount"),
            "targetTraceRowCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("targetTraceRowCount"),
            "allFourSourceWordVariantCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("allFourSourceWordVariantCount"),
            "targetRowsWithWords": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("targetRowsWithWords"),
            "totalSourceWordHits": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "strictInstructionRowCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("strictInstructionRowCount"),
            "totalStrictInstructionHits": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "actionOrderInstructionRowCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("actionOrderInstructionRowCount"),
            "totalActionOrderInstructionHits": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("totalActionOrderInstructionHits"),
            "contextTermRowCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("contextTermRowCount"),
            "totalContextTermHits": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("totalContextTermHits"),
            "sourceBackedR3BridgeHitCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_held_to_light_all_target_phrase.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_held_to_light_all_target_phrase.get("sheet"),
        },
        "currentPdfHeldToLightColorPhraseGate": {
            "decision": current_pdf_held_to_light_color_phrase.get("decision"),
            "variantCount": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("variantCount"),
            "streamRowCount": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("streamRowCount"),
            "allFourSourceWordVariantCount": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("allFourSourceWordVariantCount"),
            "populatedStreamRowCount": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("populatedStreamRowCount"),
            "allFourPopulatedStreamRowCount": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("allFourPopulatedStreamRowCount"),
            "totalSourceWordHits": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "totalStrictInstructionHits": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "totalActionOrderInstructionHits": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("totalActionOrderInstructionHits"),
            "totalContextTermHits": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("totalContextTermHits"),
            "colorSelectorCandidateCount": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("colorSelectorCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_held_to_light_color_phrase.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_held_to_light_color_phrase.get("sheet"),
        },
        "currentPdfHeldToLightComponentReadabilityGate": {
            "decision": current_pdf_held_to_light_component_readability.get("decision"),
            "candidateRowCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("candidateRowCount"),
            "activeRowCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("activeRowCount"),
            "overdoseSlotRowCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("overdoseSlotRowCount"),
            "totalComponentCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("totalComponentCount"),
            "totalLetterlikeComponents": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("totalLetterlikeComponents"),
            "totalCleanLetterlikeComponents": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("totalCleanLetterlikeComponents"),
            "visualReadableLikeRowCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("visualReadableLikeRowCount"),
            "mergedOrEdgeDominatedRowCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("mergedOrEdgeDominatedRowCount"),
            "sourceWordRowCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("sourceWordRowCount"),
            "totalSourceWordHits": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "totalStrictInstructionHits": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("totalStrictInstructionHits"),
            "totalContextTermHits": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("totalContextTermHits"),
            "selectorCandidateCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("selectorCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_held_to_light_component_readability.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_held_to_light_component_readability.get("sheet"),
        },
        "page76HighlightEdgeSlotRulerGate": {
            "decision": page76_highlight_edge_slot_ruler.get("decision"),
            "highlightCount": page76_highlight_edge_slot_ruler.get("summary", {}).get(
                "highlightCount"
            ),
            "verticalAxisCount": page76_highlight_edge_slot_ruler.get("summary", {}).get(
                "verticalAxisCount"
            ),
            "horizontalAxisCount": page76_highlight_edge_slot_ruler.get("summary", {}).get(
                "horizontalAxisCount"
            ),
            "directActiveStream": page76_highlight_edge_slot_ruler.get("summary", {}).get(
                "directActiveStream"
            ),
            "allFourMirroredInsideSlotAxisCount": page76_highlight_edge_slot_ruler.get(
                "summary", {}
            ).get("allFourMirroredInsideSlotAxisCount"),
            "maxMirroredInsideSlotCount": page76_highlight_edge_slot_ruler.get(
                "summary", {}
            ).get("maxMirroredInsideSlotCount"),
            "verticalLayoutTermAxisCount": page76_highlight_edge_slot_ruler.get(
                "summary", {}
            ).get("verticalLayoutTermAxisCount"),
            "strictSlotBoundaryContactCount": page76_highlight_edge_slot_ruler.get(
                "summary", {}
            ).get("strictSlotBoundaryContactCount"),
            "looseSlotBoundaryContactCount": page76_highlight_edge_slot_ruler.get(
                "summary", {}
            ).get("looseSlotBoundaryContactCount"),
            "horizontalAllFourInsideFrameYCount": page76_highlight_edge_slot_ruler.get(
                "summary", {}
            ).get("horizontalAllFourInsideFrameYCount"),
            "strictInstructionAxisHitCount": page76_highlight_edge_slot_ruler.get(
                "summary", {}
            ).get("strictInstructionAxisHitCount"),
            "sourceBackedR3BridgeHitCount": page76_highlight_edge_slot_ruler.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": page76_highlight_edge_slot_ruler.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": page76_highlight_edge_slot_ruler.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": page76_highlight_edge_slot_ruler.get("fingerprint"),
            "sheet": page76_highlight_edge_slot_ruler.get("sheet"),
        },
        "currentPdfLeafImageIdentityGate": {
            "decision": current_pdf_leaf_image_identity.get("decision"),
            "imageRecordCount": current_pdf_leaf_image_identity.get("summary", {}).get(
                "imageRecordCount"
            ),
            "leafPairRowCount": current_pdf_leaf_image_identity.get("summary", {}).get(
                "leafPairRowCount"
            ),
            "exactCurrentScanRecordCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("exactCurrentScanRecordCount"),
            "derivativeLikeRecordCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("derivativeLikeRecordCount"),
            "exactCurrentScanPairCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("exactCurrentScanPairCount"),
            "derivativeLikePairCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("derivativeLikePairCount"),
            "higherResolutionRecordCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("higherResolutionRecordCount"),
            "higherResolutionPairCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("higherResolutionPairCount"),
            "distinctImprovedCandidateCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("distinctImprovedCandidateCount"),
            "pdfSoftMaskRecordCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("pdfSoftMaskRecordCount"),
            "pdfMultiImagePageRecordCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("pdfMultiImagePageRecordCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_leaf_image_identity.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_leaf_image_identity.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": current_pdf_leaf_image_identity.get("fingerprint"),
            "sheet": current_pdf_leaf_image_identity.get("sheet"),
        },
        "currentPdfRenderLeafSimulationGate": {
            "decision": current_pdf_render_leaf_simulation.get("decision"),
            "pairRowCount": current_pdf_render_leaf_simulation.get("summary", {}).get(
                "pairRowCount"
            ),
            "targetRowCount": current_pdf_render_leaf_simulation.get("summary", {}).get(
                "targetRowCount"
            ),
            "renderVsEmbeddedPdfCount": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("renderVsEmbeddedPdfCount"),
            "maxMeanSourceOnlyCoverage": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("maxMeanSourceOnlyCoverage"),
            "maxTargetCountAtLeast10": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("maxTargetCountAtLeast10"),
            "maxTargetCountAtLeast25": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("maxTargetCountAtLeast25"),
            "allFourAtLeast10PairCount": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("allFourAtLeast10PairCount"),
            "allFourAtLeast25PairCount": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("allFourAtLeast25PairCount"),
            "maxRenderEmbeddedPageMeanAbsDelta": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("maxRenderEmbeddedPageMeanAbsDelta"),
            "maxRenderEmbeddedActiveMeanAbsDelta": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("maxRenderEmbeddedActiveMeanAbsDelta"),
            "sourceBackedR3BridgeHitCount": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_render_leaf_simulation.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_render_leaf_simulation.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": current_pdf_render_leaf_simulation.get("fingerprint"),
            "sheet": current_pdf_render_leaf_simulation.get("sheet"),
        },
        "currentPdfLowresRenderSourceTrace": {
            "decision": current_pdf_lowres_render_source_trace.get("decision"),
            "pairRowCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("pairRowCount"),
            "traceRowCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("traceRowCount"),
            "uniqueTraceShapeCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("uniqueTraceShapeCount"),
            "skippedBelowThresholdCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("skippedBelowThresholdCount"),
            "sourceWordRowCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("sourceWordRowCount"),
            "totalSourceWordHits": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("totalSourceWordHits"),
            "strictInstructionRowCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("strictInstructionRowCount"),
            "contextRowCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("contextRowCount"),
            "allFourEligibleTracePairCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("allFourEligibleTracePairCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_lowres_render_source_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_lowres_render_source_trace.get("fingerprint"),
            "sheet": current_pdf_lowres_render_source_trace.get("sheet"),
        },
        "currentPdfOcrReverseLeafSourceTrace": {
            "decision": current_pdf_ocr_reverse_leaf_source_trace.get("decision"),
            "pdfCount": current_pdf_ocr_reverse_leaf_source_trace.get("summary", {}).get(
                "pdfCount"
            ),
            "fitAvailableCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("fitAvailableCount"),
            "totalTokenPairCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("totalTokenPairCount"),
            "totalInlierCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("totalInlierCount"),
            "targetRowCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("targetRowCount"),
            "pdfWordTargetRowCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("pdfWordTargetRowCount"),
            "pdfExactBoxWordTargetRowCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("pdfExactBoxWordTargetRowCount"),
            "strictInstructionRowCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("strictInstructionRowCount"),
            "contextRowCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("contextRowCount"),
            "allFourExactBoxPdfTracePairCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("allFourExactBoxPdfTracePairCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ocr_reverse_leaf_source_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_ocr_reverse_leaf_source_trace.get("fingerprint"),
            "sheet": current_pdf_ocr_reverse_leaf_source_trace.get("sheet"),
        },
        "currentScanOverdoseSlotShapePhaseControl": {
            "decision": current_scan_overdose_slot_shape_phase_control.get("decision"),
            "lineGroupCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("lineGroupCount"),
            "scenarioCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("scenarioCount"),
            "activePhaseCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("activePhaseCount"),
            "controlPhaseCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("controlPhaseCount"),
            "targetRowCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("targetRowCount"),
            "totalWordHitCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("totalWordHitCount"),
            "strictInstructionScenarioCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("strictInstructionScenarioCount"),
            "contextScenarioCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("contextScenarioCount"),
            "activePhaseStrictTokenHitCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("activePhaseStrictTokenHitCount"),
            "activePhaseContextTokenHitCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("activePhaseContextTokenHitCount"),
            "controlPhaseStrictTokenHitCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("controlPhaseStrictTokenHitCount"),
            "controlPhaseContextTokenHitCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("controlPhaseContextTokenHitCount"),
            "sourceBackedR3BridgeHitCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_overdose_slot_shape_phase_control.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_overdose_slot_shape_phase_control.get("fingerprint"),
            "sheet": current_scan_overdose_slot_shape_phase_control.get("sheet"),
        },
        "currentScanOverdoseXslotPhaseControl": {
            "decision": current_scan_overdose_xslot_phase_control.get("decision"),
            "scenarioCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("scenarioCount"),
            "activePhaseCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("activePhaseCount"),
            "controlPhaseCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("controlPhaseCount"),
            "targetRowCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("targetRowCount"),
            "totalWordHitCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("totalWordHitCount"),
            "strictInstructionScenarioCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("strictInstructionScenarioCount"),
            "contextScenarioCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("contextScenarioCount"),
            "activePhaseStrictTokenHitCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("activePhaseStrictTokenHitCount"),
            "activePhaseContextTokenHitCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("activePhaseContextTokenHitCount"),
            "controlPhaseStrictTokenHitCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("controlPhaseStrictTokenHitCount"),
            "controlPhaseContextTokenHitCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("controlPhaseContextTokenHitCount"),
            "activePhaseVisualOrangeHitCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("activePhaseVisualOrangeHitCount"),
            "controlPhaseVisualOrangeHitCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("controlPhaseVisualOrangeHitCount"),
            "sourceBackedR3BridgeHitCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_overdose_xslot_phase_control.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_scan_overdose_xslot_phase_control.get("fingerprint"),
            "sheet": current_scan_overdose_xslot_phase_control.get("sheet"),
        },
        "currentPdfContainerMetadataGate": {
            "decision": current_pdf_container_metadata_gate.get("decision"),
            "pdfCount": current_pdf_container_metadata_gate.get("summary", {}).get(
                "pdfCount"
            ),
            "pageCount": current_pdf_container_metadata_gate.get("summary", {}).get(
                "pageCount"
            ),
            "signalMetadataFieldCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("signalMetadataFieldCount"),
            "xmlMetadataStreamCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("xmlMetadataStreamCount"),
            "nameTreeCount": current_pdf_container_metadata_gate.get("summary", {}).get(
                "nameTreeCount"
            ),
            "nonEmptyNameTreeCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("nonEmptyNameTreeCount"),
            "embeddedFileCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("embeddedFileCount"),
            "annotationCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("annotationCount"),
            "widgetCount": current_pdf_container_metadata_gate.get("summary", {}).get(
                "widgetCount"
            ),
            "linkCount": current_pdf_container_metadata_gate.get("summary", {}).get(
                "linkCount"
            ),
            "optionalContentGroupCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("optionalContentGroupCount"),
            "layerCount": current_pdf_container_metadata_gate.get("summary", {}).get(
                "layerCount"
            ),
            "specialActionObjectCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("specialActionObjectCount"),
            "strictInstructionHitCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("strictInstructionHitCount"),
            "contextHitCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("contextHitCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_container_metadata_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_container_metadata_gate.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": current_pdf_container_metadata_gate.get("fingerprint"),
        },
        "currentPdfLogicalStructureGate": {
            "decision": current_pdf_logical_structure_gate.get("decision", {}).get(
                "currentPdfLogicalStructureGate"
            ),
            "pdfCount": current_pdf_logical_structure_gate.get("summary", {}).get(
                "pdfCount"
            ),
            "taggedCatalogCount": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("taggedCatalogCount"),
            "logicalObjectMarkerCount": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("logicalObjectMarkerCount"),
            "contentMarkerTotalCount": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("contentMarkerTotalCount"),
            "page76ContentMarkerTotalCount": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("page76ContentMarkerTotalCount"),
            "rawOnlyBdcCandidateCount": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("rawOnlyBdcCandidateCount"),
            "strictContextHitCount": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("strictContextHitCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "logicalStructureFingerprint": current_pdf_logical_structure_gate.get(
                "summary", {}
            ).get("logicalStructureFingerprint"),
            "sheet": current_pdf_logical_structure_gate.get("sheet"),
        },
        "currentPdfPageThumbnailGate": {
            "decision": current_pdf_page_thumbnail_gate.get("decision"),
            "pdfCount": current_pdf_page_thumbnail_gate.get("summary", {}).get(
                "pdfCount"
            ),
            "pageCount": current_pdf_page_thumbnail_gate.get("summary", {}).get(
                "pageCount"
            ),
            "thumbnailPageCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("thumbnailPageCount"),
            "page76ThumbnailCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("page76ThumbnailCount"),
            "uniqueThumbnailImageCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("uniqueThumbnailImageCount"),
            "totalThumbnailByteCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("totalThumbnailByteCount"),
            "thumbnailContentXrefMatchCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("thumbnailContentXrefMatchCount"),
            "higherResolutionPage76ThumbnailCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("higherResolutionPage76ThumbnailCount"),
            "distinctSourceCarrierCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("distinctSourceCarrierCount"),
            "strictInstructionHitCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("strictInstructionHitCount"),
            "contextHitCount": current_pdf_page_thumbnail_gate.get("summary", {}).get(
                "contextHitCount"
            ),
            "sourceBackedR3BridgeHitCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_page_thumbnail_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_page_thumbnail_gate.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": current_pdf_page_thumbnail_gate.get("fingerprint"),
            "sheet": current_pdf_page_thumbnail_gate.get("sheet"),
        },
        "currentPdfThumbnailActiveSignalGate": {
            "decision": current_pdf_thumbnail_active_signal_gate.get("decision", {}).get(
                "currentPdfThumbnailActiveSignalGate"
            ),
            "thumbSize": current_pdf_thumbnail_active_signal_gate.get("summary", {}).get(
                "thumbSize"
            ),
            "bestTransform": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("bestTransform"),
            "bestTransformMad": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("bestTransformMad"),
            "activeStateMatchExpectedCount": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("activeStateMatchExpectedCount"),
            "activeStateChangedVsDownsampleCount": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("activeStateChangedVsDownsampleCount"),
            "controlStateChangedVsDownsampleCount": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("controlStateChangedVsDownsampleCount"),
            "slotStateChangedVsDownsampleCount": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("slotStateChangedVsDownsampleCount"),
            "activeMinPixelCount": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("activeMinPixelCount"),
            "hiddenThumbnailSignalCandidate": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("hiddenThumbnailSignalCandidate"),
            "sourceBackedR3BridgeHitCount": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_thumbnail_active_signal_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "thumbnailActiveSignalFingerprint": current_pdf_thumbnail_active_signal_gate.get(
                "fingerprint"
            ),
            "sheet": current_pdf_thumbnail_active_signal_gate.get("sheet"),
        },
        "currentPdfContentStreamOperatorGate": {
            "decision": current_pdf_content_stream_operator_gate.get("decision"),
            "pdfCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("pdfCount"),
            "pageCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("pageCount"),
            "contentStreamCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("contentStreamCount"),
            "formXobjectCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("formXobjectCount"),
            "imageDoCallCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("imageDoCallCount"),
            "formDoCallCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("formDoCallCount"),
            "unknownDoCallCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("unknownDoCallCount"),
            "textObjectCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("textObjectCount"),
            "invisibleTextRenderModeCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("invisibleTextRenderModeCount"),
            "visibleTextRenderModeCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("visibleTextRenderModeCount"),
            "vectorPaintOperatorCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("vectorPaintOperatorCount"),
            "clipOperatorCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("clipOperatorCount"),
            "operatorStrictHitCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("operatorStrictHitCount"),
            "operatorContextHitCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("operatorContextHitCount"),
            "decodedTextPayloadStrictRowCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("decodedTextPayloadStrictRowCount"),
            "decodedTextPayloadContextRowCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("decodedTextPayloadContextRowCount"),
            "page76VisibleTextRenderModeCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("page76VisibleTextRenderModeCount"),
            "page76VectorPaintOperatorCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("page76VectorPaintOperatorCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_content_stream_operator_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_content_stream_operator_gate.get("fingerprint"),
        },
        "currentPdfContentTransformMatrixGate": {
            "decision": current_pdf_content_transform_matrix_gate.get("decision"),
            "pageCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("pageCount"),
            "doPlacementCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("doPlacementCount"),
            "imageDoPlacementCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("imageDoPlacementCount"),
            "formDoPlacementCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("formDoPlacementCount"),
            "unknownDoPlacementCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("unknownDoPlacementCount"),
            "placementSignatureGroupCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("placementSignatureGroupCount"),
            "distinctCumulativeMatrixCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("distinctCumulativeMatrixCount"),
            "page76PlacementCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("page76PlacementCount"),
            "page76UniquePlacementSignatureCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("page76UniquePlacementSignatureCount"),
            "activeUniquePlacementSignatureCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("activeUniquePlacementSignatureCount"),
            "strictHitCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("strictHitCount"),
            "contextHitCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("contextHitCount"),
            "structuralStreamOrderMatchCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("structuralStreamOrderMatchCount"),
            "structuralOrderRowCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("structuralOrderRowCount"),
            "activeSubsetStreamOrderMatchCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("activeSubsetStreamOrderMatchCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_content_transform_matrix_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_content_transform_matrix_gate.get("fingerprint"),
        },
        "currentPdfFormXobjectDictionaryGate": {
            "decision": current_pdf_form_xobject_dictionary_gate.get("decision"),
            "formObjectCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("formObjectCount"),
            "normalizedDictionaryGroupCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("normalizedDictionaryGroupCount"),
            "page76FormObjectCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("page76FormObjectCount"),
            "page76UniqueDictionaryGroupCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("page76UniqueDictionaryGroupCount"),
            "activeUniqueDictionaryGroupCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("activeUniqueDictionaryGroupCount"),
            "specialKeyRowCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("specialKeyRowCount"),
            "visibleTextRenderModeRowCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("visibleTextRenderModeRowCount"),
            "strictHitCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("strictHitCount"),
            "contextHitCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("contextHitCount"),
            "structuralXrefOrderMatchCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("structuralXrefOrderMatchCount"),
            "structuralOrderRowCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("structuralOrderRowCount"),
            "activeSubsetXrefOrderMatchCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("activeSubsetXrefOrderMatchCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_form_xobject_dictionary_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_form_xobject_dictionary_gate.get("fingerprint"),
        },
        "currentPdfFormOverlayPlacementGate": {
            "decision": current_pdf_form_overlay_placement_gate.get("decision", {}).get(
                "currentPdfFormOverlayPlacementGate"
            ),
            "formPlacementCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("formPlacementCount"),
            "page76FormPlacementCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("page76FormPlacementCount"),
            "overlaySignatureGroupCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("overlaySignatureGroupCount"),
            "page76UniqueOverlaySignatureCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("page76UniqueOverlaySignatureCount"),
            "activeUniqueOverlaySignatureCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("activeUniqueOverlaySignatureCount"),
            "nearFullOverlayCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("nearFullOverlayCount"),
            "page76NearFullOverlayCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("page76NearFullOverlayCount"),
            "allPageRepeatingOverlayGroupCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("allPageRepeatingOverlayGroupCount"),
            "visibleTextPlacementCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("visibleTextPlacementCount"),
            "invisibleTextPlacementCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("invisibleTextPlacementCount"),
            "strictHitCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("strictHitCount"),
            "topOffsetPtValues": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("topOffsetPtValues"),
            "activeProjectionInsideCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("activeProjectionInsideCount"),
            "activeProjectionRowCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("activeProjectionRowCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_form_overlay_placement_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_form_overlay_placement_gate.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": current_pdf_form_overlay_placement_gate.get("fingerprint"),
            "sheet": current_pdf_form_overlay_placement_gate.get("sheet"),
        },
        "currentPdfTrailerXrefIntegrityGate": {
            "decision": current_pdf_trailer_xref_integrity_gate.get("decision"),
            "pdfCount": current_pdf_trailer_xref_integrity_gate.get("summary", {}).get(
                "pdfCount"
            ),
            "uniqueFileHashCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("uniqueFileHashCount"),
            "xrefObjectCountTotal": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("xrefObjectCountTotal"),
            "startxrefOccurrenceCountTotal": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("startxrefOccurrenceCountTotal"),
            "eofMarkerCountTotal": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("eofMarkerCountTotal"),
            "incrementalUpdateCandidateCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("incrementalUpdateCandidateCount"),
            "objectStreamCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("objectStreamCount"),
            "xrefStreamCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("xrefStreamCount"),
            "encryptedPdfCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("encryptedPdfCount"),
            "nonzeroGenerationObjectCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("nonzeroGenerationObjectCount"),
            "hiddenCarrierTrailerKeyCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("hiddenCarrierTrailerKeyCount"),
            "trailerIdPresentCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("trailerIdPresentCount"),
            "strictHitCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("strictHitCount"),
            "contextHitCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("contextHitCount"),
            "structuralPageXrefOrderMatchCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("structuralPageXrefOrderMatchCount"),
            "structuralOrderRowCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("structuralOrderRowCount"),
            "activeSubsetPageXrefOrderMatchCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("activeSubsetPageXrefOrderMatchCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_trailer_xref_integrity_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_trailer_xref_integrity_gate.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": current_pdf_trailer_xref_integrity_gate.get("fingerprint"),
        },
        "currentPdfFontCmapResourceGate": {
            "decision": current_pdf_font_cmap_resource_gate.get("decision"),
            "pdfCount": current_pdf_font_cmap_resource_gate.get("summary", {}).get(
                "pdfCount"
            ),
            "pageCount": current_pdf_font_cmap_resource_gate.get("summary", {}).get(
                "pageCount"
            ),
            "pageFontReferenceCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("pageFontReferenceCount"),
            "uniqueFontObjectCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("uniqueFontObjectCount"),
            "type0GlyphLessFontCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("type0GlyphLessFontCount"),
            "builtInHelveticaFontCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("builtInHelveticaFontCount"),
            "toUnicodeStreamCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("toUnicodeStreamCount"),
            "identityToUnicodeCMapCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("identityToUnicodeCMapCount"),
            "cidToGidMapCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("cidToGidMapCount"),
            "fontFileStreamCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("fontFileStreamCount"),
            "uniqueFontFileHashCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("uniqueFontFileHashCount"),
            "resourceStrictHitCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("resourceStrictHitCount"),
            "resourceContextHitCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("resourceContextHitCount"),
            "structuralFontTermHitCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("structuralFontTermHitCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_font_cmap_resource_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_font_cmap_resource_gate.get("fingerprint"),
        },
        "currentPdfEmbeddedJpegMarkerGate": {
            "decision": current_pdf_embedded_jpeg_marker_gate.get("decision"),
            "pdfCount": current_pdf_embedded_jpeg_marker_gate.get("summary", {}).get(
                "pdfCount"
            ),
            "imageRecordCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("imageRecordCount"),
            "pageImageRecordCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("pageImageRecordCount"),
            "thumbnailRecordCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("thumbnailRecordCount"),
            "page76RecordCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("page76RecordCount"),
            "appSegmentCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("appSegmentCount"),
            "comSegmentCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("comSegmentCount"),
            "structuralJfifSegmentCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("structuralJfifSegmentCount"),
            "provenanceMetadataSegmentCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("provenanceMetadataSegmentCount"),
            "sourceInstructionCarrierSegmentCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("sourceInstructionCarrierSegmentCount"),
            "strictHitCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("strictHitCount"),
            "contextHitCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("contextHitCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_embedded_jpeg_marker_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_embedded_jpeg_marker_gate.get("fingerprint"),
        },
        "currentPdfThumbnailExifOrderGate": {
            "decision": current_pdf_thumbnail_exif_order_gate.get("decision"),
            "exifRowCount": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("exifRowCount"),
            "articlePageOrder": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("articlePageOrder"),
            "timestampOrder": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("timestampOrder"),
            "articleOrderMonotonic": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("articleOrderMonotonic"),
            "articleOrderInversionCount": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("articleOrderInversionCount"),
            "page76TimestampRank": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("page76TimestampRank"),
            "sourceInstructionCarrierSegmentCount": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("sourceInstructionCarrierSegmentCount"),
            "strictHitCount": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("strictHitCount"),
            "contextHitCount": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("contextHitCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_thumbnail_exif_order_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_thumbnail_exif_order_gate.get("fingerprint"),
        },
        "currentPdfJpegCompressionProvenanceGate": {
            "decision": current_pdf_jpeg_compression_provenance_gate.get("decision"),
            "imageRecordCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("imageRecordCount"),
            "pageImageRecordCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("pageImageRecordCount"),
            "thumbnailRecordCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("thumbnailRecordCount"),
            "compressionGroupCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("compressionGroupCount"),
            "page76UniqueCompressionSignatureCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("page76UniqueCompressionSignatureCount"),
            "activeUniqueCompressionSignatureCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("activeUniqueCompressionSignatureCount"),
            "magazinePageImageByteOrder": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("magazinePageImageByteOrder"),
            "magazineThumbnailByteOrder": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("magazineThumbnailByteOrder"),
            "candidateOrderMatchCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("candidateOrderMatchCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_jpeg_compression_provenance_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_jpeg_compression_provenance_gate.get(
                "fingerprint"
            ),
        },
        "currentPdfJpegEntropyTailGate": {
            "decision": current_pdf_jpeg_entropy_tail_gate.get("decision"),
            "imageRowCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("imageRowCount"),
            "pageImageRowCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("pageImageRowCount"),
            "signatureGroupCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("signatureGroupCount"),
            "page76UniqueEntropySignatureCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("page76UniqueEntropySignatureCount"),
            "activePageUniqueEntropySignatureCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("activePageUniqueEntropySignatureCount"),
            "tailRowCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("tailRowCount"),
            "strictTailRowCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("strictTailRowCount"),
            "contextTailRowCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("contextTailRowCount"),
            "unexpectedRowCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("unexpectedRowCount"),
            "restartRowCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("restartRowCount"),
            "matchedEntropyOrderCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("matchedEntropyOrderCount"),
            "structuralOnlySignalCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("structuralOnlySignalCount"),
            "selectorCandidateCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("selectorCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_jpeg_entropy_tail_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_jpeg_entropy_tail_gate.get("fingerprint"),
            "sheet": current_pdf_jpeg_entropy_tail_gate.get("sheet"),
        },
        "currentPdfImageXobjectDictionaryGate": {
            "decision": current_pdf_image_xobject_dictionary_gate.get("decision"),
            "imageObjectCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("imageObjectCount"),
            "pageImageObjectCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("pageImageObjectCount"),
            "thumbnailObjectCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("thumbnailObjectCount"),
            "normalizedDictionaryGroupCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("normalizedDictionaryGroupCount"),
            "page76UniqueDictionaryGroupCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("page76UniqueDictionaryGroupCount"),
            "activeUniqueDictionaryGroupCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("activeUniqueDictionaryGroupCount"),
            "specialKeyRowCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("specialKeyRowCount"),
            "strictHitCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("strictHitCount"),
            "contextHitCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("contextHitCount"),
            "structuralXrefOrderMatchCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("structuralXrefOrderMatchCount"),
            "structuralOrderRowCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("structuralOrderRowCount"),
            "activeSubsetXrefOrderMatchCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("activeSubsetXrefOrderMatchCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_image_xobject_dictionary_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_image_xobject_dictionary_gate.get(
                "fingerprint"
            ),
        },
        "currentPdfPageResourceOrderGate": {
            "decision": current_pdf_page_resource_order_gate.get("decision"),
            "pageCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("pageCount"),
            "page76PageCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("page76PageCount"),
            "pageDictionaryGroupCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("pageDictionaryGroupCount"),
            "resourceSignatureGroupCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("resourceSignatureGroupCount"),
            "page76UniquePageDictionaryGroupCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("page76UniquePageDictionaryGroupCount"),
            "page76UniqueResourceSignatureGroupCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("page76UniqueResourceSignatureGroupCount"),
            "activeUniquePageDictionaryGroupCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("activeUniquePageDictionaryGroupCount"),
            "activeUniqueResourceSignatureGroupCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("activeUniqueResourceSignatureGroupCount"),
            "thumbPageCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("thumbPageCount"),
            "specialPageKeyRowCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("specialPageKeyRowCount"),
            "strictHitCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("strictHitCount"),
            "contextHitCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("contextHitCount"),
            "structuralPageXrefOrderMatchCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("structuralPageXrefOrderMatchCount"),
            "structuralOrderRowCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("structuralOrderRowCount"),
            "activeSubsetPageXrefOrderMatchCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("activeSubsetPageXrefOrderMatchCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_page_resource_order_gate.get(
                "summary", {}
            ).get("triggerCount"),
            "fingerprint": current_pdf_page_resource_order_gate.get("fingerprint"),
        },
        "currentPdfObjectLayoutInspection": {
            "decision": current_pdf_object_layout.get("decision", {}).get(
                "currentPdfObjectLayoutInspection"
            ),
            "pdfCount": current_pdf_object_layout.get("summary", {}).get(
                "pdfCount"
            ),
            "uniqueShaCount": current_pdf_object_layout.get("summary", {}).get(
                "uniqueShaCount"
            ),
            "page76CandidateCount": current_pdf_object_layout.get(
                "summary", {}
            ).get("page76CandidateCount"),
            "page76RasterDominatedCount": current_pdf_object_layout.get(
                "summary", {}
            ).get("page76RasterDominatedCount"),
            "page76OcrTextLayerCount": current_pdf_object_layout.get(
                "summary", {}
            ).get("page76OcrTextLayerCount"),
            "page76NativeOriginalLayoutEvidenceCount": current_pdf_object_layout.get(
                "summary", {}
            ).get("page76NativeOriginalLayoutEvidenceCount"),
            "page76ActivePhraseTextHitCount": current_pdf_object_layout.get(
                "summary", {}
            ).get("page76ActivePhraseTextHitCount"),
            "page76StrictUnitOrderTextHitCount": current_pdf_object_layout.get(
                "summary", {}
            ).get("page76StrictUnitOrderTextHitCount"),
            "higherThanMagazinePage76ImageCount": current_pdf_object_layout.get(
                "summary", {}
            ).get("higherThanMagazinePage76ImageCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_object_layout.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_object_layout.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_object_layout.get("summary", {}).get(
                "triggerCount"
            ),
            "pdfObjectLayoutFingerprint": current_pdf_object_layout.get(
                "summary", {}
            ).get("pdfObjectLayoutFingerprint"),
            "sheet": current_pdf_object_layout.get("sheet"),
        },
        "currentPdfPartialImagePlacementGate": {
            "decision": current_pdf_partial_image_placement.get("decision", {}).get(
                "currentPdfPartialImagePlacementGate"
            ),
            "page76PartialPlacementCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("page76PartialPlacementCount"),
            "objectLayoutPage76PartialImagePlacementCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("objectLayoutPage76PartialImagePlacementCount"),
            "page76PartialSignatureGroupCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("page76PartialSignatureGroupCount"),
            "page76UniquePartialSignatureCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("page76UniquePartialSignatureCount"),
            "page76NearFullContentPartialCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("page76NearFullContentPartialCount"),
            "page76LocalOverlayPartialCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("page76LocalOverlayPartialCount"),
            "page76AllPageRepeatingPartialGroupCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("page76AllPageRepeatingPartialGroupCount"),
            "page76PartialAllFourInsideCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("page76PartialAllFourInsideCount"),
            "activeProjectionInsideCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("activeProjectionInsideCount"),
            "activeProjectionRowCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("activeProjectionRowCount"),
            "strictHitCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("strictHitCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_partial_image_placement.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_partial_image_placement.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": current_pdf_partial_image_placement.get("fingerprint"),
            "sheet": current_pdf_partial_image_placement.get("sheet"),
        },
        "currentScanCropLightTableTargets": {
            "decision": current_scan_crop_light_table.get("decision", {}).get(
                "currentScanCropLightTableTargets"
            ),
            "scenarioCount": current_scan_crop_light_table.get("summary", {}).get(
                "scenarioCount"
            ),
            "targetRowCount": current_scan_crop_light_table.get("summary", {}).get(
                "targetRowCount"
            ),
            "allFourAt10ScenarioCount": current_scan_crop_light_table.get(
                "summary", {}
            ).get("allFourAt10ScenarioCount"),
            "allFourAt25ScenarioCount": current_scan_crop_light_table.get(
                "summary", {}
            ).get("allFourAt25ScenarioCount"),
            "allFourAt50ScenarioCount": current_scan_crop_light_table.get(
                "summary", {}
            ).get("allFourAt50ScenarioCount"),
            "bestMeanCoverageScenario": current_scan_crop_light_table.get(
                "summary", {}
            ).get("bestMeanCoverageScenario"),
            "bestMeanCoverage": current_scan_crop_light_table.get(
                "summary", {}
            ).get("bestMeanCoverage"),
            "validNaturalCoverageCsv": current_scan_crop_light_table.get(
                "summary", {}
            ).get("validNaturalCoverageCsv"),
            "validForcedCoverageCsv": current_scan_crop_light_table.get(
                "summary", {}
            ).get("validForcedCoverageCsv"),
            "benchmark79BestCoverageCsv": current_scan_crop_light_table.get(
                "summary", {}
            ).get("benchmark79BestCoverageCsv"),
            "sourceBackedR3BridgeHitCount": current_scan_crop_light_table.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_crop_light_table.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_crop_light_table.get("summary", {}).get(
                "triggerCount"
            ),
            "cropLightTableFingerprint": current_scan_crop_light_table.get(
                "summary", {}
            ).get("cropLightTableFingerprint"),
            "sheet": current_scan_crop_light_table.get("sheet"),
            "html": current_scan_crop_light_table.get("html"),
        },
        "currentScanOverdoseGlyphCropProjection": {
            "decision": current_scan_overdose_glyph_crop.get("decision", {}).get(
                "currentScanOverdoseGlyphCropProjection"
            ),
            "glyphProjectionCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("glyphProjectionCount"),
            "scenarioProjectionCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("scenarioProjectionCount"),
            "targetGlyphRowCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("targetGlyphRowCount"),
            "allFourDominant10ScenarioProjectionCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("allFourDominant10ScenarioProjectionCount"),
            "allFourTouched25ScenarioProjectionCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("allFourTouched25ScenarioProjectionCount"),
            "allFourTouched50ScenarioProjectionCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("allFourTouched50ScenarioProjectionCount"),
            "layoutHitStreamCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("layoutHitStreamCount"),
            "strictInstructionHitCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("strictInstructionHitCount"),
            "validNaturalDominant10LineStream": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("validNaturalDominant10LineStream"),
            "validForcedDominant10LineStream": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("validForcedDominant10LineStream"),
            "benchmark79BestDominant10LineStream": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("benchmark79BestDominant10LineStream"),
            "validNaturalBlackSlots10XStream": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("validNaturalBlackSlots10XStream"),
            "validForcedBlackSlots10XStream": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("validForcedBlackSlots10XStream"),
            "benchmark79BestBlackSlots10XStream": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("benchmark79BestBlackSlots10XStream"),
            "sourceBackedR3BridgeHitCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_overdose_glyph_crop.get("summary", {}).get(
                "triggerCount"
            ),
            "glyphCropProjectionFingerprint": current_scan_overdose_glyph_crop.get(
                "summary", {}
            ).get("glyphCropProjectionFingerprint"),
            "sheet": current_scan_overdose_glyph_crop.get("sheet"),
        },
        "currentScanHighlightBoundaryInstructionProbe": {
            "decision": current_scan_highlight_boundary_instruction.get("decision", {}).get(
                "currentScanHighlightBoundaryInstructionProbe"
            ),
            "activeTargetCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("activeTargetCount"),
            "boundaryRegionCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("boundaryRegionCount"),
            "regionWithWordCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("regionWithWordCount"),
            "strictInstructionRegionCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("strictInstructionRegionCount"),
            "targetEdgeStrictInstructionRegionCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("targetEdgeStrictInstructionRegionCount"),
            "cropWindowStrictInstructionRegionCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("cropWindowStrictInstructionRegionCount"),
            "contextTermRegionCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("contextTermRegionCount"),
            "contextTermHits": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("contextTermHits"),
            "sourceBackedR3BridgeHitCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("triggerCount"),
            "boundaryInstructionProbeFingerprint": current_scan_highlight_boundary_instruction.get(
                "summary", {}
            ).get("boundaryInstructionProbeFingerprint"),
            "sheet": current_scan_highlight_boundary_instruction.get("sheet"),
        },
        "currentScanBoundaryLightTableAnomalyProbe": {
            "decision": current_scan_boundary_light_table_anomaly.get("decision", {}).get(
                "currentScanBoundaryLightTableAnomalyProbe"
            ),
            "scenarioCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("scenarioCount"),
            "boundaryRowCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("boundaryRowCount"),
            "boundaryGroupCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("boundaryGroupCount"),
            "allFourAt10GroupCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("allFourAt10GroupCount"),
            "allFourAt25GroupCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("allFourAt25GroupCount"),
            "allFourAt50GroupCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("allFourAt50GroupCount"),
            "physicalNaturalAllFourAt10GroupCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("physicalNaturalAllFourAt10GroupCount"),
            "weakAllFourAt10Groups": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("weakAllFourAt10Groups"),
            "bestMeanBoundaryGroup": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("bestMeanBoundaryGroup"),
            "bestMeanBoundaryCoverage": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("bestMeanBoundaryCoverage"),
            "sourceBackedR3BridgeHitCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("triggerCount"),
            "boundaryLightTableAnomalyFingerprint": current_scan_boundary_light_table_anomaly.get(
                "summary", {}
            ).get("boundaryLightTableAnomalyFingerprint"),
            "sheet": current_scan_boundary_light_table_anomaly.get("sheet"),
        },
        "currentScanBoundaryContactSourceTrace": {
            "decision": current_scan_boundary_contact_source_trace.get("decision", {}).get(
                "currentScanBoundaryContactSourceTrace"
            ),
            "weakGroupCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("weakGroupCount"),
            "traceRowCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("traceRowCount"),
            "sourceWordHitRowCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("sourceWordHitRowCount"),
            "sourceStrictInstructionRowCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("sourceStrictInstructionRowCount"),
            "sourceContextTermRowCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("sourceContextTermRowCount"),
            "sourceStrictInstructionHits": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("sourceStrictInstructionHits"),
            "sourceContextTermHits": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("sourceContextTermHits"),
            "p75WordHitRowCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("p75WordHitRowCount"),
            "p79WordHitRowCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("p79WordHitRowCount"),
            "sourceBackedR3BridgeHitCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("triggerCount"),
            "boundaryContactSourceTraceFingerprint": current_scan_boundary_contact_source_trace.get(
                "summary", {}
            ).get("boundaryContactSourceTraceFingerprint"),
            "sheet": current_scan_boundary_contact_source_trace.get("sheet"),
        },
        "currentPdfOcrTargetProvenanceGate": {
            "decision": current_pdf_ocr_target_provenance.get("decision", {}).get(
                "currentPdfOcrTargetProvenanceGate"
            ),
            "exactActivePhraseRowCount": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("exactActivePhraseRowCount"),
            "pdfsWithAllFourExactActivePhrases": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("pdfsWithAllFourExactActivePhrases"),
            "componentExactHitRowCount": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("componentExactHitRowCount"),
            "componentStemLikeHitRowCount": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("componentStemLikeHitRowCount"),
            "approxTargetBoxWordRowCount": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("approxTargetBoxWordRowCount"),
            "approxTargetBoxExactPhraseRowCount": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("approxTargetBoxExactPhraseRowCount"),
            "strictUnitOrderTerms": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("strictUnitOrderTerms"),
            "overdoseHeaderPdfCount": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("overdoseHeaderPdfCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("triggerCount"),
            "pdfOcrTargetProvenanceFingerprint": current_pdf_ocr_target_provenance.get(
                "summary", {}
            ).get("pdfOcrTargetProvenanceFingerprint"),
            "sheet": current_pdf_ocr_target_provenance.get("sheet"),
        },
        "currentPdfOcrDocumentOrderGate": {
            "decision": current_pdf_ocr_document_order.get("decision", {}).get(
                "currentPdfOcrDocumentOrderGate"
            ),
            "pdfCount": current_pdf_ocr_document_order.get("summary", {}).get(
                "pdfCount"
            ),
            "allFourBoxPopulatedPdfCount": current_pdf_ocr_document_order.get(
                "summary", {}
            ).get("allFourBoxPopulatedPdfCount"),
            "allFourComponentPresentPdfCount": current_pdf_ocr_document_order.get(
                "summary", {}
            ).get("allFourComponentPresentPdfCount"),
            "componentOrderMatchesActiveOrderPdfCount": current_pdf_ocr_document_order.get(
                "summary", {}
            ).get("componentOrderMatchesActiveOrderPdfCount"),
            "strictNearActiveBoxCount": current_pdf_ocr_document_order.get(
                "summary", {}
            ).get("strictNearActiveBoxCount"),
            "hiddenOcrOrderCandidateCount": current_pdf_ocr_document_order.get(
                "summary", {}
            ).get("hiddenOcrOrderCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_ocr_document_order.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ocr_document_order.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ocr_document_order.get("summary", {}).get(
                "triggerCount"
            ),
            "pdfOcrDocumentOrderFingerprint": current_pdf_ocr_document_order.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_ocr_document_order.get("sheet"),
        },
        "currentPdfOcrOverdoseIndexOffsetGate": {
            "decision": current_pdf_ocr_overdose_index_offset.get("decision", {}).get(
                "currentPdfOcrOverdoseIndexOffsetGate"
            ),
            "pdfCount": current_pdf_ocr_overdose_index_offset.get("summary", {}).get(
                "pdfCount"
            ),
            "overdosePdfCount": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("overdosePdfCount"),
            "offsetRowsChecked": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("offsetRowsChecked"),
            "targetOffsetHitCount": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("targetOffsetHitCount"),
            "strictOffsetHitCount": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("strictOffsetHitCount"),
            "allFourDeltaKnownUnitPdfCount": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("allFourDeltaKnownUnitPdfCount"),
            "hiddenOverdoseIndexCandidateCount": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("hiddenOverdoseIndexCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("triggerCount"),
            "pdfOcrOverdoseIndexOffsetFingerprint": current_pdf_ocr_overdose_index_offset.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_ocr_overdose_index_offset.get("sheet"),
        },
        "currentPdfOcrOverdoseNeighborhoodGate": {
            "decision": current_pdf_ocr_overdose_neighborhood.get("decision", {}).get(
                "currentPdfOcrOverdoseNeighborhoodGate"
            ),
            "pdfCount": current_pdf_ocr_overdose_neighborhood.get("summary", {}).get(
                "pdfCount"
            ),
            "overdosePdfCount": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("overdosePdfCount"),
            "overdoseWordCount": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("overdoseWordCount"),
            "neighborhoodRowsChecked": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("neighborhoodRowsChecked"),
            "strictNeighborhoodRowCount": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("strictNeighborhoodRowCount"),
            "targetNeighborhoodRowCount": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("targetNeighborhoodRowCount"),
            "allFourNeighborhoodRowCount": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("allFourNeighborhoodRowCount"),
            "hiddenOverdoseNeighborhoodCandidateCount": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("hiddenOverdoseNeighborhoodCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("triggerCount"),
            "pdfOcrOverdoseNeighborhoodFingerprint": current_pdf_ocr_overdose_neighborhood.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_ocr_overdose_neighborhood.get("sheet"),
        },
        "currentPdfOcrPageHeaderSequenceGate": {
            "decision": current_pdf_ocr_page_header_sequence.get("decision", {}).get(
                "currentPdfOcrPageHeaderSequenceGate"
            ),
            "pdfCount": current_pdf_ocr_page_header_sequence.get("summary", {}).get(
                "pdfCount"
            ),
            "pageRowsChecked": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("pageRowsChecked"),
            "page76OverdoseHeaderPdfCount": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("page76OverdoseHeaderPdfCount"),
            "strictPageStartRowCount": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("strictPageStartRowCount"),
            "targetPageStartRowCount": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("targetPageStartRowCount"),
            "allFourPageStartRowCount": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("allFourPageStartRowCount"),
            "pageHeaderSequenceCandidateCount": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("pageHeaderSequenceCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("triggerCount"),
            "pdfOcrPageHeaderSequenceFingerprint": current_pdf_ocr_page_header_sequence.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_ocr_page_header_sequence.get("sheet"),
        },
        "currentPdfVisualHeaderFooterBandSequenceGate": {
            "decision": current_pdf_visual_header_footer_band_sequence.get(
                "decision", {}
            ).get("currentPdfVisualHeaderFooterBandSequenceGate"),
            "pdfCount": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("pdfCount"),
            "pageRowsChecked": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("pageRowsChecked"),
            "bandRowsChecked": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("bandRowsChecked"),
            "ocrOverdoseStartRowCount": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("ocrOverdoseStartRowCount"),
            "page76TopNearMatchCount": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("page76TopNearMatchCount"),
            "page76BottomNearMatchCount": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("page76BottomNearMatchCount"),
            "visualHeaderFooterSequenceCandidateCount": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("visualHeaderFooterSequenceCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("triggerCount"),
            "visualHeaderFooterBandFingerprint": current_pdf_visual_header_footer_band_sequence.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_visual_header_footer_band_sequence.get("sheet"),
        },
        "currentPdfRepeatedOverdoseHeaderLaneGate": {
            "decision": current_pdf_repeated_overdose_header_lane.get(
                "decision", {}
            ).get("currentPdfRepeatedOverdoseHeaderLaneGate"),
            "pdfCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("pdfCount"),
            "overdoseHeaderRowCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("overdoseHeaderRowCount"),
            "laneRowsChecked": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("laneRowsChecked"),
            "targetLaneRowCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("targetLaneRowCount"),
            "strictLaneRowCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("strictLaneRowCount"),
            "allFourLaneRowCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("allFourLaneRowCount"),
            "activeOrderLaneRowCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("activeOrderLaneRowCount"),
            "page76TargetLaneRowCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("page76TargetLaneRowCount"),
            "headerLaneCandidateCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("headerLaneCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("triggerCount"),
            "repeatedOverdoseHeaderLaneFingerprint": current_pdf_repeated_overdose_header_lane.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_repeated_overdose_header_lane.get("sheet"),
        },
        "currentPdfOverdoseHeaderDeltaTransferGate": {
            "decision": current_pdf_overdose_header_delta_transfer.get(
                "decision", {}
            ).get("currentPdfOverdoseHeaderDeltaTransferGate"),
            "pdfCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("pdfCount"),
            "overdoseHeaderRowCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("overdoseHeaderRowCount"),
            "transferVariantRowCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("transferVariantRowCount"),
            "transferBoxRowCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("transferBoxRowCount"),
            "textHitBoxRowCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("textHitBoxRowCount"),
            "targetTermBoxRowCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("targetTermBoxRowCount"),
            "strictTermBoxRowCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("strictTermBoxRowCount"),
            "allFourTransferVariantCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("allFourTransferVariantCount"),
            "activeOrderTransferVariantCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("activeOrderTransferVariantCount"),
            "headerDeltaTransferCandidateCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("headerDeltaTransferCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("triggerCount"),
            "overdoseHeaderDeltaTransferFingerprint": current_pdf_overdose_header_delta_transfer.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_overdose_header_delta_transfer.get("sheet"),
        },
        "currentPdfOverdoseBodyStartVectorGate": {
            "decision": current_pdf_overdose_body_start_vector.get(
                "decision", {}
            ).get("currentPdfOverdoseBodyStartVectorGate"),
            "pdfCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("pdfCount"),
            "overdoseHeaderRowCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("overdoseHeaderRowCount"),
            "bodyStartRowCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("bodyStartRowCount"),
            "bodyVectorRowCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("bodyVectorRowCount"),
            "targetVectorRowCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("targetVectorRowCount"),
            "strictVectorRowCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("strictVectorRowCount"),
            "allFourVectorRowCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("allFourVectorRowCount"),
            "activeOrderVectorRowCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("activeOrderVectorRowCount"),
            "bodyStartVectorCandidateCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("bodyStartVectorCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("triggerCount"),
            "overdoseBodyStartVectorFingerprint": current_pdf_overdose_body_start_vector.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_overdose_body_start_vector.get("sheet"),
        },
        "currentPdfOverdoseBodyBasisReflectionGate": {
            "decision": current_pdf_overdose_body_basis_reflection.get(
                "decision", {}
            ).get("currentPdfOverdoseBodyBasisReflectionGate"),
            "pdfCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("pdfCount"),
            "bodyBasisRowCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("bodyBasisRowCount"),
            "transformVariantRowCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("transformVariantRowCount"),
            "reflectedBoxRowCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("reflectedBoxRowCount"),
            "inPageReflectedBoxCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("inPageReflectedBoxCount"),
            "textHitBoxRowCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("textHitBoxRowCount"),
            "targetTermBoxRowCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("targetTermBoxRowCount"),
            "strictTermBoxRowCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("strictTermBoxRowCount"),
            "allFourTransformVariantCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("allFourTransformVariantCount"),
            "activeOrderTransformVariantCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("activeOrderTransformVariantCount"),
            "bodyBasisReflectionCandidateCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("bodyBasisReflectionCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("triggerCount"),
            "overdoseBodyBasisReflectionFingerprint": current_pdf_overdose_body_basis_reflection.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_overdose_body_basis_reflection.get("sheet"),
        },
        "currentPdfOverdoseBodyLatticeGate": {
            "decision": current_pdf_overdose_body_lattice.get("decision", {}).get(
                "currentPdfOverdoseBodyLatticeGate"
            ),
            "pdfCount": current_pdf_overdose_body_lattice.get("summary", {}).get(
                "pdfCount"
            ),
            "bodyLatticePageCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("bodyLatticePageCount"),
            "mappedTargetRowCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("mappedTargetRowCount"),
            "ownTargetLineHitCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("ownTargetLineHitCount"),
            "strictMappedLineCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("strictMappedLineCount"),
            "allFourOwnTargetVariantCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("allFourOwnTargetVariantCount"),
            "activeRowOrderVariantCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("activeRowOrderVariantCount"),
            "bodyLatticeCandidateCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("bodyLatticeCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("triggerCount"),
            "overdoseBodyLatticeFingerprint": current_pdf_overdose_body_lattice.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_overdose_body_lattice.get("sheet"),
        },
        "currentPdfOverdoseBodyOffsetTransferGate": {
            "decision": current_pdf_overdose_body_offset_transfer.get("decision", {}).get(
                "currentPdfOverdoseBodyOffsetTransferGate"
            ),
            "pdfCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("pdfCount"),
            "overdoseHeaderRowCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("overdoseHeaderRowCount"),
            "bodyOffsetPageCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("bodyOffsetPageCount"),
            "sourceOffsetRowCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("sourceOffsetRowCount"),
            "transferredOffsetRowCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("transferredOffsetRowCount"),
            "ownTargetOffsetHitCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("ownTargetOffsetHitCount"),
            "strictOffsetRowCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("strictOffsetRowCount"),
            "allFourOwnTargetPageCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("allFourOwnTargetPageCount"),
            "activeTargetOrderPageCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("activeTargetOrderPageCount"),
            "bodyOffsetCandidateCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("bodyOffsetCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("triggerCount"),
            "overdoseBodyOffsetTransferFingerprint": current_pdf_overdose_body_offset_transfer.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_overdose_body_offset_transfer.get("sheet"),
        },
        "currentPdfOverdoseBodyOffsetColumnGate": {
            "decision": current_pdf_overdose_body_offset_column.get("decision", {}).get(
                "currentPdfOverdoseBodyOffsetColumnGate"
            ),
            "pdfCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("pdfCount"),
            "overdoseHeaderRowCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("overdoseHeaderRowCount"),
            "sourcePointRowCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("sourcePointRowCount"),
            "columnLandingPageCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("columnLandingPageCount"),
            "landedWordRowCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("landedWordRowCount"),
            "targetWordHitCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("targetWordHitCount"),
            "ownTargetWordHitCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("ownTargetWordHitCount"),
            "strictWordHitCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("strictWordHitCount"),
            "allFourOwnTargetPageCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("allFourOwnTargetPageCount"),
            "activeWordTargetOrderPageCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("activeWordTargetOrderPageCount"),
            "bodyOffsetColumnCandidateCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("bodyOffsetColumnCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("triggerCount"),
            "overdoseBodyOffsetColumnFingerprint": current_pdf_overdose_body_offset_column.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_overdose_body_offset_column.get("sheet"),
        },
        "currentPdfOverdoseBodyFractionColumnGate": {
            "decision": current_pdf_overdose_body_fraction_column.get("decision", {}).get(
                "currentPdfOverdoseBodyFractionColumnGate"
            ),
            "pdfCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("pdfCount"),
            "overdoseHeaderRowCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("overdoseHeaderRowCount"),
            "sourceFractionRowCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("sourceFractionRowCount"),
            "fractionLandingPageCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("fractionLandingPageCount"),
            "landedWordRowCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("landedWordRowCount"),
            "targetWordHitCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("targetWordHitCount"),
            "ownTargetWordHitCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("ownTargetWordHitCount"),
            "strictWordHitCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("strictWordHitCount"),
            "allFourOwnTargetPageCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("allFourOwnTargetPageCount"),
            "activeWordTargetOrderPageCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("activeWordTargetOrderPageCount"),
            "bodyFractionColumnCandidateCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("bodyFractionColumnCandidateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("triggerCount"),
            "overdoseBodyFractionColumnFingerprint": current_pdf_overdose_body_fraction_column.get(
                "summary", {}
            ).get("fingerprint"),
            "sheet": current_pdf_overdose_body_fraction_column.get("sheet"),
        },
        "currentPdfOcrAffineAlignmentGate": {
            "decision": current_pdf_ocr_affine_alignment.get("decision", {}).get(
                "currentPdfOcrAffineAlignmentGate"
            ),
            "fitAvailableCount": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("fitAvailableCount"),
            "totalTokenPairCount": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("totalTokenPairCount"),
            "totalInlierCount": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("totalInlierCount"),
            "targetWordHitRowCount": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("targetWordHitRowCount"),
            "targetExactComponentRowCount": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("targetExactComponentRowCount"),
            "targetStrictInstructionRowCount": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("targetStrictInstructionRowCount"),
            "strictInstructionTermsAfterAlignment": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("strictInstructionTermsAfterAlignment"),
            "minimumComponentDistanceToOwnTargetBoxPx": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("minimumComponentDistanceToOwnTargetBoxPx"),
            "sourceBackedR3BridgeHitCount": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("triggerCount"),
            "pdfOcrAffineAlignmentFingerprint": current_pdf_ocr_affine_alignment.get(
                "summary", {}
            ).get("pdfOcrAffineAlignmentFingerprint"),
            "sheet": current_pdf_ocr_affine_alignment.get("sheet"),
        },
        "currentPdfRenderAlignmentDeltaGate": {
            "decision": current_pdf_render_alignment_delta.get("decision", {}).get(
                "currentPdfRenderAlignmentDeltaGate"
            ),
            "duplicateImageShaGroupCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("duplicateImageShaGroupCount"),
            "nonBaselinePdfCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("nonBaselinePdfCount"),
            "activeTargetMaterialResidualCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("activeTargetMaterialResidualCount"),
            "activeTargetStateMismatchCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("activeTargetStateMismatchCount"),
            "materialResidualRegionCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("materialResidualRegionCount"),
            "stateMismatchRegionCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("stateMismatchRegionCount"),
            "expectedStateMismatchRegionCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("expectedStateMismatchRegionCount"),
            "maxMeanAbsDiff": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("maxMeanAbsDiff"),
            "maxLargeResidualRatio": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("maxLargeResidualRatio"),
            "sourceBackedR3BridgeHitCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("triggerCount"),
            "pdfRenderAlignmentDeltaFingerprint": current_pdf_render_alignment_delta.get(
                "summary", {}
            ).get("pdfRenderAlignmentDeltaFingerprint"),
            "sheet": current_pdf_render_alignment_delta.get("sheet"),
        },
        "currentPdfRenderResolutionInvarianceGate": {
            "decision": current_pdf_render_resolution_invariance.get("decision", {}).get(
                "currentPdfRenderResolutionInvarianceGate"
            ),
            "pdfCount": current_pdf_render_resolution_invariance.get("summary", {}).get(
                "pdfCount"
            ),
            "zoomCount": current_pdf_render_resolution_invariance.get("summary", {}).get(
                "zoomCount"
            ),
            "renderRowCount": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("renderRowCount"),
            "comparisonRowCount": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("comparisonRowCount"),
            "activeRegionRowCount": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("activeRegionRowCount"),
            "overdoseSlotRegionRowCount": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("overdoseSlotRegionRowCount"),
            "activeOutlierCount": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("activeOutlierCount"),
            "allFourActiveOutlierComparisonCount": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("allFourActiveOutlierComparisonCount"),
            "maxActiveMeanAbsDelta": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("maxActiveMeanAbsDelta"),
            "maxControlMeanAbsDelta": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("maxControlMeanAbsDelta"),
            "maxOverdoseSlotMeanAbsDelta": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("maxOverdoseSlotMeanAbsDelta"),
            "sourceBackedR3BridgeHitCount": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("triggerCount"),
            "renderResolutionInvarianceFingerprint": current_pdf_render_resolution_invariance.get(
                "summary", {}
            ).get("renderResolutionInvarianceFingerprint"),
            "sheet": current_pdf_render_resolution_invariance.get("sheet"),
        },
        "currentPdfActiveRegionRenderEmbeddedIdentityGate": {
            "decision": current_pdf_render_embedded_identity.get("decision", {}).get(
                "currentPdfActiveRegionRenderEmbeddedIdentityGate"
            ),
            "pdfCount": current_pdf_render_embedded_identity.get("summary", {}).get(
                "pdfCount"
            ),
            "measuredRegionCount": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("measuredRegionCount"),
            "activeRenderEmbeddedMismatchCount": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("activeRenderEmbeddedMismatchCount"),
            "allFourActiveMismatchPdfCount": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("allFourActiveMismatchPdfCount"),
            "overdoseSlotRenderEmbeddedMismatchCount": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("overdoseSlotRenderEmbeddedMismatchCount"),
            "controlRenderEmbeddedMismatchCount": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("controlRenderEmbeddedMismatchCount"),
            "maxActiveRenderEmbeddedMeanAbsDiff": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("maxActiveRenderEmbeddedMeanAbsDiff"),
            "maxOverdoseSlotRenderEmbeddedMeanAbsDiff": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("maxOverdoseSlotRenderEmbeddedMeanAbsDiff"),
            "sourceBackedR3BridgeHitCount": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("triggerCount"),
            "renderEmbeddedIdentityFingerprint": current_pdf_render_embedded_identity.get(
                "summary", {}
            ).get("renderEmbeddedIdentityFingerprint"),
            "sheet": current_pdf_render_embedded_identity.get("sheet"),
        },
        "currentScanJpegBlockGridGate": {
            "decision": current_scan_jpeg_block_grid.get("decision", {}).get(
                "currentScanJpegBlockGridGate"
            ),
            "activeBoxCount": current_scan_jpeg_block_grid.get("summary", {}).get(
                "activeBoxCount"
            ),
            "shiftedControlBoxCount": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("shiftedControlBoxCount"),
            "overdoseSlotBoxCount": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("overdoseSlotBoxCount"),
            "activeStrictEdgeHitCount": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("activeStrictEdgeHitCount"),
            "controlStrictEdgeHitCount": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("controlStrictEdgeHitCount"),
            "overdoseSlotStrictEdgeHitCount": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("overdoseSlotStrictEdgeHitCount"),
            "activeBoundaryRatioOutlierCount": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("activeBoundaryRatioOutlierCount"),
            "allFourActiveBoundaryRatioOutlier": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("allFourActiveBoundaryRatioOutlier"),
            "maxActiveBoundaryRatio": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("maxActiveBoundaryRatio"),
            "maxControlBoundaryRatio": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("maxControlBoundaryRatio"),
            "maxOverdoseSlotBoundaryRatio": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("maxOverdoseSlotBoundaryRatio"),
            "sourceBackedR3BridgeHitCount": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_jpeg_block_grid.get("summary", {}).get(
                "triggerCount"
            ),
            "jpegBlockGridFingerprint": current_scan_jpeg_block_grid.get(
                "summary", {}
            ).get("jpegBlockGridFingerprint"),
            "sheet": current_scan_jpeg_block_grid.get("sheet"),
        },
        "currentScanHalftoneScreenGate": {
            "decision": current_scan_halftone_screen.get("decision", {}).get(
                "currentScanHalftoneScreenGate"
            ),
            "activeBoxCount": current_scan_halftone_screen.get("summary", {}).get(
                "activeBoxCount"
            ),
            "shiftedControlBoxCount": current_scan_halftone_screen.get(
                "summary", {}
            ).get("shiftedControlBoxCount"),
            "overdoseSlotBoxCount": current_scan_halftone_screen.get(
                "summary", {}
            ).get("overdoseSlotBoxCount"),
            "activeDominantShareOutlierCount": current_scan_halftone_screen.get(
                "summary", {}
            ).get("activeDominantShareOutlierCount"),
            "activeHighpassRmsOutlierCount": current_scan_halftone_screen.get(
                "summary", {}
            ).get("activeHighpassRmsOutlierCount"),
            "allFourActiveDominantShareOutlier": current_scan_halftone_screen.get(
                "summary", {}
            ).get("allFourActiveDominantShareOutlier"),
            "allFourActiveHighpassRmsOutlier": current_scan_halftone_screen.get(
                "summary", {}
            ).get("allFourActiveHighpassRmsOutlier"),
            "activeCommonDominantAngleBin": current_scan_halftone_screen.get(
                "summary", {}
            ).get("activeCommonDominantAngleBin"),
            "controlCommonDominantAngleBinMatchCount": current_scan_halftone_screen.get(
                "summary", {}
            ).get("controlCommonDominantAngleBinMatchCount"),
            "overdoseSlotCommonDominantAngleBinMatchCount": current_scan_halftone_screen.get(
                "summary", {}
            ).get("overdoseSlotCommonDominantAngleBinMatchCount"),
            "maxActiveDominantShare": current_scan_halftone_screen.get(
                "summary", {}
            ).get("maxActiveDominantShare"),
            "maxControlDominantShare": current_scan_halftone_screen.get(
                "summary", {}
            ).get("maxControlDominantShare"),
            "maxActiveHighpassRms": current_scan_halftone_screen.get(
                "summary", {}
            ).get("maxActiveHighpassRms"),
            "maxControlHighpassRms": current_scan_halftone_screen.get(
                "summary", {}
            ).get("maxControlHighpassRms"),
            "sourceBackedR3BridgeHitCount": current_scan_halftone_screen.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_halftone_screen.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_halftone_screen.get("summary", {}).get(
                "triggerCount"
            ),
            "halftoneScreenFingerprint": current_scan_halftone_screen.get(
                "summary", {}
            ).get("halftoneScreenFingerprint"),
            "sheet": current_scan_halftone_screen.get("sheet"),
        },
        "currentScanRgbRegistrationGate": {
            "decision": current_scan_rgb_registration.get("decision", {}).get(
                "currentScanRgbRegistrationGate"
            ),
            "activeBoxCount": current_scan_rgb_registration.get("summary", {}).get(
                "activeBoxCount"
            ),
            "shiftedControlBoxCount": current_scan_rgb_registration.get(
                "summary", {}
            ).get("shiftedControlBoxCount"),
            "overdoseSlotBoxCount": current_scan_rgb_registration.get(
                "summary", {}
            ).get("overdoseSlotBoxCount"),
            "reliableActiveBoxCount": current_scan_rgb_registration.get(
                "summary", {}
            ).get("reliableActiveBoxCount"),
            "activeNonzeroRegistrationRowCount": current_scan_rgb_registration.get(
                "summary", {}
            ).get("activeNonzeroRegistrationRowCount"),
            "activeConfidenceOutlierCount": current_scan_rgb_registration.get(
                "summary", {}
            ).get("activeConfidenceOutlierCount"),
            "allFourActiveNonzeroRegistration": current_scan_rgb_registration.get(
                "summary", {}
            ).get("allFourActiveNonzeroRegistration"),
            "allFourActiveConfidenceOutlier": current_scan_rgb_registration.get(
                "summary", {}
            ).get("allFourActiveConfidenceOutlier"),
            "activeCommonShiftSignature": current_scan_rgb_registration.get(
                "summary", {}
            ).get("activeCommonShiftSignature"),
            "controlCommonShiftSignatureMatchCount": current_scan_rgb_registration.get(
                "summary", {}
            ).get("controlCommonShiftSignatureMatchCount"),
            "overdoseSlotCommonShiftSignatureMatchCount": current_scan_rgb_registration.get(
                "summary", {}
            ).get("overdoseSlotCommonShiftSignatureMatchCount"),
            "maxActiveShiftMagnitude": current_scan_rgb_registration.get(
                "summary", {}
            ).get("maxActiveShiftMagnitude"),
            "maxControlShiftMagnitude": current_scan_rgb_registration.get(
                "summary", {}
            ).get("maxControlShiftMagnitude"),
            "maxOverdoseSlotShiftMagnitude": current_scan_rgb_registration.get(
                "summary", {}
            ).get("maxOverdoseSlotShiftMagnitude"),
            "maxActiveConfidenceGain": current_scan_rgb_registration.get(
                "summary", {}
            ).get("maxActiveConfidenceGain"),
            "maxControlConfidenceGain": current_scan_rgb_registration.get(
                "summary", {}
            ).get("maxControlConfidenceGain"),
            "maxOverdoseSlotConfidenceGain": current_scan_rgb_registration.get(
                "summary", {}
            ).get("maxOverdoseSlotConfidenceGain"),
            "sourceBackedR3BridgeHitCount": current_scan_rgb_registration.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_rgb_registration.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_rgb_registration.get("summary", {}).get(
                "triggerCount"
            ),
            "rgbRegistrationFingerprint": current_scan_rgb_registration.get(
                "summary", {}
            ).get("rgbRegistrationFingerprint"),
            "sheet": current_scan_rgb_registration.get("sheet"),
        },
        "currentScanLuminanceBitplaneGate": {
            "decision": current_scan_luminance_bitplane.get("decision", {}).get(
                "currentScanLuminanceBitplaneGate"
            ),
            "activeBoxCount": current_scan_luminance_bitplane.get("summary", {}).get(
                "activeBoxCount"
            ),
            "shiftedControlBoxCount": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("shiftedControlBoxCount"),
            "overdoseSlotBoxCount": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("overdoseSlotBoxCount"),
            "activeLowBitOutlierCount": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("activeLowBitOutlierCount"),
            "activeThresholdOutlierCount": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("activeThresholdOutlierCount"),
            "allFourActiveLowBitOutlier": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("allFourActiveLowBitOutlier"),
            "allFourActiveThresholdOutlier": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("allFourActiveThresholdOutlier"),
            "activeCommonLowBitSignature": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("activeCommonLowBitSignature"),
            "sharedActiveLowBitCarrier": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("sharedActiveLowBitCarrier"),
            "hiddenBitplaneCandidate": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("hiddenBitplaneCandidate"),
            "maxActiveLowBitAbsZ": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("maxActiveLowBitAbsZ"),
            "maxControlLowBitAbsZ": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("maxControlLowBitAbsZ"),
            "maxOverdoseSlotLowBitAbsZ": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("maxOverdoseSlotLowBitAbsZ"),
            "maxActiveThresholdAbsZ": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("maxActiveThresholdAbsZ"),
            "maxControlThresholdAbsZ": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("maxControlThresholdAbsZ"),
            "maxOverdoseSlotThresholdAbsZ": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("maxOverdoseSlotThresholdAbsZ"),
            "sourceBackedR3BridgeHitCount": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_luminance_bitplane.get("summary", {}).get(
                "triggerCount"
            ),
            "luminanceBitplaneFingerprint": current_scan_luminance_bitplane.get(
                "summary", {}
            ).get("luminanceBitplaneFingerprint"),
            "sheet": current_scan_luminance_bitplane.get("sheet"),
        },
        "currentScanThresholdMorphologyGate": {
            "decision": current_scan_threshold_morphology.get("decision", {}).get(
                "currentScanThresholdMorphologyGate"
            ),
            "activeBoxCount": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("activeBoxCount"),
            "shiftedControlBoxCount": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("shiftedControlBoxCount"),
            "overdoseSlotBoxCount": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("overdoseSlotBoxCount"),
            "activeMorphologyOutlierCount": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("activeMorphologyOutlierCount"),
            "allFourActiveMorphologyOutlier": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("allFourActiveMorphologyOutlier"),
            "activeCommonMorphologySignature": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("activeCommonMorphologySignature"),
            "sharedActiveMorphologyCarrier": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("sharedActiveMorphologyCarrier"),
            "hiddenMorphologyCandidate": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("hiddenMorphologyCandidate"),
            "maxActiveMorphologyAbsZ": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("maxActiveMorphologyAbsZ"),
            "maxControlMorphologyAbsZ": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("maxControlMorphologyAbsZ"),
            "maxOverdoseSlotMorphologyAbsZ": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("maxOverdoseSlotMorphologyAbsZ"),
            "sourceBackedR3BridgeHitCount": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("triggerCount"),
            "thresholdMorphologyFingerprint": current_scan_threshold_morphology.get(
                "summary", {}
            ).get("thresholdMorphologyFingerprint"),
            "sheet": current_scan_threshold_morphology.get("sheet"),
        },
        "currentScanHighlightEdgeHaloGate": {
            "decision": current_scan_highlight_edge_halo.get("decision", {}).get(
                "currentScanHighlightEdgeHaloGate"
            ),
            "activeBoxCount": current_scan_highlight_edge_halo.get("summary", {}).get(
                "activeBoxCount"
            ),
            "shiftedControlBoxCount": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("shiftedControlBoxCount"),
            "overdoseSlotBoxCount": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("overdoseSlotBoxCount"),
            "activeHaloOutlierCount": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("activeHaloOutlierCount"),
            "allFourActiveHaloOutlier": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("allFourActiveHaloOutlier"),
            "activeCommonHaloSignature": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("activeCommonHaloSignature"),
            "activeCommonEdgeBiasSignature": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("activeCommonEdgeBiasSignature"),
            "sharedActiveHaloCarrier": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("sharedActiveHaloCarrier"),
            "hiddenHaloCandidate": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("hiddenHaloCandidate"),
            "maxActiveHaloAbsZ": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("maxActiveHaloAbsZ"),
            "maxControlHaloAbsZ": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("maxControlHaloAbsZ"),
            "maxOverdoseSlotHaloAbsZ": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("maxOverdoseSlotHaloAbsZ"),
            "sourceBackedR3BridgeHitCount": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_highlight_edge_halo.get("summary", {}).get(
                "triggerCount"
            ),
            "highlightEdgeHaloFingerprint": current_scan_highlight_edge_halo.get(
                "summary", {}
            ).get("highlightEdgeHaloFingerprint"),
            "sheet": current_scan_highlight_edge_halo.get("sheet"),
        },
        "currentScanSlotBoundaryResidualGate": {
            "decision": current_scan_slot_boundary_residual.get("decision", {}).get(
                "currentScanSlotBoundaryResidualGate"
            ),
            "activeBoxCount": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("activeBoxCount"),
            "highlightControlBoxCount": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("highlightControlBoxCount"),
            "verticalShiftControlBoxCount": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("verticalShiftControlBoxCount"),
            "allFourActiveAnyAnchorClose16": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("allFourActiveAnyAnchorClose16"),
            "allFourActiveLeftBoundaryClose16": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("allFourActiveLeftBoundaryClose16"),
            "allFourActiveCenterClose16": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("allFourActiveCenterClose16"),
            "allFourActiveRightBoundaryClose16": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("allFourActiveRightBoundaryClose16"),
            "activeCommonSlotBoundarySignature": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("activeCommonSlotBoundarySignature"),
            "activeNearestCenterStreams": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("activeNearestCenterStreams"),
            "activeNearestBoundaryStreams": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("activeNearestBoundaryStreams"),
            "meanActiveAnchorResidualPx": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("meanActiveAnchorResidualPx"),
            "meanHighlightControlAnchorResidualPx": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("meanHighlightControlAnchorResidualPx"),
            "sharedActiveSlotBoundaryCarrier": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("sharedActiveSlotBoundaryCarrier"),
            "hiddenSlotBoundaryCandidate": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("hiddenSlotBoundaryCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_slot_boundary_residual.get("summary", {}).get(
                "triggerCount"
            ),
            "slotBoundaryResidualFingerprint": current_scan_slot_boundary_residual.get(
                "summary", {}
            ).get("slotBoundaryResidualFingerprint"),
            "sheet": current_scan_slot_boundary_residual.get("sheet"),
        },
        "currentScanActiveEnvelopeTransformGate": {
            "decision": current_scan_active_envelope_transform.get("decision", {}).get(
                "currentScanActiveEnvelopeTransformGate"
            ),
            "activeBoxCount": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("activeBoxCount"),
            "highlightControlBoxCount": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("highlightControlBoxCount"),
            "activeEnvelopeBox": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("activeEnvelopeBox"),
            "activeEnvelopeCenter": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("activeEnvelopeCenter"),
            "transformNames": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("transformNames"),
            "bestActiveOtherHitCount32": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("bestActiveOtherHitCount32"),
            "bestActiveOtherHitCount64": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("bestActiveOtherHitCount64"),
            "bestTransformByActiveOther64": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("bestTransformByActiveOther64"),
            "anyTransformAllFourActiveAny32": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("anyTransformAllFourActiveAny32"),
            "anyTransformAllFourActiveAny64": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("anyTransformAllFourActiveAny64"),
            "anyTransformAllFourActiveOther32": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("anyTransformAllFourActiveOther32"),
            "anyTransformAllFourActiveOther64": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("anyTransformAllFourActiveOther64"),
            "hiddenEnvelopeTransformCandidate": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("hiddenEnvelopeTransformCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_active_envelope_transform.get("summary", {}).get(
                "triggerCount"
            ),
            "activeEnvelopeTransformFingerprint": current_scan_active_envelope_transform.get(
                "summary", {}
            ).get("activeEnvelopeTransformFingerprint"),
            "sheet": current_scan_active_envelope_transform.get("sheet"),
        },
        "currentScanBackgroundSeamResidualGate": {
            "decision": current_scan_background_seam_residual.get("decision"),
            "pageCount": current_scan_background_seam_residual.get("summary", {}).get(
                "pageCount"
            ),
            "activeBoxCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("activeBoxCount"),
            "highlightControlBoxCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("highlightControlBoxCount"),
            "overdoseSlotBoxCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("overdoseSlotBoxCount"),
            "page76StructuralVerticalCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("page76StructuralVerticalCount"),
            "page76StructuralHorizontalCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("page76StructuralHorizontalCount"),
            "page76UniqueVerticalCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("page76UniqueVerticalCount"),
            "page76UniqueHorizontalCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("page76UniqueHorizontalCount"),
            "activeCloseX16Count": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("activeCloseX16Count"),
            "activeCloseY16Count": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("activeCloseY16Count"),
            "controlCloseX16Count": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("controlCloseX16Count"),
            "controlCloseY16Count": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("controlCloseY16Count"),
            "overdoseSlotCloseX16Count": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("overdoseSlotCloseX16Count"),
            "overdoseSlotCloseY16Count": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("overdoseSlotCloseY16Count"),
            "allFourActiveCloseX16": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("allFourActiveCloseX16"),
            "allFourActiveCloseY16": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("allFourActiveCloseY16"),
            "sharedActiveVerticalLineHitCount16": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("sharedActiveVerticalLineHitCount16"),
            "sharedActiveHorizontalLineHitCount16": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("sharedActiveHorizontalLineHitCount16"),
            "seamResidualCandidate": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("seamResidualCandidate"),
            "hiddenBackgroundSeamCandidate": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("hiddenBackgroundSeamCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("triggerCount"),
            "backgroundSeamResidualFingerprint": current_scan_background_seam_residual.get(
                "summary", {}
            ).get("backgroundSeamResidualFingerprint"),
            "sheet": current_scan_background_seam_residual.get("sheet"),
        },
        "currentScanPaperTextureDuplexGate": {
            "decision": current_scan_paper_texture_duplex.get("decision"),
            "physicalPairCount": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("physicalPairCount"),
            "controlPairCount": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("controlPairCount"),
            "transformCount": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("transformCount"),
            "rowCount": current_scan_paper_texture_duplex.get("summary", {}).get(
                "rowCount"
            ),
            "physicalMirrorBestPairCount": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("physicalMirrorBestPairCount"),
            "physicalMirrorAboveControlP95Count": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("physicalMirrorAboveControlP95Count"),
            "controlCorrelationP95": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("controlCorrelationP95"),
            "maxPhysicalMirrorCorrelation": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("maxPhysicalMirrorCorrelation"),
            "maxControlCorrelation": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("maxControlCorrelation"),
            "physicalPairBestTransforms": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("physicalPairBestTransforms"),
            "paperDuplexSelectorCandidate": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("paperDuplexSelectorCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_paper_texture_duplex.get("summary", {}).get(
                "triggerCount"
            ),
            "paperTextureDuplexFingerprint": current_scan_paper_texture_duplex.get(
                "summary", {}
            ).get("paperTextureDuplexFingerprint"),
            "sheet": current_scan_paper_texture_duplex.get("sheet"),
        },
        "currentScanPaperTextureShiftGate": {
            "decision": current_scan_paper_texture_shift.get("decision"),
            "physicalPairCount": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("physicalPairCount"),
            "controlPairCount": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("controlPairCount"),
            "shiftCount": current_scan_paper_texture_shift.get("summary", {}).get(
                "shiftCount"
            ),
            "rowCount": current_scan_paper_texture_shift.get("summary", {}).get(
                "rowCount"
            ),
            "physicalBestAboveControlBestP95Count": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("physicalBestAboveControlBestP95Count"),
            "physicalBestAtSmallShiftCount": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("physicalBestAtSmallShiftCount"),
            "physicalZeroShiftAboveControlBestP95Count": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("physicalZeroShiftAboveControlBestP95Count"),
            "controlBestCorrelationP95": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("controlBestCorrelationP95"),
            "maxPhysicalBestCorrelation": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("maxPhysicalBestCorrelation"),
            "maxControlBestCorrelation": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("maxControlBestCorrelation"),
            "physicalBestShifts": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("physicalBestShifts"),
            "paperTextureShiftSelectorCandidate": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("paperTextureShiftSelectorCandidate"),
            "sourceBackedR3BridgeHitCount": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_scan_paper_texture_shift.get("summary", {}).get(
                "triggerCount"
            ),
            "paperTextureShiftFingerprint": current_scan_paper_texture_shift.get(
                "summary", {}
            ).get("paperTextureShiftFingerprint"),
            "sheet": current_scan_paper_texture_shift.get("sheet"),
        },
        "currentPdfActiveBoxCoordinateGridGate": {
            "decision": current_pdf_active_box_coordinate_grid.get("decision", {}).get(
                "currentPdfActiveBoxCoordinateGridGate"
            ),
            "pdfCount": current_pdf_active_box_coordinate_grid.get("summary", {}).get(
                "pdfCount"
            ),
            "activeRegionCount": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("activeRegionCount"),
            "highlightControlRegionCount": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("highlightControlRegionCount"),
            "overdoseSlotRegionCount": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("overdoseSlotRegionCount"),
            "gridNames": current_pdf_active_box_coordinate_grid.get("summary", {}).get(
                "gridNames"
            ),
            "anyAllFourActiveCenterClose05": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("anyAllFourActiveCenterClose05"),
            "anyAllFourActiveCenterClose12": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("anyAllFourActiveCenterClose12"),
            "anyAllFourActiveEdgesClose05": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("anyAllFourActiveEdgesClose05"),
            "anyAllFourActiveEdgesClose12": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("anyAllFourActiveEdgesClose12"),
            "bestActiveCenterClose05Count": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("bestActiveCenterClose05Count"),
            "bestActiveCenterClose12Count": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("bestActiveCenterClose12Count"),
            "bestControlCenterClose05Count": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("bestControlCenterClose05Count"),
            "bestControlCenterClose12Count": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("bestControlCenterClose12Count"),
            "bestGridRow": current_pdf_active_box_coordinate_grid.get("summary", {}).get(
                "bestGridRow"
            ),
            "gridAlignmentCandidate": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("gridAlignmentCandidate"),
            "hiddenPdfCoordinateCandidate": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("hiddenPdfCoordinateCandidate"),
            "sourceBackedR3BridgeHitCount": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_active_box_coordinate_grid.get("summary", {}).get(
                "triggerCount"
            ),
            "pdfCoordinateGridFingerprint": current_pdf_active_box_coordinate_grid.get(
                "summary", {}
            ).get("pdfCoordinateGridFingerprint"),
            "sheet": current_pdf_active_box_coordinate_grid.get("sheet"),
        },
        "currentPdfImageRectMarginPhaseGate": {
            "decision": current_pdf_image_rect_margin_phase.get("decision", {}).get(
                "currentPdfImageRectMarginPhaseGate"
            ),
            "pdfCount": current_pdf_image_rect_margin_phase.get("summary", {}).get(
                "pdfCount"
            ),
            "activeRegionCount": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("activeRegionCount"),
            "highlightControlRegionCount": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("highlightControlRegionCount"),
            "overdoseSlotRegionCount": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("overdoseSlotRegionCount"),
            "fractionRulers": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("fractionRulers"),
            "anyAllFourFraction001": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("anyAllFourFraction001"),
            "anyAllFourFraction0025": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("anyAllFourFraction0025"),
            "anyAllFourFraction005": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("anyAllFourFraction005"),
            "anyAllFourMargin025": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("anyAllFourMargin025"),
            "anyAllFourMargin050": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("anyAllFourMargin050"),
            "anyAllFourMargin100": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("anyAllFourMargin100"),
            "bestFractionActiveClose005Count": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("bestFractionActiveClose005Count"),
            "bestFractionControlClose005Count": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("bestFractionControlClose005Count"),
            "bestMarginActiveClose100Count": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("bestMarginActiveClose100Count"),
            "bestMarginControlClose100Count": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("bestMarginControlClose100Count"),
            "bestSummaryRow": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("bestSummaryRow"),
            "marginPhaseCandidate": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("marginPhaseCandidate"),
            "hiddenMarginPhaseCandidate": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("hiddenMarginPhaseCandidate"),
            "sourceBackedR3BridgeHitCount": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_image_rect_margin_phase.get("summary", {}).get(
                "triggerCount"
            ),
            "imageRectMarginPhaseFingerprint": current_pdf_image_rect_margin_phase.get(
                "summary", {}
            ).get("imageRectMarginPhaseFingerprint"),
            "sheet": current_pdf_image_rect_margin_phase.get("sheet"),
        },
        "localPdfFilesystemProvenanceGate": {
            "decision": local_pdf_filesystem_provenance.get("decision", {}).get(
                "localPdfFilesystemProvenanceGate"
            ),
            "pdfCount": local_pdf_filesystem_provenance.get("summary", {}).get(
                "pdfCount"
            ),
            "uniqueSha256Count": local_pdf_filesystem_provenance.get(
                "summary", {}
            ).get("uniqueSha256Count"),
            "duplicateHashGroupCount": local_pdf_filesystem_provenance.get(
                "summary", {}
            ).get("duplicateHashGroupCount"),
            "duplicateHashGroups": local_pdf_filesystem_provenance.get(
                "summary", {}
            ).get("duplicateHashGroups"),
            "whereFromRows": local_pdf_filesystem_provenance.get("summary", {}).get(
                "whereFromRows"
            ),
            "strictTermHitCount": local_pdf_filesystem_provenance.get(
                "summary", {}
            ).get("strictTermHitCount"),
            "originalLayoutTermHitCount": local_pdf_filesystem_provenance.get(
                "summary", {}
            ).get("originalLayoutTermHitCount"),
            "distinctOriginalLayoutCandidateCount": local_pdf_filesystem_provenance.get(
                "summary", {}
            ).get("distinctOriginalLayoutCandidateCount"),
            "sourceBackedR3BridgeHitCount": local_pdf_filesystem_provenance.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": local_pdf_filesystem_provenance.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": local_pdf_filesystem_provenance.get("summary", {}).get(
                "triggerCount"
            ),
            "filesystemProvenanceFingerprint": local_pdf_filesystem_provenance.get(
                "summary", {}
            ).get("filesystemProvenanceFingerprint"),
            "sheet": local_pdf_filesystem_provenance.get("sheet"),
        },
        "localPageRasterLineageGate": {
            "decision": local_page_raster_lineage.get("decision"),
            "pdfReferenceCount": local_page_raster_lineage.get("summary", {}).get(
                "pdfReferenceCount"
            ),
            "candidateCount": local_page_raster_lineage.get("summary", {}).get(
                "candidateCount"
            ),
            "nearDuplicateCount": local_page_raster_lineage.get("summary", {}).get(
                "nearDuplicateCount"
            ),
            "derivativeLikeCount": local_page_raster_lineage.get("summary", {}).get(
                "derivativeLikeCount"
            ),
            "distinctCandidateCount": local_page_raster_lineage.get("summary", {}).get(
                "distinctCandidateCount"
            ),
            "promotedSourceCandidateCount": local_page_raster_lineage.get(
                "summary", {}
            ).get("promotedSourceCandidateCount"),
            "higherResolutionThanBestRefCount": local_page_raster_lineage.get(
                "summary", {}
            ).get("higherResolutionThanBestRefCount"),
            "sharperThanBestRefCount": local_page_raster_lineage.get(
                "summary", {}
            ).get("sharperThanBestRefCount"),
            "sourceBackedR3BridgeHitCount": local_page_raster_lineage.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": local_page_raster_lineage.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": local_page_raster_lineage.get("summary", {}).get(
                "triggerCount"
            ),
            "fingerprint": local_page_raster_lineage.get("fingerprint"),
            "sheet": local_page_raster_lineage.get("sheet"),
        },
        "currentPdfColorManagementExtGStateGate": {
            "decision": current_pdf_color_management_extgstate.get("decision", {}).get(
                "currentPdfColorManagementExtGStateGate"
            ),
            "pdfCount": current_pdf_color_management_extgstate.get("summary", {}).get(
                "pdfCount"
            ),
            "pageRowCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("pageRowCount"),
            "outputIntentObjectCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("outputIntentObjectCount"),
            "page76UniqueResourceSignatureCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("page76UniqueResourceSignatureCount"),
            "extGStateObjectCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("extGStateObjectCount"),
            "page76ExtGStateObjectCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("page76ExtGStateObjectCount"),
            "blendModeExtGStateCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("blendModeExtGStateCount"),
            "opacityExtGStateCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("opacityExtGStateCount"),
            "transferExtGStateCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("transferExtGStateCount"),
            "overprintExtGStateCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("overprintExtGStateCount"),
            "colorSpaceObjectCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("colorSpaceObjectCount"),
            "page76ColorSpaceObjectCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("page76ColorSpaceObjectCount"),
            "iccBasedColorSpaceObjectCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("iccBasedColorSpaceObjectCount"),
            "separationOrDeviceNColorSpaceObjectCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("separationOrDeviceNColorSpaceObjectCount"),
            "imageObjectCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("imageObjectCount"),
            "page76ImageObjectCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("page76ImageObjectCount"),
            "decodeArrayImageCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("decodeArrayImageCount"),
            "specialImageColorKeyCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("specialImageColorKeyCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("triggerCount"),
            "colorManagementExtGStateFingerprint": current_pdf_color_management_extgstate.get(
                "summary", {}
            ).get("colorManagementExtGStateFingerprint"),
        },
        "currentPdfEmbeddedChannelMaskGate": {
            "decision": current_pdf_embedded_channel_mask.get("decision", {}).get(
                "currentPdfEmbeddedChannelMaskGate"
            ),
            "page76ImageObjectCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("page76ImageObjectCount"),
            "deviceRgbDctImageCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("deviceRgbDctImageCount"),
            "duplicateImageShaGroupCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("duplicateImageShaGroupCount"),
            "hiddenChannelCandidateImageCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("hiddenChannelCandidateImageCount"),
            "smaskOrMaskImageCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("smaskOrMaskImageCount"),
            "alphaPixmapImageCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("alphaPixmapImageCount"),
            "nonRgbImageCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("nonRgbImageCount"),
            "iccCmykSeparationImageCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("iccCmykSeparationImageCount"),
            "activeRegionChannelRowCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("activeRegionChannelRowCount"),
            "activeStateMismatchCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("activeStateMismatchCount"),
            "activeUnexpectedChannelStateCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("activeUnexpectedChannelStateCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("triggerCount"),
            "pdfEmbeddedChannelMaskFingerprint": current_pdf_embedded_channel_mask.get(
                "summary", {}
            ).get("pdfEmbeddedChannelMaskFingerprint"),
            "sheet": current_pdf_embedded_channel_mask.get("sheet"),
        },
        "currentPdfTextOverlayRenderModeGate": {
            "decision": current_pdf_text_overlay_render_mode.get("decision", {}).get(
                "currentPdfTextOverlayRenderModeGate"
            ),
            "textTraceSpanCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("textTraceSpanCount"),
            "invisibleType3TraceSpanCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("invisibleType3TraceSpanCount"),
            "visiblePaintedTraceSpanCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("visiblePaintedTraceSpanCount"),
            "allTraceTextInvisiblePdfCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("allTraceTextInvisiblePdfCount"),
            "glyphLessFontPdfCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("glyphLessFontPdfCount"),
            "helveticaOnlyPdfCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("helveticaOnlyPdfCount"),
            "fitAvailablePdfCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("fitAvailablePdfCount"),
            "overdoseTextTracePdfCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("overdoseTextTracePdfCount"),
            "activeAlignedTraceRowCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("activeAlignedTraceRowCount"),
            "activeAlignedComponentHitCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("activeAlignedComponentHitCount"),
            "activeAlignedStrictInstructionHitCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("activeAlignedStrictInstructionHitCount"),
            "sourceBackedR3BridgeHitCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("triggerCount"),
            "pdfTextOverlayRenderModeFingerprint": current_pdf_text_overlay_render_mode.get(
                "summary", {}
            ).get("pdfTextOverlayRenderModeFingerprint"),
            "sheet": current_pdf_text_overlay_render_mode.get("sheet"),
        },
        "sourcePacketFoldWorldOverdoseOrderControl": {
            "decision": packet_fold_world_overdose_order.get("decision", {}).get(
                "sourcePacketFoldWorldOverdoseOrderControl"
            ),
            "orderCount": packet_fold_world_overdose_order.get("summary", {}).get(
                "orderCount"
            ),
            "uniqueStreamCount": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("uniqueStreamCount"),
            "uniqueStreamsCsv": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("uniqueStreamsCsv"),
            "knownPageOrXStreamOrderCount": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("knownPageOrXStreamOrderCount"),
            "newFoldOnlyStreamsCsv": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("newFoldOnlyStreamsCsv"),
            "instructionHitOrderCount": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("instructionHitOrderCount"),
            "layoutHitOrderCount": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("layoutHitOrderCount"),
            "thematicHitOrderCount": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("thematicHitOrderCount"),
            "sourceDepthCueHitCount": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("sourceDepthCueHitCount"),
            "sourceBackedR3BridgeHitCount": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_fold_world_overdose_order.get("summary", {}).get(
                "triggerCount"
            ),
            "foldWorldOverdoseOrderFingerprint": packet_fold_world_overdose_order.get(
                "summary", {}
            ).get("foldWorldOverdoseOrderFingerprint"),
            "sheet": packet_fold_world_overdose_order.get("sheet"),
        },
        "sourcePacketBoldPhraseLengthSlotControl": {
            "decision": packet_bold_phrase_length_slot.get("decision", {}).get(
                "sourcePacketBoldPhraseLengthSlotControl"
            ),
            "activeRowCount": packet_bold_phrase_length_slot.get("summary", {}).get(
                "activeRowCount"
            ),
            "controlRowCount": packet_bold_phrase_length_slot.get("summary", {}).get(
                "controlRowCount"
            ),
            "focusedControlRowCount": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("focusedControlRowCount"),
            "activeWordCountSpanSlotMatchCount": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("activeWordCountSpanSlotMatchCount"),
            "controlWordCountSpanSlotMatchCount": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("controlWordCountSpanSlotMatchCount"),
            "p75OverControlWordCountSpanSlotMatch": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("p75OverControlWordCountSpanSlotMatch"),
            "allActiveCenterCountFitMetricCount": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("allActiveCenterCountFitMetricCount"),
            "partialCenterCountFitMax": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("partialCenterCountFitMax"),
            "sourceCountCueHitCount": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("sourceCountCueHitCount"),
            "generatedCountCueHitCount": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("generatedCountCueHitCount"),
            "sourceBackedR3BridgeHitCount": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_bold_phrase_length_slot.get("summary", {}).get(
                "triggerCount"
            ),
            "boldPhraseLengthSlotFingerprint": packet_bold_phrase_length_slot.get(
                "summary", {}
            ).get("boldPhraseLengthSlotFingerprint"),
            "sheet": packet_bold_phrase_length_slot.get("sheet"),
        },
        "sourcePacketBoldPhraseEdgeSlotControl": {
            "decision": packet_bold_phrase_edge_slot.get("decision", {}).get(
                "sourcePacketBoldPhraseEdgeSlotControl"
            ),
            "activeRowCount": packet_bold_phrase_edge_slot.get("summary", {}).get(
                "activeRowCount"
            ),
            "controlRowCount": packet_bold_phrase_edge_slot.get("summary", {}).get(
                "controlRowCount"
            ),
            "foldOrderRowCount": packet_bold_phrase_edge_slot.get("summary", {}).get(
                "foldOrderRowCount"
            ),
            "activeCenterEdgeHitRows": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("activeCenterEdgeHitRows"),
            "activeSpanEdgeHitRows": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("activeSpanEdgeHitRows"),
            "controlSpanEdgeHitRows": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("controlSpanEdgeHitRows"),
            "orderInstructionHitRows": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("orderInstructionHitRows"),
            "orderLayoutHitRows": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("orderLayoutHitRows"),
            "orderContainsCenterSlotStreamRows": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("orderContainsCenterSlotStreamRows"),
            "sourceEdgeCueHitCount": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("sourceEdgeCueHitCount"),
            "generatedEdgeCueHitCount": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("generatedEdgeCueHitCount"),
            "sourceBackedR3BridgeHitCount": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("satisfiedReopenTriggerCount"),
            "triggerCount": packet_bold_phrase_edge_slot.get("summary", {}).get(
                "triggerCount"
            ),
            "boldPhraseEdgeSlotFingerprint": packet_bold_phrase_edge_slot.get(
                "summary", {}
            ).get("boldPhraseEdgeSlotFingerprint"),
            "sheet": packet_bold_phrase_edge_slot.get("sheet"),
        },
        "c9FrameOverdosePageControl": {
            "decision": c9_page_control.get("decision", {}).get("c9FrameOverdosePageControl"),
            "xMirrorInvariant": c9_page_control.get("mirrorCheck", {}).get("xMirrorInvariant"),
            "maxCoordinateDeltaPx": c9_page_control.get("mirrorCheck", {}).get("maxCoordinateDeltaPx"),
            "p76ActiveFullCount": c9_page_control.get("summary", {}).get("p76ActiveFullCount"),
            "p76WordCount": c9_page_control.get("summary", {}).get("p76WordCount"),
            "p76HighlightOverlapCount": c9_page_control.get("summary", {}).get("p76HighlightOverlapCount"),
            "maxControlWordCount": c9_page_control.get("summary", {}).get("maxControlWordCount"),
            "maxControlHighlightOverlapCount": c9_page_control.get("summary", {}).get("maxControlHighlightOverlapCount"),
            "totalStrictInstructionHitCount": c9_page_control.get("summary", {}).get("totalStrictInstructionHitCount"),
            "selectorUnlocked": c9_page_control.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_page_control.get("sheet"),
        },
        "c9FrameInternalGeometryGate": {
            "decision": c9_internal_gate.get("decision", {}).get("c9FrameInternalGeometryGate"),
            "strictEdgeContactCount": c9_internal_gate.get("summary", {}).get("strictEdgeContactCount"),
            "strictEdgeContactLabels": c9_internal_gate.get("summary", {}).get("strictEdgeContactLabels"),
            "axisOrDiagonalCenterHitCount": c9_internal_gate.get("summary", {}).get("axisOrDiagonalCenterHitCount"),
            "mirrorPairHitCount": c9_internal_gate.get("summary", {}).get("mirrorPairHitCount"),
            "closestPairToFrameCenter": c9_internal_gate.get("summary", {}).get("closestPairToFrameCenter"),
            "obboOrientationIsPalindromic": c9_internal_gate.get("summary", {}).get("obboOrientationIsPalindromic"),
            "ykkyOrientationIsPalindromic": c9_internal_gate.get("summary", {}).get("ykkyOrientationIsPalindromic"),
            "selectorUnlocked": c9_internal_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_internal_gate.get("sheet"),
        },
        "c9HighlightEdgeContactControl": {
            "decision": c9_highlight_edge_control.get("decision", {}).get("c9HighlightEdgeContactControl"),
            "overlappingHighlightCount": c9_highlight_edge_control.get("summary", {}).get("overlappingHighlightCount"),
            "strictContactCount": c9_highlight_edge_control.get("summary", {}).get("strictContactCount"),
            "looseContactCount": c9_highlight_edge_control.get("summary", {}).get("looseContactCount"),
            "controlLooseContactCount": c9_highlight_edge_control.get("summary", {}).get("controlLooseContactCount"),
            "wideContactCount": c9_highlight_edge_control.get("summary", {}).get("wideContactCount"),
            "internalGateStrictContacts": c9_highlight_edge_control.get("summary", {}).get("internalGateStrictContacts"),
            "selectorUnlocked": c9_highlight_edge_control.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_highlight_edge_control.get("sheet"),
        },
        "c9BoldHighlightFormatDensity": {
            "decision": c9_bold_density.get("decision", {}).get("c9BoldHighlightFormatDensity"),
            "lineCount": c9_bold_density.get("summary", {}).get("lineCount"),
            "activeLineCount": c9_bold_density.get("summary", {}).get("activeLineCount"),
            "formatSignalLineCount": c9_bold_density.get("summary", {}).get("formatSignalLineCount"),
            "nonActiveFormatLineCount": c9_bold_density.get("summary", {}).get("nonActiveFormatLineCount"),
            "activeBoldLetterStream": c9_bold_density.get("summary", {}).get("activeBoldLetterStream"),
            "nonActiveBoldLetterStream": c9_bold_density.get("summary", {}).get("nonActiveBoldLetterStream"),
            "activeExactBoldTargetMatchCount": c9_bold_density.get("summary", {}).get("activeExactBoldTargetMatchCount"),
            "hardInstructionHitCount": c9_bold_density.get("summary", {}).get("hardInstructionHitCount"),
            "selectorUnlocked": c9_bold_density.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_bold_density.get("sheet"),
        },
        "c9ActiveFormatWitnessReconciliation": {
            "decision": c9_witness.get("decision", {}).get("c9ActiveFormatWitnessReconciliation"),
            "formatAuthorityPassCount": c9_witness.get("summary", {}).get("formatAuthorityPassCount"),
            "lineLevelExactBoldMatchCount": c9_witness.get("summary", {}).get("lineLevelExactBoldMatchCount"),
            "markdownBoldContainsPhraseCount": c9_witness.get("summary", {}).get("markdownBoldContainsPhraseCount"),
            "annotatedBoldHighlightClaimCount": c9_witness.get("summary", {}).get("annotatedBoldHighlightClaimCount"),
            "witnessConflictCount": c9_witness.get("summary", {}).get("witnessConflictCount"),
            "correctionReportMentionCount": c9_witness.get("summary", {}).get("correctionReportMentionCount"),
            "selectorUnlocked": c9_witness.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_witness.get("sheet"),
        },
        "c9OverdoseLetterSlotGate": {
            "decision": c9_overdose_slots.get("decision", {}).get("c9OverdoseLetterSlotGate"),
            "slotCount": c9_overdose_slots.get("summary", {}).get("slotCount"),
            "slotWidthPx": c9_overdose_slots.get("summary", {}).get("slotWidthPx"),
            "activeCenterLineOrderStream": c9_overdose_slots.get("summary", {}).get("activeCenterLineOrderStream"),
            "activeCenterXOrderStream": c9_overdose_slots.get("summary", {}).get("activeCenterXOrderStream"),
            "activeSpanLineOrderStream": c9_overdose_slots.get("summary", {}).get("activeSpanLineOrderStream"),
            "activeSpanXOrderStream": c9_overdose_slots.get("summary", {}).get("activeSpanXOrderStream"),
            "activeBlackOnlySpanXOrderStream": c9_overdose_slots.get("summary", {}).get("activeBlackOnlySpanXOrderStream"),
            "activeOrangeOnlySpanXOrderStream": c9_overdose_slots.get("summary", {}).get("activeOrangeOnlySpanXOrderStream"),
            "activeStrictInstructionHitCount": c9_overdose_slots.get("summary", {}).get("activeStrictInstructionHitCount"),
            "overPrefixRequiresBlackTargets": c9_overdose_slots.get("summary", {}).get("overPrefixRequiresBlackTargets"),
            "selectorUnlocked": c9_overdose_slots.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_overdose_slots.get("sheet"),
        },
        "c9GreyBlackOverSlotControl": {
            "decision": c9_grey_black_over_control.get("decision", {}).get("c9GreyBlackOverSlotControl"),
            "c9GreyBlackRowCount": c9_grey_black_over_control.get("summary", {}).get("c9GreyBlackRowCount"),
            "singleRowOverCount": c9_grey_black_over_control.get("summary", {}).get("singleRowOverCount"),
            "controlSingleRowOverCount": c9_grey_black_over_control.get("summary", {}).get("controlSingleRowOverCount"),
            "singleRowOverIds": c9_grey_black_over_control.get("summary", {}).get("singleRowOverIds"),
            "pairOverCount": c9_grey_black_over_control.get("summary", {}).get("pairOverCount"),
            "activeCorrectedPairOverCount": c9_grey_black_over_control.get("summary", {}).get("activeCorrectedPairOverCount"),
            "activeCorrectedPairOverStream": c9_grey_black_over_control.get("summary", {}).get("activeCorrectedPairOverStream"),
            "controlSingleOverTexts": c9_grey_black_over_control.get("summary", {}).get("controlSingleOverTexts"),
            "strictInstructionHitCount": c9_grey_black_over_control.get("summary", {}).get("strictInstructionHitCount"),
            "selectorUnlocked": c9_grey_black_over_control.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_grey_black_over_control.get("sheet"),
        },
        "c9OverSlotToleranceGate": {
            "decision": c9_over_tolerance_gate.get("decision", {}).get("c9OverSlotToleranceGate"),
            "totalCombinations": c9_over_tolerance_gate.get("summary", {}).get("totalCombinations"),
            "activeBlackPairOverCount": c9_over_tolerance_gate.get("summary", {}).get("activeBlackPairOverCount"),
            "p75ControlOverCount": c9_over_tolerance_gate.get("summary", {}).get("p75ControlOverCount"),
            "bothOverCount": c9_over_tolerance_gate.get("summary", {}).get("bothOverCount"),
            "canonicalActiveBlackPairStream": c9_over_tolerance_gate.get("summary", {}).get("canonicalActiveBlackPairStream"),
            "canonicalP75GreyControlSpan": c9_over_tolerance_gate.get("summary", {}).get("canonicalP75GreyControlSpan"),
            "activeOverFailsAtThresholds": c9_over_tolerance_gate.get("summary", {}).get("activeOverFailsAtThresholds"),
            "controlOverPersistsAtCanonical": c9_over_tolerance_gate.get("summary", {}).get("controlOverPersistsAtCanonical"),
            "selectorUnlocked": c9_over_tolerance_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_over_tolerance_gate.get("sheet"),
        },
        "c9VerticalOverdoseSlotGate": {
            "decision": c9_vertical_slots.get("decision", {}).get("c9VerticalOverdoseSlotGate"),
            "verticalSlotHeightPx": c9_vertical_slots.get("summary", {}).get("verticalSlotHeightPx"),
            "activeVerticalTopCenterLineOrder": c9_vertical_slots.get("summary", {}).get("activeVerticalTopCenterLineOrder"),
            "activeVerticalBottomCenterLineOrder": c9_vertical_slots.get("summary", {}).get("activeVerticalBottomCenterLineOrder"),
            "activeVerticalTopSpanLineOrder": c9_vertical_slots.get("summary", {}).get("activeVerticalTopSpanLineOrder"),
            "activeVerticalBottomSpanLineOrder": c9_vertical_slots.get("summary", {}).get("activeVerticalBottomSpanLineOrder"),
            "activeBlackVerticalTopStream": c9_vertical_slots.get("summary", {}).get("activeBlackVerticalTopStream"),
            "activeBlackVerticalBottomStream": c9_vertical_slots.get("summary", {}).get("activeBlackVerticalBottomStream"),
            "activeLayoutHitCount": c9_vertical_slots.get("summary", {}).get("activeLayoutHitCount"),
            "controlLayoutHitCount": c9_vertical_slots.get("summary", {}).get("controlLayoutHitCount"),
            "activeStrictInstructionHitCount": c9_vertical_slots.get("summary", {}).get("activeStrictInstructionHitCount"),
            "selectorUnlocked": c9_vertical_slots.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_vertical_slots.get("sheet"),
        },
        "c9HeaderGlyphSlotGate": {
            "decision": c9_header_glyph_slots.get("decision", {}).get("c9HeaderGlyphSlotGate"),
            "projectionCount": c9_header_glyph_slots.get("summary", {}).get("projectionCount"),
            "maxAbsEdgeDeltaVsEqualSlotPx": c9_header_glyph_slots.get("summary", {}).get("maxAbsEdgeDeltaVsEqualSlotPx"),
            "activeBlackOverProjectionCount": c9_header_glyph_slots.get("summary", {}).get("activeBlackOverProjectionCount"),
            "p75ControlOverProjectionCount": c9_header_glyph_slots.get("summary", {}).get("p75ControlOverProjectionCount"),
            "activeStrictInstructionHitCount": c9_header_glyph_slots.get("summary", {}).get("activeStrictInstructionHitCount"),
            "selectorUnlocked": c9_header_glyph_slots.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_header_glyph_slots.get("sheet"),
        },
        "c9MirroredHeaderGlyphGate": {
            "decision": c9_mirrored_header_glyph.get("decision", {}).get("c9MirroredHeaderGlyphGate"),
            "variantCount": c9_mirrored_header_glyph.get("summary", {}).get("variantCount"),
            "activeBlackOverCount": c9_mirrored_header_glyph.get("summary", {}).get("activeBlackOverCount"),
            "activeBlackRevoCount": c9_mirrored_header_glyph.get("summary", {}).get("activeBlackRevoCount"),
            "p75ControlOverCount": c9_mirrored_header_glyph.get("summary", {}).get("p75ControlOverCount"),
            "p75ControlRevoCount": c9_mirrored_header_glyph.get("summary", {}).get("p75ControlRevoCount"),
            "p75ControlMatchesActiveBlackCount": c9_mirrored_header_glyph.get("summary", {}).get("p75ControlMatchesActiveBlackCount"),
            "strictInstructionHitCount": c9_mirrored_header_glyph.get("summary", {}).get("strictInstructionHitCount"),
            "selectorUnlocked": c9_mirrored_header_glyph.get("summary", {}).get("selectorUnlocked"),
            "sheet": c9_mirrored_header_glyph.get("sheet"),
        },
        "overdoseGlyphAxisRulerGate": {
            "decision": overdose_glyph_axis_ruler.get("decision"),
            "nativeAxisCount": overdose_glyph_axis_ruler.get("summary", {}).get("nativeAxisCount"),
            "projectedAxisCount": overdose_glyph_axis_ruler.get("summary", {}).get("projectedAxisCount"),
            "nativeAllFourInsideSlotAxisCount": overdose_glyph_axis_ruler.get("summary", {}).get("nativeAllFourInsideSlotAxisCount"),
            "projectedAllFourInsideSlotAxisCount": overdose_glyph_axis_ruler.get("summary", {}).get("projectedAllFourInsideSlotAxisCount"),
            "nativeMaxMirroredInsideSlotCount": overdose_glyph_axis_ruler.get("summary", {}).get("nativeMaxMirroredInsideSlotCount"),
            "projectedMaxMirroredInsideSlotCount": overdose_glyph_axis_ruler.get("summary", {}).get("projectedMaxMirroredInsideSlotCount"),
            "layoutTermAxisCount": overdose_glyph_axis_ruler.get("summary", {}).get("layoutTermAxisCount"),
            "strictInstructionAxisHitCount": overdose_glyph_axis_ruler.get("summary", {}).get("strictInstructionAxisHitCount"),
            "allFourProjectedStreams": overdose_glyph_axis_ruler.get("summary", {}).get("allFourProjectedStreams"),
            "sourceBackedR3BridgeHitCount": overdose_glyph_axis_ruler.get("summary", {}).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": overdose_glyph_axis_ruler.get("summary", {}).get("satisfiedReopenTriggerCount"),
            "triggerCount": overdose_glyph_axis_ruler.get("summary", {}).get("triggerCount"),
            "fingerprint": overdose_glyph_axis_ruler.get("fingerprint"),
            "sheet": overdose_glyph_axis_ruler.get("sheet"),
        },
        "overdoseGlyphAxisWordCenterControlGate": {
            "decision": overdose_glyph_axis_word_center_control.get("decision"),
            "selectedAxisCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("selectedAxisCount"),
            "activeAllFourInsideAxisCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("activeAllFourInsideAxisCount"),
            "activeMeaningfulLayoutAxisCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("activeMeaningfulLayoutAxisCount"),
            "activeStreams": overdose_glyph_axis_word_center_control.get("summary", {}).get("activeStreams"),
            "c9WordCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("c9WordCount"),
            "nonTargetC9ControlWordCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("nonTargetC9ControlWordCount"),
            "controlWordMirroredInsideSlotCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("controlWordMirroredInsideSlotCount"),
            "controlWordMirrorRowCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("controlWordMirrorRowCount"),
            "controlQuartetAllFourInsideSlotCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("controlQuartetAllFourInsideSlotCount"),
            "controlQuartetWindowCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("controlQuartetWindowCount"),
            "controlQuartetLayoutTermWindowCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("controlQuartetLayoutTermWindowCount"),
            "controlQuartetStrictInstructionWindowCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("controlQuartetStrictInstructionWindowCount"),
            "sourceBackedR3BridgeHitCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("sourceBackedR3BridgeHitCount"),
            "satisfiedReopenTriggerCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("satisfiedReopenTriggerCount"),
            "triggerCount": overdose_glyph_axis_word_center_control.get("summary", {}).get("triggerCount"),
            "fingerprint": overdose_glyph_axis_word_center_control.get("fingerprint"),
            "sheet": overdose_glyph_axis_word_center_control.get("sheet"),
        },
        "page76ActiveCropOrientationGuardrail": {
            "decision": orientation_guardrail.get("decision"),
            "orientationDecision": orientation_guardrail.get("summary", {}).get("orientationDecision"),
            "uprightSize": orientation_guardrail.get("summary", {}).get("uprightSize"),
            "nativeSize": orientation_guardrail.get("summary", {}).get("nativeSize"),
            "rot180MeanAbsDiff": orientation_guardrail.get("summary", {}).get("rot180MeanAbsDiff"),
            "directMeanAbsDiff": orientation_guardrail.get("summary", {}).get("directMeanAbsDiff"),
            "allUprightBoxesInBounds": orientation_guardrail.get("summary", {}).get("allUprightBoxesInBounds"),
            "allNativeTransformBoxesInBounds": orientation_guardrail.get("summary", {}).get("allNativeTransformBoxesInBounds"),
            "selectorUnlocked": orientation_guardrail.get("summary", {}).get("selectorUnlocked"),
            "sheet": orientation_guardrail.get("sheet"),
        },
        "page76ActiveOrderOrientationTrap": {
            "decision": order_trap.get("decision"),
            "colorPattern": order_trap.get("summary", {}).get("colorPattern"),
            "visualStatePattern": order_trap.get("summary", {}).get("visualStatePattern"),
            "colorPatternIsPalindrome": order_trap.get("summary", {}).get("colorPatternIsPalindrome"),
            "visualStatePatternIsPalindrome": order_trap.get("summary", {}).get("visualStatePatternIsPalindrome"),
            "uprightPageLines": order_trap.get("summary", {}).get("uprightPageLines"),
            "nativeUnnormalizedPageLines": order_trap.get("summary", {}).get("nativeUnnormalizedPageLines"),
            "uprightCorridorIndexes": order_trap.get("summary", {}).get("uprightCorridorIndexes"),
            "nativeUnnormalizedCorridorIndexes": order_trap.get("summary", {}).get("nativeUnnormalizedCorridorIndexes"),
            "lineOrderDetectsFlip": order_trap.get("summary", {}).get("lineOrderDetectsFlip"),
            "corridorOrderDetectsFlip": order_trap.get("summary", {}).get("corridorOrderDetectsFlip"),
            "selectorUnlocked": order_trap.get("summary", {}).get("selectorUnlocked"),
            "sheet": order_trap.get("sheet"),
        },
        "activeQuartetBoxOcrGate": {
            "decision": active_box_ocr_gate.get("decision"),
            "targetCount": active_box_ocr_gate.get("summary", {}).get("targetCount"),
            "exactBoxMatchCount": active_box_ocr_gate.get("summary", {}).get("exactBoxMatchCount"),
            "corruptedOrMisreadBoxCount": active_box_ocr_gate.get("summary", {}).get("corruptedOrMisreadBoxCount"),
            "blankBoxCount": active_box_ocr_gate.get("summary", {}).get("blankBoxCount"),
            "usableForTextExtraction": active_box_ocr_gate.get("summary", {}).get("usableForTextExtraction"),
            "lineOrder": active_box_ocr_gate.get("summary", {}).get("lineOrder"),
            "corridorOrder": active_box_ocr_gate.get("summary", {}).get("corridorOrder"),
            "selectorUnlocked": active_box_ocr_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_box_ocr_gate.get("sheet"),
        },
        "typekaComparisonMetadataGate": {
            "decision": typeka_comparison_metadata.get("decision"),
            "comparisonPdfCount": typeka_comparison_metadata.get("summary", {}).get("comparisonPdfCount"),
            "comparisonPdfFontWitnessCount": typeka_comparison_metadata.get("summary", {}).get("comparisonPdfFontWitnessCount"),
            "comparisonPdfTypekaResourceCount": typeka_comparison_metadata.get("summary", {}).get("comparisonPdfTypekaResourceCount"),
            "comparisonPdfImageOnlyCount": typeka_comparison_metadata.get("summary", {}).get("comparisonPdfImageOnlyCount"),
            "articleWithFontsTypekaChars": typeka_comparison_metadata.get("summary", {}).get("articleWithFontsTypekaChars"),
            "r3SelectorStatus": typeka_comparison_metadata.get("summary", {}).get("r3SelectorStatus"),
            "selectorUnlocked": typeka_comparison_metadata.get("summary", {}).get("selectorUnlocked"),
            "sheet": typeka_comparison_metadata.get("sheet"),
        },
        "activeObboQuartetRecurrence": {
            "decision": active_obbo_recurrence.get("decision"),
            "activeYRatios": active_obbo_recurrence.get("summary", {}).get("activeYRatios"),
            "totalObboWindows": active_obbo_recurrence.get("summary", {}).get("totalObboWindows"),
            "issue24ObboWindows": active_obbo_recurrence.get("summary", {}).get("issue24ObboWindows"),
            "independentControlObboWindows": active_obbo_recurrence.get("summary", {}).get("independentControlObboWindows"),
            "issue24ActiveLikeWindows": active_obbo_recurrence.get("summary", {}).get("issue24ActiveLikeWindows"),
            "independentControlActiveLikeWindows": active_obbo_recurrence.get("summary", {}).get("independentControlActiveLikeWindows"),
            "selectorUnlocked": active_obbo_recurrence.get("summary", {}).get("selectorUnlocked"),
            "sheet": active_obbo_recurrence.get("sheet"),
        },
        "boldDocmSourceGate": {
            "decision": bold_source_gate.get("decision"),
            "boldHasVbaProject": bold_source_gate.get("summary", {}).get("boldHasVbaProject"),
            "boldActiveTargetsPresent": bold_source_gate.get("summary", {}).get("boldActiveTargetsPresent"),
            "articleActiveTargetsPresent": bold_source_gate.get("summary", {}).get("articleActiveTargetsPresent"),
            "otrobipRecovered": bold_source_gate.get("summary", {}).get("otrobipRecovered"),
            "boldWordCount": bold_source_gate.get("summary", {}).get("boldWordCount"),
            "articleWordCount": bold_source_gate.get("summary", {}).get("articleWordCount"),
            "selectorUnlocked": bold_source_gate.get("summary", {}).get("selectorUnlocked"),
            "sheet": bold_source_gate.get("sheet"),
        },
        "boldHighlightedTextReconstruction": {
            "decision": bold_highlighted_text.get("decision"),
            "highlightedRunCount": bold_highlighted_text.get("summary", {}).get("highlightedRunCount"),
            "highlightedWordCount": bold_highlighted_text.get("summary", {}).get("highlightedWordCount"),
            "highlightedFonts": bold_highlighted_text.get("summary", {}).get("highlightedFonts"),
            "highlightedBoldValues": bold_highlighted_text.get("summary", {}).get("highlightedBoldValues"),
            "activeTargetsInBoldText": bold_highlighted_text.get("summary", {}).get("activeTargetsInBoldText"),
            "activeTargetsInHighlightedStream": bold_highlighted_text.get("summary", {}).get("activeTargetsInHighlightedStream"),
            "contextPhrasesInHighlightedStream": bold_highlighted_text.get("summary", {}).get("contextPhrasesInHighlightedStream"),
            "contextPartialHighlightedTokens": bold_highlighted_text.get("summary", {}).get("contextPartialHighlightedTokens"),
            "instructionTermHits": bold_highlighted_text.get("summary", {}).get("instructionTermHits"),
            "selectorUnlocked": bold_highlighted_text.get("summary", {}).get("selectorUnlocked"),
            "sheet": bold_highlighted_text.get("sheet"),
        },
    }


def classify_frontier() -> list[dict]:
    local_text_checks = [
        "g5_o5_units",
        "exact_edge_word_ops",
        "symmetric_line_fold",
        "axis_spine",
        "mark_pointers",
        "rky_rarity",
        "rky_control",
        "color_swap",
        "color_swap_take_right",
        "monetizing_near_miss_unit",
        "p80_symptom_relief_rule",
        "p77_one_line_near_miss",
        "canva_lineup_shift_scope",
        "zero_index_rule_scope",
        "active_line_unit_reconciliation",
        "plain_correction_selector_impact",
        "page76_target_text_authority_lock",
        "page76_target_format_authority_lock",
        "markdown_docm_mismatch_instruction_surface",
        "bold_vs_article_active_corridor",
        "bold_docm_source_gate",
        "bold_highlighted_text_reconstruction",
        "active_quartet_box_ocr_gate",
        "page76_highlight_edge_selector",
        "page76_active_highlight_fill",
        "page76_highlight_spill_direction",
        "page76_spill_control_comparison",
        "reflection_box_target_overlap",
        "reflection_line_pitch_stack_gate",
        "reflection_shifted_carrier_content_gate",
        "anchor_point_target_proximity",
        "docm_visual_highlight_consistency",
        "opening_spread_instruction_surface",
        "typeka_instruction_surface",
        "p79_take_all_energy_selector",
        "issue24_physical_page_topology",
        "p75_p76_valid_leaf_recheck",
        "p78_source_graphic_instruction_surface",
        "fold_nonboundary_ordering",
        "obbo_anchor_signature",
        "obbo_boundary_coincidences",
        "p78_contact_role_grammar",
        "p80_package_r3_gate_synthesis",
        "p80_numeric_active_order_gate",
        "active_quartet_capsule_direction_gate",
        "active_punctuation_enclosure_gate",
        "active_font_edge_transition_gate",
        "active_mix_proximity_gate",
        "active_quartet_pair_symmetry_gate",
        "active_target_envelope_density_gate",
        "active_target_center_path_gate",
        "active_target_center_path_bold_gate",
        "active_line_corridor_mirror_index_gate",
        "g5_axis_bold_highlight_rescue_gate",
        "page76_page_center_mirror_guardrail",
        "overdose_header_ray_fan_gate",
        "c9_glyph_center_ray_gate",
        "c9_target_vertical_chord_gate",
        "c9_target_horizontal_chord_gate",
        "active_frame_center_reflection_gate",
        "active_frame_edge_axis_gate",
        "active_o4_frame_rescue_gate",
        "o4_frame_rescue_offset_control",
        "o4_frame_rescue_content_gate",
        "o4_frame_rescue_signal_stream_gate",
        "o4_frame_rescue_yk_filter_control",
        "o4_frame_yk_unit_order_gate",
        "c9_frame_overdose_page_control",
        "c9_frame_internal_geometry_gate",
        "c9_highlight_edge_contact_control",
        "c9_bold_highlight_format_density",
        "c9_active_format_witness_reconciliation",
        "c9_overdose_letter_slot_gate",
        "c9_grey_black_over_slot_control",
        "c9_over_slot_tolerance_gate",
        "c9_vertical_overdose_slot_gate",
        "c9_header_glyph_slot_gate",
        "c9_mirrored_header_glyph_gate",
        "overdose_header_registration_gate",
        "overdose_same_slot_control_gate",
        "typeka_font_r3_gate_synthesis",
        "fold_mirror_r3_gate_synthesis",
        "page76_highlight_cluster_r3_gate_synthesis",
        "page76_highlight_fold_axis_population_gate",
        "comparison_overdose_layout_r3_gate_synthesis",
        "overdose_style_uniqueness",
        "active_evidence_unlock_matrix",
        "current_local_source_reopen_gate",
        "source_packet_native_benchmark_bridge",
        "source_packet_visual_state_roundtrip",
        "source_packet_alignment_tolerance",
        "source_packet_geometric_fingerprint",
        "source_packet_frame_normalized_geometry",
        "source_packet_color_profile_manifest",
        "source_packet_repaired_p78_frame_residual",
        "source_packet_repaired_frame_expansion_leakage",
        "source_packet_handoff_integrity_matrix",
        "source_packet_false_positive_guardrail",
        "source_packet_r3_bridge_audit",
        "source_packet_reopen_trigger_matrix",
        "source_packet_orientation_disambiguator",
        "source_packet_orientation_control_quartets",
        "source_packet_source_review_gate",
        "source_packet_overdose_transform_control",
        "source_packet_fold_format_intersection_control",
        "source_packet_terminal_coverage_matrix",
        "source_packet_active_target_authority_crosscheck",
        "source_packet_active_format_stream_control",
        "source_packet_active_index_slot_control",
        "source_packet_center_rotation_word_control",
        "source_packet_color_split_span_control",
        "source_packet_dominant_overlap_slot_control",
        "source_packet_span_edge_slot_control",
        "source_packet_overlap_width_profile_control",
        "source_packet_span_neighbor_slot_control",
        "source_packet_span_complement_slot_control",
        "source_packet_local_asset_orientation_gate",
        "source_packet_pdf_render_quality_gate",
        "current_scan_held_to_light_simulator",
        "scan_only_held_to_light_adjudication",
        "scan_only_held_to_light_tolerance_sweep",
        "corrected_topology_77_76_light_table",
        "open_heart_capsule_rule",
        "current_scan_held_to_light_active_box_balance_gate",
        "current_scan_held_to_light_component_readability_gate",
        "current_scan_held_to_light_opacity_gate",
        "current_scan_light_table_blend_mode_gate",
        "current_scan_valid_leaf_source_ink_landing_gate",
        "current_scan_all_leaf_light_table_parity_gate",
        "current_scan_light_table_density_calibration_gate",
        "current_scan_overdose_density_outlier_provenance_gate",
        "current_scan_overdose_density_highlight_ablation_gate",
        "current_scan_active_source_highlight_ablation_gate",
        "current_scan_physical_bleedthrough_correlation_gate",
        "current_scan_active_quartet_fingerprint_specificity_gate",
        "current_scan_target_witness_box_substitution_gate",
        "current_scan_page76_image_witness_state_stability_gate",
        "current_scan_page76_image_witness_microregistration_gate",
        "current_scan_active_box_overdose_edge_residue_gate",
        "current_scan_valid_leaf_jitter_source_ink_rescue_gate",
        "current_scan_page_frame_trim_registration_gate",
        "current_scan_content_box_registration_gate",
        "current_scan_header_footer_lane_registration_gate",
        "current_scan_lane_affine_registration_gate",
        "current_scan_lane_affine_source_trace",
        "current_scan_source_layer_landing_gate",
        "current_scan_source_layer_miss_distance_gate",
        "current_scan_b4_broad_contact_provenance_gate",
        "current_pdf_b4_contact_pixel_provenance_gate",
        "current_pdf_duplicate_background_feature_artifact_gate",
        "current_pdf_page76_carrier_state_stability_gate",
        "current_scan_b4_self_signal_guardrail",
        "current_scan_light_table_self_signal_partition_gate",
        "current_scan_overdose_slot_source_support_trace",
        "current_pdf_overdose_slot_source_support_trace",
        "current_pdf_ose_source_highlight_phrase_gate",
        "current_pdf_ose_highlight_mirror_geometry_gate",
        "current_pdf_ose_highlight_translation_rescue_gate",
        "current_scan_valid_leaf_bleedthrough_control_grid",
        "current_scan_valid_leaf_local_warp_gate",
        "current_scan_valid_leaf_local_warp_source_trace",
        "current_scan_valid_leaf_edge_contact_control",
        "current_scan_valid_leaf_edge_source_trace",
        "current_scan_valid_leaf_interior_source_trace",
        "current_scan_valid_leaf_glyph_slot_source_trace",
        "current_scan_valid_leaf_channel_source_trace",
        "current_scan_valid_leaf_word_collision_trace",
        "current_scan_valid_leaf_line_band_trace",
        "valid_leaf_strict_term_disambiguation_gate",
        "valid_leaf_target_context_instruction_gate",
        "current_pdf_page_box_pair_geometry_gate",
        "current_pdf_all_leaf_imposition_consistency_gate",
        "current_pdf_leaf_pair_texture_correlation_gate",
        "current_pdf_native_image_registration_gate",
        "current_pdf_native_registration_candidate_source_trace",
        "current_pdf_held_to_light_composite_polarity_gate",
        "current_pdf_held_to_light_candidate_source_trace",
        "current_pdf_held_to_light_all_target_phrase_gate",
        "current_pdf_held_to_light_color_phrase_gate",
        "current_pdf_held_to_light_component_readability_gate",
        "page76_highlight_edge_slot_ruler_gate",
        "overdose_glyph_axis_ruler_gate",
        "overdose_glyph_axis_word_center_control_gate",
        "current_pdf_leaf_image_identity_gate",
        "current_pdf_render_leaf_simulation_gate",
        "current_pdf_lowres_render_source_trace",
        "current_pdf_ocr_reverse_leaf_source_trace",
        "current_scan_overdose_slot_shape_phase_control",
        "current_scan_overdose_xslot_phase_control",
        "current_pdf_container_metadata_gate",
        "current_pdf_logical_structure_gate",
        "current_pdf_navigation_thread_gate",
        "current_pdf_page_thumbnail_gate",
        "current_pdf_thumbnail_active_signal_gate",
        "current_pdf_content_stream_operator_gate",
        "current_pdf_content_transform_matrix_gate",
        "current_pdf_form_xobject_dictionary_gate",
        "current_pdf_form_overlay_placement_gate",
        "current_pdf_trailer_xref_integrity_gate",
        "current_pdf_font_cmap_resource_gate",
        "current_pdf_embedded_jpeg_marker_gate",
        "current_pdf_thumbnail_exif_order_gate",
        "current_pdf_jpeg_compression_provenance_gate",
        "current_pdf_jpeg_entropy_tail_gate",
        "current_pdf_image_xobject_dictionary_gate",
        "current_pdf_page_resource_order_gate",
        "current_pdf_object_layout_inspection",
        "current_pdf_partial_image_placement_gate",
        "current_scan_crop_light_table_targets",
        "current_scan_overdose_glyph_crop_projection",
        "current_scan_highlight_boundary_instruction_probe",
        "current_scan_boundary_light_table_anomaly_probe",
        "current_scan_boundary_contact_source_trace",
        "current_pdf_ocr_target_provenance_gate",
        "current_pdf_ocr_instruction_scope_gate",
        "current_pdf_ocr_document_order_gate",
        "current_pdf_ocr_overdose_index_offset_gate",
        "current_pdf_ocr_overdose_neighborhood_gate",
        "current_pdf_ocr_page_header_sequence_gate",
        "current_pdf_visual_header_footer_band_sequence_gate",
        "current_pdf_repeated_overdose_header_lane_gate",
        "current_pdf_overdose_header_delta_transfer_gate",
        "current_pdf_overdose_body_start_vector_gate",
        "current_pdf_overdose_body_basis_reflection_gate",
        "current_pdf_overdose_body_lattice_gate",
        "current_pdf_overdose_body_offset_transfer_gate",
        "current_pdf_overdose_body_offset_column_gate",
        "current_pdf_overdose_body_fraction_column_gate",
        "current_pdf_ocr_affine_alignment_gate",
        "current_pdf_render_alignment_delta_gate",
        "current_pdf_render_resolution_invariance_gate",
        "current_pdf_active_region_render_embedded_identity_gate",
        "current_scan_jpeg_block_grid_gate",
        "current_scan_halftone_screen_gate",
        "current_scan_rgb_registration_gate",
        "current_scan_luminance_bitplane_gate",
        "current_scan_threshold_morphology_gate",
        "current_scan_highlight_edge_halo_gate",
        "current_scan_slot_boundary_residual_gate",
        "current_scan_overdose_glyph_stroke_centroid_gate",
        "current_scan_active_envelope_transform_gate",
        "current_scan_active_envelope_transform_text_trace",
        "current_scan_active_envelope_transform_format_trace",
        "current_scan_active_envelope_antidiag_overlap_control",
        "current_scan_background_seam_residual_gate",
        "current_scan_paper_texture_duplex_gate",
        "current_scan_paper_texture_shift_gate",
        "current_pdf_active_box_coordinate_grid_gate",
        "current_pdf_image_rect_margin_phase_gate",
        "local_pdf_filesystem_provenance_gate",
        "local_page_raster_lineage_gate",
        "current_pdf_color_management_extgstate_gate",
        "current_pdf_embedded_channel_mask_gate",
        "current_pdf_text_overlay_render_mode_gate",
        "source_packet_fold_world_overdose_order_control",
        "source_packet_bold_phrase_length_slot_control",
        "source_packet_highlight_count_slot_permutation_control",
        "source_packet_active_span_bridge_control",
        "source_packet_bold_phrase_edge_slot_control",
    ]
    closed_local = [name for name in local_text_checks if REPORTS[name].exists()]

    return [
        {
            "frontier": "confirmed target surface",
            "status": "open-as-location",
            "evidence": "Page 76 lower corridor, especially O5 `shitcoiner at heart` and G5 `Volcano Bonds`, remains the strongest convergence point.",
            "blockedBy": "No rule yet names the unit/order to extract from that target pair.",
            "nextAction": "Use as validation target for any new source/clue, not as key material.",
        },
        {
            "frontier": "local text/format/layout permutations",
            "status": "closed-for-current-scan",
            "evidence": f"{len(closed_local)} focused local checks are present; recent closures include G5/O5 units, exact wordplay, symmetric fold, axis spine, lower marks, R-K-Y, color-swap take/right, the p77 monetizing near miss, p80 symptom relief, p80 numeric active-order gate, active-quartet capsule-direction gate, active punctuation/enclosure gate, active font-edge transition gate, active Mix proximity gate, active quartet pair-symmetry gate, active target envelope density gate, active target center-path gate, active target center-path bold gate, active line/corridor mirror-index gate, G5-axis bold/highlight rescue gate, page-center mirror/rotation guardrail, OVERDOSE header ray fan gate, C9 glyph-center ray gate, C9 target vertical chord gate, C9 target horizontal chord gate, active frame-center reflection gate, active frame edge/axis gate, active O4 frame-rescue gate, O4 frame-rescue offset control, O4 frame-rescue content gate, O4 frame-rescue signal-stream gate, O4 frame-rescue Y/K filter control, O4 frame Y/K unit-order gate, C9 frame OVERDOSE page control, C9 frame internal geometry gate, C9 highlight edge-contact control, C9 bold/highlight format density, C9 active format witness reconciliation, C9 OVERDOSE letter-slot gate, C9 grey/black OVER slot control, C9 OVER slot tolerance gate, C9 vertical OVERDOSE slot gate, C9 header glyph slot gate, C9 mirrored header glyph gate, OVERDOSE glyph-axis ruler gate, OVERDOSE glyph-axis word-center control, OVERDOSE header registration gate, OVERDOSE same-slot control gate, p77 one-line repair, Canva line-up shifts, zero/#0 indexing, active line/sentence/corridor rows, correction markup, page-76 target text authority, page-76 target format authority, Markdown-vs-DOCM mismatch streams, BOLD-vs-DOCM, BOLD highlighted-text reconstruction, active quartet 3D box OCR gate, highlight edges/fill/spill/spill-controls, page-76 highlight-cluster R3 gate synthesis, page-76 highlight fold-axis population gate, 3D reflection boxes, 3D reflection line-pitch stack gate, 3D reflection shifted-carrier content gate, 3D anchors, 3D fold/mirror R3 gate synthesis, DOCM-vs-visual highlight consistency, opener surfaces, Typeka instruction-surface terms, Typeka/font R3 gate synthesis, p79 `right/take`, physical topology, p75->p76 same-leaf, p78 source graphic text, 3D fold ordering, O-B-B-O comparison/boundaries, p78 contact-role grammar, p80 package R3 gate synthesis, comparison/OVERDOSE layout R3 gate synthesis, OVERDOSE style uniqueness control, active evidence unlock matrix, source-packet native benchmark bridge, source-packet visual-state roundtrip, source-packet alignment tolerance, source-packet geometric fingerprint, source-packet frame-normalized geometry, source-packet color-profile manifest, source-packet repaired p78 frame residual, source-packet repaired frame expansion leakage, source-packet handoff integrity matrix, source-packet false-positive guardrail, source-packet R3 bridge audit, source-packet reopen trigger matrix, source-packet orientation disambiguator, source-packet orientation control quartets, source-packet source-review gate, source-packet OVERDOSE transform control, source-packet fold/format intersection control, source-packet terminal coverage matrix, source-packet active target authority crosscheck, source-packet active format stream control, source-packet active index-slot control, source-packet center rotation word control, source-packet color split span control, source-packet dominant overlap slot control, source-packet span edge slot control, source-packet overlap width profile control, source-packet span neighbor slot control, source-packet span complement slot control, source-packet local asset orientation gate, source-packet PDF render quality gate, current-scan held-to-light simulator, scan-only held-to-light adjudication, scan-only held-to-light tolerance sweep, corrected-topology 77->76 white-mask light-table test, open-heart O-K-K-O capsule bridge rule, current-scan held-to-light active-box balance gate, current-scan held-to-light component readability gate, current-scan held-to-light opacity gate, current-scan light-table blend-mode gate, current-scan valid-leaf source-ink landing gate, current-scan all-leaf light-table parity gate, current-scan light-table density calibration gate, current-scan OVERDOSE density outlier provenance gate, current-scan OVERDOSE source-highlight ablation gate, current-scan valid-leaf jitter source-ink rescue gate, current-scan page-frame/trim registration gate, current-scan content-box registration gate, current-scan source-layer landing gate, current-scan source-layer miss-distance gate, current-scan B4 broad-contact provenance gate, current PDF B4 contact pixel provenance gate, current PDF duplicate-background feature artifact gate, current PDF page-76 carrier-state stability gate, current-scan B4 self-signal guardrail, current-scan light-table self-signal partition gate, current-scan OVERDOSE slot source-support trace, current PDF OVERDOSE slot source-support trace, current PDF OSE source-highlight phrase gate, current PDF OSE highlight mirror geometry gate, current PDF OSE highlight translation rescue gate, current-scan valid-leaf bleed-through control grid, current-scan valid-leaf edge-contact control, current-scan valid-leaf edge source trace, current-scan valid-leaf interior source trace, current-scan valid-leaf glyph-slot source trace, current-scan valid-leaf channel source trace, current-scan valid-leaf word-collision trace, current-scan valid-leaf line-band trace, current-scan valid-leaf strict-term disambiguation, current-scan valid-leaf target-context instruction gate, current PDF page-box pair geometry gate, current PDF leaf-pair texture correlation gate, current PDF leaf-image identity gate, current PDF render leaf simulation gate, current PDF low-res render source trace, current PDF OCR reverse-leaf source trace, current PDF held-to-light all-target phrase gate, current PDF held-to-light color phrase gate, current PDF held-to-light component readability gate, current-scan OVERDOSE slot-shape phase control, current-scan OVERDOSE x-slot phase control, current PDF container metadata gate, current PDF logical structure gate, current PDF navigation/article-thread gate, current PDF page-thumbnail gate, current PDF thumbnail active-signal gate, current PDF content-stream operator gate, current PDF content transform/matrix gate, current PDF Form XObject dictionary gate, current PDF form overlay placement gate, current PDF trailer/xref integrity gate, current PDF font/CMap resource gate, current PDF embedded JPEG marker gate, current PDF thumbnail EXIF order gate, current PDF JPEG compression provenance gate, current PDF image XObject dictionary gate, current PDF page resource/order gate, current PDF object/layout inspection, current PDF partial image placement gate, current-scan crop light-table targets, current-scan OVERDOSE glyph crop projection, current-scan highlight/crop boundary instruction probe, current-scan boundary light-table anomaly probe, current-scan boundary contact source trace, current PDF OCR target provenance gate, current PDF OCR document-order gate, current PDF OCR OVERDOSE index-offset gate, current PDF OCR OVERDOSE neighborhood gate, current PDF OCR page-header sequence gate, current PDF visual header/footer band sequence gate, current PDF repeated OVERDOSE header lane gate, current PDF OVERDOSE header delta transfer gate, current PDF OVERDOSE body-start vector gate, current PDF OVERDOSE body-basis reflection gate, current PDF OVERDOSE body-line lattice gate, current PDF OVERDOSE body-offset transfer gate, current PDF OVERDOSE body-offset column gate, current PDF OVERDOSE body-fraction column gate, current PDF OCR affine alignment gate, current PDF render alignment delta gate, current PDF render resolution invariance gate, current PDF active-region render/embedded identity gate, current-scan JPEG block-grid gate, current-scan halftone screen gate, current-scan RGB registration gate, current-scan luminance bitplane gate, current-scan threshold morphology gate, current-scan background seam residual gate, current-scan paper texture duplex/shift gates, current PDF color-management/ExtGState gate, current PDF embedded channel/mask gate, current PDF text overlay render-mode gate, source-packet fold-world OVERDOSE order control, source-packet bold phrase length slot control, source-packet highlight-count slot permutation control, source-packet active span bridge control, and source-packet bold phrase edge slot control.",
            "blockedBy": "They produce ordinary prose, control/decoy text, or no procedural terms.",
            "nextAction": "Do not run more local permutations unless a new clue names `word`, `letter`, `line`, `edge`, `font`, `right`, `heart`, `sell`, or similar.",
        },
        {
            "frontier": "source/physical registration",
            "status": "highest-value-open",
            "evidence": "The repaired exact-edge signature and M3/O5/G5 tri-contact give a compact benchmark: `should sell | Volcano Bonds | shitcoiner at heart` with styles `R-K-Y`; the O4 rescue `Y/K + frame` benchmark now also isolates O4/B4/G5/O5 with no non-active in-frame Y/K groups, while still failing R3 unit/order. The active target envelope density gate shows the minimal O4/B4/G5/O5 envelope is a broad lower-corridor band with 89 OCR-map words, 86 non-target words, 0 strict instruction hits, and 12 comparable line-pitch shifted controls. The active target center-path gate shows a narrow O4->B4->G5->O5 connector rail touches only 9 OCR-map words, 6 non-target words, 0 strict instruction hits, and 10 comparable line-pitch shifted controls. The active target center-path bold gate projects DOCM bold state onto the same rail: the primary path re-hits 4 direct active target bold units, touches 4 bold OCR rail words, but only 1 non-active bold word (`Bukele`), with 0 strict instruction hits and 5 shifted controls matching or exceeding the primary non-active bold count. The C9 frame page-control pass adds that the rectangle is horizontally mirror-invariant and broad across repeated OVERDOSE lower-page slots, with 0 strict unit/order hits; the C9 internal geometry gate adds only an O4 top-edge coincidence, with 0 centerline/diagonal hits and 0 mirror-pair hits; the highlight edge-contact control shows that a page-75 control highlight is also near the C9 top edge at the looser 25 px threshold; the C9 bold/highlight density check shows only 2/4 active phrases match line-level bold letters while four non-active lines carry format signals; the C9 active format witness reconciliation locks DOCM/high-res/crop-pack as active format authority while line-level bold and Markdown only match O4/O5 and annotated notes remain witness/context only; the C9 OVERDOSE letter-slot gate shows center streams `OVED`/`VEDO`, a span stream `OVERRDODOS` that only gets `OVER` from the black B4/G5 boxes, and 0 strict instruction hits; the C9 grey/black OVER control shows non-active p75 `Don't fall for shitcoinery` spans `OVER` by itself in the same lower-frame geometry; the C9 OVER slot tolerance gate shows canonical `OVER` for B4/G5 and the p75 control, active OVER appears in 45/99 combinations while the p75 control appears in 49/99, and active OVER fails at thresholds 150/200; the C9 vertical OVERDOSE slot gate maps the active quartet to `OERE` top-to-bottom and `EODO` bottom-to-top, with 0 active layout hits and 0 strict instruction hits; the C9 header glyph slot gate uses actual p76/p78 OVERDOSE header glyph boundaries, differs from equal slots by at most 0.087628 px, reproduces active B4/G5 OVER in both projections, and reproduces p75 control OVER in both projections; and the C9 mirrored header glyph gate tests 8 normal/reversed-label and x-mirrored variants where active black streams are `OVER`, `DOSE`, `ESOD`, or `REVO`, p75 control matches the active black stream in all 8 variants, and strict instruction hits remain 0. The 3D reflection line-pitch stack gate shows three contextual p78/p79 reflected boxes can touch all four active targets only by using different per-target line shifts, while the same carriers also sweep broad page-76 controls `G3/G4/G5/O3/O4/O5`, with 0 strict instruction hits and 0 single global shifts covering O4/B4/G5/O5; the shifted-carrier content gate shows those carriers infer ordinary base rows 20/21, reproduce active line-gap phase `3/2/5`, but produce 12 row-context slices with 69 non-target words, 0 target-phrase-isolated slices, and 0 strict instruction hits. The page-76 highlight fold-axis population gate tests 141 horizontal/vertical/point axes from 10 highlight targets and finds 0 all-four active axes, 0 three-plus active axes, and 0 non-tautological two-active axes, with 0 strict instruction hits. The active line/corridor mirror-index gate finds the best axis at page line 27 / corridor 9 with 3 active hits, but it maps B4 to the non-active Novogratz line and has 0 all-four axes and 0 strict instruction hits. The G5-axis bold/highlight rescue gate keeps the same 3 active hits but still routes B4 to the non-active Novogratz signal row, yielding style stream `OBGO`, bold stream length 35, partial-bold stream `Nvz`, and 0 strict instruction hits. The page-center mirror guardrail tests 180-degree page rotation plus vertical/horizontal centerline mirrors and finds 0 all-four active re-hit scenarios, 1 total highlight contact, and 0 strict instruction hits. The OVERDOSE header ray fan gate tests 4 active rays and 3 non-active highlight control rays from the header center; active rays have 0 strict instruction hits, 0 all-quartet rays, and highlight-hit counts `[2, 1, 1, 3]`, while controls are comparable at `[1, 2, 2]`. The C9 glyph-center ray gate uses assigned glyph-slot top-center rays and finds the active stream repeats `OVED`, strict instruction hits remain 0, all-quartet rays remain 0, and active hit counts are only `[1, 1, 1, 2]`. The C9 target vertical chord gate uses exact target-center x chords through the C9 frame and again gets `OVED`, 0 strict instruction hits, 0 all-quartet chords, active hit counts `[2, 1, 1, 2]`, and control hit counts `[2, 1, 1]`. The C9 target horizontal chord gate uses exact target-center y rows through the C9 frame and finds 0 strict instruction hits, 0 all-quartet chords, active hit counts `[1, 1, 1, 1]`, and 6 non-active focus-row controls with word counts comparable to active rows. The current best scan is byte-locked, literal 78/79->76 leaf/spread physics is closed, the valid 75->76 leaf gives only upper-page hits, and the p78 source graphic text is thematic only. The source-acquisition packet integrity pass is green for files, visual panels, R1-R5 coverage, C2/C3/C4/C8 coverage, and active target handoff; supplemental handoff now points future review at the 4/4 crop sheet plus the Y/K-frame benchmark. The source-packet native benchmark bridge converts 15 benchmark boxes into native source coordinates after rotate180, preserving active line/corridor order `22 25 27 32` / `4 7 9 14`, C9 x-mirror invariance, and the measured `OVERDOSE` glyph sequence, but it is source-registration scaffolding only. The source-packet visual-state roundtrip recovers the active pixel state as `YKKY`, confirms all four active targets remain DOCM Typeka bold, keeps active native rotate180 crop mean diffs under `3.0`, and shows OVERDOSE glyph controls have max dark ratio `0.0`; this is still validation evidence, not R3. The source-packet alignment tolerance pass constrains future source matching to a narrow common window: all active targets survive only `+4px` outward padding and `±4px` all-direction shifts before black-highlight classification starts failing, while OVERDOSE controls remain non-active `N` states. The source-packet geometric fingerprint records active cluster box `[428, 2177, 1801, 2982]`, line/corridor gaps `3/2/5`, dx sign stream `-++`, dy sign stream `+++`, and native center roundtrip error `0.0px`; this is source-registration evidence only. The source-packet frame-normalized pass records C9 normalized centers `0.651,0.028; 0.136,0.289; 0.359,0.462; 0.540,0.921`, confirms `4/4` active targets fully inside the C9/Y-K frame, finds `0/4` full active targets inside the reflected p78 frame with only partial O5 overlap, and finds no simple C9-frame mirror with all-four re-hits at 4/25/50px thresholds. The source-packet color-profile manifest records active state stream `YKKY`, active Y orange range `0.7124-0.7666`, active K dark range `0.6592-0.6994`, active K orange max `0.0`, OVERDOSE control state stream `NNNNNNNNN`, control orange max `0.277`, and native roundtrip mean-diff max `2.9794`; this is visual source-matching evidence only. The source-packet repaired p78 frame residual records current/dx=-38/dx=-40 reflected-frame variants: max full-inside active count `0/4`, max partial-hit count `2/4`, best G5 gap `0.0px`, best O5 overlap `0.270725`, and repaired-frame B4/O4 still needing `503/173px` just to touch or `766/221px` to fully cover; this is source-registration residual evidence only. The source-packet repaired frame expansion leakage pass shows those touch/full-cover repairs are not selective: base frames already span 72 lower-corridor words, edge-touch expansions span at least 91 words with 89 non-target words, and full-cover expansions span 102 words, 92 non-target words, four non-active format signals, and 0 transcript/OCR-map hard instruction hits. The source-packet handoff integrity matrix checks 17 gates across orientation, order, visual state, bold/highlight authority, p78/C9 frame behavior, OVERDOSE controls, and leakage: contradictions `0`, selector unlocks `0`, extraction-ready gates `0`, with fingerprint `gates=17|pass=15|reject=8|contradictions=0|selectors=0|states=YKKY|lines=22-25-27-32|corr=4-7-9-14|shift=4|leakWords=102/92`. The source-packet false-positive guardrail flags 9 visual-only match classes as hard rejects without R3, with active order `22 25 27 32` / `4 7 9 14`, state `YKKY`, selector unlocks `0`, and fingerprint `guardrails=9|hardReject=9|states=YKKY|lines=22-25-27-32|corr=4-7-9-14|selectorUnlocks=0|requiresR3=1`. The source-packet R3 bridge audit scans canonical/plain/Markdown/annotated/correction layers and finds 31 active-target windows, 23 visual-only windows, 0 source-backed R3 bridge hits, 1 derived correction bridge window, 0 external raw-like R3 passes, and fingerprint `authority=4|targetWindows=31|visualOnly=23|sourceR3=0|derivedR3=1|externalRawR3=0|generatedUnitOrder=37|guardrails=9|selectorUnlocks=0`. The source-packet reopen trigger matrix converts those blocked visual paths into nine explicit source/provenance triggers, finds 0/9 satisfied now, keeps all 9 guardrails blocked, and records fingerprint `triggers=9|satisfied=0|sourceR3=0|states=YKKY|lines=22-25-27-32|corr=4-7-9-14|guardrailsBlocked=9|selectors=0`. The source-packet orientation disambiguator tests 5 candidate modes, accepts only the readable/upright source-comparison mode, flags 4 ambiguous signals (`YKKY`, `OBBO`, C9 x-mirror, OVERDOSE control state), keeps 6 source/geometry discriminators, and records fingerprint `modes=5|accepted=1|ambiguous=4|discriminators=6|states=YKKY|color=OBBO|lines=22-25-27-32|nativeLines=32-27-25-22|dx=-++|dy=+++|sourceR3=0|selectors=0`. The future-source scoring rubric fixes the numeric benchmarks: p78 current G5 gap `38px`, repair dx `-40`, and p77 near-miss gap `71.93px` versus line pitch `73.73px`. The rubric dry-run checks the current eight-path stack and finds `0` extraction-ready paths, with all `8` still failing R3.",
            "blockedBy": "No local source changes the geometry or supplies the missing extraction unit; the R1-R5 intake found zero local promoted cohorts and zero actionable unknown source candidates, the current gathered-local-source gate checked 364 candidates across 16 authority classes with 0 promoted and 0 manual R3 candidates, the corrected-topology 77->76 current-pixel white-mask test found all-four signal modes 0, best >=10% source coverage 3/4, best above control p95 1/4, paper texture confirmation 0, and source-backed R3 0, and the post-unlock arrival watch found zero new review candidates. Current scan remains the baseline, not final key material.",
            "nextAction": "Compare any true physical scan/photo, higher-resolution scanned source/export, or raw clue against `analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.md` and `analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.md` before reopening extraction.",
        },
        {
            "frontier": "external clue/provenance wording",
            "status": "open-but-source-dependent",
            "evidence": "Archived raw clue wording gives type/source/value (`private Bitcoin key`, `encoded`, `this piece`, `20 BTC`), Schott gives mirror-writing operation family, and Canva gives orientation/source-fidelity language.",
            "blockedBy": "Strict external clue intake found zero raw/raw-like R3 passes; existing local reports do not contain a source-backed instruction like `take first letters` or `read line X`.",
            "nextAction": "Search/inspect only for instruction language or source assets, not more private-key candidates.",
        },
    ]


def main() -> None:
    report_status = {name: exists(path) for name, path in REPORTS.items()}
    dead_count = count_dead_branches()
    summary = evidence_summary()
    frontier = classify_frontier()

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "missing-rule frontier synthesis; no key derivation, hashing, WIF, seed, or address checks",
        "reportStatus": report_status,
        "deadBranchCount": dead_count,
        "evidenceSummary": summary,
        "frontier": frontier,
        "decision": {
            "localSelectorSearch": "pause unless new clue/source changes the rule space",
            "highestValueNextMove": "new scan/physical/raw-clue asset validation against the source-acquisition packet and readable/upright 3D crop geometry",
            "activeValidationTargets": [
                "O4/B4/G5/O5 Y/K-frame quartet",
                "O5 shitcoiner at heart",
                "G5 Volcano Bonds",
                "L26-L29 source band",
                "p78 frame tri-contact",
            ],
            "sourceReopenGate": "use analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.md and analysis_outputs/source_audit/current_local_source_reopen_gate/current_local_source_reopen_gate.md; require R1-R5 before selector/key checks resume",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Missing-Rule Frontier Audit",
        "",
        "Scope: synthesize the current investigation frontier after the recent lower-corridor, R-K-Y, and color-swap closures. No key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Closed/deferred branch bullets in blacklist: `{dead_count}`",
        "",
        "## Top Target Evidence",
        "",
    ]
    for item in summary["topTargets"]:
        lines.append(f"- `{item['target']}` `{item['label']}`: score `{item['score']}`, independent layers `{item['layers']}`")

    lines.extend(["", "## Frontier", "", "| frontier | status | evidence | blocked by | next action |", "|---|---|---|---|---|"])
    for item in frontier:
        lines.append(
            f"| {item['frontier']} | `{item['status']}` | {item['evidence']} | {item['blockedBy']} | {item['nextAction']} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not run more local G5/O5 text-unit permutations under the current scan without a new clue naming an extraction unit.",
            "- Do not re-mine active page-76 highlight pixels or side/tail spill under the current scan; the latest control pass shows the active spill orders also occur in controls.",
            "- Do not re-open literal current-scan leaf physics: `78/79 -> 76` is not a same-leaf/facing-spread relation, and the valid `75 -> 76` leaf path misses the lower corridor.",
            "- Do not read p78 pull-quote wording as instruction text; it is thematic prose and has no unit/order terms.",
            "- Treat page 76 lower corridor as the validation surface, not as solved key material.",
            "- The next thing that can genuinely move the solve is a scan/physical comparison or external clue wording that names the selector.",
            "- The refreshed local source intake found no local cohort that passes R1-R5, so already-local files should not reopen extraction.",
            "- The strict archived external-clue intake found zero raw/raw-like R3 passes; do not promote terms found only in generated analysis prose.",
            "- Do not promote p80 package copy, symptom lists, relief words, or dose numbers as a current-scan R3 selector; keep p80 as C6 count/theme/source-validation evidence only.",
            "- Do not promote p80 visible numbers as the active quartet order; raw/canonical number streams do not contain page-line order `22 25 27 32`, corridor order `4 7 9 14`, or the full gap pattern `3 2 5`.",
            "- Do not promote the p73/p79 `RRLL` capsule direction as an active O4/B4/G5/O5 side-word or vertical-neighbor selector; the bounded boundary streams have 0 instruction hits.",
            "- Do not promote active target punctuation/enclosure as a selector; O4 quote+period, B4 dollar amount, G5 quotes, and O5 period preserve text authority but produce 0 instruction hits and no source-backed unit/order rule.",
            "- Do not promote active DOCM font-edge transitions as a Typeka Mix selector; all four active targets are regular-Typeka insulated (`R>Y/K>R`), have 0 direct Typeka Mix neighbors, and produce 0 instruction hits.",
            "- Do not promote active Typeka Mix proximity as a selector; O4/B4/G5 share the same broad El Salvador/Mike Novogratz Mix bracket, O5 is a separate endpoint, and the proximity streams have 0 instruction hits.",
            "- Do not promote active `OBBO`/`YKKY` pair symmetry as a fold/mirror selector; the natural orange/black pairs fail horizontal, vertical, and point-reflection tests, and the best p78-frame midpoint relation still misses by `180.92px`.",
            "- Do not promote the active O4/B4/G5/O5 bbox/hull envelope as a selector; it contains 89 OCR-map words, 86 non-target words, 0 strict instruction hits, and 12 same-size line-pitch shifted controls with comparable density.",
            "- Do not promote active target-center connector paths as a selector; the primary O4->B4->G5->O5 rail touches 9 OCR-map words, 6 non-target words, 0 strict instruction hits, and 10 shifted controls with comparable density.",
            "- Do not promote active line/corridor mirror indexes as a selector; the best axis at page line 27 / corridor 9 gives 3 active hits but maps B4 to the non-active Novogratz line, with 0 all-four axes and 0 strict instruction hits.",
            "- Do not promote the G5-axis bold/highlight rescue filter as a selector; it accepts the non-active Novogratz row as B4's mirror, yielding `OBGO`, `Nvz`, and 0 strict instruction hits.",
            "- Do not promote page-center 180-degree rotation or page-center mirrors as a selector; three bounded page-center transforms produce 0 all-four active re-hit scenarios, 1 total highlight contact, and 0 strict instruction hits.",
            "- Do not promote OVERDOSE header rays as a selector; active rays from the header center have 0 strict instruction hits, 0 all-quartet rays, and highlight-hit counts comparable to non-active highlight control rays.",
            "- Do not promote C9 glyph-center rays as a selector; assigned rays repeat the already-known `OVED` center-slot stream, have 0 strict instruction hits, 0 all-quartet rays, and do not improve the current OVERDOSE evidence.",
            "- Do not promote exact target-x C9 vertical chords as a selector; they repeat `OVED`, have 0 strict instruction hits, 0 all-quartet chords, and non-active highlight controls can touch active targets with the same `[2, 1, 1]` pattern.",
            "- Do not promote exact target-y C9 horizontal chords as a selector; active rows each hit only their own target, have 0 strict instruction hits, and non-active focus rows inside the same frame are ordinary comparable article rows.",
            "- Do not promote p78 frame-center reflection as a selector; six bounded same-layout/current-mirror reflection modes produce 0 instruction hits, 0 strong active-target re-hits, and only weak B4/O5 partial contacts with max overlap `0.198042`.",
            "- Do not promote p78 frame edges/centerlines as a selector; 12 same-layout/current-mirror lines touch B4/G5/O5 but miss O4, create 0 instruction hits, and reproduce already-known same-slot geometry.",
            "- Do not promote the O4 frame-rescue geometry as a selector; the dual p78 frame envelope recovers O4 with a clean 3-line top extension, but this is a future source-comparison benchmark only until source wording names reading above/extending the frame or a three-line offset.",
            "- Do not promote the O4 frame-rescue offset control as a selector; 3-up is the minimum integer top-only offset that touches all four active targets, but larger top offsets also work and full coverage requires a 3-up/1-down envelope.",
            "- Do not promote the O4 frame-rescue content gate as a selector; the compact 3-up/1-down full-coverage envelope captures the entire L22-L32 corridor band, 92 non-target words, 4 non-active highlight entries, and 0 hard instruction hits.",
            "- Do not promote the O4 frame-rescue signal-stream gate as a selector; the same envelope's styled stream is `YBKKBMMY`, which contains the active `YKKY` quartet plus four non-active styled groups and 0 hard instruction hits.",
            "- Do not promote the O4 frame-rescue Y/K filter as a selector without source wording; Y/K inside the frame isolates the active quartet, but full-page Y/K has four non-active controls and the intersection has 0 hard instruction hits.",
            "- Do not promote the O4 frame Y/K unit-order gate as a selector; the quartet is isolated, but 20 bounded unit/order streams have 0 hard instruction hits and group/vertical order disagrees with left-to-right spatial order unless an external order is assumed.",
            "- Do not promote C9 frame same-slot geometry as a selector; the C9 rectangle fully covers all four active p76 targets, but it is horizontally mirror-invariant, broad across repeated OVERDOSE lower-page slots, and has 0 strict unit/order hits in page controls.",
            "- Do not promote C9 internal edge/axis/diagonal/pair geometry as a selector; only O4 has a strict top-edge coincidence, while centerline/diagonal hits and mirror-pair hits are both 0.",
            "- Do not promote O4's C9 top-edge highlight contact as a selector; it is the only strict <=4 px highlight contact, but a p75 control highlight sits near the same C9 top edge at <=25 px and no unit/order rule is supplied.",
            "- Do not promote C9 bold-letter or general highlight density as a selector; active bold letters match only O4/O5, B4 has no line-level bold letters, G5's line-level bold letters are `IMF`, and four non-active C9 lines carry format signals.",
            "- Do not promote line-level bold letters, Markdown bold, annotated notes, or correction mentions as extraction permission; the C9 active format witness reconciliation keeps DOCM/high-res/crop-pack as source-comparison authority only and still supplies no R3 unit/order.",
            "- Do not promote C9 OVERDOSE 8-letter slot mapping as a selector; active centers yield `OVED`/`VEDO`, span bins yield `OVERRDODOS` only by combining black B4/G5 with orange O4/O5, and the streams contain 0 strict unit/order instruction hits.",
            "- Do not promote B4/G5's C9 grey/black `OVER` pair as a selector; the same lower-frame slot rule gives non-active p75 `Don't fall for shitcoinery` an `OVER` span by itself, and the grey/black control has 0 strict unit/order hits.",
            "- Do not tune C9 OVER slot shifts or overlap thresholds into a selector; the canonical B4/G5 `OVER` is controlled by p75, active `OVER` appears in only 45/99 bounded tolerance combinations, and it fails completely at 150 px and 200 px thresholds.",
            "- Do not promote C9 vertical OVERDOSE bands as a selector; the active quartet yields `OERE` top-to-bottom and `EODO` bottom-to-top, while active vertical streams have 0 layout hits and 0 strict unit/order instruction hits.",
            "- Do not promote actual OVERDOSE header glyph slots as a selector; p76/p78 glyph projections differ from equal slots by only 0.087628 px, reproduce B4/G5 OVER, and reproduce p75 control OVER, with 0 strict instruction hits.",
            "- Do not promote mirrored OVERDOSE header glyph slots as a selector; normal/reversed labels and x-mirrored geometry toggle the active black stream among `OVER`, `DOSE`, `ESOD`, and `REVO`, but p75 control matches in all 8 variants and strict instruction hits remain 0.",
            "- Do not promote OVERDOSE glyph edges/centers as fold axes; native header axes mirror the active centers outside the C9 frame, and C9-projected axes can keep all four centers inside slots only as non-word fragments `VODE`, `RESD`, `ODRV`, and `ESOR`, with 0 layout-term or strict instruction hits.",
            "- Do not promote Typeka Mix, Typeka bold, manual bold, font transitions, or the repaired `R-K-Y` style trio as a current-scan R3 selector; keep Typeka as formatting/corridor/source-validation evidence only.",
            "- Do not promote folded/mirrored 3D geometry, reflection-box ids, anchors, viewer focus/layout modes, or 78/79 two-hand streams as a current-scan R3 selector; keep 3D geometry as locator/orientation/source-validation evidence only.",
            "- Do not promote integer line-pitch walking of 3D reflected boxes as a selector; it can touch O4/B4/G5/O5 only with different per-target shifts, has 0 single global all-four shifts, sweeps broad page-76 highlight controls, and has 0 strict instruction hits.",
            "- Do not promote shifted 3D reflection carrier rows as extraction permission; they reproduce active line-gap phase `3/2/5` from ordinary base rows 20/21, but the 12 active slices contain 69 non-target words, 0 isolated target-phrase slices, and 0 strict instruction hits.",
            "- Do not promote page-76 highlight-population fold axes as a selector; 141 horizontal/vertical/point axes produce 0 all-four active axes, 0 three-plus active axes, and 0 non-tautological two-active axes.",
            "- Do not promote the page-76 O-B-B-O highlight cluster, edge contacts, fill residue, spill/tail side bias, or color-swap as a current-scan R3 selector; keep it as target-location/source-validation evidence only.",
            "- Do not promote comparison OVERDOSE layouts, broad house style, capsule recurrence, or bitcoin4 low-res witness as a current-scan R3 selector; keep them as style/provenance/source-validation evidence only.",
            "- Use the OVERDOSE style uniqueness audit as the comparison-article house-style stop-check; Issue 24 has sustained highlighter-like body pages 3-8 and orange-band pages 3-8, independent comparison PDFs show only partial/isolated highlighter-like pages (`issue26` 4-5, `issue27` 1, `bitcoin3` 7-8), `bitcoin4.pdf` is a lower-quality Issue 24 witness rather than an independent source, and the comparison set supplies no page-76 geometry or extraction unit.",
            "- Do not promote repeated `OVERDOSE` header/layout registration as a current-scan selector; same-layout/header translation fully covers B4/G5 and clips O5 but misses O4, while the current mirror clips only O5, and both have 0 strict unit/order hits.",
            "- Do not promote the p78 `OVERDOSE` same-layout slot as a current-scan selector; the slot hits B4/G5/O5 on page 76 but has 0 hard instruction hits and remains a future source-comparison control only.",
            "- Do not promote comparison-PDF metadata as Typeka proof or a font selector; the independent comparison PDFs are image-only/raster witnesses with 0 embedded font witnesses and 0 Typeka resources, while `Article with Fonts.docm` remains the only local Typeka font witness.",
            "- Do not promote active `OBBO` quartet recurrence as extraction permission; the lower page-76 quartet is distinctive against local independent controls, but it supplies location/source-validation evidence only and still lacks R3 unit/order wording.",
            "- Do not treat the aggregate current evidence stack as extraction permission; the active unlock matrix checks 8 paths, all 8 fail R3 unit/order evidence, and 7 fail R5 controlled improvement.",
            "- Do not reopen extraction based on post-unlock local filesystem arrivals; the bounded Desktop/Downloads/Documents watch found 0 candidate files needing R1-R5 review.",
            "- The source-acquisition packet is integrity-checked as a future-evidence gate; this readiness pass does not unlock a current-scan selector.",
            "- The source-packet Y/K-frame benchmark sync is a supplemental handoff only: it records that `Y/K + frame` isolates O4/B4/G5/O5 with 0 in-frame non-active Y/K groups, but full-page Y/K has four non-active controls and R3 unit/order remains absent.",
            "- The source-packet geometric fingerprint is source-registration only: it records the active quartet's cluster box, line/corridor gaps, center-step signs, and native rotate180 roundtrip, but still supplies no R3 unit/order selector.",
            "- The source-packet frame-normalized geometry is source-registration only: it gives scale-stable C9/Y-K coordinates and rules out simple C9-frame mirror re-hit, but still supplies no extraction unit or order.",
            "- The source-packet color-profile manifest is source-validation only: it records active orange/black separation against OVERDOSE controls for future source matching, but still supplies no extraction unit or order.",
            "- The source-packet repaired p78 frame residual is source-registration only: dx=-38/-40 improves the G5 edge and O5 clip benchmarks, but max full containment remains `0/4`, B4/O4 still need large expansions, and no unit/order selector is supplied.",
            "- Do not promote source-packet repaired frame expansion as a selector; forcing O4/B4/G5/O5 full coverage takes the whole L22-L32 lower-corridor band, 102 words, 92 non-target words, four non-active format signals, and 0 hard instruction hits.",
            "- Use the source-packet handoff integrity matrix as the compact current-stack checklist; it finds 0 contradictions, 0 selector unlocks, and 0 extraction-ready gates across 17 orientation/order/color/frame/OVERDOSE/format/leakage gates.",
            "- Use the source-packet false-positive guardrail with the handoff matrix; color/state, native raw order, C9 frame containment, OVERDOSE slot spelling, p78 contacts/leakage, bold/highlight witnesses, active-box OCR, and loose alignment are hard rejects without source-backed R3 unit/order wording.",
            "- Use the source-packet R3 bridge audit as the contamination check: authoritative local text has 31 active-target windows and 23 visual-only windows but 0 source-backed R3 bridge hits; the one derived correction bridge and 37 generated report unit/order mentions are requirements/prose, not puzzle evidence.",
            "- Use the source-packet reopen trigger matrix before future source review; it defines the exact external/source observation needed for each visual class and finds 0/9 triggers satisfied by current local evidence.",
            "- Use the source-packet orientation disambiguator before accepting a future visual match; `YKKY`, `OBBO`, and C9 frame containment are orientation-ambiguous, so require readable page-line order `22 25 27 32`, corridor order `4 7 9 14`, center-step signs `-++/+++`, and the native rotate180 bridge.",
            "- Use the source-packet orientation control quartets as a pattern-vs-geometry guardrail; `YKKY` appears in 11/70 full-page Y/K combinations and 10 mixed/non-exact controls, but the active quartet is the only contiguous filtered Y/K window and the only C9 format-line combination with exact `3/2/5` line gaps, still with 0 source-backed R3 hits.",
            "- Use the source-packet source-review gate as the compact future-evidence order: R1 distinct source, R4 readable/upright orientation, pattern controls, R2/R5 preservation and controlled improvement, then R3 source-backed unit/order; the current seven-path dry run has 0 extraction-ready paths and 7 R3 failures.",
            "- Use the source-packet OVERDOSE transform control as the current OVERDOSE geometry guardrail; measured header glyph boxes collapse to equal-slot C9 mapping, active centers stay `OVED`/`VEDO`, active black `OVER` is matched by p75 in 8/8 mirror/reverse variants, and source-backed R3 remains 0.",
            "- Use the source-packet fold/format intersection control as the folded-geometry guardrail; folded carriers need per-target shifts, shifted slices contain 69 non-target words and 0 isolated target slices, highlight axes have 0 all-four active hits, and source-backed R3 remains 0.",
            "- Use the source-packet terminal coverage matrix as the current cadence stop-check; all 8 requested focus areas have explicit guardrails, 0 areas are extraction-ready, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the source-packet active target authority crosscheck as the exact-text/format stop-check; all four active targets are present in canonical, Markdown, and annotated witnesses and pass format authority, while the raw plain G5 omission is controlled and selector-permission corrections remain 0.",
            "- Use the source-packet active format stream control as the active text/format/OVERDOSE stream stop-check; 12 named stream modes have 0 strict instruction hits, the only OVER streams are controlled by p75, YKKY has 11 full-page combinations, and source-backed R3 remains 0.",
            "- Use the source-packet active index-slot control as the line/corridor-vs-OVERDOSE stop-check; line/corridor parity reproduces YKKY, but line/corridor indexes have 0 simple modulo-8 slot fits, slot parity is KKYY, slot gaps are 4/1/2 rather than 3/2/5, and source-backed R3 remains 0.",
            "- Use the source-packet center rotation word control as the short-word artifact stop-check; rotating/reversing active center streams creates tempting words including DOVE, ROSE, SORE, and EROS, but source start/rotation cue hits remain 0, p75 still matches active black in 8/8 variants, and source-backed R3 remains 0.",
            "- Use the source-packet color split span control as the orange/black OVERDOSE-span stop-check; 72 color/slot span streams have 0 strict instruction hits and 0 source color-split cue hits, pure orange spans have 0 layout hits, active black streams are only DOSE/ESOD/OVER/REVO, and p75 matches active black in 8/8 variants.",
            "- Use the source-packet dominant overlap slot control as the maximum-overlap stop-check; dominant slot selection matches center-slot selection in 16/16 active line/x streams, has 0 active center mismatches, 0 active dominant ambiguities, 0 layout hits, and 0 source dominant-overlap cue hits.",
            "- Use the source-packet span edge slot control as the first/last touched OVERDOSE-slot stop-check; 80 span-edge streams have 0 layout hits, 0 thematic hits, 0 source edge-slot cue hits, and source-backed R3 remains 0.",
            "- Use the source-packet overlap width profile control as the measured-overlap stop-check; active profiles are only two/three-slot phrase-width measurements, p75 is a four-slot control, mirror variants flip edge bias, and source overlap-width/profile cue hits remain 0.",
            "- Use the source-packet span neighbor slot control as the adjacent/outside-slot stop-check; 120 immediate-neighbor streams have 0 layout hits, 0 thematic hits, 0 source neighbor-slot cue hits, and source-backed R3 remains 0.",
            "- Use the source-packet span complement slot control as the untouched/remainder-slot stop-check; 40 complement streams all create layout fragments because they preserve five or six OVERDOSE letters, p75 controls also create layout hits, source complement/remainder cue hits remain 0, and source-backed R3 remains 0.",
            "- Use the source-packet local asset orientation gate as the local-source stop-check; 40 image assets and 3 PDFs were reviewed, only 2 true page-76 image matches were found, 0 higher-resolution page-76 matches were found, R1 distinct improved local candidates remain 0, and source-backed R3 remains 0.",
            "- Use the source-packet PDF render quality gate as the fresh-PDF-extraction stop-check; 3 PDFs, 24 rendered pages, and 24 embedded page images produced only 1 true page-76 PDF page at the already-known 2544x3264 magazine resolution, with 0 higher-resolution page-76 hits, 0 R1 improved PDF candidates, and source-backed R3 remains 0.",
            "- Use the current-scan held-to-light simulator plus active-box balance gate as the visual light-table surface; PDF-extracted pages are normalized into readable/upright orientation, the natural 75->76 same-leaf active coverage is only 0.1003 with B4 at 0.0000, the best bounded same-leaf 75->76 shift is a forced -220/+200 translation and still has 0 all-four >=10% rows, while only nonphysical 79->76 controls reach all-four >=10%; source-backed R3 remains 0.",
            "- Use the current-scan held-to-light component readability gate as the valid-leaf readability stop-check; 3 page-75->76 modes and 12 active target rows produce 0 readable rows in the physically natural view, only 2 readable rows in the forced same-leaf guardrail, 0 all-four readable modes, 0 strict instruction rows, and source-backed R3 remains 0.",
            "- Use the current-scan held-to-light opacity gate as the color/opacity stop-check; 4 scenarios and 36 blend rows show the physically valid natural 75->76 view has best all-box darkening `0.00`, the best forced/control row is nonphysical 79->76 multiply@0.75 with only `6.33`, no natural or control row reaches all-four delta>=16, and source-backed R3 remains 0.",
            "- Use the current-scan light-table blend-mode gate as the blend/alpha stop-check; 4 scenarios, 5 blend modes, 3 alpha levels, and 60 blend rows show natural 75->76 can make all four active boxes visually pop only under average blend, but 0 natural rows are all-four source-supported and source-backed R3 remains 0.",
            "- Use the current-scan valid-leaf source-ink landing gate as the physical landing stop-check; natural 75->76 source-ink support is only O4/G5/O5, B4 has `0.0000` source ink, all-four source support is false, and source-backed R3 remains 0.",
            "- Use the current-scan all-leaf light-table parity and density-calibration gates as the natural leaf-pair stop-check; valid pairs 75->76, 77->78, and 79->80 give page-76 active ink/feature outliers 0/0, density-normalized active ink/feature outliers 0/0, all-four normalized outliers 0/0, and source-backed R3 remains 0.",
            "- Use the current-scan OVERDOSE density-outlier provenance gate as the slot-density stop-check; the 3 normalized outlier columns are `R/O/S` in x-order and `S/O/R` by ink strength, touch only 3/4 active targets, miss B4, contain 0 strict source/target instruction hits, and source-backed R3 remains 0.",
            "- Use the current-scan OVERDOSE source-highlight ablation gate as the highlight-dependence stop-check; removing mirrored `p75_orange_6/7/8` drops the outlier signal by 30.4% on average, demotes `R`, leaves only partial `O/S`, creates 0 non-outlier status flips, and source-backed R3 remains 0.",
            "- Use the current-scan active source-highlight ablation gate as the active-box highlight stop-check; removing all mirrored page-75 highlights leaves positive targets unchanged at O4/G5/O5, B4 remains 0.000000, all-four support remains false, and source-backed R3 remains 0.",
            "- Use the current-scan physical bleed-through correlation gate as the scan-translucency stop-check; fixed valid leaf pairs have 0/3 deltas above same-target invalid-source p95, page 75->76 delta `0.707301` stays below invalid p95 `0.961401`, active boxes above invalid p95 are 0/4 with 0/4 enough source-signal pixels, and source-backed R3 remains 0.",
            "- Use the current-scan active quartet fingerprint specificity gate as the box-geometry control; among 13 available page-76 highlight/annotation rows and 715 top-to-bottom quartets, only O4/B4/G5/O5 matches `YKKY/OBBO/3-2-5/OVED`, but source-backed R3 remains 0 and this stays a registration fingerprint, not an extraction selector.",
            "- Use the current-scan target witness-box substitution gate as the box-authority control; among 8 same-target O4/B4/G5/O5 witness substitutions, only the exact active-index/visual duplicate boxes preserve both line gaps `3/2/5` and C9 stream `OVED`, while annotation substitutions create 0 combined hits and source-backed R3 remains 0.",
            "- Use the current-scan page-76 image witness state-stability gate as the image-witness control; 26 full-page images produce 3 exact page-76 witnesses, all 3 preserve `YKKY/OBBO/OVED`, 9 near controls do not create a changed active-state witness, and source-backed R3 remains 0.",
            "- Use the current-scan page-76 image witness micro-registration gate as the local-shift control; across 3 exact page-76 witnesses and 12 active target checks, a +/-8px search finds 0 nonzero best shifts and 0.000 max zero-to-best improvement, so remaining crop differences are raster/JPEG differences, not geometry drift.",
            "- Use the current-scan active-box OVERDOSE edge-residue gate as the post-authority edge-ruler stop-check; exact active centers repeat `OVED` but exact close rows any/left/center/right at <=16px are only `3/2/0/0`, the only all-four any-anchor close variant uses a substituted annotation box, hidden edge-residue candidates are 0, and source-backed R3 remains 0.",
            "- Use the current-scan valid-leaf jitter source-ink rescue gate as the small-registration stop-check; 81 credible and 289 extended shifts have 0 B4-positive rows, 0 all-four source-supported rows, and source-backed R3 remains 0.",
            "- Use the current-scan page-frame/trim registration gate as the hidden-trim/skew stop-check; pages 75/76/78/79 share the same current canvas class, the valid 75->76 pair has identical `2544x3264` canvases, 0 pages expose all four frame-like physical edges, trim/skew correction candidates are 0, and source-backed R3 remains 0.",
            "- Use the current-scan content-box registration gate as the content-envelope normalization stop-check; all-page content shift is unstable, lower-half content shift is stable but clipped to canvas/band edges, the best landing remains natural `3/4`, B4 stays `0.0000`, and source-backed R3 remains 0.",
            "- Use the current-scan header/footer lane registration gate as the visible-article-lane held-to-light stop-check; top-header, footer, lower-body, header/footer mean, and natural hflip rows give best valid mode `lower_body_lane`, but only `3/4` active boxes are supported, above-control-p95 is `0/4`, invalid controls can reach `4/4`, and source-backed R3 remains 0.",
            "- Use the current-scan lane affine registration gate as the visible-lane scale/stretch stop-check; top/header+footer and top/header+lower-body affine transforms give best valid mode `top_header_lane+lower_body_lane_affine`, but only `3/4` active boxes are supported, above-control-p95 is `0/4`, invalid controls can reach supported/above-p95 `4/4`, and source-backed R3 remains 0.",
            "- Use the current-scan lane affine source trace as the provenance stop-check for the affine near miss; 3 valid affine modes trace 12 rows, 9 source-word rows, and 51 page-75 source-word hits, but above-control-p95 rows are 0, all-four modes are 0, the lone strict hit is unit-only `words` in ordinary prose, and source-backed R3 remains 0.",
            "- Use the current-scan source-layer landing gate as the color-layer held-to-light stop-check; black/orange/grey/feature/broad source masks across natural, all-content, and lower-half registrations give B4 positive rows `0/15`, all-four supported layer/modes `0`, and source-backed R3 remains 0.",
            "- Use the current-scan source-layer miss-distance gate as the crop/threshold miss stop-check; B4 needs at least 22px broad expansion and 136px feature expansion, all-four within-16px layer/modes are 0, and source-backed R3 remains 0.",
            "- Use the current-scan B4 broad-contact provenance gate as the broad-mask rescue stop-check; the all-content B4 rescue is one broad-only `[242,242,242]` pixel at 32px expansion, has 0 feature pixels, 0 source words within 128px, nearest OCR word `lab` at 249px, and source-backed R3 remains 0.",
            "- Use the current PDF B4 contact pixel provenance gate as the PDF/render carrier stop-check; 3 PDFs / 6 embedded-render rows keep the point broad-positive, the byte-locked `magazine.pdf` row remains broad/background only, duplicate lower-res carriers account for the feature-colored contacts, hidden/render-only selector candidates stay 0, and source-backed R3 remains 0.",
            "- Use the current PDF duplicate-background feature artifact gate as the duplicate-carrier control; B4 is feature-classified in 4/4 duplicate rows but 0/2 byte-locked magazine rows, while 40/54 local matched background controls and 39/57 page-grid controls also convert in all duplicate rows, so the duplicate feature contact is not unique source ink and source-backed R3 remains 0.",
            "- Use the current PDF page-76 carrier-state stability gate as the target/OVERDOSE duplicate-carrier stop-check; duplicate carriers create 10 active and 32 OVERDOSE-slot presence mismatches, but active/slot outliers above matched line-shift control p95 are 0/0, all-four active outlier is 0, and source-backed R3 remains 0.",
            "- Use the current-scan B4 self-signal guardrail as the average-blend false-positive stop-check; B4 has source ink `0.0000`, target-only delta share `0.9957`, source-supported delta share `0.0000`, average-delta outlier `+85.06` above matched controls, all-four source-supported outliers `0`, and source-backed R3 remains 0.",
            "- Use the current-scan light-table self-signal partition gate as the all-active average-blend decomposition; 4 active boxes, 24 line-shift controls, and 8 OVERDOSE slots show active target-only dominance in 4/4, source-supported dominance in 0/4, active source-supported mean/share above control p95 in 0/4 and 0/4, active min target-only delta share `0.8473`, active max source-supported share `0.1517`, and source-backed R3 remains 0.",
            "- Use the current-scan OVERDOSE slot source-support trace as the projected-slot provenance stop-check; 8 slots trace to page-75 source bands, high source-supported slots are the contiguous `OSE@5-7` run (`O5,S6,E7`), those bands contain 111 source-word hits across 58 OCR rows, only the unit-only prose term `words` appears, high-slot action/order instruction hits are 0, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current PDF OVERDOSE slot source-support trace as the scan/render consistency stop-check; 6 PDF carrier rows were checked, the byte-locked `magazine.pdf` render and embedded canvas both reproduce `OSE@5-7`, duplicate/Google carriers over-support all slots as `OVERDOSE@0-7`, action/order hits remain 0, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current PDF OSE source-highlight phrase gate as the highlight-bridge stop-check for the stable `OSE@5-7` run; the byte-locked render has source-highlight contact in 3/3 high slots but target-highlight contact and two-sided bridge in only 2/3, high-slot action/order rows are 0, selector candidates are 0, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current PDF OSE highlight mirror geometry gate as the geometry-only stop-check for the stable `OSE@5-7` source highlights; the two OSE page-75 orange highlights mirror into OVERDOSE slot bands in 2/2 rows, but page-76 highlight contact is 0/2, active O4/B4/G5/O5 target contact is 0/2, selector candidates are 0, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current PDF OSE highlight translation rescue gate as the scan-slip/translation stop-check; natural active coverage is 0/4, best coverage within 160px is 0/4, the first active hit needs a 190px shift, two-target coverage needs a 928px horizontal relocation, three/four-target coverage is impossible, selector candidates are 0, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current-scan valid-leaf bleed-through control grid as the physical light-table stop-check; natural 75->76 source-only active coverage is only mean/min `0.0032/0.0000`, the best small-jitter shift is `-80,-20` with mean/min `0.0128/0.0000`, no active targets reach 10% or 25% source-only coverage, no targets reach the 75th percentile versus same-size controls, and source-backed R3 remains 0.",
            "- Use the current-scan valid-leaf local-warp gate as the page-curl/warp upper-bound stop-check; even when each O4/B4/G5/O5 box gets an independent +/-120 px local translation over 169 shifts, active best source-only coverage is max/min/mean `0.0693/0.0038/0.0248`, 0/4 active boxes exceed same-size control p95, 0 reach 10% or 25%, controls reach `0.9982`, projected OVERDOSE slots max at `0.2575`, and source-backed R3 remains 0.",
            "- Use the current-scan valid-leaf local-warp source trace as the provenance stop-check for the local-warp upper bound; 12 active/OVERDOSE trace rows have 115 components, 143 page-75 source-word hits, 0 strict instruction rows, only 3 ordinary `bitcoin` context rows in projected OVERDOSE slots, 0 active or slot strict rows, and source-backed R3 remains 0.",
            "- Use the current-scan valid-leaf edge-contact control as the boundary-contact stop-check; natural 75->76 edge-ring source-only coverage is mean/min `0.0418/0.0000`, only 1 target reaches 10%, 0 reach 25%, 0 reach the 75th percentile versus same-size controls, the `-80,-20` small-jitter mode has 0 targets at 10% or 25%, and source-backed R3 remains 0.",
            "- Use the current-scan valid-leaf edge source trace as the provenance stop-check for boundary contacts; 8 traced rows have 6 component rows, 6 source-word rows, 42 page-75 source-word hits, 0 strict instruction rows, 0 context-term rows, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current-scan valid-leaf interior source trace as the provenance stop-check for interior bleed; 8 traced rows have 3 component rows, 14 total components, 727 component pixels, 3 source-word rows, 4 page-75 source-word hits, 0 strict instruction rows, 0 context-term rows, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current-scan valid-leaf glyph-slot source trace as the OVERDOSE-slot provenance stop-check; 8 target rows and 20 slot rows produce streams `S.RD/...D` and `S.RR/..RR`, with 4 component rows, 19 components, 830 component pixels, 5 page-75 source-word hits, 0 strict instruction rows, 0 context-term rows, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current-scan valid-leaf channel source trace as the color/channel provenance stop-check; 8 target rows and 24 channel rows have 5 component rows, 0 orange component rows, 35 components, 1494 component pixels, 6 page-75 source-word hits, 0 strict instruction rows, 0 context-term rows, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current-scan valid-leaf word-collision trace as the OCR word-level light-table stop-check; 8 active rows have 6 source-word rows, 5 collision rows, 32 page-75 source words, 18 page-76 target words, 27 source/target word collision pairs, 0 strict instruction rows, 0 context-term rows, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current-scan valid-leaf line-band trace plus strict/target-context disambiguation as the OCR line-level light-table stop-check; 8 active rows have 6 source-line rows, 6 overlap rows, 14 projected page-75 source lines, 20 page-76 target lines, 13 source/target line overlaps, the lone source strict-token row is only unit-only `words` prose on O5, and target-side `sell`/`mine`/`heart` context yields 0 action/unit/order carriers, 0 instruction candidates, source-backed R3 0, and satisfied reopen triggers 0/9.",
            "- Use the current PDF page-box pair geometry gate as the valid-leaf PDF layout stop-check; all 3 current PDF page-75/page-76 pairs have identical boxes, rotations, image rects, and scales, the 2 low-resolution duplicate PDFs have identical side margins on both pages, placement offsets are 0, hidden pair-layer candidates are 0, and source-backed R3 remains 0.",
            "- Use the current PDF all-leaf imposition consistency gate as the scanned-page pair stop-check; 3 PDFs, 18 inspected page records, and 9 leaf pairs preserve identical front/back geometry, all 3 PDFs are uniform across pages 75-80, duplicate side margins are global, placement-offset pairs and hidden pair-layer candidates are 0/0, and source-backed R3 remains 0.",
            "- Use the current PDF leaf-pair texture correlation gate as the embedded-image physical-mirror stop-check; 3 PDFs, 9 leaf pairs, and 36 fixed-transform rows show physical back-side mirror best in 0/9 pair rows and 0/3 page-75/76 rows, page-75/76 physical active-region max correlation/IoU is `-0.0158/0.0500`, the lone all-four >p95 row is `magazine.pdf` same-side/no-mirror control, and source-backed R3 remains 0.",
            "- Use the current PDF native image registration gate as the exact embedded-image light-table stop-check; all 3 page-75/page-76 pairs keep the same image rect with 0 placement-offset pairs, exact native registration gives 12 active rows with only 2 above control p95, 2 at >=10%, 2 at >=25%, 0 PDFs with all four active above p95 or >=10%, controls reach `0.8795`, projected OVERDOSE slots reach `0.6341`, and source-backed R3 remains 0.",
            "- Use the current PDF native registration candidate source trace as the provenance stop-check for the exact-registration low-res O4/slot0 anomaly; 4 threshold-crossing rows trace to 34 components and 198756 source-only pixels, but only 2 rows hit page-75 source words, both active O4 duplicates hit ordinary `Bitcoins/Buterin` context, slot0 has 0 source words, strict instruction rows are 0, and source-backed R3 remains 0.",
            "- Use the current PDF held-to-light composite polarity gate as the exact PDF-native simulator stop-check; 3 PDFs x 4 fixed orientation variants create 12 variants and 48 active rows, the original-resolution `magazine.pdf` physical-back mirror has 0 active boxes >=10% and mean source-only coverage `0.0033`, derivative PDFs can reach 3 active boxes >=10% but 0 variants have all four active >=10% or above control p95, controls reach `0.9998`, and source-backed R3 remains 0.",
            "- Use the current PDF held-to-light candidate source trace as the provenance stop-check for derivative composite hits; 23 threshold-crossing rows trace through their fixed orientation transforms to 203 components and 581806 source-only pixels, with 19 source-word rows, 110 page-75 source-word hits, 0 strict instruction rows, only 5 ordinary context hits, 0/9 reopen triggers, and source-backed R3 remains 0.",
            "- Use the current PDF held-to-light all-target phrase gate as the full-quartet text stop-check; tracing all O4/B4/G5/O5 boxes through 3 PDFs x 4 fixed orientations gives 6 all-four source-word variants and 102 page-75 word hits, but strict instruction rows and action/order rows are both 0, the true `magazine.pdf` physical-back orientation has no complete phrase, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current PDF held-to-light color phrase gate as the active color-order stop-check; grouping fixed held-to-light source words by `Y/orange` and `K/black` across 12 variants and 60 stream rows yields 510 page-75 word hits but 0 strict instruction hits, 0 action/order hits, 0 color selector candidates, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the current PDF held-to-light component readability gate as the exact-composite crop-readability stop-check; 23 threshold-crossing rows contain 203 source-only components and 122 clean letter-like components, but only 5 rows are visually readable-like, 18 are merged or edge-dominated, source-word hits remain ordinary page-75 prose at 110 words, strict instruction hits are 0, selector candidates are 0, source-backed R3 remains 0, and satisfied reopen triggers remain 0/9.",
            "- Use the page-76 highlight edge slot-ruler gate as the highlight/OVERDOSE fold-ruler stop-check; 5 highlights produce 15 vertical and 15 horizontal axes, the direct active center stream remains `OVED`, 5 vertical axes keep all four mirrored active centers inside C9 slots but produce no `OVER`/`DOSE` layout-term streams, 0 horizontal axes put all four mirrored centers inside the C9 frame Y-band, strict instruction axis hits are 0, and source-backed R3 remains 0.",
            "- Use the current PDF leaf-image identity gate as the page-75/page-76 source-raster stop-check; 12 image records and 6 leaf pairs are all current-scan or lower-resolution derivatives, higher-resolution records/pairs are 0/0, distinct improved scan/source candidates are 0, PDF soft-mask/multi-image page candidates are 0/0, and source-backed R3 remains 0.",
            "- Use the current PDF render leaf simulation gate as the renderer-vs-embedded light-table stop-check; 7 render/embedded/canonical pairs and 28 target rows have max mean source-only coverage `0.2119`, max targets above 10%/25% both `2`, all-four >=10% and >=25% pair counts both 0, render-vs-embedded page MAD max `37.2097`, active-box MAD max `26.9905`, and source-backed R3 remains 0.",
            "- Use the current PDF low-res render source trace as the provenance stop-check for derivative-PDF O4/B4/G5 inflation; 12 trace rows collapse to 6 unique trace shapes, O5 is skipped below threshold in all pairs, traced source boxes contain ordinary page-75 prose or blank/grey margins, strict instruction rows are 0, all-four eligible trace pairs are 0, and source-backed R3 remains 0.",
            "- Use the current PDF OCR reverse-leaf source trace as the hidden-text-layer stop-check for valid page 75 -> 76 mirror geometry; 3 PDF OCR layers yield 2 usable page-75 fits, 232/232 inlier token pairs, 12 target rows, 6 PDF word rows, 6 exact-box word rows, 0 strict instruction rows, 0 all-four exact-box PDF trace pairs, and source-backed R3 remains 0.",
            "- Use the current-scan OVERDOSE slot-shape phase control as the vertical-phase guardrail; 13 lower line groups produce 3 same 3/2/5 slot-shape scenarios, only 1 overlaps all active boxes, two shifted controls hit ordinary bitcoin/IMF context, strict instruction rows are 0, active-phase context hits are 0, and source-backed R3 remains 0.",
            "- Use the current-scan OVERDOSE x-slot phase control as the horizontal-phase guardrail; 8 slot-shift scenarios produce 3 all-four-overlap phases because the active boxes are wide relative to slot spacing, shifted phases hit ordinary `bitcoin`/`IMF`/`sell` context, strict instruction rows are 0, and source-backed R3 remains 0.",
            "- Use the current PDF container metadata gate as the hidden-container stop-check; 3 PDFs and 24 pages have 0 attachments, 0 annotations, 0 widgets, 0 links, 0 optional-content groups/layers, 0 XML metadata streams, 0 special action objects, empty derivative name trees, 0 strict instruction hits, and source-backed R3 remains 0.",
            "- Use the current PDF logical-structure gate as the tagged-PDF/marked-content stop-check; 3 PDFs have 0 tagged catalogs, 0 logical marker objects, 0 decoded content markers, 0 page-76 markers, one raw-only `BDC` byte occurrence outside decoded content streams, 0 strict context hits, and source-backed R3 remains 0.",
            "- Use the current PDF navigation/article-thread gate as the PDF-wrapper read-order carrier stop-check; 3 PDFs and 24 pages have 0 TOC entries, 0 outline xrefs, 0 page labels, 0 named destinations, 0 page beads, 0 links, only 6 raw structural `/Names`/`/Dests` mentions from empty derivative name trees, 0 strict/context hits, and source-backed R3 remains 0.",
            "- Use the current PDF page-thumbnail gate as the auxiliary-raster stop-check; only `magazine.pdf` has 8 tiny `82x106` page thumbnails, page 76 has 1 low-resolution thumbnail, higher-resolution page-76 thumbnail count is 0, distinct source carriers are 0, strict instruction hits are 0, and source-backed R3 remains 0.",
            "- Use the current PDF thumbnail active-signal gate as the tiny-preview visual stop-check; page 76's `82x106` thumbnail matches the trusted page only after `rot180` with MAD `15.2525`, active state matches expected in only `3/4` boxes, O4 downgrades to grey/black from blur, hidden thumbnail signal candidates are 0, and source-backed R3 remains 0.",
            "- Use the current PDF content-stream operator gate as the raw drawing-command stop-check; 24 pages have 88 page content streams, 16 OCR form XObjects, 24 image `Do` calls, 16 form `Do` calls, 0 unknown `Do` calls, 0 visible text render-mode uses, 0 vector paint/clip operators, 0 operator instruction hits, and source-backed R3 remains 0.",
            "- Use the current PDF content transform/matrix gate as the placement-transform stop-check; 40 image/form `Do` placements collapse to 3 matrix groups, page 76 has 0 unique placement groups, active pages have 0 unique placement groups, stream order is structural, and source-backed R3 remains 0.",
            "- Use the current PDF Form XObject dictionary gate as the OCR-form wrapper stop-check; 16 `OL2` form objects collapse to 1 normalized dictionary group, page 76 has 0 unique form groups, active pages have 0 unique form groups, special form keys and visible text rows are 0, and source-backed R3 remains 0.",
            "- Use the current PDF form overlay placement gate as the OL2-offset stop-check; applying the `0.119995pt` matrix offset to the form BBox yields 16 near-full-page invisible OCR overlays, page 76 has 0 unique overlay groups, active pages have 0 unique groups, visible placements and strict hits are 0, and source-backed R3 remains 0.",
            "- Use the current PDF trailer/xref integrity gate as the file-storage stop-check; 3 PDFs collapse to 2 unique file hashes, have 3 total `startxref` and 3 EOF markers, 0 incremental-update candidates, 0 object/xref streams, 0 encrypted PDFs, 0 nonzero-generation objects, 0 hidden trailer/storage carriers, page-xref order is structural, and source-backed R3 remains 0.",
            "- Use the current PDF font/CMap resource gate as the OCR-font stop-check; 24 page font refs, 24 font objects, 16 GlyphLessFont Type0 objects, 16 identity ToUnicode CMaps, 16 CIDToGID maps, 16 font files with 1 unique hash, 0 procedural resource strict/context hits, 40 structural `font` vocabulary hits, and source-backed R3 remains 0.",
            "- Use the current PDF embedded JPEG marker gate as the raw image-wrapper stop-check; 32 JPEG records have 40 APP segments, 0 COM comments, 32 structural JFIF segments, 8 Canon EXIF provenance metadata segments confined to `magazine.pdf` thumbnails, 0 source-instruction carrier segments, 0 strict/context marker hits, and source-backed R3 remains 0.",
            "- Use the current PDF thumbnail EXIF order gate as the timestamp-order stop-check; the Canon thumbnail order is `73-75-74-78-79-76-77-80`, not article/page/xref order, reverse order, valid 75->76 leaf adjacency, or active lower-page quartet order, with page 76 at rank 6, 0 instruction carriers, 0 strict/context hits, and source-backed R3 remains 0.",
            "- Use the current PDF JPEG compression provenance gate as the DCT-structure stop-check; 32 image records collapse to 3 broad compression groups, page 76 has 0 unique compression signatures, active pages have 0 unique signatures, byte-size orders `78-79-76-75-73-77-80-74` and `79-75-76-78-73-80-74-77` match none of the bounded page/active orders, and source-backed R3 remains 0.",
            "- Use the current PDF JPEG entropy/tail gate as the entropy-coded scan and post-EOI stop-check; 32 image rows and 24 page-image rows produce 24 entropy signature groups, page 76 is unique only in the high-resolution `magazine.pdf` lineage, active-page uniqueness is lineage-wide, 5 short post-EOI tails are non-printable and confined to `magazine.pdf`, strict/context tail rows are 0/0, restart/unexpected scan rows are 0/0, exact bounded entropy-order matches are 0, selector candidates are 0, and source-backed R3 remains 0.",
            "- Use the current PDF image XObject dictionary gate as the image-object wrapper stop-check; 32 image objects collapse to 3 normalized dictionary groups, page 76 has 0 unique groups, active pages have 0 unique groups, special image-object keys are 0, strict/context hits are 0, and xref order is only structural page order.",
            "- Use the current PDF page resource/order gate as the page-wrapper stop-check; 24 page dictionaries collapse to ordinary page/resource signatures, page 76 and the active quartet have 0 unique page/resource groups, page wrappers have 0 special carrier keys and 0 strict/context hits, and page xref order is only structural page order.",
            "- Use the current PDF object/layout inspection as the native-layout stop-check; page 76 is raster-dominated with OCR/text overlays in 3/3 PDFs, has 0 native layout object evidence, 0 exact active phrase OCR hits, 0 strict unit/order term hits, and 0 higher-resolution page-76 assets.",
            "- Use the current PDF partial image placement gate as the partial-row stop-check; the 2 page-76 partial rows are duplicate lower-resolution full-page rasters inset by side margins, not local overlays: 1 repeating signature group, 0 unique page-76 partial groups, 0 local overlay rows, 0 strict hits, and source-backed R3 remains 0.",
            "- Use the current-scan crop light-table targets as the target-level stop-check; the valid natural 75->76 leaf gives O4/B4/G5/O5 source coverage `0.1223,0.0000,0.0526,0.1654`, the forced 75->76 shift gives `0.9766,0.1299,0.0540,0.0999`, and the best 79->76 benchmark gives `0.8416,0.1138,0.1328,0.3203`, with 0 all-four scenarios at >=25% or >=50% coverage.",
            "- Use the current-scan OVERDOSE glyph crop projection as the glyph-aware light-table stop-check; actual p76/p78 glyph slots give valid natural 75->76 dominant stream `S.RD`, forced 75->76 `OVRR`, and non-physical best 79->76 `DVRR`, with 0 all-four scenarios at >=25% or >=50%, 0 strict instruction hits, and only the non-physical benchmark recovering black `OVER`.",
            "- Use the current-scan highlight/crop boundary instruction probe as the boundary stop-check; 32 target-edge and crop-window-edge regions around O4/B4/G5/O5 contain 21 OCR word-hit regions but 0 strict instruction regions, 0 target-edge strict hits, 0 crop-window strict hits, and only ordinary context `bitcoin` at the crop boundary.",
            "- Use the current-scan boundary light-table anomaly probe as the boundary ink stop-check; 3 scenarios, 96 boundary rows, and 24 boundary groups find only 2 weak all-four >=10% contacts, both forced/non-physical, with 0 physically natural all-four >=10% groups and 0 all-four groups at >=25% or >=50%.",
            "- Use the current-scan boundary contact source trace as the weak-contact provenance stop-check; the 2 weak all-four boundary groups trace to 8 source regions with 4 source word-hit rows, 0 source strict instruction rows, 0 source context-term rows, p75 word hits in only 1/4 rows, and p79 word hits in 3/4 rows.",
            "- Use the current PDF OCR target provenance gate as the text-layer stop-check; 3 current PDFs contain 0 exact O4/B4/G5/O5 active phrase rows, 0 PDFs with all four exact active phrases, 0 approximate target-box exact phrase rows, 0 strict unit/order terms, and only ordinary component-token OCR false positives plus 2 OVERDOSE header hits.",
            "- Use the current PDF OCR instruction-scope gate as the current-PDF text-layer instruction stop-check; 3 PDFs, 24 pages, and 4160 OCR tokens contain action/unit/transform/target hits `10/10/0/98`, but action-plus-unit windows are 0, hard phrase hits are 0, visible painted text spans are 0, and source-backed R3 remains 0.",
            "- Use the current PDF OCR document-order gate as the invisible OCR order stop-check; 3 current PDFs contain 0 all-four populated active boxes, 2 duplicate OCR PDFs contain all four component themes somewhere but their first-occurrence order is `O5-O4-G5-B4`, active-order matches are 0, strict near-active terms are 0, and source-backed R3 remains 0.",
            "- Use the current PDF OCR OVERDOSE index-offset gate as the hidden-header index stop-check; OCR `OVERDOSE` appears only in the duplicate PDFs at index 0, 46 bounded line/corridor/slot offset landings produce only 2 duplicated target hits (`G5 + corridor 9 -> heart`), 0 strict instruction hits, 0 all-four known-unit deltas, and source-backed R3 remains 0.",
            "- Use the current PDF OCR OVERDOSE neighborhood gate as the hidden-header local-window stop-check; OCR `OVERDOSE` appears only in the duplicate PDFs at index 0, 8 fixed-radius neighborhood rows produce 0 strict unit/order rows, 4 duplicated target-context rows with only O5/`heart`, 0 all-four neighborhoods, and source-backed R3 remains 0.",
            "- Use the current PDF OCR page-header sequence gate as the page-start/order stop-check; across 3 PDFs and 24 article-page starts, page 76 begins with `OVERDOSE` only in the two duplicate OCR PDFs, page-start strict unit/order rows are 0, all-four/active-order page-start rows are 0, and source-backed R3 remains 0.",
            "- Use the current PDF visual header/footer band sequence gate as the visible-layout stop-check; across 3 PDFs, 24 rendered article pages, and 48 top/bottom bands, page 76 has 15 top-band near matches and 5 bottom-band near matches, visual header/footer candidates are 0, and source-backed R3 remains 0.",
            "- Use the current PDF repeated OVERDOSE header lane gate as the mirrored/reversed lane stop-check; 6 repeated OCR OVERDOSE page-start headers and 24 normal/mirrored/reversed lane rows produce 0 target lane rows, 0 strict lane rows, 0 all-four/active-order lane rows, and source-backed R3 remains 0.",
            "- Use the current PDF OVERDOSE header delta transfer gate as the header-offset registration stop-check; measured page-76-to-74/78 OVERDOSE header deltas across 12 direct/mirrored transfer variants and 48 transferred active boxes produce 0 text-hit boxes, 0 target-term boxes, 0 strict-term boxes, and source-backed R3 remains 0.",
            "- Use the current PDF OVERDOSE body-start vector gate as the body-reading-vector stop-check; 6 repeated OCR OVERDOSE headers produce 4 body-start rows and 8 fixed-width ray rows, with 0 target rows, 0 strict rows, 0 all-four/active-order rows, 0 candidates, and source-backed R3 remains 0.",
            "- Use the current PDF OVERDOSE body-basis reflection gate as the body-axis fold/mirror stop-check; 4 body-basis rows and 8 transform variants reflect 32 active boxes, only 10 stay in-page, only 2 touch any OCR text, 0 touch target terms or strict terms, and source-backed R3 remains 0.",
            "- Use the current PDF OVERDOSE body-line lattice gate as the body-row/column stop-check; 4 lattice pages and 16 mapped active rows preserve fixed O4-B4-G5-O5 height order in both page-76 and page-78 controls, but own-target line hits are 0, strict mapped rows are 0, candidates are 0, and source-backed R3 remains 0.",
            "- Use the current PDF OVERDOSE body-offset transfer gate as the body-row offset stop-check; page-76 offsets O4=35, B4=40, G5=42, O5=44 transfer across 4 repeated body pages and 16 offset rows, but own-target offset hits are 0, strict offset rows are 0, all-four/active-order pages are 0, candidates are 0, and source-backed R3 remains 0.",
            "- Use the current PDF OVERDOSE body-offset column gate as the row-plus-column word stop-check; 8 source points and 16 landed word rows produce nearest-word streams `eis and Street siukbeodmensertslveaarty` and `@ economy aa efficie:`, with 0 target-word hits, 0 own-target hits, 0 strict-word hits, 0 candidates, and source-backed R3 remains 0.",
            "- Use the current PDF OVERDOSE body-fraction column gate as the normalized row-plus-column stop-check; source fractions `0.795455/0.909091/0.954545/1.0` land on page-78 rows `36,41,43,45` and stream `nrot peste 4 ware`, with 0 target-word hits, 0 own-target hits, 0 strict-word hits, 0 candidates, and source-backed R3 remains 0.",
            "- Use the current PDF OCR affine alignment gate as the OCR-coordinate repair stop-check; 2 low-resolution duplicate PDF OCR layers fit the page map with 268/268 token inliers, but aligned O4/B4/G5/O5 rows contain 0 exact target components, 0 strict instruction words, and the nearest own-target component remains outside its target box.",
            "- Use the current PDF render alignment delta gate as the low-resolution raster stop-check; the two non-baseline PDFs form 1 duplicate image group, preserve active target visual states after OCR-derived alignment, and only show downsample/render residuals with 0 active target state mismatches and 0 source-backed R3 hits.",
            "- Use the current PDF render resolution invariance gate as the high-DPI render stop-check; 3 PDFs at 3 zoom levels produce 9 render rows and 6 low-vs-high comparisons, only 4 individual active outliers above shifted-control p95, 0 all-four active outlier comparisons, max active/control/OVERDOSE-slot deltas `33.652/31.542/17.371`, and source-backed R3 remains 0.",
            "- Use the current PDF active-region render/embedded identity gate as the visible-layer stop-check; 3 PDFs, 60 active/OVERDOSE/control regions, 0 active render-vs-embedded mismatches, 0 all-four active mismatch PDFs, 0 OVERDOSE-slot mismatches, max active/slot render-vs-embedded MAD `7.199/3.122`, and source-backed R3 remains 0.",
            "- Use the current-scan JPEG block-grid gate as the scan-compression artifact stop-check; page 76 active boxes, shifted controls, and projected OVERDOSE slots show no unique 8x8 phase or block-boundary-energy selector, active outliers above shifted-control p95 are 0/4, max active/control/slot ratios are `1.551/4.014/1.296`, and source-backed R3 remains 0.",
            "- Use the current-scan halftone/screen-texture gate as the print-texture stop-check; active boxes share angle bin `90.0-112.5`, but 12 shifted controls and 7 OVERDOSE slots also match that bin, active dominant-share outliers are 0/4, highpass outliers are only 1/4, max active/control dominant share is `0.241/0.373`, and source-backed R3 remains 0.",
            "- Use the current-scan RGB registration gate as the chromatic-displacement stop-check; page 76 active boxes, shifted controls, and projected OVERDOSE slots all share zero-shift `RG+0,+0|BG+0,+0`, active nonzero/outlier rows are 0/4, max active/control/slot shift is `0.0/0.0/0.0`, and source-backed R3 remains 0.",
            "- Use the current-scan luminance bitplane gate as the low-bit/threshold-plane stop-check; O4/B4/G5/O5 all stand out from shifted controls in low-bit and visible-threshold metrics, but active low-bit signatures are mixed, shared active carrier / hidden bitplane candidate are 0/0, max active/control/slot low-bit abs-z is `4.62/1.81/1.50`, and source-backed R3 remains 0.",
            "- Use the current-scan threshold morphology gate as the thresholded-ink component-shape stop-check; O4/B4/G5/O5 all stand out from shifted controls, but active morphology signatures are mixed, shared active carrier / hidden morphology candidate are 0/0, max active/control/slot morphology abs-z is `78.91/2.48/30.19`, and source-backed R3 remains 0.",
            "- Use the current-scan highlight edge-halo gate as the outside-ring color/direction stop-check; O4/B4/O5 have outer-halo outliers but G5 does not, active halo and ink edge-bias signatures are mixed, shared active halo carrier / hidden halo candidate are 0/0, max active/control/slot halo abs-z is `19.49/3.72/11.78`, and source-backed R3 remains 0.",
            "- Use the current-scan slot-boundary residual gate as the C9/OVERDOSE ruler stop-check; active starts/centers/ends do not share a repeatable slot-boundary or slot-center residual, all-four any/left-boundary/center/right-boundary close<=16px are `0/0/0/0`, active nearest-center streams are `DOER/OVED/SVRO`, mean active/control residual is `31.90/26.00px`, and source-backed R3 remains 0.",
            "- Use the current-scan OVERDOSE glyph stroke-centroid gate as the actual-header-ink stop-check; p76/p78 visible orange OVERDOSE headers each produce 8 stroke components, active center stream remains `OVED`, all-four active any-anchor/center close projections are 0/0, controls produce up to 10 close<=16px rows, active-better-than-control-p05 projections are 0, and source-backed R3 remains 0.",
            "- Use the current-scan active-envelope transform gate as the active-quartet fold/mirror stop-check; hmirror, vmirror, rot180, and normalized diagonal folds around the active envelope have 0 all-four active re-hits at 32px or 64px, the best transform only gives 1 active-other hit within 64px, and source-backed R3 remains 0.",
            "- Use the current-scan active-envelope transform text trace as the projected-text stop-check for active-quartet fold/mirror mechanics; 5 transforms and 20 projected rows hit page-76 OCR in 18 rows with 61 words, but strict instruction rows are 0, all-four strict modes are 0, the lone context/target hits are ordinary article vocabulary, and source-backed R3 remains 0.",
            "- Use the current-scan active-envelope transform format trace as the full-box-overlap stop-check for active-quartet fold/mirror mechanics; the anti-diagonal mode partially overlaps all four active targets with overlap-vs-projected only `0.129087-0.324257`, has 0 strict instruction rows, 0 satisfied reopen triggers, and source-backed R3 remains 0.",
            "- Use the current-scan active-envelope anti-diagonal overlap control as the selectivity stop-check for the active-envelope near miss; among 11 page-76 active/highlight boxes and 330 quartets, 42 quartets have all-four overlap and 17 have distinct all-four streams, the active quartet ranks 1/1 with stream `O4-O5-G5-B4`, but min overlap is only `0.129086526`, paired text/format strict rows are 0/0, and source-backed R3 remains 0.",
            "- Use the current-scan background seam residual gate as the background-only crop/gutter stop-check; 4 pages are checked, page 76 has 0 unique vertical background seam lines and 14 unique horizontal background lines, active close-to-unique x/y hits at <=16px are 0/1, all-four active x/y hits are 0/0, controls also hit 0/2, OVERDOSE slots hit 0/0, and source-backed R3 remains 0.",
            "- Use the current-scan paper texture duplex gate as the background/fiber registration stop-check; 3 physical leaf pairs, 6 controls, and 36 fixed-transform rows show physical hmirror best in only 1/3 leaf pairs, above control p95 in 0/3, max physical-hmirror/control/control-p95 correlations `0.3090/0.3495/0.3220`, and source-backed R3 remains 0.",
            "- Use the current-scan paper texture shift gate as the scan-slip guardrail for background/fiber registration; 3 physical leaf pairs, 6 controls, and 729 hmirror-shift rows show physical best above control-best p95 in only 1/3 leaf pairs, only 1/3 physical best shifts are within 16px, zero-shift physical rows above control-best p95 are 0/3, max physical-best/control-best/control-best-p95 correlations are `0.4261/0.3693/0.3557`, and source-backed R3 remains 0.",
            "- Use the current PDF active-box coordinate-grid gate as the PDF point-coordinate stop-check; the only all-four active center/edge landing appears at loose 0.12pt tolerance on a 0.25pt grid, controls match the same grid more strongly, grid alignment candidate is 0, and source-backed R3 remains 0.",
            "- Use the current PDF image-rect margin phase gate as the embedded-image trim/side-margin stop-check; 3 PDFs x O4/B4/G5/O5 plus 7 highlight controls and 8 OVERDOSE slots show 0 all-four active hits on halves/thirds/quarters/eighths/sixteenths, 0 all-four active hits on 18pt side-margin units, margin phase candidates are 0, and source-backed R3 remains 0.",
            "- Use the local PDF filesystem provenance gate as the source-origin stop-check for current PDF witnesses; 3 PDFs collapse to 2 unique SHA-256 hashes, `keyser bitcoin .pdf` and the external Google Drive download are byte-identical PDF24 OCR derivatives, `magazine.pdf` is distinct but has ChatGPT download provenance, distinct higher-resolution scan/source candidates are 0, and source-backed R3 remains 0.",
            "- Use the local page raster lineage gate as the loose-image source stop-check; 24 PDF embedded reference rows and 24 local page-raster candidates all map back as near-duplicates/derivative-like rows, distinct/promoted source candidates are 0/0, higher-resolution/sharper candidates are 0/0, and source-backed R3 remains 0.",
            "- Use the current PDF color-management/ExtGState gate as the PDF graphics-state stop-check; 3 PDFs and 24 page rows have 0 OutputIntents, 0 page-76-unique resource signatures, 0 ExtGState objects, 0 ColorSpace objects, 0 image Decode arrays, 0 special image color-key rows, and source-backed R3 remains 0.",
            "- Use the current PDF embedded channel/mask gate as the channel-separation stop-check; all 3 page-76 embedded images are ordinary 8-bit DeviceRGB DCT images, with 0 alpha/mask/non-RGB/ICC/CMYK/separation candidates, 0 active channel-state mismatches, and 0 source-backed R3 hits.",
            "- Use the current PDF text overlay render-mode gate as the OCR visibility stop-check; all 755 page-76 texttrace spans are invisible/type-3 OCR, visible painted text spans are 0, active aligned overlay hits contain 0 exact components and 0 strict instruction terms, and source-backed R3 remains 0.",
            "- Use the source-packet fold-world OVERDOSE order control as the 3D fold-depth/order stop-check; 9 page/fold/depth/distance orders produce streams `DEVO,ODEV,OEVD,OVED,VEDO`, but the 3 fold-only streams have 0 instruction hits, 0 layout hits, 0 explicit source depth/fold-order cue hits, and source-backed R3 remains 0.",
            "- Use the source-packet bold phrase length slot control as the word-count/slot-count stop-check; active bold/highlight phrases match touched OVERDOSE slot counts in 4/4 rows, but non-active grey controls match in 3/13 rows, including the p75 `OVER` control, while all-active count-to-center-slot fits remain 0 and source count/length cue hits remain 0.",
            "- Use the source-packet highlight count slot permutation control as the character/highlight-count stop-check; 10 metrics and 2 index modes produce 20 canonical streams with 0 layout, 0 instruction, and 0 fold-world hits, while the 5 fold-world permutation hits all require one-based `docmHighlightCount` plus arbitrary active target order, with source count cues 0 and source-backed R3 0.",
            "- Use the source-packet active span bridge control as the adjacent-span/held-together stop-check; B4+G5 gives exact `OVER`, but non-active single spans already include exact `OVER` and `OVERDOSE`, non-active page-adjacent controls have 6/8 layout hits, source bridge cues are 0, and source-backed R3 remains 0.",
            "- Use the source-packet bold phrase edge slot control as the acrostic/initial/final stop-check; active phrase edges have 0 center-slot hits and 0 touched-span hits, 9 fold-order edge streams have 0 instruction/layout hits and never contain their center-slot stream, and source initial/final/acrostic cue hits remain 0.",
            "- The future-source scoring rubric defines R1-R5/C2-C3-C4-C8 acceptance thresholds; it is a validation rubric only and does not unlock a current-scan selector.",
            "- The future-source rubric dry-run confirms the current stack has 0 extraction-ready paths and 8 R3 failures; this confirms the rubric does not reopen already-local evidence.",
            "- Use canonical plain text, DOCM text, and the Markdown transcript as exact page-76 target text authority; raw plain text is context-only because it omitted `Volcano Bonds`, and the annotated transcript is a format witness because inline notes interrupt exact prose.",
            "- Use DOCM runs, high-res visual highlight consistency, and the page-76 crop pack/manual boxes as format authority; Markdown bold is transcript markup and the annotated transcript is a witness layer, not font-state authority or R3 selector permission.",
            "- Do not promote `BOLD.docm` as a source or selector; it is macro-enabled, references a missing external `otrobip.txt` word list, contains 0/4 locked active targets, and remains generated-artifact sanity evidence only.",
            "- Do not promote the reconstructed BOLD highlighted-word stream as a source or selector; it has 43 yellow/Typeka/bold highlighted words, contains 0/4 locked active targets, only partially overlaps `IMF loan` via `loan`, and has no source-backed unit/order instruction.",
            "- Do not promote Markdown-vs-DOCM mismatch streams as a page-76 selector; the aligned corridor Markdown-only stream has 0 instruction hits and the DOCM-only active targets are only `$1 billion` and `Volcano Bonds`.",
            "- Use the completed O4/B4/G5/O5 crop sheet as visual source-comparison authority only; it improves packet completeness from 3/4 to 4/4 active target crops but does not add R3 unit/order evidence.",
            "- Use the scan-only held-to-light adjudication as the fixed natural page-75->page-76 light-table stop-check; it used only `magazine.pdf` embedded scans, fixed opacities `0.35/0.50/0.65`, a blind overlay, and all 256 nearby controls, with active source-only >=10% `0/4`, active above control p95 `0/4`, source-backed R3 `0`, and no remaining adversarial-review blockers.",
            "- Use the scan-only held-to-light tolerance sweep as the bounded registration stop-check; it used only `magazine.pdf` embedded scans, the physically valid page 75 back -> page 76 front relation, dx/dy +/-80 px in 20 px steps, rotations -1/0/+1 degrees, fixed opacity display panels, and all 256 nearby controls, with all-four signal modes `0`, all-four >=10% modes `0`, all-four above-control-p95 modes `0`, best active >=10% `0/4`, best active above control p95 `0/4`, source-backed R3 `0`, selectors `0`, and no adversarial-review blockers.",
            "- Use the open-heart O-K-K-O capsule rule audit as the current capsule-bridge stop-check; it found the lower page-76 active bridge is a bounded real outlier (`13` words versus `0` non-active OBBO bridge words and max `2` adjacent K-K control bridge words) and re-hits the `should sell` convergence, but extraction-action/unit hits are `0/0`, source-backed R3 is `0`, reopen triggers are `0/9`, selector unlocked is `False`, and adversarial review kept it as partial selector/source-validation evidence only.",
            "- Treat the source-acquisition packet, crop-authority sync, Y/K-frame benchmark sync, native benchmark bridge, alignment tolerance, geometric fingerprint, frame-normalized geometry, color-profile manifest, repaired p78 frame residual, repaired-frame expansion leakage, handoff integrity matrix, false-positive guardrail, R3 bridge audit, reopen trigger matrix, orientation disambiguator, orientation control quartets, source-review gate, OVERDOSE transform control, fold/format intersection control, terminal coverage matrix, active target authority crosscheck, active format stream control, active index-slot control, center rotation word control, color split span control, dominant overlap slot control, span edge slot control, overlap width profile control, span neighbor slot control, span complement slot control, local asset orientation gate, PDF render quality gate, current-scan held-to-light simulator, current-scan held-to-light opacity gate, current-scan valid-leaf bleed-through control grid, current-scan valid-leaf local-warp gate, current-scan valid-leaf local-warp source trace, current-scan valid-leaf edge-contact control, current-scan valid-leaf edge source trace, current-scan valid-leaf interior source trace, current-scan valid-leaf glyph-slot source trace, current-scan valid-leaf channel source trace, current-scan valid-leaf word-collision trace, current-scan valid-leaf line-band trace, current PDF page-box pair geometry gate, current PDF leaf-image identity gate, current PDF render leaf simulation gate, current PDF low-res render source trace, current PDF OCR reverse-leaf source trace, current-scan OVERDOSE slot-shape phase control, current-scan OVERDOSE x-slot phase control, current PDF container metadata gate, current PDF logical structure gate, current PDF navigation/article-thread gate, current PDF page-thumbnail gate, current PDF content-stream operator gate, current PDF content transform/matrix gate, current PDF Form XObject dictionary gate, current PDF form overlay placement gate, current PDF trailer/xref integrity gate, current PDF font/CMap resource gate, current PDF embedded JPEG marker gate, current PDF thumbnail EXIF order gate, current PDF JPEG compression provenance gate, current PDF image XObject dictionary gate, current PDF page resource/order gate, current PDF object/layout inspection, current PDF partial image placement gate, current PDF active-region render/embedded identity gate, current-scan crop light-table targets, current-scan OVERDOSE glyph crop projection, current-scan highlight/crop boundary instruction probe, current-scan boundary light-table anomaly probe, current-scan boundary contact source trace, current PDF OCR target provenance gate, current PDF OCR affine alignment gate, current PDF render alignment delta gate, current PDF render resolution invariance gate, current-scan JPEG block-grid gate, current-scan halftone screen gate, current-scan RGB registration gate, current-scan luminance bitplane gate, current-scan threshold morphology gate, current-scan background seam residual gate, current-scan paper texture duplex/shift gates, current PDF color-management/ExtGState gate, current PDF embedded channel/mask gate, current PDF text overlay render-mode gate, fold-world OVERDOSE order control, bold phrase length slot control, highlight-count slot permutation control, active span bridge control, and bold phrase edge slot control as the current handoff stack: the historical packet remains the jobs/gates checklist, the completed 4/4 crop sheet is the active page-76 visual comparison authority, and the newer packet reports constrain scan/source-image comparison only.",
            "- Use the page-76 active crop orientation guardrail before future source comparison: O4/B4/G5/O5 boxes are in readable/upright coordinates; PDF page renders may already apply page rotation, while native `source_images` and embedded PDF page images require the documented 180-degree transform.",
            "- Use the page-76 active order orientation trap guardrail before accepting source matches: `OBBO` and `YKKY` are palindromes and cannot validate orientation, so require line order `22 25 27 32` and corridor order `4 7 9 14` in the readable/upright frame.",
            "- Do not use 3D map OCR text inside the active target boxes as extraction text; exact O4/B4/G5/O5 box matches are `0/4`, with all four corrupted or misread and G5 effectively blank in the box labels.",
            "- Any new source/clue must pass the source-reopen gate (`R1-R5`) before selector/key checks resume.",
            "- Any exact geometry should compare like orientations: the 3D/crop-pack layer and PDF page renders are readable/upright after renderer rotation, while `source_images` and embedded PDF page images need a 180-degree rotation first.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("deadBranchCount:", dead_count)
    print("highestValueNextMove:", result["decision"]["highestValueNextMove"])


if __name__ == "__main__":
    main()

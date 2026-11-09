# Typeka Authority Bridge Sheet

Scope: visual bridge from page-76 priority crops to DOCM Typeka/bold/highlight states. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.

- Sheet: `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg`
- Source audit: `analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.json`

## Panels

### L25_should_sell
- Crop: `analysis_outputs/source_audit/page76_priority_crop_pack/L25_should_sell.jpg`
- Summary: $1 billion is DOCM-bold + black-highlighted; Markdown missed it. should sell is regular.
- `$1 billion`: font `Typeka`, bold `1.0`, mix `0.0`, highlight `{'black': 10}`, markdown bold `0.0`.
- `should sell`: font `Typeka`, bold `0.0`, mix `0.0`, highlight `{'none': 11}`, markdown bold `0.0`.

### L27_G5_pair
- Crop: `analysis_outputs/source_audit/page76_priority_crop_pack/L27_G5_pair.jpg`
- Summary: Volcano Bonds is DOCM-bold + black-highlighted; Markdown missed it.
- `Volcano Bonds`: font `Typeka`, bold `1.0`, mix `0.0`, highlight `{'black': 13}`, markdown bold `0.0`.
- `IMF loan`: font `Typeka`, bold `0.889`, mix `0.0`, highlight `{'none': 8}`, markdown bold `0.7`.

### L26_L29_source_band
- Crop: `analysis_outputs/source_audit/page76_priority_crop_pack/L26_L29_source_band.jpg`
- Summary: Future earnings is regular; Mike/Novogratz contains Typeka Mix nearby context.
- `future bitcoin earnings`: font `Typeka`, bold `0.0`, mix `0.0`, highlight `{'none': 23}`, markdown bold `0.0`.
- `I tagged Mike`: font `Typeka`, bold `0.0`, mix `0.308`, highlight `{'none': 13}`, markdown bold `0.154`.
- `Novogratz`: font `Typeka Mix`, bold `0.0`, mix `1.0`, highlight `{'none': 9}`, markdown bold `0.333`.

### L32_O5_primary
- Crop: `analysis_outputs/source_audit/page76_priority_crop_pack/L32_O5_primary.jpg`
- Summary: O5 is DOCM-bold + yellow-highlighted and also Markdown-bold.
- `shitcoiner at heart`: font `Typeka`, bold `1.0`, mix `0.0`, highlight `{'yellow': 19}`, markdown bold `1.0`.

### L25_L32_frame_context
- Crop: `analysis_outputs/source_audit/page76_priority_crop_pack/L25_L32_frame_context.jpg`
- Summary: The compact p78-frame benchmark is R-K-Y; Typeka Mix lands nearby, not on the G5/O5 pair.
- `should sell`: font `Typeka`, bold `0.0`, mix `0.0`, highlight `{'none': 11}`, markdown bold `0.0`.
- `Volcano Bonds`: font `Typeka`, bold `1.0`, mix `0.0`, highlight `{'black': 13}`, markdown bold `0.0`.
- `shitcoiner at heart`: font `Typeka`, bold `1.0`, mix `0.0`, highlight `{'yellow': 19}`, markdown bold `1.0`.
- `I don't really trust that guy`: font `Typeka Mix`, bold `0.0`, mix `1.0`, highlight `{'none': 29}`, markdown bold `0.31`.

## Decision

- Use this sheet next to the 3D viewer and page-76 crop pack when checking the lower corridor.
- Markdown bold remains annotation-only; DOCM states are the formatting witness.
- This is a guardrail artifact, not extraction evidence.
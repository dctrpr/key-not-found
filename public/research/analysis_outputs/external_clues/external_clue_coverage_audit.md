# External Clue Coverage Audit

Scope: map each known external clue to tested/active branches. This is not a key-generation pass.

## Coverage

### Announcement: private Bitcoin key encoded in the Bitcoin Magazine piece

- Evidence: `analysis_outputs/external_clues/original_clue_provenance.md` exists `True`
- Status: `accounted_for`
- Tested by: `source lock, exact transcript, broad key-format tests, dead-branch blacklist`
- Finding: Confirms source and target type, but gives no selector beyond the later mirror-writing clue.

### Schott paper title: mirror writing

- Evidence: `analysis_outputs/external_clues/schott_instruction_distillation.md` exists `True`
- Status: `accounted_for_but_incomplete`
- Tested by: `hold-to-light overlays; literal string reversal; left/right and bimanual selectors; 76/79 registration; page-76 self-mirror`
- Finding: Supports visual/physical mirror and left-right operations. Current tests find regions, not extraction units.

### Schott concepts: left hand, right hemisphere, bimanual movement, corpus callosum

- Evidence: `analysis_outputs/external_clues/schott_instruction_distillation.md` exists `True`
- Status: `accounted_for_but_incomplete`
- Tested by: `78/79 two-hand selectors; registered 76/79 line anchor; source-page binary selectors`
- Finding: The concept fits crossing/registration, especially p79 -> p76, but does not name source layer or extraction unit.

### Announcement media sequence: Bukele, El Salvador, IMF, volcano imagery

- Evidence: `analysis_outputs/external_clues/source_clue_inventory.md` exists `True`
- Status: `strongly_accounted_for`
- Tested by: `page-76 corridor; page-76 B5/O5 drilldown; dose-number and p80 symptom audits`
- Finding: Repeatedly reinforces page 76 and the Bukele/IMF/volcano/Volcano Bonds corridor.

### Announcement opener spread: OVERDOSE, five capsules, cash

- Evidence: `analysis_outputs/source_audit/announcement_opening_spread/announcement_opening_spread_audit.md` exists `True`
- Status: `accounted_for_but_incomplete`
- Tested by: `opener pill/cash inventory; capsule recurrence; ordered capsule projection; spread model reconciliation`
- Finding: Five-capsule/order provenance is real but does not currently map onto page-76 text under the high-res digital scan.

### Canva note: pills don't line up / diff pic?

- Evidence: `analysis_outputs/external_clues/canva_source_inspection.md` exists `True`
- Status: `source_gap_active`
- Tested by: `source registration gap; best scan source lock; capsule projection and recurrence`
- Finding: This is not a selector. It points to a possible source/version mismatch that only a different source image, original layout asset, or physical scan can settle.

### Canva note: OCR did not pick up the #0 in browser/PDF viewer

- Evidence: `analysis_outputs/external_clues/canva_source_inspection.md` exists `True`
- Status: `source_gap_active`
- Tested by: `OCR is diagnostic only; high-res/manual text is source truth`
- Finding: Treat as OCR/source-fidelity warning. It does not identify which zero or which page without the referenced browser view or higher-res Canva/original visual.

### Canva note: XX / barbed wire / SHIT / FUCK ALL SHITCOINS line up after rotation/mirroring

- Evidence: `analysis_outputs/external_clues/canva_source_inspection.md` exists `True`
- Status: `accounted_for_as_orientation`
- Tested by: `registered Canva anchor alignment; p79 pill / p76 X-dollar-wire system; lower page-76 mark pointers`
- Finding: Supports orientation/registration. Existing high-res tests do not make it a precise ordering or letter selector.

### Canva design thumbnail / board

- Evidence: `analysis_outputs/external_clues/canva_thumbnail_export_audit.md` exists `True`
- Status: `closed_as_geometry_truth`
- Tested by: `thumbnail export audit; dead-branch blacklist`
- Finding: Current connector only exposes a low-resolution investigator thumbnail, not original geometry truth.

## Assessment

- The local external-clue set is now mostly covered. It repeatedly points to page 76 and the Bukele/IMF/volcano corridor, but does not supply the missing word/letter extraction unit.
- The only active clue items are source-fidelity gaps: `pills don't line up / diff pic?` and `OCR DIDNT PICK UP THE #0`.
- Those should not be turned into more key candidates. They require a different source image, the exact browser/PDF view, higher-resolution Canva/original layout material, or physical magazine scan evidence.

## Next Best Move

- If a new visual source is supplied, first run a zero/#0 and pill-registration inventory against the high-res scan. Without a new source, prioritize physical/original-source acquisition over further local transformations.

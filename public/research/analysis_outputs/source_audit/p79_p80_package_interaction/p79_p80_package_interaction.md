# P79/P80 Package Interaction Drilldown

Scope: inspect the two raw hflip interactions between page 80 medicine/package labels and page 79 end text. No key candidates are generated.

- Sheet: `analysis_outputs/source_audit/p79_p80_package_interaction/p79_p80_package_interaction_sheet.jpg`

## P80 Labels Reflected Onto P79

### p80 O1 -> p79 O4

- Source label: `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS`
- Source y-span estimate: `[0.8234, 0.9506]` -> `['UPSET STOMACH', 'SHITCOINS']`
- Target sentence span estimate: `[0.1817, 0.4145]` -> `ill live their `
- Center distance: `321.16` px

### p80 O2 -> p79 O4

- Source label: `6 FL OZ (473 mL)`
- Source y-span estimate: `[0.5687, 0.875]` -> `['6 FL OZ (473 mL)']`
- Target sentence span estimate: `[0.5053, 0.7062]` -> `experience in`
- Center distance: `153.17` px

## P79 Sentence Reflected Onto P80

### p79 O4 -> p80 O1

- Source sentence span estimate: `[0.1817, 0.4145]` -> `ill live their `
- Target label: `5 SYMPTOM RELIEF / NAUSEA / HEARTBURN / INDIGESTION / UPSET STOMACH / SHITCOINS`
- Target y-span estimate: `[0.8234, 0.9506]` -> `['UPSET STOMACH', 'SHITCOINS']`
- Center distance: `321.16` px

### p79 O4 -> p80 O2

- Source sentence span estimate: `[0.5053, 0.7062]` -> `experience in`
- Target label: `6 FL OZ (473 mL)`
- Target y-span estimate: `[0.5687, 0.875]` -> `['6 FL OZ (473 mL)']`
- Center distance: `153.17` px

## Assessment

- The package layer is real enough to preserve as theme/provenance: both p80 labels hit the same p79 orange sentence under raw hflip.
- It does not give a clean extraction unit. The p79 spans are broad fragments from the middle of one sentence, and the p80 hits are lower strips of multi-line package labels.
- Treat `5 SYMPTOM RELIEF` / `6 FL OZ` as OVERDOSE/dosage evidence, not as direct page-76 key material.

## Next Best Move

- Look for an explicit rule that tells how the p73 five-capsule order or p80 dosage/package labels should be applied to page 76. Do not promote the p79/p80 overlap by itself.

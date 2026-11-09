# Active Text Authority Drift

Scope: compare the active page-76 target phrases across corrected plain text, DOCM text/font runs, Markdown/annotated transcripts, and the 3D OCR labels. No key derivation, hashing, seed phrase, WIF, or address checks were run.

## Target Summary

| id | phrase | strong text witnesses | DOCM state | Markdown state | 3D OCR status |
|---|---|---|---|---|---|
| `O4_buying_the_dip` | `buying the dip.` | `root:yes, canonical:yes, docm:yes` | `bold=1.0 fonts={'Typeka': 13} hi={'yellow': 13}` | `bold=1.0 hi={'none': 13}` | `missing` |
| `B4_one_billion` | `$1 billion` | `root:yes, canonical:yes, docm:yes` | `bold=1.0 fonts={'Typeka': 9} hi={'black': 9}` | `bold=0.0 hi={'none': 9}` | `missing` |
| `G5_volcano_bonds` | `Volcano Bonds` | `root:yes, canonical:yes, docm:yes` | `bold=1.0 fonts={'Typeka': 12} hi={'black': 12}` | `bold=0.0 hi={'none': 12}` | `missing` |
| `O5_shitcoiner_heart` | `shitcoiner at heart.` | `root:yes, canonical:yes, docm:yes` | `bold=1.0 fonts={'Typeka': 18} hi={'yellow': 18}` | `bold=1.0 hi={'none': 18}` | `missing` |
| `context_imf_loan` | `IMF loan` | `root:yes, canonical:yes, docm:yes` | `bold=1.0 fonts={'Typeka': 7} hi={'none': 7}` | `missing` | `found` |
| `context_mike_novogratz` | `Mike Novogratz` | `root:yes, canonical:yes, docm:yes` | `bold=0.0 fonts={'Typeka Mix': 13} hi={'none': 13}` | `missing` | `found` |
| `context_trust_that_guy` | `trust that guy.` | `root:yes, canonical:yes, docm:yes` | `bold=0.0 fonts={'Typeka Mix': 13} hi={'none': 13}` | `bold=0.231 hi={'none': 13}` | `found` |

## Drift / Guardrails

- B4_one_billion: Markdown bold misses DOCM-bold/black-highlighted target
- B4_one_billion: absent from 3D OCR labels; use bridge/crops
- G5_volcano_bonds: Markdown bold misses DOCM-bold/black-highlighted target
- G5_volcano_bonds: absent from 3D OCR labels; use bridge/crops
- O5_shitcoiner_heart: absent from 3D OCR labels; use bridge/crops

## Assessment

- The corrected/root text, canonical plain body, and DOCM text agree on the active page-76 corridor after the latest plain-text corrections.
- The raw/user annotation layers remain useful notes, but they contain known drift such as omitted or typo-prone wording and partial-bold notation.
- Markdown bold is not source typography: it misses the DOCM-bold black-highlighted `$1 billion` and `Volcano Bonds` targets.
- DOCM states confirm the active visual sequence as yellow/orange target, black target, black target, yellow/orange target; Typeka Mix stays nearby context rather than inside the O4/B4/G5/O5 targets.
- 3D OCR labels remain unsafe for exact active target wording, especially `$1 billion`, `Volcano Bonds`, and `shitcoiner at heart`.

## Decision

- Use corrected/DOCM/plain text for wording, high-res crop/bridge sheets for geometry, and DOCM Typeka states for typography labels. Do not use Markdown bold or 3D OCR labels as extraction authority.

## Next Move

- Only reopen extraction if a source/clue names which of the locked active units to read, or if a new physical/original-layout source changes one of the priority crop/wording baselines.

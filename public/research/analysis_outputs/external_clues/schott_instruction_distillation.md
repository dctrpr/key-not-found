# Schott Instruction Distillation

Scope: distill the linked Schott mirror-writing paper into operational concepts for the puzzle. This is not a key-generation pass.

- Created: `2026-05-20T04:03:57`
- Source: `https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/`
- Parsed title: `Mirror writing: neurological reflections on an unusual phenomenon - PMC`

## Concept Counts

- `literal_mirror`: `459`
- `neurological`: `79`
- `handedness_left`: `43`
- `leonardo`: `27`
- `bimanual`: `18`
- `corpus_callosum`: `16`
- `right_hemisphere`: `10`
- `readability_with_mirror`: `1`

## Operation Map

- `literal_mirror`: Prefer physical/visual mirror actions and right-to-left reading before cryptographic transformations. Current status: Direct prose reversal and raw hflip have been tested; they identify regions, not final letters.
- `handedness_left / right_hemisphere`: A left/right page or left/right side selector remains more plausible than whole-article hashing. Current status: 78/79 as two hands is suggestive but first/last and binary selectors failed.
- `bimanual / corpus_callosum`: The strongest live geometry should be treated as a crossing/communication rule between pages, not one page alone. Current status: The p79-yellow -> p76-black row anchor fits this concept but lacks extraction unit/order.
- `Leonardo / reversed writing`: The clue supports reversing the reading direction, but only after the correct source layer and target region are known. Current status: Reversing current reflected text streams produced no instruction, so the missing piece is upstream.

## Short Context Checks

### mirror
- `Mirror writing: neurological reflections on an unusual phen`
- `in PubMed View in NLM Catalog Add to search Mirror writing: neurological reflections on an unusual ...`
- `ce PMCID: PMC2117809 PMID: 16963501 Abstract Mirror writing is an unusual script, in which the writing ...`
- `as with certain diffuse cerebral disorders. Mirror writing is nearly always undertaken with the left ha`

### leftRight
- `writing is nearly always undertaken with the left hand, and left‐handers, and those whose languages`
- `ing processes, the implications of using the left hand when writing are considered first. Motor pat`
- `an epileptic girl who used to write with the left hand, in reverse order, and with ...`
- `rm in action, wrote all his letters with the left hand, with order and form similarly ...`

### bimanual
- `hat may be important, the surrogate model of bimanual mirror movements and the contribution of the`
- `weeks after the stroke, he had impairment of bimanual tasks that required non‐mirror movements and`
- `bilities suggested by other motor phenomena. Bimanual mirror movements Perhaps the most relevant s`
- `elevant surrogate model is the phenomenon of bimanual associated movements of the upper limbs, 62`

### leonardo
- `y play an important part is entertained, and Leonardo da Vinci's unique, habitual mirror writing p`
- `1568, in describing the reversed letters of Leonardo da Vinci's script, Vasari 2 reported “whoeve`
- `rred right hand habitually, probably only by Leonardo da Vinci learnt for occupational purposes by`
- `, and perhaps the only recognised example is Leonardo da Vinci, whose mirror writing is discussed`

## Assessment

- The paper supports mirror/left-right/bimanual concepts, not a named cryptographic transform.
- It reinforces the existing page-76 and 76/79 orientation model.
- It still does not specify source layer, ordering, or extraction unit.
- Future tests should require a fully stated human rule before generating candidates.
- The clue narrows the style of solution: human visual/physical selection first, cryptography only after a clean selector exists.
- Best next move remains source fidelity: higher-resolution Canva/original layout/physical magazine evidence, or one explicit rule tied to the 76/79 row anchor.

# Page-76 Weak Landing Support Audit

Scope: re-check the non-empty line-offset landings that previously scored `0`, using only already-logged secondary layers: reflected-highlight graph and p80 package number/term evidence. No key candidates or hashing were generated.

- Created: `2026-05-20T06:07:40`

## Results

| landing | line | secondary score | secondary layers | line text |
|---|---:|---:|---|---|
| `O2+2` | 3 | 5 | strong reflected carrier, medium reflected carrier | but George Clinton and James Brown clones. It's Martin Luther |
| `B2+2` | 9 | 3 | p80 number/word hit, p80 package term/family hit | have dulled shitcoiners' and nocoiners' minds. |
| `B3+3` | 19 | 0 | - | Don't believe me? |

## Details

### O2+2 -> line 3

- Text: `but George Clinton and James Brown clones. It's Martin Luther`
- Reflected graph: `79_76_1` strong -> `orange_7` terms=`brown,clinton,clones,george,james,luther,martin` reflectedCoverage=`0.9566`
- Reflected graph: `79_76_1` medium -> `grey_black_4` terms=`brown,clinton,clones,george,james,luther,martin` reflectedCoverage=`0.571`

### B2+2 -> line 9

- Text: `have dulled shitcoiners' and nocoiners' minds.`
- P80 number: `100_percent_pow` `100` hits `{'oneBasedWord': 'dulled'}`
- P80 term: `symptoms` `NAUSEA HEARTBURN INDIGESTION UPSET STOMACH SHITCOINS` exact=`` family=`shitcoiners~shitcoins`

### B3+3 -> line 19

- Text: `Don't believe me?`
- No secondary support found.

## Assessment

- O2+2 is not actually unsupported in the full evidence stack: the `George Clinton / Martin Luther` line is the same p79 reflected carrier that strongly overlaps O1 and medium-overlaps B3 in the reflected-highlight graph.
- B2+2 gains weak p80 support: `100% Proof of Work Liquid` maps through the existing p80 number check to page-76 word 100, `dulled`, and the p80 symptom `SHITCOINS` shares the same family as `shitcoiners` in the landing line.
- This does not make #2 a final selector. It means the earlier score-0 label was too strict because it ignored reflected-carrier and package-number evidence.
- The line-offset model now looks more like a cross-reference/locator map than a direct highlight-to-highlight rule. It still does not specify the word or letter to extract.

Next move: Run one local unit audit on the secondary-supported landing set: for each supported landing, use only the externally named term/carrier word and test whether those named terms form a readable instruction before any key derivation.

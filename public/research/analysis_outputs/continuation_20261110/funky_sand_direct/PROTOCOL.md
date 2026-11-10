# Funky Upheaval — three direct George Sand readings

This is one conditional-source reading procedure. The source, code and machine protocol are published before generating target outputs. [PROTOCOL.json](PROTOCOL.json) fixes the exact pins and definitions; [SOURCE.md](../../../sources/funky-upheaval/SOURCE.md) explains the reviewed physical lines and encoding freeze.

## Why this source and operation

A bounded retained-record audit found visual/style-control work, but no owning text-decoding record, for Bitcoin and the Funky Upheaval. This is an undocumented coverage gap, not proof that nobody has tried it. Two AI visual passes checked all 115 physical content rows; the second was unblinded to the draft and proposed no lexical, wrap, order or role corrections.

Keiser's [December 26, 2022 post](https://x.com/maxkeiser/status/1607378060172460032) links the [George Sand examples](https://ciphermysteries.com/2010/05/16/george-sands-cryptography), which demonstrate first words and odd whole lines. The blog records a 2010 correction to whole odd lines and a December 28, 2022 final-line correction. Current lineation is therefore not proof of the exact layout Keiser saw. Its examples are authority for a linked mechanism, not authenticated historical correspondence or an exact magazine selector.

**This column's issue/date remain unverified.** Its eligibility under the broad December plural-key statement is conditional. The March 2023 mirror clue and photographed Issue 24 20 BTC announcement are not assigned to this column. No prize or funding address is authenticated here.

## Frozen source and exactly three readings

Use the frozen 115-row source in stored page/top-to-bottom order. Exclude exactly the four title rows, leaving 111 physical content rows on printed 108–111: 7, 41, 29, 34. Keep deck, quotation, facts, lists and all other non-title roles. Source furniture, decorative lettering, opener 107, artwork 112 and adjacent ads are outside this model.

Preserve every stored printedText string literally: case, punctuation, one ASCII word space and unjoined physical wraps. ASCII apostrophes, U+2014 long dashes and the selected book-title quote glyphs are declared transcription conventions, not original typesetting bytes. Stop on pin/count/spacing errors; do not repair the source during execution.

1. **SAND-FW-ALL:** the first nonempty space-delimited chunk of each of the 111 rows, with attached punctuation and case, joined by one ASCII space. A punctuation-only initial chunk causes a stop rather than a skipped token.
2. **SAND-ODD-LINES:** globally number the 111 retained rows after title exclusion. Keep 56 complete odd rows, joined with LF.
3. **SAND-EVEN-CONTROL:** keep the 55 complete even rows using the same global counter and LF. This complement is a predeclared parity control.

There are no page/block resets, other role/color populations, reversals, initials/finals, right-edge words, strides, selected substrings or additional variants. No format/checksum sweep, dictionary filtering, prose hashing, key/address derivation or network request is part of this procedure.

## Controls and review

Synthetic controls precede target execution: exact punctuation/case retention, a predetermined first-word sentence, global parity across pages and roles, title-only exclusion, preservation of physical wraps, and reject-not-repair behavior for malformed rows and pin/population failures. A separate implementation must agree on all three complete generated outputs, not just counts.

Two AI reviewers then independently read all three complete saved outputs, without seeing each other's conclusion. They know the puzzle context; this is not a blinded experiment or calibrated message detector. A possible second message must be directly coherent without omitted/substituted words, additional decoding or a chosen promising substring. A claimed instruction needs a concrete action and target/unit/source anchor. Isolated thematic words or ordinary cover-prose fragments do not meet that criterion. Potential key material stays private and requires a separately fixed validation step.

If both finish and recognize nothing, report only: **No clear second message was recognized in these three fixed literal readings.** This subjective finding does not exclude encoded keys, other populations/resets/orders, source eligibility, the article or the puzzle. Pin/source failure, incomplete review or unresolved disagreement is inconclusive. Execution alone supplies no semantic verdict.

## Reproduce

Python 3.9+ standard library and Git. Use a Git checkout containing the registration commit: the scripts verify the protocol, source and code against its actual Git objects without network access. A downloaded ZIP alone does not contain those Git objects.

From the repository root, choose fresh output directories outside the checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 public/research/scripts/funky_sand_direct.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 public/research/scripts/verify_funky_sand_direct.py --self-test
PYTHONDONTWRITEBYTECODE=1 python3 public/research/scripts/funky_sand_direct.py --run --protocol public/research/analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.json --registration-commit REGISTRATION_COMMIT --out ../key404-private-sand-run
PYTHONDONTWRITEBYTECODE=1 python3 public/research/scripts/verify_funky_sand_direct.py --verify --protocol public/research/analysis_outputs/continuation_20261110/funky_sand_direct/PROTOCOL.json --registration-commit REGISTRATION_COMMIT --readings ../key404-private-sand-run/READINGS.private.json --result ../key404-private-sand-run/RESULT.json --out ../key404-private-sand-check
```

Replace REGISTRATION_COMMIT with the commit first publishing this protocol. Raw generated readings and source-row mappings remain private until reviewed; public source inputs and reproducible rules are available to everyone. Execution and verification supply no semantic verdict. This procedure imports no wallet and submits no transaction.

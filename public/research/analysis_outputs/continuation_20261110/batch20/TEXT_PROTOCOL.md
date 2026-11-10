# Ten fixed text and record-format procedures

Registered before target execution. This is the text half of a twenty-procedure research batch, not twenty independent theories. Parameters, source bytes, implementations and public synthetic controls are frozen in [TEXT_PROTOCOL.json](TEXT_PROTOCOL.json). No outcome is claimed here.

The creator linked George Sand’s alternate-line and first-word examples and later linked mirror writing. T01 combines alternating reading direction with the corrected printed lines. T02–T06 are bounded extensions, with weaker source support identified in each definition. T07–T10 audit serialized formats omitted by earlier literal-key checks; they do not create a new extraction. The frozen source population for these four is the same 22 readings / 42 forms used in the preceding minikey audit.

## Fixed evaluation

WIF, 22/30-character minikey, boundary-delimited 64hex scalar and unfiltered contiguous BIP39 word windows are checked for T01–T06. BIP39 lowercases lexical words and recognizes punctuation boundaries, but never joins across an invalid decoded group. No ordinary prose is hashed into a secret, no arbitrary 32-byte ASCII string is treated as a scalar, and no wallet, transaction or network query is used. Published specification vectors and negative controls are tested before every target run. A scanner bug that crossed invalid groups was fixed and regression-tested before registration.

T01 is a corrected-source re-audit and may overlap old outputs. T05 freezes a deterministic sentence splitter; it does not claim an independently reviewed sentence-unit manifest. Parameters and limitations for every test are in the JSON. A negative result rules out only the declared literal records in the exact outputs, not an entire cipher family or the puzzle.

## Reproduce

From the research archive root, use Python 3.10 or later (standard library only):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_text.py --self-test
# Replace REGISTRATION_COMMIT with the commit that first published this protocol.
PYTHONDONTWRITEBYTECODE=1 python3 scripts/batch20_text.py --run T01 --protocol analysis_outputs/continuation_20261110/batch20/TEXT_PROTOCOL.json --registration-commit REGISTRATION_COMMIT --out text-T01-rerun
```

Use a fresh output directory and a registered ID T01–T10. The runner refuses changed source/implementation hashes and existing output directories. It writes restricted raw streams plus a redacted result. Review private-record leads before sharing raw outputs.

## Sources

- [George Sand examples](https://ciphermysteries.com/2010/05/16/george-sands-cryptography).
- [Mirror writing paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/).
- [BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki), [SLIP132](https://github.com/satoshilabs/slips/blob/master/slip-0132.md), [BIP38](https://github.com/bitcoin/bips/blob/master/bip-0038.mediawiki), [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki), [BIP173](https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki), [BIP350](https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki).

## Procedures

- **T01 — Alternating direction on the actual printed lines** (high). The older boustrophedon test used merged transcript lines; this is a corrected-source test.
- **T02 — Fixed interior columns of printed words and characters** (medium). Interior columns extend the first-word clue but are not creator instructions.
- **T03 — Mirror-axis centers of printed lines** (exploratory). The center selector is an exploratory mirror hypothesis.
- **T04 — Paragraph-boundary readings** (medium). Paragraph IDs were visually reconstructed, not supplied by an authoritative manuscript.
- **T05 — Sentence-boundary readings from the faithful body** (medium). Sentence segmentation is a declared inference; alternate segmentation is outside this test.
- **T06 — Visible capitalization as a data carrier** (exploratory). Grammar, ordinary capitalization and the all-caps paragraph are strong null explanations.
- **T07 — Serialized extended private-key records** (high). No extended-private format is specified by the creator.
- **T08 — BIP38 encrypted private-key records** (high). A structural encrypted record would require a separate passphrase/source lead.
- **T09 — Literal candidate funding addresses** (high). A valid or active address is not authenticated as Max Keiser's.
- **T10 — Literal SEC public keys and curve membership** (high). Curve membership has no embedded checksum and does not prove intentional encoding or ownership.

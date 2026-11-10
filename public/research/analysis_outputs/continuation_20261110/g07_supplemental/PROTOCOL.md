# G07 saved-output format replay

This supplements missing literal-format checks on the **same 1,038 saved spectral-OCR records**, with 833 unique texts and 1,464 exact/Unicode-whitespace-compacted forms. It does not rerun OCR or change the 112 historical source views. The original G07 procedure and its older results remain unchanged.

The [machine protocol](PROTOCOL.json) fixes eight source witness pins and five code pins. The shared common file appears in both maps: there are 13 distinct registered files including the protocol. Both controlled adapters must prove the actual Git commit and exact current/registered bytes before parsing target text. Root separately verifies prior remote publication.

Only extended-private records, BIP38 records, literal Bitcoin addresses, SEC public keys and overlapping embedded 26-character minikey shapes are added. A mini-key check is eight bits; a pass would be a private review lead. There is no scalar derivation, prose-to-key hash, wallet import, transaction or candidate-history request.

The primary reuses the frozen primary form/format/window core. The verifier reuses its separate frozen form/window core, reconstructs the complete saved population and compares every private form and validation record. Both deliberately share the unchanged four-format engine. This is not independent cryptographic mathematics for those four validators. Both compile hash-verified dependency source directly. Source-free control receipts and technical review accompany this protocol.

Python 3.9+ standard library, and a local Git checkout containing the published registration commit, are required. From `public/research`, use a fresh private parent outside the entire checkout:

```sh
task_private="$(mktemp -d /tmp/key404-g07.XXXXXX)"
python3 -B scripts/g07_supplemental_formats.py --self-test
python3 -B scripts/verify_g07_supplemental.py --self-test
python3 -B scripts/g07_supplemental_formats.py --run \
  --protocol analysis_outputs/continuation_20261110/g07_supplemental/PROTOCOL.json \
  --registration-commit PUBLISHED_REGISTRATION_COMMIT --out "$task_private/primary"
python3 -B scripts/verify_g07_supplemental.py --verify \
  --protocol analysis_outputs/continuation_20261110/g07_supplemental/PROTOCOL.json \
  --registration-commit PUBLISHED_REGISTRATION_COMMIT \
  --result "$task_private/primary/RESULT.json" \
  --forms "$task_private/primary/FORMS.private.json" \
  --validation "$task_private/primary/VALIDATION.private.json" \
  --out "$task_private/independent"
```

Replace the placeholder with the full registration commit recorded by the eventual result. Output directories must be fresh with 0700 parents; raw files are 0600. Guard failure is inconclusive. Public receipts contain aggregate counts and whole-artifact hashes, excluding raw values, fingerprints and candidate-derived associations.

OCR misses and other source readings remain outside this result. No semantic recognition or whole-puzzle exclusion is computed. The puzzle is unsolved.

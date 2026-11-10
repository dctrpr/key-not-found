# Supplemental formats on fixed batch20 outputs

The registered supplemental check completed with **zero valid records** on seven unchanged saved cohorts: **2,594 labelled streams and 2,576 summed per-cohort unique forms**. It added four literal-format families to T01–T06/G03 and the exact 26-character minikey gate to T01–T06. No selector was regenerated.

The new gates found 329 address-shaped occurrences and 47 minikey26-shaped occurrences. After deduplication within each cohort, 156 address validations and 30 minikey question-mark checks ran; **all were rejected**. Extended-private, BIP38 and SEC-public-key gates found zero shapes, so no candidate reached their validation stage.

| Cohort | Saved labels | Forms | Address occurrences / checks | Minikey26 occurrences / checks |
|---|---:|---:|---:|---:|
|T01|196|236|250 / 91|12 / 4|
|T02|628|1,120|49 / 49|18 / 15|
|T03|120|168|30 / 16|8 / 5|
|T04|252|316|0 / 0|0 / 0|
|T05|42|54|0 / 0|3 / 3|
|T06|60|66|0 / 0|6 / 3|
|G03|1,296|616|0 / 0|0 (inferred) / 0|

Forms are each cohort's unique exact texts plus Unicode-whitespace-only compaction. **The 2,576 forms and 156/30 checks are sums of per-cohort counts, not globally unique values or independent theories.** Cross-cohort overlaps were not calculated. The existing WIF, 22/30-character minikey, hex and BIP39 work is not presented as newly performed.

G03's 26-character coverage is an inference on the identical frozen forms: its old detector counted zero 22-character S/Base58 shapes before checksum validation, and every 26-character shape necessarily has such a 22-character prefix. **No new G03 minikey enumeration or checksum call ran.** The four added format families were directly checked for G03.

The independent full-output replay reported **PASS**. It reconstructed all seven original stream-object/order populations, all forms and UTF-8 content, independently enumerated the six text cohorts' 26-character windows, and matched complete private validation plus safe per-cohort/total counts. The four added format shape/validation engines deliberately share pinned code; this is not independent implementation of those four engines. Source-free controls and technical peer review preceded execution.

Registration: [`d025f95b5e8cabda35e2cc316ac44acd97e23a95`](https://github.com/dctrpr/key-not-found/commit/d025f95b5e8cabda35e2cc316ac44acd97e23a95). [Protocol](PROTOCOL.json) SHA256: `5d24ffed7de1b465874a7c64f0e522e922cca9151fb6995e4afbaec7be893669`. The [registration receipt](REGISTRATION.json) records exact remote-main agreement at **2026-11-10T18:08:26.794246Z**, before execution at **18:08:26.864Z–18:08:27.459Z**. The [independent verification](INDEPENDENT_VERIFICATION.json) completed at 18:08:39.725770Z; the [safe execution receipt](EXECUTION.json) retains all 24 source/3 code pins and private-artifact integrity hashes.

This closes a finite **format-coverage correction** on the [manifest's exact artifacts](MANIFEST.json). It does not authenticate their source selectors, add a creator instruction, perform semantic recognition, exclude a mirror/cipher family or rule out the puzzle. The format check made no scalar/seed/child-key/address derivation, bare minikey scalar hash, candidate-history query or transaction. There is no funding or prize conclusion. Raw forms, values, record fingerprints, addresses and hit locators stay private.

## Reproduce

Use a Git clone containing the exact registration commit. A source ZIP alone cannot satisfy the actual Git-object gate. From `public/research/`, run:

```sh
python3 -B scripts/batch20_supplemental_formats.py --self-test
python3 -B scripts/verify_batch20_supplemental.py --self-test

replay_dir="$(mktemp -d "${TMPDIR:-/tmp}/key404-supplemental.XXXXXX")"
chmod 700 "$replay_dir"

python3 -B scripts/batch20_supplemental_formats.py --run \
  --protocol analysis_outputs/continuation_20261110/batch20_supplemental/PROTOCOL.json \
  --registration-commit d025f95b5e8cabda35e2cc316ac44acd97e23a95 \
  --out "$replay_dir/primary"

python3 -B scripts/verify_batch20_supplemental.py --verify \
  --protocol analysis_outputs/continuation_20261110/batch20_supplemental/PROTOCOL.json \
  --registration-commit d025f95b5e8cabda35e2cc316ac44acd97e23a95 \
  --result "$replay_dir/primary/RESULT.json" \
  --forms "$replay_dir/primary/FORMS.private.json" \
  --validation "$replay_dir/primary/VALIDATION.private.json" \
  --out "$replay_dir/independent"
```

Keep the fresh private parent outside the entire checkout, with 0700 directory/0600 file permissions. Do not place raw replay artifacts under `public/`. The registered implementations also enforce byte/counter caps and reject mismatched current/registered inputs.

The [post-run review](POST_RUN_REVIEW.json) checks source/code pins, completion order, saved integrity and private permissions. The [combined checkpoint](RESULT.json) supplies the source-pinned visual metrics.

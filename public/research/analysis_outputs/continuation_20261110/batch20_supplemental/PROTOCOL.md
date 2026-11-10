# Supplemental formats on the frozen batch20 outputs

This procedure closes a documented format-coverage gap over existing outputs. It introduces no new cipher selector, text reconstruction, geometry, page order or cross-record join. The puzzle remains unsolved.

## Fixed inputs

The exact T01–T06 and G03 STREAMS files, their original safe results/checks, the [coverage manifest](MANIFEST.json), and unchanged shared controls/wordlist are hash-pinned. The seven stream artifacts total 613,097 bytes and 2,594 labelled records. Original per-cohort form counts sum to 2,576; this is not a count of globally unique forms or independent theories.

Preserve each saved text and consider only its exact form and Unicode-whitespace-only compaction, with deduplication inside each cohort. Do not regenerate any selector or normalize punctuation, case, glyphs or Unicode. The two text forms are the same policy used by the owning original scanner.

## Added gates

- For all seven cohorts: extended private records, BIP38 encrypted-private records, literal mainnet Bitcoin addresses, and SEC public-key encodings, using the unchanged pinned shared validators.
- For T01–T06: every overlapping embedded S-prefixed Base58 window of exactly 26 characters; check only the leading byte of SHA256(value + "?"). This weak eight-bit check is compatibility evidence, not authentication.
- G03 receives no new minikey scan. Its old zero embedded 22-character shapes logically excludes a 26-character shape on unchanged forms: any such shape would have a valid-length 22-character prefix. This does not exclude any of the four added formats.

The old WIF, bounded hex64, BIP39 and 22/30-character minikey checks remain unchanged. The historical 26-character support is documented in the [earlier source receipt](../minikey26_compatibility/HISTORICAL_SOURCE.json); it does not establish that Keiser used that format.

## Registration and result handling

The final protocol, code and all 24 source witnesses must match an actual public registration commit and current files before target parsing. Public preregistration is independently verified by the operator. Target execution follows source-free controls and technical review.

Both implementations preserve and compare full private forms and validation records. Reading/form construction and minikey enumeration are implemented independently; the four format validators deliberately share pinned code. Agreement is not four independently implemented cryptographic engines.

Use fresh private output folders outside the entire project checkout, with 0700 directories and 0600 files. Publish only aggregate counts and whole-artifact integrity. Raw shapes, values, fingerprints and hit locations remain private. No minikey scalar hash, key/address derivation, wallet import, signing, network candidate lookup or transaction is part of this procedure.

A positive is a lead requiring a separate source/authenticity review and, if justified, a separately fixed read-only history check. A BIP38-shaped record does not supply its password; a public address or SEC record is not a recovered private key. A negative closes only these specified gates on these exact saved forms. Inherited source and geometry uncertainty remains.

The command interface and exact final pins will be provided by the frozen implementations and PROTOCOL.json before target execution.


## Command interface

From a Git clone's `public/research/` directory, run the two source-free controls:

```sh
python3 -B scripts/batch20_supplemental_formats.py --self-test
python3 -B scripts/verify_batch20_supplemental.py --self-test
```

The target runner takes `--run --protocol analysis_outputs/continuation_20261110/batch20_supplemental/PROTOCOL.json --registration-commit FULL_PUBLIC_COMMIT --out FRESH_PRIVATE_DIRECTORY`.

The verifier takes `--verify --protocol` and the same registration commit, plus `--result`, `--forms`, `--validation` pointing to the complete primary private files, and `--out` pointing to another fresh private directory. Exact runnable commands and the actual registration commit accompany the result after execution. The registered protocol and 24 witness / three code hashes are fixed in PROTOCOL.json; no target result is claimed by this registration.

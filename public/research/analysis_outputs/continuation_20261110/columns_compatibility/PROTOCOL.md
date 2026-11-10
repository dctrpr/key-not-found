# Four earlier readings: fixed-output format check

This is one compatibility check across four saved populations. It closes recorded format gaps without introducing a new reading rule. It does not make any of these columns a verified prize target, and it does not replace the Issue24 magazine photographed in the March 2023 announcement.

| Population | Original records | Checks added here |
| --- | ---: | --- |
| Funky Upheaval: three direct Sand readings | 3 | WIF, minikey 22/30, hex64, BIP39, extended-private, BIP38, literal Bitcoin addresses, SEC public keys, and minikey 26 |
| Censorship column: saved first-word outputs | 39,744 | Minikey26 only; the other formats were already checked |
| Orange Party column: body stride 12 | 72 | Extended-private, BIP38, literal Bitcoin addresses, SEC public keys, and minikey 26 |
| Orange Party column: frozen historical streams | 3,880 | The same four additional formats and minikey 26 |

The 43,699 labelled records are correlated outputs, not independent trials. Forms are the per-population union of exact texts and Unicode-whitespace-only compaction, retaining empty text. The Funky compatibility surface is newly registered and capped at six forms; it was previously reviewed for meaning only. The other form counts are fixed at 1,746/96/3,709. The Censorship run must directly prove that its exact-text set equals its exact-plus-compacted set. No global union is computed.

## Reproduce the saved inputs first

The machine protocol pins 57 public source/witness files plus the five adapter/format code files, with one shared path in both maps. It registers all four expected original-artifact byte identities. The Censorship raw JSONL is decompressed from its public gzip. The other three original reading artifacts are reconstructed using only their public frozen sources and original reading rules. Three reconstructions are declared explicitly: no new selector, OCR run, source repair or reversal variant is introduced.

All four complete artifact byte counts and SHA-256 identities must match before any target form or format validation. The Funky raw hash was already public in its original execution receipt. The stride and historical whole-artifact hashes are newly registered here; earlier independent record agreement is not misrepresented as an older public byte pin. Exact record ordering, JSON serialization and UTF-8/LF bytes are fixed. No private historical file is a runtime requirement.

Both adapters must prove the full actual Git registration commit and matching current/registered protocol, source and code bytes before target reconstruction or parsing. Dependencies are compiled directly from hash-verified source with their original public file paths; cached bytecode is not used. Root separately checks that the registration commit was pushed before the target run.

## Separate reconstruction and validation checks

The primary and verifier use separate reading loops and separate frozen form/minikey 26 cores. They deliberately share the unchanged common format engines. This is independent reproduction of complete outputs, forms and validation records, not independent cryptographic mathematics for the shared validators. The verifier compares every original UTF8 artifact and all private forms/validation records, including any positives.

The stride population contains 60 source-known readings nested within its 72 nominal readings. Its 78 known forms are checked as a subset of the 96 nominal forms. The known subset is classified by enumerating shapes and reusing the nominal validation outcomes; it makes zero extra validator/checksum calls and is not a fifth population. Three uncertain row prefixes, all 12 affected readings, and the historical stream source limits remain intact.

Minikey validation here checks the weak eight-bit checksum only. A pass is a private review lead. No raw values, candidate fingerprints or candidate-linked source positions enter the public result. There is no prose-to-key hash, scalar/seed/child-key/address derivation, wallet import, blockchain/history request or transaction.

## Run

Python 3.9+ standard library and a local Git checkout containing the published registration commit are required. From `public/research`, use fresh private directories outside the entire checkout:

```sh
task_private="$(mktemp -d /tmp/key404-columns.XXXXXX)"
python3 -B scripts/columns_compatibility.py --self-test
python3 -B scripts/verify_columns_compatibility.py --self-test
python3 -B scripts/columns_compatibility.py --run \
  --protocol analysis_outputs/continuation_20261110/columns_compatibility/PROTOCOL.json \
  --registration-commit PUBLISHED_REGISTRATION_COMMIT \
  --out "$task_private/primary"
python3 -B scripts/verify_columns_compatibility.py --verify \
  --protocol analysis_outputs/continuation_20261110/columns_compatibility/PROTOCOL.json \
  --registration-commit PUBLISHED_REGISTRATION_COMMIT \
  --result "$task_private/primary/RESULT.json" \
  --forms "$task_private/primary/FORMS.private.json" \
  --validation "$task_private/primary/VALIDATION.private.json" \
  --artifacts-dir "$task_private/primary" \
  --out "$task_private/independent"
```

Replace the placeholder with the full registration commit recorded by the eventual result. Parents/directories must be 0700 and files 0600. Resource caps reject oversized input; nothing is silently truncated or skipped. A failed identity, schema, coverage or code gate is inconclusive.

Funky issue/date and eligibility under the separate December plural-key claim remain unverified. Censorship first-word coverage cannot settle its blurred full-line endings. The Orange Party historical and body populations retain their distinct uncertainties. A negative result excludes only the registered literal-format surfaces on these fixed outputs. The puzzle remains unsolved.

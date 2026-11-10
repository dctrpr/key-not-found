# The missing length: one weak checksum lead

Completed **2026-11-10T11:20:30.256Z**. The [protocol and both implementations](PROTOCOL.json) were published in commit [`96e206c0a86d8b2b62b4cf323862d54934927929`](https://github.com/dctrpr/key-not-found/commit/96e206c0a86d8b2b62b4cf323862d54934927929) before the target scan. Remote GitHub state was verified first.

| Fixed population | Checked scope | Distinct 26-character shapes |
|---|---|---:|
| Original saved body readings | 22 readings, 42 exact/compacted forms; 113,662 potential positions; 9 shaped occurrences | 7 |
| Original global mirror model | All 24 language graphs, unchanged source choices | 200 |
| Union | No overlap between the two sets | **207** |

**One of 207 values passed the eight-bit checksum.** This is compatible with chance and does not authenticate a puzzle solution or prize. The run is complete for its registered format scope, but it is not a complete negative. No scalar, address or network history was generated in this experiment.

The [independent predecessor/suffix checker](INDEPENDENT_CHECK.json) reproduced the complete private candidate sets, all forms, all 24 language descriptors and every evaluation. A separate [Node crypto check](NODE_CHECK.json) agreed on the shape count and checksum fingerprint. The independent source builders are shared and frozen; this agreement does not independently calibrate the physical geometry.

The only public identifier for the checksum lead is the existing domain-separated fingerprint:

`16a4c57bfd34fa3663560b3eb13ec981aed6df399d8d5701e69716cbe7c435c1`

This fingerprint is **not** SHA-256 of the mini key. Raw values, selected source locators and derived-address associations are omitted from new summaries. Public source readings remain reproducible; this is not a secrecy guarantee.

## What this changes

The [2013 compatibility source](HISTORICAL_SOURCE.json) establishes that some historical software accepted 26-character mini keys. Earlier 22/30-character results remain unchanged. This replay adds one missing literal format length to two original populations; it adds no new cipher mechanism, reading, geometry or other format.

The global model still includes uncertain, investigator-defined boundary choices. A checksum match does not select a physically justified reading or prove creator intent. Other source populations, intermediate messages and encodings remain open. A separate source-witness review and fixed read-only history protocol are next; neither is counted as completed here.

## Reproduce from a Git clone

From the clone's `public/research` directory, using fresh output folders outside any public directory:

```sh
python3 scripts/minikey26_compatibility.py --run --protocol analysis_outputs/continuation_20261110/minikey26_compatibility/PROTOCOL.json --registration-commit 96e206c0a86d8b2b62b4cf323862d54934927929 --out /tmp/key404-26-replay
python3 scripts/verify_minikey26_compatibility.py --verify --result /tmp/key404-26-replay/RESULT.json --forms /tmp/key404-26-replay/FORMS.private.json --candidates /tmp/key404-26-replay/CANDIDATES.private.json --out /tmp/key404-26-independent
```

Keep raw outputs private. No wallet import, signing or transaction is included. See [RESULT.json](RESULT.json) for exact pins, times, counts, cap accounting and limitations.

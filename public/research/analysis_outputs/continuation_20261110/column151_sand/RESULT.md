# Column151: fixed Sand readings, literal-format result

The registered scan completed with **zero validated literal records** across **three readings and six exact/whitespace-compacted forms** (8,404 submitted codepoints).

Two separate AI contexts read **all three complete saved texts**: 8,404 codepoints / 8,438 UTF-8 bytes per reader. Neither recognized a coherent second message or actionable intermediate instruction beyond ordinary article fragments. Both had prior source/protocol exposure; one also knew the earlier body-only semantic result. These are unblinded subjective reviews, without a calibrated false-negative rate. See [review A](SEMANTIC_A.json), [review B](SEMANTIC_B.json) and their coverage records. This is not formal message exclusion.

The [source model](../../../sources/issue24-column151/SOURCE.json) corrects the earlier model of 149 units by adding the column name and byline on printed page 73. It preserves the 142 body rows and seven existing title/display/signature units, giving 151 declared physical units. This is a coverage correction within the same reading family. Stored order, case, punctuation and physical wraps are retained; original typesetting bytes and every printed glyph/artwork are outside the model's claim.

The [registered protocol](PROTOCOL.json) fixes one global index:

| Reading | Selected units | Serialization |
|---|---:|---|
| First chunks |151|First whitespace chunk of every unit, space-joined|
| Odd whole lines |76|Global positions 1,3,…,151, LF-joined|
| Even control |75|Global positions 2,4,…,150, LF-joined|

Each reading contributed its exact text and whitespace-only compaction. There were no page resets, reversals, additional selectors or prose-to-key hashes.

| Embedded minikey length | Shape occurrences | Unique weak-check calls | Passes |
|---|---:|---:|---:|
|22|2|2|0|
|26|1|1|0|
|30|0|0|0|

These are exact-length, S-prefixed Base58 windows. The three candidates were checked only by the 8-bit `SHA256(value + "?")[0] == 0` gate. No minikey scalar hash, seed/child-key derivation, address derivation, network lookup or transaction occurred.

The seven other gates—WIF, bounded 64-hex scalar records, English BIP39, extended-private records, BIP38 records, Bitcoin addresses and SEC public-key encodings—each found **zero shape candidates**, so no record reached their checksum/range/curve validation stage. Those gates use the unchanged pinned shared engine. The independent checker deliberately shares that engine; it independently reconstructed all three UTF-8 readings and selected-ID orders, all six forms, and the 22/26/30 minikey enumeration, then matched the full private validation and safe counts. Its saved receipt reports **PASS**. This does not establish independent implementations of all seven shared validators.

Registration commit: [`bac7e29f8745d7dd7fb5bd444dc35f2cb5ba869c`](https://github.com/dctrpr/key-not-found/commit/bac7e29f8745d7dd7fb5bd444dc35f2cb5ba869c). Protocol SHA-256: `8e3cc1ed368e4bcb5c402f295e915b83d30d8ec62cd571ee968351e59a8b42ac`. The registration receipt records matching remote main at 2026-11-10T16:46:49.111020Z, before execution at 16:46:53.571Z–16:46:53.867Z. The independent receipt completed at 16:47:02.483932Z. The frozen protocol's retained draft-status string predates the later registration receipt.

The result applies only to the declared model of 151 units, three readings, six forms and specified literal-format gates. Readable intermediate instructions, other readings/transcriptions, untested formats and the whole puzzle remain unresolved. No prize or funding conclusion follows. Raw readings and validation artifacts remain private; no record values, fingerprints, addresses or hit locators are published.

The safe [execution receipt](EXECUTION.json), [full-output verification](INDEPENDENT_VERIFICATION.json), [remote registration receipt](REGISTRATION.json) and [combined result](RESULT.json) retain exact integrity pins. The final registration-byte audit completed just after the primary run started; the previously published technical review and actual runtime Git-object checks establish the pre-execution code/protocol controls. It is not presented as an additional pre-run timing gate.

## Reproduce

Use a Git clone containing the exact registration commit above. A ZIP supplies the source files but cannot satisfy the registered Git-object gate by itself. From `public/research/`, run the source-free controls first:

```sh
python3 -B scripts/column151_sand_probe.py --self-test
python3 -B scripts/verify_column151_sand.py --self-test
```

Then follow [the fixed protocol](PROTOCOL.md), supplying the published registration commit and a fresh private output directory outside the entire checkout, with a 0700 parent. Run the independent verifier against all saved private outputs. Do not write readings, minikey windows or validation values under `public/`. The [primary script](../../../scripts/column151_sand_probe.py) and [independent verifier](../../../scripts/verify_column151_sand.py) expose their full command options in the argument parser.

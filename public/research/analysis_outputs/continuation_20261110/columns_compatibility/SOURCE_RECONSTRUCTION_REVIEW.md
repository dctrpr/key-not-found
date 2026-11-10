# Frozen original-reading reconstruction: source-only review

**PASS: the needed public code and source bytes are available.** This review checked 30 unique public source/code/protocol files against audit05 pins. It did not parse any target source JSON/text or raw private artifact, execute a producer, generate readings/reversals/forms, or run a checksum. Full source bytes were read opaquely only for file integrity. Exact records/serializers below are future registered operations, not work already executed here.

## Primary materialization APIs

- **Funky:** `validate_source(fullModel)` ->111 non-title rows; `literal_readings(rows)` ->3 records. Rebuild the ORIGINAL envelope in this order: `schemaVersion`, `testId`, `sourceSha256`, `readings`, with old testId/source SHA. `json_bytes()` is the exact serializer: indent 2, `ensure_ascii=False`, `allow_nan=False`, UTF-8 plus one LF. Each reading inserts `id`, `selectedRowCount`, `text`. Do not use the new combined testId inside the original artifact.
- **Stride 12:** `validate_source(BODY,parent,oldProtocol.sourceExpectations,oldProtocol.sourceHashes)` ->312 rows; `make_tokens(rows)` ->2018 tokens; `make_readings(tokens)` ->72 records. Serialize each dict with default `json.dumps(...,ensure_ascii=True)` plus LF. Exact insertion order: `id,direction,phase,projection,selectedTokenCount,sourceCompleteForProjection,uncertainSelectedTokens,text`. These three source functions perform no format validation or form construction.
- **Historical 1940:** `validate_source(parent)` ->1940-stream dictionary; `list(submitted_readings(streams))` ->3880 records, sorted labels and exact then reversed-codepoints. Serializer is default `json.dumps(...,ensure_ascii=True)` plus LF. Exact insertion order: `id,sourceLabel,characterOrder,text`. Do not add new reversals or substitute the newer body model.

The original raw writer objects contain no runtime time, nonce or output path. Safe result wrappers include time and will differ. Exact byte matching still needs to be established in the new registered run; static determinism is not a new reconstruction proof. Preserve LF explicitly for cross-platform output; default Windows text mode can create CRLF.

## Independent APIs and non-obvious work

`verify_funky_sand_direct.build_readings(rows,production=True)` independently validates roles/order and manually walks U+0020 first chunks. It preserves the same reading dict order. No primary generator import is needed.

`verify_issue27_stride12.source_rows(body)` -> `tokens_from_rows(rows)` -> `readings_from_tokens(tokens)` is independent of the primary. **The last function also constructs an exact/Unicode-whitespace-compacted form union for resource-cap checks.** Reuse only after registration and truthfully declare that form work, or pin an independently implemented equivalent record loop/cap policy. It is validator-free, not form-free. `strict_known(records)` filters whole records; no missing letter/token may be dropped.

`verify_issue27_saved.compare_saved_to_primary(parent,records)` compares every record with sorted source labels and internally computes its exact/reversed counterpart. It returns no constructed record collection. Calling it is original-reading reconstruction for comparison, not metadata-only work. An independent assembler can follow that frozen rule and exact record order, with the new code pinned before use.

## Source order, uncertainty and globals

Stride body text is 312 rows on printed 79–81, even though four source-image pins include 78. Preserve that frozen population. Three first-token prefixes affect words/initials only: token-index and projection flags drive the 72 nominal/60 strict-known/12 affected readings; all finals are source-complete. Preserve the 18 wrapper characters, ASCII whitespace chunk rule, case, punctuation, censor stars and hard-wrap fragments. No joining or source repair belongs in reconstruction.

Funky excludes only four title rows globally, retaining 111 rows across 108–111. Do not reset parity by page or exclude display/list/quotation roles. First chunks are literal U+0020-delimited surfaces, not lexical words with punctuation stripped.

Compile SHA-verified source bytes directly with a non-`__main__` module name and `__file__` set to the actual original public producer/verifier path. Funky derives global ROOT directly from that path. Stride derives ROOT from its sibling common file and inserts `ROOT/scripts` into process-global `sys.path`; preserve/restore that path list after compilation or isolate the loader. New adapters should use their own strict private-output guards. Do not rely on old verifier path helpers for the new all-Site boundary.

Avoid `run/main/self_test/evaluate/verify/load_evaluator` in source-only materialization. The original CLIs reproduce old validators as well as readings; the old independent evaluator loader is bytecode-capable. None is required by the pure APIs above. A source-free loader may stat directories during module initialization; it must not open a target source before the new registration gates pass.

## Expected original artifacts and truthful protocol fields

Funky original JSON SHA is already public in its prior EXECUTION receipt and matched the retained artifact in audit05. Stride and historical current raw hashes are in audit05; their prior public receipts attest full record equality but do not publish a whole-raw-file integrity field. The combined protocol must newly register those expected hashes before reconstruction/validation. The companion JSON lists all three exact hashes and byte counts without any raw text.

A supplied-private-artifact mode can truthfully record no reconstruction. A public-input materialization mode must record originalReadingReconstruction=true, newSelectorIntroduced=false, OCR=false and sourceRepairs=false. If the full original CLI is used instead of pure APIs, record its old validator work separately. Do not hide extraction, reversal or form generation behind a blanket zero-selector-regeneration claim.

Funky chronology/December eligibility remains conditional; these Issue27 models also do not replace the authenticated photographed March Issue24 target. Reconstructing frozen readings improves reproducibility, not source identity or the physical-source uncertainty.

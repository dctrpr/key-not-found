# G02 shared query offset protocol

The [prior stencil result](../g02_shape_reachability/RESULT.md) found eight one-sided reading languages that admit Base58 syntax when uncertain positions can vary independently. This test asks which of those languages still admit the same syntax when the two directions of each registered page pair share an offset. The two pair blocks are pages 76/77 and 78/79.

## Model

Use the exact binary-rational centers and mask coordinates from the [joint color audit](../g02_joint_color_audit/RESULT.md). For a block with lower page A and higher page B, define reflection `R(x,y)=(2544-x,y)` and its linear part `F(x,y)=(-x,y)`. Use one offset `t=(tx,ty)` in the closed box `[-12,12] × [-12,12]` for that block. In direction A→B, query at the target word center plus `F(t)`. In direction B→A, query at the target word center minus `t`. At each query, sample the source at the reflected point and the target at the query itself. Keep the original half-open rectangle predicates.

All frozen word guards are at least 12 pixels. This guarantees that the shared queries stay inside the old independent-position language. The 12 pixels describe a word-position guard. Actual displacement between printed faces would move the reflected source relative to a fixed target query and requires a separately measured range. The announced opener and visible gutters support page order, while the earlier texture comparison supplies no physical alignment bound. [Page order audit](../../continuation_20261109/state_audit.md) · [Texture comparison](../../source_audit/corrected_topology_77_76_light_table/corrected_topology_77_76_light_table.md)

## Decision

Split each offset axis at the pulled-back rectangle edges and box endpoints. Keep every edge point and one representative inside each open interval, then take their Cartesian product. The primary uses the prior proof of constant class to skip stable words when collecting edges. A separate implementation uses pulled-back half-open spans to reconstruct and compare every distinct ordered selection mask across both directions. Check both direction masks together for each selector and block. The comparison uses a SHA-256 of canonical sorted JSON and per-selector counts. Zero remains a valid offset and empty selections are part of the model.

For each of the eight previously syntax-positive languages, keep the earlier projection and direction. Within a block keep both direction masks coupled. In the global language, allow any independent combination of the two whole block choices. For reversed order, reverse the blocks, the directions within each block and the word sequence within each direction. Preserve the original words and punctuation. Check exactly the previous WIF-like and minikey-like grammar flags. The largest marker-started Base58 run in a combined reading is the largest internal run or the largest marker-started trailing run in the first fragment plus the largest Base58 prefix of the second fragment. Retain both blocks in global tests even if one has no standalone match. The 152 previously shape-negative languages remain negative under the restriction.

The primary uses at most 100,000 partition cells per block, 5,000,000 variable position evaluations in total and 5,000,000 projected characters. The verifier uses at most 500,000 cells and 50,000 distinct paired masks per selector per block. A cap, changed pin, overlap, state outside the earlier membership envelope or implementation disagreement prevents a completed claim. Before registration, require source-free endpoint, reciprocal coupling and fragment-product checks. Verify current and registered Git blobs before execution.

The result records syntax presence, prior grammar flags, counts and digests. It performs zero checksum checks, derivations, history queries and wallet actions. The outcome applies to this shared query model. It gives no measurement of physical displacement and no evidence of creator intent, a verified key or a funded prize.

## Reproduce

From the Git repository root, first run both source-free controls. Supply the exact registration commit and fresh absolute output directories outside the repository.

```sh
python3 public/research/scripts/run_g02_shared_query.py --self-test
python3 public/research/scripts/verify_g02_shared_query.py --self-test
G02_PROTOCOL=public/research/analysis_outputs/continuation_20261110/g02_shared_query/PROTOCOL.json
python3 public/research/scripts/run_g02_shared_query.py \
  --research public/research --protocol "$G02_PROTOCOL" \
  --registration-commit "$REGISTRATION_COMMIT" --out "$PRIVATE_PRIMARY"
python3 public/research/scripts/verify_g02_shared_query.py \
  --research public/research --protocol "$G02_PROTOCOL" \
  --registration-commit "$REGISTRATION_COMMIT" \
  --primary-result "$PRIVATE_PRIMARY/RESULT.json" --out "$PRIVATE_VERIFICATION"
```

[Exact source and implementation pins](PROTOCOL.json)

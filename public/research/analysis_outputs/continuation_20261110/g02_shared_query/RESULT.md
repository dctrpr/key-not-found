# Three stencil matches disappear under shared offsets

Of the eight one-sided reading languages that admitted literal Base58 syntax in the [previous test](../g02_shape_reachability/RESULT.md), **three lost every match** when each page pair shared a query offset. Five still admit a shape. Every 30-character minikey-like shape disappeared. The prior negative results for the other 152 reading languages still hold under this restriction. [Machine result](RESULT.json)

| Literal pattern | Reading languages before | Reading languages with shared offsets |
| --- | ---: | ---: |
| Minikey-like, 22 characters | 7 | 3 |
| Minikey-like, 26 characters | 7 | 2 |
| Minikey-like, 30 characters | 4 | 0 |
| WIF-like, 51 characters | 2 | 2 |
| WIF-like, 52 characters | 2 | 2 |

The counts describe reading languages and can overlap across patterns. The five surviving languages use pages 76/77 or the global sequence. Global and page-local results can reflect the same occurrence. They establish syntax only. Key checksum validations, derivations, history queries and wallet actions were all zero.

## What changed

The previous test let each uncertain word use a different location within its guard. This follow-up uses one offset in a closed ±12-pixel square per page pair. Each offset fixes both directions of that pair together. The two algorithms agreed on the complete sets of paired selection masks, including boundary cases. They used 385 exact cells for pages 76/77 and 869 for pages 78/79. The target run began after public registration and verification of all 18 blobs. [Method](PROTOCOL.md) · [Registration](REGISTRATION.json) · [Independent mask verification](INDEPENDENT_VERIFICATION.json)

A separate post-result verification rebuilt the paired masks and directly scanned every complete mask combination for the eight eligible reading languages. It agreed with all 40 syntax flags. That direct replay checks the compact fragment calculation. [Flat verification](FLAT_SHAPE_VERIFICATION.json)

From the repository root, reproduce the flat comparison with the registered protocol and saved public receipts. Use a fresh absolute output file path outside the repository.

```sh
G02_DIR=public/research/analysis_outputs/continuation_20261110/g02_shared_query
python3 public/research/scripts/verify_g02_shared_query_shapes.py \
  --research public/research --protocol "$G02_DIR/PROTOCOL.json" \
  --registration-commit 93c86161f2190161a7079f485e390cbcb96f6ab7 \
  --primary-result "$G02_DIR/RESULT.json" \
  --mask-receipt "$G02_DIR/INDEPENDENT_VERIFICATION.json" --out "$PRIVATE_FLAT_RECEIPT"
```

## Physical source limit

The ±12-pixel square comes from the frozen word-position guards. In this model the offset moves both sampling queries together. Physical displacement of the reflected source relative to the target would need its own transform and measured bounds. The archived scans have no verified paired trim registration. The lower-resolution witness retains partial page edges, so the next source check is to document which physical edge segments can be located consistently on both faces before fitting any alignment. [Scan provenance and alignment evidence](PHYSICAL_SOURCE.md)

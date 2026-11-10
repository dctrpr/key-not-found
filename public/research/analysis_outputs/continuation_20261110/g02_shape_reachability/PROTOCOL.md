# G02 literal shape reachability protocol

This test checks whether the [verified stencil model](../g02_joint_color_audit/RESULT.md) can produce any of the literal text shapes used by the original G02 scanner. It uses the frozen physical word order and the must, optional and forbidden classifications already verified for each selector.

## Reading model

The four directed page pairs run in order 76→77, 77→76, 78→79 and 79→78. Test each separately and concatenate them for the global scope. For each scope, select same-color, opposite-color, source-only or target-only words. Allow every optional position independently. This includes all assignments allowed by the frozen position classifications and may include assignments that a single physical displacement cannot realize.

Read selected words in forward order and in reversed word order. Use printed words spaced or joined, and their first or last Unicode alphanumeric characters. Joined words represent the whitespace-compacted spaced reading. Both edge forms are identical under the original exact and whitespace-compacted passes. These choices yield 160 reading languages and 240 original scanner labels.

## Acceptance and completion

For each language, test whether at least one path contains a literal shape recognized by the original scanner. The shapes are Base58 WIF-like runs of length 51 or 52 with the specified prefix, minikey-like runs of length 22, 26 or 30 with prefix S, a maximal hexadecimal run of length 64, and consecutive English BIP39 dictionary words in runs admitting 12, 15, 18, 21 or 24 words. Use the pinned shared boundary and token rules. Record presence by language and shape. A present shape only establishes that the language admits the syntax.

Build an acyclic graph of the exact projected readings and propagate finite recognition states without listing large assignment sets. For each completed language with at most 256 assignments, require agreement with the shared flat scanner over all assignments. The implementation passed 525 source-free flat comparisons before registration. Stop recognition at 2,000,000 metered work units per language. A cap is inconclusive. Graph construction relies on the fixed size of the input model. Unexpected errors terminate the run without a completed report.

The report records coverage and shape presence only. The test performs zero checksum checks, derivations, history queries and wallet actions. Its scope is the declared stencil language and literal grammar.

## Reproduce

From the repository root, run the source-free check first. Supply the full Git commit that registered this protocol. Use an absolute output path outside the public research tree.

```sh
python3 public/research/scripts/g02_shape_reachability.py --self-test
python3 public/research/scripts/run_g02_shape_check.py \
  --research public/research \
  --protocol public/research/analysis_outputs/continuation_20261110/g02_shape_reachability/PROTOCOL.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --out "$PRIVATE_OUTPUT"
```

[Input and implementation hashes](PROTOCOL.json)

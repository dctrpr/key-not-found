# Read the saved alternating-direction texts

The creator-linked [mirror-writing paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2117809/) describes alternating line directions in its Table 1 footnote. It does not choose a magazine unit, parity, overlay or key format. The existing T01 procedure already generated a fixed alternating-direction population and checked literal formats. This review asks a different question: **does an exact saved output contain a recognizable intermediate instruction?**

Read all **196 existing labels / 152 byte-distinct texts**, preserving the original whole-body versus page-control labels and all seven saved projections. The 152 strings contain **114,810 codepoints / 115,170 UTF8 bytes**. Exact duplicates are read once with every alias retained; their labels are not independent trials. Twelve private packets keep every text whole and unchanged, each below 10,000 text codepoints. No new cipher output, selector or format check is introduced.

## Procedure

1. Bind the original artifact and owning provenance to the [machine protocol](PROTOCOL.json). The lossless source inventory and copy were completed as disclosed preparation before public registration; semantic judgments start after root verifies the published registration commit.
2. Two separate AI contexts each read every complete unique string, including reversed-looking or nonword material. They retain packet/group coverage and exposure disclosures, without seeing each other's current judgments.
3. Recognize only a coherent second message or determinate next puzzle operation beyond ordinary article rhetoric or fragments. An obvious unspaced message may be recognized naturally; no edited candidate text is constructed. Missing letters, extra spaces, a fresh reversal, word filter, substring sweep or guessed second decoding layer are outside this review.
4. Keep any recognized lead and its exact existing source basis private for a separate later protocol. No key/checksum, scalar/seed/address, history or wallet operation follows from this review.
5. If neither reader recognizes a lead, report finite, subjective AI nonrecognition. This cannot exclude an encoded key, overlooked message, another reading or the puzzle.

The two AI contexts are separate judgments, not calibrated statistical evidence. Reader A has already read the original article and clues and seen some experiment filenames. Reader B receives the review task and packet labels without earlier solver conclusions. Both know they are reviewing puzzle readings; neither is blind to the general purpose.

## Reproduce the exact reading packet

From `public/research` in a checkout containing the registration commit:

```sh
task_private="$(mktemp -d /tmp/key404-t01-read.XXXXXX)"
python3 scripts/pack_t01_semantic_readings.py --self-test
python3 scripts/pack_t01_semantic_readings.py \
  --source analysis_outputs/continuation_20261110/batch20/T01/STREAMS.json \
  --out "$task_private/packets"
```

Python 3.9+ standard library. Keep outputs outside the entire checkout and public directories, with 0700 directories and 0600 files. The helper verifies the complete saved artifact hash and 196 ordered IDs, groups only identical UTF8 bytes, preserves every alias, and checks complete packet roundtrips. It executes none of the old extraction or validator code. Review instructions and model judgments are reproducible records, not a promise that another reader will make the same judgment.

[PLAN.json](PLAN.json) preserves the earlier private scope freeze. [INVENTORY.json](INVENTORY.json), [MAPPING.json](MAPPING.json), [copy preflight](PACKET_PREFLIGHT.json), and [helper hardening receipt](PACKAGER_HARDENING.json) bind the complete source population. A small output-path guard was hardened before publication; all 12 copied packets and the mapping were byte-identical afterward. The current helper is the pinned hardened version. No public raw packet duplicates are needed: the complete original strings remain in the linked T01 artifact and the helper reconstructs the same packets.

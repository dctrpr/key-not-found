# One case. Four ways in.

The [interactive investigation map](https://key404-casefile.vercel.app/#investigation) groups the public work into four readable branches. Choose a branch to inspect its exact methods, scoped results, limits and evidence, or choose every method. The [full ledger](https://key404-casefile.vercel.app/#ledger) sits directly under the map: it filters by status and searches every record. [`/#open-leads`](https://key404-casefile.vercel.app/#open-leads) lists the open and partial methods; `/#method-<id>` links one record by its ledger ID.

| Branch | Starting point | What remains useful |
| --- | --- | --- |
| Text & lines | Printed words, line edges, highlights and the George Sand clue | A source-motivated reading that differs meaningfully from a recorded test |
| Mirrors & layout | Physical leaves, reading direction and reflected marks | Repeatable trim-edge evidence on both faces, followed by a frozen registration test |
| Numbers & typography | Printed numbers and letterforms | Evidence for the selection rule, followed by a falsifiable extraction |
| Sources & provenance | Creator posts, article identity and authoritative originals | Public source evidence, provenance or a correction |

The branch membership lives in [`public/data/research-map.json`](public/data/research-map.json). The results live in [`public/research/experiments.json`](public/research/experiments.json). Dated findings live in [`public/data/updates.json`](public/data/updates.json); optional `methodIds` and `branchId` connect a finding to the map. One method appears in one branch; the map covers the full curated method catalog. It is not a count of every correlated candidate or every possible theory.

## How the live view changes

1. [Propose an experiment](https://github.com/dctrpr/key-not-found/issues/new?template=experiment.yml) or submit a pull request with public sources, exact steps, output and limitations.
2. Maintainers review the evidence and privacy, then merge an accepted method/result and a dated update to `main`.
3. The site's read-only `/api/research-state` endpoint resolves public `main` to one commit and reads the ledger, map and update log from that same immutable commit. Its CDN response is cached for five minutes and may briefly serve an older verified response while refreshing.
4. The visible page checks every five minutes while it is in use. It shows the source commit and check time. An unavailable sync keeps the last verified data, marked stale, or falls back to the deployed snapshot. A new issue or pull request is a proposal until reviewed; it is not automatically a published result.

The website layout, downloadable archives, file index and original source scans remain the deployed release snapshot until the next website deployment or archive release. The live research view does not imply that these downloads have changed. GitHub activity metrics are separate from research results and do not prove a key has been found.

## Status rules

- **Tested · no result** (a scoped negative): the recorded method/candidate set did not produce the sought result. The whole branch is not exhausted, and the label says nothing about work outside this record.
- **Claim invalidated / Corrected:** an audit or a source/code correction overturned an earlier claim. The earlier record stays visible with its correction.
- **Partial lead:** some evidence exists, with unresolved limits. It is not a solution.
- **Open question:** evidence or a test is still missing.
- **In progress:** only shown for an actually recorded active method, never implied by a recent website edit.

The case remains unsolved. No authenticated prize address or reproducible recovered key is established. The official token contract is published on the site; research participation does not require a token. See [CONTRIBUTING.md](CONTRIBUTING.md) for the publication format and [FUNDING.md](public/FUNDING.md) for the separate funding commitment.

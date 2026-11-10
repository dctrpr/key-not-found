# KEY NOT FOUND / $KEY404

The key is missing. The work is public.

My independent investigation into the Bitcoin Magazine puzzle Max Keiser described in 2023. The files, tests and updates are public; help is optional. The puzzle is **unsolved**. The claimed 20 BTC has not been independently authenticated. This project is not affiliated with Max Keiser, Bitcoin Magazine, or Pump.fun.

[Latest research](public/research/analysis_outputs/continuation_20261110/g02_shape_reachability/RESULT.md) found no registered literal shapes in the same-color or opposite-color stencil readings. Eight one-sided reading languages admit Base58 syntax in the broader model. A physical alignment check comes next.

## Start here

- [The film](https://keynotfound.com/#film): a 62-second explanation, with [reproducible source](scripts/explainer/README.md), captions and a transcript.
- [Visual lab and dated recap](https://keynotfound.com/#visual-lab): actual scans in page-board, layer-stack and mirror views; evidence-linked frames with SVG and scene-data exports.
- [Research corpus](public/research/README.md): scans, public clues, source register, historical reports, code, and exact test outputs.
- [Research map and live update flow](RESEARCH_MAP.md): four branches, linked notes, and the contribution-to-publication path.
- [Experiment register](public/research/experiments.json): scoped results and open leads.
- [Source-file manifest](public/research/files.json) and [SHA256SUMS](public/research/SHA256SUMS).
- [Funding plan](public/FUNDING.md): planned creator-fee-funded research and conditional BTC buybacks.
- [Contribution guide](CONTRIBUTING.md): reproducible experiments, corrections, and updates.
- [Discord research room](https://discord.gg/ZZK6DuADS): earlier shared files, leads, and discussion.
- [Update process and website log](public/UPDATES.md): how dated notes connect to evidence and GitHub history.

The website is a React/TypeScript app with two read-only public GitHub endpoints. The research map and notes sync periodically from a single public main-branch commit; a dated deployed snapshot remains available if syncing fails. A separate endpoint returns public repository counts and the latest three commit headlines, without author identities or email addresses. The guest chat loads in an explicitly opened third-party popup. The main site has no account database, wallet custody, hidden API keys, analytics, or private chat archive. The chat provider has its own privacy policy; its iframe loads only when a visitor opens chat.

## Want to help?

- **Reader:** inspect the original pages and exact printed lines.
- **Skeptic:** challenge a result with public evidence; corrections belong in the record.
- **Solver:** propose one falsifiable experiment and publish its exact steps and result.
- **Backer:** help fund research; follow the public expense and execution records.

Useful contributions stay linked to their public issue or pull request. Buying is not required to read, test, correct or contribute.

## Run locally

```sh
npm ci
npm run dev
npm run build
```

For the historical research environment, follow `public/research/REPRODUCE.md` from the corpus directory. Historical reports retain scoped limitations and corrections; the current register supersedes unsupported old conclusions.

## Update the investigation

1. Add a redacted, reproducible report under `public/research/analysis_outputs/` and any portable script under `public/research/scripts/`.
2. Add/update its method entry in `public/research/experiments.json`. Record the exact source unit, operation, expected output, outcome, and limitations.
3. Add a test-centered note with its actual `completedAtUTC` to `public/data/updates.json` and update `public/data/project.json`'s date.
4. Run `npm run research:manifest`, `npm run audit:public`, and `npm run build`.
5. Commit and push to `main` after review. GitHub checks audit and build every change. The map, method results and dated notes sync into the existing site periodically from that commit. Evidence links pin its GitHub revision. Deploy the reviewed commit for layout, funding configuration, scans, file-index or archive changes to publish those changes. Do not invent activity on days without new work.

## Token status

The token is **KEY NOT FOUND**, ticker **KEY404**, on Pump.fun/Solana.

Official contract: `7ux4vVTCkBAUdyEHB9axUyzKnbdCophQTGHTwYWMpump`

[View on Pump.fun](https://pump.fun/coin/7ux4vVTCkBAUdyEHB9axUyzKnbdCophQTGHTwYWMpump).

Creator fees actually received by the project fund AI agents, research runs and infrastructure, with receipts. The founder commits: if this project recovers the prize BTC, 100% will fund KEY404 buybacks, with public execution records. Prize existence and recovery remain unverified; the commitment is not automated. See the full funding plan.

## License

Original website code is MIT licensed. Third-party magazine scans, tweets, papers, and other source materials retain their respective rights. Original emblem artwork was generated for this project. See [source rights](public/research/DATA_LICENSE.md).

# KEY NOT FOUND / $KEY404

The key is missing. The work is public.

An independent, open investigation into the Bitcoin Magazine puzzle Max Keiser described in 2023. The puzzle is **unsolved**. The claimed 20 BTC has not been independently authenticated. This project is not affiliated with Max Keiser, Bitcoin Magazine, or Pump.fun.

## Start here

- [Research corpus](public/research/README.md): scans, public clues, source register, historical reports, code, and exact test outputs.
- [Experiment register](public/research/experiments.json): scoped results and open leads.
- [Source-file manifest](public/research/files.json) and [SHA256SUMS](public/research/SHA256SUMS).
- [Funding plan](public/FUNDING.md): planned creator-fee-funded research and conditional BTC buybacks.
- [Contribution guide](CONTRIBUTING.md): reproducible experiments, corrections, and updates.

The website is a static React/TypeScript app. It reads versioned JSON from the repository and public Nostr notes directly from relays. It has no account database, wallet custody, hidden API keys, analytics, or private chat archive.

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
3. Add an honest field note to `public/data/updates.json` and update `public/data/project.json`'s date.
4. Run `npm run research:manifest`, `npm run audit:public`, and `npm run build`.
5. Commit and push to `main`. GitHub checks audit and build every change. Deploy the reviewed commit to Vercel using the steps below. Do not invent activity on days without new work.

## Publish an update

Production: https://key404-casefile.vercel.app

The initial release uses the authenticated Vercel CLI. Automatic Git deployments are not configured: the Vercel account first needs its GitHub login connection linked by the account owner. After that connection is configured, connect this repository to the `key404-casefile` project with `main` as its production branch.

Until then, deploy the checked, clean commit from this directory:

```sh
vercel link --project key404-casefile
vercel deploy --prod --skip-domain
# Inspect and test the returned deployment URL before promotion.
vercel promote <deployment-url>
```

Confirm the intended team and project before deploying. Generated ZIPs are created from versioned inputs during each build; local build output, credentials and account metadata stay out of uploads and Git.

The `public/research` snapshot intentionally excludes private chat records, personal paths, credentials, unrelated puzzles, and unreviewed screenshots. All publication must pass the public-data audit. Project Git commits should use a project name and a GitHub noreply address.

## Token status

The proposed token is **KEY NOT FOUND**, ticker **KEY404**, on Pump.fun/Solana. No contract address or trading link is configured at release. The site must remain marked **not launched** until a real contract and official URL are reviewed and set in `public/data/project.json`.

Creator fees actually received by the project are intended to fund AI agents, research runs and infrastructure, with receipts. If the project actually recovers the claimed puzzle BTC, the stated intention is to use 100% of the recovered BTC for token buybacks, with transaction records. This is not an automatic mechanism or guaranteed outcome. See the full funding plan.

## Nostr discussion

The shared topic is `#keiser-key-not-found`. Anyone can read without connecting a signer. Posting requires an explicit NIP-07 signer connection and a separate sign/publish click. The page never asks for a secret key. Real relay acknowledgments determine publishing success; no fabricated chat messages are shown. A signed note proves authorship, not truth. Durable research findings should also be submitted as an issue or pull request.

## License

Original website code is MIT licensed. Third-party magazine scans, tweets, papers, and other source materials retain their respective rights. Original emblem artwork was generated for this project. See [source rights](public/research/DATA_LICENSE.md).

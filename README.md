# KEY NOT FOUND / $KEY404

The key is missing. The work is public.

An independent, open investigation into the Bitcoin Magazine puzzle Max Keiser described in 2023. The puzzle is **unsolved**. The claimed 20 BTC has not been independently authenticated. This project is not affiliated with Max Keiser, Bitcoin Magazine, or Pump.fun.

## Start here

- [Research corpus](public/research/README.md): scans, public clues, source register, historical reports, code, and exact test outputs.
- [Research map and live update flow](RESEARCH_MAP.md): four branches, linked notes, and the contribution-to-publication path.
- [Experiment register](public/research/experiments.json): scoped results and open leads.
- [Source-file manifest](public/research/files.json) and [SHA256SUMS](public/research/SHA256SUMS).
- [Funding plan](public/FUNDING.md): planned creator-fee-funded research and conditional BTC buybacks.
- [Contribution guide](CONTRIBUTING.md): reproducible experiments, corrections, and updates.
- [Discord research room](https://discord.gg/ZZK6DuADS): earlier shared files, leads, and discussion.
- [Update process and website log](public/UPDATES.md): how dated notes connect to evidence and GitHub history.

The website is a React/TypeScript app with two read-only public GitHub endpoints. The research map and notes sync periodically from a single public main-branch commit; a dated deployed snapshot remains available if syncing fails. A separate endpoint returns public repository counts and the latest three commit headlines, without author identities or email addresses. The guest chat loads in an explicitly opened third-party popup. The main site has no account database, wallet custody, hidden API keys, analytics, or private chat archive. The chat provider has its own privacy policy; its iframe loads only when a visitor opens chat.

## Find your role

- **Reader:** inspect the original pages and exact printed lines.
- **Skeptic:** challenge a result with public evidence; corrections belong in the record.
- **Solver:** propose one falsifiable experiment and publish its exact steps and result.
- **Backer, after launch:** help fund research; follow the public expense and execution records.

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
3. Add an honest field note to `public/data/updates.json` and update `public/data/project.json`'s date.
4. Run `npm run research:manifest`, `npm run audit:public`, and `npm run build`.
5. Commit and push to `main` after review. GitHub checks audit and build every change. The map, method results and dated notes sync into the existing site periodically from that commit. Evidence links pin its GitHub revision. Deploy the reviewed commit for layout, funding configuration, scans, file-index or archive changes using the steps below. Do not invent activity on days without new work.

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

Creator fees actually received by the project are intended to fund AI agents, research runs and infrastructure, with receipts. The founder commits: if this project recovers the prize BTC, 100% will fund KEY404 buybacks, with public execution records. Prize existence and recovery remain unverified; the commitment is not automated. See the full funding plan.

## Community

The earlier community research and discussion also live in [BTC is Toxic AF – Treasure Hunt on Discord](https://discord.gg/ZZK6DuADS). The site links this room from the introduction, community section, and footer. The invite is maintained in the `DISCORD` constant in `src/App.tsx`; update the documentation links at the same time if it changes. Source claims and durable results still need reproducible evidence in this repository. The supplied invite was verified on 9 November 2026 and currently expires on 9 December 2026; replace it when needed or supply a permanent invite.

A floating **Chat** button and the community button open the same public nickname-only room, hosted by [tlk.io](https://tlk.io/keiser-key-not-found). Visitors choose a 2–24-character alias in the popup; the provider loads only after they select **Enter chat**. The alias is held in page memory, not local storage, and is passed using tlk.io's documented custom-nickname option. No Nostr signer, wallet connection, or project account is required. Closing the popup removes the provider iframe. Visitors can also open the room in a new tab or use Discord if their browser blocks embeds.

The popup is for live conversation, not the research archive. The project has not claimed moderator ownership. According to the provider's [privacy policy](https://tlk.io/privacy), unmoderated messages expire after 10 minutes; the provider stores nicknames, IP addresses and messages and uses Google Analytics. A guest nickname does not prove authorship or anonymity. Keep durable findings and exact evidence on GitHub.

The room name is in `public/data/project.json`. The iframe allowlist is in `vercel.json`. Do not add automatic sign-in, guessed chat messages, visitor counters, or private keys to the site.

## License

Original website code is MIT licensed. Third-party magazine scans, tweets, papers, and other source materials retain their respective rights. Original emblem artwork was generated for this project. See [source rights](public/research/DATA_LICENSE.md).

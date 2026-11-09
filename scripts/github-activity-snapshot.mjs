import fs from "node:fs/promises";
import { readGitHubActivity } from "../lib/github-activity.mjs";

const snapshot = await readGitHubActivity();
await fs.writeFile(
  new URL("../public/data/github-activity.json", import.meta.url),
  `${JSON.stringify(snapshot, null, 2)}\n`,
);
console.log(
  `Public GitHub snapshot checked ${snapshot.checkedAt}: ${snapshot.counts.stars} stars, ${snapshot.counts.forks} forks, ${snapshot.counts.openItems} open issues/PRs.`,
);

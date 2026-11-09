import assert from "node:assert/strict";
import {
  readGitHubActivity,
  summarizeGitHubActivity,
  REPOSITORY_URL,
} from "../lib/github-activity.mjs";
import { GET } from "../api/github-activity.js";

const sha = "a".repeat(40);
const repo = {
  full_name: "dctrpr/key-not-found",
  private: false,
  stargazers_count: 0,
  forks_count: 2,
  open_issues_count: 3,
  pushed_at: "2026-11-09T22:19:12Z",
  owner: { email: "private@example.test" },
};
const commits = [
  {
    sha,
    html_url: `${REPOSITORY_URL}/commit/${sha}`,
    author: { login: "private-person" },
    commit: {
      message: "A public result\nPrivate discussion",
      committer: {
        date: "2026-11-09T22:19:12Z",
        email: "private@example.test",
      },
    },
  },
];
const summary = summarizeGitHubActivity(repo, commits, "2026-11-09T22:30:00Z");
assert.deepEqual(summary.counts, { stars: 0, forks: 2, openItems: 3 });
assert.equal(summary.commits[0].title, "A public result");
assert.equal(
  JSON.stringify(summary).includes("private"),
  false,
  "Raw identities and full commit bodies must not leave the mapper",
);
assert.throws(() =>
  summarizeGitHubActivity(
    { ...repo, private: true },
    commits,
    summary.checkedAt,
  ),
);
assert.throws(() =>
  summarizeGitHubActivity(
    { ...repo, forks_count: -1 },
    commits,
    summary.checkedAt,
  ),
);
assert.throws(() =>
  summarizeGitHubActivity(
    repo,
    [{ ...commits[0], html_url: "https://example.test" }],
    summary.checkedAt,
  ),
);
let calls = 0;
await assert.rejects(
  readGitHubActivity(async () => {
    calls++;
    return new Response("rate limited", { status: 403 });
  }),
);
assert.equal(calls, 2);
const originalFetch = globalThis.fetch;
try {
  globalThis.fetch = async (url) =>
    Response.json(String(url).includes("/commits?") ? commits : repo);
  const response = await GET(
    new Request("https://example.test/api/github-activity"),
  );
  assert.equal(response.status, 200);
  assert.match(
    response.headers.get("vercel-cdn-cache-control"),
    /s-maxage=900/,
  );
  assert.equal((await response.json()).counts.stars, 0);
  assert.equal(
    (
      await GET(
        new Request(
          "https://example.test/api/github-activity?repository=other",
        ),
      )
    ).status,
    400,
  );
  globalThis.fetch = async () => {
    throw new Error("network unavailable");
  };
  assert.equal(
    (await GET(new Request("https://example.test/api/github-activity"))).status,
    503,
  );
} finally {
  globalThis.fetch = originalFetch;
}
console.log(
  "GitHub activity whitelist, fixed-repository, cache, and outage checks passed.",
);

// Only public, project-level facts leave this module. Raw GitHub responses may
// include account profiles and commit email addresses; never publish them.
export const REPOSITORY = "dctrpr/key-not-found";
export const REPOSITORY_URL = `https://github.com/${REPOSITORY}`;
const API_URL = `https://api.github.com/repos/${REPOSITORY}`;

function count(value) {
  if (!Number.isSafeInteger(value) || value < 0)
    throw new Error("Invalid GitHub count");
  return value;
}

function timestamp(value) {
  if (typeof value !== "string" || !Number.isFinite(Date.parse(value)))
    throw new Error("Invalid GitHub timestamp");
  return new Date(value).toISOString();
}

export function summarizeGitHubActivity(repo, commits, checkedAt) {
  if (repo?.full_name !== REPOSITORY || repo.private !== false)
    throw new Error("Unexpected GitHub repository");
  if (!Array.isArray(commits)) throw new Error("Invalid GitHub commits");

  return {
    schemaVersion: 1,
    repository: REPOSITORY_URL,
    checkedAt: timestamp(checkedAt),
    counts: {
      stars: count(repo.stargazers_count),
      forks: count(repo.forks_count),
      // GitHub's open_issues_count includes both issues and pull requests.
      openItems: count(repo.open_issues_count),
    },
    lastPushedAt: timestamp(repo.pushed_at),
    commits: commits.slice(0, 3).map((entry) => {
      const sha = entry?.sha;
      if (typeof sha !== "string" || !/^[a-f0-9]{40}$/.test(sha))
        throw new Error("Invalid GitHub commit");
      if (entry.html_url !== `${REPOSITORY_URL}/commit/${sha}`)
        throw new Error("Unexpected GitHub commit URL");
      const message = entry.commit?.message;
      if (typeof message !== "string") throw new Error("Invalid commit title");
      return {
        sha,
        url: entry.html_url,
        date: timestamp(entry.commit?.committer?.date),
        title: message
          .split("\n")[0]
          .replace(/[\u0000-\u001f\u007f]/g, "")
          .trim()
          .slice(0, 160),
      };
    }),
  };
}

export async function readGitHubActivity(fetcher = fetch) {
  const headers = {
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "KEY404-public-research",
  };
  const responses = await Promise.all([
    fetcher(API_URL, { headers, signal: AbortSignal.timeout(5000) }),
    fetcher(`${API_URL}/commits?per_page=3`, {
      headers,
      signal: AbortSignal.timeout(5000),
    }),
  ]);
  for (const response of responses)
    if (!response.ok) throw new Error(`GitHub status ${response.status}`);
  const [repo, commits] = await Promise.all(
    responses.map((response) => response.json()),
  );
  return summarizeGitHubActivity(repo, commits, new Date().toISOString());
}

import { useEffect, useState } from "react";

export type GitHubActivity = {
  schemaVersion: 1;
  repository: string;
  checkedAt: string;
  counts: { stars: number; forks: number; openItems: number };
  lastPushedAt: string;
  commits: { sha: string; url: string; date: string; title: string }[];
};

type ActivityState = {
  data: GitHubActivity | null;
  mode: "loading" | "current" | "snapshot" | "unavailable";
  // checkedAt is when the upstream GitHub facts were read. refreshedAt is when
  // this browser finished checking the endpoint; a CDN hit can be older.
  refreshedAt: string | null;
  isStale: boolean;
};

const REPO = "https://github.com/dctrpr/key-not-found";

function validActivity(value: unknown): value is GitHubActivity {
  if (!value || typeof value !== "object") return false;
  const item = value as Partial<GitHubActivity>;
  const dateValid = (date: unknown) =>
    typeof date === "string" && Number.isFinite(Date.parse(date));
  return (
    item.schemaVersion === 1 &&
    item.repository === REPO &&
    dateValid(item.checkedAt) &&
    dateValid(item.lastPushedAt) &&
    !!item.counts &&
    Object.values(item.counts).length === 3 &&
    [item.counts.stars, item.counts.forks, item.counts.openItems].every(
      (n) => Number.isSafeInteger(n) && n >= 0,
    ) &&
    Array.isArray(item.commits) &&
    item.commits.length <= 3 &&
    item.commits.every(
      (commit) =>
        typeof commit.sha === "string" &&
        /^[a-f0-9]{40}$/.test(commit.sha) &&
        commit.url === `${REPO}/commit/${commit.sha}` &&
        dateValid(commit.date) &&
        typeof commit.title === "string" &&
        commit.title.length <= 160,
    )
  );
}

export function useGitHubActivity(): ActivityState {
  const [state, setState] = useState<ActivityState>({
    data: null,
    mode: "loading",
    refreshedAt: null,
    isStale: true,
  });

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    let pending = false;
    let lastAttempt = 0;
    let previous: GitHubActivity | null = null;

    const load = async (path: string) => {
      const response = await fetch(path, {
        signal: AbortSignal.any([controller.signal, AbortSignal.timeout(8000)]),
      });
      if (!response.ok) throw new Error("GitHub activity unavailable");
      const data: unknown = await response.json();
      if (!validActivity(data)) throw new Error("Invalid GitHub activity");
      return data;
    };

    const refresh = async () => {
      if (
        !active ||
        pending ||
        (lastAttempt && Date.now() - lastAttempt < 300_000)
      )
        return;
      pending = true;
      lastAttempt = Date.now();
      try {
        const data = await load("/api/github-activity");
        previous = data;
        if (active)
          setState({
            data,
            mode: "current",
            refreshedAt: new Date().toISOString(),
            isStale: Date.now() - Date.parse(data.checkedAt) > 1_800_000,
          });
      } catch {
        if (!active || controller.signal.aborted) return;
        try {
          const saved = await load("/data/github-activity.json");
          const data =
            previous &&
            Date.parse(previous.checkedAt) > Date.parse(saved.checkedAt)
              ? previous
              : saved;
          previous = data;
          if (active)
            setState({
              data,
              mode: "snapshot",
              refreshedAt: new Date().toISOString(),
              isStale: true,
            });
        } catch {
          if (active)
            setState({
              data: previous,
              mode: previous ? "snapshot" : "unavailable",
              refreshedAt: new Date().toISOString(),
              isStale: true,
            });
        }
      } finally {
        pending = false;
      }
    };
    const visibleRefresh = () => {
      if (document.visibilityState === "visible") void refresh();
    };
    void refresh();
    const interval = window.setInterval(visibleRefresh, 300_000);
    document.addEventListener("visibilitychange", visibleRefresh);

    return () => {
      active = false;
      controller.abort();
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", visibleRefresh);
    };
  }, []);

  return state;
}

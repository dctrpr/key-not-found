import {
  ArrowUpRight,
  GitCommitHorizontal,
  GitFork,
  Github,
  Star,
} from "lucide-react";
import { useGitHubActivity } from "../hooks/useGitHubActivity";
import "./RepositoryActivity.css";

const utcStamp = (value: string, withTime: boolean) =>
  new Date(value).toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    ...(withTime ? { hour: "2-digit", minute: "2-digit" } : {}),
    timeZone: "UTC",
  }) + (withTime ? " UTC" : "");

export default function RepositoryActivity({ repo }: { repo: string }) {
  const { data, mode, isStale } = useGitHubActivity();
  const checked = data ? utcStamp(data.checkedAt, true) : null;
  // A zero is not interest. Counts appear once they exist.
  const counts = data
    ? [
        {
          key: "stars",
          href: repo + "/stargazers",
          value: data.counts.stars,
          label: data.counts.stars === 1 ? "star" : "stars",
          Icon: Star,
        },
        {
          key: "forks",
          href: repo + "/forks",
          value: data.counts.forks,
          label: data.counts.forks === 1 ? "fork" : "forks",
          Icon: GitFork,
        },
        {
          key: "open",
          href: repo + "/issues",
          value: data.counts.openItems,
          label: "open issues + PRs",
          Icon: null,
        },
      ].filter((count) => count.value > 0)
    : [];
  return (
    <div className="repository-activity" aria-label="Public GitHub activity">
      <div className="repository-activity-top">
        <a href={repo} target="_blank" rel="noopener noreferrer">
          <Github size={18} /> THE PUBLIC RECORD <ArrowUpRight size={14} />
        </a>
        <span>
          {mode === "loading"
            ? "Checking GitHub…"
            : data
              ? `${mode === "snapshot" || isStale ? "Saved snapshot" : "Checked"} ${checked}`
              : "Live activity unavailable"}
        </span>
      </div>
      {data ? (
        <>
          {counts.length > 0 ? (
            <div className="repository-counts">
              {counts.map(({ key, href, value, label, Icon }) => (
                <a
                  href={href}
                  key={key}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {Icon ? <Icon size={14} /> : null}
                  {value} {label}
                  {Icon ? null : <ArrowUpRight size={12} />}
                </a>
              ))}
            </div>
          ) : (
            <p className="repository-quiet">
              No open proposals yet.{" "}
              <a
                href={repo + "/issues/new?template=experiment.yml"}
                target="_blank"
                rel="noopener noreferrer"
              >
                Propose the first test ↗
              </a>
            </p>
          )}
          <div className="repository-commits">
            {data.commits.map((commit) => (
              <a
                href={commit.url}
                key={commit.sha}
                target="_blank"
                rel="noopener noreferrer"
              >
                <GitCommitHorizontal size={16} />
                <span>{commit.title}</span>
                <time dateTime={commit.date}>
                  {utcStamp(commit.date, false)}
                </time>
                <code>{commit.sha.slice(0, 7)}</code>
                <ArrowUpRight size={14} />
              </a>
            ))}
          </div>
        </>
      ) : (
        <p>The repository is always open to inspect, fork, and improve.</p>
      )}
      <p className="repository-note">
        Commits, stars and forks show repository activity. Published tests and
        evidence show the research.
      </p>
    </div>
  );
}

import {
  ArrowUpRight,
  GitCommitHorizontal,
  GitFork,
  Github,
  Star,
} from "lucide-react";
import { useGitHubActivity } from "../hooks/useGitHubActivity";
import "./RepositoryActivity.css";

export default function RepositoryActivity({ repo }: { repo: string }) {
  const { data, mode, isStale } = useGitHubActivity();
  const checked = data
    ? new Date(data.checkedAt).toLocaleString("en-GB", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "UTC",
      }) + " UTC"
    : null;
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
          <div className="repository-counts">
            <a
              href={repo + "/stargazers"}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Star size={14} />
              {data.counts.stars} stars
            </a>
            <a href={repo + "/forks"} target="_blank" rel="noopener noreferrer">
              <GitFork size={14} />
              {data.counts.forks} forks
            </a>
            <a
              href={repo + "/issues"}
              target="_blank"
              rel="noopener noreferrer"
            >
              {data.counts.openItems} open issues + PRs{" "}
              <ArrowUpRight size={12} />
            </a>
          </div>
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
                <code>{commit.sha.slice(0, 7)}</code>
                <ArrowUpRight size={14} />
              </a>
            ))}
          </div>
        </>
      ) : (
        <p>The repository is always open to inspect, fork, and improve.</p>
      )}
      <p>
        Stars and forks show repository activity. Published tests and evidence
        show the research.
      </p>
    </div>
  );
}

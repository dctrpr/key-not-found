import { useState } from "react";
import {
  ArrowDown,
  ArrowUpRight,
  Check,
  GitBranch,
  ScanLine,
  Search,
  Type,
} from "lucide-react";
import "./ResearchMap.css";

type ResearchMethod = {
  id: string;
  title: string;
  status: string;
  scope: string;
  result: string;
};
type ResearchUpdate = {
  id: string;
  title: string;
  date: string;
  methodIds?: string[];
  branchId?: string;
};
type Branch = {
  id: string;
  title: string;
  description: string;
  methodIds: string[];
  nextAction?: string;
};
type Props = {
  branches: Branch[];
  methods: ResearchMethod[];
  updates: ResearchUpdate[];
  sourceCommit: string | null;
  checkedAt: string | null;
  status: "checking" | "verified" | "stale" | "snapshot";
  repo: string;
  onOpenMethod: (id: string) => void;
};
const isOpen = (status: string) =>
  ["partial", "untested", "open"].includes(status);
const statusLabel = (status: string) =>
  ({
    falsified: "Scoped negative",
    invalidated: "Corrected",
    tested: "Tested",
    partial: "Open / partial",
    untested: "Input needed",
    open: "Open question",
    "in-progress": "In progress",
    in_progress: "In progress",
  })[status] || status;
const icons = [Type, ScanLine, GitBranch, Search];

export default function ResearchMap({
  branches,
  methods,
  updates,
  sourceCommit,
  checkedAt,
  status,
  repo,
  onOpenMethod,
}: Props) {
  const [selectedId, setSelectedId] = useState("mirror-layout");
  const selected =
    branches.find((branch) => branch.id === selectedId) || branches[0];
  const branchMethods = selected
    ? selected.methodIds
        .map((id) => methods.find((method) => method.id === id))
        .filter((method): method is ResearchMethod => Boolean(method))
    : [];
  const related = selected
    ? updates.filter(
        (update) =>
          update.branchId === selected.id ||
          update.methodIds?.some((id) => selected.methodIds.includes(id)),
      )
    : [];
  const open = methods.filter((method) => isOpen(method.status)).length;
  const active = methods.filter((method) =>
    ["in-progress", "in_progress"].includes(method.status),
  ).length;
  const stamp = checkedAt
    ? new Date(checkedAt).toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "UTC",
      }) + " UTC"
    : null;

  return (
    <section
      className="investigation-section"
      id="investigation"
      aria-labelledby="investigation-title"
    >
      <div className="section investigation-inner">
        <div className="investigation-eyebrow">
          <span>THE INVESTIGATION</span>
          <span
            className={
              status === "verified" ? "sync-status verified" : "sync-status"
            }
          >
            {status === "verified" ? (
              <>
                <Check size={13} /> GitHub checked {stamp}
              </>
            ) : status === "checking" ? (
              "Checking GitHub…"
            ) : status === "stale" ? (
              "Last verified version · sync delayed"
            ) : (
              "Release snapshot · live sync unavailable"
            )}
          </span>
        </div>
        <div className="investigation-intro">
          <h2 id="investigation-title">
            One mystery.
            <br />
            <span>
              {branches.length === 4 ? "Four" : branches.length} ways in.
            </span>
          </h2>
          <p>
            Find a thread worth pulling. See the evidence, the dead ends, and
            what still needs work. Every accepted result becomes part of the
            case.
          </p>
        </div>
        <div
          className="investigation-summary"
          aria-label="Published research totals"
        >
          <span>
            <strong>{methods.length}</strong> method families
          </span>
          <span>
            <strong>{open}</strong> open / partial questions
          </span>
          <span>
            <strong>{active}</strong> active experiments logged
          </span>
        </div>
        <div
          className="branch-selector"
          role="group"
          aria-label="Choose a research branch"
        >
          {branches.map((branch, index) => {
            const Icon = icons[index % icons.length];
            const entries = methods.filter((method) =>
              branch.methodIds.includes(method.id),
            );
            const openCount = entries.filter((method) =>
              isOpen(method.status),
            ).length;
            return (
              <button
                key={branch.id}
                aria-pressed={selected?.id === branch.id}
                aria-controls="branch-detail"
                className={
                  selected?.id === branch.id
                    ? "branch-choice selected"
                    : "branch-choice"
                }
                onClick={() => setSelectedId(branch.id)}
              >
                <span className="branch-number">
                  0{index + 1}
                  <Icon size={19} />
                </span>
                <strong>{branch.title}</strong>
                <span>
                  {entries.length} methods ·{" "}
                  {openCount
                    ? `${openCount} open / partial`
                    : "scoped results recorded"}
                </span>
                <ArrowDown size={16} className="branch-arrow" />
              </button>
            );
          })}
        </div>
        {selected && (
          <div className="branch-detail" id="branch-detail">
            <div className="branch-context">
              <span className="map-label">FOLLOW THIS THREAD</span>
              <h3>{selected.title}</h3>
              <p>{selected.description}</p>
              <div className="branch-next">
                <span className="map-label">NEXT USEFUL MOVE</span>
                <p>{selected.nextAction}</p>
              </div>
              <a
                className="text-link"
                href={repo + "/issues/new?template=experiment.yml"}
                target="_blank"
                rel="noopener noreferrer"
              >
                Propose a test <ArrowUpRight size={16} />
              </a>
            </div>
            <div className="branch-results">
              {branchMethods.map((method) => (
                <button
                  key={method.id}
                  className="map-method"
                  onClick={() => onOpenMethod(method.id)}
                >
                  <span
                    className={
                      isOpen(method.status)
                        ? "map-method-status is-open"
                        : "map-method-status"
                    }
                  >
                    {statusLabel(method.status)}
                  </span>
                  <span>
                    <strong>{method.title}</strong>
                    <small>{method.result}</small>
                  </span>
                  <ArrowUpRight size={17} />
                </button>
              ))}
              {related.length > 0 && (
                <div className="branch-notes">
                  <span className="map-label">CONNECTED FIELD NOTES</span>
                  {related.map((update) => (
                    <a key={update.id} href={"#update-" + update.id}>
                      {update.title}
                      <ArrowDown size={14} />
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
        <div className="map-footer">
          <p>
            Accepted work on GitHub syncs here periodically. Downloads stay tied
            to their release. These paths are not a percentage solved.
          </p>
          <a
            href={
              repo +
              (sourceCommit
                ? "/tree/" + sourceCommit
                : "/blob/main/RESEARCH_MAP.md")
            }
            target="_blank"
            rel="noopener noreferrer"
          >
            {sourceCommit
              ? `Source ${sourceCommit.slice(0, 7)}`
              : "Read the research map on GitHub"}{" "}
            <ArrowUpRight size={14} />
          </a>
        </div>
      </div>
    </section>
  );
}

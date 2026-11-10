import { useEffect, useMemo, useState } from "react";
import {
  ArrowDown,
  ArrowUpRight,
  Check,
  ChevronDown,
  FileText,
  Link2,
  Search,
  X,
} from "lucide-react";
import type { ResearchSyncStatus } from "../hooks/useLiveResearch";
import { followHashLinks } from "../lib/hashLinks";
import {
  describeStatus,
  isOpenStatus,
  statusBucket,
  tallyStatuses,
  type StatusBucket,
} from "../lib/methodStatus";
import type {
  ResearchBranch,
  ResearchMethod,
  ResearchUpdate,
} from "../lib/researchState";
import "./ResearchMap.css";

type Props = {
  branches: ResearchBranch[] | null;
  methods: ResearchMethod[] | null;
  updates: ResearchUpdate[];
  sourceCommit: string | null;
  checkedAt: string | null;
  status: ResearchSyncStatus;
  repo: string;
  loadFailed: boolean;
  evidenceLink: (path: string, corpus?: boolean) => string;
};
type Filter = "all" | StatusBucket;

const NO_BRANCHES: ResearchBranch[] = [];
const NO_METHODS: ResearchMethod[] = [];
const WAYS = [
  "",
  "One way",
  "Two ways",
  "Three ways",
  "Four ways",
  "Five ways",
  "Six ways",
  "Seven ways",
  "Eight ways",
];
const FILTER_LABELS: Record<Filter, string> = {
  all: "All",
  tested: "Tested",
  open: "Open / partial",
  "in-progress": "In progress",
};

const calmScroll = (): ScrollBehavior =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ? "auto"
    : "smooth";

function Stamp({ method }: { method: ResearchMethod }) {
  const { tone, label } = describeStatus(method);
  return <span className={"stamp stamp-" + tone}>{label}</span>;
}

/** One square per recorded method. A picture of the record, not of progress. */
function Blocks({ methods }: { methods: ResearchMethod[] }) {
  return (
    <span className="blocks" aria-hidden="true">
      {methods.map((method) => (
        <i
          key={method.id}
          className={"block block-" + describeStatus(method).tone}
        />
      ))}
    </span>
  );
}

export default function ResearchMap({
  branches,
  methods,
  updates,
  sourceCommit,
  checkedAt,
  status,
  repo,
  loadFailed,
  evidenceLink,
}: Props) {
  const allBranches = branches ?? NO_BRANCHES;
  const allMethods = methods ?? NO_METHODS;
  const [chosenView, setChosenView] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("all");
  const [search, setSearch] = useState("");
  const [pendingMethod, setPendingMethod] = useState<string | null>(null);
  const [pendingLedger, setPendingLedger] = useState(false);

  const methodsOf = useMemo(() => {
    const byId = new Map(allMethods.map((method) => [method.id, method]));
    return (branch: ResearchBranch) =>
      branch.methodIds
        .map((id) => byId.get(id))
        .filter((method): method is ResearchMethod => Boolean(method));
  }, [allMethods]);

  // Open on the first branch that still has a lead to pull.
  const defaultView = useMemo(() => {
    const withLead = allBranches.find((branch) =>
      methodsOf(branch).some((method) => isOpenStatus(method.status)),
    );
    return (withLead || allBranches[0])?.id ?? "all";
  }, [allBranches, methodsOf]);

  const view = chosenView ?? defaultView;
  const query = search.trim().toLowerCase();
  const activeBranch = query
    ? undefined
    : allBranches.find((branch) => branch.id === view);
  const scopeMethods = useMemo(
    () => (activeBranch ? methodsOf(activeBranch) : allMethods),
    [activeBranch, allMethods, methodsOf],
  );
  const visible = useMemo(
    () =>
      scopeMethods.filter(
        (method) =>
          (filter === "all" || statusBucket(method.status) === filter) &&
          (!query ||
            [method.id, method.title, method.scope, method.result]
              .join(" ")
              .toLowerCase()
              .includes(query)),
      ),
    [scopeMethods, filter, query],
  );
  const countIn = (bucket: StatusBucket) =>
    scopeMethods.filter((method) => statusBucket(method.status) === bucket)
      .length;
  const filters: Filter[] = ["all", "tested", "open"];
  if (countIn("in-progress") > 0 || filter === "in-progress")
    filters.push("in-progress");
  const related = activeBranch
    ? updates.filter(
        (update) =>
          update.branchId === activeBranch.id ||
          update.methodIds?.some((id) => activeBranch.methodIds.includes(id)),
      )
    : [];

  // #method-<id> opens one record in its branch; #open-leads lists what is left.
  // Both are re-applied when a link repeats the hash already in the address
  // bar, because the visitor may have changed the branch or filter since.
  useEffect(
    () =>
      followHashLinks((hash) => {
        const method = /^#method-([a-z0-9-]+)$/.exec(hash);
        // Any other destination replaces or cancels a record still waiting.
        setPendingMethod(method ? method[1] : null);
        if (hash === "#open-leads") {
          setChosenView("all");
          setFilter("open");
          setSearch("");
          setPendingLedger(true);
        }
      }),
    [],
  );

  // Resolve a linked record when the data that contains it is here: show its
  // branch, clear any filter that would hide it, then open it and move focus
  // to it. The deployed snapshot is not the last word. A record merged after
  // this deployment arrives with the live sync, so an ID that is not in the
  // current data keeps waiting until it appears or the visitor goes elsewhere.
  useEffect(() => {
    if (!pendingMethod) return;
    if (!allMethods.some((method) => method.id === pendingMethod)) return;
    const home = allBranches.find((branch) =>
      branch.methodIds.includes(pendingMethod),
    );
    const wanted = home ? home.id : "all";
    if (view !== wanted || filter !== "all" || search) {
      setChosenView(wanted);
      setFilter("all");
      setSearch("");
      return;
    }
    const target = document.getElementById("method-" + pendingMethod);
    if (target instanceof HTMLDetailsElement) {
      target.open = true;
      target.scrollIntoView({ behavior: calmScroll(), block: "start" });
      target.querySelector("summary")?.focus({ preventScroll: true });
    }
    setPendingMethod(null);
  }, [pendingMethod, allMethods, allBranches, view, filter, search]);

  // The list above the rows changes height with the view, so scroll after it.
  useEffect(() => {
    if (!pendingLedger) return;
    document
      .getElementById("ledger")
      ?.scrollIntoView({ behavior: calmScroll(), block: "start" });
    setPendingLedger(false);
  }, [pendingLedger]);

  const stamp = checkedAt
    ? new Date(checkedAt).toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "UTC",
      }) + " UTC"
    : null;
  const issueUrl = (template: string, title: string) =>
    `${repo}/issues/new?template=${template}.yml&title=${encodeURIComponent(title)}`;
  const choose = (next: string) => {
    setChosenView(next);
    setSearch("");
  };
  const reset = () => {
    setChosenView("all");
    setFilter("all");
    setSearch("");
  };
  const countLine = query
    ? `${visible.length} of ${allMethods.length} methods match “${search.trim()}”`
    : activeBranch
      ? `${visible.length} of ${scopeMethods.length} methods in ${activeBranch.title}`
      : `${visible.length} of ${allMethods.length} methods`;

  return (
    <section
      className="investigation"
      id="investigation"
      aria-labelledby="investigation-title"
    >
      <div className="section">
        <div className="section-label">
          <span>02</span>
          <span>THE INVESTIGATION</span>
          <i />
          <span
            className={
              status === "verified" ? "sync-status verified" : "sync-status"
            }
          >
            {status === "verified" ? (
              <>
                <Check size={14} aria-hidden="true" /> GitHub checked {stamp}
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
        <div className="section-intro">
          <h2 id="investigation-title">
            One mystery.
            <br />
            <span>
              {allBranches.length
                ? (WAYS[allBranches.length] || allBranches.length + " ways") +
                  " in."
                : "Every recorded method."}
            </span>
          </h2>
          <p>
            I haven’t found the key. Every recorded attempt is here: what it
            covered, what it found, and what it could not rule out.
          </p>
        </div>

        {allBranches.length > 0 && allMethods.length > 0 && (
          <div
            className="branch-grid"
            role="group"
            aria-label="Choose a research branch"
          >
            {allBranches.map((branch, index) => {
              const entries = methodsOf(branch);
              const selected = activeBranch?.id === branch.id;
              return (
                <button
                  key={branch.id}
                  type="button"
                  className={selected ? "branch is-selected" : "branch"}
                  aria-pressed={selected}
                  aria-controls="ledger"
                  onClick={() => choose(branch.id)}
                >
                  <span className="branch-index">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <strong>{branch.title}</strong>
                  <Blocks methods={entries} />
                  <span className="branch-tally">
                    {entries.length} {entries.length === 1 ? "method" : "methods"}{" "}
                    · {tallyStatuses(entries)}
                  </span>
                </button>
              );
            })}
            <button
              type="button"
              className={
                !activeBranch ? "branch branch-all is-selected" : "branch branch-all"
              }
              aria-pressed={!activeBranch}
              aria-controls="ledger"
              onClick={() => choose("all")}
            >
              <span className="branch-index">ALL</span>
              <strong>Every method</strong>
              <Blocks methods={allMethods} />
              <span className="branch-tally">
                {allMethods.length} on the record · searchable
              </span>
            </button>
          </div>
        )}

        <div className="ledger" id="ledger">
          <span id="open-leads" className="anchor" aria-hidden="true" />
          {activeBranch && (
            <div className="branch-brief">
              <div>
                <span className="map-label">THE THREAD</span>
                <h3>{activeBranch.title}</h3>
                <p>{activeBranch.description}</p>
              </div>
              <div>
                <span className="map-label">NEXT USEFUL MOVE</span>
                <p>
                  {activeBranch.nextAction ||
                    "Read the recorded scope and limits before proposing a different test."}
                </p>
                <a
                  className="text-link"
                  href={issueUrl(
                    "experiment",
                    "[Experiment] " + activeBranch.title + ": ",
                  )}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Propose a test <ArrowUpRight size={16} />
                </a>
              </div>
              {related.length > 0 && (
                <div className="brief-notes">
                  <span className="map-label">DATED NOTES</span>
                  {related.map((update) => (
                    <a key={update.id} href={"#update-" + update.id}>
                      <span>{update.title}</span>
                      <ArrowDown size={14} />
                    </a>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="ledger-toolbar">
            <div
              className="filter-tabs"
              role="group"
              aria-label="Filter methods by status"
            >
              {filters.map((value) => (
                <button
                  key={value}
                  type="button"
                  className={filter === value ? "active" : ""}
                  aria-pressed={filter === value}
                  onClick={() => setFilter(value)}
                >
                  {FILTER_LABELS[value]}{" "}
                  <span>
                    {value === "all" ? scopeMethods.length : countIn(value)}
                  </span>
                </button>
              ))}
            </div>
            <label className="search-field">
              <Search size={16} aria-hidden="true" />
              <input
                placeholder="Search all methods…"
                aria-label="Search all research methods"
                value={search}
                onChange={(event) => {
                  // A search covers every method and every status.
                  setSearch(event.target.value);
                  if (event.target.value.trim()) setFilter("all");
                }}
              />
              {search && (
                <button
                  type="button"
                  aria-label="Clear search"
                  onClick={() => setSearch("")}
                >
                  <X size={15} />
                </button>
              )}
            </label>
          </div>
          <p className="ledger-count" aria-live="polite">
            {allMethods.length ? countLine : ""}
          </p>

          <div className="method-list">
            {visible.map((method) => {
              const notes = updates.filter((update) =>
                update.methodIds?.includes(method.id),
              );
              return (
                <details
                  className="method-row"
                  key={method.id}
                  id={"method-" + method.id}
                >
                  <summary>
                    <span className="method-status">
                      <Stamp method={method} />
                    </span>
                    <code className="method-id">{method.id}</code>
                    <h3>{method.title}</h3>
                    <span className="method-result">{method.result}</span>
                    <span className="method-toggle" aria-hidden="true">
                      <ChevronDown size={19} />
                    </span>
                  </summary>
                  <div className="method-detail">
                    <div>
                      <h4>Declared scope</h4>
                      <p>{method.scope}</p>
                      {method.limitations?.length ? (
                        <>
                          <h4>Limits</h4>
                          <ul>
                            {method.limitations.map((limit) => (
                              <li key={limit}>{limit}</li>
                            ))}
                          </ul>
                        </>
                      ) : null}
                      {notes.length > 0 && (
                        <>
                          <h4>Dated notes</h4>
                          {notes.map((update) => (
                            <a
                              className="evidence-link"
                              key={update.id}
                              href={"#update-" + update.id}
                            >
                              <ArrowDown size={14} />
                              <span>{update.title}</span>
                            </a>
                          ))}
                        </>
                      )}
                    </div>
                    <div>
                      <h4>Evidence &amp; reproduction</h4>
                      {method.evidence.map((path) => (
                        <a
                          className="evidence-link"
                          key={path}
                          href={evidenceLink(path, true)}
                          title={path}
                        >
                          <FileText size={14} />
                          <span>{path.split("/").pop()}</span>
                          <ArrowUpRight size={14} />
                        </a>
                      ))}
                      {method.reproduce?.length ? (
                        <pre>{method.reproduce.join("\n")}</pre>
                      ) : (
                        <p>
                          Review the linked source before proposing a new test.
                        </p>
                      )}
                      <div className="method-actions">
                        <a
                          href={issueUrl(
                            "experiment",
                            "[Experiment] " + method.id + ": ",
                          )}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Propose a test <ArrowUpRight size={14} />
                        </a>
                        <a
                          href={issueUrl(
                            "correction",
                            "[Correction] " + method.id + ": ",
                          )}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          Challenge this record <ArrowUpRight size={14} />
                        </a>
                        <a href={"#method-" + method.id}>
                          <Link2 size={14} /> Link to this record
                        </a>
                      </div>
                    </div>
                  </div>
                </details>
              );
            })}
            {!visible.length && (
              <div className="empty-state">
                {!methods ? (
                  loadFailed ? (
                    <>
                      The ledger could not load.{" "}
                      <a href={repo} target="_blank" rel="noopener noreferrer">
                        Browse the repository ↗
                      </a>
                    </>
                  ) : (
                    "Loading the research ledger…"
                  )
                ) : (
                  <>
                    No methods match this view.{" "}
                    <button type="button" onClick={reset}>
                      Show every method
                    </button>
                  </>
                )}
              </div>
            )}
          </div>

          <div className="ledger-bottom">
            <p>
              <strong>An empty result is still a result.</strong> “No result”
              covers only the declared candidates. It does not close the wider
              idea, and it says nothing about what anyone else has found.
            </p>
            <a
              href={issueUrl("experiment", "[Experiment] ")}
              className="text-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              Propose the next experiment <ArrowUpRight size={16} />
            </a>
          </div>
        </div>

        <div className="route-block">
          <span className="map-label">HOW AN IDEA BECOMES A RESULT</span>
          <ol className="route">
            <li>
              <span className="route-step">Propose</span>
              <p>One source, one rule, one way to be wrong.</p>
              <a
                href={issueUrl("experiment", "[Experiment] ")}
                target="_blank"
                rel="noopener noreferrer"
              >
                Experiment template <ArrowUpRight size={14} />
              </a>
            </li>
            <li>
              <span className="route-step">Test</span>
              <p>Fix the rule before looking. Keep the code, output and limits.</p>
              <a
                href={repo + "/blob/main/CONTRIBUTING.md"}
                target="_blank"
                rel="noopener noreferrer"
              >
                Contribution format <ArrowUpRight size={14} />
              </a>
            </li>
            <li>
              <span className="route-step">Review</span>
              <p>I review the source, reproduction and privacy before merging.</p>
              <a
                href={repo + "/pulls"}
                target="_blank"
                rel="noopener noreferrer"
              >
                Pull requests <ArrowUpRight size={14} />
              </a>
            </li>
            <li>
              <span className="route-step">Published</span>
              <p>The map and log sync from that commit, with a dated note.</p>
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
                  ? "Source " + sourceCommit.slice(0, 7)
                  : "Read the research map on GitHub"}{" "}
                <ArrowUpRight size={14} />
              </a>
            </li>
          </ol>
          <p className="route-note">
            A new issue or pull request is a proposal until it is reviewed.
            Accepted work on GitHub syncs here periodically; downloads stay tied
            to their release. These paths are not a percentage solved.
          </p>
        </div>
      </div>
    </section>
  );
}

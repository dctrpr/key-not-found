import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Copy,
  ExternalLink,
  FileCode2,
  FileText,
  FolderOpen,
  Github,
  KeyRound,
  LockKeyhole,
  Menu,
  MessageCircle,
  Search,
  X,
} from "lucide-react";
import NostrRoom from "./components/NostrRoom";

type Method = {
  id: string;
  title: string;
  status: string;
  kind?: string;
  scope: string;
  result: string;
  evidence: string[];
  reproduce: string[];
  limitations?: string[];
};
type FileEntry = {
  path: string;
  category: string;
  mediaType: string;
  bytes: number;
  sha256: string;
  description?: string;
};
type FileIndex = {
  files: FileEntry[];
  totals: { files: number; bytes: number };
};
type Update = {
  id: string;
  date: string;
  category: string;
  title: string;
  body: string;
  evidence: string;
};
type Project = {
  repository: string;
  updatedOn: string;
  nostrTag: string;
  token: { status: string; contract: string | null; url: string | null };
  funding?: {
    receipts: {
      date: string;
      description: string;
      amount: number;
      currency: string;
      evidence: string;
    }[];
  };
};

const REPO = "https://github.com/dctrpr/key-not-found";
const DISCORD = "https://discord.gg/ZZK6DuADS";
const ARCHIVE = "/downloads/key404-casefile.zip";
const researchPath = (path: string) =>
  "/research/" + path.split("/").map(encodeURIComponent).join("/");
const formatBytes = (bytes: number) =>
  bytes < 1024
    ? bytes + " B"
    : bytes < 1048576
      ? (bytes / 1024).toFixed(0) + " KB"
      : (bytes / 1048576).toFixed(1) + " MB";
const dateLabel = (date: string) =>
  new Date(date + "T12:00:00Z").toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });

function useJson<T>(path: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    fetch(path, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Unavailable");
        return response.json() as Promise<T>;
      })
      .then(setData)
      .catch((error) => {
        if (error.name !== "AbortError") setError(true);
      });
    return () => controller.abort();
  }, [path]);
  return { data, error };
}

function SectionLabel({
  index,
  children,
  dark = false,
}: {
  index: string;
  children: React.ReactNode;
  dark?: boolean;
}) {
  return (
    <div className={"section-label" + (dark ? " on-dark" : "")}>
      <span>{index}</span>
      <span>{children}</span>
      <i />
    </div>
  );
}

function App() {
  const project = useJson<Project>("/data/project.json");
  const updates = useJson<{ updates: Update[] }>("/data/updates.json");
  const ledger = useJson<{ methods: Method[] }>("/research/experiments.json");
  const files = useJson<FileIndex>("/research/files.json");
  const [menuOpen, setMenuOpen] = useState(false);
  const [ledgerFilter, setLedgerFilter] = useState("all");
  const [ledgerSearch, setLedgerSearch] = useState("");
  const [fileSearch, setFileSearch] = useState("");
  const [fileFilter, setFileFilter] = useState("all");
  const [fileLimit, setFileLimit] = useState(16);
  const [toast, setToast] = useState("");
  const [selectedPage, setSelectedPage] = useState<number | null>(null);
  const [activeUpdate, setActiveUpdate] = useState(0);
  const dialog = useRef<HTMLDialogElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const repo = project.data?.repository || REPO;
  const latest = updates.data?.updates[activeUpdate];
  const tokenLive =
    project.data?.token.status === "live" &&
    Boolean(project.data.token.contract && project.data.token.url);

  useEffect(() => {
    if (!toast) return;
    const timeout = setTimeout(() => setToast(""), 3200);
    return () => clearTimeout(timeout);
  }, [toast]);
  useEffect(() => {
    if (selectedPage !== null && !dialog.current?.open)
      dialog.current?.showModal();
    if (selectedPage === null && dialog.current?.open) dialog.current.close();
  }, [selectedPage]);
  useEffect(() => {
    const handle = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        document
          .getElementById("files")
          ?.scrollIntoView({ behavior: "smooth" });
        fileInput.current?.focus({ preventScroll: true });
      }
      if (selectedPage !== null && event.key === "ArrowRight")
        setSelectedPage((page) =>
          page === null ? 73 : Math.min(80, page + 1),
        );
      if (selectedPage !== null && event.key === "ArrowLeft")
        setSelectedPage((page) =>
          page === null ? 73 : Math.max(73, page - 1),
        );
    };
    document.addEventListener("keydown", handle);
    return () => document.removeEventListener("keydown", handle);
  }, [selectedPage]);

  async function copy(text: string, success: string) {
    try {
      await navigator.clipboard.writeText(text);
      setToast(success);
    } catch {
      setToast("Clipboard unavailable. Select and copy the text below.");
    }
  }
  const prompt = `Investigate the public Max Keiser magazine puzzle using the source corpus at ${typeof window === "undefined" ? "" : window.location.origin}/research/README.md. Start with sources/creator-clues.json, sources/printed-lines.json, experiments.json and SHA256SUMS. The puzzle is unsolved; no authenticated prize address is known. Review corrected historical claims before choosing one untested, source-motivated hypothesis. Declare source unit, traversal, operation, expected output and falsification criterion. Preserve exact intermediate data and reproducible commands. Distinguish facts, hypotheses and scoped negative results. Do not send transactions, import wallets or contact people. Submit a concise finding and evidence through ${repo}/issues.`;
  const methods = useMemo(
    () =>
      (ledger.data?.methods || []).filter((method) => {
        const query = ledgerSearch.toLowerCase();
        const status = method.status.toLowerCase();
        const matches =
          ledgerFilter === "all" ||
          (ledgerFilter === "tested"
            ? ["falsified", "tested", "invalidated"].includes(status)
            : ledgerFilter === "open"
              ? ["untested", "partial", "open"].includes(status)
              : ["in-progress", "in_progress"].includes(status));
        return (
          matches &&
          (method.title + " " + method.scope + " " + method.result)
            .toLowerCase()
            .includes(query)
        );
      }),
    [ledger.data, ledgerSearch, ledgerFilter],
  );
  const visibleFiles = useMemo(
    () =>
      (files.data?.files || []).filter((file) => {
        const category = file.category.toLowerCase();
        const matches =
          fileFilter === "all" ||
          (fileFilter === "code"
            ? /code|script/.test(category) ||
              /\.(py|js|ts|html)$/.test(file.path)
            : fileFilter === "sources"
              ? /source|clue/.test(category) || file.path.startsWith("sources/")
              : /report|analysis|result|data/.test(category));
        return (
          matches &&
          (file.path + " " + file.description)
            .toLowerCase()
            .includes(fileSearch.toLowerCase())
        );
      }),
    [files.data, fileSearch, fileFilter],
  );

  return (
    <>
      <a className="skip-link" href="#case">
        Skip to the case
      </a>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Key Not Found home">
          <span className="brand-mark">
            <KeyRound size={21} strokeWidth={2.4} />
          </span>
          <span>
            KEY<span className="brand-slash">/</span>404
          </span>
        </a>
        <nav
          aria-label="Main navigation"
          className={menuOpen ? "nav-open" : ""}
        >
          {["Case", "Updates", "Ledger", "Files", "Community"].map((label) => (
            <a
              href={"#" + label.toLowerCase()}
              key={label}
              onClick={() => setMenuOpen(false)}
            >
              {label}
            </a>
          ))}
        </nav>
        <a
          className="header-github"
          href={repo}
          target="_blank"
          rel="noopener noreferrer"
        >
          <Github size={16} />
          <span>Open source</span>
          <ArrowUpRight size={15} />
        </a>
        <button
          className="menu-toggle"
          aria-expanded={menuOpen}
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <X /> : <Menu />}
        </button>
      </header>

      <main>
        <section className="hero" id="top">
          <div className="hero-grid" aria-hidden="true" />
          <div className="hero-topline">
            <span>
              <i className="live-dot" /> CASE FILE 001 · UNSOLVED
            </span>
            <span>INDEPENDENT / OPEN / ONGOING</span>
          </div>
          <div className="hero-main">
            <div className="hero-copy">
              <p className="hero-kicker">ONE MAGAZINE. A CLAIMED 20 BTC.</p>
              <h1>
                KEY NOT
                <br />
                <span>
                  FOUND<span className="hero-period">.</span>
                </span>
              </h1>
              <p className="hero-deck">
                The key is missing.
                <br />
                The work is public.
              </p>
              <p className="hero-description founder-story">
                <span>I found Max Keiser’s puzzle in 2023.</span>
                <span>I’ve been working on it ever since.</span>
                <strong>Now, let’s find the key together.</strong>
              </p>
              <div className="hero-actions">
                <a className="button button-lime" href="#case">
                  Open the case <ArrowDown size={17} />
                </a>
                <a
                  className="text-link light hero-discord"
                  href={DISCORD}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Join the Discord <ArrowUpRight size={16} />
                </a>
              </div>
            </div>
            <div className="hero-visual">
              <span className="visual-corner top-left">EXHIBIT 01</span>
              <span className="visual-corner top-right">[ THE SOURCE ]</span>
              <button
                className="hero-exhibit"
                onClick={() => setSelectedPage(73)}
                aria-label="Inspect printed page 73"
              >
                <img
                  src="/research/sources/pages/73.jpg"
                  alt="The original OVERDOSE opening page from Bitcoin Magazine, with pills and a dollar bill"
                  width="2544"
                  height="3264"
                  fetchPriority="high"
                />
                <span className="exhibit-hint">
                  Inspect the original <ArrowUpRight size={13} />
                </span>
              </button>
              <div className="visual-caption">
                <span>
                  ONE MAGAZINE.
                  <br />
                  ONE UNFINISHED QUESTION.
                </span>
                <img
                  className="project-seal"
                  src="/assets/key404-emblem.png"
                  alt="KEY404 project emblem"
                  width="100"
                  height="100"
                />
              </div>
            </div>
          </div>
          <div className="hero-bottom">
            <div>
              <span className="mono">THE CLAIM</span>
              <span className="hero-stat">20 BTC</span>
            </div>
            <div>
              <span className="mono">ATTRIBUTED TO</span>
              <span className="hero-stat">MAX KEISER</span>
            </div>
            <div>
              <span className="mono">REWARD STATUS</span>
              <span className="hero-stat lime-text">UNVERIFIED</span>
            </div>
            <a href="#updates">
              <span>LATEST FIELD NOTE</span>
              <strong>
                {project.data
                  ? dateLabel(project.data.updatedOn).toUpperCase()
                  : "09 NOV 2026"}{" "}
                <ArrowDownRight />
              </strong>
            </a>
          </div>
        </section>

        <div className="running-strip" aria-hidden="true">
          <span>FOLLOW THE CLUES</span>
          <span>✳</span>
          <span>REPRODUCE THE WORK</span>
          <span>✳</span>
          <span>BREAK OUR ASSUMPTIONS</span>
          <span>✳</span>
          <span>FIND THE KEY</span>
          <span>✳</span>
          <span>FOLLOW THE CLUES</span>
          <span>✳</span>
        </div>

        <section className="section case-section" id="case">
          <SectionLabel index="01">THE CASE</SectionLabel>
          <div className="section-intro">
            <h2>
              A fortune in the margins.
              <br />
              <span>Or a mystery with no answer.</span>
            </h2>
            <p>
              The claim is real. The reward has not been independently verified.
              Start with what Keiser actually posted, then inspect the pages
              yourself.
            </p>
          </div>
          <div className="case-layout">
            <div className="clues">
              <a
                className="clue"
                href="https://x.com/maxkeiser/status/1632068898169450497"
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className="clue-meta">
                  <span>04 MAR 2023</span>
                  <span className="pill">THE 20 BTC CLAIM</span>
                  <ArrowUpRight size={20} />
                </div>
                <h3>One article. Twenty bitcoin.</h3>
                <img
                  className="announcement-photo"
                  src="/research/sources/announcement.jpg"
                  alt="Public announcement photograph of Max Keiser holding the OVERDOSE magazine spread with President Bukele"
                  loading="lazy"
                />
                <blockquote>
                  “I hid a private Bitcoin key encoded in this piece…”
                </blockquote>
                <p>
                  The photograph shows the El Salvador Issue. No authenticated
                  funding address or key format was published with the
                  announcement.
                </p>
                <span className="clue-source">
                  View original post <ExternalLink size={12} />
                </span>
              </a>
              <a
                className="clue"
                href="https://x.com/maxkeiser/status/1607378060172460032"
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className="clue-meta">
                  <span>26 DEC 2022</span>
                  <span className="pill">CREATOR POST</span>
                  <ArrowUpRight size={20} />
                </div>
                <h3>Hidden in the text.</h3>
                <blockquote>
                  “Like George Sand’s hidden cryptography, I have hidden private
                  keys in the text.”
                </blockquote>
                <p>
                  The linked examples read alternate printed lines, or the first
                  word of every line. The post refers to multiple keys and
                  doesn’t name an issue.
                </p>
                <span className="clue-source">
                  View original post <ExternalLink size={12} />
                </span>
              </a>
              <a
                className="clue"
                href="https://x.com/maxkeiser/status/1632391507008278528"
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className="clue-meta">
                  <span>05 MAR 2023</span>
                  <span className="pill">MIRROR WRITING</span>
                  <ArrowUpRight size={20} />
                </div>
                <h3>Read it another way.</h3>
                <blockquote>
                  “Mirror writing: neurological reflections on an unusual
                  phenomenon.”
                </blockquote>
                <p>
                  A link to Schott’s paper on reversed letters and reading
                  direction. A clue to explore, not proof of a particular
                  page-folding method.
                </p>
                <span className="clue-source">
                  View original post <ExternalLink size={12} />
                </span>
              </a>
            </div>
            <div className="source-viewer">
              <div className="viewer-top">
                <span>BITCOIN MAGAZINE / ISSUE 24</span>
                <button
                  onClick={() => setSelectedPage(75)}
                  aria-label="Open the source page viewer"
                >
                  <ArrowUpRight size={18} />
                </button>
              </div>
              <button
                className="scan-preview"
                onClick={() => setSelectedPage(75)}
              >
                <img
                  src="/research/sources/pages/75.jpg"
                  alt="Scanned printed page 75, Bitcoin Is Toxic AF, with orange and black highlights"
                  loading="lazy"
                />
                <span>INSPECT THE ORIGINAL ↗</span>
              </button>
              <div className="page-picker" aria-label="Magazine pages">
                {Array.from({ length: 8 }, (_, i) => i + 73).map((page) => (
                  <button
                    key={page}
                    onClick={() => setSelectedPage(page)}
                    aria-label={"View printed page " + page}
                  >
                    {page}
                  </button>
                ))}
              </div>
              <p>
                Eight source pages. Original wording. Visible line breaks.
                Download both PDF witnesses in the archive.
              </p>
            </div>
          </div>
          <div className="case-footnote">
            <LockKeyhole size={18} />
            <p>
              <strong>Keep the uncertainty visible.</strong> A later “El
              Salvador” statement is authentic, but its deleted parent post
              leaves the puzzle connection unverified. We label source facts,
              hypotheses, and failed tests separately.
            </p>
            <a href="/research/sources/creator-clues.json">
              Source register <ArrowUpRight size={16} />
            </a>
          </div>
        </section>

        <section className="updates-section" id="updates">
          <div className="section updates-inner">
            <SectionLabel index="02" dark>
              FIELD NOTES
            </SectionLabel>
            <div className="updates-layout">
              <div>
                <h2>
                  The daily log.
                  <br />
                  <span>Including the dead ends.</span>
                </h2>
                <p>
                  What changed. What failed. What the next person should know.
                </p>
                <a
                  className="text-link light"
                  href={repo + "/commits/main"}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Follow the commit history <ArrowUpRight size={17} />
                </a>
              </div>
              <div className="update-panel">
                {latest ? (
                  <>
                    <div className="update-kicker">
                      <span>
                        <i className="live-dot" /> {latest.category}
                      </span>
                      <time>{dateLabel(latest.date)}</time>
                    </div>
                    <h3>{latest.title}</h3>
                    <p>{latest.body}</p>
                    <a className="text-link light" href={latest.evidence}>
                      Read the findings <ArrowUpRight size={16} />
                    </a>
                    <div className="update-pagination">
                      <span>
                        {String(activeUpdate + 1).padStart(2, "0")} /{" "}
                        {String(updates.data?.updates.length).padStart(2, "0")}
                      </span>
                      <div>
                        <button
                          aria-label="Previous update"
                          onClick={() =>
                            setActiveUpdate(
                              (index) =>
                                (index +
                                  (updates.data?.updates.length || 1) -
                                  1) %
                                (updates.data?.updates.length || 1),
                            )
                          }
                        >
                          <ChevronLeft size={19} />
                        </button>
                        <button
                          aria-label="Next update"
                          onClick={() =>
                            setActiveUpdate(
                              (index) =>
                                (index + 1) %
                                (updates.data?.updates.length || 1),
                            )
                          }
                        >
                          <ChevronRight size={19} />
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <p>
                    {updates.error
                      ? "The log is temporarily unavailable. The full history is on GitHub."
                      : "Loading the latest field notes…"}
                  </p>
                )}
              </div>
            </div>
          </div>
        </section>

        <section className="section ledger-section" id="ledger">
          <SectionLabel index="03">THE WORK, IN THE OPEN</SectionLabel>
          <div className="section-intro">
            <h2>
              Don’t start from zero.
              <br />
              <span>Start where the evidence ends.</span>
            </h2>
            <p>
              These are method families, not a scoreboard of thousands of
              correlated guesses. Open a result to see its scope, limits,
              evidence, and reproducible commands.
            </p>
          </div>
          <div className="ledger-toolbar">
            <div className="filter-tabs" aria-label="Filter research methods">
              {[
                ["all", "All work"],
                ["tested", "Tested"],
                ["open", "Open leads"],
                ["in-progress", "In progress"],
              ].map(([value, label]) => (
                <button
                  key={value}
                  className={ledgerFilter === value ? "active" : ""}
                  onClick={() => setLedgerFilter(value)}
                  aria-pressed={ledgerFilter === value}
                >
                  {label}
                </button>
              ))}
            </div>
            <label className="search-field">
              <Search size={16} />
              <input
                placeholder="Find a method…"
                aria-label="Search research methods"
                value={ledgerSearch}
                onChange={(event) => setLedgerSearch(event.target.value)}
              />
            </label>
          </div>
          <div className="ledger-table">
            <div className="ledger-heading">
              <span>STATUS / METHOD</span>
              <span>WHAT WE LEARNED</span>
              <span>REVIEW</span>
            </div>
            {methods.map((method, index) => (
              <details className="method-row" key={method.id}>
                <summary>
                  <div className="method-title">
                    <span className={"status-dot status-" + method.status} />
                    <div>
                      <span className="method-number">
                        {String(index + 1).padStart(2, "0")} /{" "}
                        {statusLabel(method.status)}
                      </span>
                      <h3>{method.title}</h3>
                    </div>
                  </div>
                  <p>{method.result}</p>
                  <span className="method-toggle">
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
                  </div>
                  <div>
                    <h4>Evidence & reproduction</h4>
                    {method.evidence.map((path) => (
                      <a
                        className="evidence-link"
                        key={path}
                        href={researchPath(path)}
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
                  </div>
                </div>
              </details>
            ))}
            {!methods.length && (
              <div className="empty-state">
                {ledger.error ? (
                  <>
                    The index could not load.{" "}
                    <a href={repo}>Browse the repository ↗</a>
                  </>
                ) : ledger.data ? (
                  "No methods match this filter."
                ) : (
                  "Loading the research ledger…"
                )}
              </div>
            )}
          </div>
          <div className="ledger-bottom">
            <span>AN EMPTY RESULT IS STILL A RESULT.</span>
            <a
              href={repo + "/issues/new?template=experiment.yml"}
              className="text-link"
              target="_blank"
              rel="noopener noreferrer"
            >
              Propose the next experiment <ArrowUpRight size={16} />
            </a>
          </div>
        </section>

        <section className="vault-section" id="files">
          <div className="section">
            <SectionLabel index="04">THE EVIDENCE VAULT</SectionLabel>
            <div className="section-intro">
              <h2>Take the whole case.</h2>
              <p>
                The sanitized public corpus includes source scans, transcripts,
                reports, data, and solver code. Historical errors stay visible
                with their corrections. Personal data and private chat records
                stay out.
              </p>
            </div>
            <div className="vault-banner">
              <div className="vault-icon">
                <FolderOpen size={30} />
              </div>
              <div>
                <span className="mono">COMPLETE RESEARCH SNAPSHOT</span>
                <h3>
                  {files.data
                    ? files.data.totals.files.toLocaleString() +
                      " public files. One starting point."
                    : "Every relevant public file. One starting point."}
                </h3>
                <p>
                  {files.data
                    ? formatBytes(files.data.totals.bytes) + " uncompressed · "
                    : ""}
                  Source manifest + SHA-256 checksums included
                </p>
              </div>
              <a className="button button-dark" href={ARCHIVE} download>
                Download case file <ArrowDownToLine size={18} />
              </a>
            </div>
            <div className="vault-toolbar">
              <div className="filter-tabs">
                {[
                  ["all", "Everything"],
                  ["sources", "Sources"],
                  ["results", "Reports & data"],
                  ["code", "Code"],
                ].map(([value, label]) => (
                  <button
                    key={value}
                    className={fileFilter === value ? "active" : ""}
                    onClick={() => {
                      setFileFilter(value);
                      setFileLimit(16);
                    }}
                    aria-pressed={fileFilter === value}
                  >
                    {label}
                  </button>
                ))}
              </div>
              <label className="search-field">
                <Search size={16} />
                <input
                  ref={fileInput}
                  placeholder="Search the archive"
                  aria-label="Search archive files"
                  value={fileSearch}
                  onChange={(event) => {
                    setFileSearch(event.target.value);
                    setFileLimit(16);
                  }}
                />
                <kbd>⌘ K</kbd>
              </label>
            </div>
            <div className="file-list">
              {visibleFiles.slice(0, fileLimit).map((file) => (
                <a
                  className="file-row"
                  key={file.path}
                  href={researchPath(file.path)}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span className="file-icon">
                    {/\.(js|py|ts|html)$/.test(file.path) ? (
                      <FileCode2 size={19} />
                    ) : (
                      <FileText size={19} />
                    )}
                  </span>
                  <span className="file-name">
                    <strong>{file.path.split("/").pop()}</strong>
                    <small>
                      {file.path.split("/").slice(0, -1).join("/") ||
                        "Corpus root"}
                    </small>
                  </span>
                  <span className="file-type">
                    {file.category.replace(/_/g, " ")}
                  </span>
                  <span className="file-size">{formatBytes(file.bytes)}</span>
                  <ArrowUpRight size={17} />
                </a>
              ))}
            </div>
            {files.error ? (
              <p className="empty-state">
                The file index is unavailable.{" "}
                <a href={repo + "/tree/main/public/research"}>
                  Browse all files on GitHub ↗
                </a>
              </p>
            ) : !files.data ? (
              <p className="empty-state">Loading the public file index…</p>
            ) : !visibleFiles.length ? (
              <p className="empty-state">
                No matching files. Try a shorter search.
              </p>
            ) : (
              <div className="vault-bottom">
                <span>
                  {Math.min(fileLimit, visibleFiles.length)} OF{" "}
                  {visibleFiles.length.toLocaleString()} FILES
                </span>
                {fileLimit < visibleFiles.length && (
                  <button
                    className="text-link"
                    onClick={() => setFileLimit((limit) => limit + 24)}
                  >
                    Load 24 more <ArrowDown size={16} />
                  </button>
                )}
                <a href="/research/SHA256SUMS" className="text-link">
                  Verify the files <ArrowUpRight size={16} />
                </a>
              </div>
            )}
          </div>
        </section>

        <section className="section agent-section" id="agent-lab">
          <SectionLabel index="05">BRING YOUR OWN INTELLIGENCE</SectionLabel>
          <div className="agent-layout">
            <div>
              <span className="agent-symbol" aria-hidden="true">
                [ _ ]
              </span>
              <h2>
                Your model.
                <br />
                The same evidence.
              </h2>
              <p>
                Human, agent, or an unreasonable combination of both—start with
                the source register and experiment ledger. Make the next attempt
                reproducible.
              </p>
              <div className="agent-links">
                <a href="/llms.txt">
                  Agent entry point <ArrowUpRight size={16} />
                </a>
                <a
                  href={repo + "/blob/main/CONTRIBUTING.md"}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  How to contribute <ArrowUpRight size={16} />
                </a>
              </div>
            </div>
            <div className="prompt-card">
              <div className="prompt-card-top">
                <span>INVESTIGATION_BRIEF.TXT</span>
                <button
                  onClick={() => copy(prompt, "Investigation brief copied.")}
                >
                  <Copy size={15} /> Copy brief
                </button>
              </div>
              <textarea
                aria-label="Copyable investigation brief"
                readOnly
                value={prompt}
                rows={10}
              />
              <div className="prompt-card-bottom">
                <span>
                  <Check size={13} /> Evidence before interpretation
                </span>
                <span>
                  <Check size={13} /> Exact steps, honest limits
                </span>
              </div>
            </div>
          </div>
        </section>

        <section className="section community-section" id="community">
          <SectionLabel index="06">LEAVE A LEAD</SectionLabel>
          <div className="section-intro">
            <h2>
              A public problem.
              <br />
              <span>An open room.</span>
            </h2>
            <p>
              The earlier research and discussion also live in Discord. Bring a
              clue, question a result, or test an idea together. Publish
              reproducible findings on GitHub; Nostr is open below.
            </p>
          </div>
          <div className="discord-room">
            <span className="discord-room-icon" aria-hidden="true">
              <MessageCircle size={26} />
            </span>
            <div>
              <span className="discord-room-label">THE PUZZLE DISCORD</span>
              <h3>Meet the other detectives.</h3>
              <p>
                Earlier files, shared leads, and people still looking for the
                key.
              </p>
            </div>
            <a
              className="button button-lime"
              href={DISCORD}
              target="_blank"
              rel="noopener noreferrer"
            >
              Join the Discord <ArrowUpRight size={17} />
            </a>
          </div>
          <NostrRoom
            roomTag={project.data?.nostrTag || "keiser-key-not-found"}
            title="The case room"
          />
        </section>

        <section className="token-section" id="token">
          <div className="section">
            <SectionLabel index="07">KEEP THE SEARCH ALIVE</SectionLabel>
            <div className="token-layout">
              <div>
                <span className="token-ticker">$KEY404</span>
                <h2>
                  The mystery keeps going.
                  <br />
                  So does the work.
                </h2>
                <p className="token-intro">
                  A planned Pump.fun token to support an open, persistent
                  investigation. Creator fees are intended to fund AI agents,
                  research runs, and the tools that make this case easier to
                  solve.
                </p>
                <span className="launch-status">
                  <span /> {tokenLive ? "TOKEN LIVE" : "TOKEN NOT LAUNCHED"}
                </span>
              </div>
              <div className="funding-plan">
                <div>
                  <span className="funding-number">01</span>
                  <div>
                    <h3>Fees → research</h3>
                    <p>
                      Project-received creator fees are intended for research
                      expenses. Publish receipts, costs, and resulting work in
                      the public ledger.
                    </p>
                  </div>
                </div>
                <div>
                  <span className="funding-number">02</span>
                  <div>
                    <h3>Work → everyone</h3>
                    <p>
                      Every funded run should add a test, source, correction, or
                      useful dead end to the shared repository. Anyone can
                      continue it.
                    </p>
                  </div>
                </div>
                <div>
                  <span className="funding-number">03</span>
                  <div>
                    <h3>Recovered BTC → buybacks</h3>
                    <p>
                      If this project actually recovers the claimed prize, the
                      stated intention is to use 100% of the recovered BTC for
                      $KEY404 buybacks. Recovery and buybacks are not
                      guaranteed.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="token-bottom">
              <div>
                <span className="mono">OFFICIAL CONTRACT</span>
                <strong>
                  {project.data?.token.contract || "Not created yet"}
                </strong>
              </div>
              {tokenLive && project.data?.token.url ? (
                <a
                  className="button button-dark"
                  href={project.data.token.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on Pump.fun <ArrowUpRight size={17} />
                </a>
              ) : (
                <button className="button button-dark" disabled>
                  Launch pending <LockKeyhole size={16} />
                </button>
              )}
              <p>
                {tokenLive
                  ? "The funding plan is a public intention, not an enforced contract, ownership right, or claim on the BTC. "
                  : "There is no live token, sale, or treasury address connected to this site. The funding plan is a public intention, not an enforced contract, ownership right, or claim on the BTC. "}
                <a href="/FUNDING.md">Read the full plan ↗</a>
              </p>
            </div>
            <details className="funding-receipts">
              <summary>
                Public funding receipts{" "}
                <span>
                  {project.data?.funding?.receipts.length || 0} published{" "}
                  <ChevronDown size={15} />
                </span>
              </summary>
              {project.data?.funding?.receipts.length ? (
                <div className="receipt-list">
                  {project.data.funding.receipts.map((receipt) => (
                    <a
                      key={receipt.date + receipt.evidence}
                      href={receipt.evidence}
                    >
                      <time>{receipt.date}</time>
                      <span>{receipt.description}</span>
                      <strong>
                        {receipt.amount} {receipt.currency}
                      </strong>
                      <ArrowUpRight size={15} />
                    </a>
                  ))}
                </div>
              ) : (
                <p>
                  No token-funded receipts have been published. Received fees,
                  costs, sanitized receipts, and resulting experiments should be
                  recorded here as funding starts.
                </p>
              )}
              <a className="text-link" href="/data/project.json">
                View the public ledger data <ArrowUpRight size={14} />
              </a>
            </details>
            <a
              className="launch-kit-link"
              href="/downloads/key404-launch-kit.zip"
              download
            >
              Download the token launch kit: name, ticker, description, artwork{" "}
              <ArrowDownToLine size={15} />
            </a>
          </div>
        </section>

        <footer className="site-footer">
          <div className="footer-main">
            <a className="brand" href="#top">
              <span className="brand-mark">
                <KeyRound size={21} />
              </span>
              <span>
                KEY<span className="brand-slash">/</span>404
              </span>
            </a>
            <p>
              THE KEY IS MISSING.
              <br />
              THE WORK IS PUBLIC.
            </p>
            <div>
              <a href={repo} target="_blank" rel="noopener noreferrer">
                GitHub <ArrowUpRight size={14} />
              </a>
              <a href={DISCORD} target="_blank" rel="noopener noreferrer">
                Discord <ArrowUpRight size={14} />
              </a>
              <a href="/research/PRIVACY_AUDIT.md">
                Release privacy audit <ArrowUpRight size={14} />
              </a>
              <a href="/research/DATA_LICENSE.md">
                Sources & rights <ArrowUpRight size={14} />
              </a>
            </div>
          </div>
          <div className="footer-small">
            <span>
              Independent community research. Not affiliated with Max Keiser,
              Bitcoin Magazine, or Pump.fun.
            </span>
            <span>
              CASE STATUS: UNSOLVED · UPDATED{" "}
              {project.data
                ? dateLabel(project.data.updatedOn).toUpperCase()
                : "09 NOV 2026"}
            </span>
          </div>
        </footer>
      </main>

      <dialog
        ref={dialog}
        className="page-dialog"
        aria-labelledby="page-viewer-title"
        onClose={() => setSelectedPage(null)}
        onClick={(event) => {
          if (event.target === dialog.current) dialog.current.close();
        }}
      >
        <div className="page-dialog-top">
          <span id="page-viewer-title">
            ISSUE 24 / PRINTED PAGE {selectedPage}
          </span>
          <div>
            <button
              disabled={selectedPage === 73}
              aria-label="Previous page"
              onClick={() =>
                setSelectedPage((page) => Math.max(73, (page || 73) - 1))
              }
            >
              <ChevronLeft />
            </button>
            <button
              disabled={selectedPage === 80}
              aria-label="Next page"
              onClick={() =>
                setSelectedPage((page) => Math.min(80, (page || 73) + 1))
              }
            >
              <ChevronRight />
            </button>
            <button
              aria-label="Close page viewer"
              onClick={() => dialog.current?.close()}
            >
              <X />
            </button>
          </div>
        </div>
        {selectedPage !== null && (
          <>
            <img
              src={"/research/sources/pages/" + selectedPage + ".jpg"}
              alt={
                "Complete scanned printed page " +
                selectedPage +
                " of Bitcoin Magazine Issue 24"
              }
            />
            <div className="page-dialog-bottom">
              <span>Use ← → to turn the pages. Escape to close.</span>
              <a
                href={"/research/sources/pages/" + selectedPage + ".jpg"}
                target="_blank"
                rel="noopener noreferrer"
              >
                Open full image <ArrowUpRight size={15} />
              </a>
            </div>
          </>
        )}
      </dialog>
      {toast && (
        <div className="toast" role="status">
          <Check size={16} />
          {toast}
        </div>
      )}
    </>
  );
}

function ArrowDownRight() {
  return <ArrowRight className="diagonal-arrow" size={18} />;
}
function statusLabel(status: string) {
  return (
    (
      {
        falsified: "Tested · no result",
        tested: "Tested",
        invalidated: "Corrected",
        partial: "Partial lead",
        untested: "Open question",
        open: "Open question",
        "in-progress": "In progress",
        in_progress: "In progress",
      } as Record<string, string>
    )[status] || status.replace(/[-_]/g, " ")
  );
}

export default App;

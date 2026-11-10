import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowDownToLine,
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
import ExplainerFilm from "./components/ExplainerFilm";
import PublicChat from "./components/PublicChat";
import ResearchMapView from "./components/ResearchMap";
import RepositoryActivity from "./components/RepositoryActivity";
import ResearchFeed from "./components/ResearchFeed";
import VisualLab from "./components/VisualLab";
import type { VisualLabView } from "./components/VisualLab";
import VisualJournal from "./components/VisualJournal";
import projectSnapshot from "../public/data/project.json";
import useLiveResearch from "./hooks/useLiveResearch";
import { followHashLinks } from "./lib/hashLinks";
import { isActiveStatus, isOpenStatus } from "./lib/methodStatus";
import type {
  ResearchLedger,
  ResearchMap,
  ResearchUpdate,
  ResearchUpdates,
} from "./lib/researchState";
import { compareResearchUpdates } from "./lib/researchState";

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
type Project = {
  repository: string;
  updatedOn: string;
  chat?: { provider: string; room: string; url: string };
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
// Date of the creator's public 20 BTC post, as recorded in the source register.
const CLAIM_DATE = "2023-03-04";
const FIRST_PAGE = 73;
const LAST_PAGE = 80;
const NAV = [
  ["Case", "case"],
  ["Visuals", "visual-lab"],
  ["Map", "investigation"],
  ["Log", "updates"],
  ["Files", "files"],
  ["Discuss", "discussion"],
  ["Funding", "token"],
];
const START_FILES: Record<string, string> = {
  "sources/creator-clues.json": "Read the creator’s clues",
  "sources/printed-lines.json": "Inspect the exact printed lines",
  "experiments.json": "See what has been tried",
  "REPRODUCE.md": "Run an experiment yourself",
  "README.md": "Read the case overview",
};
const startFileOrder = Object.keys(START_FILES);
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
const noteTone = (category: string) =>
  ({
    CORRECTION: " is-correction",
    "SOURCE FIX": " is-source",
    TESTED: " is-tested",
  })[category.trim().toUpperCase()] || "";
const calmScroll = (): ScrollBehavior =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ? "auto"
    : "smooth";

function useJson<T>(path: string, initialData: T | null = null) {
  const [data, setData] = useState<T | null>(initialData);
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
  const project = useJson<Project>("/data/project.json", projectSnapshot as Project);
  const updates = useJson<ResearchUpdates>("/data/updates.json");
  const ledger = useJson<ResearchLedger>("/research/experiments.json");
  const researchMap = useJson<ResearchMap>("/data/research-map.json");
  const liveResearch = useLiveResearch({
    ledger: ledger.data,
    updates: updates.data,
    map: researchMap.data,
  });
  const currentLedger = liveResearch.data?.ledger || ledger.data;
  const currentUpdates = liveResearch.data?.updates || updates.data;
  const currentMap = liveResearch.data?.map || researchMap.data;
  const files = useJson<FileIndex>("/research/files.json");
  const [menuOpen, setMenuOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [fileSearch, setFileSearch] = useState("");
  const [fileFilter, setFileFilter] = useState("all");
  const [fileLimit, setFileLimit] = useState(5);
  const [toast, setToast] = useState("");
  const [selectedPage, setSelectedPage] = useState<number | null>(null);
  const [showProjectNotes, setShowProjectNotes] = useState(false);
  const [pendingUpdate, setPendingUpdate] = useState<string | null>(null);
  const [visualView, setVisualView] = useState<VisualLabView>({ layout: "spread", page: 75 });
  const [visualOpenRequest, setVisualOpenRequest] = useState(0);
  const dialog = useRef<HTMLDialogElement>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const repo = project.data?.repository || REPO;
  const updateEntries = useMemo(
    () =>
      [...(currentUpdates?.updates || [])].sort(compareResearchUpdates),
    [currentUpdates],
  );
  const researchNotes = updateEntries.filter(
    (entry) => entry.kind !== "project",
  );
  const projectNotes = updateEntries.filter(
    (entry) => entry.kind === "project",
  );
  const latestFinding = updateEntries.find(
    (entry) => entry.kind === "research",
  );
  const methodCount = currentLedger?.methods.length ?? 0;
  const openMethods = (currentLedger?.methods || []).filter((method) =>
    isOpenStatus(method.status),
  ).length;
  const activeMethods = (currentLedger?.methods || []).filter((method) =>
    isActiveStatus(method.status),
  ).length;
  const daysSinceClaim = Math.floor(
    (Date.now() - Date.parse(CLAIM_DATE + "T00:00:00Z")) / 86_400_000,
  );
  const tokenLive =
    project.data?.token.status === "live" &&
    Boolean(project.data.token.contract && project.data.token.url);
  const evidenceLink = (path: string, corpus = false) =>
    liveResearch.sourceCommit
      ? `${repo}/blob/${liveResearch.sourceCommit}/public/${corpus ? "research/" : ""}${path.replace(/^\/+/, "").split("/").map(encodeURIComponent).join("/")}`
      : corpus
        ? researchPath(path)
        : path;

  // A shared visual URL can arrive before React has inserted its section.
  // Wait for the page's type to settle, then land below the sticky header.
  useEffect(() => {
    const hash = window.location.hash;
    if (!["#film", "#visual-lab", "#visual-updates"].includes(hash)) return;
    let cancelled = false;
    void document.fonts.ready.then(() => {
      if (cancelled || window.location.hash !== hash) return;
      const target = document.getElementById(hash.slice(1));
      if (!target) return;
      const headerHeight = document.querySelector("header")?.getBoundingClientRect().height ?? 0;
      window.scrollTo({
        top: window.scrollY + target.getBoundingClientRect().top - headerHeight,
        behavior: "instant",
      });
    });
    return () => {
      cancelled = true;
    };
  }, []);

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
          ?.scrollIntoView({ behavior: calmScroll() });
        fileInput.current?.focus({ preventScroll: true });
      }
      if (selectedPage !== null && event.key === "ArrowRight")
        setSelectedPage((page) =>
          page === null ? FIRST_PAGE : Math.min(LAST_PAGE, page + 1),
        );
      if (selectedPage !== null && event.key === "ArrowLeft")
        setSelectedPage((page) =>
          page === null ? FIRST_PAGE : Math.max(FIRST_PAGE, page - 1),
        );
    };
    document.addEventListener("keydown", handle);
    return () => document.removeEventListener("keydown", handle);
  }, [selectedPage]);
  // A link to a project note opens the folded list before scrolling to it,
  // including when the link repeats the hash already in the address bar.
  useEffect(
    () =>
      followHashLinks((hash) => {
        const match = /^#update-([a-z0-9-]+)$/.exec(hash);
        // Any other destination replaces or cancels a note still waiting.
        setPendingUpdate(match ? match[1] : null);
      }),
    [],
  );
  // The deployed snapshot is not the last word: a note merged after this
  // deployment arrives with the live sync. A note that is not in the current
  // data keeps waiting until it appears or the visitor goes elsewhere.
  useEffect(() => {
    if (!pendingUpdate) return;
    const entry = updateEntries.find((item) => item.id === pendingUpdate);
    if (!entry) return;
    if (entry.kind === "project" && !showProjectNotes) {
      setShowProjectNotes(true);
      return;
    }
    const target = document.getElementById("update-" + pendingUpdate);
    if (target instanceof HTMLDetailsElement) target.open = true;
    target?.scrollIntoView({ behavior: calmScroll(), block: "start" });
    setPendingUpdate(null);
  }, [pendingUpdate, updateEntries, showProjectNotes]);

  async function copy(text: string, success: string) {
    try {
      await navigator.clipboard.writeText(text);
      setToast(success);
    } catch {
      setToast("Clipboard unavailable. Select and copy the text below.");
    }
  }
  const prompt = `Investigate the public Max Keiser magazine puzzle using the source corpus at ${typeof window === "undefined" ? "" : window.location.origin}/research/README.md. Start with sources/creator-clues.json, sources/printed-lines.json, experiments.json and SHA256SUMS. The puzzle is unsolved; no authenticated prize address is known. Review corrected historical claims before choosing one untested, source-motivated hypothesis. Declare source unit, traversal, operation, expected output and falsification criterion. Preserve exact intermediate data and reproducible commands. Distinguish facts, hypotheses and scoped negative results. Do not send transactions, import wallets or contact people. Submit a concise finding and evidence through ${repo}/issues.`;
  const visibleFiles = useMemo(
    () =>
      (files.data?.files || [])
        .filter((file) => {
          const category = file.category.toLowerCase();
          const matches =
            fileFilter === "all" ||
            (fileFilter === "code"
              ? /code|script/.test(category) ||
                /\.(py|js|ts|html)$/.test(file.path)
              : fileFilter === "sources"
                ? /source|clue/.test(category) ||
                  file.path.startsWith("sources/")
                : /report|analysis|result|data/.test(category));
          return (
            matches &&
            (file.path + " " + file.description)
              .toLowerCase()
              .includes(fileSearch.toLowerCase())
          );
        })
        .sort((a, b) => {
          const aIndex = startFileOrder.indexOf(a.path);
          const bIndex = startFileOrder.indexOf(b.path);
          return (aIndex < 0 ? 99 : aIndex) - (bIndex < 0 ? 99 : bIndex);
        }),
    [files.data, fileSearch, fileFilter],
  );

  const renderNote = (entry: ResearchUpdate) => (
    <article
      className="note"
      key={entry.id}
      id={"update-" + entry.id}
      data-category={entry.category}
    >
      <div className="note-kicker">
        <span className={"note-category" + noteTone(entry.category)}>
          {entry.category}
        </span>
        <time dateTime={entry.date}>{dateLabel(entry.date)}</time>
      </div>
      <h3>{entry.title}</h3>
      <p>{entry.body}</p>
      <div className="note-links">
        <a className="text-link light" href={evidenceLink(entry.evidence)}>
          Read the evidence <ArrowUpRight size={16} />
        </a>
        {entry.methodIds?.map((id) => (
          <a className="note-method" key={id} href={"#method-" + id}>
            <code>{id}</code>
          </a>
        ))}
      </div>
    </article>
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
          {NAV.map(([label, target]) => (
            <a
              href={"#" + target}
              key={target}
              onClick={() => setMenuOpen(false)}
            >
              {label}
            </a>
          ))}
          <div className="nav-discussion-actions">
            <button
              onClick={() => {
                setMenuOpen(false);
                setChatOpen(true);
              }}
            >
              Chat <MessageCircle size={16} />
            </button>
            <a
              href={DISCORD}
              target="_blank"
              rel="noopener noreferrer"
              onClick={() => setMenuOpen(false)}
            >
              Discord <ArrowUpRight size={16} />
            </a>
          </div>
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
          <div className="hero-topline">
            <span>
              <i className="status-swatch" aria-hidden="true" /> CASE FILE 001 ·
              UNSOLVED
            </span>
            <span>INDEPENDENT · UNAFFILIATED · OPEN SOURCE</span>
          </div>
          <div className="hero-main">
            <div className="hero-copy">
              <p className="hero-kicker">
                Max Keiser says he hid a Bitcoin private key in this magazine.
              </p>
              <h1>
                KEY <span className="title-mark">NOT</span>
                <br />
                FOUND<span className="hero-period">.</span>
              </h1>
              <p className="founder-story">
                <span>I found Max Keiser’s puzzle in 2023.</span>
                <span>I’ve been working on it ever since.</span>
                <strong>I’m still hunting. Got a lead?</strong>
              </p>
              <p className="hero-claim">
                <span>20 BTC claim</span>
                <span>by Max Keiser</span>
              </p>
              <div className="hero-actions">
                <a className="button button-lime" href="#investigation">
                  Explore the investigation <ArrowDown size={17} />
                </a>
                <a
                  className="text-link hero-discord"
                  href={DISCORD}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Join the Discord <ArrowUpRight size={16} />
                </a>
                {tokenLive && project.data?.token.url && (
                  <a
                    className="text-link"
                    href={project.data.token.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View $KEY404 <ArrowUpRight size={16} />
                  </a>
                )}
              </div>
            </div>
            <div className="hero-visual">
              <div className="visual-corners">
                <span>EXHIBIT 01</span>
                <span>THE SOURCE</span>
              </div>
              <button
                className="hero-exhibit"
                onClick={() => setSelectedPage(FIRST_PAGE)}
                aria-label="Inspect printed page 73"
              >
                <img
                  src="/research/sources/pages/73.jpg"
                  alt="The original OVERDOSE opening page from Bitcoin Magazine, with pills and a dollar bill"
                  width="2544"
                  height="3264"
                  fetchPriority="high"
                />
              </button>
              <div className="visual-caption">
                <button onClick={() => setSelectedPage(FIRST_PAGE)}>
                  Inspect the original <ArrowUpRight size={15} />
                </button>
                <span>ISSUE 24 · P.73</span>
              </div>
            </div>
          </div>
          <div
            className="hero-record"
            role="group"
            aria-label="The record at a glance"
          >
            <button onClick={() => setSelectedPage(FIRST_PAGE)}>
              <span className="record-label">THE SOURCE</span>
              <strong>8 printed pages</strong>
              <small>Bitcoin Magazine · Issue 24 · pp. 73–80</small>
            </button>
            <a href="#case">
              <span className="record-label">CLAIM POSTED</span>
              <strong>{dateLabel(CLAIM_DATE)}</strong>
              <small>
                {daysSinceClaim.toLocaleString("en-GB")} days ago · by Max
                Keiser
              </small>
            </a>
            <a href="#ledger">
              <span className="record-label">ON THE RECORD</span>
              <strong>
                {currentLedger ? `${methodCount} methods` : "The ledger"}
              </strong>
              <small>each with scope, evidence and limits</small>
            </a>
            <a href="#open-leads" className="record-open">
              <span className="record-label">STILL OPEN</span>
              <strong>
                {currentLedger ? `${openMethods} open / partial` : "Open leads"}
              </strong>
              <small>
                pick one and test it <ArrowDown size={13} />
              </small>
            </a>
          </div>
        </section>

        <ExplainerFilm />

        <section className="roles" id="roles" aria-labelledby="roles-title">
          <div className="roles-head">
            <h2 id="roles-title">Want to help?</h2>
            <p>
              This is my investigation. The files, tests and updates are public.
              Read along, challenge a result, or test a lead. No token needed.
            </p>
          </div>
          <div className="roles-grid">
            <button className="role" onClick={() => setSelectedPage(FIRST_PAGE)}>
              <span className="role-index">01</span>
              <strong>Reader</strong>
              <span className="role-verb">Read the eight pages.</span>
              <span className="role-note">
                Read the original pages. Check the notes.
              </span>
              <span className="role-action">
                Open the pages <ArrowUpRight size={15} />
              </span>
            </button>
            <a
              className="role"
              href={repo + "/issues/new?template=correction.yml"}
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className="role-index">02</span>
              <strong>Skeptic</strong>
              <span className="role-verb">Challenge a result.</span>
              <span className="role-note">
                Corrections stay in the record, with their evidence.
              </span>
              <span className="role-action">
                File a correction <ArrowUpRight size={15} />
              </span>
            </a>
            <a className="role" href="#open-leads">
              <span className="role-index">03</span>
              <strong>Solver</strong>
              <span className="role-verb">Test one idea.</span>
              <span className="role-note">
                Fix the rule first. Publish what happens, including nothing.
              </span>
              <span className="role-action">
                See the open leads <ArrowDown size={15} />
              </span>
            </a>
            <a className={tokenLive ? "role" : "role role-later"} href="#token">
              <span className="role-index">{tokenLive ? "04" : "04 · AFTER LAUNCH"}</span>
              <strong>Backer</strong>
              <span className="role-verb">Fund research runs.</span>
              <span className="role-note">
                {tokenLive
                  ? "Follow the public funding and research record."
                  : "Not available yet. No token has launched."}
              </span>
              <span className="role-action">
                Read the funding plan <ArrowDown size={15} />
              </span>
            </a>
          </div>
        </section>

        <section className="section case-section" id="case">
          <SectionLabel index="01">THE CASE</SectionLabel>
          <div className="section-intro">
            <h2>
              A fortune in the margins.
              <br />
              <span>Or a mystery with no answer.</span>
            </h2>
            <p>
              Keiser made the claim publicly. The reward has not been
              independently verified. Start with what Keiser actually posted,
              then inspect the pages yourself.
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
                  View original post <ExternalLink size={13} />
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
                  View original post <ExternalLink size={13} />
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
                  View original post <ExternalLink size={13} />
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
                {Array.from(
                  { length: LAST_PAGE - FIRST_PAGE + 1 },
                  (_, i) => i + FIRST_PAGE,
                ).map((page) => (
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
              leaves the puzzle connection unverified. I label source facts,
              hypotheses, and failed tests separately.
            </p>
            <a href="/research/sources/creator-clues.json">
              Source register <ArrowUpRight size={16} />
            </a>
          </div>
        </section>

        <VisualLab view={visualView} onViewChange={setVisualView} openRequest={visualOpenRequest} />
        <VisualJournal onOpenView={(view) => {
          setVisualView(view);
          setVisualOpenRequest(value => value + 1);
          document.getElementById("visual-lab")?.scrollIntoView({ behavior: "instant", block: "start" });
        }} />

        <ResearchMapView
          branches={currentMap?.branches ?? null}
          methods={currentLedger?.methods ?? null}
          updates={updateEntries}
          sourceCommit={liveResearch.sourceCommit}
          checkedAt={liveResearch.checkedAt}
          status={liveResearch.status}
          repo={repo}
          loadFailed={ledger.error}
          evidenceLink={evidenceLink}
        />

        <section className="log-section" id="updates">
          <div className="section">
            <SectionLabel index="03" dark>
              THE TEST LOG
            </SectionLabel>
            <div className="log-layout">
              <div className="log-aside">
                <div className="log-intro">
                  <h2>
                    The tests.
                    <br />
                    <span>The results.</span>
                  </h2>
                  <p>
                    Each entry records what was tested and what it found.
                    Open a row for the evidence, limits and reproduction.
                    Failed tests and corrections stay on record.
                  </p>
                </div>
                <div className="standing">
                  <span className="map-label">THE CURRENT RECORD</span>
                  <strong>Still unsolved.</strong>
                  <p>
                    No verified solution or authenticated prize address is
                    known to this project.
                  </p>
                  {latestFinding && (
                    <p>
                      Latest finding:{" "}
                      <a href={"#update-" + latestFinding.id}>
                        {latestFinding.title}
                      </a>
                    </p>
                  )}
                  {currentLedger && (
                    <span className="standing-counts">
                      {openMethods} open / partial ·{" "}
                      {activeMethods
                        ? `${activeMethods} experiments in progress`
                        : "No active experiment logged"}
                    </span>
                  )}
                  <a href="#open-leads" className="text-link light">
                    See the open leads <ArrowUpRight size={16} />
                  </a>
                </div>
              </div>
              <div className="log-notes" aria-label="Published update history">
                <div className="log-sync" aria-live="polite">
                  <span>
                    {liveResearch.status === "verified"
                      ? "Synced from GitHub"
                      : liveResearch.status === "stale"
                        ? "Last verified GitHub data"
                        : liveResearch.status === "checking"
                          ? "Checking GitHub…"
                          : "Deployed snapshot"}
                  </span>
                  {liveResearch.checkedAt && (
                    <time dateTime={liveResearch.checkedAt}>
                      Checked{" "}
                      {new Date(liveResearch.checkedAt).toLocaleTimeString("en-GB", {
                        hour: "2-digit",
                        minute: "2-digit",
                        hourCycle: "h23",
                        timeZone: "UTC",
                      })}{" "}
                      UTC
                    </time>
                  )}
                  {liveResearch.sourceCommit && (
                    <a
                      href={repo + "/commit/" + liveResearch.sourceCommit}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {liveResearch.sourceCommit.slice(0, 7)} <ArrowUpRight size={12} />
                    </a>
                  )}
                  <small>Checks every 5 minutes while open.</small>
                </div>
                <div className="log-notes-head">
                  <span>
                    {updateEntries.length
                      ? `${researchNotes.length} RESEARCH ${researchNotes.length === 1 ? "RECORD" : "RECORDS"}`
                      : "RESEARCH RECORDS"}
                  </span>
                  <span>
                    {currentUpdates?.updatedOn
                      ? `LAST UPDATED ${dateLabel(updateEntries[0]?.date || currentUpdates.updatedOn).toUpperCase()}`
                      : ""}
                  </span>
                </div>
                <ResearchFeed
                  entries={researchNotes}
                  methods={currentLedger?.methods || []}
                  evidenceLink={evidenceLink}
                />
                {updateEntries.length > 0 && !researchNotes.length && (
                  <p className="log-empty">
                    No research note has been published yet.
                  </p>
                )}
                {projectNotes.length > 0 && (
                  <details
                    className="project-notes"
                    open={showProjectNotes}
                    onToggle={(event) =>
                      setShowProjectNotes(event.currentTarget.open)
                    }
                  >
                    <summary>
                      <span>
                        Site and project notes · {projectNotes.length}
                      </span>
                      <small>Changes to this website, not research results</small>
                      <ChevronDown size={18} />
                    </summary>
                    {projectNotes.map(renderNote)}
                  </details>
                )}
                {!updateEntries.length && (
                  <p className="log-empty">
                    {updates.error
                      ? "The update log is unavailable. The full history is on GitHub."
                      : "Loading published notes…"}
                  </p>
                )}
                <a
                  className="text-link light log-history"
                  href={repo + "/commits/main"}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  See the full commit history <ArrowUpRight size={17} />
                </a>
              </div>
            </div>
            <div className="log-record-links">
              <p className="log-origin">
                This public log opened{" "}
                {currentUpdates?.logOpenedOn
                  ? dateLabel(currentUpdates.logOpenedOn)
                  : "09 Nov 2026"}
                . Earlier work is preserved in the experiment ledger.
                Completion times are shown in UTC; older entries keep their
                recorded date.
              </p>
              <RepositoryActivity repo={repo} />
            </div>
          </div>
        </section>

        <section className="vault-section" id="files">
          <div className="section">
            <SectionLabel index="04">THE EVIDENCE VAULT</SectionLabel>
            <div className="section-intro">
              <h2>Take the whole case.</h2>
              <p>
                The sanitized public corpus includes source scans, transcripts,
                reports, data, and solver code in this release snapshot. The
                live map and notes can advance between releases; their evidence
                links open the exact GitHub revision.
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
                      setFileLimit(value === "all" && !fileSearch ? 5 : 16);
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
                    setFileLimit(event.target.value ? 16 : 5);
                  }}
                />
                <kbd>⌘ K</kbd>
              </label>
            </div>
            {!fileSearch && fileFilter === "all" && fileLimit === 5 && (
              <p className="vault-start-label">
                NEW TO THE CASE? START WITH THESE FIVE.
              </p>
            )}
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
                    <strong>
                      {START_FILES[file.path] || file.path.split("/").pop()}
                    </strong>
                    <small>
                      {START_FILES[file.path]
                        ? file.path
                        : file.path.split("/").slice(0, -1).join("/") ||
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

        <section className="section discussion-section" id="discussion">
          <SectionLabel index="06">SHARE A LEAD</SectionLabel>
          <div className="section-intro">
            <h2>
              Talk here.
              <br />
              <span>Publish there.</span>
            </h2>
            <p>
              Have a question or a lead? Drop it in the chat. Earlier files and
              discussion are on Discord; reproducible findings go to GitHub.
              Help if you want. The work stays public.
            </p>
          </div>
          <div className="discussion-doors">
            <button
              className="discussion-door primary-door"
              onClick={() => setChatOpen(true)}
            >
              <MessageCircle size={24} aria-hidden="true" />
              <span>
                <strong>Chat</strong>
                <small>Pick a nickname. Ask a question.</small>
              </span>
              <ArrowUpRight size={20} aria-hidden="true" />
            </button>
            <a
              className="discussion-door"
              href={DISCORD}
              target="_blank"
              rel="noopener noreferrer"
            >
              <MessageCircle size={24} aria-hidden="true" />
              <span>
                <strong>Discord</strong>
                <small>Earlier files and ongoing discussion.</small>
              </span>
              <ArrowUpRight size={20} aria-hidden="true" />
            </a>
            <a
              className="discussion-door"
              href={repo}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github size={24} aria-hidden="true" />
              <span>
                <strong>GitHub</strong>
                <small>The lasting research record.</small>
              </span>
              <ArrowUpRight size={20} aria-hidden="true" />
            </a>
          </div>
        </section>

        <section className="token-section" id="token">
          <div className="section">
            <SectionLabel index="07">FUNDING</SectionLabel>
            <div className="funding-head">
              <div>
                <span className="launch-status">
                  <span /> {tokenLive ? "TOKEN LIVE" : "TOKEN NOT LAUNCHED"}
                </span>
                <h2>
                  {tokenLive ? (
                    <>
                      Funding the work.
                      <br />
                      <span>In public.</span>
                    </>
                  ) : (
                    <>
                      Planned funding.
                      <br />
                      <span>Nothing is live.</span>
                    </>
                  )}
                </h2>
              </div>
              <div className="token-ticker">
                <img
                  src="/assets/key404-emblem.png"
                  alt="KEY404 emblem"
                  width="56"
                  height="56"
                  loading="lazy"
                />
                <div>
                  <strong>$KEY404</strong>
                  <span>
                    {tokenLive
                      ? "The official contract is published below."
                      : "No official contract or trading link is published."}
                  </span>
                </div>
              </div>
            </div>
            <div className="funding-terms">
              <article>
                <span className="term-label">
                  {tokenLive ? "ACTIVE" : "PLANNED"}
                </span>
                <h3>Creator fees fund research.</h3>
                <p>
                  {tokenLive
                    ? "I use creator fees received by the project to fund AI agents and research runs. Each funded run publishes its method, cost and result."
                    : "If $KEY404 launches on Pump.fun, I’ll use creator fees received by the project to fund AI agents and research runs. Each funded run publishes its method, cost and result."}
                </p>
              </article>
              <article className="term-committed">
                <span className="term-label">COMMITTED</span>
                <h3>If I recover the prize BTC, 100% goes to buybacks.</h3>
                <p>
                  If this project recovers the prize BTC, I’ll use 100% of it for
                  $KEY404 buybacks, with public execution records. That is my
                  public commitment.
                </p>
              </article>
              <article>
                <span className="term-label">UNKNOWN</span>
                <h3>Whether there is a prize to recover.</h3>
                <p>
                  The 20 BTC is Max Keiser’s claim. Recovery is uncertain.
                </p>
              </article>
            </div>
            <p className="funding-line">
              Recovery is uncertain.{" "}
              <span className="mark">The allocation is not.</span>
            </p>
            <p className="funding-free">
              Reading the evidence, testing an idea, correcting the record and
              using the tools need no token. Every funded run should add a test,
              source, correction, or useful dead end to the shared repository.
            </p>
            <div className="token-bottom">
              <div>
                <span className="mono">OFFICIAL CONTRACT</span>
                <strong>
                  {project.data?.token.contract || "Not published"}
                </strong>
                {tokenLive && (
                  <button
                    className="contract-copy"
                    onClick={() => void copy(project.data?.token.contract || "", "Contract copied")}
                  >
                    <Copy size={15} /> Copy CA
                  </button>
                )}
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
                <span className="token-unlaunched-note">
                  No official contract or purchase link has been published.
                </span>
              )}
              <p>
                {tokenLive
                  ? "The buyback commitment applies to prize BTC this project actually recovers. It is not automated and gives no ownership right or claim on the BTC. "
                  : "The token has not launched. The buyback commitment applies to prize BTC this project actually recovers. It is not automated and gives no ownership right or claim on the BTC. "}
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
              An independent investigation. Not affiliated with Max Keiser,
              Bitcoin Magazine, or Pump.fun.
            </span>
            <span>
              CASE STATUS: UNSOLVED · UPDATED{" "}
              {dateLabel(
                currentUpdates?.updatedOn ||
                  project.data?.updatedOn ||
                  "2026-11-09",
              ).toUpperCase()}
            </span>
          </div>
        </footer>
      </main>

      {selectedPage === null && (
        <PublicChat
          open={chatOpen}
          onOpenChange={setChatOpen}
          discordUrl={DISCORD}
          repositoryUrl={repo}
          room={project.data?.chat?.room || "keiser-key-not-found"}
        />
      )}

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
              disabled={selectedPage === FIRST_PAGE}
              aria-label="Previous page"
              onClick={() =>
                setSelectedPage((page) =>
                  Math.max(FIRST_PAGE, (page || FIRST_PAGE) - 1),
                )
              }
            >
              <ChevronLeft />
            </button>
            <button
              disabled={selectedPage === LAST_PAGE}
              aria-label="Next page"
              onClick={() =>
                setSelectedPage((page) =>
                  Math.min(LAST_PAGE, (page || FIRST_PAGE) + 1),
                )
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

export default App;

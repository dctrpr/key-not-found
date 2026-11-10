import { Component, lazy, Suspense, useCallback, useEffect, useId, useRef, useState } from "react";
import type { ReactNode } from "react";
import { ArrowUpRight, Box, Layers3, Maximize2, Minus, Plus, RotateCcw, ScanLine } from "lucide-react";
import "./VisualLab.css";

const VisualScene = lazy(() => import("./VisualScene"));
export const VISUAL_PAGES = [73, 74, 75, 76, 77, 78, 79, 80] as const;
export type VisualLabView = { layout: "spread" | "stack" | "mirror"; page: number; source?: "issue26" | "issue27" | "funky" };
export const VISUAL_SOURCES = {
  issue24: {
    label: "2023 puzzle", name: "Bitcoin Magazine Issue 24", pages: VISUAL_PAGES,
    width: 2544, height: 3264, provenance: "/research/sources/provenance.json",
  },
  issue26: {
    label: "Censorship column", name: "Censorship, Dematerialization and Bitcoin", pages: [102, 103, 104],
    width: 2040, height: 2805,
    provenance: "/research/sources/issue26/SOURCE_REGISTER.md",
  },
  issue27: {
    label: "Orange Party column", name: "Bitcoin Magazine Orange Party column", pages: [78, 79, 80, 81],
    width: 2040, height: 2805,
    provenance: "/research/analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/SOURCE_REGISTER.md",
  },
  funky: {
    label: "Funky Upheaval", name: "Bitcoin and the Funky Upheaval", pages: [107, 108, 109, 110, 111, 112],
    width: 2040, height: 2805,
    provenance: "/research/sources/funky-upheaval/SOURCE_REGISTER.md",
  },
} as const;
export const visualSource = (source?: VisualLabView["source"]) => VISUAL_SOURCES[source || "issue24"];
export const visualPageUrl = (page: number, source?: VisualLabView["source"]) => source === "funky"
  ? `/research/sources/funky-upheaval/pages/${page}.jpg`
  : source === "issue26"
    ? `/research/sources/issue26/page_${String(page - 99).padStart(2, "0")}.jpg`
  : source === "issue27"
    ? `/research/analysis_outputs/comparison_articles/overdose_style_uniqueness/issue27/page_${String(page - 77).padStart(2, "0")}.jpg`
    : `/research/sources/pages/${page}.jpg`;
export const visualPairPages = (view: VisualLabView): [number, number] => {
  const pages: readonly number[] = visualSource(view.source).pages;
  const index = Math.max(0, pages.indexOf(view.page));
  const start = Math.min(Math.floor(index / 2) * 2, pages.length - 2);
  return [pages[start], pages[start + 1]];
};
export type VisualZoomRequest = { serial: number; amount: number };
type VisualLabProps = {
  /** An external scene request. Local controls remain usable with or without a callback. */
  view?: VisualLabView;
  onViewChange?: (view: VisualLabView) => void;
  /** Increment after an explicit journal/scene-link click to open the requested view. */
  openRequest?: number;
};

const DEFAULT_VIEW: VisualLabView = { layout: "spread", page: 75 };
const MODES = [
  { id: "spread", label: "Page board", Icon: ScanLine },
  { id: "stack", label: "Layer stack", Icon: Layers3 },
  { id: "mirror", label: "Mirror", Icon: Box },
] as const;
const checkedView = (view?: VisualLabView): VisualLabView => {
  const source = view?.source === "issue26" || view?.source === "issue27" || view?.source === "funky" ? view.source : undefined;
  const pages: readonly number[] = visualSource(source).pages;
  return {
    ...(source ? { source } : {}),
    layout: view && ["spread", "stack", "mirror"].includes(view.layout) ? view.layout : "spread",
    page: view && pages.includes(view.page) ? view.page : pages[0],
  };
};

class SceneBoundary extends Component<
  { children: ReactNode; onFailure: () => void },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch() { this.props.onFailure(); }
  render() { return this.state.failed ? null : this.props.children; }
}

export default function VisualLab({ view, onViewChange, openRequest }: VisualLabProps) {
  const [current, setCurrent] = useState<VisualLabView>(() => checkedView(view || DEFAULT_VIEW));
  const [started, setStarted] = useState(false);
  const [unavailable, setUnavailable] = useState(false);
  const [ready, setReady] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const [reset, setReset] = useState(0);
  const [zoom, setZoom] = useState<VisualZoomRequest>({ serial: 0, amount: 0 });
  const [progress, setProgress] = useState({ loaded: 0, total: 2 });
  const instructionsId = useId();
  const stage = useRef<HTMLDivElement>(null);
  const startButton = useRef<HTMLButtonElement>(null);
  const returnFocus = useRef(false);
  const focusScene = useRef(false);

  useEffect(() => {
    if (!view) return;
    const next = checkedView(view);
    setCurrent((before) => before.layout === next.layout && before.page === next.page && before.source === next.source ? before : next);
  }, [view?.layout, view?.page, view?.source]);

  useEffect(() => {
    if (!openRequest) return;
    setAttempt((value) => value + 1);
    setUnavailable(false);
    setReady(false);
    setReset(0);
    setZoom({ serial: 0, amount: 0 });
    setStarted(true);
  }, [openRequest]);

  useEffect(() => {
    if (ready && focusScene.current) {
      stage.current?.querySelector("canvas")?.focus({ preventScroll: true });
      focusScene.current = false;
    }
    if (!started && returnFocus.current) {
      startButton.current?.focus({ preventScroll: true });
      returnFocus.current = false;
    }
  }, [ready, started]);

  const selectView = (next: VisualLabView) => {
    const safe = checkedView(next);
    setCurrent(safe);
    onViewChange?.(safe);
  };
  const handleProgress = useCallback((loaded: number, total: number) => {
    setProgress({ loaded, total });
    if (loaded < total) setReady(false);
  }, []);
  const handleReady = useCallback(() => setReady(true), []);
  const handleFailure = useCallback(() => { setUnavailable(true); setReady(false); }, []);
  const stop = useCallback(() => {
    returnFocus.current = true;
    setStarted(false);
    setReady(false);
  }, []);
  const start = () => {
    setAttempt((value) => value + 1);
    setUnavailable(false);
    setReady(false);
    setReset(0);
    setZoom({ serial: 0, amount: 0 });
    focusScene.current = true;
    setStarted(true);
  };
  const changeZoom = (amount: number) => setZoom((before) => ({ serial: before.serial + 1, amount }));
  const sourceId = current.source || "issue24";
  const source = visualSource(current.source);
  const [pairStart, pairEnd] = visualPairPages(current);
  const companion = current.page === pairStart ? pairEnd : pairStart;
  const is3D = started && !unavailable;
  const modeLabel = unavailable ? "2D source scan" : MODES.find((mode) => mode.id === current.layout)!.label;
  const stageLabel = !unavailable && current.layout === "spread" ? `Pages ${pairStart}–${pairEnd}` : `Page ${current.page}`;

  return (
    <section className="visual-lab" id="visual-lab" aria-labelledby="visual-lab-title" data-source={sourceId}>
      <div className="visual-lab-heading">
        <div>
          <span className="visual-eyebrow">THE VISUAL LAB</span>
          <h2 id="visual-lab-title">See the work.</h2>
        </div>
        <p>Turn the pages. Pull the layers apart. Inspect the actual scans, then compare a hypothesis.</p>
      </div>

      <div className="visual-console">
        <div className="visual-source-control" role="group" aria-label="Choose a source set">
          <span className="visual-page-label">SOURCE SET</span>
          {Object.entries(VISUAL_SOURCES).map(([id, option]) => (
            <button key={id} type="button" aria-pressed={sourceId === id} onClick={() => {
              if (sourceId === id) return;
              selectView({ layout: current.layout, page: option.pages[0], ...(id === "issue26" || id === "issue27" || id === "funky" ? { source: id } : {}) });
            }}>{option.label}</button>
          ))}
        </div>
        <div className="visual-toolbar">
          <div className="visual-mode-control" role="group" aria-label="Choose a visual layout">
            {MODES.map(({ id, label, Icon }) => (
              <button key={id} type="button" aria-pressed={current.layout === id}
                onClick={() => selectView({ ...current, layout: id })}>
                <Icon size={15} aria-hidden="true" /><span>{label}</span>
              </button>
            ))}
          </div>
          <span className={"visual-source-tag" + (!unavailable && current.layout === "mirror" ? " is-hypothesis" : "")}>
            {!unavailable && current.layout === "mirror" ? "INVESTIGATOR VIEW" : "SOURCE SCANS"}
          </span>
        </div>

        <div className={"visual-stage" + (is3D ? " is-live" : "") + (ready && is3D ? " is-ready" : "")} ref={stage}>
          {!is3D && (
            <div key={sourceId} className={"visual-preview is-" + current.layout + (unavailable ? " is-fallback" : "")}>
              {!unavailable && current.layout !== "mirror" && (
                <div className="visual-paper is-companion" style={{ aspectRatio: source.width / source.height }}>
                  <img src={visualPageUrl(companion, current.source)} alt="" loading="lazy" decoding="async" width={source.width} height={source.height} />
                </div>
              )}
              <div className="visual-paper is-main" style={{ aspectRatio: source.width / source.height }}>
                <img src={visualPageUrl(current.page, current.source)} alt={`Retained source scan of printed page ${current.page}, ${source.name}`} loading="lazy" decoding="async" width={source.width} height={source.height} />
              </div>
              {!unavailable && current.layout === "mirror" && (
                <div className="visual-paper is-reflection" style={{ aspectRatio: source.width / source.height }}>
                  <img src={visualPageUrl(current.page, current.source)} alt="" loading="lazy" decoding="async" width={source.width} height={source.height} />
                </div>
              )}
            </div>
          )}

          {is3D && (
            <SceneBoundary key={attempt} onFailure={handleFailure}>
              <Suspense fallback={<div className="visual-module-loading" role="status">Preparing the 3D view…</div>}>
                <VisualScene key={sourceId} view={current} resetToken={reset} zoomRequest={zoom}
                  descriptionId={instructionsId} onProgress={handleProgress} onReady={handleReady}
                  onFailure={handleFailure} onExit={stop} />
              </Suspense>
            </SceneBoundary>
          )}

          <div className="visual-stage-label" aria-live="polite">
            <span>{stageLabel}</span><small>{modeLabel}</small>
          </div>

          {!is3D && (
            <div className="visual-start-panel">
              {unavailable && <p role="status">3D is unavailable here. You can still inspect the source scan.</p>}
              <button type="button" className="visual-start" ref={startButton} onClick={start}>
                <Maximize2 size={18} aria-hidden="true" />{unavailable ? "Try 3D again" : "Explore in 3D"}
                <ArrowUpRight size={19} aria-hidden="true" />
              </button>
              {!unavailable && <span>Drag. Zoom. Look closer.</span>}
            </div>
          )}

          {is3D && !ready && (
            <div className="visual-loading" role="status" aria-live="polite">
              <span>Loading source scans · {progress.loaded}/{progress.total}</span>
              <progress value={progress.loaded} max={Math.max(1, progress.total)} aria-label="Source scans loaded" />
            </div>
          )}

          {is3D && (
            <div className="visual-camera-control" role="group" aria-label="3D camera controls">
              <button type="button" onClick={() => changeZoom(1)} disabled={!ready} aria-label="Zoom in" title="Zoom in"><Plus size={17} /></button>
              <button type="button" onClick={() => changeZoom(-1)} disabled={!ready} aria-label="Zoom out" title="Zoom out"><Minus size={17} /></button>
              <button type="button" onClick={() => setReset((value) => value + 1)} aria-label="Reset 3D view" title="Reset view"><RotateCcw size={16} /></button>
            </div>
          )}
        </div>

        <div className="visual-page-strip">
          <span className="visual-page-label">PRINTED PAGE</span>
          <div className="visual-page-buttons" role="group" aria-label="Choose a printed source page">
            {source.pages.map((page) => (
              <button type="button" key={page} aria-pressed={current.page === page}
                aria-label={`Inspect printed page ${page}`} onClick={() => selectView({ ...current, page })}>{page}</button>
            ))}
          </div>
          {is3D && <button type="button" className="visual-flat-button" onClick={stop}>Back to scan</button>}
        </div>
      </div>

      <div className="visual-lab-caption">
        <p>
          {unavailable ? `Source scan of page ${current.page}. The full scan remains available through the link.`
            : current.layout === "mirror" ? "A source page and its horizontal reflection. An investigator hypothesis; no extraction is applied."
            : current.layout === "stack" ? `${source.pages.length} source scans separated for inspection. The spacing is a viewing aid.`
              : "Source pages in printed sequence. The display arrangement adds no research conclusion."}
          {current.source === "funky" && " Issue and publication date unverified."}
        </p>
        <div>
          <a href={visualPageUrl(current.page, current.source)} target="_blank" rel="noreferrer">Open scan {current.page}<ArrowUpRight size={14} /></a>
          <a href={source.provenance}>Source provenance<ArrowUpRight size={14} /></a>
          {!current.source && <a href="/lab/index.html" target="_blank" rel="noreferrer">Archived 3D layers<ArrowUpRight size={14} /></a>}
        </div>
      </div>
      <p className="visual-keyboard-help" id={instructionsId}>
        {is3D ? "Drag to orbit · scroll or pinch to zoom · two fingers to pan. Keyboard: focus the view, use arrow keys to orbit, +/− to zoom, 0 to reset, Esc to return to the scan."
          : "Choose a page to inspect. The interactive model loads when you select Explore in 3D."}
      </p>
    </section>
  );
}

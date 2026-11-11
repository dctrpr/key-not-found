import { useEffect, useRef, useState } from 'react';
import { ArrowDownToLine, ArrowUpRight, Box, ChevronLeft, ChevronRight, Pause, Play } from 'lucide-react';
import useLiveVisualJournal from '../hooks/useLiveVisualJournal';
import type { VisualJournalEntry as Entry } from '../lib/visualJournal';
import { followHashLinks } from '../lib/hashLinks';
import type { VisualLabView } from './VisualLab';
import './VisualJournal.css';

const formatNumber = (n: number) => n.toLocaleString('en-GB');
const date = (s: string) => new Date(s).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
const clock = (s: string) => new Date(s).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' });

export function VisualFrame({ entry, number }: { entry: Entry; number: number }) {
  const lime = '#d6ff3c', paper = '#f4f1e8', muted = '#aaa79d';
  const isSavedReadingReview = entry.id === 't01-saved-reading-review-result';
  const isStencilSourceModel = entry.id === 'g02-joint-source-model';
  const isStencilShapeCheck = entry.id === 'g02-stencil-shape-reachability';
  const isSharedQueryCheck = entry.id === 'g02-shared-query-sensitivity';
  const isPaperEdgeScreen = entry.id === 'g02-paper-edge-visibility';
  const isMirrorGlyphReview = entry.id === 'g07-mirror-glyph-orientation';
  const isFullPageGlyphReview = entry.id === 'issue24-full-page-glyph-review';
  const isSecondScanHeadingReview = entry.id === 'issue24-second-scan-heading-review';
  const isLineStartAudit = entry.id === 'issue24-line-start-audit';
  const isHeadingPixelMatch = entry.id === 'issue24-heading-pixel-match';
  const isHeadingScanTransfer = entry.id === 'issue24-heading-scan-transfer';
  return <svg viewBox="0 0 900 440" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="visual-frame-title visual-frame-description">
    <title id="visual-frame-title">{entry.title}</title>
    <desc id="visual-frame-description">{entry.metrics.map(m => `${formatNumber(m.value)} ${m.label}`).join('; ')}. {entry.result}</desc>
    <rect width="900" height="440" fill="#0e0e0d" />
    <g fontFamily="Arial, sans-serif">
      <rect x="35" y="31" width="8" height="8" fill={lime}/>
      <text x="54" y="39" fill={paper} fontSize="11" letterSpacing="2">KEY NOT FOUND / RESEARCH FRAME {String(number).padStart(2, '0')}</text>
      <text x="865" y="39" textAnchor="end" fill={muted} fontSize="11">{entry.completedAtUTC.slice(0, 10)} · UNSOLVED</text>
      {entry.diagram === 'review' ? <>
        <text x="40" y="101" fill={paper} fontSize="26" fontWeight="700">Read the 40 orange-mask texts.</text>
        <text x="40" y="130" fill={muted} fontSize="13">40 historical texts · 8 physical-pair readings · 32 other-pair controls</text>
        {entry.metrics.map((metric, i) => <g key={metric.label}>
          <rect x={40 + i * 288} y="175" width="244" height="140" fill="#191917" stroke={i === 2 ? lime : '#45453c'}/>
          <text x={60 + i * 288} y="243" fill={i === 2 ? lime : paper} fontSize="47" fontWeight="700">{formatNumber(metric.value)}</text>
          <text x={60 + i * 288} y="282" fill={muted} fontSize="13">{metric.label}</text>
        </g>)}
        <text x="40" y="351" fill={paper} fontSize="14">All complete outputs read. Historical source limits remain.</text>
        <text x="40" y="375" fill={muted} fontSize="12">Nonblind AI judgment. No new cipher run or formal message exclusion.</text>
      </> : entry.diagram === 'history' ? <>
        <text x="40" y="101" fill={paper} fontSize="26" fontWeight="700">The history check.</text>
        <text x="40" y="130" fill={muted} fontSize="13">Five constructions. Two providers. One fixed, read-only check.</text>
        <text x="600" y="167" textAnchor="middle" fill={muted} fontSize="11">BLOCKSTREAM</text>
        <text x="763" y="167" textAnchor="middle" fill={muted} fontSize="11">MEMPOOL.SPACE</text>
        {['P2PKH · uncompressed', 'P2PKH · compressed', 'P2SH–P2WPKH', 'P2WPKH', 'P2TR · key path'].map((label, i) => <g key={label}>
          <line x1="40" x2="860" y1={190 + i * 36} y2={190 + i * 36} stroke="#34342e"/>
          <text x="48" y={213 + i * 36} fill={paper} fontSize="14">{label}</text>
          {[600, 763].map(x => <g key={x}><circle cx={x - 27} cy={208 + i * 36} r="4" fill={lime}/><text x={x - 13} y={213 + i * 36} fill={lime} fontSize="13">0 history</text></g>)}
        </g>)}
      </> : entry.diagram === 'support' ? <>
        <text x="40" y="101" fill={paper} fontSize="26" fontWeight="700">Source pixels. Checked memberships.</text>
        <text x="40" y="130" fill={muted} fontSize="13">Native source → candidate layers → independent token proof</text>
        {entry.metrics.map((metric, i) => <g key={metric.label}>
          <rect x={40 + i * 288} y="175" width="244" height="140" fill="#191917" stroke={i === 1 ? lime : '#45453c'}/>
          <text x={60 + i * 288} y="243" fill={i === 1 ? lime : paper} fontSize="47" fontWeight="700">{formatNumber(metric.value)}</text>
          <text x={60 + i * 288} y="282" fill={muted} fontSize="13">{metric.label}</text>
        </g>)}
        <text x="40" y="351" fill={paper} fontSize="14">Two pilot rows accepted. 1,236 token memberships remain unaccepted.</text>
        <text x="40" y="375" fill={muted} fontSize="12">Inverse-field joins remain unresolved. No new decoding result.</text>
      </> : entry.diagram === 'measurement' ? <>
        <text x="40" y="101" fill={paper} fontSize="26" fontWeight="700">Check the measurement first.</text>
        <text x="40" y="130" fill={muted} fontSize="13">All source rows · original detector · first-guard comparison</text>
        {entry.metrics.map((metric, i) => <g key={metric.label}>
          <rect x={40 + i * 288} y="175" width="244" height="140" fill="#191917" stroke={i === 2 ? lime : '#45453c'}/>
          <text x={60 + i * 288} y="243" fill={i === 2 ? lime : paper} fontSize="47" fontWeight="700">{formatNumber(metric.value)}</text>
          <text x={60 + i * 288} y="282" fill={muted} fontSize="13">{metric.label}</text>
        </g>)}
        <text x="40" y="351" fill={paper} fontSize="15">38 rows still fail the original optical guards.</text>
        <text x="40" y="375" fill={muted} fontSize="12">Diagnostics only. No gap bits, decoding or repaired-coverage claim.</text>
      </> : entry.diagram === 'reading' ? <>
        <text x="40" y="101" fill={paper} fontSize="26" fontWeight="700">Three direct readings.</text>
        <text x="40" y="130" fill={muted} fontSize="13">One frozen source · global order · no extra transforms</text>
        {['First words', 'Odd whole lines', 'Even-line control'].map((label, i) => <g key={label}>
          <rect x={40 + i * 288} y="166" width="244" height="136" fill="#191917" stroke="#45453c"/>
          <text x={60 + i * 288} y="198" fill={muted} fontSize="13">{label}</text>
          <text x={60 + i * 288} y="253" fill={paper} fontSize="43" fontWeight="700">{[111, 56, 55][i]}</text>
          <text x={60 + i * 288} y="280" fill={muted} fontSize="12">{i === 0 ? 'literal word chunks' : 'complete physical rows'}</text>
        </g>)}
        {entry.metrics.map((metric, i) => <text key={metric.label} x={40 + i * 288} y="338" fill={paper} fontSize="15">{formatNumber(metric.value)} <tspan fill={muted}>{metric.label}</tspan></text>)}
        <text x="40" y="370" fill={muted} fontSize="12">Full-output AI review is exploratory recognition, not a cipher exclusion.</text>
      </> : entry.diagram === 'source' ? <>
        <text x="40" y="101" fill={paper} fontSize="26" fontWeight="700">The source, before the test.</text>
        <text x="40" y="130" fill={muted} fontSize="13">Funky Upheaval · actual scans in the page viewer · issue and date unverified</text>
        {[107, 108, 109, 110, 111, 112].map((page, i) => <g key={page}>
          <rect x={40 + i * 103} y="164" width="85" height="116" fill="#191917" stroke={lime}/>
          <text x={82 + i * 103} y="214" textAnchor="middle" fill={paper} fontSize="24">{page}</text>
          <text x={82 + i * 103} y="248" textAnchor="middle" fill={muted} fontSize="10">{i === 0 ? 'OPENER' : i === 5 ? 'ARTWORK' : 'TEXT'}</text>
        </g>)}
        <line x1="679" x2="679" y1="164" y2="280" stroke="#45453c" strokeDasharray="4 4"/>
        <text x="772" y="203" textAnchor="middle" fill={muted} fontSize="13">2 adjacent ads</text>
        <text x="772" y="230" textAnchor="middle" fill={paper} fontSize="12">Kept separately.</text>
        <text x="772" y="252" textAnchor="middle" fill={muted} fontSize="11">Outside this page view.</text>
        {entry.metrics.map((metric, i) => <text key={metric.label} x={40 + i * 288} y="335" fill={paper} fontSize="15">{formatNumber(metric.value)} <tspan fill={muted}>{metric.label}</tspan></text>)}
        <text x="40" y="367" fill={muted} fontSize="12">Source curation only. No new decoding or cryptographic check in this frame.</text>
      </> : <>
        <text x="40" y="101" fill={paper} fontSize="26" fontWeight="700">{entry.title}</text>
        <text x="40" y="130" fill={muted} fontSize="13">{isHeadingScanTransfer ? 'Ordinary print → held-out geometry → eligibility for faint-pixel scoring' : isHeadingPixelMatch ? 'Native pixels · same search for each control · held-out body regions' : isLineStartAudit ? 'Printed lines → independent readings → source comparison' : isSecondScanHeadingReview ? 'Native crops → locked page 74 readings → page 75 reference' : isFullPageGlyphReview ? 'Native scan tiles → independent visual marks → source comparison' : isMirrorGlyphReview ? 'Upright ink and its reflection → independent visual marks' : isPaperEdgeScreen ? 'Native photographs → independent marks → agreed crossings' : isSharedQueryCheck ? 'One offset per leaf → paired direction choices → pattern check' : isStencilShapeCheck ? 'Registered stencil word choices → literal format patterns' : isStencilSourceModel ? 'Frozen word centers → joint colors → membership bounds' : isSavedReadingReview ? 'Saved texts → two AI contexts → reported nonrecognition' : 'Registered input → format checks → recorded outcome'}</text>
        {entry.metrics.map((metric, i) => <g key={metric.label}>
          <rect x={40 + i * 288} y="190" width="244" height="132" rx="1" fill={i === 2 ? lime : '#191917'} stroke={i === 2 ? lime : '#45453c'}/>
          <text x={61 + i * 288} y="251" fill={i === 2 ? '#0e0e0d' : paper} fontSize="49" fontWeight="700" letterSpacing="-2">{formatNumber(metric.value)}</text>
          <text x={62 + i * 288} y="288" fill={i === 2 ? '#30341e' : muted} fontSize="13">{metric.label}</text>
          {isSharedQueryCheck && i === 1 ? <text x="590" y="262" textAnchor="middle" fill={muted} fontSize="18">+</text> :
            i < 2 && !(isHeadingPixelMatch && i === 1) && <path d={`M ${294 + i * 288} 256 h 18 m -5 -5 l 5 5 -5 5`} stroke={muted} fill="none"/>}
        </g>)}
        {isHeadingScanTransfer ? <>
          <text x="40" y="350" fill={paper} fontSize="14">Page 75 passes its held-out check. Page 74 falls short.</text>
          <text x="40" y="375" fill={muted} fontSize="12">The faint trace is still unscored in this transfer.</text>
        </> : isHeadingPixelMatch ? <>
          <text x="40" y="350" fill={paper} fontSize="14">A shared shift holds locally in the sharper scan.</text>
          <text x="40" y="375" fill={muted} fontSize="12">The source of the faint marks remains unresolved.</text>
        </> : isLineStartAudit ? <>
          <text x="40" y="350" fill={paper} fontSize="14">A line break can change the words a first-word rule reads.</text>
          <text x="40" y="375" fill={muted} fontSize="12">The report preserves the matching criteria and unresolved rows.</text>
        </> : isSecondScanHeadingReview ? <>
          <text x="40" y="350" fill={paper} fontSize="14">The page 74 judgments were locked before page 75 was shown.</text>
          <text x="40" y="375" fill={muted} fontSize="12">The comparison uses the lower-resolution source images.</text>
        </> : isFullPageGlyphReview ? <>
          <text x="40" y="350" fill={paper} fontSize="14">The faint heading is consistent with show-through.</text>
          <text x="40" y="375" fill={muted} fontSize="12">The visual comparison leaves physical alignment unmeasured.</text>
        </> : isMirrorGlyphReview ? <>
          <text x="40" y="350" fill={paper} fontSize="14">Each pair shows the same printed pixels in two orientations.</text>
          <text x="40" y="375" fill={muted} fontSize="12">The review covers the saved detector windows.</text>
        </> : isPaperEdgeScreen ? <>
          <text x="40" y="350" fill={paper} fontSize="14">The marks locate visible paper edges in the photographs.</text>
          <text x="40" y="375" fill={muted} fontSize="12">Physical alignment still needs a separate measurement.</text>
        </> : isSharedQueryCheck ? <>
          <text x="40" y="350" fill={paper} fontSize="14">The remaining patterns are syntax only.</text>
          <text x="40" y="375" fill={muted} fontSize="12">The offsets were modeled. Physical alignment was not measured.</text>
        </> : isStencilShapeCheck ? <>
          <text x="40" y="350" fill={paper} fontSize="14">Eight languages admitted WIF or minikey syntax.</text>
          <text x="40" y="375" fill={muted} fontSize="12">No hex64 or BIP39 pattern appeared in the registered model.</text>
        </> : <text x="40" y="356" fill={muted} fontSize="12">{isStencilSourceModel ? 'Source model only. Uncertain memberships remain options. No decoding or key checks.' : isSavedReadingReview ? 'Subjective review. Prior exposure is disclosed. No new format checks or formal message exclusion.' : 'Each count is tied to the frozen result. Read the test for its exact scope and limits.'}</text>}
      </>}
      <line x1="35" x2="865" y1="397" y2="397" stroke="#34342e"/>
      <text x="40" y="420" fill={muted} fontSize="10">SOURCE {entry.source.sha256.slice(0, 16)} · {entry.completedAtUTC} · SCHEMATIC</text>
      <text x="860" y="420" textAnchor="end" fill={paper} fontSize="11">keynotfound.com</text>
    </g>
  </svg>;
}

export default function VisualJournal({ onOpenView }: { onOpenView: (view: VisualLabView) => void }) {
  const journal = useLiveVisualJournal();
  const entries = useRef(journal.entries);
  const seenFrames = useRef(journal.entries.length);
  entries.current = journal.entries;
  const [index, setIndex] = useState(journal.entries.length - 1);
  const [playing, setPlaying] = useState(false);
  const entry: Entry = journal.entries[index];
  const frameStart = Math.max(0, Math.min(index - 1, journal.entries.length - 3));
  useEffect(() => followHashLinks(hash => {
    const match = /^#visual-([a-z0-9-]+)$/.exec(hash);
    const i = match ? entries.current.findIndex(e => e.id === match[1]) : -1;
    if (i >= 0) {
      setIndex(i); setPlaying(false);
      document.getElementById('visual-updates')?.scrollIntoView({ block: 'start', behavior: 'instant' });
    }
  }), []);
  useEffect(() => {
    // Resolve a shared link that was newer than this tab's bundled snapshot.
    // Existing selections stay in place when other frames are published.
    const match = /^#visual-([a-z0-9-]+)$/.exec(window.location.hash);
    const i = match ? journal.entries.findIndex(e => e.id === match[1]) : -1;
    if (i >= seenFrames.current) {
      setIndex(i); setPlaying(false);
      document.getElementById('visual-updates')?.scrollIntoView({ block: 'start', behavior: 'instant' });
    }
    seenFrames.current = journal.entries.length;
  }, [journal.entries]);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setTimeout(() => {
      if (index === journal.entries.length - 1) setPlaying(false);
      else setIndex(index + 1);
    }, 6500);
    return () => window.clearTimeout(timer);
  }, [playing, index, journal.entries.length]);
  const choose = (i: number) => {
    setIndex(i); setPlaying(false);
    window.history.replaceState(null, '', '#visual-' + journal.entries[i].id);
  };
  return <section className="visual-journal" id="visual-updates" aria-labelledby="visual-journal-title">
    <div className="vj-heading"><div><span className="vj-eyebrow">THE VISUAL LOG</span><h2 id="visual-journal-title">The work, frame by frame.</h2></div><p>Dated views of sources, tests and results. Each frame links to the evidence. New published frames appear here automatically.</p></div>
    <div className="vj-layout">
      <div className="vj-player">
        <VisualFrame entry={entry} number={index + 1}/>
        <div className="vj-playback"><button type="button" onClick={() => { if (!playing && index === journal.entries.length - 1) setIndex(0); setPlaying(!playing); }} aria-label={playing ? 'Pause visual recap' : 'Play visual recap'}>{playing ? <Pause size={16}/> : <Play size={16}/>}<span>{playing ? 'Pause' : 'Play recap'}</span></button><span>FRAME {index + 1} / {journal.entries.length}</span><div><button type="button" disabled={index === 0} onClick={() => choose(index - 1)} aria-label="Previous research frame"><ChevronLeft size={18}/></button><button type="button" disabled={index === journal.entries.length - 1} onClick={() => choose(index + 1)} aria-label="Next research frame"><ChevronRight size={18}/></button></div></div>
      </div>
      <div className="vj-caption" aria-live="polite">
        <time dateTime={entry.completedAtUTC}>{date(entry.completedAtUTC)} · {clock(entry.completedAtUTC)} UTC</time>
        <dl className="vj-mobile-metrics">{entry.metrics.map(m => <div key={m.label}><dt>{m.label}</dt><dd>{formatNumber(m.value)}</dd></div>)}</dl>
        <h3>{entry.title}</h3><p>{entry.summary}</p><p className="vj-result">{entry.result}</p>
        <div className="vj-links"><a href={entry.evidence} target="_blank" rel="noreferrer">Read the evidence <ArrowUpRight size={15}/></a><button type="button" onClick={() => onOpenView(entry.scene as VisualLabView)}><Box size={15}/> Explore the pages</button><a href={`/research/visuals/${entry.id}.svg`} target="_blank" rel="noreferrer">Enlarge frame <ArrowUpRight size={15}/></a></div>
        <small>{entry.sceneNote}</small>
      </div>
    </div>
    {entry.exhibits && <div className="vj-source-exhibits" aria-label="Source and diagnostic excerpts">{entry.exhibits.map(exhibit => <a key={exhibit.path} href={exhibit.path} target="_blank" rel="noreferrer"><span>{exhibit.label}<ArrowUpRight size={14}/></span><img src={exhibit.path} alt={exhibit.label} width={exhibit.width || 2544} height={exhibit.height || 58} loading="lazy"/><small>Open full-resolution excerpt</small></a>)}</div>}
    <div className="vj-frames" aria-label="Nearby research frames">{journal.entries.slice(frameStart, frameStart + 3).map((e, offset) => { const i = frameStart + offset; return <button type="button" key={e.id} aria-pressed={i === index} onClick={() => choose(i)}><span>{String(i + 1).padStart(2, '0')} / {clock(e.completedAtUTC)}</span><strong>{e.title}</strong></button>; })}</div>
    {journal.entries.length > 3 && <label className="vj-date-picker">Jump to a recorded update<select value={index} onChange={event => choose(Number(event.target.value))}>{journal.entries.map((e, i) => <option key={e.id} value={i}>{date(e.completedAtUTC)} · {clock(e.completedAtUTC)} · {e.title}</option>)}</select></label>}
    <div className="vj-export"><span>Keep the visuals with the research.</span><div>{index < journal.entries.length - 1 && <button type="button" onClick={() => choose(journal.entries.length - 1)}>Latest frame <ChevronRight size={14}/></button>}<a href={`/research/visuals/${entry.id}.svg`} download>Save frame · SVG <ArrowDownToLine size={14}/></a><a href="/research/visuals/journal.json" download>Scene data · JSON <ArrowDownToLine size={14}/></a></div></div>
  </section>;
}

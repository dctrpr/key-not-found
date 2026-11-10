import { useEffect, useRef, useState } from "react";
import { ArrowDown, ArrowDownToLine, ChevronDown, Play } from "lucide-react";
import "./ExplainerFilm.css";

const FILM = "/media/key404-film.mp4";
const POSTER = "/media/key404-film-poster.jpg";
const CAPTIONS = "/media/key404-film.vtt";
const TRANSCRIPT = "/media/key404-film-transcript.txt";

// The film's on-screen statements, in order. The film itself is rendered by
// scripts/explainer; when its wording changes, change this and public/media.
const LINES: { at: string; text: string; method?: string }[] = [
  {
    at: "0:00",
    text: "Somewhere in these 6,162 printed characters there might be a Bitcoin private key.",
  },
  {
    at: "0:04",
    text: "Max Keiser, public post, 4 March 2023. In 2023 he said he hid a Bitcoin private key in this magazine article.",
  },
  {
    at: "0:08",
    text: "The claim: 20 BTC, claimed by Max Keiser. Not independently verified. No authenticated prize address is known.",
  },
  {
    at: "0:12",
    text: "One solver, a side project. I found this puzzle in 2023. I’ve been working on it ever since.",
  },
  {
    at: "0:18",
    method: "faithful-lines",
    text: "Read every other printed line. 142 printed lines; parity, edge and reversal variants. No valid key in the recorded streams. Tested, no result.",
  },
  {
    at: "0:22",
    method: "firstword-sha256",
    text: "Hash the first word of every line. 36 first-word strings, one SHA-256 each; 180 addresses looked up. Zero transactions. Tested, no result.",
  },
  {
    at: "0:25",
    method: "corrected-orange",
    text: "Read it in a mirror. Fold the pages. 20 page pairs; 80 reflected streams. No exact WIF or 64-hex output. Tested, no result. “An earlier overlap graph looked promising” is struck out: claim invalidated, kept on record.",
  },
  {
    at: "0:30",
    method: "highlight-lines",
    text: "Follow the orange highlights. 46 highlighted fragments; 540 declared variants. One weak checksum hit. Zero transactions. Tested, no result. Plus 350 highlight mnemonics, 1,050 addresses, no activity.",
  },
  {
    at: "0:34",
    method: "numeric-256",
    text: "Turn selected printed numbers into bits. 24 selected numbers, 256 bits; 20 addresses looked up. Zero transaction activity. Tested, no result.",
  },
  {
    at: "0:38",
    text: "15 recorded methods. I still haven’t found the key. 10 tested, no result; 1 claim corrected; 3 partial leads; 1 open question. “No result” covers only the candidates tested. It does not close the wider idea.",
  },
  {
    at: "0:42",
    text: "So I put all of it in public: 8 source pages, the exact printed lines, 15 method records with scope, evidence and limits, every dead end and correction, the scripts and their exact output. Anyone, or any AI, can pick it up from here. Help is optional. No token is needed.",
  },
  {
    at: "0:48",
    text: "Token not launched. No official contract or trading link. Planned: if it launches, creator fees actually received fund AI research runs, with method, cost and result published. Committed: if this project recovers the prize BTC, 100% funds $KEY404 buybacks. Unknown: the prize and its recovery are unverified.",
  },
  {
    at: "0:56",
    text: "KEY NOT FOUND. One solver. Since 2023. The work is public. Help is optional. Reading, testing and correcting need no token.",
  },
];

export default function ExplainerFilm() {
  const player = useRef<HTMLVideoElement>(null);
  const written = useRef<HTMLDetailsElement>(null);
  const [started, setStarted] = useState(false);

  // Nothing of the film loads with the page: the poster is a lazy image and
  // the film is fetched only when it is played. Playing is always a click.
  const start = () => {
    setStarted(true);
    // If the browser declines, the player's own controls are there to use.
    player.current?.play().catch(() => {});
  };
  useEffect(() => {
    if (started) player.current?.focus();
  }, [started]);

  // The film moves fast. With reduced motion requested, the written version
  // starts open beside it.
  useEffect(() => {
    if (
      written.current &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    )
      written.current.open = true;
  }, []);

  return (
    <section className="film" id="film" aria-labelledby="film-title">
      <div className="film-layout">
        <div className="film-copy">
          <p className="film-label">
            <i className="status-swatch" aria-hidden="true" /> THE FILM · 62
            SECONDS
          </p>
          <h2 id="film-title">The case in 62 seconds.</h2>
          <p className="film-lede">
            The claim, five of the ways I’ve read these pages, and where it
            stands. Nothing is spoken, so it works with the sound off.
          </p>
          <p className="film-motion-note">
            The film has fast-moving text. The written version is open below.
          </p>
        </div>
        <figure className="film-figure">
          <div className="film-frame">
            <video
              ref={player}
              controls={started}
              playsInline
              preload="none"
              poster={started ? POSTER : undefined}
              width={1920}
              height={1080}
              tabIndex={started ? 0 : -1}
              aria-hidden={!started}
              aria-label="The case in 62 seconds. A film with no speech; the written version follows."
            >
              <source src={FILM} type="video/mp4" />
              <track
                kind="captions"
                srcLang="en"
                label="English"
                src={CAPTIONS}
              />
              <a href={FILM}>Download the film (MP4, 29 MB)</a>
            </video>
            {!started && (
              <button
                className="film-start"
                onClick={start}
                aria-label="Play the film: 62 seconds, with a soundtrack and no speech"
              >
                <img
                  src={POSTER}
                  alt=""
                  width={1920}
                  height={1080}
                  loading="lazy"
                  decoding="async"
                />
                <span className="film-play" aria-hidden="true">
                  <Play />
                </span>
              </button>
            )}
          </div>
          <figcaption>
            <span>NO SPEECH · CAPTIONS AVAILABLE</span>
            <a href={FILM} download>
              Download · MP4 · 29 MB <ArrowDownToLine size={14} />
            </a>
          </figcaption>
        </figure>
      </div>
      <details className="film-written" ref={written}>
        <summary>
          <span>Read it instead</span>
          <small>What the film says on screen, in order</small>
          <ChevronDown size={18} />
        </summary>
        <ol className="film-lines">
          {LINES.map((line) => (
            <li key={line.at}>
              <span className="film-time">{line.at}</span>
              <p>{line.text}</p>
              {line.method && (
                <a className="film-method" href={"#method-" + line.method}>
                  {line.method} <ArrowDown size={12} />
                </a>
              )}
            </li>
          ))}
        </ol>
        <p className="film-files">
          <a href={TRANSCRIPT}>Full transcript (TXT)</a>
          <a href={CAPTIONS}>Timed captions (WebVTT)</a>
          <span>
            The film is a snapshot from 10 Nov 2026. The{" "}
            <a href="#ledger">ledger</a> has the current record.
          </span>
        </p>
      </details>
    </section>
  );
}

import { useEffect, useRef, useState } from "react";
import { ArrowDownToLine, Play } from "lucide-react";
import "./ExplainerFilm.css";

const FILM = "/media/key404-film.mp4";
const POSTER = "/media/key404-film-poster.jpg";
const CAPTIONS = "/media/key404-film.vtt";
const TRANSCRIPT = "/media/key404-film-transcript.txt";

export default function ExplainerFilm() {
  const player = useRef<HTMLVideoElement>(null);
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

  return (
    <section className="film" id="film" aria-labelledby="film-title">
      <div className="film-layout">
        <h2 id="film-title">The case.</h2>
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
              aria-label="The case in 62 seconds. A film with no speech; captions and transcript available."
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
            <span>62 SECONDS</span>
            <div className="film-downloads">
              <a href={TRANSCRIPT}>Transcript</a>
              <a href={FILM} download>
                Download · MP4 · 29 MB <ArrowDownToLine size={14} />
              </a>
            </div>
          </figcaption>
        </figure>
      </div>
    </section>
  );
}

import { ArrowDownToLine, ArrowUpRight, ChevronDown } from "lucide-react";
import type { ResearchMethod, ResearchUpdate } from "../lib/researchState";
import "./ResearchFeed.css";

const RECAP_UPDATE = "march-announcement-photo-lineage";
const RECAP = "/media/key404-announcement-recap";

const dateFormatter = new Intl.DateTimeFormat("en-GB", {
  day: "2-digit",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});
const timeFormatter = new Intl.DateTimeFormat("en-GB", {
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hourCycle: "h23",
  timeZone: "UTC",
});

const tone = (category: string) =>
  ({
    TESTED: " is-tested",
    CORRECTION: " is-correction",
    "SOURCE FIX": " is-source",
    "IN PROGRESS": " is-active",
  })[category.trim().toUpperCase()] || "";

export default function ResearchFeed({
  entries,
  methods,
  evidenceLink,
}: {
  entries: ResearchUpdate[];
  methods: ResearchMethod[];
  evidenceLink: (path: string) => string;
}) {
  const names = new Map(methods.map((method) => [method.id, method.title]));
  return (
    <ol className="research-feed" aria-label="Research tests and findings, newest first">
      {entries.map((entry) => {
        const hasRecap = entry.id === RECAP_UPDATE;
        const completed = entry.completedAtUTC
          ? new Date(entry.completedAtUTC)
          : null;
        const hasTime = completed !== null && Number.isFinite(completed.valueOf());
        return (
          <li key={entry.id}>
            <details
              className="research-run"
              id={"update-" + entry.id}
              data-category={entry.category}
              onToggle={hasRecap ? (event) => {
                if (!event.currentTarget.open) {
                  event.currentTarget.querySelector("video")?.pause();
                }
              } : undefined}
            >
              <summary>
                <span className="run-meta">
                  <span className={"note-category" + tone(entry.category)}>
                    {entry.category}
                  </span>
                  <time dateTime={hasTime ? entry.completedAtUTC : entry.date}>
                    <span>{dateFormatter.format(new Date(entry.date + "T12:00:00Z"))}</span>
                    <small>
                      {hasTime ? `${timeFormatter.format(completed)} UTC` : "Date recorded"}
                    </small>
                  </time>
                </span>
                <strong className="run-title">{entry.title}</strong>
                <span className="run-preview">{entry.body}</span>
                <span className="run-toggle" aria-hidden="true">
                  <ChevronDown size={18} />
                </span>
              </summary>
              <div className="run-detail">
                <p>{entry.body}</p>
                <div className="note-links">
                  <a className="text-link light" href={evidenceLink(entry.evidence)}>
                    Evidence &amp; reproduction <ArrowUpRight size={16} />
                  </a>
                  {entry.methodIds?.map((id) => (
                    <a className="run-method" key={id} href={"#method-" + id}>
                      {names.get(id) || id} <ArrowUpRight size={13} />
                    </a>
                  ))}
                </div>
                {hasRecap && (
                  <figure className="run-recap">
                    <video
                      controls
                      playsInline
                      preload="none"
                      poster={RECAP + "-poster.jpg"}
                      width={1920}
                      height={1080}
                      aria-label="Key Not Found research recap"
                    >
                      <source src={RECAP + ".mp4"} type="video/mp4" />
                      <track kind="captions" srcLang="en" label="English" src={RECAP + ".vtt"} />
                      <a href={RECAP + ".mp4"}>Open the recap video</a>
                    </video>
                    <figcaption>
                      <a className="text-link light" href={RECAP + "-transcript.txt"}>
                        Transcript
                      </a>
                      <a className="text-link light" href={RECAP + ".mp4"} download>
                        Download MP4 <ArrowDownToLine size={15} />
                      </a>
                    </figcaption>
                  </figure>
                )}
              </div>
            </details>
          </li>
        );
      })}
    </ol>
  );
}

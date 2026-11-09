import {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type FormEvent,
} from "react";
import { npubEncode, neventEncode } from "nostr-tools/nip19";
import type { Event as NostrEvent } from "nostr-tools/pure";
import {
  DEFAULT_RELAYS,
  DEFAULT_ROOM_TAG,
  MAX_POST_LENGTH,
  getNostrSigner,
  mergeRoomEvent,
  normalizeRoomTag,
  publishToRelay,
  validRelayUrls,
  verifiedRoomEvent,
  type RelayState,
} from "./nostr-room";
import "./NostrRoom.css";

type NostrRoomProps = {
  roomTag?: string;
  title?: string;
  theme?: "dark" | "light";
  className?: string;
  relays?: readonly string[];
};

function shortIdentity(pubkey: string): string {
  const npub = npubEncode(pubkey);
  return npub.slice(0, 12) + "…" + npub.slice(-6);
}

function readableError(error: unknown, fallback: string): string {
  return error instanceof Error && error.message
    ? error.message.slice(0, 180)
    : fallback;
}

function noteContent(content: string) {
  return content.split(/(https?:\/\/[^\s<>]+)/g).map((part, index) => {
    if (/^https?:\/\//.test(part)) {
      try {
        const url = new URL(part);
        if (url.protocol === "https:" || url.protocol === "http:") {
          return (
            <a
              key={index}
              href={url.href}
              target="_blank"
              rel="noopener noreferrer nofollow"
            >
              {part}
            </a>
          );
        }
      } catch {
        /* Render invalid URLs as plain text. */
      }
    }
    return part;
  });
}

function useNostrRoom(roomTag: string, relayUrls: string[]) {
  const [events, setEvents] = useState<NostrEvent[]>([]);
  const [states, setStates] = useState<RelayState[]>([]);
  const [attempt, setAttempt] = useState(0);
  const sockets = useRef(new Map<string, WebSocket>());
  const activeRoom = useRef(roomTag);
  activeRoom.current = roomTag;

  useEffect(() => {
    setEvents([]);
  }, [roomTag]);

  useEffect(() => {
    let stopped = false;
    const timers = new Set<ReturnType<typeof setTimeout>>();
    const localSockets = new Map<string, WebSocket>();
    const subscription = "key404-" + Math.random().toString(36).slice(2, 12);
    setStates(relayUrls.map((url) => ({ url, phase: "connecting" })));

    const update = (url: string, next: Omit<RelayState, "url">) => {
      if (!stopped)
        setStates((previous) =>
          previous.map((state) =>
            state.url === url ? { url, ...next } : state,
          ),
        );
    };
    const schedule = (callback: () => void, delay: number) => {
      const timer = setTimeout(() => {
        timers.delete(timer);
        callback();
      }, delay);
      timers.add(timer);
      return timer;
    };

    const connect = (url: string, retries: number) => {
      if (stopped) return;
      update(url, { phase: "connecting" });
      let socket: WebSocket;
      try {
        socket = new WebSocket(url);
      } catch {
        update(url, { phase: "offline", detail: "Could not open this relay." });
        return;
      }
      localSockets.set(url, socket);
      sockets.current.set(url, socket);
      let restricted = false;
      let reachedEnd = false;
      const timeout = schedule(() => {
        if (!reachedEnd && socket.readyState !== WebSocket.CLOSED) {
          update(url, { phase: "offline", detail: "Reading timed out." });
          socket.close();
        }
      }, 12000);

      socket.addEventListener("open", () => {
        if (stopped) {
          socket.close();
          return;
        }
        update(url, { phase: "reading" });
        socket.send(
          JSON.stringify([
            "REQ",
            subscription,
            { kinds: [1], "#t": [roomTag], limit: 80 },
          ]),
        );
      });
      socket.addEventListener("message", (message) => {
        if (stopped) return;
        try {
          const frame = String(message.data);
          if (frame.length > 100_000) return;
          const data: unknown = JSON.parse(frame);
          if (!Array.isArray(data)) return;
          if (data[0] === "EVENT" && data[1] === subscription) {
            const event = verifiedRoomEvent(data[2], roomTag);
            if (event) setEvents((previous) => mergeRoomEvent(previous, event));
          } else if (data[0] === "EOSE" && data[1] === subscription) {
            reachedEnd = true;
            clearTimeout(timeout);
            timers.delete(timeout);
            update(url, { phase: "live" });
          } else if (data[0] === "CLOSED" && data[1] === subscription) {
            restricted = true;
            clearTimeout(timeout);
            timers.delete(timeout);
            update(url, {
              phase: "restricted",
              detail: String(
                data[2] || "This relay declined the subscription.",
              ).slice(0, 180),
            });
            socket.close();
          } else if (data[0] === "NOTICE" && typeof data[1] === "string") {
            if (!reachedEnd)
              update(url, { phase: "reading", detail: data[1].slice(0, 180) });
          }
        } catch {
          /* Invalid events and malformed relay frames never enter the feed. */
        }
      });
      socket.addEventListener("error", () => {
        if (!stopped && !restricted)
          update(url, {
            phase: "offline",
            detail: "Could not reach this relay.",
          });
      });
      socket.addEventListener("close", () => {
        clearTimeout(timeout);
        timers.delete(timeout);
        if (sockets.current.get(url) === socket) sockets.current.delete(url);
        if (stopped || restricted) return;
        update(url, {
          phase: "offline",
          detail:
            retries < 3
              ? "Reconnecting…"
              : "Unavailable. Use retry to reconnect.",
        });
        if (retries < 3)
          schedule(() => connect(url, retries + 1), 1500 * 2 ** retries);
      });
    };
    // Let StrictMode's initial cleanup run before opening real connections.
    schedule(() => relayUrls.forEach((url) => connect(url, 0)), 0);

    return () => {
      stopped = true;
      timers.forEach(clearTimeout);
      localSockets.forEach((socket, url) => {
        if (socket.readyState === WebSocket.OPEN)
          socket.send(JSON.stringify(["CLOSE", subscription]));
        socket.close();
        if (sockets.current.get(url) === socket) sockets.current.delete(url);
      });
    };
  }, [roomTag, relayUrls, attempt]);

  return {
    events,
    states,
    retry: () => setAttempt((value) => value + 1),
    openSockets: () =>
      [...sockets.current.values()].filter(
        (socket) => socket.readyState === WebSocket.OPEN,
      ),
    acceptPublished: (event: NostrEvent) => {
      if (activeRoom.current === roomTag)
        setEvents((previous) => mergeRoomEvent(previous, event));
    },
  };
}

export default function NostrRoom({
  roomTag = DEFAULT_ROOM_TAG,
  title = "A lead is better shared.",
  theme = "dark",
  className = "",
  relays = DEFAULT_RELAYS,
}: NostrRoomProps) {
  const tag = normalizeRoomTag(roomTag);
  const relayKey = relays.join("|");
  const relayUrls = useMemo(() => {
    const valid = validRelayUrls(relayKey.split("|"));
    return valid.length ? valid : [...DEFAULT_RELAYS];
  }, [relayKey]);
  const room = useNostrRoom(tag, relayUrls);
  const inputId = useId();
  const noticeId = useId();
  const [draft, setDraft] = useState("");
  const [identity, setIdentity] = useState<string | null>(null);
  const [busy, setBusy] = useState<"connecting" | "publishing" | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const alive = useRef(true);
  const copiedTimer = useRef<ReturnType<typeof setTimeout> | undefined>(
    undefined,
  );

  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
      clearTimeout(copiedTimer.current);
    };
  }, []);

  const liveCount = room.states.filter(
    (state) => state.phase === "live",
  ).length;
  const readingCount = room.states.filter(
    (state) => state.phase === "reading" || state.phase === "connecting",
  ).length;
  const connectionLabel =
    liveCount > 0
      ? liveCount + "/" + relayUrls.length + " relays live"
      : readingCount > 0 || room.states.length === 0
        ? "Connecting to the room"
        : "Room connection unavailable";

  async function connectSigner() {
    setError("");
    setNotice("");
    const signer = getNostrSigner();
    if (!signer) {
      setError(
        "No Nostr signer found. Open this page in a Nostr-enabled browser or add a NIP-07 signing extension, then connect again.",
      );
      return;
    }
    setBusy("connecting");
    try {
      const pubkey = await signer.getPublicKey();
      if (!/^[a-f0-9]{64}$/.test(pubkey))
        throw new Error("The signer returned an invalid public identity.");
      if (alive.current) {
        setIdentity(pubkey);
        setNotice("Connected. Review your note, then choose Sign & publish.");
      }
    } catch (cause) {
      if (alive.current)
        setError(
          readableError(
            cause,
            "Connection declined. You can still read the room.",
          ),
        );
    } finally {
      if (alive.current) setBusy(null);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    if (!identity) {
      await connectSigner();
      return;
    }
    const text = draft.trim();
    if (!text) {
      setError("Write a note before publishing.");
      return;
    }
    if (text.length > MAX_POST_LENGTH) {
      setError("Keep your note within " + MAX_POST_LENGTH + " characters.");
      return;
    }
    const signer = getNostrSigner();
    if (!signer) {
      setError(
        "Your Nostr signer is no longer available. Reconnect to continue.",
      );
      setIdentity(null);
      return;
    }
    if (room.openSockets().length === 0) {
      setError(
        "The relays are offline. Retry the room connection before publishing.",
      );
      return;
    }
    setBusy("publishing");
    setError("");
    setNotice("Approve this public note in your signer.");
    try {
      const content = text.toLowerCase().includes("#" + tag)
        ? text
        : text + "\n\n#" + tag;
      const template = {
        kind: 1,
        created_at: Math.floor(Date.now() / 1000),
        content,
        tags: [["t", tag]],
      };
      const signed = verifiedRoomEvent(await signer.signEvent(template), tag);
      if (
        !signed ||
        signed.pubkey !== identity ||
        signed.content !== content ||
        signed.created_at !== template.created_at ||
        JSON.stringify(signed.tags) !== JSON.stringify(template.tags)
      ) {
        throw new Error(
          "The signed note did not match your draft or connected identity. Reconnect and try again.",
        );
      }
      const sockets = room.openSockets();
      if (!sockets.length)
        throw new Error(
          "Connection lost. Your note was not sent; reconnect and try again.",
        );
      if (alive.current) setNotice("Waiting for relay acknowledgment…");
      const receipts = await Promise.all(
        sockets.map((socket) => publishToRelay(socket, signed)),
      );
      const accepted = receipts.filter((receipt) => receipt.accepted);
      if (!accepted.length) {
        const reason = receipts
          .map((receipt) => receipt.message)
          .filter(Boolean)[0];
        throw new Error(
          "No relay confirmed publication. " +
            (reason || "Your draft is still here."),
        );
      }
      if (alive.current) {
        room.acceptPublished(signed);
        setDraft((current) => (current === draft ? "" : current));
        setNotice(
          "Published. Accepted by " +
            accepted.length +
            " of " +
            receipts.length +
            " connected relays.",
        );
      }
    } catch (cause) {
      if (alive.current) {
        setNotice("");
        setError(
          readableError(
            cause,
            "Publication declined. Your draft is still here.",
          ),
        );
      }
    } finally {
      if (alive.current) setBusy(null);
    }
  }

  async function copyTag() {
    try {
      await navigator.clipboard.writeText("#" + tag);
      if (!alive.current) return;
      setCopied(true);
      clearTimeout(copiedTimer.current);
      copiedTimer.current = setTimeout(() => setCopied(false), 2500);
    } catch {
      setError(
        "Copy was unavailable. The full room tag is shown above; select it to copy.",
      );
    }
  }

  return (
    <section
      className={"nostr-room " + className}
      data-theme={theme}
      id="discussion"
      aria-labelledby={inputId + "-title"}
    >
      <div className="nostr-room__intro">
        <p className="nostr-room__eyebrow">
          <span aria-hidden="true">↗</span> The open channel
        </p>
        <h2 id={inputId + "-title"}>{title}</h2>
        <p>
          Found a pattern? Ruled one out? Leave the evidence where the next
          person can find it.
        </p>
        <div className="nostr-room__tagline">
          <code>#{tag}</code>
          <button
            type="button"
            className="nostr-room__text-button"
            onClick={copyTag}
            aria-label={"Copy room tag " + tag}
          >
            {copied ? "Copied ✓" : "Copy tag ↗"}
          </button>
        </div>
        <p className="nostr-room__public-note">
          A public Nostr room. Read freely. Use your own signer to post.
        </p>
        <a
          className="nostr-room__learn"
          href="https://njump.me/#get-started"
          target="_blank"
          rel="noopener noreferrer"
        >
          New to Nostr? Start here ↗
        </a>
      </div>

      <div className="nostr-room__panel">
        <div className="nostr-room__connection">
          <span
            className={"nostr-room__status-dot" + (liveCount ? " is-live" : "")}
            aria-hidden="true"
          />
          <span role="status" aria-live="polite">
            {connectionLabel}
          </span>
          <button
            type="button"
            className="nostr-room__text-button"
            onClick={room.retry}
            disabled={busy === "publishing"}
          >
            Retry relays
          </button>
        </div>

        <div
          className="nostr-room__feed"
          aria-label="Recent public investigation notes"
        >
          {room.events.length > 0 ? (
            <ol className="nostr-room__messages">
              {room.events.map((event) => {
                const noteLink =
                  "https://njump.me/" +
                  neventEncode({
                    id: event.id,
                    author: event.pubkey,
                    relays: relayUrls.slice(0, 2),
                  });
                const timestamp = new Date(event.created_at * 1000);
                return (
                  <li key={event.id} className="nostr-room__message">
                    <div className="nostr-room__message-meta">
                      <a
                        href={"https://njump.me/" + npubEncode(event.pubkey)}
                        target="_blank"
                        rel="noopener noreferrer"
                        title={npubEncode(event.pubkey)}
                      >
                        {shortIdentity(event.pubkey)}
                      </a>
                      <a
                        href={noteLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label="Open this signed note in a Nostr client"
                      >
                        <time
                          dateTime={timestamp.toISOString()}
                          title={timestamp.toLocaleString()}
                        >
                          {timestamp.toLocaleDateString(undefined, {
                            month: "short",
                            day: "numeric",
                          })}{" "}
                          ·{" "}
                          {timestamp.toLocaleTimeString(undefined, {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </time>{" "}
                        ↗
                      </a>
                    </div>
                    <p className="nostr-room__message-content">
                      {noteContent(event.content)}
                    </p>
                  </li>
                );
              })}
            </ol>
          ) : (
            <div className="nostr-room__empty">
              <span className="nostr-room__empty-mark" aria-hidden="true">
                [ &nbsp; ]
              </span>
              <h3>
                {liveCount
                  ? "The floor is open."
                  : readingCount || room.states.length === 0
                    ? "Listening for leads…"
                    : "The room is out of reach."}
              </h3>
              <p>
                {liveCount
                  ? "No notes found on the connected relays. Bring the first source, question, or useful dead end."
                  : readingCount || room.states.length === 0
                    ? "Checking public relays for real notes in this room."
                    : "Public relays may be temporarily unavailable. Retry the connection; no account is needed to read."}
              </p>
            </div>
          )}
        </div>

        <form className="nostr-room__composer" onSubmit={submit}>
          <div className="nostr-room__composer-heading">
            <label htmlFor={inputId}>Add a note to the case</label>
            {identity && (
              <button
                type="button"
                className="nostr-room__text-button nostr-room__identity"
                onClick={() => {
                  setIdentity(null);
                  setNotice("Disconnected from this page.");
                  setError("");
                }}
                disabled={busy !== null}
                title={npubEncode(identity)}
              >
                {shortIdentity(identity)} · Disconnect
              </button>
            )}
          </div>
          <textarea
            id={inputId}
            value={draft}
            onChange={(event) => {
              setDraft(event.target.value);
              if (error) setError("");
            }}
            placeholder="A clue, a source link, a test someone else can reproduce…"
            rows={3}
            maxLength={MAX_POST_LENGTH}
            disabled={busy === "publishing"}
            aria-describedby={noticeId}
          />
          <div className="nostr-room__composer-bottom">
            <p id={noticeId}>
              Public, signed, and tagged <span>#{tag}</span>.
            </p>
            <span
              className="nostr-room__character-count"
              aria-label={
                draft.length + " of " + MAX_POST_LENGTH + " characters"
              }
            >
              {draft.length}/{MAX_POST_LENGTH}
            </span>
            <button
              type="submit"
              className="nostr-room__publish"
              disabled={busy !== null || (identity !== null && !draft.trim())}
            >
              {busy === "publishing"
                ? "Publishing…"
                : busy === "connecting"
                  ? "Connecting…"
                  : identity
                    ? "Sign & publish ↗"
                    : "Connect Nostr ↗"}
            </button>
          </div>
          {notice && (
            <p className="nostr-room__notice" role="status">
              {notice}
            </p>
          )}
          {error && (
            <p className="nostr-room__error" role="alert">
              {error}
            </p>
          )}
        </form>

        <details className="nostr-room__relays">
          <summary>
            Relay connections <span aria-hidden="true">+</span>
          </summary>
          <ul>
            {room.states.map((state) => (
              <li key={state.url}>
                <span>{new URL(state.url).hostname}</span>
                <span>
                  {state.phase === "live"
                    ? "Live"
                    : state.phase === "reading"
                      ? "Reading"
                      : state.phase === "connecting"
                        ? "Connecting"
                        : state.phase === "restricted"
                          ? "Restricted"
                          : "Offline"}
                </span>
                {state.detail && <small>{state.detail}</small>}
              </li>
            ))}
          </ul>
          <p>
            Notes are fetched directly from these relays. Signatures prove
            authorship, not the accuracy of a claim.
          </p>
        </details>
      </div>
    </section>
  );
}

import {
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type FormEvent,
  type MouseEvent,
} from "react";
import { ExternalLink, MessageCircle, X } from "lucide-react";
import "./PublicChat.css";

type PublicChatProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  discordUrl: string;
  room?: string;
  repositoryUrl?: string;
};

type FrameState = "loading" | "loaded" | "slow" | "error";

export default function PublicChat({
  open,
  onOpenChange,
  discordUrl,
  room = "keiser-key-not-found",
  repositoryUrl = "https://github.com/dctrpr/key-not-found",
}: PublicChatProps) {
  const id = useId();
  const dialog = useRef<HTMLDialogElement>(null);
  const launcher = useRef<HTMLButtonElement>(null);
  const opener = useRef<HTMLElement | null>(null);
  const loadTimer = useRef<ReturnType<typeof setTimeout> | undefined>(
    undefined,
  );
  const [frameState, setFrameState] = useState<FrameState>("loading");
  const [frameAttempt, setFrameAttempt] = useState(0);
  const [nickname, setNickname] = useState("");
  const [joinedAlias, setJoinedAlias] = useState<string | null>(null);
  const [nicknameError, setNicknameError] = useState("");
  const roomName = room.trim() || "keiser-key-not-found";
  const encodedRoom = encodeURIComponent(roomName);
  const roomUrl = "https://tlk.io/" + encodedRoom;
  const embedUrl = new URL("https://embed.tlk.io/" + encodedRoom);
  embedUrl.searchParams.set("theme", "theme--night");
  if (joinedAlias) embedUrl.searchParams.set("nickname", joinedAlias);

  useLayoutEffect(() => {
    const element = dialog.current;
    if (!element) return;
    if (open && !element.open) {
      const active = document.activeElement;
      opener.current =
        active instanceof HTMLElement && active !== document.body
          ? active
          : launcher.current;
      element.showModal();
    } else if (!open && element.open) {
      element.close();
      const focusTarget =
        opener.current?.isConnected && opener.current.getClientRects().length
          ? opener.current
          : launcher.current;
      focusTarget?.focus({ preventScroll: true });
    }
  }, [open]);

  useLayoutEffect(() => {
    clearTimeout(loadTimer.current);
    if (!open || !joinedAlias) return;
    setFrameState("loading");
    loadTimer.current = setTimeout(() => setFrameState("slow"), 15000);
    return () => clearTimeout(loadTimer.current);
  }, [open, roomName, frameAttempt, joinedAlias]);

  useEffect(() => {
    if (!open) return;
    const viewport = window.visualViewport;
    const fitViewport = () => {
      const height = viewport?.height ?? window.innerHeight;
      const bottomInset = Math.max(
        0,
        window.innerHeight - height - (viewport?.offsetTop ?? 0),
      );
      dialog.current?.style.setProperty(
        "--chat-viewport-height",
        height + "px",
      );
      dialog.current?.style.setProperty(
        "--chat-bottom-inset",
        bottomInset + "px",
      );
    };
    fitViewport();
    viewport?.addEventListener("resize", fitViewport);
    viewport?.addEventListener("scroll", fitViewport);
    window.addEventListener("resize", fitViewport);
    return () => {
      viewport?.removeEventListener("resize", fitViewport);
      viewport?.removeEventListener("scroll", fitViewport);
      window.removeEventListener("resize", fitViewport);
    };
  }, [open]);

  function closeFromBackdrop(event: MouseEvent<HTMLDialogElement>) {
    if (event.target !== event.currentTarget) return;
    const bounds = event.currentTarget.getBoundingClientRect();
    if (
      event.clientX < bounds.left ||
      event.clientX > bounds.right ||
      event.clientY < bounds.top ||
      event.clientY > bounds.bottom
    )
      onOpenChange(false);
  }

  function frameLoaded() {
    clearTimeout(loadTimer.current);
    // A loaded document is not a claim that the chat server is connected.
    setFrameState("loaded");
  }

  function frameFailed() {
    clearTimeout(loadTimer.current);
    setFrameState("error");
  }

  function joinChat(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const alias = nickname.trim();
    if (!/^[A-Za-z0-9_ -]{2,24}$/.test(alias)) {
      setNicknameError("Use 2–24 letters, numbers, spaces, _ or -.");
      return;
    }
    setNicknameError("");
    setJoinedAlias(alias);
  }

  return (
    <>
      <button
        ref={launcher}
        className="public-chat-launcher"
        type="button"
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls={id}
        onClick={() => onOpenChange(true)}
      >
        <MessageCircle size={21} aria-hidden="true" />
        <span>Chat</span>
      </button>

      <dialog
        ref={dialog}
        id={id}
        className="public-chat-dialog"
        aria-labelledby={id + "-title"}
        aria-describedby={id + "-description"}
        onCancel={(event) => {
          event.preventDefault();
          onOpenChange(false);
        }}
        onClose={() => {
          if (!dialog.current?.open) onOpenChange(false);
        }}
        onClick={closeFromBackdrop}
      >
        <div className="public-chat-layout">
          <header className="public-chat-header">
            <div>
              <h2 id={id + "-title"}>Case chat</h2>
              <p id={id + "-description"}>
                Public guest chat. Pick a nickname; no sign-in.
              </p>
            </div>
            <button
              type="button"
              className="public-chat-close"
              aria-label="Close case chat"
              onClick={() => onOpenChange(false)}
            >
              <X size={23} aria-hidden="true" />
            </button>
          </header>

          <div className="public-chat-frame-area">
            {open && !joinedAlias && (
              <form className="public-chat-join" onSubmit={joinChat}>
                <MessageCircle size={32} aria-hidden="true" />
                <h3>Bring a fresh pair of eyes.</h3>
                <p>
                  Pick an alias for the public room. No account or wallet
                  needed.
                </p>
                <label htmlFor={id + "-nickname"}>Nickname</label>
                <input
                  id={id + "-nickname"}
                  value={nickname}
                  onChange={(event) => setNickname(event.target.value)}
                  placeholder="e.g. ClueHunter"
                  autoComplete="off"
                  autoCapitalize="off"
                  spellCheck={false}
                  maxLength={24}
                  autoFocus
                  aria-describedby={
                    nicknameError ? id + "-nickname-error" : undefined
                  }
                />
                {nicknameError && (
                  <p
                    className="public-chat-form-error"
                    id={id + "-nickname-error"}
                    role="alert"
                  >
                    {nicknameError}
                  </p>
                )}
                <button type="submit">
                  Enter chat <MessageCircle size={17} aria-hidden="true" />
                </button>
              </form>
            )}
            {open && joinedAlias && (
              <iframe
                key={roomName + "-" + joinedAlias + "-" + frameAttempt}
                src={embedUrl.toString()}
                title="Public puzzle chat"
                referrerPolicy="no-referrer"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox"
                onLoad={frameLoaded}
                onError={frameFailed}
              />
            )}
            {open && joinedAlias && frameState !== "loaded" && (
              <div
                className={
                  "public-chat-loading" +
                  (frameState === "loading" ? "" : " has-fallback")
                }
                role="status"
                aria-live="polite"
              >
                {frameState === "loading" ? (
                  <>
                    <span
                      className="public-chat-loading-mark"
                      aria-hidden="true"
                    >
                      [ ··· ]
                    </span>
                    <p>Loading the chat…</p>
                  </>
                ) : (
                  <>
                    <MessageCircle size={28} aria-hidden="true" />
                    <h3>
                      {frameState === "error"
                        ? "The chat could not load."
                        : "Taking longer than usual."}
                    </h3>
                    <p>Try the room in a new tab, or continue in Discord.</p>
                    <a
                      className="public-chat-open-room"
                      href={roomUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Open the public room{" "}
                      <ExternalLink size={15} aria-hidden="true" />
                    </a>
                    <button
                      type="button"
                      className="public-chat-retry"
                      onClick={() => setFrameAttempt((attempt) => attempt + 1)}
                    >
                      Try loading again
                    </button>
                  </>
                )}
              </div>
            )}
          </div>

          <footer className="public-chat-footer">
            <div className="public-chat-links">
              <a href={roomUrl} target="_blank" rel="noopener noreferrer">
                Open room <ExternalLink size={13} aria-hidden="true" />
              </a>
              <a href={discordUrl} target="_blank" rel="noopener noreferrer">
                Discord <ExternalLink size={13} aria-hidden="true" />
              </a>
              {joinedAlias && (
                <button type="button" onClick={() => setJoinedAlias(null)}>
                  Change nickname
                </button>
              )}
            </div>
            <p>Use an alias. Never post keys or personal details.</p>
            <p>
              Messages may not be kept.{" "}
              <a
                href={repositoryUrl + "/issues"}
                target="_blank"
                rel="noopener noreferrer"
              >
                Save findings on GitHub ↗
              </a>
            </p>
            <p className="public-chat-provider">
              Hosted by tlk.io ·{" "}
              <a
                href="https://tlk.io/privacy"
                target="_blank"
                rel="noopener noreferrer"
              >
                Provider privacy
              </a>
            </p>
          </footer>
        </div>
      </dialog>
    </>
  );
}

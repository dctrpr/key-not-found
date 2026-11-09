import {
  validateEvent,
  verifyEvent,
  type Event as NostrEvent,
} from "nostr-tools/pure";

export const DEFAULT_ROOM_TAG = "keiser-key-not-found";
export const DEFAULT_RELAYS = [
  "wss://nos.lol",
  "wss://relay.primal.net",
  "wss://nostr.mom",
] as const;

export const MAX_POST_LENGTH = 1600;
export const MAX_ROOM_EVENTS = 80;

export type RelayPhase =
  | "connecting"
  | "reading"
  | "live"
  | "offline"
  | "restricted";
export type RelayState = { url: string; phase: RelayPhase; detail?: string };
export type PublishReceipt = {
  relay: string;
  accepted: boolean;
  message: string;
};

export type NostrSigner = {
  getPublicKey(): Promise<string>;
  signEvent(event: {
    kind: number;
    created_at: number;
    content: string;
    tags: string[][];
  }): Promise<NostrEvent>;
};

export function getNostrSigner(): NostrSigner | undefined {
  return (window as Window & { nostr?: NostrSigner }).nostr;
}

export function normalizeRoomTag(value: string): string {
  const tag = value.trim().replace(/^#/, "").toLowerCase();
  return /^[a-z0-9][a-z0-9-]{1,79}$/.test(tag) ? tag : DEFAULT_ROOM_TAG;
}

export function validRelayUrls(values: readonly string[]): string[] {
  return [...new Set(values)]
    .filter((value) => {
      try {
        const url = new URL(value);
        return url.protocol === "wss:" && !url.username && !url.password;
      } catch {
        return false;
      }
    })
    .slice(0, 5);
}

/** Clone only wire fields so a signer cannot supply a cached verification symbol. */
export function verifiedRoomEvent(
  value: unknown,
  roomTag: string,
): NostrEvent | null {
  if (!value || typeof value !== "object") return null;
  const input = value as Record<string, unknown>;
  if (
    input.kind !== 1 ||
    typeof input.id !== "string" ||
    !/^[a-f0-9]{64}$/.test(input.id) ||
    typeof input.pubkey !== "string" ||
    !/^[a-f0-9]{64}$/.test(input.pubkey) ||
    typeof input.sig !== "string" ||
    !/^[a-f0-9]{128}$/.test(input.sig) ||
    typeof input.created_at !== "number" ||
    !Number.isSafeInteger(input.created_at) ||
    input.created_at < 0 ||
    input.created_at > Math.floor(Date.now() / 1000) + 300 ||
    typeof input.content !== "string" ||
    !input.content.trim() ||
    input.content.length > 8000 ||
    !Array.isArray(input.tags) ||
    input.tags.length > 100
  )
    return null;

  const tags: string[][] = [];
  for (const tag of input.tags) {
    if (
      !Array.isArray(tag) ||
      tag.length > 10 ||
      tag.some((part) => typeof part !== "string" || part.length > 1024)
    )
      return null;
    tags.push(tag.slice() as string[]);
  }
  if (!tags.some((tag) => tag[0] === "t" && tag[1] === roomTag)) return null;

  const event: NostrEvent = {
    id: input.id,
    pubkey: input.pubkey,
    sig: input.sig,
    kind: 1,
    created_at: input.created_at,
    content: input.content,
    tags,
  };
  return validateEvent(event) && verifyEvent(event) ? event : null;
}

export function mergeRoomEvent(
  previous: NostrEvent[],
  event: NostrEvent,
): NostrEvent[] {
  if (previous.some((item) => item.id === event.id)) return previous;
  return [...previous, event]
    .sort((a, b) => b.created_at - a.created_at || a.id.localeCompare(b.id))
    .slice(0, MAX_ROOM_EVENTS);
}

export function publishToRelay(
  socket: WebSocket,
  event: NostrEvent,
): Promise<PublishReceipt> {
  return new Promise((resolve) => {
    let finished = false;
    const finish = (accepted: boolean, message: string) => {
      if (finished) return;
      finished = true;
      clearTimeout(timeout);
      socket.removeEventListener("message", onMessage);
      socket.removeEventListener("close", onClose);
      socket.removeEventListener("error", onError);
      resolve({ relay: socket.url, accepted, message });
    };
    const onMessage = (message: MessageEvent) => {
      try {
        const data: unknown = JSON.parse(String(message.data));
        if (Array.isArray(data) && data[0] === "OK" && data[1] === event.id) {
          finish(
            data[2] === true,
            typeof data[3] === "string" ? data[3].slice(0, 180) : "",
          );
        }
      } catch {
        /* Ignore unrelated or malformed relay frames. */
      }
    };
    const onClose = () =>
      finish(false, "Connection closed before acknowledgment.");
    const onError = () => finish(false, "Relay connection failed.");
    const timeout = setTimeout(
      () => finish(false, "No acknowledgment within 8 seconds."),
      8000,
    );

    if (socket.readyState !== WebSocket.OPEN) {
      finish(false, "Relay is offline.");
      return;
    }
    socket.addEventListener("message", onMessage);
    socket.addEventListener("close", onClose);
    socket.addEventListener("error", onError);
    try {
      socket.send(JSON.stringify(["EVENT", event]));
    } catch {
      finish(false, "Could not send to this relay.");
    }
  });
}

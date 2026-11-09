import { parseResearchData } from "../lib/research-state.mjs";

const REPO = "dctrpr/key-not-found";
const MAX_DOCUMENT_BYTES = 512_000;
const HEADERS = {
  "Content-Type": "application/json; charset=utf-8",
  "X-Content-Type-Options": "nosniff",
  "Cache-Control": "public, max-age=0, must-revalidate",
  "Vercel-CDN-Cache-Control":
    "public, s-maxage=300, stale-while-revalidate=600",
};

async function readJson(
  url: string,
  signal: AbortSignal,
  githubApi = false,
): Promise<unknown> {
  const response = await fetch(url, {
    signal,
    redirect: "error",
    headers: githubApi
      ? {
          Accept: "application/vnd.github+json",
          "X-GitHub-Api-Version": "2022-11-28",
          "User-Agent": "KEY404-public-research",
        }
      : { Accept: "application/json", "User-Agent": "KEY404-public-research" },
  });
  if (!response.ok || !response.body)
    throw new Error("Research source unavailable");
  const length = response.headers.get("content-length");
  if (length && Number(length) > MAX_DOCUMENT_BYTES)
    throw new Error("Research source too large");
  const reader = response.body.getReader();
  const chunks: Uint8Array[] = [];
  let size = 0;
  try {
    for (;;) {
      const chunk = await reader.read();
      if (chunk.done) break;
      size += chunk.value.byteLength;
      if (size > MAX_DOCUMENT_BYTES) {
        await reader.cancel();
        throw new Error("Research source too large");
      }
      chunks.push(chunk.value);
    }
  } finally {
    reader.releaseLock();
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return JSON.parse(new TextDecoder().decode(bytes));
}

export async function GET(request: Request): Promise<Response> {
  if (new URL(request.url).search)
    return Response.json(
      { status: "unavailable" },
      { status: 400, headers: { "Cache-Control": "no-store" } },
    );
  try {
    // One public ref lookup fixes all three documents to the same immutable commit.
    // No caller-controlled URL, authorization header, environment secret or user data is forwarded.
    const signal = AbortSignal.timeout(9000);
    const ref = await readJson(
      `https://api.github.com/repos/${REPO}/git/ref/heads/main`,
      signal,
      true,
    );
    const sha = (ref as { object?: { sha?: unknown } })?.object?.sha;
    if (typeof sha !== "string" || !/^[a-f0-9]{40}$/.test(sha))
      throw new Error("Invalid source revision");
    const base = `https://raw.githubusercontent.com/${REPO}/${sha}/public/`;
    const [ledger, updates, map] = await Promise.all([
      readJson(base + "research/experiments.json", signal),
      readJson(base + "data/updates.json", signal),
      readJson(base + "data/research-map.json", signal),
    ]);
    const data = parseResearchData(ledger, updates, map);
    return Response.json(
      {
        status: "ok",
        checkedAt: new Date().toISOString(),
        sourceCommit: sha,
        ...data,
      },
      { headers: HEADERS },
    );
  } catch {
    console.warn("Public research sync unavailable");
    // A static deployed snapshot stays usable in the browser. Never turn upstream
    // failures into empty results or expose raw response bodies and diagnostics.
    return Response.json(
      { status: "unavailable" },
      {
        status: 503,
        headers: {
          "Cache-Control": "no-store",
          "X-Content-Type-Options": "nosniff",
          "Retry-After": "300",
        },
      },
    );
  }
}

import { readGitHubActivity } from "../lib/github-activity.mjs";

const cacheHeaders = {
  "Cache-Control": "public, max-age=0, must-revalidate",
  "Vercel-CDN-Cache-Control":
    "public, s-maxage=900, stale-while-revalidate=3600",
  "X-Content-Type-Options": "nosniff",
};

// Fixed repository, read-only public API, no token, client identifier, or body.
export async function GET(request) {
  if (new URL(request.url).search)
    return Response.json(
      { error: "Query parameters are not supported." },
      { status: 400 },
    );
  try {
    return Response.json(await readGitHubActivity(), { headers: cacheHeaders });
  } catch (error) {
    console.warn(
      "Public GitHub activity unavailable:",
      error instanceof Error ? error.message : "unknown error",
    );
    return Response.json(
      { error: "GitHub activity is temporarily unavailable." },
      {
        status: 503,
        headers: {
          "Cache-Control": "no-store",
          "Vercel-CDN-Cache-Control": "public, s-maxage=60",
        },
      },
    );
  }
}

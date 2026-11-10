import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { GET } from "../api/research-state.ts";
import {
  parseResearchData,
  parseVerifiedResearch,
  compareResearchUpdates,
} from "../src/lib/researchState.ts";

const [ledger, updates, map] = await Promise.all(
  [
    "public/research/experiments.json",
    "public/data/updates.json",
    "public/data/research-map.json",
  ].map(async (path) =>
    JSON.parse(await readFile(new URL("../" + path, import.meta.url), "utf8")),
  ),
);
const SHA = "a".repeat(40);
const endpoint = () => new Request("https://example.test/api/research-state");

test("map covers every real method once and strips unlisted fields", () => {
  const data = parseResearchData(
    { ...ledger, privateNotes: "do not publish" },
    updates,
    map,
  );
  assert.equal(data.ledger.methods.length, ledger.methods.length);
  assert.equal(data.map.branches.length, map.branches.length);
  assert.equal(
    new Set(data.map.branches.flatMap((branch) => branch.methodIds)).size,
    ledger.methods.length,
  );
  assert.equal("privateNotes" in data.ledger, false);
  assert.equal(data.ledger.caseStatus, "unsolved");
});

test("rejects missing/duplicate map membership and unsafe evidence", () => {
  const missing = structuredClone(map);
  missing.branches[0].methodIds.pop();
  assert.throws(() => parseResearchData(ledger, updates, missing));
  const duplicate = structuredClone(map);
  duplicate.branches[1].methodIds.push(duplicate.branches[0].methodIds[0]);
  assert.throws(() => parseResearchData(ledger, updates, duplicate));
  for (const path of [
    "https://example.test/data",
    "/research/../private",
    "/research/%2e%2e/private",
    "//example.test/data",
    "/private/file.md",
  ]) {
    const unsafe = structuredClone(updates);
    unsafe.updates[0].evidence = path;
    assert.throws(() => parseResearchData(ledger, unsafe, map), path);
  }
});

test("validates optional update links against the same map and ledger", () => {
  const linked = structuredClone(updates);
  linked.updates[0].methodIds = ["numeric-256"];
  linked.updates[0].branchId = "numbers-type";
  assert.equal(
    parseResearchData(ledger, linked, map).updates.updates[0].methodIds[0],
    "numeric-256",
  );
  linked.updates[0].methodIds = ["invented-method"];
  assert.throws(() => parseResearchData(ledger, linked, map));
});

test("preserves precise UTC completion times without inventing older times", () => {
  const timed = structuredClone(updates);
  timed.updates[0].date = "2026-11-09";
  timed.updates[0].completedAtUTC = "2026-11-09T18:20:30.123Z";
  timed.updates[0].operatorTimezone = "private setting";
  delete timed.updates[1].completedAtUTC;
  const parsed = parseResearchData(ledger, timed, map).updates.updates;
  assert.equal(parsed[0].completedAtUTC, "2026-11-09T18:20:30.123Z");
  assert.equal("operatorTimezone" in parsed[0], false);
  assert.equal("completedAtUTC" in parsed[1], false);
  timed.updates[0].completedAtUTC = "2026-11-09T18:20:30Z";
  assert.equal(
    parseResearchData(ledger, timed, map).updates.updates[0].completedAtUTC,
    "2026-11-09T18:20:30Z",
  );
});

test("rejects malformed, mismatched or future research completion times", () => {
  for (const completedAtUTC of [
    "2026-11-09T18:20:30+00:00",
    "2026-11-09T18:20:30",
    "2026-11-09T18:20:30.123456Z",
    "2026-11-09T25:20:30Z",
    "2026-02-30T18:20:30Z",
    "2026-11-10T18:20:30Z",
    "yesterday",
    "",
    null,
  ]) {
    const malformed = structuredClone(updates);
    malformed.updates[0].date = "2026-11-09";
    malformed.updates[0].completedAtUTC = completedAtUTC;
    assert.throws(
      () => parseResearchData(ledger, malformed, map),
      String(completedAtUTC),
    );
  }
  const future = structuredClone(updates);
  const stamp = new Date(Date.now() + 120_000).toISOString();
  future.updates[0].date = stamp.slice(0, 10);
  future.updates[0].completedAtUTC = stamp;
  future.updatedOn = stamp.slice(0, 10);
  assert.throws(() => parseResearchData(ledger, future, map));
});

test("test feed orders exact completion times and keeps legacy same-day order", () => {
  const entry = updates.updates[0];
  const make = (id, date, completedAtUTC, kind = "research") => ({
    ...entry,
    id,
    date,
    kind,
    completedAtUTC,
  });
  const records = [
    make("legacy-first", "2026-11-09"),
    make("fractional", "2026-11-09", "2026-11-09T18:20:30.001Z"),
    make("whole-second", "2026-11-09", "2026-11-09T18:20:30Z"),
    make("legacy-second", "2026-11-09"),
    make("next-day", "2026-11-10"),
    make("project-note", "2026-11-09", "2026-11-09T23:00:00Z", "project"),
  ];
  assert.deepEqual(records.sort(compareResearchUpdates).map((record) => record.id), [
    "next-day",
    "fractional",
    "whole-second",
    "legacy-first",
    "legacy-second",
    "project-note",
  ]);
});

test("verified data requires source SHA, a valid time, and unsolved case scope", () => {
  const data = {
    status: "ok",
    sourceCommit: SHA,
    checkedAt: new Date().toISOString(),
    ledger,
    updates,
    map,
  };
  assert.equal(parseVerifiedResearch(data).sourceCommit, SHA);
  assert.throws(() => parseVerifiedResearch({ ...data, sourceCommit: "main" }));
  assert.throws(() =>
    parseVerifiedResearch({ ...data, checkedAt: "tomorrow" }),
  );
  assert.throws(() =>
    parseVerifiedResearch({
      ...data,
      ledger: { ...ledger, caseStatus: "solved" },
    }),
  );
});

test("endpoint pins all three document reads to one public commit", async (t) => {
  const original = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = original;
  });
  const urls = [];
  globalThis.fetch = async (url, options) => {
    urls.push(url);
    assert.equal(options.headers.Authorization, undefined);
    if (urls.length === 1)
      return Response.json({ object: { sha: SHA }, extra: "ignored" });
    if (url.endsWith("research/experiments.json")) return Response.json(ledger);
    if (url.endsWith("data/updates.json")) return Response.json(updates);
    if (url.endsWith("data/research-map.json")) return Response.json(map);
    throw new Error("Unexpected URL");
  };
  const response = await GET(endpoint());
  assert.equal(response.status, 200);
  const payload = await response.json();
  assert.equal(payload.sourceCommit, SHA);
  assert.equal(payload.status, "ok");
  assert.equal(urls.length, 4);
  assert.ok(
    urls
      .slice(1)
      .every((url) =>
        url.startsWith(
          `https://raw.githubusercontent.com/dctrpr/key-not-found/${SHA}/public/`,
        ),
      ),
  );
  assert.match(
    response.headers.get("Vercel-CDN-Cache-Control"),
    /s-maxage=300/,
  );
});

test("unavailable upstream returns a generic noncached failure", async (t) => {
  const original = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = original;
  });
  globalThis.fetch = async () => {
    throw new Error("private upstream diagnostics");
  };
  const response = await GET(endpoint());
  assert.equal(response.status, 503);
  assert.equal(response.headers.get("Cache-Control"), "no-store");
  assert.deepEqual(await response.json(), { status: "unavailable" });
});

test("oversized upstream and caller query strings are rejected", async (t) => {
  const original = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = original;
  });
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    return new Response(new Uint8Array(512_001));
  };
  assert.equal(
    (
      await GET(
        new Request("https://example.test/api/research-state?url=elsewhere"),
      )
    ).status,
    400,
  );
  assert.equal(calls, 0);
  assert.equal((await GET(endpoint())).status, 503);
});

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { parseResearchData } from "../src/lib/researchState.ts";

const root = path.resolve(import.meta.dirname, "..");
const excluded = new Set([
  "node_modules",
  ".git",
  ".vercel",
  ".claude",
  "dist",
  "coverage",
  "test-results",
  "playwright-report",
]);
const textExtensions =
  /\.(md|txt|json|jsonl|js|mjs|cjs|ts|tsx|jsx|css|html|py|swift|yml|yaml|csv|tsv|xml|svg|vtt)$/i;
const checks = [
  ["personal home directory", /(?:\/Users\/|\/home\/)[^\s/"'<>]+\//g],
  ["Windows personal directory", /[A-Z]:\\Users\\[^\\\s]+\\/gi],
  [
    "non-UTC location timezone",
    /\b(?:Africa|America|Antarctica|Arctic|Asia|Atlantic|Australia|Europe|Indian|Pacific)\/[A-Z][A-Za-z_+-]+(?:\/[A-Z][A-Za-z_+-]+)?\b/g,
  ],
  [
    "private discussion URL",
    /https?:\/\/(?:canary\.|ptb\.)?discord(?:app)?\.com\/channels\/\d+/gi,
  ],
  [
    "private annotation URL",
    /https?:\/\/(?:www\.)?canva\.com\/design\/[A-Za-z0-9_-]+/gi,
  ],
  [
    "GitHub access token",
    /\b(?:gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{30,})\b/g,
  ],
  ["provider secret token", /\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b/g],
  [
    "private signing material",
    /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/g,
  ],
  [
    "secret assignment",
    /(?:OPENAI_API_KEY|ANTHROPIC_API_KEY|VERCEL_TOKEN)\s*[=:]\s*["']?[A-Za-z0-9_-]{20,}/g,
  ],
];
const violations = [];
let textFiles = 0;
function walk(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (excluded.has(entry.name)) continue;
    const filename = path.join(directory, entry.name);
    const relative = path.relative(root, filename).replaceAll(path.sep, "/");
    if (entry.isSymbolicLink()) {
      violations.push([relative, "symlink must be resolved before release"]);
      continue;
    }
    if (entry.isDirectory()) {
      walk(filename);
      continue;
    }
    if (
      entry.name.startsWith(".env") ||
      /(?:auth|credentials|cookies|session)\.(?:sqlite|db)$/i.test(entry.name)
    )
      violations.push([relative, "forbidden private file class"]);
    if (!textExtensions.test(entry.name) || filename === import.meta.filename)
      continue;
    textFiles++;
    const text = fs.readFileSync(filename, "utf8");
    for (const [label, regex] of checks) {
      regex.lastIndex = 0;
      if (regex.test(text)) violations.push([relative, label]);
    }
  }
}
walk(root);
const corpus = path.join(root, "public/research");
const hashLines = fs
  .readFileSync(path.join(corpus, "SHA256SUMS"), "utf8")
  .trim()
  .split("\n");
let verified = 0;
for (const line of hashLines) {
  const match = /^([a-f0-9]{64})\s{2}(.+)$/.exec(line);
  if (!match) {
    violations.push(["SHA256SUMS", "invalid checksum row"]);
    continue;
  }
  const filename = path.resolve(corpus, match[2]);
  if (!filename.startsWith(corpus + path.sep) || !fs.existsSync(filename)) {
    violations.push([match[2], "missing or invalid corpus path"]);
    continue;
  }
  const actual = crypto
    .createHash("sha256")
    .update(fs.readFileSync(filename))
    .digest("hex");
  if (actual !== match[1])
    violations.push([match[2], "corpus checksum mismatch"]);
  verified++;
}
const project = JSON.parse(
  fs.readFileSync(path.join(root, "public/data/project.json"), "utf8"),
);
if (project.funding?.buyback?.allocationPercent !== 100)
  violations.push(["project.json", "buyback commitment must preserve its 100-percent allocation"]);
if (project.token.status !== "not-launched") {
  if (
    project.token.status !== "live" ||
    !/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(project.token.contract || "")
  )
    violations.push(["project.json", "invalid live contract configuration"]);
  try {
    const url = new URL(project.token.url);
    if (
      url.protocol !== "https:" ||
      !["pump.fun", "www.pump.fun"].includes(url.hostname) ||
      url.pathname !== "/coin/" + project.token.contract ||
      url.search || url.hash
    )
      throw new Error();
  } catch {
    violations.push(["project.json", "invalid official token URL"]);
  }
} else if (project.token.contract !== null || project.token.url !== null)
  violations.push([
    "project.json",
    "unlaunched token must have null contract and URL",
  ]);
const ledgerDocument = JSON.parse(
  fs.readFileSync(path.join(corpus, "experiments.json"), "utf8"),
);
const methods = ledgerDocument.methods;
for (const method of methods)
  for (const evidence of method.evidence)
    if (!fs.existsSync(path.join(corpus, evidence)))
      violations.push([method.id, "missing method evidence"]);
const updateLog = JSON.parse(
  fs.readFileSync(path.join(root, "public/data/updates.json"), "utf8"),
);
const updates = updateLog.updates;
try {
  parseResearchData(
    ledgerDocument,
    updateLog,
    JSON.parse(
      fs.readFileSync(path.join(root, "public/data/research-map.json"), "utf8"),
    ),
  );
} catch {
  violations.push([
    "research-map.json",
    "invalid map coverage or research/update references",
  ]);
}
const updateIds = new Set();
for (const update of updates) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(update.date) || !update.title || !update.body)
    violations.push([update.id, "invalid update"]);
  if (!update.id || updateIds.has(update.id))
    violations.push([update.id, "missing or duplicate update id"]);
  updateIds.add(update.id);
  if (!["research", "project"].includes(update.kind))
    violations.push([update.id, "update kind must be research or project"]);
  if (
    !update.evidence.startsWith("/") ||
    !fs.existsSync(path.join(root, "public", update.evidence))
  )
    violations.push([update.id, "missing update evidence"]);
}
const latestUpdate = updates
  .map((update) => update.date)
  .sort()
  .at(-1);
if (
  typeof updateLog.logOpenedOn !== "string" ||
  !/^\d{4}-\d{2}-\d{2}$/.test(updateLog.logOpenedOn) ||
  (latestUpdate && updateLog.logOpenedOn > latestUpdate)
)
  violations.push(["updates.json", "invalid public-log opening date"]);
if (latestUpdate && updateLog.updatedOn !== latestUpdate)
  violations.push([
    "updates.json",
    "updatedOn must match the newest published note",
  ]);
if (latestUpdate && project.updatedOn < latestUpdate)
  violations.push([
    "project.json",
    "project date is older than its update history",
  ]);
if (
  project.chat?.provider !== "tlk.io" ||
  typeof project.chat.room !== "string" ||
  !/^[a-z0-9-]{1,80}$/.test(project.chat.room) ||
  project.chat.url !== "https://tlk.io/" + project.chat.room
)
  violations.push(["project.json", "invalid public chat configuration"]);
console.log(
  JSON.stringify(
    {
      textFilesScanned: textFiles,
      corpusFilesVerified: verified,
      methods: methods.length,
      updates: updates.length,
      unresolvedFindings: violations.length,
      findings: violations,
    },
    null,
    2,
  ),
);
if (violations.length) process.exitCode = 1;

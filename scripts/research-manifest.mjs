import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const root = path.resolve(import.meta.dirname, "../public/research");
const generated = new Set(["files.json", "manifest.json", "SHA256SUMS"]);
const sha256 = (file) =>
  crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const files = [];
function walk(dir) {
  for (const entry of fs
    .readdirSync(dir, { withFileTypes: true })
    .sort((a, b) => a.name.localeCompare(b.name))) {
    if (
      entry.name === "node_modules" ||
      entry.name === "__pycache__" ||
      entry.name.startsWith(".")
    )
      continue;
    const absolute = path.join(dir, entry.name);
    const relative = path.relative(root, absolute).replaceAll(path.sep, "/");
    if (entry.isSymbolicLink())
      throw new Error("Resolve symlinks before publishing");
    if (entry.isDirectory()) walk(absolute);
    else if (!generated.has(relative))
      files.push({
        path: relative,
        bytes: fs.statSync(absolute).size,
        sha256: sha256(absolute),
      });
  }
}
walk(root);
const previous = JSON.parse(
  fs.readFileSync(path.join(root, "files.json"), "utf8"),
);
const metadata = new Map(previous.files.map((file) => [file.path, file]));
const entries = files.map((file) => ({
  ...(metadata.get(file.path) || {
    category: /\.(py|js|ts|html)$/.test(file.path)
      ? "code"
      : file.path.startsWith("sources/")
        ? "source"
        : "result",
    mediaType: "text/plain",
    description: "Public research contribution",
  }),
  ...file,
}));
const generatedOn = new Date().toISOString().slice(0, 10);
const payload = {
  ...previous,
  generatedOn,
  files: entries,
  totals: {
    files: entries.length,
    bytes: entries.reduce((sum, file) => sum + file.bytes, 0),
  },
};
fs.writeFileSync(
  path.join(root, "files.json"),
  JSON.stringify(payload, null, 2) + "\n",
);
const withIndex = [
  ...files,
  {
    path: "files.json",
    bytes: fs.statSync(path.join(root, "files.json")).size,
    sha256: sha256(path.join(root, "files.json")),
  },
];
fs.writeFileSync(
  path.join(root, "manifest.json"),
  JSON.stringify({ version: 1, generatedOn, files: withIndex }, null, 2) + "\n",
);
const all = [
  ...withIndex,
  { path: "manifest.json", sha256: sha256(path.join(root, "manifest.json")) },
].sort((a, b) => a.path.localeCompare(b.path));
fs.writeFileSync(
  path.join(root, "SHA256SUMS"),
  all.map((file) => file.sha256 + "  " + file.path).join("\n") + "\n",
);
console.log(
  JSON.stringify({ payloadFiles: files.length, checksums: all.length }),
);

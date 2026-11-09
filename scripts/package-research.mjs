import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { zipSync } from "fflate";

const defaultRoot = path.resolve(import.meta.dirname, "..");
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const compare = (a, b) => (a < b ? -1 : a > b ? 1 : 0);

function directory(filename, label) {
  if (!fs.existsSync(filename) || !fs.lstatSync(filename).isDirectory())
    throw new Error(label + " must be a regular directory.");
}

function collect(root) {
  const files = [];
  directory(root, "Archive input");
  function walk(current) {
    for (const entry of fs
      .readdirSync(current, { withFileTypes: true })
      .sort((a, b) => compare(a.name, b.name))) {
      const filename = path.join(current, entry.name);
      const relative = path.relative(root, filename).split(path.sep).join("/");
      if (
        relative.includes("\\") ||
        /[\x00-\x1f\x7f]/.test(relative) ||
        relative.split("/").some((part) => part === ".." || part === ".")
      )
        throw new Error("Unsafe archive entry name.");
      if (entry.isSymbolicLink())
        throw new Error("Symlinks are not archive inputs: " + relative);
      if (entry.isDirectory()) walk(filename);
      else if (entry.isFile())
        files.push({ name: relative, bytes: fs.readFileSync(filename) });
      else throw new Error("Special files are not archive inputs: " + relative);
    }
  }
  walk(root);
  return files.sort((a, b) => compare(a.name, b.name));
}

function verifyResearch(files) {
  const entries = new Map(files.map((file) => [file.name, file]));
  const sums = entries.get("SHA256SUMS");
  if (!sums) throw new Error("Research SHA256SUMS is missing.");
  const expected = new Map();
  for (const line of sums.bytes.toString("utf8").trim().split("\n")) {
    const match = /^([a-f0-9]{64}) {2}(.+)$/.exec(line);
    if (!match || expected.has(match[2]))
      throw new Error("Research SHA256SUMS has an invalid or duplicate row.");
    expected.set(match[2], match[1]);
  }
  for (const file of files) {
    if (file.name === "SHA256SUMS") continue;
    if (expected.get(file.name) !== hash(file.bytes))
      throw new Error("Research checksum missing or mismatched: " + file.name);
  }
  if (
    expected.size !== files.length - 1 ||
    [...expected.keys()].some((name) => !entries.has(name))
  )
    throw new Error(
      "Research checksum inventory does not match all archive inputs.",
    );
}

function atomicWrite(filename, bytes) {
  fs.mkdirSync(path.dirname(filename), { recursive: true });
  const temporary = filename + ".tmp";
  try {
    fs.writeFileSync(temporary, bytes, { mode: 0o644 });
    fs.renameSync(temporary, filename);
  } finally {
    if (fs.existsSync(temporary)) fs.unlinkSync(temporary);
  }
}

function archive(files, prefix, filename, output, mtime) {
  const input = Object.create(null);
  for (const file of files) {
    input[prefix + "/" + file.name] = [
      new Uint8Array(file.bytes),
      {
        level: 6,
        mtime,
        os: 0,
        attrs: 0,
        extra: {},
        comment: "",
      },
    ];
  }
  const bytes = zipSync(input, {
    level: 6,
    mtime,
    os: 0,
    attrs: 0,
    comment: "",
  });
  atomicWrite(path.join(output, filename), bytes);
  return {
    url: "/downloads/" + filename,
    bytes: bytes.length,
    sha256: hash(bytes),
    fileCount: files.length,
    uncompressedBytes: files.reduce((sum, file) => sum + file.bytes.length, 0),
  };
}

/** Build outputs only. Research inputs, manifests and their timestamps are untouched. */
export function packageResearch(siteRoot = defaultRoot) {
  const root = path.resolve(siteRoot);
  const publicRoot = path.join(root, "public");
  directory(publicRoot, "Public input");
  const project = JSON.parse(
    fs.readFileSync(path.join(publicRoot, "data/project.json"), "utf8"),
  );
  const date = project.updatedOn;
  if (typeof date !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(date))
    throw new Error("project.updatedOn must be a YYYY-MM-DD release date.");
  const mtime = new Date(date + "T00:00:00.000Z");
  if (
    !Number.isFinite(mtime.valueOf()) ||
    mtime.toISOString().slice(0, 10) !== date ||
    mtime.getUTCFullYear() < 1980 ||
    mtime.getUTCFullYear() > 2099
  )
    throw new Error(
      "Release date is invalid or outside the ZIP timestamp range 1980–2099.",
    );

  // fflate encodes DOS timestamps using local Date getters. Pin their timezone.
  const previousTimezone = process.env.TZ;
  process.env.TZ = "UTC";
  try {
    const research = collect(path.join(publicRoot, "research"));
    verifyResearch(research);
    const output = path.join(publicRoot, "downloads");
    const casefile = archive(
      research,
      "key404-casefile",
      "key404-casefile.zip",
      output,
      mtime,
    );
    const launchDirectory = path.join(publicRoot, "launch-kit");
    let launchKit = null;
    if (fs.existsSync(launchDirectory)) {
      const launchFiles = collect(launchDirectory);
      const emblem = path.join(publicRoot, "assets/key404-emblem.png");
      if (fs.existsSync(emblem)) {
        if (
          !fs.lstatSync(emblem).isFile() ||
          !fs
            .realpathSync(emblem)
            .startsWith(fs.realpathSync(publicRoot) + path.sep)
        )
          throw new Error("Launch emblem must be a regular public asset.");
        const bytes = fs.readFileSync(emblem);
        const name = "assets/key404-emblem.png";
        const existing = launchFiles.find((file) => file.name === name);
        if (existing && !existing.bytes.equals(bytes))
          throw new Error("Launch kit contains a conflicting emblem.");
        if (!existing) launchFiles.push({ name, bytes });
      }
      launchFiles.sort((a, b) => compare(a.name, b.name));
      if (launchFiles.length)
        launchKit = archive(
          launchFiles,
          "key404-launch-kit",
          "key404-launch-kit.zip",
          output,
          mtime,
        );
    }
    if (!launchKit) {
      const stale = path.join(output, "key404-launch-kit.zip");
      if (fs.existsSync(stale)) fs.unlinkSync(stale);
    }
    const metadata = {
      version: 1,
      generatedOn: date,
      normalizedEntryTime: mtime.toISOString(),
      compression: { algorithm: "DEFLATE", level: 6 },
      archives: { casefile, launchKit },
    };
    atomicWrite(
      path.join(publicRoot, "data/release.json"),
      JSON.stringify(metadata, null, 2) + "\n",
    );
    return metadata;
  } finally {
    if (previousTimezone === undefined) delete process.env.TZ;
    else process.env.TZ = previousTimezone;
  }
}

if (
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  try {
    console.log(JSON.stringify(packageResearch(), null, 2));
  } catch (error) {
    console.error(
      "Archive packaging failed: " +
        String(error.message).replaceAll(defaultRoot, "<site>"),
    );
    process.exitCode = 1;
  }
}

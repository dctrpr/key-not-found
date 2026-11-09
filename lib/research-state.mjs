const statuses = new Set([
  "untested",
  "in-progress",
  "in_progress",
  "partial",
  "tested",
  "falsified",
  "invalidated",
  "open",
]);
function object(value) {
  if (!value || typeof value !== "object" || Array.isArray(value))
    throw new Error("Invalid research data");
  return value;
}
function text(value, max = 2000) {
  if (
    typeof value !== "string" ||
    !value.trim() ||
    value.length > max ||
    /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value)
  ) {
    throw new Error("Invalid research text");
  }
  return value;
}
function id(value) {
  const result = text(value, 80);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(result))
    throw new Error("Invalid research identifier");
  return result;
}
function date(value) {
  const result = text(value, 10);
  if (
    !/^\d{4}-\d{2}-\d{2}$/.test(result) ||
    new Date(result + "T00:00:00Z").toISOString().slice(0, 10) !== result
  ) {
    throw new Error("Invalid research date");
  }
  return result;
}
function list(value, map, max) {
  if (!Array.isArray(value) || value.length > max)
    throw new Error("Invalid research list");
  return value.map(map);
}
function unique(values) {
  if (new Set(values).size !== values.length)
    throw new Error("Duplicate research identifier");
}
// Paths stay on this site's reviewed public surface. No schemes, query strings,
// fragments, encoded traversal, backslashes, or private absolute paths pass.
function evidencePath(value, absolute) {
  const result = text(value, 300);
  const path = absolute ? result.slice(1) : result;
  if (
    (absolute && !result.startsWith("/")) ||
    !/^[A-Za-z0-9][A-Za-z0-9_ ./-]*$/.test(path) ||
    path.split("/").some((part) => !part || part === "." || part === "..")
  ) {
    throw new Error("Invalid research evidence path");
  }
  if (absolute && !(path.startsWith("research/") || path === "UPDATES.md"))
    throw new Error("Invalid research evidence surface");
  return result;
}
/** Whitelist the three public documents and verify their cross references. */
export function parseResearchData(ledgerValue, updatesValue, mapValue) {
  const rawLedger = object(ledgerValue);
  if (rawLedger.caseStatus !== "unsolved")
    throw new Error("Unexpected case status");
  const methods = list(
    rawLedger.methods,
    (entry) => {
      const item = object(entry);
      const status = text(item.status, 30);
      if (!statuses.has(status)) throw new Error("Invalid research status");
      return {
        id: id(item.id),
        title: text(item.title, 180),
        status,
        ...(item.kind === undefined ? {} : { kind: text(item.kind, 60) }),
        scope: text(item.scope),
        result: text(item.result),
        evidence: list(item.evidence, (path) => evidencePath(path, false), 15),
        reproduce: list(item.reproduce, (command) => text(command, 2000), 20),
        ...(item.limitations === undefined
          ? {}
          : {
              limitations: list(item.limitations, (limit) => text(limit), 20),
            }),
      };
    },
    250,
  );
  if (!methods.length) throw new Error("Empty research ledger");
  unique(methods.map((method) => method.id));
  const methodIds = new Set(methods.map((method) => method.id));
  const rawMap = object(mapValue);
  if (rawMap.version !== 1) throw new Error("Unsupported research map version");
  const branches = list(
    rawMap.branches,
    (entry) => {
      const item = object(entry);
      const refs = list(item.methodIds, id, 250);
      if (!refs.length || refs.some((ref) => !methodIds.has(ref)))
        throw new Error("Unknown mapped method");
      return {
        id: id(item.id),
        title: text(item.title, 100),
        description: text(item.description, 700),
        methodIds: refs,
        ...(item.nextAction === undefined
          ? {}
          : { nextAction: text(item.nextAction, 700) }),
      };
    },
    8,
  );
  if (!branches.length) throw new Error("Empty research map");
  unique(branches.map((branch) => branch.id));
  const mappedIds = branches.flatMap((branch) => branch.methodIds);
  unique(mappedIds);
  if (mappedIds.length !== methods.length)
    throw new Error("Incomplete research map");
  const branchIds = new Set(branches.map((branch) => branch.id));
  const rawUpdates = object(updatesValue);
  const updates = list(
    rawUpdates.updates,
    (entry) => {
      const item = object(entry);
      const kind = item.kind;
      if (kind !== undefined && kind !== "research" && kind !== "project")
        throw new Error("Invalid update kind");
      const refs =
        item.methodIds === undefined ? undefined : list(item.methodIds, id, 50);
      if (refs) {
        unique(refs);
        if (refs.some((ref) => !methodIds.has(ref)))
          throw new Error("Unknown update method");
      }
      const branchId =
        item.branchId === undefined ? undefined : id(item.branchId);
      if (branchId && !branchIds.has(branchId))
        throw new Error("Unknown update branch");
      return {
        id: id(item.id),
        date: date(item.date),
        category: text(item.category, 60),
        title: text(item.title, 200),
        body: text(item.body, 4000),
        evidence: evidencePath(item.evidence, true),
        ...(kind === "research" || kind === "project" ? { kind } : {}),
        ...(refs === undefined ? {} : { methodIds: refs }),
        ...(branchId === undefined ? {} : { branchId }),
      };
    },
    500,
  );
  unique(updates.map((update) => update.id));
  const updatedOn = date(rawUpdates.updatedOn);
  const logOpenedOn = date(rawUpdates.logOpenedOn);
  if (
    logOpenedOn > updatedOn ||
    updates.some((update) => update.date > updatedOn)
  )
    throw new Error("Inconsistent update dates");
  return {
    ledger: {
      caseStatus: "unsolved",
      updatedOn: date(rawLedger.updatedOn),
      methods,
    },
    updates: { updatedOn, logOpenedOn, updates },
    map: { version: 1, updatedOn: date(rawMap.updatedOn), branches },
  };
}
export function parseVerifiedResearch(value) {
  const item = object(value);
  if (
    item.status !== "ok" ||
    typeof item.sourceCommit !== "string" ||
    !/^[a-f0-9]{40}$/.test(item.sourceCommit)
  )
    throw new Error("Invalid research source");
  const checkedAt = text(item.checkedAt, 30);
  const checkedTime = Date.parse(checkedAt);
  if (!Number.isFinite(checkedTime) || checkedTime > Date.now() + 60000)
    throw new Error("Invalid research check time");
  return {
    ...parseResearchData(item.ledger, item.updates, item.map),
    sourceCommit: item.sourceCommit,
    checkedAt,
  };
}

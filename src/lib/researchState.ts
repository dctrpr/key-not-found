export type ResearchMethod = {
  id: string;
  title: string;
  status: string;
  kind?: string;
  scope: string;
  result: string;
  evidence: string[];
  reproduce: string[];
  limitations?: string[];
};

export type ResearchUpdate = {
  id: string;
  date: string;
  category: string;
  title: string;
  body: string;
  evidence: string;
  kind?: "research" | "project";
  methodIds?: string[];
  branchId?: string;
  completedAtUTC?: string;
};

/** Completion time orders same-day records; older date-only entries keep their order. */
export function compareResearchUpdates(a: ResearchUpdate, b: ResearchUpdate) {
  const day = b.date.localeCompare(a.date);
  if (day) return day;
  const kind = Number(a.kind === "project") - Number(b.kind === "project");
  if (kind) return kind;
  const completedTime = (entry: ResearchUpdate) => {
    const parsed = entry.completedAtUTC ? Date.parse(entry.completedAtUTC) : NaN;
    return Number.isFinite(parsed) ? parsed : -1;
  };
  return completedTime(b) - completedTime(a);
}

export type ResearchBranch = {
  id: string;
  title: string;
  description: string;
  methodIds: string[];
  nextAction?: string;
};

export type ResearchMap = {
  version?: number;
  updatedOn: string;
  branches: ResearchBranch[];
};

export type ResearchLedger = {
  methods: ResearchMethod[];
  updatedOn?: string;
  caseStatus?: string;
};

export type ResearchUpdates = {
  updatedOn: string;
  logOpenedOn: string;
  updates: ResearchUpdate[];
};

export type ResearchData = {
  ledger: ResearchLedger;
  updates: ResearchUpdates;
  map: ResearchMap;
};

export type VerifiedResearchData = ResearchData & {
  sourceCommit: string;
  checkedAt: string;
};

// One shared runtime validator is used by the browser, API and audit.
export {
  parseResearchData,
  parseVerifiedResearch,
} from "../../lib/research-state.mjs";

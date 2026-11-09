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
};

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

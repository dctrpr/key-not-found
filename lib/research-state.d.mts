import type {
  ResearchData,
  VerifiedResearchData,
} from "../src/lib/researchState.ts";
export function parseResearchData(
  ledger: unknown,
  updates: unknown,
  map: unknown,
): ResearchData;
export function parseVerifiedResearch(value: unknown): VerifiedResearchData;

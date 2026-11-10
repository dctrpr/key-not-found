/**
 * One vocabulary for method status across the hero, map, ledger and log.
 * A status describes only the recorded method and its declared candidates.
 */
export type StatusTone = "tested" | "open" | "question" | "corrected" | "active";
export type StatusBucket = "tested" | "open" | "in-progress";

type StatusSource = { status: string; kind?: string };

const OPEN = ["partial", "untested", "open"];
const ACTIVE = ["in-progress", "in_progress"];

export const isOpenStatus = (status: string) => OPEN.includes(status);
export const isActiveStatus = (status: string) => ACTIVE.includes(status);

export function statusBucket(status: string): StatusBucket {
  if (isActiveStatus(status)) return "in-progress";
  return isOpenStatus(status) ? "open" : "tested";
}

export function describeStatus(method: StatusSource): {
  tone: StatusTone;
  label: string;
} {
  const { status, kind } = method;
  if (isActiveStatus(status)) return { tone: "active", label: "In progress" };
  if (status === "partial") return { tone: "open", label: "Partial lead" };
  if (status === "untested" || status === "open")
    return { tone: "question", label: "Open question" };
  if (status === "invalidated") return { tone: "corrected", label: "Corrected" };
  // An audit that falsifies an earlier claim is a correction to the record.
  if (status === "falsified" && kind === "evidence-audit")
    return { tone: "corrected", label: "Claim invalidated" };
  if (status === "falsified")
    return { tone: "tested", label: "Tested · no result" };
  if (status === "tested") return { tone: "tested", label: "Tested" };
  return { tone: "tested", label: status.replace(/[-_]/g, " ") };
}

const plural = (count: number, one: string, many: string) =>
  count + " " + (count === 1 ? one : many);

/** A short, scoped tally. It never reports progress toward a solution. */
export function tallyStatuses(methods: StatusSource[]) {
  const count: Record<StatusTone, number> = {
    active: 0,
    open: 0,
    question: 0,
    tested: 0,
    corrected: 0,
  };
  for (const method of methods) count[describeStatus(method).tone] += 1;
  return [
    count.active && count.active + " in progress",
    count.open && plural(count.open, "partial lead", "partial leads"),
    count.question && plural(count.question, "open question", "open questions"),
    count.tested && count.tested + " tested, no result",
    count.corrected && count.corrected + " corrected",
  ]
    .filter(Boolean)
    .join(" · ");
}

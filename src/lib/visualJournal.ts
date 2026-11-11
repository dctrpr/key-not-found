import bundled from '../../public/data/visual-journal.json';

export type VisualJournalDiagram = 'funnel' | 'history' | 'support' | 'measurement' | 'reading' | 'source' | 'review';
export type VisualJournalMetric = { label: string; value: number; pointer: string; operation?: 'countActive' };
export type VisualJournalScene = { layout: 'spread' | 'stack' | 'mirror'; page: number; source?: 'issue26' | 'issue27' | 'funky' };
export type VisualJournalExhibit = { path: string; sha256: string; label: string; width?: number; height?: number };
export type VisualJournalEntry = {
  id: string;
  completedAtUTC: string;
  title: string;
  summary: string;
  result: string;
  diagram: VisualJournalDiagram;
  metrics: VisualJournalMetric[];
  source: { path: string; sha256: string };
  evidence: string;
  scene: VisualJournalScene;
  sceneNote: string;
  methodId: string;
  exhibits?: VisualJournalExhibit[];
};
export type VisualJournal = {
  version: 1;
  updatedOn: string;
  caseStatus: 'unsolved';
  description: string;
  entries: VisualJournalEntry[];
};

const diagrams = new Set<VisualJournalDiagram>(['funnel', 'history', 'support', 'measurement', 'reading', 'source', 'review']);
type RecordValue = Record<string, unknown>;
function object(value: unknown, required: string[], optional: string[] = []): RecordValue {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid visual journal object');
  const item = value as RecordValue;
  const allowed = new Set([...required, ...optional]);
  if (required.some(key => !Object.hasOwn(item, key)) || Object.keys(item).some(key => !allowed.has(key))) {
    throw new Error('Invalid visual journal fields');
  }
  return item;
}
function text(value: unknown, max: number): string {
  if (typeof value !== 'string' || !value.trim() || value.length > max || /[\u0000-\u001f\u007f]/.test(value)) {
    throw new Error('Invalid visual journal text');
  }
  return value;
}
function id(value: unknown): string {
  const result = text(value, 100);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(result)) throw new Error('Invalid visual journal identifier');
  return result;
}
function date(value: unknown): string {
  const result = text(value, 10);
  const parsed = Date.parse(result + 'T00:00:00Z');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(result) || !Number.isFinite(parsed) || new Date(parsed).toISOString().slice(0, 10) !== result) {
    throw new Error('Invalid visual journal date');
  }
  return result;
}
function timestamp(value: unknown): string {
  const result = text(value, 24);
  const parsed = Date.parse(result);
  const canonical = result.length === 20 ? result.replace('Z', '.000Z') : result;
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(result) || !Number.isFinite(parsed) ||
      new Date(parsed).toISOString() !== canonical) {
    throw new Error('Invalid visual journal completion time');
  }
  return result;
}
function hash(value: unknown): string {
  const result = text(value, 64);
  if (!/^[a-f0-9]{64}$/.test(result)) throw new Error('Invalid visual journal hash');
  return result;
}
// Reject schemes, query strings, fragments, percent escapes, backslashes and dot segments.
function researchPath(value: unknown, absolute: boolean): string {
  const result = text(value, 350);
  if (absolute && !result.startsWith('/research/')) throw new Error('Invalid visual journal surface');
  const relative = absolute ? result.slice('/research/'.length) : result;
  if (!relative || relative.split('/').some(segment => !/^[A-Za-z0-9][A-Za-z0-9_.-]*$/.test(segment) || segment === '.' || segment === '..')) {
    throw new Error('Invalid visual journal path');
  }
  return result;
}
function integer(value: unknown, max = Number.MAX_SAFE_INTEGER): number {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || value < 0 || value > max) throw new Error('Invalid visual journal number');
  return value;
}
function metric(value: unknown): VisualJournalMetric {
  const item = object(value, ['label', 'value', 'pointer'], ['operation']);
  const pointer = text(item.pointer, 300);
  if (!/^(?:\/(?:[^~\u0000-\u001f\u007f]|~[01])*)+$/.test(pointer)) throw new Error('Invalid visual journal pointer');
  if (item.operation !== undefined && item.operation !== 'countActive') throw new Error('Invalid visual journal operation');
  return { label: text(item.label, 80), value: integer(item.value), pointer,
    ...(item.operation === undefined ? {} : { operation: item.operation }) };
}
function scene(value: unknown): VisualJournalScene {
  const item = object(value, ['layout', 'page'], ['source']);
  if (item.layout !== 'spread' && item.layout !== 'stack' && item.layout !== 'mirror') throw new Error('Invalid visual journal layout');
  if (item.source !== undefined && item.source !== 'issue26' && item.source !== 'issue27' && item.source !== 'funky') throw new Error('Unknown visual journal source');
  const page = integer(item.page);
  const [first, last] = item.source === 'issue26' ? [102, 104] : item.source === 'issue27' ? [78, 81] : item.source === 'funky' ? [107, 112] : [73, 80];
  if (page < first || page > last) throw new Error('Invalid visual journal page');
  return { layout: item.layout, page, ...(item.source === undefined ? {} : { source: item.source }) };
}
function exhibit(value: unknown): VisualJournalExhibit {
  const item = object(value, ['path', 'sha256', 'label'], ['width', 'height']);
  const path = researchPath(item.path, true);
  if (!/\.(?:png|jpe?g|webp|avif)$/.test(path) || (item.width === undefined) !== (item.height === undefined)) throw new Error('Invalid visual journal exhibit');
  const dimensions = item.width === undefined ? {} : { width: integer(item.width, 20_000), height: integer(item.height, 20_000) };
  if ('width' in dimensions && (!dimensions.width || !dimensions.height)) throw new Error('Invalid visual journal dimensions');
  return { path, sha256: hash(item.sha256), label: text(item.label, 200), ...dimensions };
}
function entry(value: unknown): VisualJournalEntry {
  const item = object(value, ['id', 'completedAtUTC', 'title', 'summary', 'result', 'diagram', 'metrics', 'source', 'evidence', 'scene', 'sceneNote', 'methodId'], ['exhibits']);
  if (!diagrams.has(item.diagram as VisualJournalDiagram) || !Array.isArray(item.metrics) || item.metrics.length !== 3) throw new Error('Unsupported visual journal frame');
  const source = object(item.source, ['path', 'sha256']);
  if (item.exhibits !== undefined && (!Array.isArray(item.exhibits) || !item.exhibits.length || item.exhibits.length > 8)) throw new Error('Invalid visual journal exhibits');
  return {
    id: id(item.id), completedAtUTC: timestamp(item.completedAtUTC), title: text(item.title, 180),
    summary: text(item.summary, 1000), result: text(item.result, 1500), diagram: item.diagram as VisualJournalDiagram,
    metrics: item.metrics.map(metric), source: { path: researchPath(source.path, false), sha256: hash(source.sha256) },
    evidence: researchPath(item.evidence, true), scene: scene(item.scene), sceneNote: text(item.sceneNote, 1000), methodId: id(item.methodId),
    ...(item.exhibits === undefined ? {} : { exhibits: (item.exhibits as unknown[]).map(exhibit) }),
  };
}
function parseJournal(value: unknown): VisualJournal {
  const item = object(value, ['version', 'updatedOn', 'caseStatus', 'description', 'entries']);
  if (item.version !== 1 || item.caseStatus !== 'unsolved' || !Array.isArray(item.entries) || !item.entries.length || item.entries.length > 500) {
    throw new Error('Unsupported visual journal');
  }
  const entries = item.entries.map(entry);
  const updatedOn = date(item.updatedOn);
  if (new Set(entries.map(frame => frame.id)).size !== entries.length || entries.some((frame, i) => i > 0 && Date.parse(frame.completedAtUTC) < Date.parse(entries[i - 1].completedAtUTC)) ||
      updatedOn !== entries[entries.length - 1].completedAtUTC.slice(0, 10)) throw new Error('Inconsistent visual journal history');
  return { version: 1, updatedOn, caseStatus: 'unsolved', description: text(item.description, 700), entries };
}

/** The checked build ships a complete fallback when polling is unavailable or invalid. */
export const bundledVisualJournal: VisualJournal = parseJournal(bundled);

// These renderer branches contain case-specific prose/counts; a fresh context needs a renderer release.
const context = (frame: VisualJournalEntry) => JSON.stringify({ diagram: frame.diagram, metrics: frame.metrics, scene: frame.scene, methodId: frame.methodId });
const bundledContexts = new Set(bundledVisualJournal.entries.filter(frame => frame.diagram !== 'funnel').map(context));

/** Accept a valid unchanged journal or appended frames; never replace recorded history. */
export function getAppendOnlyJournal(current: VisualJournal, input: unknown): VisualJournal | null {
  try {
    const previous = parseJournal(current);
    const next = parseJournal(input);
    if (next.description !== previous.description || next.updatedOn < previous.updatedOn || next.entries.length < previous.entries.length ||
        previous.entries.some((frame, i) => JSON.stringify(frame) !== JSON.stringify(next.entries[i]))) return null;
    if (next.entries.length === previous.entries.length) return next.updatedOn === previous.updatedOn ? current : null;
    const appended = next.entries.slice(previous.entries.length);
    if (appended.some(frame => frame.diagram !== 'funnel' && !bundledContexts.has(context(frame)))) return null;
    return { ...next, entries: [...current.entries, ...appended] };
  } catch {
    return null;
  }
}

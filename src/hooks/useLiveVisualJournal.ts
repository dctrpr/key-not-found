import { useEffect, useState } from 'react';
import { bundledVisualJournal, getAppendOnlyJournal } from '../lib/visualJournal';

/** Published frames refresh in open tabs; the checked bundle survives any failure. */
export default function useLiveVisualJournal() {
  const [journal, setJournal] = useState(bundledVisualJournal);
  useEffect(() => {
    let active = true;
    let request: AbortController | null = null;
    let lastAttempt = 0;
    async function refresh() {
      if (document.visibilityState === 'hidden' || request) return;
      const controller = new AbortController();
      request = controller;
      lastAttempt = Date.now();
      const timeout = window.setTimeout(() => controller.abort(), 12_000);
      try {
        const response = await fetch('/data/visual-journal.json', {
          cache: 'no-store', signal: controller.signal,
          headers: { Accept: 'application/json' },
        });
        if (!response.ok) return;
        const text = await response.text();
        if (text.length > 1_000_000) return;
        const next: unknown = JSON.parse(text);
        if (active) setJournal(previous => getAppendOnlyJournal(previous, next) ?? previous);
      } catch {
        // Keep the last checked frames, including while offline.
      } finally {
        window.clearTimeout(timeout);
        request = null;
      }
    }
    void refresh();
    const interval = window.setInterval(() => { void refresh(); }, 300_000);
    const visible = () => {
      if (document.visibilityState === 'visible' && Date.now() - lastAttempt >= 60_000)
        void refresh();
    };
    document.addEventListener('visibilitychange', visible);
    return () => {
      active = false;
      request?.abort();
      window.clearInterval(interval);
      document.removeEventListener('visibilitychange', visible);
    };
  }, []);
  return journal;
}

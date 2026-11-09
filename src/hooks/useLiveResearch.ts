import { useEffect, useMemo, useRef, useState } from "react";
import { parseVerifiedResearch } from "../lib/researchState.ts";
import type {
  ResearchData,
  ResearchLedger,
  ResearchMap,
  ResearchUpdates,
  VerifiedResearchData,
} from "../lib/researchState.ts";

const POLL_MS = 5 * 60 * 1000;
const FRESH_MS = 10 * 60 * 1000;

type Fallback = {
  ledger: ResearchLedger | null;
  updates: ResearchUpdates | null;
  map: ResearchMap | null;
};

export type ResearchSyncStatus = "checking" | "verified" | "stale" | "snapshot";

/** Public main-branch data; static inputs remain available if GitHub cannot sync. */
export default function useLiveResearch(fallback: Fallback) {
  const [remote, setRemote] = useState<VerifiedResearchData | null>(null);
  const [attemptAt, setAttemptAt] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const [checking, setChecking] = useState(true);
  const lastAttempt = useRef(0);

  useEffect(() => {
    let active = true;
    let request: AbortController | null = null;
    async function refresh() {
      if (document.visibilityState === "hidden" || request) return;
      const controller = new AbortController();
      request = controller;
      lastAttempt.current = Date.now();
      setAttemptAt(new Date().toISOString());
      const timeout = window.setTimeout(() => controller.abort(), 12_000);
      try {
        const response = await fetch("/api/research-state", {
          signal: controller.signal,
          headers: { Accept: "application/json" },
        });
        if (!response.ok) throw new Error("Research sync unavailable");
        const data = parseVerifiedResearch(await response.json());
        if (active) {
          setRemote(data);
          setFailed(false);
        }
      } catch {
        if (active) setFailed(true);
      } finally {
        window.clearTimeout(timeout);
        if (active) setChecking(false);
        request = null;
      }
    }
    void refresh();
    const interval = window.setInterval(() => {
      void refresh();
    }, POLL_MS);
    const visible = () => {
      if (
        document.visibilityState === "visible" &&
        Date.now() - lastAttempt.current >= POLL_MS
      )
        void refresh();
    };
    document.addEventListener("visibilitychange", visible);
    return () => {
      active = false;
      request?.abort();
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", visible);
    };
  }, []);

  const data = useMemo<ResearchData | null>(() => {
    if (remote) return remote;
    if (fallback.ledger && fallback.updates && fallback.map)
      return {
        ledger: fallback.ledger,
        updates: fallback.updates,
        map: fallback.map,
      };
    return null;
  }, [remote, fallback.ledger, fallback.updates, fallback.map]);

  const status: ResearchSyncStatus = remote
    ? failed || Date.now() - Date.parse(remote.checkedAt) > FRESH_MS
      ? "stale"
      : "verified"
    : checking
      ? "checking"
      : "snapshot";
  return {
    data,
    status,
    sourceCommit: remote?.sourceCommit ?? null,
    checkedAt: remote?.checkedAt ?? null,
    lastAttemptAt: attemptAt,
  };
}

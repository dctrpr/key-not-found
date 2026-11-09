#!/usr/bin/env python3
"""Audit whether plain-text corrections add a selector/instruction, not key material."""

from __future__ import annotations

import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORRECTION_JSON = ROOT / "analysis_outputs/plain_text_transcript/plain_article_correction_report.json"
ACTIVE_CONSISTENCY_MD = ROOT / "analysis_outputs/plain_text_transcript/active_corridor_witness_consistency/active_corridor_witness_consistency.md"
AUTHORITY_DRIFT_MD = ROOT / "analysis_outputs/source_audit/active_text_authority_drift/active_text_authority_drift.md"
OUT_DIR = ROOT / "analysis_outputs/plain_text_transcript/correction_selector_impact"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
]

TARGET_TERMS = [
    "buying",
    "dip",
    "billion",
    "volcano",
    "bonds",
    "imf",
    "bukele",
    "salvador",
    "sell",
    "novogratz",
    "trust",
    "shitcoiner",
    "heart",
    "money",
]

ACTIVE_IDS = {
    "buying the dip": "O4",
    "$1 billion": "B4",
    "volcano bonds": "G5",
    "shitcoiner at heart": "O5",
    "should sell": "p78-frame context",
    "future bitcoin earnings": "p78-frame context",
    "imf loan": "G5-neighbor context",
    "mike novogratz": "Typeka Mix context",
    "trust that guy": "O5-neighbor context",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+|[“”\"'.?,;:!()%-]", text)


def term_hits(text: str, terms: list[str]) -> list[str]:
    lower = normalize(text)
    found: list[str] = []
    for term in terms:
        if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lower):
            found.append(term)
    return found


def diff_tokens(raw: str, fixed: str) -> dict[str, list[str]]:
    raw_tokens = tokens(raw)
    fixed_tokens = tokens(fixed)
    removed: list[str] = []
    added: list[str] = []
    for tag, i1, i2, j1, j2 in SequenceMatcher(a=raw_tokens, b=fixed_tokens).get_opcodes():
        if tag in {"replace", "delete"}:
            removed.extend(raw_tokens[i1:i2])
        if tag in {"replace", "insert"}:
            added.extend(fixed_tokens[j1:j2])
    return {"removed": removed, "added": added}


def active_phrase_hits(text: str) -> list[str]:
    lower = normalize(text)
    hits: list[str] = []
    for phrase, label in ACTIVE_IDS.items():
        if phrase in lower:
            hits.append(label)
    return hits


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = json.loads(CORRECTION_JSON.read_text())
    corrections = report["manualCorrections"]

    rows = []
    for idx, corr in enumerate(corrections, start=1):
        raw = corr["raw"]
        fixed = corr["fixed"]
        delta = diff_tokens(raw, fixed)
        row = {
            "index": idx,
            "raw": raw,
            "fixed": fixed,
            "reason": corr["reason"],
            "rawPatternPresent": corr.get("rawPatternPresent"),
            "removedTokens": delta["removed"],
            "addedTokens": delta["added"],
            "rawInstructionHits": term_hits(raw, INSTRUCTION_TERMS),
            "fixedInstructionHits": term_hits(fixed, INSTRUCTION_TERMS),
            "addedInstructionHits": term_hits(" ".join(delta["added"]), INSTRUCTION_TERMS),
            "rawTargetHits": term_hits(raw, TARGET_TERMS),
            "fixedTargetHits": term_hits(fixed, TARGET_TERMS),
            "addedTargetHits": term_hits(" ".join(delta["added"]), TARGET_TERMS),
            "activePhraseHitsRaw": active_phrase_hits(raw),
            "activePhraseHitsFixed": active_phrase_hits(fixed),
        }
        row["affectsActiveCorridor"] = bool(
            row["fixedTargetHits"] or row["activePhraseHitsFixed"] or row["rawTargetHits"] or row["activePhraseHitsRaw"]
        )
        row["addsSelectorPermission"] = bool(row["addedInstructionHits"])
        rows.append(row)

    active_rows = [row for row in rows if row["affectsActiveCorridor"]]
    selector_rows = [row for row in rows if row["addsSelectorPermission"]]
    added_target_rows = [row for row in rows if row["addedTargetHits"] or row["activePhraseHitsFixed"]]

    assessment = [
        "The correction layer repairs exact wording but does not add a source-backed extraction instruction.",
        "No correction-added token is a procedural unit/order term such as read/take/select/word/letter/line/edge/font/mirror/key.",
        "The important page-76 correction is the restored G5 phrase `Volcano Bonds`; it repairs a missing active target in the latest raw plain text rather than creating a new selector.",
        "The O4 correction only moves the period inside the quote for `buying the dip.`; this matters for exact text but not for geometry/order.",
        "Other target-adjacent corrections (`money`, `$2 trillion`, capitalization/punctuation) are text-authority guardrails, not extraction permission.",
    ]
    decision = (
        "Use the corrected/DOCM text as wording authority, but do not treat the correction list itself as a selector or instruction stream."
    )
    next_move = (
        "Continue to require an external/source rule naming unit and order before extraction; correction markup only locks exact wording."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Plain-text correction impact audit focused on selector/instruction terms. No key derivation.",
        "sources": {
            "correctionReport": str(CORRECTION_JSON.relative_to(ROOT)),
            "activeCorridorWitness": str(ACTIVE_CONSISTENCY_MD.relative_to(ROOT)),
            "activeTextAuthority": str(AUTHORITY_DRIFT_MD.relative_to(ROOT)),
        },
        "correctionCount": len(rows),
        "activeCorridorCorrectionCount": len(active_rows),
        "selectorPermissionCorrectionCount": len(selector_rows),
        "addedTargetCorrectionCount": len(added_target_rows),
        "rows": rows,
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    (OUT_DIR / "correction_selector_impact.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# Plain Correction Selector Impact",
        "",
        "Scope: check whether the latest plain-text correction markup adds a human-readable selector/instruction, especially around the page-76 corridor. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Corrections checked: `{len(rows)}`",
        f"- Corrections touching target/corridor terms: `{len(active_rows)}`",
        f"- Corrections adding selector-permission terms: `{len(selector_rows)}`",
        "",
        "## Corridor-Relevant Corrections",
        "",
        "| # | raw | fixed | added tokens | target hits | added instruction hits | active phrase hits |",
        "|---:|---|---|---|---|---|---|",
    ]
    for row in active_rows:
        lines.append(
            f"| {row['index']} | `{row['raw']}` | `{row['fixed']}` | "
            f"`{' '.join(row['addedTokens']) or '-'}` | "
            f"{', '.join(row['fixedTargetHits']) or '-'} | "
            f"{', '.join(row['addedInstructionHits']) or '-'} | "
            f"{', '.join(row['activePhraseHitsFixed']) or '-'} |"
        )

    lines.extend(
        [
            "",
            "## Selector-Permission Check",
            "",
        ]
    )
    if selector_rows:
        for row in selector_rows:
            lines.append(f"- Correction `{row['index']}` adds instruction terms: `{', '.join(row['addedInstructionHits'])}`")
    else:
        lines.append("- No correction-added token is a procedural selector term.")

    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}", ""])
    (OUT_DIR / "correction_selector_impact.md").write_text("\n".join(lines))

    print(OUT_DIR / "correction_selector_impact.md")
    print(OUT_DIR / "correction_selector_impact.json")


if __name__ == "__main__":
    main()

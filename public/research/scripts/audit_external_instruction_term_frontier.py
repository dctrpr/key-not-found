#!/usr/bin/env python3
"""Scan archived external/provenance files for overlooked selector wording.

This pass looks for procedural/extraction terms near active target terms in
archived external clue material and source-provenance reports. It does not
generate key candidates or transform article text into private keys.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/external_clues/external_instruction_term_frontier"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "external_instruction_term_frontier.json"
OUT_MD = OUT / "external_instruction_term_frontier.md"

SEARCH_ROOTS = [
    ROOT / "analysis_outputs/external_clues",
    ROOT / "analysis_outputs/source_audit/thread_1632068898169450497.html",
]

EXTENSIONS = {".md", ".txt", ".json", ".html"}

PROCEDURAL_TERMS = [
    "read",
    "take",
    "use",
    "extract",
    "select",
    "choose",
    "count",
    "line",
    "word",
    "letter",
    "character",
    "first",
    "last",
    "left",
    "right",
    "above",
    "below",
    "inside",
    "outside",
    "mirror",
    "reverse",
    "backward",
    "fold",
    "rotate",
    "light",
    "key",
    "private",
    "encoded",
    "page",
    "zero",
    "#0",
    "pill",
    "capsule",
    "dose",
    "dosage",
    "line up",
    "diff",
]

TARGET_TERMS = [
    "volcano bonds",
    "volcano",
    "shitcoiner at heart",
    "shitcoiner",
    "heart",
    "imf",
    "bukele",
    "el salvador",
    "buying the dip",
    "$1 billion",
    "1 billion",
    "page 76",
    "p76",
    "g5",
    "o5",
]

NOISE_PATTERNS = [
    "analysis_outputs/",
    "script",
    "tested by",
    "finding:",
    "assessment",
    "next best move",
    "current status",
    "evidenceexists",
    "key derivation",
    "no key",
    "no address",
    "candidate",
    "hash",
    "wif",
    "seed",
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for root in SEARCH_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        if root.exists():
            for path in root.rglob("*"):
                if path.is_file() and path.suffix.lower() in EXTENSIONS:
                    if OUT in path.parents:
                        continue
                    files.append(path)
    return sorted(set(files))


def plain_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".json":
        try:
            return json.dumps(json.loads(text), ensure_ascii=False)
        except Exception:
            return text
    return text


def windows_for_terms(text: str, terms: list[str], radius: int = 160) -> list[dict]:
    lowered = text.lower()
    windows = []
    for term in terms:
        pattern = re.escape(term.lower()).replace(r"\ ", r"\s+")
        for match in re.finditer(pattern, lowered):
            start = max(0, match.start() - radius)
            end = min(len(text), match.end() + radius)
            window = re.sub(r"\s+", " ", text[start:end]).strip()
            windows.append({"term": term, "start": match.start(), "window": window})
    return windows


def term_hits(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    hits = []
    for term in terms:
        pattern = re.escape(term.lower()).replace(r"\ ", r"\s+")
        if re.search(pattern, lowered):
            hits.append(term)
    return hits


def is_mostly_internal(window: str) -> bool:
    lowered = window.lower()
    return sum(1 for pattern in NOISE_PATTERNS if pattern in lowered) >= 2


def is_rawish_source_file(path: Path) -> bool:
    rel = str(path.relative_to(ROOT))
    return any(
        marker in rel
        for marker in [
            "original_clue_provenance",
            "canva_source_inspection",
            "canva_connector_metadata_audit",
            "thread_1632068898169450497.html",
        ]
    )


def is_related_thread_noise(window: str) -> bool:
    lowered = window.lower()
    return "step 4." in lowered and "step 5." in lowered and "nasty shitcoiner" in lowered


def main() -> None:
    files = iter_files()
    records = []
    raw_external_hits = []
    for path in files:
        text = plain_text(path)
        proc_hits = term_hits(text, PROCEDURAL_TERMS)
        target_hits = term_hits(text, TARGET_TERMS)
        if not proc_hits and not target_hits:
            continue
        windows = []
        for item in windows_for_terms(text, TARGET_TERMS):
            ph = term_hits(item["window"], PROCEDURAL_TERMS)
            th = term_hits(item["window"], TARGET_TERMS)
            if ph and th:
                windows.append({**item, "proceduralHits": ph, "targetHits": th, "mostlyInternal": is_mostly_internal(item["window"])})
        record = {
            "file": str(path.relative_to(ROOT)),
            "proceduralHits": proc_hits,
            "targetHits": target_hits,
            "cooccurrenceWindows": windows[:12],
            "cooccurrenceCount": len(windows),
            "externalSourceLike": path.parts[-2] in {"external_clues", "max_thread_media"} or "thread_1632068898169450497.html" in str(path),
            "rawishSourceFile": is_rawish_source_file(path),
        }
        records.append(record)
        if record["externalSourceLike"]:
            raw_external_hits.append(record)

    external_cooccurrences = [
        window
        for record in raw_external_hits
        for window in record["cooccurrenceWindows"]
        if not window["mostlyInternal"]
    ]
    rawish_cooccurrences = [
        {**window, "file": record["file"]}
        for record in raw_external_hits
        if record["rawishSourceFile"]
        for window in record["cooccurrenceWindows"]
        if not window["mostlyInternal"]
    ]
    actionable_rawish = [
        window
        for window in rawish_cooccurrences
        if not is_related_thread_noise(window["window"])
    ]
    term_counts = Counter()
    target_counts = Counter()
    for record in records:
        term_counts.update(record["proceduralHits"])
        target_counts.update(record["targetHits"])

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "scan archived external/provenance files for procedural extraction terms near active target terms; no key derivation",
        "filesScanned": len(files),
        "recordsWithHits": len(records),
        "proceduralTermCounts": dict(term_counts.most_common()),
        "targetTermCounts": dict(target_counts.most_common()),
        "rawExternalRecords": raw_external_hits,
        "externalNonInternalCooccurrenceCount": len(external_cooccurrences),
        "externalNonInternalCooccurrences": external_cooccurrences[:20],
        "rawishNonInternalCooccurrenceCount": len(rawish_cooccurrences),
        "rawishNonInternalCooccurrences": rawish_cooccurrences[:20],
        "actionableRawishCooccurrenceCount": len(actionable_rawish),
        "actionableRawishCooccurrences": actionable_rawish[:20],
        "assessment": [
            "Archived external clue material contains the known broad instructions: private/key/encoded, mirror, page/source references, and Canva source-fidelity language.",
            "No raw/original-ish external window was found that combines the active G5/O5 target terms with a new explicit unit such as word, letter, line, first, last, or take.",
            "The only raw thread co-occurrence involving `shitcoiner` is from a related-thread/step-list card, not the 2023 puzzle announcement media or text.",
            "The meaningful external signals remain source/provenance signals: Schott mirror-writing, announcement media corridor targeting, Canva source-fidelity gaps (`pills don't line up`, `#0`, `diff pic`).",
            "This keeps the next path source acquisition/validation, not another local key candidate branch.",
        ],
        "nextMove": "If a new source is supplied, run source validation against zero/#0 hotspots, p79 pill geometry, page-76 priority crops, and the repaired p78-frame exact-edge benchmark.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# External Instruction-Term Frontier",
        "",
        "Scope: scan archived external/provenance files for procedural extraction terms near active target terms. No key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Files scanned: `{result['filesScanned']}`",
        f"- Files with procedural or target hits: `{result['recordsWithHits']}`",
        f"- Non-internal external co-occurrence windows: `{result['externalNonInternalCooccurrenceCount']}`",
        f"- Raw/original-ish non-internal co-occurrence windows: `{result['rawishNonInternalCooccurrenceCount']}`",
        f"- Actionable raw/original-ish co-occurrence windows: `{result['actionableRawishCooccurrenceCount']}`",
        "",
        "## External Source-Like Records",
        "",
        "| file | procedural hits | target hits | co-occurrence windows |",
        "|---|---|---|---:|",
    ]
    for record in raw_external_hits:
        lines.append(
            f"| `{record['file']}` | `{', '.join(record['proceduralHits']) or '-'}` | `{', '.join(record['targetHits']) or '-'}` | {record['cooccurrenceCount']} |"
        )

    lines.extend(["", "## Raw/Original-Ish Co-Occurrence Samples", ""])
    if rawish_cooccurrences:
        for item in rawish_cooccurrences[:10]:
            label = "related-thread noise" if is_related_thread_noise(item["window"]) else "actionable"
            lines.append(f"- `{item['file']}` `{item['term']}` ({label}) hits `{', '.join(item['proceduralHits'])}`: {item['window']}")
    else:
        lines.append("- none")

    lines.extend(["", "## Non-Internal Co-Occurrence Samples", ""])
    if external_cooccurrences:
        for item in external_cooccurrences[:10]:
            lines.append(f"- `{item['term']}` hits `{', '.join(item['proceduralHits'])}`: {item['window']}")
    else:
        lines.append("- none")

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("files scanned:", len(files))
    print("external non-internal cooccurrences:", len(external_cooccurrences))


if __name__ == "__main__":
    main()

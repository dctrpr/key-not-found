#!/usr/bin/env python3
"""Rank page-76 corridor lines by already-logged independent evidence.

This is an explanation/triage pass. It does not derive keys, hash text, or
generate wallet candidates.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORRIDOR_PATH = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
LANDING_PATH = ROOT / "analysis_outputs/source_audit/line_offset_landing_evidence/line_offset_landing_evidence.json"
SUPPORTED_PATH = ROOT / "analysis_outputs/source_audit/supported_landing_sequence_units/supported_landing_sequence_units.json"
CONVERGENCE_PATH = ROOT / "analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json"
FRAME_PATH = ROOT / "analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read.json"
OUT_DIR = ROOT / "analysis_outputs/source_audit/page76_next_target_chooser"
OUT_MD = OUT_DIR / "page76_next_target_chooser.md"
OUT_JSON = OUT_DIR / "page76_next_target_chooser.json"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def add_evidence(row: dict, label: str, weight: float, detail: str) -> None:
    row["score"] += weight
    row["evidence"].append({"label": label, "weight": weight, "detail": detail})


def line_for_label(records: list[dict], label: str) -> dict | None:
    wanted = norm(label)
    for row in records:
        if wanted and wanted in norm(row["text"]):
            return row
    return None


def main() -> None:
    corridor = json.loads(CORRIDOR_PATH.read_text())
    landing = json.loads(LANDING_PATH.read_text())
    supported = json.loads(SUPPORTED_PATH.read_text())
    convergence = json.loads(CONVERGENCE_PATH.read_text())
    frame = json.loads(FRAME_PATH.read_text())

    rows = []
    by_line = {}
    for record in corridor["records"]:
        row = {
            "lineIndex": record["lineIndex"],
            "corridorIndex": record["corridorIndex"],
            "text": record["text"],
            "highlights": record["highlights"],
            "score": 0.0,
            "evidence": [],
        }
        rows.append(row)
        by_line[record["lineIndex"]] = row

    # Line-offset evidence is the strongest already-normalized line scoring.
    for item in landing["scoredLandings"]:
        row = by_line.get(item["targetLine"])
        if not row:
            continue
        if item["score"] > 0:
            add_evidence(
                row,
                "line-offset landing score",
                float(item["score"]),
                f"{item['sourceId']} lands here; layers={', '.join(item['layers']) or '-'}",
            )

    # Supported sequence adds a small bonus for lines that survive the sequence audit.
    for item in supported["supportedRows"]:
        row = by_line.get(item["targetLine0"])
        if row:
            add_evidence(
                row,
                "supported landing sequence",
                1.0,
                f"{item['sourceId']} / preferred term `{item.get('preferredTerm', '-')}`",
            )

    # Target convergence is phrase-level. Map labels back into corrected corridor lines.
    for item in convergence["ranking"]:
        row = line_for_label(rows, item["label"])
        if row:
            add_evidence(
                row,
                "target convergence",
                float(item["score"]),
                f"{item['target']} `{item['label']}` across {item['independentLayerCount']} independent layers",
            )

    # P78 frame edge events are local geometry hits. Reward cuts more than adjacency.
    for edge, events in frame["edgeEvents"].items():
        for event in events:
            row = line_for_label(rows, event["label"])
            if not row:
                continue
            relation = event.get("relation", "")
            weight = 3.0 if relation == "cuts" else 1.5
            add_evidence(
                row,
                "p78 frame edge",
                weight,
                f"{edge} edge {relation} `{event['label']}` distance={event.get('distance')}",
            )

    # Exact-edge minimal frame phrase specifically joins should-sell -> G5 -> O5.
    for label in ["should sell", "Volcano Bonds", "shitcoiner at heart"]:
        row = line_for_label(rows, label)
        if row:
            add_evidence(
                row,
                "minimal frame phrase",
                2.0,
                "`should sell | Volcano Bonds | shitcoiner at heart`",
            )

    # Public/media target corridor support is broad, so keep it low weight and local.
    for label in ["El Salvador", "buying the dip", "President Nayib Bukele", "volcanoes", "$1 billion", "Volcano Bonds", "IMF", "shitcoiner at heart"]:
        row = line_for_label(rows, label.replace("$", ""))
        if row:
            add_evidence(row, "announcement/media corridor term", 0.75, label)

    ranked = sorted(rows, key=lambda row: (-row["score"], row["lineIndex"]))

    decision = {
        "primaryManualTarget": {
            "lineIndex": ranked[0]["lineIndex"],
            "corridorIndex": ranked[0]["corridorIndex"],
            "text": ranked[0]["text"],
            "score": ranked[0]["score"],
        },
        "pairedTarget": None,
        "sourceBandTarget": None,
    }
    for row in ranked[1:]:
        if "Volcano Bonds" in row["text"]:
            decision["pairedTarget"] = {
                "lineIndex": row["lineIndex"],
                "corridorIndex": row["corridorIndex"],
                "text": row["text"],
                "score": row["score"],
            }
            break
    for row in ranked:
        if "earnings" in row["text"] or "could sell" in row["text"]:
            decision["sourceBandTarget"] = {
                "lineIndex": row["lineIndex"],
                "corridorIndex": row["corridorIndex"],
                "text": row["text"],
                "score": row["score"],
            }
            break

    report = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Rank page-76 corrected corridor lines by already-logged independent evidence; no key derivation.",
        "inputs": [
            str(CORRIDOR_PATH.relative_to(ROOT)),
            str(LANDING_PATH.relative_to(ROOT)),
            str(SUPPORTED_PATH.relative_to(ROOT)),
            str(CONVERGENCE_PATH.relative_to(ROOT)),
            str(FRAME_PATH.relative_to(ROOT)),
        ],
        "decision": decision,
        "rankedLines": ranked,
        "assessment": [
            "Line 32 / O5 remains the strongest manual target because convergence, p78 frame cuts, the #5 landing, and p80/OVERDOSE corroboration all point there.",
            "Line 27 / G5 is the required paired target, not a standalone solution, because it carries Volcano Bonds and the p78 frame relation but lacks the O5 convergence weight.",
            "Lines 26 and 29 are the broad p78 source-band targets. They explain the #4 evidence conflict but still do not name an extraction unit.",
            "The next useful comparison for any new source image should crop/score line 32, line 27, and the line 26-29 band before any key derivation resumes.",
        ],
        "nextMove": "Use this ranked target set as the manual checklist for future Canva/original-layout/physical source comparison: primary O5, paired G5, then the line 26-29 p78 source band.",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Page 76 Next Target Chooser",
        "",
        "Scope: rank corrected page-76 corridor lines by already-logged independent evidence. No key derivation, hashing, seed phrases, WIF checks, or address checks were run.",
        "",
        f"- Created: `{report['createdAt']}`",
        "",
        "## Decision",
        "",
        f"- Primary manual target: L{decision['primaryManualTarget']['lineIndex']:02d} / corridor {decision['primaryManualTarget']['corridorIndex']} `{decision['primaryManualTarget']['text']}` score `{decision['primaryManualTarget']['score']}`.",
    ]
    if decision["pairedTarget"]:
        target = decision["pairedTarget"]
        lines.append(
            f"- Required paired target: L{target['lineIndex']:02d} / corridor {target['corridorIndex']} `{target['text']}` score `{target['score']}`."
        )
    if decision["sourceBandTarget"]:
        target = decision["sourceBandTarget"]
        lines.append(
            f"- Broad source-band target: L{target['lineIndex']:02d} / corridor {target['corridorIndex']} `{target['text']}` score `{target['score']}`."
        )

    lines.extend(
        [
            "",
            "## Ranked Lines",
            "",
            "| rank | line | corridor | score | text | main evidence |",
            "|---:|---:|---:|---:|---|---|",
        ]
    )
    for rank, row in enumerate(ranked, 1):
        top_evidence = "; ".join(f"{ev['label']}({ev['weight']})" for ev in row["evidence"][:4])
        lines.append(
            f"| {rank} | {row['lineIndex']} | {row['corridorIndex']} | {row['score']:.2f} | `{row['text']}` | {top_evidence or '-'} |"
        )

    lines.extend(["", "## Top Evidence Details", ""])
    for row in ranked[:5]:
        lines.append(f"### L{row['lineIndex']:02d} `{row['text']}`")
        for ev in row["evidence"]:
            lines.append(f"- {ev['label']} +{ev['weight']}: {ev['detail']}")
        lines.append("")

    lines.extend(
        [
            "## Assessment",
            "",
            "- L32/O5 is the next manual target for any future source comparison, not a solved extraction unit.",
            "- L27/G5 must travel with it because the strongest target is a pair: `Volcano Bonds` / `shitcoiner at heart`.",
            "- L26-L29 explains the #4/p78 graphic band conflict and should be cropped as a band if a new source appears.",
            "- No local line-ranking result justifies new key derivation without a new source rule.",
            "",
            "## Next Move",
            "",
            "- For future Canva/original-layout/physical scans, score these in order: L32/O5, L27/G5, then L26-L29. Require a named extraction unit before trying keys again.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(json.dumps(report["decision"], indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Test opener capsule order through the M3/M4 endpoint system.

Prior audits showed a clean five-capsule order on the photographed OVERDOSE
opener, and that order projects near page-76 marks M3/M4. This pass tests only
whether the resulting M3/M4 sequence can choose usable lower-corridor phrase
units.

No key derivation is performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORDERED_JSON = ROOT / "analysis_outputs/source_audit/ordered_capsule_projection/ordered_capsule_projection.json"
BRACKET_JSON = ROOT / "analysis_outputs/source_audit/m3_m4_pair_bracket/m3_m4_pair_bracket.json"
OUT = ROOT / "analysis_outputs/source_audit/opener_capsule_endpoint_selector"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "opener_capsule_endpoint_selector.json"
OUT_MD = OUT / "opener_capsule_endpoint_selector.md"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "word",
    "letter",
    "line",
    "left",
    "right",
    "mirror",
    "fold",
    "key",
    "private",
    "first",
    "last",
    "middle",
    "down",
    "up",
]


MARK_TO_UNIT = {
    "M3": {
        "label": "trust that guy",
        "role": "M3 axis / lower row support",
        "initial": "t",
        "last": "y",
    },
    "M4": {
        "label": "shitcoiner at heart",
        "role": "M3/M4 bracket endpoint / O5",
        "initial": "s",
        "last": "t",
    },
}


def hits(value: str) -> list[str]:
    lower = value.lower()
    return [term for term in INSTRUCTION_TERMS if term in lower]


def nearest_mark(row: dict) -> tuple[str, float] | tuple[None, None]:
    for target in row["nearestTargets"]:
        if target["kind"] == "mark" and target["index"] in {3, 4}:
            return f"M{target['index']}", float(target["distancePx"])
    return None, None


def main() -> None:
    ordered = json.loads(ORDERED_JSON.read_text())
    bracket = json.loads(BRACKET_JSON.read_text())
    rows = []
    for row in ordered["orderedCapsuleProjection"]:
        mark, dist = nearest_mark(row)
        rows.append(
            {
                "capsuleOrder": row["capsuleOrder"],
                "p79OrangeBoxIndex": row["p79OrangeBoxIndex"],
                "mappedCenter": row["mappedCenter"],
                "nearestEndpointMark": mark,
                "nearestEndpointDistancePx": dist,
                "forcedUnit": MARK_TO_UNIT[mark]["label"] if mark else None,
                "forcedRole": MARK_TO_UNIT[mark]["role"] if mark else None,
            }
        )

    forced_marks = [row["nearestEndpointMark"] for row in rows]
    forced_units = [row["forcedUnit"] for row in rows]
    thresholds = {}
    for threshold in [75, 100, 150, 250, 500]:
        selected = []
        for row in rows:
            if row["nearestEndpointDistancePx"] is not None and row["nearestEndpointDistancePx"] <= threshold:
                selected.append(row["nearestEndpointMark"])
            else:
                selected.append("-")
        thresholds[str(threshold)] = {
            "sequence": "".join(selected),
            "assignedCount": sum(1 for item in selected if item != "-"),
        }

    streams = {
        "forcedMarkSequence": "".join(forced_marks),
        "forcedUnitLabels": " | ".join(forced_units),
        "forcedInitials": "".join(MARK_TO_UNIT[m]["initial"] for m in forced_marks),
        "forcedLasts": "".join(MARK_TO_UNIT[m]["last"] for m in forced_marks),
        "m3As0Binary": "".join("0" if m == "M3" else "1" for m in forced_marks),
        "m3As1Binary": "".join("1" if m == "M3" else "0" for m in forced_marks),
        "bracketStream": bracket["streams"]["bracketedWordsLeftToRight"],
    }
    stream_hits = {name: hits(value) for name, value in streams.items()}
    assessment = [
        "The five opener capsules project into the M3/M4 visual endpoint region, but the geometry is only tight for the first capsule.",
        "Forced nearest-mark reading gives M3 M3 M4 M4 M4, which maps to repeated `trust that guy` and O5 `shitcoiner at heart` units.",
        "Thresholded readings are unstable: tight thresholds leave most capsules unassigned, while loose thresholds force a pattern without a rule.",
        "The M3/M4 endpoint system confirms O5 again, but it still does not specify a word/letter/line extraction unit.",
        "Close opener-capsule -> M3/M4 endpoint mapping as a direct selector under the current scan.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "opener five-capsule order through M3/M4 endpoint units; no key derivation",
        "rows": rows,
        "thresholds": thresholds,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": assessment,
        "nextMove": "Keep opener capsules as provenance/order evidence only. Reopen only if a new source transform places all five capsules tightly on text units or a clue names M3/M4 as a binary/index selector.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Opener Capsule Endpoint Selector",
        "",
        "Scope: test whether the five opener capsules, after projection near M3/M4, choose usable page-76 lower-corridor units. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Streams",
        "",
    ]
    for name, value in streams.items():
        hit_text = ", ".join(stream_hits[name]) if stream_hits[name] else "none"
        lines.append(f"- `{name}` hits={hit_text}: `{value}`")

    lines.extend(["", "## Threshold Stability", ""])
    for threshold, info in thresholds.items():
        lines.append(f"- <= `{threshold}px`: assigned `{info['assignedCount']}` / 5, sequence `{info['sequence']}`")

    lines.extend(
        [
            "",
            "## Capsule Rows",
            "",
            "| capsule | p79 box | nearest mark | distance | forced unit |",
            "|---:|---:|---|---:|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['capsuleOrder']} | {row['p79OrangeBoxIndex']} | `{row['nearestEndpointMark']}` | `{row['nearestEndpointDistancePx']}` | {row['forcedUnit']} |"
        )

    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("forcedMarkSequence", streams["forcedMarkSequence"], "hits", stream_hits["forcedUnitLabels"])
    print("thresholds", thresholds)


if __name__ == "__main__":
    main()

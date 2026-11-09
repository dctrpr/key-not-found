#!/usr/bin/env python3
"""Build a single validation packet for future source/physical material.

This consolidates the current source-registration evidence into one checklist
so a future physical scan, Canva export, browser capture, or layout file can be
scored before any extraction/key work resumes.

No OCR extraction, key derivation, hashing, seed checks, WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/future_source_validation_packet"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "future_source_validation_packet.json"
OUT_MD = OUT / "future_source_validation_packet.md"
REVIEW_SHEET = OUT / "future_source_validation_review_sheet.jpg"

SOURCE_REG = ROOT / "analysis_outputs/source_audit/source_registration_acceptance_test/source_registration_acceptance_test.json"
CURRENT_BENCH = ROOT / "analysis_outputs/source_audit/current_scan_acceptance_benchmark/current_scan_acceptance_benchmark.json"
PRIORITY_CROPS = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json"
TRICONTACT = ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json"
P77_LINE = ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json"
ZERO_CROPS = ROOT / "analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops.json"
PILL_GEOM = ROOT / "analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry.json"
SOURCE_DELTA = ROOT / "analysis_outputs/source_audit/source_delta_watch/source_delta_watch.json"
FONT_CONTACTS = ROOT / "analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states.json"
TYPEKA_AUTHORITY = ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(p)


def pick_constraints(source_reg: dict) -> list[dict]:
    rows = []
    for item in source_reg.get("constraints", []):
        rows.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "currentStatus": item.get("currentStatus"),
                "acceptance": item.get("acceptance"),
                "futureUse": "gate" if item.get("currentStatus") in {"FAIL", "PARTIAL"} else "baseline",
            }
        )
    return rows


def triconact_summary(data: dict) -> dict:
    records = {row["name"]: row for row in data.get("records", [])}
    current = records.get("current", {})
    repaired = records.get("nearest_grid_dx_-40") or records.get("g5_edge_touch", {})
    return {
        "overlay": rel(data.get("overlay")),
        "currentFrame": current.get("frame"),
        "currentO5OverlapVsTarget": current.get("o5OverlapVsTarget"),
        "currentG5GapPx": current.get("leftEdgeToG5RightPx"),
        "currentM3RightEdgeOverlapPx": current.get("rightEdgeM3VerticalOverlapPx"),
        "repairDx": repaired.get("dx"),
        "repairDy": repaired.get("dy"),
        "repairFrame": repaired.get("frame"),
        "repairG5OverlapVsTarget": repaired.get("g5OverlapVsTarget"),
        "repairO5OverlapVsTarget": repaired.get("o5OverlapVsTarget"),
        "repairTriContactPass": repaired.get("triContactPass"),
    }


def exact_edge_summary(data: dict) -> dict:
    summaries = {row["name"]: row for row in data.get("summaries", [])}
    best = summaries.get("nearest_grid_dx_minus_40") or summaries.get("g5_edge_touch_dx_minus_38") or {}
    streams = best.get("streams", {})
    return {
        "sheet": rel(data.get("sheet")),
        "scenario": best.get("name"),
        "topDownStyles": streams.get("topDownStyles"),
        "exactEdgeLabels": streams.get("exactEdgeLabels"),
        "exactEdgeStyles": streams.get("exactEdgeStyles"),
        "instructionHits": best.get("instructionTermHits") or {},
    }


def typeka_authority_summary(data: dict) -> dict:
    panels = data.get("panels", [])
    target_rows = []
    for panel in panels:
        for target in panel.get("targets", []):
            if target.get("id") in {"one_billion", "volcano_bonds", "shitcoiner_heart", "novogratz", "trust_that_guy"}:
                target_rows.append(target)
    return {
        "sheet": rel(data.get("sheet")),
        "sourceAudit": rel(data.get("sourceAudit")),
        "panelCount": len(panels),
        "keyTargets": target_rows,
        "assessment": data.get("assessment", [])[:3],
    }


def zero_summary(data: dict) -> dict:
    rows = data.get("rows", [])
    top = rows[0] if rows else {}
    return {
        "sheet": rel(data.get("sheet")),
        "primaryHotspot": {
            "page": top.get("articlePage"),
            "token": top.get("token"),
            "zeroCount": top.get("zeroCount"),
            "visualReadFromTrustedScan": top.get("visualReadFromTrustedScan"),
            "crop": rel(top.get("highresCrop")),
        },
        "hotspotCount": len(rows),
    }


def pill_summary(data: dict) -> dict:
    fragments = data.get("trustedHighresFragments", [])
    return {
        "sheet": rel(data.get("sheet")),
        "articlePage": data.get("articlePage"),
        "fragmentCount": len(fragments),
        "fragmentCenters": [row.get("center") for row in fragments],
        "assessment": data.get("assessment", [])[:2],
    }


def priority_summary(data: dict) -> dict:
    crops = data.get("crops", [])
    return {
        "sheet": rel(data.get("sheet")),
        "sourceImage": rel(data.get("sourceImage")),
        "targetPriority": data.get("targetPriority"),
        "cropCount": len(crops),
        "crops": [
            {
                "id": row.get("id") or row.get("name"),
                "label": row.get("label"),
                "path": rel(row.get("path") or row.get("cropPath")),
                "box": row.get("box") or row.get("cropBox"),
            }
            for row in crops
        ],
    }


def line_gap_summary(data: dict) -> dict:
    gap = data.get("gapVsLinePitch", {})
    hits = data.get("hitSummary", {})
    near = data.get("nearMiss", {})
    return {
        "sourcePage": near.get("sourcePage"),
        "sourceLabel": near.get("sourceLabel"),
        "target": near.get("targetId"),
        "baselineVerticalGapPx": gap.get("baselineVerticalGapPx"),
        "contentBoxVerticalGapPx": gap.get("contentBoxVerticalGapPx"),
        "medianLinePitchPx": gap.get("medianLinePitchPx"),
        "baselineGapMinusMedianPitchPx": gap.get("baselineGapMinusMedianPitchPx"),
        "p77OneLineUpO5HitCount": hits.get("p77OneLineUpO5HitCount"),
    }


def main() -> None:
    source_reg = load_json(SOURCE_REG)
    current = load_json(CURRENT_BENCH)
    priority = load_json(PRIORITY_CROPS)
    tri = load_json(TRICONTACT)
    line = load_json(P77_LINE)
    zero = load_json(ZERO_CROPS)
    pill = load_json(PILL_GEOM)
    delta = load_json(SOURCE_DELTA)
    font = load_json(FONT_CONTACTS)
    typeka = load_json(TYPEKA_AUTHORITY)

    packet = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "future source/physical validation packet; no key derivation",
        "reviewSheet": rel(REVIEW_SHEET) if REVIEW_SHEET.exists() else None,
        "currentDecision": {
            "currentScanStatusCounts": current.get("statusCounts"),
            "blockingConstraints": current.get("blockingConstraints"),
            "sourceDeltaDecision": delta.get("decision"),
            "actionableUnknownSourceCount": delta.get("actionableUnknownCount"),
        },
        "constraints": pick_constraints(source_reg),
        "benchmarks": {
            "page76PriorityCrops": priority_summary(priority),
            "p78FrameTriContact": triconact_summary(tri),
            "repairedFrameFontContact": exact_edge_summary(font),
            "typekaTypographyAuthority": typeka_authority_summary(typeka),
            "p77LinePitchNearMiss": line_gap_summary(line),
            "zeroHash0Hotspots": zero_summary(zero),
            "p79PillFragments": pill_summary(pill),
        },
        "minimumReopenConditions": [
            {
                "condition": "C3 extraction unit",
                "requiredEvidence": "source/clue text or source-visible layout must name a unit/order such as word, letter, line, edge, font, first/last, left/right, or equivalent",
                "why": "Without this, local geometry only repeats target discovery.",
            },
            {
                "condition": "C4 physical registration",
                "requiredEvidence": "physical scan/photo/hold-to-light/spread should create repeated direct O5/G5 contacts or improve the p77 71.93px near miss under one natural transform",
                "why": "Current best scan gives zero true physical O5/G5 overlaps.",
            },
            {
                "condition": "C8 source image quality",
                "requiredEvidence": "original Canva/export/browser/source asset must exceed thumbnail status and visibly resolve the #0, p79 pills, XX/barbed-wire, or p78 frame benchmarks",
                "why": "The current Canva surface is only a 668x376 investigator note thumbnail.",
            },
            {
                "condition": "C2 p78 frame signature",
                "requiredEvidence": "new source should naturally preserve or explain `should sell | Volcano Bonds | shitcoiner at heart`, current O5 clip, M3 right-edge cut, and dx≈-38/-40 G5 edge repair",
                "why": "This is the compactest existing registration signature.",
            },
        ],
        "decision": "use_packet_before_reopening_extraction",
        "nextMove": "When a new source appears, compare it against this packet first; only then run a named-unit extraction test.",
    }

    OUT_JSON.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Future Source Validation Packet",
        "",
        "Scope: consolidate the current source/geometry benchmarks that a future scan, Canva export, browser capture, or layout file must improve before extraction resumes. No key candidates were generated.",
        "",
        f"- Created: `{packet['createdAt']}`",
        f"- Current scan status counts: `{packet['currentDecision']['currentScanStatusCounts']}`",
        f"- Blocking constraints: `{packet['currentDecision']['blockingConstraints']}`",
        f"- Source-delta decision: `{packet['currentDecision']['sourceDeltaDecision']}`",
        f"- Review sheet: `{packet['reviewSheet'] or 'not generated yet'}`",
        "",
        "## Minimum Reopen Conditions",
        "",
        "| condition | required evidence | why |",
        "|---|---|---|",
    ]
    for row in packet["minimumReopenConditions"]:
        lines.append(f"| {row['condition']} | {row['requiredEvidence']} | {row['why']} |")

    lines.extend(["", "## Core Benchmarks", ""])
    frame = packet["benchmarks"]["p78FrameTriContact"]
    exact = packet["benchmarks"]["repairedFrameFontContact"]
    typeka_b = packet["benchmarks"]["typekaTypographyAuthority"]
    p77 = packet["benchmarks"]["p77LinePitchNearMiss"]
    zero_b = packet["benchmarks"]["zeroHash0Hotspots"]
    pills = packet["benchmarks"]["p79PillFragments"]
    priority_b = packet["benchmarks"]["page76PriorityCrops"]

    lines.extend(
        [
            f"- Page-76 priority crop sheet: `{priority_b['sheet']}` (`{priority_b['cropCount']}` crops).",
            f"- p78 frame current box: `{frame['currentFrame']}`; current O5 overlap `{frame['currentO5OverlapVsTarget']}`, G5 gap `{frame['currentG5GapPx']}` px, M3 right-edge overlap `{frame['currentM3RightEdgeOverlapPx']}` px.",
            f"- p78 frame repair: dx `{frame['repairDx']}`, dy `{frame['repairDy']}`, frame `{frame['repairFrame']}`, tri-contact pass `{frame['repairTriContactPass']}`.",
            f"- Repaired exact-edge phrase/style: `{exact['exactEdgeLabels']}` / `{exact['exactEdgeStyles']}`.",
            f"- Typeka typography authority sheet: `{typeka_b['sheet']}` (`{typeka_b['panelCount']}` panels); use DOCM states, not Markdown bold, for lower-corridor font/highlight labels.",
            f"- p77 near miss: `{p77['sourceLabel']}` -> `{p77['target']}`, vertical gap `{p77['baselineVerticalGapPx']}` px, page-76 median line pitch `{p77['medianLinePitchPx']}` px.",
            f"- Zero/#0 primary hotspot: page `{zero_b['primaryHotspot']['page']}` token `{zero_b['primaryHotspot']['token']}`, trusted read `{zero_b['primaryHotspot']['visualReadFromTrustedScan']}`.",
            f"- p79 pill fragments: `{pills['fragmentCount']}` trusted fragments on page `{pills['articlePage']}`.",
        ]
    )

    lines.extend(["", "## C1-C9 Gate Summary", "", "| id | status | future use | acceptance test |", "|---|---|---|---|"])
    for row in packet["constraints"]:
        lines.append(f"| `{row['id']}` | `{row['currentStatus']}` | `{row['futureUse']}` | {row['acceptance']} |")

    lines.extend(["", "## Decision", "", f"- `{packet['decision']}`.", f"- Next move: {packet['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("decision:", packet["decision"])


if __name__ == "__main__":
    main()

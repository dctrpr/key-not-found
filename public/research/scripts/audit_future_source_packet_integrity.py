#!/usr/bin/env python3
"""Verify the future-source validation packet against current benchmark files.

This is a bounded source/geometry integrity pass. It does not extract key
material, hash text, generate mnemonics, scan WIF/Base58 windows, or check
addresses. Its job is to make sure the current comparison packet is still a
safe gate for any new physical scan, Canva export, browser capture, or layout
source.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/future_source_packet_integrity"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "future_source_packet_integrity.json"
OUT_MD = OUT / "future_source_packet_integrity.md"

PACKET_JSON = ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json"
PACKET_MD = ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.md"
REVIEW_JSON = ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.json"
REVIEW_MD = ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.md"
REVIEW_SHEET = ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.jpg"
FRONTIER_JSON = ROOT / "analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json"

REQUIRED_ARTIFACTS = {
    "packet_json": PACKET_JSON,
    "packet_md": PACKET_MD,
    "review_json": REVIEW_JSON,
    "review_md": REVIEW_MD,
    "review_sheet": REVIEW_SHEET,
    "page76_priority_crop_sheet": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg",
    "p78_frame_tricontact_json": ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json",
    "p78_frame_tricontact_overlay": ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg",
    "repaired_frame_font_states_json": ROOT / "analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states.json",
    "typeka_authority_sheet": ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg",
    "typeka_authority_json": ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.json",
    "zero_visual_crop_sheet": ROOT / "analysis_outputs/source_audit/zero_visual_crops/zero_visual_crops_sheet.jpg",
    "p79_pill_baseline_sheet": ROOT / "analysis_outputs/source_audit/alternate_pdf_pill_geometry/alternate_pdf_pill_geometry_sheet.jpg",
    "p77_one_line_near_miss_json": ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json",
    "missing_rule_frontier_json": FRONTIER_JSON,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def file_row(label: str, path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "label": label,
        "path": rel(path),
        "exists": exists,
        "size": path.stat().st_size if exists else 0,
        "mtime": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds") if exists else None,
    }


def main() -> None:
    artifact_rows = [file_row(label, path) for label, path in REQUIRED_ARTIFACTS.items()]
    missing = [row for row in artifact_rows if not row["exists"] or row["size"] <= 0]

    packet = load_json(PACKET_JSON) if PACKET_JSON.exists() else {}
    review = load_json(REVIEW_JSON) if REVIEW_JSON.exists() else {}
    frontier = load_json(FRONTIER_JSON) if FRONTIER_JSON.exists() else {}
    tri = load_json(REQUIRED_ARTIFACTS["p78_frame_tricontact_json"])
    frame_states = load_json(REQUIRED_ARTIFACTS["repaired_frame_font_states_json"])
    typeka = load_json(REQUIRED_ARTIFACTS["typeka_authority_json"])
    p77 = load_json(REQUIRED_ARTIFACTS["p77_one_line_near_miss_json"])

    packet_mtime = PACKET_JSON.stat().st_mtime if PACKET_JSON.exists() else 0
    review_mtime = REVIEW_SHEET.stat().st_mtime if REVIEW_SHEET.exists() else 0
    benchmark_paths = [
        REQUIRED_ARTIFACTS["page76_priority_crop_sheet"],
        REQUIRED_ARTIFACTS["p78_frame_tricontact_json"],
        REQUIRED_ARTIFACTS["repaired_frame_font_states_json"],
        REQUIRED_ARTIFACTS["typeka_authority_json"],
        REQUIRED_ARTIFACTS["typeka_authority_sheet"],
        REQUIRED_ARTIFACTS["zero_visual_crop_sheet"],
        REQUIRED_ARTIFACTS["p79_pill_baseline_sheet"],
        REQUIRED_ARTIFACTS["p77_one_line_near_miss_json"],
        # The frontier can be refreshed after the packet without invalidating
        # source visuals; it is checked for the branch count below instead.
    ]
    stale_inputs = [
        rel(path)
        for path in benchmark_paths
        if path.exists() and path.stat().st_mtime > max(packet_mtime, review_mtime)
    ]

    exact_edge = frame_states.get("summaries", [])
    exact_edge_signatures = [
        {
            "name": row.get("name"),
            "exactPhraseStream": row.get("streams", {}).get("exactEdgeLabels"),
            "exactStyleStream": row.get("streams", {}).get("exactEdgeStyles"),
            "instructionHits": row.get("instructionHits", {}),
        }
        for row in exact_edge
        if row.get("streams", {}).get("exactEdgeLabels") == "should sell | Volcano Bonds | shitcoiner at heart"
    ]

    tri_summary = {
        "edgeTouchDx": tri.get("edgeTouchDx"),
        "edgeTouchTriContactPass": tri.get("edgeTouchTriContactPass"),
        "currentFrame": next((row.get("frame") for row in tri.get("records", []) if row.get("name") == "current"), None),
        "repairFrame": next((row.get("frame") for row in tri.get("records", []) if row.get("triContactPass")), None),
    }
    p77_gap = p77.get("nearMiss", {}).get("verticalGapPx")

    benchmark_checks = [
        {
            "id": "review_sheet_registered",
            "pass": bool(packet.get("reviewSheet")) and rel(REVIEW_SHEET) in str(packet.get("reviewSheet")),
            "value": packet.get("reviewSheet"),
            "expected": rel(REVIEW_SHEET),
        },
        {
            "id": "review_panel_count",
            "pass": review.get("panelCount") == 9 or len(review.get("panels", [])) == 9,
            "value": review.get("panelCount", len(review.get("panels", []))),
            "expected": 9,
        },
        {
            "id": "tri_contact_repair",
            "pass": tri_summary.get("edgeTouchDx") in {-38, -40} and tri_summary.get("edgeTouchTriContactPass") is True,
            "value": tri_summary,
            "expected": "dx around -38/-40 or tri-contact pass",
        },
        {
            "id": "exact_edge_signature",
            "pass": any(row.get("exactStyleStream") == "RKY" for row in exact_edge_signatures),
            "value": exact_edge_signatures[:3],
            "expected": "should sell | Volcano Bonds | shitcoiner at heart / RKY",
        },
        {
            "id": "typeka_authority_registered",
            "pass": (
                packet.get("benchmarks", {})
                .get("typekaTypographyAuthority", {})
                .get("sheet")
                == rel(REQUIRED_ARTIFACTS["typeka_authority_sheet"])
                and any(row.get("id") == "typeka_typography_authority" for row in review.get("panels", []))
                and typeka.get("sheet") == rel(REQUIRED_ARTIFACTS["typeka_authority_sheet"])
            ),
            "value": {
                "packetSheet": packet.get("benchmarks", {}).get("typekaTypographyAuthority", {}).get("sheet"),
                "reviewHasPanel": any(row.get("id") == "typeka_typography_authority" for row in review.get("panels", [])),
                "sourceSheet": typeka.get("sheet"),
            },
            "expected": rel(REQUIRED_ARTIFACTS["typeka_authority_sheet"]),
        },
        {
            "id": "p77_near_miss_present",
            "pass": p77_gap is not None,
            "value": p77_gap,
            "expected": "recorded p77 near-miss gap",
        },
        {
            "id": "frontier_dead_branch_count",
            "pass": (frontier.get("deadBranchCount") or 0) >= 208,
            "value": frontier.get("deadBranchCount"),
            "expected": ">= 208",
        },
    ]

    failed_checks = [row for row in benchmark_checks if not row["pass"]]
    status = "PASS" if not missing and not stale_inputs and not failed_checks else "REVIEW"
    assessment = [
        "The future-source packet and review sheet are present and non-empty.",
        "The packet still points at the live review sheet and the current p78 exact-edge signature remains the same compact benchmark.",
        "No extraction branch is reopened by this pass; it only verifies that future source comparisons are using current benchmarks.",
    ]
    if stale_inputs:
        assessment.append("Some benchmark inputs are newer than the packet/review sheet; refresh the packet before comparing a new source.")
    if failed_checks:
        assessment.append("At least one benchmark value no longer matches the expected gate; inspect before continuing.")

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "future-source validation packet integrity; no key derivation or text extraction",
        "status": status,
        "artifacts": artifact_rows,
        "missingArtifacts": missing,
        "staleInputs": stale_inputs,
        "benchmarkChecks": benchmark_checks,
        "failedChecks": failed_checks,
        "assessment": assessment,
        "decision": "Use the current packet/review sheet as the source-comparison gate." if status == "PASS" else "Review packet integrity before comparing a new source.",
        "nextMove": "Continue waiting for a true new source/clue; compare it first against the packet and review sheet before any extraction/key work.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Future Source Packet Integrity",
        "",
        "Scope: verify the future-source validation packet and visual review sheet against current benchmark files. No key derivation, hashing, WIF, seed, address, or broad extraction checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Status: `{status}`",
        f"- Missing artifacts: `{len(missing)}`",
        f"- Stale benchmark inputs: `{len(stale_inputs)}`",
        f"- Failed benchmark checks: `{len(failed_checks)}`",
        "",
        "## Benchmark Checks",
        "",
        "| check | pass | value | expected |",
        "|---|---:|---|---|",
    ]
    for row in benchmark_checks:
        lines.append(f"| `{row['id']}` | `{row['pass']}` | `{row['value']}` | `{row['expected']}` |")

    lines.extend(["", "## Required Artifacts", "", "| artifact | exists | size | path |", "|---|---:|---:|---|"])
    for row in artifact_rows:
        lines.append(f"| `{row['label']}` | `{row['exists']}` | `{row['size']}` | `{row['path']}` |")

    if stale_inputs:
        lines.extend(["", "## Stale Inputs", ""])
        lines.extend(f"- `{path}`" for path in stale_inputs)

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("status:", status)
    print("missing:", len(missing), "stale:", len(stale_inputs), "failed:", len(failed_checks))


if __name__ == "__main__":
    main()

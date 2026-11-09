#!/usr/bin/env python3
"""Integrity-check the source acquisition target packet.

This pass verifies that the handoff packet for future physical/original-layout
evidence is complete and internally consistent. It does not extract text,
derive keys, hash candidates, scan WIF/Base58 windows, or check addresses.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from textwrap import wrap
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_acquisition_packet_integrity"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_acquisition_packet_integrity.json"
OUT_MD = OUT / "source_acquisition_packet_integrity.md"
SHEET = OUT / "source_acquisition_packet_integrity_sheet.jpg"

PACKET_JSON = ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.json"
PACKET_MD = ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.md"
PACKET_SHEET = ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet_sheet.jpg"
SOURCE_REOPEN_JSON = ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json"
FUTURE_PACKET_JSON = ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json"
UNLOCK_MATRIX_JSON = ROOT / "analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix.json"
ARRIVAL_WATCH_JSON = ROOT / "analysis_outputs/source_audit/post_unlock_source_arrival_watch/post_unlock_source_arrival_watch.json"

CRITICAL_ARTIFACTS = {
    "packet_json": PACKET_JSON,
    "packet_md": PACKET_MD,
    "packet_sheet": PACKET_SHEET,
    "source_reopen_json": SOURCE_REOPEN_JSON,
    "source_reopen_sheet": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements_sheet.jpg",
    "future_packet_json": FUTURE_PACKET_JSON,
    "future_packet_sheet": ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.jpg",
    "unlock_matrix_json": UNLOCK_MATRIX_JSON,
    "unlock_matrix_sheet": ROOT / "analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix_sheet.jpg",
    "arrival_watch_json": ARRIVAL_WATCH_JSON,
    "arrival_watch_sheet": ROOT / "analysis_outputs/source_audit/post_unlock_source_arrival_watch/post_unlock_source_arrival_watch_sheet.jpg",
    "page76_priority_crop_json": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json",
    "page76_priority_crop_sheet": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg",
    "p78_tricontact_json": ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature.json",
    "p78_tricontact_overlay": ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg",
    "physical_model_overlay": ROOT / "analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation_overlay.jpg",
    "p77_one_line_json": ROOT / "analysis_outputs/source_audit/p77_one_line_near_miss/p77_one_line_near_miss.json",
    "capsule_motif_sheet": ROOT / "analysis_outputs/source_audit/capsule_motif_recurrence/capsule_motif_recurrence_sheet.jpg",
    "p80_package_sheet": ROOT / "analysis_outputs/source_audit/p80_package_r3_gate_synthesis/p80_package_r3_gate_synthesis_sheet.jpg",
    "typeka_font_sheet": ROOT / "analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis_sheet.jpg",
}

VISUALS = [
    ("packet", PACKET_SHEET),
    ("page76 targets", ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg"),
    ("p78 tri-contact", ROOT / "analysis_outputs/source_audit/p78_frame_tricontact_signature/p78_frame_tricontact_signature_overlay.jpg"),
    ("source reopen", ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements_sheet.jpg"),
    ("unlock matrix", ROOT / "analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix_sheet.jpg"),
    ("arrival watch", ROOT / "analysis_outputs/source_audit/post_unlock_source_arrival_watch/post_unlock_source_arrival_watch_sheet.jpg"),
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def file_row(label: str, path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "label": label,
        "path": rel(path),
        "exists": exists,
        "size": path.stat().st_size if exists else 0,
        "mtime": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds") if exists else None,
    }


def path_exists(value: str | Path | None) -> bool:
    if not value:
        return False
    p = Path(value)
    if not p.is_absolute():
        p = ROOT / p
    return p.exists() and p.stat().st_size > 0


def build_visual_sheet(checks: list[dict[str, Any]], panels: list[dict[str, Any]]) -> None:
    margin = 28
    sheet_w = 1320
    header_h = 96
    checklist_h = 34 * (len(checks) + 1) + 34
    thumb_w = 400
    thumb_h = 245
    gap = 20
    rows = (len(VISUALS) + 2) // 3
    sheet_h = margin * 2 + header_h + checklist_h + rows * (thumb_h + 52) + gap * max(0, rows - 1)

    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal_font = font(18)
    small_font = font(14)
    mono_font = font(15)

    draw.text((margin, margin), "Source Acquisition Packet Integrity", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 44),
        "Readiness check for future physical/original-layout/raw-clue evidence. No extraction or key checks.",
        fill=(174, 184, 196),
        font=normal_font,
    )

    y = margin + header_h
    draw.rectangle((margin, y, sheet_w - margin, y + 30), fill=(29, 34, 42))
    draw.text((margin + 12, y + 6), "check", fill=(236, 241, 247), font=small_font)
    draw.text((margin + 430, y + 6), "status", fill=(236, 241, 247), font=small_font)
    draw.text((margin + 530, y + 6), "value", fill=(236, 241, 247), font=small_font)
    y += 34
    for row in checks:
        ok = bool(row["pass"])
        fill = (18, 23, 28) if ok else (45, 25, 25)
        status_color = (113, 222, 154) if ok else (255, 123, 123)
        draw.rectangle((margin, y, sheet_w - margin, y + 30), fill=fill)
        draw.text((margin + 12, y + 6), row["id"], fill=(220, 228, 235), font=mono_font)
        draw.text((margin + 430, y + 6), "OK" if ok else "REVIEW", fill=status_color, font=mono_font)
        value = str(row.get("value"))
        draw.text((margin + 530, y + 6), value[:95], fill=(174, 184, 196), font=small_font)
        y += 34

    y += 24
    for idx, (label, path) in enumerate(VISUALS):
        col = idx % 3
        row = idx // 3
        x = margin + col * (thumb_w + gap)
        yy = y + row * (thumb_h + 52 + gap)
        draw.text((x, yy), label, fill=(236, 241, 247), font=normal_font)
        yy += 28
        draw.rectangle((x, yy, x + thumb_w, yy + thumb_h), fill=(19, 22, 28), outline=(52, 62, 75))
        if path.exists():
            img = Image.open(path).convert("RGB")
            img.thumbnail((thumb_w - 8, thumb_h - 8))
            sheet.paste(img, (x + 4, yy + 4))
        else:
            draw.text((x + 14, yy + 105), "missing", fill=(255, 123, 123), font=normal_font)

    sheet.save(SHEET, quality=94)


def main() -> None:
    packet = load_json(PACKET_JSON)
    reopen = load_json(SOURCE_REOPEN_JSON)
    future = load_json(FUTURE_PACKET_JSON)
    unlock = load_json(UNLOCK_MATRIX_JSON)
    arrival = load_json(ARRIVAL_WATCH_JSON)

    critical_files = [file_row(label, path) for label, path in CRITICAL_ARTIFACTS.items()]
    missing_critical = [row for row in critical_files if not row["exists"] or row["size"] <= 0]

    packet_panels = packet.get("sheetPanels", [])
    missing_packet_panels = [
        {"title": panel.get("title"), "path": panel.get("path")}
        for panel in packet_panels
        if not path_exists(panel.get("path"))
    ]

    capture_jobs = packet.get("captureJobs", [])
    r_gate_coverage = sorted({gate for job in capture_jobs for gate in job.get("rGates", [])})
    benchmark_ids = sorted({row.get("id") for row in packet.get("benchmarkChecks", []) if row.get("id")})
    target_priority = packet.get("targetPriority", {})
    future_constraints = future.get("constraints", [])
    future_constraint_ids = sorted({row.get("id") for row in future_constraints if row.get("id")})

    checks = [
        {
            "id": "critical_artifacts_present",
            "pass": len(missing_critical) == 0,
            "value": f"{len(critical_files) - len(missing_critical)}/{len(critical_files)} present",
            "expected": "all critical packet artifacts present",
        },
        {
            "id": "packet_visual_panels_present",
            "pass": len(packet_panels) >= 8 and len(missing_packet_panels) == 0,
            "value": f"{len(packet_panels)} panels, {len(missing_packet_panels)} missing",
            "expected": "8 packet panel files present",
        },
        {
            "id": "capture_jobs_complete",
            "pass": len(capture_jobs) == 5,
            "value": len(capture_jobs),
            "expected": 5,
        },
        {
            "id": "r1_r5_gate_coverage",
            "pass": all(gate in r_gate_coverage for gate in ["R1", "R2", "R3", "R4", "R5"]),
            "value": ",".join(r_gate_coverage),
            "expected": "R1,R2,R3,R4,R5",
        },
        {
            "id": "benchmark_gate_coverage",
            "pass": all(check in benchmark_ids for check in ["C2", "C3", "C4", "C8"]),
            "value": ",".join(benchmark_ids),
            "expected": "C2,C3,C4,C8",
        },
        {
            "id": "active_target_priority_present",
            "pass": all(key in target_priority for key in ["primaryManualTarget", "pairedTarget", "sourceBandTarget"]),
            "value": ",".join(sorted(target_priority.keys())),
            "expected": "primaryManualTarget,pairedTarget,sourceBandTarget",
        },
        {
            "id": "source_reopen_gate_count",
            "pass": len(reopen.get("reopenGates", [])) == 5,
            "value": len(reopen.get("reopenGates", [])),
            "expected": 5,
        },
        {
            "id": "orientation_guardrail_present",
            "pass": "C9" in future_constraint_ids
            and any(row.get("id") == "R4" for row in reopen.get("reopenGates", [])),
            "value": f"future={','.join(future_constraint_ids)}; reopen={[row.get('id') for row in reopen.get('reopenGates', [])]}",
            "expected": "C9 plus R4 orientation discipline",
        },
        {
            "id": "unlock_matrix_still_blocks_extraction",
            "pass": unlock.get("decision") == "current_evidence_stack_not_sufficient_to_resume_extraction"
            and unlock.get("summary", {}).get("allPathsBlockedOnR3") is True,
            "value": unlock.get("decision"),
            "expected": "current stack remains blocked on R3",
        },
        {
            "id": "arrival_watch_no_candidate",
            "pass": arrival.get("candidateReviewNeededCount") == 0
            and arrival.get("decision") == "no_new_post_unlock_source_or_clue_candidate",
            "value": arrival.get("decision"),
            "expected": "no new post-unlock candidate",
        },
        {
            "id": "packet_does_not_unlock_selector",
            "pass": packet.get("decision") == "source_acquisition_packet_created_no_current_selector_unlocked",
            "value": packet.get("decision"),
            "expected": "no current selector unlocked",
        },
    ]

    build_visual_sheet(checks, packet_panels)
    failed = [row for row in checks if not row["pass"]]
    status = "PASS" if not failed else "REVIEW"

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-acquisition packet integrity; no extraction, no key derivation, no hashing, no address checks",
        "status": status,
        "criticalFiles": critical_files,
        "missingCriticalFiles": missing_critical,
        "packetPanelCount": len(packet_panels),
        "missingPacketPanels": missing_packet_panels,
        "captureJobCount": len(capture_jobs),
        "rGateCoverage": r_gate_coverage,
        "benchmarkCoverage": benchmark_ids,
        "targetPriorityKeys": sorted(target_priority.keys()),
        "futureConstraintIds": future_constraint_ids,
        "checks": checks,
        "failedChecks": failed,
        "sheet": rel(SHEET),
        "decision": "source_acquisition_packet_integrity_pass_no_selector_unlocked"
        if status == "PASS"
        else "review_source_acquisition_packet_before_use",
        "nextMove": "Use the packet as the first-stop gate for new physical/original-layout/raw clue evidence. Do not resume extraction from the current scan unless a new item passes R1-R5, especially R3 unit/order evidence.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Acquisition Packet Integrity",
        "",
        "Scope: verify the source-acquisition handoff packet and its visual/R1-R5 references. No extraction, key derivation, hashing, WIF/Base58 scanning, mnemonic generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Status: `{status}`",
        f"- Missing critical files: `{len(missing_critical)}`",
        f"- Missing packet panel files: `{len(missing_packet_panels)}`",
        f"- Capture jobs: `{len(capture_jobs)}`",
        f"- R-gate coverage: `{', '.join(r_gate_coverage)}`",
        f"- Benchmark coverage: `{', '.join(benchmark_ids)}`",
        f"- Sheet: `{rel(SHEET)}`",
        "",
        "## Checks",
        "",
        "| check | pass | value | expected |",
        "|---|---:|---|---|",
    ]
    for row in checks:
        lines.append(f"| `{row['id']}` | `{row['pass']}` | `{row['value']}` | `{row['expected']}` |")

    lines.extend(["", "## Critical Files", "", "| artifact | exists | size | path |", "|---|---:|---:|---|"])
    for row in critical_files:
        lines.append(f"| `{row['label']}` | `{row['exists']}` | `{row['size']}` | `{row['path']}` |")

    lines.extend(["", "## Capture Jobs", "", "| id | priority | kind | gates |", "|---|---:|---|---|"])
    for job in capture_jobs:
        lines.append(
            f"| `{job.get('id')}` | `{job.get('priority')}` | {job.get('kind')} | `{', '.join(job.get('rGates', []))}` |"
        )

    if missing_packet_panels:
        lines.extend(["", "## Missing Packet Panels", ""])
        for panel in missing_packet_panels:
            lines.append(f"- `{panel.get('title')}`: `{panel.get('path')}`")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("status:", status)
    print("failed:", len(failed), "missingCritical:", len(missing_critical), "missingPanels:", len(missing_packet_panels))


if __name__ == "__main__":
    main()

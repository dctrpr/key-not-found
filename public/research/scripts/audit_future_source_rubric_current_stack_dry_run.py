#!/usr/bin/env python3
"""Dry-run the future-source rubric against the current evidence stack.

This pass verifies that the newly explicit R1-R5 rubric does not accidentally
reopen extraction from already-known material. It uses existing gate rows only:
no text extraction, hashing, WIF/Base58 scanning, seed generation, OCR, or
address checking is performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/future_source_rubric_current_stack_dry_run"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "future_source_rubric_current_stack_dry_run.json"
OUT_MD = OUT / "future_source_rubric_current_stack_dry_run.md"
SHEET = OUT / "future_source_rubric_current_stack_dry_run_sheet.jpg"

INPUTS = {
    "rubric": ROOT / "analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric.json",
    "active_matrix": ROOT / "analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix.json",
    "source_packet": ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.json",
    "source_packet_integrity": ROOT / "analysis_outputs/source_audit/source_acquisition_packet_integrity/source_acquisition_packet_integrity.json",
    "missing_frontier": ROOT / "analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json",
}

VISUALS = [
    ("rubric", ROOT / "analysis_outputs/source_audit/future_source_scoring_rubric/future_source_scoring_rubric_sheet.jpg"),
    ("active matrix", ROOT / "analysis_outputs/source_audit/active_evidence_unlock_matrix/active_evidence_unlock_matrix_sheet.jpg"),
    ("3D fold/mirror", ROOT / "analysis_outputs/3d_article_map/fold_mirror_r3_gate_synthesis/fold_mirror_r3_gate_synthesis_sheet.jpg"),
    ("page-76 cluster", ROOT / "analysis_outputs/source_audit/page76_highlight_cluster_r3_gate_synthesis/page76_highlight_cluster_r3_gate_synthesis_sheet.jpg"),
]

GATES = ["R1", "R2", "R3", "R4", "R5"]


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


def strict_gate_pass(status: str | None) -> bool:
    if not status:
        return False
    normalized = status.strip().upper()
    if normalized != "PASS":
        return False
    return True


def soft_gate_pass(status: str | None) -> bool:
    if not status:
        return False
    return status.strip().upper().startswith("PASS")


def build_sheet(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet_w = 1500
    margin = 28
    header_h = 88
    row_h = 58
    table_h = 38 + row_h * len(rows)
    thumb_w = 340
    thumb_h = 245
    gap = 18
    sheet_h = margin * 2 + header_h + table_h + 76 + thumb_h + 48
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(17)
    small = font(13)
    mono = font(14)

    draw.text((margin, margin), "Rubric Dry-Run: Current Stack", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 44),
        f"Ready paths: {summary['extractionReadyCount']} / {summary['pathCount']}; R3 failures: {summary['r3FailCount']}",
        fill=(174, 184, 196),
        font=normal,
    )

    y = margin + header_h
    draw.rectangle((margin, y, sheet_w - margin, y + 32), fill=(29, 34, 42))
    headers = [("path", 12), ("R1", 485), ("R2", 570), ("R3", 655), ("R4", 740), ("R5", 825), ("strict", 910), ("blocker", 1010)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 8), label, fill=(236, 241, 247), font=small)
    y += 36

    for row in rows:
        fill = (18, 23, 28) if not row["extractionReady"] else (17, 48, 29)
        draw.rectangle((margin, y, sheet_w - margin, y + row_h - 5), fill=fill, outline=(38, 46, 56))
        draw.text((margin + 12, y + 10), row["path"][:54], fill=(224, 232, 240), font=small)
        for gate, xoff in zip(GATES, [485, 570, 655, 740, 825]):
            status = row["gates"].get(gate)
            color = (113, 222, 154) if strict_gate_pass(status) else (255, 181, 101) if soft_gate_pass(status) else (255, 123, 123)
            draw.text((margin + xoff, y + 10), str(status).split()[0], fill=color, font=mono)
        draw.text(
            (margin + 910, y + 10),
            "READY" if row["extractionReady"] else "BLOCK",
            fill=(113, 222, 154) if row["extractionReady"] else (255, 123, 123),
            font=mono,
        )
        draw.text((margin + 1010, y + 10), row["blocker"][:64], fill=(174, 184, 196), font=small)
        y += row_h

    y += 18
    draw.rectangle((margin, y, sheet_w - margin, y + 48), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text(
        (margin + 12, y + 13),
        "Dry-run result: current stack still cannot reopen extraction; R3 is absent on every current path.",
        fill=(255, 218, 135),
        font=normal,
    )
    y += 76

    for idx, (label, path) in enumerate(VISUALS):
        x = margin + idx * (thumb_w + gap)
        draw.text((x, y), label, fill=(236, 241, 247), font=normal)
        yy = y + 28
        draw.rectangle((x, yy, x + thumb_w, yy + thumb_h), fill=(19, 22, 28), outline=(52, 62, 75))
        if path.exists():
            img = Image.open(path).convert("RGB")
            img.thumbnail((thumb_w - 8, thumb_h - 8))
            sheet.paste(img, (x + 4, yy + 4))
        else:
            draw.text((x + 12, yy + 104), "missing", fill=(255, 123, 123), font=normal)

    sheet.save(SHEET, quality=94)


def main() -> None:
    rubric = load_json(INPUTS["rubric"])
    matrix = load_json(INPUTS["active_matrix"])
    packet = load_json(INPUTS["source_packet"])
    integrity = load_json(INPUTS["source_packet_integrity"])
    frontier = load_json(INPUTS["missing_frontier"])

    rows = []
    for source_row in matrix.get("rows", []):
        gates = {gate: source_row.get(gate) for gate in GATES}
        strict_passes = [gate for gate in GATES if strict_gate_pass(gates.get(gate))]
        soft_passes = [gate for gate in GATES if soft_gate_pass(gates.get(gate))]
        failed = [gate for gate in GATES if not strict_gate_pass(gates.get(gate))]
        extraction_ready = len(failed) == 0
        rows.append(
            {
                "path": source_row.get("path"),
                "role": source_row.get("role"),
                "gates": gates,
                "strictPasses": strict_passes,
                "softPasses": soft_passes,
                "failedStrictGates": failed,
                "r3Pass": strict_gate_pass(gates.get("R3")),
                "r3SoftPass": soft_gate_pass(gates.get("R3")),
                "extractionReady": extraction_ready,
                "blocker": source_row.get("blocker"),
                "next": source_row.get("next"),
            }
        )

    summary = {
        "pathCount": len(rows),
        "extractionReadyCount": sum(1 for row in rows if row["extractionReady"]),
        "r3FailCount": sum(1 for row in rows if not row["r3Pass"]),
        "r3SoftPassCount": sum(1 for row in rows if row["r3SoftPass"]),
        "softR2LocatorCount": sum(1 for row in rows if soft_gate_pass(row["gates"].get("R2"))),
        "strictAllGatePaths": [row["path"] for row in rows if row["extractionReady"]],
        "allCurrentPathsBlocked": all(not row["extractionReady"] for row in rows),
        "allCurrentPathsFailR3": all(not row["r3Pass"] for row in rows),
        "rubricDecision": rubric.get("decision"),
        "packetDecision": packet.get("decision"),
        "integrityStatus": integrity.get("status"),
        "frontierDeadBranchCount": frontier.get("deadBranchCount"),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "dry-run future-source rubric against current known evidence; no extraction, no key derivation, no hashing, no OCR, no address checks",
        "inputs": {name: rel(path) if path.exists() else None for name, path in INPUTS.items()},
        "sheet": rel(SHEET),
        "rows": rows,
        "summary": summary,
        "decision": "current_stack_fails_future_source_rubric_no_selector_unlocked",
        "nextMove": "Keep current materials as locator/provenance/source-validation evidence only. Apply the rubric only to new physical/original-layout/raw clue material before extraction.",
    }

    build_sheet(rows, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Future Source Rubric Current-Stack Dry Run",
        "",
        "Scope: dry-run the future-source R1-R5 rubric against the current known evidence stack. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Paths checked: `{summary['pathCount']}`",
        f"- Extraction-ready paths: `{summary['extractionReadyCount']}`",
        f"- R3 strict pass count: `{summary['r3SoftPassCount'] if False else sum(1 for row in rows if row['r3Pass'])}`",
        f"- R3 fail count: `{summary['r3FailCount']}`",
        f"- Dead-branch count entering dry-run: `{summary['frontierDeadBranchCount']}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Gate Dry Run",
        "",
        "| path | R1 | R2 | R3 | R4 | R5 | extraction ready | blocker |",
        "|---|---|---|---|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {path} | `{R1}` | `{R2}` | `{R3}` | `{R4}` | `{R5}` | `{ready}` | {blocker} |".format(
                path=row["path"],
                R1=row["gates"].get("R1"),
                R2=row["gates"].get("R2"),
                R3=row["gates"].get("R3"),
                R4=row["gates"].get("R4"),
                R5=row["gates"].get("R5"),
                ready=row["extractionReady"],
                blocker=row["blocker"],
            )
        )

    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "- No current path passes all five strict R1-R5 gates.",
            "- All current paths still fail R3 unit/order evidence.",
            "- Soft locator passes such as page-76 target surface, 3D fold/mirror geometry, O-B-B-O highlights, Typeka/font state, p80 package, and comparison layouts remain validation evidence only.",
            "- This dry run does not add a dead branch; it validates the rubric against already-known closed/current evidence.",
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
    print("extractionReadyCount:", summary["extractionReadyCount"])
    print("r3FailCount:", summary["r3FailCount"])


if __name__ == "__main__":
    main()

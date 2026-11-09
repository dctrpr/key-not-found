#!/usr/bin/env python3
"""Build an active evidence unlock matrix for the Max Keiser puzzle.

This is a bounded synthesis pass. It does not extract text streams, derive keys,
or run address checks. It asks whether the current evidence stack is sufficient
to resume extraction, and if not, which exact dependency remains blocking.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/active_evidence_unlock_matrix"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_evidence_unlock_matrix.json"
OUT_MD = OUT / "active_evidence_unlock_matrix.md"
SHEET = OUT / "active_evidence_unlock_matrix_sheet.jpg"

REPORTS = {
    "missing_rule_frontier": ROOT / "analysis_outputs/source_audit/missing_rule_frontier/missing_rule_frontier.json",
    "target_convergence": ROOT / "analysis_outputs/source_audit/page76_target_convergence/page76_target_convergence.json",
    "source_reopen_requirements": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
    "future_source_validation_packet": ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_packet.json",
    "source_reopen_candidate_intake": ROOT / "analysis_outputs/source_audit/source_reopen_candidate_intake/source_reopen_candidate_intake.json",
    "external_clue_unit_order_intake": ROOT / "analysis_outputs/external_clues/external_clue_unit_order_intake/external_clue_unit_order_intake.json",
    "physical_model_o5_g5_validation": ROOT / "analysis_outputs/source_audit/physical_model_o5_g5_validation/physical_model_o5_g5_validation.json",
    "p80_package_gate": ROOT / "analysis_outputs/source_audit/p80_package_r3_gate_synthesis/p80_package_r3_gate_synthesis.json",
    "typeka_font_gate": ROOT / "analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis.json",
    "fold_mirror_gate": ROOT / "analysis_outputs/3d_article_map/fold_mirror_r3_gate_synthesis/fold_mirror_r3_gate_synthesis.json",
    "highlight_cluster_gate": ROOT / "analysis_outputs/source_audit/page76_highlight_cluster_r3_gate_synthesis/page76_highlight_cluster_r3_gate_synthesis.json",
    "comparison_layout_gate": ROOT / "analysis_outputs/comparison_articles/overdose_layout_r3_gate_synthesis/overdose_layout_r3_gate_synthesis.json",
}

SHEET_IMAGES = [
    (
        ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements_sheet.jpg",
        "source reopen gate",
    ),
    (
        ROOT / "analysis_outputs/source_audit/future_source_validation_packet/future_source_validation_review_sheet.jpg",
        "future source packet",
    ),
    (
        ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg",
        "page-76 priority targets",
    ),
    (
        ROOT / "analysis_outputs/3d_article_map/fold_mirror_r3_gate_synthesis/fold_mirror_r3_gate_synthesis_sheet.jpg",
        "3D fold/mirror locator",
    ),
]


def load(path: Path) -> dict:
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


def status_color(status: str) -> tuple[int, int, int]:
    s = status.lower()
    if "pass" in s:
        return (83, 188, 121)
    if "partial" in s or "locator" in s or "provenance" in s:
        return (216, 170, 69)
    if "fail" in s or "block" in s or "closed" in s:
        return (215, 92, 92)
    return (155, 166, 178)


def build_visual_sheet(rows: list[dict]) -> list[dict]:
    width = 1500
    margin = 36
    row_h = 86
    header_h = 130
    img_h = header_h + len(rows) * row_h + 420
    sheet = Image.new("RGB", (width, img_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    head_font = font(19)
    body_font = font(16)
    small_font = font(14)

    draw.text((margin, 28), "Active Evidence Unlock Matrix", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, 72),
        "Current stack confirms the target surface but does not satisfy R3 unit/order evidence.",
        fill=(172, 184, 196),
        font=head_font,
    )
    cols = [
        ("path", 36, 300),
        ("R1", 350, 85),
        ("R2", 450, 85),
        ("R3", 550, 85),
        ("R4", 650, 85),
        ("R5", 750, 85),
        ("blocker", 855, 600),
    ]
    y = header_h
    for label, x, _ in cols:
        draw.text((x, y - 30), label, fill=(220, 226, 232), font=head_font)

    for row in rows:
        draw.rectangle((margin, y - 8, width - margin, y + row_h - 14), fill=(17, 20, 25))
        draw.text((cols[0][1], y + 6), row["path"], fill=(235, 238, 242), font=body_font)
        draw.text((cols[0][1], y + 32), row["role"], fill=(145, 158, 171), font=small_font)
        for key, x, _ in cols[1:6]:
            value = row.get(key, "n/a")
            color = status_color(value)
            draw.rounded_rectangle((x, y + 7, x + 78, y + 36), radius=5, fill=(28, 32, 38), outline=color, width=2)
            draw.text((x + 7, y + 13), value[:8], fill=color, font=small_font)
        draw.text((cols[6][1], y + 6), row["blocker"][:86], fill=(218, 224, 230), font=body_font)
        draw.text((cols[6][1], y + 32), row["next"][:92], fill=(145, 158, 171), font=small_font)
        y += row_h

    panels = []
    panel_y = y + 24
    panel_w = 340
    panel_h = 260
    for idx, (path, title) in enumerate(SHEET_IMAGES):
        if not path.exists():
            continue
        source = Image.open(path).convert("RGB")
        source.thumbnail((panel_w, 210))
        x = margin + (idx % 4) * (panel_w + 22)
        panel = Image.new("RGB", (panel_w, panel_h), (16, 18, 22))
        pdraw = ImageDraw.Draw(panel)
        pdraw.text((0, 0), title, fill=(238, 242, 246), font=head_font)
        panel.paste(source, (0, 42))
        sheet.paste(panel, (x, panel_y))
        panels.append({"title": title, "path": rel(path)})

    sheet.crop((0, 0, width, min(img_h, panel_y + panel_h + margin))).save(SHEET, quality=94)
    return panels


def gate_status_map(gate_rows: list[dict]) -> dict[str, str]:
    out = {}
    for row in gate_rows:
        gate = str(row.get("gate", "")).split(" ")[0]
        if gate in {"R1", "R2", "R3", "R4", "R5"}:
            out[gate] = row.get("status", "n/a")
    return out


def main() -> None:
    data = {name: load(path) for name, path in REPORTS.items()}
    target = data["target_convergence"]
    future = data["future_source_validation_packet"]
    source_intake = data["source_reopen_candidate_intake"]
    external = data["external_clue_unit_order_intake"]

    top_targets = [
        {
            "target": row.get("target"),
            "label": row.get("label"),
            "score": row.get("score"),
            "layers": row.get("independentLayerCount"),
        }
        for row in target.get("ranking", [])[:3]
    ]

    gate_sources = [
        (
            "current local sources",
            "source/physical",
            {
                "R1": "FAIL",
                "R2": "PARTIAL",
                "R3": "FAIL",
                "R4": "PARTIAL",
                "R5": "FAIL",
                "blocker": "No local candidate passes R1-R5; source-delta actionable unknowns are 0.",
                "next": "Only score materially new physical/original-layout/source evidence.",
            },
        ),
        (
            "archived/raw clues",
            "provenance wording",
            {
                "R1": "PARTIAL",
                "R2": "PARTIAL",
                "R3": "FAIL",
                "R4": "PASS",
                "R5": "FAIL",
                "blocker": "Raw-like R3 passes are 0; no source-backed unit/order phrase is present.",
                "next": "Search only for raw wording that names word/letter/line/edge/font/order.",
            },
        ),
        (
            "page-76 target surface",
            "locator",
            {
                "R1": "FAIL",
                "R2": "PASS",
                "R3": "FAIL",
                "R4": "PASS",
                "R5": "PARTIAL",
                "blocker": "O5/G5 are strong targets, not extraction permission.",
                "next": "Use O5/G5 as validation targets for any new source/clue.",
            },
        ),
    ]

    for key, name, role in [
        ("fold_mirror_gate", "3D fold/mirror geometry", "locator/orientation"),
        ("highlight_cluster_gate", "page-76 O-B-B-O highlights", "target cluster"),
        ("typeka_font_gate", "Typeka/font state", "format witness"),
        ("p80_package_gate", "p80 package/OVERDOSE", "theme/count witness"),
        ("comparison_layout_gate", "comparison OVERDOSE layouts", "style/provenance"),
    ]:
        gate = gate_status_map(data[key].get("gateRows", []))
        gate_sources.append(
            (
                name,
                role,
                {
                    "R1": gate.get("R1", "n/a"),
                    "R2": gate.get("R2", "n/a"),
                    "R3": gate.get("R3", "FAIL"),
                    "R4": gate.get("R4", "n/a"),
                    "R5": gate.get("R5", "FAIL"),
                    "blocker": f"{data[key].get('decision', key)}; no unit/order unlock.",
                    "next": data[key].get("nextMove", "Reopen only with new source/clue evidence."),
                },
            )
        )

    rows = [
        {
            "path": name,
            "role": role,
            "R1": values["R1"],
            "R2": values["R2"],
            "R3": values["R3"],
            "R4": values["R4"],
            "R5": values["R5"],
            "blocker": values["blocker"],
            "next": values["next"],
        }
        for name, role, values in gate_sources
    ]
    panels = build_visual_sheet(rows)

    r3_fail_count = sum(1 for row in rows if "fail" in row["R3"].lower())
    r5_fail_count = sum(1 for row in rows if "fail" in row["R5"].lower())
    all_r3_blocked = r3_fail_count == len(rows)
    minimum_conditions = [
        item.get("condition")
        for item in future.get("minimumReopenConditions", [])
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active evidence unlock matrix; no extraction/key derivation",
        "inputs": {name: rel(path) if path.exists() else None for name, path in REPORTS.items()},
        "sheet": rel(SHEET) if SHEET.exists() else None,
        "sheetPanels": panels,
        "topTargets": top_targets,
        "rows": rows,
        "summary": {
            "pathsChecked": len(rows),
            "r3FailCount": r3_fail_count,
            "r5FailCount": r5_fail_count,
            "allPathsBlockedOnR3": all_r3_blocked,
            "deadBranchCountBeforeThisPass": data["missing_rule_frontier"].get("deadBranchCount"),
            "sourceIntakeDecision": source_intake.get("decision"),
            "sourceDeltaActionableUnknownCount": source_intake.get("sourceDeltaActionableUnknownCount"),
            "externalRawLikeR3PassCount": external.get("rawLikeR3PassCount"),
            "externalDerivedR3PassCount": external.get("derivedR3PassCount"),
            "minimumReopenConditions": minimum_conditions,
        },
        "decision": "current_evidence_stack_not_sufficient_to_resume_extraction",
        "nextMove": "Do not run selector/key checks from the current stack. The next useful move is to obtain or inspect physical/original-layout/source material, or raw clue wording, and score it against R1-R5 before any extraction attempt.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active Evidence Unlock Matrix",
        "",
        "Scope: roll up the active evidence stack against the source-reopen gate. No extraction, hashing, seed, WIF, address, or candidate checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Paths checked: `{len(rows)}`",
        f"- R3 fail count: `{r3_fail_count}`",
        f"- R5 fail count: `{r5_fail_count}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Top Targets",
        "",
    ]
    for item in top_targets:
        lines.append(f"- `{item['target']}` `{item['label']}`: score `{item['score']}`, layers `{item['layers']}`")

    lines.extend(["", "## Gate Matrix", "", "| path | role | R1 | R2 | R3 | R4 | R5 | blocker |", "|---|---|---|---|---|---|---|---|"])
    for row in rows:
        lines.append(
            f"| {row['path']} | {row['role']} | `{row['R1']}` | `{row['R2']}` | `{row['R3']}` | `{row['R4']}` | `{row['R5']}` | {row['blocker']} |"
        )

    lines.extend(
        [
            "",
            "## What This Rules Out",
            "",
            "- The current aggregate evidence stack is not enough to resume extraction or key checking.",
            "- A path that only confirms page 76, O5/G5, OVERDOSE styling, Typeka states, or fold/mirror orientation still fails unless it also supplies R3 unit/order evidence.",
            "- The source-reopen packet remains the gate: C3 extraction unit, C4 physical registration, C8 source-image quality, and C2 p78-frame signature are the minimum useful unlocks.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    if SHEET.exists():
        print(f"wrote {SHEET}")
    print("decision:", result["decision"])
    print("r3FailCount:", r3_fail_count)


if __name__ == "__main__":
    main()

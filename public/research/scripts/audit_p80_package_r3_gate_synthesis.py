#!/usr/bin/env python3
"""Synthesize p80 package/OVERDOSE evidence against the R1-R5 gate.

This consolidates existing page-80 package-copy, symptom, dosage, and geometry
reports into one current-scan decision. It does not rerun broad selectors or
generate key material; it asks whether p80 supplies R3 unit/order evidence or
changes source/geometry status under the current scan.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/p80_package_r3_gate_synthesis"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p80_package_r3_gate_synthesis.json"
OUT_MD = OUT / "p80_package_r3_gate_synthesis.md"
SHEET = OUT / "p80_package_r3_gate_synthesis_sheet.jpg"

REPORTS = {
    "package_copy": ROOT / "analysis_outputs/3d_article_map/p80_package_copy_audit.json",
    "five_symptom": ROOT / "analysis_outputs/3d_article_map/five_symptom_mapping.json",
    "symptom_relief": ROOT / "analysis_outputs/source_audit/p80_symptom_relief_rule/p80_symptom_relief_rule.json",
    "symptom_to_p76": ROOT / "analysis_outputs/source_audit/p80_symptom_to_p76_units/p80_symptom_to_p76_units.json",
    "p79_p80_interaction": ROOT / "analysis_outputs/source_audit/p79_p80_package_interaction/p79_p80_package_interaction.json",
    "p80_anchor_geometry": ROOT / "analysis_outputs/source_audit/p80_to_p76_anchor_geometry/p80_to_p76_anchor_geometry.json",
    "p80_four_anchor_choice": ROOT / "analysis_outputs/source_audit/p80_four_anchor_choice/p80_four_anchor_choice.json",
    "dose_number": ROOT / "analysis_outputs/source_audit/overdose_dose_number_selector/overdose_dose_number_selector.json",
    "source_reopen": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
}

SHEET_IMAGES = [
    (ROOT / "analysis_outputs/3d_article_map/page_80_upright.jpg", "p80 package page", "current scan / readable upright"),
    (
        ROOT / "analysis_outputs/source_audit/p80_to_p76_anchor_geometry/p80_to_p76_anchor_geometry_sheet.jpg",
        "p80 -> p76 anchor geometry",
        "no direct anchor overlaps under simple transforms",
    ),
    (
        ROOT / "analysis_outputs/source_audit/p79_p80_package_interaction/p79_p80_package_interaction_sheet.jpg",
        "p79/p80 interaction",
        "raw hflip touches broad p79 sentence fragments only",
    ),
    (
        ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements_sheet.jpg",
        "source reopen gate",
        "R1-R5 remains active before extraction",
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


def build_sheet() -> list[dict]:
    panels = []
    panel_w = 620
    label_h = 70
    for path, title, subtitle in SHEET_IMAGES:
        if not path.exists():
            continue
        img = Image.open(path).convert("RGB")
        img.thumbnail((panel_w, 360))
        panel = Image.new("RGB", (panel_w, label_h + img.height), (16, 18, 22))
        draw = ImageDraw.Draw(panel)
        draw.text((0, 0), title, fill=(240, 244, 248), font=font(23))
        draw.text((0, 32), subtitle, fill=(168, 181, 194), font=font(15))
        panel.paste(img, (0, label_h))
        panels.append({"title": title, "path": rel(path), "image": panel})

    if not panels:
        return []

    cols = 2
    margin = 24
    gap = 20
    rows = (len(panels) + cols - 1) // cols
    row_heights = []
    for r in range(rows):
        row_heights.append(max(p["image"].height for p in panels[r * cols : (r + 1) * cols]))
    sheet_w = margin * 2 + panel_w * cols + gap
    sheet_h = margin * 2 + 58 + sum(row_heights) + gap * (rows - 1)
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 15))
    draw = ImageDraw.Draw(sheet)
    draw.text((margin, margin), "P80 Package Gate Synthesis", fill=(244, 247, 250), font=font(31))
    draw.text((margin, margin + 36), "Current-scan p80 evidence remains count/theme, not extraction permission.", fill=(172, 184, 196), font=font(16))
    y = margin + 58
    for r in range(rows):
        x = margin
        for panel in panels[r * cols : (r + 1) * cols]:
            sheet.paste(panel["image"], (x, y))
            x += panel_w + gap
        y += row_heights[r] + gap
    sheet.save(SHEET, quality=94)
    return [{"title": p["title"], "path": p["path"]} for p in panels]


def main() -> None:
    data = {name: load(path) for name, path in REPORTS.items()}
    panels = build_sheet()

    package = data["package_copy"]
    relief = data["symptom_relief"]
    anchor_geom = data["p80_anchor_geometry"]
    four_anchor = data["p80_four_anchor_choice"]
    dose = data["dose_number"]

    manual = package.get("manualTranscription", [])
    package_terms = relief.get("packageTermAudit", {})
    explicit_terms = package_terms.get("explicitExtractionTerms", [])
    positive_overlap = anchor_geom.get("positiveOverlapRows", [])
    selections = dose.get("selections", [])
    selected_target_hits = [
        row for row in selections
        if isinstance(row, dict) and row.get("targetLabel")
    ]

    gate_rows = [
        {
            "gate": "R1 source identity",
            "status": "FAIL/PARTIAL",
            "evidence": "p80 is from the same locked current scan, not new physical/original-layout source evidence.",
        },
        {
            "gate": "R2 target preservation",
            "status": "PASS as corroboration",
            "evidence": "p80 reinforces OVERDOSE, five-count, symptoms, and O5/shitcoiner theming.",
        },
        {
            "gate": "R3 unit/order evidence",
            "status": "FAIL",
            "evidence": f"explicit extraction terms on package: {explicit_terms or 'none'}; relief/number/symptom streams have no instruction hits.",
        },
        {
            "gate": "R4 orientation discipline",
            "status": "PASS as audited",
            "evidence": "existing p80 audits use current readable/upright scan and simple hflip/identity/vflip/rotate180 transforms.",
        },
        {
            "gate": "R5 controlled improvement",
            "status": "FAIL",
            "evidence": f"p80->p76 anchor geometry has {len(positive_overlap)} positive overlap rows; no p78/G5/O5 benchmark improvement.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p80 package/OVERDOSE synthesis against source-reopen gate; no extraction/key derivation",
        "inputs": {name: rel(path) if path.exists() else None for name, path in REPORTS.items()},
        "sheet": rel(SHEET) if SHEET.exists() else None,
        "sheetPanels": panels,
        "manualPackageLineCount": len(manual),
        "packageNumbers": package.get("streams", {}).get("numbers_csv"),
        "explicitExtractionTerms": explicit_terms,
        "possibleActionTerms": package_terms.get("possibleActionTerms", []),
        "fiveSymptomAssessment": data["five_symptom"].get("assessment", []),
        "symptomToP76Assessment": data["symptom_to_p76"].get("assessment", []),
        "p80FourAnchorDecision": four_anchor.get("decision"),
        "p80ToP76Decision": anchor_geom.get("decision"),
        "p79P80Assessment": data["p79_p80_interaction"].get("assessment", []),
        "doseNumberAssessment": dose.get("assessment", []),
        "gateRows": gate_rows,
        "decision": "p80_package_layer_closed_for_current_scan_as_r3_selector",
        "nextMove": "Keep p80 as C6 five-count/theme/source-validation evidence only. Reopen only if new physical/original-layout evidence places package copy onto p76 targets or a raw clue explicitly says to use relief/symptoms/dose/package text as a selector.",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P80 Package R3 Gate Synthesis",
        "",
        "Scope: consolidate existing p80 package-copy, five-symptom, dosage, and geometry reports against the R1-R5 source-reopen gate. No extraction, hashing, seed, WIF, address, or candidate checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Manual package lines: `{result['manualPackageLineCount']}`",
        f"- Package numbers: `{result['packageNumbers']}`",
        f"- Explicit extraction terms: `{explicit_terms or 'none'}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Gate Result",
        "",
        "| gate | status | evidence |",
        "|---|---|---|",
    ]
    for row in gate_rows:
        lines.append(f"| {row['gate']} | `{row['status']}` | {row['evidence']} |")

    lines.extend(
        [
            "",
            "## Consolidated Findings",
            "",
            "- `5 SYMPTOM RELIEF` and the five listed symptoms are real count/theme evidence and support the five-unit model.",
            "- Direct symptom mapping mostly collapses to O5 through `HEARTBURN`/`heart` and `SHITCOINS`/`shitcoiner`; it does not order all active page-76 anchors.",
            "- `relief`, `reliever`, `fixes`, `proof`, `work`, `anti`, and `fake` are action/theme words, but not extraction unit terms.",
            "- P80 package labels do not overlap the four page-76 anchors under identity, hflip, vflip, or 180-degree rotation.",
            "- P79/P80 raw hflip interaction touches broad p79 sentence fragments, not a narrow text unit or instruction.",
            "- Visible numbers `5/6/16/80/100/473` corroborate the target corridor or package theme only; they do not produce a readable selector stream.",
            "",
            "## Decision",
            "",
            "- Close p80 package copy as an R3 selector under the current scan.",
            "- Keep p80 as C6 locator/theme evidence and as a future-source validation surface.",
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


if __name__ == "__main__":
    main()

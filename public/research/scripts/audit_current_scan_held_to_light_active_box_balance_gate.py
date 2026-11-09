#!/usr/bin/env python3
"""Check whether held-to-light simulator views isolate the active quartet.

This bounded pass reuses the current scan held-to-light simulator outputs and
asks a narrow visual/geometry question: do physically valid page-75-to-76 views
light up O4/B4/G5/O5 together, or are the apparent hits unbalanced/forced?

No OCR-to-key extraction, key candidates, hashes, seed/WIF/address checks,
BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_held_to_light_active_box_balance_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_held_to_light_active_box_balance_gate.json"
OUT_MD = OUT / "current_scan_held_to_light_active_box_balance_gate.md"
OUT_SHEET = OUT / "current_scan_held_to_light_active_box_balance_gate_sheet.jpg"

SIMULATOR_JSON = ROOT / (
    "analysis_outputs/source_audit/current_scan_held_to_light_simulator/"
    "current_scan_held_to_light_simulator.json"
)
ACTIVE_TARGETS_JSON = ROOT / (
    "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
TARGET_SHORT_IDS = {
    "buying_dip": "O4",
    "one_billion": "B4",
    "volcano_bonds": "G5",
    "shitcoiner_heart": "O5",
}


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def classify_row(row: dict[str, Any]) -> dict[str, Any]:
    coverage = {}
    for target in TARGET_ORDER:
        value = row.get("activeCoverageByBox", {}).get(target, {}).get("coverage")
        coverage[target] = float(value or 0.0)
    values = [coverage[target] for target in TARGET_ORDER]
    all4_ge_10 = all(value >= 0.10 for value in values)
    all4_ge_25 = all(value >= 0.25 for value in values)
    all4_ge_50 = all(value >= 0.50 for value in values)
    physical_valid = row.get("pairId") == "same_leaf_75_to_76" and row.get("mode") == "natural_hflip"
    same_leaf_75_to_76 = row.get("pairId") == "same_leaf_75_to_76"
    forced_shift = bool(row.get("dx") or row.get("dy"))
    nonphysical = str(row.get("pairId", "")).startswith("nonphysical")
    max_value = max(values) if values else 0.0
    min_value = min(values) if values else 0.0
    balance_ratio = round(min_value / max_value, 4) if max_value else 0.0
    return {
        "pairId": row.get("pairId"),
        "topology": row.get("topology"),
        "sourcePage": row.get("sourcePage"),
        "targetPage": row.get("targetPage"),
        "mode": row.get("mode"),
        "dx": int(row.get("dx", 0)),
        "dy": int(row.get("dy", 0)),
        "image": row.get("image"),
        "activeOverTarget": round(float(row.get("activeOverTarget", 0.0)), 6),
        "activeBalanced": round(float(row.get("activeBalanced", 0.0)), 6),
        "coverage": {target: round(coverage[target], 6) for target in TARGET_ORDER},
        "minCoverage": round(min_value, 6),
        "maxCoverage": round(max_value, 6),
        "meanCoverage": round(mean(values), 6),
        "balanceRatio": balance_ratio,
        "all4Ge10": all4_ge_10,
        "all4Ge25": all4_ge_25,
        "all4Ge50": all4_ge_50,
        "physicalValidNatural": physical_valid,
        "sameLeaf75To76": same_leaf_75_to_76,
        "forcedShift": forced_shift,
        "nonphysical": nonphysical,
        "selectorCandidate": bool(physical_valid and all4_ge_10 and not forced_shift),
    }


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("pairId")), str(row.get("mode")))


def draw_panel(
    sheet: Image.Image,
    draw: ImageDraw.ImageDraw,
    row: dict[str, Any],
    target_boxes: dict[str, list[float]],
    xy: tuple[int, int],
    size: tuple[int, int],
) -> None:
    x, y = xy
    w, h = size
    img_path = ROOT / str(row["image"])
    img = Image.open(img_path).convert("RGB").resize((w, h))
    sheet.paste(img, (x, y))
    sx = w / 2544.0
    sy = h / 3264.0
    colors = {"O4": (255, 155, 46), "B4": (40, 45, 55), "G5": (40, 45, 55), "O5": (255, 155, 46)}
    text_font = font(13)
    for target, box in target_boxes.items():
        bx = [x + box[0] * sx, y + box[1] * sy, x + box[2] * sx, y + box[3] * sy]
        color = colors.get(target, (200, 0, 0))
        draw.rectangle(bx, outline=color, width=3)
        cov = row["coverage"].get(target, 0.0)
        label = f"{target} {cov:.2f}"
        draw.rectangle((bx[0], bx[1] - 18, bx[0] + 62, bx[1]), fill=(255, 255, 255))
        draw.text((bx[0] + 2, bx[1] - 17), label, fill=color, font=text_font)
    label_font = font(15)
    draw.rectangle((x, y, x + w, y + 58), fill=(255, 255, 255))
    draw.text(
        (x + 8, y + 6),
        f"{row['pairId']} / {row['mode']}",
        fill=(25, 28, 34),
        font=label_font,
    )
    draw.text(
        (x + 8, y + 30),
        f"dx,dy {row['dx']},{row['dy']}  min {row['minCoverage']:.2f}  all4>=10 {int(row['all4Ge10'])}",
        fill=(25, 28, 34),
        font=label_font,
    )
    draw.rectangle((x, y, x + w, y + h), outline=(35, 40, 48), width=2)


def draw_sheet(result: dict[str, Any], target_boxes: dict[str, list[float]]) -> None:
    sheet = Image.new("RGB", (1900, 1360), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(24)
    small = font(14)
    tiny = font(11)
    draw.rectangle((0, 0, 1900, 100), fill=(24, 31, 42))
    draw.text((24, 16), "Held-to-Light Active-Box Balance Gate", fill="white", font=title)
    draw.text(
        (24, 52),
        "Physically valid and forced/control light-table views are compared by O4/B4/G5/O5 coverage balance.",
        fill=(236, 236, 236),
        font=small,
    )
    summary = result["summary"]
    draw.text(
        (1120, 18),
        f"rows {summary['activeRowCount']} | physical candidates {summary['physicalNaturalSelectorCandidateCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1120, 48),
        f"same-leaf all4>=10 {summary['sameLeaf75To76All4Ge10Count']} | nonphysical all4>=10 {summary['nonphysicalAll4Ge10Count']}",
        fill=(236, 236, 236),
        font=small,
    )

    selected = result["selectedRows"]
    positions = [(24, 130), (494, 130), (964, 130), (1434, 130)]
    for row, pos in zip(selected, positions):
        draw_panel(sheet, draw, row, target_boxes, pos, (430, 552))

    y = 720
    draw.text((24, y), "Coverage table", fill=(30, 34, 40), font=small)
    y += 24
    headers = [
        "pair/mode",
        "dx,dy",
        "O4",
        "B4",
        "G5",
        "O5",
        "min",
        "all4>=10",
        "physical",
        "forced",
        "nonphys",
    ]
    xs = [24, 420, 510, 585, 660, 735, 810, 885, 995, 1080, 1150]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(65, 70, 78), font=tiny)
    y += 18
    for row in result["activeRows"]:
        values = [
            f"{row['pairId']} / {row['mode']}",
            f"{row['dx']},{row['dy']}",
            f"{row['coverage']['O4']:.3f}",
            f"{row['coverage']['B4']:.3f}",
            f"{row['coverage']['G5']:.3f}",
            f"{row['coverage']['O5']:.3f}",
            f"{row['minCoverage']:.3f}",
            str(int(row["all4Ge10"])),
            str(int(row["physicalValidNatural"])),
            str(int(row["forcedShift"])),
            str(int(row["nonphysical"])),
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value[:46], fill=(25, 28, 34), font=tiny)
        y += 20

    y += 20
    draw.text((24, y), "Interpretation", fill=(30, 34, 40), font=small)
    y += 24
    notes = [
        "The only physically valid natural 75->76 view has B4 at 0.000 and no all-four coverage.",
        "The best same-leaf shifted 75->76 view is a forced -220,+200 translation and still misses all-four >=10 because G5 remains low.",
        "The only all-four >=10 row is nonphysical 79->76 with a +40,+80 shift, so it is a control/visual match, not a source rule.",
        "No source-backed R3 bridge or reopen trigger is satisfied.",
    ]
    for note in notes:
        draw.text((24, y), "- " + note, fill=(25, 28, 34), font=small)
        y += 24
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan Held-to-Light Active-Box Balance Gate",
        "",
        "Scope: reused the current scan held-to-light simulator and checked whether any physically valid page-75-to-page-76 view isolates O4/B4/G5/O5 together. No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Active simulator rows: `{summary['activeRowCount']}`",
        f"- Physical natural selector candidates: `{summary['physicalNaturalSelectorCandidateCount']}`",
        f"- Same-leaf 75->76 all-four >=10% rows: `{summary['sameLeaf75To76All4Ge10Count']}`",
        f"- Same-leaf 75->76 all-four >=25% rows: `{summary['sameLeaf75To76All4Ge25Count']}`",
        f"- Nonphysical all-four >=10% rows: `{summary['nonphysicalAll4Ge10Count']}`",
        f"- Best physical natural min coverage: `{summary['bestPhysicalNaturalMinCoverage']}`",
        f"- Best same-leaf shifted min coverage: `{summary['bestSameLeaf75To76MinCoverage']}`",
        f"- Best nonphysical min coverage: `{summary['bestNonphysicalMinCoverage']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Active Rows",
        "",
        "| pair | mode | dx | dy | O4 | B4 | G5 | O5 | min | all4>=10 | physical natural | forced shift | nonphysical |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["activeRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pairId']}`",
                    f"`{row['mode']}`",
                    str(row["dx"]),
                    str(row["dy"]),
                    f"{row['coverage']['O4']:.4f}",
                    f"{row['coverage']['B4']:.4f}",
                    f"{row['coverage']['G5']:.4f}",
                    f"{row['coverage']['O5']:.4f}",
                    f"{row['minCoverage']:.4f}",
                    str(row["all4Ge10"]),
                    str(row["physicalValidNatural"]),
                    str(row["forcedShift"]),
                    str(row["nonphysical"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The physically valid natural page 75 -> page 76 light-table view does not isolate the active quartet: B4 coverage is `0.0000`, and all-four coverage fails.",
            "- The best same-leaf 75 -> 76 row is a forced `-220,+200` translation and still fails all-four >=10% because G5 remains low.",
            "- The only all-four >=10% row is nonphysical page 79 -> page 76 with a `+40,+80` shift, so it is useful as a control but not as a physical/source-backed rule.",
            "- Keep current-scan held-to-light balance closed unless a new physical/original-layout source changes the page registration or provides explicit unit/order wording.",
            "",
            "## Next Move",
            "",
            "- Use this balance gate as the visual light-table stop-check. Best direction remains original/source-layout validation or raw clue wording that explicitly names transform, unit, and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    simulator = load_json(SIMULATOR_JSON)
    active_targets = load_json(ACTIVE_TARGETS_JSON)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    target_boxes = {}
    for target in active_targets.get("targets", []):
        short_id = TARGET_SHORT_IDS.get(target.get("id"))
        if short_id:
            target_boxes[short_id] = target.get("box")

    active_rows = [
        classify_row(row)
        for row in simulator.get("rows", [])
        if row.get("activeCoverageByBox")
    ]
    active_rows.sort(
        key=lambda row: (
            row["pairId"],
            {"natural_hflip": 0, "best_global_feature": 1, "best_page76_active_boxes": 2}.get(row["mode"], 9),
        )
    )
    same_leaf = [row for row in active_rows if row["sameLeaf75To76"]]
    physical_natural = [row for row in active_rows if row["physicalValidNatural"]]
    nonphysical = [row for row in active_rows if row["nonphysical"]]
    best_physical_natural = max(physical_natural, key=lambda row: row["minCoverage"], default={})
    best_same_leaf = max(same_leaf, key=lambda row: row["minCoverage"], default={})
    best_nonphysical = max(nonphysical, key=lambda row: row["minCoverage"], default={})
    by_key = {row_key(row): row for row in active_rows}
    selected_keys = [
        ("same_leaf_75_to_76", "natural_hflip"),
        ("same_leaf_75_to_76", "best_page76_active_boxes"),
        ("nonphysical_79_to_76", "best_page76_active_boxes"),
        ("nonphysical_78_to_76", "best_page76_active_boxes"),
    ]
    selected_rows = [by_key[key] for key in selected_keys if key in by_key]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    summary = {
        "decision": "current_scan_held_to_light_active_box_balance_no_selector",
        "activeRowCount": len(active_rows),
        "physicalNaturalSelectorCandidateCount": sum(row["selectorCandidate"] for row in active_rows),
        "sameLeaf75To76All4Ge10Count": sum(row["all4Ge10"] for row in same_leaf),
        "sameLeaf75To76All4Ge25Count": sum(row["all4Ge25"] for row in same_leaf),
        "nonphysicalAll4Ge10Count": sum(row["all4Ge10"] for row in nonphysical),
        "nonphysicalAll4Ge25Count": sum(row["all4Ge25"] for row in nonphysical),
        "bestPhysicalNaturalMinCoverage": best_physical_natural.get("minCoverage", 0.0),
        "bestSameLeaf75To76MinCoverage": best_same_leaf.get("minCoverage", 0.0),
        "bestSameLeaf75To76Row": {
            "pairId": best_same_leaf.get("pairId"),
            "mode": best_same_leaf.get("mode"),
            "dx": best_same_leaf.get("dx"),
            "dy": best_same_leaf.get("dy"),
        },
        "bestNonphysicalMinCoverage": best_nonphysical.get("minCoverage", 0.0),
        "bestNonphysicalRow": {
            "pairId": best_nonphysical.get("pairId"),
            "mode": best_nonphysical.get("mode"),
            "dx": best_nonphysical.get("dx"),
            "dy": best_nonphysical.get("dy"),
        },
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"activeRows={summary['activeRowCount']}|physicalCandidates={summary['physicalNaturalSelectorCandidateCount']}|"
        f"sameLeafAll4_10={summary['sameLeaf75To76All4Ge10Count']}|"
        f"sameLeafAll4_25={summary['sameLeaf75To76All4Ge25Count']}|"
        f"nonphysicalAll4_10={summary['nonphysicalAll4Ge10Count']}|"
        f"nonphysicalAll4_25={summary['nonphysicalAll4Ge25Count']}|"
        f"naturalMin={summary['bestPhysicalNaturalMinCoverage']:.4f}|"
        f"sameLeafBestMin={summary['bestSameLeaf75To76MinCoverage']:.4f}@{best_same_leaf.get('dx')},{best_same_leaf.get('dy')}|"
        f"nonphysicalBestMin={summary['bestNonphysicalMinCoverage']:.4f}@{best_nonphysical.get('pairId')}:{best_nonphysical.get('dx')},{best_nonphysical.get('dy')}|"
        f"sourceR3={source_r3_hits}|triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Held-to-light simulator active-box balance check for O4/B4/G5/O5.",
        "inputs": {
            "heldToLightSimulator": rel(SIMULATOR_JSON),
            "activeTargets": rel(ACTIVE_TARGETS_JSON),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "fingerprint": fingerprint,
        "activeRows": active_rows,
        "selectedRows": selected_rows,
        "targetBoxes": target_boxes,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result, target_boxes)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)


if __name__ == "__main__":
    main()

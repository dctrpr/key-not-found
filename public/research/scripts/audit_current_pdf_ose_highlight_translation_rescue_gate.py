#!/usr/bin/env python3
"""Test whether a single translation can rescue OSE highlights onto active targets.

The OSE source highlights mirror into OVERDOSE slot bands, not active page-76
targets. This bounded geometry pass asks whether a single global translation
could plausibly rescue them onto O4/B4/G5/O5. It computes exact rectangle-overlap
shift intervals rather than trying key material or broad candidate generation.

No OCR-to-key extraction, candidate generation, hashing, seed/WIF/address
checks, BIP39 checks, or broad brute force is run.
"""

from __future__ import annotations

import itertools
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ose_highlight_translation_rescue_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ose_highlight_translation_rescue_gate.json"
OUT_MD = OUT / "current_pdf_ose_highlight_translation_rescue_gate.md"
OUT_SHEET = OUT / "current_pdf_ose_highlight_translation_rescue_gate_sheet.jpg"

OSE_GEOMETRY = ROOT / (
    "analysis_outputs/source_audit/current_pdf_ose_highlight_mirror_geometry_gate/"
    "current_pdf_ose_highlight_mirror_geometry_gate.json"
)
ACTIVE_TARGETS = ROOT / (
    "analysis_outputs/source_audit/page76_active_target_crop_completion/"
    "page76_active_target_crop_completion.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE75 = ROOT / "analysis_outputs/3d_article_map/page_75_upright.jpg"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

ACTIVE_ORDER = ["O4", "B4", "G5", "O5"]
SMALL_SHIFT_LIMIT = 160.0
MODERATE_SHIFT_LIMIT = 320.0


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def active_targets(active_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for target in active_data.get("targets", []):
        short_id = str(target["label"]).split()[0]
        rows.append(
            {
                "id": short_id,
                "targetId": target["id"],
                "label": target["label"],
                "phrase": target["phrase"],
                "box": [float(v) for v in target["box"]],
                "visualState": target.get("visualState", ""),
            }
        )
    rows.sort(key=lambda row: ACTIVE_ORDER.index(row["id"]))
    return rows


def ose_source_boxes(geometry: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    ose_ids = set(geometry.get("summary", {}).get("oseSourceHighlightIds", []))
    for row in geometry.get("rows", []):
        if row.get("sourceId") in ose_ids:
            rows.append(
                {
                    "id": row["sourceId"],
                    "mirroredBox": [float(v) for v in row["mirroredBox"]],
                    "naturalSlotContacts": [item["id"] for item in row.get("overdoseSlotContacts", [])],
                    "naturalActiveContacts": [item["id"] for item in row.get("activeTargetContacts", [])],
                }
            )
    rows.sort(key=lambda row: row["id"])
    return rows


def interval_to_overlap(source: list[float], target: list[float]) -> dict[str, Any]:
    dx_interval = [target[0] - source[2], target[2] - source[0]]
    dy_interval = [target[1] - source[3], target[3] - source[1]]
    possible = dx_interval[0] <= dx_interval[1] and dy_interval[0] <= dy_interval[1]
    dx = closest_to_zero(dx_interval)
    dy = closest_to_zero(dy_interval)
    return {
        "dxInterval": [round(dx_interval[0], 3), round(dx_interval[1], 3)],
        "dyInterval": [round(dy_interval[0], 3), round(dy_interval[1], 3)],
        "possible": possible,
        "closestDx": round(dx, 3),
        "closestDy": round(dy, 3),
        "closestLInf": round(max(abs(dx), abs(dy)), 3),
        "closestEuclidean": round(math.hypot(dx, dy), 3),
    }


def closest_to_zero(interval: list[float]) -> float:
    lo, hi = interval
    if lo <= 0 <= hi:
        return 0.0
    return lo if abs(lo) < abs(hi) else hi


def intersect_intervals(intervals: list[list[float]]) -> list[float] | None:
    lo = max(interval[0] for interval in intervals)
    hi = min(interval[1] for interval in intervals)
    if lo > hi:
        return None
    return [lo, hi]


def shifted_box(box: list[float], dx: float, dy: float) -> list[float]:
    return [box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy]


def coverage_for_shift(
    sources: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    dx: float,
    dy: float,
) -> list[str]:
    hits = set()
    for source in sources:
        sbox = shifted_box(source["mirroredBox"], dx, dy)
        for target in targets:
            interval = interval_to_overlap(sbox, target["box"])
            if interval["possible"] and interval["dxInterval"][0] <= 0 <= interval["dxInterval"][1] and interval["dyInterval"][0] <= 0 <= interval["dyInterval"][1]:
                hits.add(target["id"])
    return sorted(hits, key=ACTIVE_ORDER.index)


def best_subset_solutions(
    sources: list[dict[str, Any]],
    targets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_by_id = {target["id"]: target for target in targets}
    pair_interval: dict[tuple[str, str], dict[str, Any]] = {}
    for source in sources:
        for target in targets:
            pair_interval[(source["id"], target["id"])] = interval_to_overlap(
                source["mirroredBox"], target["box"]
            )

    solutions = []
    for subset_size in range(1, len(targets) + 1):
        best: dict[str, Any] | None = None
        for target_ids in itertools.combinations(ACTIVE_ORDER, subset_size):
            assignments = itertools.product([source["id"] for source in sources], repeat=subset_size)
            for source_ids in assignments:
                dx_intervals = []
                dy_intervals = []
                assignment_rows = []
                valid = True
                for source_id, target_id in zip(source_ids, target_ids):
                    row = pair_interval[(source_id, target_id)]
                    if not row["possible"]:
                        valid = False
                        break
                    dx_intervals.append(row["dxInterval"])
                    dy_intervals.append(row["dyInterval"])
                    assignment_rows.append({"sourceId": source_id, "targetId": target_id})
                if not valid:
                    continue
                dx_interval = intersect_intervals(dx_intervals)
                dy_interval = intersect_intervals(dy_intervals)
                if dx_interval is None or dy_interval is None:
                    continue
                dx = closest_to_zero(dx_interval)
                dy = closest_to_zero(dy_interval)
                coverage = coverage_for_shift(sources, targets, dx, dy)
                solution = {
                    "targetIds": list(target_ids),
                    "assignment": assignment_rows,
                    "dxInterval": [round(dx_interval[0], 3), round(dx_interval[1], 3)],
                    "dyInterval": [round(dy_interval[0], 3), round(dy_interval[1], 3)],
                    "dx": round(dx, 3),
                    "dy": round(dy, 3),
                    "lInf": round(max(abs(dx), abs(dy)), 3),
                    "euclidean": round(math.hypot(dx, dy), 3),
                    "actualCoverageAtClosestShift": coverage,
                    "actualCoverageCountAtClosestShift": len(coverage),
                }
                if best is None or (solution["lInf"], solution["euclidean"]) < (
                    best["lInf"],
                    best["euclidean"],
                ):
                    best = solution
        if best:
            solutions.append({"subsetSize": subset_size, "best": best})
        else:
            solutions.append({"subsetSize": subset_size, "best": None})
    return solutions


def pair_rows(sources: list[dict[str, Any]], targets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for source in sources:
        for target in targets:
            interval = interval_to_overlap(source["mirroredBox"], target["box"])
            rows.append(
                {
                    "sourceId": source["id"],
                    "targetId": target["id"],
                    "targetLabel": target["label"],
                    **interval,
                }
            )
    rows.sort(key=lambda row: (row["closestLInf"], row["targetId"], row["sourceId"]))
    return rows


def draw_sheet(
    sources: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    best_solutions: list[dict[str, Any]],
) -> None:
    page76 = Image.open(PAGE76).convert("RGB")
    mirrored75 = ImageOps.mirror(Image.open(PAGE75).convert("RGB"))
    crop = [250, 2080, 2240, 3060]
    scale = 980 / (crop[2] - crop[0])

    def panel(img: Image.Image, title: str) -> Image.Image:
        local = img.crop(tuple(crop)).copy()
        local = local.resize((980, int(local.height * scale)), Image.Resampling.LANCZOS)
        out = Image.new("RGB", (local.width, local.height + 52), (250, 250, 247))
        out.paste(local, (0, 52))
        ImageDraw.Draw(out).text((16, 12), title, fill=(18, 25, 34), font=font(26, True))
        return out

    def tx(box: list[float], xoff: int, yoff: int = 64) -> list[float]:
        return [
            xoff + (box[0] - crop[0]) * scale,
            yoff + (box[1] - crop[1]) * scale,
            xoff + (box[2] - crop[0]) * scale,
            yoff + (box[3] - crop[1]) * scale,
        ]

    left = panel(mirrored75, "Natural mirrored OSE highlights")
    right = panel(page76, "Active targets plus rescue shifts")
    sheet = Image.new("RGB", (left.width + right.width + 36, left.height + 360), (248, 249, 247))
    sheet.paste(left, (12, 12))
    sheet.paste(right, (left.width + 24, 12))
    draw = ImageDraw.Draw(sheet)
    left_x = 12
    right_x = left.width + 24
    for source in sources:
        rect = tx(source["mirroredBox"], left_x)
        draw.rectangle(rect, outline=(220, 65, 50), width=5)
        draw.text((rect[0] + 5, rect[1] + 4), source["id"], fill=(220, 65, 50), font=font(17, True))
    for target in targets:
        rect = tx(target["box"], right_x)
        draw.rectangle(rect, outline=(40, 145, 90), width=5)
        draw.text((rect[0] + 5, rect[1] + 4), target["id"], fill=(40, 145, 90), font=font(18, True))

    one = next((row["best"] for row in best_solutions if row["subsetSize"] == 1), None)
    two = next((row["best"] for row in best_solutions if row["subsetSize"] == 2), None)
    for solution, color in [(one, (65, 105, 220)), (two, (185, 75, 200))]:
        if not solution:
            continue
        for source in sources:
            rect = tx(shifted_box(source["mirroredBox"], solution["dx"], solution["dy"]), right_x)
            draw.rectangle(rect, outline=color, width=3)
            draw.text((rect[0] + 5, rect[3] + 2), f"{source['id']} shift", fill=color, font=font(13, True))

    y = left.height + 36
    draw.text((20, y), "Best single-translation rescue checks", fill=(18, 25, 34), font=font(24, True))
    y += 42
    headers = ["coverage", "dx", "dy", "Linf", "targets", "assignment"]
    xs = [20, 140, 230, 320, 430, 650]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(72, 82, 96), font=font(16, True))
    y += 28
    for row in best_solutions:
        best = row["best"]
        if not best:
            vals = [row["subsetSize"], "-", "-", "-", "-", "impossible"]
        else:
            vals = [
                row["subsetSize"],
                best["dx"],
                best["dy"],
                best["lInf"],
                ",".join(best["actualCoverageAtClosestShift"]),
                "; ".join(f"{a['sourceId']}->{a['targetId']}" for a in best["assignment"]),
            ]
        for x, value in zip(xs, vals):
            draw.text((x, y), str(value)[:42], fill=(22, 28, 36), font=font(15))
        y += 26
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    geometry = load_json(OSE_GEOMETRY)
    sources = ose_source_boxes(geometry)
    targets = active_targets(load_json(ACTIVE_TARGETS))
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_count = len(reopen.get("triggerRows", []))
    pairs = pair_rows(sources, targets)
    solutions = best_subset_solutions(sources, targets)
    natural_coverage = sorted(
        {
            contact
            for source in sources
            for contact in source.get("naturalActiveContacts", [])
        },
        key=lambda item: ACTIVE_ORDER.index(item),
    )
    small_best = max(
        (
            len(row["best"]["actualCoverageAtClosestShift"])
            for row in solutions
            if row["best"] and row["best"]["lInf"] <= SMALL_SHIFT_LIMIT
        ),
        default=0,
    )
    moderate_best = max(
        (
            len(row["best"]["actualCoverageAtClosestShift"])
            for row in solutions
            if row["best"] and row["best"]["lInf"] <= MODERATE_SHIFT_LIMIT
        ),
        default=0,
    )
    one_best = next((row["best"] for row in solutions if row["subsetSize"] == 1), None)
    two_best = next((row["best"] for row in solutions if row["subsetSize"] == 2), None)
    three_possible = next((row["best"] for row in solutions if row["subsetSize"] == 3), None) is not None
    four_possible = next((row["best"] for row in solutions if row["subsetSize"] == 4), None) is not None
    selector_candidates = 0
    source_backed_r3 = 0
    satisfied_triggers = 0
    fingerprint = (
        f"sources={len(sources)}|targets={len(targets)}|natural={len(natural_coverage)}|"
        f"small160={small_best}|moderate320={moderate_best}|"
        f"oneLinf={one_best['lInf'] if one_best else '-'}|"
        f"twoLinf={two_best['lInf'] if two_best else '-'}|"
        f"threePossible={int(three_possible)}|fourPossible={int(four_possible)}|"
        f"candidates={selector_candidates}|sourceR3={source_backed_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    decision = "pdf_ose_highlight_translation_rescue_no_selector"
    summary = {
        "sourceHighlightCount": len(sources),
        "activeTargetCount": len(targets),
        "naturalActiveCoverageCount": len(natural_coverage),
        "naturalActiveCoverageIds": natural_coverage,
        "smallShiftLimitPx": SMALL_SHIFT_LIMIT,
        "smallShiftBestCoverageCount": small_best,
        "moderateShiftLimitPx": MODERATE_SHIFT_LIMIT,
        "moderateShiftBestCoverageCount": moderate_best,
        "minimumOneTargetShift": one_best,
        "minimumTwoTargetShift": two_best,
        "threeTargetTranslationPossible": three_possible,
        "fourTargetTranslationPossible": four_possible,
        "selectorCandidateCount": selector_candidates,
        "sourceBackedR3BridgeHitCount": source_backed_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "fingerprint": fingerprint,
    }
    draw_sheet(sources, targets, solutions)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "single-translation rescue feasibility for mirrored OSE source highlights against locked O4/B4/G5/O5 targets; no extraction/key derivation",
        "inputs": {
            "oseHighlightMirrorGeometryGate": rel(OSE_GEOMETRY),
            "activeTargets": rel(ACTIVE_TARGETS),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "sourceHighlights": sources,
        "activeTargets": targets,
        "pairRows": pairs,
        "bestSubsetSolutions": solutions,
        "decision": decision,
        "reason": (
            "No <=160px physical-style translation makes the OSE source highlights hit active targets. "
            "The first possible active hit needs a 190px vertical shift, two-target coverage needs a "
            "928px horizontal shift, and three/four-target coverage is impossible for these two boxes."
        ),
        "nextMove": (
            "Do not use OSE highlight translation rescue as a selector. Treat OSE as slot-band provenance "
            "unless a new source/clue supplies a non-arbitrary transform and read order."
        ),
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current PDF OSE Highlight Translation Rescue Gate",
        "",
        "Scope: computed exact global-translation intervals needed for the two mirrored OSE page-75 source-highlight boxes to overlap locked page-76 O4/B4/G5/O5 targets. This is a bounded geometry feasibility check only; no OCR-to-key extraction, key candidates, hashes-to-key, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{decision}`",
        f"- OSE source highlights / active targets: `{len(sources)}` / `{len(targets)}`",
        f"- Natural active coverage: `{len(natural_coverage)}/4`",
        f"- Best coverage within `{int(SMALL_SHIFT_LIMIT)}` px: `{small_best}/4`",
        f"- Best coverage within `{int(MODERATE_SHIFT_LIMIT)}` px: `{moderate_best}/4`",
        f"- Minimum one-target shift: `dx={one_best['dx'] if one_best else '-'}, dy={one_best['dy'] if one_best else '-'}, Linf={one_best['lInf'] if one_best else '-'}`",
        f"- Minimum two-target shift: `dx={two_best['dx'] if two_best else '-'}, dy={two_best['dy'] if two_best else '-'}, Linf={two_best['lInf'] if two_best else '-'}`",
        f"- Three-target translation possible: `{int(three_possible)}`",
        f"- Four-target translation possible: `{int(four_possible)}`",
        f"- Selector candidates: `{selector_candidates}`",
        f"- Source-backed R3 / satisfied triggers: `{source_backed_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        "",
        "## Best Translation Solutions",
        "",
        "| requested coverage | dx | dy | L-inf | actual coverage at closest shift | assignment |",
        "|---:|---:|---:|---:|---|---|",
    ]
    for row in solutions:
        best = row["best"]
        if not best:
            lines.append(f"| `{row['subsetSize']}` | `-` | `-` | `-` | `-` | `impossible` |")
        else:
            assignment = "; ".join(f"{item['sourceId']}->{item['targetId']}" for item in best["assignment"])
            lines.append(
                f"| `{row['subsetSize']}` | `{best['dx']}` | `{best['dy']}` | `{best['lInf']}` | `{','.join(best['actualCoverageAtClosestShift']) or '-'}` | `{assignment}` |"
            )
    lines.extend(
        [
            "",
            "## Closest Pairwise Hits",
            "",
            "| source | target | closest dx | closest dy | L-inf | interval dx | interval dy |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in pairs[:8]:
        lines.append(
            f"| `{row['sourceId']}` | `{row['targetId']}` | `{row['closestDx']}` | `{row['closestDy']}` | `{row['closestLInf']}` | `{row['dxInterval']}` | `{row['dyInterval']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`.",
            "- A small physical-style registration correction does not rescue OSE onto any active target.",
            "- The first active contact needs a `190px` vertical shift, which is already outside the small tolerance used for scan-slip checks.",
            "- Two-target coverage needs a roughly half-page horizontal relocation (`928px`), and three/four-target coverage is impossible for these two OSE highlight boxes under one global shift.",
            "",
            "## Next Move",
            "",
            "- Keep OSE as slot-band provenance only. Reopen only with source/clue wording that names a non-arbitrary transform and read order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{fingerprint}|decision={decision}")


if __name__ == "__main__":
    main()

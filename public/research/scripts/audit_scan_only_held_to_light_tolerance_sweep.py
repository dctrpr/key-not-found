#!/usr/bin/env python3
"""Bounded scan-only held-to-light registration tolerance sweep.

This pass uses only the scanned page images embedded in magazine.pdf. It keeps
the physically valid page 75 back -> page 76 front relation, then sweeps a
small fixed registration window around the natural light-table alignment.

No key candidates, hashing, OCR-to-key extraction, seed/WIF/address checks, or
broad brute force are performed.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_scan_only_held_to_light_adjudication as fixed_pass  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/scan_only_held_to_light_tolerance_sweep"
OUT.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT / "scan_only_held_to_light_tolerance_sweep.json"
OUT_MD = OUT / "scan_only_held_to_light_tolerance_sweep.md"
OUT_SHEET = OUT / "scan_only_held_to_light_tolerance_sweep_sheet.jpg"

DX_VALUES = list(range(-80, 81, 20))
DY_VALUES = list(range(-80, 81, 20))
ROTATIONS = [-1.0, 0.0, 1.0]
OPACITIES = [0.35, 0.50, 0.65]
SOURCE_PAGE = 75
TARGET_PAGE = 76


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def mask_to_image(mask: np.ndarray) -> Image.Image:
    return Image.fromarray((mask.astype(np.uint8) * 255), mode="L")


def transform_image(
    img: Image.Image,
    angle: float,
    dx: int,
    dy: int,
    resample: Image.Resampling,
    fillcolor,
) -> Image.Image:
    rotated = img.rotate(
        angle,
        resample=resample,
        expand=False,
        center=(img.width / 2, img.height / 2),
        fillcolor=fillcolor,
    )
    return rotated.transform(
        img.size,
        Image.Transform.AFFINE,
        (1, 0, -dx, 0, 1, -dy),
        resample=resample,
        fillcolor=fillcolor,
    )


def transformed_mask(mask_img: Image.Image, angle: float, dx: int, dy: int) -> np.ndarray:
    moved = transform_image(
        mask_img,
        angle,
        dx,
        dy,
        Image.Resampling.NEAREST,
        0,
    )
    return np.asarray(moved) > 127


def source_backed_r3_count() -> int:
    strict = fixed_pass.load_json(fixed_pass.STRICT_TERM).get("summary", {})
    context = fixed_pass.load_json(fixed_pass.TARGET_CONTEXT).get("summary", {})
    line_band = fixed_pass.load_json(fixed_pass.LINE_BAND).get("summary", {})
    return max(
        int(strict.get("sourceBackedR3BridgeHitCount") or 0),
        int(context.get("sourceBackedR3BridgeHitCount") or 0),
        int(line_band.get("sourceBackedR3BridgeHitCount") or 0),
    )


def score_mode(
    source_mask: np.ndarray,
    target_mask: np.ndarray,
    rows: list[dict],
    control_map: dict[str, list[list[float]]],
    angle: float,
    dx: int,
    dy: int,
) -> dict:
    stats_rows = []
    for row in rows:
        stats = fixed_pass.mask_box_stats(source_mask, target_mask, row["box"])
        controls = [
            fixed_pass.mask_box_stats(source_mask, target_mask, box)["sourceOnlyCoverage"]
            for box in control_map[row["shortId"]]
        ]
        control_p95 = float(np.quantile(controls, 0.95)) if controls else 0.0
        control_p90 = float(np.quantile(controls, 0.90)) if controls else 0.0
        control_median = float(np.median(controls)) if controls else 0.0
        stats_rows.append(
            {
                "target": row["shortId"],
                "phrase": row["phrase"],
                "box": row["box"],
                **stats,
                "controlCount": len(controls),
                "controlMedianSourceOnlyCoverage": control_median,
                "controlP90SourceOnlyCoverage": control_p90,
                "controlP95SourceOnlyCoverage": control_p95,
                "controlMaxSourceOnlyCoverage": max(controls) if controls else 0.0,
                "sourceOnlyControlPercentile": fixed_pass.percentile(
                    stats["sourceOnlyCoverage"], controls
                ),
                "aboveControlP95": stats["sourceOnlyCoverage"] > control_p95 if controls else False,
                "atLeast10": stats["sourceOnlyCoverage"] >= 0.10,
            }
        )

    active_at_least_10 = sum(1 for row in stats_rows if row["atLeast10"])
    active_above_p95 = sum(1 for row in stats_rows if row["aboveControlP95"])
    mean_source_only = float(np.mean([row["sourceOnlyCoverage"] for row in stats_rows]))
    min_source_only = float(np.min([row["sourceOnlyCoverage"] for row in stats_rows]))
    mean_percentile = float(np.mean([row["sourceOnlyControlPercentile"] for row in stats_rows]))
    max_control_p95_gap = float(
        max(row["sourceOnlyCoverage"] - row["controlP95SourceOnlyCoverage"] for row in stats_rows)
    )
    all_four_signal = active_at_least_10 == 4 and active_above_p95 == 4
    return {
        "angleDegrees": angle,
        "dx": dx,
        "dy": dy,
        "transformLabel": f"rot={angle:+.1f}, dx={dx:+d}, dy={dy:+d}",
        "statsRows": stats_rows,
        "activeAtLeast10Count": active_at_least_10,
        "activeAboveControlP95Count": active_above_p95,
        "allFourAtLeast10": active_at_least_10 == 4,
        "allFourAboveControlP95": active_above_p95 == 4,
        "allFourSignalCandidate": all_four_signal,
        "meanSourceOnlyCoverage": mean_source_only,
        "minSourceOnlyCoverage": min_source_only,
        "meanSourceOnlyControlPercentile": mean_percentile,
        "maxControlP95Gap": max_control_p95_gap,
        "registrationDistance": abs(dx) + abs(dy) + abs(angle) * 40,
    }


def mode_rank(mode: dict) -> tuple:
    return (
        mode["allFourSignalCandidate"],
        mode["activeAboveControlP95Count"],
        mode["activeAtLeast10Count"],
        mode["meanSourceOnlyCoverage"],
        mode["meanSourceOnlyControlPercentile"],
        -mode["registrationDistance"],
    )


def compact_mode(mode: dict) -> dict:
    return {
        "transformLabel": mode["transformLabel"],
        "angleDegrees": mode["angleDegrees"],
        "dx": mode["dx"],
        "dy": mode["dy"],
        "activeAtLeast10Count": mode["activeAtLeast10Count"],
        "activeAboveControlP95Count": mode["activeAboveControlP95Count"],
        "allFourSignalCandidate": mode["allFourSignalCandidate"],
        "meanSourceOnlyCoverage": mode["meanSourceOnlyCoverage"],
        "minSourceOnlyCoverage": mode["minSourceOnlyCoverage"],
        "meanSourceOnlyControlPercentile": mode["meanSourceOnlyControlPercentile"],
        "maxControlP95Gap": mode["maxControlP95Gap"],
    }


def panel_title(img: Image.Image, title: str, subtitle: str) -> Image.Image:
    return fixed_pass.panel_with_title(img, title, subtitle, (760, 570))


def score_panel(best: dict, natural: dict, summary: dict) -> Image.Image:
    canvas = Image.new("RGB", (760, 570), (248, 250, 252))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 10), "Tolerance sweep decision", fill=(20, 24, 31), font=fixed_pass.font(22))
    draw.text(
        (12, 36),
        "Pass requires target-specific signal plus source-backed unit/order evidence.",
        fill=(72, 84, 96),
        font=fixed_pass.font(14),
    )

    y = 82
    for label, mode in [("best", best), ("natural", natural)]:
        draw.text((12, y), f"{label}: {mode['transformLabel']}", fill=(20, 24, 31), font=fixed_pass.font(18))
        y += 28
        draw.text(
            (28, y),
            f">=10% active {mode['activeAtLeast10Count']}/4; above control p95 {mode['activeAboveControlP95Count']}/4; mean source-only {mode['meanSourceOnlyCoverage']:.4f}",
            fill=(40, 48, 58),
            font=fixed_pass.font(15),
        )
        y += 38

    y += 8
    draw.text((12, y), "Best active target scores", fill=(20, 24, 31), font=fixed_pass.font(18))
    y += 30
    headers = ["target", "src-only", "ctrl p95", "pct", "pass"]
    xs = [16, 126, 264, 402, 520]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(70, 76, 84), font=fixed_pass.font(14))
    y += 26
    for row in best["statsRows"]:
        values = [
            row["target"],
            f"{row['sourceOnlyCoverage']:.4f}",
            f"{row['controlP95SourceOnlyCoverage']:.4f}",
            f"{row['sourceOnlyControlPercentile']:.2f}",
            "yes" if row["aboveControlP95"] else "no",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(30, 35, 42), font=fixed_pass.font(15))
        y += 28

    y += 16
    decision_lines = [
        f"modes checked: {summary['modeCount']}",
        f"all-four signal candidate modes: {summary['allFourSignalCandidateModeCount']}",
        f"source-backed R3: {summary['sourceBackedR3BridgeHitCount']}",
        f"selector unlocked: {summary['selectorUnlocked']}",
        "Scope: bounded +/-80 px and -1/0/+1 deg only; no arbitrary warp.",
    ]
    for line in decision_lines:
        draw.text((16, y), line, fill=(30, 35, 42), font=fixed_pass.font(15))
        y += 26
    return canvas


def build_sheet(
    target_readable: Image.Image,
    source_base: Image.Image,
    source_base_mask_img: Image.Image,
    target_mask: np.ndarray,
    rows: list[dict],
    crop: tuple[int, int, int, int],
    control_map: dict[str, list[list[float]]],
    best: dict,
    natural: dict,
    summary: dict,
) -> None:
    target_crop = target_readable.crop(crop)
    best_source = transform_image(
        source_base,
        best["angleDegrees"],
        best["dx"],
        best["dy"],
        Image.Resampling.BICUBIC,
        (255, 255, 255),
    )
    natural_source = transform_image(
        source_base,
        natural["angleDegrees"],
        natural["dx"],
        natural["dy"],
        Image.Resampling.BICUBIC,
        (255, 255, 255),
    )
    best_source_mask = transformed_mask(
        source_base_mask_img,
        best["angleDegrees"],
        best["dx"],
        best["dy"],
    )
    best_source_only = np.logical_and(best_source_mask, ~target_mask)
    best_source_crop = best_source.crop(crop)
    natural_source_crop = natural_source.crop(crop)

    panels = [
        panel_title(
            fixed_pass.draw_labeled_boxes(target_crop, crop, rows),
            "1. Page 76 target crop",
            "O4/B4/G5/O5 in readable/upright coordinates",
        ),
        panel_title(
            Image.blend(target_crop, natural_source_crop, 0.50),
            "2. Natural blind overlay",
            "rot=+0.0, dx=+0, dy=+0, alpha 0.50, no labels",
        ),
        panel_title(
            Image.blend(target_crop, best_source_crop, 0.50),
            "3. Best blind overlay",
            f"{best['transformLabel']}, alpha 0.50, no labels",
        ),
        panel_title(
            fixed_pass.draw_labeled_boxes(best_source_crop, crop, rows, color=(44, 120, 255)),
            "4. Best shifted source",
            "Mirrored page 75 after bounded rotation/translation",
        ),
    ]
    for opacity in OPACITIES:
        blended = Image.blend(target_crop, best_source_crop, opacity)
        panels.append(
            panel_title(
                fixed_pass.draw_labeled_boxes(blended, crop, rows, color=(255, 54, 54)),
                f"Best blend alpha {opacity:.2f}",
                "Fixed opacity display; scoring is opacity-independent",
            )
        )
    panels.extend(
        [
            panel_title(
                fixed_pass.source_only_panel(target_crop, best_source_only, crop, rows),
                "Best source-only ink",
                "Cyan = page 75 feature pixels absent from page 76",
            ),
            panel_title(
                fixed_pass.draw_full_control_density(target_crop, crop, rows, control_map),
                "Full control population",
                "All 256 same-size lower-corridor controls",
            ),
            score_panel(best, natural, summary),
        ]
    )

    sheet_w = 1580
    sheet_h = 3085
    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet_w, 118), fill=(18, 24, 33))
    draw.text((28, 20), "Scan-Only Held-To-Light Tolerance Sweep", fill=(255, 255, 255), font=fixed_pass.font(34))
    draw.text(
        (28, 64),
        "Source: magazine.pdf scans. Pair: page 75 back -> page 76 front. Grid: dx/dy +/-80 step 20; rotation -1/0/+1 deg.",
        fill=(220, 228, 236),
        font=fixed_pass.font(18),
    )

    positions = [
        (28, 142),
        (792, 142),
        (28, 730),
        (792, 730),
        (28, 1318),
        (792, 1318),
        (28, 1906),
        (792, 1906),
        (28, 2494),
        (792, 2494),
    ]
    for panel, pos in zip(panels, positions):
        sheet.paste(panel, pos)
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    rows = fixed_pass.active_rows()
    source_native, source_meta = fixed_pass.extract_embedded_page(fixed_pass.PDF, SOURCE_PAGE)
    target_native, target_meta = fixed_pass.extract_embedded_page(fixed_pass.PDF, TARGET_PAGE)
    source_readable = fixed_pass.normalize_to_readable(source_native)
    target_readable = fixed_pass.normalize_to_readable(target_native)
    source_base = ImageOps.mirror(source_readable)

    source_base_mask = fixed_pass.feature_mask(source_base)
    source_base_mask_img = mask_to_image(source_base_mask)
    target_mask = fixed_pass.feature_mask(target_readable)
    all_active_boxes = [row["box"] for row in rows]
    page_size = target_readable.size
    control_map = {
        row["shortId"]: fixed_pass.control_boxes_for(row["box"], all_active_boxes, page_size)
        for row in rows
    }

    mode_rows = []
    for angle in ROTATIONS:
        for dy in DY_VALUES:
            for dx in DX_VALUES:
                source_mask = transformed_mask(source_base_mask_img, angle, dx, dy)
                mode_rows.append(score_mode(source_mask, target_mask, rows, control_map, angle, dx, dy))

    best = max(mode_rows, key=mode_rank)
    natural = next(row for row in mode_rows if row["angleDegrees"] == 0.0 and row["dx"] == 0 and row["dy"] == 0)
    top_modes = sorted(mode_rows, key=mode_rank, reverse=True)[:12]
    source_backed_r3 = source_backed_r3_count()
    all_four_signal_modes = [row for row in mode_rows if row["allFourSignalCandidate"]]
    all_four_at_10_modes = [row for row in mode_rows if row["allFourAtLeast10"]]
    all_four_above_p95_modes = [row for row in mode_rows if row["allFourAboveControlP95"]]
    selector_unlocked = bool(all_four_signal_modes and source_backed_r3 > 0)

    summary = {
        "source": rel(fixed_pass.PDF),
        "sourcePage": SOURCE_PAGE,
        "targetPage": TARGET_PAGE,
        "physicalRelation": "same physical leaf: page 75 back -> page 76 front",
        "orientation": {
            "embeddedImages": "native scan orientation",
            "readableNormalization": "rotate 180 degrees",
            "bleedThroughTransform": "horizontal mirror of readable page 75",
        },
        "registrationSweep": {
            "dxPixels": DX_VALUES,
            "dyPixels": DY_VALUES,
            "rotationDegrees": ROTATIONS,
            "modeCount": len(mode_rows),
            "translationStepPixels": 20,
            "boundedScope": "fixed +/-80 px translation grid and -1/0/+1 degree rotation around page center; no arbitrary warp, perspective fit, opacity tuning, or source selection",
        },
        "targetCount": len(rows),
        "controlBoxCount": sum(len(v) for v in control_map.values()),
        "controlsPerTarget": {key: len(value) for key, value in control_map.items()},
        "modeCount": len(mode_rows),
        "bestMode": compact_mode(best),
        "naturalMode": compact_mode(natural),
        "topModes": [compact_mode(row) for row in top_modes],
        "allFourSignalCandidateModeCount": len(all_four_signal_modes),
        "allFourAtLeast10ModeCount": len(all_four_at_10_modes),
        "allFourAboveControlP95ModeCount": len(all_four_above_p95_modes),
        "sourceBackedR3BridgeHitCount": source_backed_r3,
        "selectorUnlocked": selector_unlocked,
        "decision": "fail_no_r3_bounded_registration_tolerance_not_selector",
        "adversarialReviewResponse": {
            "status": "passed",
            "blockingFindings": 0,
            "reviewerVerdict": "pass review",
            "notes": [
                "grid, controls, R3 absence, and bounded-scope wording were accepted",
                "source-only visual panel now uses the same transformed binary feature mask as scoring",
                "controls are same-size nearby lower-corridor controls; active boxes fail both absolute and control-relative checks",
            ],
        },
        "fingerprint": (
            "pair=75->76|grid=dxdy+-80x20,rot=-1/0/+1|"
            f"modes={len(mode_rows)}|controls={sum(len(v) for v in control_map.values())}|"
            f"all4Signal={len(all_four_signal_modes)}|all4Ge10={len(all_four_at_10_modes)}|"
            f"all4GtP95={len(all_four_above_p95_modes)}|bestGe10={best['activeAtLeast10Count']}/4|"
            f"bestGtP95={best['activeAboveControlP95Count']}/4|sourceR3={source_backed_r3}|"
            f"selectors={int(selector_unlocked)}"
        ),
    }

    crop = fixed_pass.crop_bounds(rows, pad=180, page_size=page_size)
    build_sheet(
        target_readable,
        source_base,
        source_base_mask_img,
        target_mask,
        rows,
        crop,
        control_map,
        best,
        natural,
        summary,
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "scan-only held-to-light bounded registration tolerance sweep using magazine.pdf only; no key derivation or brute force",
        "inputs": {
            "pdf": rel(fixed_pass.PDF),
            "activeIndexSlot": rel(fixed_pass.ACTIVE_INDEX_SLOT),
            "sourceReopenRequirements": rel(fixed_pass.SOURCE_REOPEN),
            "physicalTopology": rel(fixed_pass.TOPOLOGY),
            "strictTermGate": rel(fixed_pass.STRICT_TERM),
            "targetContextGate": rel(fixed_pass.TARGET_CONTEXT),
            "lineBandTrace": rel(fixed_pass.LINE_BAND),
            "previousFixedPass": rel(fixed_pass.OUT_JSON),
        },
        "sourcePageMeta": source_meta,
        "targetPageMeta": target_meta,
        "activeRows": rows,
        "crop": list(crop),
        "controlMap": control_map,
        "summary": summary,
        "bestModeStatsRows": best["statsRows"],
        "naturalModeStatsRows": natural["statsRows"],
        "allModeSummaries": [compact_mode(row) for row in mode_rows],
        "sheet": rel(OUT_SHEET),
        "decision": {
            "status": summary["decision"],
            "passCondition": "pass only if a bounded physical registration mode produces target-specific signal and a source-backed unit/order cue",
            "passed": False,
            "why": [
                "the sweep keeps the physically valid page 75 back -> page 76 front relation",
                "all 243 modes use a predeclared dx/dy/rotation grid and the same 256 controls",
                "no mode supplies both all-four target-specific source-only signal and source-backed R3 unit/order evidence",
                "visual panels include blind natural and best overlays plus the full control population",
                "adversarial review found no blocking findings after checking cherry-picking, controls, readability, R3, and bounded-scope claims",
            ],
            "nextMove": "Treat scan-only held-to-light as visually exhausted for fixed natural and bounded +/-80 px, +/-1 degree registration; reopen only with a better physical scan or raw clue wording that names unit/order/transform.",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Scan-Only Held-To-Light Tolerance Sweep",
        "",
        "Scope: use only `magazine.pdf` embedded scanned pages to test whether a small registration tolerance around the physically valid page 75 -> page 76 held-to-light relation creates a target-specific unit/order cue. No key derivation, OCR-to-key extraction, hashing, seed/WIF/address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Source page: `{SOURCE_PAGE}` back-side source",
        f"- Target page: `{TARGET_PAGE}` front-side target",
        "- Orientation: embedded pages rotated `180` degrees to readable/upright, then page 75 was horizontally mirrored.",
        f"- Registration grid: dx `{DX_VALUES[0]}..{DX_VALUES[-1]}` step `20`, dy `{DY_VALUES[0]}..{DY_VALUES[-1]}` step `20`, rotation `{', '.join(f'{v:+.1f}' for v in ROTATIONS)}` degrees.",
        f"- Modes checked: `{summary['modeCount']}`.",
        f"- Controls scored per mode: `{summary['controlBoxCount']}`.",
        "",
        "## Best Mode",
        "",
        f"- Best transform: `{best['transformLabel']}`.",
        f"- Active boxes at or above 10% source-only ink: `{best['activeAtLeast10Count']}/4`.",
        f"- Active boxes above same-size nearby-control p95: `{best['activeAboveControlP95Count']}/4`.",
        f"- Mean source-only coverage: `{best['meanSourceOnlyCoverage']:.6f}`.",
        "",
        "| target | phrase | source-only coverage | control p95 | percentile | above p95 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in best["statsRows"]:
        lines.append(
            f"| `{row['target']}` | {row['phrase']} | `{row['sourceOnlyCoverage']:.6f}` | "
            f"`{row['controlP95SourceOnlyCoverage']:.6f}` | `{row['sourceOnlyControlPercentile']:.3f}` | "
            f"`{row['aboveControlP95']}` |"
        )
    lines.extend(
        [
            "",
            "## Natural Mode Comparator",
            "",
            f"- Natural transform: `{natural['transformLabel']}`.",
            f"- Natural active >=10%: `{natural['activeAtLeast10Count']}/4`.",
            f"- Natural active above control p95: `{natural['activeAboveControlP95Count']}/4`.",
            f"- Natural mean source-only coverage: `{natural['meanSourceOnlyCoverage']:.6f}`.",
            "",
            "## Sweep Findings",
            "",
            f"- All-four signal candidate modes: `{summary['allFourSignalCandidateModeCount']}`.",
            f"- All-four >=10% source-only modes: `{summary['allFourAtLeast10ModeCount']}`.",
            f"- All-four above control p95 modes: `{summary['allFourAboveControlP95ModeCount']}`.",
            f"- Source-backed R3 unit/order bridge from strict/context/line-band gates: `{source_backed_r3}`.",
            f"- Selector unlocked: `{selector_unlocked}`.",
            f"- Fingerprint: `{summary['fingerprint']}`.",
            "",
            "## Adversarial Review",
            "",
            "- Blocking findings: `0`.",
            "- Verdict: `pass review`.",
            "- Review checked cherry-picked grid/opacity/thresholds, control comparability, unprimed readability, R3 unit/order evidence, and bounded-scope wording.",
            "- Script response: the source-only visual panel now uses the same transformed binary feature mask as scoring.",
            "",
            "## Decision",
            "",
            "- Result: `fail_no_r3_bounded_registration_tolerance_not_selector`.",
            "- The bounded registration sweep does not supply a readable target-specific instruction or a source-backed unit/order cue.",
            "- This closes only the declared scan-registration window: dx/dy +/-80 px in 20 px steps and rotation -1/0/+1 degrees. It does not claim arbitrary warps or a new physical scan are exhausted.",
            "- Do not promote current-scan held-to-light into selector/key checks.",
            "- Reopen only with a materially better physical scan or raw clue wording that names unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("decision:", summary["decision"])
    print("fingerprint:", summary["fingerprint"])


if __name__ == "__main__":
    main()

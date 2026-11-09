#!/usr/bin/env python3
"""Audit held-to-light opacity/color transfer on the current scan.

This bounded visual pass extends the existing held-to-light simulator by
testing opacity and blend mechanics directly on the current PDF/source images.
It asks whether a plausible light-through blend reveals the page-76 active
quartet, orange/black state, or OVERDOSE-related mechanics more cleanly than
forced/non-physical controls.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_held_to_light_opacity_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_held_to_light_opacity_gate.json"
OUT_MD = OUT / "current_scan_held_to_light_opacity_gate.md"
OUT_SHEET = OUT / "current_scan_held_to_light_opacity_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
HELD_TO_LIGHT_SIMULATOR = ROOT / (
    "analysis_outputs/source_audit/current_scan_held_to_light_simulator/"
    "current_scan_held_to_light_simulator.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

ALPHAS = [0.25, 0.50, 0.75]
BLEND_MODES = ["average", "darken", "multiply"]
DELTA_THRESHOLDS = [8.0, 16.0, 32.0]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def normalize_page(page: int) -> Image.Image:
    source = Image.open(str(SOURCE_PAGE_TEMPLATE).format(page=page)).convert("RGB")
    upright = Image.open(str(UPRIGHT_PAGE_TEMPLATE).format(page=page)).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(
        ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean
    )
    return source.rotate(180) if rot_diff < same_diff else source


def shifted_mirrored_source(page: Image.Image, dx: int, dy: int) -> Image.Image:
    mirrored = ImageOps.mirror(page)
    canvas = Image.new("RGB", page.size, "white")
    canvas.paste(mirrored, (dx, dy))
    return canvas


def blend_arrays(target: np.ndarray, source: np.ndarray, mode: str, alpha: float) -> np.ndarray:
    t = target.astype(np.float32)
    s = source.astype(np.float32)
    if mode == "average":
        base = s
    elif mode == "darken":
        base = np.minimum(t, s)
    elif mode == "multiply":
        base = (t * s) / 255.0
    else:  # pragma: no cover
        raise ValueError(mode)
    return np.clip((1.0 - alpha) * t + alpha * base, 0, 255).astype(np.uint8)


def luma(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def orange_mask(arr: np.ndarray) -> np.ndarray:
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    return (r > 135) & (g > 55) & (g < 215) & (b < 155) & (r > g + 20)


def dark_mask(arr: np.ndarray) -> np.ndarray:
    return luma(arr) < 95


def classify_visual_state(arr: np.ndarray) -> str:
    orange_ratio = float(orange_mask(arr).mean()) if arr.size else 0.0
    dark_ratio = float(dark_mask(arr).mean()) if arr.size else 0.0
    if dark_ratio >= max(0.08, orange_ratio * 0.8):
        return "K"
    if orange_ratio >= 0.08:
        return "Y"
    return "N"


def crop_arr(arr: np.ndarray, box: list[float]) -> np.ndarray:
    x0, y0, x1, y1 = [round(v) for v in box]
    return arr[max(0, y0) : max(0, y1), max(0, x0) : max(0, x1), :]


def box_metrics(target_arr: np.ndarray, blend_arr: np.ndarray, box: dict[str, Any]) -> dict[str, Any]:
    target_crop = crop_arr(target_arr, box["box"])
    blend_crop = crop_arr(blend_arr, box["box"])
    target_luma = luma(target_crop)
    blend_luma = luma(blend_crop)
    mean_target = float(target_luma.mean()) if target_luma.size else 0.0
    mean_blend = float(blend_luma.mean()) if blend_luma.size else 0.0
    darkening = max(0.0, mean_target - mean_blend)
    abs_delta = float(np.abs(target_crop.astype(np.int16) - blend_crop.astype(np.int16)).mean()) if target_crop.size else 0.0
    return {
        "target": box["shortId"],
        "phrase": box["phrase"],
        "expectedVisualState": box["visualState"],
        "baselineState": classify_visual_state(target_crop),
        "blendState": classify_visual_state(blend_crop),
        "meanLumaBaseline": round(mean_target, 6),
        "meanLumaBlend": round(mean_blend, 6),
        "darkeningDelta": round(darkening, 6),
        "absoluteRgbDelta": round(abs_delta, 6),
        "baselineOrangeRatio": round(float(orange_mask(target_crop).mean()) if target_crop.size else 0.0, 6),
        "blendOrangeRatio": round(float(orange_mask(blend_crop).mean()) if blend_crop.size else 0.0, 6),
        "baselineDarkRatio": round(float(dark_mask(target_crop).mean()) if target_crop.size else 0.0, 6),
        "blendDarkRatio": round(float(dark_mask(blend_crop).mean()) if blend_crop.size else 0.0, 6),
    }


def held_sim_row(rows: list[dict[str, Any]], pair_id: str, mode: str) -> dict[str, Any]:
    for row in rows:
        if row.get("pairId") == pair_id and row.get("mode") == mode:
            return row
    raise KeyError(f"{pair_id}/{mode}")


def scenario_rows(held: dict[str, Any]) -> list[dict[str, Any]]:
    rows = held.get("rows", [])
    picked = [
        ("valid_75_to_76_natural", "same_leaf_75_to_76", "natural_hflip", "valid same leaf, natural alignment"),
        ("valid_75_to_76_forced_active", "same_leaf_75_to_76", "best_page76_active_boxes", "valid same leaf, forced active-box alignment"),
        ("nonphysical_78_to_76_forced_active", "nonphysical_78_to_76", "best_page76_active_boxes", "non-physical page-76 benchmark"),
        ("nonphysical_79_to_76_forced_active", "nonphysical_79_to_76", "best_page76_active_boxes", "non-physical page-76 benchmark"),
    ]
    scenarios: list[dict[str, Any]] = []
    for scenario_id, pair_id, mode, topology in picked:
        source = held_sim_row(rows, pair_id, mode)
        scenarios.append(
            {
                "scenarioId": scenario_id,
                "pairId": pair_id,
                "sourcePage": int(source["sourcePage"]),
                "targetPage": int(source["targetPage"]),
                "heldToLightMode": mode,
                "topology": topology,
                "dx": int(source["dx"]),
                "dy": int(source["dy"]),
                "binaryActiveOverTarget": float(source.get("activeOverTarget", 0.0)),
            }
        )
    return scenarios


def save_preview(
    image: Image.Image,
    scenario: dict[str, Any],
    mode: str,
    alpha: float,
    active_boxes: list[dict[str, Any]],
) -> Path:
    out_w = 720
    out_h = round(out_w * image.height / image.width)
    preview = image.resize((out_w, out_h))
    draw = ImageDraw.Draw(preview, "RGBA")
    sx = out_w / image.width
    sy = out_h / image.height
    for box in active_boxes:
        x0, y0, x1, y1 = box["box"]
        rect = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
        color = (255, 128, 0, 240) if box["visualState"] == "Y" else (40, 40, 40, 240)
        draw.rectangle(rect, outline=color, width=3)
        draw.text((rect[0], max(0, rect[1] - 17)), box["shortId"], fill=(255, 0, 0, 255))
    draw.rectangle((0, 0, out_w, 36), fill=(0, 0, 0, 170))
    draw.text(
        (8, 10),
        f"{scenario['scenarioId']} {mode} alpha={alpha:.2f} dx={scenario['dx']} dy={scenario['dy']}",
        fill=(255, 255, 255, 255),
    )
    path = OUT / f"{scenario['scenarioId']}_{mode}_{alpha:.2f}.jpg"
    preview.save(path, quality=90)
    return path


def draw_sheet(preview_paths: list[Path], rows: list[dict[str, Any]]) -> None:
    sheet = Image.new("RGB", (1840, 1220), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 14)
        tiny = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()
    draw.rectangle((0, 0, 1840, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Held-To-Light Opacity/Color Transfer Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Current scan only: readable/upright page 76 blended with mirrored back pages; active boxes outlined.",
        fill=(235, 235, 235),
        font=small,
    )
    x, y = 24, 120
    for path in preview_paths[:8]:
        img = Image.open(path).convert("RGB").resize((360, 462))
        sheet.paste(img, (x, y))
        x += 378
        if x + 360 > 1840:
            x = 24
            y += 520
    y = 1065
    headers = ["scenario", "mode", "alpha", "minDark", "meanDark", "states", "binaryCov"]
    xs = [24, 330, 440, 520, 620, 720, 840]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    for row in sorted(rows, key=lambda r: r["minActiveDarkeningDelta"], reverse=True)[:6]:
        vals = [
            row["scenarioId"],
            row["blendMode"],
            f"{row['alpha']:.2f}",
            f"{row['minActiveDarkeningDelta']:.2f}",
            f"{row['meanActiveDarkeningDelta']:.2f}",
            row["blendStateStream"],
            f"{row['binaryActiveOverTarget']:.3f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    held = load_json(HELD_TO_LIGHT_SIMULATOR)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    active_boxes = [
        {
            "shortId": row["shortId"],
            "phrase": row["phrase"],
            "visualState": row["visualState"],
            "box": row["box"],
        }
        for row in active_index.get("activeRows", [])
    ]
    scenarios = scenario_rows(held)
    page_cache = {page: normalize_page(page) for page in {75, 76, 78, 79}}
    target_page = page_cache[76]
    target_arr = np.asarray(target_page.convert("RGB"))

    rows: list[dict[str, Any]] = []
    box_rows: list[dict[str, Any]] = []
    preview_paths: list[Path] = []
    for scenario in scenarios:
        source_img = shifted_mirrored_source(
            page_cache[scenario["sourcePage"]], scenario["dx"], scenario["dy"]
        )
        source_arr = np.asarray(source_img.convert("RGB"))
        for mode in BLEND_MODES:
            for alpha in ALPHAS:
                blend_arr = blend_arrays(target_arr, source_arr, mode, alpha)
                metrics = [box_metrics(target_arr, blend_arr, box) for box in active_boxes]
                for metric in metrics:
                    box_rows.append({**scenario, "blendMode": mode, "alpha": alpha, **metric})
                darkening = [metric["darkeningDelta"] for metric in metrics]
                abs_delta = [metric["absoluteRgbDelta"] for metric in metrics]
                blend_states = "".join(metric["blendState"] for metric in metrics)
                expected_states = "".join(box["visualState"] for box in active_boxes)
                row = {
                    **scenario,
                    "blendMode": mode,
                    "alpha": alpha,
                    "minActiveDarkeningDelta": round(float(min(darkening)), 6),
                    "meanActiveDarkeningDelta": round(float(np.mean(darkening)), 6),
                    "minActiveAbsRgbDelta": round(float(min(abs_delta)), 6),
                    "meanActiveAbsRgbDelta": round(float(np.mean(abs_delta)), 6),
                    "blendStateStream": blend_states,
                    "expectedStateStream": expected_states,
                    "stateStreamMatchesExpected": blend_states == expected_states,
                }
                rows.append(row)
                if mode in {"darken", "multiply"} and alpha in {0.5, 0.75}:
                    path = save_preview(
                        Image.fromarray(blend_arr),
                        scenario,
                        mode,
                        alpha,
                        active_boxes,
                    )
                    preview_paths.append(path)

    natural_rows = [row for row in rows if row["scenarioId"] == "valid_75_to_76_natural"]
    forced_or_control_rows = [
        row for row in rows if row["scenarioId"] != "valid_75_to_76_natural"
    ]
    best_row = max(rows, key=lambda row: row["minActiveDarkeningDelta"])
    best_natural = max(natural_rows, key=lambda row: row["minActiveDarkeningDelta"])
    best_forced_or_control = max(
        forced_or_control_rows, key=lambda row: row["minActiveDarkeningDelta"]
    )
    threshold_counts = {
        f"naturalAllFourDelta{int(threshold)}Count": sum(
            1 for row in natural_rows if row["minActiveDarkeningDelta"] >= threshold
        )
        for threshold in DELTA_THRESHOLDS
    }
    threshold_counts.update(
        {
            f"forcedOrControlAllFourDelta{int(threshold)}Count": sum(
                1
                for row in forced_or_control_rows
                if row["minActiveDarkeningDelta"] >= threshold
            )
            for threshold in DELTA_THRESHOLDS
        }
    )
    expected_state_match_count = sum(1 for row in rows if row["stateStreamMatchesExpected"])
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    fingerprint = (
        f"scenarios={len(scenarios)}|blendRows={len(rows)}|boxRows={len(box_rows)}"
        f"|naturalBest={best_natural['minActiveDarkeningDelta']:.2f}:"
        f"{best_natural['blendMode']}@{best_natural['alpha']:.2f}"
        f"|controlBest={best_forced_or_control['minActiveDarkeningDelta']:.2f}:"
        f"{best_forced_or_control['scenarioId']}:{best_forced_or_control['blendMode']}@"
        f"{best_forced_or_control['alpha']:.2f}"
        f"|all16={threshold_counts['naturalAllFourDelta16Count']}/"
        f"{threshold_counts['forcedOrControlAllFourDelta16Count']}"
        f"|stateMatches={expected_state_match_count}/{len(rows)}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "scenarioCount": len(scenarios),
        "blendRowCount": len(rows),
        "activeBoxBlendRowCount": len(box_rows),
        "bestScenarioId": best_row["scenarioId"],
        "bestBlendMode": best_row["blendMode"],
        "bestAlpha": best_row["alpha"],
        "bestMinActiveDarkeningDelta": best_row["minActiveDarkeningDelta"],
        "bestNaturalMinActiveDarkeningDelta": best_natural["minActiveDarkeningDelta"],
        "bestNaturalBlend": f"{best_natural['blendMode']}@{best_natural['alpha']:.2f}",
        "bestForcedOrControlMinActiveDarkeningDelta": best_forced_or_control[
            "minActiveDarkeningDelta"
        ],
        "bestForcedOrControlScenario": best_forced_or_control["scenarioId"],
        "bestForcedOrControlBlend": (
            f"{best_forced_or_control['blendMode']}@{best_forced_or_control['alpha']:.2f}"
        ),
        **threshold_counts,
        "expectedStateStreamMatchCount": expected_state_match_count,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "heldToLightOpacityFingerprint": fingerprint,
    }

    draw_sheet(preview_paths, rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current scan/PDF held-to-light opacity and color-transfer gate; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "heldToLightSimulator": rel(HELD_TO_LIGHT_SIMULATOR),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "scenarios": scenarios,
        "blendRows": rows,
        "activeBoxBlendRows": box_rows,
        "summary": summary,
        "decision": {
            "currentScanHeldToLightOpacityGate": "opacity_color_transfer_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Opacity/blend mechanics require arbitrary mode and alpha choices, and the "
                "physically valid natural 75->76 view is not uniquely stronger than forced or "
                "non-physical page-76 controls. The active Y/K state stream is visual validation "
                "only and still lacks source-backed unit/order wording."
            ),
            "nextMove": (
                "Keep held-to-light outputs as visual source-review panels. The best next move "
                "remains distinct physical/original-layout source validation or raw clue wording "
                "that names the extraction unit, order, or transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Held-To-Light Opacity Gate",
        "",
        "Scope: tested opacity and color-transfer blends using the current PDF/source images in readable/upright orientation. Page 76 was blended with mirrored back pages under average, darken, and multiply modes at three opacity levels. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Scenarios / blend rows / active-box rows: `{len(scenarios)}` / `{len(rows)}` / `{len(box_rows)}`",
        f"- Best natural 75->76 all-box darkening: `{best_natural['minActiveDarkeningDelta']:.2f}` via `{best_natural['blendMode']}@{best_natural['alpha']:.2f}`",
        f"- Best forced/control all-box darkening: `{best_forced_or_control['minActiveDarkeningDelta']:.2f}` via `{best_forced_or_control['scenarioId']}` / `{best_forced_or_control['blendMode']}@{best_forced_or_control['alpha']:.2f}`",
        f"- Natural all-four delta>=16 rows / forced-or-control all-four delta>=16 rows: `{threshold_counts['naturalAllFourDelta16Count']}` / `{threshold_counts['forcedOrControlAllFourDelta16Count']}`",
        f"- Expected Y/K state-stream matches: `{expected_state_match_count}` / `{len(rows)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Blend Rows",
        "",
        "| scenario | mode | alpha | min darkening | mean darkening | min RGB delta | states | binary active coverage |",
        "|---|---|---:|---:|---:|---:|---|---:|",
    ]
    for row in sorted(rows, key=lambda item: item["minActiveDarkeningDelta"], reverse=True):
        lines.append(
            f"| `{row['scenarioId']}` | `{row['blendMode']}` | {row['alpha']:.2f} | {row['minActiveDarkeningDelta']:.2f} | {row['meanActiveDarkeningDelta']:.2f} | {row['minActiveAbsRgbDelta']:.2f} | `{row['blendStateStream']}` | {row['binaryActiveOverTarget']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `opacity_color_transfer_no_selector`",
            "- The physically valid natural 75->76 view does not become a unique active-quartet selector under opacity/color transfer.",
            "- Stronger all-box darkening requires arbitrary blend/opacity choices and is matched or exceeded by forced/non-physical page-76 controls.",
            "- The active visual state remains useful as source-validation evidence, but it does not supply the missing R3 unit/order/transform.",
            "",
            "## Next Move",
            "",
            "- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanHeldToLightOpacityGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()

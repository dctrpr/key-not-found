#!/usr/bin/env python3
"""Test two-lane affine registration for current-scan held-to-light.

The prior header/footer lane pass tested lane translations. This bounded follow-up
tests whether a simple two-anchor lane affine transform (translation plus x/y
scale) can rescue mirrored page-75 source ink into O4/B4/G5/O5 on page 76.

No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address
checks, BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_lane_affine_registration_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_lane_affine_registration_gate.json"
OUT_MD = OUT / "current_scan_lane_affine_registration_gate.md"
OUT_SHEET = OUT / "current_scan_lane_affine_registration_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

TARGET_PAGE = 76
VALID_SOURCE_PAGE = 75
INVALID_SOURCE_PAGES = [77, 78, 79, 80]
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
LANES = {
    "top_header_lane": (0.00, 0.18),
    "footer_lane": (0.84, 1.00),
    "lower_body_lane": (0.50, 0.90),
}
ANCHOR_PAIRS = [
    ("top_header_lane", "footer_lane"),
    ("top_header_lane", "lower_body_lane"),
    ("lower_body_lane", "footer_lane"),
]
MIN_ANCHOR_PIXELS = 1000
SOURCE_SUPPORT_THRESHOLD = 0.10


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


def normalize_page(page: int) -> Image.Image:
    source_path = Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))
    upright_path = Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))
    if source_path.exists() and upright_path.exists():
        source = Image.open(source_path).convert("RGB")
        upright = Image.open(upright_path).convert("RGB")
        sample_size = (318, 408)
        source_sample = source.resize(sample_size)
        upright_sample = upright.resize(sample_size)
        same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
        rot_diff = sum(
            ImageStat.Stat(
                ImageChops.difference(source_sample.rotate(180), upright_sample)
            ).mean
        )
        return source.rotate(180) if rot_diff < same_diff else source
    return Image.open(upright_path).convert("RGB")


def signal_mask(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.convert("RGB"), dtype=np.int16)
    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    dark = luma < 145
    orange = (r > 135) & (g > 55) & (g < 190) & (b < 145) & ((r - b) > 45)
    return dark | orange


def active_boxes(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in active_index.get("activeRows", []):
        if row.get("shortId") in TARGET_ORDER:
            rows.append(
                {
                    "shortId": row["shortId"],
                    "phrase": row.get("phrase", row.get("label", "")),
                    "box": [float(v) for v in row["box"]],
                }
            )
    rows.sort(key=lambda item: TARGET_ORDER.index(item["shortId"]))
    return rows


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    arr = sorted(values)
    if len(arr) == 1:
        return arr[0]
    pos = (len(arr) - 1) * pct / 100.0
    lo = int(np.floor(pos))
    hi = int(np.ceil(pos))
    if lo == hi:
        return arr[lo]
    return arr[lo] * (hi - pos) + arr[hi] * (pos - lo)


def anchor_for(mask: np.ndarray, lane: tuple[float, float]) -> dict[str, Any]:
    h, _w = mask.shape
    y0 = int(round(h * lane[0]))
    y1 = int(round(h * lane[1]))
    band = mask[y0:y1, :]
    ys, xs = np.nonzero(band)
    if len(xs) < MIN_ANCHOR_PIXELS:
        return {"ok": False, "pixels": int(len(xs)), "center": None, "box": None, "width": 0, "height": 0}
    x_min = int(xs.min())
    x_max = int(xs.max())
    y_min = int(ys.min() + y0)
    y_max = int(ys.max() + y0)
    return {
        "ok": True,
        "pixels": int(len(xs)),
        "center": [round(float(xs.mean()), 3), round(float(ys.mean() + y0), 3)],
        "box": [x_min, y_min, x_max + 1, y_max + 1],
        "width": int(x_max - x_min + 1),
        "height": int(y_max - y_min + 1),
    }


def build_transforms(target_anchors: dict[str, Any], source_anchors: dict[str, Any]) -> dict[str, dict[str, float]]:
    transforms: dict[str, dict[str, float]] = {
        "natural_hflip": {"sx": 1.0, "sy": 1.0, "tx": 0.0, "ty": 0.0}
    }
    for first, second in ANCHOR_PAIRS:
        ta = target_anchors[first]
        tb = target_anchors[second]
        sa = source_anchors[first]
        sb = source_anchors[second]
        if not (ta["ok"] and tb["ok"] and sa["ok"] and sb["ok"]):
            continue
        source_dy = float(sb["center"][1]) - float(sa["center"][1])
        target_dy = float(tb["center"][1]) - float(ta["center"][1])
        if abs(source_dy) < 1.0:
            continue
        sy = target_dy / source_dy
        sx_values = [
            float(ta["width"]) / float(sa["width"]) if sa["width"] else 1.0,
            float(tb["width"]) / float(sb["width"]) if sb["width"] else 1.0,
        ]
        sx = float(mean(sx_values))
        if not (0.80 <= sx <= 1.25 and 0.80 <= sy <= 1.25):
            continue
        tx = float(ta["center"][0]) - sx * float(sa["center"][0])
        ty = float(ta["center"][1]) - sy * float(sa["center"][1])
        transforms[f"{first}+{second}_affine"] = {
            "sx": round(sx, 6),
            "sy": round(sy, 6),
            "tx": round(tx, 3),
            "ty": round(ty, 3),
        }
    return transforms


def transformed_fraction(mask: np.ndarray, box: list[float], transform: dict[str, float]) -> float:
    h, w = mask.shape
    sx = float(transform["sx"])
    sy = float(transform["sy"])
    tx = float(transform["tx"])
    ty = float(transform["ty"])
    x0, y0, x1, y1 = box
    sx0 = max(0, min(w, int(np.floor((x0 - tx) / sx))))
    sx1 = max(0, min(w, int(np.ceil((x1 - tx) / sx))))
    sy0 = max(0, min(h, int(np.floor((y0 - ty) / sy))))
    sy1 = max(0, min(h, int(np.ceil((y1 - ty) / sy))))
    area = max(1.0, (x1 - x0) * (y1 - y0))
    if sx1 <= sx0 or sy1 <= sy0:
        return 0.0
    return float(mask[sy0:sy1, sx0:sx1].sum()) / area


def transformed_mask_image(mask: np.ndarray, transform: dict[str, float]) -> Image.Image:
    h, w = mask.shape
    src = Image.fromarray((mask.astype(np.uint8) * 255), "L")
    sx = float(transform["sx"])
    sy = float(transform["sy"])
    tx = float(transform["tx"])
    ty = float(transform["ty"])
    # PIL maps output pixels back to input coordinates.
    return src.transform(
        (w, h),
        Image.Transform.AFFINE,
        (1.0 / sx, 0.0, -tx / sx, 0.0, 1.0 / sy, -ty / sy),
        resample=Image.Resampling.NEAREST,
        fillcolor=0,
    )


def envelope_box(rows: list[dict[str, Any]], pad: int, width: int, height: int) -> tuple[int, int, int, int]:
    x0 = max(0, int(min(row["box"][0] for row in rows) - pad))
    y0 = max(0, int(min(row["box"][1] for row in rows) - pad))
    x1 = min(width, int(max(row["box"][2] for row in rows) + pad))
    y1 = min(height, int(max(row["box"][3] for row in rows) + pad))
    return x0, y0, x1, y1


def build_sheet(target: Image.Image, valid_mask: np.ndarray, valid_rows: list[dict[str, Any]], boxes: list[dict[str, Any]]) -> None:
    w, h = target.size
    crop = envelope_box(boxes, 90, w, h)
    tile_w = crop[2] - crop[0]
    tile_h = crop[3] - crop[1] + 102
    shown = valid_rows[:4]
    sheet = Image.new("RGB", (tile_w * len(shown), tile_h), "white")
    draw = ImageDraw.Draw(sheet)
    title_font = font(20)
    small_font = font(15)
    for col, row in enumerate(shown):
        tile = target.copy().convert("RGBA")
        shifted = transformed_mask_image(valid_mask, row["transform"])
        red = Image.new("RGBA", target.size, (255, 0, 0, 0))
        red.putalpha(shifted.point(lambda v: 82 if v else 0))
        tile = Image.alpha_composite(tile, red)
        td = ImageDraw.Draw(tile)
        for box_row in boxes:
            box = box_row["box"]
            td.rectangle(box, outline=(0, 180, 255, 255), width=4)
            td.text((box[0], max(0, box[1] - 22)), box_row["shortId"], fill=(0, 120, 255, 255), font=small_font)
        x = col * tile_w
        sheet.paste(tile.convert("RGB").crop(crop), (x, 102))
        draw.text((x + 10, 8), row["mode"][:54], fill="black", font=title_font)
        draw.text(
            (x + 10, 38),
            f"sx/sy {row['transform']['sx']:.4f},{row['transform']['sy']:.4f} tx/ty {row['transform']['tx']:.1f},{row['transform']['ty']:.1f}",
            fill="black",
            font=small_font,
        )
        draw.text(
            (x + 10, 62),
            f"supported {row['supportedCount']}/4 aboveP95 {row['aboveP95Count']}/4 mean {row['meanFraction']:.4f}",
            fill="black",
            font=small_font,
        )
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    boxes = active_boxes(active_index)
    target = normalize_page(TARGET_PAGE)
    pages = {page: normalize_page(page) for page in [TARGET_PAGE, VALID_SOURCE_PAGE, *INVALID_SOURCE_PAGES]}
    target_mask = signal_mask(target)
    source_masks = {page: signal_mask(ImageOps.mirror(pages[page])) for page in [VALID_SOURCE_PAGE, *INVALID_SOURCE_PAGES]}

    target_anchors = {name: anchor_for(target_mask, lane) for name, lane in LANES.items()}
    source_anchors = {
        page: {name: anchor_for(source_masks[page], lane) for name, lane in LANES.items()}
        for page in [VALID_SOURCE_PAGE, *INVALID_SOURCE_PAGES]
    }
    transforms = {
        page: build_transforms(target_anchors, source_anchors[page])
        for page in [VALID_SOURCE_PAGE, *INVALID_SOURCE_PAGES]
    }

    raw_rows: list[dict[str, Any]] = []
    for page, page_transforms in transforms.items():
        for mode, transform in page_transforms.items():
            target_fractions = {
                box["shortId"]: transformed_fraction(source_masks[page], box["box"], transform)
                for box in boxes
            }
            raw_rows.append(
                {
                    "sourcePage": page,
                    "sourceClass": "valid_same_leaf" if page == VALID_SOURCE_PAGE else "invalid_control",
                    "mode": mode,
                    "transform": transform,
                    "fractions": {key: round(value, 6) for key, value in target_fractions.items()},
                    "meanFraction": round(mean(target_fractions.values()), 6),
                    "supportedCount": sum(value >= SOURCE_SUPPORT_THRESHOLD for value in target_fractions.values()),
                }
            )

    modes = sorted({row["mode"] for row in raw_rows})
    control_p95: dict[str, dict[str, float]] = {}
    for mode in modes:
        control_p95[mode] = {}
        for target_id in TARGET_ORDER:
            values = [
                row["fractions"][target_id]
                for row in raw_rows
                if row["mode"] == mode and row["sourceClass"] == "invalid_control"
            ]
            control_p95[mode][target_id] = round(percentile(values, 95), 6)

    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        p95 = control_p95.get(row["mode"], {})
        above = {
            target_id: row["fractions"][target_id] > p95.get(target_id, 0.0)
            for target_id in TARGET_ORDER
        }
        rows.append({**row, "aboveP95": above, "aboveP95Count": sum(above.values())})

    valid_rows = [row for row in rows if row["sourcePage"] == VALID_SOURCE_PAGE]
    control_rows = [row for row in rows if row["sourceClass"] == "invalid_control"]
    best_valid = max(valid_rows, key=lambda row: (row["supportedCount"], row["aboveP95Count"], row["meanFraction"]))
    max_control_supported = max((row["supportedCount"] for row in control_rows), default=0)
    max_control_above_p95 = max((row["aboveP95Count"] for row in control_rows), default=0)
    all_four_valid_modes = [
        row["mode"] for row in valid_rows if row["supportedCount"] == 4 and row["aboveP95Count"] == 4
    ]
    affine_candidate = int(bool(all_four_valid_modes))
    source_r3 = 0
    satisfied = int(reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0) or 0)
    trigger_count = int(reopen.get("summary", {}).get("triggerCount", 9) or 9)
    selectors = int(affine_candidate and source_r3 > 0)

    build_sheet(target, source_masks[VALID_SOURCE_PAGE], valid_rows, boxes)

    summary = {
        "targetPage": TARGET_PAGE,
        "validSourcePage": VALID_SOURCE_PAGE,
        "invalidSourcePages": INVALID_SOURCE_PAGES,
        "validRows": len(valid_rows),
        "controlRows": len(control_rows),
        "modesChecked": modes,
        "bestValidMode": best_valid["mode"],
        "bestValidTransform": best_valid["transform"],
        "bestValidSupportedCount": best_valid["supportedCount"],
        "bestValidAboveP95Count": best_valid["aboveP95Count"],
        "bestValidMeanFraction": best_valid["meanFraction"],
        "maxControlSupportedCount": max_control_supported,
        "maxControlAboveP95Count": max_control_above_p95,
        "allFourValidModes": all_four_valid_modes,
        "affineRegistrationCandidate": affine_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorCandidateCount": selectors,
    }
    fingerprint = (
        f"valid={summary['validRows']}|controls={summary['controlRows']}|"
        f"modes={len(summary['modesChecked'])}|best={summary['bestValidMode']}|"
        f"bestSupport={summary['bestValidSupportedCount']}/4|"
        f"bestAboveP95={summary['bestValidAboveP95Count']}/4|"
        f"bestMean={summary['bestValidMeanFraction']:.6f}|"
        f"controlMax={summary['maxControlSupportedCount']}|"
        f"controlAboveMax={summary['maxControlAboveP95Count']}|"
        f"allFour={len(all_four_valid_modes)}|sourceR3={source_r3}|"
        f"triggers={satisfied}/{trigger_count}|selectors={selectors}"
    )

    out = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "two-lane affine held-to-light registration check; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePages": [rel(Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))) for page in [VALID_SOURCE_PAGE, *INVALID_SOURCE_PAGES]],
            "targetPage": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=TARGET_PAGE))),
        },
        "targetAnchors": target_anchors,
        "sourceAnchors": source_anchors,
        "rows": rows,
        "controlP95": control_p95,
        "summary": summary,
        "decision": {
            "status": "current_scan_lane_affine_registration_no_selector",
            "reason": (
                "Two-anchor article-lane affine transforms do not make valid mirrored "
                "page-75 source ink support all four active page-76 targets above "
                "invalid source-page controls."
            ),
            "nextMove": (
                "Keep current-scan held-to-light registration closed; require a distinct "
                "physical/original-layout source or raw clue wording that supplies unit, "
                "order, and transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Current Scan Lane Affine Registration Gate",
        "",
        "Scope: tested whether two-anchor article-lane affine registration (translation plus x/y scale) improves mirrored page-75 held-to-light support for O4/B4/G5/O5 on page 76. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{out['createdAt']}`",
        f"- Valid source page / target page: `{VALID_SOURCE_PAGE}` -> `{TARGET_PAGE}`",
        f"- Invalid source controls: `{INVALID_SOURCE_PAGES}`",
        f"- Valid affine rows / control rows: `{summary['validRows']}` / `{summary['controlRows']}`",
        f"- Best valid mode: `{summary['bestValidMode']}`",
        f"- Best valid transform: `{summary['bestValidTransform']}`",
        f"- Best valid supported / above-control-p95 count: `{summary['bestValidSupportedCount']}/4` / `{summary['bestValidAboveP95Count']}/4`",
        f"- Max control supported / above-control-p95 count: `{summary['maxControlSupportedCount']}/4` / `{summary['maxControlAboveP95Count']}/4`",
        f"- All-four valid affine modes: `{summary['allFourValidModes']}`",
        f"- Affine registration candidate / selectors: `{summary['affineRegistrationCandidate']}` / `{summary['selectorCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Valid Page-75 -> Page-76 Rows",
        "",
        "| mode | sx | sy | tx | ty | mean fraction | O4 | B4 | G5 | O5 | supported | above p95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in valid_rows:
        f = row["fractions"]
        t = row["transform"]
        lines.append(
            f"| `{row['mode']}` | `{t['sx']}` | `{t['sy']}` | `{t['tx']}` | `{t['ty']}` | `{row['meanFraction']}` | "
            f"`{f['O4']}` | `{f['B4']}` | `{f['G5']}` | `{f['O5']}` | "
            f"`{row['supportedCount']}/4` | `{row['aboveP95Count']}/4` |"
        )
    lines.extend(
        [
            "",
            "## Control P95 By Mode",
            "",
            "| mode | O4 p95 | B4 p95 | G5 p95 | O5 p95 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for mode in modes:
        p = control_p95[mode]
        lines.append(
            f"| `{mode}` | `{p.get('O4', 0.0)}` | `{p.get('B4', 0.0)}` | `{p.get('G5', 0.0)}` | `{p.get('O5', 0.0)}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{out['decision']['status']}`",
            f"- {out['decision']['reason']}",
            f"- Best valid affine mode is `{summary['bestValidMode']}`, but it supports only `{summary['bestValidSupportedCount']}/4` active boxes and beats invalid controls on only `{summary['bestValidAboveP95Count']}/4` boxes.",
            "- Two-anchor lane scaling therefore does not rescue B4/G5/O5 as a selective physical held-to-light landing.",
            "",
            "## Next Move",
            "",
            f"- {out['decision']['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()

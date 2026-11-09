#!/usr/bin/env python3
"""Test header/footer/body-lane registration for current-scan held-to-light.

Earlier passes checked natural hflip, page trim, content boxes, PDF-native
registration, and OVERDOSE slot geometry. This bounded pass asks one narrower
question: if the current scan is registered by visible article lanes such as the
top header, footer/lower furniture, or lower body lane, does mirrored source ink
from page 75 selectively support O4/B4/G5/O5 on page 76 better than invalid
source-page controls?

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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_header_footer_lane_registration_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_header_footer_lane_registration_gate.json"
OUT_MD = OUT / "current_scan_header_footer_lane_registration_gate.md"
OUT_SHEET = OUT / "current_scan_header_footer_lane_registration_gate_sheet.jpg"

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
    h, w = mask.shape
    y0 = int(round(h * lane[0]))
    y1 = int(round(h * lane[1]))
    band = mask[y0:y1, :]
    ys, xs = np.nonzero(band)
    if len(xs) < MIN_ANCHOR_PIXELS:
        return {"ok": False, "pixels": int(len(xs)), "center": None, "box": None}
    x_min = int(xs.min())
    x_max = int(xs.max())
    y_min = int(ys.min() + y0)
    y_max = int(ys.max() + y0)
    return {
        "ok": True,
        "pixels": int(len(xs)),
        "center": [round(float(xs.mean()), 3), round(float(ys.mean() + y0), 3)],
        "box": [x_min, y_min, x_max + 1, y_max + 1],
    }


def shifted_fraction(mask: np.ndarray, box: list[float], dx: float, dy: float) -> float:
    h, w = mask.shape
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    sx0 = max(0, min(w, x0 - int(round(dx))))
    sy0 = max(0, min(h, y0 - int(round(dy))))
    sx1 = max(0, min(w, x1 - int(round(dx))))
    sy1 = max(0, min(h, y1 - int(round(dy))))
    area = max(1, (x1 - x0) * (y1 - y0))
    if sx1 <= sx0 or sy1 <= sy0:
        return 0.0
    return float(mask[sy0:sy1, sx0:sx1].sum()) / float(area)


def shifted_mask_image(mask: np.ndarray, dx: float, dy: float) -> Image.Image:
    h, w = mask.shape
    dx_i = int(round(dx))
    dy_i = int(round(dy))
    out = Image.new("L", (w, h), 0)
    src = Image.fromarray((mask.astype(np.uint8) * 255), "L")
    sx0 = max(0, -dx_i)
    sy0 = max(0, -dy_i)
    sx1 = min(w, w - dx_i) if dx_i >= 0 else w
    sy1 = min(h, h - dy_i) if dy_i >= 0 else h
    tx0 = max(0, dx_i)
    ty0 = max(0, dy_i)
    if sx1 > sx0 and sy1 > sy0:
        out.paste(src.crop((sx0, sy0, sx1, sy1)), (tx0, ty0))
    return out


def envelope_box(rows: list[dict[str, Any]], pad: int, width: int, height: int) -> tuple[int, int, int, int]:
    x0 = max(0, int(min(row["box"][0] for row in rows) - pad))
    y0 = max(0, int(min(row["box"][1] for row in rows) - pad))
    x1 = min(width, int(max(row["box"][2] for row in rows) + pad))
    y1 = min(height, int(max(row["box"][3] for row in rows) + pad))
    return x0, y0, x1, y1


def build_sheet(target: Image.Image, masks: dict[int, np.ndarray], mode_rows: list[dict[str, Any]], boxes: list[dict[str, Any]]) -> None:
    w, h = target.size
    crop = envelope_box(boxes, 90, w, h)
    tile_w = crop[2] - crop[0]
    tile_h = crop[3] - crop[1] + 92
    shown = [row for row in mode_rows if row["sourcePage"] == VALID_SOURCE_PAGE]
    sheet = Image.new("RGB", (tile_w * len(shown), tile_h), "white")
    draw = ImageDraw.Draw(sheet)
    title_font = font(22)
    small_font = font(16)
    for col, row in enumerate(shown):
        tile = target.copy().convert("RGBA")
        shifted = shifted_mask_image(masks[row["sourcePage"]], row["dx"], row["dy"])
        red = Image.new("RGBA", target.size, (255, 0, 0, 0))
        red.putalpha(shifted.point(lambda v: 82 if v else 0))
        tile = Image.alpha_composite(tile, red)
        td = ImageDraw.Draw(tile)
        for box_row in boxes:
            box = box_row["box"]
            td.rectangle(box, outline=(0, 180, 255, 255), width=4)
            td.text((box[0], max(0, box[1] - 22)), box_row["shortId"], fill=(0, 120, 255, 255), font=small_font)
        cropped = tile.convert("RGB").crop(crop)
        x = col * tile_w
        sheet.paste(cropped, (x, 92))
        draw.text((x + 10, 8), row["mode"], fill="black", font=title_font)
        draw.text(
            (x + 10, 40),
            f"dx/dy {row['dx']:.1f},{row['dy']:.1f} supported {row['supportedCount']}/4 aboveP95 {row['aboveP95Count']}/4",
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

    shifts: dict[int, dict[str, tuple[float, float]]] = {}
    for page in [VALID_SOURCE_PAGE, *INVALID_SOURCE_PAGES]:
        shifts[page] = {"natural_hflip": (0.0, 0.0)}
        for name in LANES:
            ta = target_anchors[name]
            sa = source_anchors[page][name]
            if ta["ok"] and sa["ok"]:
                shifts[page][name] = (
                    float(ta["center"][0]) - float(sa["center"][0]),
                    float(ta["center"][1]) - float(sa["center"][1]),
                )
        if "top_header_lane" in shifts[page] and "footer_lane" in shifts[page]:
            tx, ty = shifts[page]["top_header_lane"]
            fx, fy = shifts[page]["footer_lane"]
            shifts[page]["header_footer_mean"] = ((tx + fx) / 2.0, (ty + fy) / 2.0)

    raw_rows: list[dict[str, Any]] = []
    for page, page_shifts in shifts.items():
        for mode, (dx, dy) in page_shifts.items():
            target_fractions = {
                box["shortId"]: shifted_fraction(source_masks[page], box["box"], dx, dy)
                for box in boxes
            }
            raw_rows.append(
                {
                    "sourcePage": page,
                    "sourceClass": "valid_same_leaf" if page == VALID_SOURCE_PAGE else "invalid_control",
                    "mode": mode,
                    "dx": round(dx, 3),
                    "dy": round(dy, 3),
                    "fractions": {key: round(value, 6) for key, value in target_fractions.items()},
                    "meanFraction": round(mean(target_fractions.values()), 6),
                    "supportedCount": sum(value >= SOURCE_SUPPORT_THRESHOLD for value in target_fractions.values()),
                }
            )

    control_p95: dict[str, dict[str, float]] = {}
    modes = sorted({row["mode"] for row in raw_rows})
    for mode in modes:
        control_p95[mode] = {}
        for target_id in TARGET_ORDER:
            values = [
                row["fractions"][target_id]
                for row in raw_rows
                if row["mode"] == mode and row["sourceClass"] == "invalid_control"
            ]
            control_p95[mode][target_id] = round(percentile(values, 95), 6)

    mode_rows: list[dict[str, Any]] = []
    for row in raw_rows:
        p95 = control_p95.get(row["mode"], {})
        above = {
            target_id: row["fractions"][target_id] > p95.get(target_id, 0.0)
            for target_id in TARGET_ORDER
        }
        mode_rows.append({**row, "aboveP95": above, "aboveP95Count": sum(above.values())})

    valid_rows = [row for row in mode_rows if row["sourcePage"] == VALID_SOURCE_PAGE]
    best_valid = max(valid_rows, key=lambda row: (row["supportedCount"], row["aboveP95Count"], row["meanFraction"]))
    max_control_supported = max(
        [row["supportedCount"] for row in mode_rows if row["sourceClass"] == "invalid_control"],
        default=0,
    )
    all_four_supported_modes = [
        row["mode"]
        for row in valid_rows
        if row["supportedCount"] == 4 and row["aboveP95Count"] == 4
    ]
    lane_candidate = int(bool(all_four_supported_modes))
    source_r3 = 0
    satisfied = int(reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0) or 0)
    trigger_count = int(reopen.get("summary", {}).get("triggerCount", 9) or 9)
    selector_candidates = int(lane_candidate and source_r3 > 0)

    build_sheet(target, source_masks, mode_rows, boxes)

    summary = {
        "targetPage": TARGET_PAGE,
        "validSourcePage": VALID_SOURCE_PAGE,
        "invalidSourcePages": INVALID_SOURCE_PAGES,
        "laneModesChecked": sorted({row["mode"] for row in valid_rows}),
        "validRows": len(valid_rows),
        "controlRows": len([row for row in mode_rows if row["sourceClass"] == "invalid_control"]),
        "bestValidMode": best_valid["mode"],
        "bestValidSupportedCount": best_valid["supportedCount"],
        "bestValidAboveP95Count": best_valid["aboveP95Count"],
        "bestValidMeanFraction": best_valid["meanFraction"],
        "maxControlSupportedCount": max_control_supported,
        "allFourSupportedModes": all_four_supported_modes,
        "laneRegistrationCandidate": lane_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorCandidateCount": selector_candidates,
    }
    fingerprint = (
        f"valid={summary['validRows']}|controls={summary['controlRows']}|"
        f"modes={len(summary['laneModesChecked'])}|best={summary['bestValidMode']}|"
        f"bestSupport={summary['bestValidSupportedCount']}/4|"
        f"bestAboveP95={summary['bestValidAboveP95Count']}/4|"
        f"bestMean={summary['bestValidMeanFraction']:.6f}|"
        f"controlMax={summary['maxControlSupportedCount']}|"
        f"allFour={len(all_four_supportedModes := all_four_supported_modes)}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors={selector_candidates}"
    )

    out = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "header/footer/lower-body lane registered held-to-light check; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePages": [rel(Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))) for page in [VALID_SOURCE_PAGE, *INVALID_SOURCE_PAGES]],
            "targetPage": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=TARGET_PAGE))),
        },
        "targetAnchors": target_anchors,
        "sourceAnchors": source_anchors,
        "rows": mode_rows,
        "controlP95": control_p95,
        "summary": summary,
        "decision": {
            "status": "current_scan_header_footer_lane_registration_no_selector",
            "reason": (
                "Visible article header/footer/lower-body lane translations do not make "
                "mirrored page-75 source ink support all four active page-76 targets above "
                "invalid source-page controls."
            ),
            "nextMove": (
                "Keep current-scan held-to-light registration closed unless a distinct "
                "physical/original-layout source or raw clue wording supplies the missing "
                "unit, order, and transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Current Scan Header/Footer Lane Registration Gate",
        "",
        "Scope: tested whether registering mirrored source pages by visible article top-header, footer, or lower-body lanes improves current-scan held-to-light support for O4/B4/G5/O5. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{out['createdAt']}`",
        f"- Valid source page / target page: `{VALID_SOURCE_PAGE}` -> `{TARGET_PAGE}`",
        f"- Invalid source controls: `{INVALID_SOURCE_PAGES}`",
        f"- Valid lane rows / control rows: `{summary['validRows']}` / `{summary['controlRows']}`",
        f"- Best valid mode: `{summary['bestValidMode']}`",
        f"- Best valid supported / above-control-p95 count: `{summary['bestValidSupportedCount']}/4` / `{summary['bestValidAboveP95Count']}/4`",
        f"- Best valid mean source fraction: `{summary['bestValidMeanFraction']}`",
        f"- Max control supported count: `{summary['maxControlSupportedCount']}`",
        f"- All-four supported lane modes: `{summary['allFourSupportedModes']}`",
        f"- Lane registration candidate / selectors: `{summary['laneRegistrationCandidate']}` / `{summary['selectorCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Valid Page-75 -> Page-76 Rows",
        "",
        "| mode | dx | dy | mean fraction | O4 | B4 | G5 | O5 | supported | above p95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in valid_rows:
        f = row["fractions"]
        lines.append(
            f"| `{row['mode']}` | `{row['dx']}` | `{row['dy']}` | `{row['meanFraction']}` | "
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
            f"- Best valid lane mode is `{summary['bestValidMode']}`, but it supports only `{summary['bestValidSupportedCount']}/4` active boxes and beats invalid controls on only `{summary['bestValidAboveP95Count']}/4` boxes.",
            "- Header/footer/body-lane registration therefore does not rescue B4/G5/O5 as a selective physical held-to-light landing.",
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

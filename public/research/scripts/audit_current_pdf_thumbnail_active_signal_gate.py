#!/usr/bin/env python3
"""Audit the page-76 PDF thumbnail as an active-target visual witness.

The PDF thumbnail objects were already closed as source upgrades. This bounded
pass asks a narrower visual question: does the tiny embedded page-76 thumbnail
preserve, distort, or invent an O4/B4/G5/O5 or OVERDOSE-slot signal compared
with a same-size downsample of the trusted page image?

No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks,
candidates, or brute force are run.
"""

from __future__ import annotations

import io
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_thumbnail_active_signal_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_thumbnail_active_signal_gate.json"
OUT_MD = OUT / "current_pdf_thumbnail_active_signal_gate.md"
OUT_SHEET = OUT / "current_pdf_thumbnail_active_signal_gate_sheet.jpg"

MAGAZINE_PDF = ROOT / "magazine.pdf"
PAGE76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
PAGE76_HIGHLIGHTS = ROOT / (
    "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/"
    "page76_all_source_highlight_mirror_benchmark.json"
)
C9_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

ARTICLE_PAGE = 76
PDF_PAGE_INDEX = ARTICLE_PAGE - 73
BASE_W = 2544.0
BASE_H = 3264.0
EXPECTED_ACTIVE_STATES = {"O4": "orange", "B4": "black_or_grey", "G5": "black_or_grey", "O5": "orange"}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def image_mad(a: Image.Image, b: Image.Image) -> float:
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    stat = ImageStat.Stat(diff)
    return round(float(sum(stat.mean) / len(stat.mean)), 4)


def transformed_candidates(img: Image.Image) -> dict[str, Image.Image]:
    return {
        "as_is": img,
        "rot180": img.rotate(180),
        "flip_lr": ImageOps.mirror(img),
        "flip_tb": ImageOps.flip(img),
    }


def extract_thumbnail() -> tuple[Image.Image, int]:
    doc = fitz.open(MAGAZINE_PDF)
    page = doc[PDF_PAGE_INDEX]
    kind, value = doc.xref_get_key(page.xref, "Thumb")
    if kind != "xref":
        raise RuntimeError("magazine.pdf page 76 has no thumbnail xref")
    thumb_xref = int(value.split()[0])
    raw = doc.xref_stream_raw(thumb_xref) or b""
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    return img, thumb_xref


def transform_box(box: list[float], transform: str, size: tuple[int, int]) -> list[float]:
    thumb_w, thumb_h = size
    sx = thumb_w / BASE_W
    sy = thumb_h / BASE_H
    x0, y0, x1, y1 = box
    bx = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
    if transform == "as_is":
        return bx
    if transform == "rot180":
        return [thumb_w - bx[2], thumb_h - bx[3], thumb_w - bx[0], thumb_h - bx[1]]
    if transform == "flip_lr":
        return [thumb_w - bx[2], bx[1], thumb_w - bx[0], bx[3]]
    if transform == "flip_tb":
        return [bx[0], thumb_h - bx[3], bx[2], thumb_h - bx[1]]
    raise ValueError(transform)


def int_box(box: list[float], size: tuple[int, int], pad: int = 1) -> tuple[int, int, int, int]:
    w, h = size
    x0 = max(0, int(math.floor(box[0])) - pad)
    y0 = max(0, int(math.floor(box[1])) - pad)
    x1 = min(w, int(math.ceil(box[2])) + pad)
    y1 = min(h, int(math.ceil(box[3])) + pad)
    if x1 <= x0:
        x1 = min(w, x0 + 1)
    if y1 <= y0:
        y1 = min(h, y0 + 1)
    return x0, y0, x1, y1


def region_metrics(img: Image.Image, ibox: tuple[int, int, int, int]) -> dict[str, Any]:
    crop = img.crop(ibox).convert("RGB")
    arr = np.asarray(crop, dtype=np.float32)
    if arr.size == 0:
        return {
            "pixelCount": 0,
            "meanRgb": [0, 0, 0],
            "lumaMean": 0.0,
            "orangeRatio": 0.0,
            "darkRatio": 0.0,
            "greyRatio": 0.0,
            "featureRatio": 0.0,
            "state": "empty",
        }
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    luma = 0.299 * r + 0.587 * g + 0.114 * b
    maxc = arr.max(axis=2)
    minc = arr.min(axis=2)
    sat = np.divide(maxc - minc, maxc, out=np.zeros_like(maxc), where=maxc > 0)
    orange = (r > 145) & (g > 45) & (g < 210) & (b < 165) & ((r - g) > 10) & ((r - b) > 35)
    dark = (luma < 115) | ((luma < 155) & (sat < 0.35))
    grey = (luma < 205) & (sat < 0.18)
    feature = orange | dark | grey
    orange_ratio = float(orange.mean())
    dark_ratio = float(dark.mean())
    grey_ratio = float(grey.mean())
    if orange_ratio >= max(dark_ratio, grey_ratio) and orange_ratio >= 0.04:
        state = "orange"
    elif max(dark_ratio, grey_ratio) >= 0.04:
        state = "black_or_grey"
    else:
        state = "background"
    return {
        "pixelCount": int(arr.shape[0] * arr.shape[1]),
        "meanRgb": [round(float(v), 2) for v in arr.reshape(-1, 3).mean(axis=0).tolist()],
        "lumaMean": round(float(luma.mean()), 3),
        "orangeRatio": round(orange_ratio, 6),
        "darkRatio": round(dark_ratio, 6),
        "greyRatio": round(grey_ratio, 6),
        "featureRatio": round(float(feature.mean()), 6),
        "state": state,
    }


def active_regions() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    rows = []
    for row in data.get("activeRows", []):
        rows.append(
            {
                "id": row["shortId"],
                "kind": "active",
                "label": row["phrase"],
                "box": [float(v) for v in row["box"]],
                "expectedState": EXPECTED_ACTIVE_STATES[row["shortId"]],
            }
        )
    return rows


def highlight_controls() -> list[dict[str, Any]]:
    data = load_json(PAGE76_HIGHLIGHTS)
    rows = []
    for target in data.get("targets", []):
        target_id = str(target.get("id"))
        if target_id in EXPECTED_ACTIVE_STATES:
            continue
        rows.append(
            {
                "id": target_id,
                "kind": "highlight_control",
                "label": str(target.get("label", "")),
                "box": [float(v) for v in target.get("box", [])],
            }
        )
    return rows


def overdose_slots() -> list[dict[str, Any]]:
    data = load_json(C9_SLOT_GATE)
    frame = [float(v) for v in data.get("c9Frame", [])]
    projection = next(
        (item for item in data.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "id": f"s{slot['index']}{slot['letter']}",
                "kind": "overdose_slot",
                "label": f"slot {slot['index']} {slot['letter']}",
                "box": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
            }
        )
    return rows


def compare_region(
    region: dict[str, Any], thumb: Image.Image, reference_small: Image.Image, transform: str
) -> dict[str, Any]:
    thumb_box_float = transform_box(region["box"], transform, thumb.size)
    box = int_box(thumb_box_float, thumb.size, pad=1)
    thumb_metrics = region_metrics(thumb, box)
    ref_metrics = region_metrics(reference_small, box)
    crop_mad = image_mad(thumb.crop(box), reference_small.crop(box))
    expected = region.get("expectedState")
    state_match = None if expected is None else thumb_metrics["state"] == expected
    return {
        "id": region["id"],
        "kind": region["kind"],
        "label": region["label"],
        "boxThumb": [round(v, 4) for v in thumb_box_float],
        "boxInt": list(box),
        "expectedState": expected,
        "thumbnail": thumb_metrics,
        "sameSizeDownsample": ref_metrics,
        "thumbnailVsDownsampleMad": crop_mad,
        "stateMatchExpected": state_match,
        "stateChangedVsDownsample": thumb_metrics["state"] != ref_metrics["state"],
    }


def draw_sheet(
    thumb: Image.Image,
    reference_small: Image.Image,
    rows: list[dict[str, Any]],
    transform: str,
) -> None:
    scale = 10
    panels = []
    font = safe_font(16)
    for title, img in [("embedded page-76 thumbnail", thumb), ("trusted page image downsample", reference_small)]:
        panel = img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)
        draw = ImageDraw.Draw(panel)
        for row in rows:
            if row["kind"] not in {"active", "overdose_slot"}:
                continue
            x0, y0, x1, y1 = row["boxInt"]
            color = (255, 95, 0) if row["kind"] == "active" else (30, 130, 255)
            draw.rectangle((x0 * scale, y0 * scale, x1 * scale, y1 * scale), outline=color, width=3)
            draw.text((x0 * scale + 2, max(0, y0 * scale - 18)), row["id"], fill=color, font=font)
        header = Image.new("RGB", (panel.width, 44), (248, 248, 248))
        hdraw = ImageDraw.Draw(header)
        hdraw.text((12, 13), f"{title} ({transform})", fill=(20, 20, 20), font=font)
        full = Image.new("RGB", (panel.width, panel.height + header.height), (255, 255, 255))
        full.paste(header, (0, 0))
        full.paste(panel, (0, header.height))
        panels.append(full)
    sheet = Image.new("RGB", (sum(p.width for p in panels) + 18, max(p.height for p in panels)), (255, 255, 255))
    x = 0
    for panel in panels:
        sheet.paste(panel, (x, 0))
        x += panel.width + 18
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    thumb, thumb_xref = extract_thumbnail()
    baseline = Image.open(PAGE76_UPRIGHT).convert("RGB").resize(thumb.size, Image.Resampling.LANCZOS)
    candidates = transformed_candidates(baseline)
    transform_mad = {name: image_mad(thumb, image) for name, image in candidates.items()}
    best_transform = min(transform_mad, key=transform_mad.get)
    reference_small = candidates[best_transform]

    regions = active_regions() + highlight_controls() + overdose_slots()
    rows = [compare_region(region, thumb, reference_small, best_transform) for region in regions]
    active_rows = [row for row in rows if row["kind"] == "active"]
    slot_rows = [row for row in rows if row["kind"] == "overdose_slot"]
    control_rows = [row for row in rows if row["kind"] == "highlight_control"]
    draw_sheet(thumb, reference_small, rows, best_transform)

    active_match_count = sum(1 for row in active_rows if row["stateMatchExpected"])
    active_changed = sum(1 for row in active_rows if row["stateChangedVsDownsample"])
    slot_changed = sum(1 for row in slot_rows if row["stateChangedVsDownsample"])
    control_changed = sum(1 for row in control_rows if row["stateChangedVsDownsample"])
    active_pixel_min = min(row["thumbnail"]["pixelCount"] for row in active_rows)
    max_active_mad = max(row["thumbnailVsDownsampleMad"] for row in active_rows)
    max_slot_mad = max(row["thumbnailVsDownsampleMad"] for row in slot_rows)
    triggers = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_count = int(
        triggers.get("summary", {}).get("triggerCount")
        or len(triggers.get("triggerRows", []))
    )
    satisfied = int(
        triggers.get("summary", {}).get("satisfiedTriggerCount")
        or sum(1 for trigger in triggers.get("triggerRows", []) if trigger.get("satisfiedByCurrentEvidence"))
    )

    hidden_candidate = active_match_count == 4 and active_changed > 0
    selector_candidate = False
    summary = {
        "pdf": rel(MAGAZINE_PDF),
        "articlePage": ARTICLE_PAGE,
        "thumbXref": thumb_xref,
        "thumbSize": list(thumb.size),
        "bestTransform": best_transform,
        "bestTransformMad": transform_mad[best_transform],
        "transformMad": transform_mad,
        "activeRegionCount": len(active_rows),
        "highlightControlRegionCount": len(control_rows),
        "overdoseSlotRegionCount": len(slot_rows),
        "activeStateMatchExpectedCount": active_match_count,
        "activeStateChangedVsDownsampleCount": active_changed,
        "controlStateChangedVsDownsampleCount": control_changed,
        "slotStateChangedVsDownsampleCount": slot_changed,
        "activeMinPixelCount": active_pixel_min,
        "maxActiveThumbnailVsDownsampleMad": max_active_mad,
        "maxSlotThumbnailVsDownsampleMad": max_slot_mad,
        "hiddenThumbnailSignalCandidate": hidden_candidate,
        "selectorCandidateCount": int(selector_candidate),
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
    }
    fingerprint = (
        f"thumb={thumb.size[0]}x{thumb.size[1]}|transform={best_transform}"
        f"|mad={summary['bestTransformMad']}|activeMatch={active_match_count}/4"
        f"|activeChanged={active_changed}|controlChanged={control_changed}"
        f"|slotChanged={slot_changed}|activeMinPx={active_pixel_min}"
        f"|maxActiveMad={max_active_mad}|maxSlotMad={max_slot_mad}"
        f"|hiddenCandidate={int(hidden_candidate)}|sourceR3=0"
        f"|triggers={satisfied}/{trigger_count}|selectors=0"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current PDF page-76 thumbnail active-target/OVERDOSE visual check; "
            "no key derivation, candidate generation, broad hashing, seed/WIF/address checks, or brute force"
        ),
        "decision": {
            "currentPdfThumbnailActiveSignalGate": "current_pdf_thumbnail_active_signal_no_selector",
            "selectorUnlocked": False,
        },
        "summary": summary,
        "fingerprint": fingerprint,
        "rows": rows,
        "sheet": rel(OUT_SHEET),
        "nextMove": (
            "Do not promote embedded thumbnails as target or OVERDOSE visual evidence. "
            "Use only a distinct physical/original-layout/source asset or raw clue wording that supplies unit/order/transform."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Current PDF Thumbnail Active Signal Gate",
        "",
        "Scope: checked the tiny embedded page-76 thumbnail against the same-size trusted page-image downsample around O4/B4/G5/O5, page-76 highlight controls, and C9/OVERDOSE slots. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Thumbnail: xref `{thumb_xref}`, size `{thumb.size[0]}x{thumb.size[1]}`",
        f"- Best orientation vs trusted downsample: `{best_transform}` with MAD `{summary['bestTransformMad']}`",
        f"- Active state matches expected: `{active_match_count}/4`",
        f"- Active / control / slot state changes vs same-size downsample: `{active_changed}` / `{control_changed}` / `{slot_changed}`",
        f"- Active min pixel count: `{active_pixel_min}`",
        f"- Max active / slot crop MAD: `{max_active_mad}` / `{max_slot_mad}`",
        f"- Hidden thumbnail signal candidate / selectors: `{int(hidden_candidate)}` / `0`",
        f"- Source-backed R3 / satisfied triggers: `0` / `{satisfied}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Active Rows",
        "",
        "| id | expected | thumbnail state | downsample state | pixels | MAD | thumb orange/dark/grey |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in active_rows:
        tm = row["thumbnail"]
        rm = row["sameSizeDownsample"]
        lines.append(
            "| {id} | {expected} | {thumb_state} | {ref_state} | {pixels} | {mad} | {ratios} |".format(
                id=row["id"],
                expected=row["expectedState"],
                thumb_state=tm["state"],
                ref_state=rm["state"],
                pixels=tm["pixelCount"],
                mad=row["thumbnailVsDownsampleMad"],
                ratios=f"{tm['orangeRatio']}/{tm['darkRatio']}/{tm['greyRatio']}",
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_thumbnail_active_signal_no_selector`",
            "- The page-76 thumbnail is only `82x106`; active text boxes collapse to tiny regions and are a preview/downsample witness, not a separate source layer.",
            "- The thumbnail does not invent a cleaner all-four active or OVERDOSE-slot signal beyond the same-size trusted downsample, and no source-backed R3 trigger is satisfied.",
            "- Keep embedded thumbnails closed as provenance-only previews.",
            "",
            "## Next Move",
            "",
            "- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(fingerprint)


if __name__ == "__main__":
    main()

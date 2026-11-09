#!/usr/bin/env python3
"""Verify orientation discipline for completed page-76 active crop boxes.

The active O4/B4/G5/O5 crop authority is in the readable/upright page-76 frame.
The native source_images extraction is upside-down and must be rotated 180
degrees before comparison. This pass creates a visual guardrail so future
source comparisons do not mix coordinate frames. It does not run extraction,
hashing, key derivation, WIF/Base58 scans, OCR, or address checks.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/page76_active_crop_orientation_guardrail"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_active_crop_orientation_guardrail.json"
OUT_MD = OUT / "page76_active_crop_orientation_guardrail.md"
SHEET = OUT / "page76_active_crop_orientation_guardrail_sheet.jpg"
UPRIGHT_OVERLAY = OUT / "page76_active_targets_upright_overlay.jpg"
NATIVE_OVERLAY = OUT / "page76_active_targets_native_overlay.jpg"
ROT180_OVERLAY = OUT / "page76_active_targets_rot180_overlay.jpg"

INPUTS = {
    "crop_completion": ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json",
    "packet_sync": ROOT / "analysis_outputs/source_audit/source_packet_crop_authority_sync/source_packet_crop_authority_sync.json",
    "source_reopen": ROOT / "analysis_outputs/source_audit/source_reopen_requirements/source_reopen_requirements.json",
}

UPRIGHT_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
NATIVE_IMAGE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"


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


def transform_rot180_box(box: list[int | float], width: int, height: int) -> list[int]:
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    return [width - x1, height - y1, width - x0, height - y0]


def draw_overlay(
    image: Image.Image,
    records: list[dict[str, Any]],
    out_path: Path,
    title: str,
    box_key: str = "box",
) -> None:
    canvas = image.copy().convert("RGB")
    draw = ImageDraw.Draw(canvas)
    title_font = font(42)
    label_font = font(22)
    draw.rectangle((20, 20, min(canvas.width - 20, 1200), 90), fill=(10, 12, 16))
    draw.text((36, 34), title, fill=(246, 248, 250), font=title_font)
    for row in records:
        box = row[box_key]
        color = row.get("color", "#ff9b2e")
        label = row.get("label", row.get("id", "target"))
        for offset in range(5):
            draw.rectangle(
                (box[0] - offset, box[1] - offset, box[2] + offset, box[3] + offset),
                outline=color,
            )
        label_w = int(draw.textlength(label, font=label_font)) + 14
        label_h = 32
        lx = max(0, min(box[0], canvas.width - label_w))
        ly = max(0, box[1] - label_h - 5)
        draw.rectangle((lx, ly, lx + label_w, ly + label_h), fill=(10, 12, 16))
        draw.text((lx + 7, ly + 5), label, fill=(246, 248, 250), font=label_font)
    canvas.save(out_path, quality=94)


def paste_thumb(sheet: Image.Image, path: Path, box: tuple[int, int, int, int], title: str) -> None:
    draw = ImageDraw.Draw(sheet)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(18, 22, 28), outline=(50, 58, 70))
    draw.text((x0 + 12, y0 + 10), title, fill=(238, 243, 248), font=font(17))
    if not path.exists():
        draw.text((x0 + 12, y0 + 42), "missing", fill=(255, 130, 130), font=font(14))
        return
    image = Image.open(path).convert("RGB")
    max_w = x1 - x0 - 24
    max_h = y1 - y0 - 58
    scale = min(max_w / image.width, max_h / image.height)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    resample = getattr(Image, "Resampling", Image).LANCZOS
    resized = image.resize(new_size, resample)
    sheet.paste(resized, (x0 + 12, y0 + 44))


def build_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1740, 1320
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(17)
    small = font(13)
    mono = font(15)

    draw.text((margin, margin), "Page-76 Active Crop Orientation Guardrail", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 45),
        "Completed O4/B4/G5/O5 boxes are valid in readable/upright coordinates; native source_images need 180-degree rotation.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("upright size", result["summary"]["uprightSize"]),
        ("native size", result["summary"]["nativeSize"]),
        ("rot180 mean abs", result["summary"]["rot180MeanAbsDiff"]),
        ("direct mean abs", result["summary"]["directMeanAbsDiff"]),
        ("orientation", result["summary"]["orientationDecision"]),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 310, y + 52), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 8), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 27), str(value)[:34], fill=(232, 239, 246), font=mono)
        x += 330

    y += 82
    draw.rectangle((margin, y, sheet_w - margin, y + 110), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Guardrail", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "Compare future page-76 source material to the completed crop boxes only after converting to the readable/upright frame.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 76),
        "Do not apply upright boxes directly to native source_images/fresh extraction coordinates.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 140
    headers = [("target", 12), ("upright box", 360), ("native rot180 box", 690), ("line/corr", 1040)]
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["targetRows"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 46), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 13), row["label"], fill=(238, 243, 248), font=small)
        draw.text((margin + 360, y + 13), str(row["uprightBox"]), fill=(176, 186, 198), font=small)
        draw.text((margin + 690, y + 13), str(row["nativeRot180Box"]), fill=(176, 186, 198), font=small)
        draw.text((margin + 1040, y + 13), f"L{row['pageLine']}/C{row['corridorIndex']}", fill=(238, 243, 248), font=mono)
        y += 50

    y += 22
    thumb_w = (sheet_w - margin * 2 - 28) // 3
    thumb_h = 475
    thumbs = [
        ("upright overlay", UPRIGHT_OVERLAY),
        ("native source overlay", NATIVE_OVERLAY),
        ("rotated-native overlay", ROT180_OVERLAY),
    ]
    for idx, (title, path) in enumerate(thumbs):
        x0 = margin + idx * (thumb_w + 14)
        paste_thumb(sheet, path, (x0, y, x0 + thumb_w, y + thumb_h), title)

    sheet.save(SHEET, quality=94)


def main() -> None:
    crop_completion = load_json(INPUTS["crop_completion"])
    packet_sync = load_json(INPUTS["packet_sync"])
    source_reopen = load_json(INPUTS["source_reopen"])

    upright = Image.open(UPRIGHT_IMAGE).convert("RGB")
    native = Image.open(NATIVE_IMAGE).convert("RGB")
    native_rot180 = native.rotate(180)
    width, height = upright.size

    if native.size != upright.size:
        raise RuntimeError(f"image size mismatch: upright={upright.size}, native={native.size}")

    rot_diff = np.asarray(ImageChops.difference(upright, native_rot180), dtype=np.uint8)
    direct_diff = np.asarray(ImageChops.difference(upright, native), dtype=np.uint8)

    target_rows = []
    native_records = []
    for target in crop_completion.get("targets", []):
        native_box = transform_rot180_box(target["box"], width, height)
        row = {
            "id": target["id"],
            "label": target["label"],
            "color": target["color"],
            "uprightBox": target["box"],
            "nativeRot180Box": native_box,
            "pageLine": target.get("pageLine"),
            "corridorIndex": target.get("corridorIndex"),
            "visualState": target.get("visualState"),
            "withinUprightBounds": 0 <= target["box"][0] < target["box"][2] <= width
            and 0 <= target["box"][1] < target["box"][3] <= height,
            "withinNativeBounds": 0 <= native_box[0] < native_box[2] <= width
            and 0 <= native_box[1] < native_box[3] <= height,
        }
        target_rows.append(row)
        native_records.append({**target, "box": native_box})

    draw_overlay(upright, crop_completion.get("targets", []), UPRIGHT_OVERLAY, "Readable/upright page-76 active boxes")
    draw_overlay(native, native_records, NATIVE_OVERLAY, "Native source_images page-76 boxes after rot180 transform")
    draw_overlay(native_rot180, crop_completion.get("targets", []), ROT180_OVERLAY, "source_images page-76 rotated 180; upright boxes apply")

    summary = {
        "uprightImage": rel(UPRIGHT_IMAGE),
        "nativeImage": rel(NATIVE_IMAGE),
        "uprightSize": f"{width}x{height}",
        "nativeSize": f"{native.size[0]}x{native.size[1]}",
        "rot180MeanAbsDiff": round(float(rot_diff.mean()), 4),
        "rot180MaxDiff": int(rot_diff.max()),
        "rot180NonzeroPct": round(float((rot_diff > 0).mean() * 100), 4),
        "directMeanAbsDiff": round(float(direct_diff.mean()), 4),
        "directMaxDiff": int(direct_diff.max()),
        "directNonzeroPct": round(float((direct_diff > 0).mean() * 100), 4),
        "allUprightBoxesInBounds": all(row["withinUprightBounds"] for row in target_rows),
        "allNativeTransformBoxesInBounds": all(row["withinNativeBounds"] for row in target_rows),
        "orientationDecision": "use_upright_boxes_after_rot180_for_native_source_images",
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 active crop orientation guardrail; no extraction, no key derivation, no hashing, no OCR, no address checks",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "summary": summary,
        "targetRows": target_rows,
        "overlays": {
            "upright": rel(UPRIGHT_OVERLAY),
            "nativeSourceImages": rel(NATIVE_OVERLAY),
            "nativeRot180": rel(ROT180_OVERLAY),
        },
        "handoffContext": {
            "packetCropSyncDecision": packet_sync.get("decision"),
            "sourceReopenDecision": source_reopen.get("decision"),
            "r4StillRequired": True,
        },
        "sheet": rel(SHEET),
        "decision": "page76_active_crop_orientation_guardrail_pass_no_selector",
        "nextMove": "For any future source comparison, first normalize orientation to the readable/upright frame or transform O4/B4/G5/O5 boxes with the recorded 180-degree formula. R3 unit/order evidence is still required before extraction.",
    }

    build_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page-76 Active Crop Orientation Guardrail",
        "",
        "Scope: verify that the completed O4/B4/G5/O5 boxes are in the readable/upright page-76 coordinate frame and document the 180-degree transform needed for native `source_images`. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Upright image: `{summary['uprightImage']}`",
        f"- Native image: `{summary['nativeImage']}`",
        f"- Upright/native size: `{summary['uprightSize']}` / `{summary['nativeSize']}`",
        f"- Native rotated 180 vs upright mean abs diff: `{summary['rot180MeanAbsDiff']}`; max diff `{summary['rot180MaxDiff']}`; nonzero `{summary['rot180NonzeroPct']}%`",
        f"- Native direct vs upright mean abs diff: `{summary['directMeanAbsDiff']}`; max diff `{summary['directMaxDiff']}`; nonzero `{summary['directNonzeroPct']}%`",
        f"- All upright boxes in bounds: `{summary['allUprightBoxesInBounds']}`",
        f"- All native-transform boxes in bounds: `{summary['allNativeTransformBoxesInBounds']}`",
        f"- Orientation decision: `{summary['orientationDecision']}`",
        f"- Selector unlocked: `{summary['selectorUnlocked']}`",
        "",
        "## Target Boxes",
        "",
        "| target | upright box | native rot180 box | line/corridor |",
        "|---|---|---|---|",
    ]
    for row in target_rows:
        lines.append(
            f"| `{row['label']}` | `{row['uprightBox']}` | `{row['nativeRot180Box']}` | `L{row['pageLine']}/C{row['corridorIndex']}` |"
        )
    lines.extend(
        [
            "",
            "## Overlays",
            "",
            f"- Upright overlay: `{rel(UPRIGHT_OVERLAY)}`",
            f"- Native source overlay: `{rel(NATIVE_OVERLAY)}`",
            f"- Native rotated-180 overlay: `{rel(ROT180_OVERLAY)}`",
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
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

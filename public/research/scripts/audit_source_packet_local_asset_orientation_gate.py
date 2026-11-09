#!/usr/bin/env python3
"""Audit local source-like assets against the page-76 orientation gate.

This pass asks whether any currently available local image/PDF asset improves
the source/physical/original-layout evidence for the active page-76 target
cluster. It normalizes image candidates against the readable/upright page-76
baseline and records source-review status only; it does not extract key
material or run candidate checks.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_local_asset_orientation_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_local_asset_orientation_gate.json"
OUT_MD = OUT / "source_packet_local_asset_orientation_gate.md"
OUT_SHEET = OUT / "source_packet_local_asset_orientation_gate_sheet.jpg"

UPRIGHT_PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
NATIVE_PAGE76 = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"
ORIENTATION_GUARDRAIL = ROOT / (
    "analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/"
    "page76_active_crop_orientation_guardrail.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
PDF_EXTS = {".pdf"}
PAGE76_MATCH_MAD = 14.0
PAGE76_DERIVATIVE_MAD = 22.0


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def small_gray(img: Image.Image, size: tuple[int, int] = (192, 256)) -> Image.Image:
    return ImageOps.grayscale(img).resize(size, Image.Resampling.BILINEAR)


def mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]


def box_from_row(row: dict) -> list[int] | None:
    if row.get("uprightBox"):
        return row["uprightBox"]
    if row.get("box"):
        return row["box"]
    return None


def scaled_crop_mad(
    candidate: Image.Image,
    candidate_orientation: str,
    baseline_upright: Image.Image,
    boxes: list[list[int]],
) -> dict:
    oriented = candidate.rotate(180) if candidate_orientation == "rotate180" else candidate
    cw, ch = oriented.size
    bw, bh = baseline_upright.size
    scale_x = cw / bw
    scale_y = ch / bh
    rows = []
    for box in boxes:
        x0, y0, x1, y1 = box
        cbox = [
            max(0, round(x0 * scale_x)),
            max(0, round(y0 * scale_y)),
            min(cw, round(x1 * scale_x)),
            min(ch, round(y1 * scale_y)),
        ]
        bbox = [max(0, x0), max(0, y0), min(bw, x1), min(bh, y1)]
        if cbox[2] <= cbox[0] or cbox[3] <= cbox[1]:
            continue
        cand_crop = small_gray(oriented.crop(cbox), (160, 42))
        base_crop = small_gray(baseline_upright.crop(bbox), (160, 42))
        rows.append(mean_abs_diff(cand_crop, base_crop))
    return {
        "activeCropMadMean": round(sum(rows) / len(rows), 4) if rows else None,
        "activeCropMadMax": round(max(rows), 4) if rows else None,
        "activeCropCount": len(rows),
    }


def candidate_paths() -> tuple[list[Path], list[Path]]:
    images: set[Path] = set()
    pdfs: set[Path] = set()

    for pattern in [
        "*.jpg",
        "*.jpeg",
        "*.png",
        "analysis_outputs/source_images/*.jpg",
        "analysis_outputs/external_clues/*.jpg",
        "analysis_outputs/external_clues/*.png",
        "analysis_outputs/external_clues/max_thread_media/*.jpg",
    ]:
        images.update(ROOT.glob(pattern))

    for pattern in [
        "*.pdf",
        "analysis_outputs/external_clues/*.pdf",
    ]:
        pdfs.update(ROOT.glob(pattern))

    # Keep this gate source-like; exclude generated masks/sheets outside the
    # explicit source/external folders.
    images = {
        path
        for path in images
        if not str(path).startswith(str(OUT))
        and path.exists()
        and path.suffix.lower() in IMAGE_EXTS
    }
    pdfs = {path for path in pdfs if path.exists() and path.suffix.lower() in PDF_EXTS}
    return sorted(images), sorted(pdfs)


def compare_image(
    path: Path,
    baseline_upright: Image.Image,
    baseline_native: Image.Image,
    active_boxes: list[list[int]],
    known_hashes: dict[str, str],
) -> dict:
    img = Image.open(path).convert("RGB")
    variants = [
        ("as_is", img),
        ("rotate180", img.rotate(180)),
    ]
    baseline_u_small = small_gray(baseline_upright)
    baseline_n_small = small_gray(baseline_native)

    best_upright = None
    best_native = None
    for name, variant in variants:
        u_mad = mean_abs_diff(small_gray(variant), baseline_u_small)
        n_mad = mean_abs_diff(small_gray(variant), baseline_n_small)
        if best_upright is None or u_mad < best_upright["mad"]:
            best_upright = {"orientation": name, "mad": round(u_mad, 4)}
        if best_native is None or n_mad < best_native["mad"]:
            best_native = {"orientation": name, "mad": round(n_mad, 4)}

    digest = md5(path)
    exact_role = next((role for role, h in known_hashes.items() if h == digest), None)
    crop_stats = scaled_crop_mad(
        img,
        best_upright["orientation"],
        baseline_upright,
        active_boxes,
    )
    page76_match = best_upright["mad"] <= PAGE76_MATCH_MAD or best_native["mad"] <= PAGE76_MATCH_MAD
    derivative_match = (
        page76_match
        or best_upright["mad"] <= PAGE76_DERIVATIVE_MAD
        or best_native["mad"] <= PAGE76_DERIVATIVE_MAD
    )
    resolution_gain = (img.size[0] * img.size[1]) / (
        baseline_upright.size[0] * baseline_upright.size[1]
    )
    higher_resolution = resolution_gain > 1.05
    reopen_candidate = bool(page76_match and higher_resolution and not exact_role)
    return {
        "path": rel(path),
        "size": [img.size[0], img.size[1]],
        "pixelCount": img.size[0] * img.size[1],
        "md5": digest,
        "exactCurrentScanRole": exact_role,
        "bestUprightOrientation": best_upright["orientation"],
        "bestUprightMad": best_upright["mad"],
        "bestNativeOrientation": best_native["orientation"],
        "bestNativeMad": best_native["mad"],
        "activeCropMadMean": crop_stats["activeCropMadMean"],
        "activeCropMadMax": crop_stats["activeCropMadMax"],
        "activeCropCount": crop_stats["activeCropCount"],
        "page76Match": page76_match,
        "derivativePage76Match": derivative_match,
        "resolutionGainVsBaseline": round(resolution_gain, 4),
        "higherResolutionThanBaseline": higher_resolution,
        "reopenCandidate": reopen_candidate,
    }


def pdf_rows(pdfs: list[Path]) -> list[dict]:
    return [
        {
            "path": rel(path),
            "bytes": path.stat().st_size,
            "md5": md5(path),
            "imageComparableInThisPass": False,
            "note": "PDF asset recorded for source review; this pass compares available rendered image pages only.",
        }
        for path in pdfs
    ]


def draw_sheet(summary: dict, image_rows: list[dict], pdfs: list[dict]) -> None:
    width, height = 1840, 1040
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 16)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 100), fill=(25, 31, 42))
    draw.text((24, 18), "Local Source Asset Orientation Gate", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"images {summary['imageCandidateCount']} | page76 matches {summary['page76MatchCount']} | "
            f"higher-res matches {summary['higherResolutionPage76Count']} | R1/R3 {summary['r1DistinctImprovedCount']}/{summary['sourceBackedR3BridgeHitCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 128
    draw.text((24, y), "Best page-76-oriented image candidates", fill=(45, 45, 45), font=small)
    y += 30
    xs = [24, 560, 730, 860, 990, 1120, 1260, 1430, 1600]
    headers = ["path", "size", "upright", "uMAD", "native", "nMAD", "crop max", "gain", "role"]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    display_rows = sorted(
        image_rows,
        key=lambda row: (
            not row["derivativePage76Match"],
            row["bestUprightMad"],
            row["path"],
        ),
    )
    for idx, row in enumerate(display_rows[:17]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 38), fill=fill)
        draw.text((xs[0], y), row["path"][:70], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), f"{row['size'][0]}x{row['size'][1]}", fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["bestUprightOrientation"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), str(row["bestUprightMad"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), row["bestNativeOrientation"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), str(row["bestNativeMad"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[6], y), str(row["activeCropMadMax"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[7], y), str(row["resolutionGainVsBaseline"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[8], y), row["exactCurrentScanRole"] or "-", fill=(30, 30, 30), font=tiny)
        y += 44

    y += 20
    draw.text((24, y), "PDF assets noted for source review", fill=(45, 45, 45), font=small)
    y += 30
    for row in pdfs[:6]:
        draw.text((24, y), f"{row['path']} ({row['bytes']} bytes)", fill=(70, 70, 70), font=tiny)
        y += 22
    y += 20
    draw.text((24, y), summary["localAssetOrientationFingerprint"], fill=(45, 45, 45), font=tiny)
    img.save(OUT_SHEET, quality=92)


def main() -> None:
    baseline_upright = Image.open(UPRIGHT_PAGE76).convert("RGB")
    baseline_native = Image.open(NATIVE_PAGE76).convert("RGB")
    guardrail = load_json(ORIENTATION_GUARDRAIL)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_boxes = [
        box
        for box in (box_from_row(row) for row in guardrail.get("targetRows", []))
        if box
    ]
    if not active_boxes:
        active_boxes = [
            [1334, 2177, 1801, 2225],
            [428, 2398, 691, 2445],
            [795, 2544, 1196, 2592],
            [1040, 2932, 1661, 2982],
        ]

    known_hashes = {
        "upright_page76": md5(UPRIGHT_PAGE76),
        "native_page76": md5(NATIVE_PAGE76),
    }
    images, pdfs = candidate_paths()
    image_rows = []
    for path in images:
        try:
            image_rows.append(
                compare_image(path, baseline_upright, baseline_native, active_boxes, known_hashes)
            )
        except Exception as exc:
            image_rows.append({"path": rel(path), "error": str(exc), "page76Match": False, "reopenCandidate": False})

    pdfs_out = pdf_rows(pdfs)
    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    if source_r3 is None:
        source_r3 = 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0)
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0)
    page76_rows = [row for row in image_rows if row.get("page76Match")]
    derivative_rows = [row for row in image_rows if row.get("derivativePage76Match")]
    higher_page76 = [row for row in page76_rows if row.get("higherResolutionThanBaseline")]
    reopen_rows = [row for row in image_rows if row.get("reopenCandidate")]

    summary = {
        "imageCandidateCount": len(image_rows),
        "pdfCandidateCount": len(pdfs_out),
        "page76MatchCount": len(page76_rows),
        "derivativePage76MatchCount": len(derivative_rows),
        "exactCurrentScanMatchCount": sum(1 for row in image_rows if row.get("exactCurrentScanRole")),
        "higherResolutionPage76Count": len(higher_page76),
        "r1DistinctImprovedCount": len(reopen_rows),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": bool(reopen_rows and source_r3 > 0 and triggers > 0),
    }
    summary["localAssetOrientationFingerprint"] = (
        f"images={summary['imageCandidateCount']}|pdfs={summary['pdfCandidateCount']}|"
        f"page76={summary['page76MatchCount']}|derivatives={summary['derivativePage76MatchCount']}|"
        f"exact={summary['exactCurrentScanMatchCount']}|higherRes={summary['higherResolutionPage76Count']}|"
        f"r1Improved={summary['r1DistinctImprovedCount']}|sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={int(summary['selectorUnlocked'])}"
    )

    decision = {
        "sourcePacketLocalAssetOrientationGate": "local_assets_do_not_reopen_source_review",
        "selectorUnlocked": summary["selectorUnlocked"],
        "reason": (
            "Current local image candidates only identify the known page-76 baseline or derivative/lower-quality "
            "views; no image provides a distinct higher-resolution page-76 source, and no source-backed R3 "
            "unit/order trigger is satisfied."
        ),
        "nextMove": (
            "Keep the source-acquisition packet as the next-action checklist. Reopen extraction only if a "
            "new physical/original-layout/raw-clue asset improves R1/R5 and supplies R3 unit/order wording."
        ),
    }

    draw_sheet(summary, image_rows, pdfs_out)
    payload = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "local source-like asset orientation/source-review gate; no extraction or candidate generation",
        "inputs": {
            "uprightPage76": rel(UPRIGHT_PAGE76),
            "nativePage76": rel(NATIVE_PAGE76),
            "orientationGuardrail": rel(ORIENTATION_GUARDRAIL),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "imageRows": image_rows,
        "pdfRows": pdfs_out,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# Source Packet Local Asset Orientation Gate",
                "",
                f"- Image candidates checked: `{summary['imageCandidateCount']}`.",
                f"- PDF candidates recorded: `{summary['pdfCandidateCount']}`.",
                f"- Page-76 image matches / derivative matches: `{summary['page76MatchCount']}` / `{summary['derivativePage76MatchCount']}`.",
                f"- Exact current-scan matches: `{summary['exactCurrentScanMatchCount']}`.",
                f"- Higher-resolution page-76 matches: `{summary['higherResolutionPage76Count']}`.",
                f"- R1 distinct improved local image candidates: `{summary['r1DistinctImprovedCount']}`.",
                f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
                f"- Selector unlocked: `{summary['selectorUnlocked']}`.",
                f"- Fingerprint: `{summary['localAssetOrientationFingerprint']}`.",
                "",
                "Top page-76 candidates:",
                "",
            ]
            + [
                (
                    f"- `{row['path']}`: size `{row['size'][0]}x{row['size'][1]}`, "
                    f"upright `{row['bestUprightOrientation']}` MAD `{row['bestUprightMad']}`, "
                    f"native `{row['bestNativeOrientation']}` MAD `{row['bestNativeMad']}`, "
                    f"gain `{row['resolutionGainVsBaseline']}`, role `{row['exactCurrentScanRole'] or '-'}`."
                )
                for row in sorted(
                    image_rows,
                    key=lambda row: (
                        not row.get("derivativePage76Match", False),
                        row.get("bestUprightMad", 999),
                        row.get("path", ""),
                    ),
                )[:8]
                if "error" not in row
            ]
            + [
                "",
                "Decision: local source-like assets do not reopen source review or extraction.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

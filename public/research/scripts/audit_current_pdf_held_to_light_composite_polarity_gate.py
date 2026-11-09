#!/usr/bin/env python3
"""Audit exact PDF-native held-to-light composite orientation/polarity variants.

This bounded pass creates a held-to-light simulator from the current PDFs using
their embedded article page images. It tests fixed physical orientations only:
no shift search, no OCR-to-key extraction, no candidate keys, no hashes, no
seed/WIF/address checks, no BIP39, and no brute force.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_current_pdf_native_image_registration_gate as native  # noqa: E402


OUT = ROOT / "analysis_outputs/source_audit/current_pdf_held_to_light_composite_polarity_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_held_to_light_composite_polarity_gate.json"
OUT_MD = OUT / "current_pdf_held_to_light_composite_polarity_gate.md"
OUT_SHEET = OUT / "current_pdf_held_to_light_composite_polarity_gate_sheet.jpg"

SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

ACTIVE_REGION_REF = [240.0, 2080.0, 1900.0, 3050.0]
EPS = 1e-9


Transform = tuple[str, str, Callable[[Image.Image], Image.Image]]
TRANSFORMS: list[Transform] = [
    (
        "physical_back_mirror",
        "Back side seen through page 76, page 75 mirrored left-right.",
        ImageOps.mirror,
    ),
    (
        "same_side_no_mirror",
        "Unmirrored page 75 over page 76, included as a non-backside control.",
        lambda img: img,
    ),
    (
        "back_mirror_rotate180",
        "Mirrored back side with 180-degree turn, testing page-turn ambiguity.",
        lambda img: ImageOps.mirror(img).rotate(180),
    ),
    (
        "front_rotate180",
        "Unmirrored 180-degree turn, included as an orientation control.",
        lambda img: img.rotate(180),
    ),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def safe_id(value: str) -> str:
    return (
        value.replace("/", "_")
        .replace(" ", "_")
        .replace(".", "_")
        .replace("-", "_")
        .strip("_")
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def page_images(pdf_path: Path) -> tuple[Image.Image, Image.Image, dict[str, Any]]:
    with fitz.open(pdf_path) as doc:
        page75 = native.page_record(doc, pdf_path, 2, 75)
        page76 = native.page_record(doc, pdf_path, 3, 76)
    source = page75.pop("image")
    target = page76.pop("image")
    if source.size != target.size:
        source = source.resize(target.size, Image.Resampling.BICUBIC)
    pair = {
        "pdf": rel(pdf_path),
        "page75": page75,
        "page76": page76,
        "sameImageSize": page75["imageSize"] == page76["imageSize"],
        "sameImageRect": native.same_list(page75["imageRect"], page76["imageRect"]),
        "imageRectDeltaPt": [
            round(page76["imageRect"][idx] - page75["imageRect"][idx], 4)
            for idx in range(4)
        ],
    }
    return source, target, pair


def box_metrics(source_mask: np.ndarray, target_mask: np.ndarray, box: list[float]) -> dict[str, float]:
    source_crop = native.crop_mask(source_mask, box)
    target_crop = native.crop_mask(target_mask, box)
    if not source_crop.size or source_crop.shape != target_crop.shape:
        return {
            "sourceCoverage": 0.0,
            "targetCoverage": 0.0,
            "sourceOnlyCoverage": 0.0,
            "overlapCoverage": 0.0,
            "unionCoverage": 0.0,
            "cleanThroughScore": 0.0,
        }
    source = source_crop.astype(bool)
    target = target_crop.astype(bool)
    source_only = np.logical_and(source, ~target)
    overlap = np.logical_and(source, target)
    union = np.logical_or(source, target)
    return {
        "sourceCoverage": float(source.mean()),
        "targetCoverage": float(target.mean()),
        "sourceOnlyCoverage": float(source_only.mean()),
        "overlapCoverage": float(overlap.mean()),
        "unionCoverage": float(union.mean()),
        "cleanThroughScore": float(source_only.mean() - overlap.mean()),
    }


def rounded_metrics(metrics: dict[str, float]) -> dict[str, float]:
    return {key: round(value, 9) for key, value in metrics.items()}


def held_to_light_composite(target: Image.Image, source_transformed: Image.Image) -> Image.Image:
    if source_transformed.size != target.size:
        source_transformed = source_transformed.resize(target.size, Image.Resampling.BICUBIC)
    multiplied = ImageChops.multiply(target.convert("RGB"), source_transformed.convert("RGB"))
    return Image.blend(target.convert("RGB"), multiplied, 0.42)


def analyze_variant(
    pdf_path: Path,
    transform_id: str,
    transform_description: str,
    source_img: Image.Image,
    target_img: Image.Image,
    transform: Callable[[Image.Image], Image.Image],
    active: list[dict[str, Any]],
    slots: list[dict[str, Any]],
) -> dict[str, Any]:
    source_transformed = transform(source_img).convert("RGB")
    if source_transformed.size != target_img.size:
        source_transformed = source_transformed.resize(target_img.size, Image.Resampling.BICUBIC)
    source_mask = native.feature_mask(source_transformed)
    target_mask = native.feature_mask(target_img)
    active_boxes = [row["box"] for row in active]

    active_rows: list[dict[str, Any]] = []
    for row in active:
        box = native.scaled_box(row["box"], target_img.size)
        metrics = box_metrics(source_mask, target_mask, box)
        control_values = [
            box_metrics(source_mask, target_mask, native.scaled_box(control, target_img.size))[
                "sourceOnlyCoverage"
            ]
            for control in native.control_boxes_for(row["box"], active_boxes)
        ]
        p95 = float(np.quantile(control_values, 0.95)) if control_values else 0.0
        active_rows.append(
            {
                "target": row["shortId"],
                "phrase": row["phrase"],
                "referenceBox": row["box"],
                "nativeBox": [round(v, 2) for v in box],
                **rounded_metrics(metrics),
                "controlCount": len(control_values),
                "controlP95SourceOnlyCoverage": round(p95, 9),
                "controlMaxSourceOnlyCoverage": round(max(control_values), 9)
                if control_values
                else 0.0,
                "controlPercentile": round(
                    native.percentile(metrics["sourceOnlyCoverage"], control_values), 9
                ),
                "isAboveControlP95": bool(metrics["sourceOnlyCoverage"] > p95),
                "isAtLeast10": bool(metrics["sourceOnlyCoverage"] >= 0.10),
                "isAtLeast25": bool(metrics["sourceOnlyCoverage"] >= 0.25),
                "isCleanThrough10": bool(
                    metrics["sourceOnlyCoverage"] >= 0.10
                    and metrics["overlapCoverage"] <= 0.15
                ),
            }
        )

    slot_rows: list[dict[str, Any]] = []
    for row in slots:
        box = native.scaled_box(row["box"], target_img.size)
        metrics = box_metrics(source_mask, target_mask, box)
        slot_rows.append(
            {
                "target": row["target"],
                "slotIndex": row["slotIndex"],
                "slotLetter": row["slotLetter"],
                "referenceBox": row["box"],
                "nativeBox": [round(v, 2) for v in box],
                **rounded_metrics(metrics),
                "isAtLeast25": bool(metrics["sourceOnlyCoverage"] >= 0.25),
            }
        )

    mean_active = float(np.mean([row["sourceOnlyCoverage"] for row in active_rows]))
    min_active = min((row["sourceOnlyCoverage"] for row in active_rows), default=0.0)
    return {
        "pdf": rel(pdf_path),
        "transform": transform_id,
        "transformDescription": transform_description,
        "imageSize": list(target_img.size),
        "activeRows": active_rows,
        "slotRows": slot_rows,
        "activeAboveControlP95Count": sum(row["isAboveControlP95"] for row in active_rows),
        "activeAtLeast10Count": sum(row["isAtLeast10"] for row in active_rows),
        "activeAtLeast25Count": sum(row["isAtLeast25"] for row in active_rows),
        "activeCleanThrough10Count": sum(row["isCleanThrough10"] for row in active_rows),
        "allFourAboveControlP95": all(row["isAboveControlP95"] for row in active_rows),
        "allFourAtLeast10": all(row["isAtLeast10"] for row in active_rows),
        "allFourCleanThrough10": all(row["isCleanThrough10"] for row in active_rows),
        "maxActiveSourceOnlyCoverage": round(
            max((row["sourceOnlyCoverage"] for row in active_rows), default=0.0), 9
        ),
        "meanActiveSourceOnlyCoverage": round(mean_active, 9),
        "minActiveSourceOnlyCoverage": round(min_active, 9),
        "maxActiveOverlapCoverage": round(
            max((row["overlapCoverage"] for row in active_rows), default=0.0), 9
        ),
        "maxControlSourceOnlyCoverage": round(
            max((row["controlMaxSourceOnlyCoverage"] for row in active_rows), default=0.0),
            9,
        ),
        "maxOverdoseSlotSourceOnlyCoverage": round(
            max((row["sourceOnlyCoverage"] for row in slot_rows), default=0.0), 9
        ),
        "overdoseSlotAtLeast25Count": sum(row["isAtLeast25"] for row in slot_rows),
    }


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


def draw_boxes(
    panel: Image.Image,
    crop_box: list[float],
    page_size: tuple[int, int],
    active: list[dict[str, Any]],
) -> None:
    draw = ImageDraw.Draw(panel)
    small = font(20)
    for row in active:
        box = native.scaled_box(row["box"], page_size)
        rect = [
            box[0] - crop_box[0],
            box[1] - crop_box[1],
            box[2] - crop_box[0],
            box[3] - crop_box[1],
        ]
        color = (240, 80, 35) if row["shortId"] in ("O4", "O5") else (20, 70, 210)
        draw.rectangle(rect, outline=color, width=5)
        draw.text((rect[0], max(0, rect[1] - 24)), row["shortId"], fill=color, font=small)


def draw_sheet(
    pdf_assets: list[dict[str, Any]],
    variant_rows: list[dict[str, Any]],
    active: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    width, height = 1780, 1260
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(23)
    small = font(14)
    tiny = font(11)

    draw.rectangle((0, 0, width, 104), fill=(24, 31, 42))
    draw.text((24, 16), "Current PDF Held-to-Light Composite Polarity Gate", fill="white", font=title)
    draw.text(
        (24, 52),
        "Exact embedded PDF page images; fixed physical orientation variants; no shift search.",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1000, 20),
        f"best active >=10: {summary['bestActiveAtLeast10Count']}/4 | all-four variants: {summary['allFourAtLeast10VariantCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1000, 50),
        f"best mean source-only: {summary['bestMeanActiveSourceOnlyCoverage']:.4f}; slot max: {summary['maxOverdoseSlotSourceOnlyCoverage']:.4f}",
        fill=(236, 236, 236),
        font=small,
    )

    y = 124
    headers = ["PDF", "transform", "mean", "min", "max", ">=10", ">p95", "clean10", "slot max"]
    xs = [22, 342, 642, 720, 795, 870, 930, 990, 1065]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(45, 48, 54), font=small)
    y += 24
    for idx, row in enumerate(variant_rows):
        if idx >= 24:
            break
        fill = (246, 248, 250) if idx % 2 == 0 else (255, 255, 255)
        draw.rectangle((16, y - 5, width - 16, y + 20), fill=fill)
        values = [
            row["pdf"],
            row["transform"],
            f"{row['meanActiveSourceOnlyCoverage']:.4f}",
            f"{row['minActiveSourceOnlyCoverage']:.4f}",
            f"{row['maxActiveSourceOnlyCoverage']:.4f}",
            str(row["activeAtLeast10Count"]),
            str(row["activeAboveControlP95Count"]),
            str(row["activeCleanThrough10Count"]),
            f"{row['maxOverdoseSlotSourceOnlyCoverage']:.4f}",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value[:42], fill=(25, 28, 34), font=tiny)
        y += 23

    panel_w, panel_h = 410, 230
    start_y = 410
    for idx, row in enumerate(variant_rows[:12]):
        asset = next(item for item in pdf_assets if item["pdf"] == row["pdf"])
        transform = next(item[2] for item in TRANSFORMS if item[0] == row["transform"])
        source_transformed = transform(asset["source"]).convert("RGB")
        composite = held_to_light_composite(asset["target"], source_transformed)
        crop_box = native.scaled_box(ACTIVE_REGION_REF, composite.size)
        crop = composite.crop(tuple(round(v) for v in crop_box))
        draw_boxes(crop, crop_box, composite.size, active)
        crop.thumbnail((panel_w, panel_h), Image.Resampling.LANCZOS)
        x = 24 + (idx % 4) * 435
        y = start_y + (idx // 4) * 270
        draw.rectangle((x - 2, y - 2, x + panel_w + 2, y + panel_h + 26), outline=(210, 214, 220))
        sheet.paste(crop, (x, y))
        draw.text((x, y + panel_h + 4), f"{row['pdf'][:28]} | {row['transform']}", fill=(25, 28, 34), font=tiny)

    sheet.save(OUT_SHEET, quality=92)


def save_representative_simulator(pdf_assets: list[dict[str, Any]]) -> list[str]:
    saved: list[str] = []
    magazine = next((row for row in pdf_assets if row["pdf"] == "magazine.pdf"), None)
    if not magazine:
        return saved
    transform = next(item[2] for item in TRANSFORMS if item[0] == "physical_back_mirror")
    composite = held_to_light_composite(magazine["target"], transform(magazine["source"]))
    full = OUT / "magazine_physical_back_mirror_held_to_light_full.jpg"
    crop_path = OUT / "magazine_physical_back_mirror_held_to_light_active_crop.jpg"
    composite.save(full, quality=92)
    crop_box = native.scaled_box(ACTIVE_REGION_REF, composite.size)
    crop = composite.crop(tuple(round(v) for v in crop_box))
    draw_boxes(crop, crop_box, composite.size, native.active_rows())
    crop.save(crop_path, quality=92)
    saved.extend([rel(full), rel(crop_path)])
    return saved


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current PDF Held-to-Light Composite Polarity Gate",
        "",
        "Scope: created a held-to-light simulator from each current PDF's embedded page-75 and page-76 article images, using only exact page placement and four fixed physical orientation hypotheses. No shift search, OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39 checks, or brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- PDFs / transforms / variants: `{summary['pdfCount']}` / `{summary['transformCount']}` / `{summary['variantCount']}`",
        f"- Active rows / projected OVERDOSE slot rows: `{summary['activeRowCount']}` / `{summary['overdoseSlotRowCount']}`",
        f"- Best active >=10% / above control p95 / clean-through >=10%: `{summary['bestActiveAtLeast10Count']}` / `{summary['bestActiveAboveControlP95Count']}` / `{summary['bestActiveCleanThrough10Count']}`",
        f"- All-four >=10% / above p95 / clean-through variants: `{summary['allFourAtLeast10VariantCount']}` / `{summary['allFourAboveControlP95VariantCount']}` / `{summary['allFourCleanThrough10VariantCount']}`",
        f"- Best mean active source-only coverage: `{summary['bestMeanActiveSourceOnlyCoverage']:.4f}`",
        f"- Magazine physical-back active >=10% / mean source-only: `{summary['magazinePhysicalActiveAtLeast10Count']}` / `{summary['magazinePhysicalMeanActiveSourceOnlyCoverage']:.4f}`",
        f"- Max active / max control / max OVERDOSE-slot source-only coverage: `{summary['maxActiveSourceOnlyCoverage']:.4f}` / `{summary['maxControlSourceOnlyCoverage']:.4f}` / `{summary['maxOverdoseSlotSourceOnlyCoverage']:.4f}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Simulator images: `{', '.join(result['simulatorImages'])}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Variant Rows",
        "",
        "| PDF | transform | mean active | min active | max active | >=10 | >p95 | clean10 | slot max |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["variantRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pdf']}`",
                    f"`{row['transform']}`",
                    f"{row['meanActiveSourceOnlyCoverage']:.4f}",
                    f"{row['minActiveSourceOnlyCoverage']:.4f}",
                    f"{row['maxActiveSourceOnlyCoverage']:.4f}",
                    str(row["activeAtLeast10Count"]),
                    str(row["activeAboveControlP95Count"]),
                    str(row["activeCleanThrough10Count"]),
                    f"{row['maxOverdoseSlotSourceOnlyCoverage']:.4f}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote exact PDF-native held-to-light orientation/polarity variants as selectors.",
            "- The original-resolution `magazine.pdf` physical-back simulation produces no active box above 10% source-only coverage and no active row above the same-size control p95.",
            "- The low-resolution derivative PDFs can still make isolated O4/slot coverage spikes, but no transform produces an all-four O4/B4/G5/O5 rule, and controls remain stronger.",
            "- The simulator is useful for visual review, but it supplies no source-backed unit/order wording and satisfies 0/9 reopen triggers.",
            "",
            "## Next Move",
            "",
            "- Stop cycling local held-to-light polarity/orientation variants unless a new source changes the physical page geometry. The next useful move is external/original-layout source validation or raw clue wording that explicitly names transform, unit, and order.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    active = native.active_rows()
    slots = native.c9_slot_boxes()
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))

    pdf_assets: list[dict[str, Any]] = []
    variant_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    for pdf_path in native.PDFS:
        if not pdf_path.exists():
            continue
        source, target, pair = page_images(pdf_path)
        pair_rows.append(pair)
        pdf_assets.append({"pdf": rel(pdf_path), "source": source, "target": target})
        for transform_id, description, transform in TRANSFORMS:
            variant_rows.append(
                analyze_variant(
                    pdf_path,
                    transform_id,
                    description,
                    source,
                    target,
                    transform,
                    active,
                    slots,
                )
            )

    best = max(
        variant_rows,
        key=lambda row: (
            row["activeAtLeast10Count"],
            row["activeAboveControlP95Count"],
            row["meanActiveSourceOnlyCoverage"],
        ),
        default={},
    )
    magazine_physical = next(
        (
            row
            for row in variant_rows
            if row["pdf"] == "magazine.pdf" and row["transform"] == "physical_back_mirror"
        ),
        {},
    )
    active_flat = [row for variant in variant_rows for row in variant["activeRows"]]
    slot_flat = [row for variant in variant_rows for row in variant["slotRows"]]
    simulator_images = save_representative_simulator(pdf_assets)

    summary = {
        "decision": "current_pdf_held_to_light_composite_polarity_no_selector",
        "pdfCount": len(pdf_assets),
        "transformCount": len(TRANSFORMS),
        "variantCount": len(variant_rows),
        "activeRowCount": len(active_flat),
        "overdoseSlotRowCount": len(slot_flat),
        "bestPdf": best.get("pdf"),
        "bestTransform": best.get("transform"),
        "bestActiveAtLeast10Count": int(best.get("activeAtLeast10Count", 0)),
        "bestActiveAboveControlP95Count": int(best.get("activeAboveControlP95Count", 0)),
        "bestActiveCleanThrough10Count": int(best.get("activeCleanThrough10Count", 0)),
        "allFourAtLeast10VariantCount": sum(row["allFourAtLeast10"] for row in variant_rows),
        "allFourAboveControlP95VariantCount": sum(
            row["allFourAboveControlP95"] for row in variant_rows
        ),
        "allFourCleanThrough10VariantCount": sum(row["allFourCleanThrough10"] for row in variant_rows),
        "bestMeanActiveSourceOnlyCoverage": float(best.get("meanActiveSourceOnlyCoverage", 0.0)),
        "magazinePhysicalActiveAtLeast10Count": int(
            magazine_physical.get("activeAtLeast10Count", 0)
        ),
        "magazinePhysicalAboveControlP95Count": int(
            magazine_physical.get("activeAboveControlP95Count", 0)
        ),
        "magazinePhysicalMeanActiveSourceOnlyCoverage": float(
            magazine_physical.get("meanActiveSourceOnlyCoverage", 0.0)
        ),
        "maxActiveSourceOnlyCoverage": max(
            (row["sourceOnlyCoverage"] for row in active_flat), default=0.0
        ),
        "maxControlSourceOnlyCoverage": max(
            (row["controlMaxSourceOnlyCoverage"] for row in active_flat), default=0.0
        ),
        "maxOverdoseSlotSourceOnlyCoverage": max(
            (row["sourceOnlyCoverage"] for row in slot_flat), default=0.0
        ),
        "overdoseSlotAtLeast25Count": sum(row["isAtLeast25"] for row in slot_flat),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|transforms={summary['transformCount']}|"
        f"variants={summary['variantCount']}|activeRows={summary['activeRowCount']}|"
        f"slots={summary['overdoseSlotRowCount']}|best10={summary['bestActiveAtLeast10Count']}|"
        f"bestP95={summary['bestActiveAboveControlP95Count']}|"
        f"all10={summary['allFourAtLeast10VariantCount']}|"
        f"allP95={summary['allFourAboveControlP95VariantCount']}|"
        f"magPhys10={summary['magazinePhysicalActiveAtLeast10Count']}|"
        f"magPhysMean={summary['magazinePhysicalMeanActiveSourceOnlyCoverage']:.4f}|"
        f"activeMax={summary['maxActiveSourceOnlyCoverage']:.4f}|"
        f"controlMax={summary['maxControlSourceOnlyCoverage']:.4f}|"
        f"slotMax={summary['maxOverdoseSlotSourceOnlyCoverage']:.4f}|"
        f"sourceR3={source_r3_hits}|triggers={len(satisfied_triggers)}/{len(trigger_rows)}|"
        "selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Exact PDF-native held-to-light simulator using embedded page 75 and page 76 images, "
            "fixed physical orientation/polarity variants, active boxes, and C9/OVERDOSE slots."
        ),
        "inputs": {
            "pdfs": [rel(path) for path in native.PDFS if path.exists()],
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": "current_pdf_held_to_light_composite_polarity_no_selector",
        "summary": summary,
        "fingerprint": fingerprint,
        "pairRows": pair_rows,
        "variantRows": variant_rows,
        "sheet": rel(OUT_SHEET),
        "simulatorImages": simulator_images,
    }
    draw_sheet(pdf_assets, variant_rows, active, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)


if __name__ == "__main__":
    main()

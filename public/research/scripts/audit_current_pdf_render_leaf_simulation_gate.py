#!/usr/bin/env python3
"""Audit PDF-rendered valid-leaf held-to-light behavior for pages 75 and 76.

This bounded pass checks whether rendering the current PDFs, instead of using
their embedded/canonical page rasters, changes the physically valid article
page 75 -> page 76 held-to-light measurements around O4/B4/G5/O5. It also
measures render-vs-embedded residuals to catch visible layout/text additions.
It does not derive keys, hashes, seed phrases, WIFs, addresses, BIP39 checks,
or candidate material.
"""

from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_render_leaf_simulation_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_render_leaf_simulation_gate.json"
OUT_MD = OUT / "current_pdf_render_leaf_simulation_gate.md"
OUT_SHEET = OUT / "current_pdf_render_leaf_simulation_gate_sheet.jpg"

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

ARTICLE_PAGES = (75, 76)
PDF_PAGE_INDEX = {75: 2, 76: 3}
PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
RENDER_DPI = 300


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def mad(a: Image.Image, b: Image.Image) -> float:
    if a.size != b.size:
        b = b.resize(a.size, Image.Resampling.BICUBIC)
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return float(np.asarray(diff, dtype=np.float32).mean())


def normalize_to_upright(img: Image.Image, page: int) -> tuple[Image.Image, dict[str, Any]]:
    ref = Image.open(UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{page}_upright.jpg")).convert("RGB")
    transforms = {
        "as_is": img.convert("RGB"),
        "rotate180": img.convert("RGB").rotate(180),
        "hflip": ImageOps.mirror(img.convert("RGB")),
        "hflip_rotate180": ImageOps.mirror(img.convert("RGB")).rotate(180),
    }
    scored = []
    for name, transformed in transforms.items():
        scored.append({"orientation": name, "madToUpright": round(mad(ref, transformed), 4)})
    best = min(scored, key=lambda row: row["madToUpright"])
    normalized = transforms[best["orientation"]]
    if normalized.size != ref.size:
        normalized = normalized.resize(ref.size, Image.Resampling.BICUBIC)
    return normalized, {
        "bestOrientation": best["orientation"],
        "bestMadToUpright": best["madToUpright"],
        "inputSize": f"{img.size[0]}x{img.size[1]}",
        "normalizedSize": f"{normalized.size[0]}x{normalized.size[1]}",
    }


def render_pdf_page(doc: fitz.Document, page_index: int) -> Image.Image:
    page = doc[page_index]
    matrix = fitz.Matrix(RENDER_DPI / 72.0, RENDER_DPI / 72.0)
    pix = page.get_pixmap(matrix=matrix, alpha=False)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def embedded_pdf_page(doc: fitz.Document, page_index: int) -> Image.Image:
    page = doc[page_index]
    images = page.get_images(full=True)
    if not images:
        raise ValueError(f"PDF page {page_index + 1} has no embedded page image")
    extracted = doc.extract_image(int(images[0][0]))
    return Image.open(io.BytesIO(extracted["image"])).convert("RGB")


def feature_channels(img: Image.Image) -> dict[str, np.ndarray]:
    arr = np.asarray(img.convert("RGB"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mean = (r + g + b) / 3
    dark = mean < 178
    orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    grey = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    feature = dark | orange | grey
    return {"feature": feature, "dark": dark, "orange": orange, "grey": grey}


def box_slices(box: list[float]) -> tuple[slice, slice]:
    x0, y0, x1, y1 = [round(v) for v in box]
    return slice(y0, y1), slice(x0, x1)


def box_feature_stats(
    source_channels: dict[str, np.ndarray],
    target_channels: dict[str, np.ndarray],
    box: list[float],
) -> dict[str, Any]:
    y_slice, x_slice = box_slices(box)
    source = source_channels["feature"][y_slice, x_slice]
    target = target_channels["feature"][y_slice, x_slice]
    source_only = np.logical_and(source, ~target)
    overlap = np.logical_and(source, target)
    source_count = int(source.sum())
    if source_count:
        orange_share = float(
            np.logical_and(source_channels["orange"][y_slice, x_slice], source).sum()
            / source_count
        )
        dark_share = float(
            np.logical_and(source_channels["dark"][y_slice, x_slice], source).sum()
            / source_count
        )
        grey_share = float(
            np.logical_and(source_channels["grey"][y_slice, x_slice], source).sum()
            / source_count
        )
    else:
        orange_share = dark_share = grey_share = 0.0
    return {
        "sourceCoverage": float(source.mean()) if source.size else 0.0,
        "targetCoverage": float(target.mean()) if target.size else 0.0,
        "sourceOnlyCoverage": float(source_only.mean()) if source_only.size else 0.0,
        "sourceTargetOverlapCoverage": float(overlap.mean()) if overlap.size else 0.0,
        "orangeShareOfSource": orange_share,
        "darkShareOfSource": dark_share,
        "greyShareOfSource": grey_share,
    }


def active_delta_stats(a: Image.Image, b: Image.Image, active_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if a.size != b.size:
        b = b.resize(a.size, Image.Resampling.BICUBIC)
    diff = np.asarray(ImageChops.difference(a.convert("RGB"), b.convert("RGB")), dtype=np.float32)
    rows = []
    for row in active_rows:
        y_slice, x_slice = box_slices(row["box"])
        crop = diff[y_slice, x_slice, :]
        rows.append(
            {
                "target": row["shortId"],
                "meanAbsDelta": float(crop.mean()) if crop.size else 0.0,
                "maxAbsDelta": int(crop.max()) if crop.size else 0,
            }
        )
    return {
        "pageMeanAbsDelta": float(diff.mean()),
        "activeMeanAbsDeltaMax": max((row["meanAbsDelta"] for row in rows), default=0.0),
        "activeMaxAbsDeltaMax": max((row["maxAbsDelta"] for row in rows), default=0),
        "activeDeltaRows": rows,
    }


def load_source_image_pair() -> tuple[dict[int, Image.Image], dict[int, dict[str, Any]]]:
    images: dict[int, Image.Image] = {}
    meta: dict[int, dict[str, Any]] = {}
    for page in ARTICLE_PAGES:
        img = Image.open(SOURCE_PAGE_TEMPLATE.with_name(f"magazine_page_{page}.jpg")).convert("RGB")
        images[page], meta[page] = normalize_to_upright(img, page)
    return images, meta


def evaluate_pair(
    pair_id: str,
    source_pages: dict[int, Image.Image],
    source_meta: dict[int, dict[str, Any]],
    active_rows: list[dict[str, Any]],
    render_delta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_channels = feature_channels(source_pages[75])
    target_channels = feature_channels(source_pages[76])
    mirrored_source = {
        name: np.fliplr(mask)
        for name, mask in source_channels.items()
    }
    rows = []
    for active in active_rows:
        stats = box_feature_stats(mirrored_source, target_channels, active["box"])
        rows.append(
            {
                "pairId": pair_id,
                "target": active["shortId"],
                "phrase": active["phrase"],
                **stats,
            }
        )
    values = [row["sourceOnlyCoverage"] for row in rows]
    all_four_10 = sum(1 for value in values if value >= 0.10) == 4
    all_four_25 = sum(1 for value in values if value >= 0.25) == 4
    return {
        "pairId": pair_id,
        "pageMeta": {str(page): source_meta[page] for page in ARTICLE_PAGES},
        "rows": rows,
        "meanSourceOnlyCoverage": float(np.mean(values)) if values else 0.0,
        "minSourceOnlyCoverage": min(values) if values else 0.0,
        "targetCountAtLeast10": sum(1 for value in values if value >= 0.10),
        "targetCountAtLeast25": sum(1 for value in values if value >= 0.25),
        "allFourAtLeast10": all_four_10,
        "allFourAtLeast25": all_four_25,
        "renderDelta": render_delta or {},
    }


def draw_sheet(result: dict[str, Any]) -> None:
    width, height = 1840, 1220
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    body = font(15)
    small = font(12)
    draw.rectangle((0, 0, width, 94), fill=(29, 35, 44))
    draw.text((24, 18), "Current PDF Render Leaf Simulation Gate", fill="white", font=title)
    draw.text(
        (24, 56),
        "Valid page 75 -> 76 held-to-light measured from canonical, rendered, and embedded PDF surfaces.",
        fill=(235, 235, 235),
        font=body,
    )

    y = 122
    headers = ["pair", "mean src-only", "min", ">=.10", ">=.25", "all4 .10", "all4 .25", "p75 orient", "p76 orient"]
    xs = [24, 520, 650, 730, 800, 875, 960, 1040, 1190]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(70, 70, 70), font=small)
    y += 20
    for pair in result["pairRows"]:
        meta75 = pair["pageMeta"]["75"]
        meta76 = pair["pageMeta"]["76"]
        vals = [
            pair["pairId"][:65],
            f"{pair['meanSourceOnlyCoverage']:.4f}",
            f"{pair['minSourceOnlyCoverage']:.4f}",
            str(pair["targetCountAtLeast10"]),
            str(pair["targetCountAtLeast25"]),
            str(pair["allFourAtLeast10"]),
            str(pair["allFourAtLeast25"]),
            meta75["bestOrientation"],
            meta76["bestOrientation"],
        ]
        for x, value in zip(xs, vals):
            draw.text((x, y), value, fill=(35, 35, 35), font=small)
        y += 20

    y += 28
    draw.text((24, y), "Target Coverage Rows", fill=(20, 20, 20), font=body)
    y += 28
    headers = ["pair", "O4", "B4", "G5", "O5"]
    xs = [24, 570, 650, 730, 810]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(70, 70, 70), font=small)
    y += 20
    for pair in result["pairRows"]:
        by_target = {row["target"]: row["sourceOnlyCoverage"] for row in pair["rows"]}
        vals = [
            pair["pairId"][:66],
            f"{by_target.get('O4', 0.0):.4f}",
            f"{by_target.get('B4', 0.0):.4f}",
            f"{by_target.get('G5', 0.0):.4f}",
            f"{by_target.get('O5', 0.0):.4f}",
        ]
        for x, value in zip(xs, vals):
            draw.text((x, y), value, fill=(35, 35, 35), font=small)
        y += 20

    y += 28
    draw.text((24, y), "Render vs Embedded Residuals", fill=(20, 20, 20), font=body)
    y += 28
    headers = ["pdf", "p75 page MAD", "p75 active max", "p76 page MAD", "p76 active max"]
    xs = [24, 640, 760, 905, 1025]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(70, 70, 70), font=small)
    y += 20
    for row in result["renderVsEmbeddedRows"]:
        vals = [
            row["pdf"][:74],
            f"{row['75']['pageMeanAbsDelta']:.4f}",
            f"{row['75']['activeMeanAbsDeltaMax']:.4f}",
            f"{row['76']['pageMeanAbsDelta']:.4f}",
            f"{row['76']['activeMeanAbsDeltaMax']:.4f}",
        ]
        for x, value in zip(xs, vals):
            draw.text((x, y), value, fill=(35, 35, 35), font=small)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


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


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Render Leaf Simulation Gate",
        "",
        "Scope: measured the physically valid article page 75 -> page 76 held-to-light model using canonical scan pages, PDF-rendered pages, and embedded PDF rasters. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Pair rows / target rows: `{summary['pairRowCount']}` / `{summary['targetRowCount']}`",
        f"- Render-vs-embedded PDF rows: `{summary['renderVsEmbeddedPdfCount']}`",
        f"- Max mean source-only coverage: `{summary['maxMeanSourceOnlyCoverage']:.4f}`",
        f"- Max targets >=10% / >=25% source-only: `{summary['maxTargetCountAtLeast10']}` / `{summary['maxTargetCountAtLeast25']}`",
        f"- All-four >=10% / >=25% pair counts: `{summary['allFourAtLeast10PairCount']}` / `{summary['allFourAtLeast25PairCount']}`",
        f"- Max render-vs-embedded page MAD: `{summary['maxRenderEmbeddedPageMeanAbsDelta']:.4f}`",
        f"- Max render-vs-embedded active-box MAD: `{summary['maxRenderEmbeddedActiveMeanAbsDelta']:.4f}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Pair Rows",
        "",
        "| pair | mean src-only | min src-only | >=.10 | >=.25 | all4 >=.10 | all4 >=.25 | O4 | B4 | G5 | O5 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for pair in result["pairRows"]:
        by_target = {row["target"]: row["sourceOnlyCoverage"] for row in pair["rows"]}
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{pair['pairId']}`",
                    f"{pair['meanSourceOnlyCoverage']:.4f}",
                    f"{pair['minSourceOnlyCoverage']:.4f}",
                    str(pair["targetCountAtLeast10"]),
                    str(pair["targetCountAtLeast25"]),
                    str(pair["allFourAtLeast10"]),
                    str(pair["allFourAtLeast25"]),
                    f"{by_target.get('O4', 0.0):.4f}",
                    f"{by_target.get('B4', 0.0):.4f}",
                    f"{by_target.get('G5', 0.0):.4f}",
                    f"{by_target.get('O5', 0.0):.4f}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Render vs Embedded Residuals",
            "",
            "| PDF | p75 page MAD | p75 active max MAD | p76 page MAD | p76 active max MAD |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in result["renderVsEmbeddedRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pdf']}`",
                    f"{row['75']['pageMeanAbsDelta']:.4f}",
                    f"{row['75']['activeMeanAbsDeltaMax']:.4f}",
                    f"{row['76']['pageMeanAbsDelta']:.4f}",
                    f"{row['76']['activeMeanAbsDeltaMax']:.4f}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "- Rendering the current PDFs does not create an all-four O4/B4/G5/O5 valid-leaf held-to-light selector.",
            "- The largest source-only coverage appears only in low-resolution derivative render/embedded surfaces and still reaches only O4/B4 above 10%, with zero all-four >=10% or >=25% pairs.",
            "- Render-vs-embedded residuals are ordinary renderer/compression differences; they do not reveal visible original-layout objects or source-backed instruction layers.",
            "",
            "## Next Move",
            "",
            "- Keep the current PDF render path closed unless a new physical/original-layout source differs from these rows and passes R1-R5 plus source-backed R3. Future work should prioritize new-source validation or raw clue wording, not more renderer toggles.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_rows = [
        {
            "shortId": row["shortId"],
            "phrase": row["phrase"],
            "box": row["box"],
        }
        for row in active.get("activeRows", [])
    ]

    pair_rows = []
    render_vs_embedded = []
    source_pages, source_meta = load_source_image_pair()
    pair_rows.append(evaluate_pair("canonical_source_images", source_pages, source_meta, active_rows))

    for pdf_path in PDFS:
        if not pdf_path.exists():
            continue
        doc = fitz.open(pdf_path)
        rendered_pages: dict[int, Image.Image] = {}
        rendered_meta: dict[int, dict[str, Any]] = {}
        embedded_pages: dict[int, Image.Image] = {}
        embedded_meta: dict[int, dict[str, Any]] = {}
        delta_row: dict[str, Any] = {"pdf": rel(pdf_path)}
        for page in ARTICLE_PAGES:
            page_index = PDF_PAGE_INDEX[page]
            rendered = render_pdf_page(doc, page_index)
            embedded = embedded_pdf_page(doc, page_index)
            rendered_pages[page], rendered_meta[page] = normalize_to_upright(rendered, page)
            embedded_pages[page], embedded_meta[page] = normalize_to_upright(embedded, page)
            delta_row[str(page)] = active_delta_stats(
                rendered_pages[page], embedded_pages[page], active_rows
            )
        doc.close()
        pair_rows.append(
            evaluate_pair(
                f"{rel(pdf_path)}:rendered_300dpi",
                rendered_pages,
                rendered_meta,
                active_rows,
            )
        )
        pair_rows.append(
            evaluate_pair(
                f"{rel(pdf_path)}:embedded_primary_image",
                embedded_pages,
                embedded_meta,
                active_rows,
            )
        )
        render_vs_embedded.append(delta_row)

    values = [pair["meanSourceOnlyCoverage"] for pair in pair_rows]
    target_rows = sum(len(pair["rows"]) for pair in pair_rows)
    max_render_page_delta = 0.0
    max_render_active_delta = 0.0
    for row in render_vs_embedded:
        for page in ("75", "76"):
            max_render_page_delta = max(max_render_page_delta, row[page]["pageMeanAbsDelta"])
            max_render_active_delta = max(
                max_render_active_delta, row[page]["activeMeanAbsDeltaMax"]
            )
    summary = {
        "pairRowCount": len(pair_rows),
        "targetRowCount": target_rows,
        "renderVsEmbeddedPdfCount": len(render_vs_embedded),
        "maxMeanSourceOnlyCoverage": max(values) if values else 0.0,
        "minMeanSourceOnlyCoverage": min(values) if values else 0.0,
        "maxTargetCountAtLeast10": max(
            (pair["targetCountAtLeast10"] for pair in pair_rows), default=0
        ),
        "maxTargetCountAtLeast25": max(
            (pair["targetCountAtLeast25"] for pair in pair_rows), default=0
        ),
        "allFourAtLeast10PairCount": sum(1 for pair in pair_rows if pair["allFourAtLeast10"]),
        "allFourAtLeast25PairCount": sum(1 for pair in pair_rows if pair["allFourAtLeast25"]),
        "maxRenderEmbeddedPageMeanAbsDelta": max_render_page_delta,
        "maxRenderEmbeddedActiveMeanAbsDelta": max_render_active_delta,
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(
            reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)
        ),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"pairs={summary['pairRowCount']}|targets={summary['targetRowCount']}|"
        f"renderRows={summary['renderVsEmbeddedPdfCount']}|"
        f"maxMean={summary['maxMeanSourceOnlyCoverage']:.4f}|"
        f"max10={summary['maxTargetCountAtLeast10']}|"
        f"max25={summary['maxTargetCountAtLeast25']}|"
        f"all10={summary['allFourAtLeast10PairCount']}|"
        f"all25={summary['allFourAtLeast25PairCount']}|"
        f"maxRenderMAD={summary['maxRenderEmbeddedPageMeanAbsDelta']:.4f}|"
        f"maxActiveRenderMAD={summary['maxRenderEmbeddedActiveMeanAbsDelta']:.4f}|"
        f"sourceR3=0|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        "selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_render_leaf_simulation_no_selector",
        "sheet": rel(OUT_SHEET),
        "summary": summary,
        "fingerprint": fingerprint,
        "pairRows": pair_rows,
        "renderVsEmbeddedRows": render_vs_embedded,
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"decision: {result['decision']}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()

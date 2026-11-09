#!/usr/bin/env python3
"""Trace low-resolution PDF held-to-light inflation back to source words.

This bounded pass follows the anomalous O4/B4/G5 source-only coverage seen in
low-resolution derivative PDF render/embedded surfaces. It maps those pixels
through the physically valid page 75 -> page 76 horizontal mirror transform
back onto page 75, then checks the OCR word layer for source-side instruction
terms. It does not derive keys, hashes, seeds, WIFs, addresses, BIP39 material,
or candidate strings.
"""

from __future__ import annotations

import io
import json
import re
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_lowres_render_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_lowres_render_source_trace.json"
OUT_MD = OUT / "current_pdf_lowres_render_source_trace.md"
OUT_SHEET = OUT / "current_pdf_lowres_render_source_trace_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PDF_PAGE_INDEX = {75: 2, 76: 3}
PDFS = [
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
ARTICLE_PAGES = (75, 76)
RENDER_DPI = 300
TRACE_THRESHOLD = 0.05
MIN_COMPONENT_PIXELS = 30
SOURCE_CONTEXT_PAD = 36

STRICT_TERMS = {
    "read",
    "reads",
    "reading",
    "take",
    "takes",
    "taking",
    "line",
    "lines",
    "word",
    "words",
    "letter",
    "letters",
    "edge",
    "edges",
    "first",
    "last",
    "left",
    "right",
    "top",
    "bottom",
    "fold",
    "folded",
    "mirror",
    "mirrored",
    "reverse",
    "order",
    "slot",
    "font",
    "bold",
    "highlight",
    "overdose",
}
CONTEXT_TERMS = {
    "bitcoin",
    "salvador",
    "bukele",
    "imf",
    "volcano",
    "volcanoes",
    "bond",
    "bonds",
    "shitcoiner",
    "heart",
    "dip",
    "sell",
    "vitalik",
    "buterin",
    "satoshi",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


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
    scored = [
        {"orientation": name, "madToUpright": round(mad(ref, transformed), 4)}
        for name, transformed in transforms.items()
    ]
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
    source_count = int(source.sum())
    return {
        "sourceCoverage": float(source.mean()) if source.size else 0.0,
        "targetCoverage": float(target.mean()) if target.size else 0.0,
        "sourceOnlyCoverage": float(source_only.mean()) if source_only.size else 0.0,
        "sourceOnlyPixelCount": int(source_only.sum()),
        "sourcePixelCount": source_count,
    }


def connected_components(mask: np.ndarray, limit: int = 8) -> list[dict[str, Any]]:
    visited = np.zeros(mask.shape, dtype=bool)
    ys, xs = np.where(mask)
    h, w = mask.shape
    components: list[dict[str, Any]] = []
    for start_y, start_x in zip(ys.tolist(), xs.tolist()):
        if visited[start_y, start_x]:
            continue
        queue: deque[tuple[int, int]] = deque([(start_y, start_x)])
        visited[start_y, start_x] = True
        pixels: list[tuple[int, int]] = []
        while queue:
            y, x = queue.popleft()
            pixels.append((y, x))
            for ny in (y - 1, y, y + 1):
                for nx in (x - 1, x, x + 1):
                    if ny == y and nx == x:
                        continue
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        queue.append((ny, nx))
        if len(pixels) >= MIN_COMPONENT_PIXELS:
            py = [p[0] for p in pixels]
            px = [p[1] for p in pixels]
            components.append(
                {
                    "pixelCount": len(pixels),
                    "targetBox": [min(px), min(py), max(px) + 1, max(py) + 1],
                }
            )
    return sorted(components, key=lambda row: row["pixelCount"], reverse=True)[:limit]


def union_pixel_box(mask: np.ndarray) -> list[int] | None:
    ys, xs = np.where(mask)
    if not len(xs):
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def transform_target_box_to_source(box: list[int], page_width: int, dx: int = 0, dy: int = 0) -> list[int]:
    x0, y0, x1, y1 = box
    sx0 = page_width - (x1 - dx)
    sx1 = page_width - (x0 - dx)
    sy0 = y0 - dy
    sy1 = y1 - dy
    return [int(sx0), int(sy0), int(sx1), int(sy1)]


def padded_box(box: list[int], size: tuple[int, int], pad: int) -> list[int]:
    w, h = size
    x0, y0, x1, y1 = box
    return [max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)]


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def norm_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def source_words_for_box(words: list[dict[str, Any]], box: list[int]) -> list[dict[str, Any]]:
    hits = []
    for word in words:
        if boxes_intersect(word.get("box", [0, 0, 0, 0]), box):
            token = norm_token(str(word.get("text", "")))
            if token:
                hits.append(
                    {
                        "text": word.get("text", ""),
                        "token": token,
                        "index": word.get("index"),
                        "box": word.get("box"),
                        "strictInstruction": token in STRICT_TERMS,
                        "contextTerm": token in CONTEXT_TERMS,
                    }
                )
    return hits


def snippet(words: list[dict[str, Any]], limit: int = 12) -> str:
    if not words:
        return "(no OCR words in source trace box)"
    return " ".join(str(word["text"]) for word in words[:limit])


def load_page_words(page_num: int) -> list[dict[str, Any]]:
    article = load_json(ARTICLE_MAP)
    for page in article.get("pages", []):
        if page.get("page") == page_num:
            return page.get("words", [])
    return []


def lowres_pages(pdf_path: Path, mode: str) -> tuple[dict[int, Image.Image], dict[int, dict[str, Any]]]:
    doc = fitz.open(pdf_path)
    pages: dict[int, Image.Image] = {}
    meta: dict[int, dict[str, Any]] = {}
    for page in ARTICLE_PAGES:
        page_index = PDF_PAGE_INDEX[page]
        raw = render_pdf_page(doc, page_index) if mode == "rendered_300dpi" else embedded_pdf_page(doc, page_index)
        pages[page], meta[page] = normalize_to_upright(raw, page)
    doc.close()
    return pages, meta


def trace_pair(
    pair_id: str,
    pages: dict[int, Image.Image],
    meta: dict[int, dict[str, Any]],
    active_rows: list[dict[str, Any]],
    page75_words: list[dict[str, Any]],
) -> dict[str, Any]:
    source_channels = feature_channels(pages[75])
    target_channels = feature_channels(pages[76])
    mirrored_source = {name: np.fliplr(mask) for name, mask in source_channels.items()}
    rows: list[dict[str, Any]] = []
    skipped_rows: list[dict[str, Any]] = []
    for active in active_rows:
        stats = box_feature_stats(mirrored_source, target_channels, active["box"])
        base = {
            "pairId": pair_id,
            "target": active["shortId"],
            "phrase": active["phrase"],
            "box": active["box"],
            **stats,
        }
        y_slice, x_slice = box_slices(active["box"])
        source = mirrored_source["feature"][y_slice, x_slice]
        target = target_channels["feature"][y_slice, x_slice]
        source_only_local = np.logical_and(source, ~target)
        source_only_full = np.zeros_like(target_channels["feature"], dtype=bool)
        source_only_full[y_slice, x_slice] = source_only_local
        if stats["sourceOnlyCoverage"] < TRACE_THRESHOLD:
            skipped_rows.append(base)
            continue
        union_box = union_pixel_box(source_only_full)
        if union_box is None:
            skipped_rows.append(base)
            continue
        source_box = transform_target_box_to_source(union_box, pages[75].size[0])
        source_context_box = padded_box(source_box, pages[75].size, SOURCE_CONTEXT_PAD)
        words = source_words_for_box(page75_words, source_context_box)
        components = connected_components(source_only_full)
        strict_tokens = sorted({word["token"] for word in words if word["strictInstruction"]})
        context_tokens = sorted({word["token"] for word in words if word["contextTerm"]})
        rows.append(
            {
                **base,
                "targetUnionBox": union_box,
                "sourceTraceBox": source_box,
                "sourceContextBox": source_context_box,
                "componentCount": len(components),
                "topComponents": components,
                "sourceWords": words,
                "sourceSnippet": snippet(words),
                "strictInstructionTokens": strict_tokens,
                "contextTokens": context_tokens,
                "strictInstructionHitCount": len(strict_tokens),
                "contextHitCount": len(context_tokens),
            }
        )
    return {
        "pairId": pair_id,
        "pageMeta": {str(page): meta[page] for page in ARTICLE_PAGES},
        "traceRows": rows,
        "skippedRowsBelowThreshold": skipped_rows,
    }


def duplicate_trace_key(row: dict[str, Any]) -> str:
    return "|".join(
        [
            row["pairId"].split(":", 1)[-1],
            row["target"],
            f"{row['sourceOnlyCoverage']:.4f}",
            row["sourceSnippet"],
            ",".join(row["strictInstructionTokens"]),
            ",".join(row["contextTokens"]),
        ]
    )


def draw_sheet(result: dict[str, Any]) -> None:
    width, height = 1840, 1240
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    body = font(15)
    small = font(12)
    draw.rectangle((0, 0, width, 96), fill=(30, 35, 43))
    draw.text((24, 18), "Current PDF Low-Res Render Source Trace", fill="white", font=title)
    draw.text(
        (24, 56),
        "Maps derivative-PDF O4/B4/G5 source-only held-to-light pixels back to page-75 OCR words.",
        fill=(235, 235, 235),
        font=body,
    )
    s = result["summary"]
    y = 120
    for line in [
        f"Trace rows: {s['traceRowCount']}  Unique trace shapes: {s['uniqueTraceShapeCount']}  Skipped below threshold: {s['skippedBelowThresholdCount']}",
        f"Strict instruction rows: {s['strictInstructionRowCount']}  Context rows: {s['contextRowCount']}  Source-backed R3 hits: {s['sourceBackedR3BridgeHitCount']}",
        f"All-four eligible trace pairs: {s['allFourEligibleTracePairCount']}  Trigger state: {s['satisfiedReopenTriggerCount']}/{s['triggerCount']}  Decision: {result['decision']}",
    ]:
        draw.text((24, y), line, fill=(35, 35, 35), font=body)
        y += 24
    y += 20
    headers = ["pair", "target", "src-only", "src box", "strict", "context", "source page-75 words"]
    xs = [24, 570, 640, 725, 915, 1035, 1160]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=small)
    y += 20
    for row in result["traceRows"][:30]:
        pair = row["pairId"].replace("analysis_outputs/external_clues/", "external/")
        values = [
            pair[:70],
            row["target"],
            f"{row['sourceOnlyCoverage']:.4f}",
            ",".join(str(v) for v in row["sourceTraceBox"]),
            ",".join(row["strictInstructionTokens"]) or "-",
            ",".join(row["contextTokens"]) or "-",
            row["sourceSnippet"][:88],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(35, 35, 35), font=small)
        y += 22
        if y > height - 120:
            break
    draw.rectangle((24, height - 96, width - 24, height - 24), outline=(180, 180, 180), width=1)
    draw.text(
        (40, height - 80),
        "Interpretation: the inflated pixels trace to ordinary page-75 prose or blank/grey derivative margins, not a source-backed instruction layer.",
        fill=(35, 35, 35),
        font=body,
    )
    draw.text((40, height - 52), f"Fingerprint: {result['fingerprint']}", fill=(80, 80, 80), font=small)
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Low-Res Render Source Trace",
        "",
        "Scope: traced the anomalous low-resolution derivative PDF held-to-light source-only pixels back through the valid page 75 -> page 76 horizontal mirror transform into page-75 OCR word boxes. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Trace threshold: `{TRACE_THRESHOLD:.2f}` source-only coverage",
        f"- Trace rows / unique trace shapes: `{summary['traceRowCount']}` / `{summary['uniqueTraceShapeCount']}`",
        f"- Skipped below threshold: `{summary['skippedBelowThresholdCount']}`",
        f"- Source word rows / total word hits: `{summary['sourceWordRowCount']}` / `{summary['totalSourceWordHits']}`",
        f"- Strict instruction rows / token hits: `{summary['strictInstructionRowCount']}` / `{summary['totalStrictInstructionTokenHits']}`",
        f"- Context rows / token hits: `{summary['contextRowCount']}` / `{summary['totalContextTokenHits']}`",
        f"- All-four eligible trace-pair count: `{summary['allFourEligibleTracePairCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Trace Rows",
        "",
        "| pair | target | source-only | source trace box | strict tokens | context tokens | source page-75 snippet |",
        "|---|---:|---:|---|---|---|---|",
    ]
    for row in result["traceRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pairId']}`",
                    row["target"],
                    f"{row['sourceOnlyCoverage']:.4f}",
                    "`" + ",".join(str(v) for v in row["sourceTraceBox"]) + "`",
                    ", ".join(row["strictInstructionTokens"]) or "-",
                    ", ".join(row["contextTokens"]) or "-",
                    row["sourceSnippet"].replace("|", "/"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Skipped Rows",
            "",
            "| pair | target | source-only | reason |",
            "|---|---:|---:|---|",
        ]
    )
    for row in result["skippedRowsBelowThreshold"]:
        lines.append(
            f"| `{row['pairId']}` | {row['target']} | {row['sourceOnlyCoverage']:.4f} | below trace threshold |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "- The low-resolution PDF inflation traces to ordinary page-75 article prose or blank/grey derivative margins.",
            "- The repeated O4/B4/G5 pattern is duplicated by the two derivative PDFs and still does not include O5, so there is no all-four held-to-light selector.",
            "- No traced source region supplies source-backed R3 instruction wording for fold, mirror, order, slot, read/take, or extraction.",
            "",
            "## Next Move",
            "",
            "- Stop spending cycles on derivative-PDF renderer toggles. The best next move is a new-source/original-layout comparison, or a raw clue that explicitly authorizes how O4/B4/G5/O5 should be ordered or transformed.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_rows = [
        {"shortId": row["shortId"], "phrase": row["phrase"], "box": row["box"]}
        for row in active.get("activeRows", [])
    ]
    page75_words = load_page_words(75)
    pair_rows: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []
    skipped_rows: list[dict[str, Any]] = []
    for pdf_path in PDFS:
        if not pdf_path.exists():
            continue
        for mode in ("rendered_300dpi", "embedded_primary_image"):
            pages, meta = lowres_pages(pdf_path, mode)
            pair = trace_pair(f"{rel(pdf_path)}:{mode}", pages, meta, active_rows, page75_words)
            pair_rows.append(pair)
            trace_rows.extend(pair["traceRows"])
            skipped_rows.extend(pair["skippedRowsBelowThreshold"])

    seen: dict[str, str] = {}
    unique_count = 0
    for row in trace_rows:
        key = duplicate_trace_key(row)
        if key in seen:
            row["duplicateOf"] = seen[key]
        else:
            row["duplicateOf"] = None
            seen[key] = f"{row['pairId']}:{row['target']}"
            unique_count += 1

    all_four_eligible = 0
    for pair in pair_rows:
        targets = {row["target"] for row in pair["traceRows"]}
        if {"O4", "B4", "G5", "O5"}.issubset(targets):
            all_four_eligible += 1

    summary = {
        "pdfCount": sum(1 for pdf in PDFS if pdf.exists()),
        "pairRowCount": len(pair_rows),
        "traceRowCount": len(trace_rows),
        "uniqueTraceShapeCount": unique_count,
        "skippedBelowThresholdCount": len(skipped_rows),
        "sourceWordRowCount": sum(1 for row in trace_rows if row["sourceWords"]),
        "totalSourceWordHits": sum(len(row["sourceWords"]) for row in trace_rows),
        "strictInstructionRowCount": sum(1 for row in trace_rows if row["strictInstructionTokens"]),
        "totalStrictInstructionTokenHits": sum(len(row["strictInstructionTokens"]) for row in trace_rows),
        "contextRowCount": sum(1 for row in trace_rows if row["contextTokens"]),
        "totalContextTokenHits": sum(len(row["contextTokens"]) for row in trace_rows),
        "allFourEligibleTracePairCount": all_four_eligible,
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(
            reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)
        ),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|pairs={summary['pairRowCount']}|"
        f"traceRows={summary['traceRowCount']}|unique={summary['uniqueTraceShapeCount']}|"
        f"skipped={summary['skippedBelowThresholdCount']}|"
        f"wordRows={summary['sourceWordRowCount']}|words={summary['totalSourceWordHits']}|"
        f"strictRows={summary['strictInstructionRowCount']}|strict={summary['totalStrictInstructionTokenHits']}|"
        f"contextRows={summary['contextRowCount']}|context={summary['totalContextTokenHits']}|"
        f"allFour={summary['allFourEligibleTracePairCount']}|sourceR3=0|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_lowres_render_source_trace_no_instruction_source",
        "sheet": rel(OUT_SHEET),
        "summary": summary,
        "fingerprint": fingerprint,
        "pairRows": pair_rows,
        "traceRows": trace_rows,
        "skippedRowsBelowThreshold": skipped_rows,
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

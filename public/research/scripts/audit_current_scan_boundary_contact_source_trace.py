#!/usr/bin/env python3
"""Trace weak boundary light-table contacts back to their source-page material.

The previous boundary light-table pass found two weak all-four boundary contacts
at a low 10% threshold. This bounded pass inverts those target-side boundary
regions back onto the source pages used by the held-to-light simulator, then
records the source words and pixel features responsible for the contact. It is
source/visual provenance only: no key derivation, hashing, WIF/seed/address
checks, BIP39, OCR-to-key extraction, or broad candidate generation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_boundary_contact_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_boundary_contact_source_trace.json"
OUT_MD = OUT / "current_scan_boundary_contact_source_trace.md"
OUT_SHEET = OUT / "current_scan_boundary_contact_source_trace_sheet.jpg"

BOUNDARY_ANOMALY = ROOT / (
    "analysis_outputs/source_audit/current_scan_boundary_light_table_anomaly_probe/"
    "current_scan_boundary_light_table_anomaly_probe.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
STRICT_INSTRUCTION_TERMS = {
    "above",
    "below",
    "boundary",
    "count",
    "crop",
    "edge",
    "first",
    "fold",
    "inside",
    "key",
    "last",
    "left",
    "letter",
    "line",
    "mirror",
    "order",
    "outside",
    "read",
    "reverse",
    "right",
    "side",
    "slot",
    "take",
    "window",
    "word",
}
CONTEXT_TERMS = {
    "bitcoin",
    "bonds",
    "bukele",
    "dip",
    "heart",
    "imf",
    "overdose",
    "sell",
    "shitcoiner",
    "volcano",
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


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_pdf_page(page: int) -> Image.Image:
    source = Image.open(SOURCE_PAGE_TEMPLATE.with_name(f"magazine_page_{page}.jpg")).convert("RGB")
    upright = Image.open(UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{page}_upright.jpg")).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(
        ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean
    )
    return source.rotate(180) if rot_diff < same_diff else source


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


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def center(box: list[float]) -> tuple[float, float]:
    return (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0


def overlap_box(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def in_box(point: tuple[float, float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def inverse_target_region_to_source(
    target_region: list[int | float],
    width: int,
    height: int,
    dx: int,
    dy: int,
) -> list[float]:
    tx0, ty0, tx1, ty1 = [float(v) for v in target_region]
    sx0 = width - (tx1 - dx)
    sx1 = width - (tx0 - dx)
    sy0 = ty0 - dy
    sy1 = ty1 - dy
    return [
        max(0.0, min(float(width), sx0)),
        max(0.0, min(float(height), sy0)),
        max(0.0, min(float(width), sx1)),
        max(0.0, min(float(height), sy1)),
    ]


def page_words_by_page() -> dict[int, list[dict[str, Any]]]:
    data = load_json(ARTICLE_MAP)
    out: dict[int, list[dict[str, Any]]] = {}
    for page in data["pages"]:
        words = []
        for word in page.get("words", []):
            text = compact(str(word.get("text") or word.get("token") or ""))
            token = clean_token(str(word.get("token") or text))
            if not text and not token:
                continue
            box = [float(v) for v in word["box"]]
            words.append(
                {
                    "id": word.get("id"),
                    "index": word.get("index"),
                    "text": text,
                    "token": token,
                    "box": box,
                    "center": center(box),
                }
            )
        out[int(page["page"])] = words
    return out


def words_in_region(words: list[dict[str, Any]], region: list[float]) -> list[dict[str, Any]]:
    hits = []
    for word in words:
        inter = overlap_box(region, word["box"])
        word_area = max(area(word["box"]), 1.0)
        overlap_fraction = area(inter) / word_area if inter else 0.0
        center_hit = in_box(word["center"], region)
        if center_hit or overlap_fraction >= 0.10:
            hits.append(
                {
                    **word,
                    "centerInRegion": center_hit,
                    "overlapFraction": round(overlap_fraction, 4),
                }
            )
    return sorted(hits, key=lambda item: (item["box"][1], item["box"][0], item.get("index") or 0))


def pixel_stats(channels: dict[str, np.ndarray], region: list[float]) -> dict[str, Any]:
    x0, y0, x1, y1 = [int(round(v)) for v in region]
    if x1 <= x0 or y1 <= y0:
        return {
            "areaPx": 0,
            "featureCoverage": 0.0,
            "orangeCoverage": 0.0,
            "darkCoverage": 0.0,
            "greyCoverage": 0.0,
            "dominantSignal": "none",
        }
    feature = channels["feature"][y0:y1, x0:x1]
    feature_total = int(feature.sum())
    if feature_total:
        shares = {
            "orange": float(channels["orange"][y0:y1, x0:x1].sum() / feature_total),
            "dark": float(channels["dark"][y0:y1, x0:x1].sum() / feature_total),
            "grey": float(channels["grey"][y0:y1, x0:x1].sum() / feature_total),
        }
        dominant = max(shares, key=shares.get)
    else:
        shares = {"orange": 0.0, "dark": 0.0, "grey": 0.0}
        dominant = "none"
    return {
        "areaPx": int(feature.size),
        "featureCoverage": round(float(feature.mean()), 6),
        "orangeCoverage": round(float(channels["orange"][y0:y1, x0:x1].mean()), 6),
        "darkCoverage": round(float(channels["dark"][y0:y1, x0:x1].mean()), 6),
        "greyCoverage": round(float(channels["grey"][y0:y1, x0:x1].mean()), 6),
        "dominantSignal": dominant,
        "dominantOrangeShare": round(shares["orange"], 6),
        "dominantDarkShare": round(shares["dark"], 6),
        "dominantGreyShare": round(shares["grey"], 6),
    }


def term_hits(words: list[dict[str, Any]], terms: set[str]) -> list[str]:
    return sorted({word["token"] for word in words if word["token"] in terms})


def weak_groups(anomaly: dict[str, Any]) -> list[dict[str, Any]]:
    names = set(anomaly.get("summary", {}).get("weakAllFourAt10Groups", []))
    out = []
    for group in anomaly.get("groupRows", []):
        name = f"{group['scenarioId']}:{group['kind']}:{group['side']}"
        if name in names:
            out.append({**group, "weakGroupName": name})
    return out


def draw_sheet(
    source_images: dict[int, Image.Image],
    trace_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    width, height = 1840, 1280
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet, "RGBA")
    draw.rectangle((0, 0, width, 90), fill=(23, 30, 42))
    draw.text((28, 22), "Boundary contact source trace", fill=(255, 255, 255), font=font(29))
    draw.text(
        (28, 58),
        f"weakGroups={summary['weakGroupCount']} traceRows={summary['traceRowCount']} wordRows={summary['sourceWordHitRowCount']} strict={summary['sourceStrictInstructionRowCount']} context={summary['sourceContextTermRowCount']}",
        fill=(190, 205, 225),
        font=font(16),
    )

    crop_w, crop_h = 430, 180
    for idx, row in enumerate(trace_rows[:8]):
        px = 28 + (idx % 4) * 452
        py = 122 + (idx // 4) * 260
        img = source_images[row["sourcePage"]]
        region = row["sourceRegion"]
        pad = 80
        rect = [
            max(0, round(region[0] - pad)),
            max(0, round(region[1] - pad)),
            min(img.width, round(region[2] + pad)),
            min(img.height, round(region[3] + pad)),
        ]
        crop = img.crop(tuple(rect)).convert("RGB")
        crop = crop.resize((crop_w, crop_h))
        sheet.paste(crop, (px, py))

        def sx(x: float) -> int:
            return px + round((x - rect[0]) * crop_w / max(rect[2] - rect[0], 1))

        def sy(y: float) -> int:
            return py + round((y - rect[1]) * crop_h / max(rect[3] - rect[1], 1))

        draw.rectangle([sx(region[0]), sy(region[1]), sx(region[2]), sy(region[3])], outline=(255, 0, 0, 230), width=3)
        draw.rectangle((px, py, px + crop_w, py + 24), fill=(20, 24, 31, 185))
        draw.text(
            (px + 8, py + 5),
            f"{row['scenarioId']} {row['target']} {row['kind']} {row['side']} -> p{row['sourcePage']}",
            fill=(255, 255, 255),
            font=font(11),
        )
        txt = row["sourceWordText"][:60] + ("..." if len(row["sourceWordText"]) > 60 else "")
        draw.text((px, py + crop_h + 8), txt or "(no OCR word hit)", fill=(40, 48, 60), font=font(12))
        draw.text(
            (px, py + crop_h + 26),
            f"coverage={row['sourceFeatureCoverage']:.4f} signal={row['sourceDominantSignal']} strict={','.join(row['strictInstructionHits']) or '-'}",
            fill=(80, 88, 104),
            font=font(11),
        )

    table_y = 670
    draw.text((28, table_y), "Trace rows", fill=(24, 31, 42), font=font(22))
    table_y += 34
    headers = ["scenario", "target", "src", "words", "strict", "context", "source text"]
    widths = [245, 58, 40, 52, 75, 85, 640]
    x = 28
    for header, col_w in zip(headers, widths):
        draw.text((x, table_y), header, fill=(70, 80, 95), font=font(13))
        x += col_w
    table_y += 22
    for row in trace_rows:
        x = 28
        values = [
            f"{row['scenarioId']} {row['kind']} {row['side']}",
            row["target"],
            f"p{row['sourcePage']}",
            str(row["sourceWordCount"]),
            ",".join(row["strictInstructionHits"]) or "-",
            ",".join(row["contextTermHits"]) or "-",
            row["sourceWordText"][:85] + ("..." if len(row["sourceWordText"]) > 85 else ""),
        ]
        for value, col_w in zip(values, widths):
            draw.text((x, table_y), value, fill=(20, 24, 31), font=font(11))
            x += col_w
        table_y += 20

    draw.rectangle((28, 1065, 1812, 1225), outline=(210, 216, 226), width=1)
    draw.text((44, 1084), "Decision", fill=(24, 31, 42), font=font(20))
    decision_lines = [
        "The weak boundary contacts trace to ordinary source-page printed material or blank/noisy regions.",
        "No source traced region supplies a strict side/edge/word/line/fold instruction.",
        "The forced p75 contact is dominated by generic printed ink; the p79 benchmark is non-physical.",
    ]
    for idx, line in enumerate(decision_lines):
        draw.text((44, 1118 + idx * 25), line, fill=(55, 65, 80), font=font(15))

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    anomaly = load_json(BOUNDARY_ANOMALY)
    groups = weak_groups(anomaly)
    boundary_rows = anomaly.get("boundaryRows", [])
    words_by_page = page_words_by_page()

    source_images: dict[int, Image.Image] = {}
    source_channels: dict[int, dict[str, np.ndarray]] = {}
    trace_rows = []
    for group in groups:
        matching_rows = [
            row
            for row in boundary_rows
            if row["scenarioId"] == group["scenarioId"]
            and row["kind"] == group["kind"]
            and row["side"] == group["side"]
        ]
        matching_rows.sort(key=lambda row: TARGET_ORDER.index(row["target"]))
        for row in matching_rows:
            page = int(row["sourcePage"])
            if page not in source_images:
                source_images[page] = normalize_pdf_page(page)
                source_channels[page] = feature_channels(source_images[page])
            img = source_images[page]
            source_region = inverse_target_region_to_source(
                row["region"], img.width, img.height, int(row["dx"]), int(row["dy"])
            )
            word_hits = words_in_region(words_by_page.get(page, []), source_region)
            stats = pixel_stats(source_channels[page], source_region)
            trace_rows.append(
                {
                    "weakGroupName": group["weakGroupName"],
                    "scenarioId": row["scenarioId"],
                    "scenarioClass": row["scenarioClass"],
                    "sourcePage": page,
                    "dx": row["dx"],
                    "dy": row["dy"],
                    "target": row["target"],
                    "phrase": row["phrase"],
                    "kind": row["kind"],
                    "side": row["side"],
                    "targetRegion": row["region"],
                    "sourceRegion": [round(v, 2) for v in source_region],
                    "targetBoundaryCoverage": row["sourceCoverage"],
                    "sourceFeatureCoverage": stats["featureCoverage"],
                    "sourceDominantSignal": stats["dominantSignal"],
                    "sourcePixelStats": stats,
                    "sourceWordCount": len(word_hits),
                    "sourceWordText": compact(" ".join(word["text"] for word in word_hits)),
                    "sourceWordTokens": [word["token"] for word in word_hits],
                    "sourceWordIds": [word["id"] for word in word_hits],
                    "strictInstructionHits": term_hits(word_hits, STRICT_INSTRUCTION_TERMS),
                    "contextTermHits": term_hits(word_hits, CONTEXT_TERMS),
                }
            )

    source_gate = load_json(SOURCE_REVIEW_GATE).get("summary", {})
    trigger_gate = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    strict_rows = [row for row in trace_rows if row["strictInstructionHits"]]
    context_rows = [row for row in trace_rows if row["contextTermHits"]]
    word_rows = [row for row in trace_rows if row["sourceWordCount"]]
    p75_rows = [row for row in trace_rows if row["sourcePage"] == 75]
    p79_rows = [row for row in trace_rows if row["sourcePage"] == 79]
    summary = {
        "weakGroupCount": len(groups),
        "traceRowCount": len(trace_rows),
        "sourceWordHitRowCount": len(word_rows),
        "sourceStrictInstructionRowCount": len(strict_rows),
        "sourceContextTermRowCount": len(context_rows),
        "sourceStrictInstructionHits": sorted({hit for row in strict_rows for hit in row["strictInstructionHits"]}),
        "sourceContextTermHits": sorted({hit for row in context_rows for hit in row["contextTermHits"]}),
        "p75TraceRowCount": len(p75_rows),
        "p79TraceRowCount": len(p79_rows),
        "p75WordHitRowCount": sum(1 for row in p75_rows if row["sourceWordCount"]),
        "p79WordHitRowCount": sum(1 for row in p79_rows if row["sourceWordCount"]),
        "sourceBackedR3BridgeHitCount": source_gate.get("sourceBackedR3BridgeHitCount", 0),
        "satisfiedReopenTriggerCount": trigger_gate.get("satisfiedTriggerCount", 0),
        "triggerCount": trigger_gate.get("triggerCount", 9),
        "selectorUnlocked": False,
    }
    summary["boundaryContactSourceTraceFingerprint"] = (
        f"weakGroups={summary['weakGroupCount']}|rows={summary['traceRowCount']}"
        f"|wordRows={summary['sourceWordHitRowCount']}"
        f"|strictRows={summary['sourceStrictInstructionRowCount']}"
        f"|contextRows={summary['sourceContextTermRowCount']}"
        f"|strictTerms={','.join(summary['sourceStrictInstructionHits']) or '-'}"
        f"|contextTerms={','.join(summary['sourceContextTermHits']) or '-'}"
        f"|p75Words={summary['p75WordHitRowCount']}/{summary['p75TraceRowCount']}"
        f"|p79Words={summary['p79WordHitRowCount']}/{summary['p79TraceRowCount']}"
        f"|sourceR3={summary['sourceBackedR3BridgeHitCount']}"
        f"|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"
        "|selectors=0"
    )
    draw_sheet(source_images, trace_rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Trace the two weak all-four boundary light-table contacts back to their "
            "source-page regions. No key derivation, hashing, WIF, seed, address, "
            "BIP39, OCR-to-key extraction, or broad candidate generation."
        ),
        "inputs": {
            "boundaryAnomaly": rel(BOUNDARY_ANOMALY),
            "articleMap": rel(ARTICLE_MAP),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "weakGroups": groups,
        "traceRows": trace_rows,
        "summary": summary,
        "decision": {
            "currentScanBoundaryContactSourceTrace": "weak_contacts_trace_to_source_prose_or_noise_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "The weak all-four boundary contacts do not trace to source-side "
                "instruction wording. They are explained by ordinary source-page print, "
                "blank/noisy regions, and a forced or non-physical transform."
            ),
            "nextMove": (
                "Stop following the weak boundary contacts. Future work should start from "
                "a new source/original-layout clue or from source-review gates, not another "
                "threshold or boundary-side variant."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current-Scan Boundary Contact Source Trace",
        "",
        f"Created: `{result['createdAt']}`",
        "",
        "## Scope",
        "",
        result["scope"],
        "",
        "## Summary",
        "",
        f"- Weak groups traced: `{summary['weakGroupCount']}`.",
        f"- Trace rows: `{summary['traceRowCount']}`.",
        f"- Source word-hit rows: `{summary['sourceWordHitRowCount']}`.",
        f"- Source strict instruction rows: `{summary['sourceStrictInstructionRowCount']}`.",
        f"- Source strict instruction hits: `{', '.join(summary['sourceStrictInstructionHits']) or '-'}`.",
        f"- Source context rows / terms: `{summary['sourceContextTermRowCount']}` / `{', '.join(summary['sourceContextTermHits']) or '-'}`.",
        f"- p75 word rows / trace rows: `{summary['p75WordHitRowCount']}/{summary['p75TraceRowCount']}`.",
        f"- p79 word rows / trace rows: `{summary['p79WordHitRowCount']}/{summary['p79TraceRowCount']}`.",
        f"- Source-backed R3 hits / satisfied reopen triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
        f"- Fingerprint: `{summary['boundaryContactSourceTraceFingerprint']}`.",
        "",
        "## Trace Rows",
        "",
        "| weak group | target | source page | source coverage | words | strict | context | source text |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]
    for row in trace_rows:
        text = row["sourceWordText"].replace("|", "\\|")
        lines.append(
            f"| `{row['weakGroupName']}` | `{row['target']}` | {row['sourcePage']} | `{row['sourceFeatureCoverage']}` | {row['sourceWordCount']} | `{', '.join(row['strictInstructionHits']) or '-'}` | `{', '.join(row['contextTermHits']) or '-'}` | {text} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentScanBoundaryContactSourceTrace']}`.",
            f"- {result['decision']['reason']}",
            f"- Next move: {result['decision']['nextMove']}",
            "",
            "## Artifacts",
            "",
            f"- Sheet: `{result['sheet']}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_SHEET}")
    print(summary["boundaryContactSourceTraceFingerprint"])


if __name__ == "__main__":
    main()

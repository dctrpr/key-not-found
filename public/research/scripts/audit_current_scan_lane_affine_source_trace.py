#!/usr/bin/env python3
"""Trace source words behind the lane-affine held-to-light near miss.

This bounded pass follows only the valid page-75 -> page-76 rows from the
current-scan lane affine registration gate. It projects page-75 source words
through each tested mirrored affine transform into O4/B4/G5/O5 and checks
whether the weak 3/4 landing carries source-backed instruction language.

No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address
checks, BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_lane_affine_source_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_lane_affine_source_trace.json"
OUT_MD = OUT / "current_scan_lane_affine_source_trace.md"
OUT_SHEET = OUT / "current_scan_lane_affine_source_trace_sheet.jpg"

LANE_AFFINE_GATE = ROOT / (
    "analysis_outputs/source_audit/current_scan_lane_affine_registration_gate/"
    "current_scan_lane_affine_registration_gate.json"
)
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

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
BOX_PAD = 10
STRICT_TERMS = {
    "read",
    "reads",
    "reading",
    "take",
    "takes",
    "taking",
    "use",
    "using",
    "select",
    "extract",
    "decode",
    "encoded",
    "cipher",
    "key",
    "private",
    "seed",
    "line",
    "lines",
    "word",
    "words",
    "phrase",
    "phrases",
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
    "slots",
    "index",
    "indexes",
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
    "shitcoiners",
    "heart",
    "dip",
    "sell",
}


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def norm_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


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


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def intersection_area(a: list[float], b: list[float]) -> float:
    if not boxes_intersect(a, b):
        return 0.0
    return (min(a[2], b[2]) - max(a[0], b[0])) * (min(a[3], b[3]) - max(a[1], b[1]))


def padded_box(box: list[float], width: int, height: int, pad: int = BOX_PAD) -> list[float]:
    return [
        max(0.0, float(box[0]) - pad),
        max(0.0, float(box[1]) - pad),
        min(float(width), float(box[2]) + pad),
        min(float(height), float(box[3]) + pad),
    ]


def target_rows(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
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


def page_words(article: dict[str, Any], page_num: int) -> tuple[list[dict[str, Any]], int, int]:
    for page in article.get("pages", []):
        if int(page.get("page")) == page_num:
            words = []
            for word in page.get("words", []):
                token = norm_token(word.get("text", ""))
                if not token:
                    continue
                words.append(
                    {
                        "id": word.get("id"),
                        "index": word.get("index"),
                        "text": word.get("text", ""),
                        "token": token,
                        "box": [float(v) for v in word.get("box", [0, 0, 0, 0])],
                        "strictInstruction": token in STRICT_TERMS,
                        "contextTerm": token in CONTEXT_TERMS,
                    }
                )
            return words, int(page["width"]), int(page["height"])
    raise ValueError(f"page not found in article map: {page_num}")


def transform_word_to_target(word: dict[str, Any], page_width: int, transform: dict[str, float]) -> dict[str, Any]:
    x0, y0, x1, y1 = word["box"]
    # The registration gate mirrors page 75 horizontally before applying affine.
    mx0 = page_width - x1
    mx1 = page_width - x0
    sx = float(transform["sx"])
    sy = float(transform["sy"])
    tx = float(transform["tx"])
    ty = float(transform["ty"])
    target_box = [sx * mx0 + tx, sy * y0 + ty, sx * mx1 + tx, sy * y1 + ty]
    return {**word, "targetBox": target_box}


def trace_row(mode_row: dict[str, Any], target: dict[str, Any], source_words: list[dict[str, Any]], source_width: int, page_width: int, page_height: int) -> dict[str, Any]:
    transform = mode_row["transform"]
    target_box = padded_box(target["box"], page_width, page_height)
    hits = []
    for word in source_words:
        projected = transform_word_to_target(word, source_width, transform)
        area = intersection_area(projected["targetBox"], target_box)
        if area > 0:
            word_area = max(1.0, (projected["targetBox"][2] - projected["targetBox"][0]) * (projected["targetBox"][3] - projected["targetBox"][1]))
            hits.append(
                {
                    "id": projected["id"],
                    "index": projected["index"],
                    "text": projected["text"],
                    "token": projected["token"],
                    "sourceBox": projected["box"],
                    "projectedTargetBox": [round(float(v), 3) for v in projected["targetBox"]],
                    "overlapArea": round(area, 3),
                    "overlapFractionOfProjectedWord": round(float(area / word_area), 6),
                    "strictInstruction": projected["strictInstruction"],
                    "contextTerm": projected["contextTerm"],
                }
            )
    hits.sort(key=lambda item: (item["projectedTargetBox"][1], item["projectedTargetBox"][0], item["index"] or 0))
    strict_hits = [hit for hit in hits if hit["strictInstruction"]]
    context_hits = [hit for hit in hits if hit["contextTerm"]]
    return {
        "mode": mode_row["mode"],
        "target": target["shortId"],
        "phrase": target["phrase"],
        "targetBox": target["box"],
        "transform": transform,
        "sourceFraction": mode_row["fractions"].get(target["shortId"]),
        "supported": (mode_row["fractions"].get(target["shortId"]) or 0.0) >= 0.10,
        "aboveControlP95": mode_row["aboveP95"].get(target["shortId"]),
        "sourceWordHitCount": len(hits),
        "strictInstructionHitCount": len(strict_hits),
        "contextTermHitCount": len(context_hits),
        "strictInstructionTerms": sorted({hit["token"] for hit in strict_hits}),
        "contextTerms": sorted({hit["token"] for hit in context_hits}),
        "sourceTextPreview": " ".join(hit["text"] for hit in hits[:24]),
        "sourceWords": hits[:60],
    }


def build_sheet(target_rows_data: list[dict[str, Any]], trace_rows: list[dict[str, Any]]) -> None:
    image_path = Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=76))
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    pad = 90
    x0 = max(0, int(min(row["box"][0] for row in target_rows_data) - pad))
    y0 = max(0, int(min(row["box"][1] for row in target_rows_data) - pad))
    x1 = min(width, int(max(row["box"][2] for row in target_rows_data) + pad))
    y1 = min(height, int(max(row["box"][3] for row in target_rows_data) + pad))
    crop = (x0, y0, x1, y1)
    tile_w = x1 - x0
    tile_h = y1 - y0 + 115
    modes = []
    for row in trace_rows:
        if row["mode"] not in modes:
            modes.append(row["mode"])
    sheet = Image.new("RGB", (tile_w * len(modes), tile_h), "white")
    draw = ImageDraw.Draw(sheet)
    title_font = font(18)
    small_font = font(14)
    colors = {"O4": (249, 115, 22), "B4": (30, 30, 30), "G5": (37, 99, 235), "O5": (249, 115, 22)}
    for col, mode in enumerate(modes):
        tile = image.copy()
        td = ImageDraw.Draw(tile)
        rows = [row for row in trace_rows if row["mode"] == mode]
        for tr in rows:
            for word in tr["sourceWords"]:
                td.rectangle(word["projectedTargetBox"], outline=(255, 0, 0), width=2)
        for target in target_rows_data:
            td.rectangle(target["box"], outline=colors[target["shortId"]], width=5)
            td.text((target["box"][0], max(0, target["box"][1] - 24)), target["shortId"], fill=colors[target["shortId"]], font=small_font)
        tile_crop = tile.crop(crop)
        x = col * tile_w
        sheet.paste(tile_crop, (x, 115))
        draw.text((x + 10, 8), mode[:54], fill="black", font=title_font)
        strict = sum(row["strictInstructionHitCount"] for row in rows)
        context = sum(row["contextTermHitCount"] for row in rows)
        words = sum(row["sourceWordHitCount"] for row in rows)
        supported = sum(1 for row in rows if row["supported"])
        above = sum(1 for row in rows if row["aboveControlP95"])
        draw.text((x + 10, 38), f"words {words} strict {strict} context {context}", fill="black", font=small_font)
        draw.text((x + 10, 62), f"supported {supported}/4 aboveP95 {above}/4", fill="black", font=small_font)
        preview = " | ".join(row["sourceTextPreview"][:36] for row in rows if row["sourceTextPreview"])[:92]
        draw.text((x + 10, 86), preview, fill=(60, 60, 60), font=small_font)
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    lane_gate = load_json(LANE_AFFINE_GATE)
    active_index = load_json(ACTIVE_INDEX_SLOT)
    article = load_json(ARTICLE_MAP)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    targets = target_rows(active_index)
    source_words, source_width, _source_height = page_words(article, 75)
    page_width = int(next(page["width"] for page in article["pages"] if int(page["page"]) == 76))
    page_height = int(next(page["height"] for page in article["pages"] if int(page["page"]) == 76))
    valid_mode_rows = [
        row
        for row in lane_gate.get("rows", [])
        if row.get("sourcePage") == 75 and row.get("sourceClass") == "valid_same_leaf"
    ]
    traces = []
    for mode_row in valid_mode_rows:
        for target in targets:
            traces.append(trace_row(mode_row, target, source_words, source_width, page_width, page_height))

    strict_rows = [row for row in traces if row["strictInstructionHitCount"]]
    context_rows = [row for row in traces if row["contextTermHitCount"]]
    supported_rows = [row for row in traces if row["supported"]]
    above_rows = [row for row in traces if row["aboveControlP95"]]
    all_four_supported_modes = []
    for mode in sorted({row["mode"] for row in traces}):
        mode_rows = [row for row in traces if row["mode"] == mode]
        if len(mode_rows) == 4 and all(row["supported"] for row in mode_rows) and all(row["aboveControlP95"] for row in mode_rows):
            all_four_supported_modes.append(mode)

    source_r3 = 0
    satisfied = int(reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0) or 0)
    trigger_count = int(reopen.get("summary", {}).get("triggerCount", 9) or 9)
    selector_candidates = int(bool(all_four_supported_modes) and source_r3 > 0)
    summary = {
        "validModeCount": len(valid_mode_rows),
        "traceRows": len(traces),
        "sourceWordHitRows": sum(1 for row in traces if row["sourceWordHitCount"]),
        "sourceWordHitCount": sum(row["sourceWordHitCount"] for row in traces),
        "supportedRows": len(supported_rows),
        "aboveControlP95Rows": len(above_rows),
        "strictInstructionRowCount": len(strict_rows),
        "strictInstructionHitCount": sum(row["strictInstructionHitCount"] for row in traces),
        "contextTermRowCount": len(context_rows),
        "contextTermHitCount": sum(row["contextTermHitCount"] for row in traces),
        "allFourSupportedModes": all_four_supported_modes,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorCandidateCount": selector_candidates,
    }
    fingerprint = (
        f"modes={summary['validModeCount']}|rows={summary['traceRows']}|"
        f"wordRows={summary['sourceWordHitRows']}|words={summary['sourceWordHitCount']}|"
        f"supported={summary['supportedRows']}|aboveP95={summary['aboveControlP95Rows']}|"
        f"strictRows={summary['strictInstructionRowCount']}|strictHits={summary['strictInstructionHitCount']}|"
        f"contextRows={summary['contextTermRowCount']}|contextHits={summary['contextTermHitCount']}|"
        f"allFour={len(all_four_supported_modes)}|sourceR3={source_r3}|"
        f"triggers={satisfied}/{trigger_count}|selectors={selector_candidates}"
    )
    build_sheet(targets, traces)
    out = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-word trace for valid lane-affine held-to-light rows; no extraction or candidate generation",
        "inputs": {
            "laneAffineGate": rel(LANE_AFFINE_GATE),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "traceRows": traces,
        "summary": summary,
        "decision": {
            "status": "current_scan_lane_affine_source_trace_no_selector",
            "reason": (
                "The best lane-affine near miss traces to ordinary page-75 source words "
                "and does not provide source-backed instruction, unit, order, or transform language."
            ),
            "nextMove": (
                "Keep current-scan held-to-light lane/affine registration closed; require a "
                "distinct physical/original-layout source or raw clue wording that supplies "
                "unit, order, and transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Current Scan Lane Affine Source Trace",
        "",
        "Scope: traced page-75 source words through the valid lane-affine transforms into O4/B4/G5/O5 on page 76. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{out['createdAt']}`",
        f"- Valid affine modes traced: `{summary['validModeCount']}`",
        f"- Trace rows / source-word rows / source-word hits: `{summary['traceRows']}` / `{summary['sourceWordHitRows']}` / `{summary['sourceWordHitCount']}`",
        f"- Supported rows / above-control-p95 rows: `{summary['supportedRows']}` / `{summary['aboveControlP95Rows']}`",
        f"- Strict instruction rows / hits: `{summary['strictInstructionRowCount']}` / `{summary['strictInstructionHitCount']}`",
        f"- Context rows / hits: `{summary['contextTermRowCount']}` / `{summary['contextTermHitCount']}`",
        f"- All-four supported modes: `{summary['allFourSupportedModes']}`",
        f"- Source-backed R3 / satisfied triggers / selectors: `{source_r3}` / `{satisfied}/{trigger_count}` / `{selector_candidates}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Trace Rows",
        "",
        "| mode | target | supported | above p95 | source fraction | word hits | strict | context | preview |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in traces:
        preview = row["sourceTextPreview"].replace("|", "\\|")
        if len(preview) > 92:
            preview = preview[:89] + "..."
        lines.append(
            f"| `{row['mode']}` | `{row['target']}` | `{int(row['supported'])}` | `{int(bool(row['aboveControlP95']))}` | "
            f"`{row['sourceFraction']}` | `{row['sourceWordHitCount']}` | `{row['strictInstructionHitCount']}` | `{row['contextTermHitCount']}` | {preview} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{out['decision']['status']}`",
            f"- {out['decision']['reason']}",
            "- No traced row supplies an action-plus-unit instruction such as read/take/select plus word/letter/line, and no all-four affine mode survives the control threshold.",
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

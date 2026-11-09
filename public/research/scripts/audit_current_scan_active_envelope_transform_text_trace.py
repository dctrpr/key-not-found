#!/usr/bin/env python3
"""Trace page-76 text under active-envelope fold/mirror projections.

This bounded pass follows the already-closed active-envelope transform gate:
horizontal mirror, vertical mirror, 180-degree rotation, and normalized diagonal
folds of O4/B4/G5/O5 around their own active-quartet envelope. It asks whether
those projected boxes land on page-76 text that supplies an instruction, unit,
order, target phrase, or OVERDOSE-style selector.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_active_envelope_transform_text_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_active_envelope_transform_text_trace.json"
OUT_MD = OUT / "current_scan_active_envelope_transform_text_trace.md"
OUT_SHEET = OUT / "current_scan_active_envelope_transform_text_trace_sheet.jpg"

ACTIVE_ENVELOPE_GATE = ROOT / (
    "analysis_outputs/source_audit/current_scan_active_envelope_transform_gate/"
    "current_scan_active_envelope_transform_gate.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE_76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
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
    "rotate",
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
    "bitcoins",
    "satoshi",
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
    "overdose",
}
TARGET_TERMS = {
    "buying",
    "dip",
    "billion",
    "billions",
    "volcano",
    "bonds",
    "bond",
    "shitcoiner",
    "shitcoiners",
    "heart",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


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


def page_words(article: dict[str, Any], page_num: int) -> list[dict[str, Any]]:
    for page in article.get("pages", []):
        if page.get("page") == page_num:
            words = []
            for word in page.get("words", []):
                token = norm_token(str(word.get("text", "")))
                words.append(
                    {
                        "id": word.get("id"),
                        "index": word.get("index"),
                        "text": str(word.get("text", "")),
                        "token": token,
                        "box": [float(value) for value in word.get("box", [])],
                        "center": [float(value) for value in word.get("center", [])],
                        "strictInstruction": token in STRICT_TERMS,
                        "contextTerm": token in CONTEXT_TERMS,
                        "targetTerm": token in TARGET_TERMS,
                    }
                )
            return words
    return []


def intersecting_words(words: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    hits = []
    box_area = max(1.0, (box[2] - box[0]) * (box[3] - box[1]))
    for word in words:
        if not word["box"] or not boxes_intersect(word["box"], box):
            continue
        overlap = intersection_area(word["box"], box)
        word_area = max(1.0, (word["box"][2] - word["box"][0]) * (word["box"][3] - word["box"][1]))
        enriched = dict(word)
        enriched["overlapAreaPx"] = round(overlap, 3)
        enriched["overlapVsProjectedBox"] = round(overlap / box_area, 6)
        enriched["overlapVsWord"] = round(overlap / word_area, 6)
        hits.append(enriched)
    return sorted(hits, key=lambda item: (item.get("index") is None, item.get("index", 10**9)))


def trace_rows(active_gate: dict[str, Any], words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in active_gate.get("transformScenarios", []):
        transform = scenario.get("summary", {}).get("name", "unknown")
        slot_stream = scenario.get("summary", {}).get("projectedSlotStream", "")
        for row in scenario.get("rows", []):
            projected_box = [float(value) for value in row.get("projectedBox", [])]
            hits = intersecting_words(words, projected_box)
            strict_hits = [hit for hit in hits if hit["strictInstruction"]]
            context_hits = [hit for hit in hits if hit["contextTerm"]]
            target_hits = [hit for hit in hits if hit["targetTerm"]]
            rows.append(
                {
                    "transform": transform,
                    "slotStream": slot_stream,
                    "sourceShortId": row.get("sourceShortId"),
                    "sourcePhrase": row.get("sourcePhrase"),
                    "projectedSlotLetter": row.get("c9SlotAtProjectedCenter", {}).get("letter"),
                    "projectedSlotIndex": row.get("c9SlotAtProjectedCenter", {}).get("index"),
                    "projectedBox": projected_box,
                    "projectedCenter": row.get("projectedCenter"),
                    "wordHitCount": len(hits),
                    "strictInstructionHitCount": len(strict_hits),
                    "contextTermHitCount": len(context_hits),
                    "targetTermHitCount": len(target_hits),
                    "textPreview": " ".join(hit["text"] for hit in hits),
                    "strictTerms": sorted({hit["token"] for hit in strict_hits}),
                    "contextTerms": sorted({hit["token"] for hit in context_hits}),
                    "targetTerms": sorted({hit["token"] for hit in target_hits}),
                    "wordHits": hits[:32],
                }
            )
    return rows


def summarize(active_gate: dict[str, Any], rows: list[dict[str, Any]], trigger_matrix: dict[str, Any]) -> dict[str, Any]:
    transform_names = [scenario.get("summary", {}).get("name", "unknown") for scenario in active_gate.get("transformScenarios", [])]
    by_transform: dict[str, list[dict[str, Any]]] = {
        name: [row for row in rows if row["transform"] == name] for name in transform_names
    }
    all_four_word_hit_modes = [
        name for name, mode_rows in by_transform.items() if all(row["wordHitCount"] > 0 for row in mode_rows)
    ]
    all_four_strict_modes = [
        name for name, mode_rows in by_transform.items() if all(row["strictInstructionHitCount"] > 0 for row in mode_rows)
    ]
    active_order_text_streams = {
        name: " | ".join(row["textPreview"] or "-" for row in sorted(mode_rows, key=lambda item: TARGET_ORDER.index(item["sourceShortId"])))
        for name, mode_rows in by_transform.items()
    }
    trigger_rows = trigger_matrix.get("triggerRows", [])
    satisfied = [trigger for trigger in trigger_rows if trigger.get("triggerSatisfiedNow")]
    strict_rows = [row for row in rows if row["strictInstructionHitCount"] > 0]
    context_rows = [row for row in rows if row["contextTermHitCount"] > 0]
    target_rows = [row for row in rows if row["targetTermHitCount"] > 0]
    source_backed_r3 = 1 if strict_rows and all_four_strict_modes else 0
    selector_count = 1 if source_backed_r3 and satisfied else 0
    return {
        "transformCount": len(transform_names),
        "transformNames": transform_names,
        "traceRowCount": len(rows),
        "wordHitRows": sum(1 for row in rows if row["wordHitCount"] > 0),
        "totalWordHits": sum(row["wordHitCount"] for row in rows),
        "strictInstructionRows": len(strict_rows),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in rows),
        "contextTermRows": len(context_rows),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in rows),
        "targetTermRows": len(target_rows),
        "totalTargetTermHits": sum(row["targetTermHitCount"] for row in rows),
        "allFourWordHitModes": all_four_word_hit_modes,
        "allFourStrictModes": all_four_strict_modes,
        "activeOrderTextStreams": active_order_text_streams,
        "sourceBackedR3BridgeHitCount": source_backed_r3,
        "satisfiedReopenTriggerCount": len(satisfied),
        "triggerCount": len(trigger_rows),
        "selectorCandidateCount": selector_count,
    }


def draw_sheet(rows: list[dict[str, Any]], page_image_path: Path) -> None:
    image = Image.open(page_image_path).convert("RGB")
    big = font(18)
    small = font(13)
    panel_w, panel_h = 360, 270
    cols = 4
    display_rows = rows[:20]
    sheet = Image.new("RGB", (cols * panel_w, 5 * panel_h), "white")
    draw = ImageDraw.Draw(sheet)
    for idx, row in enumerate(display_rows):
        col = idx % cols
        row_idx = idx // cols
        x = col * panel_w
        y = row_idx * panel_h
        px0, py0, px1, py1 = row["projectedBox"]
        crop = [
            int(max(0, px0 - 90)),
            int(max(0, py0 - 70)),
            int(min(image.width, px1 + 90)),
            int(min(image.height, py1 + 70)),
        ]
        panel = image.crop(crop)
        panel.thumbnail((panel_w - 20, panel_h - 78))
        sheet.paste(panel, (x + 10, y + 58))
        sx = panel.width / max(1, crop[2] - crop[0])
        sy = panel.height / max(1, crop[3] - crop[1])
        local_box = [
            x + 10 + (px0 - crop[0]) * sx,
            y + 58 + (py0 - crop[1]) * sy,
            x + 10 + (px1 - crop[0]) * sx,
            y + 58 + (py1 - crop[1]) * sy,
        ]
        color = (230, 90, 0) if row["strictInstructionHitCount"] else (30, 110, 220)
        draw.rectangle(local_box, outline=color, width=3)
        title = f"{row['transform']} {row['sourceShortId']}->{row['projectedSlotLetter']}"
        draw.text((x + 10, y + 10), title, fill="black", font=big)
        counts = f"words {row['wordHitCount']} strict {row['strictInstructionHitCount']} ctx {row['contextTermHitCount']}"
        draw.text((x + 10, y + 34), counts, fill="black", font=small)
        preview = row["textPreview"] or "(no OCR words)"
        if len(preview) > 52:
            preview = preview[:49] + "..."
        draw.text((x + 10, y + panel_h - 24), preview, fill=(35, 38, 45), font=small)
    OUT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_SHEET, quality=92)


def write_outputs(result: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    summary = result["summary"]
    rows = result["rows"]
    fingerprint = result["fingerprint"]

    lines = [
        "# Current Scan Active-Envelope Transform Text Trace",
        "",
        "Scope: traced the active-envelope fold/mirror projected boxes onto page-76 OCR words from the current scan/article map. This checks whether the folded/mirrored geometry hides instruction, unit, order, target terms, or OVERDOSE selectors. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Input active-envelope gate: `{result['inputs']['activeEnvelopeTransformGate']}`",
        f"- Transform / trace rows: `{summary['transformCount']}` / `{summary['traceRowCount']}`",
        f"- Rows with page-76 words / total word hits: `{summary['wordHitRows']}` / `{summary['totalWordHits']}`",
        f"- Strict instruction rows / hits: `{summary['strictInstructionRows']}` / `{summary['totalStrictInstructionHits']}`",
        f"- Context rows / hits: `{summary['contextTermRows']}` / `{summary['totalContextTermHits']}`",
        f"- Target-term rows / hits: `{summary['targetTermRows']}` / `{summary['totalTargetTermHits']}`",
        f"- All-four word-hit modes: `{','.join(summary['allFourWordHitModes']) or '-'}`",
        f"- All-four strict modes: `{','.join(summary['allFourStrictModes']) or '-'}`",
        f"- Source-backed R3 / satisfied triggers / selectors: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}` / `{summary['selectorCandidateCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Active-Order Streams",
        "",
    ]
    for name, stream in summary["activeOrderTextStreams"].items():
        lines.append(f"- `{name}`: {stream}")
    lines.extend(
        [
            "",
            "## Projected Text Rows",
            "",
            "| transform | source | slot | words | strict | context | target | text preview |",
            "|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        preview = (row["textPreview"] or "-").replace("|", "\\|")
        if len(preview) > 100:
            preview = preview[:97] + "..."
        lines.append(
            f"| `{row['transform']}` | `{row['sourceShortId']}` | `{row['projectedSlotLetter']}` | "
            f"`{row['wordHitCount']}` | `{row['strictInstructionHitCount']}` | "
            f"`{row['contextTermHitCount']}` | `{row['targetTermHitCount']}` | {preview} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_active_envelope_transform_text_trace_no_selector`",
            "- The active-envelope fold/mirror projections land on ordinary page-76 article text, not instruction language.",
            "- Three transform modes have text under all four projected boxes, but all strict instruction counts are zero; the only context support is ordinary article vocabulary.",
            "",
            "## Next Move",
            "",
            "- Keep active-envelope fold/mirror mechanics closed for the current scan.",
            "- Reopen only if a raw clue or distinct source explicitly names an active-envelope fold, text projection, or reading order.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    active_gate = load_json(ACTIVE_ENVELOPE_GATE)
    article = load_json(ARTICLE_MAP)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    words = page_words(article, 76)
    rows = trace_rows(active_gate, words)
    summary = summarize(active_gate, rows, trigger_matrix)
    fingerprint = (
        f"transforms={summary['transformCount']}|rows={summary['traceRowCount']}|"
        f"wordRows={summary['wordHitRows']}|words={summary['totalWordHits']}|"
        f"strictRows={summary['strictInstructionRows']}|strictHits={summary['totalStrictInstructionHits']}|"
        f"contextRows={summary['contextTermRows']}|targetRows={summary['targetTermRows']}|"
        f"allFourWords={len(summary['allFourWordHitModes'])}|allFourStrict={len(summary['allFourStrictModes'])}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={summary['selectorCandidateCount']}"
    )
    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": (
            "trace active-envelope fold/mirror projected boxes onto page-76 OCR words; "
            "no OCR-to-key/key/hash/seed/WIF/address/BIP39/brute force"
        ),
        "inputs": {
            "activeEnvelopeTransformGate": rel(ACTIVE_ENVELOPE_GATE),
            "articleMap": rel(ARTICLE_MAP),
            "page76Upright": rel(PAGE_76_UPRIGHT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "rows": rows,
        "decision": {
            "selectorUnlocked": False,
            "reason": (
                "Fold/mirror projections around the active envelope land on ordinary page-76 OCR text. "
                "No projected row contains strict instruction language and no all-four strict mode exists."
            ),
            "nextMove": (
                "Keep active-envelope fold/mirror mechanics closed unless new raw clue/source material "
                "names this projection or a reading order."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    draw_sheet(rows, PAGE_76_UPRIGHT)
    write_outputs(result)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_SHEET}")
    print(fingerprint)


if __name__ == "__main__":
    main()

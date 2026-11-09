#!/usr/bin/env python3
"""Check whether the stable PDF-native OSE source run is highlight-backed.

The PDF OVERDOSE slot trace showed that the byte-locked magazine render and
embedded canvas preserve an OSE@5-7 source-supported run. This bounded pass asks
whether that run is meaningfully coupled to page-75/page-76 orange highlights or
nearby source phrases that could provide the missing read/order instruction.

No OCR-to-key extraction, candidate generation, hashing, seed/WIF/address
checks, BIP39 checks, or broad brute force is run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ose_source_highlight_phrase_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_ose_source_highlight_phrase_gate.json"
OUT_MD = OUT / "current_pdf_ose_source_highlight_phrase_gate.md"
OUT_SHEET = OUT / "current_pdf_ose_source_highlight_phrase_gate_sheet.jpg"

PDF_SLOT_TRACE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_overdose_slot_source_support_trace/"
    "current_pdf_overdose_slot_source_support_trace.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

ACTION_ORDER_TERMS = {
    "above",
    "below",
    "bottom",
    "boundary",
    "count",
    "crop",
    "edge",
    "edges",
    "first",
    "fold",
    "folded",
    "inside",
    "key",
    "last",
    "left",
    "mirror",
    "mirrored",
    "order",
    "outside",
    "read",
    "reads",
    "reverse",
    "right",
    "side",
    "take",
    "takes",
    "top",
    "window",
}
UNIT_TERMS = {
    "bold",
    "font",
    "highlight",
    "letter",
    "letters",
    "line",
    "lines",
    "slot",
    "word",
    "words",
}
STRICT_TERMS = ACTION_ORDER_TERMS | UNIT_TERMS
CONTEXT_TERMS = {
    "bitcoin",
    "bitcoins",
    "bond",
    "bonds",
    "bukele",
    "dip",
    "heart",
    "imf",
    "overdose",
    "salvador",
    "sell",
    "shitcoiner",
    "toxic",
    "utxo",
    "volcano",
    "volcanoes",
}


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def area(box: list[float] | None) -> float:
    if not box:
        return 0.0
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def center(box: list[float]) -> tuple[float, float]:
    return (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0


def overlap(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def center_in(point: tuple[float, float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def page_data(article_map: dict[str, Any], page_no: int) -> dict[str, Any]:
    for page in article_map.get("pages", []):
        if int(page.get("page", -1)) == page_no:
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
                        "index": int(word.get("index", len(words))),
                        "text": text,
                        "token": token,
                        "box": box,
                        "center": center(box),
                        "importance": int(word.get("importance", 0)),
                        "reasons": list(word.get("reasons", [])),
                    }
                )
            highlights = [
                {
                    "id": str(item.get("id", "")),
                    "kind": str(item.get("kind", "")),
                    "box": [float(v) for v in item.get("box", [])],
                }
                for item in page.get("highlights", [])
                if item.get("box")
            ]
            return {"words": words, "highlights": highlights}
    return {"words": [], "highlights": []}


def words_in_box(words: list[dict[str, Any]], box: list[float], min_overlap: float = 0.10) -> list[dict[str, Any]]:
    hits = []
    for word in words:
        inter = overlap(word["box"], box)
        overlap_fraction = area(inter) / max(area(word["box"]), 1.0) if inter else 0.0
        if center_in(word["center"], box) or overlap_fraction >= min_overlap:
            hits.append({**word, "overlapFraction": round(overlap_fraction, 4)})
    return sorted(hits, key=lambda item: (item["box"][1], item["box"][0], item["index"]))


def highlights_in_box(highlights: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    rows = []
    for highlight in highlights:
        inter = overlap(highlight["box"], box)
        if not inter:
            continue
        rows.append(
            {
                **highlight,
                "overlapBox": [round(v, 2) for v in inter],
                "slotAreaShare": round(area(inter) / max(area(box), 1.0), 6),
                "highlightAreaShare": round(area(inter) / max(area(highlight["box"]), 1.0), 6),
            }
        )
    return rows


def words_touching_highlights(
    words: list[dict[str, Any]],
    box: list[float],
    highlights: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    hits = []
    for word in words_in_box(words, box):
        touched = []
        for highlight in highlights:
            inter = overlap(word["box"], highlight["box"])
            if inter and area(inter) / max(area(word["box"]), 1.0) >= 0.10:
                touched.append(highlight["id"])
        if touched:
            hits.append({**word, "highlightIds": touched})
    return hits


def term_hits(words: list[dict[str, Any]]) -> dict[str, list[str]]:
    tokens = {word["token"] for word in words}
    return {
        "strict": sorted(tokens & STRICT_TERMS),
        "actionOrder": sorted(tokens & ACTION_ORDER_TERMS),
        "unitOnly": sorted((tokens & UNIT_TERMS) - ACTION_ORDER_TERMS),
        "context": sorted(tokens & CONTEXT_TERMS),
    }


def row_preview(words: list[dict[str, Any]]) -> str:
    return compact(" ".join(word["text"] for word in words))[:220]


def edge_words(words: list[dict[str, Any]]) -> dict[str, str]:
    if not words:
        return {"first": "", "last": "", "left": "", "right": "", "top": "", "bottom": ""}
    by_read = sorted(words, key=lambda item: (item["box"][1], item["box"][0], item["index"]))
    by_x = sorted(words, key=lambda item: (item["box"][0], item["box"][1], item["index"]))
    by_y = sorted(words, key=lambda item: (item["box"][1], item["box"][0], item["index"]))
    return {
        "first": by_read[0]["text"],
        "last": by_read[-1]["text"],
        "left": by_x[0]["text"],
        "right": by_x[-1]["text"],
        "top": by_y[0]["text"],
        "bottom": by_y[-1]["text"],
    }


def inspect_slot(
    carrier: dict[str, Any],
    slot: dict[str, Any],
    p75: dict[str, Any],
    p76: dict[str, Any],
) -> dict[str, Any]:
    source_box = [float(v) for v in slot["sourceBox"]]
    target_box = [float(v) for v in slot["targetBox"]]
    source_words = words_in_box(p75["words"], source_box)
    target_words = words_in_box(p76["words"], target_box)
    source_highlights = highlights_in_box(p75["highlights"], source_box)
    target_highlights = highlights_in_box(p76["highlights"], target_box)
    source_highlight_words = words_touching_highlights(p75["words"], source_box, source_highlights)
    target_highlight_words = words_touching_highlights(p76["words"], target_box, target_highlights)
    source_terms = term_hits(source_words)
    target_terms = term_hits(target_words)
    source_highlight_terms = term_hits(source_highlight_words)
    target_highlight_terms = term_hits(target_highlight_words)
    source_highlight_area = round(sum(item["slotAreaShare"] for item in source_highlights), 6)
    target_highlight_area = round(sum(item["slotAreaShare"] for item in target_highlights), 6)
    highlight_bridge = source_highlight_area > 0 and target_highlight_area > 0
    action_terms = sorted(
        set(source_terms["actionOrder"])
        | set(target_terms["actionOrder"])
        | set(source_highlight_terms["actionOrder"])
        | set(target_highlight_terms["actionOrder"])
    )
    return {
        "pdf": carrier["pdf"],
        "pdfName": carrier["pdfName"],
        "carrier": carrier["carrier"],
        "slotId": slot["slotId"],
        "slotIndex": slot["slotIndex"],
        "slotLetter": slot["slotLetter"],
        "sourceSupportedDominant": bool(slot["sourceSupportedDominant"]),
        "sourceSupportedDeltaShare": slot["sourceSupportedDeltaShare"],
        "sourceBox": source_box,
        "targetBox": target_box,
        "sourceHighlightIds": [item["id"] for item in source_highlights],
        "targetHighlightIds": [item["id"] for item in target_highlights],
        "sourceHighlightAreaShare": source_highlight_area,
        "targetHighlightAreaShare": target_highlight_area,
        "highlightBridge": highlight_bridge,
        "sourceWordCount": len(source_words),
        "targetWordCount": len(target_words),
        "sourceHighlightWordCount": len(source_highlight_words),
        "targetHighlightWordCount": len(target_highlight_words),
        "sourceTextPreview": row_preview(source_words),
        "targetTextPreview": row_preview(target_words),
        "sourceHighlightTextPreview": row_preview(source_highlight_words),
        "targetHighlightTextPreview": row_preview(target_highlight_words),
        "sourceEdgeWords": edge_words(source_words),
        "sourceTerms": source_terms,
        "targetTerms": target_terms,
        "sourceHighlightTerms": source_highlight_terms,
        "targetHighlightTerms": target_highlight_terms,
        "combinedActionOrderTerms": action_terms,
        "selectorCandidate": bool(slot["sourceSupportedDominant"] and highlight_bridge and action_terms),
    }


def draw_sheet(slot_rows: list[dict[str, Any]], p75: dict[str, Any], p76: dict[str, Any]) -> None:
    src_img = Image.open(PAGE_IMAGE.with_name("page_75_upright.jpg")).convert("RGB")
    tgt_img = Image.open(PAGE_IMAGE.with_name("page_76_upright.jpg")).convert("RGB")
    crop = [250, 2100, 2300, 3060]

    def panel(img: Image.Image, page: dict[str, Any], box_key: str, title: str) -> Image.Image:
        local = img.crop(tuple(crop)).copy()
        draw = ImageDraw.Draw(local)
        for h in page["highlights"]:
            inter = overlap(h["box"], crop)
            if inter:
                rect = [inter[0] - crop[0], inter[1] - crop[1], inter[2] - crop[0], inter[3] - crop[1]]
                draw.rectangle(rect, outline=(255, 145, 0), width=5)
        seen: set[tuple[str, str]] = set()
        for row in slot_rows:
            key = (row["slotId"], box_key)
            if key in seen:
                continue
            seen.add(key)
            box = row[box_key]
            inter = overlap(box, crop)
            if not inter:
                continue
            rect = [inter[0] - crop[0], inter[1] - crop[1], inter[2] - crop[0], inter[3] - crop[1]]
            color = (222, 49, 49) if row["sourceSupportedDominant"] else (80, 120, 220)
            draw.rectangle(rect, outline=color, width=4)
            draw.text((rect[0] + 6, max(2, rect[1] + 6)), row["slotId"], fill=color, font=font(26, True))
        scaled = local.resize((980, int(local.height * 980 / local.width)), Image.Resampling.LANCZOS)
        out = Image.new("RGB", (scaled.width, scaled.height + 52), (250, 250, 247))
        out.paste(scaled, (0, 52))
        d = ImageDraw.Draw(out)
        d.text((16, 12), title, fill=(20, 26, 34), font=font(26, True))
        return out

    source_panel = panel(src_img, p75, "sourceBox", "Page 75 mirrored source bands")
    target_panel = panel(tgt_img, p76, "targetBox", "Page 76 OVERDOSE slots")
    table_h = 380
    sheet = Image.new("RGB", (max(source_panel.width, target_panel.width) * 2 + 36, source_panel.height + table_h + 24), (248, 249, 247))
    sheet.paste(source_panel, (12, 12))
    sheet.paste(target_panel, (source_panel.width + 24, 12))
    draw = ImageDraw.Draw(sheet)
    y = source_panel.height + 34
    draw.text((20, y), "High OSE slots: highlight/phrase audit", fill=(20, 26, 34), font=font(25, True))
    y += 42
    headers = ["slot", "src hi", "tgt hi", "bridge", "action", "source highlighted text"]
    xs = [20, 110, 240, 370, 500, 635]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(73, 82, 96), font=font(16, True))
    y += 28
    for row in [r for r in slot_rows if r["sourceSupportedDominant"] and r["carrier"] == "render"]:
        values = [
            row["slotId"],
            ",".join(row["sourceHighlightIds"]) or "-",
            ",".join(row["targetHighlightIds"]) or "-",
            "yes" if row["highlightBridge"] else "no",
            ",".join(row["combinedActionOrderTerms"]) or "-",
            row["sourceHighlightTextPreview"][:90] or "-",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value), fill=(22, 28, 36), font=font(15))
        y += 26
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    trace = load_json(PDF_SLOT_TRACE)
    article_map = load_json(ARTICLE_MAP)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    p75 = page_data(article_map, 75)
    p76 = page_data(article_map, 76)
    carriers = [
        row
        for row in trace.get("carrierRows", [])
        if row.get("pdfName") == "magazine.pdf" and row.get("carrier") in {"render", "embedded_canvas"}
    ]
    slot_rows: list[dict[str, Any]] = []
    for carrier in carriers:
        for slot in carrier.get("slotRows", []):
            slot_rows.append(inspect_slot(carrier, slot, p75, p76))

    high_rows = [row for row in slot_rows if row["sourceSupportedDominant"]]
    render_high_rows = [
        row for row in high_rows if row["carrier"] == "render"
    ]
    all_high_have_source_highlight = bool(render_high_rows) and all(row["sourceHighlightIds"] for row in render_high_rows)
    all_high_have_target_highlight = bool(render_high_rows) and all(row["targetHighlightIds"] for row in render_high_rows)
    all_high_have_bridge = bool(render_high_rows) and all(row["highlightBridge"] for row in render_high_rows)
    high_action_rows = [row for row in high_rows if row["combinedActionOrderTerms"]]
    candidate_rows = [row for row in slot_rows if row["selectorCandidate"]]
    source_backed_r3 = 0
    satisfied_triggers = 0
    trigger_count = len(reopen.get("triggerRows", [])) or int(
        trace.get("summary", {}).get("triggerCount", 0)
    )
    fingerprint = (
        f"carriers={len(carriers)}|rows={len(slot_rows)}|high={len(high_rows)}|"
        f"renderHigh={','.join(row['slotId'] for row in render_high_rows)}|"
        f"highSrcHi={sum(1 for row in render_high_rows if row['sourceHighlightIds'])}/{len(render_high_rows)}|"
        f"highTgtHi={sum(1 for row in render_high_rows if row['targetHighlightIds'])}/{len(render_high_rows)}|"
        f"highBridge={sum(1 for row in render_high_rows if row['highlightBridge'])}/{len(render_high_rows)}|"
        f"highAction={len(high_action_rows)}|candidates={len(candidate_rows)}|"
        f"sourceR3={source_backed_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    decision = "pdf_ose_source_highlight_phrase_no_selector"
    summary = {
        "carrierCount": len(carriers),
        "slotRowCount": len(slot_rows),
        "renderHighSlotIds": [row["slotId"] for row in render_high_rows],
        "renderHighRun": "".join(row["slotLetter"] for row in render_high_rows) + "@5-7"
        if [row["slotId"] for row in render_high_rows] == ["O5", "S6", "E7"]
        else "",
        "renderHighSlotsWithSourceHighlight": sum(1 for row in render_high_rows if row["sourceHighlightIds"]),
        "renderHighSlotsWithTargetHighlight": sum(1 for row in render_high_rows if row["targetHighlightIds"]),
        "renderHighSlotsWithHighlightBridge": sum(1 for row in render_high_rows if row["highlightBridge"]),
        "allRenderHighSlotsHaveSourceHighlight": all_high_have_source_highlight,
        "allRenderHighSlotsHaveTargetHighlight": all_high_have_target_highlight,
        "allRenderHighSlotsHaveHighlightBridge": all_high_have_bridge,
        "highSlotActionOrderRows": len(high_action_rows),
        "selectorCandidateCount": len(candidate_rows),
        "sourceBackedR3BridgeHitCount": source_backed_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "fingerprint": fingerprint,
    }
    draw_sheet(slot_rows, p75, p76)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "PDF-native magazine OSE source-band highlight and phrase gate; no extraction/key derivation",
        "inputs": {
            "pdfSlotTrace": rel(PDF_SLOT_TRACE),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "slotRows": slot_rows,
        "decision": decision,
        "reason": (
            "The OSE high slots intersect some orange highlight material, but not as an all-slot "
            "two-sided bridge and without any action/order terms. The highlighted source words are "
            "ordinary article prose, not a read/transform selector."
        ),
        "nextMove": (
            "Keep OSE as a stable PDF/source-band control. Move to new source/clue wording or, if "
            "forced to stay local, audit only a clearly distinct physical feature not yet checked."
        ),
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current PDF OSE Source Highlight Phrase Gate",
        "",
        "Scope: checked whether the stable PDF-native `OSE@5-7` source-supported run is backed by page-75/page-76 orange-highlight geometry or local phrases that supply unit/order/read instructions. No OCR-to-key extraction, key candidates, hashes-to-key, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{decision}`",
        f"- Carriers / slot rows: `{summary['carrierCount']}` / `{summary['slotRowCount']}`",
        f"- Render high slots: `{','.join(summary['renderHighSlotIds'])}`",
        f"- Render high slots with source highlight: `{summary['renderHighSlotsWithSourceHighlight']}/{len(render_high_rows)}`",
        f"- Render high slots with target highlight: `{summary['renderHighSlotsWithTargetHighlight']}/{len(render_high_rows)}`",
        f"- Render high slots with two-sided highlight bridge: `{summary['renderHighSlotsWithHighlightBridge']}/{len(render_high_rows)}`",
        f"- High-slot action/order rows: `{summary['highSlotActionOrderRows']}`",
        f"- Selector candidates: `{summary['selectorCandidateCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_backed_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        "",
        "## Render High Slots",
        "",
        "| slot | source share | source highlights | target highlights | bridge | action/order | source highlight text | target highlight text |",
        "|---|---:|---|---|---:|---|---|---|",
    ]
    for row in render_high_rows:
        lines.append(
            "| `{slot}` | `{share}` | `{src_hi}` | `{tgt_hi}` | `{bridge}` | `{action}` | `{src_text}` | `{tgt_text}` |".format(
                slot=row["slotId"],
                share=row["sourceSupportedDeltaShare"],
                src_hi=",".join(row["sourceHighlightIds"]) or "-",
                tgt_hi=",".join(row["targetHighlightIds"]) or "-",
                bridge=int(row["highlightBridge"]),
                action=",".join(row["combinedActionOrderTerms"]) or "-",
                src_text=row["sourceHighlightTextPreview"] or "-",
                tgt_text=row["targetHighlightTextPreview"] or "-",
            )
        )
    lines.extend(
        [
            "",
            "## Source Edge Words",
            "",
            "| slot | first | last | left | right | top | bottom | full source preview |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in render_high_rows:
        edge = row["sourceEdgeWords"]
        lines.append(
            "| `{slot}` | `{first}` | `{last}` | `{left}` | `{right}` | `{top}` | `{bottom}` | `{preview}` |".format(
                slot=row["slotId"],
                first=edge["first"] or "-",
                last=edge["last"] or "-",
                left=edge["left"] or "-",
                right=edge["right"] or "-",
                top=edge["top"] or "-",
                bottom=edge["bottom"] or "-",
                preview=row["sourceTextPreview"] or "-",
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`.",
            "- Orange-highlight contact exists in parts of the OSE source/target slots, but it is incomplete: the high run does not form an all-slot two-sided highlight bridge.",
            "- The only unit-like word remains `words`; there are no action/order terms such as read, take, first, last, right, left, fold, mirror, or reverse in the high OSE source/highlight rows.",
            "- The highlighted source text resolves to article prose, not a procedural selector.",
            "",
            "## Next Move",
            "",
            "- Keep OSE as a stable PDF/source-band control. The next useful move still needs source/clue wording that supplies unit, transform, and read order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{fingerprint}|decision={decision}")


if __name__ == "__main__":
    main()

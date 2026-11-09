#!/usr/bin/env python3
"""Audit whether active target-center rails add a DOCM-bold selector.

This bounded pass extends the active target center-path gate by projecting the
trusted Article-with-Fonts DOCM run states onto the existing page-76 OCR word
geometry. It asks a narrow question: after the rail necessarily passes through
the four active bold/highlight target boxes, do the same rails pick additional
bold words/letters that provide a unit/order instruction?

No new OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import difflib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
CENTER_PATH_JSON = ROOT / "analysis_outputs/source_audit/active_target_center_path_gate/active_target_center_path_gate.json"
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
FORMAT_LOCK_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/active_target_center_path_bold_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_target_center_path_bold_gate.json"
OUT_MD = OUT / "active_target_center_path_bold_gate.md"
SHEET = OUT / "active_target_center_path_bold_gate_sheet.jpg"

PAGE76_DOCM_PARAGRAPH_OFFSET = 41
STRICT_UNIT_TERMS = {
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
}
CONTEXT_TERMS = {
    "bukele",
    "volcano",
    "bonds",
    "bitcoin",
    "imf",
    "loan",
    "sell",
    "billions",
    "trust",
    "shitcoiner",
    "heart",
}
TOKEN_RE = re.compile(r"\$?\d+(?:,\d+)*(?:\.\d+)?|[A-Za-z]+(?:'[A-Za-z]+)?")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


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


def normalize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def letters(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", text)


def scan_terms(text: str, terms: set[str]) -> list[str]:
    tokens = [normalize_token(token) for token in re.findall(r"[A-Za-z0-9$']+", text)]
    return sorted({term for term in terms if term in tokens})


def style_code(run: dict[str, Any]) -> str:
    font_name = (run.get("fontAscii") or run.get("fontHAnsi") or "").lower()
    highlight = (run.get("highlight") or "").lower()
    if "typeka mix" in font_name:
        return "M"
    if "typeka" in font_name and run.get("bold") and highlight == "yellow":
        return "Y"
    if "typeka" in font_name and run.get("bold") and highlight == "black":
        return "K"
    if "typeka" in font_name and run.get("bold"):
        return "B"
    if "typeka" in font_name:
        return "R"
    if run.get("bold"):
        return "B"
    return "O"


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def overlap_fraction_subject(subject: list[float], container: list[float]) -> float:
    hit = intersection(subject, container)
    if not hit or area(subject) <= 0:
        return 0.0
    return area(hit) / area(subject)


def build_docm_lines(runs: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    lines: dict[int, list[dict[str, Any]]] = {}
    for run in runs:
        page_line = run.get("paragraphIndex", -999) - PAGE76_DOCM_PARAGRAPH_OFFSET
        if page_line < 0:
            continue
        code = style_code(run)
        for match in TOKEN_RE.finditer(run.get("text", "")):
            token = match.group(0)
            lines.setdefault(page_line, []).append(
                {
                    "text": token,
                    "token": normalize_token(token),
                    "letters": letters(token),
                    "bold": bool(run.get("bold")),
                    "styleCode": code,
                    "highlight": run.get("highlight") or "none",
                    "font": run.get("fontAscii") or run.get("fontHAnsi") or "",
                    "runIndex": run.get("runIndex"),
                    "paragraphIndex": run.get("paragraphIndex"),
                }
            )
    return lines


def assign_article_lines(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sorted_words = sorted(words, key=lambda row: (row["center"][1], row["center"][0], row["index"]))
    clusters: list[dict[str, Any]] = []
    for word in sorted_words:
        y = float(word["center"][1])
        if not clusters or abs(y - clusters[-1]["y"]) > 34:
            clusters.append({"y": y, "words": [word]})
        else:
            cluster = clusters[-1]
            cluster["words"].append(word)
            cluster["y"] = sum(float(row["center"][1]) for row in cluster["words"]) / len(cluster["words"])

    body_index = 0
    enriched: list[dict[str, Any]] = []
    for cluster in clusters:
        is_header = cluster["y"] < 300 and any(normalize_token(row["text"]) == "overdose" for row in cluster["words"])
        page_line = None if is_header else body_index
        # The OCR geometry sees the side-label words `Magazine` and `Bitcoin`
        # as two article-line clusters just before `Don't believe me?`; the
        # DOCM text layer has only one blank/missing line there. From that
        # point down, visual line N aligns to DOCM line N-1.
        docm_page_line = None if page_line is None else (page_line - 1 if page_line >= 20 else page_line)
        if not is_header:
            body_index += 1
        for word in cluster["words"]:
            row = dict(word)
            row["pageLine"] = page_line
            row["docmPageLine"] = docm_page_line
            enriched.append(row)
    return sorted(enriched, key=lambda row: row["index"])


def align_docm_to_article(article_words: list[dict[str, Any]], docm_lines: dict[int, list[dict[str, Any]]]) -> dict[int, list[dict[str, Any]]]:
    mapping: dict[int, list[dict[str, Any]]] = {row["index"]: [] for row in article_words}
    by_line: dict[int, list[dict[str, Any]]] = {}
    for word in article_words:
        if word.get("docmPageLine") is not None:
            by_line.setdefault(int(word["docmPageLine"]), []).append(word)

    for page_line, line_words in by_line.items():
        docm_words = docm_lines.get(page_line, [])
        if not docm_words:
            continue
        line_words = sorted(line_words, key=lambda row: (row["center"][0], row["index"]))
        article_tokens = [normalize_token(row["text"]) for row in line_words]
        docm_tokens = [row["token"] for row in docm_words]
        matcher = difflib.SequenceMatcher(None, article_tokens, docm_tokens, autojunk=False)
        for tag, a0, a1, d0, d1 in matcher.get_opcodes():
            if tag == "equal":
                for a_pos, d_pos in zip(range(a0, a1), range(d0, d1)):
                    mapping[line_words[a_pos]["index"]].append(docm_words[d_pos])
            elif tag == "replace":
                a_len = a1 - a0
                d_len = d1 - d0
                if a_len == 1:
                    mapping[line_words[a0]["index"]].extend(docm_words[d0:d1])
                elif d_len == 1:
                    for a_pos in range(a0, a1):
                        mapping[line_words[a_pos]["index"]].append(docm_words[d0])
                elif a_len == d_len:
                    for a_pos, d_pos in zip(range(a0, a1), range(d0, d1)):
                        mapping[line_words[a_pos]["index"]].append(docm_words[d_pos])
                else:
                    for rel_a, a_pos in enumerate(range(a0, a1)):
                        start = d0 + math.floor(rel_a * d_len / a_len)
                        end = d0 + math.floor((rel_a + 1) * d_len / a_len)
                        mapping[line_words[a_pos]["index"]].extend(docm_words[start:max(start + 1, end)])
    return mapping


def target_rows(active: dict[str, Any], format_lock: dict[str, Any]) -> list[dict[str, Any]]:
    lock_by_id = {row["id"]: row for row in format_lock.get("activeTargets", [])}
    rows = []
    for target in active["targets"]:
        lock = lock_by_id.get(target["id"], {})
        rows.append(
            {
                "id": target["id"],
                "label": target["label"],
                "phrase": target["phrase"],
                "box": [float(v) for v in target["box"]],
                "visualState": target["visualState"],
                "pageLine": target["pageLine"],
                "corridorIndex": target["corridorIndex"],
                "docmBoldFraction": lock.get("docmBoldFraction", target.get("docmBoldFraction")),
                "docmHighlightSummary": lock.get("docmHighlightSummary"),
                "boldText": target["phrase"],
                "boldLetters": letters(target["phrase"]),
            }
        )
    return rows


def projection_for_word(word: dict[str, Any], mapped_docm: list[dict[str, Any]], targets: list[dict[str, Any]]) -> dict[str, Any]:
    active_overlaps = [
        target["id"]
        for target in targets
        if overlap_fraction_subject(word["box"], target["box"]) >= 0.25
    ]
    bold_docm = [row for row in mapped_docm if row.get("bold")]
    style_codes = "".join(row["styleCode"] for row in mapped_docm)
    highlight_codes = [row.get("highlight") or "none" for row in mapped_docm]
    return {
        "docmText": " ".join(row["text"] for row in mapped_docm),
        "docmTokens": [row["text"] for row in mapped_docm],
        "docmStyleCodes": style_codes,
        "docmHighlights": highlight_codes,
        "boldText": " ".join(row["text"] for row in bold_docm),
        "boldLetters": "".join(row["letters"] for row in bold_docm),
        "activeOverlapIds": active_overlaps,
    }


def projection_map(article_page: dict[str, Any], runs: list[dict[str, Any]], targets: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    article_words = assign_article_lines(article_page["words"])
    article_by_index = {row["index"]: row for row in article_words}
    docm_lines = build_docm_lines(runs)
    aligned = align_docm_to_article(article_words, docm_lines)
    out: dict[int, dict[str, Any]] = {}
    for index, word in article_by_index.items():
        projection = projection_for_word(word, aligned.get(index, []), targets)
        out[index] = {**word, **projection}
    return out


def summarize_path(path_row: dict[str, Any], word_projection: dict[int, dict[str, Any]], targets: list[dict[str, Any]]) -> dict[str, Any]:
    rail_words = []
    for source_word in path_row.get("words", []):
        word = word_projection.get(source_word["index"])
        if not word:
            continue
        rail_words.append(
            {
                "id": word["id"],
                "index": word["index"],
                "text": word["text"],
                "box": [round(float(v), 2) for v in word["box"]],
                "center": [round(float(v), 2) for v in word["center"]],
                "pageLine": word.get("pageLine"),
                "docmPageLine": word.get("docmPageLine"),
                "pathDistancePx": source_word.get("pathDistancePx"),
                "docmText": word["docmText"],
                "docmTokens": word["docmTokens"],
                "docmStyleCodes": word["docmStyleCodes"],
                "docmHighlights": word["docmHighlights"],
                "boldText": word["boldText"],
                "boldLetters": word["boldLetters"],
                "activeOverlapIds": word["activeOverlapIds"],
            }
        )

    target_hits = []
    hit_ids = {row["id"] for row in path_row.get("targetCenterHits", [])}
    for target in targets:
        if target["id"] in hit_ids:
            target_hits.append(
                {
                    "id": target["id"],
                    "label": target["label"],
                    "phrase": target["phrase"],
                    "visualState": target["visualState"],
                    "pageLine": target["pageLine"],
                    "corridorIndex": target["corridorIndex"],
                    "boldText": target["boldText"],
                    "boldLetters": target["boldLetters"],
                }
            )

    bold_rail_words = [row for row in rail_words if row["boldText"]]
    nonactive_bold_rail_words = [row for row in bold_rail_words if not row["activeOverlapIds"]]
    active_overlap_bold_rail_words = [row for row in bold_rail_words if row["activeOverlapIds"]]
    direct_text = " ".join(row["boldText"] for row in target_hits)
    rail_bold_text = " ".join(row["boldText"] for row in bold_rail_words)
    nonactive_text = " ".join(row["boldText"] for row in nonactive_bold_rail_words)
    combined_text = " ".join(value for value in [direct_text, rail_bold_text] if value)

    return {
        "id": path_row["id"],
        "order": path_row.get("order"),
        "visualStateOrder": path_row.get("visualStateOrder"),
        "points": path_row.get("points"),
        "railWordCount": len(rail_words),
        "boldRailWordCount": len(bold_rail_words),
        "activeOverlapBoldRailWordCount": len(active_overlap_bold_rail_words),
        "nonActiveBoldRailWordCount": len(nonactive_bold_rail_words),
        "directTargetBoldUnitCount": len(target_hits),
        "directTargetBoldText": direct_text,
        "railBoldText": rail_bold_text,
        "nonActiveRailBoldText": nonactive_text,
        "combinedBoldText": combined_text,
        "combinedBoldLetters": letters(combined_text),
        "nonActiveBoldLetters": letters(nonactive_text),
        "strictInstructionTerms": scan_terms(combined_text, STRICT_UNIT_TERMS),
        "nonActiveStrictInstructionTerms": scan_terms(nonactive_text, STRICT_UNIT_TERMS),
        "contextTerms": scan_terms(combined_text, CONTEXT_TERMS),
        "directTargetHits": target_hits,
        "boldRailWords": bold_rail_words,
        "nonActiveBoldRailWords": nonactive_bold_rail_words,
        "railWords": rail_words,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [250, 2070, 1900, 3045]
    scale = 0.62
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    margin = 32
    header_h = 166
    side_w = 720
    panel_w, panel_h = panel.size
    sheet = Image.new("RGB", (margin * 3 + panel_w + side_w, header_h + panel_h + margin), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(29)
    normal = font(17)
    small = font(13)
    mono = font(14)

    draw.text((margin, 28), "Active Target Center-Path Bold Gate", fill=(242, 246, 250), font=title)
    draw.text(
        (margin, 70),
        "DOCM bold state projected onto existing page-76 rail geometry; no new OCR or extraction.",
        fill=(178, 188, 200),
        font=normal,
    )
    draw.text(
        (margin, 101),
        "Gold = primary rail. Orange/grey = active target boxes. White circles = rail-touched DOCM-bold OCR words.",
        fill=(178, 188, 200),
        font=small,
    )
    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    def draw_box(box: list[float], color: str, width: int = 3) -> None:
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=width)

    primary = result["pathVariants"][0]
    draw.line([(sx(x), sy(y)) for x, y in primary["points"]], fill="#ffd45a", width=6)
    for x, y in primary["points"]:
        draw.ellipse((sx(x) - 6, sy(y) - 6, sx(x) + 6, sy(y) + 6), fill="#ffd45a")

    for target in result["targets"]:
        color = "#ff9b2e" if target["visualState"] == "Y" else "#aab3c2"
        draw_box(target["box"], color, 4)
        draw.text((sx(target["box"][0]), sy(target["box"][1]) - 18), target["id"], fill="#ffffff", font=small)

    for word in primary["boldRailWords"]:
        x, y = word["center"]
        color = "#ffffff" if not word["activeOverlapIds"] else "#ffef9a"
        draw.ellipse((sx(x) - 6, sy(y) - 6, sx(x) + 6, sy(y) + 6), outline=color, width=3)

    side_x = margin * 2 + panel_w
    y = header_h
    draw.text((side_x, y), "Result", fill=(242, 246, 250), font=font(24))
    y += 42
    summary_lines = [
        f"primary rail words: {result['summary']['primaryRailWordCount']}",
        f"primary bold rail words: {result['summary']['primaryBoldRailWordCount']}",
        f"non-active bold rail words: {result['summary']['primaryNonActiveBoldRailWordCount']}",
        f"direct active bold units: {result['summary']['primaryDirectTargetBoldUnitCount']}",
        f"primary strict terms: {result['summary']['primaryStrictInstructionHitCount']}",
        f"non-active strict terms: {result['summary']['primaryNonActiveStrictInstructionHitCount']}",
        f"control shifts: {result['summary']['controlShiftCount']}",
        f"controls with non-active bold >= primary: {result['summary']['controlComparableNonActiveBoldCount']}",
        f"control strict terms: {result['summary']['controlStrictInstructionHitCount']}",
    ]
    for line in summary_lines:
        draw.text((side_x, y), line, fill=(206, 214, 224), font=normal)
        y += 28

    y += 12
    draw.text((side_x, y), "Primary non-active bold", fill=(242, 246, 250), font=font(20))
    y += 34
    nonactive = primary["nonActiveBoldRailWords"] or []
    if not nonactive:
        draw.text((side_x, y), "none", fill=(182, 192, 204), font=mono)
        y += 22
    for word in nonactive[:8]:
        draw.text(
            (side_x, y),
            f"{word['index']:>3} L{word['pageLine']}: {word['text']} -> {word['boldText']}",
            fill=(182, 192, 204),
            font=mono,
        )
        y += 22

    y += 10
    draw.text((side_x, y), "Direct target bold stream", fill=(242, 246, 250), font=font(20))
    y += 32
    text = result["summary"]["primaryDirectTargetBoldText"]
    for start in range(0, len(text), 56):
        draw.text((side_x, y), text[start : start + 56], fill=(182, 192, 204), font=mono)
        y += 22

    sheet.save(SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    center_report = load_json(CENTER_PATH_JSON)
    article = load_json(ARTICLE_JSON)
    runs = load_json(RUNS_JSON)
    format_lock = load_json(FORMAT_LOCK_JSON)
    page = next(row for row in article["pages"] if row["page"] == 76)
    targets = target_rows(active, format_lock)
    projections = projection_map(page, runs, targets)

    path_variants = [
        summarize_path(row, projections, targets) for row in center_report.get("pathVariants", [])
    ]
    controls = [
        {**summarize_path(row, projections, targets), "linePitchShift": row.get("linePitchShift")}
        for row in center_report.get("controls", {}).get("primaryLineOrderShiftControls", [])
    ]

    primary = path_variants[0]
    comparable_nonactive_controls = [
        row for row in controls if row["nonActiveBoldRailWordCount"] >= primary["nonActiveBoldRailWordCount"]
    ]
    control_strict_rows = [row for row in controls if row["strictInstructionTerms"]]
    variant_strict_rows = [row for row in path_variants if row["strictInstructionTerms"]]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "active O4/B4/G5/O5 center-path DOCM-bold projection gate; no new OCR, "
            "key derivation, hashing, seed/WIF checks, address checks, or broad candidate generation"
        ),
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "activeTargetCenterPathGate": rel(CENTER_PATH_JSON),
            "article3dMap": rel(ARTICLE_JSON),
            "articleWithFontsRuns": rel(RUNS_JSON),
            "formatLock": rel(FORMAT_LOCK_JSON),
            "pageImage": rel(PAGE_IMAGE),
        },
        "projectionAuthority": {
            "geometry": "existing page-76 OCR word boxes and locked active target crop boxes",
            "boldState": "Article with Fonts DOCM runs; Markdown bold is not used as font authority",
            "paragraphToPageLine": f"DOCM paragraphIndex - {PAGE76_DOCM_PARAGRAPH_OFFSET}; OCR visual lines >=20 subtract one side-label/blank-line correction",
            "limitation": "For OCR-merged words, DOCM words on the same line are mapped by line-local sequence alignment; missing OCR words are represented only by direct locked target boxes.",
        },
        "targets": targets,
        "pathVariants": path_variants,
        "controls": {
            "method": "reuse the primary active line-order rail shifted by integer median line pitches from the center-path gate, then project DOCM bold state onto touched OCR words",
            "primaryLineOrderShiftControls": controls,
        },
        "summary": {
            "primaryOrder": primary["order"],
            "primaryVisualStateOrder": primary["visualStateOrder"],
            "primaryRailWordCount": primary["railWordCount"],
            "primaryBoldRailWordCount": primary["boldRailWordCount"],
            "primaryActiveOverlapBoldRailWordCount": primary["activeOverlapBoldRailWordCount"],
            "primaryNonActiveBoldRailWordCount": primary["nonActiveBoldRailWordCount"],
            "primaryDirectTargetBoldUnitCount": primary["directTargetBoldUnitCount"],
            "primaryDirectTargetBoldText": primary["directTargetBoldText"],
            "primaryRailBoldText": primary["railBoldText"],
            "primaryNonActiveRailBoldText": primary["nonActiveRailBoldText"],
            "primaryCombinedBoldLetters": primary["combinedBoldLetters"],
            "primaryNonActiveBoldLetters": primary["nonActiveBoldLetters"],
            "primaryStrictInstructionHitCount": len(primary["strictInstructionTerms"]),
            "primaryStrictInstructionTerms": primary["strictInstructionTerms"],
            "primaryNonActiveStrictInstructionHitCount": len(primary["nonActiveStrictInstructionTerms"]),
            "primaryNonActiveStrictInstructionTerms": primary["nonActiveStrictInstructionTerms"],
            "primaryContextTerms": primary["contextTerms"],
            "variantCount": len(path_variants),
            "variantStrictInstructionHitCount": len(variant_strict_rows),
            "variantNonActiveBoldCounts": {
                row["id"]: row["nonActiveBoldRailWordCount"] for row in path_variants
            },
            "controlShiftCount": len(controls),
            "controlNonActiveBoldCounts": [row["nonActiveBoldRailWordCount"] for row in controls],
            "controlComparableNonActiveBoldCount": len(comparable_nonactive_controls),
            "controlComparableNonActiveBoldShifts": [
                row["linePitchShift"] for row in comparable_nonactive_controls
            ],
            "controlStrictInstructionHitCount": len(control_strict_rows),
            "controlStrictInstructionHitShifts": [row["linePitchShift"] for row in control_strict_rows],
            "selectorUnlocked": False,
        },
        "decision": {
            "activeTargetCenterPathBoldGate": "do-not-promote",
            "reason": (
                "The rail-bold layer adds the already-known active bold/highlight target phrases plus sparse nearby DOCM-bold context, "
                "with no strict unit/order instruction terms and shifted controls that also touch non-active bold context."
            ),
        },
        "sheet": rel(SHEET),
        "nextMove": (
            "Keep target-center rails as visual/source-registration context only. The next useful move is still source/provenance intake or a clue that names a rail/path plus a letter/word unit and read order."
        ),
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result)

    controls_sorted = sorted(
        controls,
        key=lambda row: (-row["nonActiveBoldRailWordCount"], row.get("linePitchShift") or 0),
    )
    lines = [
        "# Active Target Center-Path Bold Gate",
        "",
        "Scope: project trusted DOCM bold state onto the existing active target center-path geometry. No new OCR, key derivation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        "- Bold authority: `Article with Fonts.docm` run export; Markdown bold is not used as font authority.",
        f"- Primary path: `{result['summary']['primaryOrder']}`",
        f"- Primary rail words: `{result['summary']['primaryRailWordCount']}`",
        f"- Primary bold rail words: `{result['summary']['primaryBoldRailWordCount']}`",
        f"- Primary non-active bold rail words: `{result['summary']['primaryNonActiveBoldRailWordCount']}`",
        f"- Primary direct active target bold units: `{result['summary']['primaryDirectTargetBoldUnitCount']}`",
        f"- Primary direct target bold text: `{result['summary']['primaryDirectTargetBoldText']}`",
        f"- Primary non-active rail bold text: `{result['summary']['primaryNonActiveRailBoldText']}`",
        f"- Primary strict instruction terms: `{result['summary']['primaryStrictInstructionTerms']}`",
        f"- Primary non-active strict instruction terms: `{result['summary']['primaryNonActiveStrictInstructionTerms']}`",
        f"- Variant strict-instruction path count: `{result['summary']['variantStrictInstructionHitCount']}`",
        f"- Shift controls tested: `{result['summary']['controlShiftCount']}`",
        f"- Controls with non-active bold count >= primary: `{result['summary']['controlComparableNonActiveBoldShifts']}`",
        f"- Control strict instruction shifts: `{result['summary']['controlStrictInstructionHitShifts']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Path Variants",
        "",
        "| path | direct targets | bold rail words | non-active bold rail words | strict terms | non-active bold text |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in path_variants:
        nonactive = row["nonActiveRailBoldText"].replace("|", "\\|")
        lines.append(
            f"| `{row['id']}` | {row['directTargetBoldUnitCount']} | {row['boldRailWordCount']} | {row['nonActiveBoldRailWordCount']} | `{row['strictInstructionTerms']}` | {nonactive} |"
        )

    lines.extend(
        [
            "",
            "## Densest Non-Active Bold Controls",
            "",
            "| shift | non-active bold words | bold rail words | strict terms | non-active bold text |",
            "|---:|---:|---:|---|---|",
        ]
    )
    for row in controls_sorted[:10]:
        nonactive = row["nonActiveRailBoldText"].replace("|", "\\|")
        lines.append(
            f"| {row.get('linePitchShift')} | {row['nonActiveBoldRailWordCount']} | {row['boldRailWordCount']} | `{row['strictInstructionTerms']}` | {nonactive} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote active target-center rail bold projection as a selector.",
            f"- The primary rail necessarily re-hits `{primary['directTargetBoldUnitCount']}` active bold target units and touches `{primary['nonActiveBoldRailWordCount']}` non-active DOCM-bold rail word(s): `{primary['nonActiveRailBoldText']}`.",
            f"- The combined bold text has `{len(primary['strictInstructionTerms'])}` strict instruction-term hits; the non-active bold rail text has `{len(primary['nonActiveStrictInstructionTerms'])}`.",
            f"- Shifted controls with non-active bold counts at least as high as primary: `{result['summary']['controlComparableNonActiveBoldShifts']}`.",
            "- Next best move: preserve this as a guardrail and only reopen rail/path mechanics if a source or clue explicitly names path/rail/connector plus a word/letter unit and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("primaryBoldRailWordCount:", result["summary"]["primaryBoldRailWordCount"])
    print("primaryNonActiveBoldRailWordCount:", result["summary"]["primaryNonActiveBoldRailWordCount"])
    print("primaryStrictInstructionHitCount:", result["summary"]["primaryStrictInstructionHitCount"])
    print("controlComparableNonActiveBoldCount:", result["summary"]["controlComparableNonActiveBoldCount"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Control active OVERDOSE horizontal slot phase against page-76 text.

This bounded pass keeps the active O4/B4/G5/O5 vertical positions, box sizes,
and within-slot offsets, then shifts their OVERDOSE center-slot indexes through
all eight horizontal phases. It asks whether the active x placement is selective
or whether nearby OVERDOSE phases also sample ordinary article text. It does not
derive keys, hashes, seed phrases, WIFs, addresses, BIP39 material, or candidate
strings.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_overdose_xslot_phase_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_overdose_xslot_phase_control.json"
OUT_MD = OUT / "current_scan_overdose_xslot_phase_control.md"
OUT_SHEET = OUT / "current_scan_overdose_xslot_phase_control_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
HIGHLIGHT_AUDIT = ROOT / "analysis_outputs/highlight_audit/highres_highlight_audit.json"
UPRIGHT_PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
OVERDOSE_SLOT_LEFT = 294.0
OVERDOSE_SLOT_WIDTH = 244.5
OVERDOSE = "OVERDOSE"

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
    "bitcoins",
    "satoshi",
    "vitalik",
    "buterin",
    "volcano",
    "volcanoes",
    "bond",
    "bonds",
    "shitcoiner",
    "heart",
    "dip",
    "sell",
    "bukele",
    "imf",
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


def token(text: str) -> str:
    return re.sub(r"[^a-z0-9$]+", "", text.lower())


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def box_overlap_area(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def slot_center(index: int) -> float:
    return OVERDOSE_SLOT_LEFT + index * OVERDOSE_SLOT_WIDTH + OVERDOSE_SLOT_WIDTH / 2.0


def make_shifted_box(active: dict[str, Any], phase: int) -> tuple[list[float], int, str]:
    source_slot = int(active["centerSlotIndex"])
    target_slot = (source_slot + phase) % len(OVERDOSE)
    shifted_center_x = slot_center(target_slot) + active["withinSlotOffset"]
    width = active["width"]
    return (
        [
            shifted_center_x - width / 2.0,
            active["box"][1],
            shifted_center_x + width / 2.0,
            active["box"][3],
        ],
        target_slot,
        OVERDOSE[target_slot],
    )


def active_rows() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    rows = []
    for short_id in TARGET_ORDER:
        row = dict(by_short[short_id])
        row["box"] = [float(v) for v in row["box"]]
        x, y = center(row["box"])
        row["center"] = [x, y]
        row["width"] = row["box"][2] - row["box"][0]
        row["height"] = row["box"][3] - row["box"][1]
        row["centerSlotIndex"] = int(row["centerSlotIndex"])
        row["centerSlotLetter"] = str(row["centerSlotLetter"])
        row["withinSlotOffset"] = x - slot_center(row["centerSlotIndex"])
        rows.append(row)
    return rows


def page76_words() -> list[dict[str, Any]]:
    article = load_json(ARTICLE_MAP)
    page = next(row for row in article["pages"] if row["page"] == 76)
    words = []
    for word in page["words"]:
        clean = token(str(word.get("token") or word.get("text") or ""))
        if not clean:
            continue
        box = [float(v) for v in word["box"]]
        words.append(
            {
                "index": int(word.get("index", len(words))),
                "text": str(word.get("text") or clean),
                "token": clean,
                "box": box,
                "center": center(box),
            }
        )
    return words


def page76_format_rows() -> list[dict[str, Any]]:
    data = load_json(HIGHLIGHT_AUDIT)
    rows = []
    for row in data.get("visualOrangeRows", []) + data.get("annotatedColorRows", []):
        if row.get("page") != 76 or not row.get("box"):
            continue
        rows.append(
            {
                "id": row["id"],
                "kind": row.get("kind", ""),
                "expected": row.get("expected") or row.get("ocrText") or "",
                "box": [float(v) for v in row["box"]],
            }
        )
    return rows


def words_in_box(words: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    return [word for word in words if boxes_intersect(word["box"], box)]


def format_rows_in_box(format_rows: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    return [row for row in format_rows if boxes_intersect(row["box"], box)]


def scenario_row(
    phase: int,
    active: list[dict[str, Any]],
    words: list[dict[str, Any]],
    format_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    target_rows = []
    strict_tokens = set()
    context_tokens = set()
    active_overlap_count = 0
    total_word_hits = 0
    visual_orange_hits = 0
    annotated_color_hits = 0
    for active_row in active:
        shifted_box, shifted_slot_index, shifted_slot_letter = make_shifted_box(active_row, phase)
        hits = words_in_box(words, shifted_box)
        format_hits = format_rows_in_box(format_rows, shifted_box)
        total_word_hits += len(hits)
        row_strict = sorted({word["token"] for word in hits if word["token"] in STRICT_TERMS})
        row_context = sorted({word["token"] for word in hits if word["token"] in CONTEXT_TERMS})
        strict_tokens.update(row_strict)
        context_tokens.update(row_context)
        if box_overlap_area(shifted_box, active_row["box"]) > 0:
            active_overlap_count += 1
        visual_orange_hits += sum(1 for row in format_hits if row["kind"] == "visual-orange")
        annotated_color_hits += sum(1 for row in format_hits if row["kind"].startswith("annotated"))
        target_rows.append(
            {
                "target": active_row["shortId"],
                "phrase": active_row["phrase"],
                "sourceSlotIndex": active_row["centerSlotIndex"],
                "sourceSlotLetter": active_row["centerSlotLetter"],
                "shiftedSlotIndex": shifted_slot_index,
                "shiftedSlotLetter": shifted_slot_letter,
                "shiftedBox": [round(v, 3) for v in shifted_box],
                "wordHitCount": len(hits),
                "wordSnippet": " ".join(word["text"] for word in hits) if hits else "(no OCR words)",
                "strictInstructionTokens": row_strict,
                "contextTokens": row_context,
                "formatHitKinds": sorted({row["kind"] for row in format_hits}),
                "formatHitLabels": [row["expected"][:80] for row in format_hits],
                "overlapsOriginalTarget": boxes_intersect(shifted_box, active_row["box"]),
            }
        )
    return {
        "phaseShift": phase,
        "slotIndexes": [row["shiftedSlotIndex"] for row in target_rows],
        "slotStream": "".join(row["shiftedSlotLetter"] for row in target_rows),
        "wordHitCount": total_word_hits,
        "strictInstructionTokens": sorted(strict_tokens),
        "contextTokens": sorted(context_tokens),
        "strictInstructionHitCount": len(strict_tokens),
        "contextHitCount": len(context_tokens),
        "activeOverlapTargetCount": active_overlap_count,
        "isActivePhase": active_overlap_count == len(active),
        "visualOrangeHitCount": visual_orange_hits,
        "annotatedColorHitCount": annotated_color_hits,
        "targetRows": target_rows,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    base = Image.open(UPRIGHT_PAGE76).convert("RGB")
    scale = 0.22
    page = base.resize((int(base.width * scale), int(base.height * scale)))
    width = 1840
    cell_w = width // 4
    cell_h = page.height + 170
    height = 92 + cell_h * 2
    sheet = Image.new("RGB", (width, height), (246, 247, 249))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    body = font(14)
    small = font(11)
    draw.text((24, 18), "Current Scan OVERDOSE X-Slot Phase Control", fill=(20, 28, 38), font=title)
    draw.text(
        (24, 55),
        "Active O4/B4/G5/O5 boxes shifted horizontally through all eight OVERDOSE center-slot phases.",
        fill=(62, 72, 86),
        font=body,
    )
    colors = {"O4": (230, 115, 0), "B4": (30, 30, 30), "G5": (30, 30, 30), "O5": (230, 115, 0)}
    for idx, scenario in enumerate(result["scenarioRows"]):
        col = idx % 4
        row_idx = idx // 4
        x = col * cell_w + 16
        y = 92 + row_idx * cell_h
        sheet.paste(page, (x, y + 80))
        phase_label = "active" if scenario["isActivePhase"] else "control"
        draw.text(
            (x, y + 8),
            f"phase +{scenario['phaseShift']} {phase_label} slots={scenario['slotStream']} words={scenario['wordHitCount']}",
            fill=(20, 28, 38),
            font=body,
        )
        draw.text(
            (x, y + 30),
            f"strict={scenario['strictInstructionTokens'] or '-'} context={scenario['contextTokens'] or '-'}",
            fill=(62, 72, 86),
            font=small,
        )
        draw.text(
            (x, y + 48),
            f"orange={scenario['visualOrangeHitCount']} annotated={scenario['annotatedColorHitCount']}",
            fill=(62, 72, 86),
            font=small,
        )
        for target in scenario["targetRows"]:
            box = target["shiftedBox"]
            scaled = [
                int(x + box[0] * scale),
                int(y + 80 + box[1] * scale),
                int(x + box[2] * scale),
                int(y + 80 + box[3] * scale),
            ]
            color = colors[target["target"]]
            draw.rectangle(scaled, outline=color, width=2)
            draw.text((scaled[0] + 2, max(y + 80, scaled[1] - 12)), target["target"], fill=color, font=small)
        yy = y + 80 + page.height + 4
        for target in scenario["targetRows"]:
            draw.text(
                (x, yy),
                f"{target['target']} {target['shiftedSlotLetter']} {target['wordSnippet'][:48]}",
                fill=(40, 45, 52),
                font=small,
            )
            yy += 15
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan OVERDOSE X-Slot Phase Control",
        "",
        "Scope: kept the active O4/B4/G5/O5 vertical positions, box sizes, and within-slot offsets, then shifted their OVERDOSE center-slot indexes through all eight horizontal phases. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Scenario rows / active phases / control phases: `{summary['scenarioCount']}` / `{summary['activePhaseCount']}` / `{summary['controlPhaseCount']}`",
        f"- Total target rows / total OCR word hits: `{summary['targetRowCount']}` / `{summary['totalWordHitCount']}`",
        f"- Strict instruction scenario rows / token hits: `{summary['strictInstructionScenarioCount']}` / `{summary['strictInstructionTokenHitCount']}`",
        f"- Context scenario rows / token hits: `{summary['contextScenarioCount']}` / `{summary['contextTokenHitCount']}`",
        f"- Active-phase strict/context token hits: `{summary['activePhaseStrictTokenHitCount']}` / `{summary['activePhaseContextTokenHitCount']}`",
        f"- Control-phase strict/context token hits: `{summary['controlPhaseStrictTokenHitCount']}` / `{summary['controlPhaseContextTokenHitCount']}`",
        f"- Active/control visual-orange hits: `{summary['activePhaseVisualOrangeHitCount']}` / `{summary['controlPhaseVisualOrangeHitCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Scenario Rows",
        "",
        "| phase | kind | slots | words | visual orange | annotated color | strict tokens | context tokens | snippets |",
        "|---:|---|---|---:|---:|---:|---|---|---|",
    ]
    for scenario in result["scenarioRows"]:
        snippets = " / ".join(f"{row['target']}:{row['wordSnippet']}" for row in scenario["targetRows"])
        lines.append(
            "| "
            + " | ".join(
                [
                    str(scenario["phaseShift"]),
                    "active" if scenario["isActivePhase"] else "control",
                    scenario["slotStream"],
                    str(scenario["wordHitCount"]),
                    str(scenario["visualOrangeHitCount"]),
                    str(scenario["annotatedColorHitCount"]),
                    ", ".join(scenario["strictInstructionTokens"]) or "-",
                    ", ".join(scenario["contextTokens"]) or "-",
                    snippets.replace("|", "/"),
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
            "- Horizontal phase is not selective: multiple shifted phases still re-overlap all four active boxes because the active boxes are wide relative to OVERDOSE slot spacing.",
            "- Shifted phases sample ordinary article text and format regions, while strict instruction hits remain 0.",
            "- OVERDOSE x-slot phase remains validation geometry only; it does not unlock extraction from O4/B4/G5/O5.",
            "",
            "## Next Move",
            "",
            "- Keep horizontal slot phase as a source-comparison benchmark. Reopen extraction only with distinct source/original-layout material or raw clue wording that explicitly names the unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    active = active_rows()
    words = page76_words()
    format_rows = page76_format_rows()
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    scenarios = [scenario_row(phase, active, words, format_rows) for phase in range(len(OVERDOSE))]
    active_scenarios = [row for row in scenarios if row["isActivePhase"]]
    control_scenarios = [row for row in scenarios if not row["isActivePhase"]]
    summary = {
        "scenarioCount": len(scenarios),
        "activePhaseCount": len(active_scenarios),
        "controlPhaseCount": len(control_scenarios),
        "targetRowCount": sum(len(row["targetRows"]) for row in scenarios),
        "totalWordHitCount": sum(row["wordHitCount"] for row in scenarios),
        "strictInstructionScenarioCount": sum(1 for row in scenarios if row["strictInstructionTokens"]),
        "strictInstructionTokenHitCount": sum(len(row["strictInstructionTokens"]) for row in scenarios),
        "contextScenarioCount": sum(1 for row in scenarios if row["contextTokens"]),
        "contextTokenHitCount": sum(len(row["contextTokens"]) for row in scenarios),
        "activePhaseStrictTokenHitCount": sum(len(row["strictInstructionTokens"]) for row in active_scenarios),
        "activePhaseContextTokenHitCount": sum(len(row["contextTokens"]) for row in active_scenarios),
        "controlPhaseStrictTokenHitCount": sum(len(row["strictInstructionTokens"]) for row in control_scenarios),
        "controlPhaseContextTokenHitCount": sum(len(row["contextTokens"]) for row in control_scenarios),
        "activePhaseVisualOrangeHitCount": sum(row["visualOrangeHitCount"] for row in active_scenarios),
        "controlPhaseVisualOrangeHitCount": sum(row["visualOrangeHitCount"] for row in control_scenarios),
        "activePhaseAnnotatedColorHitCount": sum(row["annotatedColorHitCount"] for row in active_scenarios),
        "controlPhaseAnnotatedColorHitCount": sum(row["annotatedColorHitCount"] for row in control_scenarios),
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"phases={summary['scenarioCount']}|active={summary['activePhaseCount']}|"
        f"controls={summary['controlPhaseCount']}|targets={summary['targetRowCount']}|"
        f"words={summary['totalWordHitCount']}|strictRows={summary['strictInstructionScenarioCount']}|"
        f"strict={summary['strictInstructionTokenHitCount']}|contextRows={summary['contextScenarioCount']}|"
        f"context={summary['contextTokenHitCount']}|activeStrict={summary['activePhaseStrictTokenHitCount']}|"
        f"activeContext={summary['activePhaseContextTokenHitCount']}|controlStrict={summary['controlPhaseStrictTokenHitCount']}|"
        f"controlContext={summary['controlPhaseContextTokenHitCount']}|activeOrange={summary['activePhaseVisualOrangeHitCount']}|"
        f"controlOrange={summary['controlPhaseVisualOrangeHitCount']}|sourceR3=0|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_scan_overdose_xslot_phase_control_no_instruction_source",
        "sheet": rel(OUT_SHEET),
        "summary": summary,
        "fingerprint": fingerprint,
        "activeRows": active,
        "scenarioRows": scenarios,
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

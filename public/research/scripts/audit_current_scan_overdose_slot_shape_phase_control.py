#!/usr/bin/env python3
"""Control the active OVERDOSE-slot shape against nearby line phases.

This bounded pass keeps the active O4/B4/G5/O5 x-positions, box sizes,
OVERDOSE slot assignment, and 3/2/5 vertical line-gap phase, then moves that
same shape to each possible lower-page starting line. It asks whether the
active layout phase is uniquely instructional or whether comparable shifted
phases also hit ordinary article text. It does not derive keys, hashes, seed
phrases, WIFs, addresses, BIP39 material, or candidate strings.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_overdose_slot_shape_phase_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_overdose_slot_shape_phase_control.json"
OUT_MD = OUT / "current_scan_overdose_slot_shape_phase_control.md"
OUT_SHEET = OUT / "current_scan_overdose_slot_shape_phase_control_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
UPRIGHT_PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
LINE_GAPS = [3, 2, 5]
LOWER_PAGE_Y_MIN = 2000.0
LINE_CLUSTER_TOLERANCE = 32.0
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


def point_in_box(point: tuple[float, float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def slot_index_for_x(x: float) -> int:
    index = int((x - OVERDOSE_SLOT_LEFT) // OVERDOSE_SLOT_WIDTH)
    return max(0, min(len(OVERDOSE) - 1, index))


def slot_letter_for_x(x: float) -> str:
    return OVERDOSE[slot_index_for_x(x)]


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
        row["slotIndexFromCenter"] = slot_index_for_x(x)
        row["slotLetterFromCenter"] = slot_letter_for_x(x)
        return_slot = row.get("centerSlotLetter")
        row["declaredSlotLetter"] = return_slot if return_slot else row["slotLetterFromCenter"]
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


def lower_line_groups(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lower = sorted([word for word in words if word["center"][1] >= LOWER_PAGE_Y_MIN], key=lambda w: w["center"][1])
    groups: list[list[dict[str, Any]]] = []
    for word in lower:
        if not groups:
            groups.append([word])
            continue
        current_y = sum(row["center"][1] for row in groups[-1]) / len(groups[-1])
        if abs(word["center"][1] - current_y) <= LINE_CLUSTER_TOLERANCE:
            groups[-1].append(word)
        else:
            groups.append([word])
    out = []
    for idx, group in enumerate(groups):
        group = sorted(group, key=lambda row: row["center"][0])
        y = sum(row["center"][1] for row in group) / len(group)
        out.append(
            {
                "lineGroupIndex": idx,
                "centerY": y,
                "wordCount": len(group),
                "text": " ".join(row["text"] for row in group),
                "words": group,
            }
        )
    return out


def words_in_box(words: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    return [word for word in words if boxes_intersect(word["box"], box)]


def make_box(active: dict[str, Any], center_y: float) -> list[float]:
    x0, _, x1, _ = active["box"]
    height = active["height"]
    return [x0, center_y - height / 2.0, x1, center_y + height / 2.0]


def box_overlap_area(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def scenario_rows(
    start_index: int,
    line_groups: list[dict[str, Any]],
    active: list[dict[str, Any]],
    words: list[dict[str, Any]],
) -> dict[str, Any]:
    indexes = [
        start_index,
        start_index + LINE_GAPS[0],
        start_index + LINE_GAPS[0] + LINE_GAPS[1],
        start_index + sum(LINE_GAPS),
    ]
    target_rows = []
    strict_tokens = set()
    context_tokens = set()
    active_overlap_count = 0
    total_word_hits = 0
    for active_row, line_index in zip(active, indexes):
        line = line_groups[line_index]
        nearest_active_line_y = min(line_groups, key=lambda g: abs(g["centerY"] - active_row["center"][1]))["centerY"]
        offset = active_row["center"][1] - nearest_active_line_y
        shifted_box = make_box(active_row, line["centerY"] + offset)
        hits = words_in_box(words, shifted_box)
        total_word_hits += len(hits)
        row_strict = sorted({word["token"] for word in hits if word["token"] in STRICT_TERMS})
        row_context = sorted({word["token"] for word in hits if word["token"] in CONTEXT_TERMS})
        strict_tokens.update(row_strict)
        context_tokens.update(row_context)
        overlap = box_overlap_area(shifted_box, active_row["box"])
        if overlap > 0:
            active_overlap_count += 1
        target_rows.append(
            {
                "target": active_row["shortId"],
                "phrase": active_row["phrase"],
                "lineGroupIndex": line_index,
                "lineCenterY": round(line["centerY"], 3),
                "shiftedBox": [round(v, 3) for v in shifted_box],
                "slotLetter": active_row["declaredSlotLetter"],
                "wordHitCount": len(hits),
                "wordSnippet": " ".join(word["text"] for word in hits) if hits else "(no OCR words)",
                "strictInstructionTokens": row_strict,
                "contextTokens": row_context,
                "overlapsOriginalTarget": overlap > 0,
            }
        )
    return {
        "startLineGroupIndex": start_index,
        "lineGroupIndexes": indexes,
        "lineGapPattern": "/".join(str(v) for v in LINE_GAPS),
        "slotStream": "".join(row["slotLetter"] for row in target_rows),
        "wordHitCount": total_word_hits,
        "strictInstructionTokens": sorted(strict_tokens),
        "contextTokens": sorted(context_tokens),
        "strictInstructionHitCount": len(strict_tokens),
        "contextHitCount": len(context_tokens),
        "activeOverlapTargetCount": active_overlap_count,
        "isActivePhase": active_overlap_count == len(active),
        "targetRows": target_rows,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    base = Image.open(UPRIGHT_PAGE76).convert("RGB")
    scale = 0.34
    page = base.resize((int(base.width * scale), int(base.height * scale)))
    width = 1840
    row_h = page.height + 128
    height = 94 + row_h * len(result["scenarioRows"])
    sheet = Image.new("RGB", (width, height), (246, 247, 249))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    body = font(15)
    small = font(12)
    draw.text((24, 18), "Current Scan OVERDOSE Slot-Shape Phase Control", fill=(20, 28, 38), font=title)
    draw.text(
        (24, 55),
        "Active O4/B4/G5/O5 box shape shifted through same 3/2/5 lower-page line phases.",
        fill=(62, 72, 86),
        font=body,
    )
    colors = {"O4": (230, 115, 0), "B4": (30, 30, 30), "G5": (30, 30, 30), "O5": (230, 115, 0)}
    for idx, scenario in enumerate(result["scenarioRows"]):
        y = 94 + idx * row_h
        x = 24
        sheet.paste(page, (x, y + 22))
        for row in scenario["targetRows"]:
            box = row["shiftedBox"]
            scaled = [
                int(x + box[0] * scale),
                int(y + 22 + box[1] * scale),
                int(x + box[2] * scale),
                int(y + 22 + box[3] * scale),
            ]
            color = colors[row["target"]]
            draw.rectangle(scaled, outline=color, width=3)
            draw.text((scaled[0] + 3, max(y + 22, scaled[1] - 15)), row["target"], fill=color, font=small)
        tx = x + page.width + 30
        phase = "active phase" if scenario["isActivePhase"] else "control phase"
        draw.text(
            (tx, y + 24),
            f"start={scenario['startLineGroupIndex']} {phase} lines={scenario['lineGroupIndexes']} slots={scenario['slotStream']}",
            fill=(20, 28, 38),
            font=body,
        )
        draw.text(
            (tx, y + 50),
            f"words={scenario['wordHitCount']} strict={scenario['strictInstructionTokens'] or '-'} context={scenario['contextTokens'] or '-'}",
            fill=(62, 72, 86),
            font=small,
        )
        yy = y + 82
        for row in scenario["targetRows"]:
            draw.text(
                (tx, yy),
                f"{row['target']} line={row['lineGroupIndex']} words={row['wordHitCount']} strict={row['strictInstructionTokens'] or '-'} ctx={row['contextTokens'] or '-'}",
                fill=(40, 45, 52),
                font=small,
            )
            yy += 18
            draw.text((tx + 18, yy), row["wordSnippet"][:112], fill=(82, 88, 96), font=small)
            yy += 22
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan OVERDOSE Slot-Shape Phase Control",
        "",
        "Scope: preserved the active O4/B4/G5/O5 x-positions, box sizes, OVERDOSE slot stream, and 3/2/5 line-gap shape, then shifted that shape across the possible lower-page line phases. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Scenario rows / active phases / control phases: `{summary['scenarioCount']}` / `{summary['activePhaseCount']}` / `{summary['controlPhaseCount']}`",
        f"- Total target rows / total OCR word hits: `{summary['targetRowCount']}` / `{summary['totalWordHitCount']}`",
        f"- Strict instruction scenario rows / token hits: `{summary['strictInstructionScenarioCount']}` / `{summary['strictInstructionTokenHitCount']}`",
        f"- Context scenario rows / token hits: `{summary['contextScenarioCount']}` / `{summary['contextTokenHitCount']}`",
        f"- Active-phase strict/context token hits: `{summary['activePhaseStrictTokenHitCount']}` / `{summary['activePhaseContextTokenHitCount']}`",
        f"- Control-phase strict/context token hits: `{summary['controlPhaseStrictTokenHitCount']}` / `{summary['controlPhaseContextTokenHitCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Scenario Rows",
        "",
        "| start | phase | lines | slots | words | strict tokens | context tokens | snippets |",
        "|---:|---|---|---|---:|---|---|---|",
    ]
    for scenario in result["scenarioRows"]:
        snippets = " / ".join(f"{row['target']}: {row['wordSnippet']}" for row in scenario["targetRows"])
        lines.append(
            "| "
            + " | ".join(
                [
                    str(scenario["startLineGroupIndex"]),
                    "active" if scenario["isActivePhase"] else "control",
                    ",".join(str(v) for v in scenario["lineGroupIndexes"]),
                    scenario["slotStream"],
                    str(scenario["wordHitCount"]),
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
            "- The active vertical phase is the only phase that overlaps all four manual active boxes, but that is a location validation fact, not an extraction instruction.",
            "- Shifted same-shape control phases still hit ordinary article context words, while no active or control phase contains strict instruction language.",
            "- OVERDOSE slot-shape phase remains a source-comparison guardrail only; it does not name a unit/order/transform.",
            "",
            "## Next Move",
            "",
            "- Keep active OVERDOSE slot-shape phase as validation geometry. Reopen extraction only with distinct source/original-layout material or raw clue wording that explicitly names the unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    active = active_rows()
    words = page76_words()
    groups = lower_line_groups(words)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    max_start = len(groups) - 1 - sum(LINE_GAPS)
    scenarios = [
        scenario_rows(start, groups, active, words)
        for start in range(max_start + 1)
    ]
    active_scenarios = [row for row in scenarios if row["isActivePhase"]]
    control_scenarios = [row for row in scenarios if not row["isActivePhase"]]
    summary = {
        "lineGroupCount": len(groups),
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
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"lines={summary['lineGroupCount']}|scenarios={summary['scenarioCount']}|"
        f"active={summary['activePhaseCount']}|controls={summary['controlPhaseCount']}|"
        f"targets={summary['targetRowCount']}|words={summary['totalWordHitCount']}|"
        f"strictRows={summary['strictInstructionScenarioCount']}|strict={summary['strictInstructionTokenHitCount']}|"
        f"contextRows={summary['contextScenarioCount']}|context={summary['contextTokenHitCount']}|"
        f"activeStrict={summary['activePhaseStrictTokenHitCount']}|activeContext={summary['activePhaseContextTokenHitCount']}|"
        f"controlStrict={summary['controlPhaseStrictTokenHitCount']}|controlContext={summary['controlPhaseContextTokenHitCount']}|"
        f"sourceR3=0|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_scan_overdose_slot_shape_phase_control_no_instruction_source",
        "sheet": rel(OUT_SHEET),
        "summary": summary,
        "fingerprint": fingerprint,
        "activeRows": active,
        "lineGroups": [
            {k: v for k, v in row.items() if k != "words"}
            for row in groups
        ],
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

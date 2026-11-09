#!/usr/bin/env python3
"""Cross-check the repaired p78 frame contact ladder against DOCM font states.

The dx=-38/-40 repair preserves the same top-down phrase ladder, but it changes
which phrase units are exact edge contacts. This pass asks whether those exact
edge contacts become a readable Typeka/font/highlight instruction.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT_JSON = ROOT / "analysis_outputs/docm_format_sources/lower_corridor_font_state_selector/lower_corridor_font_state_selector.json"
CONTACT_JSON = ROOT / "analysis_outputs/source_audit/tricontact_frame_contact_stability/tricontact_frame_contact_stability.json"

OUT = ROOT / "analysis_outputs/docm_format_sources/repaired_frame_font_contact_states"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "repaired_frame_font_contact_states.json"
OUT_MD = OUT / "repaired_frame_font_contact_states.md"
OUT_SHEET = OUT / "repaired_frame_font_contact_states_sheet.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "first",
    "last",
    "middle",
    "down",
    "up",
]


STYLE_NAMES = {
    "R": "Typeka regular",
    "M": "Typeka Mix",
    "B": "Typeka bold",
    "K": "black/grey highlight",
    "Y": "orange/yellow highlight",
    "O": "other",
}


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%]+(?:'[A-Za-z]+)?", text)


def initials(labels: list[str]) -> str:
    out = []
    for label in labels:
        ws = words(label)
        out.append(ws[0][0] if ws else "")
    return "".join(out)


def lasts(labels: list[str]) -> str:
    out = []
    for label in labels:
        ws = words(label)
        out.append(ws[-1][-1] if ws else "")
    return "".join(out)


def instruction_hits(streams: dict[str, str]) -> dict[str, list[str]]:
    hits = {}
    for name, value in streams.items():
        low = value.lower()
        found = [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]
        if found:
            hits[name] = found
    return hits


def edge_class(event: dict) -> str:
    contacts = event.get("contacts", [])
    if any(contact.get("relation") == "cuts" for contact in contacts):
        return "exact"
    if contacts:
        return "adjacent"
    if event.get("overlapVsTarget", 0) > 0:
        return "overlap"
    return "none"


def contact_edges(event: dict) -> str:
    contacts = event.get("contacts", [])
    if not contacts:
        return "-"
    return ",".join(f"{contact['edge']}:{contact['relation']}" for contact in contacts)


def summarize_scenario(scenario: dict, phrase_by_id: dict[str, dict]) -> dict:
    rows = []
    for event in scenario["events"]:
        phrase = phrase_by_id.get(event["id"], {})
        rows.append(
            {
                "id": event["id"],
                "label": event["label"],
                "edgeClass": edge_class(event),
                "edges": contact_edges(event),
                "overlapVsTarget": event.get("overlapVsTarget"),
                "dominantStyle": phrase.get("dominantStyle", "-"),
                "styleRun": phrase.get("styleRun", "-"),
                "variantCounts": phrase.get("variantCounts", {}),
                "highlightCounts": phrase.get("highlightCounts", {}),
                "wordInitials": phrase.get("wordInitials", initials([event["label"]])),
                "wordLasts": phrase.get("wordLasts", lasts([event["label"]])),
            }
        )

    exact = [row for row in rows if row["edgeClass"] == "exact"]
    adjacent = [row for row in rows if row["edgeClass"] == "adjacent"]
    cut_or_adjacent = [row for row in rows if row["edgeClass"] in {"exact", "adjacent"}]
    labels = [row["label"] for row in rows]
    exact_labels = [row["label"] for row in exact]
    adjacent_labels = [row["label"] for row in adjacent]
    streams = {
        "topDownLabels": " | ".join(labels),
        "topDownStyles": "".join(row["dominantStyle"] for row in rows),
        "topDownStyleRuns": "|".join(row["styleRun"] for row in rows),
        "topDownInitials": initials(labels),
        "topDownLasts": lasts(labels),
        "exactEdgeLabels": " | ".join(exact_labels),
        "exactEdgeStyles": "".join(row["dominantStyle"] for row in exact),
        "exactEdgeStyleRuns": "|".join(row["styleRun"] for row in exact),
        "exactEdgeInitials": initials(exact_labels),
        "exactEdgeLasts": lasts(exact_labels),
        "adjacentLabels": " | ".join(adjacent_labels),
        "adjacentStyles": "".join(row["dominantStyle"] for row in adjacent),
        "contactClassCodes": "".join({"exact": "X", "adjacent": "A", "overlap": "O", "none": "N"}[row["edgeClass"]] for row in rows),
        "cutOrAdjacentStyles": "".join(row["dominantStyle"] for row in cut_or_adjacent),
        "cutOrAdjacentInitials": initials([row["label"] for row in cut_or_adjacent]),
    }
    return {
        "name": scenario["name"],
        "rows": rows,
        "styleCounts": dict(Counter(row["dominantStyle"] for row in rows)),
        "edgeClassCounts": dict(Counter(row["edgeClass"] for row in rows)),
        "streams": streams,
        "instructionTermHits": instruction_hits(streams),
    }


def draw_sheet(summaries: list[dict]) -> None:
    width = 1800
    row_h = 46
    header_h = 72
    scenario_h = header_h + row_h * 10
    height = scenario_h * len(summaries) + 80
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 24)
        font = ImageFont.truetype("Arial.ttf", 19)
        small = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        title_font = ImageFont.load_default()
        font = title_font
        small = title_font

    style_color = {
        "R": (230, 230, 230),
        "M": (210, 230, 255),
        "B": (205, 205, 205),
        "K": (85, 85, 85),
        "Y": (255, 192, 78),
        "-": (245, 245, 245),
    }

    y = 28
    draw.text((24, y), "Repaired p78 frame contacts crossed with Article with Fonts.docm states", fill=(20, 20, 20), font=title_font)
    y += 44
    for summary in summaries:
        draw.text((24, y), summary["name"], fill=(20, 20, 20), font=title_font)
        y += 34
        headers = ["order", "label", "edge", "style", "run", "initials", "lasts"]
        xs = [24, 90, 590, 840, 980, 1240, 1390]
        for x, header in zip(xs, headers):
            draw.text((x, y), header, fill=(60, 60, 60), font=small)
        y += 24
        for i, row in enumerate(summary["rows"], 1):
            bg = style_color.get(row["dominantStyle"], (245, 245, 245))
            draw.rectangle([20, y - 5, width - 20, y + row_h - 8], fill=bg)
            text_fill = (255, 255, 255) if row["dominantStyle"] == "K" else (25, 25, 25)
            values = [
                str(i),
                row["label"],
                f"{row['edgeClass']} {row['edges']}",
                f"{row['dominantStyle']} {STYLE_NAMES.get(row['dominantStyle'], '')}",
                row["styleRun"],
                row["wordInitials"],
                row["wordLasts"],
            ]
            for x, value in zip(xs, values):
                draw.text((x, y), value[:44], fill=text_fill, font=font)
            y += row_h
        draw.text((24, y), f"exact-edge stream: {summary['streams']['exactEdgeLabels']} | styles {summary['streams']['exactEdgeStyles']}", fill=(20, 20, 20), font=small)
        y += 44
    image.save(OUT_SHEET, quality=95)


def main() -> None:
    font_data = json.loads(FONT_JSON.read_text())
    contact_data = json.loads(CONTACT_JSON.read_text())
    phrase_by_id = {row["id"]: row for row in font_data["phrases"] if row.get("found")}

    scenario_names = {"current", "g5_edge_touch_dx_minus_38", "nearest_grid_dx_minus_40", "best_overlap_dx_minus_160_dy_35"}
    scenarios = [scenario for scenario in contact_data["scenarios"] if scenario["name"] in scenario_names]
    summaries = [summarize_scenario(scenario, phrase_by_id) for scenario in scenarios]
    all_streams = {
        f"{summary['name']}:{key}": value
        for summary in summaries
        for key, value in summary["streams"].items()
    }

    current = next(summary for summary in summaries if summary["name"] == "current")
    repaired = next(summary for summary in summaries if summary["name"] == "g5_edge_touch_dx_minus_38")
    grid = next(summary for summary in summaries if summary["name"] == "nearest_grid_dx_minus_40")

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "DOCM Typeka/font-state cross-check for repaired p78 frame contacts; no key derivation",
        "sourceReports": {
            "fontStates": str(FONT_JSON.relative_to(ROOT)),
            "contactStability": str(CONTACT_JSON.relative_to(ROOT)),
        },
        "summaries": summaries,
        "allInstructionTermHits": instruction_hits(all_streams),
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "assessment": [
            "The top-down font/style ladder is stable under repair: current and dx=-38 both give `RRRKRRMY`.",
            "The repair does change the exact-edge subset from current `should sell | earnings | shitcoiner at heart` (`RRY`) to dx=-38 `should sell | Volcano Bonds | shitcoiner at heart` (`RKY`).",
            "That cleaner exact-edge trio is good registration evidence, but its initials (`sVs`), last letters (`lst`), and style code (`RKY`) do not name a word/letter/line/key operation.",
            f"dx=-40 matches the same exact-edge trio as dx=-38: `{grid['streams']['exactEdgeLabels']}`.",
            "Typeka Mix still appears as semantic prose (`trust that guy`, plus Mike in a mixed run), not as an independent selector.",
        ],
        "nextMove": "Keep the repaired exact-edge trio as a compact registration signature: `should sell | Volcano Bonds | shitcoiner at heart` with styles `R K Y`. Do not use it as key material unless a source clue names font/style extraction.",
    }

    draw_sheet(summaries)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Repaired Frame Font-Contact States",
        "",
        "Scope: cross-check repaired p78 frame contacts against the DOCM Typeka/font/highlight witness. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Instruction hits across all streams: `{result['allInstructionTermHits']}`",
        "",
        "## Scenario Streams",
        "",
        "| scenario | top-down styles | exact-edge labels | exact-edge styles | exact initials | exact lasts | contact classes | instruction hits |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for summary in summaries:
        streams = summary["streams"]
        lines.append(
            f"| `{summary['name']}` | `{streams['topDownStyles']}` | `{streams['exactEdgeLabels']}` | `{streams['exactEdgeStyles']}` | `{streams['exactEdgeInitials']}` | `{streams['exactEdgeLasts']}` | `{streams['contactClassCodes']}` | `{summary['instructionTermHits']}` |"
        )

    lines.extend(["", "## Contact Ledger", ""])
    for summary in summaries:
        lines.append(f"### {summary['name']}")
        lines.extend(["", "| order | phrase | edge class | edges | style | style run | variants | highlights |", "|---:|---|---|---|---|---|---|---|"])
        for i, row in enumerate(summary["rows"], 1):
            lines.append(
                f"| {i} | `{row['label']}` | `{row['edgeClass']}` | `{row['edges']}` | `{row['dominantStyle']}` | `{row['styleRun']}` | `{row['variantCounts']}` | `{row['highlightCounts']}` |"
            )
        lines.append("")

    lines.extend(["## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("current exact:", current["streams"]["exactEdgeLabels"], current["streams"]["exactEdgeStyles"])
    print("dx=-38 exact:", repaired["streams"]["exactEdgeLabels"], repaired["streams"]["exactEdgeStyles"])
    print("instruction hits:", result["allInstructionTermHits"])


if __name__ == "__main__":
    main()

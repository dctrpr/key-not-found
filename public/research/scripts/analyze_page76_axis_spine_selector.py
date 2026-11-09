#!/usr/bin/env python3
"""Audit whether the page-76 B5/O5 mirror axis selects a readable spine.

The current strongest target is the local self-mirror pair:
G5/B5 "Volcano Bonds" and O5 "shitcoiner at heart.". This script checks a
small, human-plausible extraction unit: read the words/letters crossed by the
mirror axis running through that pair.

No key candidates are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_DATA = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
SELF_JSON = ROOT / "analysis_outputs/source_audit/page76_self_mirror/page76_self_mirror.json"
OUT = ROOT / "analysis_outputs/source_audit/page76_axis_spine_selector"
OUT.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT / "page76_axis_spine_selector.json"
OUT_MD = OUT / "page76_axis_spine_selector.md"
OVERLAY = OUT / "page76_axis_spine_selector_overlay.jpg"


def load_page76() -> dict:
    data = json.loads(ARTICLE_DATA.read_text())
    return next(page for page in data["pages"] if page["page"] == 76)


def load_axes() -> list[dict]:
    data = json.loads(SELF_JSON.read_text())
    return [
        {
            "axisName": axis["axisName"],
            "axisX": axis["axisX"],
            "edgePattern": axis.get("edgePattern"),
            "meaningfulEdges": len(axis.get("meaningfulEdges", [])),
        }
        for axis in data["axes"]
    ]


def body_words(page: dict) -> list[dict]:
    return [
        w
        for w in page["words"]
        if 300 <= w["center"][1] <= 3050
        and w["text"].strip()
        and w["text"].strip() not in {"OVERDOSE"}
    ]


def body_chars(page: dict) -> list[dict]:
    return [
        ch
        for ch in page["chars"]
        if 300 <= ch["y"] <= 3050
        and ch.get("c", "").strip()
    ]


def group_word_lines(words: list[dict], tolerance: float = 30.0) -> list[dict]:
    lines: list[dict] = []
    for word in sorted(words, key=lambda w: (w["center"][1], w["center"][0])):
        if not lines or abs(lines[-1]["y"] - word["center"][1]) > tolerance:
            lines.append({"lineIndex": len(lines), "y": word["center"][1], "words": []})
        lines[-1]["words"].append(word)
        lines[-1]["y"] = sum(w["center"][1] for w in lines[-1]["words"]) / len(lines[-1]["words"])
    return lines


def line_text(line: dict) -> str:
    return " ".join(w["text"] for w in sorted(line["words"], key=lambda w: w["center"][0]))


def clean_stream(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", text)


def font(size: int):
    for name in ("Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def chars_for_line(chars: list[dict], line: dict) -> list[dict]:
    return sorted([ch for ch in chars if abs(ch["y"] - line["y"]) <= 30], key=lambda ch: ch["x"])


def axis_line_row(axis_x: float, line: dict, chars: list[dict]) -> dict:
    words = sorted(line["words"], key=lambda w: w["center"][0])
    crossing_words = [w for w in words if w["box"][0] <= axis_x <= w["box"][2]]
    nearest_word = min(words, key=lambda w: abs(w["center"][0] - axis_x)) if words else None

    line_chars = chars_for_line(chars, line)
    crossing_chars = [ch for ch in line_chars if ch["box"][0] <= axis_x <= ch["box"][2]]
    nearest_char = min(line_chars, key=lambda ch: abs(ch["x"] - axis_x)) if line_chars else None

    return {
        "lineIndex": line["lineIndex"],
        "y": round(line["y"], 1),
        "lineText": line_text(line),
        "crossingWords": [w["text"] for w in crossing_words],
        "nearestWord": nearest_word["text"] if nearest_word else "",
        "nearestWordDistance": round(abs(nearest_word["center"][0] - axis_x), 1) if nearest_word else None,
        "crossingChars": "".join(ch["c"] for ch in crossing_chars),
        "nearestChar": nearest_char["c"] if nearest_char else "",
        "nearestCharDistance": round(abs(nearest_char["x"] - axis_x), 1) if nearest_char else None,
    }


def analyze_axis(axis: dict, lines: list[dict], chars: list[dict]) -> dict:
    rows = [axis_line_row(axis["axisX"], line, chars) for line in lines]

    def word_token(row: dict) -> str:
        if row["crossingWords"]:
            return "/".join(row["crossingWords"])
        return "-"

    def near_word_token(row: dict) -> str:
        if row["nearestWordDistance"] is not None and row["nearestWordDistance"] <= 120:
            return row["nearestWord"]
        return "-"

    def char_token(row: dict) -> str:
        return row["crossingChars"] or "-"

    def near_char_token(row: dict) -> str:
        if row["crossingChars"]:
            return row["crossingChars"]
        if row["nearestCharDistance"] is not None and row["nearestCharDistance"] <= 25:
            return row["nearestChar"]
        return "-"

    lower_rows = [row for row in rows if 2000 <= row["y"] <= 3005]
    pair_rows = [row for row in rows if 2400 <= row["y"] <= 3005]

    streams = {
        "allCrossingWords": " ".join(word_token(row) for row in rows),
        "lowerCrossingWords": " ".join(word_token(row) for row in lower_rows),
        "pairBandCrossingWords": " ".join(word_token(row) for row in pair_rows),
        "allNearestWordsWithin120px": " ".join(near_word_token(row) for row in rows),
        "lowerNearestWordsWithin120px": " ".join(near_word_token(row) for row in lower_rows),
        "allCrossingChars": "".join(char_token(row) for row in rows),
        "lowerCrossingChars": "".join(char_token(row) for row in lower_rows),
        "pairBandCrossingChars": "".join(char_token(row) for row in pair_rows),
        "allNearestCharsWithin25px": "".join(near_char_token(row) for row in rows),
        "lowerNearestCharsWithin25px": "".join(near_char_token(row) for row in lower_rows),
    }
    cleaned = {f"{k}Letters": clean_stream(v) for k, v in streams.items()}

    return {
        **axis,
        "rows": rows,
        "lowerRows": lower_rows,
        "pairBandRows": pair_rows,
        "streams": streams,
        "cleanedStreams": cleaned,
    }


def draw_overlay(page: dict, axes: list[dict], primary: dict) -> None:
    img = upright_image(76).convert("RGBA")
    draw = ImageDraw.Draw(img)
    fnt = font(24)
    axis_colors = {
        "page_center": (80, 80, 80, 255),
        "all_highlight_bbox_center": (20, 160, 80, 255),
        "orange_bbox_center": (180, 0, 220, 255),
        "grey_bbox_center": (20, 160, 80, 255),
    }
    for axis in axes:
        x = axis["axisX"]
        color = axis_colors.get(axis["axisName"], (0, 0, 0, 255))
        draw.line((x, 320, x, 3040), fill=color, width=5 if axis["axisName"] == "orange_bbox_center" else 3)
        draw.text((x + 8, 322), axis["axisName"], fill=color, font=fnt)

    for row in primary["rows"]:
        if not row["crossingWords"]:
            continue
        for word in page["words"]:
            if abs(word["center"][1] - row["y"]) <= 30 and word["text"] in row["crossingWords"] and word["box"][0] <= primary["axisX"] <= word["box"][2]:
                box = tuple(round(v) for v in word["box"])
                draw.rectangle(box, outline=(255, 0, 180, 255), width=3)
                draw.text((box[0], max(0, box[1] - 24)), word["text"], fill=(255, 0, 180, 255), font=fnt)

    img.crop((260, 1880, 2280, 3035)).convert("RGB").save(OVERLAY, quality=94)


def main() -> None:
    page = load_page76()
    axes = load_axes()
    lines = group_word_lines(body_words(page))
    chars = body_chars(page)
    axis_results = [analyze_axis(axis, lines, chars) for axis in axes]
    primary = next(row for row in axis_results if row["axisName"] == "orange_bbox_center")
    draw_overlay(page, axes, primary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Page-76 B5/O5 mirror-axis vertical spine selector audit; no key derivation.",
        "overlay": str(OVERLAY),
        "axes": axis_results,
        "assessment": [
            "All tested B5/O5 self-mirror axes select ordinary page-76 text rather than a readable instruction.",
            "The strongest lower-corridor stream for the orange bbox axis is Salvador/Fund/when/volcanoes/should/earnings/pay/tagged/could/but/trust plus the final OCR blob for shitcoiner at heart.",
            "This supports the lower El Salvador/IMF corridor as the target zone, but it does not specify a key extraction unit.",
            "Close vertical-axis spine reading as a standalone selector under the current high-res scan.",
        ],
        "nextMove": "Look for a source/provenance clue that specifies a unit for the G5/O5 pair: word, adjacent word, omitted final characters, dosage number, package symptom, or physical-source registration.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines_md = [
        "# Page 76 Axis-Spine Selector Audit",
        "",
        "Scope: test whether the mirror axis linking `Volcano Bonds` and `shitcoiner at heart` selects a vertical word/letter spine on page 76. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OVERLAY}`",
        "",
        "## Axis Streams",
        "",
    ]
    for axis in axis_results:
        lines_md.extend(
            [
                f"### {axis['axisName']} x={axis['axisX']}",
                "",
                f"- Edge pattern: `{axis['edgePattern']}`",
                f"- Lower crossing words: `{axis['streams']['lowerCrossingWords']}`",
                f"- Lower nearest words within 120px: `{axis['streams']['lowerNearestWordsWithin120px']}`",
                f"- Lower crossing chars: `{axis['streams']['lowerCrossingChars']}`",
                f"- Lower nearest chars within 25px: `{axis['streams']['lowerNearestCharsWithin25px']}`",
                "",
            ]
        )

    lines_md.extend(
        [
            "## Primary Axis Detail",
            "",
            "Primary axis: `orange_bbox_center`, because it is the axis used by the B5/O5 pair drilldown.",
            "",
            "| line | y | crossing word(s) | nearest word | crossing char | line text |",
            "|---:|---:|---|---|---|---|",
        ]
    )
    for row in primary["lowerRows"]:
        crossing = ", ".join(row["crossingWords"]) if row["crossingWords"] else "-"
        nearest = f"{row['nearestWord']} ({row['nearestWordDistance']}px)" if row["nearestWord"] else "-"
        char = row["crossingChars"] or "-"
        text = row["lineText"].replace("|", "\\|")
        lines_md.append(f"| {row['lineIndex']} | {row['y']} | `{crossing}` | `{nearest}` | `{char}` | {text} |")

    lines_md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The vertical axis is a useful registration clue, but not a standalone selector.",
            "- The lower-corridor stream reads as normal page text around `El Salvador`, `IMF`, `volcanoes`, `pay`, `Mike`, `trust`, and `shitcoiner at heart`.",
            "- No read/take/fold/mirror/word/letter/key instruction appears in the crossing-word or crossing-character streams.",
            "- Next best move: keep G5/O5 as the target pair, but look outside this axis for the rule that says what unit to extract.",
        ]
    )
    OUT_MD.write_text("\n".join(lines_md) + "\n")
    print(OUT_MD)
    print(OUT_JSON)
    print(OVERLAY)


if __name__ == "__main__":
    main()

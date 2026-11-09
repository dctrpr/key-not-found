#!/usr/bin/env python3
"""Constrained page-76 selector audit.

This tests the most plausible next rules from the current evidence:

- pages 78 and 79 as left/right hand selectors into page 76;
- source-page pattern as binary/order mask;
- high-res compact pattern B1B1B2O3;
- "buying the dip" as an adjacent-line instruction.

It intentionally does not generate private-key candidates.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH_JSON = ROOT / "analysis_outputs/3d_article_map/reflected_highlight_graph.json"
MIRROR_JSON = ROOT / "analysis_outputs/source_audit/highres_page76_mirror_selector.json"
CANONICAL_JSON = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
OUT_JSON = ROOT / "analysis_outputs/3d_article_map/page76_twohand_selector.json"
OUT_MD = ROOT / "analysis_outputs/3d_article_map/page76_twohand_selector.md"


TARGET_LINES = {
    "orange_7": [0, 1],
    "orange_8": [13],
    "orange_9": [22],
    "grey_black_4": [16],
    "grey_black_5": [25],
}

HIGHRES_TARGET_LINES = {
    ("black", 1): [6],
    ("black", 2): [7],
    ("black", 3): [16],
    ("black", 4): [25],
    ("black", 5): [27],
    ("orange", 1): [0, 1],
    ("orange", 2): [13],
    ("orange", 3): [22],
    ("orange", 4): [32],
}

INSTRUCTION_WORDS = {
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "bitcoin",
    "down",
    "below",
    "above",
    "dip",
}


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+(?:'[A-Za-z0-9]+)?", text)


def clean(text: str, limit: int = 120) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1] + "..."


def initials(text: str) -> str:
    return "".join(w[0] for w in words(text) if w)


def lasts(text: str) -> str:
    return "".join(w[-1] for w in words(text) if w)


def instruction_hits(text: str) -> list[str]:
    lowered = {w.lower() for w in words(text)}
    return sorted(lowered & INSTRUCTION_WORDS)


def printable_binary(bits: str, width: int) -> str:
    chars = []
    for i in range(0, len(bits) - width + 1, width):
        value = int(bits[i : i + width], 2)
        chars.append(chr(value) if 32 <= value <= 126 else ".")
    return "".join(chars)


def page76_lines() -> dict[int, str]:
    data = json.loads(CANONICAL_JSON.read_text())
    page = next(p for p in data["pages"].values() if p["articlePage"] == 76)
    return {line["lineIndex"]: clean(line["text"]) for line in page["lines"]}


def line_text(lines: dict[int, str], indexes: list[int]) -> str:
    return " / ".join(lines.get(i, "") for i in indexes)


def first_word_initial(text: str) -> str:
    ws = words(text)
    return ws[0][0] if ws else ""


def last_word_initial(text: str) -> str:
    ws = words(text)
    return ws[-1][0] if ws else ""


def line_word(lines: dict[int, str], line_index: int, index: int, zero_based: bool = False) -> str:
    ws = words(lines.get(line_index, ""))
    if not ws:
        return ""
    i = index if zero_based else index - 1
    if 0 <= i < len(ws):
        return ws[i]
    return ""


def source_word(text: str, index: int, zero_based: bool = False) -> str:
    ws = words(text)
    i = index if zero_based else index - 1
    if 0 <= i < len(ws):
        return ws[i]
    return ""


def graph_order(edges: list[dict]) -> list[dict]:
    color_rank = {"orange": 0, "grey_black": 1}
    return sorted(
        edges,
        key=lambda e: (
            e["targetPage"],
            color_rank.get(e["targetColor"], 2),
            e["targetId"],
            e["sourcePage"],
            e["centerDistance"],
        ),
    )


def dedupe_edges(edges: list[dict]) -> list[dict]:
    out = []
    seen = set()
    for edge in edges:
        key = (edge["targetId"], edge["sourcePage"])
        if key in seen:
            continue
        seen.add(key)
        out.append(edge)
    return out


def edge_target_text(edge: dict, lines: dict[int, str]) -> str:
    indexes = TARGET_LINES.get(edge["targetId"])
    if indexes:
        return line_text(lines, indexes)
    return edge["targetText"]


def build_graph_streams(edges: list[dict], lines: dict[int, str], label: str) -> dict[str, str]:
    streams: dict[str, str] = {}
    source_pages = "".join(str(e["sourcePage"]) for e in edges)
    bits_79 = "".join("1" if e["sourcePage"] == 79 else "0" for e in edges)
    bits_78 = "".join("1" if e["sourcePage"] == 78 else "0" for e in edges)
    streams[f"{label}:source_pages"] = source_pages
    streams[f"{label}:bits_79_is_1"] = bits_79
    streams[f"{label}:bits_78_is_1"] = bits_78
    for width in (5, 7, 8):
        streams[f"{label}:bits79_ascii_{width}"] = printable_binary(bits_79, width)
        streams[f"{label}:bits78_ascii_{width}"] = printable_binary(bits_78, width)

    streams[f"{label}:target_initials"] = "".join(first_word_initial(edge_target_text(e, lines)) for e in edges)
    streams[f"{label}:target_last_initials"] = "".join(last_word_initial(edge_target_text(e, lines)) for e in edges)
    streams[f"{label}:reflection_initials"] = "|".join(initials(e["reflectionText"]) for e in edges)

    # Two-hand literal variants. Source page 78 is treated as left; 79 as right.
    streams[f"{label}:78_first_79_last"] = "".join(
        first_word_initial(edge_target_text(e, lines)) if e["sourcePage"] == 78 else last_word_initial(edge_target_text(e, lines))
        for e in edges
    )
    streams[f"{label}:78_last_79_first"] = "".join(
        last_word_initial(edge_target_text(e, lines)) if e["sourcePage"] == 78 else first_word_initial(edge_target_text(e, lines))
        for e in edges
    )
    streams[f"{label}:78_reflection_first_79_target_first"] = "".join(
        first_word_initial(e["reflectionText"]) if e["sourcePage"] == 78 else first_word_initial(edge_target_text(e, lines))
        for e in edges
    )
    streams[f"{label}:79_reflection_first_78_target_first"] = "".join(
        first_word_initial(e["reflectionText"]) if e["sourcePage"] == 79 else first_word_initial(edge_target_text(e, lines))
        for e in edges
    )
    return streams


def build_highres_streams(mirror: dict, lines: dict[int, str]) -> tuple[dict[str, str], list[dict]]:
    edges = mirror["meaningfulEdges"]
    records = []
    for e in edges:
        target_key = (e["targetColor"], e["targetIndex"])
        indexes = HIGHRES_TARGET_LINES.get(target_key, [])
        line_index = indexes[0] if indexes else None
        target_line = line_text(lines, indexes) if indexes else e["targetLabel"]
        above = line_text(lines, [line_index - 1]) if line_index is not None else ""
        below = line_text(lines, [line_index + 1]) if line_index is not None else ""
        record = {
            "pattern": ("B" if e["targetColor"] == "black" else "O") + str(e["targetIndex"]),
            "sourcePage": e["sourcePage"],
            "sourceIndex": e["sourceIndex"],
            "sourceLabel": e["sourceLabel"],
            "targetLineIndex": line_index,
            "targetLine": target_line,
            "aboveLine": above,
            "belowLine": below,
            "targetWordBySourceIndex1": line_word(lines, line_index, e["sourceIndex"]) if line_index is not None else "",
            "targetWordBySourceIndex0": line_word(lines, line_index, e["sourceIndex"], zero_based=True) if line_index is not None else "",
            "sourceWordByTargetIndex1": source_word(e["sourceLabel"], e["targetIndex"]),
            "sourceWordByTargetIndex0": source_word(e["sourceLabel"], e["targetIndex"], zero_based=True),
        }
        records.append(record)

    streams = {
        "highres:target_pattern": "".join(r["pattern"] for r in records),
        "highres:source_page_pattern": "".join(str(r["sourcePage"]) for r in records),
        "highres:source_index_pattern": ",".join(str(r["sourceIndex"]) for r in records),
        "highres:target_line_initials": "".join(first_word_initial(r["targetLine"]) for r in records),
        "highres:target_line_last_initials": "".join(last_word_initial(r["targetLine"]) for r in records),
        "highres:above_line_initials": "".join(first_word_initial(r["aboveLine"]) for r in records),
        "highres:below_line_initials": "".join(first_word_initial(r["belowLine"]) for r in records),
        "highres:target_word_by_source_index_1based": " ".join(r["targetWordBySourceIndex1"] for r in records),
        "highres:target_word_by_source_index_0based": " ".join(r["targetWordBySourceIndex0"] for r in records),
        "highres:source_word_by_target_index_1based": " ".join(r["sourceWordByTargetIndex1"] for r in records),
        "highres:source_word_by_target_index_0based": " ".join(r["sourceWordByTargetIndex0"] for r in records),
    }
    return streams, records


def main() -> None:
    graph = json.loads(GRAPH_JSON.read_text())
    mirror = json.loads(MIRROR_JSON.read_text())
    lines = page76_lines()

    page76_edges = [
        e
        for e in graph["edges"]
        if e["targetPage"] == 76 and e["strength"] in {"medium", "strong"}
    ]
    ordered_edges = graph_order(page76_edges)
    strong_edges = graph_order([e for e in page76_edges if e["strength"] == "strong"])
    deduped_edges = dedupe_edges(ordered_edges)

    streams: dict[str, str] = {}
    streams.update(build_graph_streams(ordered_edges, lines, "graph_all"))
    streams.update(build_graph_streams(deduped_edges, lines, "graph_dedup_target_source"))
    streams.update(build_graph_streams(strong_edges, lines, "graph_strong_only"))
    highres_streams, highres_records = build_highres_streams(mirror, lines)
    streams.update(highres_streams)

    dip_edges = [e for e in ordered_edges if e["targetId"] == "orange_9"]
    dip_records = []
    for e in dip_edges:
        target_line = TARGET_LINES[e["targetId"]][0]
        dip_records.append(
            {
                "sourcePage": e["sourcePage"],
                "strength": e["strength"],
                "sourceText": e["reflectionText"],
                "above": lines.get(target_line - 1, ""),
                "target": lines.get(target_line, ""),
                "below": lines.get(target_line + 1, ""),
            }
        )
    streams["dip:above_initials"] = "".join(first_word_initial(r["above"]) for r in dip_records)
    streams["dip:target_initials"] = "".join(first_word_initial(r["target"]) for r in dip_records)
    streams["dip:below_initials"] = "".join(first_word_initial(r["below"]) for r in dip_records)
    streams["dip:source_initials"] = "|".join(initials(r["sourceText"]) for r in dip_records)

    stream_hits = {
        key: instruction_hits(value)
        for key, value in streams.items()
        if instruction_hits(value)
    }
    result = {
        "source": {
            "graph": str(GRAPH_JSON),
            "mirror": str(MIRROR_JSON),
            "canonical": str(CANONICAL_JSON),
        },
        "counts": {
            "page76MediumStrongEdges": len(page76_edges),
            "dedupTargetSourceEdges": len(deduped_edges),
            "strongOnlyEdges": len(strong_edges),
            "highresMeaningfulEdges": len(highres_records),
            "dipEdges": len(dip_records),
        },
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "highresRecords": highres_records,
        "dipRecords": dip_records,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines_out = [
        "# Page-76 Two-Hand Selector Audit",
        "",
        "Scope: constrained page-76 selector checks from the reflected graph and high-res B1B1B2O3 intersections. No private-key candidates are generated.",
        "",
        "## Counts",
        "",
    ]
    for key, value in result["counts"].items():
        lines_out.append(f"- {key}: {value}")

    lines_out.extend(["", "## Streams", ""])
    priority = [
        "graph_all:source_pages",
        "graph_all:bits_79_is_1",
        "graph_all:bits79_ascii_7",
        "graph_all:bits79_ascii_8",
        "graph_all:78_first_79_last",
        "graph_all:78_last_79_first",
        "graph_dedup_target_source:source_pages",
        "graph_dedup_target_source:78_first_79_last",
        "graph_dedup_target_source:78_last_79_first",
        "graph_strong_only:source_pages",
        "graph_strong_only:78_first_79_last",
        "graph_strong_only:78_last_79_first",
        "highres:target_pattern",
        "highres:source_page_pattern",
        "highres:source_index_pattern",
        "highres:target_line_initials",
        "highres:above_line_initials",
        "highres:below_line_initials",
        "highres:target_word_by_source_index_1based",
        "highres:target_word_by_source_index_0based",
        "highres:source_word_by_target_index_1based",
        "highres:source_word_by_target_index_0based",
        "dip:above_initials",
        "dip:target_initials",
        "dip:below_initials",
        "dip:source_initials",
    ]
    for key in priority:
        value = streams.get(key, "")
        hits = stream_hits.get(key)
        suffix = f" hits={hits}" if hits else ""
        lines_out.append(f"- `{key}`: `{value}`{suffix}")

    lines_out.extend(["", "## High-Res B1B1B2O3 Records", ""])
    for r in highres_records:
        lines_out.append(
            f"- {r['pattern']} p{r['sourcePage']} src#{r['sourceIndex']} `{clean(r['sourceLabel'])}` -> "
            f"line {r['targetLineIndex']} `{clean(r['targetLine'])}` | "
            f"srcIdx1 target word=`{r['targetWordBySourceIndex1']}`; "
            f"targetIdx1 source word=`{r['sourceWordByTargetIndex1']}`; "
            f"below=`{clean(r['belowLine'], 70)}`"
        )

    lines_out.extend(["", "## Dip Adjacent-Line Records", ""])
    for r in dip_records:
        lines_out.append(
            f"- {r['strength']} p{r['sourcePage']} `{clean(r['sourceText'], 80)}` -> "
            f"above=`{clean(r['above'], 65)}` target=`{clean(r['target'], 65)}` below=`{clean(r['below'], 65)}`"
        )

    lines_out.extend(
        [
            "",
            "## Assessment",
            "",
            "- The 78/79 source-page pattern does not decode to printable 7-bit or 8-bit text, and first/last two-hand rules do not create instruction-like language.",
            "- Deduping by target/source and using strong edges only reduces repetition but still produces short non-instruction streams.",
            "- The compact high-res `B1B1B2O3` branch gives one phrase-like stream, `That's all right fiat`, when using target box number to select a word from the reflected source phrase. It is weak: it is not an instruction, it does not select page-76 characters, and the fourth word is just inherited fiat-language context.",
            "- Reading above/below the `buying the dip` target produces initials only (`ttt` above, `III` below) and repeats the corridor narrative rather than giving a selector.",
            "- Keep page 76 as the target surface, but do not promote the current 78/79 two-hand or B1B1B2O3 interpretations without a new registration/source clue.",
        ]
    )
    OUT_MD.write_text("\n".join(lines_out) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()

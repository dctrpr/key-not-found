#!/usr/bin/env python3
"""Intersect Typeka font states with confirmed page-76 reflected-highlight hits."""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "analysis_outputs" / "docm_format_sources" / "article_with_fonts_runs.json"
FONT_AUDIT = ROOT / "analysis_outputs" / "docm_format_sources" / "docm_font_layer_audit.json"
GRAPH = ROOT / "analysis_outputs" / "3d_article_map" / "reflected_highlight_graph.json"
OUT_DIR = ROOT / "analysis_outputs" / "docm_format_sources"
MD_OUT = OUT_DIR / "typeka_reflection_intersection_audit.md"
JSON_OUT = OUT_DIR / "typeka_reflection_intersection_audit.json"


def strip_accents(value: str) -> str:
    return "".join(
        ch
        for ch in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(ch)
    )


def norm_word(value: str) -> str:
    value = strip_accents(value)
    value = value.replace("¥", "f").replace("’", "'").replace("‘", "'")
    value = value.replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9$%']", "", value.lower())


def word_tokens(text: str) -> list[dict]:
    tokens = []
    for match in re.finditer(r"[A-Za-z0-9$%¥éÉ'’]+", text):
        norm = norm_word(match.group(0))
        if not norm:
            continue
        tokens.append(
            {
                "text": match.group(0),
                "norm": norm,
                "start": match.start(),
                "end": match.end(),
            }
        )
    return tokens


def page_for_paragraph(paragraph: int, boundaries: list[dict]) -> int | None:
    for item in boundaries:
        if item["paragraphStart"] <= paragraph <= item["paragraphEnd"]:
            return item["page"]
    return None


def variant(run: dict) -> str:
    font = run.get("fontAscii") or run.get("fontHAnsi") or ""
    if font == "Typeka Mix":
        return "MIX_BOLD" if run.get("bold") else "MIX"
    if font == "Typeka":
        return "TYPEKA_BOLD" if run.get("bold") else "TYPEKA"
    if font == "Stencil":
        return "STENCIL"
    if font == "LonestarW00-Regular":
        return "LONESTAR"
    return "OTHER"


def build_pages() -> dict[int, dict]:
    runs = json.loads(RUNS.read_text())
    boundaries = json.loads(FONT_AUDIT.read_text())["pageBoundariesByParagraph"]
    pages: dict[int, dict] = {}
    for run in runs:
        page = page_for_paragraph(run["paragraphIndex"], boundaries)
        if page is None:
            continue
        item = pages.setdefault(page, {"text": "", "chars": [], "runs": []})
        run_variant = variant(run)
        run_start = len(item["text"])
        text = run.get("text") or ""
        item["text"] += text
        run_record = {
            "runIndex": run["runIndex"],
            "page": page,
            "variant": run_variant,
            "font": run.get("fontAscii"),
            "bold": bool(run.get("bold")),
            "highlight": run.get("highlight"),
            "sizeHalfPoints": run.get("sizeHalfPoints"),
            "start": run_start,
            "end": run_start + len(text),
            "text": text,
        }
        item["runs"].append(run_record)
        for idx, ch in enumerate(text):
            item["chars"].append({**run_record, "char": ch, "pos": run_start + idx})
    for page, item in pages.items():
        item["tokens"] = word_tokens(item["text"])
    return pages


def find_phrase(page: dict, phrase: str) -> dict:
    q_tokens = [token["norm"] for token in word_tokens(phrase)]
    p_tokens = page["tokens"]
    if not q_tokens:
        return {"status": "empty", "score": 0.0}

    # Exact normalized token sequence first.
    for i in range(0, max(0, len(p_tokens) - len(q_tokens) + 1)):
        window = [token["norm"] for token in p_tokens[i : i + len(q_tokens)]]
        if window == q_tokens:
            return {
                "status": "exact",
                "score": 1.0,
                "tokenStart": i,
                "tokenEnd": i + len(q_tokens),
                "charStart": p_tokens[i]["start"],
                "charEnd": p_tokens[i + len(q_tokens) - 1]["end"],
            }

    # Fuzzy word-window fallback for OCR'd reflected snippets.
    best = {"status": "not_found", "score": 0.0}
    q_join = " ".join(q_tokens)
    for n in range(max(1, len(q_tokens) - 3), len(q_tokens) + 4):
        if n > len(p_tokens):
            continue
        for i in range(0, len(p_tokens) - n + 1):
            window = [token["norm"] for token in p_tokens[i : i + n]]
            score = difflib.SequenceMatcher(None, q_join, " ".join(window)).ratio()
            if score > best["score"]:
                best = {
                    "status": "fuzzy",
                    "score": round(score, 4),
                    "tokenStart": i,
                    "tokenEnd": i + n,
                    "charStart": p_tokens[i]["start"],
                    "charEnd": p_tokens[i + n - 1]["end"],
                }
    if best["score"] < 0.48:
        best["status"] = "not_found"
    return best


def summarize_match(page: dict, match: dict) -> dict:
    if match["status"] in {"empty", "not_found"}:
        return {
            "status": match["status"],
            "score": match["score"],
            "text": "",
            "variantCounts": {},
            "highlightCounts": {},
            "runs": [],
        }
    start, end = match["charStart"], match["charEnd"]
    chars = [ch for ch in page["chars"] if start <= ch["pos"] < end and ch["char"].strip()]
    variants = Counter(ch["variant"] for ch in chars)
    highlights = Counter(ch["highlight"] or "none" for ch in chars)
    run_map = {}
    for ch in chars:
        idx = ch["runIndex"]
        if idx not in run_map:
            run_map[idx] = {
                "runIndex": idx,
                "variant": ch["variant"],
                "font": ch["font"],
                "bold": ch["bold"],
                "highlight": ch["highlight"],
                "sizeHalfPoints": ch["sizeHalfPoints"],
                "text": ch["text"],
            }
    return {
        "status": match["status"],
        "score": match["score"],
        "text": page["text"][start:end],
        "variantCounts": dict(variants),
        "highlightCounts": dict(highlights),
        "runs": list(run_map.values()),
    }


def short_counts(counts: dict) -> str:
    if not counts:
        return "-"
    return ", ".join(f"{k}:{v}" for k, v in sorted(counts.items()))


def main() -> None:
    pages = build_pages()
    graph = json.loads(GRAPH.read_text())
    edges = [
        edge
        for edge in graph["edges"]
        if edge["targetPage"] == 76 and edge["strength"] in {"medium", "strong"}
    ]

    target_records = {}
    for edge in edges:
        key = (edge["targetId"], edge["targetText"], edge["targetColor"])
        if key not in target_records:
            match = find_phrase(pages[76], edge["targetText"])
            target_records[key] = {
                "targetId": edge["targetId"],
                "targetText": edge["targetText"],
                "targetColor": edge["targetColor"],
                "match": summarize_match(pages[76], match),
                "edges": [],
            }
        refl_match = find_phrase(pages[76], edge["reflectionText"])
        target_records[key]["edges"].append(
            {
                "sourcePage": edge["sourcePage"],
                "reflectionId": edge["reflectionId"],
                "strength": edge["strength"],
                "overlapVsSpan": edge["overlapVsSpan"],
                "overlapVsReflection": edge["overlapVsReflection"],
                "reflectionText": edge["reflectionText"],
                "reflectionMatch": summarize_match(pages[76], refl_match),
            }
        )

    grouped_summary = []
    for record in target_records.values():
        target_variants = record["match"]["variantCounts"]
        reflection_variant_counter = Counter()
        reflection_status = Counter()
        has_mix = 0
        for edge in record["edges"]:
            reflection_status[edge["reflectionMatch"]["status"]] += 1
            reflection_variant_counter.update(edge["reflectionMatch"]["variantCounts"])
            if any(
                run["variant"].startswith("MIX")
                for run in edge["reflectionMatch"].get("runs", [])
            ):
                has_mix += 1
        grouped_summary.append(
            {
                "targetId": record["targetId"],
                "targetText": record["targetText"],
                "targetColor": record["targetColor"],
                "targetVariantCounts": target_variants,
                "edgeCount": len(record["edges"]),
                "reflectionMatchStatus": dict(reflection_status),
                "reflectionVariantCounts": dict(reflection_variant_counter),
                "reflectionEdgesWithMix": has_mix,
            }
        )

    result = {
        "sourceRuns": str(RUNS),
        "sourceGraph": str(GRAPH),
        "summary": grouped_summary,
        "targets": list(target_records.values()),
        "assessment": [
            "All page-76 reflected-hit target spans resolve to Typeka-bold runs, usually with orange/yellow or black highlight.",
            "Typeka Mix appears mostly in the reflected snippet windows around semantic anchors such as George Clinton and El Salvador, not as a one-character selector inside the target spans.",
            "The Typeka intersection is explanatory but not selective enough: it does not reduce the five/six page-76 target spans to one ordered key stream.",
            "Next move should combine Typeka states with a stricter visual registration rule, not rerun font-state strings through key derivation.",
        ],
    }
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Typeka Reflection Intersection Audit",
        "",
        "Scope: intersect `Article with Fonts.docm` Typeka states with the medium/strong page-76 reflected-highlight graph. This is a selector test only; no key candidates were generated.",
        "",
        "## Target Summary",
        "",
    ]
    for item in grouped_summary:
        lines.append(
            f"- `{item['targetText']}` ({item['targetColor']}, {item['targetId']}): "
            f"targetVariants={short_counts(item['targetVariantCounts'])}; "
            f"edges={item['edgeCount']}; reflectionStatus={short_counts(item['reflectionMatchStatus'])}; "
            f"reflectionVariants={short_counts(item['reflectionVariantCounts'])}; "
            f"edgesWithMix={item['reflectionEdgesWithMix']}"
        )

    lines.extend(["", "## Edge Details", ""])
    for record in target_records.values():
        lines.append(f"### {record['targetId']} {record['targetColor']} `{record['targetText']}`")
        lines.append(
            f"- target match `{record['match']['status']}` score={record['match']['score']} "
            f"variants={short_counts(record['match']['variantCounts'])} highlights={short_counts(record['match']['highlightCounts'])}"
        )
        for edge in record["edges"]:
            match = edge["reflectionMatch"]
            text = match["text"].replace("\n", " ")
            if len(text) > 140:
                text = text[:140] + "..."
            lines.append(
                f"- {edge['strength']} {edge['sourcePage']}->76 {edge['reflectionId']} "
                f"ovRefl={edge['overlapVsReflection']:.3f} ovSpan={edge['overlapVsSpan']:.3f}: "
                f"refMatch={match['status']} score={match['score']} variants={short_counts(match['variantCounts'])} "
                f"text=`{text or edge['reflectionText']}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Assessment",
            "",
            "- The confirmed page-76 target spans are almost entirely `TYPEKA_BOLD`, which mostly restates that the high-signal target spans are highlighted/bold article phrases.",
            "- `Typeka Mix` shows up in nearby/reflected snippet matches around semantic anchors, especially `George Clinton` and `El Salvador`, but it does not create a cleaner one-edge-per-letter or one-edge-per-word selector.",
            "- This rules out a simple rule such as “take Typeka Mix inside the reflected target spans.”",
            "- Keep Typeka as a layer, but it needs stricter visual registration or another instruction before it is useful for extraction.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n")
    print(MD_OUT)
    print(JSON_OUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Test the color-swap subset of raw page-76 mirror contacts.

The previous all-source benchmark showed p79 has both orange->grey and
grey->orange contacts when mirrored onto page 76. This audit asks whether that
stricter, human-plausible filter produces an instruction or only a conceptual
orientation contrast. No key derivation is performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from highres_reflection_extract import upright_image


ROOT = Path(__file__).resolve().parents[1]
BENCH_JSON = ROOT / "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/page76_all_source_highlight_mirror_benchmark.json"
OUT = ROOT / "analysis_outputs/source_audit/page76_color_swap_mirror_filter"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_color_swap_mirror_filter.json"
OUT_MD = OUT / "page76_color_swap_mirror_filter.md"
OUT_IMG = OUT / "page76_color_swap_mirror_filter_overlay.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "fold",
    "mirror",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "key",
    "private",
    "seed",
    "wif",
    "address",
    "reverse",
    "backward",
    "order",
    "index",
]


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def instruction_hits(text: str) -> list[str]:
    words = set(norm(text).split())
    return [term for term in INSTRUCTION_TERMS if term in words]


def font(size: int = 24) -> ImageFont.ImageFont:
    for name in ("Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def transition(edge: dict[str, Any]) -> str:
    return f"{edge['sourceKind']}->{edge['targetKind']}"


def target_sort_key(edge: dict[str, Any]) -> tuple[int, int]:
    kind_rank = {"orange": 0, "grey": 1}
    return (kind_rank.get(edge["targetKind"], 2), int(edge["targetIndex"]))


def source_sort_key(edge: dict[str, Any]) -> tuple[float, float]:
    box = edge["sourceBox"]
    return ((box[1] + box[3]) / 2, (box[0] + box[2]) / 2)


def draw_overlay(color_swap_edges: list[dict[str, Any]], bidirectional_pages: list[int]) -> None:
    img = upright_image(76).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    f = font(38)
    small = font(24)
    page_colors = {
        79: (150, 0, 255, 220),
        77: (0, 120, 255, 180),
        78: (255, 0, 120, 180),
        75: (100, 100, 100, 160),
        80: (100, 100, 100, 160),
    }
    target_seen: set[tuple[float, float, float, float]] = set()
    for edge in color_swap_edges:
        tbox = tuple(edge["targetBox"])
        if tbox not in target_seen:
            color = (255, 95, 0, 255) if edge["targetKind"] == "orange" else (0, 190, 230, 255)
            draw.rectangle(tuple(int(round(v)) for v in tbox), outline=color, width=6)
            draw.text(
                (int(edge["targetBox"][0]), max(0, int(edge["targetBox"][1]) - 30)),
                edge["targetId"],
                fill=color,
                font=small,
            )
            target_seen.add(tbox)
        scolor = page_colors.get(edge["sourcePage"], (180, 0, 255, 180))
        draw.rectangle(tuple(int(round(v)) for v in edge["reflectedBox"]), outline=scolor, width=4)
        draw.rectangle(tuple(int(round(v)) for v in edge["intersection"]), outline=(40, 255, 70, 255), width=5)
        draw.text(
            (int(edge["reflectedBox"][0]), max(0, int(edge["reflectedBox"][1]) - 24)),
            f"p{edge['sourcePage']} {transition(edge)}",
            fill=scolor,
            font=small,
        )

    title = "Color-swap mirror filter: bidirectional pages " + (", ".join(map(str, bidirectional_pages)) or "none")
    draw.rectangle([0, 0, img.width, 90], fill=(255, 255, 255, 235))
    draw.text((28, 26), title, fill=(20, 20, 20, 255), font=f)
    Image.alpha_composite(img, overlay).convert("RGB").save(OUT_IMG, quality=94)


def main() -> None:
    bench = json.loads(BENCH_JSON.read_text(encoding="utf-8"))
    all_edges = [edge for report in bench["reports"] for edge in report["edges"]]
    strong_edges = [
        edge
        for edge in all_edges
        if edge["overlapVsSource"] >= 0.05 or edge["overlapVsTarget"] >= 0.05
    ]
    color_swap_edges = [edge for edge in strong_edges if edge["sourceKind"] != edge["targetKind"]]
    same_color_edges = [edge for edge in strong_edges if edge["sourceKind"] == edge["targetKind"]]

    by_page: dict[int, list[dict[str, Any]]] = {}
    for edge in color_swap_edges:
        by_page.setdefault(edge["sourcePage"], []).append(edge)

    bidirectional_pages = []
    page_summaries = []
    for page, edges in sorted(by_page.items()):
        transitions = sorted({transition(edge) for edge in edges})
        has_otg = any(edge["sourceKind"] == "orange" and edge["targetKind"] == "grey" for edge in edges)
        has_gto = any(edge["sourceKind"] == "grey" and edge["targetKind"] == "orange" for edge in edges)
        if has_otg and has_gto:
            bidirectional_pages.append(page)
        page_summaries.append(
            {
                "sourcePage": page,
                "colorSwapEdges": len(edges),
                "transitions": transitions,
                "targets": sorted({edge["targetId"] for edge in edges}, key=lambda x: (x[0], int(x[1:]))),
                "bidirectional": has_otg and has_gto,
            }
        )

    selected_edges = [edge for edge in color_swap_edges if edge["sourcePage"] in set(bidirectional_pages)]
    source_order = sorted(selected_edges, key=source_sort_key)
    target_order = sorted(selected_edges, key=target_sort_key)
    score_order = sorted(selected_edges, key=lambda edge: (-edge["score"], target_sort_key(edge)))

    streams = {
        "sourceOrderSourceLabels": " | ".join(edge["sourceLabel"] for edge in source_order),
        "sourceOrderTargetLabels": " | ".join(edge["targetLabel"] for edge in source_order),
        "targetOrderSourceLabels": " | ".join(edge["sourceLabel"] for edge in target_order),
        "targetOrderTargetLabels": " | ".join(edge["targetLabel"] for edge in target_order),
        "scoreOrderTargetLabels": " | ".join(edge["targetLabel"] for edge in score_order),
        "targetIds": " ".join(edge["targetId"] for edge in target_order),
        "transitions": " ".join(transition(edge) for edge in source_order),
        "targetInitials": "".join(edge["targetLabel"][:1] for edge in target_order if edge["targetLabel"]),
        "sourceInitials": "".join(edge["sourceLabel"][:1] for edge in source_order if edge["sourceLabel"]),
    }
    stream_hits = {name: instruction_hits(value) for name, value in streams.items()}

    draw_overlay(color_swap_edges, bidirectional_pages)

    decision = (
        "The color-swap filter is useful as a noise reducer because only p79 has both orange->grey and grey->orange "
        "contacts. But the surviving p79 set selects the upper page-76 energy/war/toxicity/fiat-nonsense contrast, not "
        "the lower G5/O5 corridor. Its only instruction-term hits are `take` and `right` inside the printed sentence "
        "`That’s right, Bitcoin will take`, not procedural commands, so the streams still name no extraction unit."
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Color-swap subset of raw all-source page-76 mirror contacts; no OCR extraction or key derivation.",
        "input": str(BENCH_JSON),
        "strongEdges": len(strong_edges),
        "colorSwapEdges": color_swap_edges,
        "sameColorEdges": same_color_edges,
        "pageSummaries": page_summaries,
        "bidirectionalColorSwapPages": bidirectional_pages,
        "selectedEdges": selected_edges,
        "streams": streams,
        "instructionHits": stream_hits,
        "overlay": str(OUT_IMG),
        "decision": decision,
        "nextMove": "Keep p79 color-swap as an orientation/concept filter only. Do not derive keys from it unless a future clue points specifically to color swapping, energy/war contrast, or the upper page-76 cluster.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page 76 Color-Swap Mirror Filter",
        "",
        "Scope: test only mirrored highlight contacts where the source and target highlight colors swap, plus the stricter condition that a source page must contain both swap directions. No OCR extraction, hashing, seed checking, WIF checking, address checking, or key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_IMG}`",
        f"- Strong input edges: `{len(strong_edges)}`",
        f"- Color-swap edges: `{len(color_swap_edges)}`",
        f"- Bidirectional color-swap pages: `{bidirectional_pages}`",
        "",
        "## Page Summary",
        "",
        "| source page | swap edges | transitions | targets | bidirectional |",
        "|---:|---:|---|---|---:|",
    ]
    for row in page_summaries:
        lines.append(
            f"| `{row['sourcePage']}` | `{row['colorSwapEdges']}` | `{' '.join(row['transitions'])}` | "
            f"`{' '.join(row['targets'])}` | `{row['bidirectional']}` |"
        )
    lines.extend(["", "## Selected p79 Streams", ""])
    for name, value in streams.items():
        if not value:
            continue
        hits = stream_hits[name]
        lines.append(f"- `{name}`: `{value}`" + (f" | instruction hits: `{hits}`" if hits else ""))
    lines.extend(["", "## Selected Edges", ""])
    if not selected_edges:
        lines.append("- No bidirectional color-swap edges survived.")
    for edge in score_order:
        lines.append(
            f"- p{edge['sourcePage']} {edge['sourceKind']} `{edge['sourceLabel']}` -> "
            f"{edge['targetId']} {edge['targetKind']} `{edge['targetLabel']}` "
            f"(source={edge['overlapVsSource']}, target={edge['overlapVsTarget']}, dist={edge['centerDistance']})"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {decision}",
            "- This closes color-swap mirroring as a standalone selector under the current scan.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Summarize puzzle-relevant font layers from Article with Fonts.docm."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IN_RUNS = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
OUT_MD = ROOT / "analysis_outputs/docm_format_sources/docm_font_layer_audit.md"
OUT_JSON = ROOT / "analysis_outputs/docm_format_sources/docm_font_layer_audit.json"


PAGE_BY_PARAGRAPH = [
    (75, 0, 39),
    (76, 41, 73),
    (77, 75, 108),
    (78, 110, 139),
    (79, 141, 168),
]


def page_for_para(idx: int) -> int | None:
    for page, start, end in PAGE_BY_PARAGRAPH:
        if start <= idx <= end:
            return page
    return None


def letters(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z0-9$]", text))


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def stream(runs: list[dict]) -> str:
    return clean("".join(r["text"] for r in runs))


def letter_stream(runs: list[dict]) -> str:
    return "".join(letters(r["text"]) for r in runs)


def main() -> None:
    runs = json.loads(IN_RUNS.read_text())
    canonical = json.loads(CANONICAL.read_text())
    canonical_partial = canonical["streams"].get("partialBoldLetters", "")
    canonical_all_bold = canonical["streams"].get("allBoldLetters", "")

    layer_defs = {
        "cyan": lambda r: r.get("highlight") == "cyan",
        "yellow": lambda r: r.get("highlight") == "yellow",
        "black": lambda r: r.get("highlight") == "black",
        "typeka_mix": lambda r: (r.get("fontAscii") or "") == "Typeka Mix",
        "underline": lambda r: bool(r.get("underline")),
        "strike": lambda r: bool(r.get("strike")),
        "bold": lambda r: bool(r.get("bold")),
        "lonestar": lambda r: (r.get("fontAscii") or "") == "LonestarW00-Regular",
        "stencil": lambda r: (r.get("fontAscii") or "") == "Stencil",
    }

    pages: dict[int, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    all_layers: dict[str, list[dict]] = defaultdict(list)
    unmapped = []
    for r in runs:
        page = page_for_para(r["paragraphIndex"])
        if page is None:
            if clean(r["text"]):
                unmapped.append(r)
            continue
        for name, pred in layer_defs.items():
            if pred(r):
                pages[page][name].append(r)
                all_layers[name].append(r)

    all_streams = {
        name: {
            "text": stream(rs),
            "letters": letter_stream(rs),
            "runCount": len(rs),
            "charCount": sum(len(r["text"]) for r in rs),
        }
        for name, rs in sorted(all_layers.items())
    }
    page_streams = {
        str(page): {
            name: {
                "text": stream(rs),
                "letters": letter_stream(rs),
                "runCount": len(rs),
                "charCount": sum(len(r["text"]) for r in rs),
            }
            for name, rs in sorted(layer_map.items())
        }
        for page, layer_map in sorted(pages.items())
    }

    comparison = {
        "canonicalPartialBoldLength": len(canonical_partial),
        "canonicalPartialBoldPreview": canonical_partial[:500],
        "canonicalAllBoldLength": len(canonical_all_bold),
        "docmTypekaMixLettersLength": len(all_streams.get("typeka_mix", {}).get("letters", "")),
        "docmTypekaMixPreview": all_streams.get("typeka_mix", {}).get("letters", "")[:500],
        "docmCyanLetters": all_streams.get("cyan", {}).get("letters", ""),
    }

    result = {
        "sourceRuns": str(IN_RUNS),
        "pageBoundariesByParagraph": [
            {"page": p, "paragraphStart": s, "paragraphEnd": e} for p, s, e in PAGE_BY_PARAGRAPH
        ],
        "allStreams": all_streams,
        "pageStreams": page_streams,
        "comparisonToCanonical": comparison,
        "unmappedNonblankRuns": [
            {"runIndex": r["runIndex"], "paragraphIndex": r["paragraphIndex"], "text": r["text"]}
            for r in unmapped
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# DOCM Font Layer Audit",
        "",
        "Scope: treat `Article with Fonts.docm` as a formatting witness and extract short font/highlight layers without key derivation.",
        "",
        "## Global Layer Streams",
        "",
    ]
    for name, info in all_streams.items():
        txt = info["text"]
        preview = txt[:700] + ("..." if len(txt) > 700 else "")
        md.append(f"- `{name}` runs={info['runCount']} chars={info['charCount']} lettersLen={len(info['letters'])}: `{preview}`")

    md.extend(["", "## Per-Page Short/Important Layers", ""])
    important = ["cyan", "typeka_mix", "yellow", "black", "underline", "strike", "lonestar", "stencil"]
    for page in sorted(page_streams, key=int):
        md.append(f"### p{page}")
        layer_map = page_streams[page]
        for name in important:
            if name not in layer_map:
                continue
            info = layer_map[name]
            txt = info["text"]
            preview = txt[:700] + ("..." if len(txt) > 700 else "")
            md.append(f"- `{name}` runs={info['runCount']} chars={info['charCount']} letters=`{info['letters'][:180]}` text=`{preview}`")

    md.extend(["", "## Comparison To Existing Canonical Model", ""])
    for key, value in comparison.items():
        md.append(f"- `{key}`: `{value}`")

    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- `Article with Fonts.docm` is the cleanest local formatting witness for Word-level font/highlight state.",
            "- Yellow and black layers reproduce the already-known orange/grey highlight structure, with useful punctuation/wording corrections.",
            "- The new short layer is cyan: `MNBILLION` (`M` in Max, `N` in Nocoiners, `BILLION` inside `$85 BILLION`). This is too short to solve by itself, but it should be registered as a possible selector/anomaly.",
            "- `Typeka Mix` is a substantial alternate-font layer. It overlaps many user-marked partial-bold words but is not identical to the previous Markdown partial-bold stream, so future partial-bold work should prefer this DOCM source over manual markup.",
            "- No private-key checks were run. This is a formatting-source integration pass only.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()

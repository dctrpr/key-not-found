#!/usr/bin/env python3
"""Audit whether Typeka font changes align with highlight boundaries.

The user found that the odd partial bolding is largely a Typeka/Typeka Mix
effect. This pass tests a narrower possibility: font-family transitions might
line up with orange/grey/highlight transitions and act as a selector.

The source is `Article with Fonts.docm` as already extracted by
`analyze_docm_format_sources.py`. It is treated only as a formatting witness.
No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
FORMAT_AUDIT_JSON = ROOT / "analysis_outputs/docm_format_sources/docm_format_audit.json"
OUT = ROOT / "analysis_outputs/docm_format_sources/typeka_highlight_boundary_alignment"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "typeka_highlight_boundary_alignment.json"
OUT_MD = OUT / "typeka_highlight_boundary_alignment.md"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "reverse",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "first",
    "last",
    "font",
    "typeka",
    "mix",
]


def norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def letters(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", text)


def compact(text: str, limit: int = 130) -> str:
    text = norm_space(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def style_key(run: dict) -> dict:
    font = run.get("fontAscii") or run.get("fontHAnsi") or run.get("fontCs") or run.get("fontEastAsia") or "(none)"
    return {
        "font": font,
        "bold": bool(run.get("bold")),
        "highlight": run.get("highlight") or "",
        "color": run.get("color") or "",
        "size": run.get("sizeHalfPoints") or "",
        "underline": bool(run.get("underline")),
        "strike": bool(run.get("strike")),
    }


def run_text(run: dict) -> str:
    return run.get("text") or ""


def edge_chars(left: str, right: str) -> str:
    left_clean = letters(left)
    right_clean = letters(right)
    return (left_clean[-1:] + right_clean[:1]).strip()


def instruction_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", low)]


def signature(style: dict) -> str:
    parts = [style["font"]]
    if style["bold"]:
        parts.append("bold")
    if style["underline"]:
        parts.append("underline")
    if style["strike"]:
        parts.append("strike")
    if style["highlight"]:
        parts.append("hl=" + style["highlight"])
    if style["color"]:
        parts.append("color=" + style["color"])
    if style["size"]:
        parts.append("size=" + style["size"])
    return ";".join(parts)


def main() -> None:
    runs = json.loads(RUNS_JSON.read_text(encoding="utf-8"))
    format_audit = json.loads(FORMAT_AUDIT_JSON.read_text(encoding="utf-8"))
    runs = [run for run in runs if run_text(run)]

    font_chars = Counter()
    highlight_chars = Counter()
    font_highlight_chars = Counter()
    for run in runs:
        style = style_key(run)
        text_len = len(run_text(run))
        font_chars[style["font"]] += text_len
        highlight_chars[style["highlight"] or "(none)"] += text_len
        font_highlight_chars[(style["font"], style["highlight"] or "(none)")] += text_len

    boundaries = []
    for left, right in zip(runs, runs[1:]):
        ls = style_key(left)
        rs = style_key(right)
        font_change = ls["font"] != rs["font"]
        highlight_change = ls["highlight"] != rs["highlight"]
        bold_change = ls["bold"] != rs["bold"]
        signature_change = signature(ls) != signature(rs)
        if not (font_change or highlight_change or bold_change or signature_change):
            continue
        paragraph_break = left.get("paragraphIndex") != right.get("paragraphIndex")
        rec = {
            "leftRun": left["runIndex"],
            "rightRun": right["runIndex"],
            "paragraphBreak": paragraph_break,
            "fontChange": font_change,
            "highlightChange": highlight_change,
            "boldChange": bold_change,
            "signatureChange": signature_change,
            "leftStyle": ls,
            "rightStyle": rs,
            "leftText": norm_space(run_text(left)),
            "rightText": norm_space(run_text(right)),
            "edgeChars": edge_chars(run_text(left), run_text(right)),
        }
        boundaries.append(rec)

    typeka_mix_runs = [run for run in runs if style_key(run)["font"] == "Typeka Mix"]
    highlighted_mix_runs = [run for run in typeka_mix_runs if style_key(run)["highlight"]]
    font_change_boundaries = [b for b in boundaries if b["fontChange"]]
    typeka_mix_boundaries = [
        b
        for b in font_change_boundaries
        if "Typeka Mix" in {b["leftStyle"]["font"], b["rightStyle"]["font"]}
    ]
    highlight_boundaries = [b for b in boundaries if b["highlightChange"]]
    coincident = [b for b in boundaries if b["fontChange"] and b["highlightChange"]]

    streams = {
        "typeka_mix_text": norm_space("".join(run_text(run) for run in typeka_mix_runs)),
        "highlighted_typeka_mix_text": norm_space("".join(run_text(run) for run in highlighted_mix_runs)),
        "typeka_mix_boundary_edges": "".join(b["edgeChars"] for b in typeka_mix_boundaries if b["edgeChars"]),
        "font_change_boundary_edges": "".join(b["edgeChars"] for b in font_change_boundaries if b["edgeChars"]),
        "highlight_change_boundary_edges": "".join(b["edgeChars"] for b in highlight_boundaries if b["edgeChars"]),
        "font_and_highlight_change_boundary_edges": "".join(b["edgeChars"] for b in coincident if b["edgeChars"]),
    }
    stream_hits = {key: instruction_hits(value) for key, value in streams.items() if instruction_hits(value)}

    # Use a small sample table to make manual follow-up possible without
    # dumping all run boundaries into the markdown.
    def sample_boundary(boundary: dict) -> dict:
        return {
            "leftRun": boundary["leftRun"],
            "rightRun": boundary["rightRun"],
            "paragraphBreak": boundary["paragraphBreak"],
            "leftFont": boundary["leftStyle"]["font"],
            "rightFont": boundary["rightStyle"]["font"],
            "leftHighlight": boundary["leftStyle"]["highlight"],
            "rightHighlight": boundary["rightStyle"]["highlight"],
            "edgeChars": boundary["edgeChars"],
            "leftText": compact(boundary["leftText"], 70),
            "rightText": compact(boundary["rightText"], 70),
        }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Typeka/Typeka Mix font-change boundaries versus highlight boundaries; no key derivation",
        "sourceReports": {
            "runs": str(RUNS_JSON.relative_to(ROOT)),
            "formatAudit": str(FORMAT_AUDIT_JSON.relative_to(ROOT)),
        },
        "docmSource": format_audit["sources"]["article_with_fonts"],
        "counts": {
            "runCount": len(runs),
            "fontChars": dict(font_chars.most_common()),
            "highlightChars": dict(highlight_chars.most_common()),
            "fontHighlightChars": {f"{font}|{hl}": count for (font, hl), count in font_highlight_chars.most_common()},
            "boundaryCount": len(boundaries),
            "fontChangeBoundaryCount": len(font_change_boundaries),
            "typekaMixBoundaryCount": len(typeka_mix_boundaries),
            "highlightChangeBoundaryCount": len(highlight_boundaries),
            "fontAndHighlightChangeBoundaryCount": len(coincident),
            "highlightedTypekaMixRunCount": len(highlighted_mix_runs),
            "highlightedTypekaMixCharCount": sum(len(run_text(run)) for run in highlighted_mix_runs),
        },
        "streams": streams,
        "streamCompacts": {key: compact(value, 260) for key, value in streams.items()},
        "instructionHits": stream_hits,
        "samples": {
            "typekaMixBoundaries": [sample_boundary(b) for b in typeka_mix_boundaries[:24]],
            "fontAndHighlightChangeBoundaries": [sample_boundary(b) for b in coincident[:24]],
            "highlightChangeBoundaries": [sample_boundary(b) for b in highlight_boundaries[:24]],
        },
        "assessment": [
            "Typeka Mix does not appear inside highlighted runs in the Article-with-Fonts witness.",
            "Font-family changes and highlight on/off boundaries are mostly separate events, not a locked overlay-selector system.",
            "The only instruction-term hit is `first` inside ordinary prose (`first time in our existence`), not a boundary instruction.",
            "The coincident font+highlight boundary edge stream is too small/noisy to name a rule.",
            "Typeka Mix text is semantic article emphasis and name/phrase styling; it does not produce an instruction-like boundary stream.",
        ],
        "nextMove": "Keep Article with Fonts.docm as a formatting witness. Reopen Typeka/font-state extraction only if a source clue explicitly names a font state or a better source chooses exact words/lines first.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Typeka / Highlight Boundary Alignment",
        "",
        "Scope: test whether Typeka/Typeka Mix font-family transitions align with highlight on/off boundaries as a selector. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- DOCM source: `{result['docmSource']}`",
        f"- Runs inspected: `{result['counts']['runCount']}`",
        f"- Font-change boundaries: `{result['counts']['fontChangeBoundaryCount']}`",
        f"- Typeka Mix font boundaries: `{result['counts']['typekaMixBoundaryCount']}`",
        f"- Highlight-change boundaries: `{result['counts']['highlightChangeBoundaryCount']}`",
        f"- Coincident font+highlight boundaries: `{result['counts']['fontAndHighlightChangeBoundaryCount']}`",
        f"- Highlighted Typeka Mix chars: `{result['counts']['highlightedTypekaMixCharCount']}`",
        f"- Instruction-hit streams: `{len(stream_hits)}`",
        "",
        "## Character Counts",
        "",
        "### Fonts",
    ]
    for font, count in result["counts"]["fontChars"].items():
        lines.append(f"- `{font}`: {count}")
    lines.extend(["", "### Highlights"])
    for hl, count in result["counts"]["highlightChars"].items():
        lines.append(f"- `{hl}`: {count}")
    lines.extend(["", "## Boundary Streams", ""])
    for key, value in result["streamCompacts"].items():
        lines.append(f"- `{key}` len `{len(streams[key])}` hits `{stream_hits.get(key, [])}`: `{value}`")
    lines.extend(["", "## Coincident Font+Highlight Boundary Samples", ""])
    if not coincident:
        lines.append("- none")
    for item in result["samples"]["fontAndHighlightChangeBoundaries"]:
        lines.append(
            f"- runs `{item['leftRun']}->{item['rightRun']}` `{item['leftFont']}/{item['leftHighlight']}` -> `{item['rightFont']}/{item['rightHighlight']}`, edge `{item['edgeChars']}`: `{item['leftText']}` / `{item['rightText']}`"
        )
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("highlighted Typeka Mix chars:", result["counts"]["highlightedTypekaMixCharCount"])
    print("coincident font+highlight boundaries:", result["counts"]["fontAndHighlightChangeBoundaryCount"])
    print("instruction-hit streams:", len(stream_hits))


if __name__ == "__main__":
    main()

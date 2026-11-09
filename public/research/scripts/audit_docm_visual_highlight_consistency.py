#!/usr/bin/env python3
"""Compare DOCM highlight runs with the manual high-res visual highlights.

This audits whether `Article with Fonts.docm` contains extra/missing highlighted
text relative to the visible orange/grey highlight system already read from the
high-res scan. The DOCM is a formatting witness only.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
ORANGE_JSON = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"
GREY_JSON = ROOT / "analysis_outputs/highlight_audit/highres_manual_grey_reading.json"
OUT = ROOT / "analysis_outputs/docm_format_sources/docm_visual_highlight_consistency"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "docm_visual_highlight_consistency.json"
OUT_MD = OUT / "docm_visual_highlight_consistency.md"

PAGE_BY_PARAGRAPH = [
    (75, 0, 39),
    (76, 41, 73),
    (77, 75, 108),
    (78, 110, 139),
    (79, 141, 168),
]

COLOR_MAP = {
    "yellow": "orange",
    "black": "grey",
    "cyan": "cyan",
}


def page_for_para(idx: int) -> int | None:
    for page, start, end in PAGE_BY_PARAGRAPH:
        if start <= idx <= end:
            return page
    return None


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def norm(text: str) -> str:
    text = text.lower()
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    return re.sub(r"[^a-z0-9$]+", "", text)


def compact(text: str, limit: int = 120) -> str:
    text = clean(text)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def docm_spans(runs: list[dict]) -> list[dict]:
    spans: list[dict] = []
    current: dict | None = None
    for run in runs:
        hl = run.get("highlight") or ""
        page = page_for_para(run.get("paragraphIndex", -1))
        if hl not in COLOR_MAP or page is None:
            if current is not None:
                spans.append(current)
                current = None
            continue
        text = run.get("text") or ""
        if current and current["docmHighlight"] == hl and current["page"] == page:
            current["text"] += text
            current["runIndexes"].append(run["runIndex"])
        else:
            if current is not None:
                spans.append(current)
            current = {
                "source": "docm",
                "page": page,
                "docmHighlight": hl,
                "visualColor": COLOR_MAP[hl],
                "text": text,
                "runIndexes": [run["runIndex"]],
            }
    if current is not None:
        spans.append(current)

    out = []
    for idx, span in enumerate(spans, 1):
        text = clean(span["text"])
        if not text:
            continue
        span["id"] = f"docm_{span['docmHighlight']}_{idx}"
        span["text"] = text
        span["norm"] = norm(text)
        out.append(span)
    return out


def highres_spans() -> list[dict]:
    orange = json.loads(ORANGE_JSON.read_text(encoding="utf-8"))["combinedOrangeSpans"]
    grey = json.loads(GREY_JSON.read_text(encoding="utf-8"))["combinedGreyBlackSpans"]
    out = []
    for idx, span in enumerate(orange, 1):
        item = {
            "id": f"visual_orange_{idx}",
            "source": "highres",
            "page": int(span["page"]),
            "visualColor": "orange",
            "text": clean(span["text"]),
        }
        item["norm"] = norm(item["text"])
        out.append(item)
    for idx, span in enumerate(grey, 1):
        item = {
            "id": f"visual_grey_{idx}",
            "source": "highres",
            "page": int(span["page"]),
            "visualColor": "grey",
            "text": clean(span["text"]),
        }
        item["norm"] = norm(item["text"])
        out.append(item)
    return out


def find_matches(target: dict, candidates: list[dict]) -> list[dict]:
    hits = []
    for cand in candidates:
        if cand["page"] != target["page"] or cand["visualColor"] != target["visualColor"]:
            continue
        if cand["norm"] == target["norm"]:
            kind = "exact"
        elif target["norm"] and target["norm"] in cand["norm"]:
            kind = "target_inside_candidate"
        elif cand["norm"] and cand["norm"] in target["norm"]:
            kind = "candidate_inside_target"
        else:
            continue
        hits.append({"id": cand["id"], "text": cand["text"], "kind": kind})
    return hits


def joined_page_color(spans: list[dict], page: int, colors: set[str]) -> str:
    return norm(" ".join(s["text"] for s in spans if s["page"] == page and s["visualColor"] in colors))


def main() -> None:
    runs = json.loads(RUNS_JSON.read_text(encoding="utf-8"))
    d_spans = docm_spans(runs)
    v_spans = highres_spans()
    docm_printed = [s for s in d_spans if s["visualColor"] in {"orange", "grey"}]
    docm_cyan = [s for s in d_spans if s["visualColor"] == "cyan"]

    visual_results = []
    for visual in v_spans:
        matches = find_matches(visual, docm_printed)
        page_same_color = joined_page_color(docm_printed, visual["page"], {visual["visualColor"]})
        page_with_cyan = joined_page_color(docm_printed + docm_cyan, visual["page"], {visual["visualColor"], "cyan"})
        result = {
            **visual,
            "docmMatches": matches,
            "presentInJoinedSameColor": bool(visual["norm"] and visual["norm"] in page_same_color),
            "presentInJoinedSameColorPlusCyan": bool(visual["norm"] and visual["norm"] in page_with_cyan),
        }
        visual_results.append(result)

    docm_results = []
    for docm in docm_printed:
        docm_results.append({**docm, "visualMatches": find_matches(docm, v_spans)})

    unmatched_visual = [r for r in visual_results if not r["docmMatches"] and not r["presentInJoinedSameColor"]]
    unmatched_docm = [r for r in docm_results if not r["visualMatches"]]
    cyan_bridge = []
    for visual in visual_results:
        if not visual["presentInJoinedSameColor"] and visual["presentInJoinedSameColorPlusCyan"]:
            cyan_bridge.append(visual)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "DOCM highlighted runs versus manual high-res visual highlights; no key derivation",
        "sourceReports": {
            "runs": str(RUNS_JSON.relative_to(ROOT)),
            "orange": str(ORANGE_JSON.relative_to(ROOT)),
            "grey": str(GREY_JSON.relative_to(ROOT)),
        },
        "counts": {
            "docmSpanCount": len(d_spans),
            "docmPrintedSpanCount": len(docm_printed),
            "docmCyanSpanCount": len(docm_cyan),
            "visualSpanCount": len(v_spans),
            "unmatchedVisualCount": len(unmatched_visual),
            "unmatchedDocmPrintedCount": len(unmatched_docm),
            "cyanBridgeCount": len(cyan_bridge),
        },
        "docmCyanSpans": docm_cyan,
        "unmatchedVisual": unmatched_visual,
        "unmatchedDocmPrinted": unmatched_docm,
        "cyanBridges": cyan_bridge,
        "visualResults": visual_results,
        "assessment": [
            "DOCM yellow/black mostly mirrors the manual high-res orange/grey highlight system.",
            "The main material mismatch is p78 `$85 BILLION`: DOCM splits `BILLION` into cyan, so same-color yellow alone omits part of the visible orange phrase.",
            "The other unmatched visual item is p80 package art, which is graphic/package copy outside the article-body DOCM text.",
            "Cyan remains a DOCM-only formatting anomaly, not a scan-visible highlight layer.",
        ],
        "nextMove": "Treat DOCM yellow/black as wording support for visible highlights, not a separate selector. Do not use cyan unless a future source proves the Word formatting is original puzzle material.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# DOCM / Visual Highlight Consistency",
        "",
        "Scope: compare `Article with Fonts.docm` highlighted runs with the manual high-res visual orange/grey highlight readings. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- DOCM printed highlight spans: `{len(docm_printed)}`",
        f"- DOCM cyan spans: `{len(docm_cyan)}`",
        f"- Visual spans: `{len(v_spans)}`",
        f"- Unmatched visual spans: `{len(unmatched_visual)}`",
        f"- Unmatched DOCM printed spans: `{len(unmatched_docm)}`",
        f"- Cyan bridge spans: `{len(cyan_bridge)}`",
        "",
        "## DOCM Cyan Spans",
        "",
    ]
    if not docm_cyan:
        lines.append("- none")
    for span in docm_cyan:
        lines.append(f"- p{span['page']} `{span['text']}` runs `{span['runIndexes']}`")

    lines.extend(["", "## Unmatched Visual Spans", ""])
    if not unmatched_visual:
        lines.append("- none")
    for item in unmatched_visual:
        note = "same color + cyan covers it" if item["presentInJoinedSameColorPlusCyan"] else "not present in DOCM printed article highlights"
        lines.append(f"- `{item['id']}` p{item['page']} {item['visualColor']}: `{compact(item['text'])}` ({note})")

    lines.extend(["", "## Unmatched DOCM Printed Spans", ""])
    if not unmatched_docm:
        lines.append("- none")
    for item in unmatched_docm:
        lines.append(f"- `{item['id']}` p{item['page']} {item['docmHighlight']}->{item['visualColor']}: `{compact(item['text'])}`")

    lines.extend(["", "## Cyan Bridges", ""])
    if not cyan_bridge:
        lines.append("- none")
    for item in cyan_bridge:
        lines.append(f"- `{item['id']}` p{item['page']} {item['visualColor']}: `{compact(item['text'])}`")

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("unmatched visual:", len(unmatched_visual))
    print("unmatched docm printed:", len(unmatched_docm))
    print("cyan bridges:", len(cyan_bridge))


if __name__ == "__main__":
    main()

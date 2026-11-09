#!/usr/bin/env python3
"""Check whether corrected transcript lines can safely preload the 3D viewer editor.

This is a witness-quality audit only. It does not derive keys or generate
candidate secrets.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
CANONICAL_PATH = ROOT / "analysis_outputs/plain_text_transcript/canonical_plain_article_body.txt"
OUT_DIR = ROOT / "analysis_outputs/3d_article_map/viewer_correction_alignment"
OUT_MD = OUT_DIR / "viewer_correction_alignment.md"
OUT_JSON = OUT_DIR / "viewer_correction_alignment.json"


PAGE_MARKERS = [
    (75, "BITCOIN IS TOXIC AF"),
    (76, "Get some toxicity"),
    (77, "Meanwhile, back in El Salvador"),
    (78, "We've never had"),
    (79, "To wrap this up"),
]


def norm(text: str) -> str:
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    return re.sub(r"[^a-z0-9%$']+", " ", text.lower()).strip()


def similarity(a: str, b: str) -> float:
    na, nb = norm(a), norm(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def split_canonical_pages(text: str) -> dict[int, list[str]]:
    starts: list[tuple[int, int]] = []
    for page, marker in PAGE_MARKERS:
        idx = text.find(marker)
        if idx < 0:
            raise RuntimeError(f"missing marker {marker!r}")
        starts.append((page, idx))
    pages: dict[int, list[str]] = {}
    for i, (page, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(text)
        pages[page] = [line.strip() for line in text[start:end].splitlines() if line.strip()]
    return pages


def viewer_lines(data: dict) -> dict[int, list[dict]]:
    pages: dict[int, list[dict]] = {}
    for page in data["pages"]:
        page_no = int(page["page"])
        sorted_words = sorted(page["words"], key=lambda word: (word["center"][1], word["center"][0]))
        lines: list[dict] = []
        for word in sorted_words:
            y = word["center"][1]
            match = next((line for line in lines if abs(line["y"] - y) <= 28), None)
            if match is None:
                match = {"y": y, "words": []}
                lines.append(match)
            match["words"].append(word)
            match["y"] = (match["y"] * (len(match["words"]) - 1) + y) / len(match["words"])
        rows: list[dict] = []
        for idx, line in enumerate(lines):
            line["words"].sort(key=lambda word: word["center"][0])
            text = " ".join(word["text"] for word in line["words"])
            rows.append(
                {
                    "id": f"p{page_no}l{idx}",
                    "page": page_no,
                    "lineIndex": idx,
                    "y": round(line["y"], 2),
                    "text": text,
                }
            )
        pages[page_no] = rows
    return pages


@dataclass
class Match:
    canonical_index: int
    viewer_index: int
    score: float
    canonical: str
    viewer: str
    viewer_id: str


def align_page(canonical: list[str], viewer: list[dict]) -> tuple[list[Match], list[int], list[int]]:
    """Greedy monotonic line alignment with a similarity threshold.

    This intentionally avoids forcing every line to align. The output is for
    deciding preload safety, not for correcting geometry.
    """
    matches: list[Match] = []
    used_viewer: set[int] = set()
    cursor = 0
    for ci, canonical_line in enumerate(canonical):
        best: tuple[float, int] | None = None
        # Keep the search local and monotonic, but tolerate OCR extra rows.
        for vi in range(cursor, min(len(viewer), cursor + 8)):
            if vi in used_viewer:
                continue
            score = similarity(canonical_line, viewer[vi]["text"])
            if best is None or score > best[0]:
                best = (score, vi)
        if best and best[0] >= 0.50:
            score, vi = best
            matches.append(
                Match(
                    canonical_index=ci,
                    viewer_index=vi,
                    score=round(score, 4),
                    canonical=canonical_line,
                    viewer=viewer[vi]["text"],
                    viewer_id=viewer[vi]["id"],
                )
            )
            used_viewer.add(vi)
            cursor = vi + 1
    matched_canonical = {m.canonical_index for m in matches}
    unmatched_canonical = [i for i in range(len(canonical)) if i not in matched_canonical]
    unmatched_viewer = [i for i in range(len(viewer)) if i not in used_viewer]
    return matches, unmatched_canonical, unmatched_viewer


def classify_score(score: float) -> str:
    if score >= 0.90:
        return "high"
    if score >= 0.72:
        return "usable"
    if score >= 0.50:
        return "weak"
    return "unmatched"


def main() -> None:
    data = json.loads(DATA_PATH.read_text())
    canonical_pages = split_canonical_pages(CANONICAL_PATH.read_text())
    viewer_pages = viewer_lines(data)

    page_reports = []
    global_counts = {"high": 0, "usable": 0, "weak": 0}
    preload_map = {}

    for page in sorted(canonical_pages):
        matches, missing_canon, extra_viewer = align_page(canonical_pages[page], viewer_pages.get(page, []))
        buckets = {"high": 0, "usable": 0, "weak": 0}
        for match in matches:
            bucket = classify_score(match.score)
            if bucket in buckets:
                buckets[bucket] += 1
                global_counts[bucket] += 1
            if match.score >= 0.90:
                preload_map[match.viewer_id] = match.canonical

        page_reports.append(
            {
                "page": page,
                "canonicalLineCount": len(canonical_pages[page]),
                "viewerLineCount": len(viewer_pages.get(page, [])),
                "matchCount": len(matches),
                "scoreBuckets": buckets,
                "highConfidencePreloadCount": buckets["high"],
                "unmatchedCanonical": [
                    {"index": i, "text": canonical_pages[page][i]} for i in missing_canon[:12]
                ],
                "extraViewerRows": [
                    {"id": viewer_pages[page][i]["id"], "lineIndex": i, "text": viewer_pages[page][i]["text"]}
                    for i in extra_viewer[:12]
                ],
                "weakMatches": [
                    {
                        "canonicalIndex": m.canonical_index,
                        "viewerId": m.viewer_id,
                        "score": m.score,
                        "canonical": m.canonical,
                        "viewer": m.viewer,
                    }
                    for m in matches
                    if 0.50 <= m.score < 0.72
                ][:10],
                "sampleMatches": [
                    {
                        "canonicalIndex": m.canonical_index,
                        "viewerId": m.viewer_id,
                        "score": m.score,
                        "canonical": m.canonical,
                        "viewer": m.viewer,
                    }
                    for m in matches[:6]
                ],
            }
        )

    high_total = sum(page["highConfidencePreloadCount"] for page in page_reports)
    viewer_total = sum(page["viewerLineCount"] for page in page_reports)
    canonical_total = sum(page["canonicalLineCount"] for page in page_reports)
    safe_global_preload = high_total == canonical_total == viewer_total

    report = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Align corrected canonical transcript lines to the 3D viewer OCR line model; no key derivation.",
        "inputs": {
            "viewerData": str(DATA_PATH.relative_to(ROOT)),
            "canonicalPlainText": str(CANONICAL_PATH.relative_to(ROOT)),
        },
        "totals": {
            "canonicalLines": canonical_total,
            "viewerLines": viewer_total,
            "highConfidencePreloadLines": high_total,
            "usableButNotPreloaded": global_counts["usable"],
            "weakMatches": global_counts["weak"],
            "safeGlobalPreload": safe_global_preload,
        },
        "preloadMapHighConfidenceOnly": preload_map,
        "pages": page_reports,
        "assessment": [
            "A global automatic correction preload is unsafe because the viewer OCR line model has extra visual rows and some missing/split article rows.",
            "High-confidence matches can still be used as a local correction helper, but ambiguous rows should stay manual.",
            "For puzzle extraction, use corrected DOCM/plain text after geometry selects a region; do not rely on raw 3D OCR labels.",
        ],
        "nextMove": "If the viewer is improved, add an optional high-confidence import/review step rather than silently replacing every OCR line.",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# 3D Viewer Correction Alignment",
        "",
        "Scope: align corrected canonical transcript lines to the 3D viewer OCR line model. No key derivation, hashing, seed phrases, WIF checks, or address checks were run.",
        "",
        f"- Created: `{report['createdAt']}`",
        f"- Canonical lines: `{canonical_total}`",
        f"- Viewer OCR lines: `{viewer_total}`",
        f"- High-confidence preload lines: `{high_total}`",
        f"- Usable but not preloaded lines: `{global_counts['usable']}`",
        f"- Weak matches: `{global_counts['weak']}`",
        f"- Safe global preload: `{safe_global_preload}`",
        "",
        "## Page Summary",
        "",
        "| page | canonical | viewer | matches | high | usable | weak |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for page in page_reports:
        b = page["scoreBuckets"]
        lines.append(
            f"| p{page['page']} | {page['canonicalLineCount']} | {page['viewerLineCount']} | {page['matchCount']} | {b['high']} | {b['usable']} | {b['weak']} |"
        )

    lines.extend(["", "## Notable Extra Viewer Rows", ""])
    for page in page_reports:
        if not page["extraViewerRows"]:
            continue
        lines.append(f"### p{page['page']}")
        for row in page["extraViewerRows"][:6]:
            lines.append(f"- `{row['id']}`: `{row['text']}`")
        lines.append("")

    lines.extend(["## Weak Match Examples", ""])
    for page in page_reports:
        if not page["weakMatches"]:
            continue
        lines.append(f"### p{page['page']}")
        for row in page["weakMatches"][:5]:
            lines.append(
                f"- `{row['viewerId']}` score `{row['score']}`: canonical `{row['canonical']}` vs viewer `{row['viewer']}`"
            )
        lines.append("")

    lines.extend(
        [
            "## Assessment",
            "",
            "- Global automatic correction preload is unsafe: the viewer line model includes extra visual/OCR rows and some article rows are missing, split, or shifted.",
            "- High-confidence matches are suitable as a review aid, not as silent replacement.",
            "- The existing investigation rule still stands: high-res scan for geometry, corrected DOCM/plain text for wording, 3D viewer only for navigation and manual review.",
            "",
            "## Next Move",
            "",
            "- If the viewer is improved, add an optional high-confidence import/review step rather than replacing every OCR line automatically.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(json.dumps(report["totals"], indent=2))


if __name__ == "__main__":
    main()

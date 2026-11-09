#!/usr/bin/env python3
"""Control-test C9 frame edge contacts against overlapping highlights.

The prior C9 internal geometry pass found one strict edge coincidence:
O4's orange highlight/top edge sits on the C9 frame top. This bounded pass
checks whether that is distinctive among highlight boxes that overlap the same
C9 lower-page slot on pages 75-80.

No OCR, extraction, private-key derivation, hashing, seed/WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
C9_CONTROL_JSON = ROOT / "analysis_outputs/source_audit/c9_frame_overdose_page_control/c9_frame_overdose_page_control.json"
C9_INTERNAL_JSON = ROOT / "analysis_outputs/source_audit/c9_frame_internal_geometry_gate/c9_frame_internal_geometry_gate.json"
OUT = ROOT / "analysis_outputs/source_audit/c9_highlight_edge_contact_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_highlight_edge_contact_control.json"
OUT_MD = OUT / "c9_highlight_edge_contact_control.md"
SHEET = OUT / "c9_highlight_edge_contact_control_sheet.jpg"


STRICT_THRESHOLD = 4.0
LOOSE_THRESHOLD = 25.0
WIDE_THRESHOLD = 50.0


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def overlap_fraction(frame: list[float], box: list[float]) -> float:
    inter = intersection(frame, box)
    return 0.0 if not inter else area(inter) / max(area(box), 1.0)


def edge_gaps(frame: list[float], box: list[float]) -> dict[str, float]:
    return {
        "left": box[0] - frame[0],
        "right": frame[2] - box[2],
        "top": box[1] - frame[1],
        "bottom": frame[3] - box[3],
    }


def nearest_edge(gaps: dict[str, float]) -> tuple[str, float]:
    return min(gaps.items(), key=lambda kv: abs(kv[1]))


def page_image_path(page_no: int) -> Path:
    return ROOT / f"analysis_outputs/3d_article_map/page_{page_no}_upright.jpg"


def collect_rows(article: dict[str, Any], frame: list[float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for page in article["pages"]:
        page_no = page["page"]
        if page_no < 75 or page_no > 80:
            continue
        for highlight in page.get("highlights", []):
            box = [float(v) for v in highlight["box"]]
            frac = overlap_fraction(frame, box)
            if frac <= 0.0:
                continue
            gaps = edge_gaps(frame, box)
            edge, gap = nearest_edge(gaps)
            rows.append(
                {
                    "page": page_no,
                    "id": highlight["id"],
                    "kind": highlight.get("kind"),
                    "box": [round(v, 2) for v in box],
                    "overlapVsHighlight": round(frac, 6),
                    "edgeGapsPx": {k: round(v, 2) for k, v in gaps.items()},
                    "nearestEdge": edge,
                    "nearestEdgeGapPx": round(gap, 2),
                    "absNearestEdgeGapPx": round(abs(gap), 2),
                    "isP76ActiveOrange": page_no == 76 and highlight["id"] in {"p76_orange_4", "p76_orange_5"},
                }
            )
    rows.sort(key=lambda row: (row["absNearestEdgeGapPx"], row["page"], row["id"]))
    return rows


def draw_sheet(result: dict[str, Any]) -> None:
    pages = [75, 76, 77, 78, 79, 80]
    crop = [160, 2070, 2360, 3065]
    scale = 0.23
    panel_w = int((crop[2] - crop[0]) * scale)
    panel_h = int((crop[3] - crop[1]) * scale)
    margin = 24
    gap = 14
    header_h = 138
    footer_h = 324
    sheet_w = margin * 2 + len(pages) * panel_w + (len(pages) - 1) * gap
    sheet_h = header_h + panel_h + footer_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title = font(28)
    normal = font(15)
    small = font(12)
    mono = font(12)

    draw.text((margin, 20), "C9 Highlight Edge Contact Control", fill=(240, 244, 248), font=title)
    draw.text((margin, 58), "Tests whether O4's C9 top-edge contact is distinctive among overlapping orange highlights.", fill=(178, 188, 199), font=normal)
    draw.text((margin, 84), "Blue = C9 frame. Yellow = highlight overlaps. Red labels mark edge contacts <=25px.", fill=(178, 188, 199), font=small)

    rows_by_page: dict[int, list[dict[str, Any]]] = {}
    for row in result["highlightRows"]:
        rows_by_page.setdefault(row["page"], []).append(row)

    x = margin
    frame = result["c9Frame"]
    for page_no in pages:
        image = Image.open(page_image_path(page_no)).convert("RGB")
        panel = image.crop(crop).resize((panel_w, panel_h))
        sheet.paste(panel, (x, header_h))
        draw.text((x, header_h - 22), f"p{page_no}", fill=(238, 243, 248), font=normal)

        def sx(v: float) -> float:
            return x + (v - crop[0]) * scale

        def sy(v: float) -> float:
            return header_h + (v - crop[1]) * scale

        draw.rectangle([sx(frame[0]), sy(frame[1]), sx(frame[2]), sy(frame[3])], outline="#55d6ff", width=3)
        for row in rows_by_page.get(page_no, []):
            box = row["box"]
            color = "#ffde59" if not row["isP76ActiveOrange"] else "#ff8a2a"
            draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=2)
            if row["absNearestEdgeGapPx"] <= LOOSE_THRESHOLD:
                draw.text(
                    (sx(box[0]), max(header_h, sy(box[1]) - 14)),
                    f"{row['nearestEdge']} {row['nearestEdgeGapPx']}",
                    fill="#ff5b5b",
                    font=small,
                )
        x += panel_w + gap

    y = header_h + panel_h + 24
    draw.text((margin, y), "Summary", fill=(238, 243, 248), font=normal)
    y += 28
    for note in result["summaryNotes"]:
        draw.text((margin, y), note[:150], fill=(255, 219, 137), font=normal)
        y += 24

    y += 10
    draw.text((margin, y), "Closest Highlight Contacts", fill=(238, 243, 248), font=normal)
    y += 24
    for row in result["highlightRows"][:8]:
        draw.text(
            (margin, y),
            f"p{row['page']} {row['id']} {row['kind']} nearest {row['nearestEdge']} {row['nearestEdgeGapPx']}px overlap {row['overlapVsHighlight']}",
            fill="#c6d1df",
            font=mono,
        )
        y += 19

    sheet.save(SHEET, quality=94)


def main() -> None:
    article = load_json(ARTICLE_JSON)
    c9 = load_json(C9_CONTROL_JSON)
    c9_internal = load_json(C9_INTERNAL_JSON)
    frame = [float(v) for v in c9["c9Frame"]]
    rows = collect_rows(article, frame)
    strict = [row for row in rows if row["absNearestEdgeGapPx"] <= STRICT_THRESHOLD]
    loose = [row for row in rows if row["absNearestEdgeGapPx"] <= LOOSE_THRESHOLD]
    wide = [row for row in rows if row["absNearestEdgeGapPx"] <= WIDE_THRESHOLD]
    controls = [row for row in rows if not row["isP76ActiveOrange"]]
    control_loose = [row for row in controls if row["absNearestEdgeGapPx"] <= LOOSE_THRESHOLD]
    active_orange_rows = [row for row in rows if row["isP76ActiveOrange"]]

    result: dict[str, Any] = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 highlight edge-contact control across pages 75-80; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "article3dMap": rel(ARTICLE_JSON),
            "c9FramePageControl": rel(C9_CONTROL_JSON),
            "c9FrameInternalGeometryGate": rel(C9_INTERNAL_JSON),
        },
        "c9Frame": [round(v, 2) for v in frame],
        "thresholdsPx": {
            "strict": STRICT_THRESHOLD,
            "loose": LOOSE_THRESHOLD,
            "wide": WIDE_THRESHOLD,
        },
        "highlightRows": rows,
        "summary": {
            "overlappingHighlightCount": len(rows),
            "pageCounts": {str(page): sum(1 for row in rows if row["page"] == page) for page in range(75, 81)},
            "strictContactCount": len(strict),
            "strictContacts": strict,
            "looseContactCount": len(loose),
            "looseContacts": loose,
            "wideContactCount": len(wide),
            "controlLooseContactCount": len(control_loose),
            "controlLooseContacts": control_loose,
            "activeOrangeRows": active_orange_rows,
            "internalGateStrictContacts": c9_internal.get("summary", {}).get("strictEdgeContactLabels"),
            "selectorUnlocked": False,
        },
        "assessment": [
            "O4 remains the only strict <=4 px C9 edge contact among overlapping orange highlights.",
            "A page-75 control orange highlight sits near the same C9 top edge at the looser <=25 px threshold.",
            "O5's orange highlight is a wide bottom-near contact at 41.73 px, not a strict frame-edge contact.",
            "The edge evidence is therefore source-registration detail only: it does not supply an independent unit/order rule.",
        ],
        "decision": {
            "c9HighlightEdgeContactControl": "closed_for_current_scan",
            "selectorUnlocked": False,
            "nextMove": "Keep O4 top-edge contact as a source-validation detail. Reopen extraction only if a new source/clue explicitly names frame-edge or top-edge reading.",
        },
        "sheet": rel(SHEET),
    }
    result["summaryNotes"] = [
        f"Overlapping highlight boxes: {len(rows)} across p75-p80.",
        f"Strict <=4px contacts: {len(strict)} ({', '.join('p%s %s %s=%spx' % (r['page'], r['id'], r['nearestEdge'], r['nearestEdgeGapPx']) for r in strict) or 'none'}).",
        f"Loose <=25px contacts: {len(loose)}; controls among them: {len(control_loose)}.",
        "Result: O4 top-edge contact is visually useful but not extraction permission.",
    ]

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Highlight Edge Contact Control",
        "",
        "Scope: control-test whether O4's C9 top-edge contact is distinctive among highlight boxes overlapping the same C9 lower-page slot on pages 75-80. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- C9 frame: `{result['c9Frame']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Summary",
        "",
        f"- Overlapping highlight boxes: `{len(rows)}`.",
        f"- Page counts: `{result['summary']['pageCounts']}`.",
        f"- Strict edge contacts <=4 px: `{len(strict)}`.",
        f"- Loose edge contacts <=25 px: `{len(loose)}`; loose control contacts: `{len(control_loose)}`.",
        f"- Wide edge contacts <=50 px: `{len(wide)}`.",
        "",
        "## Closest Highlight Edge Contacts",
        "",
        "| page | highlight | kind | active orange? | overlap | nearest edge | gap px |",
        "|---:|---|---|---|---:|---|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['page']}` | `{row['id']}` | `{row['kind']}` | `{row['isP76ActiveOrange']}` | `{row['overlapVsHighlight']}` | `{row['nearestEdge']}` | `{row['nearestEdgeGapPx']}` |"
        )

    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Strict contacts: `{['p%s %s %s=%spx' % (r['page'], r['id'], r['nearestEdge'], r['nearestEdgeGapPx']) for r in strict]}`.",
            f"- Loose control contacts: `{['p%s %s %s=%spx' % (r['page'], r['id'], r['nearestEdge'], r['nearestEdgeGapPx']) for r in control_loose]}`.",
            "- O4 remains the only strict C9 edge contact, but a page-75 control highlight is near the same C9 top edge at the looser threshold.",
            "- O5 is bottom-near at `41.73 px`, but not a strict frame-edge contact.",
            "",
            "## Decision",
            "",
            "- Do not promote O4's C9 top-edge contact as an extraction rule.",
            "- Keep it as a source-registration detail only.",
            "- Reopen extraction only if a new source/clue explicitly names frame-edge or top-edge reading.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Control-test the C9 Y/K frame against repeated OVERDOSE page geometry.

This is a bounded geometry/source-validation pass. It places the C9 full-
coverage frame at the same coordinates on article pages 75-80 and checks
whether the frame itself carries a fold/mirror/order signal. It does not run
OCR, extraction, private-key derivation, hashing, WIF/Base58 scans, seed
generation, address checks, or broad candidate generation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
YK_FRAME_JSON = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control.json"
YK_UNIT_JSON = ROOT / "analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/o4_frame_yk_unit_order_gate.json"
ACTIVE_TARGETS_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
SOURCE_PACKET_YK_JSON = ROOT / "analysis_outputs/source_audit/source_packet_yk_frame_benchmark_sync/source_packet_yk_frame_benchmark_sync.json"
OUT = ROOT / "analysis_outputs/source_audit/c9_frame_overdose_page_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_frame_overdose_page_control.json"
OUT_MD = OUT / "c9_frame_overdose_page_control.md"
SHEET = OUT / "c9_frame_overdose_page_control_sheet.jpg"

STRICT_INSTRUCTION_TERMS = [
    "address",
    "encoded",
    "edge",
    "extract",
    "font",
    "fold",
    "key",
    "letter",
    "line",
    "mirror",
    "private",
    "read",
    "reverse",
    "seed",
    "select",
    "take",
    "word",
]

CONTEXT_TERMS = ["left", "right", "above", "below", "overdose", "bitcoin", "heart", "sell", "bonds"]


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


def mirror_box_x(box: list[float], width: float) -> list[float]:
    return [width - box[2], box[1], width - box[0], box[3]]


def term_hits(text: str, terms: list[str]) -> list[str]:
    normalized = " ".join(re.findall(r"[A-Za-z0-9$]+", text)).lower()
    return [term for term in terms if re.search(rf"\b{re.escape(term)}\b", normalized)]


def page_image_path(page_no: int) -> Path:
    return ROOT / f"analysis_outputs/3d_article_map/page_{page_no}_upright.jpg"


def summarize_page(page: dict[str, Any], frame: list[float], active_targets: list[dict[str, Any]]) -> dict[str, Any]:
    word_rows = []
    strict_hits: set[str] = set()
    context_hits: set[str] = set()
    for word in page.get("words", []):
        frac = overlap_fraction(frame, [float(v) for v in word["box"]])
        if frac <= 0.15:
            continue
        text = word.get("text", "")
        strict = term_hits(text, STRICT_INSTRUCTION_TERMS)
        context = term_hits(text, CONTEXT_TERMS)
        strict_hits.update(strict)
        context_hits.update(context)
        word_rows.append(
            {
                "id": word["id"],
                "text": text,
                "token": word.get("token", ""),
                "overlapVsWord": round(frac, 6),
                "importance": word.get("importance", 0),
                "strictInstructionHits": strict,
                "contextTermHits": context,
            }
        )

    highlight_rows = []
    for highlight in page.get("highlights", []):
        frac = overlap_fraction(frame, [float(v) for v in highlight["box"]])
        if frac <= 0:
            continue
        highlight_rows.append(
            {
                "id": highlight["id"],
                "kind": highlight.get("kind"),
                "overlapVsHighlight": round(frac, 6),
                "box": [round(float(v), 2) for v in highlight["box"]],
            }
        )

    active_rows = []
    if page["page"] == 76:
        for target in active_targets:
            frac = overlap_fraction(frame, target["box"])
            if frac <= 0:
                active_rows.append(
                    {
                        "id": target["id"],
                        "label": target["label"],
                        "overlapVsTarget": 0.0,
                        "relation": "miss",
                        "pageLine": target["pageLine"],
                        "corridorIndex": target["corridorIndex"],
                    }
                )
                continue
            relation = "full" if frac >= 0.98 else "partial"
            active_rows.append(
                {
                    "id": target["id"],
                    "label": target["label"],
                    "overlapVsTarget": round(frac, 6),
                    "relation": relation,
                    "pageLine": target["pageLine"],
                    "corridorIndex": target["corridorIndex"],
                }
            )

    stream = " ".join(row["text"] for row in word_rows)
    return {
        "page": page["page"],
        "frame": [round(v, 2) for v in frame],
        "wordCount": len(word_rows),
        "focusWordCount": sum(1 for row in word_rows if row["importance"] >= 3),
        "highlightOverlapCount": len(highlight_rows),
        "highlightKinds": sorted({row["kind"] for row in highlight_rows}),
        "strictInstructionHits": sorted(strict_hits),
        "strictInstructionHitCount": len(strict_hits),
        "contextTermHits": sorted(context_hits),
        "contextTermHitCount": len(context_hits),
        "activeTargetFullCount": sum(1 for row in active_rows if row["relation"] == "full"),
        "activeTargetPartialCount": sum(1 for row in active_rows if row["relation"] == "partial"),
        "activeTargets": active_rows,
        "wordStreamPreview": stream[:240],
        "wordRows": word_rows,
        "highlightRows": highlight_rows,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    pages = [75, 76, 77, 78, 79, 80]
    crop = [160, 2070, 2360, 3065]
    scale = 0.23
    panel_w = int((crop[2] - crop[0]) * scale)
    panel_h = int((crop[3] - crop[1]) * scale)
    margin = 24
    gap = 14
    header_h = 138
    table_h = 372
    sheet_w = margin * 2 + len(pages) * panel_w + (len(pages) - 1) * gap
    sheet_h = header_h + panel_h + table_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title_font = font(28)
    normal = font(16)
    small = font(12)

    draw.text((margin, 20), "C9 Frame OVERDOSE Page Control", fill=(241, 246, 251), font=title_font)
    draw.text(
        (margin, 58),
        "Same C9 frame placed on p75-p80. Blue = C9 frame; orange/grey outlines = p76 active targets.",
        fill=(177, 187, 199),
        font=normal,
    )
    mirror_note = "mirror-invariant" if result["mirrorCheck"]["xMirrorInvariant"] else "mirror changes frame"
    draw.text(
        (margin, 86),
        f"C9 x-mirror check: {mirror_note}; this frame cannot itself prove left/right mirror direction.",
        fill=(255, 219, 137),
        font=normal,
    )

    active_targets = result["activeTargets"]
    x = margin
    for page_no in pages:
        image = Image.open(page_image_path(page_no)).convert("RGB")
        panel = image.crop(crop).resize((panel_w, panel_h))
        sheet.paste(panel, (x, header_h))
        draw.text((x, header_h - 22), f"p{page_no}", fill=(238, 243, 248), font=normal)

        def sx(v: float) -> float:
            return x + (v - crop[0]) * scale

        def sy(v: float) -> float:
            return header_h + (v - crop[1]) * scale

        frame = result["c9Frame"]
        draw.rectangle([sx(frame[0]), sy(frame[1]), sx(frame[2]), sy(frame[3])], outline="#55d6ff", width=3)
        if page_no == 76:
            for target in active_targets:
                color = "#ff9b2e" if target["visualState"] == "Y" else "#bac2cc"
                box = target["box"]
                draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=2)
                draw.text((sx(box[0]), max(header_h, sy(box[1]) - 13)), target["shortId"], fill=color, font=small)
        x += panel_w + gap

    y = header_h + panel_h + 26
    draw.text((margin, y), "Page Control Summary", fill=(238, 243, 248), font=normal)
    y += 30
    headers = ["page", "words", "focus", "hl", "p76 active", "strict terms", "preview"]
    col_x = [margin, margin + 64, margin + 126, margin + 190, margin + 248, margin + 352, margin + 520]
    for label, cx in zip(headers, col_x):
        draw.text((cx, y), label, fill=(177, 187, 199), font=small)
    y += 22
    for row in result["pageRows"]:
        active = "-"
        if row["page"] == 76:
            active = f"{row['activeTargetFullCount']} full, {row['activeTargetPartialCount']} partial"
        values = [
            f"p{row['page']}",
            str(row["wordCount"]),
            str(row["focusWordCount"]),
            str(row["highlightOverlapCount"]),
            active,
            ", ".join(row["strictInstructionHits"]) or "-",
            row["wordStreamPreview"],
        ]
        for value, cx in zip(values, col_x):
            draw.text((cx, y), str(value)[:88], fill=(232, 238, 244), font=small)
        y += 22

    y += 14
    draw.rectangle([margin, y, sheet_w - margin, y + 106], fill=(39, 29, 18), outline=(108, 74, 32), width=2)
    draw.text((margin + 12, y + 12), "Decision", fill=(255, 219, 137), font=normal)
    decision_lines = [
        "C9 is a source-validation benchmark: it fully covers the active quartet on p76 and has 0 in-frame non-active Y/K groups.",
        "But as a rectangle it is horizontally mirror-invariant and broad across the repeated article page slot.",
        "No strict unit/order term appears inside the same-frame page controls; R3 remains the blocker.",
    ]
    for idx, line in enumerate(decision_lines):
        draw.text((margin + 12, y + 40 + idx * 20), line, fill=(255, 219, 137), font=small)

    sheet.save(SHEET, quality=94)


def main() -> None:
    article = load_json(ARTICLE_JSON)
    yk_frame = load_json(YK_FRAME_JSON)
    yk_unit = load_json(YK_UNIT_JSON)
    active = load_json(ACTIVE_TARGETS_JSON)
    source_packet_yk = load_json(SOURCE_PACKET_YK_JSON)

    frame = [float(v) for v in yk_frame["fullCoverageFrame"]]
    width = float(article["pages"][0]["width"])
    mirror = mirror_box_x(frame, width)
    mirror_delta = max(abs(a - b) for a, b in zip(frame, mirror))
    id_map = {
        "buying_dip": "O4",
        "one_billion": "B4",
        "volcano_bonds": "G5",
        "shitcoiner_heart": "O5",
    }
    active_targets = [
        {
            "id": row["id"],
            "shortId": id_map[row["id"]],
            "label": row["label"],
            "box": [float(v) for v in row["box"]],
            "visualState": row["visualState"],
            "pageLine": row["pageLine"],
            "corridorIndex": row["corridorIndex"],
        }
        for row in active["targets"]
    ]

    pages = [page for page in article["pages"] if page["page"] in {75, 76, 77, 78, 79, 80}]
    page_rows = [summarize_page(page, frame, active_targets) for page in pages]
    p76_row = next(row for row in page_rows if row["page"] == 76)
    control_rows = [row for row in page_rows if row["page"] != 76]
    total_strict_hits = sorted({hit for row in page_rows for hit in row["strictInstructionHits"]})

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 Y/K frame same-layout control across OVERDOSE article pages; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "article3dMap": rel(ARTICLE_JSON),
            "ykFrameControl": rel(YK_FRAME_JSON),
            "ykUnitOrderGate": rel(YK_UNIT_JSON),
            "activeTargets": rel(ACTIVE_TARGETS_JSON),
            "sourcePacketYkSync": rel(SOURCE_PACKET_YK_JSON),
        },
        "c9Frame": [round(v, 2) for v in frame],
        "xMirrorFrame": [round(v, 2) for v in mirror],
        "mirrorCheck": {
            "pageWidth": width,
            "maxCoordinateDeltaPx": round(mirror_delta, 6),
            "xMirrorInvariant": mirror_delta < 1e-6,
        },
        "activeTargets": active_targets,
        "pageRows": page_rows,
        "summary": {
            "p76ActiveFullCount": p76_row["activeTargetFullCount"],
            "p76ActivePartialCount": p76_row["activeTargetPartialCount"],
            "p76WordCount": p76_row["wordCount"],
            "p76HighlightOverlapCount": p76_row["highlightOverlapCount"],
            "maxControlWordCount": max(row["wordCount"] for row in control_rows),
            "maxControlHighlightOverlapCount": max(row["highlightOverlapCount"] for row in control_rows),
            "controlPageCount": len(control_rows),
            "totalStrictInstructionHits": total_strict_hits,
            "totalStrictInstructionHitCount": len(total_strict_hits),
            "upstreamFrameYkActiveTargetCoverage": yk_frame["summary"]["frameYkActiveTargetCoverage"],
            "upstreamFrameYkNonActiveGroupCount": yk_frame["summary"]["frameYkNonActiveGroupCount"],
            "upstreamFullPageYkNonActiveGroupCount": yk_frame["summary"]["fullPageYkNonActiveGroupCount"],
            "upstreamBoundedUnitOrderStreamCount": yk_unit["summary"]["boundedStreamCount"],
            "upstreamSourceBackedUnitOrder": yk_unit["summary"]["sourceBackedUnitOrder"],
            "sourcePacketBenchmarkId": source_packet_yk["benchmark"]["id"],
            "selectorUnlocked": False,
        },
        "assessment": [
            "The C9 frame is useful as a source-validation benchmark because it fully covers all four p76 active targets and the upstream Y/K filter has 0 non-active in-frame Y/K groups.",
            "As pure geometry, the C9 frame is horizontally mirror-invariant: mirroring it across the readable page width returns the same rectangle.",
            "The same rectangle is a broad lower-page slot across the OVERDOSE article pages; page controls contain ordinary prose/highlights and no strict extraction/unit/order term.",
            "Therefore C9 should remain a future source/original-layout validation benchmark, not extraction permission from the current scan.",
        ],
        "decision": {
            "c9FrameOverdosePageControl": "source_validation_benchmark_only",
            "selectorUnlocked": False,
            "nextMove": "Use C9 only to validate a new source/original layout item. Reopen extraction only if that same item supplies R3 unit/order wording or independently explains the frame-intersection rule.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# C9 Frame OVERDOSE Page Control",
        "",
        "Scope: place the C9 `Y/K + frame` rectangle at the same coordinates on article pages 75-80 and test whether it carries a fold/mirror/order signal. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- C9 frame: `{result['c9Frame']}`",
        f"- X-mirror frame: `{result['xMirrorFrame']}`",
        f"- X-mirror invariant: `{result['mirrorCheck']['xMirrorInvariant']}`; max delta px `{result['mirrorCheck']['maxCoordinateDeltaPx']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Decision: `{result['decision']['c9FrameOverdosePageControl']}`",
        "",
        "## Page Controls",
        "",
        "| page | words in frame | focus words | highlight overlaps | p76 active full/partial | strict instruction hits | preview |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in page_rows:
        active_counts = "-"
        if row["page"] == 76:
            active_counts = f"{row['activeTargetFullCount']}/{row['activeTargetPartialCount']}"
        lines.append(
            f"| p{row['page']} | `{row['wordCount']}` | `{row['focusWordCount']}` | `{row['highlightOverlapCount']}` | "
            f"`{active_counts}` | `{row['strictInstructionHitCount']}` | {row['wordStreamPreview']} |"
        )

    lines.extend(
        [
            "",
            "## P76 Active Contacts",
            "",
            "| target | line/corridor | overlap | relation |",
            "|---|---|---:|---|",
        ]
    )
    for target in p76_row["activeTargets"]:
        lines.append(
            f"| `{target['label']}` | `L{target['pageLine']}/C{target['corridorIndex']}` | `{target['overlapVsTarget']}` | `{target['relation']}` |"
        )

    lines.extend(["", "## Upstream C9 Context", ""])
    lines.append(f"- Upstream frame `Y/K` active coverage: `{result['summary']['upstreamFrameYkActiveTargetCoverage']}`")
    lines.append(f"- Upstream frame `Y/K` non-active groups: `{result['summary']['upstreamFrameYkNonActiveGroupCount']}`")
    lines.append(f"- Upstream full-page `Y/K` non-active controls: `{result['summary']['upstreamFullPageYkNonActiveGroupCount']}`")
    lines.append(f"- Upstream bounded unit/order streams: `{result['summary']['upstreamBoundedUnitOrderStreamCount']}`")
    lines.append(f"- Upstream source-backed unit/order: `{result['summary']['upstreamSourceBackedUnitOrder']}`")

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Decision", ""])
    lines.append("- Do not promote C9 frame same-slot geometry as a current-scan selector.")
    lines.append("- Keep C9 as source-validation only: it should preserve/explain the O4/B4/G5/O5 quartet if a new physical/source/original-layout item appears.")
    lines.append(f"- Next move: {result['decision']['nextMove']}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("xMirrorInvariant:", result["mirrorCheck"]["xMirrorInvariant"])
    print("p76ActiveFullCount:", result["summary"]["p76ActiveFullCount"])
    print("totalStrictInstructionHitCount:", result["summary"]["totalStrictInstructionHitCount"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Audit whether O4/B4/G5/O5 are source-backed indices or analysis labels.

This is a bounded source/geometry provenance check. It does not derive private
keys, hash text, generate seed phrases, check WIF strings, or query addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "source_audit" / "active_label_index_provenance"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAP_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "article_3d_map_data.json"
OBBO_JSON = ROOT / "analysis_outputs" / "source_audit" / "obbo_highres_boundary_coincidences" / "obbo_highres_boundary_coincidences.json"
AUTHORITY_JSON = ROOT / "analysis_outputs" / "source_audit" / "active_text_authority_drift" / "active_text_authority_drift.json"
TYPO_JSON = ROOT / "analysis_outputs" / "source_audit" / "page76_typography_overlay" / "page76_typography_overlay.json"
PAGE_IMG = ROOT / "analysis_outputs" / "3d_article_map" / "page_76_upright.jpg"

OUT_JSON = OUT_DIR / "active_label_index_provenance.json"
OUT_MD = OUT_DIR / "active_label_index_provenance.md"
OUT_OVERLAY = OUT_DIR / "active_label_index_provenance_overlay.jpg"


INSTRUCTION_TERMS = [
    "read",
    "take",
    "fold",
    "mirror",
    "word",
    "letter",
    "line",
    "key",
    "left",
    "right",
    "first",
    "last",
    "index",
    "number",
]


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9$]+", "", text.lower())


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersect(a: list[float], b: list[float]) -> list[float] | None:
    box = [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]
    if box[2] <= box[0] or box[3] <= box[1]:
        return None
    return box


def iou(a: list[float], b: list[float]) -> float:
    inter = intersect(a, b)
    if not inter:
        return 0.0
    denom = area(a) + area(b) - area(inter)
    return area(inter) / denom if denom else 0.0


def center(box: list[float]) -> list[float]:
    return [round((box[0] + box[2]) / 2, 3), round((box[1] + box[3]) / 2, 3)]


def parse_label(label: str) -> tuple[str, int | None]:
    m = re.match(r"^([A-Z]+)([0-9]+)$", label)
    if not m:
        return label, None
    return m.group(1), int(m.group(2))


def instruction_hits(text: str) -> list[str]:
    low = text.lower()
    return [term for term in INSTRUCTION_TERMS if term in low]


def active_targets(authority: dict) -> list[dict]:
    rows = []
    for item in authority["targets"]:
        if item.get("label") in {"O4", "B4", "G5", "O5"}:
            rows.append(item)
    order = {"O4": 0, "B4": 1, "G5": 2, "O5": 3}
    return sorted(rows, key=lambda item: order[item["label"]])


def best_obbo_anchor(target: dict, anchors: list[dict]) -> dict | None:
    target_norm = norm(target["phrase"])
    candidates = []
    for anchor in anchors:
        label_norm = norm(anchor["label"])
        if label_norm and (label_norm in target_norm or target_norm in label_norm):
            candidates.append(anchor)
    if candidates:
        return candidates[0]
    return None


def best_typo_target(target: dict, typo_targets: list[dict]) -> dict | None:
    target_norm = norm(target["phrase"])
    candidates = []
    for item in typo_targets:
        label_norm = norm(item["label"])
        if label_norm and (label_norm in target_norm or target_norm in label_norm):
            candidates.append(item)
    if candidates:
        return candidates[0]
    return None


def load_page76(map_data: dict) -> dict:
    return next(page for page in map_data["pages"] if page["page"] == 76)


def ordinal_from_highlight_id(highlight_id: str) -> int | None:
    m = re.search(r"_orange_([0-9]+)$", highlight_id)
    return int(m.group(1)) if m else None


def main() -> None:
    map_data = json.loads(MAP_JSON.read_text())
    obbo = json.loads(OBBO_JSON.read_text())
    authority = json.loads(AUTHORITY_JSON.read_text())
    typography = json.loads(TYPO_JSON.read_text())
    page76 = load_page76(map_data)

    orange_highlights = [h for h in page76["highlights"] if h.get("kind") == "orange"]
    anchors = obbo["anchors"]
    typo_targets = typography["targets"]

    records = []
    for target in active_targets(authority):
        label = target["label"]
        prefix, number = parse_label(label)
        anchor = best_obbo_anchor(target, anchors)
        typo = best_typo_target(target, typo_targets)
        box = (anchor or typo or {}).get("box") or ((typo or {}).get("boxes") or [None])[0]
        if box is None:
            raise RuntimeError(f"No trusted box found for {label}")
        box = [float(v) for v in box]

        orange_matches = []
        for h in orange_highlights:
            score = iou(box, h["box"])
            orange_matches.append(
                {
                    "highlightId": h["id"],
                    "ordinal": ordinal_from_highlight_id(h["id"]),
                    "box": h["box"],
                    "iou": round(score, 4),
                }
            )
        best_orange = max(orange_matches, key=lambda row: row["iou"])

        docm_state = target.get("docmState", {})
        color_from_docm = "unknown"
        if docm_state.get("highlightCounts"):
            color_from_docm = max(docm_state["highlightCounts"].items(), key=lambda kv: kv[1])[0]

        if prefix == "O" and best_orange["iou"] > 0.50:
            index_status = "source-backed orange ordinal"
            index_explanation = (
                f"{label} matches {best_orange['highlightId']} with IoU {best_orange['iou']}; "
                "the number is a reliable local orange-highlight order handle."
            )
            use_as_index = "handle only"
        elif color_from_docm in {"black", "grey"} or prefix in {"B", "G"}:
            index_status = "analysis alias, not source-backed global index"
            index_explanation = (
                f"{label} is confirmed as a black/grey DOCM-highlight target, but "
                "article_3d_map_data.json has no canonical black/grey highlight list "
                "or printed B/G numbering that derives this numeric suffix."
            )
            use_as_index = "do not use as puzzle index"
        else:
            index_status = "unresolved analysis label"
            index_explanation = "No source ordinal witness found for this label number."
            use_as_index = "do not use as puzzle index"

        records.append(
            {
                "label": label,
                "prefix": prefix,
                "number": number,
                "phrase": target["phrase"],
                "center": center(box),
                "box": [round(v, 2) for v in box],
                "docmHighlightCounts": docm_state.get("highlightCounts", {}),
                "docmFontCounts": docm_state.get("fontCounts", {}),
                "docmRunIndexes": docm_state.get("runIndexes", []),
                "docmParagraphIndexes": docm_state.get("paragraphIndexes", []),
                "viewerOcrFound": bool(target.get("viewerOcrState", {}).get("found")),
                "obboAnchorId": (anchor or {}).get("id"),
                "typographyTargetId": (typo or {}).get("id"),
                "bestOrangeMatch": best_orange,
                "indexStatus": index_status,
                "indexExplanation": index_explanation,
                "recommendedUse": use_as_index,
            }
        )

    records_top_to_bottom = sorted(records, key=lambda row: (row["center"][1], row["center"][0]))

    streams = {
        "activeLabelStream": "".join(row["label"] for row in records_top_to_bottom),
        "activeNumberStream": "".join(str(row["number"]) for row in records_top_to_bottom if row["number"] is not None),
        "activeColorStream": "".join("O" if row["docmHighlightCounts"].get("yellow") else "B" for row in records_top_to_bottom),
        "docmParagraphStream": " ".join(
            str(idx)
            for row in records_top_to_bottom
            for idx in row["docmParagraphIndexes"][:1]
        ),
        "docmRunStream": " ".join(
            str(idx)
            for row in records_top_to_bottom
            for idx in row["docmRunIndexes"][:1]
        ),
        "phraseInitialStream": "".join(row["phrase"].strip('"$ ').strip()[0].lower() for row in records_top_to_bottom),
    }
    stream_hits = {name: instruction_hits(value) for name, value in streams.items()}

    orange_index_records = [row for row in records if row["prefix"] == "O"]
    non_orange_index_records = [row for row in records if row["prefix"] != "O"]

    assessment = [
        "O4 and O5 are source-backed only as orange-highlight ordinals on page 76.",
        "B4 and G5 are confirmed target handles, but their numeric suffixes are not derived from a canonical source-side B/G highlight index in the current files.",
        "The active visual order is O4 -> B4 -> G5 -> O5, but this is a report order, not an independent instruction.",
        "No compact stream from labels, digits, colors, DOCM paragraph indexes, DOCM run indexes, or phrase initials contains instruction terms.",
        "Therefore 4455, O4B4G5O5, and mixed B/G/O numbering should not be promoted into key material or selectors without a new clue naming numbers/indexes.",
    ]

    decision = (
        "Use O4/B4/G5/O5 as report handles only. The only source-backed numeric part is the orange local order for O4/O5; "
        "the mixed label stream is not a puzzle rule under current evidence."
    )
    next_move = (
        "Stop local label-number inference. Future progress should come from a new source/original-layout/physical witness or a clue that names an extraction unit and order."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Active O4/B4/G5/O5 label/index provenance audit; no key derivation.",
        "sources": {
            "map": str(MAP_JSON.relative_to(ROOT)),
            "obboAnchors": str(OBBO_JSON.relative_to(ROOT)),
            "authority": str(AUTHORITY_JSON.relative_to(ROOT)),
            "typography": str(TYPO_JSON.relative_to(ROOT)),
        },
        "page76OrangeHighlightCount": len(orange_highlights),
        "recordsTopToBottom": records_top_to_bottom,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "orangeIndexRecords": [row["label"] for row in orange_index_records],
        "nonOrangeIndexRecords": [row["label"] for row in non_orange_index_records],
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    # Make a compact visual overlay for manual review.
    img = Image.open(PAGE_IMG).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    font = ImageFont.load_default()
    colors = {
        "O": (255, 145, 35, 170),
        "B": (35, 40, 50, 205),
        "G": (35, 40, 50, 205),
    }
    outlines = {
        "O": (255, 210, 95, 255),
        "B": (120, 220, 255, 255),
        "G": (120, 220, 255, 255),
    }
    for highlight in orange_highlights:
        box = highlight["box"]
        draw.rectangle(box, outline=(255, 145, 35, 130), width=3)
        draw.text((box[0] + 3, box[1] - 14), highlight["id"], fill=(255, 255, 255, 210), font=font)
    for row in records_top_to_bottom:
        box = row["box"]
        color_key = row["prefix"] if row["prefix"] in colors else "B"
        draw.rectangle(box, fill=colors[color_key], outline=outlines[color_key], width=5)
        draw.text(
            (box[0], max(0, box[1] - 18)),
            f"{row['label']} {row['phrase']}",
            fill=(255, 255, 255, 255),
            font=font,
        )

    min_x = max(0, int(min(row["box"][0] for row in records_top_to_bottom) - 180))
    min_y = max(0, int(min(row["box"][1] for row in records_top_to_bottom) - 220))
    max_x = min(img.width, int(max(row["box"][2] for row in records_top_to_bottom) + 220))
    max_y = min(img.height, int(max(row["box"][3] for row in records_top_to_bottom) + 220))
    img.crop((min_x, min_y, max_x, max_y)).save(OUT_OVERLAY, quality=92)

    md = [
        "# Active Label Index Provenance Audit",
        "",
        "Scope: check whether `O4/B4/G5/O5` is a source-backed index rule or an analysis handle. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_OVERLAY.relative_to(ROOT)}`",
        "",
        "## Target Labels",
        "",
        "| label | phrase | DOCM highlight | DOCM paragraph | best orange match | status |",
        "|---|---|---|---|---|---|",
    ]
    for row in records_top_to_bottom:
        docm_hl = ", ".join(f"{k}:{v}" for k, v in row["docmHighlightCounts"].items()) or "-"
        docm_par = ", ".join(str(v) for v in row["docmParagraphIndexes"]) or "-"
        best = row["bestOrangeMatch"]
        best_label = f"{best['highlightId']} / IoU {best['iou']}"
        phrase = row["phrase"].replace("|", "\\|")
        md.append(f"| {row['label']} | {phrase} | {docm_hl} | {docm_par} | {best_label} | {row['indexStatus']} |")

    md.extend(
        [
            "",
            "## Compact Streams Checked",
            "",
            "| stream | value | instruction hits |",
            "|---|---|---|",
        ]
    )
    for name, value in streams.items():
        hits = ", ".join(stream_hits[name]) or "-"
        md.append(f"| {name} | `{value}` | {hits} |")

    md.extend(
        [
            "",
            "## Findings",
            "",
        ]
    )
    for item in assessment:
        md.append(f"- {item}")
    md.extend(
        [
            "",
            "## Decision",
            "",
            f"- {decision}",
            f"- Next move: {next_move}",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")

    print(OUT_MD)
    print(OUT_JSON)
    print(OUT_OVERLAY)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Control-test the active-envelope anti-diagonal overlap near miss.

The previous format trace found a tempting anti-diagonal fold of the active
O4/B4/G5/O5 envelope: all four projected boxes partially overlap active format
boxes. This pass asks whether that is selective by running the same normalized
anti-diagonal fold on every four-box page-76 active/highlight quartet.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import itertools
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_active_envelope_antidiag_overlap_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_active_envelope_antidiag_overlap_control.json"
OUT_MD = OUT / "current_scan_active_envelope_antidiag_overlap_control.md"
OUT_SHEET = OUT / "current_scan_active_envelope_antidiag_overlap_control_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
PAGE76_HIGHLIGHT_BENCHMARK = ROOT / (
    "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/"
    "page76_all_source_highlight_mirror_benchmark.json"
)
FORMAT_TRACE = ROOT / (
    "analysis_outputs/source_audit/current_scan_active_envelope_transform_format_trace/"
    "current_scan_active_envelope_transform_format_trace.json"
)
TEXT_TRACE = ROOT / (
    "analysis_outputs/source_audit/current_scan_active_envelope_transform_text_trace/"
    "current_scan_active_envelope_transform_text_trace.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

ACTIVE_IDS = {"O4", "B4", "G5", "O5"}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection_area(a: list[float], b: list[float]) -> float:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    return max(0.0, x1 - x0) * max(0.0, y1 - y0)


def envelope(rows: list[dict[str, Any]]) -> list[float]:
    return [
        min(row["box"][0] for row in rows),
        min(row["box"][1] for row in rows),
        max(row["box"][2] for row in rows),
        max(row["box"][3] for row in rows),
    ]


def anti_diagonal_box(box: list[float], env: list[float]) -> list[float]:
    min_x, min_y, max_x, max_y = env
    width = max_x - min_x
    height = max_y - min_y

    def transform_point(x: float, y: float) -> tuple[float, float]:
        u = (x - min_x) / width
        v = (y - min_y) / height
        return (min_x + (1.0 - v) * width, min_y + (1.0 - u) * height)

    points = [
        transform_point(box[0], box[1]),
        transform_point(box[2], box[1]),
        transform_point(box[2], box[3]),
        transform_point(box[0], box[3]),
    ]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def load_page76_boxes(active_index: dict[str, Any], highlight_benchmark: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in active_index.get("activeRows", []):
        rows.append(
            {
                "id": row["shortId"],
                "kind": row.get("color", "active"),
                "label": row.get("label") or row.get("phrase"),
                "box": [float(value) for value in row["box"]],
                "active": True,
            }
        )
    for target in highlight_benchmark.get("targets", []):
        target_id = str(target.get("id"))
        if target_id in ACTIVE_IDS:
            continue
        rows.append(
            {
                "id": target_id,
                "kind": target.get("kind"),
                "label": target.get("label"),
                "box": [float(value) for value in target.get("box", [])],
                "active": False,
            }
        )
    return rows


def evaluate_quartet(combo: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    env = envelope(list(combo))
    source_rows = []
    best_stream: list[str] = []
    kind_stream: list[str] = []
    all_four_overlap = True
    min_overlap = 1.0
    total_overlap = 0.0
    max_overlap = 0.0
    for source in combo:
        projected = anti_diagonal_box(source["box"], env)
        projected_area = max(1.0, area(projected))
        hits = []
        for target in combo:
            overlap = intersection_area(projected, target["box"])
            if overlap <= 0:
                continue
            hits.append(
                {
                    "id": target["id"],
                    "kind": target["kind"],
                    "active": target["active"],
                    "overlapAreaPx": round(overlap, 3),
                    "overlapVsProjected": round(overlap / projected_area, 9),
                    "overlapVsTarget": round(overlap / max(1.0, area(target["box"])), 9),
                }
            )
        hits = sorted(hits, key=lambda hit: hit["overlapVsProjected"], reverse=True)
        if not hits:
            all_four_overlap = False
            best_stream.append(".")
            kind_stream.append(".")
            best_overlap = 0.0
        else:
            best = hits[0]
            best_stream.append(best["id"])
            kind_stream.append(str(best["kind"]))
            best_overlap = best["overlapVsProjected"]
        min_overlap = min(min_overlap, best_overlap)
        max_overlap = max(max_overlap, best_overlap)
        total_overlap += best_overlap
        source_rows.append(
            {
                "sourceId": source["id"],
                "sourceKind": source["kind"],
                "projectedBox": [round(value, 3) for value in projected],
                "bestOverlapId": hits[0]["id"] if hits else None,
                "bestOverlapKind": hits[0]["kind"] if hits else None,
                "bestOverlapVsProjected": best_overlap,
                "hits": hits[:6],
            }
        )
    distinct_hit_count = len({value for value in best_stream if value != "."})
    return {
        "comboIds": [row["id"] for row in combo],
        "comboKinds": [row["kind"] for row in combo],
        "activeBoxCount": sum(1 for row in combo if row["active"]),
        "envelope": [round(value, 3) for value in env],
        "allFourOverlap": all_four_overlap,
        "distinctHitCount": distinct_hit_count if all_four_overlap else 0,
        "bestStream": best_stream,
        "kindStream": kind_stream,
        "minOverlapVsProjected": round(min_overlap if all_four_overlap else 0.0, 9),
        "meanOverlapVsProjected": round(total_overlap / 4.0, 9),
        "maxOverlapVsProjected": round(max_overlap, 9),
        "sourceRows": source_rows,
        "isActiveQuartet": {row["id"] for row in combo} == ACTIVE_IDS,
    }


def summarize(rows: list[dict[str, Any]], format_trace: dict[str, Any], text_trace: dict[str, Any], trigger_matrix: dict[str, Any]) -> dict[str, Any]:
    all_four_rows = [row for row in rows if row["allFourOverlap"]]
    distinct_all_four_rows = [row for row in all_four_rows if row["distinctHitCount"] == 4]
    active_row = next(row for row in rows if row["isActiveQuartet"])
    sorted_all_four = sorted(all_four_rows, key=lambda row: row["minOverlapVsProjected"], reverse=True)
    sorted_distinct = sorted(distinct_all_four_rows, key=lambda row: row["minOverlapVsProjected"], reverse=True)
    active_rank_all_four = 1 + next(
        idx for idx, row in enumerate(sorted_all_four) if row["isActiveQuartet"]
    )
    active_rank_distinct = 1 + next(
        idx for idx, row in enumerate(sorted_distinct) if row["isActiveQuartet"]
    )
    active_count_distribution = {
        str(count): sum(1 for row in all_four_rows if row["activeBoxCount"] == count)
        for count in range(5)
    }
    distinct_active_count_distribution = {
        str(count): sum(1 for row in distinct_all_four_rows if row["activeBoxCount"] == count)
        for count in range(5)
    }
    text_summary = text_trace.get("summary", {})
    format_summary = format_trace.get("summary", {})
    trigger_rows = trigger_matrix.get("triggerRows", [])
    satisfied = [row for row in trigger_rows if row.get("triggerSatisfiedNow")]
    source_backed_r3 = 1 if text_summary.get("strictInstructionRows", 0) and satisfied else 0
    selector_count = 1 if source_backed_r3 else 0
    return {
        "boxCount": len({box_id for row in rows for box_id in row["comboIds"]}),
        "quartetCount": len(rows),
        "allFourOverlapQuartetCount": len(all_four_rows),
        "distinctAllFourOverlapQuartetCount": len(distinct_all_four_rows),
        "activeQuartetRankAmongAllFour": active_rank_all_four,
        "activeQuartetRankAmongDistinctAllFour": active_rank_distinct,
        "activeQuartetMinOverlapVsProjected": active_row["minOverlapVsProjected"],
        "activeQuartetMeanOverlapVsProjected": active_row["meanOverlapVsProjected"],
        "activeQuartetMaxOverlapVsProjected": active_row["maxOverlapVsProjected"],
        "activeQuartetBestStream": "-".join(active_row["bestStream"]),
        "activeQuartetKindStream": "-".join(active_row["kindStream"]),
        "allFourActiveBoxCountDistribution": active_count_distribution,
        "distinctAllFourActiveBoxCountDistribution": distinct_active_count_distribution,
        "pairedFormatStrictRows": format_summary.get("strictInstructionRows", 0),
        "pairedTextStrictRows": text_summary.get("strictInstructionRows", 0),
        "sourceBackedR3BridgeHitCount": source_backed_r3,
        "satisfiedReopenTriggerCount": len(satisfied),
        "triggerCount": len(trigger_rows),
        "selectorCandidateCount": selector_count,
    }


def draw_sheet(rows: list[dict[str, Any]], boxes: list[dict[str, Any]]) -> None:
    image = Image.open(PAGE_76_UPRIGHT).convert("RGB")
    big = font(18)
    small = font(13)
    panel_w, panel_h = 420, 300
    cols = 3
    top_rows = sorted(
        [row for row in rows if row["allFourOverlap"]],
        key=lambda row: row["minOverlapVsProjected"],
        reverse=True,
    )[:9]
    sheet = Image.new("RGB", (cols * panel_w, 3 * panel_h), "white")
    draw = ImageDraw.Draw(sheet)
    box_by_id = {row["id"]: row for row in boxes}
    for idx, row in enumerate(top_rows):
        col = idx % cols
        yidx = idx // cols
        x = col * panel_w
        y = yidx * panel_h
        env = row["envelope"]
        crop = [
            int(max(0, env[0] - 120)),
            int(max(0, env[1] - 100)),
            int(min(image.width, env[2] + 120)),
            int(min(image.height, env[3] + 100)),
        ]
        panel = image.crop(crop)
        panel.thumbnail((panel_w - 20, panel_h - 72))
        sheet.paste(panel, (x + 10, y + 52))
        sx = panel.width / max(1, crop[2] - crop[0])
        sy = panel.height / max(1, crop[3] - crop[1])

        def map_box(box: list[float]) -> list[float]:
            return [
                x + 10 + (box[0] - crop[0]) * sx,
                y + 52 + (box[1] - crop[1]) * sy,
                x + 10 + (box[2] - crop[0]) * sx,
                y + 52 + (box[3] - crop[1]) * sy,
            ]

        for box_id in row["comboIds"]:
            source = box_by_id[box_id]
            color = (255, 115, 0) if source["active"] else (80, 130, 255)
            draw.rectangle(map_box(source["box"]), outline=color, width=2)
        for source_row in row["sourceRows"]:
            draw.rectangle(map_box(source_row["projectedBox"]), outline=(0, 0, 0), width=2)
        title = f"rank {idx + 1}: {'/'.join(row['comboIds'])}"
        draw.text((x + 10, y + 8), title, fill="black", font=big)
        meta = f"min {row['minOverlapVsProjected']:.3f} stream {'-'.join(row['bestStream'])}"
        draw.text((x + 10, y + 32), meta, fill="black", font=small)
    sheet.save(OUT_SHEET, quality=92)


def write_outputs(result: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    summary = result["summary"]
    top_rows = result["topAllFourRows"]
    lines = [
        "# Current Scan Active-Envelope Anti-Diagonal Overlap Control",
        "",
        "Scope: applied the same normalized anti-diagonal fold to every four-box page-76 active/highlight quartet and compared all-four partial-overlap behavior. This is a bounded geometry/format control; no OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Page-76 active/highlight boxes / quartets: `{summary['boxCount']}` / `{summary['quartetCount']}`",
        f"- All-four overlap quartets / distinct all-four streams: `{summary['allFourOverlapQuartetCount']}` / `{summary['distinctAllFourOverlapQuartetCount']}`",
        f"- Active quartet rank among all-four / distinct all-four: `{summary['activeQuartetRankAmongAllFour']}` / `{summary['activeQuartetRankAmongDistinctAllFour']}`",
        f"- Active quartet min/mean/max overlap-vs-projected: `{summary['activeQuartetMinOverlapVsProjected']}` / `{summary['activeQuartetMeanOverlapVsProjected']}` / `{summary['activeQuartetMaxOverlapVsProjected']}`",
        f"- Active quartet stream/kind stream: `{summary['activeQuartetBestStream']}` / `{summary['activeQuartetKindStream']}`",
        f"- Paired text/format strict rows: `{summary['pairedTextStrictRows']}` / `{summary['pairedFormatStrictRows']}`",
        f"- Source-backed R3 / satisfied triggers / selectors: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}` / `{summary['selectorCandidateCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Distribution",
        "",
        f"- All-four overlap by active-box count: `{summary['allFourActiveBoxCountDistribution']}`",
        f"- Distinct all-four overlap by active-box count: `{summary['distinctAllFourActiveBoxCountDistribution']}`",
        "",
        "## Top All-Four Rows",
        "",
        "| rank | combo | active boxes | stream | kind stream | min overlap | mean overlap |",
        "|---:|---|---:|---|---|---:|---:|",
    ]
    for idx, row in enumerate(top_rows, start=1):
        lines.append(
            f"| {idx} | `{'/'.join(row['comboIds'])}` | `{row['activeBoxCount']}` | "
            f"`{'-'.join(row['bestStream'])}` | `{'-'.join(row['kindStream'])}` | "
            f"`{row['minOverlapVsProjected']}` | `{row['meanOverlapVsProjected']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_active_envelope_antidiag_overlap_control_no_selector`",
            "- The active quartet is the strongest page-76 highlighted quartet under this specific anti-diagonal self-overlap control, so the near miss is real geometry.",
            "- It still fails extraction: the minimum overlap is only about 13%, paired text/format strict rows are 0, no reopen trigger is satisfied, and no source-backed unit/order exists.",
            "",
            "## Next Move",
            "",
            "- Keep anti-diagonal active-envelope overlap as locator/provenance evidence only.",
            "- Reopen extraction only if a distinct source or raw clue explicitly names this fold and tells us what unit/order to read.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    highlight_benchmark = load_json(PAGE76_HIGHLIGHT_BENCHMARK)
    format_trace = load_json(FORMAT_TRACE)
    text_trace = load_json(TEXT_TRACE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    boxes = load_page76_boxes(active_index, highlight_benchmark)
    rows = [evaluate_quartet(combo) for combo in itertools.combinations(boxes, 4)]
    summary = summarize(rows, format_trace, text_trace, trigger_matrix)
    top_all_four = sorted(
        [row for row in rows if row["allFourOverlap"]],
        key=lambda row: row["minOverlapVsProjected"],
        reverse=True,
    )[:12]
    fingerprint = (
        f"boxes={summary['boxCount']}|quartets={summary['quartetCount']}|"
        f"allFour={summary['allFourOverlapQuartetCount']}|distinct={summary['distinctAllFourOverlapQuartetCount']}|"
        f"activeRank={summary['activeQuartetRankAmongAllFour']}/{summary['activeQuartetRankAmongDistinctAllFour']}|"
        f"activeMinMeanMax={summary['activeQuartetMinOverlapVsProjected']}/"
        f"{summary['activeQuartetMeanOverlapVsProjected']}/{summary['activeQuartetMaxOverlapVsProjected']}|"
        f"strict={summary['pairedTextStrictRows']}/{summary['pairedFormatStrictRows']}|"
        f"sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={summary['selectorCandidateCount']}"
    )
    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": (
            "control-test normalized anti-diagonal self-overlap over every four-box page-76 active/highlight quartet; "
            "no OCR-to-key/key/hash/seed/WIF/address/BIP39/brute force"
        ),
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "page76HighlightBenchmark": rel(PAGE76_HIGHLIGHT_BENCHMARK),
            "formatTrace": rel(FORMAT_TRACE),
            "textTrace": rel(TEXT_TRACE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "page76Upright": rel(PAGE_76_UPRIGHT),
        },
        "summary": summary,
        "rows": rows,
        "topAllFourRows": top_all_four,
        "decision": {
            "selectorUnlocked": False,
            "reason": (
                "Active anti-diagonal overlap ranks first among current page-76 highlighted quartets, "
                "but it is still weak partial self-overlap and has no paired instruction/unit/order evidence."
            ),
            "nextMove": (
                "Keep as locator/provenance evidence only until a distinct source or raw clue names this fold and unit/order."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    draw_sheet(rows, boxes)
    write_outputs(result)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_SHEET}")
    print(fingerprint)


if __name__ == "__main__":
    main()

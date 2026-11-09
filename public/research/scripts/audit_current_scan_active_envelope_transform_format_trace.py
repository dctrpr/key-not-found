#!/usr/bin/env python3
"""Trace format/highlight overlap under active-envelope fold/mirror projections.

The active-envelope transform gate checked center-distance re-hits. This pass
uses the same projected boxes but measures full box overlap against page-76
active targets and non-active highlighted controls. It closes the case where a
projection partially overlaps a target box even though its center does not re-hit
the target.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_active_envelope_transform_format_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_active_envelope_transform_format_trace.json"
OUT_MD = OUT / "current_scan_active_envelope_transform_format_trace.md"
OUT_SHEET = OUT / "current_scan_active_envelope_transform_format_trace_sheet.jpg"

ACTIVE_ENVELOPE_GATE = ROOT / (
    "analysis_outputs/source_audit/current_scan_active_envelope_transform_gate/"
    "current_scan_active_envelope_transform_gate.json"
)
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
PAGE76_HIGHLIGHT_BENCHMARK = ROOT / (
    "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/"
    "page76_all_source_highlight_mirror_benchmark.json"
)
TEXT_TRACE = ROOT / (
    "analysis_outputs/source_audit/current_scan_active_envelope_transform_text_trace/"
    "current_scan_active_envelope_transform_text_trace.json"
)
PAGE_76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
ACTIVE_IDS = set(TARGET_ORDER)


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


def intersection_box(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x0 >= x1 or y0 >= y1:
        return None
    return [x0, y0, x1, y1]


def overlap_hit(projected: list[float], target: dict[str, Any]) -> dict[str, Any] | None:
    box = [float(value) for value in target["box"]]
    inter = intersection_box(projected, box)
    if inter is None:
        return None
    inter_area = area(inter)
    projected_area = max(1.0, area(projected))
    target_area = max(1.0, area(box))
    return {
        "id": target["id"],
        "kind": target["kind"],
        "label": target["label"],
        "active": target["active"],
        "box": box,
        "intersection": inter,
        "overlapAreaPx": round(inter_area, 3),
        "overlapVsProjected": round(inter_area / projected_area, 6),
        "overlapVsTarget": round(inter_area / target_area, 6),
    }


def target_rows(active_index: dict[str, Any], highlight_benchmark: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in active_index.get("activeRows", []):
        rows.append(
            {
                "id": row["shortId"],
                "kind": row.get("color", "active"),
                "label": row.get("label") or row.get("phrase"),
                "box": [float(value) for value in row["box"]],
                "active": True,
                "visualState": row.get("visualState"),
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
                "visualState": "control",
            }
        )
    return rows


def text_lookup(text_trace: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in text_trace.get("rows", []):
        out[(row.get("transform"), row.get("sourceShortId"))] = row
    return out


def trace_rows(active_gate: dict[str, Any], targets: list[dict[str, Any]], text_rows: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in active_gate.get("transformScenarios", []):
        transform = scenario.get("summary", {}).get("name", "unknown")
        slot_stream = scenario.get("summary", {}).get("projectedSlotStream", "")
        for projected in scenario.get("rows", []):
            source_short = projected.get("sourceShortId")
            projected_box = [float(value) for value in projected.get("projectedBox", [])]
            hits = [hit for target in targets for hit in [overlap_hit(projected_box, target)] if hit]
            active_hits = [hit for hit in hits if hit["active"]]
            control_hits = [hit for hit in hits if not hit["active"]]
            best_hit = max(hits, key=lambda hit: hit["overlapVsProjected"], default=None)
            text_row = text_rows.get((transform, source_short), {})
            rows.append(
                {
                    "transform": transform,
                    "slotStream": slot_stream,
                    "sourceShortId": source_short,
                    "sourcePhrase": projected.get("sourcePhrase"),
                    "projectedSlotLetter": projected.get("c9SlotAtProjectedCenter", {}).get("letter"),
                    "projectedSlotIndex": projected.get("c9SlotAtProjectedCenter", {}).get("index"),
                    "projectedBox": projected_box,
                    "projectedCenter": projected.get("projectedCenter"),
                    "activeOverlapCount": len(active_hits),
                    "controlOverlapCount": len(control_hits),
                    "bestOverlapId": best_hit["id"] if best_hit else None,
                    "bestOverlapKind": best_hit["kind"] if best_hit else None,
                    "bestOverlapActive": bool(best_hit and best_hit["active"]),
                    "bestOverlapVsProjected": best_hit["overlapVsProjected"] if best_hit else 0.0,
                    "bestOverlapVsTarget": best_hit["overlapVsTarget"] if best_hit else 0.0,
                    "overlapHits": sorted(hits, key=lambda hit: hit["overlapVsProjected"], reverse=True),
                    "textPreview": text_row.get("textPreview", ""),
                    "strictInstructionHitCount": int(text_row.get("strictInstructionHitCount", 0)),
                    "contextTermHitCount": int(text_row.get("contextTermHitCount", 0)),
                    "targetTermHitCount": int(text_row.get("targetTermHitCount", 0)),
                }
            )
    return rows


def summarize(active_gate: dict[str, Any], rows: list[dict[str, Any]], trigger_matrix: dict[str, Any]) -> dict[str, Any]:
    transform_names = [scenario.get("summary", {}).get("name", "unknown") for scenario in active_gate.get("transformScenarios", [])]
    by_transform = {
        name: [row for row in rows if row["transform"] == name] for name in transform_names
    }
    all_four_active_overlap_modes = [
        name for name, mode_rows in by_transform.items() if all(row["activeOverlapCount"] > 0 for row in mode_rows)
    ]
    all_four_control_overlap_modes = [
        name for name, mode_rows in by_transform.items() if all(row["controlOverlapCount"] > 0 for row in mode_rows)
    ]
    active_format_streams = {
        name: "-".join(
            row["bestOverlapId"] or "." for row in sorted(mode_rows, key=lambda item: TARGET_ORDER.index(item["sourceShortId"]))
        )
        for name, mode_rows in by_transform.items()
    }
    active_kind_streams = {
        name: "-".join(
            str(row["bestOverlapKind"] or ".") for row in sorted(mode_rows, key=lambda item: TARGET_ORDER.index(item["sourceShortId"]))
        )
        for name, mode_rows in by_transform.items()
    }
    diag_anti_rows = by_transform.get("diag_anti", [])
    diag_anti_min_overlap = min((row["bestOverlapVsProjected"] for row in diag_anti_rows), default=0.0)
    diag_anti_max_overlap = max((row["bestOverlapVsProjected"] for row in diag_anti_rows), default=0.0)
    strict_rows = [row for row in rows if row["strictInstructionHitCount"] > 0]
    trigger_rows = trigger_matrix.get("triggerRows", [])
    satisfied = [trigger for trigger in trigger_rows if trigger.get("triggerSatisfiedNow")]
    source_backed_r3 = 1 if strict_rows and all_four_active_overlap_modes else 0
    selector_count = 1 if source_backed_r3 and satisfied else 0
    return {
        "transformCount": len(transform_names),
        "transformNames": transform_names,
        "traceRowCount": len(rows),
        "activeOverlapRows": sum(1 for row in rows if row["activeOverlapCount"] > 0),
        "controlOverlapRows": sum(1 for row in rows if row["controlOverlapCount"] > 0),
        "allFourActiveOverlapModes": all_four_active_overlap_modes,
        "allFourControlOverlapModes": all_four_control_overlap_modes,
        "activeFormatStreams": active_format_streams,
        "activeKindStreams": active_kind_streams,
        "diagAntiMinOverlapVsProjected": round(diag_anti_min_overlap, 6),
        "diagAntiMaxOverlapVsProjected": round(diag_anti_max_overlap, 6),
        "strictInstructionRows": len(strict_rows),
        "contextTermRows": sum(1 for row in rows if row["contextTermHitCount"] > 0),
        "targetTermRows": sum(1 for row in rows if row["targetTermHitCount"] > 0),
        "sourceBackedR3BridgeHitCount": source_backed_r3,
        "satisfiedReopenTriggerCount": len(satisfied),
        "triggerCount": len(trigger_rows),
        "selectorCandidateCount": selector_count,
    }


def draw_sheet(rows: list[dict[str, Any]], target_rows_: list[dict[str, Any]]) -> None:
    image = Image.open(PAGE_76_UPRIGHT).convert("RGB")
    big = font(18)
    small = font(13)
    panel_w, panel_h = 360, 270
    cols = 4
    sheet = Image.new("RGB", (cols * panel_w, 5 * panel_h), "white")
    draw = ImageDraw.Draw(sheet)
    for idx, row in enumerate(rows[:20]):
        col = idx % cols
        row_idx = idx // cols
        x = col * panel_w
        y = row_idx * panel_h
        px0, py0, px1, py1 = row["projectedBox"]
        crop = [
            int(max(0, px0 - 90)),
            int(max(0, py0 - 70)),
            int(min(image.width, px1 + 90)),
            int(min(image.height, py1 + 70)),
        ]
        panel = image.crop(crop)
        panel.thumbnail((panel_w - 20, panel_h - 80))
        sheet.paste(panel, (x + 10, y + 58))
        sx = panel.width / max(1, crop[2] - crop[0])
        sy = panel.height / max(1, crop[3] - crop[1])

        def map_box(box: list[float]) -> list[float]:
            return [
                x + 10 + (box[0] - crop[0]) * sx,
                y + 58 + (box[1] - crop[1]) * sy,
                x + 10 + (box[2] - crop[0]) * sx,
                y + 58 + (box[3] - crop[1]) * sy,
            ]

        for target in target_rows_:
            if intersection_box(row["projectedBox"], target["box"]):
                color = (255, 120, 0) if target["active"] else (90, 130, 255)
                draw.rectangle(map_box(target["box"]), outline=color, width=2)
        draw.rectangle(map_box(row["projectedBox"]), outline=(0, 0, 0), width=3)
        title = f"{row['transform']} {row['sourceShortId']}->{row['bestOverlapId'] or '-'}"
        draw.text((x + 10, y + 10), title, fill="black", font=big)
        counts = f"act {row['activeOverlapCount']} ctl {row['controlOverlapCount']} ov {row['bestOverlapVsProjected']:.3f}"
        draw.text((x + 10, y + 34), counts, fill="black", font=small)
        preview = row["textPreview"] or "(no OCR words)"
        if len(preview) > 50:
            preview = preview[:47] + "..."
        draw.text((x + 10, y + panel_h - 24), preview, fill=(35, 38, 45), font=small)
    sheet.save(OUT_SHEET, quality=92)


def write_outputs(result: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    summary = result["summary"]
    lines = [
        "# Current Scan Active-Envelope Transform Format Trace",
        "",
        "Scope: measured full box overlap between active-envelope fold/mirror projected boxes and page-76 active/highlight-control format boxes. This is a format/provenance check only; no OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Transform / trace rows: `{summary['transformCount']}` / `{summary['traceRowCount']}`",
        f"- Active-overlap rows / control-overlap rows: `{summary['activeOverlapRows']}` / `{summary['controlOverlapRows']}`",
        f"- All-four active-overlap modes: `{','.join(summary['allFourActiveOverlapModes']) or '-'}`",
        f"- All-four control-overlap modes: `{','.join(summary['allFourControlOverlapModes']) or '-'}`",
        f"- Diag-anti overlap-vs-projected min/max: `{summary['diagAntiMinOverlapVsProjected']}` / `{summary['diagAntiMaxOverlapVsProjected']}`",
        f"- Strict instruction rows / context rows / target rows: `{summary['strictInstructionRows']}` / `{summary['contextTermRows']}` / `{summary['targetTermRows']}`",
        f"- Source-backed R3 / satisfied triggers / selectors: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}` / `{summary['selectorCandidateCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Format Streams",
        "",
    ]
    for name, stream in summary["activeFormatStreams"].items():
        lines.append(f"- `{name}`: `{stream}` / `{summary['activeKindStreams'][name]}`")
    lines.extend(
        [
            "",
            "## Projected Format Rows",
            "",
            "| transform | source | slot | active hits | control hits | best overlap | text strict | best format | text preview |",
            "|---|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in result["rows"]:
        preview = (row["textPreview"] or "-").replace("|", "\\|")
        if len(preview) > 72:
            preview = preview[:69] + "..."
        best = row["bestOverlapId"] or "-"
        if row["bestOverlapKind"]:
            best = f"{best}/{row['bestOverlapKind']}"
        lines.append(
            f"| `{row['transform']}` | `{row['sourceShortId']}` | `{row['projectedSlotLetter']}` | "
            f"`{row['activeOverlapCount']}` | `{row['controlOverlapCount']}` | "
            f"`{row['bestOverlapVsProjected']}` | `{row['strictInstructionHitCount']}` | {best} | {preview} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_active_envelope_transform_format_trace_no_selector`",
            "- The anti-diagonal fold does create partial all-four active-box overlap, but this is weak self-overlap inside the active envelope, not a readable selector.",
            "- The overlap mode has no strict instruction text, no satisfied reopen trigger, and no source-backed unit/order.",
            "",
            "## Next Move",
            "",
            "- Keep active-envelope fold/mirror mechanics closed for the current scan.",
            "- Reopen only if a raw clue or distinct source explicitly names active-envelope folding plus a reading unit/order.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    active_gate = load_json(ACTIVE_ENVELOPE_GATE)
    active_index = load_json(ACTIVE_INDEX_SLOT)
    highlight_benchmark = load_json(PAGE76_HIGHLIGHT_BENCHMARK)
    text_trace = load_json(TEXT_TRACE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    targets = target_rows(active_index, highlight_benchmark)
    rows = trace_rows(active_gate, targets, text_lookup(text_trace))
    summary = summarize(active_gate, rows, trigger_matrix)
    fingerprint = (
        f"transforms={summary['transformCount']}|rows={summary['traceRowCount']}|"
        f"activeRows={summary['activeOverlapRows']}|controlRows={summary['controlOverlapRows']}|"
        f"allFourActive={len(summary['allFourActiveOverlapModes'])}|"
        f"diagAntiMinMax={summary['diagAntiMinOverlapVsProjected']}/{summary['diagAntiMaxOverlapVsProjected']}|"
        f"strictRows={summary['strictInstructionRows']}|sourceR3={summary['sourceBackedR3BridgeHitCount']}|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        f"selectors={summary['selectorCandidateCount']}"
    )
    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": (
            "trace active-envelope fold/mirror projected boxes against page-76 active and highlight-control format boxes; "
            "no OCR-to-key/key/hash/seed/WIF/address/BIP39/brute force"
        ),
        "inputs": {
            "activeEnvelopeTransformGate": rel(ACTIVE_ENVELOPE_GATE),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "page76HighlightBenchmark": rel(PAGE76_HIGHLIGHT_BENCHMARK),
            "textTrace": rel(TEXT_TRACE),
            "page76Upright": rel(PAGE_76_UPRIGHT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "rows": rows,
        "decision": {
            "selectorUnlocked": False,
            "reason": (
                "Partial diag-anti all-four active overlap is self-overlap inside the active envelope; "
                "the paired text trace has zero strict instruction rows and no source-backed R3."
            ),
            "nextMove": (
                "Keep active-envelope fold/mirror mechanics closed unless new source/raw clue evidence "
                "names this fold and a unit/order."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    draw_sheet(rows, targets)
    write_outputs(result)
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_SHEET}")
    print(fingerprint)


if __name__ == "__main__":
    main()

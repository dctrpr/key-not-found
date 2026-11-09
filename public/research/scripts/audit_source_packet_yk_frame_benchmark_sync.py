#!/usr/bin/env python3
"""Sync the source-acquisition handoff with the O4 frame Y/K benchmark.

This is a bounded source-validation readiness pass. It does not run OCR,
private-key derivation, hashing, WIF/Base58 scans, seed generation, address
checks, or broad candidate generation.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_yk_frame_benchmark_sync"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_yk_frame_benchmark_sync.json"
OUT_MD = OUT / "source_packet_yk_frame_benchmark_sync.md"
SHEET = OUT / "source_packet_yk_frame_benchmark_sync_sheet.jpg"

INPUTS = {
    "source_packet": ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.json",
    "crop_authority_sync": ROOT / "analysis_outputs/source_audit/source_packet_crop_authority_sync/source_packet_crop_authority_sync.json",
    "yk_filter_control": ROOT / "analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control.json",
    "yk_unit_order_gate": ROOT / "analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/o4_frame_yk_unit_order_gate.json",
    "orientation_trap": ROOT / "analysis_outputs/source_audit/page76_active_order_orientation_trap/page76_active_order_orientation_trap.json",
    "active_crops": ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json",
}

THUMBNAILS = [
    {
        "title": "source packet",
        "path": ROOT / "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet_sheet.jpg",
    },
    {
        "title": "4/4 active crop authority",
        "path": ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion_sheet.jpg",
    },
    {
        "title": "Y/K frame filter control",
        "path": ROOT / "analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/o4_frame_rescue_yk_filter_control_sheet.jpg",
    },
    {
        "title": "Y/K unit-order gate",
        "path": ROOT / "analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/o4_frame_yk_unit_order_gate_sheet.jpg",
    },
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


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


def count_dead_branches() -> int:
    path = ROOT / "analysis_outputs/dead_branch_blacklist.md"
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("- "))


def contains_yk_frame_benchmark(packet: dict[str, Any]) -> bool:
    packet_text = json.dumps(packet, ensure_ascii=False).lower()
    required_terms = ["y/k", "ykk", "frame y/k", "o4 frame"]
    return any(term in packet_text for term in required_terms)


def paste_thumb(sheet: Image.Image, path: Path, box: tuple[int, int, int, int], title: str) -> None:
    draw = ImageDraw.Draw(sheet)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(17, 22, 29), outline=(56, 64, 76))
    draw.text((x0 + 12, y0 + 10), title, fill=(240, 245, 250), font=font(18))
    if not path.exists():
        draw.text((x0 + 12, y0 + 46), "missing", fill=(255, 130, 130), font=font(14))
        return
    image = Image.open(path).convert("RGB")
    max_w = x1 - x0 - 24
    max_h = y1 - y0 - 58
    scale = min(max_w / image.width, max_h / image.height)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    resample = getattr(Image, "Resampling", Image).LANCZOS
    resized = image.resize(new_size, resample)
    sheet.paste(resized, (x0 + 12, y0 + 44))


def build_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1760, 1480
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (9, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title = font(34)
    normal = font(17)
    small = font(13)
    mono = font(15)

    draw.text((margin, margin), "Source Packet Y/K Frame Benchmark Sync", fill=(246, 249, 252), font=title)
    draw.text(
        (margin, margin + 45),
        "Supplemental source-validation benchmark only: Y/K + frame isolates O4/B4/G5/O5, but R3 unit/order is still absent.",
        fill=(178, 188, 200),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("supplement", result["summary"]["supplementNeeded"]),
        ("active coverage", result["summary"]["frameYkActiveTargetCoverage"]),
        ("non-active in frame", result["summary"]["frameYkNonActiveGroupCount"]),
        ("hard hits", result["summary"]["hardInstructionHitCount"]),
        ("selector", "blocked"),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 310, y + 52), fill=(23, 30, 39), outline=(50, 59, 70))
        draw.text((x + 12, y + 8), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 27), str(value)[:30], fill=(234, 241, 248), font=mono)
        x += 330

    y += 82
    draw.rectangle((margin, y, sheet_w - margin, y + 178), fill=(38, 31, 18), outline=(96, 73, 32))
    draw.text((margin + 14, y + 14), "Future Source Benchmark", fill=(255, 220, 140), font=normal)
    for idx, line in enumerate(result["benchmark"]["mustPreserve"] + result["benchmark"]["mustNotInfer"]):
        draw.text((margin + 14, y + 48 + idx * 28), f"- {line}", fill=(255, 220, 140), font=small)

    y += 210
    headers = [("target", 12), ("line/corr", 330), ("state", 500), ("group order", 650), ("x order", 1000)]
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 36, 45))
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38

    group_rows = result["targetRows"]["groupOrder"]
    x_rows = {row["id"]: row for row in result["targetRows"]["leftToRight"]}
    for row in group_rows:
        draw.rectangle((margin, y, sheet_w - margin, y + 44), fill=(18, 23, 30), outline=(49, 59, 72))
        x_row = x_rows.get(row["id"], {})
        draw.text((margin + 12, y + 12), row["label"], fill=(238, 243, 248), font=small)
        draw.text((margin + 330, y + 12), f"L{row['pageLine']}/C{row['corridorIndex']}", fill=(238, 243, 248), font=mono)
        draw.text((margin + 500, y + 12), row["layerCode"], fill=(238, 243, 248), font=mono)
        draw.text((margin + 650, y + 12), str(row["orderIndex"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 1000, y + 12), str(x_row.get("orderIndex")), fill=(176, 186, 198), font=mono)
        y += 48

    y += 24
    thumb_w = (sheet_w - margin * 2 - 28) // 2
    thumb_h = 340
    for idx, thumb in enumerate(THUMBNAILS):
        col = idx % 2
        row = idx // 2
        x0 = margin + col * (thumb_w + 28)
        y0 = y + row * (thumb_h + 22)
        paste_thumb(sheet, thumb["path"], (x0, y0, x0 + thumb_w, y0 + thumb_h), thumb["title"])

    sheet.save(SHEET, quality=94)


def main() -> None:
    source_packet = load_json(INPUTS["source_packet"])
    crop_sync = load_json(INPUTS["crop_authority_sync"])
    yk_filter = load_json(INPUTS["yk_filter_control"])
    yk_unit = load_json(INPUTS["yk_unit_order_gate"])
    orientation = load_json(INPUTS["orientation_trap"])
    active_crops = load_json(INPUTS["active_crops"])

    yk_summary = yk_filter.get("summary", {})
    unit_summary = yk_unit.get("summary", {})
    orientation_summary = orientation.get("summary", {})
    historical_has_yk = contains_yk_frame_benchmark(source_packet)
    supplement_needed = not historical_has_yk

    group_order = []
    for idx, target_id in enumerate(unit_summary.get("groupOrderTargetIds", []), start=1):
        crop = next((row for row in active_crops.get("targets", []) if row.get("id") == target_id), {})
        layer_codes = unit_summary.get("groupOrderLayerCodes", "")
        group_order.append(
            {
                "orderIndex": idx,
                "id": target_id,
                "label": crop.get("label", target_id),
                "pageLine": crop.get("pageLine"),
                "corridorIndex": crop.get("corridorIndex"),
                "layerCode": layer_codes[idx - 1] if idx - 1 < len(layer_codes) else "",
                "box": crop.get("box"),
            }
        )

    left_to_right = []
    for idx, target_id in enumerate(unit_summary.get("leftToRightTargetIds", []), start=1):
        crop = next((row for row in active_crops.get("targets", []) if row.get("id") == target_id), {})
        layer_code = next((row.get("layerCode") for row in group_order if row.get("id") == target_id), "")
        left_to_right.append(
            {
                "orderIndex": idx,
                "id": target_id,
                "label": crop.get("label", target_id),
                "pageLine": crop.get("pageLine"),
                "corridorIndex": crop.get("corridorIndex"),
                "layerCode": layer_code,
                "box": crop.get("box"),
            }
        )

    summary = {
        "historicalPacketHasYkFrameBenchmark": historical_has_yk,
        "supplementNeeded": supplement_needed,
        "cropAuthoritySyncStatus": crop_sync.get("summary", {}).get("syncStatus"),
        "frameYkActiveTargetCoverage": f"{yk_summary.get('frameYkActiveGroupCount')}/4",
        "frameYkAllActiveTargetsCovered": yk_summary.get("frameYkAllActiveTargetsCovered"),
        "frameYkLayerCodes": yk_summary.get("frameYkLayerCodes"),
        "frameYkNonActiveGroupCount": yk_summary.get("frameYkNonActiveGroupCount"),
        "fullPageYkNonActiveGroupCount": yk_summary.get("fullPageYkNonActiveGroupCount"),
        "boundedStreamCount": unit_summary.get("boundedStreamCount"),
        "hardInstructionHitCount": unit_summary.get("totalHardInstructionHitCount"),
        "sourceBackedUnitOrder": unit_summary.get("sourceBackedUnitOrder"),
        "groupOrderTargetIds": unit_summary.get("groupOrderTargetIds"),
        "leftToRightTargetIds": unit_summary.get("leftToRightTargetIds"),
        "pageLines": unit_summary.get("pageLines"),
        "corridorIndexes": unit_summary.get("corridorIndexes"),
        "colorPatternIsPalindrome": orientation_summary.get("colorPatternIsPalindrome"),
        "visualStatePatternIsPalindrome": orientation_summary.get("visualStatePatternIsPalindrome"),
        "selectorUnlocked": False,
        "deadBranchCount": count_dead_branches(),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source packet Y/K frame benchmark sync; no OCR, no extraction, no key derivation, no hashing, no address checks",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "summary": summary,
        "targetRows": {"groupOrder": group_order, "leftToRight": left_to_right},
        "benchmark": {
            "id": "C9_O4_FRAME_YK_ISOLATION",
            "status": "supplemental_source_validation_benchmark_only",
            "mustPreserve": [
                "Y/K + full-coverage frame isolates O4/B4/G5/O5 with no non-active in-frame Y/K groups.",
                "Readable/upright order is lines 22,25,27,32 and corridors 4,7,9,14.",
                "Frame Y/K layer stream is YKKY, but it is orientation-palindromic with OBBO.",
            ],
            "mustNotInfer": [
                "Do not infer extraction from Y/K alone: full-page Y/K has four non-active controls.",
                "Do not infer order from color/state alone; require line/corridor authority or source wording.",
                "Do not resume selector/key checks unless the same new source/clue passes R1-R5, especially R3.",
            ],
        },
        "handoffRule": {
            "useHistoricalPacketForJobs": "analysis_outputs/source_audit/source_acquisition_target_packet/source_acquisition_target_packet.md",
            "useCropAuthorityForVisualTargets": "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.md",
            "useYkFrameBenchmarkForSourceValidation": "analysis_outputs/source_audit/source_packet_yk_frame_benchmark_sync/source_packet_yk_frame_benchmark_sync.md",
            "r3GateStillRequired": True,
        },
        "decision": "source_packet_yk_frame_benchmark_synced_no_selector",
        "sheet": rel(SHEET),
        "nextMove": "Use the historical source packet plus crop authority plus this Y/K-frame benchmark as the source-review handoff; reopen extraction only if a new source/clue names the unit/order or independently explains the frame-intersection rule.",
    }

    build_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Y/K Frame Benchmark Sync",
        "",
        "Scope: check whether the source-acquisition handoff captures the clean `Y/K + frame` benchmark. No OCR, extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Historical packet already names this benchmark: `{summary['historicalPacketHasYkFrameBenchmark']}`",
        f"- Supplemental benchmark needed: `{summary['supplementNeeded']}`",
        f"- Crop authority sync status: `{summary['cropAuthoritySyncStatus']}`",
        f"- Frame `Y/K` active coverage: `{summary['frameYkActiveTargetCoverage']}`",
        f"- Frame `Y/K` non-active groups: `{summary['frameYkNonActiveGroupCount']}`",
        f"- Full-page `Y/K` non-active controls: `{summary['fullPageYkNonActiveGroupCount']}`",
        f"- Bounded unit/order streams checked upstream: `{summary['boundedStreamCount']}`",
        f"- Hard instruction hits upstream: `{summary['hardInstructionHitCount']}`",
        f"- Source-backed unit/order: `{summary['sourceBackedUnitOrder']}`",
        f"- Selector unlocked: `{summary['selectorUnlocked']}`",
        f"- Dead-branch count: `{summary['deadBranchCount']}`",
        "",
        "## Benchmark",
        "",
        f"- Id: `{result['benchmark']['id']}`",
        f"- Status: `{result['benchmark']['status']}`",
        "",
        "Must preserve in a future source/original-layout comparison:",
    ]
    lines.extend(f"- {item}" for item in result["benchmark"]["mustPreserve"])
    lines.append("")
    lines.append("Must not infer from the current scan:")
    lines.extend(f"- {item}" for item in result["benchmark"]["mustNotInfer"])

    lines.extend(
        [
            "",
            "## Target Order Contrast",
            "",
            "| order | target ids | line/corridor |",
            "|---|---|---|",
            f"| group/readable | `{' -> '.join(summary['groupOrderTargetIds'])}` | `{' / '.join(f'L{row['pageLine']} C{row['corridorIndex']}' for row in group_order)}` |",
            f"| left-to-right | `{' -> '.join(summary['leftToRightTargetIds'])}` | `{' / '.join(f'L{row['pageLine']} C{row['corridorIndex']}' for row in left_to_right)}` |",
            "",
            "## Handoff Rule",
            "",
            f"- Use historical packet for jobs/gates: `{result['handoffRule']['useHistoricalPacketForJobs']}`",
            f"- Use crop authority for visual targets: `{result['handoffRule']['useCropAuthorityForVisualTargets']}`",
            f"- Use this report for Y/K-frame source validation: `{result['handoffRule']['useYkFrameBenchmarkForSourceValidation']}`",
            f"- R3 gate still required: `{result['handoffRule']['r3GateStillRequired']}`",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

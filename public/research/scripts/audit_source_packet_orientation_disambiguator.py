#!/usr/bin/env python3
"""Build a source-packet orientation disambiguator.

This bounded pass does not try another selector. It records which visual
signals are orientation-ambiguous and which geometry/source signals can reject
raw-native, mirrored, or folded page matches during future source review.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_orientation_disambiguator"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_orientation_disambiguator.json"
OUT_MD = OUT / "source_packet_orientation_disambiguator.md"
OUT_SHEET = OUT / "source_packet_orientation_disambiguator_sheet.jpg"

INPUTS = {
    "native_benchmark_bridge": ROOT
    / "analysis_outputs/source_audit/source_packet_native_benchmark_bridge/"
    "source_packet_native_benchmark_bridge.json",
    "geometric_fingerprint": ROOT
    / "analysis_outputs/source_audit/source_packet_geometric_fingerprint/"
    "source_packet_geometric_fingerprint.json",
    "frame_normalized_geometry": ROOT
    / "analysis_outputs/source_audit/source_packet_frame_normalized_geometry/"
    "source_packet_frame_normalized_geometry.json",
    "color_profile_manifest": ROOT
    / "analysis_outputs/source_audit/source_packet_color_profile_manifest/"
    "source_packet_color_profile_manifest.json",
    "alignment_tolerance": ROOT
    / "analysis_outputs/source_audit/source_packet_alignment_tolerance/"
    "source_packet_alignment_tolerance.json",
    "orientation_guardrail": ROOT
    / "analysis_outputs/source_audit/page76_active_crop_orientation_guardrail/"
    "page76_active_crop_orientation_guardrail.json",
    "order_orientation_trap": ROOT
    / "analysis_outputs/source_audit/page76_active_order_orientation_trap/"
    "page76_active_order_orientation_trap.json",
    "handoff_integrity_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_handoff_integrity_matrix/"
    "source_packet_handoff_integrity_matrix.json",
    "reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def as_box(values: list[float]) -> tuple[float, float, float, float]:
    return float(values[0]), float(values[1]), float(values[2]), float(values[3])


def transform_center(center: list[float], width: int, height: int, mode: str) -> tuple[float, float]:
    x, y = float(center[0]), float(center[1])
    if mode == "readable_upright":
        return x, y
    if mode == "x_mirror":
        return width - x, y
    if mode == "y_mirror":
        return x, height - y
    if mode == "point_mirror_or_raw_native":
        return width - x, height - y
    raise ValueError(mode)


def sign_stream(points: list[tuple[float, float]], axis: str) -> str:
    idx = 0 if axis == "x" else 1
    chars = []
    for left, right in zip(points, points[1:]):
        delta = right[idx] - left[idx]
        chars.append("+" if delta > 0 else "-" if delta < 0 else "0")
    return "".join(chars)


def norm_stream(points: list[tuple[float, float]], frame: tuple[float, float, float, float]) -> str:
    x0, y0, x1, y1 = frame
    fw = x1 - x0
    fh = y1 - y0
    return ";".join(f"{(x - x0) / fw:.3f},{(y - y0) / fh:.3f}" for x, y in points)


def draw_sheet(summary: dict, orientation_rows: list[dict], signal_rows: list[dict]) -> None:
    width, height = 1800, 1040
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 16)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 96), fill=(26, 31, 38))
    draw.text((24, 20), "Source Packet Orientation Disambiguator", fill="white", font=title)
    draw.text(
        (24, 58),
        f"accepted modes {summary['acceptedOrientationModeCount']}/{summary['orientationModeCount']} | ambiguous signals {summary['ambiguousSignalCount']} | discriminators {summary['discriminatingSignalCount']} | fingerprint {summary['orientationDisambiguatorFingerprint']}",
        fill=(232, 232, 232),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Orientation candidate modes", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["mode", "line/corridor order", "dx/dy signs", "C9 normalized centers", "decision"]
    xs = [24, 310, 590, 820, 1420]
    for x, h in zip(xs, headers):
        draw.text((x, y), h, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(orientation_rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (236, 240, 246)
        draw.rectangle((18, y - 4, width - 18, y + 72), fill=fill)
        decision_color = (25, 110, 55) if row["acceptedForFutureSourceComparison"] else (130, 35, 25)
        draw.text((xs[0], y), row["mode"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[0], y + 18), row["readOrder"], fill=(80, 80, 80), font=tiny)
        draw.text((xs[1], y), row["pageLines"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y + 18), row["corridorIndexes"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), f"dx {row['dxSignStream']}", fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y + 18), f"dy {row['dySignStream']}", fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["c9NormalizedCenterStream"][:82], fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), row["decision"], fill=decision_color, font=tiny)
        draw.text((xs[4], y + 18), row["reason"][:44], fill=(80, 80, 80), font=tiny)
        y += 82

    y += 18
    draw.text((24, y), "Signal roles", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["signal", "observed", "role", "future-source use"]
    xs = [24, 430, 760, 1110]
    for x, h in zip(xs, headers):
        draw.text((x, y), h, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(signal_rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (236, 240, 246)
        draw.rectangle((18, y - 4, width - 18, y + 52), fill=fill)
        role_color = (130, 35, 25) if row["role"] == "ambiguous" else (25, 85, 130)
        draw.text((xs[0], y), row["signal"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), str(row["observed"])[:48], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["role"], fill=role_color, font=tiny)
        draw.text((xs[3], y), row["futureSourceUse"][:80], fill=(30, 30, 30), font=tiny)
        y += 58

    img.save(OUT_SHEET, quality=92)


def main() -> None:
    bridge = load_json(INPUTS["native_benchmark_bridge"])
    geom = load_json(INPUTS["geometric_fingerprint"])
    frame = load_json(INPUTS["frame_normalized_geometry"])
    color = load_json(INPUTS["color_profile_manifest"])
    tolerance = load_json(INPUTS["alignment_tolerance"])
    orientation = load_json(INPUTS["orientation_guardrail"])
    order_trap = load_json(INPUTS["order_orientation_trap"])
    handoff = load_json(INPUTS["handoff_integrity_matrix"])
    reopen = load_json(INPUTS["reopen_trigger_matrix"])

    width, height = bridge.get("imageSize", [2544, 3264])
    active_rows = [row for row in bridge.get("rows", []) if row.get("kind") == "active_target"]
    c9_frame = next(row for row in bridge.get("rows", []) if row.get("id") == "c9_yk_frame")
    c9_box = as_box(c9_frame["uprightBox"])

    modes = [
        (
            "readable_upright",
            "line/corridor top-to-bottom",
            active_rows,
            "accept_for_source_comparison",
            "matches text authority and native rotate180 bridge",
            True,
        ),
        (
            "raw_native_unrotated_top_to_bottom",
            "native y ascending",
            sorted(active_rows, key=lambda row: row["nativeCenter"][1]),
            "reject_until_rot180_normalized",
            "visual/color stream is unchanged but order is reversed",
            False,
        ),
        (
            "x_mirror_about_page",
            "same ids after x mirror",
            active_rows,
            "reject_as_loose_mirror",
            "horizontal center-step signs invert",
            False,
        ),
        (
            "y_mirror_about_page",
            "same ids after y mirror",
            active_rows,
            "reject_as_loose_mirror",
            "vertical order/signs invert",
            False,
        ),
        (
            "point_mirror_or_page_rotate180",
            "same ids after point mirror",
            active_rows,
            "reject_without_native_rot180_context",
            "both center-step streams invert",
            False,
        ),
    ]

    orientation_rows = []
    for mode, read_order, rows, decision, reason, accepted in modes:
        transform_mode = {
            "raw_native_unrotated_top_to_bottom": "readable_upright",
            "readable_upright": "readable_upright",
            "x_mirror_about_page": "x_mirror",
            "y_mirror_about_page": "y_mirror",
            "point_mirror_or_page_rotate180": "point_mirror_or_raw_native",
        }[mode]
        points = [transform_center(row["uprightCenter"], width, height, transform_mode) for row in rows]
        orientation_rows.append(
            {
                "mode": mode,
                "readOrder": read_order,
                "targetIds": [row["id"] for row in rows],
                "visualStateStream": "".join(row.get("visualState", "?") for row in rows),
                "pageLines": " ".join(str(row["pageLine"]) for row in rows),
                "corridorIndexes": " ".join(str(row["corridorIndex"]) for row in rows),
                "dxSignStream": sign_stream(points, "x"),
                "dySignStream": sign_stream(points, "y"),
                "c9NormalizedCenterStream": norm_stream(points, c9_box),
                "acceptedForFutureSourceComparison": accepted,
                "decision": decision,
                "reason": reason,
            }
        )

    signal_rows = [
        {
            "signal": "visual state stream",
            "observed": order_trap.get("summary", {}).get("visualStatePattern"),
            "role": "ambiguous",
            "futureSourceUse": "Do not validate orientation from YKKY alone; it survives reversal.",
        },
        {
            "signal": "orange/black color stream",
            "observed": order_trap.get("summary", {}).get("colorPattern"),
            "role": "ambiguous",
            "futureSourceUse": "Do not validate orientation from OBBO alone; it is palindromic.",
        },
        {
            "signal": "C9 frame horizontal mirror",
            "observed": f"xMirrorInvariant={bridge.get('summary', {}).get('c9FrameXMirrorInvariant')}",
            "role": "ambiguous",
            "futureSourceUse": "Treat frame-only matches as source-registration evidence, not selector permission.",
        },
        {
            "signal": "OVERDOSE control state",
            "observed": color.get("summary", {}).get("overdoseControlClassifiedStateStream"),
            "role": "ambiguous",
            "futureSourceUse": "Header glyphs stay non-active; require external slot wording before use.",
        },
        {
            "signal": "page-line order",
            "observed": f"{order_trap.get('summary', {}).get('uprightPageLines')} vs {order_trap.get('summary', {}).get('nativeUnnormalizedPageLines')}",
            "role": "discriminator",
            "futureSourceUse": "Require readable order 22/25/27/32 after orientation normalization.",
        },
        {
            "signal": "corridor-index order",
            "observed": f"{order_trap.get('summary', {}).get('uprightCorridorIndexes')} vs {order_trap.get('summary', {}).get('nativeUnnormalizedCorridorIndexes')}",
            "role": "discriminator",
            "futureSourceUse": "Require corridor order 4/7/9/14 after orientation normalization.",
        },
        {
            "signal": "center-step signs",
            "observed": f"dx {geom.get('summary', {}).get('dxSignStream')}; dy {geom.get('summary', {}).get('dySignStream')}",
            "role": "discriminator",
            "futureSourceUse": "Reject loose mirror matches that invert dx or dy signs without provenance.",
        },
        {
            "signal": "C9 normalized centers",
            "observed": frame.get("summary", {}).get("c9NormalizedCenterStream"),
            "role": "discriminator",
            "futureSourceUse": "Compare normalized positions, not just frame containment or color state.",
        },
        {
            "signal": "native rotate180 roundtrip",
            "observed": f"mean {orientation.get('summary', {}).get('rot180MeanAbsDiff')} vs direct {orientation.get('summary', {}).get('directMeanAbsDiff')}",
            "role": "discriminator",
            "futureSourceUse": "Normalize native source assets with the documented 180-degree transform first.",
        },
        {
            "signal": "alignment tolerance",
            "observed": f"shift +/-{tolerance.get('summary', {}).get('commonFullEightDirectionShiftAllTargetsPassPx')}px; pad +{tolerance.get('summary', {}).get('commonOutwardPadAllTargetsPassPx')}px",
            "role": "discriminator",
            "futureSourceUse": "Reject geometry matches outside the narrow tolerance unless source provenance explains them.",
        },
    ]

    ambiguous_count = sum(1 for row in signal_rows if row["role"] == "ambiguous")
    discriminator_count = sum(1 for row in signal_rows if row["role"] == "discriminator")
    summary = {
        "orientationModeCount": len(orientation_rows),
        "acceptedOrientationModeCount": sum(1 for row in orientation_rows if row["acceptedForFutureSourceComparison"]),
        "rejectedOrientationModeCount": sum(1 for row in orientation_rows if not row["acceptedForFutureSourceComparison"]),
        "ambiguousSignalCount": ambiguous_count,
        "discriminatingSignalCount": discriminator_count,
        "currentVisualStatePattern": order_trap.get("summary", {}).get("visualStatePattern"),
        "currentColorPattern": order_trap.get("summary", {}).get("colorPattern"),
        "visualStatePatternIsPalindrome": order_trap.get("summary", {}).get(
            "visualStatePatternIsPalindrome"
        ),
        "colorPatternIsPalindrome": order_trap.get("summary", {}).get("colorPatternIsPalindrome"),
        "readablePageLineOrder": order_trap.get("summary", {}).get("uprightPageLines"),
        "nativeUnnormalizedPageLineOrder": order_trap.get("summary", {}).get(
            "nativeUnnormalizedPageLines"
        ),
        "readableCorridorOrder": order_trap.get("summary", {}).get("uprightCorridorIndexes"),
        "nativeUnnormalizedCorridorOrder": order_trap.get("summary", {}).get(
            "nativeUnnormalizedCorridorIndexes"
        ),
        "readableDxSignStream": geom.get("summary", {}).get("dxSignStream"),
        "readableDySignStream": geom.get("summary", {}).get("dySignStream"),
        "c9NormalizedCenterStream": frame.get("summary", {}).get("c9NormalizedCenterStream"),
        "commonShiftTolerancePx": handoff.get("summary", {}).get("commonShiftTolerancePx"),
        "sourceBackedR3BridgeHitCount": reopen.get("summary", {}).get(
            "sourceBackedR3BridgeHitCount"
        ),
        "satisfiedReopenTriggerCount": reopen.get("summary", {}).get("satisfiedTriggerCount"),
        "selectorUnlockedCount": handoff.get("summary", {}).get("selectorUnlockedCount"),
        "extractionReadyGateCount": handoff.get("summary", {}).get("extractionReadyGateCount"),
    }
    summary["orientationDisambiguatorFingerprint"] = (
        f"modes={summary['orientationModeCount']}"
        f"|accepted={summary['acceptedOrientationModeCount']}"
        f"|ambiguous={summary['ambiguousSignalCount']}"
        f"|discriminators={summary['discriminatingSignalCount']}"
        f"|states={summary['currentVisualStatePattern']}"
        f"|color={summary['currentColorPattern']}"
        f"|lines={summary['readablePageLineOrder'].replace(' ', '-')}"
        f"|nativeLines={summary['nativeUnnormalizedPageLineOrder'].replace(' ', '-')}"
        f"|dx={summary['readableDxSignStream']}"
        f"|dy={summary['readableDySignStream']}"
        f"|sourceR3={summary['sourceBackedR3BridgeHitCount']}"
        f"|selectors={summary['selectorUnlockedCount']}"
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "source-packet orientation disambiguator; no OCR, extraction, key derivation, "
            "hashing, seed/WIF/address checks, BIP39 checks, or broad brute force"
        ),
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "imageSize": bridge.get("imageSize"),
        "orientationRows": orientation_rows,
        "signalRows": signal_rows,
        "summary": summary,
        "decision": {
            "sourcePacketOrientationDisambiguator": "orientation_signals_are_validation_only",
            "reason": (
                "Only readable/upright orientation is accepted for future source comparison. "
                "YKKY/OBBO and C9 frame containment are orientation-ambiguous; line/corridor order, "
                "center-step signs, C9 normalized centers, native rotate180 roundtrip, and +/-4px "
                "tolerance are the controls. No selector or extraction gate is unlocked."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "nextMove": (
            "Use this disambiguator with the reopen-trigger matrix when inspecting a new source asset: "
            "normalize orientation first, then require readable order 22/25/27/32 and corridor order 4/7/9/14 "
            "before treating visual matches as evidence."
        ),
    }

    draw_sheet(summary, orientation_rows, signal_rows)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Orientation Disambiguator",
        "",
        "Scope: record which source-packet visual/geometry signals can and cannot disambiguate page orientation for future source review. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Orientation modes checked: `{summary['orientationModeCount']}`",
        f"- Accepted source-comparison modes: `{summary['acceptedOrientationModeCount']}`",
        f"- Rejected/blocked modes: `{summary['rejectedOrientationModeCount']}`",
        f"- Ambiguous visual signals: `{summary['ambiguousSignalCount']}`",
        f"- Discriminating source/geometry signals: `{summary['discriminatingSignalCount']}`",
        f"- Visual/color patterns: `{summary['currentVisualStatePattern']}` / `{summary['currentColorPattern']}`",
        f"- Readable page-line order: `{summary['readablePageLineOrder']}`",
        f"- Raw native unnormalized page-line order: `{summary['nativeUnnormalizedPageLineOrder']}`",
        f"- Readable corridor order: `{summary['readableCorridorOrder']}`",
        f"- Raw native unnormalized corridor order: `{summary['nativeUnnormalizedCorridorOrder']}`",
        f"- Readable center-step signs: dx `{summary['readableDxSignStream']}`, dy `{summary['readableDySignStream']}`",
        f"- Common shift tolerance: `±{summary['commonShiftTolerancePx']}px`",
        f"- Source-backed R3 bridge hits: `{summary['sourceBackedR3BridgeHitCount']}`",
        f"- Satisfied reopen triggers: `{summary['satisfiedReopenTriggerCount']}`",
        f"- Selector unlocks / extraction-ready gates: `{summary['selectorUnlockedCount']}` / `{summary['extractionReadyGateCount']}`",
        f"- Orientation disambiguator fingerprint: `{summary['orientationDisambiguatorFingerprint']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        "",
        "## Orientation Modes",
        "",
        "| mode | target order | visual state | page lines | corridor indexes | dx/dy signs | C9 normalized centers | decision |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in orientation_rows:
        lines.append(
            f"| `{row['mode']}` | `{','.join(row['targetIds'])}` | `{row['visualStateStream']}` | `{row['pageLines']}` | `{row['corridorIndexes']}` | `{row['dxSignStream']}` / `{row['dySignStream']}` | `{row['c9NormalizedCenterStream']}` | `{row['decision']}` |"
        )
    lines.extend(
        [
            "",
            "## Signal Roles",
            "",
            "| signal | observed | role | future-source use |",
            "|---|---|---|---|",
        ]
    )
    for row in signal_rows:
        lines.append(
            f"| `{row['signal']}` | `{row['observed']}` | `{row['role']}` | {row['futureSourceUse']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep the source packet in readable/upright coordinates for comparison; normalize native source images with the documented 180-degree transform first.",
            "- Do not accept `YKKY`, `OBBO`, or C9 frame containment as orientation proof because all are ambiguous under reversal or mirror controls.",
            "- Accept only source matches that preserve readable page-line order `22 25 27 32`, corridor order `4 7 9 14`, center-step signs `-++/+++`, C9 normalized centers, and the narrow `±4px` tolerance unless new source provenance explains a transform.",
            "- This pass is validation-only and does not reopen extraction because source-backed R3 unit/order evidence remains absent.",
            "",
            "## Next Move",
            "",
            result["nextMove"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {rel(OUT_MD)}")
    print(f"wrote {rel(OUT_JSON)}")
    print(f"wrote {rel(OUT_SHEET)}")
    print(f"fingerprint: {summary['orientationDisambiguatorFingerprint']}")


if __name__ == "__main__":
    main()

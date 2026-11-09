#!/usr/bin/env python3
"""Control the current OVERDOSE transform/slot evidence.

This is a bounded geometry inspection. It checks whether the active
O4/B4/G5/O5 quartet gains any new selector power when the measured OVERDOSE
header glyph boxes are projected onto the C9 frame, including mirrored/reversed
variants and the existing p75 control. It does not generate key material.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_overdose_transform_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_overdose_transform_control.json"
OUT_MD = OUT / "source_packet_overdose_transform_control.md"
OUT_SHEET = OUT / "source_packet_overdose_transform_control_sheet.jpg"

INPUTS = {
    "source_packet_native_benchmark_bridge": ROOT
    / "analysis_outputs/source_audit/source_packet_native_benchmark_bridge/"
    "source_packet_native_benchmark_bridge.json",
    "source_packet_geometric_fingerprint": ROOT
    / "analysis_outputs/source_audit/source_packet_geometric_fingerprint/"
    "source_packet_geometric_fingerprint.json",
    "source_packet_frame_normalized_geometry": ROOT
    / "analysis_outputs/source_audit/source_packet_frame_normalized_geometry/"
    "source_packet_frame_normalized_geometry.json",
    "c9_header_glyph_slot_gate": ROOT
    / "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json",
    "c9_mirrored_header_glyph_gate": ROOT
    / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate/"
    "c9_mirrored_header_glyph_gate.json",
    "c9_grey_black_over_slot_control": ROOT
    / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/"
    "c9_grey_black_over_slot_control.json",
    "c9_over_slot_tolerance_gate": ROOT
    / "analysis_outputs/source_audit/c9_over_slot_tolerance_gate/"
    "c9_over_slot_tolerance_gate.json",
    "source_packet_source_review_gate": ROOT
    / "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def stream_by_suffix(streams: list[dict], suffix: str) -> dict:
    for item in streams:
        if str(item.get("name", "")).endswith(suffix):
            return item
    return {}


def unique(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        if value not in out:
            out.append(value)
    return out


def fit_line(xs: list[float], ys: list[float]) -> dict:
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    var_x = sum((x - mean_x) ** 2 for x in xs)
    cov_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    slope = cov_xy / var_x if var_x else 0.0
    intercept = mean_y - slope * mean_x
    residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
    return {
        "slope": round(slope, 6),
        "intercept": round(intercept, 6),
        "residuals": [round(v, 6) for v in residuals],
        "maxAbsResidualSlots": round(max(abs(v) for v in residuals), 6),
    }


def draw_sheet(summary: dict, rows: list[dict], variants: list[dict]) -> None:
    width, height = 1740, 980
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

    draw.rectangle((0, 0, width, 96), fill=(27, 31, 40))
    draw.text((24, 18), "Source Packet OVERDOSE Transform Control", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"glyph delta {summary['headerGlyphMaxEdgeDeltaVsEqualSlotPx']}px | "
            f"active OVER {summary['activeBlackOverProjectionCount']} projections | "
            f"control matches {summary['p75MirrorVariantMatchCount']}/"
            f"{summary['mirrorVariantCount']} | selectors {summary['selectorUnlockedCount']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Transform checks", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["check", "active", "control", "result"]
    xs = [24, 390, 700, 1000]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(rows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 58), fill=fill)
        draw.text((xs[0], y), row["check"][:42], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["active"][:38], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["control"][:38], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["result"][:82], fill=(70, 70, 70), font=tiny)
        y += 66

    y += 18
    draw.text((24, y), "Mirrored/reversed variants", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["variant", "slots", "active black", "p75 control", "strict hits"]
    xs = [24, 520, 710, 900, 1090]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 24
    for idx, row in enumerate(variants):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 34), fill=fill)
        draw.text((xs[0], y), row["name"][:62], fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["slotLetters"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), row["activeBlackSpan"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), row["p75ControlSpan"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), str(row["strictInstructionHitCount"]), fill=(30, 30, 30), font=tiny)
        y += 40

    img.save(OUT_SHEET, quality=92)


def main() -> None:
    data = {name: load_json(path) for name, path in INPUTS.items()}
    bridge = data["source_packet_native_benchmark_bridge"]
    geom = data["source_packet_geometric_fingerprint"]
    frame = data["source_packet_frame_normalized_geometry"]
    header = data["c9_header_glyph_slot_gate"]
    mirrored = data["c9_mirrored_header_glyph_gate"]
    grey = data["c9_grey_black_over_slot_control"]
    tolerance = data["c9_over_slot_tolerance_gate"]
    review = data["source_packet_source_review_gate"]

    bridge_summary = bridge.get("summary", {})
    geom_summary = geom.get("summary", {})
    frame_summary = frame.get("summary", {})
    header_summary = header.get("summary", {})
    mirrored_summary = mirrored.get("summary", {})
    grey_summary = grey.get("summary", {})
    tolerance_summary = tolerance.get("summary", {})
    review_summary = review.get("summary", {})

    glyphs = [
        row
        for row in bridge.get("rows", [])
        if row.get("kind") == "overdose_glyph"
    ]
    glyphs = sorted(glyphs, key=lambda row: row.get("slotIndex", 0))
    glyph_sequence = "".join(row.get("letter", "") for row in glyphs)
    glyph_widths = [
        round(row.get("uprightBox", [0, 0, 0, 0])[2] - row.get("uprightBox", [0, 0, 0, 0])[0], 3)
        for row in glyphs
    ]

    projection = header.get("projections", [{}])[0] if header.get("projections") else {}
    projection_streams = projection.get("streams", [])
    line_center = stream_by_suffix(projection_streams, "_active_center_line_order")
    x_center = stream_by_suffix(projection_streams, "_active_center_x_order")
    x_span = stream_by_suffix(projection_streams, "_active_span_x_order")
    black_span = stream_by_suffix(projection_streams, "_active_black_span_x_order")
    orange_span = stream_by_suffix(projection_streams, "_active_orange_span_x_order")
    p75_span = stream_by_suffix(projection_streams, "_p75_control_span")

    active_rows = projection.get("activeRows", [])
    active_center_slot_indexes = [row.get("centerSlotIndex") for row in active_rows]
    active_center_slot_letters = [row.get("centerSlotLetter") for row in active_rows]
    active_center_fit = fit_line(
        [float(row.get("centerX", 0.0)) for row in active_rows],
        [float(row.get("centerSlotIndex", 0.0)) for row in active_rows],
    )

    variant_rows = []
    for variant in mirrored.get("variants", []):
        variant_rows.append(
            {
                "name": variant.get("name"),
                "slotLetters": variant.get("slotLetters"),
                "activeBlackSpan": variant.get("activeBlackSpan"),
                "p75ControlSpan": variant.get("p75ControlSpan"),
                "activeControlMatch": variant.get("activeBlackSpan") == variant.get("p75ControlSpan"),
                "strictInstructionHitCount": len(variant.get("strictInstructionHits", [])),
            }
        )
    variant_black_streams = unique([row["activeBlackSpan"] for row in variant_rows])

    rows = [
        {
            "check": "actual glyph boxes projected to C9",
            "active": f"max edge delta {header_summary.get('maxAbsEdgeDeltaVsEqualSlotPx')}px",
            "control": f"header sequence {glyph_sequence}",
            "result": "equivalent to equal-slot geometry; no new transform signal",
        },
        {
            "check": "active center slots, line order",
            "active": f"{line_center.get('stream')} slots {active_center_slot_indexes}",
            "control": "no p75 center instruction stream",
            "result": "not OVER/DOSE and 0 strict instruction hits",
        },
        {
            "check": "active center slots, x order",
            "active": x_center.get("stream"),
            "control": f"fit residual {active_center_fit['maxAbsResidualSlots']} slots",
            "result": "simple x transform bins centers only; no source unit/order",
        },
        {
            "check": "active black span x order",
            "active": black_span.get("stream"),
            "control": p75_span.get("stream"),
            "result": "OVER is controlled by p75 in the same lower-frame geometry",
        },
        {
            "check": "active all-span x order",
            "active": x_span.get("stream"),
            "control": "duplicate/overlap span bins",
            "result": "OVER appears only inside a longer non-instruction stream",
        },
        {
            "check": "orange/yellow span x order",
            "active": orange_span.get("stream"),
            "control": "no strict hits",
            "result": "orange side does not supply a selector",
        },
        {
            "check": "mirror/reversed header variants",
            "active": ",".join(variant_black_streams),
            "control": (
                f"{mirrored_summary.get('p75ControlMatchesActiveBlackCount')}/"
                f"{mirrored_summary.get('variantCount')} match"
            ),
            "result": "p75 tracks active black stream under every tested variant",
        },
        {
            "check": "bounded slot tolerance",
            "active": f"{tolerance_summary.get('activeBlackPairOverCount')}/99 OVER",
            "control": f"{tolerance_summary.get('p75ControlOverCount')}/99 OVER",
            "result": "active fails at high thresholds; control persists at canonical",
        },
        {
            "check": "source-review gate",
            "active": f"{review_summary.get('extractionReadyCount')} ready paths",
            "control": f"R3 fails {review_summary.get('r3FailCount')}",
            "result": "OVERDOSE layout remains validation evidence only",
        },
    ]

    selector_unlocked_count = sum(
        1
        for value in [
            header_summary.get("selectorUnlocked"),
            mirrored_summary.get("selectorUnlocked"),
            grey_summary.get("selectorUnlocked"),
            tolerance_summary.get("selectorUnlocked"),
        ]
        if value
    )
    summary = {
        "glyphSequence": glyph_sequence,
        "glyphWidthRangePx": [min(glyph_widths), max(glyph_widths)] if glyph_widths else [],
        "headerGlyphMaxEdgeDeltaVsEqualSlotPx": header_summary.get("maxAbsEdgeDeltaVsEqualSlotPx"),
        "activeCenterLineOrderStream": line_center.get("stream"),
        "activeCenterXOrderStream": x_center.get("stream"),
        "activeSpanXOrderStream": x_span.get("stream"),
        "activeBlackSpanXOrderStream": black_span.get("stream"),
        "activeOrangeSpanXOrderStream": orange_span.get("stream"),
        "p75ControlSpan": p75_span.get("stream"),
        "activeCenterSlotIndexes": active_center_slot_indexes,
        "activeCenterSlotLetters": "".join(str(v) for v in active_center_slot_letters),
        "activeCenterXToSlotFit": active_center_fit,
        "activeBlackOverProjectionCount": header_summary.get("activeBlackOverProjectionCount"),
        "p75ControlOverProjectionCount": header_summary.get("p75ControlOverProjectionCount"),
        "activeStrictInstructionHitCount": header_summary.get("activeStrictInstructionHitCount"),
        "mirrorVariantCount": mirrored_summary.get("variantCount"),
        "mirrorVariantBlackStreams": variant_black_streams,
        "p75MirrorVariantMatchCount": mirrored_summary.get("p75ControlMatchesActiveBlackCount"),
        "toleranceActiveOverCount": tolerance_summary.get("activeBlackPairOverCount"),
        "toleranceP75OverCount": tolerance_summary.get("p75ControlOverCount"),
        "toleranceBothOverCount": tolerance_summary.get("bothOverCount"),
        "activeOverFailsAtThresholds": tolerance_summary.get("activeOverFailsAtThresholds"),
        "sourceReviewExtractionReadyCount": review_summary.get("extractionReadyCount"),
        "sourceReviewR3FailCount": review_summary.get("r3FailCount"),
        "sourceBackedR3BridgeHitCount": review_summary.get("sourceBackedR3BridgeHitCount"),
        "c9NormalizedCenters": frame_summary.get("c9NormalizedCenterStream"),
        "p78FrameFullInsideCount": frame_summary.get("reflectedP78FullInsideCount"),
        "readableLineCorridorOrder": {
            "pageLines": geom_summary.get("activePageLines"),
            "corridors": geom_summary.get("activeCorridorIndexes"),
            "lineGaps": geom_summary.get("pageLineGaps"),
            "dxSigns": geom_summary.get("dxSignStream"),
            "dySigns": geom_summary.get("dySignStream"),
        },
        "selectorUnlockedCount": selector_unlocked_count,
        "overdoseTransformControlFingerprint": (
            f"glyphDelta={header_summary.get('maxAbsEdgeDeltaVsEqualSlotPx')}"
            f"|center={line_center.get('stream')}/{x_center.get('stream')}"
            f"|black={black_span.get('stream')}"
            f"|p75={p75_span.get('stream')}"
            f"|mirrors={mirrored_summary.get('p75ControlMatchesActiveBlackCount')}/"
            f"{mirrored_summary.get('variantCount')}"
            f"|tol={tolerance_summary.get('activeBlackPairOverCount')}/"
            f"{tolerance_summary.get('p75ControlOverCount')}"
            f"|ready={review_summary.get('extractionReadyCount')}"
            f"|sourceR3={review_summary.get('sourceBackedR3BridgeHitCount')}"
            f"|selectors={selector_unlocked_count}"
        ),
    }

    decision = {
        "sourcePacketOverdoseTransformControl": "controlled_no_selector",
        "selectorUnlocked": False,
        "reason": (
            "Measured OVERDOSE header glyph boxes collapse to the already-tested "
            "equal-slot C9 mapping. Active center streams are not instructions; "
            "the black B4/G5 OVER span is matched by p75 controls across normal, "
            "mirrored, reversed, and tolerance variants."
        ),
        "nextMove": (
            "Keep OVERDOSE geometry as a source-validation guardrail. Reopen only "
            "if a distinct source or clue explicitly names OVERDOSE/header slots "
            "and supplies a unit/order rule that controls do not satisfy."
        ),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "bounded OVERDOSE header glyph transform/control audit; no OCR "
            "extraction, hashes, WIF, seed phrase, address, or key checks"
        ),
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "glyphs": [
            {
                "slotIndex": row.get("slotIndex"),
                "letter": row.get("letter"),
                "uprightBox": row.get("uprightBox"),
                "uprightCenter": row.get("uprightCenter"),
                "nativeBox": row.get("nativeBox"),
            }
            for row in glyphs
        ],
        "projectionRows": rows,
        "mirrorVariantRows": variant_rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet OVERDOSE Transform Control",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Scope: {result['scope']}.",
        "",
        "## Findings",
        "",
        f"- Measured header glyph sequence: `{summary['glyphSequence']}`.",
        (
            "- Actual glyph projection differs from equal C9 slots by at most "
            f"`{summary['headerGlyphMaxEdgeDeltaVsEqualSlotPx']}` px."
        ),
        (
            "- Active center streams remain "
            f"`{summary['activeCenterLineOrderStream']}` line-order and "
            f"`{summary['activeCenterXOrderStream']}` x-order."
        ),
        (
            "- The active black span gives "
            f"`{summary['activeBlackSpanXOrderStream']}`, but p75 control also gives "
            f"`{summary['p75ControlSpan']}`."
        ),
        (
            "- Mirrored/reversed variants tested: "
            f"`{summary['mirrorVariantCount']}`; p75 matched active black in "
            f"`{summary['p75MirrorVariantMatchCount']}` variants."
        ),
        (
            "- Tolerance combinations: active black OVER "
            f"`{summary['toleranceActiveOverCount']}/99`; p75 control OVER "
            f"`{summary['toleranceP75OverCount']}/99`; both "
            f"`{summary['toleranceBothOverCount']}/99`."
        ),
        (
            "- Source-review extraction-ready paths / R3 failures: "
            f"`{summary['sourceReviewExtractionReadyCount']}` / "
            f"`{summary['sourceReviewR3FailCount']}`."
        ),
        (
            "- Fingerprint: "
            f"`{summary['overdoseTransformControlFingerprint']}`."
        ),
        "",
        "## Decision",
        "",
        "- Do not promote OVERDOSE transform/slot geometry as a selector.",
        "- Keep it as a future source-validation guardrail only.",
        "- Reopen only if a distinct source or clue names OVERDOSE/header slots and a unit/order rule that p75 and mirror/tolerance controls fail.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    draw_sheet(summary, rows, variant_rows)

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", summary["overdoseTransformControlFingerprint"])


if __name__ == "__main__":
    main()

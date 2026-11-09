#!/usr/bin/env python3
"""Check repaired p78 frame variants against the active source packet.

This pass is a source-registration residual audit. It measures the current and
dx-repaired reflected p78 frames against the active O4/B4/G5/O5 boxes, using the
recent source-packet bridge as authority. It does not perform OCR, extraction,
hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_repaired_p78_frame_residual"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_repaired_p78_frame_residual.json"
OUT_MD = OUT / "source_packet_repaired_p78_frame_residual.md"
OUT_SHEET = OUT / "source_packet_repaired_p78_frame_residual_sheet.jpg"

NATIVE_BRIDGE = ROOT / "analysis_outputs/source_audit/source_packet_native_benchmark_bridge/source_packet_native_benchmark_bridge.json"
P78_BRIDGE = ROOT / "analysis_outputs/source_audit/p78_frame_source_native_bridge/p78_frame_source_native_bridge.json"
ALIGNMENT = ROOT / "analysis_outputs/source_audit/source_packet_alignment_tolerance/source_packet_alignment_tolerance.json"
COLOR_PROFILE = ROOT / "analysis_outputs/source_audit/source_packet_color_profile_manifest/source_packet_color_profile_manifest.json"
UPRIGHT_PAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def quick_font(size: int = 24) -> ImageFont.ImageFont:
    for name in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "Arial.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float]:
    return [max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])]


def overlap_fraction(target: list[float], frame: list[float]) -> float:
    return area(intersection(target, frame)) / max(1.0, area(target))


def gap_to_frame(target: list[float], frame: list[float]) -> dict[str, float]:
    return {
        "leftPx": round(max(0.0, frame[0] - target[2]), 3),
        "rightPx": round(max(0.0, target[0] - frame[2]), 3),
        "topPx": round(max(0.0, frame[1] - target[3]), 3),
        "bottomPx": round(max(0.0, target[1] - frame[3]), 3),
    }


def expansion_to_include(targets: list[dict[str, Any]], frame: list[float]) -> dict[str, float]:
    boxes = [row["uprightBox"] for row in targets]
    return {
        "leftPx": round(max(0.0, frame[0] - min(box[0] for box in boxes)), 3),
        "topPx": round(max(0.0, frame[1] - min(box[1] for box in boxes)), 3),
        "rightPx": round(max(0.0, max(box[2] for box in boxes) - frame[2]), 3),
        "bottomPx": round(max(0.0, max(box[3] for box in boxes) - frame[3]), 3),
    }


def classify_frame(targets: list[dict[str, Any]], frame: list[float]) -> list[dict[str, Any]]:
    rows = []
    for target in targets:
        target_box = target["uprightBox"]
        frac = overlap_fraction(target_box, frame)
        rows.append(
            {
                "id": target["id"],
                "label": target["label"],
                "visualState": target.get("visualState"),
                "pageLine": target.get("pageLine"),
                "corridorIndex": target.get("corridorIndex"),
                "targetBox": target_box,
                "overlapFraction": round(frac, 6),
                "partialHit": frac > 0,
                "strongPartialHit": frac >= 0.2,
                "fullInsideFrame": frac >= 0.999,
                "gapToFrame": gap_to_frame(target_box, frame),
            }
        )
    return rows


def make_sheet(targets: list[dict[str, Any]], frame_rows: list[dict[str, Any]]) -> None:
    img = Image.open(UPRIGHT_PAGE).convert("RGB")
    crop_box = [220, 2075, 2310, 3065]
    crop = img.crop(tuple(crop_box))
    draw = ImageDraw.Draw(crop)
    font = quick_font(22)
    small = quick_font(18)

    target_colors = {"Y": (245, 134, 36), "K": (35, 35, 35)}
    for target in targets:
        box = [int(round(v - crop_box[i % 2])) for i, v in enumerate(target["uprightBox"])]
        color = target_colors.get(target.get("visualState"), (40, 120, 240))
        draw.rectangle(box, outline=color, width=5)
        label = f"{target['id']} {target.get('visualState')} L{target.get('pageLine')}/C{target.get('corridorIndex')}"
        draw.text((box[0], max(0, box[1] - 24)), label, fill=color, font=small)

    for frame in frame_rows:
        color_hex = frame["color"].lstrip("#")
        color = tuple(int(color_hex[i : i + 2], 16) for i in (0, 2, 4))
        box = [int(round(v - crop_box[i % 2])) for i, v in enumerate(frame["p76ReflectedUprightBox"])]
        draw.rectangle(box, outline=color, width=4)
        full = frame["summary"]["fullInsideCount"]
        partial = frame["summary"]["partialHitCount"]
        strong = frame["summary"]["strongPartialHitCount"]
        text = f"{frame['name']} full={full}/4 partial={partial}/4 strong={strong}/4"
        draw.text((box[0] + 8, max(0, box[1] + 8)), text, fill=color, font=font)

    header = Image.new("RGB", (crop.width, 92), (248, 248, 248))
    hdraw = ImageDraw.Draw(header)
    hdraw.text((18, 16), "Source-packet repaired p78 frame residual", fill=(20, 20, 20), font=quick_font(26))
    hdraw.text(
        (18, 54),
        "Current, dx=-38, and dx=-40 reflected p78 frames over active O4/B4/G5/O5 targets",
        fill=(55, 55, 55),
        font=small,
    )
    sheet = Image.new("RGB", (crop.width, header.height + crop.height), "white")
    sheet.paste(header, (0, 0))
    sheet.paste(crop, (0, header.height))
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    native = load_json(NATIVE_BRIDGE)
    p78 = load_json(P78_BRIDGE)
    alignment = load_json(ALIGNMENT)
    color_profile = load_json(COLOR_PROFILE)

    targets = [row for row in native["rows"] if row.get("kind") == "active_target"]
    frame_rows = []
    for frame in p78["rows"]:
        p76_frame = frame["p76ReflectedUprightBox"]
        target_rows = classify_frame(targets, p76_frame)
        expansion = expansion_to_include(targets, p76_frame)
        summary = {
            "fullInsideCount": sum(1 for row in target_rows if row["fullInsideFrame"]),
            "partialHitCount": sum(1 for row in target_rows if row["partialHit"]),
            "strongPartialHitCount": sum(1 for row in target_rows if row["strongPartialHit"]),
            "coveredTargetIds": [row["id"] for row in target_rows if row["partialHit"]],
            "fullInsideTargetIds": [row["id"] for row in target_rows if row["fullInsideFrame"]],
            "strongPartialTargetIds": [row["id"] for row in target_rows if row["strongPartialHit"]],
            "expansionToCoverAllTargetsPx": expansion,
            "leftExpansionNeededForB4Px": next(row["gapToFrame"]["leftPx"] for row in target_rows if row["id"] == "one_billion"),
            "topExpansionNeededForO4Px": next(row["gapToFrame"]["topPx"] for row in target_rows if row["id"] == "buying_dip"),
            "g5OverlapFraction": next(row["overlapFraction"] for row in target_rows if row["id"] == "volcano_bonds"),
            "g5HorizontalGapPx": next(row["gapToFrame"]["leftPx"] for row in target_rows if row["id"] == "volcano_bonds"),
            "o5OverlapFraction": next(row["overlapFraction"] for row in target_rows if row["id"] == "shitcoiner_heart"),
            "selectorUnlocked": False,
        }
        frame_rows.append(
            {
                "name": frame["name"],
                "label": frame["label"],
                "dx": frame["dx"],
                "dy": frame["dy"],
                "color": frame["color"],
                "p76ReflectedUprightBox": p76_frame,
                "p76NativeBox": frame["p76NativeBox"],
                "targetRows": target_rows,
                "summary": summary,
            }
        )

    best_g5 = min(frame_rows, key=lambda row: row["summary"]["g5HorizontalGapPx"])
    best_o5 = max(frame_rows, key=lambda row: row["summary"]["o5OverlapFraction"])
    max_partial = max(row["summary"]["partialHitCount"] for row in frame_rows)
    max_full = max(row["summary"]["fullInsideCount"] for row in frame_rows)
    repaired_dx_rows = [row for row in frame_rows if row["name"] != "current"]
    min_repaired_b4_touch_left = min(row["summary"]["leftExpansionNeededForB4Px"] for row in repaired_dx_rows)
    min_repaired_o4_touch_top = min(row["summary"]["topExpansionNeededForO4Px"] for row in repaired_dx_rows)
    min_repaired_full_left = min(
        row["summary"]["expansionToCoverAllTargetsPx"]["leftPx"] for row in repaired_dx_rows
    )
    min_repaired_full_top = min(
        row["summary"]["expansionToCoverAllTargetsPx"]["topPx"] for row in repaired_dx_rows
    )
    common_shift = alignment.get("summary", {}).get("commonFullEightDirectionShiftAllTargetsPassPx")
    fingerprint = (
        f"frames=current,-38,-40|maxFull={max_full}|maxPartial={max_partial}|"
        f"bestG5Gap={best_g5['name']}:{best_g5['summary']['g5HorizontalGapPx']}|"
        f"bestO5Overlap={best_o5['name']}:{best_o5['summary']['o5OverlapFraction']}|"
        f"minRepairedB4TouchLeft={min_repaired_b4_touch_left}|"
        f"minRepairedB4FullLeft={min_repaired_full_left}|"
        f"minRepairedO4TouchTop={min_repaired_o4_touch_top}|"
        f"minRepairedO4FullTop={min_repaired_full_top}"
    )

    make_sheet(targets, frame_rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "source-packet repaired p78 frame residual audit; no OCR, extraction, "
            "key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation"
        ),
        "inputs": {
            "nativeBenchmarkBridge": str(NATIVE_BRIDGE.relative_to(ROOT)),
            "p78FrameSourceNativeBridge": str(P78_BRIDGE.relative_to(ROOT)),
            "alignmentTolerance": str(ALIGNMENT.relative_to(ROOT)),
            "colorProfileManifest": str(COLOR_PROFILE.relative_to(ROOT)),
            "uprightImage": str(UPRIGHT_PAGE.relative_to(ROOT)),
        },
        "activeOrder": [row["id"] for row in targets],
        "activeVisualStateOrder": "".join(row.get("visualState", "") for row in targets),
        "activePageLines": " ".join(str(row.get("pageLine")) for row in targets),
        "activeCorridorIndexes": " ".join(str(row.get("corridorIndex")) for row in targets),
        "sourcePacketColorFingerprint": color_profile.get("summary", {}).get("colorProfileFingerprint"),
        "commonShiftTolerancePx": common_shift,
        "frameRows": frame_rows,
        "summary": {
            "frameVariantCount": len(frame_rows),
            "maxFullInsideCount": max_full,
            "maxPartialHitCount": max_partial,
            "bestG5GapFrame": best_g5["name"],
            "bestG5HorizontalGapPx": best_g5["summary"]["g5HorizontalGapPx"],
            "bestO5OverlapFrame": best_o5["name"],
            "bestO5OverlapFraction": best_o5["summary"]["o5OverlapFraction"],
            "minimumRepairedB4TouchLeftExpansionPx": min_repaired_b4_touch_left,
            "minimumRepairedB4FullLeftExpansionPx": min_repaired_full_left,
            "minimumRepairedO4TouchTopExpansionPx": min_repaired_o4_touch_top,
            "minimumRepairedO4FullTopExpansionPx": min_repaired_full_top,
            "commonShiftTolerancePx": common_shift,
            "frameResidualFingerprint": fingerprint,
            "selectorUnlocked": False,
        },
        "decision": {
            "sourcePacketRepairedP78FrameResidual": "source-registration-only",
            "reason": (
                "The dx=-38/-40 repaired reflected p78 frames improve the G5 edge contact and O5 clip benchmark, "
                "but no frame variant fully contains any active target set beyond partial contacts, B4 remains hundreds "
                "of pixels outside, and O4 still needs a large top expansion. This is a source-comparison residual, not an extraction selector."
            ),
        },
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "nextMove": (
            "Use repaired-frame residuals only as future physical/original-layout comparison metrics. "
            "Do not reopen p78 frame, fold/mirror, OVERDOSE, or highlight extraction without source-backed R3 unit/order wording."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Repaired P78 Frame Residual",
        "",
        "Scope: measure current and dx-repaired reflected p78 frame variants against the active O4/B4/G5/O5 source-packet boxes. No OCR, extraction, key derivation, hashing, seed/WIF/address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active order: `{' -> '.join(result['activeOrder'])}`",
        f"- Active visual-state order: `{result['activeVisualStateOrder']}`",
        f"- Active page lines: `{result['activePageLines']}`",
        f"- Active corridor indexes: `{result['activeCorridorIndexes']}`",
        f"- Common source-packet all-direction shift tolerance: `{common_shift}px`",
        f"- Max full-inside active count across frames: `{max_full}/4`",
        f"- Max partial-hit active count across frames: `{max_partial}/4`",
        f"- Best G5 horizontal gap: `{best_g5['name']}` at `{best_g5['summary']['g5HorizontalGapPx']}px`",
        f"- Best O5 overlap: `{best_o5['name']}` at `{best_o5['summary']['o5OverlapFraction']}` of target area",
        f"- Minimum repaired-frame B4 left expansion to touch/full-cover: `{min_repaired_b4_touch_left}px` / `{min_repaired_full_left}px`",
        f"- Minimum repaired-frame O4 top expansion to touch/full-cover: `{min_repaired_o4_touch_top}px` / `{min_repaired_full_top}px`",
        f"- Frame residual fingerprint: `{fingerprint}`",
        f"- Sheet: `{OUT_SHEET.relative_to(ROOT)}`",
        "",
        "## Frame Residuals",
        "",
        "| frame | dx | full inside | partial hits | strong partial hits | G5 gap | G5 overlap | O5 overlap | B4 left touch/full | O4 top touch/full |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in frame_rows:
        s = row["summary"]
        lines.append(
            f"| `{row['name']}` | `{row['dx']}` | `{s['fullInsideCount']}/4` | `{s['partialHitCount']}/4` | `{s['strongPartialHitCount']}/4` | `{s['g5HorizontalGapPx']}` | `{s['g5OverlapFraction']}` | `{s['o5OverlapFraction']}` | `{s['leftExpansionNeededForB4Px']}/{s['expansionToCoverAllTargetsPx']['leftPx']}` | `{s['topExpansionNeededForO4Px']}/{s['expansionToCoverAllTargetsPx']['topPx']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep this as source-registration evidence only.",
            "- The repaired dx variants improve the G5 edge/near-edge benchmark and slightly improve O5 clipping, but they still do not fully contain the active quartet.",
            "- B4 remains far outside the repaired p78 frame and O4 still requires a large top expansion, so this does not reopen folded/mirrored p78 geometry as a selector.",
            "- The result is useful for future physical/original-layout comparison; extraction remains blocked until source-backed unit/order wording appears.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("frameResidualFingerprint:", fingerprint)
    print("selectorUnlocked:", result["summary"]["selectorUnlocked"])


if __name__ == "__main__":
    main()

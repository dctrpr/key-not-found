#!/usr/bin/env python3
"""Control-test the tempting Y/K filter inside the O4 rescue frame.

The signal-stream gate found that the full-coverage frame contains eight styled
groups (`YBKKBMMY`). Filtering that stream to only Y/K groups isolates the active
quartet, but this pass checks whether that is genuine selector evidence or just
the intersection of two already-known target-location predicates.

No OCR, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SIGNAL_GATE_JSON = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_signal_stream_gate/o4_frame_rescue_signal_stream_gate.json"
FONT_ORDER_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_corridor_font_order_audit.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "o4_frame_rescue_yk_filter_control.json"
OUT_MD = OUT / "o4_frame_rescue_yk_filter_control.md"
SHEET = OUT / "o4_frame_rescue_yk_filter_control_sheet.jpg"


ACTIVE_TARGET_IDS = {"buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"}
HARD_INSTRUCTION_TERMS = [
    "address",
    "above",
    "below",
    "edge",
    "extract",
    "font",
    "fold",
    "frame",
    "key",
    "left",
    "letter",
    "line",
    "mirror",
    "private",
    "read",
    "right",
    "seed",
    "select",
    "take",
    "word",
]


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


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+", text)


def term_hits(text: str) -> list[str]:
    normalized = " ".join(tokens(text)).lower()
    return [term for term in HARD_INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", normalized)]


def target_by_group(font_order: dict[str, Any]) -> dict[int, str]:
    by_group = {}
    for target_row in font_order.get("targetMatches", []):
        target_id = target_row.get("targetId")
        for match in target_row.get("matches", []):
            by_group[int(match["groupIndex"])] = target_id
    return by_group


def make_group_rows(font_order: dict[str, Any]) -> list[dict[str, Any]]:
    codes = font_order["streams"]["p76SignalLayerCodes"]
    group_to_target = target_by_group(font_order)
    rows = []
    for idx, group in enumerate(font_order["p76SignalGroups"], start=1):
        text = group["text"]
        target_id = group_to_target.get(idx)
        rows.append(
            {
                "groupIndex": idx,
                "layerCode": codes[idx - 1],
                "text": text,
                "targetId": target_id,
                "isActiveTarget": target_id in ACTIVE_TARGET_IDS,
                "hardInstructionHits": term_hits(text),
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    active = [row for row in rows if row["isActiveTarget"]]
    non_active = [row for row in rows if not row["isActiveTarget"]]
    hard_hits = sorted({hit for row in rows for hit in row["hardInstructionHits"]})
    return {
        "groupCount": len(rows),
        "activeGroupCount": len(active),
        "nonActiveGroupCount": len(non_active),
        "layerCodes": "".join(row["layerCode"] for row in rows),
        "targetIds": [row["targetId"] or "-" for row in rows],
        "texts": [row["text"] for row in rows],
        "nonActiveTexts": [row["text"] for row in non_active],
        "hardInstructionHits": hard_hits,
        "hardInstructionHitCount": len(hard_hits),
        "activeTargetCoverage": sorted(row["targetId"] for row in active),
        "allActiveTargetsCovered": {row["targetId"] for row in active} == ACTIVE_TARGET_IDS,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    crop = [180, 2070, 2315, 3065]
    scale = 0.42
    panel = Image.open(PAGE_IMAGE).convert("RGB").crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    margin = 28
    header_h = 120
    footer_h = 440
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + footer_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 20), "O4 Frame Rescue Y/K Filter Control", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 56),
        "Tests whether Y/K inside the rescue frame is a rule or a target-color restatement.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text((margin, 84), "Pink = frame. Y/K within frame isolates 4/4; Y/K on full page does not.", fill=(176, 186, 198), font=small)
    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    frame = result["fullCoverageFrame"]
    draw.rectangle([sx(frame[0]), sy(frame[1]), sx(frame[2]), sy(frame[3])], outline="#ff73c8", width=4)

    y = header_h + panel.size[1] + 24
    draw.text((margin, y), "Y/K Filter Results", fill=(238, 243, 248), font=normal)
    y += 30
    notes = [
        f"Frame stream: {result['summary']['frameSignalLayerCodes']} -> Y/K only {result['summary']['frameYkLayerCodes']}.",
        f"Frame Y/K covers active targets: {result['summary']['frameYkActiveGroupCount']}/4; non-active in frame Y/K: {result['summary']['frameYkNonActiveGroupCount']}.",
        f"Full-page Y/K groups: {result['summary']['fullPageYkGroupCount']}; non-active full-page Y/K groups: {result['summary']['fullPageYkNonActiveGroupCount']}.",
        f"Full-page non-active Y/K: {', '.join(result['summary']['fullPageYkNonActiveTexts'])}.",
        f"Hard instruction hits across Y/K control streams: {result['summary']['hardInstructionHitCount']}.",
        "Result: Y/K+frame is a useful validation intersection, not source-backed extraction permission.",
    ]
    for note in notes:
        draw.text((margin, y), note[:120], fill=(255, 219, 137), font=normal)
        y += 25

    y += 12
    draw.text((margin, y), "Frame Y/K Groups", fill=(238, 243, 248), font=normal)
    y += 26
    for row in result["frameYkGroups"]:
        draw.text((margin, y), f"{row['groupIndex']:02d} {row['layerCode']} {row['targetId'] or '-':<18} {row['text'][:76]}", fill="#ffdd7d", font=mono)
        y += 22

    y += 12
    draw.text((margin, y), "Full-Page Y/K Control Adds", fill=(238, 243, 248), font=normal)
    y += 26
    for row in result["fullPageYkNonActiveGroups"]:
        draw.text((margin, y), f"{row['groupIndex']:02d} {row['layerCode']} {row['targetId'] or '-':<18} {row['text'][:76]}", fill="#c6d1df", font=mono)
        y += 22

    sheet.save(SHEET, quality=94)


def main() -> None:
    signal_gate = load_json(SIGNAL_GATE_JSON)
    font_order = load_json(FONT_ORDER_JSON)
    all_groups = make_group_rows(font_order)
    full_page_yk = [row for row in all_groups if row["layerCode"] in {"Y", "K"}]
    frame_group_indexes = {row["groupIndex"] for row in signal_gate["frameSignalGroups"]}
    frame_groups = [row for row in all_groups if row["groupIndex"] in frame_group_indexes]
    frame_yk = [row for row in frame_groups if row["layerCode"] in {"Y", "K"}]
    full_page_yk_non_active = [row for row in full_page_yk if not row["isActiveTarget"]]

    full_page_summary = summarize(full_page_yk)
    frame_summary = summarize(frame_groups)
    frame_yk_summary = summarize(frame_yk)
    hard_hits = sorted(
        set(full_page_summary["hardInstructionHits"])
        | set(frame_summary["hardInstructionHits"])
        | set(frame_yk_summary["hardInstructionHits"])
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Y/K filter control for the O4 frame-rescue signal stream; no OCR, key derivation, hashing, WIF, seed, or address checks",
        "inputs": {
            "signalStreamGate": rel(SIGNAL_GATE_JSON),
            "fontOrderAudit": rel(FONT_ORDER_JSON),
        },
        "fullCoverageFrame": signal_gate["fullCoverageFrame"],
        "fullPageYkGroups": full_page_yk,
        "fullPageYkNonActiveGroups": full_page_yk_non_active,
        "frameSignalGroups": frame_groups,
        "frameYkGroups": frame_yk,
        "summaries": {
            "fullPageYk": full_page_summary,
            "frameSignal": frame_summary,
            "frameYk": frame_yk_summary,
        },
        "summary": {
            "fullPageSignalLayerCodes": "".join(row["layerCode"] for row in all_groups),
            "fullPageYkGroupCount": len(full_page_yk),
            "fullPageYkLayerCodes": full_page_summary["layerCodes"],
            "fullPageYkActiveGroupCount": full_page_summary["activeGroupCount"],
            "fullPageYkNonActiveGroupCount": full_page_summary["nonActiveGroupCount"],
            "fullPageYkNonActiveTexts": full_page_summary["nonActiveTexts"],
            "frameSignalGroupCount": len(frame_groups),
            "frameSignalLayerCodes": frame_summary["layerCodes"],
            "frameYkGroupCount": len(frame_yk),
            "frameYkLayerCodes": frame_yk_summary["layerCodes"],
            "frameYkActiveGroupCount": frame_yk_summary["activeGroupCount"],
            "frameYkNonActiveGroupCount": frame_yk_summary["nonActiveGroupCount"],
            "frameYkActiveTargetCoverage": frame_yk_summary["activeTargetCoverage"],
            "frameYkAllActiveTargetsCovered": frame_yk_summary["allActiveTargetsCovered"],
            "hardInstructionHits": hard_hits,
            "hardInstructionHitCount": len(hard_hits),
            "selectorUnlocked": False,
        },
        "decision": {
            "o4FrameRescueYkFilterControl": "isolates_active_quartet_but_source_permission_missing",
            "selectorUnlocked": False,
            "reason": "Y/K inside the rescue frame isolates the active quartet, but Y/K on the full page has four non-active control groups and no source wording names the Y/K+frame intersection as an extraction rule.",
            "nextMove": "Keep Y/K+frame as a source-validation benchmark only; reopen only if source wording names orange/black, Y/K, highlighted colors, or frame-intersection filtering.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# O4 Frame Rescue Y/K Filter Control",
        "",
        "Scope: control-test the tempting `Y/K` filter inside the `3-up / 1-down` rescue frame. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Full-page signal layer codes: `{result['summary']['fullPageSignalLayerCodes']}`",
        f"- Full-page Y/K group count: `{result['summary']['fullPageYkGroupCount']}`",
        f"- Full-page Y/K layer codes: `{result['summary']['fullPageYkLayerCodes']}`",
        f"- Full-page Y/K non-active groups: `{result['summary']['fullPageYkNonActiveGroupCount']}`",
        f"- Frame signal layer codes: `{result['summary']['frameSignalLayerCodes']}`",
        f"- Frame Y/K layer codes: `{result['summary']['frameYkLayerCodes']}`",
        f"- Frame Y/K active target coverage: `{len(result['summary']['frameYkActiveTargetCoverage'])}/4`",
        f"- Frame Y/K non-active groups: `{result['summary']['frameYkNonActiveGroupCount']}`",
        f"- Hard instruction hits: `{hard_hits}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Frame Y/K Groups",
        "",
        "| group | code | active target | hard hits | text |",
        "|---:|---|---|---|---|",
    ]
    for row in frame_yk:
        lines.append(
            f"| `{row['groupIndex']}` | `{row['layerCode']}` | `{row['targetId'] or '-'}` | `{', '.join(row['hardInstructionHits']) or '-'}` | {row['text']} |"
        )

    lines.extend(["", "## Full-Page Y/K Control", "", "| group | code | target | active? | text |", "|---:|---|---|---|---|"])
    for row in full_page_yk:
        lines.append(
            f"| `{row['groupIndex']}` | `{row['layerCode']}` | `{row['targetId'] or '-'}` | `{row['isActiveTarget']}` | {row['text']} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `Y/K` inside the rescue frame isolates the four active targets.",
            "- This is not enough to unlock extraction because full-page `Y/K` has four non-active controls: `Get some toxicity...`, `Gotta be this way...`, `by the rancid catnip...`, and `It's a stun gun...`.",
            "- The `Y/K + frame` intersection has no hard instruction hits and no source-backed permission.",
            "- Treat it as a source-validation benchmark only, not current-scan key material.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("frameYkLayerCodes:", result["summary"]["frameYkLayerCodes"])
    print("frameYkActiveTargetCoverage:", len(result["summary"]["frameYkActiveTargetCoverage"]), "/ 4")
    print("fullPageYkNonActiveGroupCount:", result["summary"]["fullPageYkNonActiveGroupCount"])
    print("hardInstructionHitCount:", len(hard_hits))
    print("selectorUnlocked:", False)


if __name__ == "__main__":
    main()

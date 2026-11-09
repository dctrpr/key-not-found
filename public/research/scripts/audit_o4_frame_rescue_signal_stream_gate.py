#!/usr/bin/env python3
"""Check the styled signal stream inside the 3-up/1-down rescue frame.

The raw content gate showed that the full-coverage frame is too broad. This
pass asks whether the existing page-76 font/highlight signal stream narrows the
same frame enough to become a selector.

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
CONTENT_GATE_JSON = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_content_gate/o4_frame_rescue_content_gate.json"
FONT_ORDER_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_corridor_font_order_audit.json"
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/o4_frame_rescue_signal_stream_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "o4_frame_rescue_signal_stream_gate.json"
OUT_MD = OUT / "o4_frame_rescue_signal_stream_gate.md"
SHEET = OUT / "o4_frame_rescue_signal_stream_gate_sheet.jpg"


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


def normalize(text: str) -> str:
    return " ".join(tokens(text)).lower()


def first_initial(text: str) -> str:
    parts = tokens(text)
    return parts[0][0] if parts else ""


def last_initial(text: str) -> str:
    parts = tokens(text)
    return parts[-1][-1] if parts else ""


def letters_only(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z0-9]", text))


def term_hits(text: str) -> list[str]:
    normalized = normalize(text)
    return [term for term in HARD_INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", normalized)]


def select_frame_groups(content_gate: dict[str, Any], font_order: dict[str, Any]) -> list[dict[str, Any]]:
    included_text = " ".join(row["text"] for row in content_gate["includedLines"])
    included_norm = normalize(included_text)
    layer_codes = font_order["streams"]["p76SignalLayerCodes"]
    active_group_to_target = {
        match["groupIndex"]: row["targetId"]
        for row in font_order.get("targetMatches", [])
        if row.get("targetId") in {"buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"}
        for match in row.get("matches", [])
    }

    frame_groups = []
    for idx, group in enumerate(font_order["p76SignalGroups"], start=1):
        text = group["text"]
        group_norm = normalize(text)
        if not group_norm or group_norm not in included_norm:
            continue
        target_id = active_group_to_target.get(idx)
        frame_groups.append(
            {
                "groupIndex": idx,
                "layerCode": layer_codes[idx - 1],
                "text": text,
                "letters": group.get("letters") or letters_only(text),
                "initial": first_initial(text),
                "lastInitial": last_initial(text),
                "length": len(letters_only(text)),
                "lengthMod10": len(letters_only(text)) % 10,
                "targetId": target_id,
                "isActiveTarget": target_id is not None,
                "hardInstructionHits": term_hits(text),
            }
        )
    return frame_groups


def draw_sheet(result: dict[str, Any]) -> None:
    crop = [180, 2070, 2315, 3065]
    scale = 0.43
    panel = Image.open(PAGE_IMAGE).convert("RGB").crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    margin = 28
    header_h = 126
    footer_h = 430
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + footer_h + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(27)
    normal = font(16)
    small = font(12)
    mono = font(13)

    draw.text((margin, 20), "O4 Frame Rescue Signal Stream Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 58),
        "Checks whether styled groups inside the 3-up/1-down frame isolate the active quartet.",
        fill=(176, 186, 198),
        font=normal,
    )
    draw.text(
        (margin, 86),
        "Pink = full-coverage frame. Rows below use the existing page-76 font/highlight signal order.",
        fill=(176, 186, 198),
        font=small,
    )
    sheet.paste(panel, (margin, header_h))

    def sx(v: float) -> float:
        return margin + (v - crop[0]) * scale

    def sy(v: float) -> float:
        return header_h + (v - crop[1]) * scale

    frame = result["fullCoverageFrame"]
    draw.rectangle([sx(frame[0]), sy(frame[1]), sx(frame[2]), sy(frame[3])], outline="#ff73c8", width=4)

    y = header_h + panel.size[1] + 24
    draw.text((margin, y), "Signal Stream", fill=(238, 243, 248), font=normal)
    y += 28
    draw.text((margin, y), "idx code target text", fill=(129, 143, 158), font=small)
    y += 20
    for row in result["frameSignalGroups"]:
        color = "#ffdd7d" if row["isActiveTarget"] else "#c6d1df"
        target = row["targetId"] or "-"
        text = row["text"][:76]
        draw.text((margin, y), f"{row['groupIndex']:02d}  {row['layerCode']}   {target:<18} {text}", fill=color, font=mono)
        y += 22

    y += 18
    draw.text((margin, y), "Summary", fill=(238, 243, 248), font=normal)
    y += 28
    notes = [
        f"Frame signal codes: {result['summary']['frameLayerCodes']}; active-only: {result['summary']['activeLayerCodes']}.",
        f"Signal groups: {result['summary']['frameSignalGroupCount']} total, {result['summary']['activeSignalGroupCount']} active, {result['summary']['nonActiveSignalGroupCount']} non-active.",
        f"Non-active group texts: {', '.join(result['summary']['nonActiveSignalTexts'])}.",
        f"Hard instruction hits: {result['summary']['hardInstructionHitCount']}.",
        "Result: styled stream still mixes active targets with context, so no selector is unlocked.",
    ]
    for note in notes:
        draw.text((margin, y), note[:120], fill=(255, 219, 137), font=normal)
        y += 25

    sheet.save(SHEET, quality=94)


def main() -> None:
    content_gate = load_json(CONTENT_GATE_JSON)
    font_order = load_json(FONT_ORDER_JSON)
    active = load_json(ACTIVE_JSON)
    groups = select_frame_groups(content_gate, font_order)
    active_groups = [row for row in groups if row["isActiveTarget"]]
    non_active_groups = [row for row in groups if not row["isActiveTarget"]]
    hard_hits = sorted({hit for row in groups for hit in row["hardInstructionHits"]})

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "styled signal stream inside 3-up/1-down O4 frame-rescue envelope; no OCR, key derivation, hashing, WIF, seed, or address checks",
        "inputs": {
            "contentGate": rel(CONTENT_GATE_JSON),
            "fontOrderAudit": rel(FONT_ORDER_JSON),
            "activeTargets": rel(ACTIVE_JSON),
        },
        "fullCoverageFrame": content_gate["fullCoverageFrame"],
        "activeTargets": [
            {"id": target["id"], "phrase": target["phrase"], "visualState": target["visualState"]}
            for target in active["targets"]
        ],
        "frameSignalGroups": groups,
        "streams": {
            "frameLayerCodes": "".join(row["layerCode"] for row in groups),
            "frameInitials": "".join(row["initial"] for row in groups),
            "frameLastInitials": "".join(row["lastInitial"] for row in groups),
            "frameLengthMod10": "".join(str(row["lengthMod10"]) for row in groups),
            "activeLayerCodes": "".join(row["layerCode"] for row in active_groups),
            "activeInitials": "".join(row["initial"] for row in active_groups),
            "activeLastInitials": "".join(row["lastInitial"] for row in active_groups),
            "nonActiveLayerCodes": "".join(row["layerCode"] for row in non_active_groups),
            "nonActiveInitials": "".join(row["initial"] for row in non_active_groups),
            "nonActiveLastInitials": "".join(row["lastInitial"] for row in non_active_groups),
        },
        "summary": {
            "frameSignalGroupCount": len(groups),
            "activeSignalGroupCount": len(active_groups),
            "nonActiveSignalGroupCount": len(non_active_groups),
            "frameLayerCodes": "".join(row["layerCode"] for row in groups),
            "activeLayerCodes": "".join(row["layerCode"] for row in active_groups),
            "nonActiveLayerCodes": "".join(row["layerCode"] for row in non_active_groups),
            "nonActiveSignalTexts": [row["text"] for row in non_active_groups],
            "hardInstructionHits": hard_hits,
            "hardInstructionHitCount": len(hard_hits),
            "selectorUnlocked": False,
        },
        "decision": {
            "o4FrameRescueSignalStreamGate": "fails_isolation_selector",
            "selectorUnlocked": False,
            "reason": "The styled stream inside the full-coverage frame is YBKKBMMY: it contains the active YKKY quartet but also four non-active styled groups, with zero hard instruction hits.",
            "nextMove": "Keep the styled stream as source-validation/context only; reopen only if source wording names a style-layer filter or exact group order.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# O4 Frame Rescue Signal Stream Gate",
        "",
        "Scope: check whether the existing page-76 styled signal stream inside the `3-up / 1-down` frame isolates the active quartet. No OCR, key derivation, hashing, WIF, seed, address checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Full-coverage frame: `{result['fullCoverageFrame']}`",
        f"- Frame signal groups: `{result['summary']['frameSignalGroupCount']}`",
        f"- Active signal groups: `{result['summary']['activeSignalGroupCount']}`",
        f"- Non-active signal groups: `{result['summary']['nonActiveSignalGroupCount']}`",
        f"- Frame layer codes: `{result['summary']['frameLayerCodes']}`",
        f"- Active layer codes: `{result['summary']['activeLayerCodes']}`",
        f"- Non-active layer codes: `{result['summary']['nonActiveLayerCodes']}`",
        f"- Hard instruction hits: `{hard_hits}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Frame Signal Groups",
        "",
        "| group | code | active target | initials | length mod 10 | hard hits | text |",
        "|---:|---|---|---|---:|---|---|",
    ]
    for row in groups:
        lines.append(
            f"| `{row['groupIndex']}` | `{row['layerCode']}` | `{row['targetId'] or '-'}` | `{row['initial']}{row['lastInitial']}` | `{row['lengthMod10']}` | `{', '.join(row['hardInstructionHits']) or '-'}` | {row['text']} |"
        )

    lines.extend(
        [
            "",
            "## Streams",
            "",
        ]
    )
    for name, value in result["streams"].items():
        lines.append(f"- `{name}`: `{value}`")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The frame's styled stream is compact, but it is not clean: `YBKKBMMY` includes the active `YKKY` quartet plus four non-active styled groups.",
            "- The non-active groups are `President Nayib Bukele`, `IMF loan`, `Mike Novogratz`, and `I don't really trust that guy.`.",
            "- The styled-group streams produce zero hard instruction hits.",
            "- Treat the styled stream as source-validation/context only, not a current-scan selector.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("frameLayerCodes:", result["summary"]["frameLayerCodes"])
    print("activeLayerCodes:", result["summary"]["activeLayerCodes"])
    print("nonActiveSignalGroupCount:", result["summary"]["nonActiveSignalGroupCount"])
    print("hardInstructionHitCount:", len(hard_hits))
    print("selectorUnlocked:", False)


if __name__ == "__main__":
    main()

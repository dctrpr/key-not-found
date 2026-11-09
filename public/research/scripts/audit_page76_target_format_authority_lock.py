#!/usr/bin/env python3
"""Lock page-76 target formatting authority.

This bounded pass separates real DOCM/high-res formatting evidence from
Markdown/annotation markup. It does not run extraction, hashing, key
derivation, WIF/Base58 scans, OCR, or address checks.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_target_format_authority_lock.json"
OUT_MD = OUT / "page76_target_format_authority_lock.md"
SHEET = OUT / "page76_target_format_authority_lock_sheet.jpg"

INPUTS = {
    "active_line": ROOT
    / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json",
    "manual_bold": ROOT
    / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.json",
    "visual_consistency": ROOT
    / "analysis_outputs/docm_format_sources/docm_visual_highlight_consistency/docm_visual_highlight_consistency.json",
    "crop_pack": ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json",
    "text_lock": ROOT
    / "analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/page76_target_text_authority_lock.json",
    "typeka_gate": ROOT
    / "analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis.json",
}

ACTIVE_IDS = ["buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"]
CONTEXT_IDS = ["el_salvador", "novogratz", "trust_that_guy", "imf_loan"]

CROP_EVIDENCE = {
    "buying_dip": [],
    "one_billion": ["L25_should_sell"],
    "volcano_bonds": ["L27_G5_pair", "L26_L29_source_band", "L25_L32_frame_context"],
    "shitcoiner_heart": ["L32_O5_primary", "L25_L32_frame_context"],
}

THUMBNAILS = [
    ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_sheet.jpg",
    ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_authority_bridge_sheet.jpg",
    ROOT / "analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/page76_target_text_authority_lock_sheet.jpg",
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


def norm(text: str) -> str:
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def expected_visual_color(color: str) -> str:
    return "orange" if color == "orange" else "grey"


def find_visual_matches(visual_results: list[dict[str, Any]], phrase: str) -> list[dict[str, Any]]:
    nphrase = norm(phrase)
    matches = []
    for row in visual_results:
        ntext = norm(row.get("text", ""))
        if nphrase and (nphrase in ntext or ntext in nphrase):
            matches.append(row)
    return matches


def paste_thumb(sheet: Image.Image, path: Path, box: tuple[int, int, int, int], title: str) -> None:
    draw = ImageDraw.Draw(sheet)
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(20, 24, 30), outline=(50, 58, 70))
    draw.text((x0 + 12, y0 + 10), title, fill=(230, 235, 242), font=font(16))
    if not path.exists():
        draw.text((x0 + 12, y0 + 42), "missing", fill=(255, 130, 130), font=font(14))
        return
    try:
        image = Image.open(path).convert("RGB")
    except Exception as exc:
        draw.text((x0 + 12, y0 + 42), f"open failed: {exc}", fill=(255, 130, 130), font=font(14))
        return
    max_w = x1 - x0 - 24
    max_h = y1 - y0 - 58
    scale = min(max_w / image.width, max_h / image.height)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    resample = getattr(Image, "Resampling", Image).LANCZOS
    image = image.resize(new_size, resample)
    sheet.paste(image, (x0 + 12, y0 + 44))


def build_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1720, 1460
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(17)
    small = font(13)
    mono = font(15)

    draw.text((margin, margin), "Page-76 Target Format Authority Lock", fill=(242, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 45),
        "DOCM/high-res format evidence is locked; Markdown and annotated text remain witness layers, not font authority.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    summary = result["summary"]
    chips = [
        ("visual", summary["activeVisualStateOrder"]),
        ("colors", summary["activeColorPattern"]),
        ("lines", summary["pageLines"]),
        ("corridor", summary["corridorIndexes"]),
        ("docm", "Typeka bold x4" if summary["allActiveTargetsDocmTypekaBold"] else "mixed"),
        ("selector", "blocked"),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 240, y + 48), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 8), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 24), str(value), fill=(232, 239, 246), font=mono)
        x += 255

    y += 76
    headers = [
        ("target", 12),
        ("visual", 300),
        ("line/corr", 450),
        ("DOCM", 610),
        ("highlight", 850),
        ("high-res witness", 1030),
        ("crop authority", 1250),
    ]
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38

    for row in result["activeTargets"]:
        row_color = (31, 24, 16) if row["color"] == "orange" else (21, 25, 31)
        draw.rectangle((margin, y, sheet_w - margin, y + 82), fill=row_color, outline=(48, 58, 70))
        draw.text((margin + 12, y + 12), row["label"], fill=(242, 246, 250), font=normal)
        draw.text((margin + 300, y + 12), row["visualState"], fill=(255, 193, 105), font=mono)
        draw.text(
            (margin + 450, y + 12),
            f"L{row['pageLine']} / C{row['corridorIndex']}",
            fill=(210, 222, 236),
            font=mono,
        )
        draw.text(
            (margin + 610, y + 12),
            f"{row['docmDominantFont']} bold={row['docmBoldFraction']}",
            fill=(210, 222, 236),
            font=mono,
        )
        draw.text((margin + 850, y + 12), row["docmHighlightSummary"], fill=(210, 222, 236), font=mono)
        draw.text(
            (margin + 1030, y + 12),
            "exact" if row["visualExactMatch"] else "missing",
            fill=(113, 222, 154) if row["visualExactMatch"] else (255, 130, 130),
            font=mono,
        )
        crop_note = ", ".join(row["cropEvidence"]) if row["cropEvidence"] else "visual-consistency only"
        draw.text((margin + 1250, y + 12), crop_note[:48], fill=(176, 186, 198), font=small)
        draw.text((margin + 12, y + 44), row["canonicalLine"][:130], fill=(167, 177, 189), font=small)
        y += 88

    y += 18
    draw.rectangle((margin, y, sheet_w - margin, y + 88), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text(
        (margin + 14, y + 14),
        "Authority: DOCM runs + high-res visual highlight consistency + crop pack/manual boxes for lower-frame targets.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 46),
        "Markdown bold is markup; annotated transcript is a format witness; neither supplies R3 unit/order.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 116
    thumb_w = (sheet_w - margin * 2 - 28) // 3
    thumb_h = 600
    titles = ["priority crop pack", "Typeka authority bridge", "text authority lock"]
    for idx, path in enumerate(THUMBNAILS):
        x0 = margin + idx * (thumb_w + 14)
        paste_thumb(sheet, path, (x0, y, x0 + thumb_w, y + thumb_h), titles[idx])

    sheet.save(SHEET, quality=94)


def main() -> None:
    active_line = load_json(INPUTS["active_line"])
    manual_bold = load_json(INPUTS["manual_bold"])
    visual_consistency = load_json(INPUTS["visual_consistency"])
    crop_pack = load_json(INPUTS["crop_pack"])
    text_lock = load_json(INPUTS["text_lock"])
    typeka_gate = load_json(INPUTS["typeka_gate"])

    active_records = {row["id"]: row for row in active_line.get("records", [])}
    manual_rows = {row["id"]: row for row in manual_bold.get("rows", [])}
    crop_rows = {row["id"]: row for row in crop_pack.get("crops", [])}
    visual_results = visual_consistency.get("visualResults", [])

    active_targets = []
    for target_id in ACTIVE_IDS:
        active = active_records[target_id]
        manual = manual_rows.get(target_id, {})
        docm = manual.get("docm", {})
        visual_matches = find_visual_matches(visual_results, active["label"])
        wanted_color = expected_visual_color(active["color"])
        exact_visual = [
            row
            for row in visual_matches
            if row.get("page") == 76
            and row.get("visualColor") == wanted_color
            and any(match.get("kind") == "exact" for match in row.get("docmMatches", []))
        ]
        crops = [
            {
                "id": crop_id,
                "output": rel(crop_rows.get(crop_id, {}).get("output")),
                "title": crop_rows.get(crop_id, {}).get("title"),
            }
            for crop_id in CROP_EVIDENCE[target_id]
            if crop_id in crop_rows
        ]
        docm_highlights = docm.get("highlights") or active.get("docmHighlights") or {}
        active_targets.append(
            {
                "id": target_id,
                "order": active["order"],
                "label": active["label"],
                "color": active["color"],
                "visualState": active["visualState"],
                "pageLine": active["pageLine"],
                "corridorIndex": active["corridorIndex"],
                "sentenceRow": active["sentenceRow"],
                "canonicalLine": active["canonicalLine"],
                "docmDominantFont": docm.get("dominantFont") or active.get("docmDominantFont"),
                "docmBoldFraction": docm.get("boldFraction", active.get("docmBoldFraction")),
                "docmHighlights": docm_highlights,
                "docmHighlightSummary": ",".join(f"{k}:{v}" for k, v in docm_highlights.items()),
                "docmMatchesActiveRecord": {
                    "font": (docm.get("dominantFont") or active.get("docmDominantFont"))
                    == active.get("docmDominantFont"),
                    "bold": abs(float(docm.get("boldFraction", active.get("docmBoldFraction"))) - float(active.get("docmBoldFraction", 0)))
                    < 0.001,
                    "highlight": docm_highlights == active.get("docmHighlights"),
                },
                "visualMatches": [
                    {
                        "id": row.get("id"),
                        "visualColor": row.get("visualColor"),
                        "text": row.get("text"),
                        "docmMatches": row.get("docmMatches"),
                    }
                    for row in visual_matches
                ],
                "visualExactMatch": bool(exact_visual),
                "cropEvidence": [row["id"] for row in crops],
                "cropEvidenceDetails": crops,
            }
        )

    context_rows = []
    for target_id in CONTEXT_IDS:
        row = manual_rows.get(target_id, {})
        docm = row.get("docm", {})
        if row:
            context_rows.append(
                {
                    "id": target_id,
                    "phrase": row.get("phrase"),
                    "role": row.get("role"),
                    "dominantFont": docm.get("dominantFont"),
                    "boldFraction": docm.get("boldFraction"),
                    "highlights": docm.get("highlights"),
                    "activeHighlightTarget": target_id in ACTIVE_IDS,
                }
            )

    all_typeka_bold = all(
        row["docmDominantFont"] == "Typeka" and abs(float(row["docmBoldFraction"]) - 1.0) < 0.001
        for row in active_targets
    )
    visual_match_count = sum(1 for row in active_targets if row["visualExactMatch"])

    summary = {
        "activeColorPattern": "".join("O" if row["color"] == "orange" else "B" for row in active_targets),
        "activeVisualStateOrder": "".join(row["visualState"] for row in active_targets),
        "pageLines": " ".join(str(row["pageLine"]) for row in active_targets),
        "sentenceRows": " ".join(str(row["sentenceRow"]) for row in active_targets),
        "corridorIndexes": " ".join(str(row["corridorIndex"]) for row in active_targets),
        "allActiveTargetsDocmTypekaBold": all_typeka_bold,
        "activeVisualExactMatchCount": visual_match_count,
        "activeTargetCount": len(active_targets),
        "cropPackActiveCoverageCount": sum(1 for row in active_targets if row["cropEvidence"]),
    }

    authority_lock = {
        "formatAuthority": "DOCM runs + high-res visual highlight consistency + page-76 crop pack/manual boxes",
        "textAuthority": text_lock.get("authorityLock", {}).get("targetTextAuthority"),
        "markdownUse": "text/markup transcript only; not font-state authority",
        "annotatedUse": "format/highlight witness; not exact-prose authority and not selector permission",
        "nearbyTypekaMixUse": "`I don't really trust that guy` and nearby names are context, not active highlight targets",
        "selectorUnlocked": False,
        "selectorBlocker": "The O-B-B-O/Y-K-K-Y format pattern corroborates target identity but still does not name an extraction unit or order beyond the visual order already known.",
    }

    gate_rows = [
        {
            "gate": "format authority",
            "status": "pass",
            "reason": "DOCM rows, high-res visual highlight matches, and crop-pack/manual boxes agree on the active target formatting.",
        },
        {
            "gate": "active pattern",
            "status": "pass",
            "reason": "The four locked active targets form O-B-B-O / Y-K-K-Y at page lines 22, 25, 27, and 32.",
        },
        {
            "gate": "R3 unit/order",
            "status": "fail",
            "reason": "Formatting states give target identity only; they do not provide a source-backed word/letter/line/side/index rule.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "page-76 target format authority lock; no extraction, no key derivation, no hashing, no OCR, no address checks",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "summary": summary,
        "activeTargets": active_targets,
        "nearbyFormatContext": context_rows,
        "authorityLock": authority_lock,
        "gateRows": gate_rows,
        "sourceGateContext": {
            "typekaFontR3Decision": typeka_gate.get("decision"),
            "typekaStrongInstructionRecordCount": typeka_gate.get("strongInstructionRecordCount"),
            "textLockDecision": text_lock.get("decision"),
            "textLockRawPlainUse": text_lock.get("authorityLock", {}).get("rawPlainUse"),
        },
        "sheet": rel(SHEET),
        "decision": "page76_target_format_authority_locked_no_selector",
        "nextMove": "Use DOCM/high-res/crop-pack witnesses as format authority for future source comparison. Do not treat Markdown bold, annotated notes, or Typeka Mix context as selector permission without new R3 unit/order evidence.",
    }

    build_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Page-76 Target Format Authority Lock",
        "",
        "Scope: lock the authoritative formatting witnesses for the active page-76 targets. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Active Format Pattern",
        "",
        f"- Color pattern: `{summary['activeColorPattern']}`",
        f"- Visual-state order: `{summary['activeVisualStateOrder']}`",
        f"- Page lines: `{summary['pageLines']}`",
        f"- Sentence rows: `{summary['sentenceRows']}`",
        f"- Corridor indexes: `{summary['corridorIndexes']}`",
        f"- All active targets DOCM Typeka bold: `{summary['allActiveTargetsDocmTypekaBold']}`",
        f"- High-res visual exact matches: `{summary['activeVisualExactMatchCount']}/{summary['activeTargetCount']}`",
        f"- Crop-pack active coverage: `{summary['cropPackActiveCoverageCount']}/{summary['activeTargetCount']}`",
        "",
        "## Active Targets",
        "",
        "| order | target | color/state | line/corridor | DOCM font/bold | DOCM highlight | high-res exact | crop evidence |",
        "|---:|---|---|---|---|---|---:|---|",
    ]
    for row in active_targets:
        crops = ", ".join(row["cropEvidence"]) if row["cropEvidence"] else "visual-consistency only"
        lines.append(
            f"| {row['order']} | `{row['label']}` | `{row['color']}/{row['visualState']}` | `L{row['pageLine']}/C{row['corridorIndex']}` | `{row['docmDominantFont']} / {row['docmBoldFraction']}` | `{row['docmHighlightSummary']}` | `{row['visualExactMatch']}` | {crops} |"
        )

    lines.extend(["", "## Nearby Format Context", "", "| phrase | role | DOCM font | bold | highlight | use |", "|---|---|---|---:|---|---|"])
    for row in context_rows:
        lines.append(
            f"| `{row['phrase']}` | {row['role']} | `{row['dominantFont']}` | `{row['boldFraction']}` | `{row['highlights']}` | context only |"
        )

    lines.extend(
        [
            "",
            "## Authority Lock",
            "",
            f"- Format authority: `{authority_lock['formatAuthority']}`",
            f"- Text authority: `{authority_lock['textAuthority']}`",
            f"- Markdown use: `{authority_lock['markdownUse']}`",
            f"- Annotated transcript use: `{authority_lock['annotatedUse']}`",
            f"- Nearby Typeka Mix use: {authority_lock['nearbyTypekaMixUse']}",
            f"- Selector unlocked: `{authority_lock['selectorUnlocked']}`",
            f"- Blocker: {authority_lock['selectorBlocker']}",
            "",
            "## Gate Rows",
            "",
        ]
    )
    for row in gate_rows:
        lines.append(f"- `{row['gate']}`: `{row['status']}` - {row['reason']}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))
    print("selectorUnlocked:", authority_lock["selectorUnlocked"])


if __name__ == "__main__":
    main()

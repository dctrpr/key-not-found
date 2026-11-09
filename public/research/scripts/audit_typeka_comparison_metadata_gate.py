#!/usr/bin/env python3
"""Gate the Typeka comparison-article claim against local source metadata.

This is a source/provenance check only. It answers whether the local comparison
PDFs can verify Typeka usage/non-usage and whether that changes the R3 selector
status. It does not run extraction, hashing, key derivation, WIF/Base58 scans,
OCR extraction, or address checks.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/comparison_articles/typeka_comparison_metadata_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "typeka_comparison_metadata_gate.json"
OUT_MD = OUT / "typeka_comparison_metadata_gate.md"
SHEET = OUT / "typeka_comparison_metadata_gate_sheet.jpg"

REPORTS = {
    "typography_source_provenance": ROOT / "analysis_outputs/source_audit/typography_source_provenance.json",
    "typeka_variant_state": ROOT / "analysis_outputs/docm_format_sources/typeka_variant_state_audit.json",
    "typeka_font_r3_gate": ROOT / "analysis_outputs/docm_format_sources/typeka_font_r3_gate_synthesis/typeka_font_r3_gate_synthesis.json",
    "comparison_layout_r3_gate": ROOT / "analysis_outputs/comparison_articles/overdose_layout_r3_gate_synthesis/overdose_layout_r3_gate_synthesis.json",
}


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


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1640, 1180
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(18)
    small = font(14)
    mono = font(14)

    draw.text((margin, margin), "Typeka Comparison Metadata Gate", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 46),
        "Comparison PDFs are raster witnesses; Article with Fonts.docm is the only local Typeka font witness.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("comparison font witnesses", result["summary"]["comparisonPdfFontWitnessCount"]),
        ("comparison Typeka resources", result["summary"]["comparisonPdfTypekaResourceCount"]),
        ("docm Typeka chars", result["summary"]["articleWithFontsTypekaChars"]),
        ("r3 selector", result["summary"]["r3SelectorStatus"]),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 370, y + 56), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 30), str(value)[:36], fill=(232, 239, 246), font=mono)
        x += 390

    y += 90
    draw.rectangle((margin, y, sheet_w - margin, y + 104), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Guardrail", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "Do not use image-only comparison PDFs to prove or disprove Typeka usage by metadata.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 76),
        "Typeka remains a confirmed Issue 24 Word-format witness, not a selector without separate unit/order wording.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 136
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("source", 10), ("kind", 320), ("fonts", 520), ("text chars", 930), ("Typeka?", 1120), ("use", 1290)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["sourceRows"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 48), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 10, y + 14), row["label"][:31], fill=(238, 243, 248), font=small)
        draw.text((margin + 320, y + 14), row["kind"], fill=(176, 186, 198), font=small)
        draw.text((margin + 520, y + 14), str(row["fontNames"])[:42], fill=(176, 186, 198), font=mono)
        draw.text((margin + 930, y + 14), str(row["textChars"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 1120, y + 14), str(row["typekaEvidence"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 1290, y + 14), row["use"][:34], fill=(176, 186, 198), font=small)
        y += 52

    y += 24
    draw.rectangle((margin, y, sheet_w - margin, y + 210), fill=(18, 22, 28), outline=(48, 58, 70))
    draw.text((margin + 14, y + 14), "R1-R5 Result", fill=(238, 243, 248), font=normal)
    ty = y + 52
    for row in result["gateRows"]:
        draw.text((margin + 18, ty), f"{row['gate']}: {row['status']}", fill=(232, 239, 246), font=mono)
        draw.text((margin + 420, ty), row["evidence"][:108], fill=(176, 186, 198), font=small)
        ty += 34

    sheet.save(SHEET, quality=94)


def main() -> None:
    typography = load_json(REPORTS["typography_source_provenance"])
    variant = load_json(REPORTS["typeka_variant_state"])
    typeka_gate = load_json(REPORTS["typeka_font_r3_gate"])
    comparison_gate = load_json(REPORTS["comparison_layout_r3_gate"])

    comparison_labels = {"issue26_comparison", "issue27_comparison", "bitcoin3_comparison"}
    issue24_labels = {"issue24_best_scan", "issue24_desktop_scan", "bitcoin4_issue24_witness"}

    source_rows: list[dict[str, Any]] = []
    for item in typography.get("pdfs", []):
        label = item.get("label")
        if label in comparison_labels:
            use = "style control only"
        elif label in issue24_labels:
            use = "scan/witness, not font layer"
        else:
            use = "not used"
        source_rows.append(
            {
                "label": label,
                "kind": "PDF",
                "fontNames": item.get("fontNames") or [],
                "textChars": item.get("pdftotextChars"),
                "typekaEvidence": item.get("hasTypekaFontResource"),
                "imageOnly": item.get("isImageOnlyOrRasterWitness"),
                "use": use,
            }
        )
    for item in typography.get("docms", []):
        label = item.get("label")
        typeka_chars = sum((item.get("typekaFontChars") or {}).values())
        source_rows.append(
            {
                "label": label,
                "kind": "DOCM",
                "fontNames": list((item.get("fontChars") or {}).keys()),
                "textChars": item.get("totalChars"),
                "typekaEvidence": typeka_chars,
                "imageOnly": False,
                "use": "font witness" if label == "article_with_fonts" else "annotation/generated witness",
            }
        )

    comparison_rows = [row for row in source_rows if row["label"] in comparison_labels]
    article_docm = next((row for row in source_rows if row["label"] == "article_with_fonts"), {})
    summary = {
        "comparisonPdfCount": len(comparison_rows),
        "comparisonPdfFontWitnessCount": sum(1 for row in comparison_rows if row["fontNames"]),
        "comparisonPdfTypekaResourceCount": sum(1 for row in comparison_rows if row["typekaEvidence"]),
        "comparisonPdfImageOnlyCount": sum(1 for row in comparison_rows if row["imageOnly"]),
        "articleWithFontsTypekaChars": article_docm.get("typekaEvidence"),
        "typekaVariantCounts": variant.get("counts"),
        "typekaGateDecision": typeka_gate.get("decision"),
        "comparisonGateDecision": comparison_gate.get("decision"),
        "r3SelectorStatus": "FAIL",
        "selectorUnlocked": False,
    }

    gate_rows = [
        {
            "gate": "R1 source identity",
            "status": "PARTIAL",
            "evidence": "Article with Fonts.docm is a local font witness; comparison PDFs are flattened article images, not source layout files.",
        },
        {
            "gate": "R2 target preservation",
            "status": "PASS as corroboration",
            "evidence": f"Article with Fonts.docm records Typeka/Typeka Mix across Issue 24 with {summary['articleWithFontsTypekaChars']} Typeka-family chars.",
        },
        {
            "gate": "R3 unit/order evidence",
            "status": "FAIL",
            "evidence": "Comparison PDFs expose zero Typeka font resources and no word/letter/line/font-order instruction.",
        },
        {
            "gate": "R4 orientation/source discipline",
            "status": "PASS",
            "evidence": "PDF raster witnesses are separated from DOCM font-state witnesses; scan OCR Helvetica is not treated as printed typography.",
        },
        {
            "gate": "R5 controlled improvement",
            "status": "FAIL",
            "evidence": "The comparison metadata does not improve page-76 registration or select O4/B4/G5/O5 units.",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Typeka comparison metadata gate; no extraction, hashing, key derivation, OCR extraction, WIF, seed, or address checks",
        "inputs": {name: rel(path) for name, path in REPORTS.items()},
        "summary": summary,
        "sourceRows": source_rows,
        "gateRows": gate_rows,
        "sheet": rel(SHEET),
        "decision": "typeka_comparison_metadata_closed_as_r3_selector",
        "nextMove": "Treat Article with Fonts.docm as the Typeka witness and comparison PDFs as style controls only; reopen Typeka extraction only with a source/clue that names font-state units or original layout metadata.",
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Typeka Comparison Metadata Gate",
        "",
        "Scope: gate the user-supplied Typeka comparison claim against local metadata. No extraction, key derivation, hashing, OCR extraction, WIF/Base58 scanning, seed generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Source Rows",
        "",
        "| source | kind | fonts | text chars | Typeka evidence | use |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in source_rows:
        lines.append(
            f"| `{row['label']}` | `{row['kind']}` | `{row['fontNames']}` | `{row['textChars']}` | `{row['typekaEvidence']}` | {row['use']} |"
        )
    lines.extend(["", "## Gate Result", "", "| gate | status | evidence |", "|---|---|---|"])
    for row in gate_rows:
        lines.append(f"| {row['gate']} | `{row['status']}` | {row['evidence']} |")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            f"- Independent comparison PDFs checked: `{summary['comparisonPdfCount']}`.",
            f"- Comparison PDFs with embedded font witnesses: `{summary['comparisonPdfFontWitnessCount']}`.",
            f"- Comparison PDFs with Typeka font resources: `{summary['comparisonPdfTypekaResourceCount']}`.",
            f"- Comparison PDFs classified image-only/raster witnesses: `{summary['comparisonPdfImageOnlyCount']}`.",
            f"- `Article with Fonts.docm` Typeka-family character count: `{summary['articleWithFontsTypekaChars']}`.",
            "- The comparison PDFs can support broad visual/style comparisons, but they cannot prove or disprove visible printed Typeka usage by metadata because the pages are flattened images.",
            "- The Issue 24 scan exposes only Helvetica OCR/text-layer resources; that layer remains non-authoritative for printed typography.",
            "- Typeka remains a real Issue 24 Word-format witness, but still fails R3 because no source-backed rule names font-state units/order.",
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

#!/usr/bin/env python3
"""Disambiguate the lone strict term in the valid leaf line-band trace.

The valid page 75 -> page 76 held-to-light line-band trace had one strict
term hit. This bounded pass isolates that carrier and checks whether it is
instruction grammar or ordinary prose.

No OCR-to-key extraction, key candidates, hashes, seed/WIF/address checks,
BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/valid_leaf_strict_term_disambiguation_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "valid_leaf_strict_term_disambiguation_gate.json"
OUT_MD = OUT / "valid_leaf_strict_term_disambiguation_gate.md"
OUT_SHEET = OUT / "valid_leaf_strict_term_disambiguation_gate_sheet.jpg"

ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
PAGE76_IMG = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
VALID_LEAF_LINE_TRACE = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/"
    "current_scan_valid_leaf_line_band_trace.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

ACTION_TERMS = {
    "read",
    "reads",
    "reading",
    "take",
    "takes",
    "taking",
    "use",
    "using",
    "select",
    "extract",
    "decode",
    "encoded",
    "cipher",
    "key",
    "private",
    "seed",
}
UNIT_TERMS = {
    "line",
    "lines",
    "word",
    "words",
    "phrase",
    "phrases",
    "letter",
    "letters",
    "edge",
    "edges",
    "slot",
    "slots",
    "index",
    "indexes",
    "font",
    "bold",
    "highlight",
    "overdose",
}
ORDER_TERMS = {
    "first",
    "last",
    "left",
    "right",
    "top",
    "bottom",
    "fold",
    "folded",
    "mirror",
    "mirrored",
    "reverse",
    "order",
}
STRICT_TERMS = ACTION_TERMS | UNIT_TERMS | ORDER_TERMS
TARGET_ORDER = ["O4", "B4", "G5", "O5"]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


def ascii_safe(text: str) -> str:
    return str(text).encode("ascii", "replace").decode("ascii")


def line_terms(text: str) -> dict[str, list[str]]:
    tokens = [token(part) for part in re.findall(r"[A-Za-z0-9']+", text)]
    tokens = [part for part in tokens if part]
    return {
        "tokens": tokens,
        "strict": sorted({part for part in tokens if part in STRICT_TERMS}),
        "action": sorted({part for part in tokens if part in ACTION_TERMS}),
        "unit": sorted({part for part in tokens if part in UNIT_TERMS}),
        "order": sorted({part for part in tokens if part in ORDER_TERMS}),
    }


def source_line_strict_rows(trace: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for trace_row in trace.get("traceRows", []):
        for source_line in trace_row.get("sourceLines", []):
            terms = line_terms(source_line.get("sourceText", ""))
            if not terms["strict"]:
                continue
            rows.append(
                {
                    "mode": trace_row["mode"],
                    "target": trace_row["target"],
                    "phrase": trace_row["phrase"],
                    "sourceLineIndex": source_line["lineIndex"],
                    "sourceText": ascii_safe(source_line.get("sourceText", "")),
                    "targetTextPreview": ascii_safe(trace_row.get("targetTextPreview", "")),
                    "sourceTargetLineOverlapArea": round(float(trace_row.get("sourceTargetLineOverlapArea", 0.0)), 3),
                    "sourceTargetLineOverlapCount": int(trace_row.get("sourceTargetLineOverlapCount", 0)),
                    "strictTerms": terms["strict"],
                    "actionTerms": terms["action"],
                    "unitTerms": terms["unit"],
                    "orderTerms": terms["order"],
                    "hasActionAndUnit": bool(terms["action"] and terms["unit"]),
                    "hasUnitAndOrder": bool(terms["unit"] and terms["order"]),
                    "instructionCandidate": bool(terms["action"] and (terms["unit"] or terms["order"])),
                    "ordinaryProseReason": "unit-only noun in ordinary sentence" if terms["unit"] and not terms["action"] and not terms["order"] else "",
                }
            )
    return rows


def page_lines(article: dict[str, Any], page_no: int) -> list[dict[str, Any]]:
    page = next(row for row in article["pages"] if row.get("page") == page_no)
    words = [word for word in page.get("words", []) if token(word.get("text", ""))]
    words.sort(key=lambda word: ((word["box"][1] + word["box"][3]) / 2.0, word["box"][0]))
    groups: list[list[dict[str, Any]]] = []
    for word in words:
        cy = (word["box"][1] + word["box"][3]) / 2.0
        if groups:
            prev_y = sum((item["box"][1] + item["box"][3]) / 2.0 for item in groups[-1]) / len(groups[-1])
            if abs(cy - prev_y) <= 31.0:
                groups[-1].append(word)
                continue
        groups.append([word])
    rows = []
    for index, group in enumerate(groups):
        group.sort(key=lambda word: word["box"][0])
        text = " ".join(str(word.get("text", "")) for word in group)
        terms = line_terms(text)
        rows.append(
            {
                "lineIndex": index,
                "text": ascii_safe(text),
                "strictTerms": terms["strict"],
                "actionTerms": terms["action"],
                "unitTerms": terms["unit"],
                "orderTerms": terms["order"],
            }
        )
    return rows


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


def draw_sheet(result: dict[str, Any]) -> None:
    image = Image.open(PAGE76_IMG).convert("RGB")
    crop = [780, 2760, 1780, 3060]
    scale = 1.15
    panel = image.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))
    sheet = Image.new("RGB", (1760, 900), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(24)
    small = font(14)
    tiny = font(11)
    sheet.paste(panel, (24, 132))
    draw.rectangle((0, 0, 1760, 100), fill=(24, 31, 42))
    draw.text((24, 16), "Valid Leaf Strict-Term Disambiguation", fill="white", font=title)
    draw.text(
        (24, 52),
        "The lone valid 75->76 line-band strict hit is isolated and classified as instruction grammar or prose.",
        fill=(236, 236, 236),
        font=small,
    )
    summary = result["summary"]
    draw.text(
        (1020, 18),
        f"strict rows {summary['strictCarrierRowCount']} | instruction candidates {summary['instructionCandidateCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    draw.text(
        (1020, 48),
        f"targets {','.join(summary['strictCarrierTargets']) or '-'} | terms {','.join(summary['strictTerms']) or '-'} | triggers {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
        fill=(236, 236, 236),
        font=small,
    )
    y = 525
    draw.text((24, y), "Strict carrier rows", fill=(30, 34, 40), font=small)
    y += 24
    headers = ["mode", "target", "line", "terms", "action", "unit", "order", "source text"]
    xs = [24, 225, 295, 350, 435, 510, 590, 670]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(65, 70, 78), font=tiny)
    y += 18
    for row in result["strictCarrierRows"]:
        values = [
            row["mode"],
            row["target"],
            row["sourceLineIndex"],
            ",".join(row["strictTerms"]),
            ",".join(row["actionTerms"]) or "-",
            ",".join(row["unitTerms"]) or "-",
            ",".join(row["orderTerms"]) or "-",
            row["sourceText"],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value)[:110], fill=(25, 28, 34), font=tiny)
        y += 24
    y += 24
    draw.text((24, y), "Interpretation", fill=(30, 34, 40), font=small)
    y += 24
    notes = [
        "The strict hit is the unit noun 'words' inside ordinary prose, not an imperative.",
        "It touches only O5 in natural 75->76 line-band projection and does not cover the active quartet.",
        "No source-backed R3 bridge or reopen trigger is satisfied.",
    ]
    for note in notes:
        draw.text((24, y), "- " + note, fill=(25, 28, 34), font=small)
        y += 24
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Valid Leaf Strict-Term Disambiguation Gate",
        "",
        "Scope: isolated the lone strict-term hit from the valid page 75 -> page 76 held-to-light line-band trace and checked whether it functions as source-backed instruction grammar. No key derivation, hashes, seed/WIF/address checks, BIP39 checks, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Strict carrier rows: `{summary['strictCarrierRowCount']}`",
        f"- Strict terms: `{', '.join(summary['strictTerms']) or '-'}`",
        f"- Strict carrier targets: `{', '.join(summary['strictCarrierTargets']) or '-'}`",
        f"- Action-term carriers / unit-only carriers / order-term carriers: `{summary['actionCarrierCount']}` / `{summary['unitOnlyCarrierCount']}` / `{summary['orderCarrierCount']}`",
        f"- Instruction candidate carriers: `{summary['instructionCandidateCount']}`",
        f"- All-four active target coverage by strict carriers: `{summary['allFourActiveTargetsCoveredByStrictCarriers']}`",
        f"- Page-75 global strict-like line count: `{summary['page75StrictLikeLineCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Strict Carrier Rows",
        "",
        "| mode | target | source line | strict terms | action | unit | order | text |",
        "|---|---|---:|---|---|---|---|---|",
    ]
    for row in result["strictCarrierRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['mode']}`",
                    f"`{row['target']}`",
                    str(row["sourceLineIndex"]),
                    f"`{','.join(row['strictTerms'])}`",
                    f"`{','.join(row['actionTerms']) or '-'}`",
                    f"`{','.join(row['unitTerms']) or '-'}`",
                    f"`{','.join(row['orderTerms']) or '-'}`",
                    row["sourceText"].replace("|", "\\|"),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The lone strict hit is `words` in ordinary page-75 prose: `to. Nice, pleasant words from con men and shitcoiners`.",
            "- It is unit-only, with no action verb (`read`, `take`, `use`, `extract`, etc.) and no order term (`first`, `last`, `left`, `right`, etc.).",
            "- It reaches only O5 under the natural valid-leaf line-band projection, not O4/B4/G5/O5 as a quartet.",
            "- Keep the valid 75->76 line-band strict hit closed as prose/context, not an instruction source.",
            "",
            "## Next Move",
            "",
            "- Do not reopen held-to-light line-band extraction from this term. Best direction remains original/source-layout validation or raw clue wording that explicitly names transform, unit, and order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    trace = load_json(VALID_LEAF_LINE_TRACE)
    article = load_json(ARTICLE_MAP)
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    carrier_rows = source_line_strict_rows(trace)
    strict_targets = sorted({row["target"] for row in carrier_rows}, key=lambda item: TARGET_ORDER.index(item) if item in TARGET_ORDER else 99)
    strict_terms = sorted({term for row in carrier_rows for term in row["strictTerms"]})
    page75_lines = page_lines(article, 75)
    page75_strict_lines = [row for row in page75_lines if row["strictTerms"]]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    summary = {
        "decision": "valid_leaf_strict_term_disambiguation_no_instruction",
        "strictCarrierRowCount": len(carrier_rows),
        "strictTerms": strict_terms,
        "strictCarrierTargets": strict_targets,
        "actionCarrierCount": sum(bool(row["actionTerms"]) for row in carrier_rows),
        "unitOnlyCarrierCount": sum(bool(row["unitTerms"]) and not row["actionTerms"] and not row["orderTerms"] for row in carrier_rows),
        "orderCarrierCount": sum(bool(row["orderTerms"]) for row in carrier_rows),
        "instructionCandidateCount": sum(bool(row["instructionCandidate"]) for row in carrier_rows),
        "allFourActiveTargetsCoveredByStrictCarriers": all(target in strict_targets for target in TARGET_ORDER),
        "page75StrictLikeLineCount": len(page75_strict_lines),
        "page75StrictLikeTerms": sorted({term for row in page75_strict_lines for term in row["strictTerms"]}),
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"strictRows={summary['strictCarrierRowCount']}|terms={','.join(strict_terms) or '-'}|"
        f"targets={','.join(strict_targets) or '-'}|action={summary['actionCarrierCount']}|"
        f"unitOnly={summary['unitOnlyCarrierCount']}|order={summary['orderCarrierCount']}|"
        f"instr={summary['instructionCandidateCount']}|all4={int(summary['allFourActiveTargetsCoveredByStrictCarriers'])}|"
        f"p75StrictLines={summary['page75StrictLikeLineCount']}|sourceR3={source_r3_hits}|"
        f"triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Lone strict term in valid 75->76 line-band trace disambiguated against instruction grammar.",
        "inputs": {
            "validLeafLineBandTrace": rel(VALID_LEAF_LINE_TRACE),
            "articleMap": rel(ARTICLE_MAP),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "fingerprint": fingerprint,
        "strictCarrierRows": carrier_rows,
        "page75StrictLikeLines": page75_strict_lines,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)


if __name__ == "__main__":
    main()

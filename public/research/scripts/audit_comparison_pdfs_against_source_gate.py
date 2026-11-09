#!/usr/bin/env python3
"""Apply the source-validation gate to comparison PDFs.

This is a source-routing audit. It decides whether local comparison PDFs can
change Issue 24 extraction geometry, or whether they must remain style/fidelity
witnesses. It does not perform OCR, key derivation, hashing, WIF, seed, or
address checks.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/comparison_pdf_source_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "comparison_pdf_source_gate.json"
OUT_MD = OUT / "comparison_pdf_source_gate.md"

INVENTORY_JSON = ROOT / "analysis_outputs/source_audit/local_source_candidate_inventory/local_source_candidate_inventory.json"
BODY_GRAMMAR_JSON = ROOT / "analysis_outputs/comparison_articles/body_highlighter_grammar/body_highlighter_grammar.json"
BITCOIN4_WITNESS_JSON = ROOT / "analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness/bitcoin4_issue24_geometry_witness.json"
BITCOIN4_CROPS_JSON = ROOT / "analysis_outputs/source_audit/priority_crops_bitcoin4_comparison/priority_crops_bitcoin4_comparison.json"
SOURCE_GATE_JSON = ROOT / "analysis_outputs/source_audit/source_validation_gate/source_validation_gate.json"

TARGETS = ["bitcoin3.pdf", "Issue_26.pdf", "Issue_27.pdf", "bitcoin4.pdf"]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find_record(inventory: dict, name: str) -> dict:
    for record in inventory.get("records", []):
        if record.get("name") == name:
            return record
    return {"name": name, "metadataStatus": "missing"}


def grammar_by_source(grammar: dict) -> dict[str, dict]:
    return {item["source"]: item for item in grammar.get("summaries", [])}


def grammar_key_for(name: str) -> str | None:
    if name == "bitcoin3.pdf":
        return "bitcoin3"
    if name == "Issue_26.pdf":
        return "issue26"
    if name == "Issue_27.pdf":
        return "issue27"
    if name == "bitcoin4.pdf":
        return "issue24_toxic_af"
    return None


def compact_grammar(summary: dict | None) -> dict:
    if not summary:
        return {
            "status": "not_tested",
            "note": "No body-highlighter grammar record exists for this PDF in the current style pass.",
        }
    return {
        "status": "available",
        "pages": summary.get("pages"),
        "orangeLineBands": summary.get("totalOrangeLineBands"),
        "darkLineBands": summary.get("totalDarkLineBands"),
        "sustainedGrammarPages": summary.get("sustainedGrammarPages"),
        "mixedOrangeDarkPages": summary.get("mixedOrangeDarkPages"),
        "maxGrammarScore": summary.get("maxGrammarScore"),
    }


def bitcoin4_witness_note(witness: dict, crops: dict) -> dict:
    transform = witness.get("transforms", {}).get("p76", {})
    p78_summary = witness.get("p78FrameTransfer", {})
    crop_rows = []
    for crop in crops.get("crops", []):
        metrics = crop.get("visualMetrics", {})
        crop_rows.append(
            {
                "id": crop.get("id"),
                "text": crop.get("text"),
                "meanAbsDiffAfterResize": metrics.get("meanAbsDiffAfterResize"),
                "avgHashHamming16": metrics.get("avgHashHamming16"),
                "edgeDensityHigh": metrics.get("edgeDensityHigh"),
                "edgeDensityBitcoin4": metrics.get("edgeDensityBitcoin4"),
            }
        )
    return {
        "p76AffineMeanAbsResidualPx": transform.get("meanAbsResidualPx"),
        "p76AffineMaxAbsResidualPx": transform.get("maxAbsResidualPx"),
        "p78FrameTransfer": p78_summary,
        "priorityCropComparisons": crop_rows,
        "interpretation": "Same Issue 24 article is visually preserved, but bitcoin4 is lower-res/distorted and does not repair the p78-frame-to-page-76 G5/O5 registration benchmark.",
    }


def classify(record: dict, style: dict, witness_note: dict | None) -> dict:
    name = record.get("name")
    if record.get("metadataStatus") == "missing":
        return {
            "sourceGateStatus": "missing",
            "allowedUse": "none",
            "reason": "File was not found in the local inventory.",
            "sourceQuality": "missing",
            "geometryTruth": "no",
            "extractionPermission": "blocked",
        }

    if name == "bitcoin4.pdf":
        return {
            "sourceGateStatus": "reject_as_geometry_truth",
            "allowedUse": "low-res Issue 24 source-fidelity witness only",
            "reason": "It is the same Issue 24 article, but the existing witness audits show lower resolution/distortion and no repair of the trusted G5/O5 p78-frame registration.",
            "sourceQuality": "fails extraction-grade quality; passes only as a rough witness",
            "geometryTruth": "no",
            "extractionPermission": "blocked: no unit/order named and no benchmark-changing geometry",
            "styleSummary": style,
            "witnessNote": witness_note,
        }

    if name in {"bitcoin3.pdf", "Issue_26.pdf", "Issue_27.pdf"}:
        return {
            "sourceGateStatus": "reject_for_issue24_geometry",
            "allowedUse": "style-only Max/OVERDOSE comparison",
            "reason": "Different issue/article material cannot alter Issue 24 page-76 geometry or provide extraction coordinates for the 20 BTC puzzle.",
            "sourceQuality": "valid comparison PDF, not source material for Issue 24",
            "geometryTruth": "no-for-issue24",
            "extractionPermission": "blocked: comparison article does not name the Issue 24 extraction unit/order",
            "styleSummary": style,
        }

    return {
        "sourceGateStatus": "reject",
        "allowedUse": "none",
        "reason": "Not part of the comparison-PDF gate target set.",
        "sourceQuality": "unknown",
        "geometryTruth": "no",
        "extractionPermission": "blocked",
    }


def md_table_value(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "-"
    text = str(value)
    return text.replace("|", "/")


def main() -> None:
    inventory = load(INVENTORY_JSON)
    grammar = load(BODY_GRAMMAR_JSON)
    witness = load(BITCOIN4_WITNESS_JSON)
    crops = load(BITCOIN4_CROPS_JSON)
    gate = load(SOURCE_GATE_JSON)
    grammar_lookup = grammar_by_source(grammar)
    b4_note = bitcoin4_witness_note(witness, crops)

    records = []
    for name in TARGETS:
        inv = find_record(inventory, name)
        style = compact_grammar(grammar_lookup.get(grammar_key_for(name)))
        witness_note = b4_note if name == "bitcoin4.pdf" else None
        gate_result = classify(inv, style, witness_note)
        records.append(
            {
                "name": name,
                "path": inv.get("path"),
                "md5": inv.get("md5"),
                "pageCount": inv.get("pageCount"),
                "inventorySourceClass": inv.get("sourceClass"),
                "inventoryGeometryTruth": inv.get("geometryTruth"),
                "inventoryPotential": inv.get("betterSourcePotential"),
                **gate_result,
            }
        )

    promoted = [r for r in records if r["sourceGateStatus"] not in {"reject_as_geometry_truth", "reject_for_issue24_geometry", "reject", "missing"}]
    style_only = [r for r in records if "style" in r["allowedUse"]]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "apply source-validation gate to local comparison PDFs; no OCR/key derivation",
        "inputs": {
            "inventory": str(INVENTORY_JSON.relative_to(ROOT)),
            "bodyHighlighterGrammar": str(BODY_GRAMMAR_JSON.relative_to(ROOT)),
            "bitcoin4Witness": str(BITCOIN4_WITNESS_JSON.relative_to(ROOT)),
            "bitcoin4PriorityCrops": str(BITCOIN4_CROPS_JSON.relative_to(ROOT)),
            "sourceGate": str(SOURCE_GATE_JSON.relative_to(ROOT)),
        },
        "sourceGateExtractionBlock": next(
            (gate_item for gate_item in gate.get("gates", []) if gate_item.get("id") == "extraction_permission"),
            {},
        ),
        "records": records,
        "promotedForExtractionGeometry": len(promoted),
        "styleOnlyComparisonCount": len(style_only),
        "decision": "No comparison PDF passes the source gate for Issue 24 extraction geometry. bitcoin4 remains a low-res Issue 24 fidelity witness; bitcoin3, Issue_26, and Issue_27 remain style-only comparison articles.",
        "nextMove": "Use comparison PDFs only to test whether Typeka/highlighter/pill grammar is unique. Do not use them to select key material unless a future raw clue explicitly references a comparison issue/article.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Comparison PDFs Against Source Gate",
        "",
        "Scope: apply the source-validation gate to local comparison PDFs. No OCR, key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Promoted for Issue 24 extraction geometry: `{result['promotedForExtractionGeometry']}`",
        f"- Style-only comparison PDFs: `{result['styleOnlyComparisonCount']}`",
        "",
        "## Gate Results",
        "",
        "| PDF | class | gate status | allowed use | style/highlighter note | reason |",
        "|---|---|---|---|---|---|",
    ]
    for record in records:
        style = record.get("styleSummary", {})
        if style.get("status") == "available":
            style_note = (
                f"orange={style.get('orangeLineBands')}, dark={style.get('darkLineBands')}, "
                f"sustained={style.get('sustainedGrammarPages')}, max={style.get('maxGrammarScore')}"
            )
        else:
            style_note = style.get("note", "-")
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{record['name']}`",
                    md_table_value(record.get("inventorySourceClass")),
                    f"`{record['sourceGateStatus']}`",
                    md_table_value(record.get("allowedUse")),
                    md_table_value(style_note),
                    md_table_value(record.get("reason")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## bitcoin4 Witness Constraint",
            "",
            "- `bitcoin4.pdf` preserves the same Issue 24 regions only as a lower-resolution witness.",
            f"- Page-76 affine residual in the witness audit: mean `{b4_note['p76AffineMeanAbsResidualPx']}` px, max `{b4_note['p76AffineMaxAbsResidualPx']}` px.",
            "- It does not repair the p78 frame / G5 / O5 benchmark, so it cannot replace `magazine.pdf` for extraction geometry.",
            "",
            "## Decision",
            "",
            f"- {result['decision']}",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("promotedForExtractionGeometry:", len(promoted))
    for record in records:
        print(record["name"], record["sourceGateStatus"], "->", record["allowedUse"])


if __name__ == "__main__":
    main()

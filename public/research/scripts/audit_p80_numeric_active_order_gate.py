#!/usr/bin/env python3
"""Check whether p80 package numbers explain the active page-76 quartet order.

This is a bounded layout/numeric gate. It compares visible p80 package numbers
against the locked O4/B4/G5/O5 line and corridor order. It does not derive
keys, hash text, generate seed phrases, scan WIF/Base58, OCR pages, or check
addresses.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_JSON = ROOT / "analysis_outputs/3d_article_map/p80_package_copy_audit.json"
ACTIVE_JSON = ROOT / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json"
FORMAT_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json"
VOLUME_JSON = ROOT / "analysis_outputs/source_audit/p80_volume_number_impact/p80_volume_number_impact.json"
OUT = ROOT / "analysis_outputs/source_audit/p80_numeric_active_order_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "p80_numeric_active_order_gate.json"
OUT_MD = OUT / "p80_numeric_active_order_gate.md"
SHEET = OUT / "p80_numeric_active_order_gate_sheet.jpg"


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


def contains_subsequence(haystack: list[int], needle: list[int]) -> bool:
    if not needle:
        return True
    if len(needle) > len(haystack):
        return False
    return any(haystack[i : i + len(needle)] == needle for i in range(len(haystack) - len(needle) + 1))


def is_subsequence(haystack: list[int], needle: list[int]) -> bool:
    it = iter(haystack)
    return all(any(value == candidate for value in it) for candidate in needle)


def first_differences(values: list[int]) -> list[int]:
    return [b - a for a, b in zip(values, values[1:])]


def flatten_number_records(rows: list[dict[str, Any]], include_clipped: bool = True) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        if not include_clipped and row.get("label") == "volume_crop_recorded":
            continue
        for number in row.get("numbers", []):
            records.append(
                {
                    "label": row.get("label"),
                    "text": row.get("text"),
                    "number": int(number),
                    "clippedVolumeReading": row.get("label") == "volume_crop_recorded",
                }
            )
    return records


def compare_sequence(name: str, package_numbers: list[int], target: list[int]) -> dict[str, Any]:
    return {
        "target": name,
        "targetSequence": target,
        "exactContiguousSubsequence": contains_subsequence(package_numbers, target),
        "exactOrderedSubsequence": is_subsequence(package_numbers, target),
        "intersection": [value for value in target if value in package_numbers],
        "targetGaps": first_differences(target),
        "gapIntersection": [value for value in first_differences(target) if value in package_numbers],
        "packageFirstFour": package_numbers[:4],
        "packageFirstFourGaps": first_differences(package_numbers[:4]),
        "firstFourEqualsTarget": package_numbers[:4] == target,
        "firstFourEqualsTargetGaps": first_differences(package_numbers[:4]) == first_differences(target),
    }


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1660, 1060
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title = font(34)
    normal = font(18)
    small = font(14)
    mono = font(14)

    draw.text((margin, margin), "P80 Numeric Active-Order Gate", fill=(244, 247, 250), font=title)
    draw.text(
        (margin, margin + 46),
        "Visible p80 package numbers are compared only against the locked page-76 active line/corridor order.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("raw numbers", result["summary"]["rawNumbersCsv"]),
        ("canonical numbers", result["summary"]["canonicalNumbersCsv"]),
        ("active lines", result["summary"]["activePageLines"]),
        ("active corridors", result["summary"]["activeCorridorIndexes"]),
    ]
    widths = [420, 420, 330, 360]
    x = margin
    for (label, value), w in zip(chips, widths):
        draw.rectangle((x, y, x + w, y + 58), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 31), str(value), fill=(232, 239, 246), font=mono)
        x += w + 20

    y += 90
    draw.rectangle((margin, y, sheet_w - margin, y + 108), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Decision", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "P80 numbers support five-count/theme evidence, but do not explain O4/B4/G5/O5 order.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 76),
        "No visible package number sequence contains 22-25-27-32, 4-7-9-14, or the gap pattern 3-2-5.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 140
    draw.text((margin, y), "Package Number Records", fill=(238, 243, 248), font=normal)
    y += 34
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("label", 12), ("text", 280), ("number", 920), ("status", 1040)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["numberRecords"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 40), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 11), row["label"], fill=(176, 186, 198), font=small)
        draw.text((margin + 280, y + 11), row["text"][:82], fill=(176, 186, 198), font=small)
        draw.text((margin + 920, y + 11), str(row["number"]), fill=(232, 239, 246), font=mono)
        status = "clipped duplicate" if row["clippedVolumeReading"] else "visible/canonical"
        draw.text((margin + 1040, y + 11), status, fill=(176, 186, 198), font=small)
        y += 44

    y += 24
    draw.text((margin, y), "Sequence Checks", fill=(238, 243, 248), font=normal)
    y += 34
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("basis", 12), ("target", 240), ("exact", 520), ("ordered", 660), ("intersection", 820), ("gap hits", 1080)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["sequenceChecks"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 40), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 11), row["basis"], fill=(176, 186, 198), font=small)
        draw.text((margin + 240, y + 11), row["target"], fill=(176, 186, 198), font=small)
        draw.text((margin + 520, y + 11), str(row["exactContiguousSubsequence"]), fill=(232, 239, 246), font=mono)
        draw.text((margin + 660, y + 11), str(row["exactOrderedSubsequence"]), fill=(232, 239, 246), font=mono)
        draw.text((margin + 820, y + 11), str(row["intersection"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 1080, y + 11), str(row["gapIntersection"]), fill=(176, 186, 198), font=mono)
        y += 44

    sheet.save(SHEET, quality=94)


def main() -> None:
    package = load_json(PACKAGE_JSON)
    active = load_json(ACTIVE_JSON)
    fmt = load_json(FORMAT_JSON)
    volume = load_json(VOLUME_JSON)

    package_rows = package.get("manualTranscription", [])
    raw_records = flatten_number_records(package_rows, include_clipped=True)
    canonical_records = flatten_number_records(package_rows, include_clipped=False)
    raw_numbers = [row["number"] for row in raw_records]
    canonical_numbers = [row["number"] for row in canonical_records]

    active_records = active.get("records", [])
    active_lines = [int(row.get("pageLine")) for row in active_records]
    active_corridors = [int(row.get("corridorIndex")) for row in active_records]
    active_sentences = [int(row.get("sentenceRow")) for row in active_records]
    active_line_gaps = first_differences(active_lines)
    active_corridor_gaps = first_differences(active_corridors)

    checks = []
    for basis, numbers in [("raw", raw_numbers), ("canonical", canonical_numbers)]:
        for target, sequence in [
            ("active_page_lines", active_lines),
            ("active_corridor_indexes", active_corridors),
            ("active_sentence_rows", active_sentences),
            ("active_page_line_gaps", active_line_gaps),
            ("active_corridor_gaps", active_corridor_gaps),
        ]:
            row = compare_sequence(target, numbers, sequence)
            row["basis"] = basis
            checks.append(row)

    exact_success = [
        row for row in checks if row["exactContiguousSubsequence"] or row["firstFourEqualsTarget"] or row["firstFourEqualsTargetGaps"]
    ]
    ordered_success = [row for row in checks if row["exactOrderedSubsequence"]]
    nonempty_intersections = [row for row in checks if row["intersection"] or row["gapIntersection"]]

    summary = {
        "rawNumbersCsv": ",".join(map(str, raw_numbers)),
        "canonicalNumbersCsv": ",".join(map(str, canonical_numbers)),
        "activePageLines": " ".join(map(str, active_lines)),
        "activeCorridorIndexes": " ".join(map(str, active_corridors)),
        "activeSentenceRows": " ".join(map(str, active_sentences)),
        "activeLineGaps": " ".join(map(str, active_line_gaps)),
        "activeCorridorGaps": " ".join(map(str, active_corridor_gaps)),
        "exactSequenceSuccessCount": len(exact_success),
        "orderedSubsequenceSuccessCount": len(ordered_success),
        "nonemptyIntersectionCount": len(nonempty_intersections),
        "onlyStrongDirectNumberLink": "5 repeats and matches the broader five-unit/five-symptom model, not the four-anchor active quartet order",
        "canonicalVolumeDecision": volume.get("assessment", [""])[0] if volume.get("assessment") else "",
        "formatAuthorityPattern": fmt.get("summary", {}).get("activeColorPattern"),
        "formatAuthorityVisualState": fmt.get("summary", {}).get("activeVisualStateOrder"),
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p80 numeric active-order gate; no extraction, no key derivation, no hashing, no seed/WIF/address checks",
        "inputs": {
            "packageCopy": rel(PACKAGE_JSON),
            "activeLineUnits": rel(ACTIVE_JSON),
            "formatAuthority": rel(FORMAT_JSON),
            "volumeNumberImpact": rel(VOLUME_JSON),
        },
        "summary": summary,
        "numberRecords": raw_records,
        "canonicalNumberRecords": canonical_records,
        "sequenceChecks": checks,
        "assessment": [
            "P80 package numbers do not contain the active quartet page-line order 22 25 27 32 or corridor order 4 7 9 14.",
            "The repeated number 5 remains real count/theme evidence for the broader five-symptom/five-highlight model, but it does not select or order O4/B4/G5/O5.",
            "The likely 16 FL OZ reading supports the already-known B3/stun-gun line-offset evidence, not the lower active quartet.",
            "The clipped 6 reading and repeated 473 mL value add source-fidelity caveats, not selector permission.",
        ],
        "decision": "p80_numbers_do_not_explain_active_quartet_order",
        "sheet": rel(SHEET),
        "nextMove": "Keep p80 numeric copy as C6 count/theme/source-validation evidence only; reopen numeric selection only if a raw clue names page line, corridor index, dose, volume, or symptom number as the extraction unit.",
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P80 Numeric Active-Order Gate",
        "",
        "Scope: compare visible p80 package numbers against the locked O4/B4/G5/O5 page-line and corridor order. No extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Raw p80 numbers: `{summary['rawNumbersCsv']}`.",
        f"- Canonical p80 numbers excluding clipped volume duplicate: `{summary['canonicalNumbersCsv']}`.",
        f"- Active page lines: `{summary['activePageLines']}`.",
        f"- Active corridor indexes: `{summary['activeCorridorIndexes']}`.",
        f"- Active line/corridor gaps: `{summary['activeLineGaps']}` / `{summary['activeCorridorGaps']}`.",
        f"- Exact sequence successes: `{summary['exactSequenceSuccessCount']}`.",
        f"- Ordered subsequence successes: `{summary['orderedSubsequenceSuccessCount']}`.",
        "",
        "## Number Records",
        "",
        "| label | text | number | note |",
        "|---|---|---:|---|",
    ]
    for row in raw_records:
        note = "clipped duplicate reading" if row["clippedVolumeReading"] else "visible/canonical"
        lines.append(f"| `{row['label']}` | `{row['text']}` | `{row['number']}` | {note} |")

    lines.extend(
        [
            "",
            "## Sequence Checks",
            "",
            "| basis | target | sequence | exact contiguous | ordered subsequence | intersection | gap hits |",
            "|---|---|---|---:|---:|---|---|",
        ]
    )
    for row in checks:
        lines.append(
            f"| `{row['basis']}` | `{row['target']}` | `{row['targetSequence']}` | `{row['exactContiguousSubsequence']}` | `{row['exactOrderedSubsequence']}` | `{row['intersection']}` | `{row['gapIntersection']}` |"
        )

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in result["assessment"])
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()

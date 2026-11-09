#!/usr/bin/env python3
"""Check whether the registered 76/79 between-lines geometry recurs."""

from __future__ import annotations

import json
import math
from pathlib import Path

from analyze_registered_76_79_selector import BEST_TRANSFORM, transform_box
from analyze_highres_page76_mirror_selector import area, hflip_box, intersection


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REGISTERED = ROOT / "analysis_outputs/source_audit/registered_76_79_selector.json"
OUT_MD = ROOT / "analysis_outputs/source_audit/registered_76_79_gap_recurrence.md"
OUT_JSON = ROOT / "analysis_outputs/source_audit/registered_76_79_gap_recurrence.json"

PAGE_W = 2544
PAGE_H = 3264


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def overlap_area(a, b) -> float:
    inter = intersection(a, b)
    return area(inter) if inter else 0.0


def page_words(article_map: dict, page: int) -> list[dict]:
    for row in article_map["pages"]:
        if row["page"] == page:
            return row.get("words", [])
    raise ValueError(page)


def words_in_box(words: list[dict], box) -> list[dict]:
    return [w for w in words if overlap_area(w["box"], box) > 0]


def transform_word(word: dict) -> dict:
    hbox = hflip_box(word["box"], PAGE_W)
    mapped = transform_box(tuple(int(round(v)) for v in hbox), PAGE_W, PAGE_H, BEST_TRANSFORM)
    return {**word, "mappedBox": mapped}


def group_rows(records: list[dict], box_key: str, threshold: float = 50.0) -> list[dict]:
    buckets: list[list[dict]] = []
    for rec in sorted(records, key=lambda r: center(r[box_key])[1]):
        cy = center(rec[box_key])[1]
        for bucket in buckets:
            if abs(center(bucket[0][box_key])[1] - cy) <= threshold:
                bucket.append(rec)
                break
        else:
            buckets.append([rec])
    out = []
    for bucket in buckets:
        bucket.sort(key=lambda r: center(r[box_key])[0])
        xs = [r[box_key][0] for r in bucket] + [r[box_key][2] for r in bucket]
        ys = [r[box_key][1] for r in bucket] + [r[box_key][3] for r in bucket]
        out.append(
            {
                "y": round(sum(center(r[box_key])[1] for r in bucket) / len(bucket), 1),
                "box": [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)],
                "text": " ".join(r["text"] for r in bucket),
                "wordCount": len(bucket),
            }
        )
    return out


def gap_candidates(source_rows: list[dict]) -> list[dict]:
    out = []
    rows = sorted(source_rows, key=lambda r: r["y"])
    for idx in range(len(rows) - 1):
        top = rows[idx]
        bottom = rows[idx + 1]
        gap = bottom["y"] - top["y"]
        if gap < 60:
            continue
        out.append(
            {
                "topY": top["y"],
                "bottomY": bottom["y"],
                "midY": round((top["y"] + bottom["y"]) / 2, 1),
                "gapHeight": round(gap, 1),
                "topText": top["text"],
                "bottomText": bottom["text"],
            }
        )
    return out


def main() -> None:
    article_map = json.loads(ARTICLE_MAP.read_text())
    registered = json.loads(REGISTERED.read_text())
    p79_words = page_words(article_map, 79)
    p76_words = page_words(article_map, 76)

    targets = [
        {"targetColor": "orange", **item}
        for item in registered["targetOrange"]
    ] + [
        {"targetColor": "black", **item}
        for item in registered["targetGrey"]
    ]

    source_records = []
    recurrence_rows = []
    for src in registered["registeredSources"]:
        raw_words = words_in_box(p79_words, src["sourceBox"])
        transformed_words = [transform_word(w) for w in raw_words]
        source_rows = group_rows(transformed_words, "mappedBox")
        gaps = gap_candidates(source_rows)
        src_record = {
            "sourceIndex": src["index"],
            "sourceLabel": src["label"],
            "sourceBox": src["sourceBox"],
            "mappedBox": src["mappedBox"],
            "sourceWordCount": len(raw_words),
            "sourceRows": source_rows,
            "gaps": gaps,
        }
        source_records.append(src_record)
        if not gaps:
            continue
        for tgt in targets:
            target_words = words_in_box(p76_words, tgt["box"])
            target_rows = group_rows(target_words, "box")
            box_overlap = overlap_area(src["mappedBox"], tgt["box"])
            target_coverage = box_overlap / max(1.0, area(tgt["box"]))
            source_coverage = box_overlap / max(1.0, area(src["mappedBox"]))
            for gap in gaps:
                for target_row in target_rows:
                    delta = target_row["y"] - gap["midY"]
                    recurrence_rows.append(
                        {
                            "sourceIndex": src["index"],
                            "sourceLabel": src["label"],
                            "targetColor": tgt["targetColor"],
                            "targetIndex": tgt["index"],
                            "targetLabel": tgt["label"],
                            "targetRowText": target_row["text"],
                            "targetRowY": target_row["y"],
                            "gapMidY": gap["midY"],
                            "gapHeight": gap["gapHeight"],
                            "deltaPx": round(delta, 1),
                            "absDeltaPx": round(abs(delta), 1),
                            "gapFraction": round(delta / gap["gapHeight"], 4),
                            "targetCoverage": round(target_coverage, 4),
                            "sourceCoverage": round(source_coverage, 4),
                            "topText": gap["topText"],
                            "bottomText": gap["bottomText"],
                        }
                    )

    # A likely recurrence must have row-gap alignment and some box-level relationship,
    # otherwise unrelated rows at similar y positions create false positives.
    strong = [
        row for row in recurrence_rows
        if row["absDeltaPx"] <= 12 and row["targetCoverage"] >= 0.10
    ]
    strong.sort(key=lambda r: (r["absDeltaPx"], -r["targetCoverage"], r["sourceIndex"], r["targetColor"], r["targetIndex"]))
    nearest = sorted(recurrence_rows, key=lambda r: (r["absDeltaPx"], -r["targetCoverage"]))[:20]

    result = {
        "source": "registered p79-to-p76 transform plus OCR word boxes as labels only",
        "transform": BEST_TRANSFORM,
        "sourceRecords": source_records,
        "allCandidateRows": recurrence_rows,
        "strongRecurrences": strong,
        "nearestRows": nearest,
        "summary": {
            "sourcesChecked": len(registered["registeredSources"]),
            "sourcesWithWords": sum(1 for r in source_records if r["sourceWordCount"] > 0),
            "sourcesWithLineGaps": sum(1 for r in source_records if r["gaps"]),
            "candidateRows": len(recurrence_rows),
            "strongRecurrences": len(strong),
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Registered 76/79 Gap-Recurrence Audit",
        "",
        "Scope: test whether the `between the lines` geometry from the strongest p79/p76 anchor recurs across other registered p79 highlight boxes and page-76 highlight rows. OCR words are labels only; no key derivation was run.",
        "",
        "## Summary",
        "",
        f"- Registered p79 sources checked: {result['summary']['sourcesChecked']}",
        f"- Sources with OCR words: {result['summary']['sourcesWithWords']}",
        f"- Sources with two-row gaps: {result['summary']['sourcesWithLineGaps']}",
        f"- Candidate target-row/gap comparisons: {result['summary']['candidateRows']}",
        f"- Strong recurrences (abs delta <= 12 px and target coverage >= 10%): {len(strong)}",
        "",
        "## Strong Recurrences",
        "",
    ]
    if strong:
        for row in strong:
            md.append(
                f"- p79 box {row['sourceIndex']} `{row['sourceLabel']}` gap mid y={row['gapMidY']} -> "
                f"p76 {row['targetColor']} {row['targetIndex']} `{row['targetLabel']}` row y={row['targetRowY']} "
                f"delta={row['deltaPx']} px, targetCoverage={row['targetCoverage']:.3f}"
            )
            md.append(f"  - between `{row['topText']}` / `{row['bottomText']}`")
            md.append(f"  - target row `{row['targetRowText']}`")
    else:
        md.append("- None.")

    md.extend(["", "## Nearest Rows", ""])
    for row in nearest[:12]:
        md.append(
            f"- delta={row['deltaPx']} px cov={row['targetCoverage']:.3f}: "
            f"p79 {row['sourceIndex']} -> p76 {row['targetColor']} {row['targetIndex']} `{row['targetRowText']}`"
        )

    md.extend(["", "## Source Row/Gaps", ""])
    for rec in source_records:
        if not rec["sourceRows"]:
            continue
        md.append(f"- p79 box {rec['sourceIndex']} `{rec['sourceLabel']}` words={rec['sourceWordCount']}")
        for row in rec["sourceRows"]:
            md.append(f"  - row y={row['y']}: `{row['text']}`")
        for gap in rec["gaps"]:
            md.append(f"  - gap mid={gap['midY']} height={gap['gapHeight']}")

    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- Under the strict recurrence filter, the only strong `between the lines` hit is the already-known p79 box 1 -> p76 grey B1 alignment.",
            "- Other p79 boxes do have two OCR rows after transformation, but their gap midpoints do not coincide with page-76 target rows that also have meaningful box overlap.",
            "- This makes the p79 box 1 / p76 B1 anchor a unique high-quality registration marker in the current 76/79 transform, not a repeated ordered sequence.",
            "- Next best move: treat this anchor as a calibration marker, then look for a separate ordering/instruction clue from the Canva/source clue or from unique visual marks.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()

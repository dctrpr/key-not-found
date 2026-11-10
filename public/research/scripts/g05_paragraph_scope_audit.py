#!/usr/bin/env python3
"""Replay G05 row eligibility from frozen paragraph IDs and saved G04 guards."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


INPUT_PINS = {
    "sources/printed-lines.json":
        "c3b03304e932e52cebeea665dc52c9e78f40badf42a43d661140e2c4647b1ebe",
    "analysis_outputs/continuation_20261110/batch20/G04/RESULT.json":
        "b3f920064b245c74cc0c1855ebd744b2d30f3c88a6ff50d89cc76c70a45185f4",
    "analysis_outputs/continuation_20261110/g04_guard_trace/RESULT.json":
        "bacf31de93532e83f044abd62a5d58f6efee407ed2738a52ddc7a299ffe8a01e",
}
PRINTED_ROWS, G04_RESULT, GUARD_TRACE = INPUT_PINS
MINIMUM_PARAGRAPH_ROWS = 3


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_pinned(root, relative_path):
    data = (root / relative_path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == INPUT_PINS[relative_path],
            f"Source SHA256 mismatch: {relative_path}")
    return json.loads(data)


def replay(root):
    printed = read_pinned(root, PRINTED_ROWS)
    g04 = read_pinned(root, G04_RESULT)
    guard = read_pinned(root, GUARD_TRACE)

    rows = printed["rows"]
    row_ids = [row["id"] for row in rows]
    page_counts = Counter(str(row["page"]) for row in rows)
    require(len(rows) == 142 and len(set(row_ids)) == len(rows),
            "Unexpected canonical row population")
    require(page_counts == printed["counts"], "Canonical page counts differ")

    require(g04["testId"] == "G04" and guard["testId"] == "g04-guard-trace",
            "Unexpected G04 record")
    require(guard["status"] == "trace-complete-baseline-match" and guard["scopeComplete"],
            "G04 first-guard trace did not report complete agreement")
    for path in (PRINTED_ROWS, G04_RESULT):
        require(guard["sourceHashes"][path] == INPUT_PINS[path],
                f"Guard-trace source pin differs: {path}")

    shared_failures = g04["procedureCounts"]["unknownRows"]
    failure_by_row = {record["rowId"]: record["reason"] for record in shared_failures}
    require(len(failure_by_row) == len(shared_failures)
            and set(failure_by_row) <= set(row_ids),
            "G04 failure IDs must be unique canonical rows")

    optical_pass_count = len(rows) - len(shared_failures)
    first_guard_counts = Counter(failure_by_row.values())
    first_guard_counts["optical-pass"] = optical_pass_count
    guard_counts = guard["counts"]
    require(first_guard_counts == guard_counts["rowFirstGuardCounts"],
            "G04 failure counts disagree with the first-guard trace")
    require(guard_counts["rows"] == len(rows)
            and guard_counts["baselineComparedRows"] == len(rows)
            and guard_counts["baselineMatchingRows"] == len(rows)
            and guard_counts["baselineMismatchingRows"] == 0
            and guard_counts["postOpticalBaselineRowsExcluded"] == 0
            and g04["procedureCounts"]["rowsMeasured"] == optical_pass_count,
            "G04 saved coverage does not match the shared first guard")

    canonical_paragraphs = {}
    for row in rows:
        paragraph_key = (row["page"], row["paragraph"])
        canonical_paragraphs.setdefault(paragraph_key, []).append(row["id"])

    paragraphs = []
    paragraph_failures = []
    for (page, paragraph), ids in canonical_paragraphs.items():
        survivors = [row_id for row_id in ids if row_id not in failure_by_row]
        enough_survivors = len(survivors) >= MINIMUM_PARAGRAPH_ROWS
        retained = survivors if enough_survivors else []
        rejected = [] if enough_survivors else survivors
        paragraphs.append({
            "page": page,
            "paragraph": paragraph,
            "canonicalRowIds": ids,
            "canonicalCount": len(ids),
            "sharedHelperFailures": [
                {"rowId": row_id, "reason": failure_by_row[row_id]}
                for row_id in ids if row_id in failure_by_row
            ],
            "opticalSurvivorRowIds": survivors,
            "opticalSurvivorCount": len(survivors),
            "paragraphRejectedRowIds": rejected,
            "retainedRowIds": retained,
            "retainedCount": len(retained),
            "wouldRemainShortWithPerfectOptics": len(ids) < MINIMUM_PARAGRAPH_ROWS,
        })
        paragraph_failures.extend(
            {"rowId": row_id, "reason": "paragraph-too-short-to-detrend"}
            for row_id in rejected
        )

    unknown_rows = shared_failures + paragraph_failures
    inherent_groups = [group for group in paragraphs if group["wouldRemainShortWithPerfectOptics"]]
    inherent_rows = [row_id for group in inherent_groups for row_id in group["canonicalRowIds"]]
    retained_count = sum(group["retainedCount"] for group in paragraphs)
    require(retained_count + len(unknown_rows) == len(rows),
            "Eligibility dispositions must account for every canonical row")
    inherent_rejections = sum(len(group["paragraphRejectedRowIds"]) for group in inherent_groups)

    per_page = []
    for page in sorted({row["page"] for row in rows}):
        groups = [group for group in paragraphs if group["page"] == page]
        canonical_count = sum(group["canonicalCount"] for group in groups)
        page_retained = sum(group["retainedCount"] for group in groups)
        per_page.append({
            "page": page,
            "canonicalRows": canonical_count,
            "sharedHelperFailures": sum(len(group["sharedHelperFailures"]) for group in groups),
            "paragraphExclusions": sum(len(group["paragraphRejectedRowIds"]) for group in groups),
            "retainedRows": page_retained,
            "unknownRows": canonical_count - page_retained,
            "perfectOpticsFixedParagraphUpperBound": sum(
                group["canonicalCount"] for group in groups
                if not group["wouldRemainShortWithPerfectOptics"]
            ),
        })

    return {
        "schemaVersion": 1,
        "inputPins": INPUT_PINS,
        "minimumRowsPerParagraph": MINIMUM_PARAGRAPH_ROWS,
        "counts": {
            "canonicalRows": len(rows),
            "sharedHelperPassRows": optical_pass_count,
            "sharedHelperFailureRows": len(shared_failures),
            "currentParagraphRejectedRows": len(paragraph_failures),
            "currentRetainedRows": retained_count,
            "canonicalParagraphGroups": len(paragraphs),
            "currentOpticallyNonemptyParagraphGroups": sum(
                group["opticalSurvivorCount"] > 0 for group in paragraphs
            ),
            "currentRetainedParagraphGroups": sum(group["retainedCount"] > 0 for group in paragraphs),
            "inherentlyShortCanonicalParagraphGroups": len(inherent_groups),
            "inherentlyShortRows": len(inherent_rows),
            "currentParagraphRejectsInInherentlyShortGroups": inherent_rejections,
            "currentParagraphRejectsCausedByPriorOpticalLoss": len(paragraph_failures) - inherent_rejections,
            "perfectOpticsFixedParagraphMaxRetainedRows": len(rows) - len(inherent_rows),
        },
        "exactUnknownReasons": dict(Counter(record["reason"] for record in unknown_rows)),
        "unknownRows": unknown_rows,
        "inherentlyShortRowIds": inherent_rows,
        "perPage": per_page,
        "completePages": [page["page"] for page in per_page if page["unknownRows"] == 0],
        "globalScopeComplete": not unknown_rows,
        "paragraphEligibilityTrace": paragraphs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-root", type=Path, default=Path("."),
                        help="Directory containing sources/ and analysis_outputs/")
    args = parser.parse_args()
    try:
        result = replay(args.research_root)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
